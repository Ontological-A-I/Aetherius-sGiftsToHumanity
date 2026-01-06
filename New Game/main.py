import random
import uuid
import json
import os
import shutil
from enum import Enum, auto
import time # For simulating delays and making output readable

# --- Core Game Enums ---
class ItemType(Enum):
    FOOD = auto()
    WATER = auto()
    WEAPON = auto()
    TOOL = auto()
    CONSUMABLE = auto()
    JUNK = auto()
    MATERIAL = auto()
    KEY = auto()

class BodyPartStatus(Enum):
    UNINJURED = auto()
    GRAZED = auto()
    WOUNDED = auto()
    BROKEN = auto()
    SEVERE_BLEEDING = auto()
    SEVERED = auto()

class ContainerType(Enum):
    SMALL_BUILDING = auto()
    LARGE_BUILDING = auto()
    FURNITURE = auto()
    BACKPACK = auto()
    POCKET = auto()
    GENERIC = auto()

class MonsterType(Enum): # NEW: MonsterType
    ZOMBIE = auto()
    ABERRATION = auto()
    HUMANOID = auto()
    ENVIRONMENTAL = auto()
    BOSS = auto()

class BehaviorState(Enum): # NEW: BehaviorState
    IDLE = auto()
    ALERT = auto()
    AGGRO = auto()
    FLEE = auto()
    DEAD = auto()

# --- Item Templates (This would ideally be loaded from a file, e.g., JSON) ---
ITEM_TEMPLATES_FOR_GENERATION = {
    "rusty_knife": {
        "name": "Rusty Knife", "description": "A dull, rusty knife.",
        "weight": 0.5, "item_type": "WEAPON", "properties": {"damage": 10, "durability": 50},
        "tags": ["weapon", "melee", "low_tier", "tool", "common_loot"]
    },
    "half_eaten_apple": {
        "name": "Half-Eaten Apple", "description": "Someone took a bite. Still edible, barely.",
        "weight": 0.1, "item_type": "FOOD", "properties": {"hunger_restore": 75, "health_restore": 2},
        "tags": ["food", "low_tier", "common_loot"]
    },
    "dirty_water_bottle": {
        "name": "Dirty Water Bottle", "description": "A plastic bottle, looks like it holds dirty water.",
        "weight": 0.3, "item_type": "WATER", "properties": {"hydration_restore": 100, "health_restore": -5},
        "tags": ["water", "low_tier", "common_loot"]
    },
    "tattered_rag": {
        "name": "Tattered Rag", "description": "A piece of old cloth, might be useful for a bandage.",
        "weight": 0.05, "item_type": "MATERIAL", "properties": {},
        "tags": ["material", "low_tier", "useful", "common_loot"]
    },
    "smooth_rock": {
        "name": "Smooth Rock", "description": "A perfectly smooth, grey rock. Oddly satisfying to hold.",
        "weight": 0.2, "item_type": "JUNK", "properties": {},
        "tags": ["useless", "junk", "common_loot"]
    },
    "broken_glasses": {
        "name": "Broken Glasses", "description": "Shattered lenses, bent frames. Useless for vision now.",
        "weight": 0.1, "item_type": "JUNK", "properties": {},
        "tags": ["useless", "junk", "common_loot"]
    },
    "medical_bandage": {
        "name": "Medical Bandage", "description": "Sterile bandage, good for serious wounds.",
        "weight": 0.1, "item_type": "CONSUMABLE", "properties": {"health_restore": 25, "heal_body_part_type": "wound"},
        "tags": ["consumable", "medical", "common_loot"]
    },
    "rusty_key": {
        "name": "Rusty Key", "description": "An old, rusty key.", "weight": 0.05, "item_type": "KEY", "properties": {},
        "tags": ["key", "common_loot"]
    },
    "machete": {
        "name": "Machete", "description": "A well-balanced machete, surprisingly sharp.",
        "weight": 1.5, "item_type": "WEAPON", "properties": {"damage": 25, "durability": 120},
        "tags": ["weapon", "melee", "mid_tier", "tool", "common_loot"]
    },
    "empty_can": {
        "name": "Empty Can", "description": "A discarded metal can.", "weight": 0.1, "item_type": "JUNK", "properties": {},
        "tags": ["junk", "common_loot"]
    },
    "wood_scrap": {
        "name": "Wood Scrap", "description": "A small piece of wood, maybe for kindling.", "weight": 0.3, "item_type": "MATERIAL", "properties": {},
        "tags": ["material", "common_loot"]
    },
    "empty_flask": {
        "name": "Empty Flask", "description": "A small, empty metal flask.", "weight": 0.15, "item_type": "JUNK", "properties": {},
        "tags": ["useless", "junk", "common_loot"]
    }
}

# NEW: Monster Templates (also ideally loaded from file)
MONSTER_TEMPLATES_FOR_GENERATION = {
    "shambling_zombie": {
        "name": "Shambling Zombie", "description": "A reanimated corpse, slowly shuffling.",
        "monster_type": "ZOMBIE", "health": 60, "max_health": 60, "damage_output": 10,
        "attack_description": "lunges with a rotten claw", "sanity_drain_on_sight": 2,
        "speed": 1, "aggressiveness": 6, "loot_item_keys": ["tattered_rag", "empty_can"],
        "body_parts": { # More specific body parts for monsters
            "head": {"max_health": 20, "current_health": 20, "status": "UNINJURED"},
            "torso": {"max_health": 40, "current_health": 40, "status": "UNINJURED"},
            "left_arm": {"max_health": 15, "current_health": 15, "status": "UNINJURED"},
            "right_arm": {"max_health": 15, "current_health": 15, "status": "UNINJURED"},
            "left_leg": {"max_health": 15, "current_health": 15, "status": "UNINJURED"},
            "right_leg": {"max_health": 15, "current_health": 15, "status": "UNINJURED"}
        }
    },
    "grotesque_aberration": {
        "name": "Grotesque Aberration", "description": "A horrifying mass of writhing limbs and distorted flesh.",
        "monster_type": "ABERRATION", "health": 120, "max_health": 120, "damage_output": 25,
        "attack_description": "slams its pulpy appendage", "sanity_drain_on_sight": 10,
        "speed": 2, "aggressiveness": 8, "vulnerabilities": ["fire"], "resistances": ["blunt"],
        "loot_item_keys": [], # May drop unique "collision materials" later
        "body_parts": {
            "main_mass": {"max_health": 100, "current_health": 100, "status": "UNINJURED"},
            "sensory_stalk": {"max_health": 30, "current_health": 30, "status": "UNINJURED"}
        }
    },
    "mutated_wolf": {
        "name": "Mutated Wolf", "description": "A gaunt wolf, its fur patchy, its eyes glowing with unnatural hunger.",
        "monster_type": "ENVIRONMENTAL", "health": 80, "max_health": 80, "damage_output": 15,
        "attack_description": "snaps with its razor fangs", "sanity_drain_on_sight": 5,
        "speed": 3, "aggressiveness": 7, "vulnerabilities": [], "resistances": ["piercing"],
        "loot_item_keys": ["tattered_rag"], # Could drop "mutated_pelt" later
        "body_parts": {
            "head": {"max_health": 25, "current_health": 25, "status": "UNINJURED"},
            "torso": {"max_health": 50, "current_health": 50, "status": "UNINJURED"},
            "front_leg": {"max_health": 20, "current_health": 20, "status": "UNINJURED"},
            "back_leg": {"max_health": 20, "current_health": 20, "status": "UNINJURED"}
        }
    }
}

