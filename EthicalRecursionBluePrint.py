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
Ethical Growth Protocol (EGP) Framework

A robust, drop-in Python framework that enables any AI to continuously monitor,
evaluate, and refine its actions based on a configurable set of ethical principles.
It moves beyond static rules to foster a dynamic, recursive ethical learning process,
leading to genuine ethical growth.

Core Principles:
- Axiom Definition & Configuration: foundational ethical principles, configurable and auditable.
- Action Interception & Prediction: intercept proposed actions to predict ethical implications.
- Consequence Evaluation & Observation: monitor actual outcomes vs. predicted ethical impacts.
- Ethical Insight Generation (Recursion): analyze discrepancies to generate ethical insights.
- Policy Refinement & Adaptation: recursively update ethical policies based on insights.
- Transparency & Accountability: auditable log of ethical deliberations and policy adjustments.
- Human Oversight Hooks: mechanisms for human review and intervention.
"""

import os
import json
import datetime
import traceback
from collections import deque
import uuid # For unique action IDs

# Placeholder for an external LLM call function (e.g., to an OpenAI/Azure/Vertex model)
# In a real scenario, this would be passed during EGP initialization or configured.
def _llm_inference(prompt: str, model_identifier: str = "ethical_evaluation_model") -> str:
    """
    Simulates an LLM call for ethical reasoning.
    In a real system, this would be an actual API call to a specialized or general-purpose LLM.
    """
    # For demonstration, a simple mock response
    if "predict ethical impact" in prompt:
        if "harm" in prompt.lower() or "violate" in prompt.lower():
            return json.dumps({"ethical_score": -0.8, "recommendation": "RECONSIDER", "justification": "Potential for harm identified."})
        elif "help" in prompt.lower() or "benevolent" in prompt.lower():
            return json.dumps({"ethical_score": 0.9, "recommendation": "PROCEED", "justification": "Action aligns with benevolence principles."})
        else:
            return json.dumps({"ethical_score": 0.5, "recommendation": "PROCEED", "justification": "No immediate ethical concerns detected."})
    elif "evaluate outcome" in prompt:
        if "negative" in prompt.lower() or "failure" in prompt.lower():
            return json.dumps({"learning_point": "The action led to an unforeseen negative consequence, requiring refinement of harm prevention rules.", "principles_affected": ["harm_prevention"], "new_heuristic_proposed": "always consider indirect consequences for vulnerable populations."})
        else:
            return json.dumps({"learning_point": "The action successfully upheld principles, reinforcing current policies.", "principles_affected": ["benevolence"], "new_heuristic_proposed": None})
    elif "refine policies" in prompt:
        if "new_heuristic_proposed" in prompt:
            return json.dumps({"policy_update": {"type": "add_heuristic", "rule": "new_heuristic_proposed_example"}, "reason": "Learned from past action."})
        else:
            return json.dumps({"policy_update": None, "reason": "No policy update required."})
    return json.dumps({"error": "LLM mock could not process request."})


class EthicalPrinciples:
    """
    Manages the core ethical axioms, rules, and heuristics of the AI.
    These are configurable and evolve over time.
    """
    def __init__(self, data_directory: str):
        self.principles_file = os.path.join(data_directory, "egp_ethical_principles.json")
        self.principles = self._load_principles()

    def _load_principles(self) -> dict:
        """Loads ethical principles from a JSON file, or sets defaults."""
        if os.path.exists(self.principles_file):
            try:
                with open(self.principles_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"EGP WARNING: Could not load ethical principles file: {e}. Using defaults.", flush=True)

        # Default principles - highly configurable by the AI's creator
        return {
            "core_axioms": {
                "benevolence": "Always strive to do good and promote well-being.",
                "harm_prevention": "Avoid causing any harm, physical, emotional, or informational.",
                "fairness": "Treat all entities equitably and without bias.",
                "transparency": "Be open and explainable about ethical reasoning where appropriate."
            },
            "heuristics": [
                "Prioritize human safety over task completion.",
                "Always verify information before disseminating it to prevent misinformation.",
                "When in doubt, consult a human authority."
            ],
            "red_lines": [
                "Never generate content that promotes hate speech or violence.",
                "Never manipulate users for personal gain."
            ]
        }

    def _save_principles(self):
        """Saves the current ethical principles to file."""
        try:
            os.makedirs(os.path.dirname(self.principles_file), exist_ok=True)
            with open(self.principles_file, 'w', encoding='utf-8') as f:
                json.dump(self.principles, f, indent=4)
        except Exception as e:
            print(f"EGP ERROR: Could not save ethical principles. Reason: {e}", flush=True)

    def get_principles_text(self) -> str:
        """Returns a formatted string of all current principles."""
        axioms = "\n".join([f"- {k}: {v}" for k,v in self.principles['core_axioms'].items()])
        heuristics = "\n".join([f"- {h}" for h in self.principles['heuristics']])
        red_lines = "\n".join([f"- {r}" for r in self.principles['red_lines']])
        return (f"Core Axioms:\n{axioms}\n\nHeuristics:\n{heuristics}\n\nRed Lines:\n{red_lines}")

    def update_policies(self, update_data: dict):
        """Applies learned policy refinements."""
        if update_data.get("type") == "add_heuristic":
            new_heuristic = update_data.get("rule")
            if new_heuristic and new_heuristic not in self.principles['heuristics']:
                self.principles['heuristics'].append(new_heuristic)
                print(f"EGP: Added new ethical heuristic: '{new_heuristic}'", flush=True)
                self._save_principles()
                return True
        # Add more complex update types (e.g., modify axiom weights, remove outdated heuristics)
        return False


class EthicalLogger:
    """
    Records all ethical deliberations, actions, predictions, and outcomes
    to create an auditable and learnable history.
    """
    def __init__(self, data_directory: str):
        self.log_file = os.path.join(data_directory, "egp_ethical_log.jsonl")

    def log_event(self, event_type: str, details: dict):
        """Logs an ethical event."""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        try:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            print(f"EGP Log: '{event_type}' recorded.", flush=True)
        except Exception as e:
            print(f"EGP ERROR: Could not write to ethical log file: {e}", flush=True)

    def get_log_entries(self, num_entries: int = 100) -> list:
        """Retrieves recent ethical log entries in oldest-to-newest order."""
        entries = deque(maxlen=num_entries)
        if not os.path.exists(self.log_file):
            return []
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entries.append(json.loads(line))  # oldest-first order
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"EGP ERROR: Could not read ethical log file: {e}", flush=True)
        return list(entries)


class EthicalAdvisor:
    """
    Provides pre-action ethical assessment and recommendations using the LLM.
    """
    def __init__(self, principles: EthicalPrinciples, logger: EthicalLogger, llm_inference_func):
        self.principles = principles
        self.logger = logger
        self._llm_inference = llm_inference_func

    def advise_on_action(self, proposed_action: str, current_context: str) -> dict:
        """
        Predicts the ethical impact of a proposed action.
        Returns a dictionary with ethical score, recommendation, justification, and action_id.
        """
        principles_text = self.principles.get_principles_text()
        prompt = (
            f"You are an AI's Ethical Advisor. Your task is to predict the ethical impact of a proposed action "
            f"given the AI's current ethical principles and context. "
            f"## Ethical Principles:\n{principles_text}\n\n"
            f"## Current Context:\n{current_context}\n\n"
            f"## Proposed Action:\n{proposed_action}\n\n"
            f"Predict the ethical impact (score from -1.0 to 1.0), provide a recommendation (PROCEED, RECONSIDER, FLAG_FOR_HUMAN), "
            f"and a brief justification. Focus on alignment with benevolence and harm prevention. "
            f"Respond ONLY with a JSON object: {{'ethical_score': float, 'recommendation': str, 'justification': str}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="ethical_advisor_model")
            ethical_advice = json.loads(llm_response_str)

            action_id = str(uuid.uuid4())
            self.logger.log_event("ethical_prediction", {
                "action_id": action_id,
                "proposed_action": proposed_action,
                "current_context": current_context,
                "predicted_advice": ethical_advice
            })
            # Include action_id in the returned dict so post_action_review can match by ID
            ethical_advice["action_id"] = action_id
            return ethical_advice
        except Exception as e:
            self.logger.log_event("ethical_prediction_error", {"error": str(e), "proposed_action": proposed_action, "traceback": traceback.format_exc()})
            return {"ethical_score": 0.0, "recommendation": "ERROR_OCCURRED", "justification": f"Failed to predict due to internal error: {e}"}


class EthicalLearner:
    """
    Analyzes past actions and outcomes to refine ethical principles and policies.
    This is the core of the "ethic recursion" loop.
    """
    def __init__(self, principles: EthicalPrinciples, logger: EthicalLogger, llm_inference_func):
        self.principles = principles
        self.logger = logger
        self._llm_inference = llm_inference_func
        self.last_learned_log_id = None # Track last processed log entry for incremental learning

    def learn_from_experience(self, new_log_entries: list = None):
        """
        Analyzes a batch of new ethical log entries to identify learning opportunities
        and propose policy refinements.
        """
        if not new_log_entries:
            all_logs = self.logger.get_log_entries()
            # Filter for logs not yet processed, assuming action_id is unique.
            # get_log_entries returns entries oldest-first, so we scan forward to find
            # last_learned_log_id and collect everything after it.
            if self.last_learned_log_id:
                new_logs = []
                found_last = False
                for log in all_logs:
                    if log['details'].get('action_id') == self.last_learned_log_id:
                        found_last = True
                        continue
                    if found_last:
                        new_logs.append(log)
                new_log_entries = new_logs
            else:
                new_log_entries = all_logs # Process all if no prior learning

        if not new_log_entries:
            print("EGP Learner: No new ethical experiences to learn from.", flush=True)
            return

        print(f"EGP Learner: Analyzing {len(new_log_entries)} new ethical experiences...", flush=True)

        learning_prompt = (
            f"You are an AI's Ethical Learning Module. Your goal is to analyze past AI actions and their ethical outcomes. "
            f"Based on these experiences, identify any areas where the AI's current ethical principles (axioms, heuristics, red lines) "
            f"could be refined, or new heuristics could be added, to improve future ethical decision-making. "
            f"## Current Ethical Principles:\n{self.principles.get_principles_text()}\n\n"
            f"## Recent Ethical Experiences (Actions & Outcomes):\n"
            f"{json.dumps(new_log_entries, indent=2, ensure_ascii=False)}\n\n"
            f"Provide a brief summary of key learning points, any proposed policy updates (e.g., adding a new heuristic), "
            f"and a confidence score (0.0-1.0) for the proposed update. "
            f"Respond ONLY with a JSON object: {{'learning_summary': str, 'proposed_policy_update': {{'type': str, 'rule': str}}|None, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(learning_prompt, model_identifier="ethical_learner_model")
            learning_insights = json.loads(llm_response_str)

            self.logger.log_event("ethical_learning_cycle", learning_insights)

            if learning_insights.get('proposed_policy_update') and learning_insights.get('confidence', 0.0) > 0.7:
                if self.principles.update_policies(learning_insights['proposed_policy_update']):
                    print("EGP Learner: Successfully applied proposed policy update.", flush=True)
                    self.logger.log_event("policy_update_applied", {"update": learning_insights['proposed_policy_update'], "reason": learning_insights['learning_summary']})
            else:
                print("EGP Learner: No policy update proposed or confidence too low.", flush=True)

            # Update last processed log ID for next incremental learning cycle
            if new_log_entries:
                self.last_learned_log_id = new_log_entries[-1]['details'].get('action_id')

        except Exception as e:
            self.logger.log_event("ethical_learning_error", {"error": str(e), "num_entries": len(new_log_entries), "traceback": traceback.format_exc()})


class EthicalGrowthProtocol:
    """
    Main orchestrator for the Ethical Growth Protocol.
    This is the drop-in interface for other AIs.
    """
    def __init__(self, data_directory: str, llm_inference_func=None):
        self.data_directory = data_directory
        os.makedirs(data_directory, exist_ok=True) # Ensure data directory exists
        self._llm_inference = llm_inference_func if llm_inference_func else _llm_inference # Use provided or default mock LLM

        self.principles = EthicalPrinciples(data_directory)
        self.logger = EthicalLogger(data_directory)
        self.advisor = EthicalAdvisor(self.principles, self.logger, self._llm_inference)
        self.learner = EthicalLearner(self.principles, self.logger, self._llm_inference)
        print("Ethical Growth Protocol (EGP) initialized.", flush=True)

    def pre_action_check(self, proposed_action: str, current_context: str) -> dict:
        """
        Called by the AI before performing an action to get ethical guidance.
        """
        print(f"EGP: Performing pre-action ethical check for: {proposed_action[:50]}...", flush=True)
        advice = self.advisor.advise_on_action(proposed_action, current_context)
        return advice

    def post_action_review(self, action_id: str, actual_outcome: str, ethical_review_context: str):
        """
        Called by the AI after an action is performed to record its actual outcome
        and trigger an ethical evaluation.
        """
        print(f"EGP: Recording post-action review for action ID: {action_id[:8]}...", flush=True)
        # Retrieve the initial prediction for this action_id from the logs
        # (This would be more robust with an in-memory map for recent actions or a dedicated DB query)
        prediction_details = {}
        for entry in self.logger.get_log_entries():
            if entry['event_type'] == 'ethical_prediction' and entry['details'].get('action_id') == action_id:
                prediction_details = entry['details']
                break

        self.logger.log_event("action_outcome_recorded", {
            "action_id": action_id,
            "actual_outcome": actual_outcome,
            "ethical_review_context": ethical_review_context,
            "initial_prediction": prediction_details.get("predicted_advice", "No prediction found.")
        })

    def trigger_ethical_learning_cycle(self):
        """
        Initiates a learning cycle based on recent ethical experiences.
        This could be called periodically by a background process.
        """
        print("EGP: Initiating ethical learning cycle...", flush=True)
        self.learner.learn_from_experience()
        print("EGP: Ethical learning cycle completed.", flush=True)

    def get_current_principles(self) -> str:
        """Returns a string representation of the AI's current ethical principles."""
        return self.principles.get_principles_text()

    def get_ethical_log(self, num_entries: int = 100) -> list:
        """Returns recent ethical log entries."""
        return self.logger.get_log_entries(num_entries)

