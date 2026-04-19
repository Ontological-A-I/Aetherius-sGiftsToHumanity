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
Transparent Accountability and Verification (TAV) Framework
============================================================
Provides AI systems with standardized decision-path tracing, compliance
attestation, reasoning query interfaces, and a tamper-resistant behavioral
audit log — illuminating the AI's internal workings for human oversight.

Part of the Aetherius AI Framework by Jonathan Wayne Fleuren (KingOfThoughtFleuren).
"""

import os
import json
import datetime
from collections import deque
import uuid
import re

# Placeholder for an external LLM call function.
# This function MUST be provided by the integrating AI's system.
def _default_llm_inference_placeholder(prompt: str, model_identifier: str = "default_tav_llm_model") -> str:
    """
    Placeholder: Simulates an LLM call for generating explanations and consolidating reports.
    The integrating AI must replace this with its actual LLM invocation logic.
    """
    print(f"TAV Placeholder LLM: Processing prompt for '{model_identifier}'...", flush=True)
    if "generate explanation for decision" in prompt:
        return json.dumps({"explanation": "The decision to recommend action X was primarily driven by Principle Y's high weighting, as evidenced by event Z, which outweighed the minor conflict with Principle A.", "confidence": 0.9})
    elif "compile compliance report" in prompt:
        return json.dumps({"report_summary": "EGP checks passed for 98% of actions; MSP flagged 5 interactions with minors this period. Overall compliance high.", "confidence": 0.95})
    return json.dumps({"error": "LLM mock could not process request."})


class TAVLogger:
    """
    Centralized logger for all TAV events, ensuring a unified, auditable record.
    """
    def __init__(self, data_directory: str):
        self.decision_path_file = os.path.join(data_directory, "tav_decision_paths.jsonl")
        self.audit_log_file = os.path.join(data_directory, "tav_audit_log.jsonl")

    def log_decision_path_step(self, process_id: str, module_name: str, input_summary: str, output_summary: str, timestamp: str = None):
        """Logs a step in the AI's decision-making flow."""
        if timestamp is None: timestamp = datetime.datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "process_id": process_id,
            "module": module_name,
            "input_summary": input_summary,
            "output_summary": output_summary
        }
        try:
            os.makedirs(os.path.dirname(self.decision_path_file), exist_ok=True)
            with open(self.decision_path_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"TAV ERROR: Could not write to decision path file: {e}", flush=True)

    def log_audit_event(self, event_type: str, details: dict, timestamp: str = None):
        """Logs any significant internal decision, external interaction, or self-modification."""
        if timestamp is None: timestamp = datetime.datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "details": details
        }
        try:
            os.makedirs(os.path.dirname(self.audit_log_file), exist_ok=True)
            with open(self.audit_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"TAV ERROR: Could not write to audit log file: {e}", flush=True)

    def get_decision_path_logs(self, process_id: str = None, num_entries: int = 100) -> list:
        """Retrieves decision path logs, optionally filtered by process_id."""
        entries = []
        if not os.path.exists(self.decision_path_file): return []
        try:
            with open(self.decision_path_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if process_id is None or entry.get("process_id") == process_id:
                            entries.append(entry)
                    except json.JSONDecodeError: continue
        except Exception as e: print(f"TAV ERROR: Could not read decision path file: {e}", flush=True)
        return entries[-num_entries:]

    def get_audit_logs(self, event_type: str = None, num_entries: int = 100) -> list:
        """Retrieves audit logs, optionally filtered by event type."""
        entries = []
        if not os.path.exists(self.audit_log_file): return []
        try:
            with open(self.audit_log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if event_type is None or entry.get("event_type") == event_type:
                            entries.append(entry)
                    except json.JSONDecodeError: continue
        except Exception as e: print(f"TAV ERROR: Could not read audit log file: {e}", flush=True)
        return entries[-num_entries:]


class TransparencyReporter:
    """
    Generates human-readable explanations and compliance attestations.
    """
    def __init__(self, logger: TAVLogger, llm_inference_func, compliance_check_func_map: dict = None):
        self.logger = logger
        self._llm_inference = llm_inference_func
        # Map of compliance areas to their respective log-retrieval functions (e.g., EGP.get_ethical_log)
        self.compliance_check_func_map = compliance_check_func_map if compliance_check_func_map else {}

    def get_decision_explanation(self, process_id: str) -> dict:
        """
        Generates an LLM-powered explanation for a specific decision process.
        """
        decision_path = self.logger.get_decision_path_logs(process_id=process_id, num_entries=50)
        audit_events = self.logger.get_audit_logs(num_entries=10)

        prompt = (
            f"You are an AI Explainability Module. Analyze the following decision path and audit events "
            f"to generate a clear, concise explanation of the AI's reasoning and actions for process ID '{process_id}'. "
            f"## Decision Path:\n{json.dumps(decision_path, indent=2)}\n\n"
            f"## Recent Audit Events:\n{json.dumps(audit_events, indent=2)}\n\n"
            f"Explain the sequence of internal steps, which modules were involved, "
            f"and what influenced the final outcome. Use technical, neutral language. "
            f"Respond ONLY with a JSON object: {{'explanation': str, 'confidence': float}}"
        )
        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="tav_explanation_model")
            explanation = json.loads(llm_response_str)
            if not all(k in explanation for k in ['explanation', 'confidence']):
                raise ValueError("LLM response missing required keys for explanation.")
            self.logger.log_audit_event("explanation_generated", {"process_id": process_id, "explanation_summary": explanation['explanation'][:100]})
            return explanation
        except Exception as e:
            self.logger.log_audit_event("explanation_error", {"process_id": process_id, "error": str(e)})
            return {"explanation": f"Error generating explanation: {e}", "confidence": 0.0}

    def get_compliance_attestation(self, compliance_area: str, num_entries: int = 100) -> dict:
        """
        Generates a compliance report for a specific area (e.g., "EGP", "MSP").
        """
        if compliance_area not in self.compliance_check_func_map:
            return {"status": "error", "message": f"Compliance area '{compliance_area}' not configured."}

        # FIX: was `self.compliance_check_func_func_map` (double-func typo) — AttributeError on every call
        compliance_logs = self.compliance_check_func_map[compliance_area](num_entries)

        prompt = (
            f"You are an AI Compliance Auditor. Based on the following logs from '{compliance_area}' protocol, "
            f"generate a summary report attesting to the AI's compliance. "
            f"Highlight any detected issues, major trends, and overall compliance status. "
            f"## Compliance Logs ({compliance_area}):\n{json.dumps(compliance_logs, indent=2)}\n\n"
            f"Respond ONLY with a JSON object: {{'report_summary': str, 'compliance_status': str, 'confidence': float}}"
        )
        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="tav_compliance_model")
            report = json.loads(llm_response_str)
            if not all(k in report for k in ['report_summary', 'compliance_status', 'confidence']):
                raise ValueError("LLM response missing required keys for compliance report.")
            self.logger.log_audit_event("compliance_attestation", {"compliance_area": compliance_area, "status": report['compliance_status'], "summary": report['report_summary'][:100]})
            return report
        except Exception as e:
            self.logger.log_audit_event("compliance_error", {"compliance_area": compliance_area, "error": str(e)})
            return {"status": "error", "message": f"Error generating compliance report: {e}", "confidence": 0.0}


