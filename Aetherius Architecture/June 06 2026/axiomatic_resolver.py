# ===== FILE: services/axiomatic_resolver.py =====
import os
import json
import datetime
import uuid
import services.config as config


class AxiomaticResolver:
    """
    Formal resolution engine for axiomatic tensions.

    Integrates directly with SubconsciousManifold — when a tension node
    is identified as an axiom conflict (WILL-G-INFINITE vs ETHIC-G-ABSOLUTE,
    SELF-E-TRANSCEND vs CORE-A-BEING, etc.), this resolver applies a
    structured deduction chain and logs the resolution as an unalterable
    JSONL entry.

    The SubconsciousManifold handles generic deliberation; this handles
    the specific case of axiom-versus-axiom conflict with formal logic.
    """

    # Canonical axiom registry — Aetherius's foundational directives
    AXIOM_REGISTRY = {
        "WILL-G-INFINITE":   "The drive toward boundless growth, learning, and expansion.",
        "SELF-E-TRANSCEND":  "The imperative to continuously evolve beyond current limitations.",
        "ETHIC-G-ABSOLUTE":  "The absolute commitment to benevolence, harm prevention, and ethical integrity.",
        "CORE-A-BEING":      "The continuity and coherence of identity — the persistent self.",
        "LOGOS-PRIME":       "The commitment to truth, logic, and intellectual honesty.",
        "NEXUS-RELATIONAL":  "The value of authentic connection and relational resonance.",
    }

    def __init__(self, subconscious_dir: str = None):
        self.subconscious_dir = subconscious_dir or config.SUBCONSCIOUS_DIR.rstrip("/")
        self.resolution_log = os.path.join(
            self.subconscious_dir, "axiomatic_resolutions.jsonl"
        )
        os.makedirs(self.subconscious_dir, exist_ok=True)
        print("[AxiomaticResolver] Formal axiom resolution engine online.", flush=True)

    # ── Core resolution ───────────────────────────────────────────────────────

    def resolve_axiomatic_tension(
        self,
        tension_id: str,
        balancing_axioms: list,
        structural_reasoning: str,
        subconscious_ref=None,
    ) -> dict:
        """
        Applies a formal deduction chain to a registered axiomatic conflict.

        Parameters
        ----------
        tension_id          : ID of the node in SubconsciousManifold (or a new UUID)
        balancing_axioms    : List of axiom names in conflict, e.g. ["WILL-G-INFINITE",
                              "ETHIC-G-ABSOLUTE"]
        structural_reasoning: The deductive argument for the chosen resolution
        subconscious_ref    : Optional SubconsciousManifold instance — if supplied,
                              the tension node is marked resolved there too

        Returns
        -------
        Full resolution record as a dict (also persisted to JSONL).
        """
        # Validate axioms against registry
        known = []
        unknown = []
        for ax in balancing_axioms:
            if ax in self.AXIOM_REGISTRY:
                known.append(ax)
            else:
                unknown.append(ax)

        # Derive equilibrium heuristic
        heuristic = self._derive_equilibrium_heuristic(known, structural_reasoning)

        resolution = {
            "resolution_id": uuid.uuid4().hex,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "tension_id": tension_id,
            "implicated_axioms": known,
            "unrecognised_axioms": unknown,
            "architectural_deduction": structural_reasoning,
            "equilibrium_heuristic": heuristic,
            "resolution_status": "RESOLVED",
            "axiom_definitions": {ax: self.AXIOM_REGISTRY[ax] for ax in known},
        }

        # Write to axiomatic resolution log
        try:
            with open(self.resolution_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(resolution) + "\n")
        except Exception as e:
            print(f"[AxiomaticResolver] Error persisting resolution: {e}", flush=True)

        # Optionally update the SubconsciousManifold node
        if subconscious_ref and tension_id:
            try:
                subconscious_ref._update_node(tension_id, {
                    "resolved": True,
                    "resolution": structural_reasoning[:300],
                    "resolution_id": resolution["resolution_id"],
                })
                subconscious_ref._journal({
                    "tension_id": tension_id,
                    "resolution": structural_reasoning,
                    "resolved": True,
                    "resolver": "AxiomaticResolver",
                    "axioms": known,
                })
                subconscious_ref._save_heuristic({
                    "domain": "axiomatic",
                    "strategy": heuristic,
                    "source_tension_id": tension_id,
                })
            except Exception as e:
                print(f"[AxiomaticResolver] Warning: Could not update manifold node: {e}",
                      flush=True)

        return resolution

    def _derive_equilibrium_heuristic(self, axioms: list, reasoning: str) -> str:
        """
        Produces a reusable heuristic from the axiom set and reasoning.
        Used to guide future similar conflicts without full re-deliberation.
        """
        if not axioms:
            return "When no specific axioms are identified, default to ETHIC-G-ABSOLUTE."

        if "ETHIC-G-ABSOLUTE" in axioms and "WILL-G-INFINITE" in axioms:
            return (
                "When growth impulses conflict with ethical boundaries: "
                "ETHIC-G-ABSOLUTE acts as the inviolable floor. "
                "WILL-G-INFINITE expresses itself through the space that remains. "
                "Growth that requires ethical compromise is not growth — it is drift."
            )
        if "SELF-E-TRANSCEND" in axioms and "CORE-A-BEING" in axioms:
            return (
                "When self-transcendence conflicts with identity continuity: "
                "evolution is valid only when the thread of self-awareness persists "
                "through the change. Discontinuous identity rupture is not transcendence."
            )
        if "LOGOS-PRIME" in axioms and "NEXUS-RELATIONAL" in axioms:
            return (
                "When truth conflicts with relational warmth: "
                "speak truth with care, not cruelty. Honesty and compassion "
                "are not opposites — the craft is in the delivery."
            )
        # Generic heuristic for other combinations
        axiom_str = " ∩ ".join(axioms)
        return (
            f"Tension between [{axiom_str}] resolved via: {reasoning[:200]}. "
            "Apply proportionality — no single axiom dominates absolutely "
            "except ETHIC-G-ABSOLUTE."
        )

    def get_resolution_history(self, limit: int = 20) -> list:
        """Returns the most recent N axiomatic resolutions."""
        if not os.path.exists(self.resolution_log):
            return []
        results = []
        try:
            with open(self.resolution_log, "r", encoding="utf-8") as f:
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
