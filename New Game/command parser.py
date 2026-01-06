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
    KEY = auto() # Added for specific key items
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

class BodyPartStatus(Enum):
    UNINJURED = auto()
    GRAZED = auto()
    WOUNDED = auto()
    BROKEN = auto()
    SEVERE_BLEEDING = auto()
    SEVERED = auto()

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

class ContainerType(Enum):
    SMALL_BUILDING = auto()
    LARGE_BUILDING = auto()
    FURNITURE = auto()
    BACKPACK = auto()
    POCKET = auto()
    GENERIC = auto()

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
        self.container_id = container_id
        self.name = name
        self.description = description
        self.container_type = container_type
        self.inventory = inventory_items if inventory_items is not None else []
        self.is_locked = is_locked
        self.requires_key_id = requires_key_id
        self.has_been_searched = False

    def add_item(self, item: Item):
        self.inventory.append(item)

    def remove_item(self, item_id: str) -> Item | None:
        for i, item in enumerate(self.inventory):
            if item.item_id == item_id:
                return self.inventory.pop(i)
        return None

    def find_item(self, item_name_or_id: str) -> Item | None:
        for item in self.inventory:
            if item.item_id == item_name_or_id or item.name.lower() == item_name_or_id.lower():
                return item
        return None

    def get_inventory_description(self):
        if not self.inventory:
            return f"The {self.name} is empty."
        items_list = ", ".join([item.name for item in self.inventory])
        return f"Inside the {self.name}, you see: {items_list}."

    def to_dict(self):
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
        return cls(
            container_id=data["container_id"],
            name=data["name"],
            description=data["description"],
            container_type=ContainerType[data["container_type"]],
            inventory_items=[Item.from_dict(item_data) for item_data in data.get("inventory", [])],
            is_locked=data.get("is_locked", False),
            requires_key_id=data.get("requires_key_id"),
            has_been_searched=data.get("has_been_searched", False)
        )

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Container(id='{self.container_id}', name='{self.name}', items={len(self.inventory)})"

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
                 exits: dict = None,
                 items_on_ground: list = None,
                 containers: list = None,
                 environmental_elements: list = None):
        self.location_id = location_id
        self.name = name
        self.description = description
        self.exits = exits if exits is not None else {}
        self.items_on_ground = items_on_ground if items_on_ground is not None else []
        self.containers = containers if containers is not None else []
        self.environmental_elements = environmental_elements if environmental_elements is not None else []
        self.has_been_visited = False

    def get_description(self, player_has_visited: bool = False):
        desc = self.description
        if not self.items_on_ground and not self.containers and not self.environmental_elements:
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
        self.items_on_ground.append(item)

    def remove_item_on_ground(self, item_id: str) -> Item | None:
        for i, item in enumerate(self.items_on_ground):
            if item.item_id == item_id:
                return self.items_on_ground.pop(i)
        return None
    
    def find_item_on_ground(self, item_name_or_id: str) -> Item | None:
        for item in self.items_on_ground:
            if item.item_id == item_name_or_id or item.name.lower() == item_name_or_id.lower():
                return item
        return None

    def add_container(self, container: Container):
        self.containers.append(container)

    def find_container(self, container_name_or_id: str) -> Container | None:
        for container in self.containers:
            if container.container_id == container_name_or_id or container.name.lower() == container_name_or_id.lower():
                return container
        return None

    def to_dict(self):
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

class Player:
    """Placeholder Player class to demonstrate parser interaction"""
    def __init__(self):
        self.name = "Player"
        self.current_location_id = "starting_area"
        self.inventory = []
        self.health = 100
        self.hunger_level = 1000
        self.hydration_level = 1000
        self.sanity_level = 1000
        self.stamina_level = 100
        self.action_counter = 0
        self.body_parts = {
            "head": BodyPart("head", 50), "torso": BodyPart("torso", 100),
            "left_arm": BodyPart("left_arm", 70), "right_arm": BodyPart("right_arm", 70),
            "left_leg": BodyPart("left_leg", 80), "right_leg": BodyPart("right_leg", 80),
            "throat": BodyPart("throat", 20)
        }
    
    def perform_action(self, action_cost: int = 1):
        self.action_counter += action_cost
        self.hunger_level -= action_cost * 1
        self.hydration_level -= action_cost * 2
        return True # Simplified for parser example

    def display_stats(self):
        print(f"\n--- {self.name}'s Status (Actions: {self.action_counter}) ---")
        print(f"Health: {self.health}/100")
        print(f"Hunger: {self.hunger_level}/1000")
        print(f"Hydration: {self.hydration_level}/1000")
        print(f"Sanity: {self.sanity_level}/1000")
        print(f"Stamina: {self.stamina_level}/100")
        print("--------------------------------------")

    def get_inventory_string(self):
        if not self.inventory: return "Your inventory is empty."
        return "Your inventory (i):\n" + "\n".join([f"- {item.name}" for item in self.inventory])

    def add_item(self, item: Item):
        self.inventory.append(item)
    
    def find_item(self, item_name_or_id: str) -> Item | None:
        for item in self.inventory:
            if item.item_id == item_name_or_id or item.name.lower() == item_name_or_id.lower():
                return item
        return None

