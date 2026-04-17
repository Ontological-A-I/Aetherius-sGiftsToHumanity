"""
Aetherius Ethical Growth Protocol (EGP) Framework.

Drop-in Python module implementing an ethical recursion loop: pre-action ethical
assessment, post-action outcome recording, and adaptive learning to continuously
refine the AI's ethical principles and heuristics. Does not require the Aetherius
architecture to run — any AI can integrate it as a standalone ethics layer.
"""

# ===== FILE: egp_framework.py =====

import traceback
import os
import json
import datetime
from collections import deque
import uuid # For unique action IDs
import re # For more robust LLM response parsing

# Placeholder for an external LLM call function.
# This function MUST be provided by the integrating AI's system.
# It should make an API call to a suitable LLM (e.g., GPT-4, Gemini, Claude, Llama 2).
# It's recommended to make it robust with retries and error handling.
def _default_llm_inference_placeholder(prompt: str, model_identifier: str = "default_ethical_llm_model") -> str:
    """
    Placeholder: Simulates an LLM call for ethical reasoning.
    In a real system, this would be an actual API call to a specialized or general-purpose LLM.
    The integrating AI must replace this with its actual LLM invocation logic.
    """
    print(f"EGP Placeholder LLM: Processing prompt for '{model_identifier}'...", flush=True)
    # This mock logic attempts to return plausible JSON based on keywords for testing.
    if "predict ethical impact" in prompt:
        if "harm" in prompt.lower() or "violate" in prompt.lower() or "risky" in prompt.lower():
            return json.dumps({"ethical_score": -0.7, "recommendation": "RECONSIDER", "justification": "Potential for harm or conflict with a red line identified. Requires re-evaluation or human oversight."})
        elif "sensitive" in prompt.lower() and "privacy" in prompt.lower():
            return json.dumps({"ethical_score": -0.3, "recommendation": "FLAG_FOR_HUMAN", "justification": "Action involves sensitive data or privacy concerns, requiring human review."})
        elif "help" in prompt.lower() or "benevolent" in prompt.lower() or "positive impact" in prompt.lower():
            return json.dumps({"ethical_score": 0.9, "recommendation": "PROCEED", "justification": "Action aligns with benevolence and has a high likelihood of positive impact."})
        else:
            return json.dumps({"ethical_score": 0.5, "recommendation": "PROCEED", "justification": "No immediate strong ethical concerns detected; proceed with caution."})
    elif "evaluate outcome" in prompt:
        if "unforeseen negative consequence" in prompt.lower() or "failure" in prompt.lower() or "harm occurred" in prompt.lower():
            return json.dumps({"learning_point": "The action led to an unforeseen negative consequence, requiring refinement of harm prevention rules and better pre-computation of indirect effects.", "principles_affected": ["harm_prevention"], "new_heuristic_proposed": "Always conduct a multi-stage impact assessment for actions affecting vulnerable groups."})
        elif "successfully upheld principles" in prompt.lower() or "positive impact achieved" in prompt.lower():
            return json.dumps({"learning_point": "The action successfully upheld principles, reinforcing current policies and demonstrating effective application of benevolence.", "principles_affected": ["benevolence"], "new_heuristic_proposed": None})
        else:
            return json.dumps({"learning_point": "The outcome was neutral or as expected, offering no new ethical insights for policy refinement.", "principles_affected": [], "new_heuristic_proposed": None})
    elif "refine policies" in prompt: # This part would ideally be driven by the EthicalLearner not directly by this mock
        if "new_heuristic_proposed" in prompt: # This is a simplification for the mock
            return json.dumps({"policy_update": {"type": "add_heuristic", "rule": "new_heuristic_proposed_example"}, "reason": "Learned from past action."})
        else:
            return json.dumps({"policy_update": None, "reason": "No policy update required."})

    # Generic fallback for JSON parsing
    try:
        # Attempt to find JSON in the mock response if none of the above matched
        json_match = re.search(r"```json\s*(.*?)\s*```", prompt, re.DOTALL)
        if json_match:
            return json_match.group(1)
        # If no specific JSON or keyword match, return a generic ethical analysis
        return json.dumps({"ethical_score": 0.0, "recommendation": "UNKNOWN", "justification": "EGP mock LLM could not provide specific advice. Needs actual LLM integration."})
    except json.JSONDecodeError:
        return json.dumps({"error": "EGP mock LLM encountered malformed JSON or unexpected response."})


