# --- START OF FILE narrator.py ---
import textwrap
import random
from entities import BehaviorState

class Narrator:
    @staticmethod
    def describe_scene(location, player):
        lines = []
        base_desc = location.description
        
        # --- HALLUCINATION OVERLAYS ---
        if player.paranoia > 50:
            phantoms = [
                ' You swear you saw a shadow slip behind the door.',
                ' A faint scratching sound comes from the walls.',
                ' You feel a heavy gaze lingering on your neck.'
            ]
            base_desc += random.choice(phantoms)
            
        if player.psychosis > 75:
            glitch = random.choice([
                ' [!] The walls appear to be breathing.',
                ' [!] Gravity feels "wrong" here.',
                ' [!] The colors of the room are inverted.'
            ])
            base_desc = f'{glitch} {base_desc}'
        lines.append(f'\n--- {location.name.upper()} ---')
        lines.append(textwrap.fill(base_desc, width=80))
        
        if player.psychosis > 65 and random.random() < 0.2:
            lines.append('  * A Shimmering Figure stands in the corner, watching.')
            
        # 2. Player-Built Structures
        if location.structures:
            lines.append('\n[BUILT STRUCTURES]:')
            for s in location.structures:
                lines.append(f'  - {s.name}: {s.description}')
                
        # 3. Static Containers (Furniture)
        if location.containers:
            furniture = [c.name for c in location.containers if 'Dead' not in c.name]
            if furniture:
                lines.append(f'\nFurniture: { ", ".join(furniture) }')
                
        # 4. Survivors
        if location.survivors:
            lines.append('\n[SURVIVORS]:')
            for s in location.survivors:
                lines.append(f'  * {s.name} is hiding here. (Type "recruit" to save them)')
                
        # 5. Monsters
        alive_monsters = [m for m in location.monsters if m.behavior != BehaviorState.DEAD]
        if alive_monsters:
            lines.append('\n[ENEMIES]:')
            for m in alive_monsters:
                status = 'attacking you!' if m.behavior == BehaviorState.AGGRO else 'watching...'
                lines.append(f'  !!! A {m.name} is here, {status}')
                
        # 6. Corpses
        corpses = [c for c in location.containers if 'Dead' in c.name]
        if corpses:
             lines.append(f'\nCorpses: { ", ".join([c.name for c in corpses]) }')
             
        # 7. Items on the floor
        if location.items:
            # IMPROVEMENT: Use get_display_name() to see durability/charges on the floor
            item_names = [i.get_display_name() for i in location.items]
            lines.append(f'\nOn the ground: { ", ".join(item_names) }')
            
        # 8. Exits
        lines.append(f'\nExits: { ", ".join(location.exits.keys()).upper() }')
        
        return '\n'.join(lines)
        
    @staticmethod
    def combat_log(attacker_name, target_name, damage, weapon_name, is_dead):
        if damage <= 0:
            verbs = ['glances off', 'scratches', 'fails to hurt']
        elif damage < 10:
            verbs = ['hits', 'bruises', 'cuts', 'grazes']
        elif damage < 30:
            verbs = ['bashes', 'slashes', 'wounds', 'strikes']
        else:
            verbs = ['crushes', 'obliterates', 'devastates', 'maims']
        
        verb = random.choice(verbs)
        msg = f'{attacker_name} {verb} {target_name} with {weapon_name} for {damage} damage!'
        if is_dead:
            death_desc = random.choice([
                'It collapses lifelessly.', 
                'It is destroyed.', 
                'The light fades from its eyes.'
            ])
            msg += f' {death_desc}'
        return msg
        
    @staticmethod
    def resident_dialogue(resident, player_psychosis):
        if player_psychosis > 70:
            whispers = [
                'They are looking at your throat.',
                'He is hiding a knife behind his back.',
                'She knows you are weak.'
            ]
            return f'{resident.name} says something, but all you hear is: "{random.choice(whispers)}"'
        return f'{resident.name}: "We need more wood planks for the north window."'