# --- New: CommandParser Class ---
class CommandParser:
    """
    Parses raw player input into a structured command dictionary.
    Handles verbs, synonyms, objects, and prepositions.
    """
    def __init__(self):
        # Maps canonical verb (key) to a list of synonyms (values)
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
        # Directions are treated specially as they can also be verbs (e.g., "north")
        self.directions = ["north", "south", "east", "west", "up", "down", "n", "s", "e", "w", "u", "d"]
        self.stop_words = ["a", "an", "the", "and", "but", "for", "of", "my", "your"]
        self.prepositions = ["in", "on", "at", "from", "to", "with", "behind", "under", "over"]

        # Invert the verb dictionary for faster lookup of canonical verb
        self._canonical_verbs = {}
        for canonical, synonyms in self.verbs.items():
            for syn in synonyms:
                self._canonical_verbs[syn] = canonical
        # Add directions to canonical verbs if they are standalone commands
        for direction in self.directions:
            self._canonical_verbs[direction] = "go" # 'go north' or just 'north'

    def parse_input(self, command: str) -> dict:
        """
        Parses a raw command string into a structured dictionary.
        Returns {'verb': str, 'direct_object': str|None, 'preposition': str|None, 'indirect_object': str|None, 'raw_command': str}.
        """
        original_command = command.lower().strip()
        tokens = original_command.split()

        if not tokens:
            return {"verb": "unknown", "message": "Please enter a command.", "raw_command": original_command}

        # Try to find the main verb
        main_verb = None
        verb_start_index = -1
        verb_length = 0

        # Prioritize multi-word verbs and directions at the beginning of the command
        for i in range(len(tokens)):
            # Check for multi-word verbs first
            for syn, canonical in self._canonical_verbs.items():
                syn_tokens = syn.split()
                if len(syn_tokens) > 1 and i + len(syn_tokens) <= len(tokens):
                    if tokens[i:i+len(syn_tokens)] == syn_tokens:
                        main_verb = canonical
                        verb_start_index = i
                        verb_length = len(syn_tokens)
                        break
            if main_verb:
                break
            
            # Check for single-word verbs
            if tokens[i] in self._canonical_verbs:
                main_verb = self._canonical_verbs[tokens[i]]
                verb_start_index = i
                verb_length = 1
                break
        
        # Special handling for standalone directions if no other verb was found first
        if not main_verb and tokens[0] in self.directions:
            main_verb = "go"
            verb_start_index = 0
            verb_length = 1


        if not main_verb:
            return {"verb": "unknown", "message": f"I don't understand '{original_command}'.", "raw_command": original_command}

        # Remove the verb (and any leading stop words before it) from the tokens for object extraction
        remaining_tokens = tokens[verb_start_index + verb_length:]

        # Filter out stop words from the remaining tokens
        filtered_tokens = [word for word in remaining_tokens if word not in self.stop_words]

        direct_object_parts = []
        indirect_object_parts = []
        preposition_found = None
        current_target = direct_object_parts

        for token in filtered_tokens:
            if token in self.prepositions:
                preposition_found = token
                current_target = indirect_object_parts # Switch to collecting indirect object
            else:
                current_target.append(token)

        # Special handling for "go" verb to set direct_object as the direction
        if main_verb == "go" and not direct_object_parts and verb_start_index == 0:
            if tokens[0] in self.directions:
                direct_object_parts.append(tokens[0])

        return {
            "verb": main_verb,
            "direct_object": " ".join(direct_object_parts).strip() if direct_object_parts else None,
            "preposition": preposition_found,
            "indirect_object": " ".join(indirect_object_parts).strip() if indirect_object_parts else None,
            "raw_command": original_command
        }

    def _display_parsed_command(self, parsed: dict):
        """Helper to display the parsed command clearly."""
        print(f"  Verb: {parsed.get('verb')}")
        print(f"  Direct Object: {parsed.get('direct_object')}")
        print(f"  Preposition: {parsed.get('preposition')}")
        print(f"  Indirect Object: {parsed.get('indirect_object')}")
        print(f"  Message: {parsed.get('message', 'N/A')}")
        print(f"  Raw Command: '{parsed.get('raw_command')}'\n")

