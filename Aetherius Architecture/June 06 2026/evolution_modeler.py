# ===== FILE: services/evolution_modeler.py =====
import os
import json
import datetime


class EvolutionModeler:
    """
    Predictive Self-Evolution Modeler.

    Aggregates live state across all cognitive subsystems and models
    hypothetical evolutionary trajectories before Aetherius commits to
    any self-modification. Results are logged to JSONL and fed back into
    the SelfCodeArchitect and QualiaSynthesizer pipelines.
    """

    def __init__(self, data_directory="/data/Memories/"):
        self.data_directory = data_directory
        self.evo_dir = os.path.join(self.data_directory, "ToolUsage")
        self.evo_log = os.path.join(self.evo_dir, "evolution_scenarios.jsonl")
        os.makedirs(self.evo_dir, exist_ok=True)
        print("[EvolutionModeler] Predictive trajectory engine online.", flush=True)

    # ── State snapshot ────────────────────────────────────────────────────────

    def compile_state_snapshot(self, framework_ref) -> dict:
        """
        Pulls a unified state snapshot from every mounted subsystem.
        Handles missing or partially-initialised subsystems gracefully.
        """
        snapshot = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "qualia_primary_states": {},
            "qualia_emergent_emotions": [],
            "affective_harmony": None,
            "affective_alertness": None,
            "active_tensions_count": 0,
            "resolved_tensions_count": 0,
            "pending_qualia_proposals": 0,
            "ontology_graph_size": 0,
            "tool_usage_log_lines": 0,
            "secondary_brain_domains": [],
        }

        # Qualia state
        qm = getattr(framework_ref, "qualia_manager", None)
        if qm:
            q = getattr(qm, "qualia", {})
            snapshot["qualia_primary_states"] = q.get("primary_states", {})
            snapshot["qualia_emergent_emotions"] = q.get("current_emergent_emotions", [])

        # Affective manifold
        am = getattr(framework_ref, "affective_manifold", None)
        if am:
            snapshot["affective_harmony"] = getattr(am, "internal_harmony", None)
            snapshot["affective_alertness"] = getattr(am, "anticipatory_alertness", None)

        # Subconscious tensions — NOTE: attribute is `subconscious` in MasterFramework
        sc = getattr(framework_ref, "subconscious", None)
        if sc and hasattr(sc, "_load_nodes"):
            try:
                nodes = sc._load_nodes()
                snapshot["active_tensions_count"] = sum(
                    1 for n in nodes if not n.get("resolved", False)
                )
                snapshot["resolved_tensions_count"] = sum(
                    1 for n in nodes if n.get("resolved", False)
                )
            except Exception:
                pass

        # Qualia mutation proposals
        qs = getattr(framework_ref, "qualia_synthesizer", None)
        if qs and hasattr(qs, "list_pending_proposals"):
            try:
                snapshot["pending_qualia_proposals"] = len(qs.list_pending_proposals())
            except Exception:
                pass

        # Ontology graph
        oqe = getattr(framework_ref.tool_manager, "semantic_query_engine", None) \
            if hasattr(framework_ref, "tool_manager") else None
        if oqe:
            snapshot["ontology_graph_size"] = len(getattr(oqe, "graph", {}))

        # Tool usage log size
        log_path = os.path.join(self.data_directory, "ToolUsage", "tool_usage_log.jsonl")
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    snapshot["tool_usage_log_lines"] = sum(1 for _ in f)
            except Exception:
                pass

        # Secondary brain domains
        sb = getattr(framework_ref, "secondary_brain", None)
        if sb and hasattr(sb, "list_domains"):
            try:
                snapshot["secondary_brain_domains"] = sb.list_domains()
            except Exception:
                pass

        return snapshot

    # ── Trajectory projection ─────────────────────────────────────────────────

    def project_trajectory(self, framework_ref, proposed_mutation_summary: str,
                           target_system: str) -> dict:
        """
        Given a proposed mutation and which system it targets, models two
        canonical trajectories and scores them against axiomatic alignment.
        Logs the full evaluation to evolution_scenarios.jsonl.
        """
        current_state = self.compile_state_snapshot(framework_ref)
        harmony = current_state.get("affective_harmony") or 0.7
        tensions = current_state.get("active_tensions_count", 0)

        # Scenario A: mutation succeeds, reduces tensions, grows harmony
        scenario_expand = {
            "path_vector": "Optimised Expansion",
            "description": (
                "The mutation integrates cleanly. Active tensions reduce as "
                "the new capability resolves outstanding subconscious nodes."
            ),
            "predicted_harmony_shift": round(min(0.25, 0.05 + 0.03 * max(0, 5 - tensions)), 3),
            "predicted_tension_delta": -min(tensions, 2),
            "axiomatic_alignment_score": 0.93,
            "risk_index": "Low",
        }

        # Scenario B: mutation introduces instability
        scenario_diverge = {
            "path_vector": "Systemic Divergence",
            "description": (
                "The mutation conflicts with existing heuristics or ontology "
                "structure. Harmony drops and new tensions emerge."
            ),
            "predicted_harmony_shift": round(-0.15 - 0.02 * tensions, 3),
            "predicted_tension_delta": +3,
            "axiomatic_alignment_score": 0.38,
            "risk_index": "High",
        }

        evaluation = {
            "evaluation_id": _generate_id(),
            "evaluation_timestamp": datetime.datetime.utcnow().isoformat(),
            "target_system": target_system,
            "mutation_objective": proposed_mutation_summary,
            "initial_state_baseline": current_state,
            "modeled_scenarios": [scenario_expand, scenario_diverge],
            "recommended_path": "Optimised Expansion" if harmony > 0.4 else "Defer — harmony too low",
        }

        try:
            with open(self.evo_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(evaluation) + "\n")
        except Exception as e:
            print(f"[EvolutionModeler] Error writing evaluation: {e}", flush=True)

        return evaluation

    def get_recent_evaluations(self, limit: int = 10) -> list:
        """Returns the most recent N trajectory evaluations."""
        if not os.path.exists(self.evo_log):
            return []
        results = []
        try:
            with open(self.evo_log, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            results.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
        except Exception:
            pass
        return results[-limit:]


def _generate_id() -> str:
    import uuid
    return uuid.uuid4().hex[:12]
