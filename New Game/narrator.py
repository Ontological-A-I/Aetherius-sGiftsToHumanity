# --- START OF FILE narrator.py ---

import textwrap
import random
from entities import BehaviorState

class Narrator:
    @staticmethod
    def describe_scene(location):
        """
        Generates a formatted string describing the location and everything in it.
        """
        lines = []
        
        # 1. Location Header & Description
        lines.append(f"\n--- {location.name.upper()} ---")
        lines.append(textwrap.fill(location.description, width=80))
        
        # 2. Player-Built Structures
        if location.structures:
            lines.append("\n[BUILT STRUCTURES]:")
            for s in location.structures:
                lines.append(f"  - {s.name}: {s.description}")

        # 3. Static Containers (Furniture)
        if location.containers:
            # Filter out Corpses from "Furniture" list, they are handled separately or with items
            furniture = [c.name for c in location.containers if "Dead" not in c.name]
            if furniture:
                lines.append(f"\nFurniture: {', '.join(furniture)}")

        # 4. Survivors (NEW)
        if location.survivors:
            lines.append("\n[SURVIVORS]:")
            for s in location.survivors:
                lines.append(f"  * {s.name} is hiding here. (Type 'recruit' to save them)")

        # 5. Monsters (Dynamic description based on state)
        alive_monsters = [m for m in location.monsters if m.behavior != BehaviorState.DEAD]
        
        if alive_monsters:
            lines.append("\n[ENEMIES]:")
            for m in alive_monsters:
                status = "attacking you!" if m.behavior == BehaviorState.AGGRO else "watching..."
                lines.append(f"  !!! A {m.name} is here, {status}")
        
        # 6. Corpses (Containers named "Dead ...")
        corpses = [c for c in location.containers if "Dead" in c.name]
        if corpses:
             lines.append(f"\nCorpses: {', '.join([c.name for c in corpses])}")

        # 7. Items on the floor
        if location.items:
            item_names = [i.name for i in location.items]
            lines.append(f"\nOn the ground: {', '.join(item_names)}")

        # 8. Exits
        lines.append(f"\nExits: {', '.join(location.exits.keys()).upper()}")
        
        return "\n".join(lines)

    @staticmethod
    def combat_log(attacker_name, target_name, damage, weapon_name, is_dead):
        """
        Generates a dynamic combat message.
        """
        if damage <= 0:
            verbs = ["glances off", "scratches", "fails to hurt"]
        elif damage < 10:
            verbs = ["hits", "bruises", "cuts", "grazes"]
        elif damage < 30:
            verbs = ["bashes", "slashes", "wounds", "strikes"]
        else:
            verbs = ["crushes", "obliterates", "devastates", "maims"]
        
        verb = random.choice(verbs)
        
        msg = f"{attacker_name} {verb} {target_name} with {weapon_name} for {damage} damage!"
        
        if is_dead:
            death_desc = random.choice([
                "It collapses lifelessly.", 
                "It is destroyed.", 
                "The light fades from its eyes."
            ])
            msg += f" {death_desc}"
        
        return msg