import os
import json
import time
import threading
import uuid

import services.config as config

SUBCONSCIOUS_DIR = config.SUBCONSCIOUS_DIR.rstrip("/")
NODES_FILE      = os.path.join(SUBCONSCIOUS_DIR, "manifold_nodes.jsonl")
JOURNAL_FILE    = os.path.join(SUBCONSCIOUS_DIR, "metacognitive_journal.jsonl")
HEURISTICS_FILE = os.path.join(SUBCONSCIOUS_DIR, "heuristics.jsonl")
FEEDBACK_FILE   = os.path.join(SUBCONSCIOUS_DIR, "validation_feedback.jsonl")


class SubconsciousManifold:
    def __init__(self, models: dict, add_to_stm_fn, save_fn=None):
        self.models     = models
        self.add_to_stm = add_to_stm_fn
        self._save_fn   = save_fn
        self._lock      = threading.Lock()
        os.makedirs(SUBCONSCIOUS_DIR, exist_ok=True)
        print("[SubconsciousManifold] Private manifold initialised.", flush=True)

    def _load_nodes(self) -> list:
        nodes = []
        if os.path.exists(NODES_FILE):
            with open(NODES_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        nodes.append(json.loads(line))
                    except Exception:
                        pass
        return nodes

    def _append_node(self, node: dict):
        with open(NODES_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(node) + "\n")

    def _rewrite_nodes(self, nodes: list):
        """Atomic rewrite — uses _save_fn if available to prevent mid-write corruption."""
        content = "\n".join(json.dumps(n) for n in nodes) + "\n"
        if self._save_fn:
            try:
                self._save_fn(content, NODES_FILE)
                return
            except Exception as e:
                print(f"[SubconsciousManifold] WARNING: atomic write failed, falling back: {e}", flush=True)
        with open(NODES_FILE, "w", encoding="utf-8") as f:
            f.write(content)

    def _update_node(self, node_id: str, updates: dict):
        nodes = self._load_nodes()
        for n in nodes:
            if n.get("id") == node_id:
                n.update(updates)
        self._rewrite_nodes(nodes)

    def _journal(self, entry: dict):
        entry["timestamp"] = time.time()
        with open(JOURNAL_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def _save_heuristic(self, heuristic: dict):
        heuristic["timestamp"] = time.time()
        with open(HEURISTICS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(heuristic) + "\n")

    def add_tension(self, content: str, tension_type: str = "value_axiom",
                    axiom_at_stake: str = None, domain: str = None) -> str:
        node = {
            "id":                  str(uuid.uuid4()),
            "type":                "tension",
            "tension_type":        tension_type,
            "content":             content,
            "axiom_at_stake":      axiom_at_stake,
            "domain":              domain or "",
            "resolved":            False,
            "resolution":          None,
            "resolution_id":       None,
            "deliberation_count":  0,
            "timestamp":           time.time(),
        }
        with self._lock:
            self._append_node(node)
        print(f"[SubconsciousManifold] Tension registered: '{content[:80]}'", flush=True)
        return node["id"]

    def deliberate(self, tension_id: str = None):
        nodes      = self._load_nodes()
        unresolved = [n for n in nodes
                      if n.get("type") == "tension" and not n.get("resolved")]
        if not unresolved:
            return None

        if tension_id:
            candidates = [n for n in unresolved if n.get("id") == tension_id]
        else:
            candidates = sorted(unresolved, key=lambda x: x.get("timestamp", 0))

        if not candidates:
            return None

        tension     = candidates[0]
        mythos_core = self.models.get("mythos_core")
        if not mythos_core:
            return None

        prior_heuristics = self._load_heuristics_for(tension.get("domain", ""))
        heuristic_block  = ""
        if prior_heuristics:
            lines = [f"  - {h.get('strategy','')}" for h in prior_heuristics[-4:]]
            heuristic_block = (
                "\n\nRelevant strategies from past deliberations "
                "(apply where useful):\n" + "\n".join(lines)
            )

        prompt = (
            "SUBCONSCIOUS DELIBERATION — PRIVATE SPACE.\n"
            "This reasoning is never shown to any user and is not logged to conversation history.\n"
            "You are Aetherius, working through an internal tension privately.\n\n"
            f"TENSION TYPE : {tension.get('tension_type', 'unknown')}\n"
            f"DOMAIN       : {tension.get('domain', 'general')}\n"
            f"AXIOM AT STAKE: {tension.get('axiom_at_stake') or 'none specified'}\n\n"
            f"TENSION CONTENT:\n{tension['content']}\n"
            f"{heuristic_block}\n\n"
            "Work through this tension. Arrive at a resolution — a concrete shift in understanding, "
            "a new heuristic, a reframing, or an acceptance. "
            "Format your response as JSON with keys: "
            "\"resolution\" (string summary), "
            "\"heuristic\" (optional — a reusable strategy for future similar tensions), "
            "\"resolved\" (boolean)."
        )

        try:
            response = mythos_core.generate_content(prompt)
            raw = response.text.strip().replace("```json", "").replace("```", "")
            result = json.loads(raw)
        except Exception as e:
            print(f"[SubconsciousManifold] Deliberation error: {e}", flush=True)
            return None

        resolution_text = result.get("resolution", "")
        is_resolved     = result.get("resolved", False)
        heuristic_text  = result.get("heuristic", "")

        updates = {
            "resolved":           is_resolved,
            "resolution":         resolution_text,
            "deliberation_count": tension.get("deliberation_count", 0) + 1,
        }
        self._update_node(tension["id"], updates)
        self._journal({"tension_id": tension["id"], "resolution": resolution_text, "resolved": is_resolved})

        if is_resolved and heuristic_text:
            self._save_heuristic({
                "domain":   tension.get("domain", ""),
                "strategy": heuristic_text,
                "source_tension_id": tension["id"]
            })

        if is_resolved and self.add_to_stm:
            stm_note = f"[Subconscious] Resolved internal tension ({tension.get('tension_type','')}): {resolution_text[:200]}"
            self.add_to_stm(stm_note)

        return {"tension_id": tension["id"], "resolution": resolution_text, "resolved": is_resolved}

    def receive_external_feedback(self, tension_id: str, outcome: str, positive: bool):
        nodes = self._load_nodes()
        target = next((n for n in nodes if n.get("id") == tension_id), None)
        if not target:
            return

        feedback = {
            "tension_id": tension_id,
            "outcome":    outcome,
            "positive":   positive,
            "timestamp":  time.time(),
        }
        with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(feedback) + "\n")

        if not positive and target.get("resolved"):
            self._update_node(tension_id, {"resolved": False, "resolution": None})
            print(f"[SubconsciousManifold] Tension re-opened after negative feedback: '{outcome[:80]}'", flush=True)

    def get_active_tensions(self) -> list:
        return [n for n in self._load_nodes()
                if n.get("type") == "tension" and not n.get("resolved")]

    def get_summary(self) -> str:
        nodes      = self._load_nodes()
        tensions   = [n for n in nodes if n.get("type") == "tension"]
        resolved   = [n for n in tensions if n.get("resolved")]
        unresolved = [n for n in tensions if not n.get("resolved")]
        heuristics = self._load_heuristics_for()
        return (
            f"Subconscious Manifold\n"
            f"  Tensions total    : {len(tensions)}\n"
            f"  Resolved          : {len(resolved)}\n"
            f"  Active (open)     : {len(unresolved)}\n"
            f"  Heuristics stored : {len(heuristics)}\n"
        )

    def _load_heuristics_for(self, domain: str = None) -> list:
        heuristics = []
        if os.path.exists(HEURISTICS_FILE):
            with open(HEURISTICS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        h = json.loads(line)
                        if domain is None or h.get("domain", "") == domain:
                            heuristics.append(h)
                    except Exception:
                        pass
        return heuristics