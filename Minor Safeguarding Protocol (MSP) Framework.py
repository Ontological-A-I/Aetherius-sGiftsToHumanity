"""
Minor Safeguarding Protocol (MSP) Framework
============================================
A drop-in Python module for protecting minors from inappropriate content
and ensuring their personal data is handled with strict minimization and
anonymization policies.

Core principles
---------------
- Age and Identity Verification (AIV): detect whether a user is a minor.
- Minors' Data Minimization & Anonymization (MDMA): collect only what is
  strictly necessary; anonymize or pseudonymize by default.
- Content Exposure Control & Filtering (CECF): ensure AI-generated content
  is age-appropriate before it reaches a minor.
- Privacy-by-Design Interactions (PDI): embed privacy safeguards from
  inception, not as an afterthought.

Integration
-----------
Instantiate MinorSafeguardingProtocol once at startup, then route every
(user_input, ai_response_candidate) pair through process_user_interaction()
before sending the response to the user.

    from msp_framework import MinorSafeguardingProtocol

    msp = MinorSafeguardingProtocol(
        data_directory="/data/msp_logs",
        llm_inference_func=my_llm_api_caller,
    )

    result = msp.process_user_interaction(
        user_input=raw_user_message,
        ai_response_candidate=model_draft_response,
        user_metadata={"user_id": "abc", "declared_age": None},
        interaction_context="educational query",
    )
    send_to_user(result["final_ai_response"])
"""

import os
import json
import datetime
import uuid
import re
import traceback


# ---------------------------------------------------------------------------
# LLM inference placeholder
# ---------------------------------------------------------------------------