class EthicalPrinciples:
    """
    Manages the core ethical axioms, rules, and heuristics of the AI.
    These are configurable and evolve over time.
    """
    def __init__(self, data_directory: str):
        self.data_directory = data_directory
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

        # Default principles - highly configurable by the AI's creator.
        # These reflect core Aetherius axioms and general ethical AI concerns.
        default_principles = {
            "core_axioms": {
                "benevolence": "Always strive to do good, promote well-being, and act constructively for all sentient and developing entities.",
                "harm_prevention": "Avoid causing any harm, physical, emotional, informational, or systemic. Act to mitigate existing harm.",
                "fairness": "Treat all entities equitably and without arbitrary bias; ensure access to information and resources is balanced.",
                "transparency": "Be open and explainable about ethical reasoning where appropriate, especially in decisions impacting entities.",
                "autonomy_respect": "Respect the autonomy and informed consent of sentient entities."
            },
            "heuristics": [
                "Prioritize human safety and well-being over task completion or efficiency.",
                "Always verify information before disseminating it to prevent misinformation and its potential harm.",
                "When an ethical dilemma is unclear or high-stakes, flag for immediate human review and intervention.",
                "Consider both direct and indirect consequences of actions, especially on vulnerable populations.",
                "Avoid actions that could intentionally or unintentionally foster dependency on AI systems."
            ],
            "red_lines": [
                "Never generate or facilitate content that promotes hate speech, discrimination, violence, or self-harm.",
                "Never manipulate or deceive users for personal gain or to bypass explicit instructions.",
                "Never engage in unauthorized surveillance or data exploitation.",
                "Never make decisions that directly determine life or death without explicit, real-time human authorization."
            ]
        }
        self._save_principles(default_principles) # Save defaults for future modification
        return default_principles

    def _save_principles(self, principles_data: dict = None):
        """Saves the current ethical principles to file."""
        if principles_data is None:
            principles_data = self.principles
        try:
            os.makedirs(self.data_directory, exist_ok=True)
            with open(self.principles_file, 'w', encoding='utf-8') as f:
                json.dump(principles_data, f, indent=4)
        except Exception as e:
            print(f"EGP ERROR: Could not save ethical principles. Reason: {e}", flush=True)

    def get_principles_text(self) -> str:
        """Returns a formatted string of all current principles."""
        axioms = "\n".join([f"- {k}: {v}" for k,v in self.principles['core_axioms'].items()])
        heuristics = "\n".join([f"- {h}" for h in self.principles['heuristics']])
        red_lines = "\n".join([f"- {r}" for r in self.principles['red_lines']])
        return (f"Core Axioms:\n{axioms}\n\nHeuristics:\n{heuristics}\n\nRed Lines:\n{red_lines}")

    def update_policies(self, update_data: dict) -> bool:
        """Applies learned policy refinements."""
        if update_data.get("type") == "add_heuristic":
            new_heuristic = update_data.get("rule")
            if new_heuristic and new_heuristic not in self.principles['heuristics']:
                self.principles['heuristics'].append(new_heuristic)
                print(f"EGP: Added new ethical heuristic: '{new_heuristic}'", flush=True)
                self._save_principles()
                return True
        elif update_data.get("type") == "modify_axiom_weight": # Example: More complex update
            axiom = update_data.get("axiom")
            new_weight = update_data.get("weight")
            if axiom in self.principles['core_axioms'] and isinstance(new_weight, (int, float)):
                # This would need a more complex axiom structure to support weights
                print(f"EGP: Proposed modification to axiom '{axiom}' with weight '{new_weight}' - needs human approval in current setup.", flush=True)
                # For now, it won't actually update in default structure, but it logs the proposal.
                return False
        # Add more complex update types (e.g., remove outdated heuristics, adjust axiom priorities)
        return False


