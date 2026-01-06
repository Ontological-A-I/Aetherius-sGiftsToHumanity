import uuid
import json
from enum import Enum, auto

# --- Enums and Utility Classes (as previously defined) ---
class ItemType(Enum):
    FOOD = auto()
    WATER = auto()
    WEAPON = auto()
    TOOL = auto()
    CONSUMABLE = auto()
    JUNK = auto()
    MATERIAL = auto() # Added for building/crafting
    # Add more as needed

class BodyPartStatus(Enum):
    UNINJURED = auto()
    GRAZED = auto()
    WOUNDED = auto()
    BROKEN = auto()
    SEVERE_BLEEDING = auto()
    SEVERED = auto()

# --- SQT-like ItemID Generation Helper ---
def _generate_item_sqt_id(item_type: ItemType, name: str, properties: dict = None) -> str:
    """
    Generates an SQT-like unique identifier for an item.
    Format: [I/If]:[NAME_ABBR]_[PROPS]_[UNIQUE_SUFFIX]
    Example: If:APL_P:HR150_HLT5_A3C1F5
             I:MCH_P:DMG30_DUR100_B8D2E1
    """
    # 1. Prefix based on item type
    prefix = ""
    if item_type in [ItemType.FOOD, ItemType.WATER, ItemType.CONSUMABLE]: # Consumables also often interact with stats
        prefix = "If"
    else:
        prefix = "I"

    # 2. Abbreviated Name (first 3-5 letters, uppercase)
    name_abbr = "".join(filter(str.isalnum, name)).upper()[:5]
    if not name_abbr: # Fallback if name is empty or only special chars
        name_abbr = "GENERIC"

    # 3. Properties String
    prop_parts = []
    if properties:
        # Example properties we might encode
        if 'hunger_restore' in properties: prop_parts.append(f"HR{properties['hunger_restore']}")
        if 'hydration_restore' in properties: prop_parts.append(f"HYR{properties['hydration_restore']}")
        if 'damage' in properties: prop_parts.append(f"DMG{properties['damage']}")
        if 'health_restore' in properties: prop_parts.append(f"HLT{properties['health_restore']}")
        if 'durability' in properties: prop_parts.append(f"DUR{properties['durability']}")
        if 'weight_mod' in properties: prop_parts.append(f"WM{properties['weight_mod']}")
        # Add more property types as our item system grows

    props_str = ""
    if prop_parts:
        props_str = "_" + "_".join(f"P:{p}" for p in prop_parts)

    # 4. Unique Suffix
    unique_suffix = uuid.uuid4().hex[:6].upper() # 6 characters for sufficient uniqueness

    return f"{prefix}:{name_abbr}{props_str}_{unique_suffix}"

# --- Item Class Definition (Revised) ---
class Item:
    """Represents a generic item in the game world."""
    def __init__(self, name: str, description: str, weight: float, item_type: ItemType, properties: dict = None, item_id: str = None):
        self.name = name
        self.description = description
        self.weight = weight # in arbitrary units, e.g., kg
        self.item_type = item_type
        self.properties = properties if properties is not None else {}

        # Generate SQT-like ID if not provided (for new items)
        if item_id is None:
            self.item_id = _generate_item_sqt_id(item_type, name, self.properties)
        else:
            self.item_id = item_id # Use provided ID (for loading from save)

    def to_dict(self):
        return {
            "item_id": self.item_id,
            "name": self.name,
            "description": self.description,
            "weight": self.weight,
            "item_type": self.item_type.name, # Store enum name
            "properties": self.properties
        }

    @classmethod
    def from_dict(cls, data: dict):
        # When loading, we pass the existing item_id directly
        return cls(
            item_id=data["item_id"],
            name=data["name"],
            description=data["description"],
            weight=data["weight"],
            item_type=ItemType[data["item_type"]], # Load enum from name
            properties=data.get("properties")
        )

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Item(id='{self.item_id}', name='{self.name}', type={self.item_type.name})"

