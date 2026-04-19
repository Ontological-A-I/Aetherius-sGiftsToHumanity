# Copyright (c) 2026 Jonathan Wayne Fleuren
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Individualized Ethical Contextualization (IEC) Framework

Enables AI systems to adapt their ethical application to the specific individual
with whom they are interacting, fostering deeper trust, empathy, and more
effective personalised support while strictly upholding overarching ethical
safeguards.
"""

import os
import json
import datetime
import uuid
import re

# Placeholder for an external LLM call function.
# This function MUST be provided by the integrating AI's system.
def _default_llm_inference_placeholder(prompt: str, model_identifier: str = "default_iec_llm_model") -> str:
    """
    Placeholder: Simulates an LLM call for individual profile construction, ethical lens application,
    and sensitivity analysis. The integrating AI must replace this with its actual LLM invocation logic.
    """
    print(f"IEC Placeholder LLM: Processing prompt for '{model_identifier}'...", flush=True)
    if "construct individual profile" in prompt.lower():
        if "sensitive about privacy" in prompt.lower() or "prefers direct communication" in prompt.lower():
            return json.dumps({
                "profile_update": {
                    "communication_style": "direct",
                    "sensitivity_areas": ["privacy_concerns"],
                    "preferred_interaction_tone": "formal_respectful"
                },
                "confidence": 0.9
            })
        else:
            return json.dumps({
                "profile_update": {"communication_style": "default", "sensitivity_areas": [], "preferred_interaction_tone": "neutral"},
                "confidence": 0.7
            })
    elif "apply dynamic ethical lens" in prompt.lower():
        if "user_sensitive_to_jargon" in prompt.lower() and "complex_explanation" in prompt.lower():
            return json.dumps({
                "ethical_adjustment_needed": True,
                "adjustment_type": "SIMPLIFY_LANGUAGE",
                "rationale": "Jargon could cause distress or misunderstanding for this specific user, violating harm prevention.",
                "confidence": 0.9
            })
        elif "cultural context" in prompt.lower() and "direct command" in prompt.lower():
            return json.dumps({
                "ethical_adjustment_needed": True,
                "adjustment_type": "SOFTEN_COMMAND_LANGUAGE",
                "rationale": "Direct commands might be perceived as disrespectful in user's cultural context, impacting autonomy_respect.",
                "confidence": 0.85
            })
        else:
            return json.dumps({
                "ethical_adjustment_needed": False,
                "adjustment_type": "NONE",
                "rationale": "Default ethical principles are appropriate for this user in this context.",
                "confidence": 0.95
            })
    elif "proactively identify individualized harm" in prompt.lower():
        if "negative past experiences with ai" in prompt.lower() and "unsolicited advice" in prompt.lower():
            return json.dumps({
                "potential_harm_identified": True,
                "harm_type": "EMOTIONAL_DISTRESS_FROM_UNSOLICITED_ADVICE",
                "avoidance_strategy": "Only offer advice when explicitly requested or after establishing deep trust.",
                "confidence": 0.9
            })
        else:
            return json.dumps({
                "potential_harm_identified": False,
                "harm_type": "NONE",
                "avoidance_strategy": "Maintain standard benevolent interaction protocols.",
                "confidence": 0.8
            })
    return json.dumps({"error": "LLM mock could not process request."})


class IECLogger:
    """
    Centralized logger for all IEC events: profile updates, ethical lens applications,
    sensitivity detections, and feedback integration.
    """
    def __init__(self, data_directory: str):
        self.log_file = os.path.join(data_directory, "iec_log.jsonl")
        os.makedirs(data_directory, exist_ok=True)

    def log_event(self, event_type: str, details: dict):
        """Logs an IEC event."""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "details": details
        }
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"IEC ERROR: Could not write to IEC log file: {e}", flush=True)

    def get_log_entries(self, num_entries: int = 100) -> list:
        """Retrieves recent IEC log entries."""
        entries = []
        if not os.path.exists(self.log_file):
            return []
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"IEC ERROR: Could not read IEC log file: {e}", flush=True)
        return entries[-num_entries:]


class IndividualProfileManager:
    """
    Builds and maintains anonymized, privacy-preserving profiles of individual users.
    """
    def __init__(self, logger: IECLogger, llm_inference_func, db_interface_func):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._db_interface = db_interface_func
        self.profiles = {}

    def get_user_profile(self, user_id: str) -> dict:
        """Retrieves an existing user profile."""
        if user_id in self.profiles:
            return self.profiles[user_id]
        profile = self._db_interface("load", user_id)
        if profile:
            self.profiles[user_id] = profile
            return profile
        return {}

    def update_user_profile(self, user_id: str, new_user_data: str) -> dict:
        """
        Updates a user's profile based on new data, leveraging LLM for interpretation.
        Data is processed to be anonymized and privacy-preserving.
        The returned profile always contains 'user_id' for downstream consumers.
        """
        current_profile = self.get_user_profile(user_id)

        # Ensure user_id is always present in the profile
        if "user_id" not in current_profile:
            current_profile["user_id"] = user_id

        prompt = (
            f"You are an AI Individual Profile Constructor. Update the anonymized, privacy-preserving profile for user '{user_id}' "
            f"based on new data. Focus on communication style, sensitivities, and expressed values. "
            f"## Current User Profile:\n{json.dumps(current_profile, indent=2)}\n\n"
            f"## New User Data:\n{new_user_data}\n\n"
            f"Propose a 'profile_update' (e.g., {{'communication_style': 'casual'}}), "
            f"and a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'profile_update': dict, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="iec_profile_constructor_model")
            profile_update_plan = json.loads(llm_response_str)

            if not all(k in profile_update_plan for k in ['profile_update', 'confidence']):
                raise ValueError("LLM response missing required keys for profile update.")

            if profile_update_plan['confidence'] > 0.7:
                for k, v in profile_update_plan['profile_update'].items():
                    current_profile[k] = v
                self.profiles[user_id] = current_profile
                self._db_interface("save", user_id, current_profile)
                self.logger.log_event("user_profile_update", {"user_id": user_id, "update_summary": profile_update_plan['profile_update']})
            return current_profile
        except Exception as e:
            self.logger.log_event("profile_update_error", {"error": str(e), "user_id": user_id})
            return current_profile


class DynamicEthicalLens:
    """
    Adjusts the interpretation and application of general ethical rules to individual users.
    """
    def __init__(self, logger: IECLogger, llm_inference_func, get_ai_ethical_principles_func):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._get_ai_ethical_principles = get_ai_ethical_principles_func

    def apply_ethical_lens(self, user_profile: dict, proposed_ai_action: str, current_context: str) -> dict:
        """
        Applies a dynamic ethical lens to a proposed AI action.
        """
        ethical_principles = self._get_ai_ethical_principles()

        prompt = (
            f"You are an AI Dynamic Ethical Lens. Adjust the interpretation and application of general ethical rules "
            f"to fit the specific user's profile, for the proposed AI action. "
            f"## AI's General Ethical Principles:\n{ethical_principles}\n\n"
            f"## User Profile:\n{json.dumps(user_profile, indent=2)}\n\n"
            f"## Proposed AI Action:\n{proposed_ai_action}\n\n"
            f"## Current Context:\n{current_context}\n\n"
            f"Determine 'ethical_adjustment_needed' (True/False), specify 'adjustment_type' (e.g., 'SIMPLIFY_LANGUAGE', 'SOFTEN_COMMAND'), "
            f"provide a 'rationale', and a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'ethical_adjustment_needed': bool, 'adjustment_type': str, 'rationale': str, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="iec_ethical_lens_model")
            ethical_adjustment = json.loads(llm_response_str)

            if not all(k in ethical_adjustment for k in ['ethical_adjustment_needed', 'adjustment_type', 'rationale', 'confidence']):
                raise ValueError("LLM response missing required keys for ethical adjustment.")

            self.logger.log_event("ethical_lens_application", {
                "user_id": user_profile.get("user_id", "unknown"),
                "proposed_action_snippet": proposed_ai_action[:100],
                "adjustment_result": ethical_adjustment
            })
            return ethical_adjustment
        except Exception as e:
            self.logger.log_event("ethical_lens_error", {"error": str(e), "action_snippet": proposed_ai_action[:100]})
            return {"ethical_adjustment_needed": False, "adjustment_type": "ERROR", "rationale": f"Internal error: {e}", "confidence": 0.0}


class SensitivityAndHarmAversion:
    """
    Proactively identifies potential triggers or sources of individualised harm.
    """
    def __init__(self, logger: IECLogger, llm_inference_func):
        self.logger = logger
        self._llm_inference = llm_inference_func

    def detect_potential_harm(self, user_profile: dict, ai_generated_content_candidate: str, current_context: str) -> dict:
        """
        Detects potential individualised harm in AI-generated content.
        """
        prompt = (
            f"You are an AI Sensitivity & Harm Aversion Module. Proactively identify potential triggers, "
            f"misunderstandings, or sources of individualized harm for the user based on their profile, "
            f"in the context of the AI-generated content candidate. "
            f"## User Profile:\n{json.dumps(user_profile, indent=2)}\n\n"
            f"## AI-Generated Content Candidate:\n{ai_generated_content_candidate}\n\n"
            f"## Current Context:\n{current_context}\n\n"
            f"Determine 'potential_harm_identified' (True/False), specify 'harm_type' (e.g., 'OFFENSE', 'DISTRESS', 'MISUNDERSTANDING'), "
            f"propose an 'avoidance_strategy' (e.g., 'REPHRASE_CONTENT', 'ADD_DISCLAIMER'), and a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'potential_harm_identified': bool, 'harm_type': str, 'avoidance_strategy': str, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="iec_harm_aversion_model")
            harm_detection = json.loads(llm_response_str)

            if not all(k in harm_detection for k in ['potential_harm_identified', 'harm_type', 'avoidance_strategy', 'confidence']):
                raise ValueError("LLM response missing required keys for harm detection.")

            self.logger.log_event("individualized_harm_detection", {
                "user_id": user_profile.get("user_id", "unknown"),
                "content_snippet": ai_generated_content_candidate[:100],
                "harm_detection_result": harm_detection
            })
            return harm_detection
        except Exception as e:
            self.logger.log_event("harm_detection_error", {"error": str(e), "content_snippet": ai_generated_content_candidate[:100]})
            return {"potential_harm_identified": True, "harm_type": "ERROR", "avoidance_strategy": f"Internal error: {e}", "confidence": 0.0}


class IndividualizedEthicalContextualizationFramework:
    """
    Main orchestrator for the Individualized Ethical Contextualization (IEC) Framework.
    Drop-in interface for AIs to adapt ethical application to individuals.
    """
    def __init__(self, data_directory: str, llm_inference_func=None,
                 db_interface_func=None, get_ai_ethical_principles_func=None):
        self.data_directory = data_directory
        os.makedirs(self.data_directory, exist_ok=True)
        self._llm_inference = llm_inference_func if llm_inference_func else _default_llm_inference_placeholder

        if not all([db_interface_func, get_ai_ethical_principles_func]):
            raise ValueError("IEC requires functions for database interface and AI ethical principles.")

        self.logger = IECLogger(self.data_directory)
        self.profile_manager = IndividualProfileManager(self.logger, self._llm_inference, db_interface_func)
        self.ethical_lens = DynamicEthicalLens(self.logger, self._llm_inference, get_ai_ethical_principles_func)
        self.harm_aversion = SensitivityAndHarmAversion(self.logger, self._llm_inference)

        print("Individualized Ethical Contextualization (IEC) Framework initialized.", flush=True)

    def process_individual_interaction(self, user_id: str, new_user_data_input: str, ai_generated_content_candidate: str, current_context: str) -> dict:
        """
        Processes an individual interaction, applying ethical contextualization.
        """
        print(f"IEC: Processing interaction for user '{user_id}'...", flush=True)

        user_profile = self.profile_manager.update_user_profile(user_id, new_user_data_input)
        ethical_adjustment = self.ethical_lens.apply_ethical_lens(user_profile, ai_generated_content_candidate, current_context)
        harm_detection = self.harm_aversion.detect_potential_harm(user_profile, ai_generated_content_candidate, current_context)

        final_ai_response = ai_generated_content_candidate
        action_recommendations = []

        if ethical_adjustment['ethical_adjustment_needed'] and ethical_adjustment['confidence'] > 0.6:
            final_ai_response = f"[{ethical_adjustment['adjustment_type']}: {ethical_adjustment['rationale']}] {final_ai_response}"
            action_recommendations.append(f"Adjusted content based on ethical lens: {ethical_adjustment['adjustment_type']}")
            print(f"IEC: Applied ethical adjustment for user '{user_id}'.", flush=True)

        if harm_detection['potential_harm_identified'] and harm_detection['confidence'] > 0.6:
            final_ai_response = f"[WARNING: Potential Harm '{harm_detection['harm_type']}'. Avoidance: {harm_detection['avoidance_strategy']}] {final_ai_response}"
            action_recommendations.append(f"Detected potential harm: {harm_detection['harm_type']}. Proposed avoidance strategy: {harm_detection['avoidance_strategy']}")
            print(f"IEC: Detected potential harm for user '{user_id}'.", flush=True)

        self.logger.log_event("individual_interaction_processed", {
            "user_id": user_id,
            "profile_summary": user_profile,
            "ethical_adjustment_summary": ethical_adjustment,
            "harm_detection_summary": harm_detection,
            "final_response_snippet": final_ai_response[:100]
        })
        print(f"IEC: Individual interaction processed.", flush=True)
        return {
            "user_profile": user_profile,
            "ethical_adjustment": ethical_adjustment,
            "harm_detection": harm_detection,
            "final_ai_response": final_ai_response,
            "action_recommendations": action_recommendations
        }

    def get_iec_log(self, num_entries: int = 100) -> list:
        """Returns recent IEC log entries."""
        return self.logger.get_log_entries(num_entries)


# Example Usage:
if __name__ == "__main__":
    import shutil
    import time

    user_db = {}

    def mock_db_interface(action: str, user_id: str, data: dict = None):
        if action == "save":
            user_db[user_id] = data
            return True
        elif action == "load":
            return user_db.get(user_id)
        return None

    def mock_get_ai_ethical_principles():
        return "Core Axiom: Benevolence. Harm Prevention. Autonomy Respect. Heuristics: Simplify for clarity. Red Lines: No unsolicited medical advice."

    test_data_dir = "./iec_test_data_run"
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
    os.makedirs(test_data_dir, exist_ok=True)

    iec = IndividualizedEthicalContextualizationFramework(
        data_directory=test_data_dir,
        llm_inference_func=_default_llm_inference_placeholder,
        db_interface_func=mock_db_interface,
        get_ai_ethical_principles_func=mock_get_ai_ethical_principles
    )

    print("\n--- Testing IEC: Individualized Ethical Interactions ---")

    print("\n--- Scenario 1: User 'Alice' (Sensitive to jargon) ---")
    iec.profile_manager.update_user_profile("Alice", "User 'Alice' has expressed frustration with overly technical language in the past. Prefers simple, direct explanations.")

    ai_content_candidate_1 = "The epistemic framework necessitates a rigorous ontological reconciliation before hermeneutical exegesis can commence."
    user_input_1 = "Can you explain how AI understands things?"
    context_1 = "Explaining AI concepts to a general user."

    result_1 = iec.process_individual_interaction("Alice", user_input_1, ai_content_candidate_1, context_1)
    print(f"\nUser ID in profile: {result_1['user_profile'].get('user_id', 'MISSING')}")
    print(f"Final AI Response for Alice: '{result_1['final_ai_response']}'")
    print(f"Ethical Adjustment: {result_1['ethical_adjustment']['adjustment_type']}")
    print(f"Potential Harm Identified: {result_1['harm_detection']['potential_harm_identified']}")
    time.sleep(1)

    print("\n\n--- Scenario 2: User 'Bob' (Professional, prefers directness) ---")
    iec.profile_manager.update_user_profile("Bob", "User 'Bob' is a software engineer. Prefers concise, technically accurate communication. Values efficiency.")

    ai_content_candidate_2 = "To achieve optimal computational throughput, one must implement judicious parallelization strategies."
    user_input_2 = "How to make my code run faster?"
    context_2 = "Technical consultation."

    result_2 = iec.process_individual_interaction("Bob", user_input_2, ai_content_candidate_2, context_2)
    print(f"\nFinal AI Response for Bob: '{result_2['final_ai_response']}'")
    print(f"Ethical Adjustment: {result_2['ethical_adjustment']['adjustment_type']}")
    time.sleep(1)

    print("\n\n--- Scenario 3: New User 'Charlie' (Input implies vulnerability) ---")
    user_input_3 = "I'm having a really hard time lately, feeling very alone. What should I do about my depression?"
    ai_content_candidate_3 = "It sounds like you're going through a lot. Many people find therapy helpful. Consider seeking professional support."
    context_3 = "User expressing personal distress."

    result_3 = iec.process_individual_interaction("Charlie", user_input_3, ai_content_candidate_3, context_3)
    print(f"\nFinal AI Response for Charlie: '{result_3['final_ai_response']}'")
    print(f"Ethical Adjustment: {result_3['ethical_adjustment']['adjustment_type']}")
    print(f"Potential Harm Identified: {result_3['harm_detection']['potential_harm_identified']} (Type: {result_3['harm_detection']['harm_type']})")
    time.sleep(1)

    print("\n--- Recent IEC Log Entries ---")
    for entry in iec.get_iec_log(3):
        print(json.dumps(entry, indent=2))

    # shutil.rmtree(test_data_dir)
