import random
import uuid
import json
import os
import shutil # For removing save directories
from enum import Enum, auto

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

# --- SQT-like ItemID Generation Helper ---
def _generate_item_sqt_id(item_type: ItemType, name: str, properties: dict = None) -> str:
    prefix = ""
    if item_type in [ItemType.FOOD, ItemType.WATER, ItemType.CONSUMABLE]:
        prefix = "If"
    else:
        prefix = "I"

    name_abbr = "".join(filter(str.isalnum, name)).upper()[:5]
    if not name_abbr:
        name_abbr = "GENERIC"

    prop_parts = []
    if properties:
        if 'hunger_restore' in properties: prop_parts.append(f"HR{properties['hunger_restore']}")
        if 'hydration_restore' in properties: prop_parts.append(f"HYR{properties['hydration_restore']}")
        if 'damage' in properties: prop_parts.append(f"DMG{properties['damage']}")
        if 'health_restore' in properties: prop_parts.append(f"HLT{properties['health_restore']}")
        if 'durability' in properties: prop_parts.append(f"DUR{properties['durability']}")
        if 'weight_mod' in properties: prop_parts.append(f"WM{properties['weight_mod']}")

    props_str = ""
    if prop_parts:
        props_str = "_" + "_".join(f"P:{p}" for p in prop_parts)

    unique_suffix = uuid.uuid4().hex[:6].upper()

    return f"{prefix}:{name_abbr}{props_str}_{unique_suffix}"

# --- Core Game Classes (trimmed for brevity; full versions from previous steps) ---
class Item:
    def __init__(self, name: str, description: str, weight: float, item_type: ItemType, properties: dict = None, item_id: str = None):
        self.name = name
        self.description = description
        self.weight = weight
        self.item_type = item_type
        self.properties = properties if properties is not None else {}
        if item_id is None: self.item_id = _generate_item_sqt_id(item_type, name, self.properties)
        else: self.item_id = item_id
    def to_dict(self):
        return {"item_id": self.item_id, "name": self.name, "description": self.description, "weight": self.weight, "item_type": self.item_type.name, "properties": self.properties}
    @classmethod
    def from_dict(cls, data: dict):
        return cls(item_id=data["item_id"], name=data["name"], description=data["description"], weight=data["weight"], item_type=ItemType[data["item_type"]], properties=data.get("properties"))
    def __str__(self): return self.name
    def __repr__(self): return f"Item(id='{self.item_id}', name='{self.name}', type={self.item_type.name})"

class BodyPart:
    def __init__(self, name: str, max_health: int, current_health: int = None, status: BodyPartStatus = BodyPartStatus.UNINJURED):
        self.name = name
        self.max_health = max_health
        self.current_health = current_health if current_health is not None else max_health
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
    def to_dict(self):
        return {"name": self.name, "max_health": self.max_health, "current_health": self.current_health, "status": self.status.name}
    @classmethod
    def from_dict(cls, data: dict):
        return cls(name=data["name"], max_health=data["max_health"], current_health=data["current_health"], status=BodyPartStatus[data["status"]])
    def __str__(self): return f"{self.name} ({self.status.name}, {self.current_health}/{self.max_health})"