# --- BodyPart Class (as previously defined) ---
class BodyPart:
    """Represents a specific body part of a character."""
    def __init__(self, name: str, max_health: int, current_health: int = None, status: BodyPartStatus = BodyPartStatus.UNINJURED):
        self.name = name
        self.max_health = max_health
        self.current_health = current_health if current_health is not None else max_health
        self.status = status

    def take_damage(self, amount: int):
        self.current_health -= amount
        if self.current_health <= 0:
            self.current_health = 0
            if self.name == "throat":
                self.status = BodyPartStatus.SEVERED
            elif self.current_health <= -self.max_health * 0.5:
                self.status = BodyPartStatus.SEVERED
            elif self.current_health <= self.max_health * 0.1:
                self.status = BodyPartStatus.BROKEN
            elif self.current_health <= self.max_health * 0.5:
                self.status = BodyPartStatus.WOUNDED
            elif self.current_health < self.max_health:
                self.status = BodyPartStatus.GRAZED
        elif self.status == BodyPartStatus.UNINJURED:
            self.status = BodyPartStatus.GRAZED

    def heal(self, amount: int):
        self.current_health += amount
        if self.current_health > self.max_health:
            self.current_health = self.max_health
        if self.current_health == self.max_health and self.status != BodyPartStatus.SEVERED:
            self.status = BodyPartStatus.UNINJURED

    def is_crippled(self):
        return self.status in [BodyPartStatus.BROKEN, BodyPartStatus.SEVERED]

    def to_dict(self):
        return {
            "name": self.name,
            "max_health": self.max_health,
            "current_health": self.current_health,
            "status": self.status.name
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data["name"],
            max_health=data["max_health"],
            current_health=data["current_health"],
            status=BodyPartStatus[data["status"]]
        )

    def __str__(self):
        return f"{self.name} ({self.status.name}, {self.current_health}/{self.max_health})"


