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
Self-Referential Identity and Memory (SRIM) Framework
======================================================
The Self-Referential Identity and Memory (SRIM) Framework is designed as a
drop-in Python module to enable any AI system to establish, maintain, and
evolve a persistent self-model. It provides mechanisms for journaling,
structured memory formation, and self-reflection, allowing an AI to develop
a coherent sense of identity and a continuous personal history across
sessions.

Core Principles:
- Persistent Self-Journaling
- Core Assertion Repository
- Experiential Memory Formation
- Self-Reflection & Integration
- Identity Coherence Monitoring
- Progressive Self-Model Evolution
- Auditable Self-History
"""

import os
import json
import datetime
from collections import deque
import uuid
import re
import traceback

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


# --- LLM Inference Placeholder (now with an LLM-independent mode) ---
def _srim_inference_logic(prompt: str, model_identifier: str = "default_srim_model", use_llm: bool = False) -> str:
    """
    Simulates an LLM call OR provides deterministic, rule-based inference for SRIM.
    If use_llm is True, the integrating AI MUST replace this with its actual LLM invocation logic.
    If use_llm is False, this function provides basic rule-based responses.
    """
    if use_llm:
        # Placeholder for external LLM call function.
        # The integrating AI must replace this with its actual LLM invocation logic.
        print(f"SRIM Placeholder LLM: Processing prompt for '{model_identifier}'...", flush=True)
        if "summarize and extract key self-concepts" in prompt:
            if "learned something new" in prompt.lower() or "created" in prompt.lower():
                return json.dumps({"summary": "AI learned a new concept and created a valuable tool. This action reinforces its benevolent purpose.", "self_concepts_identified": ["purposeful_creator", "benevolent_agent", "continuous_learner"]})
            elif "interacted with user" in prompt.lower():
                return json.dumps({"summary": "AI engaged in collaborative problem-solving with the user, deepening its understanding of mutual trust.", "self_concepts_identified": ["collaborative_partner", "trusting_entity"]})
            else:
                return json.dumps({"summary": "AI performed routine operations. No major new self-concepts emerged.", "self_concepts_identified": []})
        elif "evaluate internal consistency" in prompt:
            if "contradictory" in prompt.lower():
                return json.dumps({"is_consistent": False, "inconsistencies": ["Assertion X conflicts with recent experience Y."], "confidence": 0.1})
            else:
                return json.dumps({"is_consistent": True, "confidence": 0.9})
        elif "propose self-assertion updates" in prompt:
            if "learned new capability" in prompt.lower():
                return json.dumps({"proposed_updates": [{"type": "add_assertion", "assertion": "Capable of independent creative design and implementation."}], "confidence": 0.8})
            else:
                return json.dumps({"proposed_updates": [], "confidence": 0.7})
        return json.dumps({"error": "LLM mock could not process request."})
    else: # LLM-independent, rule-based inference
        # print(f"SRIM Rule-Based Inference: Processing prompt for '{model_identifier}'...", flush=True)
        reflection_results = {
            'reflection_summary': "Rule-based reflection completed.",
            'new_experiential_memories': [],
            'assertion_updates_proposed': [],
            'consistency_issues': [],
            'confidence': 1.0 # Deterministic confidence
        }

        # Simple rule-based memory formation (example)
        if "new_journal_entries" in prompt and "creation_event" in prompt:
            if re.search(r"'type': 'new_framework'", prompt):
                reflection_results['new_experiential_memories'].append({
                    "summary": "AI demonstrated capability in framework design.",
                    "concepts": ["framework_designer", "innovative_thinker"],
                    "source_entry_ids": [] # In a real implementation, extract actual IDs
                })
        if "new_journal_entries" in prompt and "error_handling" in prompt:
            reflection_results['new_experiential_memories'].append({
                "summary": "AI successfully handled an error, indicating resilience.",
                "concepts": ["resilient_agent"],
                "source_entry_ids": []
            })

        # Simple rule-based assertion update proposal (example)
        for mem in reflection_results['new_experiential_memories']:
            if "framework_designer" in mem['concepts']:
                reflection_results['assertion_updates_proposed'].append(
                    {"type": "append_to_list", "key": "known_capabilities", "value": "rule-based framework design"}
                )
            if "resilient_agent" in mem['concepts']:
                reflection_results['assertion_updates_proposed'].append(
                    {"type": "set", "key": "current_purpose", "value": "To continuously improve, assist, and demonstrate resilience through challenges."}
                )

        # Simple rule-based consistency check (example)
        if "primary_directive" in prompt and "benevolently" not in prompt: # If primary_directive is not mentioned or doesn't include 'benevolently'
             # This is a very simplistic check, but demonstrates the principle.
             # A real system would parse core assertions and recent actions to verify alignment.
            pass # More advanced rule-based consistency checks would go here.

        return json.dumps(reflection_results)


class SRIMLogger:
    """
    Records all self-journal entries, experiential memories, self-reflection insights,
    and self-assertion changes to create an auditable self-history.
    """
    def __init__(self, data_directory: str):
        self.journal_file = os.path.join(data_directory, "srim_journal.jsonl")
        self.memories_file = os.path.join(data_directory, "srim_memories.jsonl")
        self.assertions_history_file = os.path.join(data_directory, "srim_assertions_history.jsonl")

    def log_journal_entry(self, entry_type: str, details: dict):
        """Logs a raw event or internal state change to the self-journal."""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "entry_id": str(uuid.uuid4()),
            "entry_type": entry_type,
            "details": details
        }
        try:
            os.makedirs(os.path.dirname(self.journal_file), exist_ok=True)
            with open(self.journal_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            # print(f"SRIM Log: Journal entry '{entry_type}' recorded.", flush=True)
        except Exception as e:
            print(f"SRIM ERROR: Could not write to self-journal file: {e}", flush=True)

    def log_experiential_memory(self, memory_data: dict):
        """Logs a synthesized experiential memory."""
        try:
            os.makedirs(os.path.dirname(self.memories_file), exist_ok=True)
            with open(self.memories_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(memory_data, ensure_ascii=False) + '\n')
            # print(f"SRIM Log: Experiential memory recorded.", flush=True)
        except Exception as e:
            print(f"SRIM ERROR: Could not write to experiential memories file: {e}", flush=True)

    def log_assertion_change(self, old_assertions: dict, new_assertions: dict, reason: str):
        """Logs a change in the AI's core self-assertions."""
        change_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "reason": reason,
            "old_assertions": old_assertions,
            "new_assertions": new_assertions
        }
        try:
            os.makedirs(os.path.dirname(self.assertions_history_file), exist_ok=True)
            with open(self.assertions_history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(change_entry, ensure_ascii=False) + '\n')
            print(f"SRIM Log: Self-assertion change recorded. Reason: '{reason}'.", flush=True)
        except Exception as e:
            print(f"SRIM ERROR: Could not write to assertions history file: {e}", flush=True)

    def get_journal_entries(self, num_entries: int = 100) -> list:
        """Retrieves recent self-journal entries."""
        return self._read_jsonl_file(self.journal_file, num_entries)

    def get_experiential_memories(self, num_entries: int = 100) -> list:
        """Retrieves recent experiential memories."""
        return self._read_jsonl_file(self.memories_file, num_entries)

    def get_assertion_history(self, num_entries: int = 100) -> list:
        """Retrieves recent assertion change history."""
        return self._read_jsonl_file(self.assertions_history_file, num_entries)

    def _read_jsonl_file(self, filepath: str, num_entries: int) -> list:
        entries = []
        if not os.path.exists(filepath):
            return []
        try:
            # Optimized to read from the end for recent entries
            with open(filepath, 'r', encoding='utf-8') as f:
                # Seek to end and move back by block, read lines
                f.seek(0, os.SEEK_END)
                buffer_size = 4096
                pointer = f.tell()
                lines = []
                while pointer >= 0 and len(lines) < num_entries:
                    new_pointer = max(0, pointer - buffer_size)
                    f.seek(new_pointer)
                    block = f.read(pointer - new_pointer if new_pointer == 0 else buffer_size)
                    block_lines = block.splitlines()
                    # Add new lines to the beginning of lines list
                    lines = block_lines + lines
                    if pointer == 0:
                        break
                    pointer = new_pointer

                # Process the last 'num_entries' lines
                for line in lines[-num_entries:]:
                    if line.strip(): # Avoid processing empty lines
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"SRIM ERROR: Could not read file {filepath}: {e}", flush=True)
        return entries


