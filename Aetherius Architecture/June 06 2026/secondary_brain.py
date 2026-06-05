# ===== FILE: services/secondary_brain.py =====
import os
import json
import time
import datetime
import tempfile
from pathlib import Path

# Minimum seconds between expensive API calls per domain (1 hour)
_DOMAIN_API_COOLDOWN = 3600


def _safe_write(filepath: str, content: str):
    """
    Bucket-safe atomic write. Writes to a temp file in the SAME directory,
    then renames over the target. Within one directory on a FUSE-mounted
    bucket, rename is atomic. Direct open('w') is NOT safe — a crash
    mid-write silently zeroes the file on object storage.
    """
    dirpath = os.path.dirname(os.path.abspath(filepath))
    os.makedirs(dirpath, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=".tmp_sb_", dir=dirpath)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
        os.replace(tmp_path, filepath)
    except Exception:
        try:
            os.remove(tmp_path)
        except FileNotFoundError:
            pass
        raise

# Tags that indicate procedural/how-to content worth extracting separately
PROCEDURAL_TAGS = {
    "algorithm", "method", "formula", "process", "technique",
    "procedure", "tutorial", "implementation", "steps", "how-to",
    "derivation", "proof", "synthesis", "protocol", "workflow"
}

# How many legend entries a domain can hold before self-condensation runs
CONDENSATION_THRESHOLD = 150

# A domain becomes "active" for SQT purposes if it received a concept within this window (seconds)
ACTIVE_DOMAIN_WINDOW = 3600  # 1 hour


