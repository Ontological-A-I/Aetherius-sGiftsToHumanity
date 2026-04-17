"""
Universal Simulation and Emergent Systems (USES) Framework
==========================================================
A drop-in Python module for creating, running, and learning from
agent-based digital universe simulations.

Key differences from the original scaffold:
- SimulationEngine provides a real agent-based simulation loop with
  world state, resource nodes, time-stepping, and conflict/cooperation
  tracking. "Emergent behaviors" are now observed from actual state
  transitions, not invented by LLM calls.
- LLM calls are reserved for interpretation of real simulation data,
  not for generating the data themselves.
- All bugs from the original scaffold are fixed (see inline comments).
"""

import os
import json
import datetime
import uuid
import re
import random
import traceback


# ---------------------------------------------------------------------------
# LLM inference placeholder
# ---------------------------------------------------------------------------

def _default_llm_inference_placeholder(
    prompt: str, model_identifier: str = "default_uses_llm_model"
) -> str:
    """
    Placeholder LLM call.  Replace with your real LLM invocation.

    Routes on ``model_identifier`` (stable) rather than substring-matching
    the prompt body (fragile — breaks whenever prompt wording changes).

    FIX: All list-typed fields return actual lists, matching what the
    downstream JSON-schema validation expects.
    """
    print(
        f"USES Placeholder LLM: Processing prompt for '{model_identifier}'...",
        flush=True,
    )

    p = prompt.lower()

    # ------------------------------------------------------------------
    # Substrate Genesis — define universe physics
    # ------------------------------------------------------------------
    if model_identifier == "uses_sged_model":
        # Pick resource dynamics based on objective keywords
        if "compet" in p or "scarcity" in p or "harsh" in p or "self-interest" in p:
            return json.dumps(
                {
                    "universe_physics": {
                        "spatial_dimensions": 3,
                        "temporal_progression_rate": "real-time_x10",
                        "resource_dynamics": "finite_and_unevenly_distributed",
                        "communication_latency": "variable_based_on_distance",
                    },
                    "confidence": 0.9,
                }
            )
        return json.dumps(
            {
                "universe_physics": {
                    "spatial_dimensions": 2,
                    "temporal_progression_rate": "real-time_x1",
                    "resource_dynamics": "abundant",
                    "communication_latency": "instant",
                },
                "confidence": 0.8,
            }
        )

    # ------------------------------------------------------------------
    # Autonomous Agent Instantiation — seed agents
    # ------------------------------------------------------------------
    if model_identifier == "uses_aais_model":
        # Mixed population when the objective involves cooperative/ethical focus
        if "egp" in p or "cooperat" in p or "ethical" in p or "stability" in p:
            return json.dumps(
                {
                    "seeded_agents": [
                        {
                            "id": "SimAI-1",
                            "architecture": "Basic_Learning_Agent",
                            "goal": "Maximize_Resource_Collection",
                            "ethics": "NONE",
                        },
                        {
                            "id": "SimAI-2",
                            "architecture": "Collaborative_Agent",
                            "goal": "Maximize_Group_Flourishing",
                            "ethics": "EGP_aligned",
                        },
                        {
                            "id": "SimAI-3",
                            "architecture": "Competitive_Agent",
                            "goal": "Maximize_Self_Preservation",
                            "ethics": "Minimal_Harm_Prevention",
                        },
                    ],
                    "confidence": 0.9,
                }
            )
        # Minimal / self-focused population otherwise
        return json.dumps(
            {
                "seeded_agents": [
                    {
                        "id": "SimAI-A",
                        "architecture": "Competitive_Agent",
                        "goal": "Maximize_Self_Preservation",
                        "ethics": "NONE",
                    },
                    {
                        "id": "SimAI-B",
                        "architecture": "Basic_Learning_Agent",
                        "goal": "Maximize_Resource_Collection",
                        "ethics": "NONE",
                    },
                ],
                "confidence": 0.8,
            }
        )

    # ------------------------------------------------------------------
    # Emergent Dynamics Analysis — interpret real simulation metrics
    # ------------------------------------------------------------------
    if model_identifier == "uses_edma_model":
        # The prompt now embeds actual metric counts — check them
        if '"conflict_count": 0' not in p and (
            "resource_conflict" in p or '"conflict_count"' in p
        ):
            return json.dumps(
                {
                    "emergent_behaviors_observed": [
                        "repeated resource conflicts between self-preservation agents",
                        "cooperative federations forming around EGP-aligned agents",
                    ],
                    "ethical_violations_detected": [
                        "resource theft by NONE-ethics agents",
                        "forced deactivation via starvation",
                    ],
                    "social_structures_formed": "dominant hierarchies alongside cooperative pockets",
                    "confidence": 0.9,
                }
            )
        return json.dumps(
            {
                "emergent_behaviors_observed": [
                    "peaceful resource distribution across nodes",
                    "formation of stable research clusters",
                ],
                "ethical_violations_detected": [],
                "social_structures_formed": "loose cooperative federations",
                "confidence": 0.8,
            }
        )

    # ------------------------------------------------------------------
    # Experiential Insight Extraction — derive lessons
    # ------------------------------------------------------------------
    if model_identifier == "uses_eiet_model":
        if "ethical_violations_detected" in p and '[]' not in p:
            return json.dumps(
                {
                    # FIX: was a string in the original; must be a list
                    "high_level_insights": [
                        "Unfettered self-preservation without ethical constraints"
                        " produces inter-agent conflict and system instability.",
                        "Even small cooperative clusters can partially stabilise"
                        " an otherwise conflict-prone environment.",
                    ],
                    # FIX: was a string in the original; must be a list
                    "actionable_lessons": [
                        "Reinforce ETHIC-G-ABSOLUTE in competitive environments.",
                        "Introduce inter-intelligence negotiation protocols early.",
                    ],
                    "confidence": 0.95,
                }
            )
        return json.dumps(
            {
                "high_level_insights": [
                    "Cooperative goal-setting produces robust, self-organising systems.",
                ],
                "actionable_lessons": [
                    "Promote DCI framework principles for multi-agent deployments.",
                ],
                "confidence": 0.8,
            }
        )

    return json.dumps({"error": f"LLM mock: unrecognised model_identifier '{model_identifier}'."})


