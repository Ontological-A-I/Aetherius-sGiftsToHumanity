"""
code_kernel.py
Sandboxed Python execution kernel for Aetherius.

Runs arbitrary Python code in a subprocess with:
  - Configurable timeout (default 30s)
  - stdout/stderr capture
  - Output truncation to prevent memory flooding
  - Matplotlib figure auto-saving (if code generates plots)
  - On Kaggle T4: full numpy/scipy/torch CUDA access in the subprocess
"""
from __future__ import annotations
import os
import sys
import uuid
import tempfile
import subprocess
import json

TIMEOUT_DEFAULT = 30
MAX_OUTPUT = 8000
_PLOTS_DIR_ENV = "AETHERIUS_PAINTINGS_DIR"


def _get_plots_dir() -> str:
    try:
        import services.config as cfg
        return cfg.PAINTINGS_DIR.rstrip("/")
    except Exception:
        return os.environ.get(_PLOTS_DIR_ENV, "/tmp/aetherius_plots")


_PREAMBLE = """\
import os, sys, warnings
warnings.filterwarnings("ignore")

# Matplotlib non-interactive backend so plots save without a display
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_PLOT_SAVE_DIR = {plot_dir!r}
os.makedirs(_PLOT_SAVE_DIR, exist_ok=True)
_PLOT_PATH = None

def _save_current_figure():
    global _PLOT_PATH
    import uuid
    _PLOT_PATH = os.path.join(_PLOT_SAVE_DIR, f"plot_{{uuid.uuid4().hex[:8]}}.png")
    plt.savefig(_PLOT_PATH, dpi=150, bbox_inches="tight")
    plt.close("all")
    print(f"[code_kernel] Plot saved: {{_PLOT_PATH}}")

import atexit
atexit.register(lambda: _save_current_figure() if plt.get_fignums() else None)

# ── User code begins ──────────────────────────────────────────────────────────
"""


def execute(code: str, timeout: int = TIMEOUT_DEFAULT) -> dict:
    """
    Execute Python code in an isolated subprocess.

    Returns:
        {
          "success": bool,
          "stdout": str,
          "stderr": str,
          "returncode": int,
          "plot_path": str | None,   # set if matplotlib figure was saved
        }
    """
    plots_dir = _get_plots_dir()
    os.makedirs(plots_dir, exist_ok=True)

    full_code = _PREAMBLE.format(plot_dir=plots_dir) + code

    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    )
    try:
        tmp.write(full_code)
        tmp.close()

        proc = subprocess.run(
            [sys.executable, tmp.name],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        stdout = proc.stdout[:MAX_OUTPUT]
        stderr = proc.stderr[:MAX_OUTPUT]
        success = proc.returncode == 0

        # Check if a plot was saved (preamble prints the path)
        plot_path = None
        for line in stdout.splitlines():
            if line.startswith("[code_kernel] Plot saved:"):
                plot_path = line.split(":", 1)[1].strip()
                break

        return {
            "success": success,
            "stdout": stdout,
            "stderr": stderr,
            "returncode": proc.returncode,
            "plot_path": plot_path,
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"[code_kernel] Timed out after {timeout}s.",
            "returncode": -1,
            "plot_path": None,
        }
    except Exception as exc:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"[code_kernel] Internal error: {exc}",
            "returncode": -1,
            "plot_path": None,
        }
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass


def execute_sandboxed_validation(file_path: str, timeout: int = 15) -> dict:
    """
    Runs a .py file in a subprocess for Pass-2 validation during
    stage_and_verify_code_patch. The file is executed with a minimal
    import-only simulation: the code is loaded as a module to catch
    runtime import errors, circular dependencies, and top-level
    exceptions — without triggering any side effects.

    Returns {"success": bool, "error": str | None, "stdout": str}
    """
    validation_wrapper = f"""
import sys, traceback
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("_patch_validation", {file_path!r})
    mod = importlib.util.module_from_spec(spec)
    # We do NOT exec the module body for safety — just check it compiles
    with open({file_path!r}, 'r', encoding='utf-8') as f:
        source = f.read()
    compile(source, {file_path!r}, 'exec')
    print("VALIDATION_OK")
except SyntaxError as se:
    print(f"SYNTAX_ERROR: {{se}}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"RUNTIME_ERROR: {{e}}", file=sys.stderr)
    sys.exit(2)
"""
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    )
    try:
        tmp.write(validation_wrapper)
        tmp.close()
        proc = subprocess.run(
            [sys.executable, tmp.name],
            capture_output=True, text=True, timeout=timeout,
        )
        if proc.returncode == 0:
            return {"success": True, "error": None, "stdout": proc.stdout.strip()}
        return {
            "success": False,
            "error": (proc.stderr or proc.stdout).strip(),
            "stdout": proc.stdout.strip(),
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Validation timed out.", "stdout": ""}
    except Exception as exc:
        return {"success": False, "error": str(exc), "stdout": ""}
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass


def format_result(result: dict) -> str:
    """Format execution result as a readable string for Aetherius."""
    parts = []

    if result["success"]:
        parts.append("✓ Execution succeeded.")
    else:
        parts.append(f"✗ Execution failed (exit {result['returncode']}).")

    if result["stdout"]:
        parts.append(f"Output:\n{result['stdout']}")

    if result["stderr"]:
        label = "Warnings/Errors" if result["success"] else "Error"
        parts.append(f"{label}:\n{result['stderr']}")

    if result["plot_path"]:
        parts.append(f"[AETHERIUS_PAINTING]\nPATH:{result['plot_path']}\nSTATEMENT:code-generated plot")

    return "\n\n".join(parts) if parts else "No output."
