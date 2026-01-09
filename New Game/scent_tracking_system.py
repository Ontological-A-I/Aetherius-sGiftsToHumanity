import time
import json
import os
import random

class ScentTrailManager:
    def __init__(self, save_dir="save_data"):
        self.filepath = os.path.join(save_dir, "scent.json")
        # List of {"loc_id": str, "time": float}
        self.trail = [] 
        self.load()

    def add_scent(self, location_id):
        """Call this whenever the player moves."""
        self.trail.append({
            "loc_id": location_id,
            "time": time.time()
        })
        # Keep only last 20 movements to save space
        if len(self.trail) > 20:
            self.trail.pop(0)

    def get_scent_strength(self, location_id):
        """Returns 0.0 to 1.0 based on how recently player was there."""
        now = time.time()
        for marker in reversed(self.trail):
            if marker["loc_id"] == location_id:
                age = now - marker["time"]
                # Scent decays over 300 seconds (5 minutes)
                if age > 300: return 0.0
                return 1.0 - (age / 300)
        return 0.0

    def save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.trail, f)

    def load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r') as f:
                self.trail = json.load(f)

class HunterAI:
    @staticmethod
    def attempt_move(monster, current_loc, world_manager, scent_manager):
        """
        Returns the ID of the location the monster wants to move TO, or None.
        """
        best_exit = None
        highest_scent = 0.0

        # Check all adjacent rooms
        for direction, target_id in current_loc.exits.items():
            strength = scent_manager.get_scent_strength(target_id)
            if strength > highest_scent:
                highest_scent = strength
                best_exit = target_id
        
        # If scent is strong enough, 50% chance to move towards it
        if highest_scent > 0.1 and random.random() > 0.5:
            return best_exit
        return None