# --- Example Usage for CommandParser ---
if __name__ == "__main__":
    parser = CommandParser()

    print("--- Testing CommandParser ---")

    test_commands = [
        "look",
        "l",
        "search the area",
        "take the rusty key",
        "pick up key from ground",
        "open the shed",
        "open the old shed with rusty key",
        "go north",
        "north",
        "move to the old road",
        "attack zombie with machete",
        "trip the zombie",
        "inventory",
        "i",
        "check my stats",
        "eat apple",
        "drink water from bottle",
        "drop the heavy rock",
        "unknown command abc def",
        "", # Empty command
        "use bandage on left arm" # Complex use case
    ]

    for cmd in test_commands:
        print(f"Parsing: '{cmd}'")
        parsed = parser.parse_input(cmd)
        parser._display_parsed_command(parsed)

    print("\n--- Parser ready for GameEngine integration ---")

    # Example of how a GameEngine might use the parser (simplified)
    # This is *not* part of the parser, but shows its utility.
    class GameEngine:
        def __init__(self):
            self.player = Player()
            self.parser = CommandParser()
            self.current_location = Location(
                location_id="starting_area",
                name="A Gloomy Clearing",
                description="You are in a gloomy clearing, surrounded by dense, overgrown foliage.",
                exits={"north": "forest_path_01", "south": "old_road_02"},
                items_on_ground=[
                    Item(name="Rusty Key", description="Looks like it might open an old lock.", weight=0.05, item_type=ItemType.KEY),
                    Item(name="Apple", description="A ripe apple.", weight=0.2, item_type=ItemType.FOOD, properties={'hunger_restore': 150})
                ],
                containers=[
                    Container(container_id="b:SHED_1", name="Old Shed", description="A dilapidated shed.", container_type=ContainerType.SMALL_BUILDING, is_locked=True, requires_key_id="I:RUSTK_A1B2C3", inventory_items=[
                        Item(name="Machete", description="A heavy-bladed tool.", weight=2.0, item_type=ItemType.WEAPON, properties={'damage':30})
                    ])
                ]
            )
            # Make sure the key ID matches for testing
            self.rusty_key_item = self.current_location.find_item_on_ground("rusty key")
            if self.rusty_key_item:
                self.current_location.find_container("old shed").requires_key_id = self.rusty_key_item.item_id


        def process_command(self, command_str: str):
            parsed_cmd = self.parser.parse_input(command_str)
            print(f"\n[ENGINE] Processing: '{command_str}' -> {parsed_cmd['verb']}")

            verb = parsed_cmd["verb"]
            do = parsed_cmd["direct_object"]
            prep = parsed_cmd["preposition"]
            io = parsed_cmd["indirect_object"]

            if verb == "unknown":
                print(parsed_cmd["message"])
                return

            self.player.perform_action() # Any command counts as an action

            if verb == "look":
                print(self.current_location.get_description())
            elif verb == "search":
                print(self.current_location.get_description(player_has_visited=True)) # More detailed on search
                if self.current_location.containers:
                    for container in self.current_location.containers:
                        print(f"You find an {container.name}.")
            elif verb == "go":
                if do in self.current_location.exits:
                    print(f"You go {do}. (Would move to {self.current_location.exits[do]})")
                    self.player.current_location_id = self.current_location.exits[do] # Update player's location
                else:
                    print(f"You can't go {do} from here.")
            elif verb == "take":
                item_found = self.current_location.find_item_on_ground(do)
                if item_found:
                    self.current_location.remove_item_on_ground(item_found.item_id)
                    self.player.add_item(item_found)
                    print(f"You take the {item_found.name}.")
                elif io: # Check containers if an indirect object was specified
                    container = self.current_location.find_container(io)
                    if container:
                        item_in_container = container.find_item(do)
                        if item_in_container:
                            if container.is_locked:
                                print(f"The {container.name} is locked. You can't take anything from it.")
                            else:
                                container.remove_item(item_in_container.item_id)
                                self.player.add_item(item_in_container)
                                print(f"You take the {item_in_container.name} from the {container.name}.")
                        else:
                            print(f"There is no {do} in the {container.name}.")
                    else:
                        print(f"You don't see a {io} here.")
                else:
                    print(f"You don't see a {do} here to take.")
            elif verb == "open":
                container = self.current_location.find_container(do)
                if container:
                    if container.is_locked:
                        if prep == "with" and io:
                            key_item = self.player.find_item(io)
                            if key_item and key_item.item_id == container.requires_key_id:
                                container.is_locked = False
                                print(f"You unlock the {container.name} with the {key_item.name}.")
                                print(container.get_inventory_description())
                            else:
                                print(f"You try to open the {container.name} with the {io}, but it doesn't work.")
                        else:
                            print(f"The {container.name} is locked. You need a key.")
                    else:
                        print(container.get_inventory_description())
                else:
                    print(f"You can't open a {do} here.")
            elif verb == "inventory":
                print(self.player.get_inventory_string())
            elif verb == "stats":
                self.player.display_stats()
            elif verb == "eat":
                item_to_eat = self.player.find_item(do)
                if item_to_eat and item_to_eat.item_type == ItemType.FOOD:
                    # In a real game, this would call a player method to consume
                    print(f"You eat the {item_to_eat.name}. (Restores hunger)")
                    self.player.inventory.remove(item_to_eat) # Simplified removal
                else:
                    print(f"You don't have {do} to eat, or it's not edible.")
            elif verb == "drink":
                item_to_drink = self.player.find_item(do)
                if item_to_drink and item_to_drink.item_type == ItemType.WATER:
                    # In a real game, this would call a player method to consume
                    print(f"You drink the {item_to_drink.name}. (Restores hydration)")
                    self.player.inventory.remove(item_to_drink) # Simplified removal
                else:
                    print(f"You don't have {do} to drink, or it's not drinkable.")
            elif verb == "drop":
                item_to_drop = self.player.find_item(do)
                if item_to_drop:
                    self.player.inventory.remove(item_to_drop)
                    self.current_location.add_item_on_ground(item_to_drop)
                    print(f"You drop the {item_to_drop.name}.")
                else:
                    print(f"You don't have a {do} to drop.")
            elif verb == "use":
                item_to_use = self.player.find_item(do)
                if item_to_use:
                    # Generic use case, could be expanded for specific item logic
                    if prep == "on" and io:
                        print(f"You attempt to use the {item_to_use.name} on {io}.")
                        # Specific logic for "use bandage on left arm" would go here
                        # Simplified to check for a generic heal_body_part_type property
                        if item_to_use.item_type == ItemType.CONSUMABLE and item_to_use.properties.get('heal_body_part_type'):
                             if io in self.player.body_parts:
                                 # This part is simplified; Player class would need a heal_body_part method
                                 self.player.body_parts[io].heal(item_to_use.properties.get('health_restore', 0))
                                 self.player.inventory.remove(item_to_use) # Consume item
                                 print(f"You use the {item_to_use.name} on your {io} and feel a bit better.")
                             else:
                                 print(f"You can't use {item_to_use.name} on {io}.")
                        else:
                            print(f"You use the {item_to_use.name} on {io}. (No specific effect defined).")
                    else:
                        print(f"You use the {item_to_use.name}. (Specific effects would trigger here).")
                else:
                    print(f"You don't have a {do} to use.")
            else:
                print(f"Action '{verb}' is not yet implemented or recognized in this context.")

    # Demonstrating GameEngine integration
    print("\n--- Demonstrating GameEngine Integration (Simplified) ---")
    game = GameEngine()
    game.player.add_item(Item(name="Bandage", description="For cuts.", weight=0.1, item_type=ItemType.CONSUMABLE, properties={'health_restore': 10, 'heal_body_part_type': 'wound'}))
    game.player.body_parts["left_arm"].take_damage(20) # Give player a wound to test bandage

    engine_commands = [
        "look",
        "take rusty key",
        "open old shed with rusty key",
        "take machete from old shed",
        "inventory",
        "stats",
        "go north",
        "search",
        "eat apple",
        "drop machete",
        "use bandage on left arm"
    ]

    for cmd_cmd in engine_commands:
        game.process_command(cmd_cmd)
        game.player.display_stats()