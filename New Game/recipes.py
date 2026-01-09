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
}
