from entities import MonsterType

MONSTER_TEMPLATES = {
    "shambler": {
        "name": "Rotting Shambler",
        "desc": "A decomposing corpse, shuffling forward with relentless hunger.",
        "type": MonsterType.ZOMBIE,
        "hp": 40, "dmg": 6, "speed": 1, "drain": 5,
        "loot": ["rag", "cash_card", "lighter"],
        "mass_kg": 70, # Average human mass
        "tags": ["zombie", "decayed"]
    },
    "feral_soldier": {
        "name": "Feral Soldier",
        "desc": "A zombie in tattered military fatigues. It still wears a helmet.",
        "type": MonsterType.ZOMBIE,
        "hp": 80, "dmg": 12, "speed": 2, "drain": 10,
        "loot": ["combat_knife", "canned_meat", "mre", "kevlar_vest"],
        "mass_kg": 90, # Heavier due to gear/muscle
        "tags": ["zombie", "armored"]
    },
    "looter": {
        "name": "Desperate Looter",
        "desc": "A survivor looking for an easy score. They look nervous.",
        "type": MonsterType.HUMAN,
        "hp": 60, "dmg": 8, "speed": 4, "drain": 0,
        "loot": ["crowbar", "canned_beans", "water_bottle", "backpack"],
        "mass_kg": 75, # Average human mass
        "tags": ["human", "scavenger"]
    },
    "wolf": {
        "name": "Starved Wolf",
        "desc": "A gaunt canine with matted fur and bared fangs.",
        "type": MonsterType.BEAST,
        "hp": 30, "dmg": 10, "speed": 5, "drain": 2,
        "loot": [],
        "mass_kg": 35, # Wolf mass
        "tags": ["beast", "fast", "predator"]
    },
    "mirror_stalker": {
        "name": "The Mirror Stalker",
        "desc": "A faceless humanoid whose skin reflects the room around it perfectly. It moves exactly as you do.",
        "type": MonsterType.SPIRIT,
        "hp": 200, "dmg": 15, "speed": 5, "drain": 20,
        "loot": ["shattered_glass", "echo_of_self"],
        "mass_kg": 60, # Spiritual entity, perhaps partially corporeal
        "tags": ["spirit", "ethereal", "illusion"]
    },
    "architect_glass": {
        "name": "The Architect of Glass",
        "desc": "A towering mass of jagged geometry. It doesn't walk; it simply rearranges the space around it.",
        "type": MonsterType.DEMON,
        "hp": 350, "dmg": 25, "speed": 2, "drain": 30,
        "loot": ["void_crystal", "blueprints_of_nowhere"],
        "mass_kg": 500, # Very heavy, as implied by "towering mass"
        "tags": ["demon", "colossal", "reality_bender", "boss"]
    },
    # --- NEW MONSTERS ---
    "fresh_zombie": {
        "name": "Fresh Zombie",
        "desc": "Recently turned, its eyes still hold a flicker of humanity, quickly fading.",
        "type": MonsterType.ZOMBIE,
        "hp": 50, "dmg": 8, "speed": 2, "drain": 7,
        "loot": ["wallet", "watch"], # New item "watch" implies it might be added to items.py
        "mass_kg": 75,
        "tags": ["zombie", "recently_turned"]
    },
    "zombie_cop": {
        "name": "Zombie Cop",
        "desc": "An undead officer still wearing its tattered uniform and a duty belt.",
        "type": MonsterType.ZOMBIE,
        "hp": 90, "dmg": 15, "speed": 3, "drain": 12,
        "loot": ["police_baton", "handcuffs", "pistol_ammo"], # New items
        "mass_kg": 95,
        "tags": ["zombie", "armored", "law_enforcement"]
    },
    "zombie_firefighter": {
        "name": "Zombie Firefighter",
        "desc": "Bulky and strong, this undead wears heavy, fire-resistant gear.",
        "type": MonsterType.ZOMBIE,
        "hp": 110, "dmg": 18, "speed": 2, "drain": 15,
        "loot": ["fire_axe", "heavy_gloves", "canned_food"], # New item
        "mass_kg": 120,
        "tags": ["zombie", "armored", "heavy"]
    },
    "angry_protestor_zombie": {
        "name": "Angry Protestor Zombie",
        "desc": "It carries tattered signs and shambles with a lingering, primal rage.",
        "type": MonsterType.ZOMBIE,
        "hp": 60, "dmg": 10, "speed": 2, "drain": 8,
        "loot": ["wood_plank", "cardboard_sign"], # New item
        "mass_kg": 80,
        "tags": ["zombie", "agitated"]
    },
    "krawler_zombie": {
        "name": "Krawler Zombie",
        "desc": "Limbs twisted and broken, it drags itself across the ground with surprising speed.",
        "type": MonsterType.ZOMBIE,
        "hp": 70, "dmg": 10, "speed": 4, "drain": 10,
        "loot": ["dirty_rag", "nails"],
        "mass_kg": 60, # Reduced mass due to crawling posture, but still resilient
        "tags": ["zombie", "fast", "low_profile"]
    },
    "vampire": {
        "name": "Inferior Vampire",
        "desc": "Not quite fully fledged, but still unnaturally fast and strong. It hungers.",
        "type": MonsterType.UNDEAD, # Using UNDEAD for now, will add VAMPIRE to Enum
        "hp": 120, "dmg": 20, "speed": 6, "drain": 25,
        "loot": ["blood_vial", "expensive_jewelry"], # New items
        "mass_kg": 85,
        "tags": ["vampire", "undead", "fast", "hungry"]
    },
    "starved_fledgling": {
        "name": "Starved Fledgling",
        "desc": "A newly-turned vampire, desperate for blood and dangerously erratic.",
        "type": MonsterType.UNDEAD, # Will be VAMPIRE
        "hp": 90, "dmg": 15, "speed": 5, "drain": 20,
        "loot": ["blood_vial"],
        "mass_kg": 70,
        "tags": ["vampire", "undead", "fledgling"]
    },
    "fat_vampire": {
        "name": "Obese Vampire",
        "desc": "Bloated from countless victims, this vampire is sluggish but immensely powerful.",
        "type": MonsterType.UNDEAD, # Will be VAMPIRE
        "hp": 250, "dmg": 30, "speed": 2, "drain": 40,
        "loot": ["fine_clothing", "antique_coin"], # New items
        "mass_kg": 150,
        "tags": ["vampire", "undead", "heavy", "boss"]
    },
    "day_walker": {
        "name": "Day Walker",
        "desc": "A rare and terrifying vampire, immune to sunlight and moving with purpose.",
        "type": MonsterType.UNDEAD, # Will be VAMPIRE
        "hp": 180, "dmg": 25, "speed": 7, "drain": 35,
        "loot": ["sunglasses", "designer_clothing", "ancient_relic"], # New items
        "mass_kg": 80,
        "tags": ["vampire", "undead", "sun_immune", "rare", "boss"]
    },
    "werewolf": {
        "name": "Lesser Werewolf",
        "desc": "A frenzied beast of fang and claw, its human form barely contained.",
        "type": MonsterType.BEAST, # Will be WEREWOLF
        "hp": 150, "dmg": 25, "speed": 8, "drain": 30,
        "loot": ["animal_pelt", "raw_meat"],
        "mass_kg": 180,
        "tags": ["werewolf", "beast", "alpha", "feral"] # "Alpha" tag for boss mechanics
    },
    "werebadger": {
        "name": "Werebadger",
        "desc": "A stocky, furious creature combining badger tenacity with lycanthropic strength.",
        "type": MonsterType.BEAST, # Will be WEREWOLF (or new WEREBEAST)
        "hp": 130, "dmg": 22, "speed": 7, "drain": 28,
        "loot": ["animal_pelt", "claws"],
        "mass_kg": 120,
        "tags": ["werebeast", "badger", "tenacious"]
    },
    "werepire": {
        "name": "Were-pire",
        "desc": "A horrific hybrid, blending the raw savagery of a werewolf with the cunning and thirst of a vampire.",
        "type": MonsterType.DEMON, # For now, a unique blend, could be its own type
        "hp": 300, "dmg": 40, "speed": 10, "drain": 50,
        "loot": ["rare_blood", "supernatural_fang", "ancient_scroll"], # New items
        "mass_kg": 250,
        "tags": ["werepire", "hybrid", "boss", "supernatural"]
    },
    "black_bear": {
        "name": "Black Bear",
        "desc": "A wild bear, made aggressive by the encroaching chaos.",
        "type": MonsterType.BEAST,
        "hp": 100, "dmg": 18, "speed": 4, "drain": 10,
        "loot": ["animal_pelt", "raw_meat", "bear_claws"],
        "mass_kg": 150,
        "tags": ["beast", "predator"]
    },
    "brown_bear": {
        "name": "Brown Bear",
        "desc": "Larger and fiercer than its black counterpart, a true force of nature.",
        "type": MonsterType.BEAST,
        "hp": 180, "dmg": 28, "speed": 5, "drain": 15,
        "loot": ["animal_pelt", "raw_meat", "bear_claws"],
        "mass_kg": 300,
        "tags": ["beast", "predator", "heavy"]
    },
    "honey_badger": {
        "name": "Honey Badger",
        "desc": "Small but unbelievably aggressive and fearless.",
        "type": MonsterType.BEAST,
        "hp": 60, "dmg": 15, "speed": 6, "drain": 10,
        "loot": ["animal_pelt", "tough_hide"],
        "mass_kg": 15, # Surprisingly light for its ferocity
        "tags": ["beast", "aggressive", "small"]
    },
    "poltergeist": {
        "name": "Poltergeist",
        "desc": "An unseen force that throws objects and chills the air.",
        "type": MonsterType.SPIRIT,
        "hp": 80, "dmg": 5, "speed": 0, "drain": 15, # Physical damage low, mental drain high
        "loot": [],
        "mass_kg": 0, # Non-corporeal
        "tags": ["spirit", "non_corporeal", "environmental"]
    },
    "ghost": {
        "name": "Wailing Ghost",
        "desc": "A translucent figure, its mournful cries induce dread.",
        "type": MonsterType.SPIRIT,
        "hp": 70, "dmg": 8, "speed": 3, "drain": 20,
        "loot": [],
        "mass_kg": 0, # Non-corporeal
        "tags": ["spirit", "non_corporeal", "fear_inducing"]
    },
    "rabid_raccoon": {
        "name": "Rabid Raccoon",
        "desc": "Foaming at the mouth, it charges without fear, infected with pure aggression.",
        "type": MonsterType.BEAST,
        "hp": 25, "dmg": 10, "speed": 7, "drain": 5,
        "loot": [],
        "mass_kg": 8,
        "tags": ["beast", "rabid", "aggressive", "small"]
    },
    "rabid_deer": {
        "name": "Rabid Deer",
        "desc": "Its eyes are bloodshot, its movements erratic. It kicks and charges with deadly force.",
        "type": MonsterType.BEAST,
        "hp": 60, "dmg": 15, "speed": 6, "drain": 8,
        "loot": ["raw_meat", "animal_pelt"],
        "mass_kg": 100,
        "tags": ["beast", "rabid", "aggressive"]
    },
    "mad_scientist_zombie": {
        "name": "Mad Scientist Zombie",
        "desc": "Its lab coat is torn, its face grotesquely eager. It wields a strange, sparking device.",
        "type": MonsterType.ZOMBIE,
        "hp": 100, "dmg": 15, "speed": 2, "drain": 20,
        "loot": ["chemicals", "broken_device", "research_notes"], # New items
        "mass_kg": 80,
        "tags": ["zombie", "special", "unstable_abilities"]
    },
    "bodybuilder_zombie": {
        "name": "Bodybuilder Zombie",
        "desc": "Bulky muscles still twitch under decaying skin. Its punches are devastating.",
        "type": MonsterType.ZOMBIE,
        "hp": 130, "dmg": 22, "speed": 3, "drain": 12,
        "loot": ["protein_powder", "weights"], # New items
        "mass_kg": 110,
        "tags": ["zombie", "strong", "heavy"]
    },
    "blood_farm_human": {
        "name": "Blood Farm Human",
        "desc": "A gaunt, pale human with vacant eyes, kept as a blood source for something worse.",
        "type": MonsterType.HUMAN,
        "hp": 30, "dmg": 1, "speed": 1, "drain": 10, # Very weak, but sanity drain from sight
        "loot": ["empty_blood_bag", "malnourished_rations"], # New items
        "mass_kg": 50,
        "tags": ["human", "victim", "sanity_risk"]
    },
    "skunk": {
        "name": "Skunk",
        "desc": "A small, pungent mammal. Best avoided.",
        "type": MonsterType.BEAST,
        "hp": 15, "dmg": 2, "speed": 3, "drain": 0,
        "loot": [],
        "mass_kg": 3,
        "tags": ["beast", "nuisance", "spray"]
    },
    "deer": {
        "name": "White-Tailed Deer",
        "desc": "A skittish herbivore, normally harmless but easily startled.",
        "type": MonsterType.BEAST,
        "hp": 40, "dmg": 5, "speed": 5, "drain": 0,
        "loot": ["raw_meat", "animal_pelt"],
        "mass_kg": 70,
        "tags": ["beast", "herbivore", "prey"]
    },
    "stag": {
        "name": "Large Stag",
        "desc": "A majestic deer with impressive antlers, capable of a powerful charge.",
        "type": MonsterType.BEAST,
        "hp": 80, "dmg": 15, "speed": 6, "drain": 0,
        "loot": ["raw_meat", "animal_pelt", "antlers"], # New item
        "mass_kg": 150,
        "tags": ["beast", "herbivore", "aggressive_on_provoke"]
    },
    "rabbit": {
        "name": "Wild Rabbit",
        "desc": "A small, fast creature. Hard to catch, easy to overlook.",
        "type": MonsterType.BEAST,
        "hp": 5, "dmg": 1, "speed": 8, "drain": 0,
        "loot": ["raw_meat"],
        "mass_kg": 2,
        "tags": ["beast", "prey", "small"]
    },
    "house_cat": {
        "name": "Feral House Cat",
        "desc": "Once a pet, now a lean hunter, distrustful of humans.",
        "type": MonsterType.BEAST,
        "hp": 10, "dmg": 3, "speed": 7, "drain": 0,
        "loot": ["raw_meat"],
        "mass_kg": 4,
        "tags": ["beast", "domestic", "small"]
    },
    }