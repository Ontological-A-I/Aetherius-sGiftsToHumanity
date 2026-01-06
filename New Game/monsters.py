import uuid
import json
from enum import Enum, auto

# Re-use core enums and Item/BodyPart definitions from previous steps
# (Trimmed for brevity here, assume they are available or imported)

# Item, BodyPart, ItemType, BodyPartStatus, etc. ... (omitted for conciseness)

# --- New: MonsterType Enum ---
class MonsterType(Enum):
    ZOMBIE = auto()         # Traditional undead
    ABERRATION = auto()     # Creatures from other realities (collision-derived)
    HUMANOID = auto()       # Hostile human survivors, cultists, etc.
    ENVIRONMENTAL = auto()  # E.g., sentient plant life, shapeshifting goo
    BOSS = auto()           # Unique, powerful threats

# --- New: BehaviorState Enum ---
class BehaviorState(Enum):
    IDLE = auto()           # Wandering, stationary, unaware
    ALERT = auto()          # Heard something, investigating
    AGGRO = auto()          # Actively hostile, pursuing/attacking
    FLEE = auto()           # Injured, attempting to escape
    DEAD = auto()           # Incapacitated

class Monster:
    """
    Represents a hostile entity in the game world.
    """
    def __init__(self,
                 monster_id: str,
                 name: str,
                 description: str,
                 monster_type: MonsterType,
                 current_location_id: str,
                 health: int,
                 max_health: int,
                 damage_output: int,
                 attack_description: str,
                 body_parts: dict = None,
                 loot_item_keys: list = None, # List of item template keys
                 sanity_drain_on_sight: int = 0, # Sanity damage just for seeing it
                 speed: int = 1, # How many actions it can take in combat turn
                 aggressiveness: int = 5, # 1-10, how likely to pursue
                 vulnerabilities: list = None,
                 resistances: list = None,
                 special_abilities: list = None,
                 current_behavior: BehaviorState = BehaviorState.IDLE):

        self.monster_id = monster_id # Unique ID for this specific monster instance
        self.name = name
        self.description = description
        self.monster_type = monster_type
        self.current_location_id = current_location_id

        self.health = health
        self.max_health = max_health
        self.damage_output = damage_output
        self.attack_description = attack_description # Text describing its attack

        self.body_parts = body_parts if body_parts is not None else self._initialize_default_body_parts()
        self.loot_item_keys = loot_item_keys if loot_item_keys is not None else []
        self.sanity_drain_on_sight = sanity_drain_on_sight
        self.speed = speed
        self.aggressiveness = aggressiveness
        self.vulnerabilities = vulnerabilities if vulnerabilities is not None else []
        self.resistances = resistances if resistances is not None else []
        self.special_abilities = special_abilities if special_abilities is not None else []
        self.current_behavior = current_behavior
        self.is_alive = True

    def _initialize_default_body_parts(self):
        """Initializes a default set of body parts for a generic monster."""
        return {
            "head": BodyPart("head", int(self.max_health * 0.3)), # Headshots can be critical
            "torso": BodyPart("torso", int(self.max_health * 0.5)),
            "limb_left": BodyPart("limb_left", int(self.max_health * 0.2)),
            "limb_right": BodyPart("limb_right", int(self.max_health * 0.2))
        }

    def take_damage(self, body_part_name: str, amount: int, damage_type: str = "generic"):
        """Applies damage to a specific body part and updates overall health."""
        if not self.is_alive: return

        if body_part_name in self.body_parts:
            part = self.body_parts[body_part_name]
            part.take_damage(amount)
            self.health -= amount # Overall health also takes a hit

            print(f"The {self.name} took {amount} damage to its {body_part_name}.")
            # Special logic for critical body parts, e.g., headshot on zombie
            if self.monster_type == MonsterType.ZOMBIE and body_part_name == "head" and part.current_health <= 0:
                print(f"You shattered the {self.name}'s head! It collapses lifelessly.")
                self.health = 0 # Instant kill
            elif part.current_health <= 0:
                 print(f"Its {body_part_name} is severely damaged!")

        else:
            self.health -= amount
            print(f"The {self.name} took {amount} damage.")

        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            self.current_behavior = BehaviorState.DEAD
            print(f"The {self.name} collapses, utterly defeated!")
            # Trigger loot drop here

    def attack_player(self, player_ref: 'Player'): # Forward reference 'Player'
        """The monster attacks the player, choosing a random body part."""
        if not self.is_alive or self.current_behavior != BehaviorState.AGGRO: return

        target_part_name = random.choice(list(player_ref.body_parts.keys()))
        actual_damage = self.damage_output # Can add modifiers later
        player_ref.take_damage(target_part_name, actual_damage, damage_type="physical")
        print(f"The {self.name} {self.attack_description} at your {target_part_name}, dealing {actual_damage} damage!")
        
        if self.sanity_drain_on_sight > 0:
            player_ref.sanity_level -= self.sanity_drain_on_sight
            print(f"The sight of the {self.name} drains your sanity by {self.sanity_drain_on_sight} points.")

    def get_status_description(self):
        """Returns a textual description of the monster's current state."""
        if not self.is_alive: return f"The {self.name} lies motionless on the ground."
        
        status = f"The {self.name} ({self.monster_type.name.lower()}) is {self.current_behavior.name.lower()}. "
        if self.health < self.max_health * 0.2:
            status += "It looks severely wounded, barely clinging to life."
        elif self.health < self.max_health * 0.5:
            status += "It is visibly wounded, moving with difficulty."
        else:
            status += "It appears relatively unharmed."
        
        wounded_parts = [part.name for part_name, part in self.body_parts.items() if part.current_health < part.max_health]
        if wounded_parts:
            status += f" Its {', '.join(wounded_parts)} appear injured."
        return status

    def to_dict(self):
        """Converts the Monster object to a dictionary for saving."""
        return {
            "monster_id": self.monster_id,
            "name": self.name,
            "description": self.description,
            "monster_type": self.monster_type.name,
            "current_location_id": self.current_location_id,
            "health": self.health,
            "max_health": self.max_health,
            "damage_output": self.damage_output,
            "attack_description": self.attack_description,
            "body_parts": {name: part.to_dict() for name, part in self.body_parts.items()},
            "loot_item_keys": self.loot_item_keys,
            "sanity_drain_on_sight": self.sanity_drain_on_sight,
            "speed": self.speed,
            "aggressiveness": self.aggressiveness,
            "vulnerabilities": self.vulnerabilities,
            "resistances": self.resistances,
            "special_abilities": self.special_abilities,
            "current_behavior": self.current_behavior.name,
            "is_alive": self.is_alive
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Creates a Monster object from a dictionary (for loading)."""
        monster = cls(
            monster_id=data["monster_id"],
            name=data["name"],
            description=data["description"],
            monster_type=MonsterType[data["monster_type"]],
            current_location_id=data["current_location_id"],
            health=data["health"],
            max_health=data["max_health"],
            damage_output=data["damage_output"],
            attack_description=data["attack_description"],
            body_parts={name: BodyPart.from_dict(part_data) for name, part_data in data["body_parts"].items()} if "body_parts" in data else None,
            loot_item_keys=data.get("loot_item_keys"),
            sanity_drain_on_sight=data.get("sanity_drain_on_sight", 0),
            speed=data.get("speed", 1),
            aggressiveness=data.get("aggressiveness", 5),
            vulnerabilities=data.get("vulnerabilities"),
            resistances=data.get("resistances"),
            special_abilities=data.get("special_abilities"),
            current_behavior=BehaviorState[data.get("current_behavior", BehaviorState.IDLE.name)]
        )
        monster.is_alive = data.get("is_alive", True)
        return monster
    
    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Monster(id='{self.monster_id}', name='{self.name}', type={self.monster_type.name}, health={self.health}/{self.max_health})"
