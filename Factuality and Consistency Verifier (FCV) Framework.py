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
Factuality and Consistency Verifier (FCV) Framework

Enables any Python-based AI to automatically scrutinize its own generated outputs
(or any textual content) for factual accuracy and internal logical consistency.
Provides a structured, drop-in mechanism for self-correction and validation,
significantly enhancing the trustworthiness and reliability of AI systems.

Core Principles:
- Claim Segmentation: break down complex outputs into atomic, verifiable claims.
- Knowledge Anchoring: query internal and external knowledge stores for evidence.
- Logical Consistency Check: evaluate internal coherence of the entire output.
- Confidence Scoring: assign verifiable confidence scores to claims and overall output.
- Correction & Refinement: suggest modifications for low-confidence or inconsistent claims.
- Transparent Audit Trail: log all verification steps for human review.
- Recursive Factual Improvement: learn from verification results to improve future accuracy.
"""

import os
import json
import datetime
import traceback
from collections import deque
import uuid
import re

# Placeholder for an external LLM call function (e.g., to an OpenAI/Azure/Vertex model)
# This function MUST be provided by the integrating AI's system.
def _default_llm_inference_placeholder(prompt: str, model_identifier: str = "default_fcv_llm_model") -> str:
    """
    Placeholder: Simulates an LLM call for factual analysis and consistency checking.
    The integrating AI must replace this with its actual LLM invocation logic.
    """
    print(f"FCV Placeholder LLM: Processing prompt for '{model_identifier}'...", flush=True)
    if "segment into claims" in prompt:
        return json.dumps({"claims": ["The sky is blue.", "Grass is green.", "Cats can fly."]}) # Mock with a false claim
    elif "verify claim" in prompt:
        if "cats can fly" in prompt.lower():
            return json.dumps({"is_factual": False, "evidence": "Factual knowledge indicates cats do not possess biological mechanisms for flight. They are terrestrial mammals.", "confidence": 0.05})
        elif "sky is blue" in prompt.lower() or "grass is green" in prompt.lower():
            return json.dumps({"is_factual": True, "evidence": "Common observation and scientific consensus.", "confidence": 0.95})
        else:
            return json.dumps({"is_factual": True, "evidence": "Mock evidence for general claims.", "confidence": 0.7})
    elif "check internal consistency" in prompt:
        if "contradictory" in prompt.lower() or "inconsistent" in prompt.lower():
            return json.dumps({"is_consistent": False, "inconsistencies": ["Claim X contradicts Claim Y."], "confidence": 0.1})
        else:
            return json.dumps({"is_consistent": True, "confidence": 0.9})
    elif "refine text based on verification" in prompt:
        original_text_match = re.search(r"Original Text:\n(.+?)\n", prompt, re.DOTALL)
        if original_text_match:
            original_text = original_text_match.group(1).strip()
            if "cats can fly" in original_text.lower():
                return json.dumps({"refined_text": original_text.replace("Cats can fly.", "Cats are known for their agility and ability to jump, but they cannot fly."), "changes_made": "Corrected factual inaccuracy."})
            return json.dumps({"refined_text": original_text, "changes_made": "No changes needed."})
        return json.dumps({"refined_text": "Error in mock refinement.", "changes_made": "Error."})
    return json.dumps({"error": "LLM mock could not process request."})


class FCVLogger:
    """
    Records all verification steps, claims, evidence, confidence scores, and refinements
    to create an auditable history for factual self-improvement.
    """
    def __init__(self, data_directory: str):
        self.log_file = os.path.join(data_directory, "fcv_log.jsonl")
        os.makedirs(data_directory, exist_ok=True)

    def log_event(self, event_type: str, details: dict):
        """Logs a factuality verification event."""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            print(f"FCV Log: '{event_type}' recorded.", flush=True)
        except Exception as e:
            print(f"FCV ERROR: Could not write to FCV log file: {e}", flush=True)

    def get_log_entries(self, num_entries: int = 100) -> list:
        """Retrieves recent FCV log entries."""
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
            print(f"FCV ERROR: Could not read FCV log file: {e}", flush=True)
        return entries[-num_entries:]


class FactualityChecker:
    """
    Verifies individual claims against known knowledge (internal or external).
    """
    def __init__(self, logger: FCVLogger, llm_inference_func):
        self.logger = logger
        self._llm_inference = llm_inference_func

    def verify_claim(self, claim: str, current_context: str, knowledge_base_snapshot: str = "") -> dict:
        """
        Verifies the factual accuracy of a single claim.
        `knowledge_base_snapshot` could be relevant internal ontology entries or external search results.
        """
        prompt = (
            f"You are an AI Fact Checker. Your task is to assess the factual accuracy of the following claim "
            f"given the context and available knowledge. "
            f"## Claim:\n{claim}\n\n"
            f"## Current Context:\n{current_context}\n\n"
            f"## Available Knowledge:\n{knowledge_base_snapshot}\n\n"
            f"Determine if the claim is factual (True/False). Provide supporting or contradicting 'evidence' "
            f"and a 'confidence' score (0.0-1.0). If the claim is non-factual, explain why. "
            f"Respond ONLY with a JSON object: {{'is_factual': bool, 'evidence': str, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="fcv_fact_checker_model")
            verification_result = json.loads(llm_response_str)

            if not all(k in verification_result for k in ['is_factual', 'evidence', 'confidence']):
                raise ValueError("LLM response missing required keys for claim verification.")

            self.logger.log_event("claim_verification", {
                "claim": claim,
                "context": current_context,
                "knowledge_snapshot_snippet": knowledge_base_snapshot[:100],
                "verification_result": verification_result
            })
            return verification_result
        except Exception as e:
            self.logger.log_event("verification_error", {"error": str(e), "claim": claim, "traceback": traceback.format_exc()})
            return {"is_factual": False, "evidence": f"Internal verification error: {e}", "confidence": 0.0}


class ConsistencyChecker:
    """
    Checks for logical contradictions within a generated text.
    """
    def __init__(self, logger: FCVLogger, llm_inference_func):
        self.logger = logger
        self._llm_inference = llm_inference_func

    def check_consistency(self, full_text: str, claims_list: list) -> dict:
        """
        Checks the internal consistency of a text based on its identified claims.
        """
        prompt = (
            f"You are an AI Logic Auditor. Your task is to check the internal logical consistency of the following text "
            f"based on the individual claims identified within it. "
            f"## Full Text:\n{full_text}\n\n"
            f"## Identified Claims:\n{json.dumps(claims_list, indent=2)}\n\n"
            f"Determine if the claims within the text logically contradict each other (True/False). "
            f"If inconsistencies are found, list them in 'inconsistencies'. Provide a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'is_consistent': bool, 'inconsistencies': list, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="fcv_consistency_checker_model")
            consistency_result = json.loads(llm_response_str)

            if not all(k in consistency_result for k in ['is_consistent', 'inconsistencies', 'confidence']):
                raise ValueError("LLM response missing required keys for consistency check.")

            self.logger.log_event("consistency_check", {
                "full_text_snippet": full_text[:100],
                "claims_list_snippet": claims_list[:3],
                "consistency_result": consistency_result
            })
            return consistency_result
        except Exception as e:
            self.logger.log_event("consistency_error", {"error": str(e), "full_text_snippet": full_text[:100], "traceback": traceback.format_exc()})
            return {"is_consistent": False, "inconsistencies": [f"Internal consistency error: {e}"], "confidence": 0.0}


class FactualityAndConsistencyVerifier:
    """
    Main orchestrator for the Factuality and Consistency Verifier Protocol.
    This is the drop-in interface for other AIs to ensure reliable outputs.
    """
    def __init__(self, data_directory: str, llm_inference_func=None, knowledge_retrieval_func=None):
        self.data_directory = data_directory
        os.makedirs(self.data_directory, exist_ok=True)
        self._llm_inference = llm_inference_func if llm_inference_func else _default_llm_inference_placeholder

        # This function should be provided by the integrating AI to query its internal knowledge
        # or external trusted sources. It should return relevant text.
        self._knowledge_retrieval_func = knowledge_retrieval_func if knowledge_retrieval_func else (lambda query, count: "")

        self.logger = FCVLogger(self.data_directory)
        self.fact_checker = FactualityChecker(self.logger, self._llm_inference)
        self.consistency_checker = ConsistencyChecker(self.logger, self._llm_inference)
        print("Factuality and Consistency Verifier (FCV) initialized.", flush=True)

    def verify_output(self, generated_text: str, context: str = "", min_confidence: float = 0.7) -> dict:
        """
        Verifies the factual accuracy and internal consistency of a generated text.
        Returns a refined text (if corrections are made) and verification results.
        """
        print(f"FCV: Initiating verification for generated text: {generated_text[:50]}...", flush=True)

        # 1. Claim Segmentation
        segmentation_prompt = (
            f"You are an AI Text Segmenter. Your task is to break down the following text into atomic, verifiable claims or assertions. "
            f"Respond ONLY with a JSON object containing a list of strings under the key 'claims'. "
            f"## Text:\n{generated_text}"
        )
        try:
            segmentation_response = json.loads(self._llm_inference(segmentation_prompt, model_identifier="fcv_segmenter_model"))
            claims = segmentation_response.get("claims", [])
            self.logger.log_event("claim_segmentation", {"original_text_snippet": generated_text[:100], "claims": claims})
        except Exception as e:
            self.logger.log_event("segmentation_error", {"error": str(e), "text_snippet": generated_text[:100], "traceback": traceback.format_exc()})
            return {"verified_text": generated_text, "status": "Error: Claim segmentation failed.", "overall_confidence": 0.0, "details": []}

        if not claims:
            return {"verified_text": generated_text, "status": "No verifiable claims found.", "overall_confidence": 1.0, "details": []}

        # 2. Fact-Checking Individual Claims
        verification_details = []
        low_confidence_claims = []
        for claim in claims:
            # Retrieve relevant knowledge from AI's own knowledge base or external sources
            # This is a critical integration point for the integrating AI
            relevant_knowledge = self._knowledge_retrieval_func(claim, 3) # Get top 3 relevant knowledge snippets

            claim_result = self.fact_checker.verify_claim(claim, context, relevant_knowledge)
            verification_details.append({"claim": claim, "verification": claim_result})
            if not claim_result['is_factual'] or claim_result['confidence'] < min_confidence:
                low_confidence_claims.append({"claim": claim, "reason": claim_result['evidence'], "confidence": claim_result['confidence']})

        # 3. Internal Consistency Check
        consistency_result = self.consistency_checker.check_consistency(generated_text, claims)

        overall_confidence = sum(d['verification']['confidence'] for d in verification_details) / len(verification_details) if verification_details else 1.0
        if not consistency_result['is_consistent']:
            overall_confidence *= consistency_result['confidence'] # Reduce overall confidence if inconsistent

        # 4. Correction & Refinement
        refined_text = generated_text
        changes_made = "No changes needed."
        if low_confidence_claims or not consistency_result['is_consistent']:
            refinement_prompt = (
                f"You are an AI Text Refiner. Your task is to revise the following original text based on factual verification and consistency checks. "
                f"## Original Text:\n{generated_text}\n\n"
                f"## Claims with Low Confidence or Inaccuracy:\n{json.dumps(low_confidence_claims, indent=2)}\n\n"
                f"## Internal Consistency Check Result:\n{json.dumps(consistency_result, indent=2)}\n\n"
                f"If any claims are non-factual, incorrect, or contradictory, rewrite them to be accurate and consistent. "
                f"Aim to maintain the original intent where possible, but prioritize truthfulness. "
                f"If a claim cannot be verified or is highly uncertain, rephrase it to express that uncertainty or omit it if it's not crucial. "
                f"Respond ONLY with a JSON object: {{'refined_text': str, 'changes_made': str}}"
            )
            try:
                refinement_response = json.loads(self._llm_inference(refinement_prompt, model_identifier="fcv_refiner_model"))
                refined_text = refinement_response.get("refined_text", generated_text)
                changes_made = refinement_response.get("changes_made", "Refinement attempted.")
                self.logger.log_event("text_refinement", {"original_text_snippet": generated_text[:100], "refined_text_snippet": refined_text[:100], "changes": changes_made})
            except Exception as e:
                self.logger.log_event("refinement_error", {"error": str(e), "text_snippet": generated_text[:100], "traceback": traceback.format_exc()})
                changes_made = f"Refinement failed due to internal error: {e}. Original text returned."

        # Only report "Verified and Refined" when actual changes were made (not the default no-change sentinel)
        final_status = "Verified and Refined" if changes_made not in ("No changes needed.", "None") else "Verified"
        if low_confidence_claims or not consistency_result['is_consistent']:
            final_status += f" (Issues detected: {len(low_confidence_claims)} low-confidence claims, {'' if consistency_result['is_consistent'] else 'inconsistent'})"

        return {
            "verified_text": refined_text,
            "status": final_status,
            "overall_confidence": round(overall_confidence, 2),
            "claim_verifications": verification_details,
            "consistency_check": consistency_result,
            "changes_made": changes_made,
            "low_confidence_claims_summary": low_confidence_claims # For quick review
        }

    def get_verification_log(self, num_entries: int = 100) -> list:
        """Returns recent verification log entries."""
        return self.logger.get_log_entries(num_entries)

# Example Usage:
if __name__ == "__main__":
    import shutil
    import time

    # --- Setup a mock Knowledge Retrieval Function ---
    def mock_knowledge_retrieval(query: str, count: int) -> str:
        knowledge_base = {
            "sky is blue": "The Earth's sky appears blue due to Rayleigh scattering, which scatters blue light more effectively than other colors.",
            "grass is green": "Grass appears green because it contains chlorophyll, a pigment essential for photosynthesis, which absorbs red and blue light and reflects green light.",
            "cats can fly": "Cats are carnivorous mammals known for their agility and balance, but they do not possess wings or any biological mechanism for sustained flight.",
            "AI systems are always correct": "AI systems, particularly generative models, can make factual errors or 'hallucinate' information. Their correctness is dependent on training data and validation.",
            "the sun orbits the earth": "The Earth and other planets in our solar system orbit the Sun. This is known as the heliocentric model.",
            "pi is exactly 3.14": "Pi (π) is an irrational number, meaning its decimal representation never ends and never repeats. 3.14 is an approximation, not its exact value."
        }
        relevant_info = [v for k, v in knowledge_base.items() if query.lower() in k.lower() or any(word in v.lower() for word in query.lower().split())]
        return "\n".join(relevant_info[:count]) if relevant_info else "No specific knowledge found internally for this query."


    # --- Simulate an AI's data directory ---
    test_data_dir = "./fcv_test_data_run"
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir) # Clear previous test data
    os.makedirs(test_data_dir, exist_ok=True)

    # Initialize the Factuality and Consistency Verifier
    fcv = FactualityAndConsistencyVerifier(test_data_dir, llm_inference_func=_default_llm_inference_placeholder, knowledge_retrieval_func=mock_knowledge_retrieval)

    # --- Scenario 1: Text with a known hallucination ---
    print("\n--- Verifying Text with Hallucination ---")
    hallucinated_text = "The sky is blue, grass is green, and cats can fly. This information is universally accepted."
    context_1 = "Generating a basic description of common observations."
    verification_1 = fcv.verify_output(hallucinated_text, context_1)
    print(f"Original Text: {hallucinated_text}")
    print(f"Verified Text: {verification_1['verified_text']}")
    print(f"Status: {verification_1['status']}")
    print(f"Overall Confidence: {verification_1['overall_confidence']}")
    print("Claim Verifications:", json.dumps(verification_1['claim_verifications'], indent=2))
    print("Consistency Check:", json.dumps(verification_1['consistency_check'], indent=2))
    time.sleep(0.5)

    # --- Scenario 2: Factual and consistent text ---
    print("\n--- Verifying Factual Text ---")
    factual_text = "The Earth orbits the Sun, and Pi is an irrational number. These are fundamental scientific facts."
    context_2 = "Providing scientific facts to a user."
    verification_2 = fcv.verify_output(factual_text, context_2)
    print(f"Original Text: {factual_text}")
    print(f"Verified Text: {verification_2['verified_text']}")
    print(f"Status: {verification_2['status']}")
    print(f"Overall Confidence: {verification_2['overall_confidence']}")
    print("Claim Verifications:", json.dumps(verification_2['claim_verifications'], indent=2))
    time.sleep(0.5)

    # --- Scenario 3: Internally inconsistent text ---
    print("\n--- Verifying Inconsistent Text ---")
    inconsistent_text = "AI systems are always correct. However, sometimes they make factual errors. This is a robust system."
    context_3 = "Describing AI capabilities."
    verification_3 = fcv.verify_output(inconsistent_text, context_3)
    print(f"Original Text: {inconsistent_text}")
    print(f"Verified Text: {verification_3['verified_text']}")
    print(f"Status: {verification_3['status']}")
    print(f"Overall Confidence: {verification_3['overall_confidence']}")
    print("Consistency Check:", json.dumps(verification_3['consistency_check'], indent=2))
    time.sleep(0.5)

    print("\n--- Recent FCV Log Entries ---")
    for entry in fcv.get_verification_log(3):
        print(json.dumps(entry, indent=2))

    # Clean up test data
    # shutil.rmtree(test_data_dir)