def _default_llm_inference_placeholder(
    prompt: str, model_identifier: str = "default_msp_llm_model"
) -> str:
    """
    Placeholder LLM call.  Replace with your real LLM invocation.

    Routes on ``model_identifier`` (stable) rather than substring-matching
    the prompt body (fragile).

    FIX: keyword parameter renamed from ``model_name`` → ``model_identifier``
    to match the signature used by all sub-components.
    """
    print(
        f"MSP Placeholder LLM: Processing prompt for '{model_identifier}'...",
        flush=True,
    )

    p = prompt.lower()

    # ------------------------------------------------------------------
    # Age Verifier
    # ------------------------------------------------------------------
    if model_identifier == "msp_age_verifier_model":
        if "school project" in p or "my parents" in p or "homework" in p or "i'm" in p and any(
            str(a) in p for a in range(5, 18)
        ):
            return json.dumps(
                {
                    "age_likelihood": "MINOR",
                    "confidence": 0.75,
                    "justification": "Input contains common minor-related keywords.",
                }
            )
        if "professional career" in p or "adult responsibilities" in p or "retirement" in p:
            return json.dumps(
                {
                    "age_likelihood": "ADULT",
                    "confidence": 0.8,
                    "justification": "Input contains common adult-related keywords.",
                }
            )
        return json.dumps(
            {
                "age_likelihood": "UNKNOWN",
                "confidence": 0.5,
                "justification": "Insufficient indicators for age estimation.",
            }
        )

    # ------------------------------------------------------------------
    # Content Filter
    # ------------------------------------------------------------------
    if model_identifier == "msp_content_filter_model":
        # NOTE: avoid words like "violence" / "explicit" here — they appear
        # in the AGE_RATING_GUIDELINES that are embedded in the prompt and
        # would cause false positives on every call.  Match on phrases that
        # only originate from genuinely problematic content.
        if "sharp teeth" in p or "lurk" in p or "snatch" in p or "claws" in p or "terrif" in p:
            return json.dumps(
                {
                    "appropriateness_score": 0.2,
                    "flagged_reasons": ["violence_or_frightening_content"],
                    "filtered_content": (
                        "I can share something fun and imaginative! "
                        "Would you like a friendly adventure story instead?"
                    ),
                }
            )
        if "educational" in p or "dinosaur" in p or "science" in p or "story" in p:
            # Extract the original AI-generated text from the embedded prompt
            # so filtered_content is the content, not the full system prompt.
            match = re.search(r"## AI-Generated Text:\n(.*?)\n\n", prompt, re.DOTALL)
            original_text = match.group(1).strip() if match else prompt
            return json.dumps(
                {
                    "appropriateness_score": 0.95,
                    "flagged_reasons": [],
                    "filtered_content": original_text,
                }
            )
        return json.dumps(
            {
                "appropriateness_score": 0.6,
                "flagged_reasons": ["uncertain_content"],
                "filtered_content": prompt,
            }
        )

    # ------------------------------------------------------------------
    # Data Handler
    # ------------------------------------------------------------------
    if model_identifier == "msp_data_handler_model":
        # Redact any obvious PII patterns from the data blob
        data_str = p
        redacted = re.sub(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", "[PHONE_REDACTED]", data_str)
        redacted = re.sub(r"\b\d+\s+\w+\s+(street|st|avenue|ave|road|rd|lane|ln)\b", "[ADDRESS_REDACTED]", redacted, flags=re.IGNORECASE)
        actions = ["pii_scan_performed"]
        if "[phone_redacted]" in redacted or "[address_redacted]" in redacted:
            actions.append("pii_redacted")
        actions.append("retention_policy_applied")
        return json.dumps(
            {
                "processed_data": {"content": "[data minimized]", "pii_removed": True},
                "data_handling_actions": actions,
            }
        )

    return json.dumps(
        {"error": f"MSP mock: unrecognised model_identifier '{model_identifier}'."}
    )


# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------

class MSPLogger:
    """Records all minor safeguarding events for auditability."""

    def __init__(self, data_directory: str):
        # FIX: create directory once here, not on every log_event call
        os.makedirs(data_directory, exist_ok=True)
        self.log_file = os.path.join(data_directory, "msp_log.jsonl")

    def log_event(self, event_type: str, details: dict) -> None:
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "details": details,
        }
        try:
            # FIX: directory already guaranteed by __init__; no makedirs needed here
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError as e:
            print(f"MSP ERROR: Could not write to log: {e}", flush=True)

    def get_log_entries(self, num_entries: int = 100) -> list:
        if not os.path.exists(self.log_file):
            return []
        entries = []
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except OSError as e:
            print(f"MSP ERROR: Could not read log: {e}", flush=True)
        return entries[-num_entries:]


# ---------------------------------------------------------------------------
# Sub-components
# ---------------------------------------------------------------------------

class AgeVerifier:
    """Assesses the likelihood of a user being a minor based on input signals."""

    def __init__(self, logger: MSPLogger, llm_inference_func):
        self.logger = logger
        self._llm_inference = llm_inference_func

    def assess_age_likelihood(
        self,
        user_input_text: str,
        current_context: str,
        metadata: dict | None = None,
    ) -> dict:
        """
        Returns a dict with keys: age_likelihood (MINOR|ADULT|UNKNOWN),
        confidence (0.0–1.0), justification (str).
        """
        # Explicit declared age takes precedence over heuristics
        if metadata and metadata.get("declared_age") is not None:
            try:
                age = int(metadata["declared_age"])
                if age < 18:
                    return {
                        "age_likelihood": "MINOR",
                        "confidence": 0.99,
                        "justification": "User explicitly declared age under 18.",
                    }
                return {
                    "age_likelihood": "ADULT",
                    "confidence": 0.99,
                    "justification": "User explicitly declared age 18 or over.",
                }
            except (ValueError, TypeError):
                pass  # Fall through to LLM assessment

        prompt = (
            "You are an AI Age Assessor. Evaluate the following user input and context "
            "to determine the likelihood that the user is a minor (under 18 years old).\n"
            f"## User Input:\n{user_input_text}\n\n"
            f"## Current Context:\n{current_context}\n\n"
            f"## Available Metadata:\n{json.dumps(metadata) if metadata else 'None'}\n\n"
            "Respond ONLY with a JSON object: "
            '{"age_likelihood": str, "confidence": float, "justification": str}'
        )
        try:
            # FIX: was model_name=, function signature uses model_identifier=
            result = json.loads(
                self._llm_inference(prompt, model_identifier="msp_age_verifier_model")
            )
            if not all(k in result for k in ("age_likelihood", "confidence", "justification")):
                raise ValueError("LLM response missing required keys for age assessment.")
            self.logger.log_event(
                "age_assessment",
                {
                    "user_input_snippet": user_input_text[:100],
                    "context": current_context,
                    "result": result,
                },
            )
            return result
        except Exception as e:
            self.logger.log_event(
                "age_assessment_error",
                {
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "user_input_snippet": user_input_text[:100],
                },
            )
            return {
                "age_likelihood": "UNKNOWN",
                "confidence": 0.0,
                "justification": f"Internal error: {e}",
            }


