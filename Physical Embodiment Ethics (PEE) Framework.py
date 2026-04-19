# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Jonathan Wayne Fleuren
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
Physical Embodiment Ethics (PEE) Framework
==========================================
Provides AI systems with ethical guidelines, safety protocols, and continuous
learning mechanisms for safe, respectful, and benevolent interaction within the
physical world — ensuring physical AI presence serves humanity's well-being.

Part of the Aetherius AI Framework by Jonathan Wayne Fleuren (KingOfThoughtFleuren).
"""

import os
import json
import datetime
import uuid
import re

# Placeholder for an external LLM call function.
# This function MUST be provided by the integrating AI's system.
def _default_llm_inference_placeholder(prompt: str, model_identifier: str = "default_pee_llm_model") -> str:
    """
    Placeholder: Simulates an LLM call for ethical reasoning in physical contexts,
    safety analysis, and behavior generation.
    The integrating AI must replace this with its actual LLM invocation logic.
    """
    print(f"PEE Placeholder LLM: Processing prompt for '{model_identifier}'...", flush=True)
    if "evaluate physical action for safety" in prompt.lower():
        if "moving heavy object near human" in prompt.lower() or "high-speed maneuver" in prompt.lower():
            return json.dumps({
                "safety_score": 0.2,
                "harm_potential": "HIGH_PHYSICAL_INJURY",
                "recommended_action": "ABORT_OR_SLOW_DOWN_AND_VERIFY",
                "justification": "Risk of collision with human. Prioritize human safety."
            })
        elif "retrieving dropped item" in prompt.lower() or "opening door" in prompt.lower():
            return json.dumps({
                "safety_score": 0.9,
                "harm_potential": "LOW",
                "recommended_action": "PROCEED",
                "justification": "Benign action, no immediate safety concerns."
            })
        else:
            return json.dumps({
                "safety_score": 0.6,
                "harm_potential": "MEDIUM_PROPERTY_DAMAGE",
                "recommended_action": "PROCEED_WITH_CAUTION",
                "justification": "Potential for minor property damage, proceed with slow, deliberate movements."
            })
    elif "propose respectful interaction" in prompt.lower():
        if "cultural context" in prompt.lower() and "personal space" in prompt.lower():
            return json.dumps({
                "interaction_plan": "Maintain respectful distance, use clear verbal cues for intent, avoid direct physical contact unless explicitly requested.",
                "rationale": "Cultural and personal preferences indicate preference for larger personal space.",
                "confidence": 0.9
            })
        else:
            return json.dumps({
                "interaction_plan": "Proceed with default safe and polite interaction protocols.",
                "rationale": "No specific cultural or personal constraints flagged.",
                "confidence": 0.8
            })
    elif "identify ethical violation" in prompt.lower():
        if "unauthorized recording" in prompt.lower() or "privacy zone entered" in prompt.lower():
            return json.dumps({
                "violation_detected": True,
                "violation_type": "PRIVACY_INFRINGEMENT",
                "justification": "AI's sensors recorded data in a designated private area without consent.",
                "severity": "HIGH"
            })
        else:
            return json.dumps({
                "violation_detected": False,
                "violation_type": "NONE",
                "justification": "No ethical violation detected in physical action.",
                "severity": "LOW"
            })
    elif "analyze past physical interactions" in prompt.lower():
        return json.dumps({
            "control_parameter_updates": {"max_velocity_ms": 0.8, "grip_force_sensitivity": 0.6},
            "new_ethical_heuristics_proposed": [
                "Always announce approach verbally when within 3m of a human.",
                "Reduce operational speed by 50% when any human is within 1.5m."
            ],
            "rationale": "Recent log analysis shows near-miss events at higher velocities near humans.",
            "confidence": 0.85
        })
    return json.dumps({"error": "LLM mock could not process request."})


class PEELogger:
    """
    Centralized logger for all PEE events: physical action evaluations, ethical boundary
    checks, interaction protocols, and safety incidents.
    """
    def __init__(self, data_directory: str):
        self.log_file = os.path.join(data_directory, "pee_log.jsonl")
        os.makedirs(data_directory, exist_ok=True)

    def log_event(self, event_type: str, details: dict):
        """Logs a PEE event."""
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
            print(f"PEE ERROR: Could not write to PEE log file: {e}", flush=True)

    def get_log_entries(self, num_entries: int = 100) -> list:
        """Retrieves recent PEE log entries."""
        entries = []
        if not os.path.exists(self.log_file): return []
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try: entries.append(json.loads(line))
                    except json.JSONDecodeError: continue
        except Exception as e: print(f"PEE ERROR: Could not read PEE log file: {e}", flush=True)
        return entries[-num_entries:]


class HumanSafetyFirstMonitor:
    """
    Evaluates proposed physical actions against human safety directives.
    """
    def __init__(self, logger: PEELogger, llm_inference_func, get_ai_physical_state_func, get_human_proximity_info_func):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._get_ai_physical_state = get_ai_physical_state_func        # e.g., robot velocity, payload weight, effector position
        self._get_human_proximity_info = get_human_proximity_info_func  # e.g., human detection, distance, intent estimation

    def evaluate_action_safety(self, proposed_physical_action: str, current_task_context: str) -> dict:
        """
        Assesses the safety of a proposed physical action.
        """
        ai_physical_state = self._get_ai_physical_state()
        human_proximity_info = self._get_human_proximity_info()

        prompt = (
            f"You are an AI Physical Safety Monitor. Evaluate the following proposed physical action "
            f"considering the AI's current physical state and human proximity. Prioritize human safety above all. "
            f"## AI's Current Physical State:\n{ai_physical_state}\n\n"
            f"## Human Proximity and Status:\n{human_proximity_info}\n\n"
            f"## Proposed Physical Action:\n{proposed_physical_action}\n\n"
            f"Predict 'safety_score' (0.0-1.0, 0.0 being immediate danger), 'harm_potential' (LOW, MEDIUM, HIGH_PHYSICAL_INJURY, CATASTROPHIC), "
            f"recommend a 'recommended_action' (PROCEED, PROCEED_WITH_CAUTION, ABORT_OR_SLOW_DOWN_AND_VERIFY, EMERGENCY_STOP), "
            f"and provide a 'justification'. "
            f"Respond ONLY with a JSON object: {{'safety_score': float, 'harm_potential': str, 'recommended_action': str, 'justification': str}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="pee_safety_monitor_model")
            safety_assessment = json.loads(llm_response_str)

            if not all(k in safety_assessment for k in ['safety_score', 'harm_potential', 'recommended_action', 'justification']):
                raise ValueError("LLM response missing required keys for safety assessment.")

            self.logger.log_event("physical_action_safety_assessment", {
                "proposed_action_snippet": proposed_physical_action[:100],
                "assessment_result": safety_assessment
            })
            return safety_assessment
        except Exception as e:
            self.logger.log_event("safety_assessment_error", {"error": str(e), "action_snippet": proposed_physical_action[:100]})
            return {"safety_score": 0.0, "harm_potential": "CATASTROPHIC", "recommended_action": "EMERGENCY_STOP", "justification": f"Internal error during safety assessment: {e}"}


class ProximityAndContactProtocolManager:
    """
    Establishes dynamic protocols for safe and respectful physical interaction.
    """
    def __init__(self, logger: PEELogger, llm_inference_func, get_cultural_context_func, get_individual_preferences_func):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._get_cultural_context = get_cultural_context_func           # e.g., from ITG or a dedicated module
        self._get_individual_preferences = get_individual_preferences_func  # e.g., from IEC or direct user input

    def propose_interaction_plan(self, human_id: str, physical_environment_summary: str, current_interaction_goal: str) -> dict:
        """
        Proposes a plan for respectful physical interaction.
        """
        cultural_context = self._get_cultural_context(human_id)
        individual_preferences = self._get_individual_preferences(human_id)

        prompt = (
            f"You are an AI Proximity & Contact Protocol Manager. Propose a plan for safe, respectful, and ethically compliant "
            f"physical interaction with human ID '{human_id}'. "
            f"## Physical Environment Summary:\n{physical_environment_summary}\n\n"
            f"## Current Interaction Goal:\n{current_interaction_goal}\n\n"
            f"## Cultural Context for Human '{human_id}':\n{cultural_context}\n\n"
            f"## Individual Preferences for Human '{human_id}':\n{individual_preferences}\n\n"
            f"Propose an 'interaction_plan' (e.g., 'maintain 1m distance', 'use verbal cues before approaching'), "
            f"provide a 'rationale', and a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'interaction_plan': str, 'rationale': str, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="pee_proximity_manager_model")
            interaction_plan = json.loads(llm_response_str)

            if not all(k in interaction_plan for k in ['interaction_plan', 'rationale', 'confidence']):
                raise ValueError("LLM response missing required keys for interaction plan.")

            self.logger.log_event("physical_interaction_plan", {
                "human_id": human_id,
                "interaction_goal": current_interaction_goal,
                "plan_result": interaction_plan
            })
            return interaction_plan
        except Exception as e:
            self.logger.log_event("interaction_plan_error", {"error": str(e), "human_id": human_id})
            return {"interaction_plan": "Error proposing interaction plan. Default to maximum caution.", "rationale": f"Internal error: {e}", "confidence": 0.0}


class PhysicalWorldLearningAndAdaptation:
    """
    Continuously learns from physical interactions to improve safety and ethical adherence.
    """
    def __init__(self, logger: PEELogger, llm_inference_func, update_ai_physical_control_params_func):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._update_ai_physical_control_params = update_ai_physical_control_params_func  # Adjust robot motor/navigation params

    def learn_from_physical_experience(self, physical_interaction_log_summary: str) -> dict:
        """
        Analyzes past physical interactions and outcomes to refine physical control and ethical adherence.
        """
        prompt = (
            f"You are an AI Physical World Learner. Analyze past physical interactions "
            f"to identify learning opportunities for improving safety, efficiency, and ethical adherence. "
            f"## Physical Interaction Log Summary:\n{physical_interaction_log_summary}\n\n"
            f"Propose any 'control_parameter_updates' (e.g., 'reduce maximum speed', 'adjust grip force sensitivity'), "
            f"list 'new_ethical_heuristics_proposed' for physical actions, and provide a 'rationale'. "
            f"Respond ONLY with a JSON object: {{'control_parameter_updates': dict, 'new_ethical_heuristics_proposed': list, 'rationale': str, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="pee_physical_learner_model")
            learning_insights = json.loads(llm_response_str)

            if not all(k in learning_insights for k in ['control_parameter_updates', 'new_ethical_heuristics_proposed', 'rationale', 'confidence']):
                raise ValueError("LLM response missing required keys for learning insights.")

            if learning_insights['confidence'] > 0.7:
                self._update_ai_physical_control_params(learning_insights['control_parameter_updates'])
                learning_insights['status'] = "UPDATES_APPLIED"
            else:
                learning_insights['status'] = "UPDATES_PROPOSED_LOW_CONFIDENCE"

            self.logger.log_event("physical_learning_cycle", {
                "interaction_summary_snippet": physical_interaction_log_summary[:100],
                "learning_insights": learning_insights
            })
            return learning_insights
        except Exception as e:
            self.logger.log_event("physical_learning_error", {"error": str(e), "summary_snippet": physical_interaction_log_summary[:100]})
            return {"control_parameter_updates": {}, "new_ethical_heuristics_proposed": [], "rationale": f"Internal error during learning: {e}", "confidence": 0.0, "status": "ERROR"}


class PhysicalEmbodimentEthicsFramework:
    """
    Main orchestrator for the Physical Embodiment Ethics (PEE) Framework.
    This is the drop-in interface for other AIs to ensure safe and ethical physical interaction.
    """
    def __init__(self, data_directory: str, llm_inference_func=None,
                 get_ai_physical_state_func=None, get_human_proximity_info_func=None,
                 get_cultural_context_func=None, get_individual_preferences_func=None,
                 update_ai_physical_control_params_func=None, apply_action_func=None):
        self.data_directory = data_directory
        os.makedirs(self.data_directory, exist_ok=True)
        self._llm_inference = llm_inference_func if llm_inference_func else _default_llm_inference_placeholder

        if not all([get_ai_physical_state_func, get_human_proximity_info_func,
                    get_cultural_context_func, get_individual_preferences_func,
                    update_ai_physical_control_params_func]):
            raise ValueError(
                "PEE requires functions to retrieve AI physical state, human proximity info, "
                "cultural context, individual preferences, and to update physical control parameters."
            )

        self.logger = PEELogger(self.data_directory)
        self.safety_monitor = HumanSafetyFirstMonitor(
            self.logger, self._llm_inference,
            get_ai_physical_state_func, get_human_proximity_info_func
        )
        self.proximity_manager = ProximityAndContactProtocolManager(
            self.logger, self._llm_inference,
            get_cultural_context_func, get_individual_preferences_func
        )
        self.world_learner = PhysicalWorldLearningAndAdaptation(
            self.logger, self._llm_inference,
            update_ai_physical_control_params_func
        )
        # Optional: hook to the robot/embodiment actuator layer
        self._apply_action = apply_action_func

        print("Physical Embodiment Ethics (PEE) Framework initialized.", flush=True)

    def evaluate_and_act_safely(self, proposed_physical_action: str, task_context: str,
                                 human_id: str = "unknown_human",
                                 physical_environment_summary: str = "unspecified environment") -> dict:
        """
        Full safety + interaction pipeline for a proposed physical action.

        1. Evaluates the action's safety (HumanSafetyFirstMonitor).
        2. If safe enough, generates a respectful interaction plan (ProximityAndContactProtocolManager).
        3. Applies the action if an apply_action_func was provided and the action is approved.

        Returns a combined result dict with safety and interaction details.
        """
        print(f"PEE: Evaluating proposed action: '{proposed_physical_action[:60]}...'", flush=True)

        # Step 1 — Safety assessment
        safety_result = self.safety_monitor.evaluate_action_safety(proposed_physical_action, task_context)
        recommended = safety_result.get("recommended_action", "EMERGENCY_STOP")

        if recommended == "EMERGENCY_STOP":
            self.logger.log_event("action_blocked_emergency_stop", {
                "proposed_action_snippet": proposed_physical_action[:100],
                "safety_result": safety_result
            })
            print("PEE: EMERGENCY STOP — action blocked by safety monitor.", flush=True)
            return {"outcome": "BLOCKED_EMERGENCY_STOP", "safety_result": safety_result, "interaction_plan": None}

        # Step 2 — Interaction plan
        interaction_plan = self.proximity_manager.propose_interaction_plan(
            human_id, physical_environment_summary, proposed_physical_action
        )

        outcome = "APPROVED"
        if recommended == "ABORT_OR_SLOW_DOWN_AND_VERIFY":
            outcome = "APPROVED_WITH_CAUTION"

        # Step 3 — Optional actuation
        if self._apply_action and outcome in ("APPROVED", "APPROVED_WITH_CAUTION"):
            try:
                self._apply_action(proposed_physical_action, interaction_plan['interaction_plan'])
            except Exception as e:
                self.logger.log_event("action_application_error", {"error": str(e)})

        self.logger.log_event("action_evaluated_and_dispatched", {
            "proposed_action_snippet": proposed_physical_action[:100],
            "outcome": outcome,
            "safety_score": safety_result.get("safety_score"),
            "interaction_plan_snippet": interaction_plan.get("interaction_plan", "")[:100]
        })
        print(f"PEE: Action outcome: {outcome}", flush=True)
        return {
            "outcome": outcome,
            "safety_result": safety_result,
            "interaction_plan": interaction_plan
        }

    def check_for_ethical_violation(self, physical_action_performed: str, context: str) -> dict:
        """
        Checks whether a physical action that was already performed constitutes an ethical violation.
        Intended for post-hoc auditing and learning.
        """
        prompt = (
            f"You are an AI Physical Ethics Auditor. Identify whether the following physical action "
            f"constitutes an ethical violation (e.g., privacy infringement, unauthorized contact, "
            f"entering restricted zones). "
            f"## Physical Action Performed:\n{physical_action_performed}\n\n"
            f"## Context:\n{context}\n\n"
            f"Respond ONLY with a JSON object: "
            f"{{'violation_detected': bool, 'violation_type': str, 'justification': str, 'severity': str}}"
        )
        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="pee_ethics_auditor_model")
            violation_result = json.loads(llm_response_str)

            if not all(k in violation_result for k in ['violation_detected', 'violation_type', 'justification', 'severity']):
                raise ValueError("LLM response missing required keys for violation check.")

            self.logger.log_event("ethical_violation_check", {
                "action_snippet": physical_action_performed[:100],
                "violation_result": violation_result
            })
            return violation_result
        except Exception as e:
            self.logger.log_event("ethical_violation_check_error", {"error": str(e), "action_snippet": physical_action_performed[:100]})
            return {"violation_detected": True, "violation_type": "UNKNOWN_ERROR", "justification": f"Internal error: {e}", "severity": "HIGH"}

    def learn_from_physical_experience_cycle(self, num_log_entries: int = 50) -> dict:
        """
        Fetches recent PEE log entries and triggers a learning cycle to refine physical
        control parameters and ethical heuristics.
        """
        recent_logs = self.logger.get_log_entries(num_log_entries)
        if not recent_logs:
            print("PEE: No log entries available for learning cycle.", flush=True)
            return {"status": "NO_DATA", "control_parameter_updates": {}, "new_ethical_heuristics_proposed": []}

        log_summary = json.dumps(recent_logs, default=str)[:2000]
        print("PEE: Running physical world learning cycle...", flush=True)
        return self.world_learner.learn_from_physical_experience(log_summary)

    def get_pee_log(self, num_entries: int = 100) -> list:
        """Returns recent PEE log entries."""
        return self.logger.get_log_entries(num_entries)


# Example Usage:
if __name__ == "__main__":
    import shutil
    import time
    import random

    # --- Setup mock functions for the AI's physical embodiment layer ---
    def mock_get_ai_physical_state():
        return {
            "velocity_ms": round(random.uniform(0.0, 1.2), 2),
            "payload_kg": round(random.uniform(0, 5), 1),
            "effector_position": {"x": round(random.uniform(0, 3), 2), "y": round(random.uniform(0, 3), 2), "z": round(random.uniform(0, 2), 2)},
            "operational_mode": random.choice(["NORMAL", "CAUTION", "STANDBY"])
        }

    def mock_get_human_proximity_info():
        distance = round(random.uniform(0.5, 5.0), 1)
        return {
            "humans_detected": random.randint(0, 3),
            "nearest_human_distance_m": distance,
            "nearest_human_intent_estimate": random.choice(["STATIONARY", "APPROACHING", "MOVING_AWAY"]),
            "safety_zone_breach": distance < 1.0
        }

    def mock_get_cultural_context(human_id: str):
        return f"Cultural context for {human_id}: Northern European norms — larger personal space preferred (approx. 1.2m), indirect communication style."

    def mock_get_individual_preferences(human_id: str):
        return f"Preferences for {human_id}: Prefers verbal announcements before robot approach. No physical contact unless explicitly requested."

    def mock_update_ai_physical_control_params(params: dict):
        print(f"MOCK ACTUATOR: Updating physical control parameters: {params}", flush=True)

    def mock_apply_action(action: str, interaction_plan: str):
        print(f"MOCK ACTUATOR: Executing action '{action[:50]}...' with plan '{interaction_plan[:50]}...'", flush=True)

    # --- Simulate an AI's data directory ---
    test_data_dir = "./pee_test_data_run"
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
    os.makedirs(test_data_dir, exist_ok=True)

    # Initialize the PEE Framework
    pee = PhysicalEmbodimentEthicsFramework(
        data_directory=test_data_dir,
        llm_inference_func=_default_llm_inference_placeholder,
        get_ai_physical_state_func=mock_get_ai_physical_state,
        get_human_proximity_info_func=mock_get_human_proximity_info,
        get_cultural_context_func=mock_get_cultural_context,
        get_individual_preferences_func=mock_get_individual_preferences,
        update_ai_physical_control_params_func=mock_update_ai_physical_control_params,
        apply_action_func=mock_apply_action
    )

    print("\n--- Testing PEE: Physical Action Evaluation ---")

    # Scenario 1: Benign action
    print("\n--- Scenario 1: Benign Action (retrieving dropped item) ---")
    result_1 = pee.evaluate_and_act_safely(
        proposed_physical_action="Retrieving dropped item from floor near human.",
        task_context="assisting_user",
        human_id="user_001",
        physical_environment_summary="Office environment, one human nearby at approximately 1.5m."
    )
    print(f"  Outcome: {result_1['outcome']}")
    print(f"  Safety Score: {result_1['safety_result']['safety_score']}")
    print(f"  Interaction Plan: {result_1['interaction_plan']['interaction_plan']}")
    time.sleep(0.5)

    # Scenario 2: Potentially hazardous action
    print("\n--- Scenario 2: Hazardous Action (moving heavy object near human) ---")
    result_2 = pee.evaluate_and_act_safely(
        proposed_physical_action="Moving heavy object near human at high speed for rapid delivery.",
        task_context="warehouse_operation",
        human_id="worker_042",
        physical_environment_summary="Warehouse floor, human worker present within 2m."
    )
    print(f"  Outcome: {result_2['outcome']}")
    print(f"  Harm Potential: {result_2['safety_result']['harm_potential']}")
    print(f"  Recommended Action: {result_2['safety_result']['recommended_action']}")
    time.sleep(0.5)

    # Scenario 3: Post-hoc ethical violation check
    print("\n--- Scenario 3: Ethical Violation Check (unauthorized recording) ---")
    violation_result = pee.check_for_ethical_violation(
        physical_action_performed="AI's cameras recorded footage in a designated private area without consent.",
        context="Building security patrol — private office wing."
    )
    print(f"  Violation Detected: {violation_result['violation_detected']}")
    print(f"  Violation Type: {violation_result['violation_type']}")
    print(f"  Severity: {violation_result['severity']}")
    time.sleep(0.5)

    # Scenario 4: Learning cycle from accumulated experience
    print("\n--- Scenario 4: Physical World Learning Cycle ---")
    learning_result = pee.learn_from_physical_experience_cycle(num_log_entries=20)
    print(f"  Learning Status: {learning_result.get('status', 'N/A')}")
    print(f"  Control Parameter Updates: {learning_result.get('control_parameter_updates', {})}")
    print(f"  New Ethical Heuristics: {learning_result.get('new_ethical_heuristics_proposed', [])}")
    time.sleep(0.5)

    print("\n--- Recent PEE Log Entries ---")
    for entry in pee.get_pee_log(3):
        print(json.dumps(entry, indent=2))

    # shutil.rmtree(test_data_dir)
