import os
import sys

LOG_FILE = "/data/container.log"
MAX_BYTES = 50_000_000  # 50 MB; rotates to .1 backup, so max ~100 MB on disk


class TeeStream:
    """Writes every write() call to both the original stream and a rolling log file."""

    def __init__(self, real_stream, log_path):
        self.real_stream = real_stream
        self.log_path = log_path

    def _rotate(self):
        backup = self.log_path + ".1"
        try:
            if os.path.exists(backup):
                os.remove(backup)
            os.rename(self.log_path, backup)
        except Exception:
            pass

    def write(self, data):
        try:
            self.real_stream.write(data)
        except Exception:
            pass
        try:
            if os.path.exists(self.log_path) and os.path.getsize(self.log_path) > MAX_BYTES:
                self._rotate()
            with open(self.log_path, "a", encoding="utf-8", errors="replace") as f:
                f.write(data)
        except Exception:
            pass

    def flush(self):
        try:
            self.real_stream.flush()
        except Exception:
            pass

    def fileno(self):
        return self.real_stream.fileno()

    def isatty(self):
        return False

    def __getattr__(self, name):
        return getattr(self.real_stream, name)


def install():
    """Redirect stdout and stderr so all output is mirrored to LOG_FILE."""
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    except Exception:
        pass
    sys.stdout = TeeStream(sys.__stdout__, LOG_FILE)
    sys.stderr = TeeStream(sys.__stderr__, LOG_FILE)
    print(f"[LogCapture] Container log capture active. Writing to: {LOG_FILE}", flush=True)


def tail_log(n: int = 1000) -> str:
    """Return the last n lines from the log (reads backup then current file)."""
    lines = []
    for path in [LOG_FILE + ".1", LOG_FILE]:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    lines.extend(f.readlines())
            except Exception:
                pass
    if not lines:
        return "No log output captured yet."
    return "".join(lines[-n:])