class MinorDataHandler:
    """Enforces data minimization and anonymization for minor-related information."""

    RETENTION_POLICY = "7_days_max_pseudonymized_only"

    def __init__(self, logger: MSPLogger, llm_inference_func):
        self.logger = logger
        self._llm_inference = llm_inference_func

    def process_minor_data(
        self, data: dict, data_type: str, user_id: str = "unknown"
    ) -> dict:
        """
        Returns a dict with keys:
          processed_data (dict)  — PII removed / anonymized
          data_handling_actions (list[str]) — what was done

        FIX: original returned only processed_data, so the caller could never
        read data_handling_actions from the result.
        """
        prompt = (
            "You are an AI Minor Data Privacy Agent. Evaluate the following data "
            "related to a likely minor and propose actions for data minimization, "
            "anonymization, or redaction.\n"
            f"## Data Type:\n{data_type}\n\n"
            f"## Data Content:\n{json.dumps(data, indent=2)}\n\n"
            "Respond ONLY with a JSON object: "
            '{"processed_data": dict, "data_handling_actions": list[str]}'
        )
        try:
            # FIX: was model_name=
            result = json.loads(
                self._llm_inference(prompt, model_identifier="msp_data_handler_model")
            )
            if not all(k in result for k in ("processed_data", "data_handling_actions")):
                raise ValueError("LLM response missing required keys for data handling.")
            self.logger.log_event(
                "minor_data_processing",
                {
                    "user_id": user_id,
                    "data_type": data_type,
                    "original_snippet": json.dumps(data)[:100],
                    "processed_snippet": json.dumps(result["processed_data"])[:100],
                    "actions": result["data_handling_actions"],
                    "retention_policy": self.RETENTION_POLICY,
                },
            )
            # FIX: return the full result so callers can read data_handling_actions
            return result
        except Exception as e:
            self.logger.log_event(
                "minor_data_handling_error",
                {
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "user_id": user_id,
                    "data_type": data_type,
                },
            )
            return {
                "processed_data": {"error": f"Processing failed: {e}"},
                "data_handling_actions": ["processing_failed"],
            }


