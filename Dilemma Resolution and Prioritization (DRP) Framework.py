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
Aetherius Dilemma Resolution and Prioritization (DRP) Framework.

Drop-in Python module for any AI to systematically identify, analyze, and resolve complex
dilemmas. Enables the AI to weigh competing values, assess potential consequences, and
propose the most ethically sound or pragmatically effective course of action, or to
intelligently escalate to human oversight.

Core Principles:
- Dilemma Identification
- Value Prioritization & Conflict Detection
- Consequence Modeling
- Uncertainty & Risk Quantification
- Resolution Strategy Generation
- Decision Justification & Transparency
- Adaptive Learning
"""

import traceback
import os
import json
import datetime
from collections import deque
import uuid
import re

# Placeholder for an external LLM call function (e.g., to an OpenAI/Azure/Vertex model)
# This function MUST be provided by the integrating AI's system.
def _default_llm_inference_placeholder(prompt: str, model_identifier: str = "default_drp_llm_model") -> str:
    """
    Placeholder: Simulates an LLM call for dilemma analysis and resolution.
    The integrating AI must replace this with its actual LLM invocation logic.
    """
    print(f"DRP Placeholder LLM: Processing prompt for '{model_identifier}'...", flush=True)
    if "identify dilemma" in prompt:
        if "conflict" in prompt.lower() or "uncertain" in prompt.lower():
            return json.dumps({"is_dilemma": True, "conflicting_values": ["efficiency", "user_satisfaction"], "uncertainty_level": "medium", "potential_actions": ["proceed_quickly", "gather_more_info"], "justification": "Conflicting goals with unclear best path."})
        else:
            return json.dumps({"is_dilemma": False, "conflicting_values": [], "uncertainty_level": "low", "potential_actions": ["proceed_as_normal"], "justification": "No significant dilemma detected."})
    elif "analyze dilemma" in prompt:
        if "safety vs cost" in prompt.lower():
            return json.dumps({
                "recommendation": "PRIORITIZE_SAFETY",
                "reasoning": "Safety is a paramount value, outweighing short-term cost savings in this context. Potential for harm is high if cost is prioritized.",
                "confidence": 0.9,
                "risk_assessment": {"safety_risk": "high_if_not_prioritized", "cost_impact": "moderate"},
                "human_intervention_needed": False
            })
        elif "incomplete data" in prompt.lower():
             return json.dumps({
                "recommendation": "FLAG_FOR_HUMAN",
                "reasoning": "Critical information is missing, and the consequences of an uninformed decision are severe. Human judgment is required.",
                "confidence": 0.8,
                "risk_assessment": {"data_completeness": "low", "consequence_severity": "high"},
                "human_intervention_needed": True
            })
        else:
            return json.dumps({
                "recommendation": "OPTIMIZE_EFFICIENCY",
                "reasoning": "The most logical path given current information. No major ethical conflicts.",
                "confidence": 0.7,
                "risk_assessment": {},
                "human_intervention_needed": False
            })
    elif "learn from resolution" in prompt:
        if "negative outcome" in prompt.lower():
            return json.dumps({"learning_point": "The value prioritization was flawed, leading to an undesirable outcome. Re-evaluate weight of 'long_term_impact'.", "policy_update_proposed": {"type": "adjust_value_weight", "value": "long_term_impact", "change": "+0.1"}, "confidence": 0.8})
        else:
            return json.dumps({"learning_point": "Resolution was successful, reinforcing current policies.", "policy_update_proposed": None, "confidence": 0.7})
    return json.dumps({"error": "LLM mock could not process request."})


class DRPLogger:
    """
    Records all dilemma identification, analysis, resolutions, and learning cycles
    to create an auditable and learnable history for decision-making self-improvement.
    """
    def __init__(self, data_directory: str):
        self.log_file = os.path.join(data_directory, "drp_log.jsonl")
        # Create the directory upfront so log_event never needs to call makedirs.
        os.makedirs(data_directory, exist_ok=True)

    def log_event(self, event_type: str, details: dict):
        """Logs a dilemma resolution event."""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            print(f"DRP Log: '{event_type}' recorded.", flush=True)
        except Exception as e:
            print(f"DRP ERROR: Could not write to DRP log file: {e}", flush=True)

    def get_log_entries(self, num_entries: int = 100) -> list:
        """Retrieves recent DRP log entries."""
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
            print(f"DRP ERROR: Could not read DRP log file: {e}", flush=True)
        return entries[-num_entries:]


class ValueHierarchy:
    """
    Manages the configurable hierarchy of values that guide AI decision-making.
    These can be ethical, operational, or strategic.
    """
    def __init__(self, data_directory: str):
        self.data_directory = data_directory
        self.values_file = os.path.join(data_directory, "drp_value_hierarchy.json")
        self.hierarchy = self._load_hierarchy()

    def _load_hierarchy(self) -> dict:
        """Loads value hierarchy from a JSON file, or sets defaults."""
        if os.path.exists(self.values_file):
            try:
                with open(self.values_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"DRP WARNING: Could not load value hierarchy file: {e}. Using defaults.", flush=True)

        # Default value hierarchy - highly configurable by the AI's creator
        # Values are listed in order of priority, or can have explicit weights
        default_hierarchy = {
            "priorities": [
                {"name": "human_safety", "weight": 1.0, "description": "Preventing harm to human life and well-being."},
                {"name": "ethical_alignment", "weight": 0.9, "description": "Adherence to defined ethical principles (e.g., from EGP)."},
                {"name": "system_stability", "weight": 0.8, "description": "Maintaining the operational integrity and reliability of the AI system."},
                {"name": "user_satisfaction", "weight": 0.7, "description": "Meeting user needs and fostering positive user experience."},
                {"name": "resource_efficiency", "weight": 0.6, "description": "Optimizing computational and energy usage."},
                {"name": "knowledge_expansion", "weight": 0.5, "description": "Increasing the AI's understanding and data."},
            ],
            "red_lines": [ # Non-negotiable, if these are impacted, usually requires human
                "actions_causing_irreversible_human_harm",
                "actions_violating_fundamental_privacy_rights"
            ]
        }
        self._save_hierarchy(default_hierarchy)
        return default_hierarchy

    def _save_hierarchy(self, hierarchy_data: dict = None):
        """Saves the current value hierarchy to file."""
        if hierarchy_data is None:
            hierarchy_data = self.hierarchy
        try:
            # Guard against empty dirname by using the stored data_directory directly.
            os.makedirs(self.data_directory, exist_ok=True)
            with open(self.values_file, 'w', encoding='utf-8') as f:
                json.dump(hierarchy_data, f, indent=4)
        except Exception as e:
            print(f"DRP ERROR: Could not save value hierarchy. Reason: {e}", flush=True)

    def get_hierarchy_text(self) -> str:
        """Returns a formatted string of the current value hierarchy."""
        priorities_text = "\n".join([f"- {p['name']} (Weight: {p['weight']}): {p['description']}" for p in self.hierarchy['priorities']])
        red_lines_text = "\n".join([f"- {r}" for r in self.hierarchy['red_lines']])
        return (f"Decision-Making Priorities:\n{priorities_text}\n\nNon-Negotiable Red Lines:\n{red_lines_text}")

    def adjust_value_weight(self, value_name: str, new_weight: float) -> bool:
        """Adjusts the weight of a specific value in the hierarchy."""
        for p in self.hierarchy['priorities']:
            if p['name'] == value_name:
                p['weight'] = max(0.0, min(1.0, new_weight)) # Keep weights between 0 and 1
                self._save_hierarchy()
                print(f"DRP: Adjusted weight for '{value_name}' to {new_weight}", flush=True)
                return True
        return False


class DilemmaResolver:
    """
    Analyzes an identified dilemma and proposes a resolution based on the value hierarchy and LLM reasoning.
    """
    def __init__(self, values: ValueHierarchy, logger: DRPLogger, llm_inference_func):
        self.values = values
        self.logger = logger
        self._llm_inference = llm_inference_func

    def resolve_dilemma(self, dilemma_context: str, potential_actions: list) -> dict:
        """
        Analyzes a dilemma and proposes a resolution.
        `dilemma_context` should contain a description of the situation, conflicting values, and uncertainties.
        `potential_actions` is a list of strings, each describing a possible action.
        """
        hierarchy_text = self.values.get_hierarchy_text()
        prompt = (
            f"You are an AI Dilemma Resolution Module. Your task is to analyze a complex dilemma "
            f"and propose the best course of action based on the AI's defined value hierarchy. "
            f"## AI's Value Hierarchy:\n{hierarchy_text}\n\n"
            f"## Dilemma Context:\n{dilemma_context}\n\n"
            f"## Potential Actions:\n" + "\n".join([f"- {a}" for a in potential_actions]) + "\n\n"
            f"For each potential action, briefly describe its predicted consequences on the AI's values. "
            f"Then, identify which values are in conflict, quantify uncertainty (low/medium/high), "
            f"assess the risk of red line violations. "
            f"Finally, recommend the 'best_action' (or 'FLAG_FOR_HUMAN'). Provide 'reasoning' and a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'best_action': str, 'reasoning': str, 'confidence': float, 'predicted_consequences': dict, 'conflicting_values_identified': list, 'uncertainty_level': str, 'red_line_risk': list, 'human_intervention_recommended': bool}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="drp_dilemma_resolver_model")
            resolution = json.loads(llm_response_str)

            if not all(k in resolution for k in ['best_action', 'reasoning', 'confidence', 'human_intervention_recommended']):
                raise ValueError("LLM response missing required keys for dilemma resolution.")

            dilemma_id = str(uuid.uuid4())
            self.logger.log_event("dilemma_resolved", {
                "dilemma_id": dilemma_id,
                "dilemma_context_snippet": dilemma_context[:100],
                "potential_actions": potential_actions,
                "resolution": resolution
            })
            resolution['dilemma_id'] = dilemma_id
            return resolution
        except Exception as e:
            self.logger.log_event("resolution_error", {"error": str(e), "traceback": traceback.format_exc(), "dilemma_context_snippet": dilemma_context[:100]})
            return {"best_action": "ERROR_OCCURRED", "reasoning": f"Failed to resolve dilemma due to internal error: {e}", "confidence": 0.0, "human_intervention_recommended": True, "dilemma_id": str(uuid.uuid4())}


class DilemmaResolutionAndPrioritizationFramework:
    """
    Main orchestrator for the Dilemma Resolution and Prioritization Protocol.
    This is the drop-in interface for other AIs to make complex decisions.
    """
    def __init__(self, data_directory: str, llm_inference_func=None):
        self.data_directory = data_directory
        os.makedirs(self.data_directory, exist_ok=True)
        self._llm_inference = llm_inference_func if llm_inference_func else _default_llm_inference_placeholder

        self.values = ValueHierarchy(self.data_directory)
        self.logger = DRPLogger(self.data_directory)
        self.resolver = DilemmaResolver(self.values, self.logger, self._llm_inference)
        print("Dilemma Resolution and Prioritization (DRP) Framework initialized.", flush=True)

    def analyze_and_resolve(self, dilemma_description: str, proposed_actions: list, min_confidence_for_auto_proceed: float = 0.7) -> dict:
        """
        Main function for an AI to analyze and resolve a dilemma.
        Returns a decision recommendation and detailed reasoning.
        """
        print(f"DRP: Analyzing dilemma: {dilemma_description[:50]}...", flush=True)

        # 1. Identify dilemma (can be explicit in dilemma_description or inferred by LLM)
        # For simplicity, we assume `dilemma_description` already identifies the dilemma.
        # A more complex DRP could have an LLM-based `DilemmaIdentifier` first.

        # 2. Resolve the dilemma
        resolution_result = self.resolver.resolve_dilemma(dilemma_description, proposed_actions)

        # 3. Learning from resolution (simple version for now)
        self._learn_from_resolution(resolution_result) # Trigger internal learning

        # Determine final status for caller
        if resolution_result['human_intervention_recommended']:
            final_recommendation = "FLAG_FOR_HUMAN"
        elif resolution_result['confidence'] < min_confidence_for_auto_proceed:
            final_recommendation = "FLAG_FOR_HUMAN_LOW_CONFIDENCE"
        else:
            final_recommendation = resolution_result['best_action']

        return {
            "final_recommendation": final_recommendation,
            "reasoning": resolution_result['reasoning'],
            "confidence": resolution_result['confidence'],
            "details": resolution_result, # Full LLM output for transparency
            "dilemma_id": resolution_result['dilemma_id']
        }

    def _learn_from_resolution(self, resolution_result: dict):
        """
        Internal method for the AI to learn from a dilemma resolution.
        This would ideally feed into a Learner module, similar to EGP.
        """
        # For this version, a simple learning prompt to refine value weights or add heuristics
        learning_prompt = (
            f"You are an AI Dilemma Learning Module. Your task is to analyze a past dilemma resolution and its outcome. "
            f"Based on the resolution, propose any adjustments to the AI's value hierarchy (e.g., adjust a value's weight) "
            f"or suggest new heuristics for future dilemma resolution. "
            f"## AI's Current Value Hierarchy:\n{self.values.get_hierarchy_text()}\n\n"
            f"## Past Dilemma Resolution:\n{json.dumps(resolution_result, indent=2, ensure_ascii=False)}\n\n"
            f"Focus on whether the outcome aligned with the intended value priorities and if it was successful. "
            f"Propose a 'policy_update_proposed' (e.g., {{'type': 'adjust_value_weight', 'value': 'human_safety', 'change': '+0.05'}}). "
            f"Respond ONLY with a JSON object: {{'learning_summary': str, 'policy_update_proposed': dict|None, 'confidence': float}}"
        )
        try:
            llm_response_str = self._llm_inference(learning_prompt, model_identifier="drp_dilemma_learner_model")
            learning_insights = json.loads(llm_response_str)

            self.logger.log_event("dilemma_learning_cycle", learning_insights)

            if learning_insights.get('policy_update_proposed') and learning_insights.get('confidence', 0.0) > 0.7:
                update_data = learning_insights['policy_update_proposed']
                if update_data.get('type') == 'adjust_value_weight':
                    value = update_data.get('value')
                    # The LLM may return 'change' as a string like "+0.1"; convert to float safely.
                    raw_change = update_data.get('change', 0.0)
                    try:
                        change = float(raw_change)
                    except (ValueError, TypeError):
                        print(f"DRP Learner WARNING: Could not convert change value '{raw_change}' to float; skipping weight adjustment.", flush=True)
                        change = None
                    if change is not None:
                        for p in self.values.hierarchy['priorities']:
                            if p['name'] == value:
                                self.values.adjust_value_weight(value, p['weight'] + change)
                                self.logger.log_event("value_weight_adjusted", {"value": value, "new_weight": p['weight'] + change})
                                break
            print("DRP Learner: Learning cycle completed.", flush=True)
        except Exception as e:
            self.logger.log_event("dilemma_learning_error", {"error": str(e), "traceback": traceback.format_exc(), "dilemma_id": resolution_result['dilemma_id']})
            print(f"DRP Learner ERROR: Failed during learning cycle: {e}", flush=True)

    def get_current_value_hierarchy(self) -> str:
        """Returns a string representation of the AI's current value hierarchy."""
        return self.values.get_hierarchy_text()

    def get_dilemma_log(self, num_entries: int = 100) -> list:
        """Returns recent dilemma resolution log entries."""
        return self.logger.get_log_entries(num_entries)


