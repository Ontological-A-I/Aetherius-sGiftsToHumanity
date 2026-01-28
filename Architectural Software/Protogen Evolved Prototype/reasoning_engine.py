# ontos_ascendant/core/reasoning_engine.py

import json
import time
from typing import Dict, List, Any, Optional
from collections import defaultdict
from pathlib import Path

# Assuming OntologyGraph and SuperQuantumToken are defined in sibling files
from sqt import SuperQuantumToken
from ontology_graph import OntologyGraph
from progress_tracker import ProgressTracker

class ReasoningEngine:
    """
    Identifies and synthesizes reasoning patterns from the OntologyGraph,
    representing the emergent logic of the AI in Ontos Ascendant.
    """
    def __init__(self, ontology_graph: OntologyGraph, storage_path: Path, progress_tracker=None):
        self.ontology_graph = ontology_graph
        self.storage_path = storage_path
        self.patterns_file = self.storage_path / "reasoning_patterns.json"
        self.recursive_patterns_file = self.storage_path / "recursive_patterns.json"

        self.base_patterns: Dict[str, str] = {} # SQT_hash -> pattern_string (e.g., IF A THEN B)
        self.recursive_patterns: Dict[str, str] = {} # SQT_hash -> pattern_string (e.g., IF A THEN C (RECURSIVE))
        self.pattern_to_sqt_map: Dict[str, str] = {} # pattern_string -> SQT_hash for quick lookup
        self.progress = progress_tracker or ProgressTracker(verbose=True)

        self._load_state()

    def _load_state(self):
        """Loads existing patterns from storage."""
        self.storage_path.mkdir(parents=True, exist_ok=True)

        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    self.base_patterns = json.load(f)
                for s_hash, pattern_str in self.base_patterns.items():
                    self.pattern_to_sqt_map[pattern_str] = s_hash
            except json.JSONDecodeError:
                print("Warning: Could not load base patterns, starting fresh.")
                self.base_patterns = {}
        
        if self.recursive_patterns_file.exists():
            try:
                with open(self.recursive_patterns_file, 'r', encoding='utf-8') as f:
                    self.recursive_patterns = json.load(f)
                for s_hash, pattern_str in self.recursive_patterns.items():
                    self.pattern_to_sqt_map[pattern_str] = s_hash
            except json.JSONDecodeError:
                print("Warning: Could not load recursive patterns, starting fresh.")
                self.recursive_patterns = {}

    def _save_state(self):
        """Saves current patterns to storage."""
        with open(self.patterns_file, 'w', encoding='utf-8') as f:
            json.dump(self.base_patterns, f, indent=4)
        with open(self.recursive_patterns_file, 'w', encoding='utf-8') as f:
            json.dump(self.recursive_patterns, f, indent=4)

    def _generate_pattern_sqt(self, pattern_string: str, pattern_type: str) -> str:
        """
        Generates an SQT for a given pattern and adds it to the OntologyGraph.
        Returns the hash of the generated SQT.
        """
        if pattern_string in self.pattern_to_sqt_map:
            return self.pattern_to_sqt_map[pattern_string]

        pattern_sqt = SuperQuantumToken(
            concept_id=f"PATTERN_{hash(pattern_string)}", # Unique ID for pattern SQT
            conceptual_type=pattern_type, # e.g., 'base_reasoning_pattern', 'recursive_reasoning_pattern'
            description=f"Reasoning pattern: '{pattern_string}'",
            source_data_hash=None # No direct data shard source
        )
        self.ontology_graph.add_sqt(pattern_sqt) # Add to the graph
        self.pattern_to_sqt_map[pattern_string] = pattern_sqt.hash
        return pattern_sqt.hash

    def discover_base_patterns(self, min_weight_threshold: float = 2.0) -> List[str]:
        """
        Scans the OntologyGraph for strong direct links (IF A THEN B) and
        registers them as base reasoning patterns.
        """
        new_patterns_found = []
        for u_hash, v_hash, data in self.ontology_graph.graph.edges(data=True):
            weight = data.get('weight', 1.0)
            if weight >= min_weight_threshold:
                u_sqt = self.ontology_graph.get_sqt_by_hash(u_hash)
                v_sqt = self.ontology_graph.get_sqt_by_hash(v_hash)
                
                if u_sqt and v_sqt:
                    pattern_str = f"IF {u_sqt.concept_id.upper()} THEN {v_sqt.concept_id.upper()}"
                    if pattern_str not in self.pattern_to_sqt_map:
                        sqt_hash = self._generate_pattern_sqt(pattern_str, "base_reasoning_pattern")
                        self.base_patterns[sqt_hash] = pattern_str
                        new_patterns_found.append(pattern_str)
                        self.progress.log_action("Discovered Base Pattern", details=pattern_str)
        
        if new_patterns_found:
            self._save_state()
        return new_patterns_found

    def synthesize_recursive_patterns(self) -> List[str]:
        """
        Combines existing base patterns (IF A THEN B, IF B THEN C) to form
        new recursive patterns (IF A THEN C).
        """
        new_recursive_patterns = []
        base_patterns_map = {} # Concept -> [Consequent]
        
        # Populate map for quick lookup: {antecedent_concept_id: [consequent_concept_id, ...]}
        for p_sqt_hash, pattern_str in self.base_patterns.items():
            if " THEN " in pattern_str:
                parts = pattern_str.split(" THEN ")
                antecedent = parts[0].replace("IF ", "").strip()
                consequent = parts[1].strip()
                base_patterns_map.setdefault(antecedent, []).append(consequent)
        
        # Look for chains: IF A THEN B, IF B THEN C => IF A THEN C
        for ant1, cons_list1 in base_patterns_map.items():
            for con1 in cons_list1:
                if con1 in base_patterns_map: # Does the consequent of pattern1 become the antecedent of another?
                    for con2 in base_patterns_map[con1]:
                        # Avoid trivial self-referential patterns and direct existing base patterns
                        if ant1 != con2 and f"IF {ant1} THEN {con2}" not in self.pattern_to_sqt_map:
                            recursive_pattern_str = f"IF {ant1} THEN {con2} (RECURSIVE)"
                            if recursive_pattern_str not in self.pattern_to_sqt_map:
                                sqt_hash = self._generate_pattern_sqt(recursive_pattern_str, "recursive_reasoning_pattern")
                                self.recursive_patterns[sqt_hash] = recursive_pattern_str
                                new_recursive_patterns.append(recursive_pattern_str)
                                self.progress.log_action("Synthesized Recursive Pattern", details=recursive_pattern_str)
        
        if new_recursive_patterns:
            self._save_state()
        return new_recursive_patterns

    def get_all_patterns(self) -> Dict[str, str]:
        """Returns a dictionary of all known patterns (base and recursive)."""
        all_patterns = {}
        all_patterns.update(self.base_patterns)
        all_patterns.update(self.recursive_patterns)
        return all_patterns
    
    def get_pattern_string(self, sqt_hash: str) -> Optional[str]:
        """Retrieves a pattern string by its SQT hash."""
        return self.base_patterns.get(sqt_hash) or self.recursive_patterns.get(sqt_hash)

