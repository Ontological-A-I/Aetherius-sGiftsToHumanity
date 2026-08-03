"""
Principle 5, 11, 12, 18, 20: Non-Linear M-String Mutation & Selection Engine
Implements non-sequential fractal M-strings and selection as duplicate removal.
"""

from typing import List, Set, Dict, Any
import numpy as np


class MStringVectorizer:
    """
    Non-Linear M-String & Selection Engine.

    Key Logic:
    1. M-Strings connect non-sequentially (fractal connectivity: M1 -> M124 -> M3956).
    2. Selection is strictly the REMOVAL of already-present mutations (Principle 12).
    3. Prevents duplicate attraction to enforce system stability and prevent chaotic collapse (Principle 18).
    """
    def __init__(self, max_strand_capacity: int = 500):
        self.max_capacity = max_strand_capacity

    def apply_selection(self, existing_mutations: List[int], incoming_mutations: List[int]) -> List[int]:
        """
        Principle 12: Selection is removing what is already there.
        Eliminates duplicate mutations to prevent incoherence and system destruction.
        """
        existing_set = set(existing_mutations)
        cleaned_incoming = [m for m in incoming_mutations if m not in existing_set]

        # Deduplicate incoming while preserving order
        seen: Set[int] = set()
        unique_cleaned: List[int] = []
        for m in cleaned_incoming:
            if m not in seen:
                seen.add(m)
                unique_cleaned.append(m)

        return existing_mutations + unique_cleaned

    def attract_mutation(self, strand: Dict[str, Any], candidate_mutation: int) -> bool:
        """
        Principle 5 & 18: Non-sequential fractal attraction.
        If candidate mutation is ALREADY present or strand capacity is reached, attraction is blocked.
        Uses a set index for O(1) duplicate checks.
        """
        existing = strand["mutations"]

        # Principle 18: Evolution ceiling / halting condition
        if len(existing) >= self.max_capacity:
            return False  # Capacity ceiling reached

        # Use the set index for O(1) lookup instead of O(n) list scan
        mutation_index: set = strand.setdefault("_mutation_index", set(existing))

        if candidate_mutation in mutation_index:
            return False  # Duplicate mutation blocked by selection

        # Non-linear fractal connection
        existing.append(candidate_mutation)
        mutation_index.add(candidate_mutation)
        return True

    def compute_causal_connectivity_metric(self, strand: Dict[str, Any]) -> float:
        """
        Principle 5: Causal metric is the degree of any-value connectivity retained at tip-to-tip handoff.
        Higher variance between consecutive mutation values = more fractal, non-linear connectivity.
        """
        mutations = strand["mutations"]
        if len(mutations) < 2:
            return 1.0

        # Measures fractal variance between consecutive mutation values
        diffs = [abs(mutations[i + 1] - mutations[i]) for i in range(len(mutations) - 1)]
        causal_metric = float(np.std(diffs)) if diffs else 0.0
        return causal_metric