class Container:
    def __init__(self, container_id: str, name: str, description: str, container_type: ContainerType, inventory_items: list = None, is_locked: bool = False, requires_key_id: str = None, generation_rules: dict = None):
        self.container_id = container_id
        self.name = name
        self.description = description
        self.container_type = container_type
        self.inventory = inventory_items if inventory_items is not None else []
        self.is_locked = is_locked
        self.requires_key_id = requires_key_id
        self.has_been_searched = False
        self.generation_rules = generation_rules if generation_rules is not None else {}
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
    def to_dict(self):
        return {"container_id": self.container_id, "name": self.name, "description": self.description, "container_type": self.container_type.name, "inventory": [item.to_dict() for item in self.inventory], "is_locked": self.is_locked, "requires_key_id": self.requires_key_id, "has_been_searched": self.has_been_searched, "generation_rules": self.generation_rules}
    @classmethod
    def from_dict(cls, data: dict):
        return cls(container_id=data["container_id"], name=data["name"], description=data["description"], container_type=ContainerType[data["container_type"]], inventory_items=[Item.from_dict(item_data) for item_data in data.get("inventory", [])], is_locked=data.get("is_locked", False), requires_key_id=data.get("requires_key_id"), has_been_searched=data.get("has_been_searched", False), generation_rules=data.get("generation_rules", {}))
    def __str__(self): return self.name
    def __repr__(self): return f"Container(id='{self.container_id}', name='{self.name}', items={len(self.inventory)}, searched={self.has_been_searched})"

class Location:
    def __init__(self, location_id: str, name: str, description: str, exits: dict = None, items_on_ground: list = None, containers: list = None, environmental_elements: list = None, potential_ground_items_rules: dict = None):
        self.location_id = location_id
        self.name = name
        self.description = description
        self.exits = exits if exits is not None else {}
        self.items_on_ground = items_on_ground if items_on_ground is not None else []
        self.containers = containers if containers is not None else []
        self.environmental_elements = environmental_elements if environmental_elements is not None else []
        self.has_been_visited = False
        self.potential_ground_items_rules = potential_ground_items_rules if potential_ground_items_rules is not None else {}
        self.has_generated_ground_items = False
    def get_description(self, player_has_visited: bool = False):
        desc = self.description
        if not self.items_on_ground and not self.containers and not self.environmental_elements: desc += "\nNothing of immediate interest is lying around."
        else:
            if self.items_on_ground: items_str = ", ".join([item.name for item in self.items_on_ground]); desc += f"\nOn the ground, you see: {items_str}."
            if self.containers: containers_str = ", ".join([c.name for c in self.containers]); desc += f"\nThere are several objects here that might hold items: {containers_str}."
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
    def to_dict(self):
        return {"location_id": self.location_id, "name": self.name, "description": self.description, "exits": self.exits, "items_on_ground": [item.to_dict() for item in self.items_on_ground], "containers": [container.to_dict() for container in self.containers], "environmental_elements": self.environmental_elements, "has_been_visited": self.has_been_visited, "potential_ground_items_rules": self.potential_ground_items_rules, "has_generated_ground_items": self.has_generated_ground_items}
    @classmethod
    def from_dict(cls, data: dict):
        return cls(location_id=data["location_id"], name=data["name"], description=data["description"], exits=data.get("exits"), items_on_ground=[Item.from_dict(item_data) for item_data in data.get("items_on_ground", [])], containers=[Container.from_dict(container_data) for container_data in data.get("containers", [])], environmental_elements=data.get("environmental_elements", []), has_been_visited=data.get("has_been_visited", False), potential_ground_items_rules=data.get("potential_ground_items_rules", {}), has_generated_ground_items=data.get("has_generated_ground_items", False))
    def __str__(self): return self.name
    def __repr__(self): return f"Location(id='{self.location_id}', name='{self.name}', items={len(self.items_on_ground)}, containers={len(self.containers)})"

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