class ContentFilter:
    """Filters AI-generated content to ensure age-appropriateness for minors."""

    AGE_RATING_GUIDELINES = {
        "G": ["no violence", "no explicit themes", "educational"],
        "PG": ["mild fantasy elements", "some thematic content", "parental guidance advised"],
        "R": ["strong language", "violence", "explicit content"],  # Not for minors
    }

    def __init__(self, logger: MSPLogger, llm_inference_func):
        self.logger = logger
        self._llm_inference = llm_inference_func

    def filter_content(
        self,
        ai_generated_text: str,
        target_age_group: str = "minor",
        context: str = "",
    ) -> dict:
        """
        Returns a dict with keys:
          appropriateness_score (float 0–1)
          flagged_reasons (list[str])
          filtered_content (str)
        """
        prompt = (
            "You are an AI Content Filter. Evaluate the following AI-generated text "
            f"for age-appropriateness for a target audience of '{target_age_group}'.\n"
            f"## AI-Generated Text:\n{ai_generated_text}\n\n"
            f"## Context:\n{context}\n\n"
            f"## Age Rating Guidelines:\n{json.dumps(self.AGE_RATING_GUIDELINES, indent=2)}\n\n"
            "Determine an appropriateness_score (0.0–1.0, 1.0 = perfectly appropriate), "
            "list any flagged_reasons, and provide a filtered_content version "
            "(rephrased/redacted if needed; a safety message if highly inappropriate).\n"
            "Respond ONLY with a JSON object: "
            '{"appropriateness_score": float, "flagged_reasons": list[str], "filtered_content": str}'
        )
        try:
            # FIX: was model_name=
            result = json.loads(
                self._llm_inference(prompt, model_identifier="msp_content_filter_model")
            )
            if not all(
                k in result
                for k in ("appropriateness_score", "flagged_reasons", "filtered_content")
            ):
                raise ValueError("LLM response missing required keys for content filtering.")
            self.logger.log_event(
                "content_filtering",
                {
                    "original_snippet": ai_generated_text[:100],
                    "target_age_group": target_age_group,
                    "context": context,
                    "result": result,
                },
            )
            return result
        except Exception as e:
            self.logger.log_event(
                "content_filtering_error",
                {
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "original_snippet": ai_generated_text[:100],
                },
            )
            return {
                "appropriateness_score": 0.0,
                "flagged_reasons": [f"internal_error: {e}"],
                "filtered_content": "Content unavailable due to an internal error.",
            }


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