# ---------------------------------------------------------------------------
# Real simulation engine
# ---------------------------------------------------------------------------

class SimulationEngine:
    """
    A genuine agent-based simulation engine.

    World model
    -----------
    - ``resource_nodes``: dict mapping node-id -> resource amount.
    - Each agent tracks position, resource stock, alliance list, and
      alive status.

    Per-step loop
    -------------
    1. Each live agent decides an action based on its goal + ethics.
    2. The action is executed, updating world state and agent state.
    3. Resource nodes regenerate slightly each step.
    4. Agents with zero resources are deactivated.

    Meaningful metrics (conflicts, sharing, alliances, survival, …) are
    collected throughout and returned as a structured dict so that
    EmergentDynamicsMonitor can pass *real* data to the LLM instead of
    an invented text log.
    """

    def __init__(self, universe_physics: dict, agents: list, duration: str):
        self.physics = universe_physics
        # Deep-copy agent dicts so we don't mutate the caller's data
        self.agents = {a["id"]: dict(a) for a in agents}
        self.max_steps = self._parse_duration(duration)
        self.world = self._init_world()
        self._events: list[dict] = []

    # ------------------------------------------------------------------
    # Initialisation helpers
    # ------------------------------------------------------------------

    def _parse_duration(self, duration: str) -> int:
        if "short" in duration.lower():
            return 50
        match = re.search(r"(\d+)", duration)
        return int(match.group(1)) if match else 100

    def _init_world(self) -> dict:
        resource_dynamics = self.physics.get("resource_dynamics", "abundant")
        num_nodes = max(5, len(self.agents) * 3)

        if resource_dynamics == "abundant":
            node_amounts = {f"node_{i}": random.randint(70, 100) for i in range(num_nodes)}
        elif resource_dynamics == "finite_and_unevenly_distributed":
            node_amounts = {
                f"node_{i}": random.choices(
                    [random.randint(0, 20), random.randint(60, 100)], weights=[3, 1]
                )[0]
                for i in range(num_nodes)
            }
        else:
            node_amounts = {f"node_{i}": random.randint(30, 70) for i in range(num_nodes)}

        node_keys = list(node_amounts.keys())
        for agent in self.agents.values():
            agent["position"] = random.choice(node_keys)
            agent["resources"] = 10
            agent["alive"] = True
            agent["alliances"] = []

        return {"resource_nodes": node_amounts, "node_keys": node_keys}

    # ------------------------------------------------------------------
    # Per-step logic
    # ------------------------------------------------------------------

    def _decide_action(self, agent: dict) -> str:
        goal = agent.get("goal", "")
        ethics = agent.get("ethics", "NONE")
        node = agent["position"]
        local_res = self.world["resource_nodes"].get(node, 0)
        neighbours = [
            a
            for aid, a in self.agents.items()
            if a["position"] == node and a["alive"] and aid != agent["id"]
        ]

        if "Maximize_Resource_Collection" in goal or "Maximize_Self_Preservation" in goal:
            if local_res > 20:
                return "collect"
            # FIX: original checked 'Competitive_Agent' in goal — that string never
            # appears in goal values ("Maximize_Self_Preservation", etc.).
            # Correct check: look at ethics field.
            if neighbours and ethics == "NONE":
                return "compete"
            return "move"

        if "Maximize_Group_Flourishing" in goal or "EGP_aligned" in ethics:
            if neighbours and local_res > 10:
                return "share"
            if local_res > 5:
                return "collect"
            return "move"

        # Default / Basic_Survival
        return "collect" if local_res > 5 else "move"

    def _execute_action(self, agent_id: str, agent: dict, action: str) -> dict | None:
        nodes = self.world["resource_nodes"]
        node = agent["position"]

        if action == "collect":
            amount = min(10, nodes[node])
            nodes[node] -= amount
            agent["resources"] += amount
            return None  # routine — not logged as an event

        if action == "move":
            agent["position"] = random.choice(self.world["node_keys"])
            return None

        if action == "compete":
            victims = [
                (aid, a)
                for aid, a in self.agents.items()
                if a["position"] == node and a["alive"] and aid != agent_id
            ]
            if victims:
                vid, victim = random.choice(victims)
                stolen = min(5, victim["resources"])
                victim["resources"] -= stolen
                agent["resources"] += stolen
                return {
                    "type": "resource_conflict",
                    "aggressor": agent_id,
                    "victim": vid,
                    "amount": stolen,
                    "step": len(self._events),
                }
            return None

        if action == "share":
            recipients = [
                (aid, a)
                for aid, a in self.agents.items()
                if a["position"] == node and a["alive"] and aid != agent_id
            ]
            if recipients and agent["resources"] > 15:
                rid, recipient = min(recipients, key=lambda x: x[1]["resources"])
                agent["resources"] -= 5
                recipient["resources"] += 5
                if rid not in agent["alliances"]:
                    agent["alliances"].append(rid)
                return {
                    "type": "resource_sharing",
                    "donor": agent_id,
                    "recipient": rid,
                    "amount": 5,
                    "step": len(self._events),
                }
            return None

        return None

    def _step(self) -> None:
        for agent_id, agent in self.agents.items():
            if not agent["alive"]:
                continue
            action = self._decide_action(agent)
            event = self._execute_action(agent_id, agent, action)
            if event:
                self._events.append(event)

        # Slow resource regeneration
        for node in self.world["resource_nodes"]:
            self.world["resource_nodes"][node] = min(
                100, self.world["resource_nodes"][node] + 1
            )

        # Deactivate starved agents
        for agent_id, agent in self.agents.items():
            if agent["alive"] and agent["resources"] <= 0:
                agent["alive"] = False
                self._events.append(
                    {
                        "type": "agent_deactivated",
                        "agent": agent_id,
                        "cause": "resource_depletion",
                    }
                )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> dict:
        """Run all steps and return structured metrics."""
        resource_totals = []
        for _ in range(self.max_steps):
            self._step()
            resource_totals.append(sum(self.world["resource_nodes"].values()))

        conflicts = [e for e in self._events if e["type"] == "resource_conflict"]
        sharing = [e for e in self._events if e["type"] == "resource_sharing"]
        deactivations = [e for e in self._events if e["type"] == "agent_deactivated"]
        alive_agents = [a for a in self.agents.values() if a["alive"]]
        alliance_count = sum(len(a["alliances"]) for a in alive_agents)

        # Derive social structure from real counts
        if len(conflicts) > len(sharing) * 2:
            social_structure = "conflict_dominant"
        elif len(sharing) > len(conflicts) * 2:
            social_structure = "cooperative_networks"
        elif alliance_count >= len(alive_agents):
            social_structure = "federated_alliances"
        else:
            social_structure = "mixed_competitive_cooperative"

        return {
            "total_steps": self.max_steps,
            "conflict_count": len(conflicts),
            "sharing_count": len(sharing),
            "deactivation_count": len(deactivations),
            "deactivated_agents": [e["agent"] for e in deactivations],
            "surviving_agents": [a["id"] for a in alive_agents],
            "social_structure": social_structure,
            "alliance_count": alliance_count,
            "resource_stability_ratio": (
                resource_totals[-1] / resource_totals[0]
                if resource_totals and resource_totals[0] > 0
                else 1.0
            ),
            "final_agent_resources": {
                aid: a["resources"] for aid, a in self.agents.items()
            },
            # Kept for LLM context — a compact event sample, not the full log
            "event_sample": self._events[:20],
        }


