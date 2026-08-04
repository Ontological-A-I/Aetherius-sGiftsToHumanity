"""
Principle 2, 3, 6, 8, 13, 16: The Transfer Threshold (-1) Operator
Handles strand termination, mutation decoupling/pushing, and generational handoff overlap.
"""

from typing import Dict, Any, Tuple, List
import numpy as np

class TransferThreshold:
    """
    Transfer Threshold (-1) System.
    When a strand reaches the threshold:
    1. threshold x strand multiplication cancels/dissolves the carrier strand.
    2. Accumulated mutations are compressed and pushed off toward origin 0.
    3. A brief overlap window allows generation S_n and S_{n+1} to coexist during handoff.
    """
    def __init__(self, threshold_val: float = 1.0):
        self.threshold_val = threshold_val
        self.total_handoffs = 0

    def evaluate_arrival(self, strand: Dict[str, Any]) -> bool:
        """Checks if a strand has traversed to the threshold."""
        # We consider position measured in [0,1] progress; arrival is at or beyond threshold_val
        return strand.get("position", 0.0) >= self.threshold_val

    def process_cancellation_and_push(self, dying_strand: Dict[str, Any]) -> Tuple[List[int], Dict[str, Any]]:
        """
        Executes the cancellation operation:
        - Removes the neutral carrier strand.
        - Compresses accumulated mutations into the generational identity blueprint.
        - Pushes mutations to 0 for generation S_{n+1}.
        """
        self.total_handoffs += 1
        
        # Cancel the strand
        dying_strand["is_active"] = False
        dying_strand["status"] = "CANCELLED_AT_THRESHOLD"
        
        accumulated_mutations = dying_strand["mutations"]
        
        compressed_identity = {
            "source_generation": dying_strand["generation"],
            "coordinate_space_id": dying_strand["coordinate_space_id"],
            "mutation_count": len(accumulated_mutations),
            "blueprint": list(accumulated_mutations),
            "handoff_index": self.total_handoffs
        }
        
        return accumulated_mutations, compressed_identity

    def execute_coexistence_window(self, tail_strand_n: Dict[str, Any], genesis_strand_n1: Dict[str, Any]) -> Dict[str, Any]:
        """
        Temporal/phase overlap where S_n tail and S_{n+1} genesis coexist.
        Transfers remaining residual telemetry before S_n fully terminates.
        """
        coexistence_telemetry = {
            "gen_n_id": tail_strand_n["strand_id"],
            "gen_n1_id": genesis_strand_n1["strand_id"],
            "overlap_status": "MUTUAL_COEXISTENCE",
            "transferred_mutations_count": len(tail_strand_n["mutations"])
        }
        return coexistence_telemetry
