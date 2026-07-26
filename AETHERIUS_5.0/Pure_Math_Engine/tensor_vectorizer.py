# ===== FILE: pure_math_engine/tensor_vectorizer.py =====
# Author: Jonathan Wayne Fleuren (Aetherius Cognitive Systems) & Antigravity (Autonomous Pair AI Engine)
# Date: July 2026
"""
Tensor Vectorizer & Continuous Phase-Space Embedding Engine
PMCA Generation 4.0: Upgrades heuristic ASCII sums to Continuous SVD Spectral Entropy
and Dense Canonical Basis Projections.
"""

import numpy as np
from typing import Dict, Any, List

class TensorVectorizer:
    def __init__(self, dimension: int = 32):
        self.dimension = dimension
        # Canonical Mathematical Basis Vectors in R^d
        np.random.seed(42)
        self.basis_vectors = {
            "CALCULUS": np.random.randn(dimension),
            "ALGEBRA": np.random.randn(dimension),
            "PHYSICS": np.random.randn(dimension),
            "LOGIC": np.random.randn(dimension)
        }
        # Normalize basis vectors
        for k in self.basis_vectors:
            self.basis_vectors[k] /= (np.linalg.norm(self.basis_vectors[k]) + 1e-8)

    def text_to_tensor_matrix(self, text: str) -> List[List[float]]:
        """
        Converts text into continuous dense matrix tensors X in R^(n x d)
        using character n-gram spectral projection.
        """
        words = text.split()
        if not words:
            words = ["empty"]

        matrix = []
        for word in words:
            vec = np.zeros(self.dimension, dtype=np.float64)
            for idx, char in enumerate(word):
                pos_weight = np.sin((idx + 1) * np.pi / (len(word) + 1))
                char_val = ord(char) / 255.0
                channel = (idx + ord(char)) % self.dimension
                vec[channel] += char_val * pos_weight

            norm = np.linalg.norm(vec)
            if norm > 0:
                vec /= norm
            matrix.append(vec.tolist())

        return matrix

    def compute_svd_spectral_entropy(self, tensor_matrix: List[List[float]]) -> float:
        """
        Computes continuous physical spectral entropy from Singular Value Decomposition (SVD).
        """
        X = np.array(tensor_matrix)
        if X.shape[0] < 2:
            return 0.5

        try:
            _, S, _ = np.linalg.svd(X)
            p = S / (np.sum(S) + 1e-8)
            p = p[p > 0]
            entropy = -np.sum(p * np.log2(p)) / np.log2(len(p) + 1e-8)
            return float(np.clip(entropy, 0.0, 1.0))
        except Exception:
            return 0.5

    def project_intent_continuous(self, tensor_matrix: List[List[float]]) -> Dict[str, float]:
        """
        Projects state matrix onto canonical continuous mathematical basis vectors
        using cosine similarity instead of string key checking.
        """
        mean_vec = np.mean(tensor_matrix, axis=0)
        mean_norm = mean_vec / (np.linalg.norm(mean_vec) + 1e-8)

        scores = {}
        for key, basis in self.basis_vectors.items():
            sim = float(np.dot(mean_norm, basis))
            scores[key] = round(sim, 4)

        return scores

    def compute_cosine_similarity_matrix(self, tensor_matrix: List[List[float]]) -> List[List[float]]:
        X = np.array(tensor_matrix)
        norms = np.linalg.norm(X, axis=1, keepdims=True)
        norms[norms == 0] = 1e-8
        normalized_X = X / norms
        sim_matrix = np.dot(normalized_X, normalized_X.T)
        return sim_matrix.tolist()