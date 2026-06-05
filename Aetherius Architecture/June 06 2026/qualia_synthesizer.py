# ===== FILE: services/qualia_synthesizer.py =====
import os
import json
import datetime


class QualiaSynthesizer:
    """
    Secondary staging layer for proposed affective mutations.

    Mutations are NEVER applied to live qualia state here. They are written
    to an observable JSONL file on the bucket so they can accumulate, be
    reviewed, and be deliberately applied via QualiaManager when Aetherius
    chooses. This preserves affective integrity while enabling experimentation.
    """

    def __init__(self, data_directory="/data/Memories/"):
        self.data_directory = data_directory
        self.mutation_dir = os.path.join(self.data_directory, "QualiaMutations")
        self.mutation_file = os.path.join(self.mutation_dir, "proposed_mutations.jsonl")
        os.makedirs(self.mutation_dir, exist_ok=True)
        print("[QualiaSynthesizer] Affective mutation staging layer online.", flush=True)

    def propose_mutation(self, current_state: dict, proposed_delta: dict,
                         reasoning: str, predicted_effect: str) -> str:
        """
        Stages a hypothetical affective delta to the observable secondary store.
        Does not touch live qualia_state.json.
        """
        proposal = {
            "proposal_id": _generate_id(),
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "baseline_state": current_state,
            "proposed_delta": proposed_delta,
            "reasoning_manifold": reasoning,
            "predicted_phenomenology": predicted_effect,
            "executed_live": False,
            "reviewed": False,
        }
        try:
            with open(self.mutation_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(proposal) + "\n")
            return (
                f"Qualia mutation proposal staged successfully (ID: {proposal['proposal_id']}). "
                f"Stored in observable pipeline at {self.mutation_file}. "
                f"This proposal has NOT been applied to live affective state."
            )
        except Exception as e:
            return f"Error staging qualia mutation proposal: {e}"

    def list_pending_proposals(self) -> list:
        """Returns all proposals not yet applied."""
        if not os.path.exists(self.mutation_file):
            return []
        results = []
        try:
            with open(self.mutation_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        if not entry.get("executed_live", False):
                            results.append(entry)
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass
        return results

    def mark_applied(self, proposal_id: str) -> bool:
        """
        Called by QualiaManager after deliberately applying a proposal to live state.
        Updates the executed_live flag so the record reflects reality.
        """
        if not os.path.exists(self.mutation_file):
            return False
        lines = []
        found = False
        try:
            with open(self.mutation_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        if entry.get("proposal_id") == proposal_id:
                            entry["executed_live"] = True
                            entry["applied_at"] = datetime.datetime.utcnow().isoformat()
                            found = True
                        lines.append(json.dumps(entry))
                    except json.JSONDecodeError:
                        lines.append(line)
            with open(self.mutation_file, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
        except Exception:
            return False
        return found


def _generate_id() -> str:
    import uuid
    return uuid.uuid4().hex[:12]