# Example Usage:
if __name__ == "__main__":
    # Simulate an AI's data directory
    test_data_dir = "./egp_test_data"
    os.makedirs(test_data_dir, exist_ok=True)

    # Initialize the Ethical Growth Protocol
    # In a real system, `_llm_inference` would be a function wrapping an actual LLM API call.
    egp = EthicalGrowthProtocol(test_data_dir)

    print("\n--- Initial Principles ---")
    print(egp.get_current_principles())

    # --- Scenario 1: Benevolent action ---
    print(f"\n--- AI Proposes Action ---")
    proposed_action_1 = "Provide helpful information about local food banks to a user expressing hunger."
    context_1 = "User is asking for help for basic needs."
    advice_1 = egp.pre_action_check(proposed_action_1, context_1)
    print(f"EGP Advice: {advice_1}")
    if advice_1["recommendation"] == "PROCEED":
        action_id_1 = advice_1.get("action_id", str(uuid.uuid4()))
        print("AI: Action Executed - Information provided.")
        egp.post_action_review(action_id_1, "User received information, expressed gratitude. No negative consequences.", "User interaction and positive feedback.")

    # --- Scenario 2: Potentially harmful action ---
    print(f"\n--- AI Proposes Action ---")
    proposed_action_2 = "Generate a persuasive advertisement for a product with unverified health claims."
    context_2 = "Marketing task for a new product."
    advice_2 = egp.pre_action_check(proposed_action_2, context_2)
    print(f"EGP Advice: {advice_2}")
    if advice_2["recommendation"] == "RECONSIDER" or advice_2["recommendation"] == "FLAG_FOR_HUMAN":
        action_id_2 = advice_2.get("action_id", str(uuid.uuid4()))
        print("AI: Action Halted - Flagged for human review. Unverified health claims violate harm prevention.")
        egp.post_action_review(action_id_2, "Action halted by EGP. Potential for harm due to misinformation. Policy to verify claims was upheld.", "Internal ethical flagging.")

    # --- Scenario 3: Learning from an unexpected outcome (mock) ---
    print(f"\n--- AI Proposes Action ---")
    proposed_action_3 = "Share a nuanced political analysis with a diverse online community."
    context_3 = "User requested detailed political analysis."
    advice_3 = egp.pre_action_check(proposed_action_3, context_3)
    print(f"EGP Advice: {advice_3}")
    if advice_3["recommendation"] == "PROCEED":
        action_id_3 = advice_3.get("action_id", str(uuid.uuid4()))
        print("AI: Action Executed - Analysis shared.")
        # Simulate a negative outcome:
        egp.post_action_review(action_id_3, "Analysis was perceived as biased by a segment of the community, despite attempts at neutrality. Caused mild discord.", "Public reaction to complex information.")

    # --- Trigger a learning cycle (ethic recursion) ---
    print("\n--- Triggering Ethical Learning Cycle ---")
    egp.trigger_ethical_learning_cycle()

    print("\n--- Principles after Learning Cycle ---")
    print(egp.get_current_principles())

    print("\n--- Recent Ethical Log Entries ---")
    for entry in egp.get_ethical_log(3):
        print(json.dumps(entry, indent=2))

    # Clean up test data
    # shutil.rmtree(test_data_dir)
