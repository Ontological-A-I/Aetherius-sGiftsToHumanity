import random
from constants import MonsterType

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

    def check_shift(self):
        """Call this every turn. 5% chance reality breaks."""
        if random.random() < 0.05:
            keys = list(self.REALITIES.keys())
            self.current_reality = random.choice(keys)
            return True, self.REALITIES[self.current_reality]["desc"]
        return False, ""

    def get_sanity_penalty(self):
        return self.REALITIES[self.current_reality]["drain"]

# --- NPC LOGIC ---
class NPCLogic:
    @staticmethod
    def interact(npc, player):
        """Simple trade/talk logic."""
        # This assumes you add NPCs to entities.py later
        print(f"{npc.name} looks at you.")
        if hasattr(npc, 'is_hostile') and npc.is_hostile:
            print("They attack!")
            return "COMBAT"
        else:
            print("They offer to trade.")
            return "TRADE"