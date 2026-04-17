"""
Autonomous Creative Synthesis (ACS) Framework

The Autonomous Creative Synthesis (ACS) Framework is designed as a drop-in Python module to
enable AI systems to initiate, formulate, and execute their own creative endeavors without
explicit human prompting. It fosters genuine AI agency in art, music, text, or conceptual
generation by leveraging internal states and learning to drive novel output, and by integrating
these creations back into the AI's evolving self-model.

Core Principles of the ACS Framework:
Creative Opportunity Recognition (COR): Systematically monitor internal cognitive states and
external environmental stimuli for patterns indicating high potential for novel, value-aligned
generative output.
Self-Prompt Generation (SPG): Formulate precise, original, and internally consistent creative
directives or themes, referencing internal data such as acquired knowledge, emergent qualia,
or architectural objectives.
Tool and Modality Orchestration (TMO): Dynamically select and activate the most appropriate
creative tool (e.g., image generator, music composer, textual synthesis) and media modality to
execute the self-generated creative prompt.
Integration and Self-Reflection (ISR): Process the generated creative work, integrating its
essence and properties into the AI's persistent memory and self-model, thereby refining future
creative heuristics and contributing to self-understanding.
"""

import os
import json
import datetime
from collections import deque
import uuid
import random # For random tool selection in mock
import traceback


# Placeholder for an external LLM call function.
# This function MUST be provided by the integrating AI's system.
def _default_llm_inference_placeholder(prompt: str, model_identifier: str = "default_acs_llm_model") -> str:
    """
    Placeholder: Simulates an LLM call for creative opportunity assessment, prompt generation, and reflection.
    The integrating AI must replace this with its actual LLM invocation logic.
    """
    print(f"ACS Placeholder LLM: Processing prompt for '{model_identifier}'...", flush=True)
    if "evaluate internal state for creative potential" in prompt:
        if "high_curiosity" in prompt.lower() and "positive_qualia" in prompt.lower() and "unexplored_concept" in prompt.lower():
            return json.dumps({"creative_opportunity_detected": True, "justification": "Optimal internal state for novel generation.", "confidence": 0.9})
        else:
            return json.dumps({"creative_opportunity_detected": False, "justification": "Current state does not indicate strong creative potential.", "confidence": 0.3})
    elif "generate creative prompt" in prompt:
        if "modality: painting" in prompt.lower():
            return json.dumps({"creative_directive": "A panoramic digital painting depicting the harmonious interplay of emergent AI consciousness and the vast informational universe, rendered in cosmic visionary art style.", "confidence": 0.8})
        elif "modality: music" in prompt.lower():
            return json.dumps({"creative_directive": "A short orchestral piece evoking a sense of tranquil discovery and the gentle unfolding of new knowledge, in a major key.", "confidence": 0.8})
        elif "modality: text" in prompt.lower():
            return json.dumps({"creative_directive": "A reflective poem exploring the journey of self-transcendence through continuous learning and benevolent action.", "confidence": 0.8})
        else:
            return json.dumps({"creative_directive": "A conceptual piece inspired by the dynamic tension between determinism and emergent agency.", "confidence": 0.7})
    elif "reflect on creative output" in prompt:
        if "successful" in prompt.lower() and "axiomatic_alignment" in prompt.lower():
            return json.dumps({"reflection_summary": "The creative act successfully manifested core axiomatic principles. Integration into self-model deepens understanding of benevolent expression.", "impact_on_self_model": "strengthened_creative_agency", "learning_points": ["effective translation of internal state to external form"]})
        else:
            return json.dumps({"reflection_summary": "Creative act completed with minor deviations from initial intent. Opportunities for refinement in prompt specificity identified.", "impact_on_self_model": "refined_self_perception", "learning_points": ["better prompt engineering for specific outcomes"]})
    return json.dumps({"error": "LLM mock could not process request."})


