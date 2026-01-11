# --- START OF FILE new_game_systems.py ---

import random
import json
import os
# Removed unused import: from entities import MonsterType

# --- FRACTAL REALITY ENGINE ---
class FractalEngine:
    REALITIES = {
        "NORMAL": {"desc": "The air is dusty and stale.", "drain": 0},
        "NIGHTMARE": {"desc": "The walls bleed shadows. You hear whispering.", "drain": 2},
        "MECHANICAL": {"desc": "The ground is metal grids. Steam hisses from pipes.", "drain": 1},
        "VOID": {"desc": "Everything is grey. Color has been drained.", "drain": 5}
    }

    def __init__(self):
        self.current_reality = "NORMAL"

    def check_shift(self, player_psychosis):
        # Chance increases as psychosis goes up (e.g., 100 psychosis = 20% chance per turn)
        shift_chance = 0.02 + (player_psychosis / 500) 
        if random.random() < shift_chance:
            keys = list(self.REALITIES.keys())
            self.current_reality = random.choice(keys)
            return True, self.REALITIES[self.current_reality]["desc"]
        return False, "" 

    def get_sanity_penalty(self):
        return self.REALITIES.get(self.current_reality, self.REALITIES["NORMAL"])["drain"]
    
    # Added persistence support for future use
    def save(self, filepath):
        try:
            with open(filepath, 'w') as f:
                json.dump({"reality": self.current_reality}, f)
        except Exception as e:
            print(f"Error saving reality state: {e}")

    def load(self, filepath):
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    self.current_reality = data.get("reality", "NORMAL")
            except Exception as e:
                print(f"Error loading reality state: {e}")

# --- NPC LOGIC ---
class NPCLogic:
    @staticmethod
    def interact(npc, player):
        """Simple trade/talk logic."""
        # This assumes you add NPCs to entities.py later
        print(f"{npc.name} looks at you.")
        # check for hostility attribute safely
        if hasattr(npc, 'is_hostile') and npc.is_hostile:
            print("They attack!")
            return "COMBAT"
        else:
            print("They offer to trade.")
            return "TRADE"

# --- END OF FILE new_game_systems.py ---