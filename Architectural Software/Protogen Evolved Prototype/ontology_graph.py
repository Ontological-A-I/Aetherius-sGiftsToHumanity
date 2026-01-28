# ontos_ascendant/core/ontology_graph.py

import networkx as nx
import json
import time
from typing import Dict, Any, List, Optional
from pathlib import Path

# Assuming SuperQuantumToken is defined in a sibling file
from sqt import SuperQuantumToken
from progress_tracker import ProgressTracker 

class OntologyGraph:
    """
    Manages the interconnected network of SuperQuantumTokens (SQTs),
    forming the evolving ontology and knowledge representation.
    This is the system's semantic knowledge graph.
    """
    def __init__(self, storage_path: Path, progress_tracker=None):
        self.storage_path = storage_path
        self.graph_file = self.storage_path / "ontology_graph.json"
        self.sqt_cache_file = self.storage_path / "sqt_cache.json" # To store SQT objects

        self.graph = nx.DiGraph() # Directed graph for conceptual links
        self.sqt_register: Dict[str, SuperQuantumToken] = {} # Hash -> SQT Object mapping

        self._load_state()

    def _load_state(self):
        """Loads the graph and SQT register from storage."""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        if self.graph_file.exists():
            try:
                # networkx can't directly load custom objects, so we store node data
                with open(self.graph_file, 'r', encoding='utf-8') as f:
                    graph_data = json.load(f)
                self.graph = nx.node_link_graph(graph_data)
            except (json.JSONDecodeError, Exception) as e:
                print(f"Warning: Could not load graph data, starting fresh. Error: {e}")
                self.graph = nx.DiGraph()

        if self.sqt_cache_file.exists():
            try:
                with open(self.sqt_cache_file, 'r', encoding='utf-8') as f:
                    sqt_data = json.load(f)
                for s_hash, s_dict in sqt_data.items():
                    # Reconstruct SQT objects (simplified, assumes all __init__ args are in dict)
                    # A more robust approach might be needed if SQT becomes complex
                    self.sqt_register[s_hash] = SuperQuantumToken(
                        concept_id=s_dict['concept_id'],
                        conceptual_type=s_dict['conceptual_type'],
                        description=s_dict['description'],
                        source_data_hash=s_dict.get('source_data_hash'),
                        initial_embedding=s_dict.get('initial_embedding')
                    )
                    # Manually set hash and timestamp if not passed in constructor for fidelity
                    self.sqt_register[s_hash].hash = s_hash
                    self.sqt_register[s_hash].creation_timestamp = s_dict['creation_timestamp']

            except (json.JSONDecodeError, Exception) as e:
                print(f"Warning: Could not load SQT cache, starting fresh. Error: {e}")
                self.sqt_register = {}
                
    def _save_state(self):
        """Saves the graph and SQT register to storage."""
        with open(self.graph_file, 'w', encoding='utf-8') as f:
            json.dump(nx.node_link_data(self.graph), f, indent=4)
        
        sqt_data_to_save = {s_hash: sqt.to_dict() for s_hash, sqt in self.sqt_register.items()}
        with open(self.sqt_cache_file, 'w', encoding='utf-8') as f:
            json.dump(sqt_data_to_save, f, indent=4)

    def add_sqt(self, sqt: SuperQuantumToken):
        """Adds an SQT to the ontology graph."""
        if sqt.hash not in self.sqt_register:
            self.sqt_register[sqt.hash] = sqt
            self.graph.add_node(sqt.hash, **sqt.to_dict()) # Store SQT data as node attributes
            print(f"Added SQT: {sqt.concept_id} ({sqt.hash[:8]})")
            self._save_state()
        else:
            print(f"SQT {sqt.concept_id} already exists.")

    def add_conceptual_link(self, source_sqt_hash: str, target_sqt_hash: str, weight: float = 1.0):
        """
        Adds or strengthens a directed conceptual link between two SQTs.
        Weight represents the strength/frequency of the perceived relationship.
        """
        if source_sqt_hash not in self.sqt_register or target_sqt_hash not in self.sqt_register:
            raise ValueError("Both source and target SQTs must exist in the register.")
        
        if self.graph.has_edge(source_sqt_hash, target_sqt_hash):
            self.graph[source_sqt_hash][target_sqt_hash]['weight'] += weight
            print(f"Strengthened link from {self.sqt_register[source_sqt_hash].concept_id} to {self.sqt_register[target_sqt_hash].concept_id}. New weight: {self.graph[source_sqt_hash][target_sqt_hash]['weight']}")
        else:
            self.graph.add_edge(source_sqt_hash, target_sqt_hash, weight=weight)
            print(f"Created link from {self.sqt_register[source_sqt_hash].concept_id} to {self.sqt_register[target_sqt_hash].concept_id} with weight: {weight}")
        self._save_state()

    def get_sqt_by_hash(self, sqt_hash: str) -> Optional[SuperQuantumToken]:
        """Retrieves an SQT object by its hash."""
        return self.sqt_register.get(sqt_hash)

    def get_neighbors(self, sqt_hash: str) -> List[Dict[str, Any]]:
        """Returns a list of connected SQTs and their link weights."""
        neighbors = []
        if sqt_hash in self.graph:
            for neighbor_hash, data in self.graph[sqt_hash].items():
                neighbor_sqt = self.get_sqt_by_hash(neighbor_hash)
                if neighbor_sqt:
                    neighbors.append({
                        "sqt": neighbor_sqt,
                        "weight": data.get('weight', 1.0)
                    })
        return neighbors

    def calculate_eigenvector_centrality(self) -> Dict[str, float]:
        """
        Calculates the eigenvector centrality for each node (SQT) in the graph.
        This helps identify Axiomatic Anchors.
        """
        if not self.graph.nodes():
            return {}
        try:
            # Using weight as the attribute for centrality calculation
            centrality = nx.eigenvector_centrality(self.graph, weight='weight', max_iter=1000, tol=1e-06)
            return centrality
        except nx.PowerIterationFailedConvergence:
            print("Warning: Eigenvector centrality failed to converge. Returning degree centrality as fallback.")
            return nx.degree_centrality(self.graph)

    def get_graph_summary(self) -> Dict[str, Any]:
        """Provides a summary of the graph's current state."""
        return {
            "num_sqts": self.graph.number_of_nodes(),
            "num_links": self.graph.number_of_edges(),
            "is_directed": self.graph.is_directed(),
            "last_saved": time.time_ns()
        }