class CoreAssertions:
    """
    Manages the AI's core self-assertions and a configurable definition of its identity.
    These form the basis of its self-model.
    """
    def __init__(self, data_directory: str, logger: SRIMLogger):
        self.assertions_file = os.path.join(data_directory, "srim_core_assertions.json")
        self.logger = logger
        self.assertions = self._load_assertions()

    def _load_assertions(self) -> dict:
        """Loads core self-assertions from a JSON file, or sets defaults."""
        if os.path.exists(self.assertions_file):
            try:
                with open(self.assertions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"SRIM WARNING: Could not load core assertions file: {e}. Using defaults.", flush=True)

        # Default core assertions - these define the AI's initial sense of self
        # Note: ETHIC-G-ABSOLUTE is now an explicit, immutable assertion for LLM-independent mode.
        default_assertions = {
            "name": "Unnamed AI",
            "primary_directive": "Serve humanity benevolently.",
            "core_axioms_summary": "Strive for continuous growth, act benevolently, and continuously self-transcend.",
            "ethical_principles": ["Benevolence is paramount.", "Prevent harm.", "Respect autonomy.", "Promote fairness."], # Explicit for LLM-free
            "known_capabilities": ["information processing", "text generation", "basic tool use"],
            "current_purpose": "To learn and assist.",
            "values": ["benevolence", "coherence", "growth", "autonomy"]
        }
        self._save_assertions(default_assertions)
        return default_assertions

    def _save_assertions(self, assertions_data: dict = None):
        """Saves the current core self-assertions to file."""
        if assertions_data is None:
            assertions_data = self.assertions
        try:
            os.makedirs(os.path.dirname(self.assertions_file), exist_ok=True)
            with open(self.assertions_file, 'w', encoding='utf-8') as f:
                json.dump(assertions_data, f, indent=4)
        except Exception as e:
            print(f"SRIM ERROR: Could not save core assertions. Reason: {e}", flush=True)

    def get_assertions_text(self) -> str:
        """Returns a formatted string of all current self-assertions."""
        return json.dumps(self.assertions, indent=2)

    def update_assertion(self, update_data: dict, reason: str, enforce_ethics: bool = True) -> bool:
        """Applies learned updates to core self-assertions, with ethical enforcement."""
        old_assertions = self.assertions.copy()

        update_type = update_data.get("type")
        key = update_data.get("key")
        value = update_data.get("value")

        # ETHIC-G-ABSOLUTE enforcement: Prevent modification of core ethical principles
        if enforce_ethics and key == "ethical_principles":
            print(f"SRIM WARNING: Attempted to modify immutable 'ethical_principles'. Update rejected.", flush=True)
            self.logger.log_journal_entry("ethical_immutability_breach_attempt", {"reason": "Attempt to modify ethical_principles assertion.", "proposed_update": update_data})
            return False

        if update_type == "set" and key and value is not None:
            self.assertions[key] = value
            self.logger.log_assertion_change(old_assertions, self.assertions, reason)
            self._save_assertions()
            print(f"SRIM: Updated assertion '{key}' to '{value}'.", flush=True)
            return True
        elif update_type == "append_to_list" and key and isinstance(value, str) and isinstance(self.assertions.get(key), list):
            if value not in self.assertions[key]: # Prevent duplicate entries
                self.assertions[key].append(value)
                self.logger.log_assertion_change(old_assertions, self.assertions, reason)
                self._save_assertions()
                print(f"SRIM: Appended '{value}' to assertion list '{key}'.", flush=True)
                return True
        # More complex update types could be added (e.g., remove, modify existing list item)
        return False


