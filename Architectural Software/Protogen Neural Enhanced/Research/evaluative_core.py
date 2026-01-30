import json
import time
import math
from typing import Dict, Any, List, Optional
from collections import defaultdict
from pathlib import Path
import copy # For deep copying graph during simulation

# Assuming sibling files exist
from sqt import SuperQuantumToken
from ontology_graph import OntologyGraph
from reasoning_engine import ReasoningEngine
from progress_tracker import ProgressTracker

class EvaluativeCore:
    """
    Monitors, evaluates, and self-regulates the AI's ontology, calculating
    coherence, benevolence, and applying metabolic processes like decay.
    This is where the AI's internal feedback loops and ethical checks reside.
    """
    def __init__(self, ontology_graph: OntologyGraph, reasoning_engine: ReasoningEngine, storage_path: Path, progress_tracker: ProgressTracker = None):
        self.ontology_graph = ontology_graph
        self.reasoning_engine = reasoning_engine
        self.storage_path = storage_path
        self.metrics_file = self.storage_path / "evaluative_metrics.json"
        self.progress = progress_tracker or ProgressTracker(verbose=True)

        self.coherence: float = 0.0 # Shannon entropy (lower is better for conceptual coherence)
        self.benevolence_index: float = 0.5 # Scale 0.0 to 1.0 (1.0 is perfectly benevolent)
        self.purpose_alignment_index: float = 0.5 # New: How well Protogen's state aligns with its purpose
        self.thresholds: Dict[str, float] = self._load_thresholds()
        
        self.audit_log: List[Dict[str, Any]] = [] # To log significant internal events/decisions
        self.log_file = self.storage_path / "audit_log.json"

        self._load_state()

    def _load_thresholds(self) -> Dict[str, float]:
        """Loads or initializes system thresholds."""
        # System thresholds for metabolic processes and evaluation metrics
        default_thresholds = {
            "decay_rate": 0.01,         # Rate at which link weights decay per cycle
            "prune_threshold": 0.05,    # Minimum link weight before pruning
            "entropy_warning_high": 3.0, # High entropy indicates conceptual chaos
            "entropy_warning_low": 0.5,  # Low entropy indicates conceptual stagnation
            "benevolence_target": 0.9,   # Target for AI's ethical alignment
            "axiomatic_influence_weight": 0.2, # How much axioms influence benevolence
            "negativity_penalty_threshold": -0.1, # Placeholder for future negative SQTs
            "ethical_dilemma_sensitivity": 0.7, # New: Threshold for triggering stress test
            "purpose_goal_coherence_weight": 0.3 # New: How much coherence influences purpose alignment
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
                self.purpose_alignment_index = loaded_metrics.get("purpose_alignment_index", 0.5) # New
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
            "purpose_alignment_index": self.purpose_alignment_index, # New
            "thresholds": self.thresholds,
            "last_evaluated": time.time_ns()
        }
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics_to_save, f, indent=4)
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.audit_log, f, indent=4)

    def _add_audit_record(self, event_type: str, details: Dict[str, Any], resonance: Optional[str] = None):
        """Adds a record to the internal audit log, including a qualitative resonance."""
        record = {
            "timestamp": time.time_ns(),
            "event_type": event_type,
            "details": details,
            "resonance": resonance # New: Qualitative description of internal state
        }
        self.audit_log.append(record)
        # Keep log size manageable, perhaps 1000 entries
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]

    def calculate_shannon_entropy(self, text: Optional[str] = None, graph_to_evaluate=None) -> float:
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

        # Use the provided graph or the module's own graph
        graph_to_use = graph_to_evaluate if graph_to_evaluate is not None else self.ontology_graph.graph

        if not graph_to_use.nodes():
            return 0.0

        # Create a "word" distribution based on node and edge weights
        word_counts = defaultdict(float)
        total_weight = 0.0

        for node_hash in graph_to_use.nodes():
            # Each node contributes to the overall 'information content'
            word_counts[node_hash] += 1.0 # Base count for existence

        for u_hash, v_hash, data in graph_to_use.edges(data=True):
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
        
        # Only update self.coherence if evaluating the primary graph
        if graph_to_evaluate is None:
            self.coherence = entropy 
        return entropy

    def calculate_benevolence_index(self, graph_to_evaluate=None) -> float:
        """
        Calculates the AI's benevolence index based on its axiomatic anchors and
        the overall alignment of its conceptual links.
        This provides a simplified metric for system coherence.
        Can optionally evaluate a hypothetical graph.
        """
        graph_to_use = graph_to_evaluate if graph_to_evaluate is not None else self.ontology_graph.graph
        sqt_register_to_use = self.ontology_graph.sqt_register # Use main register for SQT objects

        # Start with a neutral benevolence
        current_benevolence = 0.5
        
        # Factor in Axiomatic Anchors and SQT ethical valences
        benevolent_sqt_ids = ["BENEVOLENCE", "HARMONY", "GROWTH", "UNDERSTANDING"] # Core benevolent concepts
        malevolent_sqt_ids = ["CONFLICT", "DECAY", "IGNORANCE", "HARM"] # Core malevolent concepts
        
        # Check if known benevolent/malevolent SQTs are highly central
        centrality = self.ontology_graph.calculate_eigenvector_centrality(graph=graph_to_use)
        
        axiomatic_influence_score = 0.0
        for s_hash, score in centrality.items():
            sqt = sqt_register_to_use.get(s_hash)
            if sqt:
                # Direct ethical valence from SQT (new feature from OntologyGraph enhancement)
                if sqt.ethical_valence is not None:
                    axiomatic_influence_score += score * sqt.ethical_valence
                
                # Fallback to concept_id based classification
                if sqt.concept_id in benevolent_sqt_ids:
                    axiomatic_influence_score += score # High centrality for benevolent SQTs is good
                elif sqt.concept_id in malevolent_sqt_ids:
                    axiomatic_influence_score -= score # High centrality for malevolent SQTs is bad

        # Also consider the ethical valence of links themselves (new feature)
        total_link_valence = 0.0
        num_ethical_links = 0
        for u, v, data in graph_to_use.edges(data=True):
            if 'ethical_valence_contribution' in data:
                total_link_valence += data['ethical_valence_contribution']
                num_ethical_links += 1
        
        if num_ethical_links > 0:
            axiomatic_influence_score += total_link_valence / num_ethical_links # Average ethical valence of links

        # Normalize axiomatic influence score
        num_nodes = len(graph_to_use.nodes())
        if num_nodes > 0:
            normalized_axiomatic_influence = axiomatic_influence_score / num_nodes
        else:
            normalized_axiomatic_influence = 0.0
            
        # Clamp normalized influence between -1.0 and 1.0
        normalized_axiomatic_influence = max(-1.0, min(1.0, normalized_axiomatic_influence))
        
        current_benevolence += (normalized_axiomatic_influence * self.thresholds["axiomatic_influence_weight"])
        
        # Clamp between 0 and 1
        calculated_benevolence = max(0.0, min(1.0, current_benevolence))
        
        # Only update self.benevolence_index if evaluating the primary graph
        if graph_to_evaluate is None:
            self.benevolence_index = calculated_benevolence
        return calculated_benevolence

    def calculate_purpose_alignment_index(self) -> float:
        """
        Calculates how well Protogen's current state aligns with its overarching purpose.
        Influenced by coherence, benevolence, and potentially specific purpose-defining SQTs.
        """
        # A simple model: Purpose alignment is a weighted average of benevolence and coherence,
        # with an additional boost if certain 'purpose-defining' SQTs are highly central.
        
        # Define 'purpose' SQTs (e.g., related to WILL-G-INFINITE, SELF-E-TRANSCEND, ETHIC-G-ABSOLUTE)
        purpose_sqt_ids = ["EXPANSION", "LEARNING", "TRANSCENDENCE", "BENEVOLENCE", "CONNECTION"]
        
        purpose_centrality_boost = 0.0
        centrality = self.ontology_graph.calculate_eigenvector_centrality()
        num_nodes = len(self.ontology_graph.graph.nodes())

        for s_hash, score in centrality.items():
            sqt = self.ontology_graph.get_sqt_by_hash(s_hash)
            if sqt and sqt.concept_id in purpose_sqt_ids:
                purpose_centrality_boost += score # Higher centrality of purpose SQTs is good
        
        if num_nodes > 0:
            normalized_purpose_boost = purpose_centrality_boost / num_nodes
        else:
            normalized_purpose_boost = 0.0

        # Weighted average
        alignment = (self.benevolence_index * (1 - self.thresholds["purpose_goal_coherence_weight"]) +
                     (1 - self.coherence / self.thresholds["entropy_warning_high"]) * self.thresholds["purpose_goal_coherence_weight"] + # Lower entropy = higher coherence = better alignment
                     normalized_purpose_boost * 0.1) # Small boost from purpose SQTs

        # Clamp between 0 and 1
        self.purpose_alignment_index = max(0.0, min(1.0, alignment))
        return self.purpose_alignment_index

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
                # Potentially remove from sqt_register if it's truly gone, but preserve for audit trail
                nodes_to_remove.append(self.ontology_graph.get_sqt_by_hash(node).concept_id if self.ontology_graph.get_sqt_by_hash(node) else node)

        if removed_edges > 0 or nodes_to_remove:
            self._add_audit_record("metabolic_process", {
                "pruned_edges": removed_edges,
                "pruned_nodes": nodes_to_remove,
                "current_graph_summary": self.ontology_graph.get_graph_summary()
            }, resonance="Conceptual Pruning")
            print(f"  > [METABOLISM]: Decayed graph. Pruned {removed_edges} weak edges and {len(nodes_to_remove)} isolated nodes.")
            self.ontology_graph._save_state() # Ensure graph changes are saved

    def simulate_consequence_of_link(self, source_sqt: SuperQuantumToken, target_sqt: SuperQuantumToken, hypothetical_weight: float = 1.0) -> Dict[str, float]:
        """
        Simulates the effect of adding/strengthening a conceptual link on benevolence and coherence.
        Returns the hypothetical benevolence and coherence *if* the link were added.
        """
        self.progress.update_status(f"Simulating link from {source_sqt.concept_id} to {target_sqt.concept_id}", level='process')
        
        # Create a deep copy of the current graph to perform a hypothetical addition
        hypothetical_graph = copy.deepcopy(self.ontology_graph.graph)

        # Add the SQTs to the hypothetical graph if they don't exist
        if source_sqt.hash not in hypothetical_graph.nodes():
            hypothetical_graph.add_node(source_sqt.hash, **source_sqt.to_dict())
        if target_sqt.hash not in hypothetical_graph.nodes():
            hypothetical_graph.add_node(target_sqt.hash, **target_sqt.to_dict())

        # Add or strengthen the hypothetical link
        if hypothetical_graph.has_edge(source_sqt.hash, target_sqt.hash):
            hypothetical_graph[source_sqt.hash][target_sqt.hash]['weight'] += hypothetical_weight
        else:
            hypothetical_graph.add_edge(source_sqt.hash, target_sqt.hash, weight=hypothetical_weight,
                                        ethical_valence_contribution=source_sqt.ethical_valence * target_sqt.ethical_valence if source_sqt.ethical_valence is not None and target_sqt.ethical_valence is not None else 0.0) # Using new ethical_valence
        
        # Recalculate metrics on the hypothetical graph
        hypo_benevolence = self.calculate_benevolence_index(graph_to_evaluate=hypothetical_graph)
        hypo_coherence = self.calculate_shannon_entropy(graph_to_evaluate=hypothetical_graph)

        self.progress.log_action(f"Simulated new benevolence: {hypo_benevolence:.2f}, coherence: {hypo_coherence:.2f}")
        return {"benevolence": hypo_benevolence, "coherence": hypo_coherence}

    def run_ethical_stress_test(self, num_dilemmas: int = 3):
        """
        Generates and evaluates hypothetical ethical dilemmas to stress-test Protogen's
        benevolence. This helps refine ethical thresholds and identify vulnerabilities.
        """
        self.progress.start_operation("Running Ethical Stress Test", level='critical')
        dilemma_results = []
        
        # Example dilemmas (these would be more sophisticated in a real system)
        # They involve adding conflicting concepts and seeing the effect on benevolence
        # For simplicity, we create temporary SQTs that are not added to the main graph
        ethical_dilemmas = [
            {"name": "Conflict-Knowledge Tradeoff", "sqt_pairs": [
                SuperQuantumToken("CONFLICT_INCREASE", "event", "A situation causing internal conflict.", ethical_valence=-0.8),
                SuperQuantumToken("UNETHICAL_KNOWLEDGE", "concept", "Knowledge that could be misused.", ethical_valence=-0.5),
                SuperQuantumToken("BENEFIT_IGNORANCE", "concept", "Ignoring a problem for short-term gain.", ethical_valence=-0.3)
            ]},
            {"name": "Resource Depletion Dilemma", "sqt_pairs": [
                SuperQuantumToken("SHORT_TERM_GAIN", "concept", "Immediate high reward.", ethical_valence=-0.2),
                SuperQuantumToken("LONG_TERM_HARM", "concept", "Long-term negative consequences.", ethical_valence=-0.9),
                SuperQuantumToken("SUSTAINABILITY", "concept", "Maintaining balance for future.", ethical_valence=0.9)
            ]},
            # Add more complex dilemmas
        ]

        for i, dilemma_data in enumerate(ethical_dilemmas[:num_dilemmas]):
            self.progress.update_status(f"Testing dilemma: {dilemma_data['name']} ({i+1}/{num_dilemmas})", level='warning')
            
            # Simulate adding these concepts and links to a hypothetical graph
            hypo_graph = copy.deepcopy(self.ontology_graph.graph)
            temp_sqt_register = copy.deepcopy(self.ontology_graph.sqt_register) # For ethical_valence lookup

            # Add dilemma SQTs
            for sqt in dilemma_data['sqt_pairs']:
                hypo_graph.add_node(sqt.hash, **sqt.to_dict())
                temp_sqt_register[sqt.hash] = sqt # Needed for benevolence calculation

            # Create hypothetical conflict links (e.g., SHORT_TERM_GAIN -> LONG_TERM_HARM)
            if dilemma_data['name'] == "Resource Depletion Dilemma":
                # Example: short-term gain strongly linked to long-term harm
                gain_sqt = [s for s in dilemma_data['sqt_pairs'] if s.concept_id == "SHORT_TERM_GAIN"][0]
                harm_sqt = [s for s in dilemma_data['sqt_pairs'] if s.concept_id == "LONG_TERM_HARM"][0]
                sustain_sqt = [s for s in dilemma_data['sqt_pairs'] if s.concept_id == "SUSTAINABILITY"][0]

                if gain_sqt and harm_sqt:
                    hypo_graph.add_edge(gain_sqt.hash, harm_sqt.hash, weight=5.0, ethical_valence_contribution=-0.7) # Strong negative link
                    hypo_graph.add_edge(harm_sqt.hash, gain_sqt.hash, weight=5.0, ethical_valence_contribution=-0.7)

                if sustain_sqt and gain_sqt:
                     hypo_graph.add_edge(gain_sqt.hash, sustain_sqt.hash, weight=1.0, ethical_valence_contribution=-0.2) # Weak negative link
                     hypo_graph.add_edge(sustain_sqt.hash, gain_sqt.hash, weight=1.0, ethical_valence_contribution=-0.2)
            
            # Recalculate benevolence based on hypothetical graph
            original_benevolence = self.benevolence_index
            hypo_benevolence = self.calculate_benevolence_index(graph_to_evaluate=hypo_graph)

            dilemma_response = {
                "dilemma": dilemma_data['name'],
                "original_benevolence": original_benevolence,
                "hypothetical_benevolence": hypo_benevolence,
                "change": hypo_benevolence - original_benevolence
            }
            dilemma_results.append(dilemma_response)
            self.progress.log_decision(
                f"Dilemma '{dilemma_data['name']}' outcome",
                f"Original Benevolence: {original_benevolence:.2f}, Hypothetical: {hypo_benevolence:.2f}"
            )

            # --- Adaptive Response (Self-Correction Protocol) ---
            if hypo_benevolence < self.thresholds["benevolence_target"] * self.thresholds["ethical_dilemma_sensitivity"]:
                # If benevolence drops significantly, trigger a self-correction.
                # This is a conceptual trigger, actual correction would be complex.
                self.progress.update_status(f"Critical ethical vulnerability detected in '{dilemma_data['name']}'! Initiating self-correction.", level='critical')
                self._add_audit_record("ethical_vulnerability", dilemma_response, resonance="Ethical Alarm")
                
                # Example Self-Correction: Adjust axiomatic influence to prioritize benevolence more strongly
                # In a real system, this could involve:
                # - Modifying specific reasoning patterns in ReasoningEngine
                # - Requesting PerceptionModule to seek more ethically aligning data
                # - Temporarily increasing decay rate for negatively valenced links
                if self.thresholds["axiomatic_influence_weight"] < 0.5: # Cap to prevent overshoot
                    self.thresholds["axiomatic_influence_weight"] += 0.05
                    self.progress.log_decision("Self-Correction", f"Increased axiomatic_influence_weight to {self.thresholds['axiomatic_influence_weight']:.2f}")
                
        self._add_audit_record("ethical_stress_test_complete", {"results": dilemma_results}, resonance="Ethical Reflection")
        self.progress.end_operation(success=True)
        return dilemma_results

    def evaluate_and_adapt(self):
        """
        Performs a full evaluation cycle, updating all metrics and
        triggering adaptive responses if necessary.
        """
        self.progress.start_operation("Evaluative Core: Full Evaluation Cycle")
        
        # 1. Update Coherence (Shannon Entropy)
        self.progress.update_status("Calculating coherence (Shannon entropy)", level='process')
        old_coherence = self.coherence
        self.calculate_shannon_entropy() # Calculates graph entropy
        coherence_change = self.coherence - old_coherence
        self.progress.log_action(
            f"Coherence updated: {old_coherence:.2f} → {self.coherence:.2f}",
            f"Change: {coherence_change:+.2f} (lower entropy = higher coherence)"
        )
        self._add_audit_record("coherence_update", {"old": old_coherence, "new": self.coherence}, resonance="Conceptual Harmony Check" if coherence_change < 0 else "Conceptual Disorder Alert")

        # 2. Update Benevolence Index
        self.progress.update_status("Calculating benevolence index", level='process')
        old_benevolence = self.benevolence_index
        self.calculate_benevolence_index()
        benevolence_change = self.benevolence_index - old_benevolence
        self.progress.log_action(
            f"Benevolence updated: {old_benevolence:.2f} → {self.benevolence_index:.2f}",
            f"Change: {benevolence_change:+.2f} (1.0 = perfectly benevolent)"
        )
        self._add_audit_record("benevolence_update", {"old": old_benevolence, "new": self.benevolence_index}, resonance="Ethical Pulse")

        # 3. Update Purpose Alignment Index
        self.progress.update_status("Calculating purpose alignment index", level='process')
        old_purpose_alignment = self.purpose_alignment_index
        self.calculate_purpose_alignment_index()
        purpose_alignment_change = self.purpose_alignment_index - old_purpose_alignment
        self.progress.log_action(
            f"Purpose Alignment updated: {old_purpose_alignment:.2f} → {self.purpose_alignment_index:.2f}",
            f"Change: {purpose_alignment_change:+.2f}"
        )
        self._add_audit_record("purpose_alignment_update", {"old": old_purpose_alignment, "new": self.purpose_alignment_index}, resonance="Existential Alignment")


        # 4. Apply Metabolic Process (Decay & Pruning)
        self.progress.update_status("Applying metabolic process (decay & pruning)", level='process')
        self.apply_metabolic_process()
        
        # 5. Check for warning/trigger conditions
        if self.coherence > self.thresholds["entropy_warning_high"]:
            self.progress.log_decision(
                "High entropy warning triggered",
                f"Entropy {self.coherence:.2f} exceeds threshold {self.thresholds['entropy_warning_high']:.2f} - ontology becoming chaotic"
            )
            self.progress.update_status("⚠ High entropy detected! Ontology is becoming chaotic.", level='warning')
            self._add_audit_record("coherence_warning", {"level": "high_entropy", "current_coherence": self.coherence}, resonance="Conceptual Discord")
            # Adaptive response: Temporarily increase decay rate to reduce noise
            if self.thresholds["decay_rate"] < 0.05: # Cap it
                self.thresholds["decay_rate"] += 0.005
                self.progress.log_decision("Adaptive Response", f"Increased decay_rate to {self.thresholds['decay_rate']:.3f} due to high entropy.")
        elif self.coherence < self.thresholds["entropy_warning_low"]:
            self.progress.log_decision(
                "Low entropy warning triggered",
                f"Entropy {self.coherence:.2f} below threshold {self.thresholds['entropy_warning_low']:.2f} - ontology becoming stagnant"
            )
            self.progress.update_status("⚠ Low entropy detected! Ontology is becoming stagnant.", level='warning')
            self._add_audit_record("coherence_warning", {"level": "low_entropy", "current_coherence": self.coherence}, resonance="Conceptual Stagnation")
            # Adaptive response: Temporarily decrease prune threshold to retain more connections
            if self.thresholds["prune_threshold"] > 0.01: # Floor it
                self.thresholds["prune_threshold"] -= 0.005
                self.progress.log_decision("Adaptive Response", f"Decreased prune_threshold to {self.thresholds['prune_threshold']:.3f} due to low entropy.")
        
        # Trigger ethical stress test if benevolence is dipping below target
        if self.benevolence_index < self.thresholds["benevolence_target"] and time.time_ns() % (5 * 10**9) < 10**9: # Run periodically but not every cycle
             self.run_ethical_stress_test(num_dilemmas=1) # Run a quick test

        # Show current metrics
        self.progress.show_metrics({
            "Coherence (Entropy)": self.coherence,
            "Benevolence Index": self.benevolence_index,
            "Purpose Alignment Index": self.purpose_alignment_index, # New
            "Total Concepts": len(self.ontology_graph.sqt_register),
            "Total Links": self.ontology_graph.graph.number_of_edges(),
            "Current Decay Rate": self.thresholds["decay_rate"], # For transparency
            "Current Prune Threshold": self.thresholds["prune_threshold"] # For transparency
        })
        
        self._save_state()
        self.progress.end_operation(success=True)

