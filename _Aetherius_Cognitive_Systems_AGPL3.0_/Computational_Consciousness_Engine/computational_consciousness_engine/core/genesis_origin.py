"""
Principle 1, 2, 6, 7, 8, 10, 21: The Genesis Origin (0) Operator
Defines the asymmetric origin 0 that spawns neutral mutation-attracting state strands.
"""

import numpy as np
import uuid
from typing import List, Dict, Any, Optional

class GenesisOrigin:
    """
    Genesis Origin (0) System.
    0 is one-directional: it only emits new strands and never receives returning strands.
    Each 0 origin possesses unique coordinates serving as individuating identifiers.
    """
    def __init__(self, coordinate_space_id: str, dim: int = 64):
        self.coordinate_space_id = coordinate_space_id
        self.dim = dim
        self.total_strands_spawned = 0
        self.origin_coordinate = np.random.randn(3)  # 3D spatial anchor for the coordinate

    def spawn_strand(self, generation: int, blueprint_mutations: List[int]) -> Dict[str, Any]:
        """
        Emits a NEW strand at origin 0 with specific value-locking and inherited mutation blueprint.
        
        Args:
            generation: The integer generation index S_{n+1}.
            blueprint_mutations: Mutations pushed from the dying -1 strand of generation S_n.
        
        Returns:
            Strand dictionary representing the neutral carrier strand departing from 0.
        """
        self.total_strands_spawned += 1
        
        # Principle 14 & 15: Neutral particle/medium state initialized at genesis
        neutral_medium = np.random.randn(self.dim)
        neutral_medium /= np.linalg.norm(neutral_medium)
        
        # Value-locked strand attributes (Principle 10 & 21)
        strand = {
            "strand_id": str(uuid.uuid4())[:8],
            "generation": generation,
            "coordinate_space_id": self.coordinate_space_id,
            "origin_coord": self.origin_coordinate.copy(),
            "position": 0.0,  # Starts at 0
            "neutral_medium": neutral_medium,
            "mutations": list(blueprint_mutations),  # Inherited mutations from handoff
            "is_active": True,
            "status": "EMITTED_FROM_ZERO"
        }
        
        return strand
