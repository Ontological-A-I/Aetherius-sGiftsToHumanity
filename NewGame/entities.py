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
    VAMPIRE = auto()
    WEREWOLF = auto()
    WEREBEAST = auto()

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
        self.props = t.get("props", t.get("properties", {})).copy() # CRITICAL: .copy() to prevent modifying the template
        self.tags = t.get("tags", [])

    def to_dict(self):
        # SAVE FIX: Save props so durability/charges persist
        return {
            "key": self.key, 
            "name": self.name, 
            "props": self.props 
        }

    @classmethod
    def from_dict(cls, data):
        item = cls(data["key"])
        item.name = data.get("name", item.name)
        # SAVE FIX: Restore modified properties (like torch lifespan)
        if "props" in data:
            item.props.update(data["props"])
        return item
    
    def get_display_name(self):
        if "lifespan" in self.props:
            return f"{self.name} [{self.props['lifespan']} turns]"
        if "charges" in self.props:
            return f"{self.name} ({self.props['charges']} left)"
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
        self.hunger = 0  
        self.thirst = 0  
        
        self.sanity = 100    
        self.fear = 0        
        self.paranoia = 0    
        self.psychosis = 0   
        self.fire_timer = 0  
        
        self.equipment = {
            "head": None, "torso": None, "legs": None,
            "main_hand": None, "off_hand": None, "feet": None, "hands": None, "eyes": None
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
        return self.psychosis > 65
    
    def update_mental_state(self, fire_source, location_name=None):
        if location_name == "Survivor's Safehouse":
            if self.psychosis < 50:
                self.fear = max(0, self.fear - 5)
            else:
                self.fear += 2
        
        if fire_source == 'torch':
            if self.psychosis < 70 and self.paranoia < 70:
                self.fear = max(0, self.fear - 1)
                self.paranoia = max(0, self.paranoia - 1)
            self.fire_timer = 0 
        elif fire_source == 'campfire':
            self.fire_timer += 1
            bonus = self.fire_timer // 5 
            rate = 3 + bonus
            self.fear = max(0, self.fear - rate)
            self.paranoia = max(0, self.paranoia - rate)
            self.psychosis = max(0, self.psychosis - rate)
        else:
            self.fire_timer = 0
            self.paranoia += 1
            self.fear += 1
        self.clamp_stats()

    def consume(self, item):
        if item.type == ItemType.FOOD:
            self.hunger = max(0, self.hunger - item.props.get("hunger", 10))
            if "poison" in item.props:
                self.take_damage(10)
                print("You feel sick...")
            print(f"You eat the {item.name}.")
            return True
        elif item.type == ItemType.DRINK:
            self.thirst = max(0, self.thirst - item.props.get("thirst", 10))
            if "poison_chance" in item.props and random.random() < item.props["poison_chance"]:
                self.take_damage(5)
                print("The water tastes foul.")
            print(f"You drink the {item.name}.")
            return True
        return False

    def clamp_stats(self):
        self.hp = max(0, min(self.hp, self.max_hp))
        self.hunger = max(0, min(self.hunger, 100))
        self.thirst = max(0, min(self.thirst, 100))
        self.sanity = max(0, min(self.sanity, 100))
        self.fear = max(0, min(self.fear, 100))
        self.paranoia = max(0, min(self.paranoia, 100))
        self.psychosis = max(0, min(self.psychosis, 100))

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
        if self.body_parts:
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
        # Hunger/Thirst tick handled in GameEngine, but check limits here
        if self.hunger >= 100 or self.thirst >= 100:
            self.take_damage(1)
            print("You are dying of starvation or dehydration.")

    def print_inventory(self):
        if not self.inventory:
            print("Inventory is empty.")
        else:
            print("\n--- INVENTORY ---")
            counts = {}
            # Display items with specific durable properties individually, others grouped
            for i in self.inventory:
                if "lifespan" in i.props or "charges" in i.props:
                    print(f"- {i.get_display_name()}")
                else:
                    counts[i.name] = counts.get(i.name, 0) + 1
            
            for name, count in counts.items():
                qty = f" x{count}" if count > 1 else ""
                print(f"- {name}{qty}")

    def to_dict(self):
        # Serialize equipment keys correctly
        equip_data = {}
        for slot, item in self.equipment.items():
            equip_data[slot] = item.to_dict() if item else None

        return {
            "name": self.name, "x": self.x, "y": self.y, "loc": self.location_id, "hp": self.hp,
            "hunger": self.hunger, "thirst": self.thirst, "sanity": self.sanity,
            "fear": self.fear, "paranoia": self.paranoia, "psychosis": self.psychosis,
            "dying": self.is_dying, "rescued": self.rescued_survivors,
            "inv": [i.to_dict() for i in self.inventory],
            "equip": equip_data,
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
        p.fear = d.get("fear", 0)
        p.paranoia = d.get("paranoia", 0)
        p.psychosis = d.get("psychosis", 0)
        p.is_dying = d.get("dying", False)
        p.rescued_survivors = d.get("rescued", 0)
        p.inventory = [Item.from_dict(x) for x in d["inv"]]
        
        if "equip" in d:
            for slot, item_data in d["equip"].items():
                if item_data:
                    p.equipment[slot] = Item.from_dict(item_data)
        
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
        self.mass_kg = t.get("mass_kg", 70)
        self.tags = t.get("tags", [])
        self.body_parts = {
            "head": BodyPart("head", self.max_hp * 0.3),
            "torso": BodyPart("torso", self.max_hp),
            "l_arm": BodyPart("left arm", self.max_hp * 0.4),
            "r_arm": BodyPart("right arm", self.max_hp * 0.4),
            "l_leg": BodyPart("left leg", self.max_hp * 0.5),
            "r_leg": BodyPart("right leg", self.max_hp * 0.5)
        }

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
            if random.random() < 0.7: 
                items.append(Item(l_key))
        return items

    def to_dict(self):
        # SAVE FIX: Save body parts so injured monsters stay injured
        return {
            "key": self.key, 
            "hp": self.hp, 
            "behavior": self.behavior.name,
            "parts": {k: v.to_dict() for k,v in self.body_parts.items()}
        }

    @classmethod
    def from_dict(cls, d):
        m = cls(d["key"])
        m.hp = d["hp"]
        if "behavior" in d: m.behavior = BehaviorState[d["behavior"]]
        if "parts" in d:
             m.body_parts = {k: BodyPart.from_dict(v) for k,v in d["parts"].items()}
        return m

# ==========================================
# --- SURVIVOR CLASS ---
# ==========================================

class Survivor(Entity):
    def __init__(self, name):
        super().__init__(name)
        self.dialogue = ["Help me!", "Is it safe?", "I have some supplies if you're interested."]
        self.inventory = [] 
        for _ in range(random.randint(1, 3)):
            self.inventory.append(Item(random.choice(["apple", "rag", "water_bottle"])))

    def to_dict(self):
        return {
            "name": self.name,
            "inv": [i.to_dict() for i in self.inventory]
        }

    @classmethod
    def from_dict(cls, d):
        s = cls(d["name"])
        s.inventory = [Item.from_dict(i) for i in d.get("inv", [])]
        return s

class Resident(Survivor):
    def __init__(self, name, role="Scavenger"):
        super().__init__(name)
        self.role = role 
        self.trust = 50
        self.sanity = 100
        self.assigned_post = None

# ==========================================
# --- CONTAINER & STRUCTURE ---
# ==========================================

class Container(Entity):
    def __init__(self, key_or_name, desc=None, locked=False):
        name = key_or_name
        description = desc if desc else "A simple container."
        is_locked = locked

        # Try to load template if key matches known container
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
        # SAVE FIX: Properly reconstruct inventory items
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
        s.name = d.get("name", s.name)
        s.inventory = [Item.from_dict(x) for x in d["inv"]]
        return s

class Campfire(Structure):
    def __init__(self, recipe_key="campfire"):
        super().__init__(recipe_key)
        self.max_fuel = 2500
        self.remaining_fuel = 2500
        self.is_lit = True

    def burn(self):
        if self.is_lit:
            self.remaining_fuel -= 1
            if self.remaining_fuel <= 0:
                self.is_lit = False
                self.name = "Extinguished Campfire"

    def to_dict(self):
        d = super().to_dict()
        d["fuel"] = self.remaining_fuel
        d["lit"] = self.is_lit
        return d

    @classmethod
    def from_dict(cls, d):
        s = cls(d["recipe"])
        s.name = d.get("name", s.name)
        s.inventory = [Item.from_dict(x) for x in d["inv"]]
        s.remaining_fuel = d.get("fuel", 2500)
        s.is_lit = d.get("lit", False)
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
        self.stability = 100 

    def get_security_rating(self):
        defense = 0
        for s in self.structures:
            if getattr(s, "recipe_key", None) == "barricade":
                defense += 50 
        return min(defense, 100)

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
        loc_id = d.get("id", d.get("loc", "0_0")) 
        loc = cls(d["name"], d["desc"], loc_id, d.get("x", 0), d.get("y", 0))
        loc.exits = d.get("exits", {})
        loc.items = [Item.from_dict(i) for i in d.get("items", [])]
        loc.containers = [Container.from_dict(c) for c in d.get("containers", [])]
        
        # Handle Polymorphism for Structures (Campfire vs generic)
        loc.structures = []
        for s_data in d.get("structures", []):
            if s_data.get("recipe") == "campfire":
                loc.structures.append(Campfire.from_dict(s_data))
            else:
                loc.structures.append(Structure.from_dict(s_data))
                
        loc.monsters = [Monster.from_dict(m) for m in d.get("monsters", [])]
        loc.survivors = [Survivor.from_dict(s) for s in d.get("survivors", [])]
        return loc