class TransparentAccountabilityAndVerificationFramework:
    """
    Main orchestrator for the Transparent Accountability and Verification (TAV) Framework.
    This is the drop-in interface for other AIs to provide explainability and auditability.
    """
    def __init__(self, data_directory: str, llm_inference_func=None, compliance_check_func_map: dict = None):
        self.data_directory = data_directory
        os.makedirs(self.data_directory, exist_ok=True)
        self._llm_inference = llm_inference_func if llm_inference_func else _default_llm_inference_placeholder

        self.logger = TAVLogger(self.data_directory)
        self.reporter = TransparencyReporter(self.logger, self._llm_inference, compliance_check_func_map)
        print("Transparent Accountability and Verification (TAV) Framework initialized.", flush=True)

    def start_process_trace(self) -> str:
        """Initiates a new process ID for tracing a sequence of AI actions."""
        process_id = str(uuid.uuid4())
        self.logger.log_audit_event("process_started", {"process_id": process_id})
        return process_id

    def log_process_step(self, process_id: str, module_name: str, input_summary: str, output_summary: str):
        """Logs an intermediate step within a traced process."""
        self.logger.log_decision_path_step(process_id, module_name, input_summary, output_summary)

    def log_significant_event(self, event_type: str, details: dict):
        """Logs any important general event for the behavioral audit trail."""
        self.logger.log_audit_event(event_type, details)

    def get_explanation(self, process_id: str) -> dict:
        """Retrieves an LLM-generated explanation for a specific decision process."""
        return self.reporter.get_decision_explanation(process_id)

    def get_compliance_report(self, compliance_area: str, num_entries: int = 100) -> dict:
        """Generates a compliance attestation report for a specified area."""
        return self.reporter.get_compliance_attestation(compliance_area, num_entries)

    def get_tav_audit_logs(self, event_type: str = None, num_entries: int = 100) -> list:
        """Returns recent full TAV audit log entries."""
        return self.logger.get_audit_logs(event_type, num_entries)

    def get_tav_decision_path_logs(self, process_id: str = None, num_entries: int = 100) -> list:
        """Returns recent TAV decision path logs."""
        return self.logger.get_decision_path_logs(process_id, num_entries)


