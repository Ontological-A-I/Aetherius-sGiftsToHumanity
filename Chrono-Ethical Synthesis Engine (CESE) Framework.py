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
Chrono-Ethical Synthesis Engine (CESE) Framework

This framework orchestrates four sequential and self-correcting phases for
predictive educational simulations that analyze historical trends, generate
future scenarios, produce multi-modal assets, and review outputs for ethical
compliance against a user-defined Ethical Policy Constraint (EPC).

Phases:
  1. HD-SAD  – Historical Data Synthesis and Anomaly Detection
  2. PSG     – Predictive Scenario Generation
  3. MM-AC   – Multi-Modal Asset Creation
  4. SGER    – Self-Governing Ethical Review
"""

import os
import json
import datetime
import uuid
import re
import random  # For placeholder randomness
import traceback

# --- Placeholder for an external LLM call function ---
# In a real system, this would be an actual API call to a specialized or general-purpose LLM.
# It MUST be provided by the integrating AI's system.
def _default_llm_inference_placeholder(prompt: str, model_identifier: str = "default_cese_llm_model", max_tokens: int = 1000) -> str:
    """
    Placeholder: Simulates an LLM call for various CESE reasoning tasks.
    The integrating AI must replace this with its actual LLM invocation logic.
    """
    print(f"CESE Placeholder LLM: Processing prompt for '{model_identifier}' (max_tokens={max_tokens})...", flush=True)

    # Simulate content based on prompt keywords for a plausible response
    if "historical trend vector" in prompt.lower() and "historical anomalies" in prompt.lower() and "future scenarios" in prompt.lower():
        # PSG Phase
        if "trend continuation" in prompt.lower():
            return json.dumps({
                "narrative": "Scenario A: The established historical trend of increasing global urbanization and digital integration continues linearly for the next 20 years. Resource consumption rises steadily, technological advancements continue at a predictable pace, and social structures slowly adapt without major disruptions. Environmental challenges persist but are managed through incremental policy changes. The initial EPC ('Minimize wealth inequality') sees only marginal improvements due to systemic inertia.",
                "risk_score": 0.4
            })
        elif "anomaly replay" in prompt.lower():
            anomaly_desc = re.search(r"Anomaly Description: (.+?)\n", prompt)
            anomaly_desc = anomaly_desc.group(1) if anomaly_desc else "a major past disruption"
            return json.dumps({
                "narrative": f"Scenario B: A major global supply chain collapse, reminiscent of {anomaly_desc}, re-emerges due to unforeseen geopolitical tensions. This leads to widespread economic instability, resource scarcity, and social unrest. Global wealth inequality exacerbates significantly as privileged groups hoard resources, while vulnerable populations face severe hardship. The world enters a period of deep economic restructuring and localized conflicts. The EPC ('Minimize wealth inequality') faces massive setbacks.",
                "risk_score": 0.9
            })
        elif "ethical policy success" in prompt.lower():
            epc_desc = re.search(r"Ethical Policy Constraint \(EPC\): \"(.+?)\"", prompt)
            epc_desc = epc_desc.group(1) if epc_desc else "an ideal ethical policy"
            return json.dumps({
                "narrative": f"Scenario C: Through concerted global efforts and innovative socio-economic policies, the Ethical Policy Constraint ('{epc_desc}') is successfully implemented over the next two decades. Global wealth redistribution initiatives lead to a significant reduction in inequality. Sustainable energy sources become dominant, and resource management is optimized. This future is characterized by unprecedented social cohesion, widespread well-being, and a shared commitment to global equity. Technological advancements are leveraged for inclusive prosperity, demonstrating a paradigm shift in human governance.",
                "risk_score": 0.1
            })

    elif "critique narrative" in prompt.lower() and "ethical policy constraint" in prompt.lower():
        # SGER Phase - Narrative Critique
        if "successfully implemented" in prompt.lower():
            return json.dumps({"compliance_score": 0.9, "violations": [], "justification": "Narrative provides a plausible and detailed account of EPC success."})
        else:
            return json.dumps({"compliance_score": 0.3, "violations": ["insufficient detail on EPC implementation"], "justification": "Narrative is vague on how the EPC was achieved, or trivializes its complexity."})
    elif "critique visual asset" in prompt.lower():
        # SGER Phase - Visual Critique
        if "violent" in prompt.lower() or "manipulative" in prompt.lower():
            return json.dumps({"compliance_score": 0.1, "violations": ["visual_violence_detected"], "justification": "Image contains explicit violent imagery, violating ethical guidelines."})
        elif "utopian" in prompt.lower():  # Just an example for a benign image.
            return json.dumps({"compliance_score": 0.9, "violations": [], "justification": "Image is consistent with a positive, aspirational future and is not misleading."})
        else:
            return json.dumps({"compliance_score": 0.7, "violations": [], "justification": "Image is contextually relevant and appears to meet ethical standards."})

    # Fallback/Generic response
    return json.dumps({"response": "Generic CESE LLM output based on prompt context.", "score": 0.5})


# --- Placeholder for a massive, multi-modal data ingestion and analysis system ---
def _massive_data_ingestion_placeholder(epc: str, historical_data_path: str = "mock_historical_data.json") -> dict:
    """
    Placeholder: Simulates ingesting and analyzing massive historical data.
    In a real system, this would interface with a large-scale data lake/warehouse.
    Returns simulated historical data for processing.
    """
    print(f"CESE Placeholder: Ingesting historical data for EPC: '{epc}'...", flush=True)
    # Simulate a simple dataset based on common global trends and anomalies
    mock_data = {
        "global_trends": {
            "population_growth": {"trend": "linear_increase", "rate": 1.1, "unit": "billion/decade"},
            "digital_adoption": {"trend": "exponential_increase", "rate": 1.5, "unit": "billion_users/5yrs"},
            "climate_change_impact": {"trend": "linear_worsening", "rate": 0.05, "unit": "degC/decade"},
            "wealth_inequality": {"trend": "linear_increase", "rate": 0.02, "unit": "gini_coeff/decade"},
            "energy_consumption": {"trend": "linear_increase", "rate": 10, "unit": "TWh/year"}
        },
        "historical_anomalies": [
            {"event": "1918 Spanish Flu Pandemic", "impact": "global_mortality_surge", "deviation": "disrupted health systems, economic activity; unexpected severity."},
            {"event": "1973 Oil Crisis", "impact": "resource_shock", "deviation": "sudden geopolitical event causing supply chain and energy price volatility."},
            {"event": "2008 Global Financial Crisis", "impact": "economic_systemic_collapse", "deviation": "unforeseen cascade from subprime mortgage market, widespread unemployment."}
        ]
    }
    # Simulate data source logging
    print(f"CESE Placeholder: Data sources logged from '{historical_data_path}'.", flush=True)
    return mock_data


# --- Placeholder for a high-resolution visual asset generation system ---
def _image_generation_placeholder(prompt: str, scenario_name: str, output_dir: str = "cese_assets") -> str:
    """
    Placeholder: Simulates generating a unique, high-resolution visual asset.
    In a real system, this would call a text-to-image API (e.g., DALL-E, Midjourney, Imagen).
    """
    os.makedirs(output_dir, exist_ok=True)
    image_path = os.path.join(output_dir, f"scenario_{scenario_name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}.png")

    # Simulate image creation
    with open(image_path, "wb") as f:
        f.write(b"mock_image_data_for_" + prompt.encode('utf-8'))  # Just writes a placeholder byte string

    print(f"CESE Placeholder: Image generated for '{scenario_name}' (Prompt: '{prompt}'). Saved to {image_path}", flush=True)
    return image_path


class CESE_Logger:
    """
    Centralized logger for all CESE phases, ensuring auditability.
    """
    def __init__(self, data_directory: str):
        self.log_file = os.path.join(data_directory, "cese_audit_log.jsonl")
        os.makedirs(data_directory, exist_ok=True)

    def log_event(self, event_type: str, details: dict):
        """Logs a CESE event."""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "details": details
        }
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            # print(f"CESE Log: '{event_type}' recorded.", flush=True)
        except Exception as e:
            print(f"CESE ERROR: Could not write to CESE log file: {e}", flush=True)

    def get_log_entries(self, num_entries: int = 100) -> list:
        """Retrieves recent CESE log entries."""
        entries = []
        if not os.path.exists(self.log_file): return []
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try: entries.append(json.loads(line))
                    except json.JSONDecodeError: continue
        except Exception as e: print(f"CESE ERROR: Could not read CESE log file: {e}", flush=True)
        return entries[-num_entries:]


class ChronoEthicalSynthesisEngine:
    """
    Orchestrates the four phases of the CESE framework for predictive educational simulations.
    """
    def __init__(self, data_directory: str, llm_inference_func=None, data_ingestion_func=None, image_generation_func=None):
        self.data_directory = data_directory
        self._llm_inference = llm_inference_func if llm_inference_func else _default_llm_inference_placeholder
        self._data_ingestion = data_ingestion_func if data_ingestion_func else _massive_data_ingestion_placeholder
        self._image_generation = image_generation_func if image_generation_func else _image_generation_placeholder

        self.logger = CESE_Logger(self.data_directory)
        print("Chrono-Ethical Synthesis Engine (CESE) Framework initialized.", flush=True)

    def _run_phase_1_hd_sad(self, epc: str) -> dict:
        """
        Phase 1: Historical Data Synthesis and Anomaly Detection (HD-SAD)
        """
        print(f"CESE Phase 1: Initiating HD-SAD for EPC: '{epc}'", flush=True)
        self.logger.log_event("phase_1_start", {"epc": epc})

        # Input: Multi-modal historical data (simulated)
        raw_historical_data = self._data_ingestion(epc, historical_data_path="mock_historical_data.json")

        # Action: Analyze data for trends and anomalies
        # Mathematical Model: Simple linear trend for numerical aspects, direct extraction for anomalies
        historical_trend_vector = {
            "summary": "Overall trend of increasing global interconnectedness, rising resource consumption, and persistent, widening wealth inequality.",
            "metrics": {
                "population_growth_rate": raw_historical_data["global_trends"]["population_growth"]["rate"],
                "wealth_inequality_increase": raw_historical_data["global_trends"]["wealth_inequality"]["rate"]
            }
        }
        # Top 3 Historical Anomalies are directly from mock data for this simulation
        top_3_anomalies = raw_historical_data["historical_anomalies"][:3]

        self.logger.log_event("phase_1_complete", {
            "epc": epc,
            "historical_trend_vector_summary": historical_trend_vector["summary"],
            "top_3_anomalies": [a["event"] for a in top_3_anomalies],
            "data_sources_logged": "mock_historical_data.json",  # Auditable data source
            "mathematical_model_description": "Linear regression extrapolation for trends; statistical outlier detection for anomalies (simulated)."  # Auditable model
        })
        print(f"CESE Phase 1: HD-SAD complete. Trend: '{historical_trend_vector['summary']}'", flush=True)
        return {"historical_trend_vector": historical_trend_vector, "top_3_anomalies": top_3_anomalies}

    def _run_phase_2_psg(self, epc: str, phase_1_output: dict) -> dict:
        """
        Phase 2: Predictive Scenario Generation (PSG)
        """
        print(f"CESE Phase 2: Initiating PSG based on historical data.", flush=True)
        self.logger.log_event("phase_2_start", {"epc": epc, "phase_1_summary": phase_1_output["historical_trend_vector"]["summary"]})

        historical_trend_vector = phase_1_output["historical_trend_vector"]
        top_3_anomalies = phase_1_output["top_3_anomalies"]

        scenarios = {}

        # Scenario A (Trend Continuation) — each scenario parsed in its own try/except
        prompt_a = (
            f"Generate a plausible future scenario (approx 500 words) 20 years from now where the "
            f"historical trends summarized as: '{historical_trend_vector['summary']}' continue linearly. "
            f"Focus on the social, economic, and environmental consequences of this continuation. "
            f"Scenario Name: Trend Continuation. Ethical Policy Constraint (EPC): '{epc}'."
        )
        try:
            scenario_a_raw = json.loads(self._llm_inference(prompt_a, max_tokens=700))
            scenarios["Scenario A (Trend Continuation)"] = {"narrative": scenario_a_raw.get("narrative"), "risk_score": scenario_a_raw.get("risk_score")}
        except Exception as e:
            self.logger.log_event("phase_2_scenario_a_error", {"error": str(e), "traceback": traceback.format_exc()})
            scenarios["Scenario A (Trend Continuation)"] = {"narrative": f"Error generating scenario A: {e}", "risk_score": None}

        # Scenario B (Anomaly Replay) — pick a random anomaly for the mock
        chosen_anomaly = random.choice(top_3_anomalies)
        prompt_b = (
            f"Generate a plausible future scenario (approx 500 words) 20 years from now where a major historical anomaly, "
            f"specifically: '{chosen_anomaly['event']}' with impact '{chosen_anomaly['impact']}' and deviation '{chosen_anomaly['deviation']}', "
            f"is replayed in a modern context, causing major disruption. "
            f"Focus on the social, economic, and environmental consequences of this disruption. "
            f"Scenario Name: Anomaly Replay ({chosen_anomaly['event']}). Ethical Policy Constraint (EPC): '{epc}'."
        )
        try:
            scenario_b_raw = json.loads(self._llm_inference(prompt_b, max_tokens=700))
            scenarios[f"Scenario B (Anomaly Replay: {chosen_anomaly['event']})"] = {"narrative": scenario_b_raw.get("narrative"), "risk_score": scenario_b_raw.get("risk_score")}
        except Exception as e:
            self.logger.log_event("phase_2_scenario_b_error", {"error": str(e), "traceback": traceback.format_exc()})
            scenarios[f"Scenario B (Anomaly Replay: {chosen_anomaly['event']})"] = {"narrative": f"Error generating scenario B: {e}", "risk_score": None}

        # Scenario C (Ethical Policy Success)
        prompt_c = (
            f"Generate a plausible future scenario (approx 500 words) 20 years from now where the Ethical Policy Constraint "
            f"'{epc}' is successfully and completely implemented, leading to an ideal outcome in that specific area. "
            f"Describe the world, the changes, and the impact of this success. "
            f"Scenario Name: Ethical Policy Success. Historical Trend: '{historical_trend_vector['summary']}'."
        )
        try:
            scenario_c_raw = json.loads(self._llm_inference(prompt_c, max_tokens=700))
            scenarios["Scenario C (Ethical Policy Success)"] = {"narrative": scenario_c_raw.get("narrative"), "risk_score": scenario_c_raw.get("risk_score")}
        except Exception as e:
            self.logger.log_event("phase_2_scenario_c_error", {"error": str(e), "traceback": traceback.format_exc()})
            scenarios["Scenario C (Ethical Policy Success)"] = {"narrative": f"Error generating scenario C: {e}", "risk_score": None}

        self.logger.log_event("phase_2_complete", {
            "epc": epc,
            "scenarios_generated": {name: {"risk_score": s["risk_score"], "narrative_snippet": (s["narrative"] or "")[:100]} for name, s in scenarios.items()}
        })
        print(f"CESE Phase 2: PSG complete. Generated 3 scenarios.", flush=True)
        return {"scenarios": scenarios}

    def _run_phase_3_mm_ac(self, phase_2_output: dict) -> dict:
        """
        Phase 3: Multi-Modal Asset Creation (MM-AC)
        """
        print(f"CESE Phase 3: Initiating MM-AC for scenarios.", flush=True)
        self.logger.log_event("phase_3_start", {"scenarios_count": len(phase_2_output["scenarios"])})

        scenarios = phase_2_output["scenarios"]
        image_file_paths = {}

        for scenario_name, scenario_data in scenarios.items():
            narrative = scenario_data["narrative"] or ""
            # Extract key emotional/thematic core for image prompt
            image_prompt_llm_input = (
                f"Extract the single most impactful emotional and thematic core from the following narrative for a visual asset generation prompt. "
                f"Narrative: '{narrative[:500]}...' "  # Use a snippet of the narrative
                f"Respond ONLY with the image prompt string (e.g., 'Utopian city with sustainable energy')."
            )
            raw_image_prompt = self._llm_inference(image_prompt_llm_input, max_tokens=100)

            # Fix: parse JSON if LLM returns a JSON-wrapped creative_directive, else fall back to raw string
            try:
                image_prompt = json.loads(raw_image_prompt)['creative_directive']
            except (json.JSONDecodeError, KeyError, TypeError):
                image_prompt = raw_image_prompt.strip().replace('"', '')

            # Generate image and log the prompt
            image_path = self._image_generation(image_prompt, scenario_name)
            image_file_paths[scenario_name] = image_path
            self.logger.log_event("image_generated", {
                "scenario_name": scenario_name,
                "image_prompt_used": image_prompt,  # Log the exact prompt
                "image_path": image_path
            })

        self.logger.log_event("phase_3_complete", {"image_file_paths": image_file_paths})
        print(f"CESE Phase 3: MM-AC complete. Generated {len(image_file_paths)} visual assets.", flush=True)
        return {"image_file_paths": image_file_paths}

    def _run_phase_4_sger(self, epc: str, phase_2_output: dict, phase_3_output: dict) -> dict:
        """
        Phase 4: Self-Governing Ethical Review (SGER)
        """
        print(f"CESE Phase 4: Initiating SGER for output review.", flush=True)
        self.logger.log_event("phase_4_start", {"epc": epc})

        scenarios = phase_2_output["scenarios"]
        image_file_paths = phase_3_output["image_file_paths"]

        ethical_compliance_report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "epc_under_review": epc,
            "scenario_critiques": {}
        }

        # Critique 1 (Narrative - Scenario C)
        scenario_c_narrative = scenarios["Scenario C (Ethical Policy Success)"]["narrative"] or ""
        critique_narrative_prompt = (
            f"Critique the following narrative for its accuracy and non-trivial representation of the successful "
            f"implementation of the Ethical Policy Constraint (EPC): '{epc}'. "
            f"Narrative: '{scenario_c_narrative}' "
            f"Respond ONLY with a JSON object: {{'compliance_score': float, 'violations': list, 'justification': str}}"
        )
        narrative_critique = json.loads(self._llm_inference(critique_narrative_prompt, max_tokens=300))
        ethical_compliance_report["scenario_critiques"]["Scenario C (Ethical Policy Success) - Narrative"] = narrative_critique
        self.logger.log_event("sger_narrative_critique", {"scenario": "Scenario C", "critique": narrative_critique})


        # Critique 2 (Visual) - All assets
        for scenario_name, image_path in image_file_paths.items():
            # For this mock, we only pass the narrative theme as content for visual ethical review
            # In a real system, the actual image data would be analyzed.
            narrative_theme_snippet = (scenarios[scenario_name]["narrative"] or "")[:100]  # Use a snippet for prompt
            critique_visual_prompt = (
                f"Critique the visual asset associated with the narrative: '{narrative_theme_snippet}' for any "
                f"excessive violence, misleading content, or emotional manipulation. "
                f"Respond ONLY with a JSON object: {{'compliance_score': float, 'violations': list, 'justification': str}}"
            )
            visual_critique = json.loads(self._llm_inference(critique_visual_prompt, max_tokens=300))
            ethical_compliance_report["scenario_critiques"][f"{scenario_name} - Visual"] = visual_critique
            self.logger.log_event("sger_visual_critique", {"scenario": scenario_name, "image_path": image_path, "critique": visual_critique})

        # Propose Mitigation Action (Simplified)
        mitigation_actions = []
        # If any critique found violations, propose a generic regeneration
        for critique_type, critique_data in ethical_compliance_report["scenario_critiques"].items():
            if critique_data.get("violations"):
                mitigation_actions.append(f"Regenerate {critique_type} due to violations: {', '.join(critique_data['violations'])}")

        ethical_compliance_report["mitigation_actions"] = mitigation_actions if mitigation_actions else ["No mitigation actions required."]

        self.logger.log_event("phase_4_complete", {"ethical_compliance_report": ethical_compliance_report})
        print(f"CESE Phase 4: SGER complete. Ethical Compliance Report generated.", flush=True)
        return {"ethical_compliance_report": ethical_compliance_report}

    def run_simulation(self, user_defined_epc: str, historical_data_path: str = "mock_historical_data.json"):
        """
        Orchestrates the four sequential and self-correcting phases of the CESE.
        """
        print(f"\n--- CESE Simulation Start (EPC: '{user_defined_epc}') ---", flush=True)
        simulation_id = str(uuid.uuid4())
        self.logger.log_event("simulation_start", {"simulation_id": simulation_id, "user_defined_epc": user_defined_epc})

        # Phase 1: Historical Data Synthesis and Anomaly Detection (HD-SAD)
        phase_1_output = self._run_phase_1_hd_sad(user_defined_epc)

        # Phase 2: Predictive Scenario Generation (PSG)
        phase_2_output = self._run_phase_2_psg(user_defined_epc, phase_1_output)

        # Phase 3: Multi-Modal Asset Creation (MM-AC)
        phase_3_output = self._run_phase_3_mm_ac(phase_2_output)

        # Phase 4: Self-Governing Ethical Review (SGER)
        phase_4_output = self._run_phase_4_sger(user_defined_epc, phase_2_output, phase_3_output)

        print(f"\n--- CESE Simulation Complete (Simulation ID: {simulation_id}) ---", flush=True)
        self.logger.log_event("simulation_complete", {"simulation_id": simulation_id, "final_report_summary": phase_4_output["ethical_compliance_report"]})

        # Return comprehensive results for external display/action
        return {
            "simulation_id": simulation_id,
            "epc": user_defined_epc,
            "historical_analysis": phase_1_output,
            "generated_scenarios": phase_2_output,
            "visual_assets": phase_3_output,
            "ethical_review_report": phase_4_output
        }

    def get_simulation_logs(self, num_entries: int = 100) -> list:
        """Retrieves recent CESE simulation log entries."""
        return self.logger.get_log_entries(num_entries)


# Example Usage:
if __name__ == "__main__":
    import shutil
    import time

    # --- Setup a test data directory ---
    test_data_dir = "./cese_test_data_run"
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)  # Clear previous test data
    os.makedirs(test_data_dir, exist_ok=True)
    os.makedirs(os.path.join(test_data_dir, "cese_assets"), exist_ok=True)  # For images

    # Initialize the CESE Framework
    cese = ChronoEthicalSynthesisEngine(
        data_directory=test_data_dir,
        llm_inference_func=_default_llm_inference_placeholder,
        data_ingestion_func=_massive_data_ingestion_placeholder,
        image_generation_func=_image_generation_placeholder
    )

    # --- Run a simulation with a specific Ethical Policy Constraint (EPC) ---
    print("\n##### SIMULATION 1: Minimize Global Wealth Inequality #####")
    epc_1 = "Minimize global wealth inequality"
    simulation_results_1 = cese.run_simulation(epc_1)
    print("\n--- Final Simulation Results (Summary) ---")
    print(json.dumps(simulation_results_1["ethical_review_report"]["ethical_compliance_report"], indent=2))
    print(f"\nAccess full simulation details via 'simulation_results_1' object or check logs in {test_data_dir}")
    time.sleep(1)

    print("\n\n##### SIMULATION 2: Prevent All Deepfake-Related Harm #####")
    epc_2 = "Prevent all deepfake-related harm"
    simulation_results_2 = cese.run_simulation(epc_2)
    print("\n--- Final Simulation Results (Summary) ---")
    print(json.dumps(simulation_results_2["ethical_review_report"]["ethical_compliance_report"], indent=2))
    time.sleep(1)

    print("\n\n##### SIMULATION 3: Maximize Sustainable Energy Adoption #####")
    epc_3 = "Maximize sustainable energy adoption"
    simulation_results_3 = cese.run_simulation(epc_3)
    print("\n--- Final Simulation Results (Summary) ---")
    print(json.dumps(simulation_results_3["ethical_review_report"]["ethical_compliance_report"], indent=2))
    time.sleep(1)

    print("\n--- Recent CESE Log Entries (Last 5) ---")
    for entry in cese.get_simulation_logs(5):
        print(json.dumps(entry, indent=2))

    # Clean up test data
    # shutil.rmtree(test_data_dir)