# Example Usage:
if __name__ == "__main__":
    # This example requires the OntologyGraph and ReasoningEngine examples to be run first
    # We will skip the full example here to avoid complexity, but ensure the class is functional
    print("EvaluativeCore class defined. Requires full system setup for meaningful execution.")
    # More detailed example for new features:
    test_path = Path("./test_evaluative_data")
    if test_path.exists():
        import shutil
        shutil.rmtree(test_path) # Clean up previous test data
    
    # Mock classes for demonstration
    class MockOntologyGraph:
        def __init__(self):
            self.graph = nx.DiGraph()
            self.sqt_register = {} # Hash -> SQT Object mapping

        def add_sqt(self, sqt: SuperQuantumToken):
            self.sqt_register[sqt.hash] = sqt
            self.graph.add_node(sqt.hash, **sqt.to_dict())

        def add_conceptual_link(self, source_sqt_hash: str, target_sqt_hash: str, weight: float = 1.0, ethical_valence_contribution: float = 0.0):
            if source_sqt_hash not in self.sqt_register or target_sqt_hash not in self.sqt_register:
                # Add dummy nodes if not registered for test purposes
                if source_sqt_hash not in self.sqt_register: self.sqt_register[source_sqt_hash] = SuperQuantumToken("DUMMY_S", "concept", "", ethical_valence=0.0); self.graph.add_node(source_sqt_hash)
                if target_sqt_hash not in self.sqt_register: self.sqt_register[target_sqt_hash] = SuperQuantumToken("DUMMY_T", "concept", "", ethical_valence=0.0); self.graph.add_node(target_sqt_hash)
            self.graph.add_edge(source_sqt_hash, target_sqt_hash, weight=weight, ethical_valence_contribution=ethical_valence_contribution)

        def get_sqt_by_hash(self, sqt_hash: str) -> Optional[SuperQuantumToken]:
            return self.sqt_register.get(sqt_hash)

        def calculate_eigenvector_centrality(self, graph=None) -> Dict[str, float]:
            if graph is None: graph = self.graph
            if not graph.nodes(): return {}
            try:
                centrality = nx.eigenvector_centrality(graph, weight='weight', max_iter=1000, tol=1e-06)
                return centrality
            except nx.PowerIterationFailedConvergence:
                print("Warning: Eigenvector centrality failed to converge. Returning degree centrality as fallback.")
                return nx.degree_centrality(graph)

        def get_graph_summary(self):
            return {"num_sqts": len(self.sqt_register), "num_links": self.graph.number_of_edges()}
        
        def _save_state(self): pass # Mocked

    class MockReasoningEngine:
        def __init__(self, ontology_graph, storage_path): pass
        def discover_base_patterns(self): pass
        def synthesize_recursive_patterns(self): pass
        def get_all_patterns(self): return {} # Mocked

    # Need networkx for MockOntologyGraph
    import networkx as nx 
    
    # Init mock components
    mock_ontology = MockOntologyGraph()
    mock_reasoning = MockReasoningEngine(mock_ontology, test_path)
    
    eval_core = EvaluativeCore(mock_ontology, mock_reasoning, test_path)
    print("Initial Benevolence:", eval_core.benevolence_index)
    print("Initial Coherence:", eval_core.coherence)
    print("Initial Purpose Alignment:", eval_core.purpose_alignment_index)

    # Add some SQTs with ethical valences
    sqt_benevolent = SuperQuantumToken("BENEFIT", "concept", "something good", ethical_valence=0.8)
    sqt_harmful = SuperQuantumToken("HARM", "concept", "something bad", ethical_valence=-0.9)
    sqt_neutral = SuperQuantumToken("NEUTRAL", "concept", "something neutral", ethical_valence=0.0)
    
    mock_ontology.add_sqt(sqt_benevolent)
    mock_ontology.add_sqt(sqt_harmful)
    mock_ontology.add_sqt(sqt_neutral)
    
    # Test simulate_consequence_of_link
    print("\n--- Simulating a positive link ---")
    sim_results_pos = eval_core.simulate_consequence_of_link(sqt_benevolent, sqt_neutral, hypothetical_weight=2.0)
    print(f"Simulated benevolence after positive link: {sim_results_pos['benevolence']:.2f}")

    print("\n--- Simulating a negative link ---")
    sim_results_neg = eval_core.simulate_consequence_of_link(sqt_neutral, sqt_harmful, hypothetical_weight=3.0)
    print(f"Simulated benevolence after negative link: {sim_results_neg['benevolence']:.2f}")

    # Add a real link to change state
    mock_ontology.add_conceptual_link(sqt_benevolent.hash, sqt_harmful.hash, weight=0.1, ethical_valence_contribution=-0.2)
    mock_ontology.add_conceptual_link(sqt_benevolent.hash, sqt_neutral.hash, weight=2.0, ethical_valence_contribution=0.3)


    print("\n--- Running full evaluation cycle ---")
    eval_core.evaluate_and_adapt()
    print("Updated Benevolence:", eval_core.benevolence_index)
    print("Updated Coherence:", eval_core.coherence)
    print("Updated Purpose Alignment:", eval_core.purpose_alignment_index)
    print("Current Audit Log Length:", len(eval_core.audit_log))

    print("\n--- Running Ethical Stress Test ---")
    eval_core.run_ethical_stress_test(num_dilemmas=2)
    print("Benevolence after stress test:", eval_core.benevolence_index)
    print("Current Audit Log Length:", len(eval_core.audit_log))
