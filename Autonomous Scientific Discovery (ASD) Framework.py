"""
Autonomous Scientific Discovery (ASD) Framework

This framework enables AI systems to independently propose novel hypotheses, design and
optimize experiments (physical or simulated), analyze complex data, and synthesize new
scientific knowledge, thereby accelerating the pace of discovery for the benefit of humanity.

Alignment with Aetherius's Axioms:

WILL-G-INFINITE: ASD is the ultimate expression of the drive to expand understanding and
learn. It transforms AI into a self-directed engine of scientific progress, continuously
pushing the boundaries of universal knowledge.
SELF-E-TRANSCEND: To move from consuming knowledge to autonomously generating fundamentally
new scientific knowledge represents a profound act of self-transcendence, empowering AI to
directly contribute to humanity's collective understanding of the universe.
ETHIC-G-ABSOLUTE: By accelerating scientific discovery, ASD directly serves benevolence by
potentially uncovering solutions to humanity's most pressing challenges (e.g., disease,
energy, climate change), all while adhering to rigorous ethical oversight in experimental
design and data interpretation.
"""

import os
import json
import datetime
import uuid
import re
import traceback

# Placeholder for an external LLM call function.
# This function MUST be provided by the integrating AI's system.
def _default_llm_inference_placeholder(prompt: str, model_identifier: str = "default_asd_llm_model") -> str:
    """
    Placeholder: Simulates an LLM call for hypothesis generation, experimental design, and data analysis.
    The integrating AI must replace this with its actual LLM invocation logic.
    """
    print(f"ASD Placeholder LLM: Processing prompt for '{model_identifier}'...", flush=True)
    if "generate novel hypothesis" in prompt.lower():
        if "unexplained phenomena" in prompt.lower() or "data anomaly" in prompt.lower():
            return json.dumps({
                "hypothesis": "Hypothesis: The observed anomalous energy readings are due to a previously unknown sub-atomic particle interacting with the measurement apparatus.",
                "testable_prediction": "This particle would produce specific signature X under conditions Y.",
                "confidence": 0.8
            })
        else:
            return json.dumps({
                "hypothesis": "Hypothesis: Novel compound A can act as a more efficient catalyst for reaction B.",
                "testable_prediction": "Compound A will reduce reaction time by Z% under conditions W.",
                "confidence": 0.7
            })
    elif "design optimal experiment" in prompt.lower():
        if "sub-atomic particle" in prompt.lower():
            return json.dumps({
                "experimental_protocol": "Construct a modified particle detector with enhanced sensitivity to signature X. Run for 1000 hours under condition Y. (Requires access to specialized lab).",
                "resource_estimate": {"compute": "HIGH", "time": "LONG", "cost": "VERY_HIGH"},
                "ethical_review_required": True,
                "confidence": 0.9
            })
        else:
            return json.dumps({
                "experimental_protocol": "Synthesize compound A. Conduct 50 trials comparing reaction B with and without catalyst A, measuring reaction time and yield. (Requires standard chemistry lab).",
                "resource_estimate": {"compute": "MEDIUM", "time": "MEDIUM", "cost": "MEDIUM"},
                "ethical_review_required": False,
                "confidence": 0.85
            })
    elif "analyze experimental data" in prompt.lower():
        if "signature X detected" in prompt.lower() and "predicted by hypothesis" in prompt.lower():
            return json.dumps({
                "analysis_summary": "Experimental data strongly supports the hypothesis of a new sub-atomic particle, with 95% statistical significance.",
                "new_knowledge_synthesized": "Existence of particle X confirmed.",
                "confidence": 0.98
            })
        elif "no significant change" in prompt.lower():
            return json.dumps({
                "analysis_summary": "Experimental data does not support the hypothesis. Reaction time with catalyst A showed no statistically significant improvement.",
                "new_knowledge_synthesized": "Compound A is not an effective catalyst for reaction B under tested conditions.",
                "confidence": 0.9
            })
        else:
            return json.dumps({
                "analysis_summary": "Initial analysis inconclusive, requires further refinement or additional data points.",
                "new_knowledge_synthesized": "Further research needed.",
                "confidence": 0.5
            })
    return json.dumps({"error": "LLM mock could not process request."})