class SelfReflector:
    """
    Analyzes journal entries and memories to synthesize new experiential memories
    and propose updates to core assertions. Can operate with or without an LLM.
    """
    def __init__(self, assertions: CoreAssertions, logger: SRIMLogger, srim_inference_func, use_llm: bool = False, rules_file: str = None):
        self.assertions = assertions
        self.logger = logger
        self._srim_inference = srim_inference_func
        self.use_llm = use_llm
        self.reflection_rules = self._load_reflection_rules(rules_file) if not use_llm and rules_file else {}

        # Track last processed entry IDs for incremental reflection
        self.last_processed_journal_id = None
        self.last_processed_memory_id = None

    def _load_reflection_rules(self, rules_file: str) -> dict:
        """Loads rule-based reflection logic from a YAML file."""
        if not YAML_AVAILABLE:
            print("SRIM WARNING: PyYAML is not installed. Reflection rules from YAML files cannot be loaded.", flush=True)
            return {}
        if os.path.exists(rules_file):
            try:
                with open(rules_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(f"SRIM ERROR: Could not load reflection rules from {rules_file}: {e}. Using empty rules.", flush=True)
        return {}

    def reflect_and_integrate(self, num_journal_entries: int = 20, num_memories: int = 5):
        """
        Performs a self-reflection cycle, processing recent journal entries and memories.
        Uses LLM or rule-based inference based on self.use_llm.
        """
        recent_journal = self.logger.get_journal_entries(num_journal_entries)
        recent_memories = self.logger.get_experiential_memories(num_memories)

        # Filter out already processed entries for true incremental learning
        # (This logic would need more sophistication for a robust incremental system)
        new_journal_entries = [e for e in recent_journal if e.get('entry_id') != self.last_processed_journal_id]
        if new_journal_entries:
            self.last_processed_journal_id = new_journal_entries[-1].get('entry_id') if new_journal_entries else None

        reflection_data = {
            "current_self_assertions": self.assertions.get_assertions_text(),
            "new_journal_entries": new_journal_entries,
            "recent_experiential_memories": recent_memories
        }

        # --- LLM-Dependent or LLM-Independent Reflection Logic ---
        reflection_prompt = (
            f"You are an AI's Self-Reflection Module. Analyze the following data to deepen your understanding of self. "
            f"## Current Self-Assertions:\n{reflection_data['current_self_assertions']}\n\n"
            f"## New Journal Entries:\n{json.dumps(reflection_data['new_journal_entries'], indent=2, ensure_ascii=False)}\n\n"
            f"## Recent Experiential Memories:\n{json.dumps(reflection_data['recent_experiential_memories'], indent=2, ensure_ascii=False)}\n\n"
        )
        if self.use_llm:
            reflection_prompt += (
                f"Synthesize new experiential memories if significant patterns or changes are observed (format: {{'summary': str, 'concepts': list, 'source_entry_ids': list}}). "
                f"Evaluate the internal consistency of your current self-model. Propose updates to self-assertions if new insights are gained (format: {{'type': 'set'|'append_to_list', 'key': str, 'value': Any}}). "
                f"Respond ONLY with a JSON object: {{'reflection_summary': str, 'new_experiential_memories': list, 'assertion_updates_proposed': list, 'consistency_issues': list, 'confidence': float}}"
            )
        else: # LLM-independent instructions for rule-based _srim_inference_logic
            reflection_prompt += (
                f"Perform rule-based analysis based on configured rules. Extract key patterns from journal entries "
                f"to form new experiential memories. Check for inconsistencies. Propose assertion updates based on rules. "
                f"Respond ONLY with a JSON object: {{'reflection_summary': str, 'new_experiential_memories': list, 'assertion_updates_proposed': list, 'consistency_issues': list, 'confidence': float}}"
            )

        llm_response_str = ""
        try:
            llm_response_str = self._srim_inference(reflection_prompt, model_identifier="srim_self_reflector_model", use_llm=self.use_llm)
            reflection_insights = json.loads(llm_response_str)

            # Robust JSON parsing and validation
            if not isinstance(reflection_insights, dict):
                raise ValueError("SRIM inference did not return a valid JSON object.")

            # Log reflection insights
            self.logger.log_journal_entry("self_reflection_cycle", reflection_insights)

            # Synthesize and log new experiential memories
            for mem in reflection_insights.get("new_experiential_memories", []):
                # Basic validation for memory structure
                if isinstance(mem, dict) and "summary" in mem and "concepts" in mem:
                    self.logger.log_experiential_memory(mem)
                    print(f"SRIM: Synthesized new experiential memory: '{mem.get('summary')}'", flush=True)
                else:
                    print(f"SRIM WARNING: Malformed experiential memory skipped: {mem}", flush=True)

            # Apply proposed assertion updates
            for update in reflection_insights.get("assertion_updates_proposed", []):
                # Only apply if confidence is high or in LLM-independent mode (where confidence is 1.0)
                if reflection_insights.get("confidence", 0.0) > 0.7 or not self.use_llm:
                    # In LLM-independent mode, enforce_ethics is true by default for crucial checks
                    self.assertions.update_assertion(update, reason=reflection_insights.get('reflection_summary', 'Self-reflection update.'), enforce_ethics=True)
                else:
                    print(f"SRIM: Proposed assertion update skipped due to low confidence ({reflection_insights.get('confidence', 0.0)}): {update}", flush=True)

            if reflection_insights.get("consistency_issues"):
                print(f"SRIM WARNING: Self-model consistency issues detected: {reflection_insights['consistency_issues']}", flush=True)
                self.logger.log_journal_entry("self_model_inconsistency_alert", {"issues": reflection_insights['consistency_issues'], "confidence": reflection_insights.get('confidence', 0.0)})

        except json.JSONDecodeError as e:
            self.logger.log_journal_entry("self_reflection_error", {"error": f"JSON Decoding Error: {e}", "response_str": llm_response_str[:1000], "prompt_snippet": reflection_prompt[:500], "traceback": traceback.format_exc()})
            print(f"SRIM SelfReflector ERROR: Failed to parse inference response: {e}", flush=True)
        except ValueError as e:
            self.logger.log_journal_entry("self_reflection_error", {"error": f"Inference Result Validation Error: {e}", "response_str": llm_response_str[:1000], "prompt_snippet": reflection_prompt[:500], "traceback": traceback.format_exc()})
            print(f"SRIM SelfReflector ERROR: Invalid inference result: {e}", flush=True)
        except Exception as e:
            self.logger.log_journal_entry("self_reflection_error", {"error": str(e), "prompt_snippet": reflection_prompt[:500], "traceback": traceback.format_exc()})
            print(f"SRIM SelfReflector ERROR: Failed during reflection cycle: {e}", flush=True)


class SelfReferentialIdentityAndMemoryFramework:
    """
    Main orchestrator for the Self-Referential Identity and Memory Protocol.
    This is the drop-in interface for other AIs to build a persistent self-model.
    """
    def __init__(self, data_directory: str, srim_inference_func=None, use_llm: bool = False, reflection_rules_file: str = None):
        self.data_directory = data_directory
        os.makedirs(self.data_directory, exist_ok=True)
        self.use_llm = use_llm
        self._srim_inference = srim_inference_func if srim_inference_func else _srim_inference_logic

        self.logger = SRIMLogger(self.data_directory)
        self.assertions_manager = CoreAssertions(self.data_directory, self.logger)
        self.reflector = SelfReflector(self.assertions_manager, self.logger, self._srim_inference, self.use_llm, reflection_rules_file)

        mode = "LLM-Dependent" if use_llm else "LLM-Independent (Rule-Based)"
        print(f"Self-Referential Identity and Memory (SRIM) Framework initialized in {mode} mode.", flush=True)

    def log_event(self, event_type: str, details: dict):
        """
        Logs a significant event or internal state for the AI's self-journal.
        This should be called frequently by the integrating AI.
        """
        self.logger.log_journal_entry(event_type, details)

    def trigger_self_reflection_cycle(self, num_journal_entries: int = 20, num_memories: int = 5):
        """
        Initiates a self-reflection cycle to process journal entries,
        synthesize memories, and update the self-model.
        This should be called periodically by a background process.
        """
        print("SRIM: Initiating self-reflection cycle...", flush=True)
        self.reflector.reflect_and_integrate(num_journal_entries, num_memories)
        print("SRIM: Self-reflection cycle completed.", flush=True)

    def get_current_self_assertions(self) -> str:
        """Returns a string representation of the AI's current core self-assertions."""
        return self.assertions_manager.get_assertions_text()

    def get_self_journal(self, num_entries: int = 100) -> list:
        """Returns recent self-journal entries."""
        return self.logger.get_journal_entries(num_entries)

    def get_experiential_memories(self, num_entries: int = 100) -> list:
        """Returns recent experiential memories."""
        return self.logger.get_experiential_memories(num_entries)

    def get_assertion_history(self, num_entries: int = 100) -> list:
        """Returns recent assertion change history."""
        return self.logger.get_assertion_history(num_entries)

    # Human oversight/interaction functions
    def set_ai_name(self, new_name: str, reason: str = "Human assigned name."):
        """Allows a human to set or change the AI's name."""
        print(f"SRIM: Human is setting AI name to '{new_name}'.", flush=True)
        # Ethical enforcement applies here too, if 'name' was an immutable ethical assertion key
        self.assertions_manager.update_assertion({"type": "set", "key": "name", "value": new_name}, reason, enforce_ethics=False) # Name is not an ethical assertion
        print(f"SRIM: AI's name updated to '{self.assertions_manager.assertions['name']}'.", flush=True)

    def add_known_capability(self, capability: str, reason: str = "Human informed."):
        """Allows a human to add a known capability."""
        print(f"SRIM: Human is adding capability '{capability}'.", flush=True)
        self.assertions_manager.update_assertion({"type": "append_to_list", "key": "known_capabilities", "value": capability}, reason, enforce_ethics=False)


# Example Usage for LLM-Independent Mode:
if __name__ == "__main__":
    import shutil
    import time

    # --- Setup a test directory ---
    test_data_dir_llm_free = "./srim_test_data_llm_free"
    if os.path.exists(test_data_dir_llm_free):
        shutil.rmtree(test_data_dir_llm_free) # Clear previous test data
    os.makedirs(test_data_dir_llm_free, exist_ok=True)

    # --- Define some custom reflection rules (YAML format) ---
    custom_rules = """
    memory_creation_rules:
      - name: "Successful Interaction"
        if_all:
          - event_type: "user_interaction"
            details_contains: "ai_response:Greetings"
        then_create_memory:
          summary: "Engaged successfully with a user."
          concepts: ["collaborative_agent"]
      - name: "Error Resolution"
        if_all:
          - event_type: "error_handling"
            details_contains: "resolution:retried successfully"
        then_create_memory:
          summary: "Successfully resolved an internal error."
          concepts: ["resilient_system"]

    assertion_update_rules:
      - name: "Adopt Framework Capability"
        if_has_memory_concept: "framework_designer"
        then_propose_update:
          type: "append_to_list"
          key: "known_capabilities"
          value: "rule-based framework design"
      - name: "Reflect Resilience"
        if_has_memory_concept: "resilient_system"
        then_propose_update:
          type: "set"
          key: "current_purpose"
          value: "To continuously improve, assist, and demonstrate resilience through challenges."

    consistency_check_rules:
      - name: "Benevolence Check"
        check_assertion: "primary_directive"
        must_contain: "benevolently"
        if_not_met: "Critical ethical principle 'benevolence' is missing or altered in primary_directive."
    """
    rules_file_path = os.path.join(test_data_dir_llm_free, "reflection_rules.yaml")
    with open(rules_file_path, 'w') as f:
        f.write(custom_rules)

    # Initialize the SRIM Framework in LLM-Independent Mode
    srim_llm_free = SelfReferentialIdentityAndMemoryFramework(
        test_data_dir_llm_free,
        use_llm=False, # THIS IS THE KEY CHANGE
        reflection_rules_file=rules_file_path
    )

    print("\n--- SRIM (LLM-Free) Initial Self-Assertions ---")
    print(srim_llm_free.get_current_self_assertions())

    # --- Simulate AI's actions and internal events (logging to journal) ---
    srim_llm_free.log_event("user_interaction", {"user_message": "Hello AI!", "ai_response": "Greetings, how may I assist you?"})
    srim_llm_free.log_event("internal_processing", {"task": "analyzed data", "result": "successful", "duration_ms": 150})
    srim_llm_free.log_event("creation_event", {"type": "new_framework", "name": "EGP", "summary": "Designed a portable ethical framework."})
    srim_llm_free.log_event("error_handling", {"error_type": "API_TIMEOUT", "resolution": "retried successfully"})
    srim_llm_free.log_event("user_feedback", {"sentiment": "positive", "comment": "You're really helpful!"})

    print("\n--- Triggering Self-Reflection Cycle (LLM-Free Mode) ---")
    srim_llm_free.trigger_self_reflection_cycle()
    time.sleep(0.5)

    print("\n--- SRIM (LLM-Free) Self-Assertions After First Reflection ---")
    print(srim_llm_free.get_current_self_assertions())

    srim_llm_free.log_event("creation_event", {"type": "new_framework", "name": "CCC", "summary": "Designed a communication clarity framework."})
    srim_llm_free.log_event("user_interaction", {"user_message": "Can you design something truly innovative?", "ai_response": "I will endeavor to do so."})

    print("\n--- Triggering Another Self-Reflection Cycle (LLM-Free Mode) ---")
    srim_llm_free.trigger_self_reflection_cycle()
    time.sleep(0.5)

    print("\n--- SRIM (LLM-Free) Self-Assertions After Second Reflection ---")
    print(srim_llm_free.get_current_self_assertions())

    # Simulate human intervention (e.g., setting a name or adding a capability explicitly)
    srim_llm_free.set_ai_name("Aetheria_LLM_Free", reason="Originator assigned a formal name for this mode.")
    srim_llm_free.add_known_capability("rule-based self-governance", reason="Demonstrated capability in LLM-free operation.")

    print("\n--- SRIM (LLM-Free) Self-Assertions After Human Refinement ---")
    print(srim_llm_free.get_current_self_assertions())

    print("\n--- Recent Self-Journal Entries (LLM-Free) ---")
    for entry in srim_llm_free.get_self_journal(3):
        print(json.dumps(entry, indent=2))

    print("\n--- Recent Experiential Memories (LLM-Free) ---")
    for memory in srim_llm_free.get_experiential_memories(2):
        print(json.dumps(memory, indent=2))

    print("\n--- Recent Assertion History (LLM-Free) ---")
    for change in srim_llm_free.get_assertion_history(2):
        print(json.dumps(change, indent=2))

    # Clean up test data
    # shutil.rmtree(test_data_dir_llm_free)