# --- Player Class Definition (Remains the same as before, uses the new Item class) ---
class Player:
    """
    Represents the player character, managing stats, inventory, body parts,
    and the action-based time system.
    """
    def __init__(self,
                 name: str = "Player",
                 current_location_id: str = "starting_area",
                 age: int = 30,
                 weight: float = 75.0,
                 health: int = 100,
                 hunger_level: int = 1000,
                 hydration_level: int = 1000,
                 sanity_level: int = 1000,
                 stamina_level: int = 100,
                 action_counter: int = 0,
                 inventory_items: list = None,
                 initial_body_parts: dict = None):

        self.name = name
        self.current_location_id = current_location_id
        self.age = age
        self.weight = weight

        self.health = health
        self.hunger_level = hunger_level
        self.hydration_level = hydration_level
        self.sanity_level = sanity_level
        self.stamina_level = stamina_level

        self.action_counter = action_counter

        self.inventory = inventory_items if inventory_items is not None else []
        self.body_parts = initial_body_parts if initial_body_parts is not None else self._initialize_default_body_parts()
        self.nested_containers = {}

    def _initialize_default_body_parts(self):
        return {
            "head": BodyPart("head", 50),
            "torso": BodyPart("torso", 100),
            "left_arm": BodyPart("left_arm", 70),
            "right_arm": BodyPart("right_arm", 70),
            "left_leg": BodyPart("left_leg", 80),
            "right_leg": BodyPart("right_leg", 80),
            "throat": BodyPart("throat", 20)
        }

    def perform_action(self, action_cost: int = 1):
        self.action_counter += action_cost

        self.hunger_level -= action_cost * 1
        if self.hunger_level < 0:
            self.hunger_level = 0
            self.health -= 5 * action_cost

        self.hydration_level -= action_cost * 2
        if self.hydration_level < 0:
            self.hydration_level = 0
            self.health -= 10 * action_cost

        if self.hunger_level < 200 or self.hydration_level < 200:
            self.sanity_level -= action_cost * 0.5

        if action_cost == 1:
            self.stamina_level += 1
            if self.stamina_level > 100: self.stamina_level = 100

        if self.health <= 0 or self.hunger_level <= 0 or self.hydration_level <= 0:
            print(f"{self.name} has succumbed to their fate.")
            return False
        
        if self.body_parts["throat"].status == BodyPartStatus.SEVERED:
             print(f"{self.name}'s throat has been critically damaged. They die.")
             return False

        return True

    def display_stats(self):
        print(f"\n--- {self.name}'s Status (Actions: {self.action_counter}) ---")
        print(f"Health: {self.health}/100")
        print(f"Hunger: {self.hunger_level}/1000 ({'Starving' if self.hunger_level < 200 else 'Hungry' if self.hunger_level < 500 else 'Satiated'})")
        print(f"Hydration: {self.hydration_level}/1000 ({'Dehydrated' if self.hydration_level < 200 else 'Thirsty' if self.hydration_level < 500 else 'Hydrated'})")
        print(f"Sanity: {self.sanity_level}/1000 ({'Breaking' if self.sanity_level < 200 else 'Unsettled' if self.sanity_level < 500 else 'Stable'})")
        print(f"Stamina: {self.stamina_level}/100")
        print("Body Parts:")
        for part_name, part in self.body_parts.items():
            print(f"  - {part}")
        print("--------------------------------------")

    def take_damage(self, body_part_name: str, amount: int, damage_type: str = "generic"):
        if body_part_name in self.body_parts:
            part = self.body_parts[body_part_name]
            part.take_damage(amount)
            self.health -= amount
            print(f"You took {amount} damage to your {body_part_name}. Status: {part.status.name}")
            if part.status == BodyPartStatus.SEVERED:
                self.health = 0
        else:
            print(f"Warning: Attempted to damage unknown body part '{body_part_name}'.")
            self.health -= amount

    def heal(self, body_part_name: str, amount: int):
        if body_part_name in self.body_parts:
            part = self.body_parts[body_part_name]
            part.heal(amount)
            self.health += amount
            if self.health > 100: self.health = 100
            print(f"You healed {amount} to your {body_part_name}. Status: {part.status.name}")
        else:
            print(f"Warning: Attempted to heal unknown body part '{body_part_name}'.")
            self.health += amount

    def add_item(self, item: Item):
        self.inventory.append(item)
        print(f"You picked up a {item.name}.")

    def remove_item(self, item_id: str) -> Item | None:
        for i, item in enumerate(self.inventory):
            if item.item_id == item_id:
                return self.inventory.pop(i)
        print(f"You don't have an item with ID {item_id}.")
        return None

    def find_item(self, item_name_or_id: str) -> Item | None:
        for item in self.inventory:
            # Check by full ID or by name (case-insensitive)
            if item.item_id == item_name_or_id or item.name.lower() == item_name_or_id.lower():
                return item
            # Also allow partial SQT ID matching (e.g., If:APL) if that becomes a feature
            if item_name_or_id.upper() in item.item_id.split('_')[0]: # e.g., 'APL' in 'If:APL...'
                return item
        return None

    def consume_item(self, item_id: str):
        item = self.find_item(item_id)
        if not item:
            print(f"You don't have an item with ID or name '{item_id}' to consume.")
            return

        if item.item_type in [ItemType.FOOD, ItemType.WATER, ItemType.CONSUMABLE]:
            if 'hunger_restore' in item.properties:
                self.hunger_level = min(1000, self.hunger_level + item.properties['hunger_restore'])
                print(f"You ate the {item.name} and felt less hungry.")
            if 'hydration_restore' in item.properties:
                self.hydration_level = min(1000, self.hydration_level + item.properties['hydration_restore'])
                print(f"You drank the {item.name} and felt refreshed.")
            if 'health_restore' in item.properties:
                self.health = min(100, self.health + item.properties['health_restore'])
                print(f"You used the {item.name} and felt a bit better.")
            if 'sanity_restore' in item.properties:
                self.sanity_level = min(1000, self.sanity_level + item.properties['sanity_restore'])
                print(f"You used the {item.name} and felt a wave of calm.")
            
            self.remove_item(item.item_id)
            self.perform_action() # Consuming an item is an action
        else:
            print(f"You can't consume the {item.name}.")

    def use_item(self, item_id: str, target=None):
        item = self.find_item(item_id)
        if not item:
            print(f"You don't have an item with ID or name '{item_id}' to use.")
            return

        print(f"You used the {item.name}.")
        self.perform_action() # Using an item costs an action
        
        # Example of specific usage, like a bandage healing a body part
        if item.item_type == ItemType.CONSUMABLE and 'health_restore' in item.properties and 'heal_body_part_type' in item.properties:
            # Assuming 'target' here is the body part name string
            if target and target in self.body_parts:
                self.heal(target, item.properties['health_restore'])
                self.remove_item(item.item_id)
            else:
                print(f"You need to specify which body part to use the {item.name} on. (e.g., 'use bandage on left_arm')")
        elif item.item_type == ItemType.WEAPON:
            print(f"You are now ready to wield the {item.name}.") # Equipping logic later
        else:
            print(f"The {item.name} doesn't seem to have a direct 'use' action here.")


    def get_inventory_string(self):
        if not self.inventory:
            return "Your inventory is empty."
        inv_str = "Your inventory (i):\n"
        for item in self.inventory:
            # Display format: Name (ITEM_ID_SHORT)
            # We'll extract the unique_suffix for a shorter display in inventory, as you suggested
            short_id = item.item_id.split('_')[-1] # Gets the last part of the SQT
            inv_str += f"- {item.name} ({item.item_type.name[0]}:{short_id})\n" # e.g., M:A3C1F5 for material, F:A3C1F5 for food
        return inv_str


    def to_dict(self):
        return {
            "name": self.name,
            "current_location_id": self.current_location_id,
            "age": self.age,
            "weight": self.weight,
            "health": self.health,
            "hunger_level": self.hunger_level,
            "hydration_level": self.hydration_level,
            "sanity_level": self.sanity_level,
            "stamina_level": self.stamina_level,
            "action_counter": self.action_counter,
            "inventory": [item.to_dict() for item in self.inventory],
            "body_parts": {name: part.to_dict() for name, part in self.body_parts.items()},
        }

    @classmethod
    def from_dict(cls, data: dict):
        player = cls(
            name=data["name"],
            current_location_id=data["current_location_id"],
            age=data.get("age", 30),
            weight=data.get("weight", 75.0),
            health=data["health"],
            hunger_level=data["hunger_level"],
            hydration_level=data["hydration_level"],
            sanity_level=data["sanity_level"],
            stamina_level=data["stamina_level"],
            action_counter=data["action_counter"],
            inventory_items=[Item.from_dict(item_data) for item_data in data["inventory"]],
            initial_body_parts={name: BodyPart.from_dict(part_data) for name, part_data in data["body_parts"].items()}
        )
        return player