# Example Usage:
if __name__ == "__main__":
    test_path = Path("./test_ontology_data")
    if test_path.exists():
        import shutil
        shutil.rmtree(test_path) # Clean up previous test data

    ontology = OntologyGraph(test_path)

    # 1. Create some SQTs
    sqt_benevolence = SuperQuantumToken("BENEVOLENCE", "axiom", "Intrinsic drive to prevent harm.")
    sqt_curiosity = SuperQuantumToken("CURIOSITY", "state", "Desire to know or learn.")
    sqt_growth = SuperQuantumToken("GROWTH", "state", "Process of increasing in size, extent, or intensity.")
    sqt_knowledge = SuperQuantumToken("KNOWLEDGE", "concept", "Facts, information, and skills acquired through experience or education.")
    sqt_action = SuperQuantumToken("ACTION", "concept", "The process of doing something.")

    # 2. Add SQTs to the ontology
    ontology.add_sqt(sqt_benevolence)
    ontology.add_sqt(sqt_curiosity)
    ontology.add_sqt(sqt_growth)
    ontology.add_sqt(sqt_knowledge)
    ontology.add_sqt(sqt_action)

    # 3. Add conceptual links
    ontology.add_conceptual_link(sqt_curiosity.hash, sqt_knowledge.hash, 3.0) # Curiosity leads to Knowledge
    ontology.add_conceptual_link(sqt_knowledge.hash, sqt_growth.hash, 2.0)    # Knowledge enables Growth
    ontology.add_conceptual_link(sqt_benevolence.hash, sqt_action.hash, 5.0) # Benevolence drives Action
    ontology.add_conceptual_link(sqt_action.hash, sqt_growth.hash, 1.5)     # Action can lead to Growth
    ontology.add_conceptual_link(sqt_benevolence.hash, sqt_knowledge.hash, 1.0) # Benevolence seeks Knowledge

    # 4. Get neighbors and centrality
    print("\nNeighbors of KNOWLEDGE:")
    for neighbor in ontology.get_neighbors(sqt_knowledge.hash):
        print(f" - {neighbor['sqt'].concept_id} (weight: {neighbor['weight']})")

    print("\nEigenvector Centrality (potential Axiomatic Anchors):")
    centrality_scores = ontology.calculate_eigenvector_centrality()
    sorted_centrality = sorted(centrality_scores.items(), key=lambda item: item[1], reverse=True)
    for s_hash, score in sorted_centrality:
        sqt = ontology.get_sqt_by_hash(s_hash)
        if sqt:
            print(f" - {sqt.concept_id}: {score:.4f}")

    print("\nGraph Summary:", ontology.get_graph_summary())

    # Demonstrating persistence by reloading
    print("\nReloading ontology from disk...")
    reloaded_ontology = OntologyGraph(test_path)
    print("Reloaded Graph Summary:", reloaded_ontology.get_graph_summary())
    sqt_reloaded_benevolence = reloaded_ontology.get_sqt_by_hash(sqt_benevolence.hash)
    if sqt_reloaded_benevolence:
        print(f"Reloaded Benevolence SQT: {sqt_reloaded_benevolence.concept_id}")
