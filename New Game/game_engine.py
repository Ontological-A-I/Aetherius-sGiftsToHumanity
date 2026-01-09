# --- START OF FILE game_engine.py ---

import sys
import time
import random
from world_manager import WorldManager
from narrator import Narrator
from entities import Item, Structure, BehaviorState, ItemType, Container
from parser import CommandParser
from scent_tracking_system import ScentTrailManager, HunterAI
from combat_pattern_recognition import CombatTacticsEngine

class GameEngine:
    def __init__(self):
        self.wm = WorldManager()
        self.parser = CommandParser()
        self.scent_manager = ScentTrailManager()
        self.tactics_engine = CombatTacticsEngine()
        self.running = True

    def start(self):
        print("Initializing World...")
        if not self.wm.load():
            print("No save found. Generating new world...")
            self.wm.create_new_world()
        
        # Load external systems
        self.scent_manager.load()
        self.tactics_engine.load()

        print("\n" + "="*50)
        print("   S U R V I V A L   R P G")
        print("   Commands: look, go [dir], take [item], i")
        print("             attack [enemy] [head/legs/arms/torso]")
        print("             recruit [survivor], search [corpse/container]")
        print("             craft [item], build [struct]")
        print("="*50 + "\n")
        
        self.look()
        self.loop()

    def get_loc(self):
        p = self.wm.player
        return self.wm.generate_location(p.x, p.y)

    def find_object_fuzzy(self, search_term, object_list):
        if not search_term: return None
        search_term = search_term.lower()
        for obj in object_list:
            if obj.name.lower() == search_term: return obj
        for obj in object_list:
            if search_term in obj.name.lower(): return obj
        return None

    def loop(self):
        while self.running:
            if self.wm.player.hp < 0:
                print("\n\n" + "#"*30 + "\n   Y O U   H A V E   D I E D\n" + "#"*30)
                break

            try:
                cmd_raw = input("\n> ").strip().lower()
            except EOFError:
                break
            
            parsed = self.parser.parse(cmd_raw)
            if not parsed: continue

            verb = parsed["verb"]
            noun = parsed["noun"]
            
            turn_taken = self.process_command(verb, noun)

            if turn_taken and self.running and not self.wm.player.is_dying:
                self.monster_turns()
                self.wm.player.update_status()

    def process_command(self, verb, noun):
        player = self.wm.player
        loc = self.get_loc()

        if player.is_dying:
            allowed = ["use", "go", "inventory", "i", "quit"]
            if verb not in allowed:
                print("You are bleeding out! You can't do that right now!")
                return False

        if verb == "go":
            dx, dy = 0, 0
            if noun == "north": dy = 1
            elif noun == "south": dy = -1
            elif noun == "east": dx = 1
            elif noun == "west": dx = -1
            else:
                print("Go where?")
                return False
            
            player.x += dx
            player.y += dy
            new_loc = self.wm.generate_location(player.x, player.y)
            player.location_id = new_loc.location_id
            
            # SCENT: Record movement
            self.scent_manager.add_scent(player.location_id)
            
            print(f"You move {noun}...")
            self.look()
            return True

        elif verb == "look": self.look(); return False 
        elif verb == "inventory" or verb == "i": player.print_inventory(); return False
        elif verb == "status": player.print_stats(); return False
        elif verb == "take": return self.cmd_take(noun, loc)
        elif verb == "drop": return self.cmd_drop(noun, loc)
        elif verb in ["open", "search"]: return self.cmd_open(noun, loc)
        elif verb == "use": return self.cmd_use(noun)
        elif verb == "attack": return self.cmd_attack(noun, loc)
        elif verb == "build": return self.cmd_build(noun, loc)
        elif verb == "craft": return self.cmd_craft(noun)
        elif verb == "recruit": return self.cmd_recruit(noun, loc)
        elif verb == "save": 
            self.wm.save()
            self.scent_manager.save()
            self.tactics_engine.save()
            print("Game saved.")
            return False
        elif verb == "quit": self.running = False; return False
        else: print(f"I don't know how to '{verb}'."); return False

    def look(self):
        loc = self.get_loc()
        print(Narrator.describe_scene(loc))

    # --- UPDATED ATTACK LOGIC WITH LIMBS ---
    def cmd_attack(self, noun, loc):
        if not noun: print("Attack what?"); return False
        
        # Parse "attack zombie head" vs "attack zombie"
        parts = noun.split()
        target_limb = None
        target_name = noun
        
        potential_limbs = ["head", "legs", "leg", "arms", "arm", "torso"]
        if len(parts) > 1 and parts[-1] in potential_limbs:
            target_limb = parts[-1]
            target_name = " ".join(parts[:-1])

        monster = self.find_object_fuzzy(target_name, loc.monsters)
        
        if not monster:
            print(f"You don't see '{target_name}' here.")
            return False

        if monster.behavior == BehaviorState.DEAD:
            print(f"The {monster.name} is already dead.")
            return False

        # Calculate Damage
        weapon = self.wm.player.inventory[0] if self.wm.player.inventory else Item("fist", {"name": "Fist", "props": {"damage": 2}})
        damage = weapon.props.get("damage", 2)
        
        # Apply Tactics Adaptation
        penalty = self.tactics_engine.get_adaptation_penalty(target_limb)
        if penalty < 1.0:
            print(f"The {monster.name} anticipates your attack on its {target_limb or 'body'}!")
        damage = int(damage * penalty)

        # Limb targeting modifiers
        hit_desc = "body"
        if target_limb:
            hit_desc = target_limb
            self.tactics_engine.record_attack(target_limb)
            if "head" in target_limb:
                hit_chance = 0.4
                damage *= 2.0 # Critical hit
            elif "leg" in target_limb:
                hit_chance = 0.6
                damage *= 0.8 # Less damage but maybe slow them (not impl yet)
            else:
                hit_chance = 0.8
        else:
            hit_chance = 0.9 # General attack is easy to hit
            self.tactics_engine.record_attack("torso")

        if random.random() > hit_chance:
            print(f"You swing at the {monster.name}'s {hit_desc}, but miss!")
            return True

        # Deal Damage
        is_dead = monster.take_damage(damage)
        print(Narrator.combat_log("You", monster.name, damage, weapon.name, is_dead))

        # Handle Death (Corpse Conversion)
        if is_dead:
            print(f"The {monster.name} falls. You can search the corpse.")
            loc.monsters.remove(monster)
            
            # Create Corpse Container
            corpse = Container(f"Dead {monster.name}", "A fallen enemy.")
            corpse.inventory = monster.generate_loot()
            loc.containers.append(corpse)

        return True

    def monster_turns(self):
        # 1. Active Monsters in current room
        loc = self.get_loc()
        for m in loc.monsters:
            if m.behavior == BehaviorState.DEAD: continue
            
            # If aggressive, attack player
            if m.behavior == BehaviorState.AGGRO or random.random() < 0.5:
                dmg = m.dmg
                print(f"The {m.name} attacks you!")
                self.wm.player.take_damage(dmg)
                m.behavior = BehaviorState.AGGRO
            else:
                print(f"The {m.name} growls at you.")

        # 2. Scent Tracking (Monsters in adjacent rooms moving in)
        # Note: In a full game, we'd iterate ALL active monsters. 
        # For optimization, we only check adjacent rooms here.
        adj_coords = [
            (loc.x+1, loc.y), (loc.x-1, loc.y),
            (loc.x, loc.y+1), (loc.x, loc.y-1)
        ]
        
        for ax, ay in adj_coords:
            n_loc = self.wm.get_location_safe(ax, ay) # Need safe accessor
            if not n_loc: continue
            
            migrators = []
            for m in n_loc.monsters:
                if m.behavior == BehaviorState.DEAD: continue
                # AI Logic
                desired_loc_id = HunterAI.attempt_move(m, n_loc, self.wm, self.scent_manager)
                
                if desired_loc_id == loc.location_id:
                    migrators.append(m)
            
            # Move them
            for m in migrators:
                n_loc.monsters.remove(m)
                loc.monsters.append(m)
                print(f"!!! A {m.name} followed your scent and entered from the shadows!")
                m.behavior = BehaviorState.AGGRO

    def cmd_open(self, noun, loc):
        # Handle "search area" or just "search"
        if not noun or noun in ["area", "room", "surroundings"]:
            print("You search the area...")
            found = False
            if loc.items:
                print("On the ground:", ", ".join([i.name for i in loc.items]))
                found = True
            
            # Include Corpses in general search
            for c in loc.containers:
                if "Dead" in c.name and c.inventory:
                     print(f"Corpse ({c.name}) contains loot.")
                     found = True
            
            if not found: print("Nothing of interest.")
            return True

        # Fuzzy Search for container 
        target = self.find_object_fuzzy(noun, loc.containers + loc.structures)
        if not target:
            print(f"You don't see '{noun}' here.")
            return False

        if target.locked:
            # (Lock logic same as before, omitted for brevity but assumed present)
            print("It's locked.")
            return False

        if not target.inventory:
            print(f"The {target.name} is empty.")
        else:
            print(f"--- {target.name} ---")
            for item in target.inventory:
                print(f" - {item.name}")
        return True

    def cmd_recruit(self, noun, loc):
        if not loc.survivors:
            print("There is no one here to recruit.")
            return False
        
        survivor = self.find_object_fuzzy(noun, loc.survivors)
        if not survivor:
            # Default to first if not specific
            survivor = loc.survivors[0]
        
        print(f"You approach {survivor.name}.")
        print(f'"{random.choice(survivor.dialogue)}"')
        print("You give them coordinates to the Safehouse (0,0).")
        
        loc.survivors.remove(survivor)
        self.wm.player.rescued_survivors += 1
        print("They run off towards safety. (+1 Survivor Rescued)")
        return True

    # --- BASIC CRAFTING/BUILDING STUBS (As placeholders) ---
    def cmd_take(self, noun, loc):
        if not noun: print("Take what?"); return False
        item = self.find_object_fuzzy(noun, loc.items)
        if item:
            loc.items.remove(item)
            self.wm.player.inventory.append(item)
            print(f"You picked up the {item.name}.")
            return True
        # Check containers (including corpses)
        for cont in loc.containers + loc.structures:
            if cont.locked: continue
            item = self.find_object_fuzzy(noun, cont.inventory)
            if item:
                cont.inventory.remove(item)
                self.wm.player.inventory.append(item)
                print(f"You took the {item.name} from the {cont.name}.")
                return True
        print(f"You don't see '{noun}' here."); return False

    def cmd_drop(self, noun, loc):
        item = self.find_object_fuzzy(noun, self.wm.player.inventory)
        if item:
            self.wm.player.inventory.remove(item)
            loc.items.append(item)
            print("Dropped."); return True
        return False
        
    def cmd_use(self, noun):
        # Basic use logic
        item = self.find_object_fuzzy(noun, self.wm.player.inventory)
        if item:
            if item.props.get("heal"): 
                self.wm.player.heal(item.props["heal"])
                self.wm.player.inventory.remove(item)
                return True
        print("You can't use that."); return False

    def cmd_build(self, noun, loc): print("Construction requires a workbench."); return False
    def cmd_craft(self, noun): print("Crafting requires a safe area."); return False