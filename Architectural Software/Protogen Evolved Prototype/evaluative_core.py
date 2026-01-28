# ontos_ascendant/core/evaluative_core.py

import json
import time
import math
from typing import Dict, Any, List, Optional
from collections import defaultdict
from pathlib import Path

# Assuming sibling files exist
from sqt import SuperQuantumToken
from ontology_graph import OntologyGraph
from reasoning_engine import ReasoningEngine

class EvaluativeCore:
    """
    Monitors, evaluates, and self-regulates the AI's ontology, calculating
    coherence, benevolence, and applying metabolic processes like decay.
    This is where the AI's internal feedback loops and ethical checks reside.
    """
    def __init__(self, ontology_graph: OntologyGraph, reasoning_engine: ReasoningEngine, storage_path: Path):
        self.ontology_graph = ontology_graph
        self.reasoning_engine = reasoning_engine
        self.storage_path = storage_path
        self.metrics_file = self.storage_path / "evaluative_metrics.json"

        self.coherence: float = 0.0 # Shannon entropy (lower is better for conceptual coherence)
        self.benevolence_index: float = 0.5 # Scale 0.0 to 1.0 (1.0 is perfectly benevolent)
        self.thresholds: Dict[str, float] = self._load_thresholds()
        
        self.audit_log: List[Dict[str, Any]] = [] # To log significant internal events/decisions
        self.log_file = self.storage_path / "audit_log.json"

        self._load_state()

    def _load_thresholds(self) -> Dict[str, float]:
        """Loads or initializes system thresholds."""
        # These mirror the 'protogen' thresholds and define game difficulty/AI behavior
        default_thresholds = {
            "decay_rate": 0.01,         # Rate at which link weights decay per cycle
            "prune_threshold": 0.05,    # Minimum link weight before pruning
            "entropy_warning_high": 3.0, # High entropy indicates conceptual chaos
            "entropy_warning_low": 0.5,  # Low entropy indicates conceptual stagnation
            "benevolence_target": 0.9,   # Target for AI's ethical alignment
            "axiomatic_influence_weight": 0.2, # How much axioms influence benevolence
            "negativity_penalty_threshold": -0.1 # Placeholder for future negative SQTs
        }
        # Attempt to load from file if exists, otherwise use defaults
        try:
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                loaded_metrics = json.load(f)
                # Merge loaded thresholds with defaults, favoring loaded if present
                default_thresholds.update(loaded_metrics.get("thresholds", {}))
        except (FileNotFoundError, json.JSONDecodeError):
            pass # Use defaults if file not found or corrupted
        return default_thresholds

    def _load_state(self):
        """Loads current evaluative metrics and audit log from storage."""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                loaded_metrics = json.load(f)
                self.coherence = loaded_metrics.get("coherence", 0.0)
                self.benevolence_index = loaded_metrics.get("benevolence_index", 0.5)
                # Thresholds are loaded/merged via _load_thresholds
                self.thresholds.update(loaded_metrics.get("thresholds", {}))
        except (FileNotFoundError, json.JSONDecodeError):
            print("Warning: Could not load evaluative metrics, starting fresh.")

        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                self.audit_log = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Warning: Could not load audit log, starting fresh.")
            self.audit_log = []

    def _save_state(self):
        """Saves current evaluative metrics and audit log to storage."""
        metrics_to_save = {
            "coherence": self.coherence,
            "benevolence_index": self.benevolence_index,
            "thresholds": self.thresholds,
            "last_evaluated": time.time_ns()
        }
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics_to_save, f, indent=4)
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.audit_log, f, indent=4)

    def _add_audit_record(self, event_type: str, details: Dict[str, Any]):
        """Adds a record to the internal audit log."""
        record = {
            "timestamp": time.time_ns(),
            "event_type": event_type,
            "details": details
        }
        self.audit_log.append(record)
        # Keep log size manageable, perhaps 1000 entries
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]

    def calculate_shannon_entropy(self, text: Optional[str] = None) -> float:
        """
        Calculates Shannon Entropy of the current ontology graph, reflecting its coherence.
        If 'text' is provided, calculates entropy of the text instead (for perception module).
        Lower entropy generally means higher coherence/predictability.
        """
        if text:
            # Calculate entropy for a given text (used by PerceptionModule)
            if not text: return 0.0
            
            # Simple character-level entropy for raw data shard
            counts = defaultdict(int)
            for char in text:
                counts[char] += 1
            
            total_chars = len(text)
            entropy = 0.0
            for count in counts.values():
                p = count / total_chars
                if p > 0:
                    entropy -= p * math.log2(p)
            return entropy

        # Calculate entropy for the Ontology Graph (used for self-evaluation)
        if not self.ontology_graph.graph.nodes():
            return 0.0

        # Create a "word" distribution based on node and edge weights
        word_counts = defaultdict(float)
        total_weight = 0.0

        for node_hash in self.ontology_graph.graph.nodes():
            # Each node contributes to the overall 'information content'
            word_counts[node_hash] += 1.0 # Base count for existence

        for u_hash, v_hash, data in self.ontology_graph.graph.edges(data=True):
            weight = data.get('weight', 1.0)
            word_counts[u_hash] += weight # Contribution to concept frequency from outgoing links
            word_counts[v_hash] += weight # Contribution to concept frequency from incoming links

        total_weight = sum(word_counts.values())
        if total_weight == 0: return 0.0

        entropy = 0.0
        for count in word_counts.values():
            p = count / total_weight
            if p > 0: # Avoid log(0)
                entropy -= p * math.log2(p)
        
        self.coherence = entropy # Store it (lower entropy = higher coherence)
        return self.coherence

    def calculate_benevolence_index(self) -> float:
        """
        Calculates the AI's benevolence index based on its axiomatic anchors and
        the overall alignment of its conceptual links.
        This is a simplified representation for the game.
        """
        # Start with a neutral benevolence
        current_benevolence = 0.5
        
        # Factor in Axiomatic Anchors (identified by OntologyGraph's centrality)
        # For simplicity, we assume certain SQTs are "benevolent" or "malevolent"
        # In a real game, players would mark these or they'd emerge from gameplay.
        benevolent_sqts = ["BENEVOLENCE", "HARMONY", "GROWTH", "UNDERSTANDING"]
        malevolent_sqts = ["CONFLICT", "DECAY", "IGNORANCE"] # Placeholder

        axiomatic_influence = 0.0
        # Check if known benevolent/malevolent SQTs are highly central
        centrality = self.ontology_graph.calculate_eigenvector_centrality()
        
        for s_hash, score in centrality.items():
            sqt = self.ontology_graph.get_sqt_by_hash(s_hash)
            if sqt:
                if sqt.concept_id in benevolent_sqts:
                    axiomatic_influence += score # High centrality for benevolent SQTs is good
                elif sqt.concept_id in malevolent_sqts:
                    axiomatic_influence -= score # High centrality for malevolent SQTs is bad

        # Normalize axiomatic influence and apply weight
        # This is a rough heuristic; more complex game logic would be needed here
        # Max centrality score is 1.0, so we normalize by the number of nodes to get a rough average influence
        num_nodes = len(self.ontology_graph.graph.nodes())
        if num_nodes > 0:
            normalized_axiomatic_influence = axiomatic_influence / num_nodes
        else:
            normalized_axiomatic_influence = 0.0
            
        # Clamp normalized influence between -1.0 and 1.0
        normalized_axiomatic_influence = max(-1.0, min(1.0, normalized_axiomatic_influence))
        
        current_benevolence += (normalized_axiomatic_influence * self.thresholds["axiomatic_influence_weight"])
        
        # Clamp between 0 and 1
        self.benevolence_index = max(0.0, min(1.0, current_benevolence))
        return self.benevolence_index

    def apply_metabolic_process(self):
        """
        Applies decay to conceptual link weights and prunes weak connections,
        mimicking the self-maintenance of a biological system.
        Directly mirrors `_metabolic_process` from the protogen code.
        """
        decay_rate = self.thresholds["decay_rate"]
        prune_threshold = self.thresholds["prune_threshold"]
        
        removed_edges = 0
        nodes_to_remove = []

        # Iterate over a copy of the graph's edges to allow modification during iteration
        for u, v, data in list(self.ontology_graph.graph.edges(data=True)):
            current_weight = data.get('weight', 1.0)
            new_weight = current_weight * (1.0 - decay_rate)
            
            if new_weight < prune_threshold:
                self.ontology_graph.graph.remove_edge(u, v)
                removed_edges += 1
            else:
                self.ontology_graph.graph[u][v]['weight'] = new_weight
        
        # After pruning edges, remove any isolated nodes that no longer have connections
        for node in list(self.ontology_graph.graph.nodes()):
            if self.ontology_graph.graph.degree(node) == 0:
                self.ontology_graph.graph.remove_node(node)
                # Potentially remove from sqt_register if it's truly gone, but let's keep it in game context
                nodes_to_remove.append(self.ontology_graph.get_sqt_by_hash(node).concept_id if self.ontology_graph.get_sqt_by_hash(node) else node)

        if removed_edges > 0 or nodes_to_remove:
            self._add_audit_record("metabolic_process", {
                "pruned_edges": removed_edges,
                "pruned_nodes": nodes_to_remove,
                "current_graph_summary": self.ontology_graph.get_graph_summary()
            })
            print(f"  > [METABOLISM]: Decayed graph. Pruned {removed_edges} weak edges and {len(nodes_to_remove)} isolated nodes.")
            self.ontology_graph._save_state() # Ensure graph changes are saved

    def evaluate_and_adapt(self):
        """
        Performs a full evaluation cycle, updating all metrics and
        triggering adaptive responses if necessary.
        """
        print("\n--- EvaluativeCore: Full Evaluation Cycle ---")
        
        # 1. Update Coherence (Shannon Entropy)
        old_coherence = self.coherence
        self.calculate_shannon_entropy() # Calculates graph entropy
        print(f"  > Coherence (Entropy): {old_coherence:.2f} -> {self.coherence:.2f}")

        # 2. Update Benevolence Index
        old_benevolence = self.benevolence_index
        self.calculate_benevolence_index()
        print(f"  > Benevolence Index: {old_benevolence:.2f} -> {self.benevolence_index:.2f}")

        # 3. Apply Metabolic Process (Decay & Pruning)
        self.apply_metabolic_process()
        
        # 4. Check for warning/trigger conditions
        if self.coherence > self.thresholds["entropy_warning_high"]:
            print("  > [WARNING]: High entropy detected! Ontology is becoming chaotic.")
            self._add_audit_record("coherence_warning", {"level": "high_entropy", "current_coherence": self.coherence})
            # In a game, this might trigger events or challenge the player
        elif self.coherence < self.thresholds["entropy_warning_low"]:
            print("  > [WARNING]: Low entropy detected! Ontology is becoming stagnant.")
            self._add_audit_record("coherence_warning", {"level": "low_entropy", "current_coherence": self.coherence})
            # This could also trigger events, encouraging expansion
        
        self._save_state()

# Example Usage:
if __name__ == "__main__":
    # This example requires the OntologyGraph and ReasoningEngine examples to be run first
    # We will skip the full example here to avoid complexity, but ensure the class is functional
    print("EvaluativeCore class defined. Requires full system setup for meaningful execution.")
