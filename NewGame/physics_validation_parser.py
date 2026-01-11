# --- START OF FILE physics_validation_parser.py ---

import random 
from entities import BodyPartStatus, ItemType, Monster # Added Monster import

class PhysicsValidationParser:
    def __init__(self):
        # --- GAME CONSTANTS ---
        self.GRAVITY_ACCELERATION_MPS2 = 9.81  
        self.DAMAGE_PER_JOULE_FALL = 0.05      
        self.BASE_PUSH_THRESHOLD_KG = 20       
        self.PUSH_STRENGTH_MULTIPLIER = 10     
        self.ZOMBIE_FRAGILITY_FACTOR = 1.5     
        self.LETHALITY_THRESHOLD_PERCENT = 0.999 

    def get_effective_mass_kg(self, entity):
        """Helper to get an entity's mass."""
        if hasattr(entity, 'mass_kg'):
            return entity.mass_kg
        elif hasattr(entity, 'weight'): 
             return entity.weight * 0.5
        
        if entity.__class__.__name__ == "Player":
            return 70 
        return 100 

    def calculate_kinetic_energy(self, mass_kg, fall_height_meters):
        return mass_kg * self.GRAVITY_ACCELERATION_MPS2 * fall_height_meters

    def can_be_pushed(self, pusher_entity, target_entity, applied_force_magnitude=None):
        target_mass_kg = self.get_effective_mass_kg(target_entity)

        if pusher_entity.__class__.__name__ == "Player":
            player_strength = 10 # Default baseline for player since stats aren't fully implemented
            effective_push_force_kg = self.BASE_PUSH_THRESHOLD_KG + (player_strength * self.PUSH_STRENGTH_MULTIPLIER)
        else:
            effective_push_force_kg = applied_force_magnitude if applied_force_magnitude is not None else 0

        if effective_push_force_kg >= target_mass_kg:
            return True, f"You successfully pushed the {target_entity.name}!"
        else:
            return False, f"The {target_entity.name} (approx. {int(target_mass_kg)}kg) is too heavy to move!"

    def calculate_fall_damage(self, entity, fall_height_meters, surface_type="hard"):
        if fall_height_meters <= 0:
            return {}, [] # Fixed return type to match expected unpacking

        mass_kg = self.get_effective_mass_kg(entity)
        kinetic_energy_joules = self.calculate_kinetic_energy(mass_kg, fall_height_meters)
        base_damage = int(kinetic_energy_joules * self.DAMAGE_PER_JOULE_FALL)

        # Apply fragility for zombies using safe class check
        if isinstance(entity, Monster) and "zombie" in entity.tags:
            base_damage = int(base_damage * self.ZOMBIE_FRAGILITY_FACTOR)

        damage_distribution = {}
        
        # More damage to legs/arms from falls
        total_parts_damage = 0
        for _ in range(random.randint(2, 4)): 
            part_key = random.choice(["l_leg", "r_leg", "l_arm", "r_arm", "torso"])
            part_damage = random.randint(max(1, base_damage // 5), max(2, base_damage // 2)) 
            damage_distribution[part_key] = damage_distribution.get(part_key, 0) + part_damage
            total_parts_damage += part_damage
            
        if base_damage > total_parts_damage:
             damage_distribution["torso"] = damage_distribution.get("torso", 0) + (base_damage - total_parts_damage)
             
        narrative = []
        # Narrative generation logic
        if hasattr(entity, 'body_parts'):
            for part_key, dmg in damage_distribution.items():
                if part_key in entity.body_parts:
                    p_health = entity.body_parts[part_key].max_health
                    if dmg > (p_health * 0.7):
                        narrative.append(f"Its {part_key} looks severely mangled!")
                    elif dmg > (p_health * 0.4):
                        narrative.append(f"Its {part_key} seems badly injured!")

        return damage_distribution, narrative

    def validate_attack(self, attacker_item, target_entity, target_body_part_key):
        """
        Validates an attack based on weapon properties, target entity, and body part.
        """
        base_damage = attacker_item.props.get("damage", 1) 
        special_effect = None
        message = ""

        # Check for specific lethal conditions (e.g., head stab for zombie)
        # FIX: Changed check from ItemType.MONSTER (which doesn't exist) to isinstance
        if isinstance(target_entity, Monster):
            if "zombie" in target_entity.tags and target_body_part_key == "head":
                if attacker_item.type == ItemType.WEAPON and ("pierce" in attacker_item.tags or "slash" in attacker_item.tags):
                    # 99.9% Lethality Rule
                    if random.random() < self.LETHALITY_THRESHOLD_PERCENT:
                        special_effect = "INSTANT_KILL"
                        message = f"You perfectly {random.choice(['pierce', 'stab', 'drive'])} the {target_entity.name}'s skull with your {attacker_item.name}! It collapses instantly!"
                        return base_damage * 100, special_effect, message 
                    else:
                        message = f"Your {attacker_item.name} pierces the {target_entity.name}'s head, but it surprisingly shrugs it off slightly...!"
                        base_damage = int(base_damage * 5) 

        # General limb targeting modifications
        if target_body_part_key == "head":
            base_damage = int(base_damage * 2.0)
            message = message or "You strike the head!"
        elif target_body_part_key and "leg" in target_body_part_key: 
            base_damage = int(base_damage * 0.8)
            special_effect = special_effect or "SLOW"
            message = message or "You aim for the legs!"
        elif target_body_part_key and "arm" in target_body_part_key: 
            base_damage = int(base_damage * 0.9)
            special_effect = special_effect or "DISARM"
            message = message or "You hit an arm!"
        else:
            message = message or "You land a solid blow!"

        return base_damage, special_effect, message