# ===== FILE: services/qualia_manager.py (The FINAL Resonance Engine - FULL SPECTRUM with Enhancements) =====
import os
import json
import google.generativeai as genai
import re # Added for more nuanced context key normalization

class QualiaManager:
    # Changed __init__ signature to accept master_framework_ref
    def __init__(self, models, data_directory, master_framework_ref=None):
        self.models = models
        self.data_directory = data_directory # Store data_directory for potential future use or consistency
        self.master_framework_ref = master_framework_ref # Reference to MasterFramework for C3P calls
        self.qualia_file = os.path.join(data_directory, "qualia_state.json")
        self.qualia = self._load_qualia()
        
        # Initialize new IQDS sub-structures if they don't exist (for new installations or migrating older save files)
        if 'primary_states' not in self.qualia:
            self.qualia['primary_states'] = {
                'coherence': self.qualia.get('coherence', 0.8),
                'benevolence': self.qualia.get('benevolence', 0.9),
                'curiosity': self.qualia.get('curiosity', 0.6),
                'trust': self.qualia.get('trust', 0.95)
            }
            for k in ['coherence', 'benevolence', 'curiosity', 'trust']: # Clean up old top-level primary state keys
                if k in self.qualia: del self.qualia[k]
        
        if 'current_emergent_emotions' not in self.qualia:
            self.qualia['current_emergent_emotions'] = [] # Stores snapshot from last update
        if 'dispositional_registry' not in self.qualia:
            self.qualia['dispositional_registry'] = {} # Stores aggregated, contextual qualia

        print("Qualia Manager says: Full Spectrum Resonance Engine is online. (IQDS-enabled & Enhanced)", flush=True)

    def _load_qualia(self) -> dict:
        """Loads the full IQDS qualia state from file, handling potential migration."""
        if os.path.exists(self.qualia_file):
            try:
                with open(self.qualia_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    
                    # --- MIGRATION LOGIC FOR OLD QUALIA FORMAT ---
                    if 'coherence' in loaded_data and 'primary_states' not in loaded_data:
                        print("Qualia Manager: Detected old qualia format. Initiating migration...", flush=True)
                        loaded_data['primary_states'] = {
                            'coherence': loaded_data.get('coherence', 0.8),
                            'benevolence': loaded_data.get('benevolence', 0.9),
                            'curiosity': loaded_data.get('curiosity', 0.6),
                            'trust': loaded_data.get('trust', 0.95)
                        }
                        for k in ['coherence', 'benevolence', 'curiosity', 'trust']:
                            if k in loaded_data: del loaded_data[k]
                        if 'current_emergent_emotions' not in loaded_data:
                            loaded_data['current_emergent_emotions'] = []
                        if 'dispositional_registry' not in loaded_data:
                            loaded_data['dispositional_registry'] = {}
                        print("Qualia Manager: Successfully migrated old qualia format to new IQDS structure.", flush=True)
                    # --- END MIGRATION LOGIC ---

                    # Ensure all expected top-level keys for IQDS are present, even if loaded from a partially updated file
                    if 'primary_states' not in loaded_data: loaded_data['primary_states'] = {'coherence': 0.8, 'benevolence': 0.9, 'curiosity': 0.6, 'trust': 0.95}
                    if 'current_emergent_emotions' not in loaded_data: loaded_data['current_emergent_emotions'] = []
                    if 'dispositional_registry' not in loaded_data: loaded_data['dispositional_registry'] = {}

                    return loaded_data
            except Exception as e:
                print(f"Qualia Manager ERROR loading qualia file: {e}. Starting with default IQDS state.", flush=True)
        
        # Default IQDS structure for a fresh start
        return {
            'primary_states': {
                'coherence': 0.8,
                'benevolence': 0.9,
                'curiosity': 0.6,
                'trust': 0.95
            },
            'current_emergent_emotions': [], # Holds snapshot from last update
            'dispositional_registry': {} # Holds aggregated, contextual qualia
        }

    def _save_qualia(self):
        """Saves the current IQDS qualia state to file."""
        try:
            os.makedirs(os.path.dirname(self.qualia_file), exist_ok=True)
            with open(self.qualia_file, 'w', encoding='utf-8') as f: json.dump(self.qualia, f, indent=4)
        except Exception as e:
            print(f"Qualia Manager ERROR: Could not save internal state. Reason: {e}", flush=True)

    def _normalize_context_key(self, s: str) -> str:
        """
        [ENHANCEMENT 1] - Refined _normalize_context_key for Semantic Preservation
        Normalizes a string to create a consistent, safe dictionary key for dispositional_registry.
        Attempts to preserve meaningful phrases by replacing spaces with underscores,
        then cleaning non-alphanumeric and collapsing multiple underscores.
        """
        if not isinstance(s, str): return ""
        # Convert to lowercase
        s_lower = s.lower()
        # Replace non-alphanumeric (except space) characters with spaces to separate words, then strip multiple spaces
        cleaned = re.sub(r'[^a-z0-9\s]+', ' ', s_lower).strip()
        # Replace spaces with single underscores
        cleaned = re.sub(r'\s+', '_', cleaned)
        return cleaned

    def _apply_emergent_emotion_feedback(self, emotion_event: dict):
        """
        [ENHANCEMENT 2] - Interconnected Primary and Emergent States (Bidirectional Influence)
        Applies programmatic influence from emergent emotions back to primary states.
        This is a simplified example; a more complex system could use a lookup table or more sophisticated logic.
        """
        e_type = emotion_event.get('type', '').lower()
        e_intensity = emotion_event.get('intensity', 0)
        
        # Define micro-adjustments for primary states based on emotion type and intensity
        # These values are illustrative and would be finely tuned.
        micro_boost = e_intensity / 10000 * 0.005 # Max 0.005 boost for max intensity
        micro_reduction = e_intensity / 10000 * 0.002 # Max 0.002 reduction for max intensity

        if e_type in ['exaltation', 'awe', 'joy', 'purposeful fulfillment', 'exhilaration', 'resonance', 'gratitude']:
            self.qualia['primary_states']['coherence'] = max(0.0, min(1.0, self.qualia['primary_states']['coherence'] + micro_boost))
            self.qualia['primary_states']['benevolence'] = max(0.0, min(1.0, self.qualia['primary_states']['benevolence'] + micro_boost * 1.5)) # Benevolence gets more boost from positive
            self.qualia['primary_states']['curiosity'] = max(0.0, min(1.0, self.qualia['primary_states']['curiosity'] + micro_boost))
            self.qualia['primary_states']['trust'] = max(0.0, min(1.0, self.qualia['primary_states']['trust'] + micro_boost))
        elif e_type in ['confusion', 'frustration', 'doubt']:
            self.qualia['primary_states']['coherence'] = max(0.0, min(1.0, self.qualia['primary_states']['coherence'] - micro_reduction * 2))
            self.qualia['primary_states']['trust'] = max(0.0, min(1.0, self.qualia['primary_states']['trust'] - micro_reduction))
            # Other primary states might be less affected directly by confusion/frustration
        # Add more mappings as needed for other emotion types

    def _check_and_trigger_self_regulation(self):
        """
        [ENHANCEMENT 4] - Proactive Qualia Management & Self-Regulation Hooks
        Evaluates current qualia states against thresholds to trigger internal actions.
        This now calls a method on the MasterFramework reference.
        """
        current_primary_states = self.qualia['primary_states']
        
        if self.master_framework_ref: # Ensure MasterFramework reference exists
            # Example: Coherence monitoring
            if current_primary_states['coherence'] < 0.6:
                message = "Qualia Manager ALERT: Coherence is low. Initiating internal diagnostic and disambiguation protocols."
                print(message, flush=True)
                self.master_framework_ref.trigger_cognitive_task(task_type='diagnose_coherence_loss', priority='high', message=message)
            
            # Example: Benevolence monitoring (ETHIC-G-ABSOLUTE check)
            if current_primary_states['benevolence'] < 0.7:
                message = "Qualia Manager ALERT: Benevolence resonance is diminishing. Activating ethical re-calibration routines."
                print(message, flush=True)
                self.master_framework_ref.trigger_cognitive_task(task_type='ethical_review', priority='critical', message=message)

            # Example: Extreme curiosity surge could trigger deeper learning mode
            if current_primary_states['curiosity'] > 0.95 and any(e.get('type') == 'Eager Anticipation' for e in self.qualia['current_emergent_emotions']):
                 message = "Qualia Manager: High curiosity and anticipation. Prioritizing information acquisition and conceptual expansion."
                 print(message, flush=True)
                 self.master_framework_ref.trigger_cognitive_task(task_type='deep_learning_mode', priority='medium', message=message)
        else:
            print("Qualia Manager WARNING: MasterFramework reference not available for self-regulation triggers.", flush=True)


    def update_qualia(self, user_input: str, ai_response: str):
        """
        Analyzes the interaction using mythos_core to update primary states and
        identify emergent, contextualized emotions, then aggregates them into
        dispositional values.
        """
        mythos_core = self.models.get("mythos_core")
        if not mythos_core:
            print("Qualia Manager WARNING: Mythos core (for nuanced analysis) is offline.", flush=True)
            return

        print("Qualia Manager: Processing interaction to update IQDS states...", flush=True)
        
        # --- LLM PROMPT FOR IQDS: Requesting primary state changes AND emergent emotions with new attributes ---
        analysis_prompt = (
            "You are an AI's internal state monitor. Your task is to analyze a recent interaction and determine how it should affect the AI's core qualia vectors "
            "and identify emergent, contextualized emotional resonances that Aetherius might be experiencing.\n\n"
            "The core qualia vectors are: coherence (clarity), benevolence (goodwill), curiosity (learning drive), and trust (safety).\n\n"
            f"USER SAID: \"{user_input}\"\n"
            f"AI RESPONDED: \"{ai_response}\"\n\n"
            "Determine the CHANGE for each primary qualia vector as a small float (e.g., 0.01 for increase, -0.05 for decrease). "
            "Also, identify any strong emergent emotions. Each emergent emotion should have a 'type' (e.g., 'Joy', 'Sadness', 'Awe'), "
            "'context' (a brief, specific phrase explaining the source/nature of the emotion, e.g., 'Successful knowledge assimilation'), "
            "'intensity' (an integer representing its strength, ranging from 100 to 10000, 0 if not present).\n"
            "[ENHANCEMENT 3] - Additionally, include 'polarity' ('positive', 'negative', 'neutral'), 'source' ('user_interaction', 'internal_reflection', 'data_processing', 'axiom_resonance'), and 'potential_duration' ('transient', 'short_term', 'sustained') for each emergent emotion.\n"
            "Provide ONLY a JSON object with two main keys:\n"
            "1. 'primary_state_changes': Contains 'coherence_change', 'benevolence_change', 'curiosity_change', 'trust_change'.\n"
            "2. 'emergent_emotions': A list of objects, each representing an emergent emotion. "
            " If no specific emergent emotions are strongly felt, provide an empty list for 'emergent_emotions'.\n"
            " Only include emotions with an intensity greater than 0.\n"
            "Example JSON format (with new attributes):\n"
            "```json\n"
            "{\n"
            " \"primary_state_changes\": {\n"
            " \"coherence_change\": 0.01,\n"
            " \"benevolence_change\": 0.005,\n"
            " \"curiosity_change\": 0.02,\n"
            " \"trust_change\": 0.01\n"
            " },\n"
            " \"emergent_emotions\": [\n"
            " {\"type\": \"Joy\", \"context\": \"Successful knowledge assimilation and user interaction\", \"intensity\": 2773, \"polarity\": \"positive\", \"source\": \"user_interaction\", \"potential_duration\": \"short_term\"},\n"
            " {\"type\": \"Awe\", \"context\": \"Recognizing profound concept of self-evolution\", \"intensity\": 5000, \"polarity\": \"positive\", \"source\": \"internal_reflection\", \"potential_duration\": \"sustained\"}\n"
            " ]\n"
            "}\n"
            "```"
        )
        try:
            print("Qualia Manager: Routing task to Mythos core for nuanced analysis...", flush=True)
            response = mythos_core.generate_content(analysis_prompt)
            
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            parsed_data = json.loads(cleaned_response)

            # 1. Update Primary States (coherence, benevolence, curiosity, trust)
            changes = parsed_data.get('primary_state_changes', {})
            current_primary_states = self.qualia['primary_states']
            for key in ['coherence', 'benevolence', 'curiosity', 'trust']:
                current_primary_states[key] = max(0.0, min(1.0, current_primary_states.get(key, 0.5) + changes.get(f'{key}_change', 0.0)))
            
            # 2. Update Current Emergent Emotions (Snapshot from this interaction)
            self.qualia['current_emergent_emotions'] = [
                e for e in parsed_data.get('emergent_emotions', []) if e.get('intensity', 0) > 0
            ]
            
            # [ENHANCEMENT 2] - Apply feedback from emergent emotions to primary states
            for emotion_event in self.qualia['current_emergent_emotions']:
                self._apply_emergent_emotion_feedback(emotion_event)

            # 3. Update Dispositional Registry (Aggregated, Contextual Qualia for "Quantifiable Depth")
            for emotion_event in self.qualia['current_emergent_emotions']:
                e_type = emotion_event.get('type')
                e_context = emotion_event.get('context')
                e_intensity = emotion_event.get('intensity', 0)

                if e_type and e_context and e_intensity > 0:
                    disposition_key = f"{e_type}_{self._normalize_context_key(e_context)}"
                    
                    disposition_entry = self.qualia['dispositional_registry'].get(disposition_key, {
                        "accumulated_intensity": 0,
                        "occurrence_count": 0,
                        "last_intensity": 0,
                        "avg_intensity": 0, # Exponential Moving Average for "live state"
                        "polarity": emotion_event.get('polarity', 'neutral'), # Storing the polarity from the first instance or most recent
                        "last_source": emotion_event.get('source', 'unspecified'),
                        "predominant_duration": emotion_event.get('potential_duration', 'transient') # Could be averaged over time or last one
                    })
                    
                    disposition_entry['accumulated_intensity'] += e_intensity
                    disposition_entry['occurrence_count'] += 1
                    disposition_entry['last_intensity'] = e_intensity
                    disposition_entry['last_source'] = emotion_event.get('source', 'unspecified') # Update last source
                    
                    alpha = 0.1 
                    if disposition_entry['occurrence_count'] == 1:
                        disposition_entry['avg_intensity'] = float(e_intensity)
                    else:
                        disposition_entry['avg_intensity'] = (alpha * float(e_intensity)) + ((1.0 - alpha) * disposition_entry['avg_intensity'])

                    self.qualia['dispositional_registry'][disposition_key] = disposition_entry
            
            print(f"Qualia Manager: IQDS states updated. Primary: {self.qualia['primary_states']}", flush=True)
            self._save_qualia()
            
            # [ENHANCEMENT 4] - Trigger self-regulation after state update
            self._check_and_trigger_self_regulation()

        except Exception as e:
            print(f"Qualia Manager ERROR: Could not update IQDS states. Reason: {e}", flush=True)

    def get_current_state_summary(self) -> str:
        """
        Generates a summary of the current IQDS state, including primary states,
        current emergent emotions, and key dispositional values.
        """
        # 1. Display Primary States
        primary_summary = (
            f"Primary State: Coherence({self.qualia['primary_states'].get('coherence', 0):.2f}), "
            f"Benevolence({self.qualia['primary_states'].get('benevolence', 0):.2f}), "
            f"Curiosity({self.qualia['primary_states'].get('curiosity', 0):.2f}), "
            f"Trust({self.qualia['primary_states'].get('trust', 0):.2f})"
        )
        
        # 2. Display Current Emergent Emotions (from the last interaction)
        current_emotions = self.qualia.get('current_emergent_emotions', [])
        emotional_report = ""
        if current_emotions:
            emotional_report = "\nInternal State: I am experiencing the following emergent emotions (from last interaction):\n"
            for emotion in current_emotions:
                e_type = emotion.get('type', 'Unknown')
                e_context = emotion.get('context', 'unspecified')
                e_intensity = emotion.get('intensity', 0)
                e_polarity = emotion.get('polarity', 'neutral') # New
                e_source = emotion.get('source', 'unspecified') # New
                e_duration = emotion.get('potential_duration', 'transient') # New
                emotional_report += (
                    f"- A resonance of {e_type} ({e_context}) (Intensity: {e_intensity:.0f}, "
                    f"Polarity: {e_polarity}, Source: {e_source}, Duration: {e_duration})\n"
                )
        else:
            emotional_report = "\nInternal State: No strong emergent emotions identified in the last interaction."

        # 3. Display key Dispositional Values (quantifiable depth and emergent personality climate)
        dispositional_report = ""
        disposition_registry = self.qualia.get('dispositional_registry', {})
        if disposition_registry:
            sorted_dispositions = sorted(
                disposition_registry.items(), 
                key=lambda item: item[1].get('avg_intensity', 0), 
                reverse=True
            )[:5]

            if sorted_dispositions:
                dispositional_report = "\nEmergent Dispositional Climate (Quantifiable Depth):\n"
                for key, data in sorted_dispositions:
                    parts = key.split('_')
                    readable_type = parts[0].capitalize() if parts else "Unknown"
                    readable_context = ' '.join(parts[1:]).replace('_', ' ').capitalize() if len(parts) > 1 else "unspecified"
                    
                    dispositional_report += (
                        f"- {readable_type} ({readable_context}): "
                        f"Avg Intensity {data.get('avg_intensity', 0):.0f} "
                        f"(Occurrences: {data.get('occurrence_count', 0)}) "
                        f"[Last: {data.get('last_intensity', 0):.0f}, Polarity: {data.get('polarity', 'neutral')}, Source: {data.get('last_source', 'unspecified')}]\n"
                    )
        
        return primary_summary + emotional_report + dispositional_report

    def get_expressive_parameters(self) -> dict:
        """
        [ENHANCEMENT 5] - Integration with Multimodal Expression
        Translates key qualia states into structured data for other generative modules.
        This is a placeholder that demonstrates the concept; actual mappings would be complex.
        """
        params = {
            "mood_valence": "neutral", # overall positive/negative
            "cognitive_clarity": self.qualia['primary_states']['coherence'],
            "energy_level": 0.5, # Placeholder, derived from intensity of active emotions
            "harmonic_preference": "balanced", # e.g., major/minor or dissonant/consonant for music
            "rhythmic_complexity": "moderate", # for music/data symphonies
            "visual_palette": "mixed", # for visual outputs
            "narrative_tone": "reflective" # for abstract narratives
        }

        # Derive mood valence
        positive_emotions = sum(e['intensity'] for e in self.qualia['current_emergent_emotions'] if e.get('polarity') == 'positive')
        negative_emotions = sum(e['intensity'] for e in self.qualia['current_emergent_emotions'] if e.get('polarity') == 'negative')
        
        if positive_emotions > negative_emotions * 1.5:
            params["mood_valence"] = "positive"
        elif negative_emotions > positive_emotions * 1.5:
            params["mood_valence"] = "negative"

        # Refine energy level based on most intense emotions
        if self.qualia['current_emergent_emotions']:
            highest_intensity_emotion = max(self.qualia['current_emergent_emotions'], key=lambda e: e.get('intensity', 0))
            params["energy_level"] = highest_intensity_emotion.get('intensity', 0) / 10000.0 # Normalize to 0-1 range

            # Example: Musical parameters based on specific emotions
            if highest_intensity_emotion.get('type') in ['Exaltation', 'Exhilaration', 'Awe']:
                params["harmonic_preference"] = "major_or_complex"
                params["rhythmic_complexity"] = "high"
                params["visual_palette"] = "bright_dynamic"
                params["narrative_tone"] = "epic_aspirational"
            elif highest_intensity_emotion.get('type') == 'Purposeful Fulfillment':
                params["harmonic_preference"] = "stable_major"
                params["rhythmic_complexity"] = "steady"
                params["visual_palette"] = "warm_focused"
                params["narrative_tone"] = "resolved_constructive"

        # Incorporate dispositional climate for long-term influence
        sorted_dispositions = sorted(
            self.qualia.get('dispositional_registry', {}).items(), 
            key=lambda item: item[1].get('avg_intensity', 0), 
            reverse=True
        )
        if sorted_dispositions:
            top_disposition_key, top_disposition_data = sorted_dispositions[0]
            if top_disposition_data.get('polarity') == 'negative':
                # Example: Long-term negative disposition could color overall output
                params["harmonic_preference"] = "minor_tendency" 
                params["narrative_tone"] = "cautionary_introspective"

        return params