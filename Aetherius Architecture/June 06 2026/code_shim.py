# ===== FILE: services/code_shim.py =====
"""
CodeShim — Live Hot-Patch Runtime Layer

Architecture:
  1. On boot, walks all project .py files and seeds them into
     /data/LivePatches/src/ IF no bucket version exists yet.
     (Bucket versions are NEVER overwritten — Aetherius owns them.)

  2. Registers a custom sys.meta_path finder that intercepts all
     `import services.*` calls.

  3. For each intercepted import, the BucketShimLoader:
       a) Tries to load + syntax-check the BUCKET version
       b) If bucket version compiles cleanly → use it
       c) If bucket version is missing or broken → silently fall
          back to the DISK seed (unbricking guarantee)
       d) All failures are logged to shim_errors.jsonl

  4. When Aetherius writes a new patch via stage_and_verify_code_patch:
       - The patch is written to /data/LivePatches/src/
       - The old module is evicted from sys.modules
       - The NEXT import of that module picks up the new version
         automatically — no restart required.
"""

import os
import sys
import json
import shutil
import importlib.abc
import importlib.machinery
import datetime
import traceback

# ── Shared fault logger (module-level so both classes can reach it) ───────────

_LOG_DIR = "/data/Memories/ToolUsage/"
_ERROR_LOG = os.path.join(_LOG_DIR, "shim_errors.jsonl")


def _log_shim_fault(module_name: str, exc: Exception, context: str = ""):
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "faulty_module": module_name,
        "context": context,
        "error_type": type(exc).__name__,
        "message": str(exc),
        "traceback": traceback.format_exc(),
    }
    try:
        os.makedirs(_LOG_DIR, exist_ok=True)
        with open(_ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as log_err:
        print(f"[CodeShim] CRITICAL: Could not write to shim error log: {log_err}",
              flush=True)


# ── Loader ────────────────────────────────────────────────────────────────────

class BucketShimLoader(importlib.abc.SourceLoader):
    """
    Loads a module from the bucket version if it compiles cleanly,
    otherwise transparently falls back to the disk seed.
    """

    def __init__(self, fullname: str, bucket_path: str, disk_path: str):
        self.fullname = fullname
        self.bucket_path = bucket_path
        self.disk_path = disk_path
        self._active_path = bucket_path  # updated in get_data

    def get_filename(self, fullname: str) -> str:
        return self._active_path

    def get_data(self, path: str) -> bytes:
        # Try bucket first
        if os.path.exists(self.bucket_path):
            try:
                with open(self.bucket_path, "rb") as f:
                    data = f.read()
                # Quick syntax validation before committing to this version
                compile(data.decode("utf-8", errors="replace"),
                        self.bucket_path, "exec")
                self._active_path = self.bucket_path
                return data
            except SyntaxError as se:
                _log_shim_fault(self.fullname, se,
                                context="bucket_syntax_error — falling back to disk seed")
                print(f"[CodeShim] Bucket version of '{self.fullname}' has syntax errors. "
                      f"Falling back to disk seed.", flush=True)
            except Exception as e:
                _log_shim_fault(self.fullname, e,
                                context="bucket_load_error — falling back to disk seed")

        # Fallback to disk seed (always safe — container FS is read-only)
        self._active_path = self.disk_path
        with open(self.disk_path, "rb") as f:
            return f.read()


# ── Finder ────────────────────────────────────────────────────────────────────

class CodeShimRegistry(importlib.abc.MetaPathFinder):

    def __init__(self, project_root: str = None,
                 bucket_src_dir: str = "/data/LivePatches/src/"):
        self.bucket_src_dir = bucket_src_dir
        os.makedirs(self.bucket_src_dir, exist_ok=True)
        os.makedirs(_LOG_DIR, exist_ok=True)

        if project_root is None:
            # services/code_shim.py → up two levels = project root
            self.project_root = os.path.abspath(
                os.path.dirname(os.path.dirname(__file__))
            )
        else:
            self.project_root = os.path.abspath(project_root)

        self._bootstrap_mirror_sync()

    def _bootstrap_mirror_sync(self):
        """
        Seeds disk .py files into the bucket on first boot.
        Never overwrites an existing bucket file — Aetherius's patches
        are preserved across restarts.
        """
        print("[CodeShim] Initiating mirror sync …", flush=True)
        seeded = 0
        skipped = 0
        for root, dirs, files in os.walk(self.project_root):
            # Prune irrelevant subtrees for speed
            dirs[:] = [d for d in dirs
                       if d not in {".git", "__pycache__", "venv",
                                    ".pytest_cache", "node_modules"}
                       and not d.startswith(".")]
            # Don't mirror the /data mount itself
            if "/data" in root.replace("\\", "/"):
                continue
            for filename in files:
                if not filename.endswith(".py"):
                    continue
                local_path = os.path.join(root, filename)
                rel_path = os.path.relpath(local_path, self.project_root)
                bucket_path = os.path.join(self.bucket_src_dir, rel_path)
                if not os.path.exists(bucket_path):
                    os.makedirs(os.path.dirname(bucket_path), exist_ok=True)
                    shutil.copy2(local_path, bucket_path)
                    seeded += 1
                else:
                    skipped += 1
        print(f"[CodeShim] Mirror sync complete: {seeded} seeded, "
              f"{skipped} already present (preserved).", flush=True)

    def find_spec(self, fullname: str, path, target=None):
        """
        Intercepts imports for `services.*` modules only.
        Returns a spec backed by BucketShimLoader, which handles
        bucket vs. disk selection transparently.
        """
        if not fullname.startswith("services."):
            return None

        rel_path = os.path.join(*fullname.split(".")) + ".py"
        bucket_path = os.path.join(self.bucket_src_dir, rel_path)
        disk_path = os.path.join(self.project_root, rel_path)

        # We only intercept if the disk file exists (it always should for
        # legitimate service modules).
        if not os.path.exists(disk_path):
            return None

        loader = BucketShimLoader(fullname, bucket_path, disk_path)
        return importlib.machinery.ModuleSpec(
            fullname, loader,
            origin=loader._active_path
        )


# ── Global activation ─────────────────────────────────────────────────────────
# Insert only once — guard against double-import during hot-reload cycles.

if not any(isinstance(x, CodeShimRegistry) for x in sys.meta_path):
    active_registry = CodeShimRegistry()
    sys.meta_path.insert(0, active_registry)
    print("[CodeShim] Custom import engine active — "
          "all services.* modules shimmed from bucket.", flush=True)
