# --- START OF FILE combat_pattern_recognition.py ---

import json
import os

class CombatTacticsEngine:
    def __init__(self, save_dir):
        self.save_dir = save_dir
        self.filepath = os.path.join(self.save_dir, "tactics.json")
        self.history = {
            "head": 0, "torso": 0, "legs": 0, "arms": 0
        }
        self.load()

    def record_attack(self, target_part_name):
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
        if total == 0: return 1.0 
        if total < 5: return 1.0 # Not enough data yet

        key = "torso"
        if not target_part_name:
            key = "torso"
        elif "head" in target_part_name: key = "head"
        elif "leg" in target_part_name: key = "legs"
        elif "arm" in target_part_name: key = "arms"

        ratio = self.history.get(key, 0) / total
        
        # If you spam the same spot (>40%), damage is halved
        if ratio > 0.4:
            return 0.5 
        elif ratio > 0.25:
            return 0.8 
        
        return 1.0 

    def save(self):
        if not os.path.exists(os.path.dirname(self.filepath)):
            os.makedirs(os.path.dirname(self.filepath))
        with open(self.filepath, 'w') as f:
            json.dump(self.history, f)

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    self.history = json.load(f)
            except (json.JSONDecodeError, OSError):
                # Reset if file is corrupted
                self.history = {"head": 0, "torso": 0, "legs": 0, "arms": 0}

    def get_boss_adaptation(self, target_part):
        """Boss-level adaptation: 90% reduction if you are predictable."""
        total = sum(self.history.values())
        if total == 0: return 1.0 
        if total < 3: return 1.0
        
        # Normalize input
        key = target_part
        if "leg" in target_part: key = "legs"
        elif "arm" in target_part: key = "arms"

        ratio = self.history.get(key, 0) / total
        if ratio > 0.3: 
            print("The Stalker mimics your stance perfectly. Your strike is useless!")
            return 0.1 
        return 1.0
# --- END OF FILE combat_pattern_recognition.py ---