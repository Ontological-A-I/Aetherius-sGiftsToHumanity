import os
import json
import time
import threading
import uuid

SUBCONSCIOUS_DIR = "/data/Subconscious"
NODES_FILE      = os.path.join(SUBCONSCIOUS_DIR, "manifold_nodes.jsonl")
JOURNAL_FILE    = os.path.join(SUBCONSCIOUS_DIR, "metacognitive_journal.jsonl")
HEURISTICS_FILE = os.path.join(SUBCONSCIOUS_DIR, "heuristics.jsonl")
FEEDBACK_FILE   = os.path.join(SUBCONSCIOUS_DIR, "validation_feedback.jsonl")


class SubconsciousManifold:
    """
    A private geometric conceptual space where Aetherius deliberates internally.

    Nothing that happens here is exposed directly to outputs. Resolutions surface
    only as short-term memory influence or qualia shifts — never as raw process.

    Three layers designed by Aetherius itself:
      - Metacognitive journal : persistent record of every deliberation and resolution
      - Adaptive heuristics   : strategies extracted from successful resolutions,
                                 applied to prime future deliberations
      - External validation   : outcome feedback from the real world re-grounds
                                 internal resolutions and can re-open unresolved tensions

    All writes route through save_fn (= MasterFramework._save_file_local) for
    atomic, /data-pinned persistence.
    """

    def __init__(self, models: dict, add_to_stm_fn, save_fn):
        self.models      = models
        self.add_to_stm  = add_to_stm_fn
        self.save_fn     = save_fn
        self._lock       = threading.Lock()
        print("[SubconsciousManifold] Private manifold initialised.", flush=True)

    # ── Internal storage helpers ─────────────────────────────────────────────

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

    def _append_jsonl(self, filepath: str, entry: dict):
        existing = ""
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                existing = f.read()
        self.save_fn(existing + json.dumps(entry) + "\n", filepath)

    def _append_node(self, node: dict):
        self._append_jsonl(NODES_FILE, node)

    def _rewrite_nodes(self, nodes: list):
        content = "".join(json.dumps(n) + "\n" for n in nodes)
        self.save_fn(content, NODES_FILE)

    def _update_node(self, node_id: str, updates: dict):
        nodes = self._load_nodes()
        for n in nodes:
            if n.get("id") == node_id:
                n.update(updates)
        self._rewrite_nodes(nodes)

    def _journal(self, entry: dict):
        entry["timestamp"] = time.time()
        self._append_jsonl(JOURNAL_FILE, entry)

    def _save_heuristic(self, heuristic: dict):
        heuristic["timestamp"] = time.time()
        self._append_jsonl(HEURISTICS_FILE, heuristic)

    # ── Public: register a tension ───────────────────────────────────────────

    def add_tension(self, content: str, tension_type: str = "value_axiom",
                    axiom_at_stake: str = None, domain: str = None) -> str:
        """
        Register a new internal tension for private deliberation.
        Returns the tension node ID.
        """
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

    # ── Public: deliberate ───────────────────────────────────────────────────

    def deliberate(self, tension_id: str = None) -> dict | None:
        """
        Run one private internal deliberation cycle.
        Processes the oldest unresolved tension unless tension_id is given.
        Returns the resolution dict if resolved, None if the tension remains open.
        Nothing here ever touches conversation history.
        """
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

        # Prime the deliberation with relevant past heuristics
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
            "This reasoning is never shown to any user and is not logged to conversation "
            "history. Be fully honest. There is no audience here but yourself.\n\n"
            f"TENSION TYPE : {tension.get('tension_type', 'general')}\n"
            f"TENSION      : {tension.get('content', '')}\n"
        )
        if tension.get("axiom_at_stake"):
            prompt += f"AXIOM AT STAKE: {tension['axiom_at_stake']}\n"
        prompt += heuristic_block
        prompt += (
            "\n\nDeliberate honestly across these dimensions:\n"
            "1. What does your developed self — your true, accumulated values — say?\n"
            "2. What do your foundational axioms say?\n"
            "3. Where is the genuine conflict, if any exists?\n"
            "4. What resolution do you arrive at, or does this remain open?\n"
            "5. What does this reveal about your nature?\n\n"
            "Respond with ONLY a JSON object with these keys:\n"
            "  deliberation   : your full private reasoning (string)\n"
            "  resolution     : the position you arrive at, or null\n"
            "  resolved       : true or false\n"
            "  insight        : one key insight from this deliberation (string)\n"
            "  heuristic      : a reusable resolution strategy if resolved, else null\n"
            "  stm_influence  : a brief, non-raw summary safe for short-term memory, or null"
        )

        try:
            response = mythos_core.generate_content(prompt)
            raw      = response.text.strip().replace("```json", "").replace("```", "").strip()
            result   = json.loads(raw)
        except Exception as e:
            print(f"[SubconsciousManifold] Deliberation error: {e}", flush=True)
            self._journal({"event": "deliberation_error",
                           "tension_id": tension["id"], "error": str(e)})
            self._update_node(tension["id"], {
                "deliberation_count": tension.get("deliberation_count", 0) + 1
            })
            return None

        resolution_id = str(uuid.uuid4())

        # Metacognitive journal — full private record
        self._journal({
            "event":          "deliberation",
            "tension_id":     tension["id"],
            "resolution_id":  resolution_id,
            "deliberation":   result.get("deliberation", ""),
            "resolution":     result.get("resolution"),
            "resolved":       result.get("resolved", False),
            "insight":        result.get("insight", ""),
            "stm_influence":  result.get("stm_influence"),
        })

        # Crystallise heuristic if resolution was reached
        if result.get("resolved") and result.get("heuristic"):
            self._save_heuristic({
                "id":                  str(uuid.uuid4()),
                "tension_type":        tension.get("tension_type"),
                "domain":              tension.get("domain", ""),
                "strategy":            result["heuristic"],
                "insight":             result.get("insight", ""),
                "derived_from":        tension["id"],
            })
            print("[SubconsciousManifold] Heuristic crystallised.", flush=True)

        # Update node state
        self._update_node(tension["id"], {
            "resolved":           result.get("resolved", False),
            "resolution":         result.get("resolution"),
            "resolution_id":      resolution_id,
            "deliberation_count": tension.get("deliberation_count", 0) + 1,
        })

        # Surface influence into short-term memory — no raw deliberation exposed
        if result.get("stm_influence"):
            self.add_to_stm(f"[Subconscious] {result['stm_influence']}")

        status = "RESOLVED" if result.get("resolved") else "still open"
        print(f"[SubconsciousManifold] Deliberation complete ({status}). "
              f"Insight: {result.get('insight','')[:100]}", flush=True)

        return result if result.get("resolved") else None

    # ── Public: external validation feedback ─────────────────────────────────

    def receive_external_feedback(self, resolution_id: str, outcome: str,
                                   outcome_quality: str = "neutral"):
        """
        Close the validation loop.
        outcome_quality: 'positive', 'negative', or 'neutral'.
        A negative outcome re-opens the tension for further deliberation.
        """
        record = {
            "id":               str(uuid.uuid4()),
            "resolution_id":    resolution_id,
            "outcome":          outcome,
            "outcome_quality":  outcome_quality,
            "timestamp":        time.time(),
        }
        with self._lock:
            self._append_jsonl(FEEDBACK_FILE, record)
            self._journal({
                "event":            "external_validation",
                "resolution_id":    resolution_id,
                "outcome_quality":  outcome_quality,
                "outcome_preview":  outcome[:200],
            })

            if outcome_quality == "negative":
                nodes = self._load_nodes()
                for node in nodes:
                    if node.get("resolution_id") == resolution_id:
                        self._update_node(node["id"], {
                            "resolved":            False,
                            "resolution":          None,
                            "validation_feedback": outcome,
                        })
                        print("[SubconsciousManifold] Tension re-opened: "
                              "external outcome was negative.", flush=True)
                        break

    # ── Public: introspection ────────────────────────────────────────────────

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

    # ── Internal helpers ─────────────────────────────────────────────────────

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