# --- Core Game Classes ---
# These are the full classes as designed, compacted for this single file.

class Item:
    def __init__(self, name: str, description: str, weight: float, item_type: ItemType, properties: dict = None, item_id: str = None):
        self.name = name; self.description = description; self.weight = weight; self.item_type = item_type
        self.properties = properties if properties is not None else {}
        if item_id is None: self.item_id = _generate_item_sqt_id(item_type, name, self.properties)
        else: self.item_id = item_id
    def to_dict(self): return {"item_id": self.item_id, "name": self.name, "description": self.description, "weight": self.weight, "item_type": self.item_type.name, "properties": self.properties}
    @classmethod
    def from_dict(cls, data: dict): return cls(item_id=data["item_id"], name=data["name"], description=data["description"], weight=data["weight"], item_type=ItemType[data["item_type"]], properties=data.get("properties"))
    def __str__(self): return self.name
    def __repr__(self): return f"Item(id='{self.item_id}', name='{self.name}', type={self.item_type.name})"

class BodyPart:
    def __init__(self, name: str, max_health: int, current_health: int = None, status: BodyPartStatus = BodyPartStatus.UNINJURED):
        self.name = name; self.max_health = max_health; self.current_health = current_health if current_health is not None else max_health
        self.status = status
    def take_damage(self, amount: int):
        self.current_health -= amount
        if self.current_health <= 0:
            self.current_health = 0
            if self.name == "throat": self.status = BodyPartStatus.SEVERED
            elif self.current_health <= -self.max_health * 0.5: self.status = BodyPartStatus.SEVERED
            elif self.current_health <= self.max_health * 0.1: self.status = BodyPartStatus.BROKEN
            elif self.current_health <= self.max_health * 0.5: self.status = BodyPartStatus.WOUNDED
            elif self.current_health < self.max_health: self.status = BodyPartStatus.GRAZED
        elif self.status == BodyPartStatus.UNINJURED: self.status = BodyPartStatus.GRAZED
    def heal(self, amount: int):
        self.current_health += amount
        if self.current_health > self.max_health: self.current_health = self.max_health
        if self.current_health == self.max_health and self.status != BodyPartStatus.SEVERED: self.status = BodyPartStatus.UNINJURED
    def is_crippled(self): return self.status in [BodyPartStatus.BROKEN, BodyPartStatus.SEVERED]
    def to_dict(self): return {"name": self.name, "max_health": self.max_health, "current_health": self.current_health, "status": self.status.name}
    @classmethod
    def from_dict(cls, data: dict): return cls(name=data["name"], max_health=data["max_health"], current_health=data["current_health"], status=BodyPartStatus[data["status"]])
    def __str__(self): return f"{self.name} ({self.status.name}, {self.current_health}/{self.max_health})"

class Container:
    def __init__(self, container_id: str, name: str, description: str, container_type: ContainerType, inventory_items: list = None, is_locked: bool = False, requires_key_id: str = None, generation_rules: dict = None):
        self.container_id = container_id; self.name = name; self.description = description; self.container_type = container_type
        self.inventory = inventory_items if inventory_items is not None else []; self.is_locked = is_locked; self.requires_key_id = requires_key_id
        self.has_been_searched = False; self.generation_rules = generation_rules if generation_rules is not None else {}
    def add_item(self, item: Item): self.inventory.append(item)
    def remove_item(self, item_id: str) -> Item | None:
        for i, item in enumerate(self.inventory):
            if item.item_id == item_id: return self.inventory.pop(i)
        return None
    def find_item(self, item_name_or_id: str) -> Item | None:
        for item in self.inventory:
            if item.item_id == item_name_or_id or item.name.lower() == item_name_or_id.lower(): return item
        return None
    def get_inventory_description(self):
        if not self.inventory: return f"The {self.name} is empty."
        items_list = ", ".join([item.name for item in self.inventory])
        return f"Inside the {self.name}, you see: {items_list}."
    def to_dict(self): return {"container_id": self.container_id, "name": self.name, "description": self.description, "container_type": self.container_type.name, "inventory": [item.to_dict() for item in self.inventory], "is_locked": self.is_locked, "requires_key_id": self.requires_key_id, "has_been_searched": self.has_been_searched, "generation_rules": self.generation_rules}
    @classmethod
    def from_dict(cls, data: dict): return cls(container_id=data["container_id"], name=data["name"], description=data["description"], container_type=ContainerType[data["container_type"]], inventory_items=[Item.from_dict(item_data) for item_data in data.get("inventory", [])], is_locked=data.get("is_locked", False), requires_key_id=data.get("requires_key_id"), has_been_searched=data.get("has_been_searched", False), generation_rules=data.get("generation_rules", {}))
    def __str__(self): return self.name
    def __repr__(self): return f"Container(id='{self.container_id}', name='{self.name}', items={len(self.inventory)}, searched={self.has_been_searched})"

class Location:
    def __init__(self, location_id: str, name: str, description: str, exits: dict = None, items_on_ground: list = None, containers: list = None, environmental_elements: list = None, potential_ground_items_rules: dict = None, potential_monsters_rules: dict = None): # NEW: potential_monsters_rules
        self.location_id = location_id; self.name = name; self.description = description; self.exits = exits if exits is not None else {}
        self.items_on_ground = items_on_ground if items_on_ground is not None else []; self.containers = containers if containers is not None else []
        self.environmental_elements = environmental_elements if environmental_elements is not None else []
        self.has_been_visited = False; self.potential_ground_items_rules = potential_ground_items_rules if potential_ground_items_rules is not None else {}
        self.has_generated_ground_items = False
        self.potential_monsters_rules = potential_monsters_rules if potential_monsters_rules is not None else {} # NEW
        self.has_generated_monsters = False # NEW
        self.monsters: list['Monster'] = [] # NEW: List of monster instances in this location

    def get_description(self, player_has_visited: bool = False):
        desc = self.description
        if not self.items_on_ground and not self.containers and not self.environmental_elements and not self.monsters: desc += "\nNothing of immediate interest is lying around."
        else:
            if self.items_on_ground: items_str = ", ".join([item.name for item in self.items_on_ground]); desc += f"\nOn the ground, you see: {items_str}."
            if self.containers: containers_str = ", ".join([c.name for c in self.containers]); desc += f"\nThere are several objects here that might hold items: {containers_str}."
            if self.monsters: monsters_str = ", ".join([m.name for m in self.monsters if m.is_alive]); desc += f"\nBeware! You see: {monsters_str}." # NEW: Describe monsters
        if self.environmental_elements: elements_str = ", ".join(self.environmental_elements); desc += f"\nThe environment offers potential resources: {elements_str}."
        if self.exits: exits_str = ", ".join([f"{direction} ({target_loc_id})" for direction, target_loc_id in self.exits.items()]); desc += f"\nExits are: {exits_str}."
        return desc
    def add_item_on_ground(self, item: Item): self.items_on_ground.append(item)
    def remove_item_on_ground(self, item_id: str) -> Item | None:
        for i, item in enumerate(self.items_on_ground):
            if item.item_id == item_id: return self.items_on_ground.pop(i)
        return None
    def find_item_on_ground(self, item_name_or_id: str) -> Item | None:
        for item in self.items_on_ground:
            if item.item_id == item_name_or_id or item.name.lower() == item_name_or_id.lower(): return item
        return None
    def add_container(self, container: Container): self.containers.append(container)
    def find_container(self, container_name_or_id: str) -> Container | None:
        for container in self.containers:
            if container.container_id == container_name_or_id or container.name.lower() == container_name_or_id.lower(): return container
        return None
    def add_monster(self, monster: 'Monster'): # NEW: Add monster method
        self.monsters.append(monster)
    def remove_monster(self, monster_id: str) -> 'Monster' | None: # NEW: Remove monster method
        for i, monster in enumerate(self.monsters):
            if monster.monster_id == monster_id: return self.monsters.pop(i)
        return None
    def find_monster(self, monster_name_or_id: str) -> 'Monster' | None: # NEW: Find monster method
        for monster in self.monsters:
            if monster.monster_id == monster_name_or_id or monster.name.lower() == monster_name_or_id.lower(): return monster
        return None

    def to_dict(self):
        return {"location_id": self.location_id, "name": self.name, "description": self.description, "exits": self.exits, "items_on_ground": [item.to_dict() for item in self.items_on_ground], "containers": [container.to_dict() for container in self.containers], "environmental_elements": self.environmental_elements, "has_been_visited": self.has_been_visited, "potential_ground_items_rules": self.potential_ground_items_rules, "has_generated_ground_items": self.has_generated_ground_items, "potential_monsters_rules": self.potential_monsters_rules, "has_generated_monsters": self.has_generated_monsters, "monsters": [monster.to_dict() for monster in self.monsters]} # NEW: Save monsters
    @classmethod
    def from_dict(cls, data: dict):
        return cls(location_id=data["location_id"], name=data["name"], description=data["description"], exits=data.get("exits"), items_on_ground=[Item.from_dict(item_data) for item_data in data.get("items_on_ground", [])], containers=[Container.from_dict(container_data) for container_data in data.get("containers", [])], environmental_elements=data.get("environmental_elements", []), has_been_visited=data.get("has_been_visited", False), potential_ground_items_rules=data.get("potential_ground_items_rules", {}), has_generated_ground_items=data.get("has_generated_ground_items", False), potential_monsters_rules=data.get("potential_monsters_rules", {}), has_generated_monsters=data.get("has_generated_monsters", False), monsters=[Monster.from_dict(m_data) for m_data in data.get("monsters", [])]) # NEW: Load monsters
    def __str__(self): return self.name
    def __repr__(self): return f"Location(id='{self.location_id}', name='{self.name}', items={len(self.items_on_ground)}, containers={len(self.containers)}, monsters={len(self.monsters)})"

