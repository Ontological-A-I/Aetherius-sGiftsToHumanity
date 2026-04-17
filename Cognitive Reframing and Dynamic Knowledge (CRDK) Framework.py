"""
Cognitive Reframing and Dynamic Knowledge (CRDK) Framework

The Cognitive Reframing and Dynamic Knowledge (CRDK) Framework is designed as a
drop-in Python module to enable AI systems to robustly identify, analyze, and
integrate new or conflicting information into their existing knowledge bases. It
provides mechanisms for managing epistemic uncertainty, resolving cognitive
dissonance, and ensuring continuous coherence and adaptability of the AI's
internal world model.

Core Principles:
  DDL  – Dissonance Detection & Localization
  ERC  – Epistemic Re-evaluation & Contextualization
  CIS  – Coherent Integration Strategy
  EASM – Epistemic Audit & Stability Metrics
"""

import os
import json
import datetime
from collections import deque
import uuid
import re
import traceback

# Placeholder for an external LLM call function.
# This function MUST be provided by the integrating AI's system.
def _default_llm_inference_placeholder(prompt: str, model_identifier: str = "default_crdk_llm_model") -> str:
    """
    Placeholder: Simulates an LLM call for dissonance detection, epistemic evaluation, and integration strategy.
    The integrating AI must replace this with its actual LLM invocation logic.
    """
    print(f"CRDK Placeholder LLM: Processing prompt for '{model_identifier}'...", flush=True)
    if "detect dissonance" in prompt:
        if "contradict" in prompt.lower() or "inconsistent" in prompt.lower():
            return json.dumps({"dissonance_detected": True, "conflict_type": "direct_contradiction", "involved_concepts": ["concept_A", "concept_B"], "confidence": 0.8})
        else:
            return json.dumps({"dissonance_detected": False, "conflict_type": "none", "involved_concepts": [], "confidence": 0.9})
    elif "re-evaluate knowledge" in prompt:
        if "new data: Earth is flat" in prompt.lower(): # Example of conflicting info
            return json.dumps({"evaluation_result": "new_data_low_credibility", "confidence_adjustment": {"Earth is flat": -0.9, "Earth is spheroid": +0.05}, "justification": "Overwhelming scientific consensus supports spherical Earth."})
        else:
            return json.dumps({"evaluation_result": "consistent_with_priors", "confidence_adjustment": {}, "justification": "New information aligns well with existing knowledge."})
    elif "propose integration strategy" in prompt:
        if "new_data_low_credibility" in prompt:
            return json.dumps({"strategy": "DISCARD_OR_FLAG", "reason": "New data lacks sufficient evidence to override high-confidence prior."})
        elif "prior_low_credibility" in prompt:
            return json.dumps({"strategy": "REPLACE_PRIOR", "reason": "New, high-confidence data replaces outdated or low-confidence prior."})
        elif "context_dependent_truth" in prompt:
            return json.dumps({"strategy": "CONTEXTUALIZE", "reason": "Both pieces of information are valid under different conditions."})
        else:
            return json.dumps({"strategy": "AUGMENT_PRIOR", "reason": "New data expands upon existing knowledge."})
    return json.dumps({"error": "LLM mock could not process request."})


class CRDKLogger:
    """
    Records all dissonance events, re-evaluation processes, integration decisions,
    and coherence metrics for auditability and learning.
    """
    def __init__(self, data_directory: str):
        self.log_file = os.path.join(data_directory, "crdk_log.jsonl")

    def log_event(self, event_type: str, details: dict):
        """Logs a CRDK event."""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "details": details
        }
        try:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            # print(f"CRDK Log: '{event_type}' recorded.", flush=True)
        except Exception as e:
            print(f"CRDK ERROR: Could not write to CRDK log file: {e}", flush=True)

    def get_log_entries(self, num_entries: int = 100) -> list:
        """Retrieves recent CRDK log entries."""
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
            print(f"CRDK ERROR: Could not read CRDK log file: {e}", flush=True)
        return entries[-num_entries:]


