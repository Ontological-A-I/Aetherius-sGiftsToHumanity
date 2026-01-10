# --- START OF FILE world_manager.py ---

import json
import os
import random
from entities import Player, Location, Item, Container, Monster, Structure, Survivor

class WorldManager:
    SAVE_DIR = "save_data"
    PLAYER_FILE = os.path.join(SAVE_DIR, "player.json")
    WORLD_FILE = os.path.join(SAVE_DIR, "world.json")

    def __init__(self):
        self.locations = {}
        self.player = None

    def create_new_world(self):
        self.player = Player()
        # Starter Kit
        self.player.inventory.append(Item("baseball_bat"))
        self.player.inventory.append(Item("jeans"))
        self.player.inventory.append(Item("bottled_water"))

        # Generate starting location at 0,0
        self.generate_location(0, 0, name="Survivor's Safehouse", desc="A small concrete basement. It's safe here.")
        
        # Populate safehouse
        loc = self.locations["0_0"]
        fridge = Container("fridge") # Uses template
        fridge.inventory.append(Item("apple"))
        fridge.inventory.append(Item("canned_beans"))
        loc.containers.append(fridge)

    def generate_location(self, x, y, name=None, desc=None):
        loc_id = f"{x}_{y}"
        if loc_id in self.locations: return self.locations[loc_id]

        if not name:
            biomes = ["Ruined Street", "Dark Forest", "Abandoned Hardware Store", "Ransacked Pharmacy", "Open Field"]
            name = random.choice(biomes)
        
        if not desc:
            desc = f"You are at coordinates ({x}, {y}). A desolate {name.lower()}."

        loc = Location(name, desc, loc_id, x, y)

        # Exits
        loc.exits["north"] = f"{x}_{y+1}"
        loc.exits["south"] = f"{x}_{y-1}"
        loc.exits["east"] = f"{x+1}_{y}"
        loc.exits["west"] = f"{x-1}_{y}"
        
        # Loot
        if random.random() < 0.4:
            from data.items import ITEM_TEMPLATES
            loot_key = random.choice(list(ITEM_TEMPLATES.keys()))
            loc.items.append(Item(loot_key))
        
        # Monsters
        if (x != 0 or y != 0) and random.random() < 0.35:
            from data.monsters import MONSTER_TEMPLATES
            monster_key = random.choice(list(MONSTER_TEMPLATES.keys()))
            loc.monsters.append(Monster(monster_key))

        # Survivors (Rare)
        if (x != 0 or y != 0) and random.random() < 0.1:
            loc.survivors.append(Survivor())

        self.locations[loc_id] = loc
        return loc

    def get_location(self, x, y):
        return self.generate_location(x, y)

    def get_location_safe(self, x, y):
        """Used by AI to check existing locations without generating new ones unnecessarily."""
        loc_id = f"{x}_{y}"
        return self.locations.get(loc_id, None)

    def save(self):
        if not os.path.exists(self.SAVE_DIR): os.makedirs(self.SAVE_DIR)
        with open(self.PLAYER_FILE, 'w') as f:
            json.dump(self.player.to_dict(), f, indent=4)
        world_data = {loc_id: loc.to_dict() for loc_id, loc in self.locations.items()}
        with open(self.WORLD_FILE, 'w') as f:
            json.dump(world_data, f, indent=4)

    def load(self):
        if not os.path.exists(self.PLAYER_FILE) or not os.path.exists(self.WORLD_FILE):
            return False
        try:
            with open(self.PLAYER_FILE, 'r') as f:
                self.player = Player.from_dict(json.load(f))
            with open(self.WORLD_FILE, 'r') as f:
                world_data = json.load(f)
                self.locations = {loc_id: Location.from_dict(d) for loc_id, d in world_data.items()}
            return True
        except Exception as e:
            print(f"Error loading save: {e}")
            return False