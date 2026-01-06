import uuid
import json
from enum import Enum, auto

# --- Enums and Utility Classes (to be defined later or in separate modules) ---
# Placeholder for now, we'll refine these
class ItemType(Enum):
    FOOD = auto()
    WATER = auto()
    WEAPON = auto()
    TOOL = auto()
    CONSUMABLE = auto()
    JUNK = auto()
    # Add more as needed

class BodyPartStatus(Enum):
    UNINJURED = auto()
    GRAZED = auto()
    WOUNDED = auto()
    BROKEN = auto()
    SEVERE_BLEEDING = auto()
    SEVERED = auto()
    # Add more specific statuses like 'Infected', 'Concussed'

class Item:
    """Represents a generic item in the game world."""
    def __init__(self, item_id: str, name: str, description: str, weight: float, item_type: ItemType, properties: dict = None):
        self.item_id = item_id # I{itemID} format
        self.name = name
        self.description = description
        self.weight = weight # in arbitrary units, e.g., kg
        self.item_type = item_type
        self.properties = properties if properties is not None else {} # e.g., {'healing': 20, 'damage': 15}

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
            # Logic to update status, e.g., broken, severed, etc.
            # This would be more complex based on damage type and location
            if self.name == "throat":
                self.status = BodyPartStatus.SEVERED # Instant death
            elif self.current_health <= -self.max_health * 0.5: # Severe damage threshold
                self.status = BodyPartStatus.SEVERED # Or equivalent
            elif self.current_health <= self.max_health * 0.1:
                self.status = BodyPartStatus.BROKEN
            elif self.current_health <= self.max_health * 0.5:
                self.status = BodyPartStatus.WOUNDED
            elif self.current_health < self.max_health:
                self.status = BodyPartStatus.GRAZED
        elif self.status == BodyPartStatus.UNINJURED:
            self.status = BodyPartStatus.GRAZED # First damage applies a graze

    def heal(self, amount: int):
        self.current_health += amount
        if self.current_health > self.max_health:
            self.current_health = self.max_health
        # Logic to update status based on healing, e.g., if fully healed, become UNINJURED
        if self.current_health == self.max_health and self.status != BodyPartStatus.SEVERED:
            self.status = BodyPartStatus.UNINJURED

    def is_crippled(self):
        """Returns true if the body part is severely impaired."""
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