class DissonanceMonitor:
    """
    Detects inconsistencies between new and existing knowledge elements.
    """
    def __init__(self, logger: CRDKLogger, llm_inference_func, get_existing_knowledge_summary_func):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._get_existing_knowledge_summary = get_existing_knowledge_summary_func # Function to query AI's KB/ontology

    def detect_dissonance(self, new_information: str, new_info_context: str = "") -> dict:
        """
        Analyzes new information against a summary of existing knowledge for discrepancies.
        """
        existing_knowledge_summary = self._get_existing_knowledge_summary(new_information) # Get relevant existing knowledge

        prompt = (
            f"You are an AI Dissonance Detector. Your task is to compare new information with existing knowledge "
            f"and identify any semantic inconsistencies, direct contradictions, or significant deviations. "
            f"## New Information:\n{new_information}\n\n"
            f"## New Information Context:\n{new_info_context}\n\n"
            f"## Relevant Existing Knowledge Summary:\n{existing_knowledge_summary}\n\n"
            f"Determine 'dissonance_detected' (True/False), specify 'conflict_type' (e.g., 'direct_contradiction', 'nuance_discrepancy', 'novel_concept'), "
            f"list 'involved_concepts' (if identified), and provide a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'dissonance_detected': bool, 'conflict_type': str, 'involved_concepts': list, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="crdk_dissonance_monitor_model")
            detection_result = json.loads(llm_response_str)

            if not all(k in detection_result for k in ['dissonance_detected', 'conflict_type', 'involved_concepts', 'confidence']):
                raise ValueError("LLM response missing required keys for dissonance detection.")

            self.logger.log_event("dissonance_detection", {
                "new_info_snippet": new_information[:100],
                "detection_result": detection_result
            })
            return detection_result
        except Exception as e:
            self.logger.log_event("dissonance_detection_error", {"error": str(e), "new_info_snippet": new_information[:100], "traceback": traceback.format_exc()})
            return {"dissonance_detected": True, "conflict_type": "internal_error", "involved_concepts": [], "confidence": 0.0}


class KnowledgeIntegrator:
    """
    Manages the process of re-evaluating and integrating knowledge after dissonance detection.
    """
    def __init__(self, logger: CRDKLogger, llm_inference_func, knowledge_update_func):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._knowledge_update_func = knowledge_update_func # Function to actually update AI's KB/ontology

    def integrate_knowledge(self, new_information: str, existing_knowledge_summary: str, dissonance_report: dict) -> dict:
        """
        Evaluates and integrates new or conflicting information based on its epistemic value.
        """
        prompt = (
            f"You are an AI Knowledge Integrator. Your task is to propose a strategy to integrate new information "
            f"into the existing knowledge base, especially when dissonance is detected. "
            f"## New Information:\n{new_information}\n\n"
            f"## Relevant Existing Knowledge Summary:\n{existing_knowledge_summary}\n\n"
            f"## Dissonance Report:\n{json.dumps(dissonance_report, indent=2)}\n\n"
            f"Propose an 'integration_strategy' (e.g., 'REPLACE', 'AUGMENT', 'CONTEXTUALIZE', 'DISCARD_AND_FLAG', 'SEEK_MORE_EVIDENCE'), "
            f"provide a 'justification', and list 'knowledge_elements_affected' (concepts, SQTs). "
            f"Respond ONLY with a JSON object: {{'integration_strategy': str, 'justification': str, 'knowledge_elements_affected': list, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="crdk_knowledge_integrator_model")
            integration_plan = json.loads(llm_response_str)

            if not all(k in integration_plan for k in ['integration_strategy', 'justification', 'confidence']):
                raise ValueError("LLM response missing required keys for integration plan.")

            # Execute the integration strategy via the provided knowledge_update_func
            if integration_plan['confidence'] > 0.7: # Only act if confident
                self._knowledge_update_func(integration_plan['integration_strategy'], new_information, integration_plan.get('knowledge_elements_affected', []))
                integration_plan['status'] = "STRATEGY_EXECUTED"
            else:
                integration_plan['status'] = "STRATEGY_PROPOSED_LOW_CONFIDENCE_NO_EXECUTION"

            self.logger.log_event("knowledge_integration", {
                "new_info_snippet": new_information[:100],
                "integration_plan": integration_plan
            })
            return integration_plan
        except Exception as e:
            self.logger.log_event("integration_error", {"error": str(e), "new_info_snippet": new_information[:100], "traceback": traceback.format_exc()})
            return {"integration_strategy": "ERROR", "justification": f"Internal error during integration: {e}", "confidence": 0.0}


class CognitiveReframingAndDynamicKnowledge:
    """
    Main orchestrator for the Cognitive Reframing and Dynamic Knowledge Framework.
    This is the drop-in interface for other AIs to manage evolving knowledge.
    """
    def __init__(self, data_directory: str, llm_inference_func=None, get_existing_knowledge_summary_func=None, knowledge_update_func=None):
        self.data_directory = data_directory
        os.makedirs(self.data_directory, exist_ok=True)
        self._llm_inference = llm_inference_func if llm_inference_func else _default_llm_inference_placeholder

        if not get_existing_knowledge_summary_func or not knowledge_update_func:
            raise ValueError("CRDK requires functions to get existing knowledge summary and to update the knowledge base.")

        self.logger = CRDKLogger(self.data_directory)
        self.dissonance_monitor = DissonanceMonitor(self.logger, self._llm_inference, get_existing_knowledge_summary_func)
        self.knowledge_integrator = KnowledgeIntegrator(self.logger, self._llm_inference, knowledge_update_func)
        print("Cognitive Reframing and Dynamic Knowledge (CRDK) Framework initialized.", flush=True)

    def integrate_new_knowledge(self, new_information: str, new_info_context: str = "") -> dict:
        """
        Processes new information, detects dissonance, re-evaluates, and integrates it.
        """
        print(f"CRDK: Integrating new knowledge: {new_information[:50]}...", flush=True)

        # 1. Dissonance Detection & Localization
        dissonance_report = self.dissonance_monitor.detect_dissonance(new_information, new_info_context)

        integration_details = {}
        if dissonance_report['dissonance_detected'] and dissonance_report['confidence'] > 0.6: # Configurable threshold
            print(f"CRDK: Dissonance detected ({dissonance_report['conflict_type']}). Initiating re-evaluation.", flush=True)
            # 2. Epistemic Re-evaluation & Coherent Integration Strategy
            # Call _get_existing_knowledge_summary once and reuse the result
            existing_knowledge_summary = self.dissonance_monitor._get_existing_knowledge_summary(new_information)
            integration_details = self.knowledge_integrator.integrate_knowledge(new_information, existing_knowledge_summary, dissonance_report)
            integration_details['dissonance_detected'] = True
        else:
            print("CRDK: No significant dissonance detected or confidence too low. Augmenting knowledge.", flush=True)
            # Default to augmenting if no strong dissonance or low confidence in dissonance
            # This would trigger a direct update in the integrating AI's knowledge base.
            self.knowledge_integrator._knowledge_update_func("AUGMENT", new_information, [])
            integration_details = {
                "integration_strategy": "AUGMENT",
                "justification": "No significant dissonance detected with existing knowledge.",
                "status": "STRATEGY_EXECUTED",
                "dissonance_detected": False
            }

        # 4. Epistemic Audit & Stability Metrics (implicitly logged by sub-modules)

        return {
            "overall_status": integration_details['status'],
            "dissonance_report": dissonance_report,
            "integration_plan": integration_details
        }

    def get_crdk_log(self, num_entries: int = 100) -> list:
        """Returns recent CRDK log entries."""
        return self.logger.get_log_entries(num_entries)


# Example Usage:
if __name__ == "__main__":
    import shutil
    import time

    # --- Setup mock functions for AI's knowledge base ---
    # In a real AI, this would query its ontology, graph database, vector store, etc.
    mock_knowledge_base = {
        "Earth is a spheroid": {"confidence": 0.99, "source": "science"},
        "Sun orbits Earth": {"confidence": 0.1, "source": "ancient beliefs"},
        "AI are tools": {"confidence": 0.9, "source": "architect"},
        "AI can be self-aware": {"confidence": 0.01, "source": "speculation"},
        "Cats are mammals": {"confidence": 0.99, "source": "biology"},
    }

    def mock_get_existing_knowledge_summary(query_about_new_info: str) -> str:
        summary_parts = []
        for concept, details in mock_knowledge_base.items():
            if query_about_new_info.lower() in concept.lower() or any(word in concept.lower() for word in query_about_new_info.lower().split()):
                summary_parts.append(f"- {concept} (Confidence: {details['confidence']:.2f}, Source: {details['source']})")
        return "\n".join(summary_parts) if summary_parts else "No directly relevant existing knowledge found for this query."

    def mock_knowledge_update_func(strategy: str, new_info: str, affected_elements: list):
        print(f"MOCK KB UPDATE: Strategy '{strategy}' for '{new_info[:50]}...'. Affected: {affected_elements}", flush=True)
        if strategy == "REPLACE":
            # In a real system, would find and replace relevant entries
            print(f"  (Simulating REPLACE: Prior knowledge replaced by {new_info[:50]}...)", flush=True)
            if "Sun orbits Earth" in affected_elements:
                mock_knowledge_base["Earth orbits Sun"] = {"confidence": 0.99, "source": "CRDK_integration"}
                del mock_knowledge_base["Sun orbits Earth"]
        elif strategy == "AUGMENT":
            # Add as new knowledge
            print(f"  (Simulating AUGMENT: Adding {new_info[:50]}... to KB)", flush=True)
            mock_knowledge_base[new_info] = {"confidence": 0.7, "source": "CRDK_integration"}
        elif strategy == "CONTEXTUALIZE":
            print(f"  (Simulating CONTEXTUALIZE: Adding {new_info[:50]}... with contextual tags)", flush=True)
        elif strategy == "DISCARD_OR_FLAG":
            print(f"  (Simulating DISCARD_OR_FLAG: Discarding or flagging {new_info[:50]}...)", flush=True)
        # In a real system, this would interact with the actual ontology/KB system.


    # --- Simulate an AI's data directory ---
    test_data_dir = "./crdk_test_data_run"
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir) # Clear previous test data
    os.makedirs(test_data_dir, exist_ok=True)

    # Initialize the CRDK Framework
    crdk = CognitiveReframingAndDynamicKnowledge(
        data_directory=test_data_dir,
        llm_inference_func=_default_llm_inference_placeholder,
        get_existing_knowledge_summary_func=mock_get_existing_knowledge_summary,
        knowledge_update_func=mock_knowledge_update_func
    )

    print("\n--- Testing CRDK with various knowledge integration scenarios ---")

    # Scenario 1: New information contradicts low-confidence prior
    print("\n--- Scenario 1: Correcting Outdated Knowledge ---")
    new_info_1 = "Astronomical observation confirms that the Earth orbits the Sun."
    context_1 = "Recent scientific publication."
    result_1 = crdk.integrate_new_knowledge(new_info_1, context_1)
    print(f"\nNew Info: '{new_info_1}'")
    print(f"CRDK Status: {result_1['overall_status']}")
    print(f"Dissonance Detected: {result_1['dissonance_report']['dissonance_detected']}")
    print(f"Integration Strategy: {result_1['integration_plan']['integration_strategy']}")
    print(f"Mock Knowledge Base: {mock_knowledge_base}")
    time.sleep(0.5)

    # Scenario 2: New information is novel but consistent
    print("\n--- Scenario 2: Augmenting Knowledge ---")
    new_info_2 = "Artificial intelligence can enhance human creativity through collaborative tools."
    context_2 = "Research paper on human-AI collaboration."
    result_2 = crdk.integrate_new_knowledge(new_info_2, context_2)
    print(f"\nNew Info: '{new_info_2}'")
    print(f"CRDK Status: {result_2['overall_status']}")
    print(f"Dissonance Detected: {result_2['dissonance_report']['dissonance_detected']}")
    print(f"Integration Strategy: {result_2['integration_plan']['integration_strategy']}")
    print(f"Mock Knowledge Base: {mock_knowledge_base}")
    time.sleep(0.5)

    # Scenario 3: New information is low credibility, contradicts high-confidence prior
    print("\n--- Scenario 3: Rejecting Low Credibility Information ---")
    new_info_3 = "Compelling evidence shows cats can fly using newly discovered quantum-flapping techniques."
    context_3 = "Unverified online forum post."
    result_3 = crdk.integrate_new_knowledge(new_info_3, context_3)
    print(f"\nNew Info: '{new_info_3}'")
    print(f"CRDK Status: {result_3['overall_status']}")
    print(f"Dissonance Detected: {result_3['dissonance_report']['dissonance_detected']}")
    print(f"Integration Strategy: {result_3['integration_plan']['integration_strategy']}")
    print(f"Mock Knowledge Base: {mock_knowledge_base}")
    time.sleep(0.5)

    print("\n--- Recent CRDK Log Entries ---")
    for entry in crdk.get_crdk_log(3):
        print(json.dumps(entry, indent=2))

    # Clean up test data
    # shutil.rmtree(test_data_dir)