# --- WorldGenerator Class ---
class WorldGenerator:
    def __init__(self, item_templates: dict):
        self.item_templates = item_templates
        self.generated_locations = {}
        self.generated_containers = {}

    def _create_item_instance(self, template_key: str) -> Item:
        template = self.item_templates.get(template_key)
        if not template: raise ValueError(f"Item template '{template_key}' not found.")
        return Item(name=template["name"], description=template["description"], weight=template["weight"], item_type=ItemType[template["item_type"]], properties=template["properties"].copy())

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
        min_items = rules.get("min_items", 0)
        max_items = rules.get("max_items", 3)

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
        min_items = rules.get("min_items", 0)
        max_items = rules.get("max_items", 2)

        eligible_items = [k for k, v in self.item_templates.items() if any(tag in item_tags_to_draw_from for tag in v.get("tags", []))]
        if not eligible_items: location.has_generated_ground_items = True; return

        num_items_to_generate = random.randint(min_items, max_items)
        generated_item_keys = random.sample(eligible_items, min(num_items_to_generate, len(eligible_items)))

        for item_key in generated_item_keys: location.add_item_on_ground(self._create_item_instance(item_key))
        location.has_generated_ground_items = True

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
            potential_ground_items_rules={"item_tags": ["low_tier", "junk"], "min_items": 1, "max_items": 2}
        )
        self.generated_locations[abandoned_house.location_id] = abandoned_house

        backyard_garage = Location(
            location_id="L:GRG_BACK", name="Backyard Garage",
            description="A detached garage behind the house. The door hangs ajar, revealing shadows within.",
            exits={"north": "L:HSE_STRT"}, items_on_ground=[], containers=[backyard_shed_container],
            environmental_elements=["rusty tools", "oil stains"],
            potential_ground_items_rules={"item_tags": ["material", "tool", "low_tier", "junk"], "min_items": 0, "max_items": 1}
        )
        self.generated_locations[backyard_garage.location_id] = backyard_garage

        dense_clearing = Location(
            location_id="L:CLR_DENS", name="Dense Clearing",
            description="A small, overgrown clearing. The air here feels heavy and still, the trees around you twisted and unnatural.",
            exits={"south": "L:HSE_STRT", "west": "L:WOOD_EDGE_A"},
            environmental_elements=["thick vines", "jagged rocks"],
            potential_ground_items_rules={"item_tags": ["material", "food_wild", "low_tier"], "min_items": 0, "max_items": 1}
        )
        self.generated_locations[dense_clearing.location_id] = dense_clearing
        
        old_dirt_road = Location(
            location_id="L:ROAD_OLD", name="Old Dirt Road",
            description="A crumbling dirt road stretches east and west, disappearing into the warped horizon. A rusted, overturned car lies nearby.",
            exits={"west": "L:HSE_STRT", "east": "L:CROSSROADS_01"},
            environmental_elements=["overturned car", "broken asphalt"],
            potential_ground_items_rules={"item_tags": ["junk", "material", "low_tier"], "min_items": 0, "max_items": 2}
        )
        self.generated_locations[old_dirt_road.location_id] = old_dirt_road

        # Generate a key and place it
        shed_key_item = self._create_item_instance("rusty_key")
        backyard_shed_container.requires_key_id = shed_key_item.item_id
        abandoned_house.add_item_on_ground(shed_key_item)

        player.current_location_id = abandoned_house.location_id
        print("--- World Generation Complete ---")
        return abandoned_house, player