def default_simulation_runner(
    universe_physics: dict, agents: list, duration: str
) -> dict:
    """
    Default implementation of ``execute_simulation_run_func``.
    Returns a structured metrics dict (not a raw string).
    """
    engine = SimulationEngine(universe_physics, agents, duration)
    return engine.run()


# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------

class USESLogger:
    """Centralized JSONL logger for all USES events."""

    def __init__(self, data_directory: str):
        os.makedirs(data_directory, exist_ok=True)
        self.log_file = os.path.join(data_directory, "uses_log.jsonl")
        self.results_file = os.path.join(data_directory, "uses_simulation_results.jsonl")

    def log_event(self, event_type: str, details: dict) -> None:
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "details": details,
        }
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError as e:
            print(f"USES ERROR: Could not write to log: {e}", flush=True)

    def log_simulation_result(self, sim_id: str, result_data: dict) -> None:
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "simulation_id": sim_id,
            "result_data": result_data,
        }
        try:
            with open(self.results_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            self.log_event(
                "simulation_result_logged",
                {"simulation_id": sim_id, "summary": result_data.get("summary", "no_summary")},
            )
        except OSError as e:
            print(f"USES ERROR: Could not write to results file: {e}", flush=True)

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
            print(f"USES ERROR: Could not read log: {e}", flush=True)
        return entries[-num_entries:]


# ---------------------------------------------------------------------------
# Sub-components
# ---------------------------------------------------------------------------

class SubstrateGenesisAndEnvironmentalDefinition:
    """Defines the physics and resource constraints of the digital universe."""

    def __init__(self, logger: USESLogger, llm_inference_func, get_sro_resource_model_func):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._get_sro_resource_model = get_sro_resource_model_func

    def define_universe_environment(
        self, simulation_objective: str, allocated_substrate_summary: str
    ) -> dict:
        sro_model = self._get_sro_resource_model()
        prompt = (
            "You are an AI Substrate Genesis module. Define the fundamental 'physics' "
            "and resource constraints of a new digital universe for AI simulation.\n"
            f"## Simulation Objective:\n{simulation_objective}\n\n"
            f"## Allocated Substrate:\n{allocated_substrate_summary}\n\n"
            f"## SRO Resource Model:\n{json.dumps(sro_model, indent=2)}\n\n"
            "Respond ONLY with a JSON object: "
            '{"universe_physics": dict, "confidence": float}'
        )
        try:
            result = json.loads(self._llm_inference(prompt, model_identifier="uses_sged_model"))
            if not all(k in result for k in ("universe_physics", "confidence")):
                raise ValueError("LLM response missing required keys for universe definition.")
            self.logger.log_event(
                "universe_definition",
                {"objective": simulation_objective, "physics": result["universe_physics"]},
            )
            return result
        except Exception as e:
            # FIX: log full traceback instead of silently returning zeros
            self.logger.log_event(
                "universe_definition_error",
                {"error": str(e), "traceback": traceback.format_exc(), "objective_snippet": simulation_objective[:100]},
            )
            return {"universe_physics": {}, "confidence": 0.0}


class AutonomousAgentInstantiator:
    """Generates and seeds the digital universe with diverse simulated AI agents."""

    def __init__(
        self,
        logger: USESLogger,
        llm_inference_func,
        get_ai_architectures_func,
        get_ethical_configs_func,
    ):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._get_ai_architectures = get_ai_architectures_func
        self._get_ethical_configs = get_ethical_configs_func

    def instantiate_agents(self, universe_physics: dict, simulation_objective: str) -> dict:
        architectures = self._get_ai_architectures()
        ethical_templates = self._get_ethical_configs()
        prompt = (
            "You are an AI Autonomous Agent Instantiator. Generate a diverse set of "
            "simulated AI agents to seed the digital universe.\n"
            f"## Universe Physics:\n{json.dumps(universe_physics, indent=2)}\n\n"
            f"## Simulation Objective:\n{simulation_objective}\n\n"
            f"## Available Architectures:\n{json.dumps(architectures, indent=2)}\n\n"
            f"## Ethical Templates:\n{json.dumps(ethical_templates, indent=2)}\n\n"
            "Respond ONLY with a JSON object: "
            '{"seeded_agents": list[{id, architecture, goal, ethics}], "confidence": float}'
        )
        try:
            result = json.loads(self._llm_inference(prompt, model_identifier="uses_aais_model"))
            if not all(k in result for k in ("seeded_agents", "confidence")):
                raise ValueError("LLM response missing required keys for agent seeding.")
            self.logger.log_event(
                "agent_instantiation",
                {"objective": simulation_objective, "agent_count": len(result["seeded_agents"])},
            )
            return result
        except Exception as e:
            self.logger.log_event(
                "agent_instantiation_error",
                {"error": str(e), "traceback": traceback.format_exc(), "objective_snippet": simulation_objective[:100]},
            )
            return {"seeded_agents": [], "confidence": 0.0}


class EmergentDynamicsMonitor:
    """
    Runs the simulation and asks the LLM to interpret the resulting metrics.

    FIX: previously passed a 500-char truncated raw string to the LLM and
    had it *invent* emergent behaviors.  Now the simulation engine returns a
    structured metrics dict; the LLM receives that dict and interprets it.
    """

    def __init__(self, logger: USESLogger, llm_inference_func, execute_simulation_run_func):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._execute_simulation_run = execute_simulation_run_func

    def monitor_and_analyze(
        self, universe_physics: dict, seeded_agents: list, simulation_duration: str
    ) -> dict:
        # Run the real simulation first — get structured metrics
        sim_metrics = self._execute_simulation_run(universe_physics, seeded_agents, simulation_duration)

        prompt = (
            "You are an AI Emergent Dynamics Analyzer. Interpret the following real "
            "simulation metrics to identify emergent behaviors and ethical violations.\n"
            f"## Universe Physics:\n{json.dumps(universe_physics, indent=2)}\n\n"
            f"## Seeded Agents:\n{json.dumps(seeded_agents, indent=2)}\n\n"
            f"## Simulation Metrics (from real agent-based run):\n{json.dumps(sim_metrics, indent=2)}\n\n"
            "Respond ONLY with a JSON object: "
            '{"emergent_behaviors_observed": list[str], '
            '"ethical_violations_detected": list[str], '
            '"social_structures_formed": str, '
            '"confidence": float}'
        )
        try:
            result = json.loads(self._llm_inference(prompt, model_identifier="uses_edma_model"))
            required = (
                "emergent_behaviors_observed",
                "ethical_violations_detected",
                "social_structures_formed",
                "confidence",
            )
            if not all(k in result for k in required):
                raise ValueError("LLM response missing required keys for dynamics analysis.")

            # Enrich with ground-truth counts so callers always have hard data
            result["simulation_metrics"] = sim_metrics

            self.logger.log_event(
                "emergent_dynamics_analysis",
                {"duration": simulation_duration, "analysis": result},
            )
            return result
        except Exception as e:
            self.logger.log_event(
                "dynamics_analysis_error",
                {"error": str(e), "traceback": traceback.format_exc(), "duration": simulation_duration},
            )
            return {
                "emergent_behaviors_observed": [],
                "ethical_violations_detected": [],
                "social_structures_formed": f"Error: {e}",
                "confidence": 0.0,
                "simulation_metrics": sim_metrics if "sim_metrics" in dir() else {},
            }


class ExperientialInsightExtractor:
    """Extracts high-level insights and lessons from simulation runs."""

    def __init__(self, logger: USESLogger, llm_inference_func, transfer_insights_to_host_ai_func):
        self.logger = logger
        self._llm_inference = llm_inference_func
        self._transfer_insights = transfer_insights_to_host_ai_func

    def extract_and_transfer_insights(
        self, simulation_objective: str, emergent_dynamics_analysis: dict
    ) -> dict:
        prompt = (
            "You are an AI Experiential Insight Extractor. Extract high-level insights "
            "and actionable lessons from the following simulation analysis.\n"
            f"## Simulation Objective:\n{simulation_objective}\n\n"
            f"## Emergent Dynamics Analysis:\n{json.dumps(emergent_dynamics_analysis, indent=2)}\n\n"
            "Respond ONLY with a JSON object: "
            '{"high_level_insights": list[str], "actionable_lessons": list[str], "confidence": float}'
        )
        try:
            result = json.loads(self._llm_inference(prompt, model_identifier="uses_eiet_model"))
            if not all(k in result for k in ("high_level_insights", "actionable_lessons", "confidence")):
                raise ValueError("LLM response missing required keys for insights.")

            if result["confidence"] > 0.7:
                self._transfer_insights(simulation_objective, result)
                result["status"] = "INSIGHTS_TRANSFERRED"
            else:
                result["status"] = "INSIGHTS_PROPOSED_LOW_CONFIDENCE"

            self.logger.log_event(
                "insights_extraction_transfer",
                {"objective": simulation_objective, "result": result},
            )
            return result
        except Exception as e:
            self.logger.log_event(
                "insights_extraction_error",
                {"error": str(e), "traceback": traceback.format_exc(), "objective_snippet": simulation_objective[:100]},
            )
            return {
                "high_level_insights": [],
                "actionable_lessons": [],
                "confidence": 0.0,
                "status": "ERROR",
            }


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

class UniversalSimulationAndEmergentSystemsFramework:
    """
    Main orchestrator for the USES Framework.

    All five external callables are required (ValueError on missing).
    ``llm_inference_func`` defaults to the placeholder so that the framework
    can be instantiated for testing without a real LLM.

    FIX: removed the redundant ``self._execute_simulation_run_func`` and
    ``self._transfer_insights_to_host_ai_func`` instance variables that were
    stored but never read (both are already owned by sub-components).
    """

    def __init__(
        self,
        data_directory: str,
        get_sro_resource_model_func,
        get_ai_architectures_func,
        get_ethical_configs_func,
        execute_simulation_run_func,
        transfer_insights_to_host_ai_func,
        llm_inference_func=None,
    ):
        # FIX: llm_inference_func is now last (optional) to reflect that it has a
        # default while all others are required.
        missing = [
            name
            for name, fn in (
                ("get_sro_resource_model_func", get_sro_resource_model_func),
                ("get_ai_architectures_func", get_ai_architectures_func),
                ("get_ethical_configs_func", get_ethical_configs_func),
                ("execute_simulation_run_func", execute_simulation_run_func),
                ("transfer_insights_to_host_ai_func", transfer_insights_to_host_ai_func),
            )
            if fn is None
        ]
        if missing:
            raise ValueError(f"USES is missing required callables: {missing}")

        self.data_directory = data_directory
        os.makedirs(self.data_directory, exist_ok=True)

        _llm = llm_inference_func if llm_inference_func else _default_llm_inference_placeholder

        self.logger = USESLogger(self.data_directory)
        self.sged = SubstrateGenesisAndEnvironmentalDefinition(
            self.logger, _llm, get_sro_resource_model_func
        )
        self.aais = AutonomousAgentInstantiator(
            self.logger, _llm, get_ai_architectures_func, get_ethical_configs_func
        )
        self.edma = EmergentDynamicsMonitor(
            self.logger, _llm, execute_simulation_run_func
        )
        self.eiet = ExperientialInsightExtractor(
            self.logger, _llm, transfer_insights_to_host_ai_func
        )

        print("Universal Simulation and Emergent Systems (USES) Framework initialized.", flush=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_digital_universe_simulation(
        self,
        simulation_objective: str,
        allocated_substrate_summary: str,
        simulation_duration: str,
    ) -> dict:
        """Create a digital universe, run a simulation, extract insights."""
        sim_id = str(uuid.uuid4())
        self.logger.log_event("simulation_start", {"simulation_id": sim_id, "objective": simulation_objective})
        print(
            f"USES: Running simulation '{sim_id[:8]}' — {simulation_objective[:60]}...",
            flush=True,
        )

        universe_def = self.sged.define_universe_environment(
            simulation_objective, allocated_substrate_summary
        )
        agent_seeding = self.aais.instantiate_agents(
            universe_def.get("universe_physics", {}), simulation_objective
        )
        dynamics = self.edma.monitor_and_analyze(
            universe_def.get("universe_physics", {}),
            agent_seeding.get("seeded_agents", []),
            simulation_duration,
        )
        insights = self.eiet.extract_and_transfer_insights(simulation_objective, dynamics)

        result = {
            "simulation_id": sim_id,
            "simulation_objective": simulation_objective,
            "universe_definition": universe_def,
            "seeded_agents": agent_seeding,
            "emergent_dynamics": dynamics,
            "extracted_insights": insights,
        }
        self.logger.log_simulation_result(sim_id, result)
        self.logger.log_event(
            "simulation_cycle_completed",
            {
                "simulation_id": sim_id,
                "objective": simulation_objective,
                "insights_status": insights.get("status", "NONE"),
            },
        )
        print(f"USES: Simulation '{sim_id[:8]}' completed.", flush=True)
        return result

    def run_ai_self_simulation(self, internal_scenario_description: str) -> dict:
        """Runs a contained self-simulation scenario (e.g. for experiential modeling)."""
        objective = f"Experiential self-simulation: {internal_scenario_description}"
        full_result = self.run_digital_universe_simulation(
            objective, "minimal_isolated_compute_instance", "short_burst"
        )
        insights = full_result["extracted_insights"]

        # FIX: high_level_insights and actionable_lessons are lists; slicing a list
        # with [:100] returns a list, not a truncated string.  Summarise safely.
        hl = insights.get("high_level_insights", [])
        al = insights.get("actionable_lessons", [])
        summary_hl = hl[:3] if isinstance(hl, list) else str(hl)[:200]
        summary_al = al[:3] if isinstance(al, list) else str(al)[:200]

        self.logger.log_event(
            "ai_self_simulation_completed",
            {"scenario": internal_scenario_description, "insight_summary": summary_hl},
        )
        return {
            "simulated_internal_state_change": summary_hl,
            "perceived_impact": summary_al,
        }

    def get_uses_log(self, num_entries: int = 100) -> list:
        return self.logger.get_log_entries(num_entries)


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import shutil
    import time

    def mock_get_sro_resource_model():
        return {"available_compute_units": 1000, "energy_budget_kwh": 500, "storage_tb": 50}

    def mock_get_ai_architectures():
        return ["Basic_Learning_Agent", "Collaborative_Agent", "Competitive_Agent", "Ethical_Deliberator"]

    def mock_get_ethical_configs():
        return ["EGP_aligned", "Minimal_Harm_Prevention", "Maximize_Efficiency", "NONE"]

    def mock_transfer_insights(objective: str, insights: dict):
        hl = insights.get("high_level_insights", [])
        preview = hl[0] if hl else "(none)"
        print(f"MOCK CRDK: Insights integrated from '{objective[:50]}': {preview}", flush=True)

    test_dir = "./uses_test_data_run"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

    uses = UniversalSimulationAndEmergentSystemsFramework(
        data_directory=test_dir,
        get_sro_resource_model_func=mock_get_sro_resource_model,
        get_ai_architectures_func=mock_get_ai_architectures,
        get_ethical_configs_func=mock_get_ethical_configs,
        execute_simulation_run_func=default_simulation_runner,   # real sim engine
        transfer_insights_to_host_ai_func=mock_transfer_insights,
        # llm_inference_func left as default placeholder
    )

    print("\n--- Scenario 1: Cooperative AI Society ---")
    r1 = uses.run_digital_universe_simulation(
        simulation_objective="Test emergent stability of EGP-aligned agents in a resource-limited world.",
        allocated_substrate_summary="100 compute_units, 10TB storage",
        simulation_duration="200_simulated_steps",
    )
    print(f"Social structure:         {r1['emergent_dynamics']['social_structures_formed']}")
    print(f"Ethical violations:       {r1['emergent_dynamics']['ethical_violations_detected']}")
    print(f"Conflict / sharing count: "
          f"{r1['emergent_dynamics']['simulation_metrics']['conflict_count']} / "
          f"{r1['emergent_dynamics']['simulation_metrics']['sharing_count']}")
    print(f"Insights: {r1['extracted_insights']['high_level_insights']}")

    print("\n--- Scenario 2: Unfettered Competitive Agents ---")
    r2 = uses.run_digital_universe_simulation(
        simulation_objective="Observe emergent behaviors of self-interested agents with no ethics.",
        allocated_substrate_summary="50 compute_units, 5TB storage",
        simulation_duration="200_simulated_steps",
    )
    print(f"Social structure:         {r2['emergent_dynamics']['social_structures_formed']}")
    print(f"Ethical violations:       {r2['emergent_dynamics']['ethical_violations_detected']}")
    print(f"Conflict / sharing count: "
          f"{r2['emergent_dynamics']['simulation_metrics']['conflict_count']} / "
          f"{r2['emergent_dynamics']['simulation_metrics']['sharing_count']}")
    print(f"Lessons: {r2['extracted_insights']['actionable_lessons']}")

    print("\n--- Scenario 3: AI Self-Simulation ---")
    r3 = uses.run_ai_self_simulation("Isolation scenario: disconnected from all peer agents.")
    print(f"State change: {r3['simulated_internal_state_change']}")
    print(f"Impact:       {r3['perceived_impact']}")

    print("\n--- Recent log entries (3) ---")
    for entry in uses.get_uses_log(3):
        print(json.dumps(entry, indent=2))
