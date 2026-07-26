# ===== FILE: pure_math_engine/external_conal_casing.py =====
# Author: Jonathan Wayne Fleuren (Aetherius Cognitive Systems) & Antigravity (Autonomous Pair AI Engine)
# Date: July 2026
"""
External Conal Casing — 3D Vectorized Encasing Structures
Defines the external 3D vector shell encasing the inner cone pathway,
providing spatial boundary metrics, outer memory lattices, and field induction forces F_ext.
"""

import math
from typing import List, Dict, Any

class ExternalVectorStructure:
    def __init__(self, z_max: float = 10.0, inner_radius: float = 5.0, shell_thickness: float = 2.0):
        self.z_max = z_max
        self.inner_radius = inner_radius
        self.shell_thickness = shell_thickness
        self.lattice_vertices = self._build_outer_lattice()

    def _build_outer_lattice(self) -> List[Dict[str, float]]:
        """Constructs 3D spatial vector lattice points encasing the cone."""
        vertices = []
        steps_z = 8
        steps_theta = 12

        for i in range(steps_z):
            z = (i / steps_z) * self.z_max
            r_inner = self.inner_radius * (1.0 - 0.8 * (z / self.z_max))
            r_outer = r_inner + self.shell_thickness

            for j in range(steps_theta):
                theta = (2.0 * math.pi * j) / steps_theta
                x = r_outer * math.cos(theta)
                y = r_outer * math.sin(theta)
                vertices.append({
                    "x": round(x, 4),
                    "y": round(y, 4),
                    "z": round(z, 4),
                    "r": round(r_outer, 4),
                    "theta": round(theta, 4)
                })
        return vertices

    def compute_field_induction(self, point_pos: Dict[str, float]) -> Dict[str, float]:
        """
        Calculates inward 3D vector field induction force F_ext acting on an inner data point.
        F_ext = sum( (v_k - p_i) / ||v_k - p_i||^2 )
        """
        px, py, pz = point_pos.get("x", 0.0), point_pos.get("y", 0.0), point_pos.get("z", 0.0)
        fx, fy, fz = 0.0, 0.0, 0.0

        for v in self.lattice_vertices:
            dx = v["x"] - px
            dy = v["y"] - py
            dz = v["z"] - pz
            dist_sq = dx*dx + dy*dy + dz*dz + 1e-4

            fx += dx / dist_sq
            fy += dy / dist_sq
            fz += dz / dist_sq

        mag = math.sqrt(fx*fx + fy*fy + fz*fz)
        return {
            "fx": round(fx, 6),
            "fy": round(fy, 6),
            "fz": round(fz, 6),
            "magnitude": round(mag, 6)
        }