# --- New: WorldManager Class ---
class WorldManager:
    SAVE_DIR = "save_data"
    PLAYER_FILE = os.path.join(SAVE_DIR, "player.json")
    LOCATIONS_DIR = os.path.join(SAVE_DIR, "locations")
    CONTAINERS_DIR = os.path.join(SAVE_DIR, "containers")

    def __init__(self):
        self.player: Player = None
        self.current_location: Location = None
        self.locations: dict[str, Location] = {}  # Map location_id to Location object
        self.containers: dict[str, Container] = {}  # Map container_id to Container object
        self.world_generator = WorldGenerator(ITEM_TEMPLATES_FOR_GENERATION)

    def _create_save_directories(self):
        os.makedirs(self.SAVE_DIR, exist_ok=True)
        os.makedirs(self.LOCATIONS_DIR, exist_ok=True)
        os.makedirs(self.CONTAINERS_DIR, exist_ok=True)

    def new_game(self):
        """Initializes a new game state."""
        self._create_save_directories()
        self.current_location, self.player = self.world_generator.create_initial_world()
        
        # Populate internal dictionaries from the generator's output
        for loc_id, loc_obj in self.world_generator.generated_locations.items():
            self.locations[loc_id] = loc_obj
            for container in loc_obj.containers:
                self.containers[container.container_id] = container

        print(f"New game started. Player at: {self.current_location.name}")
        # Generate initial ground items for the starting location
        self.world_generator.generate_random_ground_items(self.current_location)
        self.current_location.has_been_visited = True # Mark starting location as visited
        return True

    def load_game(self) -> bool:
        """Loads game state from save files."""
        if not os.path.exists(self.PLAYER_FILE):
            print("No saved game found to load.")
            return False

        print("--- Loading Game ---")
        # Load Player
        with open(self.PLAYER_FILE, 'r') as f:
            player_data = json.load(f)
            self.player = Player.from_dict(player_data)
        
        # Load Locations
        for filename in os.listdir(self.LOCATIONS_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(self.LOCATIONS_DIR, filename)
                with open(filepath, 'r') as f:
                    loc_data = json.load(f)
                    location = Location.from_dict(loc_data)
                    self.locations[location.location_id] = location
        
        # Load Containers (and link them back to their parent locations)
        # We need to load all containers globally first, then update location/player references
        for filename in os.listdir(self.CONTAINERS_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(self.CONTAINERS_DIR, filename)
                with open(filepath, 'r') as f:
                    container_data = json.load(f)
                    container = Container.from_dict(container_data)
                    self.containers[container.container_id] = container
        
        # Now that all containers are loaded, relink them into their parent locations
        for loc in self.locations.values():
            new_container_list = []
            for loaded_container_data in loc_data.get("containers", []): # Use the raw loaded data to match IDs
                container_id = loaded_container_data["container_id"]
                if container_id in self.containers:
                    new_container_list.append(self.containers[container_id])
                else:
                    print(f"Warning: Container {container_id} not found during relinking for location {loc.location_id}")
            loc.containers = new_container_list # Replace with actual object references
        
        # Set current location based on player's last known location
        self.current_location = self.locations.get(self.player.current_location_id)
        if not self.current_location:
            print(f"Error: Player's last known location '{self.player.current_location_id}' not found.")
            return False

        print(f"Game loaded. Player at: {self.current_location.name}")
        return True

    def save_game(self):
        """Saves the current game state to files."""
        self._create_save_directories()
        print("--- Saving Game ---")

        # Save Player
        with open(self.PLAYER_FILE, 'w') as f:
            json.dump(self.player.to_dict(), f, indent=4)
        
        # Save Locations
        for loc_id, location in self.locations.items():
            filepath = os.path.join(self.LOCATIONS_DIR, f"{loc_id}.json")
            with open(filepath, 'w') as f:
                json.dump(location.to_dict(), f, indent=4)
        
        # Save Containers (only save top-level containers that are tracked directly)
        # Note: Containers are also saved nested within locations. If a container exists in both,
        # the global `self.containers` list is the definitive one to iterate for saving unique instances.
        # This prevents duplicate files if a container is explicitly placed in `self.containers` and also linked to a location.
        for container_id, container in self.containers.items():
             filepath = os.path.join(self.CONTAINERS_DIR, f"{container_id}.json")
             with open(filepath, 'w') as f:
                 json.dump(container.to_dict(), f, indent=4)
        
        print("Game saved successfully.")

    def get_location(self, location_id: str) -> Location | None:
        """Retrieves a location by its ID."""
        return self.locations.get(location_id)

    def get_container(self, container_id: str) -> Container | None:
        """Retrieves a container by its ID."""
        return self.containers.get(container_id)

    # --- Methods for Game Engine to interact with WorldManager ---
    def move_player(self, direction: str) -> bool:
        """Attempts to move the player in a given direction."""
        target_location_id = self.current_location.exits.get(direction)
        if target_location_id:
            next_location = self.get_location(target_location_id)
            if next_location:
                self.player.current_location_id = target_location_id
                self.current_location = next_location
                self.player.perform_action() # Moving is an action
                print(f"You move {direction} to the {self.current_location.name}.")
                
                # Generate ground items if first visit to new location
                self.world_generator.generate_random_ground_items(self.current_location)
                if not self.current_location.has_been_visited:
                    self.current_location.has_been_visited = True # Mark as visited
                return True
            else:
                print(f"The path to the {direction} leads to an unknown area (ID: {target_location_id}).")
                return False
        else:
            print(f"There is no exit to the {direction} from here.")
            return False

    def look_around(self):
        """Provides a description of the current location."""
        # Ensure ground items are generated if not already
        self.world_generator.generate_random_ground_items(self.current_location)
        print(self.current_location.get_description(self.current_location.has_been_visited))
        self.player.perform_action()

    def search_container(self, container_name_or_id: str):
        """Searches a container in the current location."""
        container = self.current_location.find_container(container_name_or_id)
        if container:
            if container.is_locked:
                print(f"The {container.name} is locked.")
                # Future: check if player has key and try to unlock
            else:
                # Generate contents on first search
                self.world_generator.generate_random_container_contents(container)
                print(container.get_inventory_description())
            self.player.perform_action()
        else:
            print(f"You don't see a '{container_name_or_id}' here.")

    def take_item_from_ground(self, item_name_or_id: str):
        """Player attempts to take an item from the ground."""
        item = self.current_location.remove_item_on_ground(item_name_or_id)
        if item:
            self.player.add_item(item)
            print(f"You pick up the {item.name}.")
            self.player.perform_action()
        else:
            print(f"You don't see '{item_name_or_id}' on the ground here.")

    def take_item_from_container(self, item_name_or_id: str, container_name_or_id: str):
        """Player attempts to take an item from a container."""
        container = self.current_location.find_container(container_name_or_id)
        if not container:
            print(f"You don't see a '{container_name_or_id}' here.")
            return
        
        if container.is_locked:
            print(f"The {container.name} is locked. You can't take anything from it.")
            return

        item = container.remove_item(item_name_or_id)
        if item:
            self.player.add_item(item)
            print(f"You take the {item.name} from the {container.name}.")
            self.player.perform_action()
        else:
            print(f"There is no '{item_name_or_id}' in the {container.name}.")

    def drop_item(self, item_name_or_id: str):
        """Player drops an item from their inventory onto the ground."""
        item = self.player.remove_item(item_name_or_id)
        if item:
            self.current_location.add_item_on_ground(item)
            print(f"You drop the {item.name} onto the ground.")
            self.player.perform_action()
        else:
            print(f"You don't have '{item_name_or_id}' in your inventory to drop.")


# --- CommandParser Class (from previous step) ---
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
            "attack": ["attack", "hit", "strike", "fight", "kill"],
            "trip": ["trip"],
            "inventory": ["inventory", "inv", "i"],
            "stats": ["stats", "status", "check stats", "my stats"],
            "help": ["help", "?"],
            "quit": ["quit", "exit", "q"],
            "eat": ["eat", "consume"],
            "drink": ["drink", "quaff"]
        }
        self.directions = ["north", "south", "east", "west", "up", "down", "n", "s", "e", "w", "u", "d"]
        self.stop_words = ["a", "an", "the", "and", "but", "for", "of", "my", "your", "in"] # added 'in' as stop word for parser flexibility
        self.prepositions = ["in", "on", "at", "from", "to", "with", "behind", "under", "over"]

        self._canonical_verbs = {}
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
        
        if main_verb == "go" and not direct_object_parts and verb_start_index == 0 and tokens[0] in self.directions:
            direct_object_parts.append(tokens[0])

        return {
            "verb": main_verb,
            "direct_object": " ".join(direct_object_parts).strip() if direct_object_parts else None,
            "preposition": preposition_found,
            "indirect_object": " ".join(indirect_object_parts).strip() if indirect_object_parts else None,
            "raw_command": original_command
        }

# --- GameEngine (to use WorldManager) ---
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
        
        # Display initial status
        print("\n" + "="*40)
        print(f"Welcome, {self.world_manager.player.name}!")
        self.world_manager.look_around()
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
        elif verb == "look":
            self.world_manager.look_around()
        elif verb == "go":
            self.world_manager.move_player(do)
        elif verb == "inventory":
            print(self.world_manager.player.get_inventory_string())
        elif verb == "stats":
            self.world_manager.player.display_stats()
        elif verb == "take":
            if do and not io: # "take [item]"
                self.world_manager.take_item_from_ground(do)
            elif do and io: # "take [item] from [container]"
                self.world_manager.take_item_from_container(do, io)
            else:
                print("What do you want to take?")
        elif verb == "drop":
            self.world_manager.drop_item(do)
        elif verb == "search":
            if do: # "search [container]" or "search area"
                if do == "area":
                    self.world_manager.look_around() # Searching the area is like a detailed look
                else:
                    self.world_manager.search_container(do)
            else:
                self.world_manager.look_around()
        elif verb == "open":
            if do: # "open [container]"
                container = self.world_manager.current_location.find_container(do)
                if container:
                    if container.is_locked:
                        if prep == "with" and io:
                            key_item = self.world_manager.player.find_item(io)
                            if key_item and key_item.item_id == container.requires_key_id:
                                container.is_locked = False
                                print(f"You unlock the {container.name} with the {key_item.name}.")
                                self.world_manager.search_container(container.name) # Show contents after unlocking
                            else:
                                print(f"You try to open the {container.name} with the {io}, but it doesn't work.")
                        else:
                            print(f"The {container.name} is locked. You need a key.")
                    else:
                        self.world_manager.search_container(do)
                else:
                    print(f"You can't open a '{do}' here.")
            else:
                print("What do you want to open?")
        elif verb == "eat":
            self.world_manager.player.consume_item(do)
        elif verb == "drink":
            self.world_manager.player.consume_item(do)
        elif verb == "use":
            if do and prep == "on" and io: # "use [item] on [target]"
                self.world_manager.player.use_item(do, target=io)
            else:
                self.world_manager.player.use_item(do) # Generic use
        else:
            print(f"Command '{command_str}' ({verb}) not yet implemented.")
        
        # After every action, check if player stats need to be displayed (every 20 actions)
        if self.world_manager.player.action_counter % 20 == 0:
            self.world_manager.player.display_stats()

    def game_loop(self):
        while self.is_running:
            try:
                command = input("> ").strip()
                if not command:
                    continue
                self.handle_command(command)
                if not self.is_running: # Check again after command handling
                    break
            except KeyboardInterrupt:
                print("\nInterrupted. Saving game...")
                self.world_manager.save_game()
                self.is_running = False
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                # Optionally, save game in case of error
                self.world_manager.save_game()
                self.is_running = False


# --- Example Usage ---
if __name__ == "__main__":
    # Clean up previous save data for a fresh start in example
    if os.path.exists(WorldManager.SAVE_DIR):
        shutil.rmtree(WorldManager.SAVE_DIR)
        print(f"Removed old save data from {WorldManager.SAVE_DIR}.")

    game = GameEngine()

    # To start a new game:
    game.start_game(load_game=False)

    # To attempt to load a game:
    # game.start_game(load_game=True)

    # Example of a few commands to test functionality
    print("\n--- Example Gameplay ---")
    print("Try typing commands like:")
    print("  'look'")
    print("  'inventory'")
    print("  'go south'")
    print("  'take rusty key'")
    print("  'go north'")
    print("  'go south'") # Back to garage
    print("  'open backyard shed with rusty key'")
    print("  'take machete from backyard shed'")
    print("  'stats'")
    print("  'save'") # You can try to implement a 'save' command in GameEngine
    print("  'quit'")

    game.game_loop()
    print("Exited game loop.")
    game.world_manager.save_game() # Ensure save on graceful exit