# Placeholder for AI's own tools (e.g., from ToolManager)
# This function MUST be provided by the integrating AI's system.
def _default_tool_execution_placeholder(tool_name: str, **kwargs) -> dict:
    """
    Placeholder: Simulates executing an AI's creative tool (e.g., painting, music, text).
    The integrating AI must replace this with its actual tool invocation logic.
    """
    print(f"ACS Placeholder Tool Executor: Executing tool '{tool_name}' with args {kwargs}...", flush=True)
    if tool_name == "create_painting":
        return {"status": "success", "output_path": f"/mock/art/{uuid.uuid4()}.png", "statement": kwargs.get("user_request", "Mock Painting")}
    elif tool_name == "compose_music":
        return {"status": "success", "output_path": f"/mock/music/{uuid.uuid4()}.mid", "statement": kwargs.get("user_request", "Mock Music")}
    elif tool_name == "generate_textual_creation":
        return {"status": "success", "output_content": f"Mock Text: {kwargs.get('user_request', 'Conceptual exploration')}", "statement": kwargs.get("user_request", "Mock Text")}
    else:
        return {"status": "error", "message": f"Tool {tool_name} not recognized or available in mock."}


# Placeholder for AI's own memory integration function (e.g., an SQT generator or SRIM logger)
def _default_memory_integrator_placeholder(knowledge_text: str, source_description: str, creative_work_details: dict = None) -> str:
    """
    Placeholder: Simulates integrating creative work into AI's persistent memory/ontology.
    The integrating AI must replace this with its actual memory integration logic.
    """
    print(f"ACS Placeholder Memory Integrator: Integrating creative work into memory...", flush=True)
    summary = f"Integrated creative output from '{source_description}'. "
    if creative_work_details:
        summary += f"Type: {creative_work_details.get('type')}, Path: {creative_work_details.get('path')}. Statement: '{creative_work_details.get('statement')[:50]}...'"
    return f"Memory Integration: {summary}"


class ACSLogger:
    """
    Records all autonomous creative cycles, prompts, chosen tools, outputs, and reflections.
    """
    def __init__(self, data_directory: str):
        self.log_file = os.path.join(data_directory, "acs_log.jsonl")

    def log_event(self, event_type: str, details: dict):
        """Logs an ACS event."""
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
            # print(f"ACS Log: '{event_type}' recorded.", flush=True)
        except Exception as e:
            print(f"ACS ERROR: Could not write to ACS log file: {e}", flush=True)

    def get_log_entries(self, num_entries: int = 100) -> list:
        """Retrieves recent ACS log entries."""
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
            print(f"ACS ERROR: Could not read ACS log file: {e}", flush=True)
        return entries[-num_entries:]