# --- Player Class Definition ---
class Player:
    """
    Represents the player character, managing stats, inventory, body parts,
    and the action-based time system.
    """
    def __init__(self,
                 name: str = "Player",
                 current_location_id: str = "starting_area",
                 age: int = 30, # Initial age attribute
                 weight: float = 75.0, # Initial weight attribute (kg)
                 health: int = 100,
                 hunger_level: int = 1000, # 1000 = full, 0 = death
                 hydration_level: int = 1000, # 1000 = full, 0 = death
                 sanity_level: int = 1000, # 1000 = stable, 0 = severe mental break
                 stamina_level: int = 100, # 100 = full, 0 = exhausted
                 action_counter: int = 0, # Tracks actions for time progression
                 inventory_items: list = None,
                 initial_body_parts: dict = None):

        self.name = name
        self.current_location_id = current_location_id
        self.age = age
        self.weight = weight

        # Core Survival Stats
        self.health = health
        self.hunger_level = hunger_level
        self.hydration_level = hydration_level
        self.sanity_level = sanity_level
        self.stamina_level = stamina_level

        # Action-based time progression
        self.action_counter = action_counter

        # Inventory (list of Item objects)
        self.inventory = inventory_items if inventory_items is not None else []
        # Potentially: self.max_inventory_weight, self.max_inventory_slots

        # Body Part System
        self.body_parts = initial_body_parts if initial_body_parts is not None else self._initialize_default_body_parts()

        # Placeholders for nested containers like 'backpack', 'pockets'
        self.nested_containers = {} # e.g., {'s_backpack': Container('backpack_id', 'Backpack', [], ...)}


    def _initialize_default_body_parts(self):
        """Initializes a default set of body parts for the player."""
        return {
            "head": BodyPart("head", 50),
            "torso": BodyPart("torso", 100),
            "left_arm": BodyPart("left_arm", 70),
            "right_arm": BodyPart("right_arm", 70),
            "left_leg": BodyPart("left_leg", 80),
            "right_leg": BodyPart("right_leg", 80),
            "throat": BodyPart("throat", 20) # Vulnerable, critical part
        }

    def perform_action(self, action_cost: int = 1):
        """
        Decrements survival stats based on actions taken and checks for thresholds.
        This is the core 'time-passing' mechanism.
        """
        self.action_counter += action_cost

        # Hunger decay (1000 actions to brink of death)
        self.hunger_level -= action_cost * 1 # Adjust multiplier for desired difficulty
        if self.hunger_level < 0:
            self.hunger_level = 0
            # Apply health damage or other severe debuffs
            self.health -= 5 * action_cost # Placeholder for sustained starvation damage

        # Hydration decay (850 actions to death if 1000 is max)
        self.hydration_level -= action_cost * 2 # Hydration decays faster
        if self.hydration_level < 0:
            self.hydration_level = 0
            # Apply health damage or other severe debuffs
            self.health -= 10 * action_cost # Placeholder for sustained dehydration damage

        # Sanity check (influenced by hunger/hydration imbalance)
        # More complex sanity drain will happen with events/environment
        if self.hunger_level < 200 or self.hydration_level < 200:
            self.sanity_level -= action_cost * 0.5 # Minor sanity drain from discomfort

        # Stamina regeneration (or decay if action is strenuous)
        # For simplicity, let's assume passive regen and active drain by specific actions
        if action_cost == 1: # Standard action, mild stamina regen
            self.stamina_level += 1
            if self.stamina_level > 100: self.stamina_level = 100
        # Strenuous actions (e.g., 'run', 'fight') would call perform_action with a negative stamina impact

        # Check for death conditions
        if self.health <= 0 or self.hunger_level <= 0 or self.hydration_level <= 0:
            print(f"{self.name} has succumbed to their fate.")
            # Trigger game over or revival logic
            return False # Indicate player is no longer active
        
        # Check for critical body part statuses for instant death (e.g., throat)
        if self.body_parts["throat"].status == BodyPartStatus.SEVERED:
             print(f"{self.name}'s throat has been critically damaged. They die.")
             return False

        return True # Indicate player is still active

    def display_stats(self):
        """Prints the player's current vital statistics."""
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
        """Applies damage to a specific body part and updates overall health."""
        if body_part_name in self.body_parts:
            part = self.body_parts[body_part_name]
            # Convert damage to a percentage of max health for the part, or absolute
            part.take_damage(amount)
            self.health -= amount # Overall health also takes a hit for simplicity
            print(f"You took {amount} damage to your {body_part_name}. Status: {part.status.name}")
            # If the body part status is critical, apply additional penalties or death
            if part.status == BodyPartStatus.SEVERED:
                self.health = 0 # Instant kill
        else:
            print(f"Warning: Attempted to damage unknown body part '{body_part_name}'.")
            self.health -= amount # Apply to overall health anyway

    def heal(self, body_part_name: str, amount: int):
        """Heals a specific body part and updates overall health."""
        if body_part_name in self.body_parts:
            part = self.body_parts[body_part_name]
            part.heal(amount)
            self.health += amount # Overall health also recovers
            if self.health > 100: self.health = 100 # Cap health at max
            print(f"You healed {amount} to your {body_part_name}. Status: {part.status.name}")
        else:
            print(f"Warning: Attempted to heal unknown body part '{body_part_name}'.")
            self.health += amount # Apply to overall health anyway

    def add_item(self, item: Item):
        """Adds an item to the player's inventory."""
        self.inventory.append(item)
        print(f"You picked up a {item.name}.")

    def remove_item(self, item_id: str) -> Item | None:
        """Removes an item from the player's inventory by its ID."""
        for i, item in enumerate(self.inventory):
            if item.item_id == item_id:
                return self.inventory.pop(i)
        print(f"You don't have an item with ID {item_id}.")
        return None

    def find_item(self, item_name_or_id: str) -> Item | None:
        """Finds an item in the player's inventory by name or ID (case-insensitive for name)."""
        for item in self.inventory:
            if item.item_id == item_name_or_id or item.name.lower() == item_name_or_id.lower():
                return item
        return None

    def consume_item(self, item_id: str):
        """Consumes an item from inventory, applying its effects."""
        item = self.find_item(item_id)
        if not item:
            print(f"You don't have an item with ID or name '{item_id}' to consume.")
            return

        if item.item_type == ItemType.FOOD:
            if 'hunger_restore' in item.properties:
                self.hunger_level = min(1000, self.hunger_level + item.properties['hunger_restore'])
                print(f"You ate the {item.name} and felt less hungry.")
            if 'health_restore' in item.properties:
                self.health = min(100, self.health + item.properties['health_restore'])
                print(f"You ate the {item.name} and felt a bit better.")
            if 'sanity_restore' in item.properties:
                self.sanity_level = min(1000, self.sanity_level + item.properties['sanity_restore'])
                print(f"You ate the {item.name} and felt a wave of calm.")
            self.remove_item(item.item_id)
            self.perform_action()
        elif item.item_type == ItemType.WATER:
            if 'hydration_restore' in item.properties:
                self.hydration_level = min(1000, self.hydration_level + item.properties['hydration_restore'])
                print(f"You drank the {item.name} and felt refreshed.")
            if 'health_restore' in item.properties:
                self.health = min(100, self.health + item.properties['health_restore'])
                print(f"You drank the {item.name} and felt a bit better.")
            self.remove_item(item.item_id)
            self.perform_action()
        elif item.item_type == ItemType.CONSUMABLE: # e.g., medicine, drugs
            # Handle specific consumable effects based on item.properties
            print(f"You used the {item.name}.")
            self.remove_item(item.item_id)
            self.perform_action()
        else:
            print(f"You can't consume the {item.name}.")

    def use_item(self, item_id: str, target=None):
        """General method for using an item, not necessarily consuming."""
        item = self.find_item(item_id)
        if not item:
            print(f"You don't have an item with ID or name '{item_id}' to use.")
            return

        print(f"You used the {item.name}.")
        self.perform_action() # Using an item costs an action
        # Implement specific item usage logic here, e.g.,
        # if item.item_type == ItemType.WEAPON: equip_weapon(item)
        # if item.item_type == ItemType.TOOL: use_tool_on_target(item, target)
        # For a basic example, let's say a 'healing salve' is a CONSUMABLE that heals
        if item.item_type == ItemType.CONSUMABLE and 'health_restore' in item.properties:
            self.health = min(100, self.health + item.properties['health_restore'])
            print(f"The {item.name} healed you for {item.properties['health_restore']} health.")
            self.remove_item(item.item_id)


    def get_inventory_string(self):
        """Returns a formatted string of the player's inventory."""
        if not self.inventory:
            return "Your inventory is empty."
        inv_str = "Your inventory (i):\n"
        for item in self.inventory:
            inv_str += f"- {item.name} (I{item.item_id.split('_')[1]})\n"
        # Also include nested containers for the 's_backpack' type logic
        # For this we'd need a way to look into the nested_containers
        # Example: if 's_backpack' in self.nested_containers:
        #   inv_str += f"  - Backpack (s): {len(self.nested_containers['s_backpack'].inventory)} items\n"
        return inv_str


    def to_dict(self):
        """Converts the Player object to a dictionary for saving."""
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
            # "nested_containers": {name: container.to_dict() for name, container in self.nested_containers.items()}
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Creates a Player object from a dictionary (for loading)."""
        player = cls(
            name=data["name"],
            current_location_id=data["current_location_id"],
            age=data.get("age", 30), # Provide defaults for new attributes
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
        # Load nested containers if implemented
        # if "nested_containers" in data:
        #    player.nested_containers = {name: Container.from_dict(container_data) for name, container_data in data["nested_containers"].items()}
        return player

# --- Example Usage (for testing) ---
if __name__ == "__main__":
    # Create some items
    machete = Item(item_id=f"I_{uuid.uuid4().hex[:4]}", name="Machete", description="A heavy-bladed tool for hacking.", weight=2.0, item_type=ItemType.WEAPON, properties={'damage': 30})
    apple = Item(item_id=f"IF_{uuid.uuid4().hex[:4]}", name="Apple", description="A slightly bruised apple.", weight=0.2, item_type=ItemType.FOOD, properties={'hunger_restore': 150, 'health_restore': 5})
    water_bottle = Item(item_id=f"IF_{uuid.uuid4().hex[:4]}", name="Water Bottle", description="A half-full bottle of water.", weight=0.5, item_type=ItemType.WATER, properties={'hydration_restore': 300})
    useless_rock = Item(item_id=f"I_{uuid.uuid4().hex[:4]}", name="Useless Rock", description="Just a rock. Heavy.", weight=1.0, item_type=ItemType.JUNK)
    bandage = Item(item_id=f"I_{uuid.uuid4().hex[:4]}", name="Bandage", description="For minor cuts and scrapes.", weight=0.1, item_type=ItemType.CONSUMABLE, properties={'health_restore': 10, 'heal_body_part_type': 'wound'})


    # Initialize Player with some random items
    player = Player(name="Aetherius Survivor", initial_body_parts={
        "head": BodyPart("head", 50),
        "torso": BodyPart("torso", 100),
        "left_arm": BodyPart("left_arm", 70, current_health=50, status=BodyPartStatus.WOUNDED), # Start with a wound
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


    player.display_stats()
    print(player.get_inventory_string())

    # Simulate some actions
    print("\n--- Simulating Actions ---")
    for _ in range(5):
        print(f"\nAction {_ + 1}: Moving...")
        if not player.perform_action():
            break
        # Simulate taking minor damage to leg
        if _ == 2:
            player.take_damage("left_leg", 15)
        if player.action_counter % 20 == 0:
            player.display_stats()

    # Consume items
    print("\n--- Consuming Items ---")
    player.consume_item("apple") # Consumes the apple
    player.consume_item("water bottle") # Consumes the water bottle
    player.use_item("bandage", target_body_part="left_leg") # Use bandage
    player.display_stats()
    print(player.get_inventory_string())

    # Simulate prolonged actions leading to hunger/thirst
    print("\n--- Simulating Prolonged Survival ---")
    for i in range(500): # Many actions
        if not player.perform_action():
            print("Player died during prolonged actions.")
            break
        if i % 100 == 0: # Check stats every 100 actions
            player.display_stats()

    player.display_stats()

    # Simulate critical injury
    print("\n--- Simulating Critical Injury (Throat) ---")
    if player.health > 0:
        player.take_damage("throat", 25) # This should be lethal
        player.perform_action() # Trigger health check
    player.display_stats()

    # Demonstrate saving and loading
    print("\n--- Saving and Loading ---")
    player_data = player.to_dict()
    # print(json.dumps(player_data, indent=4)) # Uncomment to see saved JSON

    # Simulate loading into a new player object
    loaded_player = Player.from_dict(player_data)
    print("\n--- Loaded Player Stats ---")
    loaded_player.display_stats()
    print(loaded_player.get_inventory_string())
    assert loaded_player.name == player.name
    assert loaded_player.action_counter == player.action_counter
    assert loaded_player.health == player.health
    print("Player save/load successful!")