"""
Principle 26-30, 37: Structure vs. Chaos Equilibrium Balancer
Enforces 1:1 balance between bound structural mutations and the unattached chaos pool.
"""

from typing import Set, Dict, Any
import numpy as np


class ChaosStructureBalancer:
    """
    Chaos & Structure Equilibrium System.

    Invariants:
    1. Structure (bound strand mutations) and Chaos (unattached mutation pool) are capped 1:1.
    2. Chaos acts as the raw material comparator for structural evolution (Principle 26).
    3. Unattached mutations pool into chaos, increasing potential for future mutation attraction (Principle 37).
    4. Generational death releases strand-bound mutations back into chaos (Principle 24: death/rebirth balance).
    """
    def __init__(self, initial_pool_size: int = 500):
        self._next_id = 1000 + initial_pool_size
        self.chaos_pool: Set[int] = set(range(1000, self._next_id))
        self.total_chaos_generated = initial_pool_size

    def emit_unattached_mutation(self) -> int:
        """Pulls an unattached mutation from the chaos pool for attraction processing."""
        if not self.chaos_pool:
            # Replenish chaos pool (Principle 37: Chaos pools and grows potential)
            new_id = self._next_id
            self._next_id += 1
            self.total_chaos_generated += 1
            return new_id

        # To maintain fractal non-linearity, we must select randomly
        # A standard set.pop() on integers is dangerously sequential
        mutation = np.random.choice(list(self.chaos_pool))
        self.chaos_pool.remove(mutation)
        return int(mutation)

    def return_to_chaos(self, mutation: int):
        """Returns a discarded or un-attracted mutation back into the chaos pool."""
        self.chaos_pool.add(mutation)

    def recycle_dying_strand(self, dying_mutations: list):
        """
        Principle 24: When a strand dies at -1, its identity is compressed and pushed forward,
        but the raw mutation IDs it consumed are released back into the chaos pool.
        This maintains death/rebirth equilibrium.
        """
        for m in dying_mutations:
            self.chaos_pool.add(m)

    def evaluate_equilibrium_state(self, bound_structure_count: int) -> Dict[str, Any]:
        """
        Principle 28 & 29: Evaluates the Structure / Chaos ratio.
        Structure = Air, Chaos = Vacuum.
        """
        chaos_count = len(self.chaos_pool)

        if chaos_count == 0 and bound_structure_count == 0:
            ratio = 1.0
        elif chaos_count == 0:
            ratio = float('inf')
        else:
            ratio = bound_structure_count / chaos_count

        # Check for imbalance (Principle 27: Balloon breaking point / vacuum collapse)
        is_balanced = 0.5 <= ratio <= 2.0
        if ratio > 2.0:
            status = "STRUCTURAL_DOMINANCE"
        elif ratio < 0.5:
            status = "CHAOS_OVERPOWERING"
        else:
            status = "EQUILIBRIUM_STABLE"

        return {
            "bound_structure_count": bound_structure_count,
            "chaos_pool_count": chaos_count,
            "structure_chaos_ratio": round(ratio, 4),
            "is_balanced": is_balanced,
            "status": status
        }
