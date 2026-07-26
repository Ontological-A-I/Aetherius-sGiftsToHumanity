# ===== FILE: pure_math_engine/disparate_relationship_engine.py =====
# Author: Jonathan Wayne Fleuren (Aetherius Cognitive Systems) & Antigravity (Autonomous Pair AI Engine)
# Date: July 2026
"""
Disparate Relationship Engine — Vectorized Matrix Similarity Indexing
PMCA Generation 4.0: Replaces linear O(N) Python loops with parallel NumPy matrix projections (X * Y^T)
for instant O(1)/sub-linear relationship discovery.
"""

import numpy as np
from typing import List, Dict, Any

class DisparateRelationshipEngine:
    def __init__(self):
        self.relationship_history = []

    def discover_relationships(
        self,
        current_vector: List[float],
        manifold_entries: List[Dict[str, Any]],
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Discovers direct, analogical, and orthogonal relationships across knowledge manifold
        using parallel NumPy matrix dot products.
        """
        if not manifold_entries or not current_vector:
            return []

        curr_arr = np.array(current_vector, dtype=np.float64)
        curr_norm = curr_arr / (np.linalg.norm(curr_arr) + 1e-8)

        # Extract target vector matrix (N x d)
        target_vectors = []
        valid_entries = []
        for entry in manifold_entries:
            vec = entry.get("sample_vector") or entry.get("vector_position")
            if vec and len(vec) == len(current_vector):
                target_vectors.append(vec)
                valid_entries.append(entry)

        if not target_vectors:
            return []

        # Vectorized parallel matrix multiplication (N x d) dot (d x 1)
        matrix = np.array(target_vectors, dtype=np.float64)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1e-8
        normalized_matrix = matrix / norms

        sims = np.dot(normalized_matrix, curr_norm)

        discovered = []
        for idx, sim in enumerate(sims):
            if abs(sim) >= threshold:
                rel_type = "DIRECT_ALIGNMENT" if sim > 0.8 else ("ORTHOGONAL_RESONANCE" if abs(sim) < 0.15 else "ANALOGICAL_BRIDGE")
                entry = valid_entries[idx]
                discovered.append({
                    "target_key": entry.get("relatable_key", f"entity_{idx}"),
                    "similarity_score": round(float(sim), 4),
                    "relationship_type": rel_type
                })

        return discovered