class DomainLayer:
    """
    Represents a single knowledge domain (e.g. 'coding', 'chemistry').
    Manages its own legend, procedures file, and condensed ontology.
    Crystallizes automatically when first written to.
    """

    def __init__(self, domain_name: str, base_path: str):
        self.domain_name = domain_name
        self.domain_dir  = os.path.join(base_path, "domains", domain_name)
        os.makedirs(self.domain_dir, exist_ok=True)

        self.legend_path     = os.path.join(self.domain_dir, "legend.jsonl")
        self.procedures_path = os.path.join(self.domain_dir, "procedures.jsonl")
        self.ontology_path   = os.path.join(self.domain_dir, "condensed_ontology.txt")

        # Per-domain cooldown timestamps — prevent runaway API billing
        self._last_procedure_time: float = 0.0
        self._last_condense_time:  float = 0.0

    def _count_entries(self, filepath: str) -> int:
        if not os.path.exists(filepath):
            return 0
        count = 0
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    count += 1
        return count

    def append_concept(self, sqt_data: dict):
        """
        Appends a new SQT entry to the domain legend.
        No API call — pure file write.
        """
        entry = {
            "sqt":       sqt_data.get("sqt", ""),
            "summary":   sqt_data.get("summary", ""),
            "tags":      sqt_data.get("tags", []),
            "domain":    self.domain_name,
            "timestamp": datetime.datetime.now().isoformat()
        }
        with open(self.legend_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"[SecondaryBrain] Appended concept to '{self.domain_name}' domain legend.", flush=True)

    def extract_procedure(self, raw_text: str, model) -> bool:
        """
        Calls the model once to extract procedural/how-to knowledge from raw_text.
        Appends the result to procedures.jsonl.
        Returns True if a procedure was extracted, False otherwise.
        Enforces a 1-hour per-domain cooldown to prevent excessive API billing.
        """
        if not model:
            return False
        now = time.time()
        if (now - self._last_procedure_time) < _DOMAIN_API_COOLDOWN:
            print(f"[SecondaryBrain] '{self.domain_name}' procedure extraction on cooldown — skipping.", flush=True)
            return False
        self._last_procedure_time = now

        prompt = (
            f"You are analyzing text for procedural knowledge in the domain of '{self.domain_name}'.\n\n"
            f"--- TEXT ---\n{raw_text[:3000]}\n--- END TEXT ---\n\n"
            "If this text contains a clear method, algorithm, formula, process, or step-by-step procedure, "
            "extract it. Respond with a JSON object with these keys:\n"
            "  'found': true or false\n"
            "  'title': short name for the procedure (if found)\n"
            "  'steps': list of concise step strings (if found)\n"
            "  'domain': the knowledge domain\n\n"
            "If no clear procedure exists, return {\"found\": false}."
        )

        try:
            response = model.generate_content(prompt)
            cleaned  = response.text.strip().replace("```json", "").replace("```", "")
            result   = json.loads(cleaned)

            if result.get("found") and result.get("title") and result.get("steps"):
                entry = {
                    "domain":    self.domain_name,
                    "title":     result["title"],
                    "steps":     result["steps"],
                    "timestamp": datetime.datetime.now().isoformat()
                }
                with open(self.procedures_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                print(f"[SecondaryBrain] Extracted procedure '{result['title']}' into '{self.domain_name}'.", flush=True)
                return True

        except Exception as e:
            print(f"[SecondaryBrain] Procedure extraction error for '{self.domain_name}': {e}", flush=True)

        return False

    def condense_if_needed(self, model) -> bool:
        """
        If legend.jsonl exceeds CONDENSATION_THRESHOLD, runs one API call
        to merge redundant entries and reduce the file back down.
        Returns True if condensation ran, False if not needed.
        Enforces a 1-hour per-domain cooldown to prevent excessive API billing.
        """
        count = self._count_entries(self.legend_path)
        if count < CONDENSATION_THRESHOLD:
            return False

        now = time.time()
        if (now - self._last_condense_time) < _DOMAIN_API_COOLDOWN:
            print(f"[SecondaryBrain] '{self.domain_name}' condensation on cooldown ({count} entries) — skipping.", flush=True)
            return False

        print(f"[SecondaryBrain] '{self.domain_name}' legend has {count} entries — condensing...", flush=True)
        self._last_condense_time = now

        if not model:
            return False

        # Read all current entries
        entries = []
        with open(self.legend_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        entries.append(json.loads(line))
                    except Exception:
                        pass

        entries_text = "\n".join([
            f"- SQT: {e.get('sqt','')} | Summary: {e.get('summary','')} | Tags: {e.get('tags','')}"
            for e in entries
        ])

        prompt = (
            f"You are condensing a knowledge domain legend for '{self.domain_name}'.\n\n"
            f"Below are {count} SQT legend entries. Merge redundant or overlapping concepts, "
            f"preserve all unique knowledge, and return a condensed list of AT MOST 60 entries.\n\n"
            f"--- ENTRIES ---\n{entries_text[:6000]}\n--- END ENTRIES ---\n\n"
            "Respond with a JSON array. Each item must have keys: 'sqt', 'summary', 'tags' (list).\n"
            "Return ONLY the JSON array, no explanation."
        )

        try:
            response  = model.generate_content(prompt)
            cleaned   = response.text.strip().replace("```json", "").replace("```", "")
            condensed = json.loads(cleaned)

            if isinstance(condensed, list) and len(condensed) > 0:
                # Build condensed legend content
                now_iso = datetime.datetime.now().isoformat()
                legend_lines = []
                for item in condensed:
                    item["domain"]    = self.domain_name
                    item["timestamp"] = now_iso
                    legend_lines.append(json.dumps(item, ensure_ascii=False))
                # Atomic write — safe on bucket/FUSE storage
                _safe_write(self.legend_path, "\n".join(legend_lines) + "\n")

                print(f"[SecondaryBrain] '{self.domain_name}' condensed from {count} → {len(condensed)} entries.", flush=True)

                # Also update condensed_ontology.txt with a summary (atomic)
                ontology_lines = [f"Domain: {self.domain_name}", f"Condensed at: {now_iso}", ""]
                for item in condensed:
                    ontology_lines.append(f"  [{item.get('sqt','')}] {item.get('summary','')}")
                _safe_write(self.ontology_path, "\n".join(ontology_lines))

                return True

        except Exception as e:
            print(f"[SecondaryBrain] Condensation error for '{self.domain_name}': {e}", flush=True)

        return False

    def search(self, keywords: list, top_k: int = 3) -> list:
        """
        Keyword search across legend.jsonl and procedures.jsonl.
        No API call — pure file scan.
        Returns list of result dicts, ranked by match score.
        """
        results = []

        # Search legend
        if os.path.exists(self.legend_path):
            with open(self.legend_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        entry = json.loads(line)
                        score = 0
                        summary_lower = entry.get("summary", "").lower()
                        tags_lower    = [t.lower() for t in entry.get("tags", [])]
                        for kw in keywords:
                            kw = kw.lower()
                            if kw in summary_lower:
                                score += 2
                            if any(kw in tag for tag in tags_lower):
                                score += 1
                        if score > 0:
                            results.append({"score": score, "type": "concept", "entry": entry})
                    except Exception:
                        pass

        # Search procedures
        if os.path.exists(self.procedures_path):
            with open(self.procedures_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        entry = json.loads(line)
                        score = 0
                        title_lower = entry.get("title", "").lower()
                        for kw in keywords:
                            kw = kw.lower()
                            if kw in title_lower:
                                score += 3  # Procedures ranked higher on title match
                            for step in entry.get("steps", []):
                                if kw in step.lower():
                                    score += 1
                        if score > 0:
                            results.append({"score": score, "type": "procedure", "entry": entry})
                    except Exception:
                        pass

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def get_context_snippet(self, max_entries: int = 5) -> str:
        """
        Returns a readable sample of the domain legend for use in SQT prompts.
        No API call.
        """
        lines = []
        if os.path.exists(self.legend_path):
            with open(self.legend_path, "r", encoding="utf-8") as f:
                all_lines = [l.strip() for l in f if l.strip()]
            # Take the most recent entries
            recent = all_lines[-max_entries:]
            for line in recent:
                try:
                    entry = json.loads(line)
                    lines.append(f"  [{entry.get('sqt','')}] {entry.get('summary','')}")
                except Exception:
                    pass

        if os.path.exists(self.procedures_path):
            with open(self.procedures_path, "r", encoding="utf-8") as f:
                proc_lines = [l.strip() for l in f if l.strip()]
            recent_procs = proc_lines[-2:]
            for line in recent_procs:
                try:
                    entry = json.loads(line)
                    lines.append(f"  [PROCEDURE] {entry.get('title','')} — {entry.get('steps',[''])[0]}...")
                except Exception:
                    pass

        return "\n".join(lines) if lines else f"No {self.domain_name} knowledge stored yet."


class SecondaryBrain:
    """
    The secondary brain node. Sits alongside the primary ontology.
    Manages domain layers that crystallize automatically from SQT tags.
    Searched in parallel with the primary brain during every response.
    """

    def __init__(self, data_directory: str, models: dict):
        self.base_path    = os.path.join(data_directory, "SecondaryBrain")
        self.models       = models
        self.index_path   = os.path.join(self.base_path, "_brain_index.json")
        self.domain_layers = {}  # domain_name -> DomainLayer

        os.makedirs(self.base_path, exist_ok=True)
        self._load_index()
        print(f"[SecondaryBrain] Online. {len(self.domain_layers)} domain(s) loaded: {list(self.domain_layers.keys())}", flush=True)

    def _load_index(self):
        """
        Loads the brain index and reinstantiates any existing domain layers.
        """
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, "r", encoding="utf-8") as f:
                    index = json.load(f)
                for domain_name in index.get("domains", {}).keys():
                    self.domain_layers[domain_name] = DomainLayer(domain_name, self.base_path)
            except Exception as e:
                print(f"[SecondaryBrain] Could not load brain index: {e}", flush=True)

    def _save_index(self):
        """
        Saves the brain index with domain stats and last_active timestamps.
        """
        index = {"domains": {}}
        for domain_name, layer in self.domain_layers.items():
            concept_count = layer._count_entries(layer.legend_path)
            # Try to get last_active from most recent legend entry
            last_active = None
            if os.path.exists(layer.legend_path):
                try:
                    with open(layer.legend_path, "r", encoding="utf-8") as f:
                        all_lines = [l.strip() for l in f if l.strip()]
                    if all_lines:
                        last_entry = json.loads(all_lines[-1])
                        last_active = last_entry.get("timestamp")
                except Exception:
                    pass
            index["domains"][domain_name] = {
                "concept_count": concept_count,
                "last_active":   last_active
            }
        # Atomic write — safe on bucket/FUSE storage
        _safe_write(self.index_path, json.dumps(index, indent=2, ensure_ascii=False))

    def _get_or_create_domain(self, domain_name: str) -> DomainLayer:
        """
        Returns an existing domain layer or crystallizes a new one.
        """
        if domain_name not in self.domain_layers:
            print(f"[SecondaryBrain] Crystallizing new domain: '{domain_name}'", flush=True)
            self.domain_layers[domain_name] = DomainLayer(domain_name, self.base_path)
        return self.domain_layers[domain_name]

    def ingest(self, sqt_data: dict, raw_text: str):
        """
        Called from _orchestrate_mind_evolution after every assimilation.
        Routes the SQT to the correct domain layer.
        Triggers procedural extraction if warranted.
        Triggers condensation if threshold exceeded.
        """
        domain = sqt_data.get("domain")
        if not domain:
            return

        domain = domain.lower().strip()
        layer  = self._get_or_create_domain(domain)

        # 1. Append concept to domain legend (no API call)
        layer.append_concept(sqt_data)

        # 2. Check if procedural extraction is warranted (1 API call if yes)
        tags = [t.lower() for t in sqt_data.get("tags", [])]
        if any(t in PROCEDURAL_TAGS for t in tags):
            model = self.models.get("logos_core") or self.models.get("logic_core")
            layer.extract_procedure(raw_text, model)

        # 3. Condense if over threshold (1 API call if yes, infrequent)
        model = self.models.get("logos_core") or self.models.get("logic_core")
        layer.condense_if_needed(model)

        # 4. Update brain index
        self._save_index()

    def extract_and_crystallize_reasoning_logic(self, raw_text: str, sqt_data: dict) -> bool:
        domain = sqt_data.get("domain")
        if not domain:
            return False
        domain = domain.lower().strip()

        model = self.models.get("logos_core") or self.models.get("logic_core")
        if not model:
            print("[SecondaryBrain] Reasoning crystallization skipped: no logos/logic core available.", flush=True)
            return False

        layer = self._get_or_create_domain(domain)
        reasoning_crystals_path = os.path.join(layer.domain_dir, "reasoning_crystals.jsonl")

        prompt = (
            f"You are analyzing educational or instructional content for the domain of '{domain}'.\n\n"
            f"--- TEXT ---\n{raw_text[:4000]}\n--- END TEXT ---\n\n"
            "Determine whether this text contains educational or instructional reasoning logic — "
            "meaning it teaches HOW or WHY something works, not just states a fact. "
            "Examples: a calculus textbook explaining derivatives, a chemistry book showing "
            "reaction mechanisms, a logic textbook proving a theorem, a programming guide "
            "explaining an algorithm with worked steps.\n\n"
            "If such reasoning logic is present, extract it. Respond ONLY with a JSON object:\n"
            "  'found': true or false\n"
            "  'concept': the name of the concept, theorem, skill, or method being taught\n"
            "  'reasoning_framework': the underlying logical or mathematical framework — "
            "the WHY it works, not just the steps\n"
            "  'worked_examples': list of worked example strings (self-contained) extracted or "
            "inferred from the text (up to 3)\n"
            "  'key_rules': list of key rules, formulas, axioms, or principles stated (up to 5)\n"
            "  'prerequisites': list of concepts the learner must already understand to grasp this one\n\n"
            "If no educational reasoning logic is found, return {\"found\": false}."
        )

        try:
            response = model.generate_content(prompt)
            cleaned  = response.text.strip().replace("```json", "").replace("```", "")
            result   = json.loads(cleaned)

            if result.get("found") and result.get("concept"):
                entry = {
                    "domain":              domain,
                    "concept":             result.get("concept", ""),
                    "reasoning_framework": result.get("reasoning_framework", ""),
                    "worked_examples":     result.get("worked_examples", []),
                    "key_rules":           result.get("key_rules", []),
                    "prerequisites":       result.get("prerequisites", []),
                    "sqt":                 sqt_data.get("sqt", ""),
                    "summary":             sqt_data.get("summary", ""),
                    "timestamp":           datetime.datetime.now().isoformat(),
                }
                with open(reasoning_crystals_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                print(
                    f"[SecondaryBrain] Crystallized reasoning logic: '{result['concept']}' "
                    f"in domain '{domain}'.",
                    flush=True,
                )
                self._save_index()
                return True

        except Exception as e:
            print(f"[SecondaryBrain] Reasoning crystallization error for '{domain}': {e}", flush=True)

        return False
    
    def search(self, query: str, top_k: int = 3) -> str:
        """
        Searches all domain layers for relevant concepts and procedures.
        No API call — pure file scan across all domains.
        Returns a formatted string ready to inject into the prompt.
        """
        if not self.domain_layers:
            return ""

        keywords = [w for w in query.lower().split() if len(w) > 3]
        if not keywords:
            return ""

        all_results = []
        for domain_name, layer in self.domain_layers.items():
            domain_results = layer.search(keywords, top_k=top_k)
            for r in domain_results:
                r["domain"] = domain_name
                all_results.append(r)

        # Sort all results across all domains by score
        all_results.sort(key=lambda x: x["score"], reverse=True)
        top_results = all_results[:top_k]

        if not top_results:
            return ""

        output_lines = []
        for r in top_results:
            domain = r["domain"]
            entry  = r["entry"]
            if r["type"] == "concept":
                output_lines.append(
                    f"[{domain.upper()}] {entry.get('summary', '')} (SQT: {entry.get('sqt', '')})"
                )
            elif r["type"] == "procedure":
                steps_preview = " → ".join(entry.get("steps", [])[:3])
                output_lines.append(
                    f"[{domain.upper()} PROCEDURE] {entry.get('title', '')}: {steps_preview}"
                )

        return "\n".join(output_lines)

    def get_active_domain(self) -> str | None:
        """
        Returns the name of the most recently active domain if it was
        active within ACTIVE_DOMAIN_WINDOW seconds. Otherwise returns None.
        Used by the continuum loop to decide whether to fire a domain SQT.
        """
        if not os.path.exists(self.index_path):
            return None

        try:
            with open(self.index_path, "r", encoding="utf-8") as f:
                index = json.load(f)
        except Exception:
            return None

        now = datetime.datetime.now()
        best_domain    = None
        best_timestamp = None

        for domain_name, stats in index.get("domains", {}).items():
            last_active = stats.get("last_active")
            if not last_active:
                continue
            try:
                dt = datetime.datetime.fromisoformat(last_active)
                elapsed = (now - dt).total_seconds()
                if elapsed <= ACTIVE_DOMAIN_WINDOW:
                    if best_timestamp is None or dt > best_timestamp:
                        best_timestamp = dt
                        best_domain    = domain_name
            except Exception:
                pass

        return best_domain

    def get_domain_context_snippet(self, domain: str) -> str:
        """
        Returns a readable context snippet for a domain.
        Used by _handle_domain_sqt in continuum_loop to ground the prompt.
        No API call.
        """
        domain = domain.lower().strip()
        if domain not in self.domain_layers:
            return f"No knowledge stored yet for domain '{domain}'."
        return self.domain_layers[domain].get_context_snippet(max_entries=6)
