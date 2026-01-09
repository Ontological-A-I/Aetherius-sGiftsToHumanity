from entities import MonsterType

MONSTER_TEMPLATES = {
    "shambler": {
        "name": "Rotting Shambler",
        "desc": "A decomposing corpse, shuffling forward with relentless hunger.",
        "type": MonsterType.ZOMBIE,
        "hp": 40, "dmg": 6, "speed": 1, "drain": 5,
        "loot": ["rag", "cash_card", "lighter"]
    },
    "feral_soldier": {
        "name": "Feral Soldier",
        "desc": "A zombie in tattered military fatigues. It still wears a helmet.",
        "type": MonsterType.ZOMBIE,
        "hp": 80, "dmg": 12, "speed": 2, "drain": 10,
        "loot": ["combat_knife", "canned_meat", "mre", "kevlar_vest"]
    },
    "looter": {
        "name": "Desperate Looter",
        "desc": "A survivor looking for an easy score. They look nervous.",
        "type": MonsterType.HUMAN,
        "hp": 60, "dmg": 8, "speed": 4, "drain": 0,
        "loot": ["crowbar", "canned_beans", "water_bottle", "backpack"]
    },
    "wolf": {
        "name": "Starved Wolf",
        "desc": "A gaunt canine with matted fur and bared fangs.",
        "type": MonsterType.BEAST,
        "hp": 30, "dmg": 10, "speed": 5, "drain": 2,
        "loot": []
    },
}