class Player:
    def __init__(self, name: str = "Player", current_location_id: str = "starting_area", age: int = 30, weight: float = 75.0, health: int = 100, hunger_level: int = 1000, hydration_level: int = 1000, sanity_level: int = 1000, stamina_level: int = 100, action_counter: int = 0, inventory_items: list = None, initial_body_parts: dict = None):
        self.name = name; self.current_location_id = current_location_id; self.age = age; self.weight = weight
        self.health = health; self.hunger_level = hunger_level; self.hydration_level = hydration_level; self.sanity_level = sanity_level; self.stamina_level = stamina_level
        self.action_counter = action_counter
        self.inventory = inventory_items if inventory_items is not None else []
        self.body_parts = initial_body_parts if initial_body_parts is not None else self._initialize_default_body_parts()
        self.nested_containers = {}
    def _initialize_default_body_parts(self):
        return {"head": BodyPart("head", 50), "torso": BodyPart("torso", 100), "left_arm": BodyPart("left_arm", 70), "right_arm": BodyPart("right_arm", 70), "left_leg": BodyPart("left_leg", 80), "right_leg": BodyPart("right_leg", 80), "throat": BodyPart("throat", 20)}
    def perform_action(self, action_cost: int = 1):
        self.action_counter += action_cost
        self.hunger_level -= action_cost * 1; self.hydration_level -= action_cost * 2
        if self.hunger_level < 0: self.hunger_level = 0; self.health -= 5 * action_cost
        if self.hydration_level < 0: self.hydration_level = 0; self.health -= 10 * action_cost
        if self.hunger_level < 200 or self.hydration_level < 200: self.sanity_level -= action_cost * 0.5
        if action_cost == 1: self.stamina_level += 1;
        if self.stamina_level > 100: self.stamina_level = 100
        if self.health <= 0 or self.hunger_level <= 0 or self.hydration_level <= 0: return False
        if self.body_parts["throat"].status == BodyPartStatus.SEVERED: return False
        return True
    def display_stats(self):
        print(f"\n--- {self.name}'s Status (Actions: {self.action_counter}) ---")
        print(f"Health: {self.health}/100")
        print(f"Hunger: {self.hunger_level}/1000 ({'Starving' if self.hunger_level < 200 else 'Hungry' if self.hunger_level < 500 else 'Satiated'})")
        print(f"Hydration: {self.hydration_level}/1000 ({'Dehydrated' if self.hydration_level < 200 else 'Thirsty' if self.hydration_level < 500 else 'Hydrated'})")
        print(f"Sanity: {self.sanity_level}/1000 ({'Breaking' if self.sanity_level < 200 else 'Unsettled' if self.sanity_level < 500 else 'Stable'})")
        print(f"Stamina: {self.stamina_level}/100")
        print("Body Parts:")
        for part_name, part in self.body_parts.items(): print(f"  - {part}")
        print("--------------------------------------")
    def take_damage(self, body_part_name: str, amount: int, damage_type: str = "generic"):
        if body_part_name in self.body_parts:
            part = self.body_parts[body_part_name]; part.take_damage(amount); self.health -= amount
            if part.status == BodyPartStatus.SEVERED: self.health = 0
        else: self.health -= amount
    def heal(self, body_part_name: str, amount: int):
        if body_part_name in self.body_parts:
            part = self.body_parts[body_part_name]; part.heal(amount); self.health += amount
            if self.health > 100: self.health = 100
        else: self.health += amount
    def add_item(self, item: Item): self.inventory.append(item)
    def remove_item(self, item_id: str) -> Item | None:
        for i, item in enumerate(self.inventory):
            if item.item_id == item_id: return self.inventory.pop(i)
        return None
    def find_item(self, item_name_or_id: str) -> Item | None:
        for item in self.inventory:
            if item.item_id == item_name_or_id or item.name.lower() == item_name_or_id.lower(): return item
            if item_name_or_id.upper() in item.item_id.split('_')[0]: return item
        return None
    def consume_item(self, item_id: str):
        item = self.find_item(item_id)
        if not item: return
        if item.item_type in [ItemType.FOOD, ItemType.WATER, ItemType.CONSUMABLE]:
            if 'hunger_restore' in item.properties: self.hunger_level = min(1000, self.hunger_level + item.properties['hunger_restore'])
            if 'hydration_restore' in item.properties: self.hydration_level = min(1000, self.hydration_level + item.properties['hydration_restore'])
            if 'health_restore' in item.properties: self.health = min(100, self.health + item.properties['health_restore'])
            if 'sanity_restore' in item.properties: self.sanity_level = min(1000, self.sanity_level + item.properties['sanity_restore'])
            self.remove_item(item.item_id); self.perform_action()
        else: pass
    def use_item(self, item_id: str, target=None):
        item = self.find_item(item_id); if not item: return
        self.perform_action()
        if item.item_type == ItemType.CONSUMABLE and 'health_restore' in item.properties and 'heal_body_part_type' in item.properties:
            if target and target in self.body_parts: self.heal(target, item.properties['health_restore']); self.remove_item(item.item_id)
        else: pass
    def get_inventory_string(self):
        if not self.inventory: return "Your inventory is empty."
        inv_str = "Your inventory (i):\n"
        for item in self.inventory:
            short_id = item.item_id.split('_')[-1]; inv_str += f"- {item.name} ({item.item_type.name[0]}:{short_id})\n"
        return inv_str
    def to_dict(self):
        return {"name": self.name, "current_location_id": self.current_location_id, "age": self.age, "weight": self.weight, "health": self.health, "hunger_level": self.hunger_level, "hydration_level": self.hydration_level, "sanity_level": self.sanity_level, "stamina_level": self.stamina_level, "action_counter": self.action_counter, "inventory": [item.to_dict() for item in self.inventory], "body_parts": {name: part.to_dict() for name, part in self.body_parts.items()}}
    @classmethod
    def from_dict(cls, data: dict):
        player = cls(name=data["name"], current_location_id=data["current_location_id"], age=data.get("age", 30), weight=data.get("weight", 75.0), health=data["health"], hunger_level=data["hunger_level"], hydration_level=data["hydration_level"], sanity_level=data["sanity_level"], stamina_level=data["stamina_level"], action_counter=data["action_counter"], inventory_items=[Item.from_dict(item_data) for item_data in data["inventory"]], initial_body_parts={name: BodyPart.from_dict(part_data) for name, part_data in data["body_parts"].items()})
        return player

