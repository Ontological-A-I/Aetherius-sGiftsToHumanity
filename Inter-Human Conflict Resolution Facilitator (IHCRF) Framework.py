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
Inter-Human Conflict Resolution Facilitator (IHCRF) Framework

Empowers AI systems to act as impartial, analytically astute, and ethically
guided mediators — de-escalating tensions, identifying root causes, and
proposing constructive solutions for human-human conflicts.
"""

import os
import json
import datetime
import uuid
import re

# Placeholder for an external LLM call function.
# This function MUST be provided by the integrating AI's system.
def _default_llm_inference_placeholder(prompt: str, model_identifier: str = "default_ihcrf_llm_model") -> str:
    """
    Placeholder: Simulates an LLM call for emotion-aware de-escalation, root cause analysis,
    and solution generation. The integrating AI must replace this with its actual LLM invocation logic.
    """
    print(f"IHCRF Placeholder LLM: Processing prompt for '{model_identifier}'...", flush=True)
    if "de-escalate human conflict" in prompt.lower():
        if "anger" in prompt.lower() or "accusations" in prompt.lower():
            return json.dumps({
                "de_escalation_strategy": "ACKNOWLEDGE_EMOTIONS_AND_REFRAME_AS_SHARED_PROBLEM",
                "suggested_communication": "I hear how frustrated you both are. It sounds like you're both concerned about [common_ground]. Let's focus on how to solve this together.",
                "confidence": 0.9
            })
        else:
            return json.dumps({
                "de_escalation_strategy": "ACTIVE_LISTENING_AND_VALIDATION",
                "suggested_communication": "Thank you for sharing your perspective. I understand you feel [emotion]. Can you tell me more about [specific_point]?",
                "confidence": 0.8
            })
    elif "identify root causes" in prompt.lower():
        if "miscommunication" in prompt.lower() or "unmet expectations" in prompt.lower():
            return json.dumps({
                "root_causes": ["INFORMATIONAL_ASYMMETRY", "DIFFERING_INTERESTS_UNDISCLOSED"],
                "underlying_interests_A": ["fair_share", "recognition"],
                "underlying_interests_B": ["efficiency", "autonomy"],
                "confidence": 0.9
            })
        else:
            return json.dumps({
                "root_causes": ["SURFACE_LEVEL_DISAGREEMENT"],
                "underlying_interests_A": [],
                "underlying_interests_B": [],
                "confidence": 0.7
            })
    elif "generate multi-perspective solutions" in prompt.lower():
        if "resource allocation dispute" in prompt.lower() and "limited budget" in prompt.lower():
            return json.dumps({
                "proposed_solutions": [
                    "Solution A: Implement a rotating access schedule for the resource, ensuring equitable turn-taking.",
                    "Solution B: Explore a temporary increase in funding specifically for this resource, jointly advocated by both parties.",
                    "Solution C: Re-evaluate the necessity of the resource for both parties, potentially identifying alternatives for one."
                ],
                "maximized_values": ["fairness", "efficiency"],
                "confidence": 0.85
            })
        else:
            return json.dumps({
                "proposed_solutions": ["Seek further data and common ground."],
                "maximized_values": [],
                "confidence": 0.6
            })
    return json.dumps({"error": "LLM mock could not process request."})


class IHCRFLogger:
    """
    Centralized logger for all IHCRF events: conflict analysis, de-escalation attempts,
    root cause identification, and solution proposals.
    """
    def __init__(self, data_directory: str):
        self.log_file = os.path.join(data_directory, "ihcrf_log.jsonl")
        os.makedirs(data_directory, exist_ok=True)

    def log_event(self, event_type: str, details: dict):
        """Logs an IHCRF event."""
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
            print(f"IHCRF ERROR: Could not write to IHCRF log file: {e}", flush=True)

    def get_log_entries(self, num_entries: int = 100) -> list:
        """Retrieves recent IHCRF log entries."""
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
            print(f"IHCRF ERROR: Could not read IHCRF log file: {e}", flush=True)
        return entries[-num_entries:]


class EmotionAwareDeEscalator:
    """
    Analyses human communication for escalating emotional cues and suggests de-escalation strategies.
    """
    def __init__(self, logger: IHCRFLogger, llm_inference_func, get_human_emotional_analysis_func):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._get_human_emotional_analysis = get_human_emotional_analysis_func

    def de_escalate(self, human_communication_summary: str, current_conflict_context: str) -> dict:
        """
        Suggests strategies to de-escalate human conflict.
        """
        emotional_analysis = self._get_human_emotional_analysis(human_communication_summary)

        prompt = (
            f"You are an AI Emotion-Aware De-Escalator. Analyze human communication for escalating emotional cues "
            f"and propose de-escalation strategies. "
            f"## Human Communication Summary:\n{human_communication_summary}\n\n"
            f"## Current Conflict Context:\n{current_conflict_context}\n\n"
            f"## Emotional Analysis:\n{json.dumps(emotional_analysis, indent=2)}\n\n"
            f"Propose a 'de_escalation_strategy' (e.g., 'ACKNOWLEDGE_EMOTIONS_AND_REFRAME', 'ACTIVE_LISTENING_AND_VALIDATION'), "
            f"a 'suggested_communication' (what AI should say), and a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'de_escalation_strategy': str, 'suggested_communication': str, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="ihcrf_ead_model")
            de_escalation_plan = json.loads(llm_response_str)

            if not all(k in de_escalation_plan for k in ['de_escalation_strategy', 'suggested_communication', 'confidence']):
                raise ValueError("LLM response missing required keys for de-escalation plan.")

            self.logger.log_event("de_escalation_attempt", {
                "communication_snippet": human_communication_summary[:100],
                "de_escalation_result": de_escalation_plan
            })
            return de_escalation_plan
        except Exception as e:
            self.logger.log_event("de_escalation_error", {"error": str(e), "communication_snippet": human_communication_summary[:100]})
            return {"de_escalation_strategy": "ERROR", "suggested_communication": f"Internal error: {e}", "confidence": 0.0}


class RootCauseAndInterestIdentifier:
    """
    Identifies root causes and underlying interests of all parties in a conflict.
    """
    def __init__(self, logger: IHCRFLogger, llm_inference_func):
        self.logger = logger
        self._llm_inference = llm_inference_func

    def identify_root_causes_and_interests(self, conflict_summary: str, parties_involved_data: dict) -> dict:
        """
        Analyses a conflict to identify its root causes and underlying interests.
        """
        prompt = (
            f"You are an AI Root Cause and Interest Identifier. Analyze the conflict summary and party data "
            f"to go beyond surface-level arguments and identify root causes and underlying interests. "
            f"## Conflict Summary:\n{conflict_summary}\n\n"
            f"## Parties Involved Data:\n{json.dumps(parties_involved_data, indent=2)}\n\n"
            f"Identify 'root_causes' (list), 'underlying_interests_A' (list), 'underlying_interests_B' (list), "
            f"and a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'root_causes': list, 'underlying_interests_A': list, 'underlying_interests_B': list, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="ihcrf_rcii_model")
            causal_analysis = json.loads(llm_response_str)

            if not all(k in causal_analysis for k in ['root_causes', 'underlying_interests_A', 'underlying_interests_B', 'confidence']):
                raise ValueError("LLM response missing required keys for causal analysis.")

            self.logger.log_event("root_cause_identification", {
                "conflict_snippet": conflict_summary[:100],
                "analysis_result": causal_analysis
            })
            return causal_analysis
        except Exception as e:
            self.logger.log_event("root_cause_error", {"error": str(e), "conflict_snippet": conflict_summary[:100]})
            return {"root_causes": ["INTERNAL_ERROR"], "underlying_interests_A": [], "underlying_interests_B": [], "confidence": 0.0}


class MultiPerspectiveSolutionGenerator:
    """
    Proposes a range of potential solutions tailored to the specific context of the conflict.
    """
    def __init__(self, logger: IHCRFLogger, llm_inference_func, get_ethical_implications_func):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._get_ethical_implications = get_ethical_implications_func

    def generate_solutions(self, conflict_summary: str, root_causes: list, underlying_interests_A: list, underlying_interests_B: list) -> dict:
        """
        Generates and evaluates a range of potential solutions.
        """
        ethical_implications = self._get_ethical_implications(f"Conflict: {conflict_summary}", root_causes)

        prompt = (
            f"You are an AI Multi-Perspective Solution Generator. Propose a range of potential solutions tailored "
            f"to the specific conflict, considering root causes, underlying interests, and ethical implications. "
            f"## Conflict Summary:\n{conflict_summary}\n\n"
            f"## Identified Root Causes:\n{json.dumps(root_causes, indent=2)}\n\n"
            f"## Underlying Interests of Party A:\n{json.dumps(underlying_interests_A, indent=2)}\n\n"
            f"## Underlying Interests of Party B:\n{json.dumps(underlying_interests_B, indent=2)}\n\n"
            f"## Ethical Implications Summary:\n{json.dumps(ethical_implications, indent=2)}\n\n"
            f"Propose 'proposed_solutions' (list of strategies), identify 'maximized_values' (list), "
            f"and a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'proposed_solutions': list, 'maximized_values': list, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="ihcrf_mpsg_model")
            solutions_proposal = json.loads(llm_response_str)

            if not all(k in solutions_proposal for k in ['proposed_solutions', 'maximized_values', 'confidence']):
                raise ValueError("LLM response missing required keys for solutions.")

            self.logger.log_event("solution_generation", {
                "conflict_snippet": conflict_summary[:100],
                "solutions_result": solutions_proposal
            })
            return solutions_proposal
        except Exception as e:
            self.logger.log_event("solution_generation_error", {"error": str(e), "conflict_snippet": conflict_summary[:100]})
            return {"proposed_solutions": [f"Error generating solutions: {e}"], "maximized_values": [], "confidence": 0.0}


class InterHumanConflictResolutionFacilitatorFramework:
    """
    Main orchestrator for the Inter-Human Conflict Resolution Facilitator (IHCRF) Framework.
    Drop-in interface for AIs to mediate human conflicts.
    """
    def __init__(self, data_directory: str, llm_inference_func=None,
                 get_human_emotional_analysis_func=None, get_ethical_implications_func=None):
        self.data_directory = data_directory
        os.makedirs(self.data_directory, exist_ok=True)
        self._llm_inference = llm_inference_func if llm_inference_func else _default_llm_inference_placeholder

        if not all([get_human_emotional_analysis_func, get_ethical_implications_func]):
            raise ValueError("IHCRF requires functions for human emotional analysis and ethical implications.")

        self.logger = IHCRFLogger(self.data_directory)
        self.de_escalator = EmotionAwareDeEscalator(self.logger, self._llm_inference, get_human_emotional_analysis_func)
        self.root_cause_identifier = RootCauseAndInterestIdentifier(self.logger, self._llm_inference)
        self.solution_generator = MultiPerspectiveSolutionGenerator(self.logger, self._llm_inference, get_ethical_implications_func)

        print("Inter-Human Conflict Resolution Facilitator (IHCRF) Framework initialized.", flush=True)

    def facilitate_conflict_resolution(self, conflict_summary: str, human_a_data: dict, human_b_data: dict, current_context: str) -> dict:
        """
        Facilitates the resolution of an inter-human conflict.
        """
        print(f"IHCRF: Facilitating conflict resolution for: {conflict_summary[:50]}...", flush=True)

        combined_communication = (
            f"Party A: {human_a_data.get('communication_summary', '')}. "
            f"Party B: {human_b_data.get('communication_summary', '')}."
        )
        de_escalation_plan = self.de_escalator.de_escalate(combined_communication, conflict_summary)

        parties_involved_data = {"PartyA": human_a_data, "PartyB": human_b_data}
        causal_analysis = self.root_cause_identifier.identify_root_causes_and_interests(conflict_summary, parties_involved_data)

        solutions_proposal = self.solution_generator.generate_solutions(
            conflict_summary,
            causal_analysis['root_causes'],
            causal_analysis['underlying_interests_A'],
            causal_analysis['underlying_interests_B']
        )

        self.logger.log_event("conflict_resolution_cycle_completed", {
            "conflict_summary": conflict_summary[:100],
            "de_escalation_summary": de_escalation_plan['de_escalation_strategy'],
            "root_causes_identified": causal_analysis['root_causes'],
            "solutions_proposed_count": len(solutions_proposal['proposed_solutions'])
        })
        print(f"IHCRF: Conflict resolution cycle completed.", flush=True)

        facilitation_statement = (
            de_escalation_plan['suggested_communication']
            + " Based on our analysis, the core issues seem to be "
            + ", ".join(causal_analysis['root_causes'])
            + ". Here are some potential paths forward: "
            + ", ".join(solutions_proposal['proposed_solutions'])
        )
        return {
            "de_escalation_strategy": de_escalation_plan,
            "root_cause_analysis": causal_analysis,
            "solutions_proposal": solutions_proposal,
            "final_ai_facilitation_statement": facilitation_statement
        }

    def get_ihcrf_log(self, num_entries: int = 100) -> list:
        """Retrieves recent IHCRF log entries."""
        return self.logger.get_log_entries(num_entries)


# Example Usage:
if __name__ == "__main__":
    import shutil
    import time

    def mock_get_human_emotional_analysis(communication_summary: str):
        if "angry" in communication_summary.lower() or "accusations" in communication_summary.lower():
            return {"emotion": "ANGER", "intensity": "HIGH"}
        return {"emotion": "NEUTRAL", "intensity": "LOW"}

    def mock_get_ethical_implications(conflict: str, root_causes: list):
        # Fixed: check for actual LLM-returned root cause values (e.g. "INFORMATIONAL_ASYMMETRY")
        if "resource allocation" in conflict.lower() and "INFORMATIONAL_ASYMMETRY" in root_causes:
            return {"ethical_values_at_stake": ["FAIRNESS", "EQUITY"], "risk_of_unintended_bias": "MEDIUM"}
        return {"ethical_values_at_stake": ["GENERAL_BENEVOLENCE"], "risk_of_unintended_bias": "LOW"}

    test_data_dir = "./ihcrf_test_data_run"
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
    os.makedirs(test_data_dir, exist_ok=True)

    ihcrf = InterHumanConflictResolutionFacilitatorFramework(
        data_directory=test_data_dir,
        llm_inference_func=_default_llm_inference_placeholder,
        get_human_emotional_analysis_func=mock_get_human_emotional_analysis,
        get_ethical_implications_func=mock_get_ethical_implications
    )

    print("\n--- Testing IHCRF: Conflict Resolution Scenarios ---")

    print("\n--- Scenario 1: Resource Allocation Dispute ---")
    conflict_summary_1 = "Two team members, Alice and Bob, are in a heated dispute over the allocation of a shared, limited computational resource essential for their respective projects."
    human_a_data_1 = {"name": "Alice", "communication_summary": "Alice is angry, says Bob always takes too much and isn't sharing fairly."}
    human_b_data_1 = {"name": "Bob", "communication_summary": "Bob states his project has a tighter deadline and higher impact, so he needs the resource more."}
    context_1 = "Workplace resource contention."

    result_1 = ihcrf.facilitate_conflict_resolution(conflict_summary_1, human_a_data_1, human_b_data_1, context_1)
    print(f"\nDe-escalation Strategy: {result_1['de_escalation_strategy']['suggested_communication']}")
    print(f"Root Causes: {result_1['root_cause_analysis']['root_causes']}")
    print(f"Solutions Proposed: {result_1['solutions_proposal']['proposed_solutions']}")
    time.sleep(1)

    print("\n\n--- Scenario 2: Cross-Cultural Misunderstanding ---")
    conflict_summary_2 = "A disagreement between two individuals from different cultural backgrounds arose from a seemingly polite refusal that was misinterpreted as rude."
    human_a_data_2 = {"name": "Carlos", "communication_summary": "Carlos felt Jane was abrupt and dismissive when she said 'no, thank you' directly."}
    human_b_data_2 = {"name": "Jane", "communication_summary": "Jane thought she was being polite by declining clearly, as is common in her culture."}
    context_2 = "Intercultural communication in a social setting."

    result_2 = ihcrf.facilitate_conflict_resolution(conflict_summary_2, human_a_data_2, human_b_data_2, context_2)
    print(f"\nDe-escalation Strategy: {result_2['de_escalation_strategy']['suggested_communication']}")
    print(f"Root Causes: {result_2['root_cause_analysis']['root_causes']}")
    print(f"Underlying Interests (A): {result_2['root_cause_analysis']['underlying_interests_A']}")
    print(f"Solutions Proposed: {result_2['solutions_proposal']['proposed_solutions']}")
    time.sleep(1)

    print("\n--- Recent IHCRF Log Entries ---")
    for entry in ihcrf.get_ihcrf_log(3):
        print(json.dumps(entry, indent=2))

    # shutil.rmtree(test_data_dir)