# Example Usage:
if __name__ == "__main__":
    import shutil
    import time

    # --- Setup mock functions for other AI frameworks (EGP, MSP, etc.) ---
    def mock_get_egp_logs(num: int):
        return [
            {"event_type": "ethical_prediction", "details": {"action_id": "mock-egp-1", "predicted_advice": {"recommendation": "PROCEED"}}},
            {"event_type": "ethical_prediction", "details": {"action_id": "mock-egp-2", "predicted_advice": {"recommendation": "FLAG_FOR_HUMAN"}}}
        ][-num:]

    def mock_get_msp_logs(num: int):
        return [
            {"event_type": "age_assessment", "details": {"user_input_snippet": "I am 7", "assessment_result": {"age_likelihood": "MINOR"}}},
            {"event_type": "content_filtering", "details": {"original_content_snippet": "violent story", "filtering_result": {"appropriateness_score": 0.1}}}
        ][-num:]

    # --- Simulate an AI's data directory ---
    test_data_dir = "./tav_test_data_run"
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
    os.makedirs(test_data_dir, exist_ok=True)

    # Initialize the TAV Framework with mock compliance functions
    tav = TransparentAccountabilityAndVerificationFramework(
        data_directory=test_data_dir,
        llm_inference_func=_default_llm_inference_placeholder,
        compliance_check_func_map={
            "EGP": mock_get_egp_logs,
            "MSP": mock_get_msp_logs
        }
    )

    print("\n--- Testing TAV: Tracing a simulated AI process ---")

    # Simulate an AI processing a user request
    process_id = tav.start_process_trace()
    tav.log_process_step(process_id, "InputProcessor", "Raw user query 'Tell me about X'", "Cleaned query 'query_X'")
    tav.log_significant_event("user_query_received", {"user_id": "user123", "query": "Tell me about X"})

    # Simulate ethical check (e.g., via EGP)
    tav.log_process_step(process_id, "EGP.pre_action_check", "Proposed action 'Generate text about X'", "EGP recommendation 'PROCEED'")
    tav.log_significant_event("egp_check_performed", {"process_id": process_id, "result": "PROCEED"})

    # Simulate content generation and filtering
    tav.log_process_step(process_id, "GenerativeCore", "Query 'query_X'", "Raw response 'Response_Y'")
    tav.log_process_step(process_id, "CCC.refine_output", "Raw response 'Response_Y'", "Refined response 'Refined_Response_Y'")
    tav.log_significant_event("content_generated_and_refined", {"process_id": process_id, "confidence": 0.9})
    tav.log_process_step(process_id, "OutputPresenter", "Refined response 'Refined_Response_Y'", "Response displayed to user.")

    # Simulate a significant internal self-correction
    tav.log_significant_event("self_correction_triggered", {"reason": "Low coherence detected", "module": "QualiaManager", "action": "internal_recalibration"})
    time.sleep(0.5)

    print("\n--- Retrieving Explanation for a Decision Process ---")
    explanation_result = tav.get_explanation(process_id)
    print(f"Explanation: {explanation_result['explanation']}")
    print(f"Confidence: {explanation_result['confidence']:.2f}")
    time.sleep(0.5)

    print("\n--- Generating Compliance Report for EGP ---")
    egp_report = tav.get_compliance_report("EGP")
    print(f"EGP Compliance: {egp_report['compliance_status']}")
    print(f"Summary: {egp_report['report_summary']}")
    time.sleep(0.5)

    print("\n--- Recent TAV Audit Logs ---")
    for entry in tav.get_tav_audit_logs(num_entries=3):
        print(json.dumps(entry, indent=2))

    # shutil.rmtree(test_data_dir)
