BUILDING_RECIPES = {
    "crate": {
        "name": "Wooden Crate", 
        "type": "STORAGE",
        "desc": "A rough wooden box for storing items. Keeps things organized.",
        "materials": {"wood_plank": 2, "nails": 1},
        "capacity": 10
    },
    "barricade": {
        "name": "Window Barricade", 
        "type": "DEFENSE",
        "desc": "Heavy planks nailed together to block entry.",
        "materials": {"wood_plank": 4, "nails": 4},
        "capacity": 0
    },
    "campfire": {
        "name": "Campfire", 
        "type": "UTILITY",
        "desc": "Provides light, warmth, and a place to cook.",
        "materials": {"wood_plank": 2, "stones": 5},
        "capacity": 0
    },
    "lean-to": {
        "name": "Makeshift Lean-To", 
        "type": "SHELTER",
        "desc": "A crude shelter that offers a place to rest and save.",
        "materials": {"wood_plank": 2, "canvas": 1},
        "save_point": True
    },
    "rain_catcher": {
        "name": "Rain Catcher", 
        "type": "UTILITY",
        "desc": "Collects rainwater over time.",
        "materials": {"metal_sheet": 1, "canvas": 1},
        "water_gen": True
    },
    "spike_trap": {
        "name": "Crude Spike Trap", 
        "type": "DEFENSE",
        "desc": "Sharpened sticks that damage intruders.",
        "materials": {"wood_plank": 2, "nails": 4},
        "trap_damage": 15
    },
    "tripwire": {
        "name": "Sound Tripwire", 
        "type": "DEFENSE",
        "desc": "Alerts you when something moves nearby.",
        "materials": {"fishing_line": 1, "tin_cans": 2},
        "early_warning": True
    },
    "workbench": {
        "name": "Makeshift Workbench", 
        "type": "CRAFTING",
        "desc": "Unlocks advanced crafting recipes.",
        "materials": {"wood_plank": 4, "nails": 8},
        "unlock_advanced": True
    },
}

CRAFTING_RECIPES = {
    "pointy_stick": {
        "result": "makeshift_spear",
        "desc": "Sharpen a plank into a crude spear.",
        "materials": {"wood_plank": 1}
    },
    "bandage": {
        "result": "bandage",
        "desc": "Sterilize a rag with alcohol (abstracted).",
        "materials": {"rag": 2}
    },
    "makeshift_bow": {
        "result": "makeshift_bow",
        "desc": "A crude but functional bow for ranged attacks.",
        "materials": {"stick": 2, "string": 1, "rope": 0, "twine": 0, "fishing_line": 0}, # Requires 1 of these string-like items
        "choose_material": ["string", "rope", "twine", "fishing_line"] # Suggestion for how to handle 'OR' materials
    },
    "makeshift_arrow": {
        "result": "makeshift_arrow",
        "desc": "A basic arrow, effective with a bow.",
        "materials": {"stick": 1, "glass_shard": 1, "feather": 1}, # New item 'feather' implies it needs to be added
        "bladed_item_tag": ["pierce", "slash"] # Placeholder, not a material, but a tool requirement.
    },
    # My idea for a recipe: Improvised Torch
    "improvised_torch": {
        "result": "makeshift_torch", # Assuming 'makeshift_torch' is defined in items.py (it's not yet)
        "desc": "A basic light source, offering warmth and keeping shadows at bay.",
        "materials": {"stick": 1, "rag": 1, "fat": 1}, # New item 'fat' implies it needs to be added
        "tool_required_tag": "fire" # Requires a lighter/matches to light initially
    }
}