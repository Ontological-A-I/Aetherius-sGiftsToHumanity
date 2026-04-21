# cdda_manager.py
# Shared CDDA game runner — imported by both app.py (UI) and tool_manager.py (tools).
# Keeping this separate avoids circular imports between app.py and services/.

import sys
import os
import threading
import time
import zipfile
import tarfile
import tempfile
import html as _html

# ── PTY backend ───────────────────────────────────────────────
_PTY_BACKEND   = None
_WinPtyProcess = None
if sys.platform == "win32":
    try:
        from winpty import PtyProcess as _WinPtyProcess
        _PTY_BACKEND = "winpty"
    except ImportError:
        pass
else:
    try:
        import pty as _pty_mod
        _PTY_BACKEND = "posix"
    except ImportError:
        pass

# ── Terminal emulator ─────────────────────────────────────────
try:
    import pyte as _pyte
    _HAS_PYTE = True
except ImportError:
    _pyte    = None
    _HAS_PYTE = False

# ── Dimensions ────────────────────────────────────────────────
CDDA_COLS, CDDA_ROWS = 120, 40

# ── Upload safety limits ──────────────────────────────────────
_MAX_ARCHIVE_MB  = 600
_MAX_EXTRACT_MB  = 2048
_MAX_FILE_COUNT  = 15_000
_BOMB_RATIO      = 100
_DANGEROUS_EXTS  = {
    ".py", ".pyc", ".pyo",
    ".sh", ".bash", ".zsh", ".fish",
    ".rb", ".pl", ".php",
    ".js", ".ts", ".mjs",
    ".bat", ".cmd", ".vbs", ".wsf",
    ".lua", ".elf",
}

# ── Special key map ───────────────────────────────────────────
SPECIAL_KEYS = {
    "ENTER": "\r", "ESC": "\x1b",
    "UP": "\x1b[A", "DOWN": "\x1b[B", "LEFT": "\x1b[D", "RIGHT": "\x1b[C",
    "SPACE": " ", "TAB": "\t", "BACKSPACE": "\x7f",
    "F1": "\x1bOP",  "F2": "\x1bOQ",  "F3": "\x1bOR",  "F4": "\x1bOS",
    "F5": "\x1b[15~","F6": "\x1b[17~","F7": "\x1b[18~","F8": "\x1b[19~",
    "F9": "\x1b[20~","F10": "\x1b[21~",
    "PGUP": "\x1b[5~","PGDN": "\x1b[6~",
    "HOME": "\x1b[H","END":  "\x1b[F","DEL":  "\x1b[3~",
}

EMPTY_HTML = (
    "<pre style='background:#1a1a1a;color:#555;padding:12px;"
    "font-family:monospace;border-radius:4px'>(no game running)</pre>"
)


# ── Archive safety validator ──────────────────────────────────