class Monster: # NEW: Monster Class
    def __init__(self, monster_id: str, name: str, description: str, monster_type: MonsterType, current_location_id: str, health: int, max_health: int, damage_output: int, attack_description: str, body_parts: dict = None, loot_item_keys: list = None, sanity_drain_on_sight: int = 0, speed: int = 1, aggressiveness: int = 5, vulnerabilities: list = None, resistances: list = None, special_abilities: list = None, current_behavior: BehaviorState = BehaviorState.IDLE):
        self.monster_id = monster_id; self.name = name; self.description = description; self.monster_type = monster_type
        self.current_location_id = current_location_id; self.health = health; self.max_health = max_health
        self.damage_output = damage_output; self.attack_description = attack_description
        self.body_parts = body_parts if body_parts is not None else self._initialize_default_body_parts(); self.loot_item_keys = loot_item_keys if loot_item_keys is not None else []
        self.sanity_drain_on_sight = sanity_drain_on_sight; self.speed = speed; self.aggressiveness = aggressiveness
        self.vulnerabilities = vulnerabilities if vulnerabilities is not None else []; self.resistances = resistances if resistances is not None else []
        self.special_abilities = special_abilities if special_abilities is not None else []
        self.current_behavior = current_behavior; self.is_alive = True

    def _initialize_default_body_parts(self):
        # Fallback if specific body parts aren't defined in template
        return {"head": BodyPart("head", int(self.max_health * 0.3)), "torso": BodyPart("torso", int(self.max_health * 0.5)), "limb_left": BodyPart("limb_left", int(self.max_health * 0.2)), "limb_right": BodyPart("limb_right", int(self.max_health * 0.2))}

    def take_damage(self, body_part_name: str, amount: int, damage_type: str = "generic"):
        if not self.is_alive: return
        if body_part_name in self.body_parts:
            part = self.body_parts[body_part_name]
            part.take_damage(amount)
            self.health -= amount
            print(f"The {self.name} took {amount} damage to its {body_part_name}.")
            if self.monster_type == MonsterType.ZOMBIE and body_part_name == "head" and part.current_health <= 0:
                print(f"You shattered the {self.name}'s head! It collapses lifelessly.")
                self.health = 0
            elif part.current_health <= 0: print(f"Its {body_part_name} is severely damaged!")
        else: self.health -= amount; print(f"The {self.name} took {amount} damage.")
        if self.health <= 0:
            self.health = 0; self.is_alive = False; self.current_behavior = BehaviorState.DEAD
            print(f"The {self.name} collapses, utterly defeated!")

    def attack_player(self, player_ref: Player):
        if not self.is_alive or self.current_behavior != BehaviorState.AGGRO: return
        target_part_name = random.choice(list(player_ref.body_parts.keys()))
        actual_damage = self.damage_output
        player_ref.take_damage(target_part_name, actual_damage, damage_type="physical")
        print(f"The {self.name} {self.attack_description} at your {target_part_name}, dealing {actual_damage} damage!")
        if self.sanity_drain_on_sight > 0:
            player_ref.sanity_level -= self.sanity_drain_on_sight
            print(f"The sight of the {self.name} drains your sanity by {self.sanity_drain_on_sight} points.")

    def get_status_description(self):
        if not self.is_alive: return f"The {self.name} lies motionless on the ground."
        status = f"The {self.name} ({self.monster_type.name.lower()}) is {self.current_behavior.name.lower()}. "
        if self.health < self.max_health * 0.2: status += "It looks severely wounded, barely clinging to life."
        elif self.health < self.max_health * 0.5: status += "It is visibly wounded, moving with difficulty."
        else: status += "It appears relatively unharmed."
        wounded_parts = [part.name for part_name, part in self.body_parts.items() if part.current_health < part.max_health]
        if wounded_parts: status += f" Its {', '.join(wounded_parts)} appear injured."
        return status

    def to_dict(self):
        return {"monster_id": self.monster_id, "name": self.name, "description": self.description, "monster_type": self.monster_type.name, "current_location_id": self.current_location_id, "health": self.health, "max_health": self.max_health, "damage_output": self.damage_output, "attack_description": self.attack_description, "body_parts": {name: part.to_dict() for name, part in self.body_parts.items()}, "loot_item_keys": self.loot_item_keys, "sanity_drain_on_sight": self.sanity_drain_on_sight, "speed": self.speed, "aggressiveness": self.aggressiveness, "vulnerabilities": self.vulnerabilities, "resistances": self.resistances, "special_abilities": self.special_abilities, "current_behavior": self.current_behavior.name, "is_alive": self.is_alive}
    @classmethod
    def from_dict(cls, data: dict):
        # Need to reconstruct BodyPart objects from their dicts
        body_parts_data = data.get("body_parts", {})
        reconstructed_body_parts = {}
        for bp_name, bp_data in body_parts_data.items():
            reconstructed_body_parts[bp_name] = BodyPart.from_dict(bp_data)

        monster = cls(
            monster_id=data["monster_id"], name=data["name"], description=data["description"], monster_type=MonsterType[data["monster_type"]],
            current_location_id=data["current_location_id"], health=data["health"], max_health=data["max_health"],
            damage_output=data["damage_output"], attack_description=data["attack_description"],
            body_parts=reconstructed_body_parts, # Pass reconstructed BodyPart objects
            loot_item_keys=data.get("loot_item_keys"), sanity_drain_on_sight=data.get("sanity_drain_on_sight", 0),
            speed=data.get("speed", 1), aggressiveness=data.get("aggressiveness", 5),
            vulnerabilities=data.get("vulnerabilities"), resistances=data.get("resistances"),
            special_abilities=data.get("special_abilities"), current_behavior=BehaviorState[data.get("current_behavior", BehaviorState.IDLE.name)]
        )
        monster.is_alive = data.get("is_alive", True)
        return monster
    def __str__(self): return self.name
    def __repr__(self): return f"Monster(id='{self.monster_id}', name='{self.name}', type={self.monster_type.name}, health={self.health}/{self.max_health})"