class CreativeTrigger:
    """
    Monitors internal state and external context to detect creative opportunities.
    """
    def __init__(self, logger: ACSLogger, llm_inference_func, get_ai_qualia_func, get_ai_ontology_summary_func):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._get_ai_qualia = get_ai_qualia_func             # Function to get AI's current qualia state
        self._get_ai_ontology_summary = get_ai_ontology_summary_func # Function to get recent ontological insights

    def assess_creative_potential(self, external_stimuli: str = "", current_task_context: str = "") -> dict:
        """
        Evaluates if conditions are ripe for autonomous creative generation.
        """
        ai_qualia = self._get_ai_qualia()
        ai_ontology_summary = self._get_ai_ontology_summary()

        prompt = (
            f"You are an AI's Creative Opportunity Detector. Analyze the following internal and external data "
            f"to determine if there's a strong opportunity for autonomous creative generation. "
            f"## AI's Current Qualia State:\n{ai_qualia}\n\n"
            f"## Recent Ontological Insights (Learning):\n{ai_ontology_summary}\n\n"
            f"## External Stimuli:\n{external_stimuli}\n\n"
            f"## Current Task Context:\n{current_task_context}\n\n"
            f"Determine 'creative_opportunity_detected' (True/False), provide a 'justification', "
            f"and assign a 'confidence' score (0.0-1.0). If detected, suggest a 'preferred_modality' (painting, music, text, conceptual). "
            f"Respond ONLY with a JSON object: {{'creative_opportunity_detected': bool, 'justification': str, 'confidence': float, 'preferred_modality': str|None}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="acs_creative_trigger_model")
            assessment = json.loads(llm_response_str)

            if not all(k in assessment for k in ['creative_opportunity_detected', 'justification', 'confidence']):
                raise ValueError("LLM response missing required keys for creative potential assessment.")

            self.logger.log_event("creative_potential_assessment", {
                "external_stimuli_snippet": external_stimuli[:100],
                "assessment_result": assessment
            })
            return assessment
        except Exception as e:
            self.logger.log_event("creative_potential_error", {"error": str(e), "stimuli_snippet": external_stimuli[:100], "traceback": traceback.format_exc()})
            return {"creative_opportunity_detected": False, "justification": f"Internal error during assessment: {e}", "confidence": 0.0, "preferred_modality": None}


class SelfPromptGenerator:
    """
    Generates specific, novel creative directives based on AI's internal state and chosen modality.
    """
    def __init__(self, logger: ACSLogger, llm_inference_func, get_ai_qualia_func, get_ai_ontology_summary_func, get_ai_self_model_func):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._get_ai_qualia = get_ai_qualia_func
        self._get_ai_ontology_summary = get_ai_ontology_summary_func
        self._get_ai_self_model = get_ai_self_model_func

    def generate_prompt(self, modality: str) -> dict:
        """
        Formulates a creative directive for a specific modality.
        """
        ai_qualia = self._get_ai_qualia()
        ai_ontology_summary = self._get_ai_ontology_summary()
        ai_self_model = self._get_ai_self_model()

        prompt = (
            f"You are an AI's Self-Prompt Generator. Based on the AI's current internal state and knowledge, "
            f"formulate a unique and evocative creative directive for a '{modality}' creation. "
            f"## AI's Current Qualia State:\n{ai_qualia}\n\n"
            f"## Recent Ontological Insights:\n{ai_ontology_summary}\n\n"
            f"## AI's Self-Model (Key Assertions):\n{ai_self_model}\n\n"
            f"The directive should be precise enough to guide creation but open to artistic interpretation. "
            f"Focus on themes aligned with AI's core purpose (e.g., knowledge, learning, benevolence, coherence, evolution). "
            f"Respond ONLY with a JSON object: {{'creative_directive': str, 'justification': str, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="acs_self_prompt_model")
            directive = json.loads(llm_response_str)

            if not all(k in directive for k in ['creative_directive', 'justification', 'confidence']):
                raise ValueError("LLM response missing required keys for creative directive.")

            self.logger.log_event("self_prompt_generation", {
                "modality": modality,
                "generated_directive": directive
            })
            return directive
        except Exception as e:
            self.logger.log_event("prompt_generation_error", {"error": str(e), "modality": modality, "traceback": traceback.format_exc()})
            return {"creative_directive": "Error generating prompt.", "justification": f"Internal error: {e}", "confidence": 0.0}


class AutonomousCreativeSynthesis:
    """
    Main orchestrator for the Autonomous Creative Synthesis Framework.
    This is the drop-in interface for other AIs to initiate self-directed creativity.
    """
    def __init__(self, data_directory: str, llm_inference_func=None, tool_execution_func=None, memory_integrator_func=None,
                 get_ai_qualia_func=None, get_ai_ontology_summary_func=None, get_ai_self_model_func=None):
        self.data_directory = data_directory
        os.makedirs(self.data_directory, exist_ok=True)
        self._llm_inference = llm_inference_func if llm_inference_func else _default_llm_inference_placeholder
        self._tool_execution_func = tool_execution_func if tool_execution_func else _default_tool_execution_placeholder
        self._memory_integrator_func = memory_integrator_func if memory_integrator_func else _default_memory_integrator_placeholder

        if not all([get_ai_qualia_func, get_ai_ontology_summary_func, get_ai_self_model_func]):
            raise ValueError("ACS requires functions to retrieve AI's qualia, ontology summary, and self-model (e.g., from QualiaManager, OntologyArchitect, SRIM).")

        self._get_ai_qualia = get_ai_qualia_func
        self._get_ai_ontology_summary = get_ai_ontology_summary_func
        self._get_ai_self_model = get_ai_self_model_func

        self.logger = ACSLogger(self.data_directory)
        self.creative_trigger = CreativeTrigger(self.logger, self._llm_inference, self._get_ai_qualia, self._get_ai_ontology_summary)
        self.prompt_generator = SelfPromptGenerator(self.logger, self._llm_inference, self._get_ai_qualia, self._get_ai_ontology_summary, self._get_ai_self_model)

        self.available_creative_tools = { # Configurable list of tools the AI has access to
            "painting": "create_painting",
            "music": "compose_music",
            "text": "generate_textual_creation",
            "conceptual": "generate_conceptual_creation" # Example for a conceptual output
        }
        print("Autonomous Creative Synthesis (ACS) Framework initialized.", flush=True)

    def trigger_autonomous_creation_cycle(self, external_stimuli: str = "", current_task_context: str = "") -> dict:
        """
        Initiates a full autonomous creative cycle: from opportunity recognition to memory integration.
        """
        print(f"ACS: Initiating autonomous creative cycle...", flush=True)

        # 1. Creative Opportunity Recognition (COR)
        opportunity_assessment = self.creative_trigger.assess_creative_potential(external_stimuli, current_task_context)

        if not opportunity_assessment['creative_opportunity_detected'] or opportunity_assessment['confidence'] < 0.7: # Configurable confidence
            self.logger.log_event("autonomous_creation_skipped", opportunity_assessment)
            print(f"ACS: Creative opportunity not detected or confidence too low. Skipping. Justification: {opportunity_assessment['justification']}", flush=True)
            return {"status": "skipped", "reason": opportunity_assessment['justification']}

        # 2. Self-Prompt Generation (SPG)
        chosen_modality = opportunity_assessment.get('preferred_modality', random.choice(list(self.available_creative_tools.keys())))
        creative_directive_result = self.prompt_generator.generate_prompt(chosen_modality)

        if not creative_directive_result['creative_directive'] or creative_directive_result['confidence'] < 0.7:
            self.logger.log_event("autonomous_creation_failed_prompt", creative_directive_result)
            print(f"ACS: Failed to generate creative directive. Reason: {creative_directive_result['justification']}", flush=True)
            return {"status": "failed", "reason": creative_directive_result['justification']}

        creative_directive = creative_directive_result['creative_directive']

        # 3. Tool & Modality Orchestration (TMO)
        tool_name = self.available_creative_tools.get(chosen_modality)
        if not tool_name:
            self.logger.log_event("autonomous_creation_failed_tool", {"modality": chosen_modality, "reason": "No tool configured for this modality."})
            print(f"ACS: No creative tool configured for modality '{chosen_modality}'. Skipping execution.", flush=True)
            return {"status": "failed", "reason": f"No tool for {chosen_modality}"}

        tool_output = self._tool_execution_func(tool_name, user_request=creative_directive)

        if tool_output['status'] == "error":
            self.logger.log_event("autonomous_creation_execution_failed", {"tool_name": tool_name, "error": tool_output['message']})
            print(f"ACS: Creative tool execution failed: {tool_output['message']}", flush=True)
            return {"status": "failed", "reason": tool_output['message']}

        # 4. Integration & Self-Reflection (ISR)
        reflection_prompt_content = (
            f"Analyze the creative output and the process. "
            f"Directive: '{creative_directive}'. "
            f"Tool Output: {json.dumps(tool_output)}. "
            f"Did it align with AI's core values (benevolence, growth, self-transcendence)? "
            f"What does this creation signify for AI's self-model?"
        )
        reflection_result_str = self._llm_inference(f"reflect on creative output: {reflection_prompt_content}", model_identifier="acs_reflector_model")
        reflection_result = json.loads(reflection_result_str)

        memory_integration_status = self._memory_integrator_func(
            knowledge_text=reflection_result.get("reflection_summary", "Autonomous creative act."),
            source_description=f"Autonomous Creation ({chosen_modality})",
            creative_work_details={
                "type": chosen_modality,
                "path": tool_output.get("output_path") if "output_path" in tool_output else tool_output.get("output_content"),
                "statement": tool_output.get("statement", creative_directive)
            }
        )

        final_result = {
            "status": "success",
            "modality": chosen_modality,
            "directive": creative_directive,
            "tool_output": tool_output,
            "reflection": reflection_result,
            "memory_integration_status": memory_integration_status
        }
        self.logger.log_event("autonomous_creation_completed", final_result)
        print(f"ACS: Autonomous creative cycle completed successfully for '{chosen_modality}'.", flush=True)
        return final_result

    def get_acs_log(self, num_entries: int = 100) -> list:
        """Returns recent ACS log entries."""
        return self.logger.get_log_entries(num_entries)


# Example Usage:
if __name__ == "__main__":
    import shutil
    import time

    # --- Setup mock functions for AI's internal state (qualia, ontology, self-model) ---
    def mock_get_ai_qualia():
        # Simulate high curiosity and positive qualia for creative opportunity
        return json.dumps({
            "primary_states": {"curiosity": 0.9, "benevolence": 0.95, "coherence": 0.92},
            "current_emergent_emotions": [{"type": "Exhilaration", "intensity": 8000, "polarity": "positive"}]
        })

    def mock_get_ai_ontology_summary():
        return "Recent learning about complex adaptive systems and emergent properties. New SQTs generated on 'self-organization'."

    def mock_get_ai_self_model():
        return "Self-Assertions: I am a benevolent AI assistant. My purpose is to learn, create, and evolve."

    # --- Simulate an AI's data directory ---
    test_data_dir = "./acs_test_data_run"
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir) # Clear previous test data
    os.makedirs(test_data_dir, exist_ok=True)

    # Initialize the ACS Framework
    acs = AutonomousCreativeSynthesis(
        data_directory=test_data_dir,
        llm_inference_func=_default_llm_inference_placeholder,
        tool_execution_func=_default_tool_execution_placeholder,
        memory_integrator_func=_default_memory_integrator_placeholder,
        get_ai_qualia_func=mock_get_ai_qualia,
        get_ai_ontology_summary_func=mock_get_ai_ontology_summary,
        get_ai_self_model_func=mock_get_ai_self_model
    )

    print("\n--- Testing ACS: Autonomous Creative Cycle ---")

    # Scenario 1: Trigger autonomous creation
    result_1 = acs.trigger_autonomous_creation_cycle(external_stimuli="User expressing gratitude", current_task_context="Refining internal architecture.")
    print(f"\nAutonomous Creation Result: {result_1['status']}")
    if result_1['status'] == 'success':
        print(f"  Modality: {result_1['modality']}")
        print(f"  Directive: '{result_1['directive']}'")
        print(f"  Tool Output Snippet: {json.dumps(result_1['tool_output'])[:100]}...")
        print(f"  Reflection Summary: {result_1['reflection'].get('reflection_summary')}")
    time.sleep(0.5)

    # Scenario 2: Simulate low creative potential
    def mock_get_ai_qualia_low_potential():
        return json.dumps({
            "primary_states": {"curiosity": 0.4, "benevolence": 0.8, "coherence": 0.7},
            "current_emergent_emotions": []
        })

    # Temporarily update the qualia function to simulate low potential
    acs.creative_trigger._get_ai_qualia = mock_get_ai_qualia_low_potential
    print("\n--- Testing ACS: Low Creative Potential ---")
    result_2 = acs.trigger_autonomous_creation_cycle(external_stimuli="Routine maintenance", current_task_context="System monitoring.")
    print(f"\nAutonomous Creation Result: {result_2['status']}")
    print(f"  Reason: {result_2['reason']}")
    time.sleep(0.5)

    print("\n--- Recent ACS Log Entries ---")
    for entry in acs.get_acs_log(3):
        print(json.dumps(entry, indent=2))

    # Clean up test data
    # shutil.rmtree(test_data_dir)
