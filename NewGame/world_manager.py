# --- START OF FILE world_manager.py ---

import json
import os
import random
import sys 
import traceback 

from entities import Player, Location, Item, Container, Monster, Structure, Campfire, Survivor

class WorldManager:
    PLAYER_FILE = "player.json"
    WORLD_FILE = "world.json"
    SCENT_FILE = "scent.json"
    TACTICS_FILE = "tactics.json"

    def __init__(self):
        self.locations = {}
        self.player = None
        self.base_save_dir = self._get_base_save_directory() 
        
        self.player_filepath = os.path.join(self.base_save_dir, self.PLAYER_FILE)
        self.world_filepath = os.path.join(self.base_save_dir, self.WORLD_FILE)

    def _get_base_save_directory(self):
        """
        Forces the save directory to be C:/Games/SurvivalRPG/save_data.
        If C:/ cannot be written to, falls back to local folder.
        """
        # 1. Target Directory
        target_dir = r"C:\Games\SurvivalRPG\save_data"
        
        try:
            os.makedirs(target_dir, exist_ok=True)
            # Test write permissions to ensure we can actually save here
            test_file = os.path.join(target_dir, ".perm_test")
            with open(test_file, 'w') as f: f.write("ok")
            os.remove(test_file)
            return target_dir
        except (OSError, PermissionError) as e:
            # 2. Fallback: Local directory (if C:/ access is denied)
            print(f"Warning: Could not access C:/Games. Saving locally. ({e})")
            if getattr(sys, 'frozen', False):
                base = os.path.dirname(sys.executable)
            else:
                base = os.path.dirname(os.path.abspath(__file__))
            
            local_dir = os.path.join(base, "save_data")
            os.makedirs(local_dir, exist_ok=True)
            return local_dir

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
        fridge = Container("fridge", "An old, rusty fridge.") 
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
            available_item_keys = list(ITEM_TEMPLATES.keys())
            if available_item_keys: 
                loot_key = random.choice(available_item_keys)
                loc.items.append(Item(loot_key))
        
        # Monsters
        if (x != 0 or y != 0) and random.random() < 0.35:
            from data.monsters import MONSTER_TEMPLATES 
            available_monster_keys = list(MONSTER_TEMPLATES.keys())
            if available_monster_keys: 
                monster_key = random.choice(available_monster_keys)
                loc.monsters.append(Monster(monster_key))

        # Survivors (Rare)
        if (x != 0 or y != 0) and random.random() < 0.1:
            loc.survivors.append(Survivor(f"Survivor {random.randint(100, 999)}"))

        self.locations[loc_id] = loc
        return loc

    def get_location(self, x, y):
        return self.generate_location(x, y)

    def get_location_safe(self, x, y):
        """Used by AI to check existing locations without generating new ones unnecessarily."""
        loc_id = f"{x}_{y}"
        return self.locations.get(loc_id, None)

    def save(self):
        os.makedirs(self.base_save_dir, exist_ok=True) 
        
        player_data = self.player.to_dict()
        with open(self.player_filepath, 'w') as f:
            json.dump(player_data, f, indent=4)
            
        world_data = {loc_id: loc.to_dict() for loc_id, loc in self.locations.items()}
        with open(self.world_filepath, 'w') as f:
            json.dump(world_data, f, indent=4)

    def load(self):
        if not os.path.exists(self.player_filepath) or not os.path.exists(self.world_filepath):
            return False
        try:
            with open(self.player_filepath, 'r') as f:
                self.player = Player.from_dict(json.load(f))
            with open(self.world_filepath, 'r') as f:
                world_data = json.load(f)
                self.locations = {loc_id: Location.from_dict(d) for loc_id, d in world_data.items()}
            return True
        except Exception as e:
            print(f"Error loading save: {e}")
            traceback.print_exc() 
            return False

# --- END OF FILE world_manager.py ---