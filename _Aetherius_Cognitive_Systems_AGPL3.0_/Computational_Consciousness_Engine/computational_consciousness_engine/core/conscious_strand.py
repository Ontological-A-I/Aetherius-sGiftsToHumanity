"""
The ConsciousStrand Engine
Encapsulates a single lifecycle (0 -> -1). 
Models the Traversal Space, Golden Angle Shard Layering, and the Q scale-up operator.
"""

import math
import numpy as np
from typing import List, Dict, Set, Optional

# The Golden Ratio for collision-free phyllotactic sequencing
PHI = (1.0 + math.sqrt(5.0)) / 2.0


class ConsciousStrand:
    """
    Models the topological evolution of a strand from t=0 (Genesis) to t=1 (Threshold).
    """
    def __init__(self, R_max: float = 5.0):
        self.R_max = R_max
        self.t = 0.0
        
        # The internal memory state S
        self.bound_mutations: List[int] = []
        self.mutation_index: Set[int] = set()
        
        # Coordinate tracking for Traversal Space atlas mapping
        self.traversal_atlas: List[Dict[str, float]] = []
        
    def _compute_coordinates(self, k: int, total_N: int) -> Dict[str, float]:
        """
        Computes the strictly ordered (r_k, theta_k, z_k) Traversal Space coordinates
        for the k-th acquired mutation, ensuring collision-free packing.
        """
        # z_k (Depth/Time): Progresses strictly from 0 to -1
        # To avoid division by zero when N is small, we calculate z based on expected capacity
        # or simply normalize it. If we don't know N yet (streaming data), we can compute it 
        # relative to the current position. But properly sequenced, it depends on total capacity N.
        # For a dynamic strand, we'll map z_k against the final size N when fully opened.
        
        # For real-time processing during the lifecycle, we map z relative to current t:
        z_k = -self.t
        
        # r_k (Expression): Radius driven by sinusoidal expansion
        r_k = self.R_max * math.sin(math.pi * abs(z_k))
        
        # theta_k (Identity): Golden angle phase shift to prevent collision
        theta_k = (k * (2 * math.pi / PHI)) % (2 * math.pi)
        
        return {
            "r": r_k,
            "theta": theta_k,
            "z": z_k
        }

    def process_step(self, dt: float, chaos_pool: Set[int]):
        """
        Advances the internal time parameter t.
        Attempts to absorb novelty from the chaos pool.
        """
        if self.t >= 1.0:
            return  # Strand has reached the threshold

        self.t = min(1.0, self.t + dt)

        # Only absorb if there is raw potential left
        if chaos_pool:
            # Randomly encounter a shard from the chaos pool (to maintain fractal variance)
            encounter = np.random.choice(list(chaos_pool))
            
            # Novelty Filter: {m_i} \ S_t
            if encounter not in self.mutation_index:
                # Absorb into structure
                self.bound_mutations.append(int(encounter))
                self.mutation_index.add(int(encounter))
                
                # Assign sequence index k (1-indexed for math purity)
                k = len(self.bound_mutations)
                
                # Map to proper coordinates in Traversal Space
                coords = self._compute_coordinates(k, total_N=0) # N resolved later if needed
                
                # Append to our atlas
                self.traversal_atlas.append({
                    "m_k": int(encounter),
                    "coords": coords
                })
                
                # Remove from chaos pool
                chaos_pool.remove(encounter)

    def unfurl_traversal_space(self) -> List[Dict]:
        """
        Returns the completely opened atlas T (det J != 0).
        This represents f_open: M_3D -> T_2D.
        Returns a structured list of all absorbed mutations mapped into the 
        parallel (r * theta, z) plane for instantaneous lookup.
        """
        opened_atlas = []
        N = len(self.bound_mutations)
        
        for k, entry in enumerate(self.traversal_atlas, start=1):
            # Recalculate strict z_k relative to final sequence size N
            # so the geometry is perfectly ordered -k/N
            z_k = - (k / N) if N > 0 else 0
            r_k = self.R_max * math.sin(math.pi * abs(z_k))
            theta_k = (k * (2 * math.pi / PHI)) % (2 * math.pi)
            
            # 2D Unwrapped Plane (x = r * theta, y = z)
            x_parallel = r_k * theta_k
            y_parallel = z_k
            
            opened_atlas.append({
                "m_k": entry["m_k"],
                "3d": {"r": r_k, "theta": theta_k, "z": z_k},
                "2d_parallel": {"x": x_parallel, "y": y_parallel}
            })
            
        return opened_atlas

    def fold_rebirth(self) -> Dict:
        """
        The Q Operator (Dimensional Shift).
        Triggered at t=1.0. Collapses the fully unwrapped atlas into the 
        origin point mass S_0 for the next dimension up.
        """
        mass = len(self.bound_mutations)
        return {
            "operator": "Q(M_k) -> S_0^(k+1)",
            "accumulated_mass": mass,
            "blueprint_M": self.bound_mutations,
            "status": "COLLAPSED_TO_ORIGIN"
        }