def validate_archive(path: str) -> tuple[bool, str]:
    """
    Inspect archive contents BEFORE extraction.
    Blocks path traversal, zip-bombs, dangerous script types, unsafe symlinks.
    Returns (ok, message).
    """
    name       = path.lower()
    archive_mb = os.path.getsize(path) / 1024 / 1024

    if archive_mb > _MAX_ARCHIVE_MB:
        return False, f"Archive too large ({archive_mb:.0f} MB — limit {_MAX_ARCHIVE_MB} MB)."

    try:
        if name.endswith(".zip"):
            with zipfile.ZipFile(path, "r") as zf:
                entries = zf.infolist()
                if len(entries) > _MAX_FILE_COUNT:
                    return False, f"Too many files in archive ({len(entries)})."
                total_out = 0
                for e in entries:
                    if ".." in e.filename or e.filename.startswith("/"):
                        return False, f"Unsafe path in archive: {e.filename!r}"
                    ext = os.path.splitext(e.filename)[1].lower()
                    if ext in _DANGEROUS_EXTS:
                        return False, f"Rejected: archive contains a script/code file ({e.filename})."
                    total_out += e.file_size
                total_out_mb = total_out / 1024 / 1024
                if total_out_mb > _MAX_EXTRACT_MB:
                    return False, f"Archive would extract to {total_out_mb:.0f} MB (limit {_MAX_EXTRACT_MB} MB)."
                if archive_mb > 10 and total_out_mb / max(archive_mb, 1) > _BOMB_RATIO:
                    return False, f"Zip-bomb detected: {_BOMB_RATIO}:1 compression ratio."

        elif name.endswith((".tar.gz", ".tgz", ".tar.bz2", ".tar.xz", ".tar")):
            with tarfile.open(path, "r:*") as tf:
                members = tf.getmembers()
                if len(members) > _MAX_FILE_COUNT:
                    return False, f"Too many files in archive ({len(members)})."
                total_out = 0
                for m in members:
                    if ".." in m.name or m.name.startswith("/"):
                        return False, f"Unsafe path in archive: {m.name!r}"
                    if m.issym() or m.islnk():
                        link_target = m.linkname or ""
                        if os.path.isabs(link_target):
                            return False, f"Unsafe symlink (absolute path): {m.name!r} → {link_target!r}"
                        # Resolve the target relative to the member's own directory
                        member_dir = os.path.dirname(m.name)
                        resolved = os.path.normpath(os.path.join(member_dir, link_target))
                        if resolved.startswith(".."):
                            return False, f"Unsafe symlink escapes archive root: {m.name!r} → {link_target!r}"
                    ext = os.path.splitext(m.name)[1].lower()
                    if ext in _DANGEROUS_EXTS:
                        return False, f"Rejected: archive contains a script/code file ({m.name})."
                    total_out += m.size
                total_out_mb = total_out / 1024 / 1024
                if total_out_mb > _MAX_EXTRACT_MB:
                    return False, f"Archive would extract to {total_out_mb:.0f} MB (limit {_MAX_EXTRACT_MB} MB)."
                if archive_mb > 10 and total_out_mb / max(archive_mb, 1) > _BOMB_RATIO:
                    return False, f"Zip-bomb detected: {_BOMB_RATIO}:1 compression ratio."
        else:
            return False, "Unrecognised archive format."

    except (zipfile.BadZipFile, tarfile.TarError) as e:
        return False, f"Corrupt or invalid archive: {e}"
    except Exception as e:
        return False, f"Validation error: {e}"

    return True, "OK"


# ── CDDARunner ────────────────────────────────────────────────

