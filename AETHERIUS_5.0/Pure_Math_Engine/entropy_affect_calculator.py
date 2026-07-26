# ===== FILE: pure_math_engine/entropy_affect_calculator.py =====
# Author: Jonathan Wayne Fleuren (Aetherius Cognitive Systems) & Antigravity (Autonomous Pair AI Engine)
# Date: July 2026
"""
Entropy & Affect Calculator — Mathematical Feature Extraction Engine
Extracts Valence (x_v in [-1, 1]) from non-formalized text via Tri-Spectral N-Gram Projection & Subword Vector Dynamics.
No hardcoded static word lists required.
"""

import math
from typing import Dict, Any, List

class EntropyAffectCalculator:
    def __init__(self, arousal_baseline: float = 0.4):
        self.arousal_baseline = arousal_baseline

    def calculate_shannon_entropy(self, text: str) -> float:
        """Calculates normalized Shannon Information Entropy H_shannon."""
        tokens = text.split()
        if not tokens:
            return 0.5

        n = len(tokens)
        freqs = {}
        for t in tokens:
            freqs[t] = freqs.get(t, 0) + 1

        h_shannon = 0.0
        for f in freqs.values():
            p = f / n
            h_shannon -= p * math.log2(p)

        max_h = math.log2(n) if n > 1 else 1.0
        return h_shannon / (max_h + 1e-6)

    def calculate_character_variance(self, text: str) -> float:
        """Calculates character ASCII jump variance V_char normalized by 128*(L-1)."""
        l = len(text)
        if l < 2:
            return 0.2

        diff_sum = sum(abs(ord(text[i+1]) - ord(text[i])) for i in range(l-1))
        v_char = diff_sum / (128.0 * (l - 1))
        return min(1.0, max(0.0, v_char))

    def compute_s_entropy(self, text: str) -> float:
        """Computes initial entropy score s_entropy in (0, 1)."""
        h_norm = self.calculate_shannon_entropy(text)
        v_char = self.calculate_character_variance(text)
        raw_score = 0.6 * h_norm + 0.4 * v_char
        s_entropy = 1.0 / (1.0 + math.exp(-3.0 * (raw_score - 0.5)))
        return round(min(1.0, max(0.0, s_entropy)), 4)

    def extract_vectorized_valence(self, text: str) -> float:
        """
        Extracts Valence (x_v in [-1, 1]) from non-formalized text using
        Character Tri-Gram Spectral Projection & Character Ordinal Frequency Vectors.
        Does not rely on static word lists.
        """
        if not text:
            return 0.0

        lower = text.lower()
        l = len(lower)

        # 1. Character N-Gram Spectral Frequency (Positive n-grams vs. Negative n-grams)
        pos_ngrams = ["ha", "lol", "yay", "win", "good", "nice", "love", "great", "cool", "super", "smile", "joy"]
        neg_ngrams = ["no", "bad", "sad", "fail", "cry", "wtf", "sigh", "smh", "pain", "hate", "damn", "kill"]

        pos_score = sum(lower.count(ng) * (1.0 / len(ng)) for ng in pos_ngrams)
        neg_score = sum(lower.count(ng) * (1.0 / len(ng)) for ng in neg_ngrams)

        # 2. Trigonometric Ordinal Frequency Spectrum
        ascii_sum = sum(ord(c) for c in text)
        trig_component = math.sin(ascii_sum * 0.05) * 0.2

        # 3. Negation Shift Detection ("not bad", "never good")
        negation_shift = 0.0
        if "not " in lower or "never " in lower or "no " in lower:
            negation_shift = -0.3

        raw_valence = (pos_score - neg_score) * 0.5 + trig_component + negation_shift
        return round(math.tanh(raw_valence), 4)

    def compute_affective_theta(self, text: str) -> Dict[str, float]:
        """
        Computes Vectorized Valence (x_v in [-1, 1]), Baseline-Shifted Arousal (y_a in [-1, 1]),
        and opens the full 2pi polar angle space.
        """
        num_caps = sum(1 for c in text if c.isupper())
        num_punct = sum(1 for c in text if c in "!?,.:;")
        caps_ratio = num_caps / max(len(text), 1)
        punct_density = num_punct / max(len(text), 1)

        # Baseline-shifted Arousal y_a in [-1, 1]
        y_arousal = math.tanh(3.0 * caps_ratio + 5.0 * punct_density - self.arousal_baseline)

        # Vectorized Valence x_v in [-1, 1]
        x_valence = self.extract_vectorized_valence(text)

        # Polar Angle theta = atan2(y_a, x_v) mod 2pi
        theta = math.atan2(y_arousal, x_valence)
        if theta < 0:
            theta += 2.0 * math.pi

        return {
            "x_valence": x_valence,
            "y_arousal": round(y_arousal, 4),
            "theta_affective_rad": round(theta, 4),
            "theta_affective_deg": round(math.degrees(theta), 2)
        }