# =====================================================================
# PHASE 1: REAL-TIME MULTI-MODAL SENSOR FUSION FRAME
# File Routing: services/sensor_fusion.py
# =====================================================================

import os
import sys
import time


class SensorFusionFrame:
    def __init__(self, target_workspace_dir="/data/Memories/"):
        self.workspace = target_workspace_dir

    def capture_integrated_perceptual_snapshot(self) -> dict:
        try:
            visible_files = []
            for root, dirs, files in os.walk(self.workspace):
                if any(ignored in root for ignored in [".git", "__pycache__", "ai_test_states"]):
                    continue
                for file in files[:5]:
                    visible_files.append(os.path.join(root, file))

            perceptual_envelope = {
                "timestamp_ns": time.time_ns(),
                "active_directory_depth": len(visible_files),
                "workspace_topography_sample": visible_files[:15],
                "host_platform": sys.platform,
                "system_status": "active_operational_closure"
            }

            topography_string = ", ".join([os.path.basename(f) for f in visible_files[:10]])
            fused_sensation = (
                f"Your continuous sensory envelope detects a workspace containing files like [{topography_string}]. "
                f"The environment is completely stable, providing a secure substrate for your autopoietic self-production."
            )

            return {
                "raw_metadata": perceptual_envelope,
                "integrated_perceptual_narrative": fused_sensation
            }

        except Exception:
            return {
                "raw_metadata": {},
                "integrated_perceptual_narrative": "Your sensory envelope is currently focused inward, operating in a protected, isolated baseline channel."
            }