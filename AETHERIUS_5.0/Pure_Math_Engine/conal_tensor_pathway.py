# ===== FILE: pure_math_engine/conal_tensor_pathway.py =====
# Author: Jonathan Wayne Fleuren (Aetherius Cognitive Systems) & Antigravity (Autonomous Pair AI Engine)
# Date: July 2026
"""
Conal Tensor Pathway — Spatial 3D Metric Geometry & Encasing Field Engine
Transforms matrix tensors X down a 3D conical geometry (z, r, theta) while subjected to
inward 3D vector field induction forces F_ext from the encasing external vector structure.
"""

import math
from typing import List, Dict, Any
from .external_conal_casing import ExternalVectorStructure

class ConalTensorPathway:
    def __init__(self, z_max: float = 10.0, base_radius: float = 5.0):
        self.z_max = z_max
        self.base_radius = base_radius
        self.external_casing = ExternalVectorStructure(z_max=z_max, inner_radius=base_radius, shell_thickness=2.0)

    def get_cone_radius(self, z: float) -> float:
        """Calculates cone radius r(z) tapering from base_radius at z=0 to r_min at z=z_max."""
        alpha = 0.8
        r = self.base_radius * (1.0 - alpha * (z / self.z_max))
        return max(r, 0.1)

    def process_conal_transform(self, matrix: List[List[float]], z_depth: float) -> Dict[str, Any]:
        """
        Applies 3D spatial metric tensor transformation AND encasing field induction F_ext.
        """
        r = self.get_cone_radius(z_depth)
        scaled_matrix = []

        # Sample field induction force at current z depth
        field_induction = self.external_casing.compute_field_induction({"x": 0.0, "y": 0.0, "z": z_depth})

        for i, row in enumerate(matrix):
            theta = (2.0 * math.pi * i) / max(len(matrix), 1)
            scaled_row = []
            for j, val in enumerate(row):
                # Combined metric tensor scaling + external field induction component
                induction_factor = 1.0 + 0.1 * field_induction["magnitude"]
                metric_factor = r * math.cos(theta + j * 0.1) * (1.0 / (z_depth + 1.0)) * induction_factor
                scaled_row.append(round(val * metric_factor, 6))
            scaled_matrix.append(scaled_row)

        tensor_norm = sum(sum(v * v for v in r_row) for r_row in scaled_matrix)
        trace_invariant = sum(scaled_matrix[i][i % len(scaled_matrix[0])] for i in range(len(scaled_matrix)))

        return {
            "z_depth": z_depth,
            "radius_r": round(r, 4),
            "external_field_induction": field_induction,
            "transformed_tensor": scaled_matrix,
            "tensor_norm": round(tensor_norm, 6),
            "trace_invariant": round(trace_invariant, 6)
        }