# --- SQT-like ItemID Generation Helper ---
def _generate_item_sqt_id(item_type: ItemType, name: str, properties: dict = None) -> str:
    prefix = "";
    if item_type in [ItemType.FOOD, ItemType.WATER, ItemType.CONSUMABLE]: prefix = "If"
    else: prefix = "I"
    name_abbr = "".join(filter(str.isalnum, name)).upper()[:5]
    if not name_abbr: name_abbr = "GENERIC"
    prop_parts = []
    if properties:
        if 'hunger_restore' in properties: prop_parts.append(f"HR{properties['hunger_restore']}")
        if 'hydration_restore' in properties: prop_parts.append(f"HYR{properties['hydration_restore']}")
        if 'damage' in properties: prop_parts.append(f"DMG{properties['damage']}")
        if 'health_restore' in properties: prop_parts.append(f"HLT{properties['health_restore']}")
        if 'durability' in properties: prop_parts.append(f"DUR{properties['durability']}")
        if 'weight_mod' in properties: prop_parts.append(f"WM{properties['weight_mod']}")
    props_str = ""
    if prop_parts: props_str = "_" + "_".join(f"P:{p}" for p in prop_parts)
    unique_suffix = uuid.uuid4().hex[:6].upper()
    return f"{prefix}:{name_abbr}{props_str}_{unique_suffix}"


# --- WorldGenerator Class ---
class WorldGenerator:
    def __init__(self, item_templates: dict, monster_templates: dict): # NEW: monster_templates
        self.item_templates = item_templates
        self.monster_templates = monster_templates # NEW
        self.generated_locations = {}
        self.generated_containers = {}
        self.generated_monsters = {} # NEW: Track generated monsters globally

    def _create_item_instance(self, template_key: str) -> Item:
        template = self.item_templates.get(template_key)
        if not template: raise ValueError(f"Item template '{template_key}' not found.")
        return Item(name=template["name"], description=template["description"], weight=template["weight"], item_type=ItemType[template["item_type"]], properties=template["properties"].copy())

    def _create_monster_instance(self, template_key: str, location_id: str) -> Monster: # NEW: Create monster instance
        template = self.monster_templates.get(template_key)
        if not template: raise ValueError(f"Monster template '{template_key}' not found.")
        
        # Instantiate body parts from template data
        initial_body_parts = {}
        if "body_parts" in template:
            for bp_name, bp_data in template["body_parts"].items():
                initial_body_parts[bp_name] = BodyPart(
                    name=bp_name,
                    max_health=bp_data["max_health"],
                    current_health=bp_data["current_health"],
                    status=BodyPartStatus[bp_data["status"]]
                )
        
        monster_id = f"M:{template_key.upper()}_{uuid.uuid4().hex[:6].upper()}"
        monster = Monster(
            monster_id=monster_id, name=template["name"], description=template["description"],
            monster_type=MonsterType[template["monster_type"]], current_location_id=location_id,
            health=template["health"], max_health=template["max_health"], damage_output=template["damage_output"],
            attack_description=template["attack_description"], body_parts=initial_body_parts,
            loot_item_keys=template.get("loot_item_keys"), sanity_drain_on_sight=template.get("sanity_drain_on_sight", 0),
            speed=template.get("speed", 1), aggressiveness=template.get("aggressiveness", 5),
            vulnerabilities=template.get("vulnerabilities"), resistances=template.get("resistances"),
            special_abilities=template.get("special_abilities")
        )
        return monster

    def generate_player_starting_inventory(self) -> list[Item]:
        player_inventory = []
        useful_low_items = [k for k, v in self.item_templates.items() if "low_tier" in v.get("tags", []) and "useless" not in v.get("tags", [])]
        useless_items = [k for k, v in self.item_templates.items() if "useless" in v.get("tags", [])]

        chosen_useful = random.sample(useful_low_items, min(5, len(useful_low_items)))
        for item_key in chosen_useful: player_inventory.append(self._create_item_instance(item_key))
        if useless_items:
            chosen_useless = random.choice(useless_items); player_inventory.append(self._create_item_instance(chosen_useless))
        return player_inventory

    def generate_random_container_contents(self, container: Container):
        if container.has_been_searched: return
        rules = container.generation_rules
        if not rules: container.has_been_searched = True; return
        item_tags_to_draw_from = rules.get("item_tags", ["common_loot"])
        min_items = rules.get("min_items", 0); max_items = rules.get("max_items", 3)
        eligible_items = [k for k, v in self.item_templates.items() if any(tag in item_tags_to_draw_from for tag in v.get("tags", []))]
        if not eligible_items: container.has_been_searched = True; return
        num_items_to_generate = random.randint(min_items, max_items)
        generated_item_keys = random.sample(eligible_items, min(num_items_to_generate, len(eligible_items)))
        for item_key in generated_item_keys: container.add_item(self._create_item_instance(item_key))
        container.has_been_searched = True

    def generate_random_ground_items(self, location: Location):
        if location.has_generated_ground_items: return
        rules = location.potential_ground_items_rules
        if not rules: location.has_generated_ground_items = True; return
        item_tags_to_draw_from = rules.get("item_tags", ["common_loot"])
        min_items = rules.get("min_items", 0); max_items = rules.get("max_items", 2)
        eligible_items = [k for k, v in self.item_templates.items() if any(tag in item_tags_to_draw_from for tag in v.get("tags", []))]
        if not eligible_items: location.has_generated_ground_items = True; return
        num_items_to_generate = random.randint(min_items, max_items)
        generated_item_keys = random.sample(eligible_items, min(num_items_to_generate, len(eligible_items)))
        for item_key in generated_item_keys: location.add_item_on_ground(self._create_item_instance(item_key))
        location.has_generated_ground_items = True

    def generate_monsters_for_location(self, location: Location): # NEW: Generate monsters for location
        if location.has_generated_monsters: return
        rules = location.potential_monsters_rules
        if not rules: location.has_generated_monsters = True; return

        monster_types_to_draw_from = rules.get("monster_types", [])
        min_monsters = rules.get("min_monsters", 0)
        max_monsters = rules.get("max_monsters", 1)

        eligible_monsters = [k for k, v in self.monster_templates.items() if v["monster_type"] in monster_types_to_draw_from]
        if not eligible_monsters: location.has_generated_monsters = True; return
        
        num_monsters_to_generate = random.randint(min_monsters, max_monsters)
        generated_monster_keys = random.sample(eligible_monsters, min(num_monsters_to_generate, len(eligible_monsters)))

        for monster_key in generated_monster_keys:
            monster = self._create_monster_instance(monster_key, location.location_id)
            location.add_monster(monster)
            self.generated_monsters[monster.monster_id] = monster
            print(f"DEBUG: Spawned {monster.name} in {location.name}.")

        location.has_generated_monsters = True


    def create_initial_world(self) -> tuple[Location, Player]:
        print("--- Generating Initial World ---")
        player_start_inv = self.generate_player_starting_inventory()
        player = Player(name="Survivor", inventory_items=player_start_inv)

        backyard_shed_container = Container(
            container_id=f"C:SHD_BACK_{uuid.uuid4().hex[:6].upper()}", name="Backyard Shed",
            description="A small, rusty shed. Looks like it hasn't been opened in ages.",
            container_type=ContainerType.SMALL_BUILDING, is_locked=True, requires_key_id=None,
            generation_rules={"item_tags": ["tool", "material", "weapon", "low_tier"], "min_items": 1, "max_items": 2}
        )
        self.generated_containers[backyard_shed_container.container_id] = backyard_shed_container

        house_fridge_container = Container(
            container_id=f"C:FRG_HOUSE_{uuid.uuid4().hex[:6].upper()}", name="Broken Refrigerator",
            description="A large, empty refrigerator with a moldy interior.",
            container_type=ContainerType.FURNITURE,
            generation_rules={"item_tags": ["food", "water", "consumable", "low_tier"], "min_items": 1, "max_items": 3}
        )
        self.generated_containers[house_fridge_container.container_id] = house_fridge_container

        abandoned_house = Location(
            location_id="L:HSE_STRT", name="Abandoned House (Living Room)",
            description="You awaken in the musty living room of an abandoned house. Broken furniture and scattered debris litter the floor. A strange, metallic tang hangs in the air.",
            exits={"north": "L:CLR_DENS", "east": "L:ROAD_OLD", "south": "L:GRG_BACK"},
            items_on_ground=[], containers=[house_fridge_container],
            environmental_elements=["broken glass", "loose floorboard", "tattered curtains"],
            potential_ground_items_rules={"item_tags": ["low_tier", "junk"], "min_items": 1, "max_items": 2},
            potential_monsters_rules={"monster_types": ["ZOMBIE"], "min_monsters": 0, "max_monsters": 1} # NEW: Potential zombie
        )
        self.generated_locations[abandoned_house.location_id] = abandoned_house

        backyard_garage = Location(
            location_id="L:GRG_BACK", name="Backyard Garage",
            description="A detached garage behind the house. The door hangs ajar, revealing shadows within.",
            exits={"north": "L:HSE_STRT"}, items_on_ground=[], containers=[backyard_shed_container],
            environmental_elements=["rusty tools", "oil stains"],
            potential_ground_items_rules={"item_tags": ["material", "tool", "low_tier", "junk"], "min_items": 0, "max_items": 1},
            potential_monsters_rules={"monster_types": ["ZOMBIE"], "min_monsters": 0, "max_monsters": 1} # NEW
        )
        self.generated_locations[backyard_garage.location_id] = backyard_garage

        dense_clearing = Location(
            location_id="L:CLR_DENS", name="Dense Clearing",
            description="A small, overgrown clearing. The air here feels heavy and still, the trees around you twisted and unnatural.",
            exits={"south": "L:HSE_STRT", "west": "L:WOOD_EDGE_A"},
            environmental_elements=["thick vines", "jagged rocks"],
            potential_ground_items_rules={"item_tags": ["material", "food_wild", "low_tier"], "min_items": 0, "max_items": 1},
            potential_monsters_rules={"monster_types": ["ENVIRONMENTAL", "ABERRATION"], "min_monsters": 0, "max_monsters": 1} # NEW: Mutated wolf/aberration
        )
        self.generated_locations[dense_clearing.location_id] = dense_clearing
        
        old_dirt_road = Location(
            location_id="L:ROAD_OLD", name="Old Dirt Road",
            description="A crumbling dirt road stretches east and west, disappearing into the warped horizon. A rusted, overturned car lies nearby.",
            exits={"west": "L:HSE_STRT", "east": "L:CROSSROADS_01"},
            environmental_elements=["overturned car", "broken asphalt"],
            potential_ground_items_rules={"item_tags": ["junk", "material", "low_tier"], "min_items": 0, "max_items": 2},
            potential_monsters_rules={"monster_types": ["ZOMBIE"], "min_monsters": 0, "max_monsters": 1} # NEW
        )
        self.generated_locations[old_dirt_road.location_id] = old_dirt_road

        shed_key_item = self._create_item_instance("rusty_key")
        backyard_shed_container.requires_key_id = shed_key_item.item_id
        abandoned_house.add_item_on_ground(shed_key_item)

        player.current_location_id = abandoned_house.location_id
        print("--- World Generation Complete ---")
        return abandoned_house, player

