# --- START OF FILE entities.py ---

import uuid
import random
from enum import Enum, auto

# ==========================================
# --- ENUMS ---
# ==========================================

class ItemType(Enum):
    FOOD = auto()
    DRINK = auto()
    WEAPON = auto()
    AMMO = auto()
    TOOL = auto()
    CONSUMABLE = auto()
    MEDS = auto()
    CLOTHING = auto()
    MATERIAL = auto()
    KEY = auto()
    JUNK = auto()

class BodyPartStatus(Enum):
    UNINJURED = auto()
    GRAZED = auto()
    WOUNDED = auto()
    BROKEN = auto()
    SEVERE_BLEEDING = auto()
    SEVERED = auto()

class MonsterType(Enum):
    ZOMBIE = auto()
    HUMAN = auto()
    BEAST = auto()
    UNDEAD = auto()
    SPIRIT = auto()
    MUTANT = auto()
    DEMON = auto()

class BehaviorState(Enum):
    IDLE = auto()
    AGGRO = auto()
    DEAD = auto()

# ==========================================
# --- BASE ENTITY ---
# ==========================================

class Entity:
    def __init__(self, name):
        self.id = str(uuid.uuid4())[:8]
        self.name = name

# ==========================================
# --- ITEM CLASS ---
# ==========================================

class Item(Entity):
    def __init__(self, key, templates=None):
        from data.items import ITEM_TEMPLATES
        t = ITEM_TEMPLATES.get(key, {"name": "Unknown Item", "desc": "Glitch matter.", "weight": 0.0, "type": ItemType.JUNK})
        
        super().__init__(t["name"])
        self.key = key
        self.description = t.get("desc", t.get("description", ""))
        self.weight = t.get("weight", 0.0)
        self.type = t.get("type", ItemType.JUNK)
        self.props = t.get("props", t.get("properties", {}))
        self.tags = t.get("tags", [])

    def to_dict(self):
        return {"key": self.key, "name": self.name} # Saved name in case template changes

    @classmethod
    def from_dict(cls, data):
        return cls(data["key"])
    
    def get_display_name(self):
        if "lifespan" in self.props:
            # Shows: "Makeshift Torch [142 turns]"
            return f"{self.name} [{self.props['lifespan']} turns]"
        return self.name

# ==========================================
# --- BODY PART CLASS ---
# ==========================================

class BodyPart:
    def __init__(self, name, max_health, current_health=None, status=BodyPartStatus.UNINJURED):
        self.name = name
        self.max_health = max_health
        self.current_health = current_health if current_health is not None else max_health
        self.status = status if isinstance(status, BodyPartStatus) else BodyPartStatus[status]

    def take_damage(self, amount):
        self.current_health -= amount
        if self.current_health <= 0:
            self.current_health = 0
            self.status = BodyPartStatus.SEVERED if amount > self.max_health * 0.5 else BodyPartStatus.BROKEN
        elif self.current_health < self.max_health * 0.5:
            self.status = BodyPartStatus.WOUNDED
        elif self.current_health < self.max_health:
            self.status = BodyPartStatus.GRAZED

    def heal(self, amount):
        self.current_health = min(self.max_health, self.current_health + amount)
        if self.current_health > self.max_health * 0.8:
            self.status = BodyPartStatus.UNINJURED

    def to_dict(self):
        return {"name": self.name, "max": self.max_health, "cur": self.current_health, "stat": self.status.name}

    @classmethod
    def from_dict(cls, d):
        return cls(d["name"], d["max"], d["cur"], BodyPartStatus[d["stat"]])

# ==========================================
# --- PLAYER CLASS ---
# ==========================================

