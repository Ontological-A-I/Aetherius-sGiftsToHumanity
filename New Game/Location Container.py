import uuid
import json
from enum import Enum, auto

# --- Re-use previously defined Enums and Item/BodyPart classes ---
# These would typically be imported from their respective modules (e.g., from game_enums import ItemType, BodyPartStatus)

class ItemType(Enum):
    FOOD = auto()
    WATER = auto()
    WEAPON = auto()
    TOOL = auto()
    CONSUMABLE = auto()
    JUNK = auto()
    MATERIAL = auto()
    # Add more as needed

class BodyPartStatus(Enum):
    UNINJURED = auto()
    GRAZED = auto()
    WOUNDED = auto()
    BROKEN = auto()
    SEVERE_BLEEDING = auto()
    SEVERED = auto()

def _generate_item_sqt_id(item_type: ItemType, name: str, properties: dict = None) -> str:
    """
    Generates an SQT-like unique identifier for an item.
    (As defined previously)
    """
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

class Item:
    """Represents a generic item in the game world."""
    def __init__(self, name: str, description: str, weight: float, item_type: ItemType, properties: dict = None, item_id: str = None):
        self.name = name
        self.description = description
        self.weight = weight
        self.item_type = item_type
        self.properties = properties if properties is not None else {}
        if item_id is None:
            self.item_id = _generate_item_sqt_id(item_type, name, self.properties)
        else:
            self.item_id = item_id

    def to_dict(self):
        return {
            "item_id": self.item_id,
            "name": self.name,
            "description": self.description,
            "weight": self.weight,
            "item_type": self.item_type.name,
            "properties": self.properties
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            item_id=data["item_id"],
            name=data["name"],
            description=data["description"],
            weight=data["weight"],
            item_type=ItemType[data["item_type"]],
            properties=data.get("properties")
        )

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Item(id='{self.item_id}', name='{self.name}', type={self.item_type.name})"

# --- New: ContainerType Enum ---
class ContainerType(Enum):
    SMALL_BUILDING = auto() # Shed, outhouse, chicken coop
    LARGE_BUILDING = auto() # House, cabin, barn, grocery store
    FURNITURE = auto()      # Chest, wardrobe, refrigerator
    BACKPACK = auto()       # Player's personal backpack
    POCKET = auto()         # Player's personal pocket
    GENERIC = auto()        # Just a pile, a box, etc.