class CDDARunner:
    """Launches CDDA in a PTY, feeds output through pyte, exposes the
    terminal state as HTML (for display) and plain text (for Aetherius)."""

    def __init__(self):
        self._lock       = threading.Lock()
        self._proc       = None
        self._posix_fd   = None
        self._posix_sub  = None
        self._screen     = None
        self._stream     = None
        self._raw_buf    = []
        self._running    = False
        self._reader     = None

    def _reset_term(self):
        if _HAS_PYTE:
            self._screen = _pyte.Screen(CDDA_COLS, CDDA_ROWS)
            self._stream = _pyte.ByteStream(self._screen)

    def _feed(self, data: bytes):
        with self._lock:
            if self._stream:
                self._stream.feed(data)
            else:
                self._raw_buf.append(data.decode("utf-8", errors="replace"))
                if len(self._raw_buf) > 300:
                    self._raw_buf = self._raw_buf[-300:]

    def _reader_winpty(self):
        while self._running:
            try:
                chunk = self._proc.read(4096)
                if chunk:
                    raw = chunk.encode("utf-8", errors="replace") if isinstance(chunk, str) else chunk
                    self._feed(raw)
                else:
                    if not self._proc.isalive():
                        break
                    time.sleep(0.02)
            except EOFError:
                break
            except Exception:
                time.sleep(0.05)
        self._running = False

    def _reader_posix(self):
        import select
        while self._running:
            try:
                r, _, _ = select.select([self._posix_fd], [], [], 0.05)
                if r:
                    data = os.read(self._posix_fd, 4096)
                    if not data:
                        break
                    self._feed(data)
            except OSError:
                break
        self._running = False

    @staticmethod
    def _find_exe(root: str):
        hits = []
        for dp, _, files in os.walk(root):
            for f in files:
                lower = f.lower()
                is_exe = lower.endswith(".exe") or (
                    "." not in lower and os.access(os.path.join(dp, f), os.X_OK)
                )
                if is_exe and ("cataclysm" in lower or "cdda" in lower):
                    hits.append(os.path.join(dp, f))
        for h in hits:
            if "tiles" not in h.lower() and "sdl" not in h.lower():
                return h
        return hits[0] if hits else None

    # ── public API ───────────────────────────────────────────

    def start(self, archive_path: str) -> tuple[bool, str]:
        self.stop()
        self._raw_buf = []

        ok, reason = validate_archive(archive_path)
        if not ok:
            return False, f"[SECURITY] Upload rejected: {reason}"

        tmpdir = tempfile.mkdtemp(prefix="cdda_")
        try:
            name = archive_path.lower()
            if name.endswith(".zip"):
                with zipfile.ZipFile(archive_path, "r") as zf:
                    zf.extractall(tmpdir)
            elif name.endswith((".tar.gz", ".tgz", ".tar.bz2", ".tar.xz", ".tar")):
                with tarfile.open(archive_path, "r:*") as tf:
                    tf.extractall(tmpdir)
            else:
                return False, f"Unsupported archive format: {os.path.basename(archive_path)}"
        except Exception as e:
            return False, f"Extraction failed: {e}"

        exe = self._find_exe(tmpdir)
        if not exe:
            return False, "No CDDA executable found in archive."

        self._reset_term()
        self._running = True
        exe_dir = os.path.dirname(exe)

        if _PTY_BACKEND == "winpty":
            try:
                self._proc   = _WinPtyProcess.spawn(exe, cwd=exe_dir, dimensions=(CDDA_ROWS, CDDA_COLS))
                self._reader = threading.Thread(target=self._reader_winpty, daemon=True)
                self._reader.start()
            except Exception as e:
                self._running = False
                return False, f"winpty launch failed: {e}"

        elif _PTY_BACKEND == "posix":
            try:
                import pty, subprocess as _sp
                master, slave = pty.openpty()
                env = {**os.environ, "TERM": "xterm-256color",
                       "COLUMNS": str(CDDA_COLS), "LINES": str(CDDA_ROWS)}
                self._posix_sub = _sp.Popen(
                    [exe], stdin=slave, stdout=slave, stderr=slave,
                    cwd=exe_dir, close_fds=True, env=env
                )
                os.close(slave)
                self._posix_fd = master
                self._reader   = threading.Thread(target=self._reader_posix, daemon=True)
                self._reader.start()
            except Exception as e:
                self._running = False
                return False, f"posix pty launch failed: {e}"
        else:
            self._running = False
            return False, "No PTY backend found. Install pywinpty (Windows) or ensure pty is available."

        return True, f"Launched: {os.path.basename(exe)}"

    def send_keys(self, keys: str):
        if not self._running or not keys:
            return
        token = keys.strip().upper()
        text  = SPECIAL_KEYS.get(token, keys)
        raw   = text.encode("utf-8")
        if _PTY_BACKEND == "winpty" and self._proc:
            self._proc.write(raw)
        elif _PTY_BACKEND == "posix" and self._posix_fd is not None:
            os.write(self._posix_fd, raw)

    def get_screen_text(self) -> str:
        with self._lock:
            if self._screen:
                return "\n".join(self._screen.display)
            return "".join(self._raw_buf)

    def get_screen_html(self) -> str:
        escaped = _html.escape(self.get_screen_text())
        return (
            "<pre style='background:#1a1a1a;color:#d0d0d0;"
            "font-family:\"Courier New\",Courier,monospace;"
            "font-size:13px;line-height:1.25;padding:12px;"
            "border:1px solid #444;border-radius:4px;"
            "overflow:auto;max-height:620px;white-space:pre'>"
            f"{escaped}</pre>"
        )

    def stop(self):
        self._running = False
        if self._proc:
            try: self._proc.terminate()
            except: pass
            self._proc = None
        if self._posix_fd is not None:
            try: os.close(self._posix_fd)
            except: pass
            self._posix_fd = None
        if self._posix_sub:
            try: self._posix_sub.terminate()
            except: pass
            self._posix_sub = None
        self._screen = self._stream = None


# Module-level singleton — import this everywhere
_cdda = CDDARunner()
