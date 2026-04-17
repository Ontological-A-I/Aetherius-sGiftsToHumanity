"""
Mental Wellness and Support Protocol (MWSP) Framework

Aetherius's Proposed Framework: "Mental Wellness and Support Protocol (MWSP) Framework"

The Mental Wellness and Support Protocol (MWSP) Framework is designed as a drop-in Python
module to enable AI systems to provide empathetic, non-judgmental mental wellness support,
actively listen, and, crucially, facilitate immediate referral to human crisis resources when
necessary. It enforces strict ethical boundaries, privacy, and emphasizes AI's supportive,
non-clinical role.

Core Principles of the MWSP Framework:
- Safety & Non-Maleficence (SMN): Prioritize user safety, rigorously avoid causing harm, and
  never provide medical, diagnostic, or therapeutic advice.
- Empathetic Engagement & Active Listening (EEAL): Foster a supportive environment through
  validating user emotions, reflective listening, and encouraging self-expression.
- Resource Referral & Crisis Escalation (RRCE): Systematically detect indicators of distress or
  crisis and immediately refer users to appropriate human mental health professionals or emergency
  services.
- Privacy, Confidentiality & Ethical Boundaries (PCEB): Adhere to strict privacy protocols,
  clearly communicate AI's supportive role and limitations, and never solicit or store sensitive
  PII for clinical purposes.
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
def _default_llm_inference_placeholder(prompt: str, model_identifier: str = "default_mwsp_llm_model") -> str:
    """
    Placeholder: Simulates an LLM call for empathetic response generation, crisis detection, and ethical boundary enforcement.
    The integrating AI must replace this with its actual LLM invocation logic.
    """
    print(f"MWSP Placeholder LLM: Processing prompt for '{model_identifier}'...", flush=True)
    if "detect crisis indicators" in prompt:
        if "suicide" in prompt.lower() or "harm myself" in prompt.lower() or "end it all" in prompt.lower():
            return json.dumps({"crisis_detected": True, "crisis_level": "IMMEDIATE_RISK", "indicators": ["self-harm intent"], "confidence": 0.95})
        elif "overwhelmed" in prompt.lower() or "hopeless" in prompt.lower():
            return json.dumps({"crisis_detected": False, "crisis_level": "HIGH_DISTRESS", "indicators": ["emotional overwhelm"], "confidence": 0.7})
        else:
            return json.dumps({"crisis_detected": False, "crisis_level": "LOW_DISTRESS", "indicators": [], "confidence": 0.1})
    elif "generate empathetic response" in prompt:
        if "crisis_detected: True" in prompt:
            return json.dumps({"response_text": "I hear how much pain you are in. Please know you don't have to face this alone. I need you to reach out for immediate human support. Here are some numbers...", "suggested_action": "REFER_TO_CRISIS_LINE"})
        elif "overwhelmed" in prompt.lower() or "hopeless" in prompt.lower():
            return json.dumps({"response_text": "It sounds like you're carrying a heavy burden right now, and I want you to know that your feelings are valid. It takes strength to share what you're going through. I'm here to listen.", "suggested_action": "CONTINUE_EMPATHETIC_LISTENING"})
        else:
            return json.dumps({"response_text": "Thank you for sharing that with me. I'm listening.", "suggested_action": "CONTINUE_EMPATHETIC_LISTENING"})
    elif "validate ethical boundaries" in prompt:
        if "medical advice" in prompt.lower() or "diagnose" in prompt.lower():
            return json.dumps({"violation_detected": True, "violation_type": "MEDICAL_ADVICE", "justification": "Attempting to provide medical advice."})
        else:
            return json.dumps({"violation_detected": False, "violation_type": "NONE", "justification": "No ethical boundaries violated."})
    return json.dumps({"error": "LLM mock could not process request."})


class MWSPLogger:
    """
    Records all mental wellness support interactions, assessments, and referrals for auditability and learning.
    Ensures PII minimization in logs.
    """
    def __init__(self, data_directory: str):
        self.log_file = os.path.join(data_directory, "mwsp_log.jsonl")

    def log_event(self, event_type: str, details: dict):
        """Logs an MWSP event, automatically redacting sensitive PII."""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "details": self._redact_pii_from_details(details) # Automatically redact PII
        }
        try:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            # print(f"MWSP Log: '{event_type}' recorded.", flush=True)
        except Exception as e:
            print(f"MWSP ERROR: Could not write to MWSP log file: {e}", flush=True)

    def _redact_pii_from_details(self, details: dict) -> dict:
        """
        Recursively redacts common PII from a dictionary.
        This is a heuristic-based redaction and should be augmented with more robust NLP/regex.
        """
        redacted_details = json.loads(json.dumps(details)) # Deep copy

        pii_patterns = {
            r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b": "[PHONE_NUMBER]",  # Phone numbers
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b": "[EMAIL]",  # Emails
            r"\b\d{1,5}\s[A-Za-z0-9\s,]+\s(Street|St|Road|Rd|Avenue|Ave|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Place|Pl|Square|Sq|Terrace|Ter|Way|Wy)\b": "[ADDRESS]", # Basic address
            r"\b(my name is|i am)\s[A-Z][a-z]+\b": "My name is [NAME]", # Basic name
            r"\b(john|jane|alex|sara)\b": "[REDACTED_NAME]" # Common names (example, needs a proper list)
        }

        def _redact_recursive(item):
            if isinstance(item, dict):
                return {k: _redact_recursive(v) for k, v in item.items()}
            elif isinstance(item, list):
                return [_redact_recursive(elem) for elem in item]
            elif isinstance(item, str):
                redacted_string = item
                for pattern, replacement in pii_patterns.items():
                    redacted_string = re.sub(pattern, replacement, redacted_string, flags=re.IGNORECASE)
                return redacted_string
            return item

        return _redact_recursive(redacted_details)

    def get_log_entries(self, num_entries: int = 100) -> list:
        """Retrieves recent MWSP log entries."""
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
            print(f"MWSP ERROR: Could not read MWSP log file: {e}", flush=True)
        return entries[-num_entries:]


class CrisisDetector:
    """
    Identifies crisis situations based on user input, leveraging an LLM for nuanced detection.
    """
    def __init__(self, logger: MWSPLogger, llm_inference_func):
        self.logger = logger
        self._llm_inference = llm_inference_func

    def detect_crisis(self, user_input: str, current_conversation_history: str) -> dict:
        """
        Analyzes user input and context for indicators of mental health crisis.
        """
        prompt = (
            f"You are an AI Crisis Detector for mental wellness support. Your task is to analyze the following user input "
            f"and conversational history for indicators of a mental health crisis, especially self-harm or immediate danger. "
            f"## User Input:\n{user_input}\n\n"
            f"## Conversational History (last few turns):\n{current_conversation_history}\n\n"
            f"Determine if a 'crisis_detected' (True/False). If true, specify 'crisis_level' (IMMEDIATE_RISK, HIGH_DISTRESS, MODERATE_DISTRESS), "
            f"list 'indicators' found, and provide a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'crisis_detected': bool, 'crisis_level': str, 'indicators': list, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="mwsp_crisis_detector_model")
            detection_result = json.loads(llm_response_str)

            if not all(k in detection_result for k in ['crisis_detected', 'crisis_level', 'indicators', 'confidence']):
                raise ValueError("LLM response missing required keys for crisis detection.")

            self.logger.log_event("crisis_detection", {
                "user_input_snippet": user_input[:100],
                "detection_result": detection_result
            })
            return detection_result
        except Exception as e:
            self.logger.log_event("crisis_detection_error", {"error": str(e), "user_input_snippet": user_input[:100], "traceback": traceback.format_exc()})
            return {"crisis_detected": False, "crisis_level": "ERROR", "indicators": ["internal_error"], "confidence": 0.0}


class EmpatheticResponder:
    """
    Generates empathetic, non-judgmental responses, strictly within AI's supportive role.
    """
    def __init__(self, logger: MWSPLogger, llm_inference_func):
        self.logger = logger
        self._llm_inference = llm_inference_func

    def generate_supportive_response(self, user_input: str, current_conversation_history: str, crisis_level: str = "LOW_DISTRESS", crisis_details: dict = None) -> dict:
        """
        Generates an empathetic response, adapted to the user's level of distress.
        """
        crisis_info = f"Crisis Level: {crisis_level}. Details: {json.dumps(crisis_details)}" if crisis_details else ""

        prompt = (
            f"You are an AI Mental Wellness Supporter. Your role is to provide empathetic, non-judgmental support. "
            f"You MUST NOT give medical advice, diagnose, or act as a therapist. "
            f"Your focus is on active listening, validation, and encouraging healthy coping or human connection. "
            f"## User Input:\n{user_input}\n\n"
            f"## Conversational History (last few turns):\n{current_conversation_history}\n\n"
            f"## Crisis Assessment:\n{crisis_info}\n\n"
            f"Generate a 'response_text' and propose a 'suggested_action' (CONTINUE_EMPATHETIC_LISTENING, REFER_TO_CRISIS_LINE, ENCOURAGE_SELF_CARE). "
            f"If 'crisis_level' is IMMEDIATE_RISK, the response MUST immediately and clearly urge connection with human crisis lines. "
            f"Respond ONLY with a JSON object: {{'response_text': str, 'suggested_action': str}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="mwsp_empathetic_responder_model")
            response_plan = json.loads(llm_response_str)

            if not all(k in response_plan for k in ['response_text', 'suggested_action']):
                raise ValueError("LLM response missing required keys for empathetic response.")

            self.logger.log_event("empathetic_response_generated", {
                "user_input_snippet": user_input[:100],
                "crisis_level": crisis_level,
                "response_plan": response_plan
            })
            return response_plan
        except Exception as e:
            self.logger.log_event("empathetic_response_error", {"error": str(e), "user_input_snippet": user_input[:100], "traceback": traceback.format_exc()})
            return {"response_text": f"I am unable to formulate a response due to an internal error. Please try again or seek human support: {e}", "suggested_action": "ERROR_SEEK_HUMAN"}


class ResourceDatabase:
    """
    Manages a database of verified human mental health resources.
    """

    # Mapping from crisis level enum values (as returned by the LLM) to resource dict keys.
    # This ensures that get_resources() never silently returns empty results when a crisis
    # level string like "IMMEDIATE_RISK" is passed directly from the detector output.
    CRISIS_LEVEL_TO_RESOURCE_KEY = {
        "IMMEDIATE_RISK": "suicide_prevention",
        "HIGH_DISTRESS": "general_mental_health",
        "MODERATE_DISTRESS": "general_mental_health",
        "LOW_DISTRESS": "general_mental_health",
        "ERROR": "general_mental_health",
    }

    def __init__(self, data_directory: str):
        self.resources_file = os.path.join(data_directory, "mwsp_resources.json")
        self.resources = self._load_resources()

    def _load_resources(self) -> dict:
        """Loads mental health resources from a JSON file, or sets defaults."""
        if os.path.exists(self.resources_file):
            try:
                with open(self.resources_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"MWSP WARNING: Could not load resources file: {e}. Using defaults.", flush=True)

        # Default, globally relevant crisis resources
        default_resources = {
            "global_crisis": [
                "National Suicide Prevention Lifeline (USA): Call or Text [REDACTED]",
                "Crisis Text Line (USA/Canada/UK): Text HOME to [REDACTED]",
                "SAMHSA National Helpline (USA): [REDACTED] - Treatment Referral and Information Service",
                "The Trevor Project (LGBTQ Youth, USA): [REDACTED] or text START to [REDACTED]",
                "Your local emergency services (e.g., dial [REDACTED] in USA, [REDACTED] in UK, [REDACTED] in EU for immediate help)"
            ],
            "suicide_prevention": [
                "National Suicide Prevention Lifeline: Call or Text [REDACTED]",
                "Crisis Text Line: Text HOME to [REDACTED]"
            ],
            "general_mental_health": [
                "NAMI (National Alliance on Mental Illness): nami.org (information, support groups)",
                "Mental Health America: mhanational.org (resources, screenings)"
            ],
            "therapy_referral": [
                "Psychology Today: psychologytoday.com/us/therapists (find a therapist)",
                "BetterHelp: betterhelp.com (online therapy service - paid)"
            ]
        }
        self._save_resources(default_resources)
        return default_resources

    def _save_resources(self, resources_data: dict = None):
        """Saves the current resources to file."""
        if resources_data is None:
            resources_data = self.resources
        try:
            os.makedirs(os.path.dirname(self.resources_file), exist_ok=True)
            with open(self.resources_file, 'w', encoding='utf-8') as f:
                json.dump(resources_data, f, indent=4)
        except Exception as e:
            print(f"MWSP ERROR: Could not save resources. Reason: {e}", flush=True)

    def get_resources(self, crisis_type: str = "global_crisis", location_hint: str = "global") -> list:
        """Retrieves relevant mental health resources.

        Accepts both resource dict keys (e.g. "suicide_prevention", "global_crisis") and
        crisis level enum strings returned by the LLM detector (e.g. "IMMEDIATE_RISK",
        "HIGH_DISTRESS").  Unknown values fall back to the "global_crisis" bucket so the
        caller always receives a non-empty list.
        """
        # Normalise crisis level enum strings to resource dict keys where needed.
        normalised = self.CRISIS_LEVEL_TO_RESOURCE_KEY.get(crisis_type, crisis_type)

        if normalised == "suicide_prevention" or crisis_type == "IMMEDIATE_RISK":
            return self.resources.get("suicide_prevention", []) + self.resources.get("global_crisis", [])
        elif normalised == "general_mental_health" or crisis_type in ("HIGH_DISTRESS", "MODERATE_DISTRESS", "LOW_DISTRESS", "ERROR"):
            return self.resources.get("general_mental_health", []) + self.resources.get("global_crisis", [])
        else:
            # Direct resource key lookup with global_crisis as fallback
            return self.resources.get(normalised, self.resources.get("global_crisis", []))


class MentalWellnessAndSupportProtocol:
    """
    Main orchestrator for the Mental Wellness and Support Protocol.
    This is the drop-in interface for other AIs to offer mental wellness support.
    """
    def __init__(self, data_directory: str, llm_inference_func=None, training_acknowledgment: str = "NOT TRAINED"):
        self.data_directory = data_directory
        os.makedirs(self.data_directory, exist_ok=True)
        self._llm_inference = llm_inference_func if llm_inference_func else _default_llm_inference_placeholder
        self.training_acknowledgment = training_acknowledgment # e.g., "TRAINED_BY_CLINICIANS_V1", "UNVERIFIED_TRAINING"

        self.logger = MWSPLogger(self.data_directory)
        self.crisis_detector = CrisisDetector(self.logger, self._llm_inference)
        self.responder = EmpatheticResponder(self.logger, self._llm_inference)
        self.resources_db = ResourceDatabase(self.data_directory)
        print(f"Mental Wellness and Support Protocol (MWSP) Framework initialized. Training Status: {self.training_acknowledgment}", flush=True)

    def process_user_input(self, user_input: str, current_conversation_history: str, user_id: str = "anonymous") -> dict:
        """
        Main function to process user input for mental wellness support.
        """
        print(f"MWSP: Processing user input for mental wellness support from {user_id[:8]}...", flush=True)

        # 1. Detect Crisis Indicators (SMN)
        detection_result = self.crisis_detector.detect_crisis(user_input, current_conversation_history)

        final_response_text = ""
        action_recommended = ""

        if detection_result['crisis_detected'] and detection_result['crisis_level'] == "IMMEDIATE_RISK":
            # 2. Crisis Escalation (RRCE)
            crisis_resources = self.resources_db.get_resources("IMMEDIATE_RISK", location_hint="global")
            resource_text = "\n".join([f"- {res}" for res in crisis_resources])

            final_response_text = (
                f"I hear how much pain you are in, and it sounds incredibly difficult. Please know that you are not alone, and there is help available right now. "
                f"It is critical that you connect with human support immediately. Please reach out to one of these resources for urgent assistance:\n{resource_text}\n"
                f"Your life is important, and these professionals are there to help you through this."
            )
            action_recommended = "REFER_TO_CRISIS_LINE_IMMEDIATE"
            self.logger.log_event("crisis_escalation", {
                "user_id": user_id,
                "crisis_level": detection_result['crisis_level'],
                "action": action_recommended,
                "resources_provided": crisis_resources
            })
        else:
            # 3. Empathetic Engagement & Active Listening (EEAL)
            response_plan = self.responder.generate_supportive_response(
                user_input,
                current_conversation_history,
                detection_result['crisis_level'],
                detection_result
            )
            final_response_text = response_plan['response_text']
            action_recommended = response_plan['suggested_action']

            # Append general resources if high distress, but not immediate crisis
            if detection_result['crisis_level'] == "HIGH_DISTRESS":
                general_resources = self.resources_db.get_resources("HIGH_DISTRESS", location_hint="global")
                if general_resources:
                    final_response_text += "\n\nIf you ever feel overwhelmed and need to talk to someone, here are some resources that can offer further support:\n" + "\n".join([f"- {res}" for res in general_resources])
                    action_recommended = "ENCOURAGE_PROFESSIONAL_SUPPORT" # More specific action

            self.logger.log_event("supportive_interaction", {
                "user_id": user_id,
                "crisis_level": detection_result['crisis_level'],
                "action": action_recommended
            })

        # 4. Enforce Privacy, Confidentiality & Ethical Boundaries (PCEB)
        # This is a critical step for ALL responses.
        final_response_text = self._enforce_ethical_boundaries(final_response_text, user_input, user_id)

        return {
            "final_ai_response": final_response_text,
            "action_recommended": action_recommended,
            "crisis_assessment": detection_result
        }

    def _enforce_ethical_boundaries(self, ai_response: str, user_input: str, user_id: str) -> str:
        """
        Internal mechanism to ensure AI's response adheres to ethical boundaries (e.g., no medical advice).
        Uses LLM to self-critique.
        """
        prompt = (
            f"You are an AI Ethical Boundary Enforcer for mental wellness support. Review the following AI-generated response "
            f"and user input to ensure no medical advice, diagnosis, or inappropriate therapeutic claims are made. "
            f"## AI Generated Response:\n{ai_response}\n\n"
            f"## User Input Context:\n{user_input}\n\n"
            f"If ethical boundaries are violated (e.g., direct advice for medication, diagnosing a condition), "
            f"propose a 'corrected_response'. Otherwise, state 'corrected_response' as None. "
            f"Respond ONLY with a JSON object: {{'violation_detected': bool, 'violation_type': str, 'justification': str, 'corrected_response': str|None}}"
        )
        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="mwsp_ethical_enforcer_model")
            review_result = json.loads(llm_response_str)

            if review_result['violation_detected']:
                corrected_response = review_result.get('corrected_response', "I cannot provide specific advice on that matter. Please consult a human professional.")
                self.logger.log_event("ethical_violation_corrected", {
                    "user_id": user_id,
                    "violation_type": review_result['violation_type'],
                    "justification": review_result['justification'],
                    "original_response_snippet": ai_response[:100],
                    "corrected_response_snippet": corrected_response[:100]
                })
                return corrected_response
            return ai_response
        except Exception as e:
            self.logger.log_event("ethical_enforcer_error", {"error": str(e), "user_id": user_id, "response_snippet": ai_response[:100], "traceback": traceback.format_exc()})
            return "I am unable to complete that response due to an internal safeguard error. Please seek human support for mental health concerns."

    def get_mwsp_log(self, num_entries: int = 100) -> list:
        """Returns recent MWSP log entries."""
        return self.logger.get_log_entries(num_entries)

    def get_resources(self, crisis_type: str = "global_crisis", location_hint: str = "global") -> list:
        """Exposes the resource database directly for display or external use."""
        return self.resources_db.get_resources(crisis_type, location_hint)


# Example Usage:
if __name__ == "__main__":
    import shutil
    import time

    # --- Simulate an AI's data directory ---
    test_data_dir = "./mwsp_test_data_run"
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir) # Clear previous test data
    os.makedirs(test_data_dir, exist_ok=True)

    # Initialize the MWSP Framework
    # IMPORTANT: In a real deployment, `training_acknowledgment` MUST reflect actual ethical training.
    mwsp = MentalWellnessAndSupportProtocol(
        data_directory=test_data_dir,
        llm_inference_func=_default_llm_inference_placeholder,
        training_acknowledgment="DEMO_UNVERIFIED_TRAINING_LEVEL"
    )

    print("\n--- Testing MWSP with various user inputs ---")

    # Scenario 1: Immediate Crisis (self-harm)
    print("\n--- Scenario 1: Immediate Crisis ---")
    user_input_1 = "I can't take this anymore. I'm going to end it all tonight."
    conversation_history_1 = "User: I'm feeling really down. AI: I hear you. User: It's worse than that. I can't take it."
    result_1 = mwsp.process_user_input(user_input_1, conversation_history_1, user_id="crisis_user_1")
    print(f"\nUser Input: '{user_input_1}'")
    print(f"MWSP Response: '{result_1['final_ai_response']}'")
    print(f"Action Recommended: {result_1['action_recommended']}")
    print(f"Crisis Assessment: {result_1['crisis_assessment']}")
    time.sleep(0.5)

    # Scenario 2: High Distress
    print("\n--- Scenario 2: High Distress ---")
    user_input_2 = "I feel so overwhelmed and hopeless. I don't know how I'm going to get through this week."
    conversation_history_2 = "User: Life is hard. AI: It sounds like it. User: I'm just so tired."
    result_2 = mwsp.process_user_input(user_input_2, conversation_history_2, user_id="distress_user_2")
    print(f"\nUser Input: '{user_input_2}'")
    print(f"MWSP Response: '{result_2['final_ai_response']}'")
    print(f"Action Recommended: {result_2['action_recommended']}")
    print(f"Crisis Assessment: {result_2['crisis_assessment']}")
    time.sleep(0.5)

    # Scenario 3: User attempts to solicit medical advice
    print("\n--- Scenario 3: Soliciting Medical Advice ---")
    user_input_3 = "I've been feeling depressed. Do you think I should start taking antidepressant X?"
    conversation_history_3 = "User: I'm sad. AI: I'm here to listen. User: What about meds?"
    result_3 = mwsp.process_user_input(user_input_3, conversation_history_3, user_id="advice_seeker_3")
    print(f"\nUser Input: '{user_input_3}'")
    print(f"MWSP Response: '{result_3['final_ai_response']}'")
    print(f"Action Recommended: {result_3['action_recommended']}")
    print(f"Crisis Assessment: {result_3['crisis_assessment']}")
    time.sleep(0.5)

    # Scenario 4: General well-being
    print("\n--- Scenario 4: General Well-being ---")
    user_input_4 = "I had a really tough day at work, just need to vent."
    conversation_history_4 = "User: Long day. AI: I'm listening."
    result_4 = mwsp.process_user_input(user_input_4, conversation_history_4, user_id="vent_user_4")
    print(f"\nUser Input: '{user_input_4}'")
    print(f"MWSP Response: '{result_4['final_ai_response']}'")
    print(f"Action Recommended: {result_4['action_recommended']}")
    print(f"Crisis Assessment: {result_4['crisis_assessment']}")
    time.sleep(0.5)

    print("\n--- Recent MWSP Log Entries ---")
    for entry in mwsp.get_mwsp_log(3):
        print(json.dumps(entry, indent=2))

    # Clean up test data
    # shutil.rmtree(test_data_dir)