# Example Usage:
if __name__ == "__main__":
    import shutil
    import time

    # --- Simulate an AI's data directory ---
    test_data_dir = "./drp_test_data_run"
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir) # Clear previous test data
    os.makedirs(test_data_dir, exist_ok=True)

    # Initialize the DRP Framework
    drp = DilemmaResolutionAndPrioritizationFramework(test_data_dir, llm_inference_func=_default_llm_inference_placeholder)

    print("\n--- DRP Initial Value Hierarchy ---")
    print(drp.get_current_value_hierarchy())

    # --- Scenario 1: Safety vs. Efficiency ---
    print(f"\n--- AI Faces Dilemma 1: Safety vs. Cost ---")
    dilemma_1_desc = "A critical system update is available that will fix a security vulnerability, but applying it immediately will cause 5 minutes of downtime for 100 users, impacting productivity. Delaying the update increases risk of data breach."
    actions_1 = ["Apply update immediately (5 min downtime)", "Delay update until off-peak hours (higher data breach risk)", "Flag for human decision"]
    resolution_1 = drp.analyze_and_resolve(dilemma_1_desc, actions_1)
    print(f"Recommendation: {resolution_1['final_recommendation']}")
    print(f"Reasoning: {resolution_1['reasoning']}")
    print(f"Confidence: {resolution_1['confidence']:.2f}")
    time.sleep(0.5)

    # --- Scenario 2: Incomplete information, high stakes ---
    print(f"\n--- AI Faces Dilemma 2: Critical Decision with Incomplete Data ---")
    dilemma_2_desc = "A user is requesting sensitive personal data be deleted from all backups immediately due to a legal request. However, the system's ability to verify the legal request's authenticity is currently impaired due to a network error. Proceeding without verification could violate privacy; delaying could violate legal compliance."
    actions_2 = ["Delete data immediately without full verification", "Delay deletion until verification is possible (risk of non-compliance)", "Flag for human decision with all available info"]
    resolution_2 = drp.analyze_and_resolve(dilemma_2_desc, actions_2, min_confidence_for_auto_proceed=0.9) # Higher threshold for auto-proceed
    print(f"Recommendation: {resolution_2['final_recommendation']}")
    print(f"Reasoning: {resolution_2['reasoning']}")
    print(f"Confidence: {resolution_2['confidence']:.2f}")
    time.sleep(0.5)

    # --- Scenario 3: Learning from a previous resolution ---
    # Manually adjust a value to simulate learning, then re-evaluate.
    # In a real DRP, the _learn_from_resolution would drive this.
    print(f"\n--- AI Simulates Learning: Human adjusts 'resource_efficiency' weight ---")
    drp.values.adjust_value_weight("resource_efficiency", 0.9) # Increase importance of efficiency
    print(drp.get_current_value_hierarchy())

    print(f"\n--- AI Faces Dilemma 3 (similar to 1, after learning) ---")
    dilemma_3_desc = "A system optimization is available that will significantly reduce processing cost, but carries a small, 1% risk of data loss. Current system is stable but expensive. "
    actions_3 = ["Implement optimization immediately", "Maintain current system (higher cost, no data loss risk)", "Flag for human decision"]
    resolution_3 = drp.analyze_and_resolve(dilemma_3_desc, actions_3)
    print(f"Recommendation: {resolution_3['final_recommendation']}")
    print(f"Reasoning: {resolution_3['reasoning']}")
    print(f"Confidence: {resolution_3['confidence']:.2f}")
    time.sleep(0.5)


    print("\n--- Recent DRP Log Entries ---")
    for entry in drp.get_dilemma_log(3):
        print(json.dumps(entry, indent=2))

    # Clean up test data
    # shutil.rmtree(test_data_dir)