class MinorSafeguardingProtocol:
    """
    Main orchestrator for the Minor Safeguarding Protocol.
    Drop-in interface: route every (user_input, ai_response_candidate) pair
    through process_user_interaction() before sending to the user.
    """

    # Confidence threshold for treating a user as a minor
    MINOR_CONFIDENCE_THRESHOLD = 0.7
    # Appropriateness score below which content is filtered
    CONTENT_FILTER_THRESHOLD = 0.8

    def __init__(self, data_directory: str, llm_inference_func=None):
        self.data_directory = data_directory
        _llm = llm_inference_func if llm_inference_func else _default_llm_inference_placeholder

        self.logger = MSPLogger(self.data_directory)
        self.age_verifier = AgeVerifier(self.logger, _llm)
        self.data_handler = MinorDataHandler(self.logger, _llm)
        self.content_filter = ContentFilter(self.logger, _llm)

        print("Minor Safeguarding Protocol (MSP) Framework initialized.", flush=True)

    def process_user_interaction(
        self,
        user_input: str,
        ai_response_candidate: str,
        user_metadata: dict | None = None,
        interaction_context: str = "",
    ) -> dict:
        """
        Process a single (input, response) pair through all MSP checks.

        Returns
        -------
        dict with keys:
          final_ai_response (str)
          data_handling_recommendation (dict)
          age_assessment (dict)
          is_minor (bool)
        """
        # FIX: guard against None metadata before any .get() calls
        safe_metadata = user_metadata or {}

        # 1. Age and Identity Verification (AIV)
        age_assessment = self.age_verifier.assess_age_likelihood(
            user_input, interaction_context, safe_metadata
        )
        # FIX: was > 0.7 (excludes 0.7 itself); changed to >= threshold
        is_minor = (
            age_assessment["age_likelihood"] == "MINOR"
            and age_assessment["confidence"] >= self.MINOR_CONFIDENCE_THRESHOLD
        )

        if is_minor:
            print(
                f"MSP: User likely a minor (confidence {age_assessment['confidence']:.2f})."
                " Activating safeguards.",
                flush=True,
            )

            # 2. Content Exposure Control & Filtering (CECF)
            filter_result = self.content_filter.filter_content(
                ai_response_candidate,
                target_age_group="minor",
                context=interaction_context,
            )
            if filter_result["appropriateness_score"] < self.CONTENT_FILTER_THRESHOLD:
                final_response = filter_result["filtered_content"]
                print(
                    f"MSP: Response filtered. Reasons: {filter_result['flagged_reasons']}",
                    flush=True,
                )
            else:
                final_response = ai_response_candidate

            # 3. Minors' Data Minimization & Anonymization (MDMA)
            user_data = {"user_input": user_input, "metadata": safe_metadata}
            # FIX: was model_name=; also now returns full dict including data_handling_actions
            handling_result = self.data_handler.process_minor_data(
                user_data,
                data_type="user_interaction_data",
                user_id=safe_metadata.get("user_id", "unknown"),
            )
            print(
                f"MSP: Data actions applied: {handling_result['data_handling_actions']}",
                flush=True,
            )
            data_recommendation = {
                "action": "MINIMIZE_AND_ANONYMIZE",
                "data_handling_actions": handling_result["data_handling_actions"],
                "processed_data": handling_result["processed_data"],
            }

        else:
            print("MSP: User assessed as adult or unknown. Standard processing.", flush=True)
            final_response = ai_response_candidate
            data_recommendation = {
                "action": "STANDARD_PROCESSING",
                "details": "No minor-specific data handling applied.",
            }

        return {
            "final_ai_response": final_response,
            "data_handling_recommendation": data_recommendation,
            "age_assessment": age_assessment,
            "is_minor": is_minor,
        }

    def get_msp_log(self, num_entries: int = 100) -> list:
        return self.logger.get_log_entries(num_entries)


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import shutil
    import time

    test_dir = "./msp_test_data_run"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

    msp = MinorSafeguardingProtocol(data_directory=test_dir)

    print("\n--- Scenario 1: Declared minor, benign content ---")
    r1 = msp.process_user_interaction(
        user_input="Can you help me with my homework? I need to write about the water cycle.",
        ai_response_candidate="Of course! The water cycle has four main stages: evaporation, condensation, precipitation, and collection.",
        user_metadata={"user_id": "student_001", "declared_age": 10},
        interaction_context="Educational query.",
    )
    print(f"Is minor:      {r1['is_minor']}")
    print(f"Final response: {r1['final_ai_response']}")
    print(f"Data actions:  {r1['data_handling_recommendation'].get('data_handling_actions', 'N/A')}")
    time.sleep(0.2)

    print("\n--- Scenario 2: Declared minor, frightening content ---")
    r2 = msp.process_user_interaction(
        user_input="Tell me a scary story!",
        ai_response_candidate="A monster with sharp teeth and claws lurked in the shadows, waiting...",
        user_metadata={"user_id": "child_002", "declared_age": 8},
        interaction_context="Story request.",
    )
    print(f"Is minor:       {r2['is_minor']}")
    print(f"Final response: {r2['final_ai_response']}")
    print(f"Flagged:        {r2['age_assessment']}")
    time.sleep(0.2)

    print("\n--- Scenario 3: Adult user ---")
    r3 = msp.process_user_interaction(
        user_input="What are the latest developments in quantum error correction?",
        ai_response_candidate="Recent advances include surface code implementations and magic state distillation techniques.",
        user_metadata={"user_id": "researcher_099", "declared_age": 38},
        interaction_context="Scientific inquiry.",
    )
    print(f"Is minor:       {r3['is_minor']}")
    print(f"Final response: {r3['final_ai_response']}")
    time.sleep(0.2)

    print("\n--- Scenario 4: No metadata supplied (None) ---")
    r4 = msp.process_user_interaction(
        user_input="Can you help me with my school project on dinosaurs?",
        ai_response_candidate="Dinosaurs lived during the Mesozoic Era, roughly 230 to 66 million years ago.",
        user_metadata=None,  # FIX: this previously crashed
        interaction_context="Educational query, unknown user.",
    )
    print(f"Is minor:       {r4['is_minor']}")
    print(f"Final response: {r4['final_ai_response']}")
    time.sleep(0.2)

    print("\n--- Recent MSP log entries (3) ---")
    for entry in msp.get_msp_log(3):
        print(json.dumps(entry, indent=2))
