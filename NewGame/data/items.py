# --- START OF FILE data/items.py ---

from entities import ItemType

ITEM_TEMPLATES = {
    # ==========================================
    # --- MELEE WEAPONS ---
    # ==========================================
    "fists": { # Fallback weapon
        "name": "Fists", "desc": "Your bare hands.",
        "weight": 0.0, "type": ItemType.WEAPON, "props": {"damage": 2}, "tags": ["melee", "blunt"]
    },
    "rock": {
        "name": "Rock", "desc": "A jagged stone. Good for smashing.",
        "weight": 1.0, "type": ItemType.WEAPON, "props": {"damage": 4, "ranged_damage": 5, "range": 4}, "tags": ["melee", "thrown", "blunt"]
    },
    "brick": {
        "name": "Red Brick", "desc": "Heavy and rough.",
        "weight": 1.5, "type": ItemType.WEAPON, "props": {"damage": 5, "ranged_damage": 8}, "tags": ["melee", "thrown", "blunt"]
    },
    "shiv": {
        "name": "Toothbrush Shiv", "desc": "A sharpened plastic handle.",
        "weight": 0.1, "type": ItemType.WEAPON, "props": {"damage": 8, "fast": True}, "tags": ["melee", "pierce", "stealth"]
    },
    "switchblade": {
        "name": "Switchblade", "desc": "A small folding knife. Fast.",
        "weight": 0.2, "type": ItemType.WEAPON, "props": {"damage": 10, "fast": True}, "tags": ["melee", "pierce", "slash"]
    },
    "kitchen_knife": {
        "name": "Kitchen Knife", "desc": "8-inch chef's knife. Very sharp.",
        "weight": 0.3, "type": ItemType.WEAPON, "props": {"damage": 14}, "tags": ["melee", "slash", "tool"]
    },
    "hammer": {
        "name": "Claw Hammer", "desc": "Good for nails and skulls.",
        "weight": 1.0, "type": ItemType.WEAPON, "props": {"damage": 12}, "tags": ["melee", "blunt", "tool"]
    },
    "wrench": {
        "name": "Pipe Wrench", "desc": "Heavy iron tool.",
        "weight": 2.5, "type": ItemType.WEAPON, "props": {"damage": 15}, "tags": ["melee", "blunt", "tool"]
    },
    "screwdriver": {
        "name": "Screwdriver", "desc": "A long flathead. Good for stabbing.",
        "weight": 0.2, "type": ItemType.WEAPON, "props": {"damage": 6, "pierce": True}, "tags": ["melee", "pierce", "tool"]
    },
    "crowbar": {
        "name": "Crowbar", "desc": "Painted red. Opens doors and crates.",
        "weight": 2.5, "type": ItemType.WEAPON, "props": {"damage": 18, "pry": True}, "tags": ["melee", "blunt", "tool"]
    },
    "baseball_bat": {
        "name": "Baseball Bat", "desc": "Ash wood. A classic.",
        "weight": 1.5, "type": ItemType.WEAPON, "props": {"damage": 20}, "tags": ["melee", "blunt"]
    },
    "nail_bat": {
        "name": "Spiked Bat", "desc": "A bat with rusty nails driven through it.",
        "weight": 1.8, "type": ItemType.WEAPON, "props": {"damage": 28, "bleed": True}, "tags": ["melee", "pierce", "blunt"]
    },
    "hatchet": {
        "name": "Camping Hatchet", "desc": "Small axe for chopping wood or limbs.",
        "weight": 1.2, "type": ItemType.WEAPON, "props": {"damage": 22, "chop": True}, "tags": ["melee", "slash", "tool"]
    },
    "fire_axe": {
        "name": "Fire Axe", "desc": "Heavy, two-handed axe. Devastating.",
        "weight": 4.0, "type": ItemType.WEAPON, "props": {"damage": 35, "two_handed": True, "chop": True}, "tags": ["melee", "slash", "heavy"]
    },
    "machete": {
        "name": "Machete", "desc": "Rusted blade for clearing brush.",
        "weight": 1.0, "type": ItemType.WEAPON, "props": {"damage": 25}, "tags": ["melee", "slash"]
    },
    "combat_knife": {
        "name": "Combat Knife", "desc": "Military grade Ka-Bar. Durable and lethal.",
        "weight": 0.5, "type": ItemType.WEAPON, "props": {"damage": 22}, "tags": ["melee", "slash", "pierce"]
    },
    "katana": {
        "name": "Replica Katana", "desc": "Cheap steel, but sharp enough.",
        "weight": 1.2, "type": ItemType.WEAPON, "props": {"damage": 30}, "tags": ["melee", "slash", "rare"]
    },
    "sledgehammer": {
        "name": "Sledgehammer", "desc": "Industrial demolition tool.",
        "weight": 6.0, "type": ItemType.WEAPON, "props": {"damage": 50, "two_handed": True, "slow": True}, "tags": ["melee", "blunt", "heavy"]
    },
    "makeshift_spear": {
        "name": "Pointy Stick", "desc": "A wood plank sharpened to a point.",
        "weight": 1.2, "type": ItemType.WEAPON, "props": {"damage": 15, "reach": True}, "tags": ["melee", "pierce", "crafted"]
    },
    "rusty_pipe": {
        "name": "Lead Pipe", "desc": "Heavy and corroded.",
        "weight": 2.0, "type": ItemType.WEAPON, "props": {"damage": 14}, "tags": ["melee", "blunt"]
    },
    "police_baton": {
        "name": "Police Baton", "desc": "Collapsible steel baton.",
        "weight": 0.8, "type": ItemType.WEAPON, "props": {"damage": 16}, "tags": ["melee", "blunt"]
    },

    # ==========================================
    # --- THROWABLES & EXPLOSIVES ---
    # ==========================================
    "molotov": {
        "name": "Molotov Cocktail", "desc": "Bottle filled with gas and a rag.",
        "weight": 0.8, "type": ItemType.WEAPON, "props": {"ranged_damage": 40, "fire": True, "area_effect": True}, "tags": ["thrown", "fire"]
    },
    "grenade": {
        "name": "Frag Grenade", "desc": "Pull pin, throw, run.",
        "weight": 0.5, "type": ItemType.WEAPON, "props": {"ranged_damage": 100, "area_effect": True}, "tags": ["thrown", "explosive", "military"]
    },

    # ==========================================
    # --- FOOD (Survival) ---
    # ==========================================
    "apple": {
        "name": "Red Apple", "desc": "Fresh fruit. A rare treat.",
        "weight": 0.2, "type": ItemType.FOOD, "props": {"hunger": 10, "thirst": 5}, "tags": ["food", "perishable"]
    },
    "berries": {
        "name": "Handful of Berries", "desc": "Hopefully not poisonous.",
        "weight": 0.1, "type": ItemType.FOOD, "props": {"hunger": 5, "thirst": 2}, "tags": ["food", "perishable"]
    },
    "canned_beans": {
        "name": "Canned Beans", "desc": "Baked beans in tomato sauce.",
        "weight": 0.5, "type": ItemType.FOOD, "props": {"hunger": 30, "thirst": 5}, "tags": ["food", "canned"]
    },
    "canned_peaches": {
        "name": "Canned Peaches", "desc": "Sweet and sugary.",
        "weight": 0.5, "type": ItemType.FOOD, "props": {"hunger": 20, "thirst": 15}, "tags": ["food", "canned"]
    },
    "canned_tuna": {
        "name": "Canned Tuna", "desc": "Protein packed.",
        "weight": 0.3, "type": ItemType.FOOD, "props": {"hunger": 25}, "tags": ["food", "canned"]
    },
    "canned_meat": {
        "name": "Spam", "desc": "Salty mystery meat block.",
        "weight": 0.4, "type": ItemType.FOOD, "props": {"hunger": 40, "thirst": -5}, "tags": ["food", "canned"]
    },
    "dog_food": {
        "name": "Dog Food", "desc": "Mushy meat chunks. Desperate times.",
        "weight": 0.5, "type": ItemType.FOOD, "props": {"hunger": 25, "sanity": -5}, "tags": ["food", "canned", "gross"]
    },
    "mre": {
        "name": "MRE", "desc": "Meal Ready to Eat. High calorie military ration.",
        "weight": 0.6, "type": ItemType.FOOD, "props": {"hunger": 80, "thirst": 5}, "tags": ["food", "military"]
    },
    "beef_jerky": {
        "name": "Beef Jerky", "desc": "Dried meat. Lasts forever.",
        "weight": 0.1, "type": ItemType.FOOD, "props": {"hunger": 15}, "tags": ["food", "dried"]
    },
    "chips": {
        "name": "Bag of Chips", "desc": "Mostly air, some potato.",
        "weight": 0.1, "type": ItemType.FOOD, "props": {"hunger": 10, "thirst": -5}, "tags": ["food", "junk"]
    },
    "chocolate_bar": {
        "name": "Chocolate Bar", "desc": "Melty, but provides energy.",
        "weight": 0.1, "type": ItemType.FOOD, "props": {"hunger": 15, "sanity": 5}, "tags": ["food", "junk"]
    },
    "rotten_meat": {
        "name": "Rotten Meat", "desc": "Smells horrific.",
        "weight": 0.5, "type": ItemType.FOOD, "props": {"hunger": 10, "poison": True, "sanity": -10}, "tags": ["food", "poison"]
    },

    # ==========================================
    # --- DRINK ---
    # ==========================================
    "bottled_water": {
        "name": "Bottled Water", "desc": "Clear, purified water.",
        "weight": 0.5, "type": ItemType.DRINK, "props": {"thirst": 50}, "tags": ["drink", "essential"]
    },
    "water_bottle": { # Alias for systems that look for this name
        "name": "Bottled Water", "desc": "Clear, purified water.",
        "weight": 0.5, "type": ItemType.DRINK, "props": {"thirst": 50}, "tags": ["drink", "essential"]
    },
    "dirty_water": {
        "name": "Dirty Water", "desc": "Murky water in a bottle. Needs boiling.",
        "weight": 0.5, "type": ItemType.DRINK, "props": {"thirst": 30, "poison_chance": 0.5}, "tags": ["drink", "unsafe"]
    },
    "soda": {
        "name": "Orange Soda", "desc": "Fizzy and sugary.",
        "weight": 0.4, "type": ItemType.DRINK, "props": {"thirst": 20, "hunger": 5}, "tags": ["drink", "junk"]
    },
    "whiskey": {
        "name": "Whiskey Bottle", "desc": "Good for wounds or forgetting.",
        "weight": 1.0, "type": ItemType.DRINK, "props": {"thirst": -10, "sanity": 20, "disinfect": True}, "tags": ["drink", "alcohol"]
    },
    "bleach": {
        "name": "Bleach", "desc": "Do not drink.",
        "weight": 1.0, "type": ItemType.JUNK, "props": {"poison": True, "cleaning": True}, "tags": ["chemical", "poison"]
    },

    # ==========================================
    # --- MEDICAL ---
    # ==========================================
    "rag": {
        "name": "Dirty Rag", "desc": "A torn piece of cloth. Infection risk if used on wounds.",
        "weight": 0.1, "type": ItemType.MEDS, "props": {"heal": 2, "infection_chance": 0.3}, "tags": ["meds", "crafting"]
    },
    "bandage": {
        "name": "Clean Bandage", "desc": "Sterile gauze to stop bleeding.",
        "weight": 0.1, "type": ItemType.MEDS, "props": {"heal": 15, "stop_bleed": True}, "tags": ["meds", "essential"]
    },
    "first_aid_kit": {
        "name": "First Aid Kit", "desc": "Professional medical supplies.",
        "weight": 1.0, "type": ItemType.MEDS, "props": {"heal": 60, "stop_bleed": True, "cure_infection": True}, "tags": ["meds", "essential"]
    },
    "antibiotics": {
        "name": "Antibiotics", "desc": "Pills to fight infection.",
        "weight": 0.05, "type": ItemType.MEDS, "props": {"cure_infection": True, "heal": 5}, "tags": ["meds", "pills"]
    },
    "painkillers": {
        "name": "Painkillers", "desc": "Opiates to numb the pain.",
        "weight": 0.05, "type": ItemType.MEDS, "props": {"heal": 5, "sanity": 5}, "tags": ["meds", "pills"]
    },
    "vitamins": {
        "name": "Vitamins", "desc": "Gummy bears, basically.",
        "weight": 0.1, "type": ItemType.MEDS, "props": {"heal": 2}, "tags": ["meds", "pills"]
    },

    # ==========================================
    # --- CLOTHING & ARMOR ---
    # ==========================================
    "tshirt": {
        "name": "Cotton T-Shirt", "desc": "Grey and worn.",
        "weight": 0.2, "type": ItemType.CLOTHING, "props": {"warmth": 1, "armor": 0}, "tags": ["clothing", "torso"]
    },
    "hoodie": {
        "name": "Thick Hoodie", "desc": "Warm and comfortable.",
        "weight": 0.5, "type": ItemType.CLOTHING, "props": {"warmth": 3, "armor": 1}, "tags": ["clothing", "torso"]
    },
    "leather_jacket": {
        "name": "Leather Jacket", "desc": "Offers some protection against bites.",
        "weight": 1.5, "type": ItemType.CLOTHING, "props": {"warmth": 4, "armor": 5}, "tags": ["clothing", "torso"]
    },
    "kevlar_vest": {
        "name": "Kevlar Vest", "desc": "Police issue body armor.",
        "weight": 4.0, "type": ItemType.CLOTHING, "props": {"warmth": 1, "armor": 15}, "tags": ["clothing", "torso", "military"]
    },
    "jeans": {
        "name": "Blue Jeans", "desc": "Denim is tough.",
        "weight": 0.6, "type": ItemType.CLOTHING, "props": {"warmth": 2, "armor": 2}, "tags": ["clothing", "legs"]
    },
    "cargo_pants": {
        "name": "Cargo Pants", "desc": "Lots of pockets.",
        "weight": 0.7, "type": ItemType.CLOTHING, "props": {"warmth": 2, "armor": 2, "capacity_bonus": 5}, "tags": ["clothing", "legs"]
    },
    "combat_boots": {
        "name": "Combat Boots", "desc": "Steel-toed.",
        "weight": 1.2, "type": ItemType.CLOTHING, "props": {"warmth": 3, "armor": 3, "kick_bonus": True}, "tags": ["clothing", "feet"]
    },
    "sneakers": {
        "name": "Sneakers", "desc": "Good for running.",
        "weight": 0.5, "type": ItemType.CLOTHING, "props": {"warmth": 1, "speed_bonus": True}, "tags": ["clothing", "feet"]
    },
    "gas_mask": {
        "name": "Gas Mask", "desc": "Protects against airborne toxins.",
        "weight": 1.0, "type": ItemType.CLOTHING, "props": {"filter": True, "armor": 2}, "tags": ["clothing", "head"]
    },
    "helmet": {
        "name": "Bicycle Helmet", "desc": "Better than nothing.",
        "weight": 0.5, "type": ItemType.CLOTHING, "props": {"armor": 5}, "tags": ["clothing", "head"]
    },
    "riot_helmet": {
        "name": "Riot Helmet", "desc": "Full face protection.",
        "weight": 1.5, "type": ItemType.CLOTHING, "props": {"armor": 12}, "tags": ["clothing", "head", "military"]
    },

    # ==========================================
    # --- WEARABLE CONTAINERS (Backpacks) ---
    # ==========================================
    # These items are typically "equipped" to increase inventory limit
    "fanny_pack": {
        "name": "Fanny Pack", "desc": "Small but handy.",
        "weight": 0.2, "type": ItemType.CLOTHING, "props": {"capacity": 5}, "tags": ["container", "belt"]
    },
    "school_bag": {
        "name": "School Backpack", "desc": "A standard bookbag.",
        "weight": 0.5, "type": ItemType.CLOTHING, "props": {"capacity": 10}, "tags": ["container", "back"]
    },
    "backpack": {
        "name": "Hiking Backpack", "desc": "Large frame pack for long treks.",
        "weight": 1.5, "type": ItemType.CLOTHING, "props": {"capacity": 20}, "tags": ["container", "back"]
    },
    "military_rucksack": {
        "name": "Military Rucksack", "desc": "Huge camouflaged pack. Holds everything.",
        "weight": 2.5, "type": ItemType.CLOTHING, "props": {"capacity": 35}, "tags": ["container", "back", "military"]
    },
    "duffle_bag": {
        "name": "Duffle Bag", "desc": "A large gym bag. Awkward to carry.",
        "weight": 1.0, "type": ItemType.CLOTHING, "props": {"capacity": 25}, "tags": ["container", "hand"]
    },

    # ==========================================
    # --- CRAFTING MATERIALS & TOOLS ---
    # ==========================================
    "wood_plank": {
        "name": "Wood Plank", "desc": "Basic construction material.",
        "weight": 1.0, "type": ItemType.MATERIAL, "props": {}, "tags": ["wood", "build"]
    },
    "stick": {
        "name": "Stick", "desc": "A fallen branch.",
        "weight": 0.3, "type": ItemType.MATERIAL, "props": {"burn_time": 10}, "tags": ["wood", "fuel"]
    },
    "scrap_metal": {
        "name": "Scrap Metal", "desc": "Rusted bits of iron.",
        "weight": 0.5, "type": ItemType.MATERIAL, "props": {}, "tags": ["metal", "build"]
    },
    "nails": {
        "name": "Box of Nails", "desc": "Required for building.",
        "weight": 0.2, "type": ItemType.MATERIAL, "props": {}, "tags": ["hardware", "build"]
    },
    "duct_tape": {
        "name": "Duct Tape", "desc": "Fixes everything.",
        "weight": 0.2, "type": ItemType.MATERIAL, "props": {"repair": True}, "tags": ["crafting", "essential"]
    },
    "rope": {
        "name": "Coil of Rope", "desc": "Sturdy nylon rope.",
        "weight": 1.0, "type": ItemType.MATERIAL, "props": {}, "tags": ["crafting", "climbing"]
    },
    "glass_shard": {
        "name": "Glass Shard", "desc": "Sharp.",
        "weight": 0.1, "type": ItemType.MATERIAL, "props": {"damage": 2}, "tags": ["sharp"]
    },
    "plastic_bottle": {
        "name": "Empty Bottle", "desc": "Can hold water.",
        "weight": 0.1, "type": ItemType.MATERIAL, "props": {"holds_liquid": True}, "tags": ["plastic", "container"]
    },
    "lighter": {
        "name": "Lighter", "desc": "Creates fire.",
        "weight": 0.05, "type": ItemType.TOOL, "props": {"fire": True}, "tags": ["tool", "light"]
    },
    "matches": {
        "name": "Box of Matches", "desc": "Creates fire, but wind is an enemy.",
        "weight": 0.02, "type": ItemType.TOOL, "props": {"fire": True}, "tags": ["tool", "light"]
    },
    "flashlight": {
        "name": "Flashlight", "desc": "Batteries included.",
        "weight": 0.4, "type": ItemType.TOOL, "props": {"light": True}, "tags": ["tool", "light"]
    },
    "fat": {
        "name": "Animal Fat", "desc": "Greasy and flammable.",
        "weight": 0.2, "type": ItemType.MATERIAL, "props": {}, "tags": ["material", "fuel"]
    },
    "feather": {
        "name": "Bird Feather", "desc": "Used for fletching arrows.",
        "weight": 0.01, "type": ItemType.MATERIAL, "props": {}, "tags": ["material"]
    },
    "stones": {
        "name": "Small Stones", "desc": "A collection of smooth rocks.",
        "weight": 1.0, "type": ItemType.MATERIAL, "props": {}, "tags": ["material", "build"]
    },
    "makeshift_torch": {
        "name": "Makeshift Torch", "desc": "A rag soaked in fat on a stick.",
        "weight": 0.5, "type": ItemType.TOOL, "props": {"fire": True, "lifespan": 50}, "tags": ["light", "fire"]
    },
    "canvas": {
        "name": "Tattered Canvas", "desc": "Heavy, weather-worn fabric.",
        "weight": 1.5, "type": ItemType.MATERIAL, "props": {}, "tags": ["material", "build"]
    },
    "metal_sheet": {
        "name": "Scrap Metal Sheet", "desc": "A rusted but sturdy piece of siding.",
        "weight": 5.0, "type": ItemType.MATERIAL, "props": {}, "tags": ["material", "build", "heavy"]
    },
    "copper_tubing": {
        "name": "Copper Tubing", "desc": "Salvaged from an old AC unit.",
        "weight": 0.8, "type": ItemType.MATERIAL, "props": {}, "tags": ["material", "crafting"]
    },
    "glass_bottle": {
        "name": "Empty Glass Bottle", "desc": "Clear and unbroken.",
        "weight": 0.3, "type": ItemType.MATERIAL, "props": {}, "tags": ["material", "container"]
    },
    "fishing_line": {
        "name": "Fishing Line", "desc": "Thin, strong, and nearly invisible.",
        "weight": 0.05, "type": ItemType.MATERIAL, "props": {}, "tags": ["material", "trap"]
    },
    "tin_cans": {
        "name": "Empty Tin Cans", "desc": "A few cans tied together.",
        "weight": 0.2, "type": ItemType.MATERIAL, "props": {}, "tags": ["material", "trap"]
    },

    # ==========================================
    # --- JUNK & FLAVOR ---
    # ==========================================
    "cash_card": {
        "name": "Cash Card", "desc": "Useless plastic now.",
        "weight": 0.0, "type": ItemType.JUNK, "props": {}, "tags": ["junk"]
    },
    "wallet": {
        "name": "Leather Wallet", "desc": "Contains photos of a stranger's family.",
        "weight": 0.1, "type": ItemType.JUNK, "props": {}, "tags": ["junk", "sad"]
    },
    "teddy_bear": {
        "name": "Teddy Bear", "desc": "Missing an eye.",
        "weight": 0.3, "type": ItemType.JUNK, "props": {"sanity": 2}, "tags": ["junk", "comfort"]
    },
    "cigarettes": {
        "name": "Pack of Cigarettes", "desc": "Unhealthy, but calming.",
        "weight": 0.1, "type": ItemType.CONSUMABLE, "props": {"sanity": 10, "hp": -1}, "tags": ["luxury", "drug"]
    },
    "newspaper": {
        "name": "Old Newspaper", "desc": "Headlines scream about the outbreak.",
        "weight": 0.1, "type": ItemType.JUNK, "props": {"burn_time": 2}, "tags": ["paper", "fuel"]
    },
    "battery": {
        "name": "AA Battery", "desc": "might be useful.",
        "weight": 0.05, "type": ItemType.JUNK, "props": {}, "tags": ["electronics"]
    },
    "watch": {
        "name": "Broken Watch", "desc": "A simple analog watch, stopped at 3:17.",
        "weight": 0.05, "type": ItemType.JUNK, "props": {}, "tags": ["junk", "personal"]
    },
    "handcuffs": {
        "name": "Handcuffs", "desc": "Standard police issue. Maybe useful for restraining something?",
        "weight": 0.5, "type": ItemType.TOOL, "props": {"restrain": True}, "tags": ["tool", "restraint"]
    },
    "pistol_ammo": {
        "name": "Pistol Ammo (9mm)", "desc": "A box of 9mm cartridges.",
        "weight": 0.2, "type": ItemType.AMMO, "props": {"caliber": "9mm", "quantity": 12}, "tags": ["ammo", "firearm"]
    },
    "heavy_gloves": {
        "name": "Heavy Duty Gloves", "desc": "Thick work gloves. Offer some protection.",
        "weight": 0.3, "type": ItemType.CLOTHING, "props": {"warmth": 1, "armor": 1, "slot": "hands"}, "tags": ["clothing", "hands", "tool"]
    },
    "cardboard_sign": {
        "name": "Cardboard Sign", "desc": "Faded protest slogan, barely legible.",
        "weight": 0.2, "type": ItemType.JUNK, "props": {}, "tags": ["junk", "fuel"]
    },
    "blood_vial": {
        "name": "Vial of Blood", "desc": "Fresh, still warm. Unsettling.",
        "weight": 0.1, "type": ItemType.CONSUMABLE, "props": {"hp": 10, "thirst": 5, "sanity_gain": -5}, "tags": ["consumable", "gross"]
    },
    "expensive_jewelry": {
        "name": "Expensive Jewelry", "desc": "Glimmering gold and gems. Likely valuable, if there were any buyers.",
        "weight": 0.1, "type": ItemType.JUNK, "props": {"trade_value": 50}, "tags": ["junk", "valuables"]
    },
    "fine_clothing": {
        "name": "Fine Clothing", "desc": "Well-tailored, but now stained and tattered.",
        "weight": 0.5, "type": ItemType.CLOTHING, "props": {"warmth": 2, "armor": 0}, "tags": ["clothing"]
    },
    "antique_coin": {
        "name": "Antique Coin", "desc": "Old and possibly valuable.",
        "weight": 0.01, "type": ItemType.JUNK, "props": {"trade_value": 20}, "tags": ["junk", "valuables"]
    },
    "sunglasses": {
        "name": "Sunglasses", "desc": "Fashionable, provides minor glare protection.",
        "weight": 0.1, "type": ItemType.CLOTHING, "props": {"slot": "eyes"}, "tags": ["clothing", "fashion"]
    },
    "designer_clothing": {
        "name": "Designer Clothing", "desc": "High-end fashion, now just rags.",
        "weight": 0.6, "type": ItemType.CLOTHING, "props": {"warmth": 2, "armor": 0}, "tags": ["clothing", "fashion"]
    },
    "ancient_relic": {
        "name": "Ancient Relic", "desc": "An artifact of unknown origin, pulsating faintly.",
        "weight": 0.8, "type": ItemType.JUNK, "props": {"sanity_gain": 10, "reality_influence": 0.1}, "tags": ["junk", "mystical", "quest_item"]
    },
    "animal_pelt": {
        "name": "Animal Pelt", "desc": "The hide of a wild animal. Good for crafting.",
        "weight": 1.0, "type": ItemType.MATERIAL, "props": {}, "tags": ["material", "crafting"]
    },
    "raw_meat": {
        "name": "Raw Meat", "desc": "Freshly harvested meat. Needs cooking.",
        "weight": 0.5, "type": ItemType.FOOD, "props": {"hunger": 15, "poison_chance": 0.5}, "tags": ["food", "perishable"]
    },
    "claws": {
        "name": "Animal Claws", "desc": "Sharp talons from a beast. Crafting material.",
        "weight": 0.1, "type": ItemType.MATERIAL, "props": {}, "tags": ["material", "crafting"]
    },
    "bear_claws": {
        "name": "Bear Claws", "desc": "Large, formidable claws. Potent crafting material.",
        "weight": 0.2, "type": ItemType.MATERIAL, "props": {}, "tags": ["material", "crafting"]
    },
    "rare_blood": {
        "name": "Rare Blood Sample", "desc": "A vial of unique blood, shimmering with strange energies.",
        "weight": 0.1, "type": ItemType.CONSUMABLE, "props": {"hp": 30, "sanity_gain": -10, "reality_influence": 0.2}, "tags": ["consumable", "mystical", "research"]
    },
    "supernatural_fang": {
        "name": "Supernatural Fang", "desc": "A jagged, unnatural fang, still dripping ichor.",
        "weight": 0.3, "type": ItemType.MATERIAL, "props": {"pierce_damage": 5}, "tags": ["material", "crafting", "weapon_component"]
    },
    "ancient_scroll": {
        "name": "Ancient Scroll", "desc": "Covered in esoteric symbols and forgotten languages.",
        "weight": 0.1, "type": ItemType.JUNK, "props": {"sanity_gain": 5, "knowledge_chance": 0.05}, "tags": ["junk", "mystical", "lore"]
    },
    "chemicals": {
        "name": "Assorted Chemicals", "desc": "Various reagents. Potentially volatile.",
        "weight": 0.5, "type": ItemType.MATERIAL, "props": {}, "tags": ["material", "crafting", "volatile"]
    },
    "broken_device": {
        "name": "Broken Device", "desc": "A strange, sparking contraption. Looks like it once did something important.",
        "weight": 1.0, "type": ItemType.JUNK, "props": {"scrap_value": 3}, "tags": ["junk", "electronics", "scrap"]
    },
    "research_notes": {
        "name": "Tattered Research Notes", "desc": "Unsettling insights into forbidden science.",
        "weight": 0.1, "type": ItemType.JUNK, "props": {"sanity_gain": -5, "knowledge_chance": 0.1}, "tags": ["junk", "lore"]
    },
    "protein_powder": {
        "name": "Protein Powder", "desc": "A dusty tub of pre-apocalypse gains.",
        "weight": 1.0, "type": ItemType.FOOD, "props": {"hunger": 40, "hp": 5}, "tags": ["food", "supplement"]
    },
    "weights": {
        "name": "Dumbbell", "desc": "A heavy, rusted dumbbell. More for smashing than lifting now.",
        "weight": 5.0, "type": ItemType.WEAPON, "props": {"damage": 25, "slow": True}, "tags": ["melee", "blunt", "heavy"]
    },
    "empty_blood_bag": {
        "name": "Empty Blood Bag", "desc": "Used for collecting or storing vital fluids.",
        "weight": 0.1, "type": ItemType.MATERIAL, "props": {"capacity": 1}, "tags": ["material", "medical"]
    },
    "malnourished_rations": {
        "name": "Malnourished Rations", "desc": "A grim meal, barely sustaining.",
        "weight": 0.3, "type": ItemType.FOOD, "props": {"hunger": 10}, "tags": ["food", "basic"]
    },
    "antlers": {
        "name": "Deer Antlers", "desc": "Heavy, bone-like antlers. Could be weaponized or used in crafting.",
        "weight": 2.0, "type": ItemType.MATERIAL, "props": {"blunt_damage": 8}, "tags": ["material", "crafting", "weapon_component"]
    },
    "tough_hide": {
        "name": "Tough Hide", "desc": "A thick animal hide, resilient to damage.",
        "weight": 1.5, "type": ItemType.MATERIAL, "props": {}, "tags": ["material", "crafting"]
    },
    "string": {
        "name": "Ball of String", "desc": "Thin but useful for small tasks.",
        "weight": 0.05, "type": ItemType.MATERIAL, "props": {}, "tags": ["material", "crafting"]
    },
    "water_proof_matches": {
        "name": "Waterproof Matches", "desc": "Reliable fire starters, even in damp conditions.",
        "weight": 0.02, "type": ItemType.TOOL, "props": {"fire": True}, "tags": ["tool", "light", "reliable"]
    },
    "fishing_line": {
        "name": "Fishing Line", "desc": "Strong nylon line.",
        "weight": 0.05, "type": ItemType.MATERIAL, "props": {}, "tags": ["material", "crafting", "fishing"]
    },
    "bolo_machete": {
        "name": "Bolo Machete", "desc": "A heavy, curved blade, excellent for chopping.",
        "weight": 1.5, "type": ItemType.WEAPON, "props": {"damage": 28, "chop": True}, "tags": ["melee", "slash", "tool"]
    },
    "unreliable_shotgun": {
        "name": "Unreliable Shotgun", "desc": "Old and prone to jamming, but still lethal up close.",
        "weight": 3.0, "type": ItemType.WEAPON, "props": {"damage": 50, "ranged": True, "ammo": "shotgun_shell", "jam_chance": 0.3}, "tags": ["ranged", "firearm"] # New ammo type
    },
    "shotgun_shell": { # Needed for unreliable shotgun
        "name": "Shotgun Shell", "desc": "12-gauge shotgun ammunition.",
        "weight": 0.05, "type": ItemType.AMMO, "props": {"caliber": "12_gauge", "quantity": 1}, "tags": ["ammo", "firearm"]
    },
    "twine": {
        "name": "Roll of Twine", "desc": "Rough, strong cordage.",
        "weight": 0.1, "type": ItemType.MATERIAL, "props": {}, "tags": ["material", "crafting"]
    },
    "hiking_bag": {
        "name": "Hiking Bag", "desc": "A moderately sized backpack.",
        "weight": 1.0, "type": ItemType.CLOTHING, "props": {"capacity": 15}, "tags": ["container", "back"]
    },
    "pack_of_batteries_4": {
        "name": "Pack of Batteries (4xAA)", "desc": "Four AA batteries.",
        "weight": 0.2, "type": ItemType.CONSUMABLE, "props": {"charges": 4, "battery_type": "AA"}, "tags": ["consumable", "electronics"]
    },
    "pack_of_batteries_36": {
        "name": "Pack of Batteries (36xAA)", "desc": "A bulk pack of AA batteries.",
        "weight": 1.8, "type": ItemType.CONSUMABLE, "props": {"charges": 36, "battery_type": "AA"}, "tags": ["consumable", "electronics", "rare"]
    },
    "new_shotgun": {
        "name": "Pump-Action Shotgun", "desc": "A pristine shotgun. Reliable and powerful.",
        "weight": 4.0, "type": ItemType.WEAPON, "props": {"damage": 60, "ranged": True, "ammo": "shotgun_shell", "jam_chance": 0.05}, "tags": ["ranged", "firearm", "rare"]
    },
    "new_water_purifier": {
        "name": "Portable Water Purifier", "desc": "Cleans dirty water. Essential survival gear.",
        "weight": 1.0, "type": ItemType.TOOL, "props": {"purify_liquid": True, "uses": 20}, "tags": ["tool", "survival", "rare"]
    },
    "new_multi_tool": { # Example for 'new [tools]'
        "name": "High-Quality Multi-Tool", "desc": "A versatile tool with many functions.",
        "weight": 0.5, "type": ItemType.TOOL, "props": {"crafting_bonus": 0.1, "repair_bonus": 0.1}, "tags": ["tool", "crafting", "rare"]
    },
    "unreliable_lighter": {
        "name": "Unreliable Lighter", "desc": "Flicks often, but sometimes sparks.",
        "weight": 0.05, "type": ItemType.TOOL, "props": {"fire": True, "reliability": 0.5}, "tags": ["tool", "light"]
    },
    "copper_wire": {
        "name": "Copper Wire", "desc": "Thin strands of conductive metal.",
        "weight": 0.1, "type": ItemType.MATERIAL, "props": {}, "tags": ["material", "electronics", "crafting"]
    },
    "screws": {
        "name": "Handful of Screws", "desc": "Small fasteners.",
        "weight": 0.05, "type": ItemType.MATERIAL, "props": {}, "tags": ["hardware", "build"]
    },
    "fork": {
        "name": "Bent Fork", "desc": "Useful for eating, less so for fighting.",
        "weight": 0.05, "type": ItemType.JUNK, "props": {"damage": 1}, "tags": ["junk", "utensil"]
    },
    "dirty_shoes": {
        "name": "Dirty Shoes", "desc": "Worn and scuffed sneakers.",
        "weight": 0.5, "type": ItemType.CLOTHING, "props": {"warmth": 1, "speed_bonus": True}, "tags": ["clothing", "feet"]
    },
    "dirty_boots": {
        "name": "Dirty Boots", "desc": "Mud-caked work boots.",
        "weight": 1.2, "type": ItemType.CLOTHING, "props": {"warmth": 2, "armor": 1}, "tags": ["clothing", "feet"]
    },
    "dead_battery": {
        "name": "Dead AA Battery", "desc": "Completely drained of power.",
        "weight": 0.05, "type": ItemType.JUNK, "props": {}, "tags": ["junk", "electronics"]
    },
}