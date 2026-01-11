# --- START OF FILE game_engine.py ---

import sys
import time
import random
from world_manager import WorldManager
from narrator import Narrator
from entities import Item, Structure, BehaviorState, ItemType, Container, Campfire, Monster
from parser import CommandParser
from scent_tracking_system import ScentTrailManager, HunterAI
from combat_pattern_recognition import CombatTacticsEngine
from physics_validation_parser import PhysicsValidationParser
from new_game_systems import FractalEngine 

class GameEngine:
    def __init__(self):
        self.wm = WorldManager() 
        self.parser = CommandParser()
        # FIX: Pass the base_save_dir from WorldManager to other managers
        self.scent_manager = ScentTrailManager(save_dir=self.wm.base_save_dir) 
        self.tactics_engine = CombatTacticsEngine(save_dir=self.wm.base_save_dir)
        self.physics_parser = PhysicsValidationParser()
        self.fractal_engine = FractalEngine() 
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
        # FIX: Print the save directory so you can find the files
        print(f"   [Save Directory: {self.wm.base_save_dir}]")
        print("   Commands: look, go [dir], take [item], i")
        print("             attack [enemy] [head/legs/arms/torso]")
        print("             equip [item], unequip [slot/item]")
        print("             eat [food], drink [liquid], use [item]")
        print("             craft [item], build [struct], recipes")
        print("             recruit [survivor], search [corpse/container]")
        print("             push [monster], save, quit")
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
        p.hunger += 0.15 
        p.thirst += 0.25 
        
        # --- 2. FIRE & LIGHT DECAY ---
        torch = p.equipment.get("off_hand")
        is_lit_torch = torch and torch.props.get("fire")
        
        if is_lit_torch:
            # FIX: Safer integer subtraction
            current_life = torch.props.get("lifespan", 0)
            torch.props["lifespan"] = current_life - 1
            
            if torch.props["lifespan"] <= 0:
                print("\n[!] Your torch has flickered out.")
                p.equipment["off_hand"] = None
                p.fear = min(100, p.fear + 20) 
                is_lit_torch = False

        active_campfire = next((s for s in loc.structures if isinstance(s, Campfire) and s.is_lit), None)
        if active_campfire:
            active_campfire.burn() 

        # --- 3. MENTAL STATE UPDATE ---
        if active_campfire and active_campfire.is_lit:
            p.update_mental_state('campfire', loc.name) 
        elif is_lit_torch:
            p.update_mental_state('torch', loc.name)
        else:
            p.update_mental_state(None, loc.name)
            
        # Integrate FractalEngine reality shifts
        self.check_reality_shift() 
        p.clamp_stats()
    
    def check_reality_shift(self):
        shifted, description = self.fractal_engine.check_shift(self.wm.player.psychosis)
        if shifted:
            print(f"\n[REALITY SHIFT!] {description}")
            # Apply sanity penalty from the new reality
            self.wm.player.sanity = max(0, self.wm.player.sanity - self.fractal_engine.get_sanity_penalty())
            self.wm.player.clamp_stats()

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
                parsed = self.parser.parse(cmd_raw)
                if parsed:
                    self.process_command(parsed["verb"], parsed["noun"])

    def tick_breach(self):
        loc = self.wm.get_location(0, 0) 
        security = loc.get_security_rating()
        
        print(f"\n--- BREACH WAVE {self.current_wave}/{self.breach_waves} ---")
        print(f"Base Integrity: {security}%")

        for res in loc.residents:
            if res.role == "Guard" and res.sanity > 20:
                damage = random.randint(10, 20)
                print(f"{res.name} fires from the barricades, dealing {damage} damage to the horde!")
        
        if security < 100:
            breach_chance = (100 - security) / 100
            if random.random() < breach_chance:
                print("A barricade splinters! The monsters are pushing through!")
                if loc.structures:
                    target_struct = random.choice(loc.structures)
                    loc.structures.remove(target_struct)
       
        for res in loc.residents:
            if res.sanity < 15:
                print(f"\n[!!!] {res.name} has snapped!")
                print(f"{res.name} screams: 'THEY AREN'T MONSTERS, THEY'RE SAVIORS!'")
                print(f"{res.name} begins tearing down a barricade from the inside!")
                loc.stability = max(0, loc.stability - 30) 

    def end_breach(self, success):
        if success:
            print("\n" + "="*60)
            print("THE GREY RECEDES. THE SUN BREAKS THROUGH THE CLOUDS.")
            print("The horde dissolves into ash. You have held the line.")
            print("="*60)
            self.wm.player.psychosis = 0 
            self.wm.player.fear = 0
            self.wm.player.paranoia = 0
            self.wm.player.sanity = 100
        else:
            print("The safehouse has fallen. Reality dissolves into the void.")
            self.running = False 

    def process_command(self, verb, noun):
        player = self.wm.player
        loc = self.get_loc()

        if player.is_dying:
            allowed = ["use", "go", "inventory", "i", "quit"]
            if verb not in allowed:
                print("You are bleeding out! You can't do that right now!")
                return False
            
        if player.fear > 85 and random.random() < 0.2:
            print("Your heart hammers against your ribs. You're too paralyzed with fear to move!")
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
        elif verb == "eat": return self.cmd_use(noun)
        elif verb == "drink": return self.cmd_use(noun)
        elif verb == "attack": return self.cmd_attack(noun, loc)
        elif verb == "build": return self.cmd_build(noun, loc)
        elif verb == "craft": return self.cmd_craft(noun)
        elif verb == "recruit": return self.cmd_recruit(noun, loc)
        elif verb == "push": return self.cmd_push(noun, loc)
        elif verb == "equip": return self.cmd_equip(noun) 
        elif verb == "unequip": return self.cmd_unequip(noun)
        elif verb == "trade": return self.cmd_trade(noun, loc)
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
        player = self.wm.player  
        
        # 1. Describe the physical scene
        print(Narrator.describe_scene(loc, player))
        
        # 2. Handle Paranoia Hallucinations (Visual)
        if player.paranoia > 50 and random.random() < 0.3:
            hallucinations = [
                "a tall, thin figure", 
                "something with far too many limbs", 
                "a pale, weeping face",
                "the reflection of someone standing right behind you",
                "the shadows on the wall briefly detach and move independently"
            ]
            print(f"\n[!] Out of the corner of your eye, you see {random.choice(hallucinations)} vanish into the shadows.")

        # 3. Handle Persistent Reality Shifts
        if self.fractal_engine.current_reality != "NORMAL":
            reality_data = self.fractal_engine.REALITIES[self.fractal_engine.current_reality]
            print(f"\n[!] REALITY SHIFT: {reality_data['desc']}")
            
            if reality_data['drain'] > 0:
                player.psychosis += 0.5
                player.clamp_stats()            

    def cmd_attack(self, noun, loc): 
        p = self.wm.player
    
        if p.psychosis > 75 and random.random() < 0.15:
            print("Your hand spasms and turns the weapon toward you!")
            p.take_damage(10)
            return True 

        parts = noun.split()
        target_limb_key = None
        target_name = noun 
        
        # FIX: Better limb parsing for multi-word monsters
        potential_limbs = ["head", "legs", "leg", "arms", "arm", "torso", "l_leg", "r_leg", "l_arm", "r_arm"]
        if len(parts) > 1 and parts[-1] in potential_limbs:
            raw_limb = parts[-1]
            target_name = " ".join(parts[:-1]) 
            
            # Normalize and randomize limbs
            if raw_limb in ["leg", "legs"]: 
                target_limb_key = random.choice(["l_leg", "r_leg"])
            elif raw_limb in ["arm", "arms"]: 
                target_limb_key = random.choice(["l_arm", "r_arm"])
            else: 
                target_limb_key = raw_limb

        monster = self.find_object_fuzzy(target_name, loc.monsters)
        
        if not monster:
            print(f"You don't see '{target_name}' here.")
            return False

        if monster.behavior == BehaviorState.DEAD:
            print(f"The {monster.name} is already dead.")
            return False

        if p.fear > 80:
            print("Too terrified to aim! You swing wildly at the torso.")
            target_limb_key = "torso"
            
        weapon = p.equipment.get("main_hand")
        if not weapon:
             weapon = Item("fists") 
        
        calculated_damage, special_effect, physics_message = \
            self.physics_parser.validate_attack(weapon, monster, target_limb_key)

        # Normalize tactics key
        tactics_limb_name = target_limb_key if target_limb_key else "torso"
        if "leg" in tactics_limb_name: tactics_limb_name = "legs"
        if "arm" in tactics_limb_name: tactics_limb_name = "arms"

        penalty = self.tactics_engine.get_adaptation_penalty(tactics_limb_name)
        
        if penalty < 1.0 and not (special_effect == "INSTANT_KILL"): 
            print(f"The {monster.name} anticipates your attack on its {target_limb_key or 'body'}!")
            
        final_damage = int(calculated_damage * penalty)
        
        self.tactics_engine.record_attack(tactics_limb_name)

        if special_effect == "INSTANT_KILL":
            is_dead = monster.take_damage(monster.hp + 9999) 
            print(physics_message) 
        else:
            hit_chance = 0.9 
            if target_limb_key == "head": hit_chance = 0.4 
            elif target_limb_key in ["l_leg", "r_leg", "l_arm", "r_arm"]: hit_chance = 0.6 

            if random.random() > hit_chance:
                print(f"You swing at the {monster.name}'s {target_limb_key or 'body'}, but miss!")
                return True 

            is_dead = monster.take_damage(final_damage)
            print(physics_message or Narrator.combat_log("You", monster.name, final_damage, weapon.name, is_dead))
            
        if is_dead:
            print(f"The {monster.name} falls. You can search the corpse.")
            loc.monsters.remove(monster)
            
            # FIX: Corpse Looting - Provide description for Container
            corpse = Container(f"Dead {monster.name}", "A fallen enemy, ready for scavenging.") 
            corpse.inventory = monster.generate_loot()
            loc.containers.append(corpse)

        return True 

    def cmd_push(self, noun, loc):
        p = self.wm.player
        target_entity = self.find_object_fuzzy(noun, loc.monsters) 
        
        if not target_entity:
            print(f"You don't see '{noun}' to push.")
            return False

        if not isinstance(target_entity, Monster): 
             print(f"You can't push the {target_entity.name}.")
             return False

        can_push, message = self.physics_parser.can_be_pushed(p, target_entity)
        print(message)
        
        if can_push:
            # Logic for pushing (e.g. delaying attack)
            pass 
            
        return True 

    def monster_turns(self):
        loc = self.get_loc()
        
        # 1. Check for Spike Traps in the current room
        has_spike_trap = any(s.recipe_key == "spike_trap" for s in loc.structures)
        
        # 2. Check for Tripwires in adjacent rooms to provide early warnings
        adj_coords_list = [
            ("east", loc.x+1, loc.y), ("west", loc.x-1, loc.y),
            ("north", loc.x, loc.y+1), ("south", loc.x, loc.y-1)
        ]
        
        for direction, ax, ay in adj_coords_list:
            n_loc = self.wm.get_location_safe(ax, ay)
            if n_loc:
                if any(s.recipe_key == "tripwire" for s in n_loc.structures):
                    if any(m.behavior != BehaviorState.DEAD for m in n_loc.monsters):
                        print(f"[!] You hear the clatter of cans to the {direction}!")

        # MONSTER ATTACK LOGIC
        for m in loc.monsters:
            if m.behavior == BehaviorState.DEAD: continue
            
            if has_spike_trap:
                print(f"The {m.name} steps on a spike trap!")
                m.take_damage(15)
                if m.behavior == BehaviorState.DEAD:
                    print(f"The {m.name} was impaled and died!")
                    continue

            if m.behavior == BehaviorState.AGGRO or random.random() < 0.5:
                print(f"The {m.name} attacks you!")
                self.wm.player.take_damage(m.dmg)
                m.behavior = BehaviorState.AGGRO
            else:
                print(f"The {m.name} growls at you.")

        # MONSTER MIGRATION LOGIC
        for direction, ax, ay in adj_coords_list:
            n_loc = self.wm.get_location_safe(ax, ay) 
            if not n_loc: continue
            
            migrators = []
            for m in n_loc.monsters:
                if m.behavior == BehaviorState.DEAD: continue
                desired_loc_id = HunterAI.attempt_move(m, n_loc, self.wm, self.scent_manager)
                
                if desired_loc_id == loc.location_id:
                    migrators.append(m)
            
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
                print(f"The Architect warps the space to the {direction}. The way is blocked!")
                del loc.exits[direction]            
         
    def check_for_breach(self, loc):
        security = loc.get_security_rating()
        if security < 100 and random.random() > (security / 100):
             pass

    def start_final_breach(self):
        self.breach_active = True
        self.breach_waves = 5 
        self.current_wave = 1
        
        print("\n" + "!"*60)
        print("THE HIVE HAS FOUND YOU.")
        print("The air grows thick with the smell of rot and ozone.")
        print("Your residents take their positions. The siege begins.")
        print("!"*60)             

    def cmd_open(self, noun, loc):
        if not noun or noun in ["area", "room", "surroundings"]:
            print("You search the area...")
            found = False
            if loc.items:
                print("On the ground:", ", ".join([i.name for i in loc.items]))
                found = True
            
            for c in loc.containers:
                if "Dead" in c.name and c.inventory:
                     print(f"Corpse ({c.name}) contains loot.")
                     found = True
            
            if not found: print("Nothing of interest.")
            return True

        target = self.find_object_fuzzy(noun, loc.containers + loc.structures)
        if not target:
            print(f"You don't see '{noun}' here.")
            return False

        if hasattr(target, 'locked') and target.locked:
            print("It's locked.")
            return False

        if not target.inventory:
            print(f"The {target.name} is empty.")
        else:
            print(f"--- {target.name} Contents ---")
            for item in target.inventory:
                print(f" - {item.name}")
        return True

    def cmd_recruit(self, noun, loc):
        if not loc.survivors:
            print("There is no one here to recruit.")
            return False
        
        survivor = self.find_object_fuzzy(noun, loc.survivors)
        if not survivor:
            survivor = loc.survivors[0]
        
        print(f"You approach {survivor.name}.")
        print(f'"{random.choice(survivor.dialogue)}"')
        print("You give them coordinates to the Safehouse (0,0).")
        
        loc.survivors.remove(survivor)
        self.wm.player.rescued_survivors += 1
        print("They run off towards safety. (+1 Survivor Rescued)")
        return True
        
    def cmd_assign(self, noun):
        pass    

    def cmd_take(self, noun, loc):
        if not noun: print("Take what?"); return False
        
        # 1. Check items on the ground
        item = self.find_object_fuzzy(noun, loc.items)
        if item:
            loc.items.remove(item)
            self.wm.player.inventory.append(item)
            print(f"You picked up the {item.name}.")
            return True
            
        # 2. Check containers and structures
        # FIX: Ensure we check inside all unlocked containers
        for cont in loc.containers + loc.structures:
            if hasattr(cont, 'locked') and cont.locked: continue
            
            if hasattr(cont, 'inventory') and cont.inventory is not None:
                item = self.find_object_fuzzy(noun, cont.inventory)
                if item:
                    cont.inventory.remove(item)
                    self.wm.player.inventory.append(item)
                    print(f"You took the {item.name} from the {cont.name}.")
                    return True
                    
        print(f"You don't see '{noun}' here.")
        return False

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
            print("You can't use that.") 
            return False
        
        used = False

        # Handle Food and Drink types first
        if item.type == ItemType.FOOD or item.type == ItemType.DRINK:
            if p.consume(item): 
                used = True
        
        # Handle other consumable effects (heal, sanity)
        if item.props.get("heal"):
            p.heal(item.props["heal"])
            used = True
        
        if item.props.get("sanity"):
            bonus = item.props["sanity"]
            p.sanity = min(100, p.sanity + bonus) 
            p.psychosis = max(0, p.psychosis - (bonus / 2)) 
            print(f"You focus on the {item.name}. The world feels a little more solid.")
            if "comfort" in item.tags:
                print("Memory: You remember the smell of rain before the grey took over.")
            used = True
            
        if item.name == "Echo of Self": 
            p.psychosis = 0
            p.fear = 0
            p.paranoia = 0
            p.sanity = 100 
            print("You remember who you are. The fractured world loses its grip on you.")
            used = True
            
        if used:
            # FIX: Only remove if still in inventory (consumable)
            if item in p.inventory:
                p.inventory.remove(item)
            return True
        else:
            print("You can't use that.") 
            return False

    def cmd_build(self, noun, loc):
        from data.recipes import BUILDING_RECIPES 
        p = self.wm.player
        
        recipe = BUILDING_RECIPES.get(noun)
        if not recipe:
            print(f"You don't know how to build a '{noun}'.")
            return False

        missing = []
        for mat_key, qty in recipe["materials"].items():
            material_found_count = len([i for i in p.inventory if i.key == mat_key]) 
            if material_found_count < qty:
                missing.append(f"{qty}x {mat_key.replace('_', ' ')}")

        if missing:
            print(f"Missing materials: {', '.join(missing)}")
            return False

        for mat_key, qty in recipe["materials"].items():
            for _ in range(qty):
                item_to_remove = next((i for i in p.inventory if i.key == mat_key), None)
                if item_to_remove:
                    p.inventory.remove(item_to_remove)

        new_struct = Campfire() if noun == "campfire" else Structure(noun)
        loc.structures.append(new_struct)
        print(f"You successfully constructed a {recipe['name']}!")
        return True
    
    def cmd_craft(self, noun):
        p = self.wm.player
        from data.recipes import CRAFTING_RECIPES 

        recipe = CRAFTING_RECIPES.get(noun)
        if not recipe:
            if p.is_delirious:
                print("The whispers don't know that recipe... yet.")
            else:
                print(f"You don't know how to craft a {noun}.")
            return False

        missing = []
        materials_to_consume = []
        for mat_key, qty in recipe["materials"].items():
            if "choose_material" in recipe and mat_key in recipe["choose_material"]:
                found_one = False
                for choice_key in recipe["choose_material"]:
                    if len([i for i in p.inventory if i.key == choice_key]) >= qty:
                        materials_to_consume.append((choice_key, qty))
                        found_one = True
                        break
                if not found_one:
                    missing.append(f"{qty}x (any of {', '.join(recipe['choose_material']).replace('_', ' ')})")
            else:
                current_count = len([i for i in p.inventory if i.key == mat_key])
                if current_count < qty:
                    missing.append(f"{qty}x {mat_key.replace('_', ' ')}")
                else:
                    materials_to_consume.append((mat_key, qty))

        if missing:
            print(f"Missing materials: {', '.join(missing)}")
            return False

        for mat_key, qty in materials_to_consume:
            for _ in range(qty):
                item_to_remove = next((i for i in p.inventory if i.key == mat_key), None)
                if item_to_remove:
                    p.inventory.remove(item_to_remove)

        if "bladed_item_tag" in recipe:
            has_bladed_tool = False
            for equipped_item in p.equipment.values():
                if equipped_item and any(tag in recipe["bladed_item_tag"] for tag in equipped_item.tags):
                    has_bladed_tool = True
                    break
            for inventory_item in p.inventory:
                 if any(tag in recipe["bladed_item_tag"] for tag in inventory_item.tags):
                     has_bladed_tool = True
                     break
            if not has_bladed_tool:
                print("You need a bladed item (knife, shiv, etc.) to craft this.")
                return False

        if "tool_required_tag" in recipe:
            has_required_tool = False
            for equipped_item in p.equipment.values():
                if equipped_item and recipe["tool_required_tag"] in equipped_item.tags:
                    has_required_tool = True
                    break
            for inventory_item in p.inventory:
                 if recipe["tool_required_tag"] in inventory_item.tags:
                     has_required_tool = True
                     break
            if not has_required_tool:
                print(f"You need a tool with the '{recipe['tool_required_tag']}' tag to craft this.")
                return False

        crafted_item_key = recipe["result"]
        crafted_item = Item(crafted_item_key)
        p.inventory.append(crafted_item)
        print(f"\n[!] You successfully crafted a {crafted_item.name}!")
        
        if p.is_delirious and "nightmare_effect" in recipe:
            effect_desc = recipe["nightmare_effect"].get("desc", "It feels... wrong.")
            p.paranoia += recipe["nightmare_effect"].get("paranoia_gain", 0)
            p.fear += recipe["nightmare_effect"].get("fear_gain", 0)
            print(effect_desc)

        return True

    def cmd_equip(self, noun):
        p = self.wm.player
        item = self.find_object_fuzzy(noun, p.inventory)
        if not item:
            print(f"You don't have a \"{noun}\" in your inventory.")
            return False
        slot = None
        if item.type == ItemType.WEAPON or item.type == ItemType.TOOL:
            if item.props.get("two_handed", False):
                slot = "main_hand" 
                if p.equipment["off_hand"]:
                    self.cmd_unequip("off_hand")
            else:
                if not p.equipment["main_hand"]:
                    slot = "main_hand"
                elif not p.equipment["off_hand"]:
                    slot = "off_hand"
                else: 
                    slot = "main_hand"

        elif item.type == ItemType.CLOTHING:
            slot = item.props.get("slot") 
            if not slot:
                if "torso" in item.tags: slot = "torso"
                elif "legs" in item.tags: slot = "legs"
                elif "feet" in item.tags: slot = "feet"
                elif "head" in item.tags: slot = "head"
                elif "hands" in item.tags: slot = "hands"
                elif "eyes" in item.tags: slot = "eyes"
                else: print(f"Can't determine equip slot for {item.name}."); return False
            
        if slot:
            if p.equipment.get(slot): 
                self.cmd_unequip(slot)
            p.equipment[slot] = item
            p.inventory.remove(item)
            print(f"You equipped the {item.name} to your {slot.replace('_', ' ')}.")
            return True
        print(f"You cannot equip the {item.name}.")
        return False

    def cmd_unequip(self, slot_name):
        p = self.wm.player
        
        normalized_slot_name = slot_name.lower().replace(" ", "_")
        if normalized_slot_name == "left_leg": normalized_slot_name = "l_leg"
        elif normalized_slot_name == "right_leg": normalized_slot_name = "r_leg"
        elif normalized_slot_name == "left_arm": normalized_slot_name = "l_arm"
        elif normalized_slot_name == "right_arm": normalized_slot_name = "r_arm"

        item = p.equipment.get(normalized_slot_name) 
        
        if not item:
            for s, i in p.equipment.items():
                if i and normalized_slot_name in i.name.lower():
                    normalized_slot_name, item = s, i 
                    break

        if item:
            p.equipment[normalized_slot_name] = None
            p.inventory.append(item)
            print(f"You unequipped the {item.name}.")
            return True
        print("Nothing is equipped there or could be unequipped.")
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
    
    def cmd_trade(self, noun, loc):
        if not loc.survivors:
            print("There is no one here to trade with.")
            return False
        
        survivor = self.find_object_fuzzy(noun, loc.survivors)
        if not survivor:
            print(f"You don't see '{noun}' here.")
            return False

        print(f"\n--- TRADING WITH {survivor.name.upper()} ---")
        if not survivor.inventory:
            print(f"{survivor.name} has nothing to trade.")
            return True

        print(f"{survivor.name} is offering:")
        for i, item in enumerate(survivor.inventory):
            print(f" [{i}] {item.name}")
        
        print("\nWhat will you give in return? (Enter item name or 'cancel')")
        offer_name = input("> ").strip().lower()
        if offer_name == "cancel": return True

        my_item = self.find_object_fuzzy(offer_name, self.wm.player.inventory)
        if not my_item:
            print(f"You don't have a '{offer_name}'.")
            return False

        print(f"Which item do you want from {survivor.name}? (Enter number)")
        try:
            choice = int(input("> "))
            target_item = survivor.inventory[choice]
        except (ValueError, IndexError):
            print("Invalid choice.")
            return False

        # Simple trade logic: 1 for 1 exchange
        self.wm.player.inventory.remove(my_item)
        survivor.inventory.remove(target_item)
        
        self.wm.player.inventory.append(target_item)
        survivor.inventory.append(my_item)

        print(f"\n[!] Trade successful! You gave {my_item.name} and received {target_item.name}.")
        return True
# --- END OF FILE game_engine.py ---