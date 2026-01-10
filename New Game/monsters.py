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
    "mirror_stalker": {
        "name": "The Mirror Stalker",
        "desc": "A faceless humanoid whose skin reflects the room around it perfectly. It moves exactly as you do.",
        "type": MonsterType.SPIRIT,
        "hp": 200, "dmg": 15, "speed": 5, "drain": 20,
        "loot": ["shattered_glass", "echo_of_self"]
    },
    "architect_glass": {
        "name": "The Architect of Glass",
        "desc": "A towering mass of jagged geometry. It doesn't walk; it simply rearranges the space around it.",
        "type": MonsterType.DEMON,
        "hp": 350, "dmg": 25, "speed": 2, "drain": 30,
        "loot": ["void_crystal", "blueprints_of_nowhere"]
    }
}