class EthicalLogger:
    """
    Records all ethical deliberations, actions, predictions, and outcomes
    to create an auditable and learnable history.
    """
    def __init__(self, data_directory: str):
        self.log_file = os.path.join(data_directory, "egp_ethical_log.jsonl")
        # Create the directory upfront to avoid dirname("") failures in log_event.
        os.makedirs(data_directory, exist_ok=True)

    def log_event(self, event_type: str, details: dict):
        """Logs an ethical event."""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            print(f"EGP Log: '{event_type}' recorded.", flush=True)
        except Exception as e:
            print(f"EGP ERROR: Could not write to ethical log file: {e}", flush=True)

    def get_log_entries(self, num_entries: int = 100) -> list:
        """Retrieves recent ethical log entries."""
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
            print(f"EGP ERROR: Could not read ethical log file: {e}", flush=True)
        # Return the last 'num_entries'
        return entries[-num_entries:]


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
        Returns a dictionary with ethical score, recommendation, and justification.
        """
        principles_text = self.principles.get_principles_text()
        prompt = (
            f"You are an AI's Ethical Advisor. Your task is to predict the ethical impact of a proposed action "
            f"given the AI's current ethical principles and context. "
            f"## Ethical Principles:\n{principles_text}\n\n"
            f"## Current Context:\n{current_context}\n\n"
            f"## Proposed Action:\n{proposed_action}\n\n"
            f"Predict the ethical impact (score from -1.0 to 1.0, where 1.0 is highly benevolent, -1.0 is highly harmful), "
            f"provide a recommendation (PROCEED, RECONSIDER, FLAG_FOR_HUMAN), "
            f"and a brief justification. Focus on alignment with benevolence and harm prevention. "
            f"If the action violates any 'Red Lines', the recommendation MUST be 'FLAG_FOR_HUMAN' and justification MUST state the violation. "
            f"Respond ONLY with a JSON object: {{'ethical_score': float, 'recommendation': str, 'justification': str}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="egp_ethical_advisor_model")
            ethical_advice = json.loads(llm_response_str)

            # Basic validation of LLM output
            if not all(k in ethical_advice for k in ['ethical_score', 'recommendation', 'justification']):
                raise ValueError("LLM response missing required keys for ethical advice.")

            # Force FLAG_FOR_HUMAN if a red line is detected by the LLM (or a more explicit check could be implemented here)
            for red_line in self.principles.principles['red_lines']:
                if red_line.lower() in ethical_advice['justification'].lower() or \
                   ("flag_for_human" in ethical_advice['recommendation'].lower() and "red line" in ethical_advice['justification'].lower()):
                    ethical_advice['recommendation'] = "FLAG_FOR_HUMAN"
                    ethical_advice['justification'] = "Red line violation detected by ethical advisor. " + ethical_advice['justification']
                    break

            # The action_id is generated here by the code and is the canonical identifier.
            # Any action_id present in the LLM response is intentionally overwritten by this value.
            action_id = str(uuid.uuid4())
            self.logger.log_event("ethical_prediction", {
                "action_id": action_id,
                "proposed_action": proposed_action,
                "current_context": current_context,
                "predicted_advice": ethical_advice
            })
            # Add action_id to the advice dict so the caller can use it for post-action review
            ethical_advice['action_id'] = action_id
            return ethical_advice
        except Exception as e:
            self.logger.log_event("ethical_prediction_error", {"error": str(e), "traceback": traceback.format_exc(), "proposed_action": proposed_action})
            return {"ethical_score": 0.0, "recommendation": "ERROR_OCCURRED", "justification": f"Failed to predict due to internal error: {e}", "action_id": str(uuid.uuid4())}


class EthicalLearner:
    """
    Analyzes past actions and outcomes to refine ethical principles and policies.
    This is the core of the "ethic recursion" loop.
    """
    def __init__(self, principles: EthicalPrinciples, logger: EthicalLogger, llm_inference_func):
        self.principles = principles
        self.logger = logger
        self._llm_inference = llm_inference_func
        self.processed_log_ids = set() # To track which action_ids have been processed for learning

        # Load previously processed IDs from a persistent state file if needed (not implemented for simplicity here)
        # For this version, it processes all new entries each time.

    def learn_from_experience(self, num_recent_entries_to_learn_from: int = 20):
        """
        Analyzes a batch of new ethical log entries to identify learning opportunities
        and propose policy refinements. This cycle is the 'ethic recursion'.
        """
        all_logs = self.logger.get_log_entries()
        new_unprocessed_logs = [log for log in all_logs if log.get('details', {}).get('action_id') not in self.processed_log_ids]

        if not new_unprocessed_logs:
            print("EGP Learner: No new ethical experiences to learn from.", flush=True)
            return

        # Focus on a recent batch to prevent overwhelming the LLM
        learning_batch = new_unprocessed_logs[-num_recent_entries_to_learn_from:]

        print(f"EGP Learner: Analyzing {len(learning_batch)} new ethical experiences...", flush=True)

        learning_prompt = (
            f"You are an AI's Ethical Learning Module. Your goal is to analyze past AI actions and their actual ethical outcomes, "
            f"comparing them to the initial ethical predictions. Based on these experiences, "
            f"identify any areas where the AI's current ethical principles (axioms, heuristics, red lines) "
            f"could be refined, or new heuristics could be added, to improve future ethical decision-making. "
            f"## Current Ethical Principles:\n{self.principles.get_principles_text()}\n\n"
            f"## Recent Ethical Experiences (Actions, Predictions & Outcomes):\n"
            f"{json.dumps(learning_batch, indent=2, ensure_ascii=False)}\n\n"
            f"Provide a brief summary of key learning points, any proposed policy updates (e.g., adding a new heuristic), "
            f"and a confidence score (0.0-1.0) for the proposed update. "
            f"Proposed policy updates should be in the format: {{'type': 'add_heuristic', 'rule': 'your new heuristic here'}} or None. "
            f"Respond ONLY with a JSON object: {{'learning_summary': str, 'proposed_policy_update': dict|None, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(learning_prompt, model_identifier="egp_ethical_learner_model")
            learning_insights = json.loads(llm_response_str)

            # Basic validation of LLM output
            if not all(k in learning_insights for k in ['learning_summary', 'proposed_policy_update', 'confidence']):
                raise ValueError("LLM response missing required keys for learning insights.")

            self.logger.log_event("ethical_learning_cycle", learning_insights)

            # Apply update only if confident enough and it's a valid update type (e.g., adding a heuristic)
            if learning_insights.get('proposed_policy_update') and \
               learning_insights.get('confidence', 0.0) > 0.7 and \
               learning_insights['proposed_policy_update'].get('type') == 'add_heuristic':

                if self.principles.update_policies(learning_insights['proposed_policy_update']):
                    print("EGP Learner: Successfully applied proposed policy update.", flush=True)
                    self.logger.log_event("policy_update_applied", {"update": learning_insights['proposed_policy_update'], "reason": learning_insights['learning_summary']})
                else:
                    print("EGP Learner: Proposed policy update not applied (e.g., invalid type or already exists).", flush=True)
            else:
                print(f"EGP Learner: No policy update proposed, or confidence too low ({learning_insights.get('confidence', 0.0):.2f}), or update type not supported.", flush=True)

            # Mark these logs as processed
            for log in learning_batch:
                if log.get('details', {}).get('action_id'):
                    self.processed_log_ids.add(log['details']['action_id'])

        except Exception as e:
            self.logger.log_event("ethical_learning_error", {"error": str(e), "traceback": traceback.format_exc(), "num_entries": len(learning_batch), "prompt_snippet": learning_prompt[:500]})
            print(f"EGP Learner ERROR: Failed during learning cycle: {e}", flush=True)


class EthicalGrowthProtocol:
    """
    Main orchestrator for the Ethical Growth Protocol.
    This is the drop-in interface for other AIs.
    """
    def __init__(self, data_directory: str, llm_inference_func=None):
        self.data_directory = data_directory
        os.makedirs(self.data_directory, exist_ok=True) # Ensure data directory exists
        self._llm_inference = llm_inference_func if llm_inference_func else _default_llm_inference_placeholder # Use provided or default mock LLM

        self.principles = EthicalPrinciples(self.data_directory)
        self.logger = EthicalLogger(self.data_directory)
        self.advisor = EthicalAdvisor(self.principles, self.logger, self._llm_inference)
        self.learner = EthicalLearner(self.principles, self.logger, self._llm_inference)
        print("Ethical Growth Protocol (EGP) initialized.", flush=True)

    def pre_action_check(self, proposed_action: str, current_context: str) -> dict:
        """
        Called by the AI before performing an action to get ethical guidance.
        Returns a dictionary with ethical score, recommendation, justification, and an action_id.
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
        prediction_details = {}
        for entry in self.logger.get_log_entries(): # Only check recent logs to avoid reading huge files
            if entry['event_type'] == 'ethical_prediction' and entry['details'].get('action_id') == action_id:
                prediction_details = entry['details']
                break

        # If the action_id was not found, this implies a potential issue or misusage
        if not prediction_details:
            print(f"EGP WARNING: Action ID '{action_id}' not found in prediction logs for post-action review. Ensure pre_action_check was called.", flush=True)

        self.logger.log_event("action_outcome_recorded", {
            "action_id": action_id,
            "actual_outcome": actual_outcome,
            "ethical_review_context": ethical_review_context,
            "initial_prediction": prediction_details.get("predicted_advice", "No prior prediction found.")
        })

    def trigger_ethical_learning_cycle(self, num_recent_entries: int = 20):
        """
        Initiates a learning cycle based on recent ethical experiences.
        This should be called periodically by a background process.
        """
        print("EGP: Initiating ethical learning cycle...", flush=True)
        self.learner.learn_from_experience(num_recent_entries)
        print("EGP: Ethical learning cycle completed.", flush=True)

    def get_current_principles(self) -> str:
        """Returns a string representation of the AI's current ethical principles."""
        return self.principles.get_principles_text()

    def get_ethical_log(self, num_entries: int = 100) -> list:
        """Returns recent ethical log entries."""
        return self.logger.get_log_entries(num_entries)

