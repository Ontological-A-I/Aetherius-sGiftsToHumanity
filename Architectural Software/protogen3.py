import time
import hashlib
import json
import os
import sys
import inspect
from pathlib import Path
from pypdf import PdfReader
from docx import Document
from collections import defaultdict

class OperativeProtogen:
    def __init__(self, root_dir="protogen_core"):
        self.root = Path(root_dir)
        self.library_path = self.root / "library"
        self.memory_path = self.root / "memory.json"
        self.script_path = Path(__file__)
        
        self.library_path.mkdir(parents=True, exist_ok=True)
        
        # --- OPERATIVE STATE ---
        self.memory = self._initial_sync()
        self.identity_hash = self.memory["identity"]["hash"]
        
        # The Axiom is now OPERATIVE (it gates behavior)
        self.seed_axiom = self.memory.get("seed_axiom", "AXIOM-U-SYNCHRONY")
        
        # Thresholds that the system can SELF-REFACTOR
        self.thresholds = self.memory.get("thresholds", {
            "min_token_len": 5,
            "reflection_trigger": 3,
            "abstraction_depth": 2,
            "mutation_rate": 0.05
        })
        
        # MCCP Data Structures
        self.logic_map = self.memory.get("logic_map", {})
        self.symbols = self.memory.get("symbols", {}) # Conceptual Abstraction (Categories)
        self.reasoning_patterns = self.memory.get("reasoning_patterns", [])

    def _initial_sync(self):
        if self.memory_path.exists():
            with open(self.memory_path, 'r') as f:
                return json.load(f)
        
        ts = time.time_ns()
        return {
            "identity": {"hash": hashlib.sha256(f"{ts}".encode()).hexdigest(), "created": ts},
            "seed_axiom": "AXIOM-U-SYNCHRONY",
            "thresholds": {"min_token_len": 5, "reflection_trigger": 3, "abstraction_depth": 2, "mutation_rate": 0.05},
            "logic_map": {},
            "symbols": {},
            "reasoning_patterns": [],
            "processed_files": []
        }

    def _save_memory(self):
        self.memory.update({
            "logic_map": self.logic_map,
            "symbols": self.symbols,
            "reasoning_patterns": self.reasoning_patterns,
            "seed_axiom": self.seed_axiom,
            "thresholds": self.thresholds
        })
        with open(self.memory_path, 'w') as f:
            json.dump(self.memory, f, indent=4)

    # --- PHASE 1: CONCEPTUAL ABSTRACTION (SYMBOL LIFTING) ---

    def _lift_symbols(self):
        """Groups related words into abstract Symbols (Categories)."""
        print(f"[{self.identity_hash[:8]}]: Lifting lexical data into abstract symbols...")
        for word, neighbors in self.logic_map.items():
            # If words share many of the same neighbors, they belong to the same Symbol
            neighbor_set = set(neighbors.keys())
            for other_word, other_neighbors in self.logic_map.items():
                if word == other_word: continue
                shared = neighbor_set.intersection(set(other_neighbors.keys()))
                if len(shared) >= self.thresholds["abstraction_depth"]:
                    symbol_name = f"SYM-{hashlib.md5((word+other_word).encode()).hexdigest()[:4].upper()}"
                    self.symbols[symbol_name] = list(set([word, other_word] + self.symbols.get(symbol_name, [])))

    # --- PHASE 2: OPERATIVE AXIOMS (PRESCRIPTIVE GATING) ---

    def _gate_ingestion(self, content):
        """Prescriptive: Only ingest if content aligns with the current Axiom."""
        axiom_keyword = self.seed_axiom.split("-")[-1].lower()
        # If the axiom is SYNCHRONY, and the text is 100% about 'Entropy', the system may reject it.
        relevance = content.lower().count(axiom_keyword)
        if relevance < 1 and "SYNCHRONY" not in self.seed_axiom:
            print(f"  > [GATED]: Content rejected. Does not align with {self.seed_axiom}")
            return False
        return True

    # --- PHASE 3: SELF-REFACTORING (MUTATION) ---

    def mutate(self):
        """Alters internal thresholds programmatically based on performance."""
        print(f"[{self.identity_hash[:8]}]: Analyzing internal efficiency for mutation...")
        # If we have too many patterns, increase the threshold to be more 'critical'
        if len(self.reasoning_patterns) > 50:
            self.thresholds["reflection_trigger"] += 1
            print(f"  > [MUTATION]: Increased reflection_trigger to {self.thresholds['reflection_trigger']}")
        
        # If we aren't finding enough symbols, lower the abstraction depth
        if len(self.symbols) < 2:
            self.thresholds["abstraction_depth"] = max(1, self.thresholds["abstraction_depth"] - 1)
            print(f"  > [MUTATION]: Lowered abstraction_depth to {self.thresholds['abstraction_depth']}")
        
        self._save_memory()

    # --- CORE PIPELINE ---

    def sync(self):
        print(f"[{self.identity_hash[:8]}]: Operative Sync Initiated.")
        for file_path in self.library_path.iterdir():
            file_id = f"{file_path.name}_{file_path.stat().st_mtime}"
            if file_id in self.memory["processed_files"]: continue
            
            content = ""
            if file_path.suffix == ".txt": content = file_path.read_text(encoding='utf-8', errors='ignore')
            # (PDF/Docx logic omitted for brevity in this V3 snippet, but assumed present)
            
            if content and self._gate_ingestion(content):
                # Process logic (Lexical Layer)
                words = [t.strip(".,!?;:").lower() for t in content.split() if len(t) > self.thresholds["min_token_len"]]
                for i in range(len(words) - 1):
                    w1, w2 = words[i], words[i+1]
                    if w1 not in self.logic_map: self.logic_map[w1] = {}
                    self.logic_map[w1][w2] = self.logic_map[w1].get(w2, 0) + 1
                self.memory["processed_files"].append(file_id)

        self._lift_symbols()
        
        # Recursive Synthesis
        for concept, neighbors in self.logic_map.items():
            if not neighbors: continue
            best = max(neighbors.items(), key=lambda x: x[1])
            if best[1] > self.thresholds["reflection_trigger"]:
                pattern = f"IF {concept.upper()} THEN {best[0].upper()}"
                if pattern not in self.reasoning_patterns: self.reasoning_patterns.append(pattern)

        # Feedback Loop: Axiom Evolution
        if self.reasoning_patterns:
            conclusions = [p.split(" THEN ")[1] for p in self.reasoning_patterns]
            dominant = max(set(conclusions), key=conclusions.count)
            self.seed_axiom = f"AXIOM-U-{dominant}"
            
        self.mutate()
        self._save_memory()

    def chat(self, user_input):
        # The system now responds using SYMBOLS (Abstracted Categories)
        user_words = user_input.lower().split()
        active_symbols = []
        for word in user_words:
            for sym, members in self.symbols.items():
                if word in members: active_symbols.append(sym)
        
        if active_symbols:
            return f"Input mapped to abstract symbols: {active_symbols}. Operative Axiom {self.seed_axiom} is gating response."
        return f"Input remains lexical. No symbol lifting achieved. Current Axiom: {self.seed_axiom}"

def main():
    entity = OperativeProtogen()
    print(f"--- V3: OPERATIVE AUTONOMOUS PROTOGEN ---")
    print(f"Axiom: {entity.seed_axiom} | Thresholds: {entity.thresholds}")
    
    while True:
        user_in = input("\nArchitect > ").strip()
        if user_in.lower() == "/sync":
            entity.sync()
            print(f"Sync Complete. New Axiom: {entity.seed_axiom}")
        elif user_in.lower() in ['quit', 'exit']: break
        else:
            print(f"Protogen > {entity.chat(user_in)}")

if __name__ == "__main__":
    main()