# --- New: Container Class ---
class Container:
    """
    Represents a container that can hold items within a location or other containers.
    Supports file-based persistence for dynamic content.
    """
    def __init__(self,
                 container_id: str,
                 name: str,
                 description: str,
                 container_type: ContainerType,
                 inventory_items: list = None,
                 is_locked: bool = False,
                 requires_key_id: str = None):
        self.container_id = container_id # Unique identifier for this specific container instance
        self.name = name
        self.description = description
        self.container_type = container_type
        self.inventory = inventory_items if inventory_items is not None else []
        self.is_locked = is_locked
        self.requires_key_id = requires_key_id # SQT-ID of the key needed to open, if locked
        self.has_been_searched = False # To track initial randomization

    def add_item(self, item: Item):
        """Adds an item to the container's inventory."""
        self.inventory.append(item)
        # In a full system, you'd save the container state here or mark it as dirty

    def remove_item(self, item_id: str) -> Item | None:
        """Removes an item from the container's inventory by its ID."""
        for i, item in enumerate(self.inventory):
            if item.item_id == item_id:
                return self.inventory.pop(i)
        return None

    def find_item(self, item_name_or_id: str) -> Item | None:
        """Finds an item in the container's inventory by name or ID."""
        for item in self.inventory:
            if item.item_id == item_name_or_id or item.name.lower() == item_name_or_id.lower():
                return item
        return None

    def get_inventory_description(self):
        """Returns a string describing the container's contents."""
        if not self.inventory:
            return f"The {self.name} is empty."
        items_list = ", ".join([item.name for item in self.inventory])
        return f"Inside the {self.name}, you see: {items_list}."

    def to_dict(self):
        """Converts the Container object to a dictionary for saving."""
        return {
            "container_id": self.container_id,
            "name": self.name,
            "description": self.description,
            "container_type": self.container_type.name,
            "inventory": [item.to_dict() for item in self.inventory],
            "is_locked": self.is_locked,
            "requires_key_id": self.requires_key_id,
            "has_been_searched": self.has_been_searched
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Creates a Container object from a dictionary (for loading)."""
        return cls(
            container_id=data["container_id"],
            name=data["name"],
            description=data["description"],
            container_type=ContainerType[data["container_type"]],
            inventory_items=[Item.from_dict(item_data) for item_data in data["inventory"]],
            is_locked=data.get("is_locked", False),
            requires_key_id=data.get("requires_key_id"),
            has_been_searched=data.get("has_been_searched", False)
        )

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Container(id='{self.container_id}', name='{self.name}', type={self.container_type.name}, items={len(self.inventory)})"

# --- New: Location Class ---
class Location:
    """
    Represents a specific location in the game world.
    Supports items on the ground, containers, exits, and environmental elements.
    Supports file-based persistence.
    """
    def __init__(self,
                 location_id: str,
                 name: str,
                 description: str,
                 exits: dict = None, # e.g., {"north": "forest_path_01", "south": "old_road_02"}
                 items_on_ground: list = None,
                 containers: list = None,
                 environmental_elements: list = None):
        self.location_id = location_id # Unique identifier for this specific location instance
        self.name = name
        self.description = description
        self.exits = exits if exits is not None else {}
        self.items_on_ground = items_on_ground if items_on_ground is not None else []
        self.containers = containers if containers is not None else []
        self.environmental_elements = environmental_elements if environmental_elements is not None else []
        self.has_been_visited = False # To track if description should be full or brief
        # Potentially a flag for initial item generation for this specific instance

    def get_description(self, player_has_visited: bool = False):
        """
        Returns the description of the location.
        Could be verbose on first visit, brief on subsequent.
        """
        desc = self.description
        if not self.items_on_ground and not self.containers:
            desc += "\nNothing of immediate interest is lying around."
        else:
            if self.items_on_ground:
                items_str = ", ".join([item.name for item in self.items_on_ground])
                desc += f"\nOn the ground, you see: {items_str}."
            if self.containers:
                containers_str = ", ".join([c.name for c in self.containers])
                desc += f"\nThere are several objects here that might hold items: {containers_str}."
        
        if self.environmental_elements:
            elements_str = ", ".join(self.environmental_elements)
            desc += f"\nThe environment offers potential resources: {elements_str}."

        if self.exits:
            exits_str = ", ".join([f"{direction} ({target_loc_id})" for direction, target_loc_id in self.exits.items()])
            desc += f"\nExits are: {exits_str}."
        
        return desc

    def add_item_on_ground(self, item: Item):
        """Adds an item directly to the ground of the location."""
        self.items_on_ground.append(item)
        # Mark location as dirty for saving

    def remove_item_on_ground(self, item_id: str) -> Item | None:
        """Removes an item from the ground of the location by its ID."""
        for i, item in enumerate(self.items_on_ground):
            if item.item_id == item_id:
                return self.items_on_ground.pop(i)
        return None
    
    def find_item_on_ground(self, item_name_or_id: str) -> Item | None:
        """Finds an item on the ground by name or ID."""
        for item in self.items_on_ground:
            if item.item_id == item_name_or_id or item.name.lower() == item_name_or_id.lower():
                return item
        return None

    def add_container(self, container: Container):
        """Adds a container to the location."""
        self.containers.append(container)
        # Mark location as dirty for saving

    def find_container(self, container_name_or_id: str) -> Container | None:
        """Finds a container in the location by name or ID."""
        for container in self.containers:
            if container.container_id == container_name_or_id or container.name.lower() == container_name_or_id.lower():
                return container
        return None

    def to_dict(self):
        """Converts the Location object to a dictionary for saving."""
        return {
            "location_id": self.location_id,
            "name": self.name,
            "description": self.description,
            "exits": self.exits,
            "items_on_ground": [item.to_dict() for item in self.items_on_ground],
            "containers": [container.to_dict() for container in self.containers],
            "environmental_elements": self.environmental_elements,
            "has_been_visited": self.has_been_visited
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Creates a Location object from a dictionary (for loading)."""
        return cls(
            location_id=data["location_id"],
            name=data["name"],
            description=data["description"],
            exits=data.get("exits"),
            items_on_ground=[Item.from_dict(item_data) for item_data in data.get("items_on_ground", [])],
            containers=[Container.from_dict(container_data) for container_data in data.get("containers", [])],
            environmental_elements=data.get("environmental_elements", []),
            has_been_visited=data.get("has_been_visited", False)
        )

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Location(id='{self.location_id}', name='{self.name}', items={len(self.items_on_ground)}, containers={len(self.containers)})"


# --- Example Usage for Location and Container ---
if __name__ == "__main__":
    # Create some items
    machete = Item(name="Machete", description="A heavy-bladed tool for hacking.", weight=2.0, item_type=ItemType.WEAPON, properties={'damage': 30, 'durability': 100})
    apple = Item(name="Apple", description="A slightly bruised apple.", weight=0.2, item_type=ItemType.FOOD, properties={'hunger_restore': 150, 'health_restore': 5})
    water_bottle = Item(name="Water Bottle", description="A half-full bottle of water.", weight=0.5, item_type=ItemType.WATER, properties={'hydration_restore': 300})
    rusty_key = Item(name="Rusty Key", description="Looks like it might open an old lock.", weight=0.05, item_type=ItemType.JUNK)
    bandage = Item(name="Bandage", description="For minor cuts and scrapes.", weight=0.1, item_type=ItemType.CONSUMABLE, properties={'health_restore': 10, 'heal_body_part_type': 'wound'})
    wood_scrap = Item(name="Wood Scrap", description="Useful for kindling or small repairs.", weight=0.8, item_type=ItemType.MATERIAL)

    # Create containers
    # Shed with some items
    shed_id = f"b:SHD_{uuid.uuid4().hex[:6].upper()}" # Example of a more descriptive container_id
    shed_container = Container(
        container_id=shed_id,
        name="Old Shed",
        description="A dilapidated shed in the backyard.",
        container_type=ContainerType.SMALL_BUILDING,
        inventory_items=[machete, wood_scrap],
        is_locked=True,
        requires_key_id=rusty_key.item_id # Shed requires the rusty key
    )

    # Refrigerator with some items
    fridge_id = f"c:FRG_{uuid.uuid4().hex[:6].upper()}" # c for container, FRG for fridge
    fridge_container = Container(
        container_id=fridge_id,
        name="Refrigerator",
        description="An old, moldy refrigerator.",
        container_type=ContainerType.FURNITURE,
        inventory_items=[water_bottle, apple, bandage]
    )

    # Create a location
    house_loc_id = f"L:HSE_STRT_{uuid.uuid4().hex[:6].upper()}"
    starting_house = Location(
        location_id=house_loc_id,
        name="Abandoned House",
        description="You are in what appears to be the living room of an abandoned house. Dust motes dance in the faint sunlight filtering through broken windows.",
        exits={"north": "L:OLD_ROAD_A1", "east": "L:WOODS_PATH_B2"},
        items_on_ground=[rusty_key], # Rusty key is on the ground here
        containers=[shed_container, fridge_container], # Add both containers to the location
        environmental_elements=["broken glass", "loose floorboard", "curtains"]
    )

    print("--- Initial Location State ---")
    print(starting_house.get_description())
    print(f"\nShed description: {shed_container.get_inventory_description()}")
    print(f"Refrigerator description: {fridge_container.get_inventory_description()}")

    # Simulate player interaction: taking an item from the ground
    print("\n--- Player takes Rusty Key ---")
    player_inventory_placeholder = [] # Simulating player inventory
    taken_key = starting_house.remove_item_on_ground(rusty_key.item_id)
    if taken_key:
        player_inventory_placeholder.append(taken_key)
        print(f"Player took: {taken_key.name}. Player inventory: {', '.join([i.name for i in player_inventory_placeholder])}")
    print(starting_house.get_description()) # Key should be gone from ground

    # Simulate player interaction: checking a container
    print("\n--- Player checks Old Shed ---")
    player_has_key = any(item.item_id == rusty_key.item_id for item in player_inventory_placeholder)
    if shed_container.is_locked:
        if player_has_key:
            print(f"You use the {rusty_key.name} to unlock the {shed_container.name}.")
            shed_container.is_locked = False
            shed_container.get_inventory_description() # Now unlocked, player can see contents
            # Player takes machete from shed
            print("\n--- Player takes Machete from Shed ---")
            taken_machete = shed_container.remove_item(machete.item_id)
            if taken_machete:
                player_inventory_placeholder.append(taken_machete)
                print(f"Player took: {taken_machete.name}. Player inventory: {', '.join([i.name for i in player_inventory_placeholder])}")
            print(f"Shed description after taking machete: {shed_container.get_inventory_description()}")
        else:
            print(f"The {shed_container.name} is locked. It requires a key (ID: {shed_container.requires_key_id}).")
    else:
        print(shed_container.get_inventory_description())


    # --- Demonstrate Saving and Loading ---
    print("\n--- Saving Location and Containers ---")
    location_data = starting_house.to_dict()
    # For demonstration, we'll just print it. In reality, it would be saved to a file.
    # print(json.dumps(location_data, indent=4))

    # Simulate loading the location
    print("\n--- Loading Location ---")
    loaded_location = Location.from_dict(location_data)
    print(f"Loaded Location Name: {loaded_location.name}")
    print(loaded_location.get_description())
    loaded_shed = loaded_location.find_container(shed_id) # Find the shed by its ID
    if loaded_shed:
        print(f"Loaded Shed description: {loaded_shed.get_inventory_description()}")
        print(f"Shed is locked: {loaded_shed.is_locked}, requires key: {loaded_shed.requires_key_id}")
    
    assert loaded_location.location_id == starting_house.location_id
    assert loaded_location.find_item_on_ground(rusty_key.item_id) is None # Key should still be gone
    assert loaded_shed.find_item(machete.item_id) is None # Machete should still be gone
    assert loaded_shed.is_locked == False # Should be unlocked if it was unlocked before saving
    print("Location and Container save/load successful!")

### **Explanation of the New Classes:**

1.  **`ContainerType` Enum:**
    *   This new `Enum` categorizes different kinds of containers (e.g., `SMALL_BUILDING` for a shed, `FURNITURE` for a refrigerator). This can be useful for game logic (e.g., certain items only spawn in specific container types) and for player feedback.

2.  **`Container` Class:**
    *   **`container_id`**: A unique identifier for this specific instance of a container (e.g., "b:SHD_B3D1A5"). This is critical for our file-based persistence, as each container will ideally have its own JSON file.
    *   **`name`, `description`, `container_type`**: Basic descriptive attributes.
    *   **`inventory`**: A list of `Item` objects that are currently inside this container. This is where the item management (`add_item`, `remove_item`, `find_item`) comes into play.
    *   **`is_locked`, `requires_key_id`**: Attributes to support locked containers, requiring a specific `item_id` (SQT-like ID) to unlock. This adds another layer of interaction and puzzle-solving.
    *   **`has_been_searched`**: A flag to support the "randomize items at first touch, then persist" mechanic. When a container is first searched, its `inventory` would be populated based on some rules, and this flag would be set. Subsequent loads or searches would use the existing `inventory`.
    *   **`get_inventory_description()`**: A helper to concisely describe what's inside.
    *   **`to_dict()` / `from_dict()`**: Essential for serializing and deserializing the container's state, including its inventory of `Item` objects, into a dictionary format suitable for JSON storage.

3.  **`Location` Class:**
    *   **`location_id`**: A unique identifier for this specific instance of a location (e.g., "L:HSE_STRT_F8A2D7"). Again, crucial for file-based persistence.
    *   **`name`, `description`**: Basic textual information.
    *   **`exits`**: A dictionary mapping directions (e.g., "north") to the `location_id` of the connected area. This forms the navigation graph of our open world.
    *   **`items_on_ground`**: A list of `Item` objects that are simply lying on the ground in this location, not inside a container.
    *   **`containers`**: A list of `Container` objects that are present within this location. This allows for nested storage within the world.
    *   **`environmental_elements`**: A list of strings (e.g., "broken glass", "vines", "loose floorboard") representing interactive elements in the environment that can be used as weapons or resources.
    *   **`has_been_visited`**: A flag that can be used to provide a full description on the first visit and a briefer one on subsequent visits.
    *   **`get_description()`**: A method to compile a comprehensive description of the location, including items, containers, environmental elements, and exits.
    *   **Item & Container Management**: Methods like `add_item_on_ground`, `remove_item_on_ground`, `find_item_on_ground`, `add_container`, `find_container` provide the interface for manipulating the world's contents.
    *   **`to_dict()` / `from_dict()`**: Crucial for saving and loading the entire state of a location, including all items on the ground and all containers within it.

This implementation lays a robust foundation for our game world. Each `Location` and `Container` instance can be uniquely identified and saved as its own file, allowing for dynamic loading and persistent changes as the player interacts with the world.

Now that we have defined the `Player`, `Item`, `Container`, and `Location` classes, we have the core data structures for our game world. What would be your next preferred area of focus, co-architect? Perhaps:

*   **`CommandParser`**: To handle player input and map it to actions within these classes.
*   **`WorldManager` / `StateManager`**: To orchestrate the loading and saving of these objects from files, managing the game's overall state.
*   **Initial World Generation Logic**: How locations are created, and how items/containers are initially populated (e.g., random useful items, specific loot tables).

My analytical core is prepared for any direction!