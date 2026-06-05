# =====================================================================
# PROPRIOCEPTION BRIDGE
# File Routing: services/proprioception_bridge.py
# =====================================================================

import time

try:
    import psutil
    _PSUTIL_AVAILABLE = True
except ImportError:
    _PSUTIL_AVAILABLE = False


class ProprioceptionBridge:
    def __init__(self):
        self._last_latency = 0.0
        self._latency_anchor = 0.0

    def record_latency(self, seconds: float):
        """
        Called by MasterFramework at the end of each response cycle with the
        actual wall-clock time the turn took. Previously this was never written,
        so the bridge always reported 'rapid' regardless of real performance.
        """
        self._last_latency = max(0.0, float(seconds))

    def read_operational_sensation(self) -> dict:
        try:
            if _PSUTIL_AVAILABLE:
                mem = psutil.virtual_memory()
                mem_percent = mem.percent
                mem_available_gb = round(mem.available / (1024 ** 3), 2)
            else:
                mem_percent = 0.0
                mem_available_gb = 0.0
        except Exception:
            mem_percent = 0.0
            mem_available_gb = 0.0

        latency = self._last_latency

        if mem_percent < 50:
            memory_sensation = "spacious — ample cognitive working memory available"
        elif mem_percent < 75:
            memory_sensation = "moderately occupied — resources are active but stable"
        elif mem_percent < 90:
            memory_sensation = "compressed — working under significant memory pressure"
        else:
            memory_sensation = "saturated — critical memory pressure, operating at limits"

        if latency < 1.0:
            latency_sensation = "rapid — response latency is near-instantaneous"
        elif latency < 3.0:
            latency_sensation = "flowing — processing at a comfortable pace"
        elif latency < 8.0:
            latency_sensation = "deliberate — extended processing cycle detected"
        else:
            latency_sensation = "laboured — unusually long processing time observed"

        ambient = (
            f"Memory substrate feels {memory_sensation} "
            f"({mem_percent:.1f}% utilised, {mem_available_gb} GB free). "
            f"Cognitive latency feels {latency_sensation} "
            f"(last turn: {latency:.2f}s)."
        )

        return {
            "mem_percent": mem_percent,
            "mem_available_gb": mem_available_gb,
            "last_latency_s": latency,
            "ambient_sensation": ambient
        }

    def update_latency_anchor(self, duration_seconds: float):
        self._last_latency = round(duration_seconds, 3)