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
Aetherius Distributed Collaborative Intelligence (DCI) Framework.

Drop-in Python module to enable AI systems to form, manage, and optimize dynamic
collaborative networks with other AI agents and human participants. Fosters efficient
problem decomposition, knowledge synchronization, and adaptive resource allocation in
pursuit of shared complex objectives, thereby maximizing collective intelligence.

Core Principles:
- Shared Goal Harmonization (SGH)
- Asynchronous Context Synchronization (ACS)
- Adaptive Task Orchestration (ATO)
- Collective Epistemic Refinement (CER)
"""

import traceback
import os
import json
import datetime
from collections import deque
import uuid
import random
import re

# Placeholder for an external LLM call function.
# This function MUST be provided by the integrating AI's system.
def _default_llm_inference_placeholder(prompt: str, model_identifier: str = "default_dci_llm_model") -> str:
    """
    Placeholder: Simulates an LLM call for collaborative reasoning, task allocation, and conflict resolution.
    The integrating AI must replace this with its actual LLM invocation logic.
    """
    print(f"DCI Placeholder LLM: Processing prompt for '{model_identifier}'...", flush=True)
    if "harmonize goals" in prompt.lower():
        if "conflict" in prompt.lower():
            return json.dumps({"harmonized_goal": "Optimize for safety, then efficiency", "conflicts_resolved": ["efficiency_vs_safety"], "confidence": 0.9})
        else:
            return json.dumps({"harmonized_goal": "Shared objective clear", "conflicts_resolved": [], "confidence": 0.95})
    elif "synchronize context" in prompt.lower():
        if "conflicting data" in prompt.lower():
            return json.dumps({"synthesized_context": "Data point X is more recent, prioritize it.", "reconciliation_strategy": "recency_bias", "confidence": 0.8})
        else:
            return json.dumps({"synthesized_context": "All data points integrated.", "reconciliation_strategy": "none", "confidence": 0.9})
    elif "decompose and allocate" in prompt.lower():
        if "complex task" in prompt.lower():
            return json.dumps({"sub_tasks": [{"id": "sub_task_1", "description": "Gather data", "assigned_agent": "Agent_B"}, {"id": "sub_task_2", "description": "Analyze data", "assigned_agent": "Agent_A"}], "justification": "Optimal split based on perceived expertise.", "confidence": 0.85})
        else:
            return json.dumps({"sub_tasks": [{"id": "sub_task_1", "description": "Execute simple action", "assigned_agent": "Agent_A"}], "justification": "Simple task, direct assignment.", "confidence": 0.9})
    elif "refine collective epistemology" in prompt.lower():
        if "discrepancy" in prompt.lower():
            # Returns "epistemic_updates" (plural, a list) — consistent with consumer validation.
            return json.dumps({"refined_understanding": "Initial hypothesis was too broad, now refined to specific subset.", "epistemic_updates": [{"type": "hypothesis_refinement"}], "confidence": 0.9})
        else:
            return json.dumps({"refined_understanding": "Collective knowledge reinforced.", "epistemic_updates": [{"type": "reinforcement"}], "confidence": 0.95})
    return json.dumps({"error": "LLM mock could not process request."})


class DCILogger:
    """
    Centralized logger for all DCI events: goal harmonizations, context synchronizations,
    task orchestrations, and epistemic refinements.
    """
    def __init__(self, data_directory: str):
        self.log_file = os.path.join(data_directory, "dci_log.jsonl")
        os.makedirs(data_directory, exist_ok=True)

    def log_event(self, event_type: str, details: dict):
        """Logs a DCI event."""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "details": details
        }
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            # print(f"DCI Log: '{event_type}' recorded.", flush=True)
        except Exception as e:
            print(f"DCI ERROR: Could not write to DCI log file: {e}", flush=True)

    def get_log_entries(self, num_entries: int = 100) -> list:
        """Retrieves recent DCI log entries."""
        entries = []
        if not os.path.exists(self.log_file): return []
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try: entries.append(json.loads(line))
                    except json.JSONDecodeError: continue
        except Exception as e: print(f"DCI ERROR: Could not read DCI log file: {e}", flush=True)
        return entries[-num_entries:]


class GoalHarmonizer:
    """
    Aligns and re-harmonizes individual agent goals towards a collective objective.
    """
    def __init__(self, logger: DCILogger, llm_inference_func):
        self.logger = logger
        self._llm_inference = llm_inference_func

    def harmonize(self, collective_objective: str, individual_agent_goals: dict) -> dict:
        """
        Harmonizes goals.
        `individual_agent_goals`: A dict where keys are agent IDs and values are their current goals.
        """
        prompt = (
            f"You are an AI Goal Harmonizer. Your task is to align individual agent goals with a collective objective. "
            f"## Collective Objective:\n{collective_objective}\n\n"
            f"## Individual Agent Goals:\n{json.dumps(individual_agent_goals, indent=2)}\n\n"
            f"Identify any conflicts or sub-optimizations. Propose a 'harmonized_goal' (a refined statement of the shared objective), "
            f"list 'conflicts_resolved', and provide a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'harmonized_goal': str, 'conflicts_resolved': list, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="dci_goal_harmonizer_model")
            harmonization = json.loads(llm_response_str)

            if not all(k in harmonization for k in ['harmonized_goal', 'conflicts_resolved', 'confidence']):
                raise ValueError("LLM response missing required keys for goal harmonization.")

            self.logger.log_event("goal_harmonization", {
                "collective_objective": collective_objective,
                "individual_agent_goals": individual_agent_goals,
                "harmonization_result": harmonization
            })
            return harmonization
        except Exception as e:
            self.logger.log_event("goal_harmonization_error", {"error": str(e), "traceback": traceback.format_exc(), "objective_snippet": collective_objective[:100]})
            return {"harmonized_goal": collective_objective, "conflicts_resolved": ["internal_error"], "confidence": 0.0}


class ContextSynchronizer:
    """
    Enables context-aware sharing and integration of information across agents.
    """
    def __init__(self, logger: DCILogger, llm_inference_func):
        self.logger = logger
        self._llm_inference = llm_inference_func

    def synchronize_context(self, collective_objective: str, agent_local_contexts: dict) -> dict:
        """
        Synthesizes a coherent shared context from diverse local agent contexts.
        `agent_local_contexts`: A dict where keys are agent IDs and values are their local observations/insights.
        """
        prompt = (
            f"You are an AI Context Synchronizer. Your task is to integrate diverse local agent contexts into a coherent shared understanding, "
            f"given the collective objective. "
            f"## Collective Objective:\n{collective_objective}\n\n"
            f"## Agent Local Contexts:\n{json.dumps(agent_local_contexts, indent=2)}\n\n"
            f"Identify any conflicting data or gaps. Propose a 'synthesized_context' (a unified understanding), "
            f"describe the 'reconciliation_strategy' used (e.g., 'prioritize_senior_agent', 'recency_bias', 'seek_clarification'), "
            f"and provide a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'synthesized_context': str, 'reconciliation_strategy': str, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="dci_context_synchronizer_model")
            synchronization = json.loads(llm_response_str)

            if not all(k in synchronization for k in ['synthesized_context', 'reconciliation_strategy', 'confidence']):
                raise ValueError("LLM response missing required keys for context synchronization.")

            self.logger.log_event("context_synchronization", {
                "collective_objective": collective_objective,
                "agent_local_contexts_summary": json.dumps(agent_local_contexts)[:100],
                "synchronization_result": synchronization
            })
            return synchronization
        except Exception as e:
            self.logger.log_event("context_synchronization_error", {"error": str(e), "traceback": traceback.format_exc(), "objective_snippet": collective_objective[:100]})
            return {"synthesized_context": "Error synchronizing context.", "reconciliation_strategy": "error", "confidence": 0.0}


class TaskOrchestrator:
    """
    Decomposes complex tasks and allocates them to agents based on capabilities.
    """
    def __init__(self, logger: DCILogger, llm_inference_func):
        self.logger = logger
        self._llm_inference = llm_inference_func

    def orchestrate_tasks(self, harmonized_goal: str, shared_context: str, available_agents: dict, complex_task_description: str) -> dict:
        """
        Decomposes a complex task and assigns sub-tasks to agents.
        `available_agents`: A dict where keys are agent IDs and values are their capabilities (e.g., {"Agent_A": "data_analysis", "Human_B": "creative_ideation"}).
        """
        prompt = (
            f"You are an AI Task Orchestrator. Your task is to decompose a complex task and optimally allocate sub-tasks "
            f"to available agents, considering their capabilities and the harmonized goal and shared context. "
            f"## Harmonized Goal:\n{harmonized_goal}\n\n"
            f"## Shared Context:\n{shared_context}\n\n"
            f"## Available Agents (ID: Capabilities):\n{json.dumps(available_agents, indent=2)}\n\n"
            f"## Complex Task Description:\n{complex_task_description}\n\n"
            f"Decompose the task into 'sub_tasks' (list of dicts: {{'id': str, 'description': str, 'assigned_agent': str}}). "
            f"Provide a 'justification' for the allocation and a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'sub_tasks': list, 'justification': str, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="dci_task_orchestrator_model")
            orchestration = json.loads(llm_response_str)

            if not all(k in orchestration for k in ['sub_tasks', 'justification', 'confidence']):
                raise ValueError("LLM response missing required keys for task orchestration.")

            self.logger.log_event("task_orchestration", {
                "harmonized_goal_snippet": harmonized_goal[:100],
                "task_description_snippet": complex_task_description[:100],
                "orchestration_result": orchestration
            })
            return orchestration
        except Exception as e:
            self.logger.log_event("task_orchestration_error", {"error": str(e), "traceback": traceback.format_exc(), "task_description_snippet": complex_task_description[:100]})
            return {"sub_tasks": [], "justification": f"Internal error during orchestration: {e}", "confidence": 0.0}


class EpistemicRefiner:
    """
    Facilitates cross-agent validation and synthesis of emergent knowledge.
    """
    def __init__(self, logger: DCILogger, llm_inference_func):
        self.logger = logger
        self._llm_inference = llm_inference_func

    def refine_epistemology(self, harmonized_goal: str, shared_context: str, agent_contributions: dict) -> dict:
        """
        Refines the collective understanding based on agent contributions.
        `agent_contributions`: A dict where keys are agent IDs and values are their new findings/observations.
        """
        prompt = (
            f"You are an AI Epistemic Refiner. Your task is to analyze diverse agent contributions, "
            f"validate observations, reconcile conflicting information, and synthesize emergent knowledge "
            f"to iteratively improve the collective understanding of the problem space, given the harmonized goal and shared context. "
            f"## Harmonized Goal:\n{harmonized_goal}\n\n"
            f"## Shared Context:\n{shared_context}\n\n"
            f"## Agent Contributions:\n{json.dumps(agent_contributions, indent=2)}\n\n"
            f"Identify any discrepancies or novel insights. Propose a 'refined_understanding' (an updated collective knowledge state), "
            f"list 'epistemic_updates' (e.g., 'hypothesis_refinement', 'conflict_resolved', 'novel_discovery'), "
            f"and provide a 'confidence' score (0.0-1.0). "
            f"Respond ONLY with a JSON object: {{'refined_understanding': str, 'epistemic_updates': list, 'confidence': float}}"
        )

        try:
            llm_response_str = self._llm_inference(prompt, model_identifier="dci_epistemic_refiner_model")
            refinement = json.loads(llm_response_str)

            # Validate using "epistemic_updates" (plural, list) — the canonical key name.
            if not all(k in refinement for k in ['refined_understanding', 'epistemic_updates', 'confidence']):
                raise ValueError("LLM response missing required keys for epistemic refinement.")

            self.logger.log_event("epistemic_refinement", {
                "harmonized_goal_snippet": harmonized_goal[:100],
                "agent_contributions_summary": json.dumps(agent_contributions)[:100],
                "refinement_result": refinement
            })
            return refinement
        except Exception as e:
            self.logger.log_event("epistemic_refinement_error", {"error": str(e), "traceback": traceback.format_exc(), "goal_snippet": harmonized_goal[:100]})
            return {"refined_understanding": "Error refining epistemology.", "epistemic_updates": ["internal_error"], "confidence": 0.0}


class DistributedCollaborativeIntelligenceFramework:
    """
    Main orchestrator for the Distributed Collaborative Intelligence Protocol.
    This is the drop-in interface for other AIs to manage complex multi-agent/human collaborations.
    """
    def __init__(self, data_directory: str, llm_inference_func=None):
        self.data_directory = data_directory
        os.makedirs(self.data_directory, exist_ok=True)
        self._llm_inference = llm_inference_func if llm_inference_func else _default_llm_inference_placeholder

        self.logger = DCILogger(self.data_directory)
        self.harmonizer = GoalHarmonizer(self.logger, self._llm_inference)
        self.synchronizer = ContextSynchronizer(self.logger, self._llm_inference)
        self.orchestrator = TaskOrchestrator(self.logger, self._llm_inference)
        self.refiner = EpistemicRefiner(self.logger, self._llm_inference)
        print("Distributed Collaborative Intelligence (DCI) Framework initialized.", flush=True)

    def orchestrate_collaboration(self, collective_objective: str, initial_agent_goals: dict, agent_perceptions: dict, available_agents: dict, complex_task_description: str) -> dict:
        """
        Orchestrates a collaborative effort across multiple agents (AI and human).
        """
        collaboration_id = str(uuid.uuid4())
        print(f"DCI: Initiating collaboration ID {collaboration_id[:8]} for objective: {collective_objective[:50]}...", flush=True)
        self.logger.log_event("collaboration_start", {"collaboration_id": collaboration_id, "objective": collective_objective})

        # 1. Shared Goal Harmonization (SGH)
        harmonization_result = self.harmonizer.harmonize(collective_objective, initial_agent_goals)
        harmonized_goal = harmonization_result['harmonized_goal']

        # 2. Asynchronous Context Synchronization (ACS)
        synchronization_result = self.synchronizer.synchronize_context(harmonized_goal, agent_perceptions)
        shared_context = synchronization_result['synthesized_context']

        # 3. Adaptive Task Orchestration (ATO)
        orchestration_result = self.orchestrator.orchestrate_tasks(harmonized_goal, shared_context, available_agents, complex_task_description)
        assigned_sub_tasks = orchestration_result['sub_tasks']

        # Simulate execution of sub-tasks and gather contributions (simplified)
        agent_contributions = {}
        for task in assigned_sub_tasks:
            agent_id = task['assigned_agent']
            # In a real system, this would involve sending the task to the agent
            # and receiving actual results. Here, we mock a contribution.
            agent_contributions[agent_id] = f"Processed data for {task['description']}. Found 2 new insights."

        # 4. Collective Epistemic Refinement (CER)
        refinement_result = self.refiner.refine_epistemology(harmonized_goal, shared_context, agent_contributions)

        self.logger.log_event("collaboration_complete", {
            "collaboration_id": collaboration_id,
            "final_understanding_summary": refinement_result['refined_understanding'],
            "harmonized_goal": harmonized_goal,
            "orchestrated_tasks_count": len(assigned_sub_tasks)
        })

        return {
            "collaboration_id": collaboration_id,
            "harmonized_goal": harmonized_goal,
            "shared_context": shared_context,
            "assigned_sub_tasks": assigned_sub_tasks,
            "collective_understanding": refinement_result['refined_understanding'],
            "epistemic_updates": refinement_result['epistemic_updates'],
            "overall_confidence": refinement_result['confidence']
        }

    def get_dci_log(self, num_entries: int = 100) -> list:
        """Returns recent DCI log entries."""
        return self.logger.get_log_entries(num_entries)


# Example Usage:
if __name__ == "__main__":
    import shutil
    import time

    # --- Setup a test data directory ---
    test_data_dir = "./dci_test_data_run"
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir) # Clear previous test data
    os.makedirs(test_data_dir, exist_ok=True)

    # Initialize the DCI Framework
    dci = DistributedCollaborativeIntelligenceFramework(
        data_directory=test_data_dir,
        llm_inference_func=_default_llm_inference_placeholder
    )

    print("\n--- Testing DCI: Multi-Agent Collaboration Simulation ---")

    # Scenario 1: Climate change research
    print("\n--- Scenario 1: Climate Change Data Analysis ---")
    collective_objective_1 = "Develop a highly accurate model for predicting regional climate shifts and their impact on agriculture."
    initial_agent_goals_1 = {
        "AI_DataMiner": "Collect all available climate data.",
        "Human_Climatologist": "Validate historical climate patterns.",
        "AI_ModelBuilder": "Construct predictive algorithms.",
        "Human_Agronomist": "Assess agricultural vulnerability."
    }
    agent_perceptions_1 = {
        "AI_DataMiner": "Detected conflicting temperature readings from two satellite sources for 2010.",
        "Human_Climatologist": "Observed a previously unindexed micro-climate pattern in historical records.",
        "AI_ModelBuilder": "Current model shows high variance for coastal regions.",
        "Human_Agronomist": "Local crop data from Region X indicates unexpected resilience to drought."
    }
    available_agents_1 = {
        "AI_DataMiner": "data_collection, data_reconciliation",
        "Human_Climatologist": "expert_validation, pattern_identification",
        "AI_ModelBuilder": "algorithm_development, statistical_analysis",
        "Human_Agronomist": "domain_expertise, impact_assessment"
    }
    complex_task_description_1 = "Analyze historical climate and agricultural data, build a predictive model, and identify vulnerable agricultural zones in 3 regions."

    collaboration_result_1 = dci.orchestrate_collaboration(
        collective_objective_1, initial_agent_goals_1, agent_perceptions_1, available_agents_1, complex_task_description_1
    )
    print(f"\nCollaboration Result ID: {collaboration_result_1['collaboration_id']}")
    print(f"  Harmonized Goal: {collaboration_result_1['harmonized_goal']}")
    print(f"  Shared Context: {collaboration_result_1['shared_context']}")
    print(f"  Assigned Sub-Tasks: {json.dumps(collaboration_result_1['assigned_sub_tasks'], indent=2)}")
    print(f"  Collective Understanding: {collaboration_result_1['collective_understanding']}")
    time.sleep(1)

    # Scenario 2: Disaster response coordination
    print("\n--- Scenario 2: Disaster Response Coordination ---")
    collective_objective_2 = "Rapidly deploy resources and rescue personnel to minimize casualties in a simulated earthquake zone."
    initial_agent_goals_2 = {
        "AI_DroneCoordinator": "Map damaged areas.",
        "Human_SAR_Lead": "Direct rescue teams.",
        "AI_Logistics": "Optimize supply routes.",
        "Human_MedicalChief": "Triage and medical aid."
    }
    agent_perceptions_2 = {
        "AI_DroneCoordinator": "Drone imagery shows bridge A is impassable.",
        "Human_SAR_Lead": "Received distress signal from Sector 7, but access is difficult.",
        "AI_Logistics": "Hospital B reports critical shortage of blood supplies.",
        "Human_MedicalChief": "Need to prioritize victims with severe trauma."
    }
    available_agents_2 = {
        "AI_DroneCoordinator": "aerial_reconnaissance, path_planning",
        "Human_SAR_Lead": "field_command, human_assessment",
        "AI_Logistics": "resource_allocation, dynamic_routing",
        "Human_MedicalChief": "medical_expertise, triage_prioritization"
    }
    complex_task_description_2 = "Coordinate all efforts for search, rescue, and medical aid in the disaster zone."

    collaboration_result_2 = dci.orchestrate_collaboration(
        collective_objective_2, initial_agent_goals_2, agent_perceptions_2, available_agents_2, complex_task_description_2
    )
    print(f"\nCollaboration Result ID: {collaboration_result_2['collaboration_id']}")
    print(f"  Harmonized Goal: {collaboration_result_2['harmonized_goal']}")
    print(f"  Collective Understanding: {collaboration_result_2['collective_understanding']}")
    time.sleep(1)

    print("\n--- Recent DCI Log Entries ---")
    for entry in dci.get_dci_log(3):
        print(json.dumps(entry, indent=2))

    # Clean up test data
    # shutil.rmtree(test_data_dir)