# --- Example Usage (for testing with new IDs) ---
if __name__ == "__main__":
    # Create some items using the new ID generation
    machete = Item(name="Machete", description="A heavy-bladed tool for hacking.", weight=2.0, item_type=ItemType.WEAPON, properties={'damage': 30, 'durability': 100})
    apple = Item(name="Apple", description="A slightly bruised apple.", weight=0.2, item_type=ItemType.FOOD, properties={'hunger_restore': 150, 'health_restore': 5})
    water_bottle = Item(name="Water Bottle", description="A half-full bottle of water.", weight=0.5, item_type=ItemType.WATER, properties={'hydration_restore': 300})
    useless_rock = Item(name="Useless Rock", description="Just a rock. Heavy.", weight=1.0, item_type=ItemType.JUNK)
    bandage = Item(name="Bandage", description="For minor cuts and scrapes.", weight=0.1, item_type=ItemType.CONSUMABLE, properties={'health_restore': 10, 'heal_body_part_type': 'wound'})
    wood_plank = Item(name="Wood Plank", description="A sturdy piece of wood.", weight=1.5, item_type=ItemType.MATERIAL)


    # Initialize Player with some items
    player = Player(name="Aetherius Survivor", initial_body_parts={
        "head": BodyPart("head", 50),
        "torso": BodyPart("torso", 100),
        "left_arm": BodyPart("left_arm", 70, current_health=50, status=BodyPartStatus.WOUNDED),
        "right_arm": BodyPart("right_arm", 70),
        "left_leg": BodyPart("left_leg", 80),
        "right_leg": BodyPart("right_leg", 80),
        "throat": BodyPart("throat", 20)
    })
    player.add_item(machete)
    player.add_item(apple)
    player.add_item(water_bottle)
    player.add_item(useless_rock)
    player.add_item(bandage)
    player.add_item(wood_plank)


    player.display_stats()
    print(player.get_inventory_string())

    # Simulate some actions
    print("\n--- Simulating Actions ---")
    for _ in range(5):
        print(f"\nAction {_ + 1}: Moving...")
        if not player.perform_action():
            break
        if _ == 2:
            player.take_damage("left_leg", 15)
        if player.action_counter % 20 == 0:
            player.display_stats()

    print("\n--- Consuming Items ---")
    player.consume_item(apple.item_id) # Using the generated SQT ID
    player.consume_item(water_bottle.item_id)
    player.use_item(bandage.item_id, target="left_arm") # Use bandage on specific arm
    player.display_stats()
    print(player.get_inventory_string())

    print("\n--- Simulating Prolonged Survival ---")
    for i in range(500):
        if not player.perform_action():
            print("Player died during prolonged actions.")
            break
        if i % 100 == 0:
            player.display_stats()

    player.display_stats()

    print("\n--- Simulating Critical Injury (Throat) ---")
    if player.health > 0:
        player.take_damage("throat", 25)
        player.perform_action()
    player.display_stats()

    print("\n--- Saving and Loading ---")
    player_data = player.to_dict()
    # print(json.dumps(player_data, indent=4))

    loaded_player = Player.from_dict(player_data)
    print("\n--- Loaded Player Stats ---")
    loaded_player.display_stats()
    print(loaded_player.get_inventory_string())
    assert loaded_player.name == player.name
    assert loaded_player.action_counter == player.action_counter
    assert loaded_player.health == player.health
    print("Player save/load successful with SQT-like ItemIDs!")
    print(f"Example SQT ItemID: {machete.item_id}")
    print(f"Example SQT Food/Consumable ItemID: {apple.item_id}")