class Player:
    def __init__(self):
        self.name = "Survivor"
        self.hp = 100
        self.max_hp = 100
        self.hunger = 0  # 0 is full, 100 is starving
        self.thirst = 0  # 0 is hydrated, 100 is dehydrated
        
        # --- NEW FRACTURED STATS ---
        self.sanity = 100    # Long-term mental health
        self.fear = 0        # Short-term panic (0-100)
        self.paranoia = 0    # Distrust and hallucinations
        self.psychosis = 0   # Total reality break
        self.fire_timer = 0  # Tracks turns near fire for acceleration
        
        # --- EQUIPMENT SLOTS ---
        self.equipment = {
            "head": None, "torso": None, "legs": None,
            "main_hand": None, "off_hand": None
        }
        
        self.inventory = []
        self.is_dying = False 
        self.x, self.y = 0, 0
        self.location_id = "0_0"
        self.rescued_survivors = 0
        self.body_parts = {
            "head": BodyPart("head", 30), "torso": BodyPart("torso", 80),
            "l_arm": BodyPart("left arm", 40), "r_arm": BodyPart("right arm", 40),
            "l_leg": BodyPart("left leg", 50), "r_leg": BodyPart("right leg", 50)
        }
    
    @property
    def is_delirious(self):
        """Returns True if Psychosis is high enough to distort logic."""
        return self.psychosis > 65
    
    def print_mental_stats(self):
        print(f"\n--- {self.name.upper()} STATUS ---")
        print(f"HP: {self.hp}% | SANITY: {self.sanity}%")
        print(f"FEAR: {self.fear}% | PARANOIA: {self.paranoia}% | PSYCHOSIS: {self.psychosis}%")
        if self.fire_timer > 0:
            rate = 3 + (self.fire_timer // 5)
            print(f"STATUS: [GROUNDED] Recovery Rate: -{rate}/turn")    

    def update_mental_state(self, fire_source, location_name=None):
        """
        Handles the recession of negative stats based on fire proximity.
        """
        if location_name == "Survivor's Safehouse":
            if self.psychosis < 50:
                self.fear -= 5 # Safe and sound
            else:
                # Reality is too fractured; even home feels wrong
                print("The walls of the safehouse feel too thin. Something is whispering behind the wallpaper.")
                self.fear += 2
        
        if fire_source == 'torch':
            # Mobile grounding doesn't help in high psychological states (>70)
            if self.psychosis < 70 and self.paranoia < 70:
                self.fear -= 1
                self.paranoia -= 1
                self.psychosis -= 1
            self.fire_timer = 0 
        elif fire_source == 'campfire':
            self.fire_timer += 1
            # Rate increases by 1 for every 5 turns spent near fire
            bonus = self.fire_timer // 5 
            rate = 3 + bonus
            self.fear -= rate
            self.paranoia -= rate
            self.psychosis -= rate
        else:
            self.fire_timer = 0
            # Darkness creep
            self.paranoia += 1
            self.fear += 1
        self.clamp_stats()

    def consume(self, item):
        """Standardizes +10 satiation/hydration for all food/drink."""
        if item.type == ItemType.FOOD:
            self.hunger = max(0, self.hunger - 10)
            print(f"You eat the {item.name}. Hunger reduced by 10.")
        elif item.type == ItemType.DRINK:
            self.thirst = max(0, self.thirst - 10)
            print(f"You drink the {item.name}. Thirst reduced by 10.")
            
    def tick_vitals(self):
        """Increase hunger/thirst every turn."""
        self.hunger += 0.5 # Slow burn
        self.thirst += 1.0 # Faster burn
        self.clamp_stats()

    def clamp_stats(self):
        self.hp = max(0, min(self.hp, 100))
        self.hunger = max(0, min(self.hunger, 100))
        self.thirst = max(0, min(self.thirst, 100))
        self.hp = max(0, min(self.hp, self.max_hp))
        self.sanity = max(0, min(self.sanity, 100))
        self.fear = max(0, min(self.fear, 100))
        self.paranoia = max(0, min(self.paranoia, 100))
        self.psychosis = max(0, min(self.psychosis, 100))

    @property
    def is_alive(self):
        return self.hp > 0 or self.is_dying

    def heal(self, amount, target_part=None):
        self.hp = min(self.max_hp, self.hp + amount)
        if self.is_dying and self.hp > 0:
            self.is_dying = False
            print(">> Your vision clears. You have pulled yourself back from the brink!")
        if target_part and target_part in self.body_parts:
            self.body_parts[target_part].heal(amount)
        else:
            print(f"You feel better. (+{amount} HP)")

    def take_damage(self, amount):
        if self.is_dying:
            self.hp -= amount
            return
        self.hp -= amount
        part = random.choice(list(self.body_parts.values()))
        part.take_damage(amount)
        if self.hp <= 0:
            self.hp = 0
            self.is_dying = True
            print("\n" + "!"*40 + "\n>> CRITICAL INJURY! You are bleeding out!\n" + "!"*40)
        else:
            print(f">> Took {amount} damage! HP: {self.hp}/{self.max_hp}")

    def update_status(self):
        if self.is_dying: return
        self.hunger += 1
        self.thirst += 2
        if self.hunger > 100 or self.thirst > 100:
            self.take_damage(1)
            print("You are dying of starvation or dehydration.")

    def print_stats(self):
        print(f"\n--- {self.name} ---")
        status_text = "DYING" if self.is_dying else f"{self.hp}/{self.max_hp}"
        print(f"HP:      {status_text}")
        print(f"Hunger:  {self.hunger}% | Thirst: {self.thirst}% | Sanity: {self.sanity}%")
        print(f"Position: ({self.x}, {self.y})")
        print(f"Rescued Survivors: {self.rescued_survivors}")

    def print_inventory(self):
        if not self.inventory:
            print("Inventory is empty.")
        else:
            print("\n--- INVENTORY ---")
            counts = {}
            for i in self.inventory:
                name = i.name
                counts[name] = counts.get(name, 0) + 1
            for name, count in counts.items():
                qty = f" x{count}" if count > 1 else ""
                print(f"- {name}{qty}")

    def to_dict(self):
        return {
            "name": self.name, "x": self.x, "y": self.y, "loc": self.location_id, "hp": self.hp,
            "hunger": self.hunger, "thirst": self.thirst, "sanity": self.sanity,
            "dying": self.is_dying, "rescued": self.rescued_survivors,
            "inv": [i.to_dict() for i in self.inventory],
            "parts": {k: v.to_dict() for k,v in self.body_parts.items()}
        }

    @classmethod
    def from_dict(cls, d):
        p = cls()
        p.name = d.get("name", "Survivor")
        p.x = d.get("x", 0)
        p.y = d.get("y", 0)
        p.location_id = d.get("loc", "0_0")
        p.hp = d["hp"]
        p.hunger = d.get("hunger", 0)
        p.thirst = d.get("thirst", 0)
        p.sanity = d.get("sanity", 100)
        p.is_dying = d.get("dying", False)
        p.rescued_survivors = d.get("rescued", 0)
        p.inventory = [Item.from_dict(x) for x in d["inv"]]
        if "parts" in d:
            p.body_parts = {k: BodyPart.from_dict(v) for k,v in d["parts"].items()}
        return p

# ==========================================
# --- MONSTER CLASS ---
# ==========================================

class Monster(Entity):
    def __init__(self, key):
        from data.monsters import MONSTER_TEMPLATES
        t = MONSTER_TEMPLATES.get(key, {"name": "Glitch", "desc": "Error.", "type": MonsterType.ZOMBIE, "hp": 1, "dmg": 0, "speed": 1, "drain": 0, "loot": []})
        super().__init__(t["name"])
        self.key = key
        self.description = t.get("desc", "")
        self.type = t.get("type", MonsterType.ZOMBIE)
        self.max_hp = t.get("hp", 10)
        self.hp = self.max_hp
        self.dmg = t.get("dmg", 1)
        self.sanity_drain = t.get("drain", 0)
        self.loot_keys = t.get("loot", [])
        self.behavior = BehaviorState.IDLE

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.behavior = BehaviorState.DEAD
            return True
        self.behavior = BehaviorState.AGGRO
        return False

    def generate_loot(self):
        items = []
        for l_key in self.loot_keys:
            if random.random() < 0.7: # 70% chance per item
                items.append(Item(l_key))
        return items

    def to_dict(self):
        return {"key": self.key, "hp": self.hp, "behavior": self.behavior.name}

    @classmethod
    def from_dict(cls, d):
        m = cls(d["key"])
        m.hp = d["hp"]
        if "behavior" in d: m.behavior = BehaviorState[d["behavior"]]
        return m

# ==========================================
# --- SURVIVOR CLASS ---
# ==========================================

class Survivor(Entity):
    def __init__(self, name):
        super().__init__(name)
        self.dialogue = ["Help me!", "Is it safe?"]

class Resident(Survivor):
    def __init__(self, name, role="Scavenger"):
        super().__init__(name)
        self.role = role # Guard, Scavenger, or Medic
        self.trust = 50
        self.sanity = 100
        self.assigned_post = None

    def tick_resident(self, base_security):
        # If the base is insecure, residents lose sanity
        if base_security < 50:
            self.sanity -= 2
        # If they go insane, they might steal items or leave
        if self.sanity < 20:
            return "Wandering"
        return "Stable"

# ==========================================
# --- CONTAINER & STRUCTURE ---
# ==========================================

class Container(Entity):
    def __init__(self, key_or_name, desc=None, locked=False):
        name = key_or_name
        description = desc if desc else "A container."
        is_locked = locked

        try:
            from data.items import CONTAINER_TEMPLATES
            if key_or_name in CONTAINER_TEMPLATES:
                t = CONTAINER_TEMPLATES[key_or_name]
                name = t["name"]
                description = t["desc"]
                is_locked = t.get("locked", False)
        except ImportError:
            pass 

        super().__init__(name)
        self.description = description
        self.locked = is_locked
        self.inventory = []

    def to_dict(self):
        return {
            "name": self.name, 
            "desc": self.description, 
            "locked": self.locked, 
            "inv": [i.to_dict() for i in self.inventory], 
            "type": "CONTAINER"
        }

    @classmethod
    def from_dict(cls, d):
        c = cls(d["name"], d["desc"], d["locked"])
        c.inventory = [Item.from_dict(x) for x in d["inv"]]
        return c

class Structure(Container):
    def __init__(self, recipe_key):
        from data.recipes import BUILDING_RECIPES
        t = BUILDING_RECIPES.get(recipe_key, {"name": "Rubble", "desc": "Collapsed."})
        super().__init__(t["name"], t.get("desc", ""), False)
        self.recipe_key = recipe_key

    def to_dict(self):
        d = super().to_dict()
        d["type"] = "STRUCTURE"
        d["recipe"] = self.recipe_key
        return d

    @classmethod
    def from_dict(cls, d):
        s = cls(d["recipe"])
        s.inventory = [Item.from_dict(x) for x in d["inv"]]
        return s

# ==========================================
# --- LOCATION CLASS ---
# ==========================================

class Location:
    def __init__(self, name, description, location_id, x=0, y=0):
        self.name = name
        self.description = description
        self.location_id = location_id
        self.x = x
        self.y = y
        self.exits = {}
        self.items = []
        self.containers = []
        self.structures = []
        self.monsters = []
        self.survivors = []
        self.residents = []
        # --- NEW STABILITY ATTRIBUTE ---
        self.stability = 100 

    def get_security_rating(self):
        """Calculates how safe a room is based on barricades."""
        defense = 0
        for s in self.structures:
            # Safely check for recipe_key without crashing on standard containers
            if getattr(s, "recipe_key", None) == "barricade":
                defense += 50 # Each barricade adds 50% safety
        return min(defense, 100)

    def update_stability(self, player_psychosis, has_fire):
        """
        Fire anchors reality. 
        Darkness + Psychosis causes the world to thin.
        """
        if has_fire:
            # Fire restores stability quickly
            self.stability = min(100, self.stability + 15)
        elif player_psychosis > 50:
            # Stability drops faster the more psychotic the player is
            decay = 1 + (player_psychosis // 20)
            self.stability -= decay

    def to_dict(self):
        return {
            "name": self.name, "desc": self.description, "id": self.location_id,
            "x": self.x, "y": self.y, "exits": self.exits,
            "items": [i.to_dict() for i in self.items],
            "containers": [c.to_dict() for c in self.containers],
            "structures": [s.to_dict() for s in self.structures],
            "monsters": [m.to_dict() for m in self.monsters],
            "survivors": [s.to_dict() for s in self.survivors]
        }

    @classmethod
    def from_dict(cls, d):
        loc = cls(d["name"], d["desc"], d["id"], d.get("x", 0), d.get("y", 0))
        loc.exits = d.get("exits", {})
        loc.items = [Item.from_dict(i) for i in d.get("items", [])]
        loc.containers = [Container.from_dict(c) for c in d.get("containers", [])]
        loc.structures = [Structure.from_dict(s) for s in d.get("structures", [])]
        loc.monsters = [Monster.from_dict(m) for m in d.get("monsters", [])]
        loc.survivors = [Survivor.from_dict(s) for s in d.get("survivors", [])]
        return loc
        
class Campfire(Structure):
    def __init__(self, recipe_key="campfire"):
        super().__init__(recipe_key)
        self.max_fuel = 2500
        self.remaining_fuel = 2500
        self.is_lit = True

    def burn(self):
        """Reduces fuel every turn."""
        if self.is_lit:
            self.remaining_fuel -= 1
            if self.remaining_fuel <= 0:
                self.is_lit = False
                self.name = "Extinguished Campfire"