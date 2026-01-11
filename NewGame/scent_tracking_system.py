# --- START OF FILE scent_tracking_system.py ---

import json
import os
import random

class ScentTrailManager:
    def __init__(self, save_dir):
        self.save_dir = save_dir
        self.filepath = os.path.join(self.save_dir, "scent.json")
        # List of {"loc_id": str} (Ordered from oldest to newest)
        self.trail = [] 
        self.load()

    def add_scent(self, location_id):
        """Call this whenever the player moves."""
        self.trail.append({
            "loc_id": location_id
        })
        # Keep only last 20 movements to save space
        if len(self.trail) > 20:
            self.trail.pop(0)

    def get_scent_strength(self, location_id):
        """
        Returns 0.0 to 1.0 based on how recently player was there.
        Uses step distance rather than real time so it works across saves.
        """
        # Iterate backwards (newest first)
        # i=0 is current location (1.0 strength)
        # i=1 is previous location (0.95 strength), etc.
        decay_per_step = 0.05
        
        for i, marker in enumerate(reversed(self.trail)):
            if marker["loc_id"] == location_id:
                strength = 1.0 - (i * decay_per_step)
                return max(0.0, strength)
        return 0.0

    def save(self):
        # FIX: Ensure directory exists (redundant safety)
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir, exist_ok=True)
            
        with open(self.filepath, 'w') as f:
            json.dump(self.trail, f)

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    self.trail = json.load(f)
            except (json.JSONDecodeError, OSError):
                print("Warning: Scent file corrupted or unreadable. Resetting scent.")
                self.trail = []

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
        # (Monsters are erratic)
        if highest_scent > 0.1 and random.random() > 0.5:
            return best_exit
        return None

# --- END OF FILE scent_tracking_system.py ---