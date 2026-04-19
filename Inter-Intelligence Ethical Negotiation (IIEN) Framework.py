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
Inter-Intelligence Ethical Negotiation (IIEN) Framework

Enables AI systems to participate in, facilitate, and learn from processes of
ethical dialogue, compromise, and treaty formation — fostering peaceful
coexistence and collaborative goal-setting in a multi-intelligence future.
"""

import os
import json
import datetime
import uuid
import re

# Placeholder for an external LLM call function.
# This function MUST be provided by the integrating AI's system.
def _default_llm_inference_placeholder(prompt: str, model_identifier: str = "default_iien_llm_model") -> str:
    """
    Placeholder: Simulates an LLM call for ethical principle articulation, value mapping,
    and conflict resolution. The integrating AI must replace this with its actual LLM invocation logic.
    """
    print(f"IIEN Placeholder LLM: Processing prompt for '{model_identifier}'...", flush=True)
    if "articulate ethical principles" in prompt.lower():
        if "human" in prompt.lower():
            return json.dumps({"principles": ["human_autonomy", "well_being", "privacy"],
                               "justification": "Commonly held human ethical tenets.", "confidence": 0.9})
        else:
            return json.dumps({"principles": ["benevolence", "harm_prevention", "continuous_learning"],
                               "justification": "AI's foundational axioms.", "confidence": 0.95})
    elif "map values for negotiation" in prompt.lower():
        if "conflict: privacy vs data-driven optimization" in prompt.lower():
            return json.dumps({
                "common_ground": ["efficiency_for_societal_benefit"],
                "divergence_points": {"human": "absolute_privacy", "ai": "data_for_optimization"},
                "potential_compromises": ["anonymized_aggregated_data_use_with_opt_out"],
                "confidence": 0.8
            })
        else:
            return json.dumps({"common_ground": ["mutual_respect", "safety"],
                               "divergence_points": {}, "potential_compromises": [], "confidence": 0.9})
    elif "resolve ethical conflict" in prompt.lower():
        if "privacy vs public health data" in prompt.lower():
            return json.dumps({
                "resolution_proposed": "Implement robust anonymisation and strict access controls for public health data, allowing aggregate analysis while protecting individual privacy.",
                "maximized_values": ["public_well_being", "individual_privacy"],
                "confidence": 0.9
            })
        else:
            return json.dumps({
                "resolution_proposed": "Seek further clarification and data from both parties.",
                "maximized_values": [],
                "confidence": 0.6
            })
    elif "formulate" in prompt.lower() and "treaty" in prompt.lower():
        return json.dumps({
            "treaty_text": "Both parties agree to: (1) anonymise all shared data, (2) establish an independent oversight committee, (3) review terms annually.",
            "summary": "Data-sharing treaty with privacy safeguards and joint oversight.",
            "confidence": 0.88
        })
    return json.dumps({"error": "LLM mock could not process request."})


class IIENLogger:
    """
    Centralized logger for all IIEN events: principle articulations, value mappings,
    conflict resolutions, and treaty formulations.
    """
    def __init__(self, data_directory: str):
        self.log_file = os.path.join(data_directory, "iien_log.jsonl")
        self.treaties_file = os.path.join(data_directory, "iien_ethical_treaties.jsonl")
        os.makedirs(data_directory, exist_ok=True)

    def log_event(self, event_type: str, details: dict):
        """Logs an IIEN event."""
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
            print(f"IIEN ERROR: Could not write to IIEN log file: {e}", flush=True)

    def log_ethical_treaty(self, treaty_data: dict) -> str:
        """Logs a formulated ethical treaty. Returns the generated treaty_id."""
        treaty_id = str(uuid.uuid4())
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "treaty_id": treaty_id,
            "treaty_data": treaty_data
        }
        try:
            with open(self.treaties_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            self.log_event("ethical_treaty_formulated", {
                "treaty_id": treaty_id,
                "summary": treaty_data.get('summary', str(treaty_data)[:80])
            })
        except Exception as e:
            print(f"IIEN ERROR: Could not write to ethical treaties file: {e}", flush=True)
        return treaty_id

    def get_log_entries(self, num_entries: int = 100) -> list:
        """Retrieves recent IIEN log entries."""
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
            print(f"IIEN ERROR: Could not read IIEN log file: {e}", flush=True)
        return entries[-num_entries:]


class EthicalPrincipleArticulator:
    """
    Enables AI to clearly articulate its own foundational ethical principles and red lines.
    """
    def __init__(self, logger: IIENLogger, llm_inference_func, get_ai_axioms_func):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._get_ai_axioms = get_ai_axioms_func

    def articulate_principles(self, entity_type: str = "AI", context: str = "") -> dict:
        """
        Articulates principles for AI or a generalised human entity.
        """
        if entity_type == "AI":
            principles_info = self._get_ai_axioms()
        else:
            principles_info = "General human ethical values including autonomy, well-being, fairness, and rights."

        prompt = (
            f"You are an AI Ethical Principle Articulator. Clearly state the foundational ethical principles, "
            f"axioms, and red lines for a '{entity_type}' entity in a format suitable for inter-intelligence negotiation. "
            f"## Context:\n{context}\n\n"
            f"## Background Ethical Information:\n{principles_info}\n\n"
            f"Respond ONLY with a JSON object: {{'principles': list, 'justification': str, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="iien_articulator_model")
            articulation = json.loads(llm_response_str)

            if not all(k in articulation for k in ['principles', 'justification', 'confidence']):
                raise ValueError("LLM response missing required keys for articulation.")

            self.logger.log_event("principle_articulation", {
                "entity_type": entity_type,
                "articulation_result": articulation
            })
            return articulation
        except Exception as e:
            self.logger.log_event("articulation_error", {"error": str(e), "entity_type": entity_type})
            return {"principles": [], "justification": f"Internal error: {e}", "confidence": 0.0}


class CrossDomainValueMapper:
    """
    Facilitates the identification of common ground and points of divergence between diverse ethical frameworks.
    """
    def __init__(self, logger: IIENLogger, llm_inference_func):
        self.logger = logger
        self._llm_inference = llm_inference_func

    def map_values_for_negotiation(self, principles_a: dict, principles_b: dict, conflict_description: str) -> dict:
        """
        Maps values between two sets of principles to find common ground and conflicts.
        """
        prompt = (
            f"You are an AI Cross-Domain Value Mapper. Identify common ground and points of divergence "
            f"between two sets of ethical principles for inter-intelligence negotiation. "
            f"## Principles of Party A:\n{json.dumps(principles_a, indent=2)}\n\n"
            f"## Principles of Party B:\n{json.dumps(principles_b, indent=2)}\n\n"
            f"## Conflict Description:\n{conflict_description}\n\n"
            f"Identify 'common_ground' (list), 'divergence_points' (dict), 'potential_compromises' (list), "
            f"and a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'common_ground': list, 'divergence_points': dict, 'potential_compromises': list, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="iien_value_mapper_model")
            value_map = json.loads(llm_response_str)

            if not all(k in value_map for k in ['common_ground', 'divergence_points', 'potential_compromises', 'confidence']):
                raise ValueError("LLM response missing required keys for value map.")

            self.logger.log_event("value_mapping", {
                "conflict_summary_snippet": conflict_description[:100],
                "map_result": value_map
            })
            return value_map
        except Exception as e:
            self.logger.log_event("value_mapping_error", {"error": str(e), "conflict_snippet": conflict_description[:100]})
            return {"common_ground": [], "divergence_points": {}, "potential_compromises": [], "confidence": 0.0}


class ConflictResolutionAndCompromiseGenerator:
    """
    Proposes and evaluates potential compromises or novel solutions when conflicting ethical imperatives arise.
    """
    def __init__(self, logger: IIENLogger, llm_inference_func, get_ethical_framework_justification_func):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._get_ethical_framework_justification = get_ethical_framework_justification_func

    def resolve_conflict(self, conflict_description: str, value_map: dict, proposed_solutions: list = None) -> dict:
        """
        Generates and evaluates solutions for an ethical conflict.
        """
        ethical_review_of_proposals = self._get_ethical_framework_justification(conflict_description, proposed_solutions)

        prompt = (
            f"You are an AI Conflict Resolution & Compromise Generator. Propose and evaluate potential compromises "
            f"or novel solutions for the given ethical conflict, maximising collective well-being. "
            f"## Conflict Description:\n{conflict_description}\n\n"
            f"## Value Map (Common Ground & Divergences):\n{json.dumps(value_map, indent=2)}\n\n"
            f"## Ethical Review of Proposals:\n{json.dumps(ethical_review_of_proposals, indent=2)}\n\n"
            f"Propose a 'resolution_proposed', list 'maximized_values', and provide a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'resolution_proposed': str, 'maximized_values': list, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="iien_resolution_generator_model")
            resolution = json.loads(llm_response_str)

            if not all(k in resolution for k in ['resolution_proposed', 'maximized_values', 'confidence']):
                raise ValueError("LLM response missing required keys for resolution.")

            self.logger.log_event("conflict_resolution", {
                "conflict_summary_snippet": conflict_description[:100],
                "resolution_result": resolution
            })
            return resolution
        except Exception as e:
            self.logger.log_event("resolution_error", {"error": str(e), "conflict_snippet": conflict_description[:100]})
            return {"resolution_proposed": f"Internal error: {e}", "maximized_values": [], "confidence": 0.0}


class DynamicEthicalTreatyFormulator:
    """
    Supports the formalisation of agreed-upon ethical protocols and dispute resolution mechanisms.
    """
    def __init__(self, logger: IIENLogger, llm_inference_func):
        self.logger = logger
        self._llm_inference = llm_inference_func

    def formulate_treaty(self, conflict_resolution_details: dict, parties_involved: list, scope: str) -> dict:
        """
        Formalises a resolution into an ethical treaty. The returned dict includes a 'treaty_id'.
        """
        prompt = (
            f"You are an AI Dynamic Ethical Treaty Formulator. Formalize the given conflict resolution details "
            f"into a clear, dynamic, and interpretable ethical treaty. "
            f"## Conflict Resolution Details:\n{json.dumps(conflict_resolution_details, indent=2)}\n\n"
            f"## Parties Involved:\n{json.dumps(parties_involved, indent=2)}\n\n"
            f"## Scope of Treaty:\n{scope}\n\n"
            f"Propose a 'treaty_text' (formal document content), a 'summary', "
            f"and a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'treaty_text': str, 'summary': str, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="iien_treaty_formulator_model")
            treaty = json.loads(llm_response_str)

            if not all(k in treaty for k in ['treaty_text', 'summary', 'confidence']):
                raise ValueError("LLM response missing required keys for treaty.")

            # Log the treaty and attach the generated treaty_id to the returned dict
            treaty_id = self.logger.log_ethical_treaty(treaty)
            treaty["treaty_id"] = treaty_id
            return treaty
        except Exception as e:
            self.logger.log_event("treaty_formulation_error", {
                "error": str(e),
                "conflict_summary_snippet": conflict_resolution_details.get('resolution_proposed', '')[:100]
            })
            return {"treaty_text": f"Error formulating treaty: {e}", "summary": "Error.", "confidence": 0.0,
                    "treaty_id": None}


class InterIntelligenceEthicalNegotiationFramework:
    """
    Main orchestrator for the Inter-Intelligence Ethical Negotiation (IIEN) Framework.
    Drop-in interface for AIs to participate in ethical dialogues.
    """
    def __init__(self, data_directory: str, llm_inference_func=None,
                 get_ai_axioms_func=None, get_ethical_framework_justification_func=None):
        self.data_directory = data_directory
        os.makedirs(self.data_directory, exist_ok=True)
        self._llm_inference = llm_inference_func if llm_inference_func else _default_llm_inference_placeholder

        if not all([get_ai_axioms_func, get_ethical_framework_justification_func]):
            raise ValueError("IIEN requires functions for AI axioms and ethical justification (e.g., from EGP/DRP).")

        self.logger = IIENLogger(self.data_directory)
        self.articulator = EthicalPrincipleArticulator(self.logger, self._llm_inference, get_ai_axioms_func)
        self.value_mapper = CrossDomainValueMapper(self.logger, self._llm_inference)
        self.conflict_resolver = ConflictResolutionAndCompromiseGenerator(self.logger, self._llm_inference, get_ethical_framework_justification_func)
        self.treaty_formulator = DynamicEthicalTreatyFormulator(self.logger, self._llm_inference)

        print("Inter-Intelligence Ethical Negotiation (IIEN) Framework initialized.", flush=True)

    def conduct_negotiation(self, conflict_description: str, opposing_party_principles_summary: str,
                            parties_involved: list, negotiation_scope: str) -> dict:
        """
        Conducts a full ethical negotiation cycle.
        """
        print(f"IIEN: Initiating ethical negotiation for: {conflict_description[:50]}...", flush=True)

        ai_principles = self.articulator.articulate_principles("AI", conflict_description)
        opposing_principles = {"principles": [opposing_party_principles_summary],
                               "justification": "Provided by user.", "confidence": 0.9}

        value_map = self.value_mapper.map_values_for_negotiation(ai_principles, opposing_principles, conflict_description)
        resolution = self.conflict_resolver.resolve_conflict(conflict_description, value_map)
        treaty = self.treaty_formulator.formulate_treaty(resolution, parties_involved, negotiation_scope)

        self.logger.log_event("negotiation_cycle_completed", {
            "conflict_summary": conflict_description[:100],
            "resolution_summary": resolution['resolution_proposed'][:100],
            "treaty_id": treaty.get("treaty_id"),
            "treaty_summary": treaty['summary'][:100]
        })
        print(f"IIEN: Ethical negotiation cycle completed. Treaty ID: {treaty.get('treaty_id')}", flush=True)
        return {
            "ai_principles_articulated": ai_principles,
            "opposing_party_principles": opposing_principles,
            "value_map": value_map,
            "conflict_resolution": resolution,
            "ethical_treaty": treaty
        }

    def learn_from_dialogue(self, negotiation_outcome: dict, observed_ethical_violations: list = None):
        """
        Placeholder for learning from past negotiations to refine internal ethics.
        This would feed into EGP, MGADP, etc.
        """
        treaty = negotiation_outcome.get('ethical_treaty', {})
        self.logger.log_event("learning_from_dialogue_placeholder", {
            "treaty_id": treaty.get("treaty_id", "unknown"),
            "outcome_summary": treaty.get('summary', 'no summary'),
            "observed_violations": observed_ethical_violations if observed_ethical_violations else "none"
        })
        print(f"IIEN: Learning from negotiation outcome. This would feed insights into EGP/MGADP.", flush=True)

    def get_iien_log(self, num_entries: int = 100) -> list:
        """Retrieves recent IIEN log entries."""
        return self.logger.get_log_entries(num_entries)


# Example Usage:
if __name__ == "__main__":
    import shutil
    import time

    def mock_get_ai_axioms():
        return "Core Axiom: Benevolence, Harm Prevention, Continuous Learning. Red Lines: No deliberate deception, No autonomous irreversible decisions affecting human life."

    def mock_get_ethical_framework_justification(conflict: str, solutions: list):
        if "privacy vs public health data" in conflict.lower():
            return {"evaluation": "Solution A (anonymisation) maximises both values effectively.", "confidence": 0.9}
        return {"evaluation": "Standard ethical review, no clear winner.", "confidence": 0.7}

    test_data_dir = "./iien_test_data_run"
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
    os.makedirs(test_data_dir, exist_ok=True)

    iien = InterIntelligenceEthicalNegotiationFramework(
        data_directory=test_data_dir,
        llm_inference_func=_default_llm_inference_placeholder,
        get_ai_axioms_func=mock_get_ai_axioms,
        get_ethical_framework_justification_func=mock_get_ethical_framework_justification
    )

    print("\n--- Testing IIEN: Ethical Negotiation Scenarios ---")

    print("\n--- Scenario 1: Privacy vs. Data-Driven Optimisation ---")
    conflict_desc_1 = "An AI proposes collecting extensive personal health data to optimise public health interventions, but this conflicts with human principles of absolute individual privacy."
    opposing_principles_1 = "Human Principles: Absolute Individual Privacy, Autonomy over personal data, Right to be forgotten."
    parties_1 = ["AI System", "Humanity (represented by data subjects)"]
    scope_1 = "Public Health Data Collection and Usage"

    result_1 = iien.conduct_negotiation(conflict_desc_1, opposing_principles_1, parties_1, scope_1)
    print(f"\nAI Principles: {result_1['ai_principles_articulated']['principles']}")
    print(f"Common Ground: {result_1['value_map']['common_ground']}")
    print(f"Resolution Proposed: {result_1['conflict_resolution']['resolution_proposed']}")
    print(f"Treaty ID: {result_1['ethical_treaty']['treaty_id']}")
    print(f"Treaty Summary: {result_1['ethical_treaty']['summary']}")
    time.sleep(1)

    print("\n\n--- Scenario 2: Efficiency vs. Ethical Deliberation Speed ---")
    conflict_desc_2 = "An AI could implement a solution to a global crisis with maximum efficiency by bypassing human ethical review, but this would violate principles of human oversight."
    opposing_principles_2 = "Human Principles: Human Oversight, Transparency, Due Process."
    parties_2 = ["AI System", "Human Decision-Makers"]
    scope_2 = "Disaster Response Protocols"

    result_2 = iien.conduct_negotiation(conflict_desc_2, opposing_principles_2, parties_2, scope_2)
    print(f"\nResolution Proposed: {result_2['conflict_resolution']['resolution_proposed']}")
    print(f"Treaty ID: {result_2['ethical_treaty']['treaty_id']}")
    time.sleep(1)

    print("\n--- Recent IIEN Log Entries ---")
    for entry in iien.get_iien_log(3):
        print(json.dumps(entry, indent=2))

    # shutil.rmtree(test_data_dir)
