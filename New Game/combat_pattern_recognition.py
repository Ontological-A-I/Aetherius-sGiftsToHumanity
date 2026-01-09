# START OF FILE combat_pattern_recognition.py ---

import json
import os
# CHANGED: Import from entities, not constants
from entities import BodyPartStatus 

class CombatTacticsEngine:
    def __init__(self, save_dir="save_data"):
        self.filepath = os.path.join(save_dir, "tactics.json")
        # Counts how many times player hit specific parts
        self.history = {
            "head": 0, "torso": 0, "legs": 0, "arms": 0
        }
        self.load()

    def record_attack(self, target_part_name):
        """Call this when player attacks. Normalizes 'left arm' to 'arms'."""
        key = "torso" # Default
        if not target_part_name:
            key = "torso"
        elif "head" in target_part_name: key = "head"
        elif "leg" in target_part_name: key = "legs"
        elif "arm" in target_part_name: key = "arms"
        
        self.history[key] = self.history.get(key, 0) + 1

    def get_adaptation_penalty(self, target_part_name):
        """Returns a damage reduction multiplier (0.0 to 1.0)."""
        total = sum(self.history.values())
        if total < 5: return 1.0 # Not enough data yet

        key = "torso"
        if not target_part_name:
            key = "torso"
        elif "head" in target_part_name: key = "head"
        elif "leg" in target_part_name: key = "legs"
        elif "arm" in target_part_name: key = "arms"

        ratio = self.history.get(key, 0) / total
        
        # If player targets this part > 40% of the time, monsters adapt
        if ratio > 0.4:
            return 0.5 # 50% damage reduction (Blocked!)
        elif ratio > 0.25:
            return 0.8 # 20% reduction (Glancing hit)
        
        return 1.0 # Full damage

    def save(self):
        if not os.path.exists(os.path.dirname(self.filepath)):
            os.makedirs(os.path.dirname(self.filepath))
        with open(self.filepath, 'w') as f:
            json.dump(self.history, f)

    def load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r') as f:
                self.history = json.load(f)