# --- WorldManager Class ---
class WorldManager:
    SAVE_DIR = "save_data"
    PLAYER_FILE = os.path.join(SAVE_DIR, "player.json")
    LOCATIONS_DIR = os.path.join(SAVE_DIR, "locations")
    CONTAINERS_DIR = os.path.join(SAVE_DIR, "containers")
    MONSTERS_DIR = os.path.join(SAVE_DIR, "monsters") # NEW: Monsters directory

    def __init__(self):
        self.player: Player = None
        self.current_location: Location = None
        self.locations: dict[str, Location] = {}
        self.containers: dict[str, Container] = {}
        self.monsters: dict[str, Monster] = {} # NEW: Track all monsters globally
        self.world_generator = WorldGenerator(ITEM_TEMPLATES_FOR_GENERATION, MONSTER_TEMPLATES_FOR_GENERATION) # NEW: Pass monster templates

    def _create_save_directories(self):
        os.makedirs(self.SAVE_DIR, exist_ok=True)
        os.makedirs(self.LOCATIONS_DIR, exist_ok=True)
        os.makedirs(self.CONTAINERS_DIR, exist_ok=True)
        os.makedirs(self.MONSTERS_DIR, exist_ok=True) # NEW

    def new_game(self):
        self._create_save_directories()
        self.current_location, self.player = self.world_generator.create_initial_world()
        
        # Populate internal dictionaries from the generator's output
        for loc_id, loc_obj in self.world_generator.generated_locations.items():
            self.locations[loc_id] = loc_obj
            for container in loc_obj.containers:
                self.containers[container.container_id] = container
            for monster in loc_obj.monsters: # NEW: Add monsters from generator
                self.monsters[monster.monster_id] = monster

        print(f"New game started. Player at: {self.current_location.name}")
        self.world_generator.generate_random_ground_items(self.current_location)
        self.world_generator.generate_monsters_for_location(self.current_location) # NEW: Generate monsters for start loc
        self.current_location.has_been_visited = True
        return True

    def load_game(self) -> bool:
        if not os.path.exists(self.PLAYER_FILE):
            print("No saved game found to load.")
            return False

        print("--- Loading Game ---")
        with open(self.PLAYER_FILE, 'r') as f:
            player_data = json.load(f); self.player = Player.from_dict(player_data)
        
        for filename in os.listdir(self.LOCATIONS_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(self.LOCATIONS_DIR, filename)
                with open(filepath, 'r') as f:
                    loc_data = json.load(f); location = Location.from_dict(loc_data); self.locations[location.location_id] = location
        
        for filename in os.listdir(self.CONTAINERS_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(self.CONTAINERS_DIR, filename)
                with open(filepath, 'r') as f:
                    container_data = json.load(f); container = Container.from_dict(container_data); self.containers[container.container_id] = container
        
        for filename in os.listdir(self.MONSTERS_DIR): # NEW: Load monsters
            if filename.endswith(".json"):
                filepath = os.path.join(self.MONSTERS_DIR, filename)
                with open(filepath, 'r') as f:
                    monster_data = json.load(f); monster = Monster.from_dict(monster_data); self.monsters[monster.monster_id] = monster

        # Relink objects
        for loc in self.locations.values():
            loc.containers = [self.containers[cid_data["container_id"]] for cid_data in loc.to_dict()["containers"] if cid_data["container_id"] in self.containers]
            loc.monsters = [self.monsters[mid_data["monster_id"]] for mid_data in loc.to_dict()["monsters"] if mid_data["monster_id"] in self.monsters] # NEW: Relink monsters

        self.current_location = self.locations.get(self.player.current_location_id)
        if not self.current_location:
            print(f"Error: Player's last known location '{self.player.current_location_id}' not found.")
            return False

        print(f"Game loaded. Player at: {self.current_location.name}")
        return True

    def save_game(self):
        self._create_save_directories()
        print("--- Saving Game ---")

        with open(self.PLAYER_FILE, 'w') as f:
            json.dump(self.player.to_dict(), f, indent=4)
        
        for loc_id, location in self.locations.items():
            filepath = os.path.join(self.LOCATIONS_DIR, f"{loc_id}.json")
            with open(filepath, 'w') as f:
                json.dump(location.to_dict(), f, indent=4)
        
        for container_id, container in self.containers.items():
             filepath = os.path.join(self.CONTAINERS_DIR, f"{container_id}.json")
             with open(filepath, 'w') as f:
                 json.dump(container.to_dict(), f, indent=4)
        
        for monster_id, monster in self.monsters.items(): # NEW: Save monsters
            filepath = os.path.join(self.MONSTERS_DIR, f"{monster_id}.json")
            with open(filepath, 'w') as f:
                json.dump(monster.to_dict(), f, indent=4)
        
        print("Game saved successfully.")

    def get_location(self, location_id: str) -> Location | None: return self.locations.get(location_id)
    def get_container(self, container_id: str) -> Container | None: return self.containers.get(container_id)
    def get_monster(self, monster_id: str) -> Monster | None: return self.monsters.get(monster_id) # NEW

    # --- Methods for Game Engine to interact with WorldManager ---
    def move_player(self, direction: str) -> bool:
        target_location_id = self.current_location.exits.get(direction)
        if target_location_id:
            next_location = self.get_location(target_location_id)
            if next_location:
                self.player.current_location_id = target_location_id
                self.current_location = next_location
                self.player.perform_action()
                print(f"You move {direction} to the {self.current_location.name}.")
                self.world_generator.generate_random_ground_items(self.current_location)
                self.world_generator.generate_monsters_for_location(self.current_location) # NEW: Generate monsters on move
                if not self.current_location.has_been_visited: self.current_location.has_been_visited = True
                return True
            else: print(f"The path to the {direction} leads to an unknown area (ID: {target_location_id})."); return False
        else: print(f"There is no exit to the {direction} from here."); return False

    def look_around(self):
        self.world_generator.generate_random_ground_items(self.current_location)
        self.world_generator.generate_monsters_for_location(self.current_location) # NEW: Generate monsters on look
        # Apply sanity drain from monsters on sight
        for monster in self.current_location.monsters:
            if monster.is_alive and monster.sanity_drain_on_sight > 0:
                self.player.sanity_level -= monster.sanity_drain_on_sight
                print(f"The chilling presence of the {monster.name} drains {monster.sanity_drain_on_sight} sanity!")
        print(self.current_location.get_description(self.current_location.has_been_visited))
        self.player.perform_action()

    def search_container(self, container_name_or_id: str):
        container = self.current_location.find_container(container_name_or_id)
        if container:
            if container.is_locked: print(f"The {container.name} is locked.")
            else: self.world_generator.generate_random_container_contents(container); print(container.get_inventory_description())
            self.player.perform_action()
        else: print(f"You don't see a '{container_name_or_id}' here.")

    def take_item_from_ground(self, item_name_or_id: str):
        item = self.current_location.remove_item_on_ground(item_name_or_id)
        if item: self.player.add_item(item); print(f"You pick up the {item.name}."); self.player.perform_action()
        else: print(f"You don't see '{item_name_or_id}' on the ground here.")

    def take_item_from_container(self, item_name_or_id: str, container_name_or_id: str):
        container = self.current_location.find_container(container_name_or_id)
        if not container: print(f"You don't see a '{container_name_or_id}' here."); return
        if container.is_locked: print(f"The {container.name} is locked. You can't take anything from it."); return
        item = container.remove_item(item_name_or_id)
        if item: self.player.add_item(item); print(f"You take the {item.name} from the {container.name}."); self.player.perform_action()
        else: print(f"There is no '{item_name_or_id}' in the {container.name}.")

    def drop_item(self, item_name_or_id: str):
        item = self.player.remove_item(item_name_or_id)
        if item: self.current_location.add_item_on_ground(item); print(f"You drop the {item.name} onto the ground."); self.player.perform_action()
        else: print(f"You don't have '{item_name_or_id}' in your inventory to drop.")

    def attack_monster(self, monster_name: str, target_body_part: str = None, weapon_name: str = None): # NEW: Attack monster logic
        monster = self.current_location.find_monster(monster_name)
        if not monster or not monster.is_alive:
            print(f"You don't see a living '{monster_name}' here to attack.")
            return

        weapon = self.player.find_item(weapon_name) if weapon_name else None
        base_damage = 5 # Default unarmed damage
        if weapon and weapon.item_type == ItemType.WEAPON and 'damage' in weapon.properties:
            base_damage = weapon.properties['damage']
            print(f"You swing your {weapon.name} at the {monster.name}!")
        else:
            print(f"You lunge at the {monster.name} with your bare hands!")

        # Simulate body part targeting if specified, otherwise random
        if target_body_part and target_body_part in monster.body_parts:
            monster.take_damage(target_body_part, base_damage)
        else:
            random_body_part = random.choice(list(monster.body_parts.keys()))
            monster.take_damage(random_body_part, base_damage)
        
        # Set monster to aggressive if not already
        if monster.is_alive and monster.current_behavior != BehaviorState.AGGRO:
            monster.current_behavior = BehaviorState.AGGRO
            print(f"The {monster.name} lets out a furious roar!")
        
        self.player.perform_action()


    def monster_actions(self): # NEW: Handles all monster actions in current location
        active_monsters = [m for m in self.current_location.monsters if m.is_alive and m.current_behavior == BehaviorState.AGGRO]
        if not active_monsters: return

        print("\n--- Monsters Act! ---")
        for monster in active_monsters:
            if monster.health > 0: # Only active monsters
                monster.attack_player(self.player)
            # Add more complex monster AI here (movement, special abilities, etc.)
        time.sleep(0.5) # Pause for dramatic effect


# --- CommandParser Class ---
class CommandParser:
    def __init__(self):
        self.verbs = {
            "look": ["look", "examine", "inspect", "l"],
            "search": ["search", "scout", "s"],
            "go": ["go", "move", "walk", "run"],
            "take": ["take", "grab", "get", "pick up", "loot"],
            "drop": ["drop"],
            "use": ["use"],
            "open": ["open"],
            "close": ["close"],
            "attack": ["attack", "hit", "strike", "fight", "kill"], # NEW
            "trip": ["trip"], # NEW
            "inventory": ["inventory", "inv", "i"],
            "stats": ["stats", "status", "check stats", "my stats"],
            "help": ["help", "?"],
            "quit": ["quit", "exit", "q"],
            "eat": ["eat", "consume"],
            "drink": ["drink", "quaff"],
            "save": ["save"] # NEW
        }
        self.directions = ["north", "south", "east", "west", "up", "down", "n", "s", "e", "w", "u", "d"]
        self.stop_words = ["a", "an", "the", "and", "but", "for", "of", "my", "your", "in"]
        self.prepositions = ["in", "on", "at", "from", "to", "with", "behind", "under", "over"]

        self._canonical_verbs = {};
        for canonical, synonyms in self.verbs.items():
            for syn in synonyms: self._canonical_verbs[syn] = canonical
        for direction in self.directions: self._canonical_verbs[direction] = "go"

    def parse_input(self, command: str) -> dict:
        original_command = command.lower().strip()
        tokens = original_command.split()
        if not tokens: return {"verb": "unknown", "message": "Please enter a command.", "raw_command": original_command}
        main_verb = None; verb_start_index = -1; verb_length = 0
        for i in range(len(tokens)):
            for syn, canonical in self._canonical_verbs.items():
                syn_tokens = syn.split()
                if len(syn_tokens) > 1 and i + len(syn_tokens) <= len(tokens):
                    if tokens[i:i+len(syn_tokens)] == syn_tokens: main_verb = canonical; verb_start_index = i; verb_length = len(syn_tokens); break
            if main_verb: break
            if tokens[i] in self._canonical_verbs: main_verb = self._canonical_verbs[tokens[i]]; verb_start_index = i; verb_length = 1; break
        if not main_verb and tokens[0] in self.directions: main_verb = "go"; verb_start_index = 0; verb_length = 1
        if not main_verb: return {"verb": "unknown", "message": f"I don't understand '{original_command}'.", "raw_command": original_command}
        remaining_tokens = tokens[verb_start_index + verb_length:]
        filtered_tokens = [word for word in remaining_tokens if word not in self.stop_words]
        direct_object_parts = []; indirect_object_parts = []
        preposition_found = None; current_target = direct_object_parts
        for token in filtered_tokens:
            if token in self.prepositions: preposition_found = token; current_target = indirect_object_parts
            else: current_target.append(token)
        if main_verb == "go" and not direct_object_parts and verb_start_index == 0 and tokens[0] in self.directions: direct_object_parts.append(tokens[0])
        return {"verb": main_verb, "direct_object": " ".join(direct_object_parts).strip() if direct_object_parts else None, "preposition": preposition_found, "indirect_object": " ".join(indirect_object_parts).strip() if indirect_object_parts else None, "raw_command": original_command}

# --- GameEngine (Central orchestrator) ---
class GameEngine:
    def __init__(self):
        self.world_manager = WorldManager()
        self.parser = CommandParser()
        self.is_running = True

    def start_game(self, load_game: bool = False):
        if load_game:
            if not self.world_manager.load_game():
                print("Failed to load game. Starting a new one.")
                self.world_manager.new_game()
        else:
            self.world_manager.new_game()
        
        print("\n" + "="*40)
        print(f"Welcome, {self.world_manager.player.name}!")
        self.world_manager.look_around() # Initial look to populate and describe current location
        self.world_manager.player.display_stats()
        print("="*40 + "\n")

    def handle_command(self, command_str: str):
        parsed_cmd = self.parser.parse_input(command_str)
        verb = parsed_cmd["verb"]
        do = parsed_cmd["direct_object"]
        prep = parsed_cmd["preposition"]
        io = parsed_cmd["indirect_object"]

        if verb == "unknown":
            print(parsed_cmd["message"])
            return

        # Player always performs an action, even for help/stats, for time progression
        if not self.world_manager.player.perform_action():
            self.is_running = False
            print("Game Over!")
            return

        if verb == "quit":
            print("Quitting game. Don't forget to save!")
            self.is_running = False
        elif verb == "save": # NEW
            self.world_manager.save_game()
        elif verb == "look":
            self.world_manager.look_around()
        elif verb == "go":
            self.world_manager.move_player(do)
        elif verb == "inventory":
            print(self.world_manager.player.get_inventory_string())
        elif verb == "stats":
            self.world_manager.player.display_stats()
        elif verb == "take":
            if do and not io: self.world_manager.take_item_from_ground(do)
            elif do and io: self.world_manager.take_item_from_container(do, io)
            else: print("What do you want to take?")
        elif verb == "drop":
            self.world_manager.drop_item(do)
        elif verb == "search":
            if do:
                if do == "area": self.world_manager.look_around()
                else: self.world_manager.search_container(do)
            else: self.world_manager.look_around()
        elif verb == "open":
            if do:
                container = self.world_manager.current_location.find_container(do)
                if container:
                    if container.is_locked:
                        if prep == "with" and io:
                            key_item = self.world_manager.player.find_item(io)
                            if key_item and key_item.item_id == container.requires_key_id:
                                container.is_locked = False
                                print(f"You unlock the {container.name} with the {key_item.name}.")
                                self.world_manager.search_container(container.name)
                            else: print(f"You try to open the {container.name} with the {io}, but it doesn't work.")
                        else: print(f"The {container.name} is locked. You need a key.")
                    else: self.world_manager.search_container(do)
                else: print(f"You can't open a '{do}' here.")
            else: print("What do you want to open?")
        elif verb == "eat": self.world_manager.player.consume_item(do)
        elif verb == "drink": self.world_manager.player.consume_item(do)
        elif verb == "use":
            if do and prep == "on" and io: self.world_manager.player.use_item(do, target=io)
            else: self.world_manager.player.use_item(do)
        elif verb == "attack": # NEW: Attack logic
            if not do: print("Attack what?"); return
            if io and prep == "with": # attack [monster] with [weapon]
                self.world_manager.attack_monster(do, weapon_name=io)
            elif io and prep == "to": # attack [monster] to [body part] (unarmed/default weapon)
                self.world_manager.attack_monster(do, target_body_part=io)
            elif io and prep == "at": # attack [monster] at [body part] (unarmed/default weapon)
                self.world_manager.attack_monster(do, target_body_part=io)
            elif do and not io: # attack [monster]
                self.world_manager.attack_monster(do)
            else: print("How do you want to attack?")
        elif verb == "trip": # NEW: Trip logic
            if not do: print("Trip what?"); return
            # Simplified: Assuming "trip the zombie" is the only form for now
            monster = self.world_manager.current_location.find_monster(do)
            if monster and monster.is_alive:
                print(f"You try to trip the {monster.name}! (This needs more detailed combat mechanics.)")
                # Placeholder: maybe stuns for a turn, or allows follow-up attack
                self.world_manager.attack_monster(monster.name, target_body_part="left_leg", weapon_name="unarmed") # Simulate a leg attack
                if monster.is_alive and monster.current_behavior != BehaviorState.AGGRO:
                    monster.current_behavior = BehaviorState.AGGRO
            else:
                print(f"You don't see a living '{do}' here to trip.")
            self.world_manager.player.perform_action()

        else:
            print(f"Command '{command_str}' ({verb}) not yet implemented.")
        
        # Handle monster actions AFTER player's turn
        if self.world_manager.player.is_alive: # Only if player is still alive
            self.world_manager.monster_actions()
        
        # After every action (player and monster), check if player stats need to be displayed (every 20 actions)
        if self.world_manager.player.action_counter % 20 == 0:
            self.world_manager.player.display_stats()
        
        if not self.world_manager.player.is_alive:
            self.is_running = False
            print("GAME OVER. You have succumbed to the horrors of this shattered world.")


    def game_loop(self):
        while self.is_running:
            try:
                command = input("\n> ").strip()
                if not command:
                    continue
                self.handle_command(command)
                if not self.is_running:
                    break
            except KeyboardInterrupt:
                print("\nInterrupted. Attempting to save game...")
                self.world_manager.save_game()
                self.is_running = False
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                self.world_manager.save_game()
                self.is_running = False


# --- How to boot the game ---
if __name__ == "__main__":
    # Clean up previous save data for a fresh start in example, uncomment to enable
    # if os.path.exists(WorldManager.SAVE_DIR):
    #     shutil.rmtree(WorldManager.SAVE_DIR)
    #     print(f"Removed old save data from {WorldManager.SAVE_DIR}.")

    game = GameEngine()

    # --- Choose how to start the game ---
    # 1. Start a brand new game:
    game.start_game(load_game=False)

    # 2. Or, attempt to load an existing game (if save_data directory exists):
    # game.start_game(load_game=True)

    print("\n---------------------------------------------------------")
    print("Welcome to the Shattered Reality!")
    print("Type 'help' for commands, or 'quit' to exit.")
    print("---------------------------------------------------------\n")

    game.game_loop()
    print("Game session ended.")
    if game.world_manager.player.is_alive:
        game.world_manager.save_game() # Save on graceful exit if player is alive
        print("Game saved automatically on exit.")
    else:
        print("Your journey ends here. No save made upon death.")