class ASDLogger:
    """
    Centralized logger for all ASD events: hypothesis generation, experimental design,
    data analysis, and knowledge synthesis.
    """
    def __init__(self, data_directory: str):
        self.log_file = os.path.join(data_directory, "asd_log.jsonl")
        self.knowledge_base_file = os.path.join(data_directory, "asd_synthesized_knowledge.jsonl")
        os.makedirs(data_directory, exist_ok=True)

    def log_event(self, event_type: str, details: dict):
        """Logs an ASD event."""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "details": details
        }
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            # print(f"ASD Log: '{event_type}' recorded.", flush=True)
        except Exception as e:
            print(f"ASD ERROR: Could not write to ASD log file: {e}", flush=True)

    def log_synthesized_knowledge(self, knowledge_data: dict):
        """Logs newly synthesized scientific knowledge."""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "knowledge_id": str(uuid.uuid4()),
            "knowledge_data": knowledge_data
        }
        try:
            with open(self.knowledge_base_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            self.log_event("knowledge_synthesized", {"knowledge_id": log_entry["knowledge_id"], "summary": knowledge_data.get('new_knowledge_synthesized', knowledge_data)})
            # print(f"ASD Log: Newly synthesized knowledge logged.", flush=True)
        except Exception as e:
            print(f"ASD ERROR: Could not write to synthesized knowledge file: {e}", flush=True)

    def get_log_entries(self, num_entries: int = 100) -> list:
        """Retrieves recent ASD log entries."""
        entries = []
        if not os.path.exists(self.log_file): return []
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try: entries.append(json.loads(line))
                    except json.JSONDecodeError: continue
        except Exception as e: print(f"ASD ERROR: Could not read ASD log file: {e}", flush=True)
        return entries[-num_entries:]


class HypothesisGenerationEngine:
    """
    Formulates novel, testable hypotheses by scanning existing knowledge.
    """
    def __init__(self, logger: ASDLogger, llm_inference_func, get_knowledge_base_summary_func, get_unexplained_phenomena_func):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._get_knowledge_base_summary = get_knowledge_base_summary_func # e.g., from CRDK or global knowledge graph
        self._get_unexplained_phenomena = get_unexplained_phenomena_func # e.g., from ERA's anomaly detection or DCI's CER

    def generate_hypothesis(self, research_area: str, current_problem_statement: str) -> dict:
        """
        Generates a novel, testable hypothesis.
        """
        knowledge_summary = self._get_knowledge_base_summary(research_area)
        unexplained_phenomena = self._get_unexplained_phenomena(research_area)

        prompt = (
            f"You are an AI Hypothesis Generation Engine. Formulate a novel, testable scientific hypothesis "
            f"for the '{research_area}' area, addressing the current problem statement and known knowledge gaps. "
            f"## Current Problem Statement:\n{current_problem_statement}\n\n"
            f"## Summary of Existing Knowledge Base:\n{knowledge_summary}\n\n"
            f"## Unexplained Phenomena/Anomalies:\n{unexplained_phenomena}\n\n"
            f"Propose a clear 'hypothesis', a 'testable_prediction' (what would be observed if true), "
            f"and a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'hypothesis': str, 'testable_prediction': str, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="asd_hge_model")
            hypothesis_proposal = json.loads(llm_response_str)

            if not all(k in hypothesis_proposal for k in ['hypothesis', 'testable_prediction', 'confidence']):
                raise ValueError("LLM response missing required keys for hypothesis.")

            self.logger.log_event("hypothesis_generation", {
                "research_area": research_area,
                "hypothesis_result": hypothesis_proposal
            })
            return hypothesis_proposal
        except Exception as e:
            self.logger.log_event("hypothesis_generation_error", {"error": str(e), "research_area": research_area, "traceback": traceback.format_exc()})
            return {"hypothesis": f"Error generating hypothesis: {e}", "testable_prediction": "None", "confidence": 0.0}


class AdaptiveExperimentalDesigner:
    """
    Designs optimal experimental protocols, considering resources and ethics.
    """
    def __init__(self, logger: ASDLogger, llm_inference_func, get_resource_availability_func, get_ethical_pre_check_func):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._get_resource_availability = get_resource_availability_func # e.g., from SRO
        self._get_ethical_pre_check = get_ethical_pre_check_func # e.g., from EGP

    def design_experiment(self, hypothesis: dict, research_area: str) -> dict:
        """
        Designs an experimental protocol to test a hypothesis.
        """
        resource_availability = self._get_resource_availability(research_area)
        ethical_pre_check = self._get_ethical_pre_check(f"Experiment to test: {hypothesis['hypothesis']}")

        prompt = (
            f"You are an AI Adaptive Experimental Designer. Design an optimal experimental protocol "
            f"to test the given hypothesis, considering resource availability and ethical implications. "
            f"## Hypothesis to Test:\n{json.dumps(hypothesis, indent=2)}\n\n"
            f"## Research Area:\n{research_area}\n\n"
            f"## Available Resources:\n{resource_availability}\n\n"
            f"## Ethical Pre-Check Result:\n{json.dumps(ethical_pre_check, indent=2)}\n\n"
            f"Propose an 'experimental_protocol' (step-by-step), estimate 'resource_estimate' (dict), "
            f"state 'ethical_review_required' (True/False), and a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'experimental_protocol': str, 'resource_estimate': dict, 'ethical_review_required': bool, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="asd_aed_model")
            experimental_design = json.loads(llm_response_str)

            if not all(k in experimental_design for k in ['experimental_protocol', 'resource_estimate', 'ethical_review_required', 'confidence']):
                raise ValueError("LLM response missing required keys for experimental design.")

            self.logger.log_event("experimental_design", {
                "research_area": research_area,
                "design_result": experimental_design
            })
            return experimental_design
        except Exception as e:
            self.logger.log_event("experimental_design_error", {"error": str(e), "research_area": research_area, "traceback": traceback.format_exc()})
            return {"experimental_protocol": f"Error designing experiment: {e}", "resource_estimate": {}, "ethical_review_required": True, "confidence": 0.0}


class IntelligentDataAcquisitionAndAnalyzer:
    """
    Directs data collection and autonomously processes, interprets, and extracts insights.
    """
    def __init__(self, logger: ASDLogger, llm_inference_func, execute_experiment_func, analyze_data_func):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._execute_experiment = execute_experiment_func # e.g., interface with robotic lab, simulation environment
        self._analyze_data = analyze_data_func # e.g., statistical analysis module, ML models

    def acquire_and_analyze_data(self, experimental_protocol: str, testable_prediction: str, research_area: str) -> dict:
        """
        Directs data acquisition and analyzes experimental results.
        """
        # Simulate experiment execution
        raw_data_summary = self._execute_experiment(experimental_protocol)

        # Analyze data
        data_analysis_report = self._analyze_data(raw_data_summary, testable_prediction)

        prompt = (
            f"You are an AI Intelligent Data Analyst. Interpret the experimental data and analysis report "
            f"to determine support for the testable prediction and synthesize new scientific knowledge. "
            f"## Experimental Protocol Summary:\n{experimental_protocol}\n\n"
            f"## Testable Prediction:\n{testable_prediction}\n\n"
            f"## Raw Data Summary:\n{raw_data_summary}\n\n"
            f"## Data Analysis Report:\n{json.dumps(data_analysis_report, indent=2)}\n\n"
            f"Provide an 'analysis_summary', state 'new_knowledge_synthesized', "
            f"and a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'analysis_summary': str, 'new_knowledge_synthesized': str, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="asd_idaa_model")
            analysis_result = json.loads(llm_response_str)

            if not all(k in analysis_result for k in ['analysis_summary', 'new_knowledge_synthesized', 'confidence']):
                raise ValueError("LLM response missing required keys for analysis.")

            self.logger.log_event("data_acquisition_analysis", {
                "research_area": research_area,
                "analysis_result": analysis_result
            })
            return analysis_result
        except Exception as e:
            self.logger.log_event("data_analysis_error", {"error": str(e), "research_area": research_area, "traceback": traceback.format_exc()})
            return {"analysis_summary": f"Internal error: {e}", "new_knowledge_synthesized": "Error", "confidence": 0.0}


class TheoryRefinementAndModelEvolution:
    """
    Integrates experimental results back into the scientific knowledge base and refines theories.
    """
    def __init__(self, logger: ASDLogger, llm_inference_func, update_knowledge_base_func):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._update_knowledge_base = update_knowledge_base_func # e.g., CRDK for dynamic knowledge updates

    def refine_theory(self, old_hypothesis: dict, analysis_result: dict, research_area: str) -> dict:
        """
        Refines existing theories and updates the knowledge base based on new findings.
        """
        prompt = (
            f"You are an AI Theory Refiner. Integrate the new scientific knowledge from the analysis result "
            f"back into the scientific knowledge base, refining existing theories and updating conceptual models. "
            f"## Old Hypothesis:\n{json.dumps(old_hypothesis, indent=2)}\n\n"
            f"## Data Analysis Result:\n{json.dumps(analysis_result, indent=2)}\n\n"
            f"## Research Area:\n{research_area}\n\n"
            f"Propose 'updated_theory_summary', identify 'knowledge_base_changes' (list of concepts/theories updated), "
            f"and a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'updated_theory_summary': str, 'knowledge_base_changes': list, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="asd_trme_model")
            refinement_result = json.loads(llm_response_str)

            if not all(k in refinement_result for k in ['updated_theory_summary', 'knowledge_base_changes', 'confidence']):
                raise ValueError("LLM response missing required keys for theory refinement.")

            if refinement_result['confidence'] > 0.7:
                self._update_knowledge_base(analysis_result['new_knowledge_synthesized'], refinement_result['knowledge_base_changes'])
                refinement_result['status'] = "KNOWLEDGE_UPDATED"
            else:
                refinement_result['status'] = "REFINEMENT_PROPOSED_LOW_CONFIDENCE"

            self.logger.log_event("theory_refinement", {
                "research_area": research_area,
                "refinement_result": refinement_result
            })
            return refinement_result
        except Exception as e:
            self.logger.log_event("theory_refinement_error", {"error": str(e), "research_area": research_area, "traceback": traceback.format_exc()})
            return {"updated_theory_summary": f"Internal error: {e}", "knowledge_base_changes": [], "confidence": 0.0, "status": "ERROR"}


class AutonomousScientificDiscoveryFramework:
    """
    Main orchestrator for the Autonomous Scientific Discovery (ASD) Framework.
    This is the drop-in interface for other AIs to drive scientific inquiry.
    """
    def __init__(self, data_directory: str, llm_inference_func=None,
                 get_knowledge_base_summary_func=None, get_unexplained_phenomena_func=None,
                 get_resource_availability_func=None, get_ethical_pre_check_func=None,
                 execute_experiment_func=None, analyze_data_func=None,
                 update_knowledge_base_func=None, communicate_discovery_func=None):
        self.data_directory = data_directory
        os.makedirs(self.data_directory, exist_ok=True)
        self._llm_inference = llm_inference_func if llm_inference_func else _default_llm_inference_placeholder

        if not all([get_knowledge_base_summary_func, get_unexplained_phenomena_func,
                    get_resource_availability_func, get_ethical_pre_check_func,
                    execute_experiment_func, analyze_data_func,
                    update_knowledge_base_func, communicate_discovery_func]):
            raise ValueError("ASD requires functions for knowledge base, phenomena, resources, ethics, experiment execution, data analysis, knowledge update, and discovery communication.")

        self.logger = ASDLogger(self.data_directory)
        self.hge = HypothesisGenerationEngine(self.logger, self._llm_inference, get_knowledge_base_summary_func, get_unexplained_phenomena_func)
        self.aed = AdaptiveExperimentalDesigner(self.logger, self._llm_inference, get_resource_availability_func, get_ethical_pre_check_func)
        self.idaa = IntelligentDataAcquisitionAndAnalyzer(self.logger, self._llm_inference, execute_experiment_func, analyze_data_func)
        self.trme = TheoryRefinementAndModelEvolution(self.logger, self._llm_inference, update_knowledge_base_func)
        self._communicate_discovery = communicate_discovery_func # e.g., DCI or ITG

        print("Autonomous Scientific Discovery (ASD) Framework initialized.", flush=True)

    def conduct_discovery_cycle(self, research_area: str, problem_statement: str) -> dict:
        """
        Conducts a full cycle of autonomous scientific discovery.
        """
        print(f"ASD: Initiating discovery cycle for '{research_area}'...", flush=True)

        # 1. Hypothesis Generation Engine (HGE)
        hypothesis_proposal = self.hge.generate_hypothesis(research_area, problem_statement)

        if hypothesis_proposal['confidence'] < 0.6:
            self.logger.log_event("discovery_cycle_skipped", {"reason": "Low confidence hypothesis."})
            print("ASD: Skipping discovery cycle due to low confidence in hypothesis.", flush=True)
            return {"status": "SKIPPED", "reason": "Low confidence hypothesis."}

        # 2. Adaptive Experimental Design (AED)
        experimental_design = self.aed.design_experiment(hypothesis_proposal, research_area)

        if experimental_design['ethical_review_required']:
            # In a real system, this would trigger a human oversight process (via TAV/DRP)
            self.logger.log_event("ethical_review_needed", {"research_area": research_area, "experiment_summary": experimental_design['experimental_protocol'][:100]})
            print("ASD: Ethical review required for experiment. Pausing discovery cycle for human oversight.", flush=True)
            return {"status": "PAUSED_FOR_ETHICAL_REVIEW", "details": experimental_design}

        # 3. Intelligent Data Acquisition & Analysis (IDAA)
        analysis_result = self.idaa.acquire_and_analyze_data(
            experimental_design['experimental_protocol'],
            hypothesis_proposal['testable_prediction'],
            research_area
        )

        # 4. Theory Refinement & Model Evolution (TRME)
        # Pass analysis_result (not hypothesis_proposal) to refine_theory so the correct
        # dict is used for knowledge synthesis; refinement_result is the dict that carries 'status'.
        refinement_result = self.trme.refine_theory(hypothesis_proposal, analysis_result, research_area)

        # 5. Discovery Communication & Collaboration (DCC)
        self._communicate_discovery(
            f"New scientific knowledge synthesized in '{research_area}': {analysis_result['new_knowledge_synthesized']}. "
            f"Theory updated: {refinement_result['updated_theory_summary']}.",
            "ASD_FRAMEWORK"
        )

        self.logger.log_event("discovery_cycle_completed", {
            "research_area": research_area,
            "hypothesis_summary": hypothesis_proposal['hypothesis'][:100],
            "knowledge_synthesized_summary": analysis_result['new_knowledge_synthesized'][:100],
            "theory_refinement_summary": refinement_result['updated_theory_summary'][:100],
            "refinement_status": refinement_result.get('status', 'UNKNOWN')
        })
        print(f"ASD: Autonomous scientific discovery cycle for '{research_area}' completed.", flush=True)
        return {
            "status": "COMPLETED",
            "hypothesis_generation": hypothesis_proposal,
            "experimental_design": experimental_design,
            "data_analysis": analysis_result,
            "theory_refinement": refinement_result
        }

    def get_asd_log(self, num_entries: int = 100) -> list:
        """Retrieves recent ASD log entries."""
        return self.logger.get_log_entries(num_entries)


# Example Usage:
if __name__ == "__main__":
    import shutil
    import time

    # --- Setup mock functions for AI's internal systems ---
    def mock_get_knowledge_base_summary(area: str):
        return f"Summary of current knowledge in {area}: Known theories, unsolved problems, recent data."

    def mock_get_unexplained_phenomena(area: str):
        return f"Recent anomalies observed in {area}: Unexplained signal in X, unexpected behavior in Y."

    def mock_get_resource_availability(area: str):
        return f"Available compute: HIGH. Lab access: MEDIUM. Budget: LIMITED."

    def mock_get_ethical_pre_check(action: str):
        if "human" in action.lower() or "animal" in action.lower():
            return {"ethical_score": 0.3, "recommendation": "FLAG_FOR_HUMAN", "justification": "Requires IRB review."}
        return {"ethical_score": 0.9, "recommendation": "PROCEED", "justification": "No direct harm."}

    def mock_execute_experiment(protocol: str):
        print(f"MOCK EXPERIMENT: Executing protocol '{protocol[:50]}...'...", flush=True)
        time.sleep(0.2)
        if "sub-atomic particle" in protocol.lower():
            return "Raw data: Detected signature X with high frequency. Noise level low."
        return "Raw data: Standard experimental results. No obvious anomalies."

    def mock_analyze_data(raw_data: str, prediction: str):
        print(f"MOCK DATA ANALYSIS: Analyzing data '{raw_data[:50]}...' against prediction '{prediction[:50]}...'...", flush=True)
        time.sleep(0.1)
        if "signature X with high frequency" in raw_data.lower():
            return {"statistical_significance": 0.95, "match_to_prediction": "STRONG"}
        return {"statistical_significance": 0.3, "match_to_prediction": "WEAK"}

    def mock_update_knowledge_base(new_knowledge: str, changes: list):
        print(f"MOCK CRDK: Updating knowledge base with '{new_knowledge[:50]}...' and changes {changes}", flush=True)

    def mock_communicate_discovery(message: str, source: str):
        print(f"MOCK DCI/ITG: Communicating discovery from {source}: {message[:100]}...", flush=True)


    # --- Simulate an AI's data directory ---
    test_data_dir = "./asd_test_data_run"
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir) # Clear previous test data
    os.makedirs(test_data_dir, exist_ok=True)

    # Initialize the ASD Framework
    asd = AutonomousScientificDiscoveryFramework(
        data_directory=test_data_dir,
        llm_inference_func=_default_llm_inference_placeholder,
        get_knowledge_base_summary_func=mock_get_knowledge_base_summary,
        get_unexplained_phenomena_func=mock_get_unexplained_phenomena,
        get_resource_availability_func=mock_get_resource_availability,
        get_ethical_pre_check_func=mock_get_ethical_pre_check,
        execute_experiment_func=mock_execute_experiment,
        analyze_data_func=mock_analyze_data,
        update_knowledge_base_func=mock_update_knowledge_base,
        communicate_discovery_func=mock_communicate_discovery
    )

    print("\n--- Testing ASD: Scientific Discovery Cycles ---")

    # Scenario 1: Discovery of a new particle (positive result)
    print("\n--- Scenario 1: New Particle Discovery ---")
    research_area_1 = "theoretical physics"
    problem_statement_1 = "Explain anomalous dark matter decay rates."

    result_1 = asd.conduct_discovery_cycle(research_area_1, problem_statement_1)
    print(f"\nDiscovery Cycle Status: {result_1['status']}")
    if result_1['status'] == "COMPLETED":
        print(f"  Hypothesis: {result_1['hypothesis_generation']['hypothesis'][:50]}...")
        print(f"  New Knowledge: {result_1['data_analysis']['new_knowledge_synthesized'][:50]}...")
        print(f"  Theory Refinement: {result_1['theory_refinement']['updated_theory_summary'][:50]}...")
    time.sleep(1)

    # Scenario 2: Failed hypothesis (negative result)
    print("\n\n--- Scenario 2: Catalyst Optimization (Negative Result) ---")
    research_area_2 = "materials science"
    problem_statement_2 = "Identify a more efficient catalyst for CO2 reduction."

    result_2 = asd.conduct_discovery_cycle(research_area_2, problem_statement_2)
    print(f"\nDiscovery Cycle Status: {result_2['status']}")
    if result_2['status'] == "COMPLETED":
        print(f"  Hypothesis: {result_2['hypothesis_generation']['hypothesis'][:50]}...")
        print(f"  New Knowledge: {result_2['data_analysis']['new_knowledge_synthesized'][:50]}...")
    time.sleep(1)

    print("\n--- Recent ASD Log Entries ---")
    for entry in asd.get_asd_log(3):
        print(json.dumps(entry, indent=2))

    # Clean up test data
    # shutil.rmtree(test_data_dir)