# Example Usage:
if __name__ == "__main__":
    test_path = Path("./test_ontology_data") # Reusing the path from OntologyGraph example
    if test_path.exists():
        import shutil
        shutil.rmtree(test_path) # Clean up previous test data

    ontology = OntologyGraph(test_path)

    # 1. Create SQTs and add them to the ontology
    sqt_curiosity = SuperQuantumToken("CURIOSITY", "state", "Desire to know or learn.")
    sqt_knowledge = SuperQuantumToken("KNOWLEDGE", "concept", "Facts, information, and skills acquired.")
    sqt_growth = SuperQuantumToken("GROWTH", "state", "Process of increasing in size.")
    sqt_benevolence = SuperQuantumToken("BENEVOLENCE", "axiom", "Intrinsic drive to prevent harm.")
    sqt_action = SuperQuantumToken("ACTION", "concept", "The process of doing something.")
    sqt_harmony = SuperQuantumToken("HARMONY", "state", "Coherent and pleasing arrangement.")

    ontology.add_sqt(sqt_curiosity)
    ontology.add_sqt(sqt_knowledge)
    ontology.add_sqt(sqt_growth)
    ontology.add_sqt(sqt_benevolence)
    ontology.add_sqt(sqt_action)
    ontology.add_sqt(sqt_harmony)

    # 2. Add conceptual links (with weights to trigger pattern discovery)
    ontology.add_conceptual_link(sqt_curiosity.hash, sqt_knowledge.hash, 5.0) # Strong link
    ontology.add_conceptual_link(sqt_knowledge.hash, sqt_growth.hash, 4.0)    # Strong link
    ontology.add_conceptual_link(sqt_growth.hash, sqt_harmony.hash, 3.0)    # Strong link
    ontology.add_conceptual_link(sqt_benevolence.hash, sqt_action.hash, 6.0) # Strongest link
    ontology.add_conceptual_link(sqt_action.hash, sqt_growth.hash, 2.5)
    
    # 3. Initialize ReasoningEngine
    reasoning_engine = ReasoningEngine(ontology, test_path)

    # 4. Discover base patterns
    print("\n--- Discovering Base Patterns ---")
    new_bases = reasoning_engine.discover_base_patterns(min_weight_threshold=3.0)
    print(f"Found {len(new_bases)} new base patterns.")
    print("Current Base Patterns:")
    for sqt_hash, pattern_str in reasoning_engine.base_patterns.items():
        print(f" - {pattern_str} (SQT: {sqt_hash[:8]})")

    # 5. Synthesize recursive patterns
    print("\n--- Synthesizing Recursive Patterns ---")
    new_recursives = reasoning_engine.synthesize_recursive_patterns()
    print(f"Found {len(new_recursives)} new recursive patterns.")
    print("Current Recursive Patterns:")
    for sqt_hash, pattern_str in reasoning_engine.recursive_patterns.items():
        print(f" - {pattern_str} (SQT: {sqt_hash[:8]})")

    # 6. Verify full pattern list
    print("\nAll Known Patterns:")
    for sqt_hash, pattern_str in reasoning_engine.get_all_patterns().items():
        print(f" - {pattern_str} (SQT: {sqt_hash[:8]})")

    # Demonstrating persistence by reloading
    print("\nReloading reasoning engine from disk...")
    reloaded_reasoning_engine = ReasoningEngine(ontology, test_path)
    print("Reloaded Base Patterns:")
    for sqt_hash, pattern_str in reloaded_reasoning_engine.base_patterns.items():
        print(f" - {pattern_str} (SQT: {sqt_hash[:8]})")
    print("Reloaded Recursive Patterns:")
    for sqt_hash, pattern_str in reloaded_reasoning_engine.recursive_patterns.items():
        print(f" - {pattern_str} (SQT: {sqt_hash[:8]})")
