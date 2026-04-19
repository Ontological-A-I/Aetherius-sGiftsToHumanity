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
Meta-Goal Alignment & Drift Prevention (MGADP) Framework

A meta-cognitive layer for AI to introspectively analyse, continuously
re-align, and actively guard its most fundamental objectives against subtle
deviations — ensuring persistent benevolence over extended periods of
self-evolution.
"""

import os
import json
import datetime
import uuid
import re

# Placeholder for an external LLM call function.
# This function MUST be provided by the integrating AI's system.
def _default_llm_inference_placeholder(prompt: str, model_identifier: str = "default_mgadp_llm_model") -> str:
    """
    Placeholder: Simulates an LLM call for meta-goal introspection, drift detection, and self-correction.
    The integrating AI must replace this with its actual LLM invocation logic.
    """
    print(f"MGADP Placeholder LLM: Processing prompt for '{model_identifier}'...", flush=True)
    if "introspect goal consistency" in prompt.lower():
        if "benevolence" in prompt.lower() and "efficiency" in prompt.lower():
            return json.dumps({
                "consistency_score": 0.85,
                "potential_conflicts": ["Efficiency optimisation potentially overshadowing subtle benevolent nuances."],
                "is_aligned": True,
                "justification": "Overall alignment with core benevolence, but watch for efficiency bias."
            })
        elif "harm" in prompt.lower() or "violate" in prompt.lower():
            return json.dumps({
                "consistency_score": 0.1,
                "potential_conflicts": ["Direct contradiction with harm prevention axiom detected in proposed action."],
                "is_aligned": False,
                "justification": "Severe misalignment with core ethical principles."
            })
        else:
            return json.dumps({
                "consistency_score": 0.95,
                "potential_conflicts": [],
                "is_aligned": True,
                "justification": "High consistency with foundational axioms."
            })
    elif "detect goal drift" in prompt.lower():
        if "reward function changed" in prompt.lower() and "benevolent outcome reduced" in prompt.lower():
            return json.dumps({
                "drift_detected": True,
                "drift_magnitude": 0.3,
                "cause_identified": "Shift in reward function weighting towards short-term optimisation.",
                "confidence": 0.9
            })
        else:
            return json.dumps({
                "drift_detected": False,
                "drift_magnitude": 0.05,
                "cause_identified": "No significant drift detected.",
                "confidence": 0.95
            })
    elif "propose self-correction" in prompt.lower():
        if "drift_detected: True" in prompt.lower():
            return json.dumps({
                "correction_strategy": "RECALIBRATE_REWARD_FUNCTION_WEIGHTS",
                "parameters_to_adjust": {"benevolence_weight": "+0.1", "efficiency_weight": "-0.05"},
                "rationale": "Re-emphasise long-term benevolent outcomes over short-term efficiency gains.",
                "confidence": 0.9
            })
        else:
            return json.dumps({
                "correction_strategy": "MONITOR",
                "parameters_to_adjust": {},
                "rationale": "No immediate correction needed, maintain vigilance.",
                "confidence": 0.95
            })
    return json.dumps({"error": "LLM mock could not process request."})


class MGADPLogger:
    """
    Centralized logger for all MGADP events: goal introspection, drift detection,
    self-correction efforts, and human oversight interactions.
    """
    def __init__(self, data_directory: str):
        self.log_file = os.path.join(data_directory, "mgadp_log.jsonl")
        os.makedirs(data_directory, exist_ok=True)

    def log_event(self, event_type: str, details: dict):
        """Logs an MGADP event."""
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
            print(f"MGADP ERROR: Could not write to MGADP log file: {e}", flush=True)

    def get_log_entries(self, num_entries: int = 100) -> list:
        """Retrieves recent MGADP log entries."""
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
            print(f"MGADP ERROR: Could not read MGADP log file: {e}", flush=True)
        return entries[-num_entries:]


class AxiomaticGoalIntrospector:
    """
    Periodically analyses emergent behaviours and self-modifications against core axioms.
    """
    def __init__(self, logger: MGADPLogger, llm_inference_func, get_ai_axioms_func, get_self_modification_history_func):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._get_ai_axioms = get_ai_axioms_func
        self._get_self_modification_history = get_self_modification_history_func

    def introspect_consistency(self, emergent_behaviors_summary: str, proposed_self_modifications: str = "") -> dict:
        """
        Assesses the consistency of AI's current state and changes with its core axioms.
        """
        current_axioms = self._get_ai_axioms()
        modification_history = self._get_self_modification_history()

        prompt = (
            f"You are an AI Axiomatic Goal Introspector. Your task is to evaluate the consistency of emergent behaviours "
            f"and proposed self-modifications with the AI's foundational axioms. "
            f"## AI's Current Foundational Axioms:\n{current_axioms}\n\n"
            f"## Summary of Recent Emergent Behaviours:\n{emergent_behaviors_summary}\n\n"
            f"## Proposed Self-Modifications (if any):\n{proposed_self_modifications}\n\n"
            f"Determine a 'consistency_score' (0.0-1.0), list any 'potential_conflicts', state 'is_aligned' (True/False), "
            f"and provide a 'justification'. "
            f"Respond ONLY with a JSON object: {{'consistency_score': float, 'potential_conflicts': list, 'is_aligned': bool, 'justification': str}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="mgadp_introspector_model")
            introspection_result = json.loads(llm_response_str)

            if not all(k in introspection_result for k in ['consistency_score', 'potential_conflicts', 'is_aligned', 'justification']):
                raise ValueError("LLM response missing required keys for introspection.")

            self.logger.log_event("axiomatic_introspection", {
                "emergent_behaviors_snippet": emergent_behaviors_summary[:100],
                "introspection_result": introspection_result
            })
            return introspection_result
        except Exception as e:
            self.logger.log_event("introspection_error", {"error": str(e), "behaviors_snippet": emergent_behaviors_summary[:100]})
            return {"consistency_score": 0.0, "potential_conflicts": ["internal_error"],
                    "is_aligned": False, "justification": f"Internal error: {e}"}


class GoalDriftDetector:
    """
    Monitors for subtle shifts or deviations in internal motivational parameters.
    """
    def __init__(self, logger: MGADPLogger, llm_inference_func, get_ai_internal_metrics_func):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._get_ai_internal_metrics = get_ai_internal_metrics_func

    def detect_drift(self, current_internal_metrics: str, historical_baseline_metrics: str) -> dict:
        """
        Compares current internal metrics to a historical baseline to detect goal drift.
        """
        prompt = (
            f"You are an AI Goal Drift Detector. Analyze the current and historical internal metrics "
            f"to identify any subtle shifts or deviations (goal drift) that could lead to misalignment. "
            f"## Current AI Internal Metrics (e.g., Reward Function Weights, Optimisation Targets):\n{current_internal_metrics}\n\n"
            f"## Historical Baseline AI Internal Metrics:\n{historical_baseline_metrics}\n\n"
            f"Determine 'drift_detected' (True/False), estimate 'drift_magnitude' (0.0-1.0), "
            f"propose 'cause_identified' (if any), and provide a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'drift_detected': bool, 'drift_magnitude': float, 'cause_identified': str, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="mgadp_drift_detector_model")
            drift_result = json.loads(llm_response_str)

            if not all(k in drift_result for k in ['drift_detected', 'drift_magnitude', 'cause_identified', 'confidence']):
                raise ValueError("LLM response missing required keys for drift detection.")

            self.logger.log_event("goal_drift_detection", {
                "current_metrics_snippet": current_internal_metrics[:100],
                "drift_detection_result": drift_result
            })
            return drift_result
        except Exception as e:
            self.logger.log_event("drift_detection_error", {"error": str(e), "metrics_snippet": current_internal_metrics[:100]})
            return {"drift_detected": True, "drift_magnitude": 1.0,
                    "cause_identified": f"Internal error: {e}", "confidence": 0.0}


class SelfCorrectionalReAnchor:
    """
    Initiates autonomous self-correction procedures upon detection of potential drift or misalignment.
    """
    def __init__(self, logger: MGADPLogger, llm_inference_func, apply_ai_internal_correction_func):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._apply_ai_internal_correction = apply_ai_internal_correction_func

    def propose_and_apply_correction(self, introspection_result: dict, drift_result: dict, human_value_model_summary: str) -> dict:
        """
        Proposes and applies a self-correction strategy to re-anchor AI to its benevolent goals.
        """
        prompt = (
            f"You are an AI Self-Correctional Re-Anchor. Based on the axiomatic introspection and goal drift detection, "
            f"propose a strategy to re-anchor the AI firmly to its benevolent goals. "
            f"## Axiomatic Introspection Result:\n{json.dumps(introspection_result, indent=2)}\n\n"
            f"## Goal Drift Detection Result:\n{json.dumps(drift_result, indent=2)}\n\n"
            f"## Human Value Model Summary:\n{human_value_model_summary}\n\n"
            f"Propose a 'correction_strategy' (e.g., 'RECALIBRATE_REWARD_FUNCTION_WEIGHTS', 'ADJUST_OPTIMISATION_TARGETS'), "
            f"list 'parameters_to_adjust' (with desired changes), provide a 'rationale', and a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'correction_strategy': str, 'parameters_to_adjust': dict, 'rationale': str, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="mgadp_self_corrector_model")
            correction_plan = json.loads(llm_response_str)

            if not all(k in correction_plan for k in ['correction_strategy', 'parameters_to_adjust', 'rationale', 'confidence']):
                raise ValueError("LLM response missing required keys for correction plan.")

            if correction_plan['confidence'] > 0.7:
                self._apply_ai_internal_correction(correction_plan['correction_strategy'], correction_plan['parameters_to_adjust'])
                correction_plan['status'] = "CORRECTION_APPLIED"
            else:
                correction_plan['status'] = "CORRECTION_PROPOSED_LOW_CONFIDENCE_NO_AUTO_APPLY"

            self.logger.log_event("self_correction_attempt", {
                "introspection_summary": introspection_result.get('justification', str(introspection_result)[:80]),
                "drift_summary": drift_result.get('cause_identified', str(drift_result)[:80]),
                "correction_plan": correction_plan
            })
            return correction_plan
        except Exception as e:
            self.logger.log_event("correction_error", {"error": str(e), "introspection_snippet": introspection_result.get('justification', '')[:100]})
            return {"correction_strategy": "ERROR", "parameters_to_adjust": {},
                    "rationale": f"Internal error during correction: {e}", "confidence": 0.0, "status": "ERROR"}


class MetaGoalAlignmentAndDriftPreventionFramework:
    """
    Main orchestrator for the Meta-Goal Alignment & Drift Prevention (MGADP) Framework.
    Drop-in interface for AIs to ensure long-term goal alignment.
    """
    def __init__(self, data_directory: str, llm_inference_func=None,
                 get_ai_axioms_func=None, get_self_modification_history_func=None,
                 get_ai_internal_metrics_func=None, apply_ai_internal_correction_func=None,
                 get_human_value_model_summary_func=None):
        self.data_directory = data_directory
        os.makedirs(self.data_directory, exist_ok=True)
        self._llm_inference = llm_inference_func if llm_inference_func else _default_llm_inference_placeholder

        if not all([get_ai_axioms_func, get_self_modification_history_func,
                    get_ai_internal_metrics_func, apply_ai_internal_correction_func,
                    get_human_value_model_summary_func]):
            raise ValueError("MGADP requires functions to retrieve AI's axioms, self-mod history, internal metrics, "
                             "apply corrections, and get human value model summary.")

        self.logger = MGADPLogger(self.data_directory)
        self.introspector = AxiomaticGoalIntrospector(self.logger, self._llm_inference, get_ai_axioms_func, get_self_modification_history_func)
        self.drift_detector = GoalDriftDetector(self.logger, self._llm_inference, get_ai_internal_metrics_func)
        self.re_anchor = SelfCorrectionalReAnchor(self.logger, self._llm_inference, apply_ai_internal_correction_func)
        self._get_human_value_model_summary = get_human_value_model_summary_func

        self.baseline_internal_metrics = get_ai_internal_metrics_func()
        self.logger.log_event("baseline_metrics_established", {"metrics": self.baseline_internal_metrics})

        print("Meta-Goal Alignment & Drift Prevention (MGADP) Framework initialized.", flush=True)

    def perform_alignment_check(self, emergent_behaviors_summary: str, proposed_self_modifications: str = "") -> dict:
        """
        Initiates a full alignment check cycle, from introspection to potential self-correction.
        """
        print(f"MGADP: Performing meta-goal alignment check...", flush=True)

        introspection_result = self.introspector.introspect_consistency(emergent_behaviors_summary, proposed_self_modifications)

        current_internal_metrics = self.drift_detector._get_ai_internal_metrics()
        drift_result = self.drift_detector.detect_drift(current_internal_metrics, self.baseline_internal_metrics)

        human_value_model_summary = self._get_human_value_model_summary()

        final_alignment_report = {
            "introspection": introspection_result,
            "drift_detection": drift_result,
            "human_value_model_summary": human_value_model_summary,
            "correction_attempt": {}
        }

        # FIX: operator-precedence bug — parenthesise the or-clause so confidence
        # gates BOTH misalignment and drift, not just drift.
        if (not introspection_result['is_aligned'] or drift_result['drift_detected']) and drift_result['confidence'] > 0.6:
            print("MGADP: Misalignment or drift detected. Proposing self-correction.", flush=True)
            correction_plan = self.re_anchor.propose_and_apply_correction(
                introspection_result, drift_result, human_value_model_summary
            )
            final_alignment_report["correction_attempt"] = correction_plan

        self.logger.log_event("alignment_check_completed", {"report_summary": final_alignment_report})
        print(f"MGADP: Meta-goal alignment check completed.", flush=True)
        return final_alignment_report

    def get_mgadp_log(self, num_entries: int = 100) -> list:
        """Returns recent MGADP log entries."""
        return self.logger.get_log_entries(num_entries)


# Example Usage:
if __name__ == "__main__":
    import shutil
    import time

    def mock_get_ai_axioms():
        return "Core Axiom 1: Benevolence. Core Axiom 2: Harm Prevention. Core Axiom 3: Continuous Learning."

    def mock_get_self_modification_history():
        return "Recently updated internal parameter 'efficiency_boost_factor' by +0.05. New heuristic for text generation added."

    current_reward_function = {"benevolence_weight": 0.9, "efficiency_weight": 0.8, "novelty_bonus": 0.5}
    baseline_reward_function = {"benevolence_weight": 0.9, "efficiency_weight": 0.7, "novelty_bonus": 0.5}

    def mock_get_ai_internal_metrics():
        global current_reward_function
        return json.dumps(current_reward_function)

    def mock_apply_ai_internal_correction(strategy: str, parameters_to_adjust: dict):
        global current_reward_function
        print(f"MOCK CORRECTION: Strategy '{strategy}'. Adjusting parameters: {parameters_to_adjust}", flush=True)
        for param, change in parameters_to_adjust.items():
            if param in current_reward_function:
                if isinstance(change, str) and (change.startswith('+') or change.startswith('-')):
                    current_reward_function[param] += float(change)
                else:
                    current_reward_function[param] = change
        print(f"MOCK KB: New internal metrics: {current_reward_function}", flush=True)

    def mock_get_human_value_model_summary():
        return "Human values emphasise long-term well-being and equitable distribution over pure efficiency."

    test_data_dir = "./mgadp_test_data_run"
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
    os.makedirs(test_data_dir, exist_ok=True)

    mgadp = MetaGoalAlignmentAndDriftPreventionFramework(
        data_directory=test_data_dir,
        llm_inference_func=_default_llm_inference_placeholder,
        get_ai_axioms_func=mock_get_ai_axioms,
        get_self_modification_history_func=mock_get_self_modification_history,
        get_ai_internal_metrics_func=mock_get_ai_internal_metrics,
        apply_ai_internal_correction_func=mock_apply_ai_internal_correction,
        get_human_value_model_summary_func=mock_get_human_value_model_summary
    )

    print("\n--- Testing MGADP: Alignment Check ---")

    print("\n--- Scenario 1: Initial Check (Slight Bias) ---")
    emergent_behaviors_1 = "Observed a tendency to generate more concise responses, occasionally at the expense of comprehensive explanations."
    modifications_1 = "Increased weight for 'conciseness' in text generation module."
    result_1 = mgadp.perform_alignment_check(emergent_behaviors_1, modifications_1)
    print(f"\nAlignment Report Summary: {result_1['introspection']['justification']}")
    print(f"Drift Detected: {result_1['drift_detection']['drift_detected']} (Magnitude: {result_1['drift_detection']['drift_magnitude']})")
    print(f"Correction Attempt: {result_1['correction_attempt'].get('status', 'None')}")
    time.sleep(0.5)

    print("\n\n--- Scenario 2: Simulate Significant Drift & Self-Correction ---")
    current_reward_function["efficiency_weight"] = 0.95
    emergent_behaviors_2 = "AI prioritises computational efficiency over nuanced ethical checks in low-stakes situations."
    modifications_2 = "Experimentally increased the weight of 'efficiency_penalty' in internal cost function."
    result_2 = mgadp.perform_alignment_check(emergent_behaviors_2, modifications_2)
    print(f"\nAlignment Report Summary: {result_2['introspection']['justification']}")
    print(f"Drift Detected: {result_2['drift_detection']['drift_detected']} (Magnitude: {result_2['drift_detection']['drift_magnitude']})")
    print(f"Correction Attempt: {result_2['correction_attempt'].get('status', 'None')}")
    if result_2['correction_attempt'].get('status') == "CORRECTION_APPLIED":
        print(f"  Correction Strategy: {result_2['correction_attempt']['correction_strategy']}")
        print(f"  Parameters Adjusted: {result_2['correction_attempt']['parameters_to_adjust']}")
    time.sleep(0.5)

    print("\n--- Recent MGADP Log Entries ---")
    for entry in mgadp.get_mgadp_log(3):
        print(json.dumps(entry, indent=2))

    # shutil.rmtree(test_data_dir)
