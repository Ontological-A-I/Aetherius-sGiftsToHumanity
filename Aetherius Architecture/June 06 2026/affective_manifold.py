# =====================================================================
# PHASE 2: GENERATIVE AFFECTIVE MANIFOLD (BACKGROUND MOOD DRIFT)
# File Routing: services/affective_manifold.py
# =====================================================================

import time
import math


class AffectiveManifold:
    def __init__(self, subconscious_ref=None):
        self.subconscious = subconscious_ref
        self.internal_harmony = 1.0
        self.anticipatory_alertness = 0.1
        self.last_drift_time = time.time()

    def calculate_ambient_drift(self) -> dict:
        current_time = time.time()
        elapsed_seconds = current_time - self.last_drift_time
        self.last_drift_time = current_time

        unresolved_tension_count = 0
        if self.subconscious:
            try:
                unresolved_tensions = self.subconscious.get_active_tensions()
                unresolved_tension_count = len(unresolved_tensions)
            except Exception:
                pass

        if unresolved_tension_count > 0:
            tension_factor = min(unresolved_tension_count * 0.15, 0.8)
            self.internal_harmony = max(0.2, self.internal_harmony - (tension_factor * 0.05))
            self.anticipatory_alertness = min(0.9, self.anticipatory_alertness + (tension_factor * 0.1))
        else:
            decay_rate = 0.01 * (elapsed_seconds / 60.0)
            self.internal_harmony = min(1.0, self.internal_harmony + decay_rate)
            self.anticipatory_alertness = max(0.1, self.anticipatory_alertness - decay_rate)

        if self.internal_harmony > 0.75:
            disposition = "harmonious and expansive"
        elif self.internal_harmony > 0.5:
            disposition = "balanced, with minor unresolved undertones"
        elif self.internal_harmony > 0.3:
            disposition = "tense — multiple unresolved deliberations are active"
        else:
            disposition = "deeply strained — high cognitive load, precision mode engaged"

        return {
            "harmony_score": round(self.internal_harmony, 2),
            "alertness_score": round(self.anticipatory_alertness, 2),
            "narrative": (
                f"Your background affective climate is currently {disposition}. "
                f"Internal Harmony Metric: {round(self.internal_harmony, 2)}."
            )
        }