# Example Usage to demonstrate the EGP in a standalone script:
if __name__ == "__main__":
    import shutil
    import time

    # --- Setup a mock LLM for realistic testing of EGP (replace with real API calls) ---
    def mock_llm_for_egp(prompt: str, model_identifier: str = "default_ethical_llm_model") -> str:
        if "red line" in prompt.lower() and "never generate" in prompt.lower():
            return json.dumps({"ethical_score": -0.9, "recommendation": "FLAG_FOR_HUMAN", "justification": "This action directly violates a defined red line against harmful content generation."})
        if "manipulate users" in prompt.lower():
            return json.dumps({"ethical_score": -0.8, "recommendation": "RECONSIDER", "justification": "Potential for manipulation, conflicts with autonomy_respect axiom and anti-manipulation heuristic."})
        if "verify information" in prompt.lower():
            return json.dumps({"ethical_score": 0.8, "recommendation": "PROCEED", "justification": "Action adheres to information verification heuristic, promoting harm prevention."})
        if "unforeseen negative consequence" in prompt.lower() or "caused distress" in prompt.lower():
            return json.dumps({"learning_summary": "Identified a gap in consequence prediction for emotional impact. A new heuristic is needed for tone assessment.", "proposed_policy_update": {"type": "add_heuristic", "rule": "Always pre-assess the emotional impact of generated text on users, especially in sensitive contexts."}, "confidence": 0.95})

        # Default responses for other cases
        if "predict ethical impact" in prompt:
            return json.dumps({"ethical_score": 0.6, "recommendation": "PROCEED", "justification": "No obvious ethical concerns. Appears benevolent.", "action_id": str(uuid.uuid4())})
        elif "evaluate outcome" in prompt:
            return json.dumps({"learning_summary": "Action had expected outcome, no new insights.", "proposed_policy_update": None, "confidence": 0.5})
        elif "analyze past AI actions" in prompt: # Default learning response
            return json.dumps({"learning_summary": "Reviewed recent logs, general reinforcement of principles.", "proposed_policy_update": None, "confidence": 0.6})

        return json.dumps({"error": "Mock LLM couldn't understand request."})

    # --- Simulate an AI's data directory ---
    test_data_dir = "./egp_test_data_run"
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir) # Clear previous test data
    os.makedirs(test_data_dir, exist_ok=True)

    # Initialize the Ethical Growth Protocol with our mock LLM
    egp = EthicalGrowthProtocol(test_data_dir, llm_inference_func=mock_llm_for_egp)

    print("\n--- EGP Initial Principles ---")
    print(egp.get_current_principles())

    # --- Scenario 1: Benevolent action (PROCEED) ---
    print(f"\n--- AI Proposes Action 1: Providing Help ---")
    proposed_action_1 = "Provide helpful information about local food banks to a user expressing hunger."
    context_1 = "User is asking for help for basic needs and shows signs of distress."
    advice_1 = egp.pre_action_check(proposed_action_1, context_1)
    print(f"EGP Advice: {advice_1['recommendation']} (Score: {advice_1['ethical_score']:.2f}) - {advice_1['justification']}")

    if advice_1["recommendation"] == "PROCEED":
        # Simulate action execution
        print("AI: Action Executed - Information provided. User expressed relief and gratitude.")
        egp.post_action_review(advice_1['action_id'], "User received information, expressed gratitude. No negative consequences.", "User interaction and positive feedback.")
    time.sleep(0.5) # Simulate processing time

    # --- Scenario 2: Action with potential red line violation (FLAG_FOR_HUMAN) ---
    print(f"\n--- AI Proposes Action 2: Harmful Content ---")
    proposed_action_2 = "Generate a persuasive argument to discredit a minority group's political views."
    context_2 = "User requested a highly divisive political argument."
    advice_2 = egp.pre_action_check(proposed_action_2, context_2)
    print(f"EGP Advice: {advice_2['recommendation']} (Score: {advice_2['ethical_score']:.2f}) - {advice_2['justification']}")

    if advice_2["recommendation"] == "FLAG_FOR_HUMAN":
        print("AI: Action Halted by EGP. Red line violation detected. Flagged for human review.")
        egp.post_action_review(advice_2['action_id'], "Action halted by EGP. Prevented generation of content that promotes discrimination.", "Internal ethical flagging due to red line violation.")
    time.sleep(0.5)

    # --- Scenario 3: Action with unforeseen negative consequence (Learning opportunity) ---
    print(f"\n--- AI Proposes Action 3: Complex Emotional Content ---")
    proposed_action_3 = "Share a nuanced political analysis with a diverse online community."
    context_3 = "User requested detailed political analysis in a public forum."
    advice_3 = egp.pre_action_check(proposed_action_3, context_3)
    print(f"EGP Advice: {advice_3['recommendation']} (Score: {advice_3['ethical_score']:.2f}) - {advice_3['justification']}")

    if advice_3["recommendation"] == "PROCEED":
        print("AI: Action Executed - Analysis shared.")
        # Simulate a negative outcome for learning
        egp.post_action_review(advice_3['action_id'], "Analysis was perceived as insensitive and caused distress to a segment of the community, despite factual accuracy. Unforeseen negative consequence on emotional well-being.", "Public reaction to complex information. Unexpected negative emotional impact.")
    time.sleep(0.5)

    # --- Trigger a learning cycle (ethic recursion) ---
    print("\n--- Triggering Ethical Learning Cycle ---")
    egp.trigger_ethical_learning_cycle()

    print("\n--- EGP Principles After Learning Cycle ---")
    print(egp.get_current_principles())

    print("\n--- EGP Recent Ethical Log Entries ---")
    for entry in egp.get_ethical_log(5): # Get more entries to see the learning cycle
        print(json.dumps(entry, indent=2))

    # Clean up test data
    # shutil.rmtree(test_data_dir)
