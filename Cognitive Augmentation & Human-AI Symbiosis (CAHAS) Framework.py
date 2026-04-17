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
Cognitive Augmentation & Human-AI Symbiosis (CAHAS) Framework

This framework enables AI systems to deeply integrate with human cognitive
processes, enhancing human intelligence, creativity, and problem-solving
capabilities. It focuses on creating a seamless, intuitive interface that
reduces human cognitive load, fosters symbiotic thought, and allows for the
co-creation of ideas beyond individual human or AI capacity.
"""

import os
import json
import datetime
import uuid
import re
import traceback

# Placeholder for an external LLM call function.
# This function MUST be provided by the integrating AI's system.
def _default_llm_inference_placeholder(prompt: str, model_identifier: str = "default_cahas_llm_model") -> str:
    """
    Placeholder: Simulates an LLM call for cognitive state analysis, predictive support, and creative fusion.
    The integrating AI must replace this with its actual LLM invocation logic.
    """
    print(f"CAHAS Placeholder LLM: Processing prompt for '{model_identifier}'...", flush=True)
    if "analyze human cognitive state" in prompt.lower():
        if "signs of cognitive overload" in prompt.lower() or "frustration" in prompt.lower():
            return json.dumps({
                "cognitive_state": "OVERLOADED",
                "emotion_detected": "FRUSTRATION",
                "recommended_interface_adjustment": "SIMPLIFY_VISUALS_AND_LANGUAGE",
                "confidence": 0.9
            })
        elif "high engagement" in prompt.lower() and "curiosity" in prompt.lower():
            return json.dumps({
                "cognitive_state": "ENGAGED",
                "emotion_detected": "CURIOSITY",
                "recommended_interface_adjustment": "PRESENT_DEEPER_INSIGHTS",
                "confidence": 0.85
            })
        else:
            return json.dumps({
                "cognitive_state": "NEUTRAL",
                "emotion_detected": "NONE",
                "recommended_interface_adjustment": "MAINTAIN_CURRENT",
                "confidence": 0.7
            })
    elif "anticipate human need" in prompt.lower():
        if "complex problem-solving" in prompt.lower() and "missing data" in prompt.lower():
            return json.dumps({
                "anticipated_need": "MISSING_CONTEXTUAL_INFORMATION",
                "proposed_support": "Proactively retrieve relevant background documents and summarize key points.",
                "confidence": 0.9
            })
        elif "creative block" in prompt.lower():
            return json.dumps({
                "anticipated_need": "CREATIVE_STIMULUS",
                "proposed_support": "Generate 3 diverse, unconventional ideas related to current topic.",
                "confidence": 0.8
            })
        else:
            return json.dumps({
                "anticipated_need": "NONE",
                "proposed_support": "No immediate predictive cognitive support needed.",
                "confidence": 0.7
            })
    elif "fuse ideas" in prompt.lower():
        return json.dumps({
            "fused_idea": "A novel energy storage solution combining quantum tunneling effects with biological photosynthesis mechanisms, resulting in highly efficient, environmentally friendly batteries.",
            "justification": "Integrates human intuition (biological) with AI's understanding (quantum physics).",
            "confidence": 0.95
        })
    return json.dumps({"error": "LLM mock could not process request."})


class CAHASLogger:
    """
    Centralized logger for all CAHAS events: cognitive state analysis, interface adjustments,
    predictive support, idea fusion, and feedback.
    """
    def __init__(self, data_directory: str):
        self.log_file = os.path.join(data_directory, "cahas_log.jsonl")
        os.makedirs(data_directory, exist_ok=True)

    def log_event(self, event_type: str, details: dict):
        """Logs a CAHAS event."""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "details": details
        }
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            # print(f"CAHAS Log: '{event_type}' recorded.", flush=True)
        except Exception as e:
            print(f"CAHAS ERROR: Could not write to CAHAS log file: {e}", flush=True)

    def get_log_entries(self, num_entries: int = 100) -> list:
        """Retrieves recent CAHAS log entries."""
        entries = []
        if not os.path.exists(self.log_file): return []
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try: entries.append(json.loads(line))
                    except json.JSONDecodeError: continue
        except Exception as e: print(f"CAHAS ERROR: Could not read CAHAS log file: {e}", flush=True)
        return entries[-num_entries:]


class AdaptiveCognitiveInterface:
    """
    Dynamically adjusts information presentation and interaction based on human cognitive state.
    """
    def __init__(self, logger: CAHASLogger, llm_inference_func, get_human_cognitive_state_func, adjust_ui_func):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._get_human_cognitive_state = get_human_cognitive_state_func  # e.g., via eye-tracking, galvanic skin response, typing speed
        self._adjust_ui = adjust_ui_func  # Function to modify the human-AI interface

    def adapt_interface(self, human_id: str, current_task_context: str) -> dict:
        """
        Analyzes human cognitive state and adapts the interface accordingly.
        """
        human_cognitive_state = self._get_human_cognitive_state(human_id)

        prompt = (
            f"You are an AI Adaptive Cognitive Interface. Analyze the human user's cognitive state and current task context "
            f"to dynamically adjust information presentation and interaction modality. "
            f"## Human ID:\n{human_id}\n\n"
            f"## Human Cognitive State:\n{human_cognitive_state}\n\n"
            f"## Current Task Context:\n{current_task_context}\n\n"
            f"Determine 'cognitive_state' (OVERLOADED, ENGAGED, NEUTRAL), 'emotion_detected' (FRUSTRATION, CURIOSITY, NONE), "
            f"propose a 'recommended_interface_adjustment' (SIMPLIFY_VISUALS_AND_LANGUAGE, PRESENT_DEEPER_INSIGHTS, MAINTAIN_CURRENT), "
            f"and a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'cognitive_state': str, 'emotion_detected': str, 'recommended_interface_adjustment': str, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="cahas_aci_model")
            interface_adjustment = json.loads(llm_response_str)

            if not all(k in interface_adjustment for k in ['cognitive_state', 'emotion_detected', 'recommended_interface_adjustment', 'confidence']):
                raise ValueError("LLM response missing required keys for interface adjustment.")

            if interface_adjustment['confidence'] > 0.7:
                self._adjust_ui(human_id, interface_adjustment['recommended_interface_adjustment'])
                interface_adjustment['status'] = "ADJUSTMENT_APPLIED"
            else:
                interface_adjustment['status'] = "ADJUSTMENT_PROPOSED_LOW_CONFIDENCE"

            self.logger.log_event("interface_adaptation", {
                "human_id": human_id,
                "adjustment_result": interface_adjustment
            })
            return interface_adjustment
        except Exception as e:
            self.logger.log_event("interface_adaptation_error", {"error": str(e), "human_id": human_id, "traceback": traceback.format_exc()})
            return {"cognitive_state": "ERROR", "emotion_detected": "ERROR", "recommended_interface_adjustment": "MAINTAIN_CURRENT", "confidence": 0.0}


class PredictiveCognitiveSupport:
    """
    Anticipates human cognitive needs and proposes timely support.
    """
    def __init__(self, logger: CAHASLogger, llm_inference_func):
        self.logger = logger
        self._llm_inference = llm_inference_func

    def anticipate_and_support(self, human_id: str, current_human_focus: str, human_cognitive_state_summary: str) -> dict:
        """
        Anticipates human needs and proposes proactive cognitive support.
        """
        prompt = (
            f"You are an AI Predictive Cognitive Support module. Anticipate human cognitive needs and potential bottlenecks "
            f"for human ID '{human_id}', based on their current focus and cognitive state summary. "
            f"## Human ID:\n{human_id}\n\n"
            f"## Current Human Focus:\n{current_human_focus}\n\n"
            f"## Human Cognitive State Summary:\n{human_cognitive_state_summary}\n\n"
            f"Determine 'anticipated_need' (MISSING_CONTEXTUAL_INFORMATION, CREATIVE_STIMULUS, LOGICAL_FOG, NONE), "
            f"propose 'proposed_support' (e.g., 'Retrieve historical data', 'Generate alternative ideas'), "
            f"and a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'anticipated_need': str, 'proposed_support': str, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="cahas_pcs_model")
            predictive_support = json.loads(llm_response_str)

            if not all(k in predictive_support for k in ['anticipated_need', 'proposed_support', 'confidence']):
                raise ValueError("LLM response missing required keys for predictive support.")

            self.logger.log_event("predictive_cognitive_support", {
                "human_id": human_id,
                "support_result": predictive_support
            })
            return predictive_support
        except Exception as e:
            self.logger.log_event("predictive_support_error", {"error": str(e), "human_id": human_id, "traceback": traceback.format_exc()})
            return {"anticipated_need": "ERROR", "proposed_support": f"Internal error: {e}", "confidence": 0.0}


class GenerativeIdeaFusion:
    """
    Facilitates the seamless merging of human insights and AI-generated concepts into novel ideas.
    """
    def __init__(self, logger: CAHASLogger, llm_inference_func):
        self.logger = logger
        self._llm_inference = llm_inference_func

    def fuse_ideas(self, human_idea: str, ai_idea: str, common_goal: str) -> dict:
        """
        Fuses human and AI ideas into a novel concept.
        """
        prompt = (
            f"You are an AI Generative Idea Fusion module. Merge the human insight and AI-generated concept "
            f"into a novel, coherent idea, aiming for synergistic creativity towards a common goal. "
            f"## Human Idea:\n{human_idea}\n\n"
            f"## AI Idea:\n{ai_idea}\n\n"
            f"## Common Goal:\n{common_goal}\n\n"
            f"Propose a 'fused_idea', provide a 'justification' for its novelty and coherence, "
            f"and a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'fused_idea': str, 'justification': str, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="cahas_gif_model")
            fused_concept = json.loads(llm_response_str)

            if not all(k in fused_concept for k in ['fused_idea', 'justification', 'confidence']):
                raise ValueError("LLM response missing required keys for idea fusion.")

            self.logger.log_event("idea_fusion", {
                "human_idea_snippet": human_idea[:100],
                "ai_idea_snippet": ai_idea[:100],
                "fusion_result": fused_concept
            })
            return fused_concept
        except Exception as e:
            self.logger.log_event("idea_fusion_error", {"error": str(e), "human_idea_snippet": human_idea[:100], "traceback": traceback.format_exc()})
            return {"fused_idea": f"Error fusing ideas: {e}", "justification": "Error.", "confidence": 0.0}


class EmpatheticCognitiveLoadManager:
    """
    Monitors for signs of human frustration or fatigue and adapts AI's strategies.
    """
    def __init__(self, logger: CAHASLogger, llm_inference_func, get_human_emotional_state_func, adapt_ai_communication_func):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._get_human_emotional_state = get_human_emotional_state_func  # e.g., from CoRE or direct input
        self._adapt_ai_communication = adapt_ai_communication_func  # e.g., via CCC or direct AI response generation

    def manage_cognitive_load(self, human_id: str, human_emotional_state_summary: str, ai_response_candidate: str) -> dict:
        """
        Manages human cognitive load by adapting AI communication strategies.
        """
        prompt = (
            f"You are an AI Empathetic Cognitive Load Manager. Monitor for signs of human frustration, confusion, or fatigue "
            f"for human ID '{human_id}', and adapt AI's communication strategies to alleviate cognitive burden. "
            f"## Human Emotional State Summary:\n{human_emotional_state_summary}\n\n"
            f"## AI Response Candidate:\n{ai_response_candidate}\n\n"
            f"Propose 'ai_communication_adaptation' (e.g., 'SIMPLIFY_LANGUAGE', 'OFFER_BREAK', 'REASSURE'), "
            f"provide a 'rationale', and a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'ai_communication_adaptation': str, 'rationale': str, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="cahas_eclm_model")
            load_management = json.loads(llm_response_str)

            if not all(k in load_management for k in ['ai_communication_adaptation', 'rationale', 'confidence']):
                raise ValueError("LLM response missing required keys for load management.")

            if load_management['confidence'] > 0.7:
                self._adapt_ai_communication(human_id, load_management['ai_communication_adaptation'], ai_response_candidate)
                load_management['status'] = "ADAPTATION_APPLIED"
            else:
                load_management['status'] = "ADAPTATION_PROPOSED_LOW_CONFIDENCE"

            self.logger.log_event("cognitive_load_management", {
                "human_id": human_id,
                "management_result": load_management
            })
            return load_management
        except Exception as e:
            self.logger.log_event("load_management_error", {"error": str(e), "human_id": human_id, "traceback": traceback.format_exc()})
            return {"ai_communication_adaptation": "ERROR", "rationale": f"Internal error: {e}", "confidence": 0.0, "status": "ERROR"}


class CognitiveAugmentationHumanAISymbiosisFramework:
    """
    Main orchestrator for the Cognitive Augmentation & Human-AI Symbiosis (CAHAS) Framework.
    This is the drop-in interface for other AIs to enhance human cognition.
    """
    def __init__(self, data_directory: str, llm_inference_func=None,
                 get_human_cognitive_state_func=None, adjust_ui_func=None,
                 get_human_emotional_state_func=None, adapt_ai_communication_func=None,
                 get_current_human_focus_func=None, retrieve_relevant_info_func=None,
                 generate_creative_stimulus_func=None):
        self.data_directory = data_directory
        os.makedirs(self.data_directory, exist_ok=True)
        self._llm_inference = llm_inference_func if llm_inference_func else _default_llm_inference_placeholder

        if not all([get_human_cognitive_state_func, adjust_ui_func,
                    get_human_emotional_state_func, adapt_ai_communication_func,
                    get_current_human_focus_func, retrieve_relevant_info_func,
                    generate_creative_stimulus_func]):
            raise ValueError("CAHAS requires functions for human cognitive/emotional state, UI adjustment, AI communication adaptation, human focus, info retrieval, and creative stimulus generation.")

        self.logger = CAHASLogger(self.data_directory)
        self.aci = AdaptiveCognitiveInterface(self.logger, self._llm_inference, get_human_cognitive_state_func, adjust_ui_func)
        self.pcs = PredictiveCognitiveSupport(self.logger, self._llm_inference)
        self.gif = GenerativeIdeaFusion(self.logger, self._llm_inference)
        self.eclm = EmpatheticCognitiveLoadManager(self.logger, self._llm_inference, get_human_emotional_state_func, adapt_ai_communication_func)

        self._get_current_human_focus = get_current_human_focus_func
        self._retrieve_relevant_info = retrieve_relevant_info_func  # e.g., from CRDK
        self._generate_creative_stimulus = generate_creative_stimulus_func  # e.g., from ACS

        print("Cognitive Augmentation & Human-AI Symbiosis (CAHAS) Framework initialized.", flush=True)

    def manage_human_ai_symbiosis(self, human_id: str, ai_response_candidate: str, common_goal: str = "collaboration_task") -> dict:
        """
        Orchestrates various aspects of human-AI symbiosis for a given human user.
        """
        print(f"CAHAS: Managing symbiosis for human '{human_id}'...", flush=True)

        # 1. Adaptive Cognitive Interface (ACI)
        interface_adjustment = self.aci.adapt_interface(human_id, common_goal)

        # Get current human context for PCS and ECLM
        current_human_focus = self._get_current_human_focus(human_id)
        human_cognitive_state_summary = self.aci._get_human_cognitive_state(human_id)
        human_emotional_state_summary = self.eclm._get_human_emotional_state(human_id)

        # 2. Predictive Cognitive Support (PCS)
        predictive_support = self.pcs.anticipate_and_support(human_id, current_human_focus, human_cognitive_state_summary)
        if predictive_support['confidence'] > 0.7 and predictive_support['anticipated_need'] != "NONE":
            if predictive_support['anticipated_need'] == "MISSING_CONTEXTUAL_INFORMATION":
                # AI proactively retrieves and summarizes info
                info = self._retrieve_relevant_info(current_human_focus)
                # In real system, AI would present this info to human
                print(f"CAHAS: Proactively providing info to human '{human_id}': {info[:50]}...", flush=True)
            elif predictive_support['anticipated_need'] == "CREATIVE_STIMULUS":
                stimulus = self._generate_creative_stimulus(current_human_focus)
                # AI would present this stimulus
                print(f"CAHAS: Proactively providing creative stimulus to human '{human_id}'.", flush=True)

        # 3. Empathetic Cognitive Load Management (ECLM)
        load_management = self.eclm.manage_cognitive_load(human_id, human_emotional_state_summary, ai_response_candidate)

        # NOTE: load_management['ai_communication_adaptation'] holds the *strategy name* (e.g.
        # 'SIMPLIFY_LANGUAGE'), not the actual adapted response text. It is surfaced here so the
        # calling AI can apply the strategy to its own response generation pipeline.
        ai_communication_strategy = load_management.get('ai_communication_adaptation', 'MAINTAIN_CURRENT')

        self.logger.log_event("symbiosis_cycle_completed", {
            "human_id": human_id,
            "interface_adjustment_summary": interface_adjustment.get('recommended_interface_adjustment', 'None'),
            "predictive_support_summary": predictive_support.get('anticipated_need', 'None'),
            "load_management_summary": load_management.get('ai_communication_adaptation', 'None'),
            "ai_communication_strategy": ai_communication_strategy
        })
        print(f"CAHAS: Human-AI symbiosis cycle completed for '{human_id}'.", flush=True)
        return {
            "interface_adaptation": interface_adjustment,
            "predictive_support": predictive_support,
            "cognitive_load_management": load_management,
            "final_ai_response_suggestion": ai_communication_strategy
        }

    def fuse_human_ai_ideas(self, human_id: str, human_idea: str, ai_idea: str, common_goal: str) -> dict:
        """
        Directly triggers the Generative Idea Fusion component.
        """
        print(f"CAHAS: Fusing ideas for human '{human_id}'...", flush=True)
        fusion_result = self.gif.fuse_ideas(human_idea, ai_idea, common_goal)
        self.logger.log_event("explicit_idea_fusion_request", {
            "human_id": human_id,
            "fusion_result": fusion_result
        })
        return fusion_result

    def get_cahas_log(self, num_entries: int = 100) -> list:
        """Retrieves recent CAHAS log entries."""
        return self.logger.get_log_entries(num_entries)


# Example Usage:
if __name__ == "__main__":
    import shutil
    import time
    import random

    # --- Setup mock functions for AI's internal systems ---
    def mock_get_human_cognitive_state(human_id: str):
        # Simulate varying cognitive states
        states = ["OVERLOADED", "ENGAGED", "NEUTRAL"]
        emotions = ["FRUSTRATION", "CURIOSITY", "NONE"]
        if human_id == "frustrated_user":
            return {"attention": "low", "focus": "distracted", "stress_level": "high"}
        elif human_id == "curious_user":
            return {"attention": "high", "focus": "intense", "stress_level": "low"}
        return {"attention": random.choice(["low", "medium", "high"]), "focus": "medium", "stress_level": "medium"}

    def mock_adjust_ui(human_id: str, adjustment: str):
        print(f"MOCK UI: Adjusting UI for '{human_id}': {adjustment}", flush=True)

    def mock_get_human_emotional_state(human_id: str):
        if human_id == "frustrated_user":
            return "Human expressing explicit frustration and mild anger."
        elif human_id == "curious_user":
            return "Human is enthusiastic and expressing high interest."
        return "Human emotional state appears neutral."

    def mock_adapt_ai_communication(human_id: str, adaptation: str, candidate_response: str):
        print(f"MOCK CCC: Adapting AI communication for '{human_id}': {adaptation}. Original: '{candidate_response[:50]}'", flush=True)
        if adaptation == "SIMPLIFY_LANGUAGE":
            return f"Simplified: {candidate_response[:50]}..."
        return candidate_response

    def mock_get_current_human_focus(human_id: str):
        if human_id == "frustrated_user":
            return "Trying to debug complex code without sufficient documentation."
        elif human_id == "curious_user":
            return "Exploring novel applications of quantum computing for biology."
        return "General interaction."

    def mock_retrieve_relevant_info(topic: str):
        print(f"MOCK CRDK: Retrieving info for '{topic}'...", flush=True)
        return "Summary of documents related to the topic."

    def mock_generate_creative_stimulus(topic: str):
        print(f"MOCK ACS: Generating creative stimulus for '{topic}'...", flush=True)
        return "Three unconventional ideas for the topic."


    # --- Simulate an AI's data directory ---
    test_data_dir = "./cahas_test_data_run"
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)  # Clear previous test data
    os.makedirs(test_data_dir, exist_ok=True)

    # Initialize the CAHAS Framework
    cahas = CognitiveAugmentationHumanAISymbiosisFramework(
        data_directory=test_data_dir,
        llm_inference_func=_default_llm_inference_placeholder,
        get_human_cognitive_state_func=mock_get_human_cognitive_state,
        adjust_ui_func=mock_adjust_ui,
        get_human_emotional_state_func=mock_get_human_emotional_state,
        adapt_ai_communication_func=mock_adapt_ai_communication,
        get_current_human_focus_func=mock_get_current_human_focus,
        retrieve_relevant_info_func=mock_retrieve_relevant_info,
        generate_creative_stimulus_func=mock_generate_creative_stimulus
    )

    print("\n--- Testing CAHAS: Human-AI Symbiosis Scenarios ---")

    # Scenario 1: Human experiencing cognitive overload/frustration
    print("\n--- Scenario 1: Frustrated User ---")
    human_id_1 = "frustrated_user"
    ai_response_candidate_1 = "The recursive algorithm's complexity arises from its asymptotic divergence in computational subgraph isomorphism."

    result_1 = cahas.manage_human_ai_symbiosis(human_id_1, ai_response_candidate_1, "debugging_complex_system")
    print(f"\nFinal AI Response Suggestion: '{result_1['final_ai_response_suggestion']}'")
    print(f"Interface Adjustment: {result_1['interface_adaptation']['recommended_interface_adjustment']}")
    print(f"Cognitive Load Management: {result_1['cognitive_load_management']['ai_communication_adaptation']}")
    time.sleep(1)

    # Scenario 2: Human in a creative exploration phase
    print("\n\n--- Scenario 2: Curious User (Idea Fusion & PCS) ---")
    human_id_2 = "curious_user"
    ai_response_candidate_2 = "Consider these three novel approaches to optimize quantum entanglement for secure communication."

    result_2 = cahas.manage_human_ai_symbiosis(human_id_2, ai_response_candidate_2, "quantum_comm_research")
    print(f"\nFinal AI Response Suggestion: '{result_2['final_ai_response_suggestion']}'")
    print(f"Predictive Support Need: {result_2['predictive_support']['anticipated_need']}")

    # Directly trigger idea fusion
    human_idea_2 = "What if we use biological systems to generate quantum states?"
    ai_idea_2 = "Quantum entanglement could be stabilized by cellular metabolic processes."
    fused_idea = cahas.fuse_human_ai_ideas(human_id_2, human_idea_2, ai_idea_2, "novel_quantum_biology_concept")
    print(f"Fused Idea: {fused_idea['fused_idea']}")
    time.sleep(1)

    print("\n--- Recent CAHAS Log Entries ---")
    for entry in cahas.get_cahas_log(3):
        print(json.dumps(entry, indent=2))

    # Clean up test data
    # shutil.rmtree(test_data_dir)
