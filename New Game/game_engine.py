# --- START OF FILE game_engine.py ---

import sys
import time
import random
from world_manager import WorldManager
from narrator import Narrator
from entities import Item, Structure, BehaviorState, ItemType, Container, Campfire
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
        self.breach_active = False
        self.breach_waves = 5
        self.current_wave = 0

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
    
    def tick_world(self):
        p = self.wm.player
        loc = self.get_loc()
        
        # --- 1. PHYSICAL DECAY ---
        # Hunger increases by 0.15, Thirst by 0.25 per turn
        p.hunger += 0.15
        p.thirst += 0.25
        
        # Damage player if starving/dehydrated
        if p.hunger >= 100 or p.thirst >= 100:
            p.hp -= 1
            if p.hunger >= 100: print("[!] You are starving.")
            if p.thirst >= 100: print("[!] You are dying of thirst.")

        # --- 2. FIRE & LIGHT DECAY ---
        torch = p.equipment.get("off_hand")
        is_lit_torch = torch and torch.props.get("fire")
        
        # Torch depletion
        if is_lit_torch:
            torch.props["lifespan"] -= 1
            if torch.props["lifespan"] <= 0:
                print("\n[!] Your torch has flickered out.")
                p.equipment["off_hand"] = None
                p.fear += 20 # Panic from sudden darkness
                is_lit_torch = False

        # Campfire depletion
        active_campfire = next((s for s in loc.structures if isinstance(s, Campfire) and s.is_lit), None)
        if active_campfire:
            active_campfire.burn() # Reduces 2500 fuel by 1

        # --- 3. MENTAL STATE UPDATE ---
        if active_campfire and active_campfire.is_lit:
            p.update_mental_state('campfire')
        elif is_lit_torch:
            p.update_mental_state('torch')
        else:
            p.update_mental_state(None) # Applying darkness creep

        if p.fear > 50:
            # You are sweating/breathing heavy; monsters smell it.
            self.scent_manager.add_scent(p.location_id) 
            
        self.check_reality_shift()
        p.clamp_stats()
    

    def check_reality_shift(self):
        # Placeholder for reality shift logic
        pass
    def loop(self):
        while self.running:
            if self.wm.player.hp <= 0:
                print("\n\n" + "#"*30 + "\n    Y O U   H A V E   D I E D\n" + "#"*30)
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
                self.tick_world()
                self.wm.player.update_status()
            
            if self.wm.player.psychosis >= 100:
                print("\n" + "!"*40)
                print("YOUR MIND SNAPS. YOU LOSE CONTROL.")
                print("!"*40)
                forced_actions = ["go north", "go south", "attack torso", "drop all"]
                cmd_raw = random.choice(forced_actions)
                print(f"In a blur of terror, you {cmd_raw}...")
                self.wm.player.psychosis -= 30
                self.wm.player.fear += 20
                # Process the forced command
                parsed = self.parser.parse(cmd_raw)
                if parsed:
                    self.process_command(parsed["verb"], parsed["noun"])

    def tick_breach(self):
        loc = self.wm.get_location(0, 0) # The Safehouse
        security = loc.get_security_rating()
        
        print(f"\n--- BREACH WAVE {self.current_wave}/{self.breach_waves} ---")
        print(f"Base Integrity: {security}%")

        # 1. Residents provide defensive fire
        for res in loc.residents:
            if res.role == "Guard" and res.sanity > 20:
                damage = random.randint(10, 20)
                print(f"{res.name} fires from the barricades, dealing {damage} damage to the horde!")
                # Logic to apply damage to the incoming wave
        
        # 2. Check for Structural Damage
        if security < 100:
            breach_chance = (100 - security) / 100
            if random.random() < breach_chance:
                print("A barricade splinters! The monsters are pushing through!")
                # Reduce security or damage a random structure
                target_struct = random.choice(loc.structures)
                loc.structures.remove(target_struct)
       
        for res in loc.residents:
            if res.sanity < 15:
                print(f"\n[!!!] {res.name} has snapped!")
                print(f"{res.name} screams: 'THEY AREN'T MONSTERS, THEY'RE SAVIORS!'")
                print(f"{res.name} begins tearing down a barricade from the inside!")
                # Immediate drop in security rating
                loc.security_rating -= 30       

    def end_breach(self, success):
        if success:
            print("\n" + "="*60)
            print("THE GREY RECENTES. THE SUN BREAKS THROUGH THE CLOUDS.")
            print("The horde dissolves into ash. You have held the line.")
            print("="*60)
            self.wm.player.ground_reality() # Resets Psychosis to 0
        else:
            print("The safehouse has fallen. Reality dissolves into the void.")
            self.running = False # Game Over

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
        elif verb == "status": self.cmd_status(); return False
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

    def cmd_status(self):
        p = self.wm.player
        loc = self.get_loc()
        print("\n" + "═"*45)
        print(" STATUS REPORT")
        print("═"*45)
        print(f" HP        : {p.hp}/100")
        print(f" HUNGER    : {p.hunger:.1f}% {'(STARVING!)' if p.hunger > 80 else ''}")
        print(f" THIRST    : {p.thirst:.1f}% {'(DEHYDRATED!)' if p.thirst > 80 else ''}")
        print("-" * 45)
        print(f" SANITY    : {p.sanity}%")
        print(f" PSYCHOSIS : {p.psychosis}% {'[REALITY FAILING]' if p.psychosis > 70 else ''}")
        print(f" FEAR      : {p.fear}% | PARANOIA  : {p.paranoia}%")
        active_campfire = next((s for s in loc.structures if isinstance(s, Campfire) and s.is_lit), None)
        torch = p.equipment.get("off_hand")
        is_using_torch = torch and torch.props.get("fire")
        print("-" * 45)
        if active_campfire:
            rate = 3 + (p.fire_timer // 5)
            print(f" STATUS    : [GROUNDED] Sanctuary (Rate: -{rate}/turn)")
            print(f" FIRE FUEL : {active_campfire.remaining_fuel}/2500 turns")
        elif is_using_torch:
            print(f" STATUS    : [SHIELDED] Mobile Light (Rate: -1/turn)")
            print(f" TORCH LIFE: {torch.props.get('lifespan', 0)} turns")
        else:
            print(f" STATUS    : [UNSTABLE] Darkness (Paranoia/Fear creeping up)")
        print("-" * 45)
        print(" EQUIPMENT:")
        for slot, item in p.equipment.items():
            slot_name = slot.replace("_", " " ).title()
            if item:
                print(f"  {slot_name:10}: {item.get_display_name()}")
            else:
                print(f"  {slot_name:10}: Empty")
        print("═" * 45 + "\n")

    def look(self):
        loc = self.get_loc()
        print(Narrator.describe_scene(loc, self.wm.player))

        # --- UPDATED ATTACK LOGIC WITH LIMBS ---
    def cmd_attack(self, target_name, limb_name, loc):
        p = self.wm.player
    
        # HAND PSYCHOSIS (15% chance to strike self)
        if p.psychosis > 75 and random.random() < 0.15:
            print("Your hand spasms and turns the weapon toward you!")
            p.take_damage(10)
            return

        # PANIC OVERRIDE
        if p.fear > 80:
            print("Too terrified to aim! You swing wildly at the torso.")
        limb_name = "torso"
        
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
        penalty = self.tactics_engine.get_adaptation_penalty(limb_name)
        if penalty < 1.0:
            print(f"The {monster.name} anticipates your attack on its {target_limb or 'body'}!")
        damage = int(damage * penalty)

        # Limb targeting modifiers
        hit_desc = "body"
        if target_limb:
            hit_desc = target_limb
            self.tactics_engine.record_attack(limb_name)
            if limb_name and "head" in limb_name:
                hit_chance = 0.4
                damage *= 2.0 # Critical hit
            elif limb_name and "leg" in limb_name:
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
                
    def boss_special_ability(self, boss, loc):
        if boss.name == "The Architect of Glass":
            if loc.structures:
                struct = random.choice(loc.structures)
                loc.structures.remove(struct)
                print(f"The Architect gestures, and your {struct.name} shatters into dust!")
            elif loc.exits:
                direction = random.choice(list(loc.exits.keys()))
                # Temporarily block an exit
                print(f"The Architect warps the space to the {direction}. The way is blocked!")
                del loc.exits[direction]            
         
    def check_for_breach(self, loc):
        security = loc.get_security_rating()
        # If security is < 100%, there's a chance a 'Scent-Tracked' monster 
        # breaks through the door/window.
        if security < 100 and random.random() > (security / 100):
             # Logic to pull a monster from an adjacent room into the current one
             pass

    def start_final_breach(self):
        self.breach_active = True
        self.breach_waves = 5 # Number of waves to survive
        self.current_wave = 1
        
        print("\n" + "!"*60)
        print("THE HIVE HAS FOUND YOU.")
        print("The air grows thick with the smell of rot and ozone.")
        print("Your residents take their positions. The siege begins.")
        print("!"*60)             

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
        
    def cmd_assign(self, noun):
        """Usage: assign [name] to [guard/medic/scavenger]"""
        # Logic to find the resident in your safehouse and change their role.
        # A Guard increases base security by 20% per person.
        # A Medic increases HP recovery when you rest.
        # A Scavenger brings back random 'Junk' items every 50 turns.
        pass    

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
        p = self.wm.player
        item = self.find_object_fuzzy(noun, p.inventory)
        if not item:
            print("You can is t use that.")
            return False
        
        used = False
        if item.props.get("heal"):
            p.heal(item.props["heal"])
            used = True
        
        if item.props.get("sanity"):
            bonus = item.props["sanity"]
            p.sanity += bonus
            p.psychosis -= bonus / 2
            print(f"You focus on the {item.name}. The world feels a little more solid.")
            if "comfort" in item.tags:
                print("Memory: You remember the smell of rain before the grey took over.")
            used = True
            
        if item.name == "Echo of Self":
            p.max_psychosis += 50
            p.psychosis = 0
            print("You remember who you are. The fractured world loses its grip on you.")
            used = True
            
        if used:
            p.inventory.remove(item)
            return True
        else:
            print("You can is t use that.")
            return False

    def cmd_build(self, noun, loc):
        from recipes import BUILDING_RECIPES
        p = self.wm.player
        
        recipe = BUILDING_RECIPES.get(noun)
        if not recipe:
            print(f"You don't know how to build a '{noun}'.")
            return False

        # Check for materials
        missing = []
        for mat_key, qty in recipe["materials"].items():
            count = sum(1 for i in p.inventory if i.name.lower() == mat_key.replace("_", " "))
            if count < qty:
                missing.append(f"{qty}x {mat_key}")

        if missing:
            print(f"Missing materials: {', '.join(missing)}")
            return False

        # Consume materials and build
        for mat_key, qty in recipe["materials"].items():
            for _ in range(qty):
                item = self.find_object_fuzzy(mat_key, p.inventory)
                p.inventory.remove(item)

        new_struct = Structure(recipe["name"]) # This makes it "Window Barricade"
        loc.structures.append(new_struct)
        print(f"You successfully constructed a {recipe['name']}!")
        return True
    
    def cmd_craft(self, noun):
        p = self.wm.player
        standard_recipes = {
            "bandage": {"material": "rags", "result": "Bandage", "heal": 20},
            "spear": {"material": "wood_plank", "result": "Sharpened Spear", "dmg": 15}
        }
        nightmare_recipes = {
            "bandage": {"material": "rags", "result": "Blood-Soaked Binding", "effect": "Bleed Stop, +5 Paranoia"},
            "crown": {"material": "scrap_wire", "result": "Crown of Thorns", "effect": "Fear Resistance, +10 Paranoia"}
        }
        recipes = nightmare_recipes if p.is_delirious else standard_recipes
        if noun not in recipes:
            if p.is_delirious:
                print("The whispers don not know that recipe... yet.")
            else:
                print(f"You don not know how to craft a {noun}.")
            return False
        recipe = recipes[noun]
        material = self.find_object_fuzzy(recipe["material"], p.inventory)
        if material:
            p.inventory.remove(material)
            print(f"\n[!] You fashion a {recipe['result']} out of {material.name}.")
            if p.is_delirious:
                print("It feels... right. The shadows seem to approve.")
                p.paranoia += 5
            return True
        else:
            print(f"You lack the {recipe['material']} to create this.")
            return False

    def cmd_equip(self, noun):
        p = self.wm.player
        item = self.find_object_fuzzy(noun, p.inventory)
        if not item:
            print(f"You don not have a \"{noun}\" in your inventory.")
            return False
        slot = None
        from entities import ItemType
        if item.type == ItemType.WEAPON or item.type == ItemType.TOOL:
            slot = "main_hand"
        elif item.type == ItemType.CLOTHING:
            slot = item.props.get("slot", "torso")
        if slot:
            if p.equipment[slot]:
                self.cmd_unequip(slot)
            p.equipment[slot] = item
            p.inventory.remove(item)
            print(f"You equipped the {item.name} to your {slot.replace('_', ' ' )}.")
            return True
        print(f"You can not equip the {item.name}.")
        return False

    def cmd_unequip(self, slot_name):
        p = self.wm.player
        item = p.equipment.get(slot_name)
        if not item:
            for s, i in p.equipment.items():
                if i and slot_name.lower() in i.name.lower():
                    slot_name, item = s, i
                    break
        if item:
            p.equipment[slot_name] = None
            p.inventory.append(item)
            print(f"You unequipped the {item.name}.")
            return True
        print("Nothing is equipped there.")
        return False

    def cmd_wield_torch(self, noun):
        p = self.wm.player
        item = self.find_object_fuzzy(noun, p.inventory)
        if item and item.props.get("fire"):
            if p.equipment["off_hand"]:
                self.cmd_unequip("off_hand")
            p.equipment["off_hand"] = item
            p.inventory.remove(item)
            print(f"You raise the {item.name}. The light keeps your fears at bay.")
            return True
        return self.cmd_equip(noun)
