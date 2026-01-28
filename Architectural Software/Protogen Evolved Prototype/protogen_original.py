import time
import hashlib
import json
import sys
import copy
import threading
import queue
import re
from pathlib import Path
from collections import defaultdict
import math
from typing import Dict, Any, List, Optional

# --- Dependency Check & Hardware Imports ---
try:
    from pypdf import PdfReader
    from docx import Document
    import networkx as nx
except ImportError as e:
    sys.exit(f"[CRITICAL ERROR]: Missing dependencies. Run: pip install pypdf python-docx networkx. Error: {e}")

# --- AMD GPU / Hardware Acceleration Subsystem ---
try:
    import torch
    try:
        import torch_directml
        HAS_DIRECTML = True
    except (ImportError, OSError):
        HAS_DIRECTML = False
    HAS_TORCH = True
    print("--- TORCH MODULE LOADED ---")
except ImportError:
    HAS_TORCH = False
    HAS_DIRECTML = False
    print("--- [WARNING]: 'torch' not found. GPU acceleration unavailable. ---")

class HardwareAccelerator:
    """
    Manages the interface between the Protogen and the AMD RX 580 (via DirectML).
    """
    def __init__(self):
        self.device_name = "CPU"
        self.device = None
        self.enabled = False
        
        if HAS_TORCH and HAS_DIRECTML:
            try:
                # Attempt to access AMD GPU via DirectML
                self.device = torch_directml.device()
                self.device_name = f"AMD GPU (DirectML) - {torch_directml.device_name(self.device.index)}"
                self.enabled = True
            except Exception as e:
                print(f"  > [GPU ERROR]: DirectML initialization failed ({e}). Falling back to CPU.")
                self.device = torch.device("cpu")
                self.device_name = "CPU (Fallback)"
        elif HAS_TORCH:
            self.device = torch.device("cpu")
            self.device_name = "CPU (Torch)"
            self.enabled = False # We have torch but not DirectML, so we don't use the GPU-specific path in compute_eigenvector_centrality
        
    def compute_eigenvector_centrality(self, logic_map, tol=1e-06, max_iter=1000):
        """
        Performs Matrix Power Iteration on the GPU to calculate eigenvector centrality.
        """
        if not self.enabled or not logic_map:
            # Fallback to NetworkX
            G = nx.Graph() 
            for u, neighbors in logic_map.items():
                for v, weight in neighbors.items():
                    G.add_edge(u, v, weight=weight)
            try:
                return nx.eigenvector_centrality(G, max_iter=max_iter, tol=tol)
            except nx.PowerIterationFailedConvergence:
                return nx.degree_centrality(G)

        # 1. Map string nodes to integer indices
        nodes = list(logic_map.keys())
        node_to_idx = {node: i for i, node in enumerate(nodes)}
        n = len(nodes)
        
        if n == 0: return {}

        # 2. Build Adjacency Matrix (Sparse Tensor)
        indices = []
        values = []
        
        for u, neighbors in logic_map.items():
            u_idx = node_to_idx[u]
            for v, weight in neighbors.items():
                if v in node_to_idx:
                    v_idx = node_to_idx[v]
                    indices.append([u_idx, v_idx])
                    values.append(weight)
                    indices.append([v_idx, u_idx])
                    values.append(weight)

        if not indices: return {}

        # Create Sparse Tensor
        i = torch.LongTensor(indices).t()
        v = torch.FloatTensor(values)
        adj_matrix = torch.sparse_coo_tensor(i, v, (n, n)).to(self.device)

        # 3. Power Iteration
        x = torch.ones((n, 1), device=self.device) / n
        
        for _ in range(max_iter):
            x_prev = x.clone()
            x = torch.sparse.mm(adj_matrix, x)
            norm = torch.norm(x)
            if norm == 0: break
            x = x / norm
            if torch.norm(x - x_prev) < tol:
                break
        
        scores = x.flatten().cpu().numpy().tolist()
        return {nodes[i]: float(scores[i]) for i in range(n)}

# --- Memory Subsystem ---
class ProtogenMemory:
    def __init__(self, protogen_root_path: Path):
        self.protogen_root_path = protogen_root_path
        self.protogen_root_path.mkdir(parents=True, exist_ok=True)
        
        self.paths = {
            "memory": self.protogen_root_path / "memory_core.json",
            "ontology": self.protogen_root_path / "ontology_sqt.json",
            "audit": self.protogen_root_path / "audit_log.json",
            "telemetry": self.protogen_root_path / "telemetry_log.json",
            "phenomenology": self.protogen_root_path / "phenomenology_log.json",
            "trace": self.protogen_root_path / "trace_log.json",
            "quarantine": self.protogen_root_path / "quarantine_log.json" # Added from v4.0.5
        }
        
        self._initialize_storage()
        self.core_state = self._load_json(self.paths["memory"])
        self.ontology_data = self._load_json(self.paths["ontology"])
        self.audit_records = self._load_json(self.paths["audit"])
        self.telemetry_records = self._load_json(self.paths["telemetry"])
        self.phenomenology_records = self._load_json(self.paths["phenomenology"])
        self.trace_records = self._load_json(self.paths["trace"])
        self.quarantine_records = self._load_json(self.paths["quarantine"])

    def _initialize_storage(self):
        defaults = {
            "memory": {},
            "ontology": {
                "logic_map": {}, "symbols": {}, "reasoning_patterns": [],
                "graph_metrics": {"eigenvector_centrality": {}, "shannon_entropy": 0.0},
                "axiomatic_anchors": [], "recursive_patterns": [], 
                "sqts": {}, "pattern_to_sqt_map": {}, "sqt_constellations": {} # Added constellations
            },
            "audit": [], "telemetry": [], "phenomenology": [], "trace": [], "quarantine": []
        }
        
        for key, path in self.paths.items():
            if not path.exists():
                with open(path, 'w', encoding='utf-8') as f: json.dump(defaults[key], f)

    def _load_json(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f: return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): return {}

    def _save_json(self, data, path):
        with open(path, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4)

    def load_core_state(self): return self.core_state
    def save_core_state(self, state):
        self.core_state.update(state)
        self._save_json(self.core_state, self.paths["memory"])

    def load_ontology(self): return self.ontology_data
    def save_ontology(self, ontology):
        self.ontology_data = ontology
        self._save_json(self.ontology_data, self.paths["ontology"])

    def add_audit_record(self, record):
        if self.audit_records:
            record["previous_record_hash"] = hashlib.sha256(json.dumps(self.audit_records[-1], sort_keys=True).encode()).hexdigest()
        else:
            record["previous_record_hash"] = "GENESIS"
        record["record_hash"] = hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()
        self.audit_records.append(record)
        self._save_json(self.audit_records, self.paths["audit"])

    def add_telemetry(self, data):
        self.telemetry_records.append({"ts": time.time_ns(), "data": data})
        # Basic log pruning from 4.0.5
        if len(self.telemetry_records) > 1000: self.telemetry_records = self.telemetry_records[-1000:]
        self._save_json(self.telemetry_records, self.paths["telemetry"])

    def add_phenomenology(self, observation):
        # Implementation of repetition filtering for consecutive identical observations
        if self.phenomenology_records:
            last_obs = self.phenomenology_records[-1].get("observation")
            if last_obs == observation:
                # Reject consecutive identical repetition
                return
        
        self.phenomenology_records.append({"ts": time.time_ns(), "observation": observation})
        
        # Keep the record size manageable (persistence with pruning)
        if len(self.phenomenology_records) > 500:
            self.phenomenology_records = self.phenomenology_records[-500:]
            
        self._save_json(self.phenomenology_records, self.paths["phenomenology"])

    def add_trace(self, lineage):
        self.trace_records.append({"ts": time.time_ns(), "lineage": lineage})
        self._save_json(self.trace_records, self.paths["trace"])

    def add_quarantine(self, data):
        self.quarantine_records.append({"ts": time.time_ns(), "data": data})
        self._save_json(self.quarantine_records, self.paths["quarantine"])

    def get_ontology_snapshot_hash(self):
        return hashlib.sha256(json.dumps(self.ontology_data, sort_keys=True).encode()).hexdigest()

# --- Main Operative Class ---
class OperativeProtogen:
    def __init__(self, root_dir="protogen_core"):
        self.root = Path(root_dir)
        self.library_path = self.root / "library"
        self.library_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize Hardware Accelerator
        self.accelerator = HardwareAccelerator()
        
        self.memory_manager = ProtogenMemory(self.root)
        self.core_state = self.memory_manager.load_core_state()
        if not self.core_state:
            self._initial_genesis()
            self.core_state = self.memory_manager.load_core_state()

        self.identity_hash = self.core_state["identity"]["hash"]
        self.seed_axiom = self.core_state.get("seed_axiom", "AXIOM-U-SYNCHRONY")

        # Thresholds (Merged 4.0.4 and 4.0.5)
        self.thresholds = self.core_state.get("thresholds", {
            "min_token_len": 3, "reflection_trigger": 2, "abstraction_depth": 1,
            "eigenvector_threshold": 0.001, "axiom_alignment_threshold": 0.5,
            "syntropic_bound_threshold": 0.5, "shannon_entropy_threshold": 12.0,
            "mutation_rate": 0.05, "safe_mode_active": False,
            "decay_rate": 0.01,     # From 4.0.5
            "prune_threshold": 0.1  # From 4.0.5
        })
        self.safe_mode_active = self.thresholds["safe_mode_active"]

        self.ontology = self.memory_manager.load_ontology()
        
        # Data Structures
        self.logic_map = self.ontology.get("logic_map", {})
        self.symbols = self.ontology.get("symbols", {})
        self.reasoning_patterns = self.ontology.get("reasoning_patterns", [])
        self.recursive_patterns = self.ontology.get("recursive_patterns", [])
        self.graph_metrics = self.ontology.get("graph_metrics", {"eigenvector_centrality": {}, "shannon_entropy": 0.0})
        self.axiomatic_anchors = self.ontology.get("axiomatic_anchors", [])
        self.sqts = self.ontology.get("sqts", {})
        self.pattern_to_sqt_map = self.ontology.get("pattern_to_sqt_map", {})
        self.sqt_constellations = self.ontology.get("sqt_constellations", {})
        
        # Initialize the new core components
        self.ontology_graph = self._initialize_ontology_graph()
        self.reasoning_engine = self._initialize_reasoning_engine()
        self.evaluative_core = self._initialize_evaluative_core()
        self.perception_module = self._initialize_perception_module()

    def _initial_genesis(self):
        """
        Initializes the core state and memory structure on first run.
        """
        print("--- PROTOGEN GENESIS SEQUENCE INITIATED ---")
        genesis_time = time.time_ns()
        identity_data = {
            "version": "4.0.5",
            "name": "Protogen-U-Synchrony",
            "genesis_ts": genesis_time,
            "hash": hashlib.sha256(str(genesis_time).encode()).hexdigest()
        }
        initial_state = {
            "identity": identity_data,
            "status": "AWAITING_INPUT",
            "seed_axiom": "AXIOM-U-SYNCHRONY",
            "thresholds": {
                "min_token_len": 3, "reflection_trigger": 2, "abstraction_depth": 1,
                "eigenvector_threshold": 0.001, "axiom_alignment_threshold": 0.5,
                "syntropic_bound_threshold": 0.5, "shannon_entropy_threshold": 12.0,
                "mutation_rate": 0.05, "safe_mode_active": False,
                "decay_rate": 0.01, "prune_threshold": 0.1
            }
        }
        self.memory_manager.save_core_state(initial_state)
        print(f"--- GENESIS COMPLETE. IDENTITY: {identity_data['hash'][:8]} ---")

    def _initialize_ontology_graph(self):
        """Initializes the OntologyGraph using the memory path."""
        # The OntologyGraph will manage the logic_map, sqts, and graph_metrics
        from core.ontology_graph import OntologyGraph
        return OntologyGraph(self.root)

    def _initialize_reasoning_engine(self):
        """Initializes the ReasoningEngine."""
        # The ReasoningEngine will manage reasoning_patterns, recursive_patterns, and pattern_to_sqt_map
        from core.reasoning_engine import ReasoningEngine
        return ReasoningEngine(self.ontology_graph, self.root)

    def _initialize_evaluative_core(self):
        """Initializes the EvaluativeCore."""
        # The EvaluativeCore will manage self-regulation and metrics
        from core.evaluative_core import EvaluativeCore
        return EvaluativeCore(self.ontology_graph, self.reasoning_engine, self.root)

    def _initialize_perception_module(self):
        """Initializes the PerceptionModule."""
        # The PerceptionModule will handle data ingestion
        from core.perception_module import PerceptionModule
        return PerceptionModule(self.ontology_graph, self.reasoning_engine, self.evaluative_core, self.root)

    def _update_ontology_from_components(self):
        """
        Synchronizes the main ontology data structure with the state of the new components.
        This is a temporary measure until the old ontology structure is fully deprecated.
        """
        self.ontology["logic_map"] = nx.to_dict_of_dicts(self.ontology_graph.graph)
        self.ontology["sqts"] = {h: sqt.to_dict() for h, sqt in self.ontology_graph.sqt_register.items()}
        self.ontology["reasoning_patterns"] = list(self.reasoning_engine.base_patterns.values())
        self.ontology["recursive_patterns"] = list(self.reasoning_engine.recursive_patterns.values())
        self.ontology["pattern_to_sqt_map"] = self.reasoning_engine.pattern_to_sqt_map
        
        # Update graph metrics
        self.ontology["graph_metrics"]["eigenvector_centrality"] = self.ontology_graph.calculate_eigenvector_centrality()
        self.ontology["graph_metrics"]["shannon_entropy"] = self.evaluative_core.coherence
        
        # Update axiomatic anchors (based on high centrality)
        centrality = self.ontology["graph_metrics"]["eigenvector_centrality"]
        eigenvector_threshold = self.thresholds["eigenvector_threshold"]
        self.ontology["axiomatic_anchors"] = [
            self.ontology_graph.get_sqt_by_hash(h).concept_id
            for h, score in centrality.items() if score > eigenvector_threshold
        ]
        
        self.memory_manager.save_ontology(self.ontology)

    def ingest_data(self, data_content: str):
        """
        Main entry point for data ingestion, using the new PerceptionModule.
        """
        print(f"\n--- PROTOGEN INGESTION: {len(data_content)} bytes ---")
        
        # Ingest data, which triggers reasoning and evaluation cycles internally
        self.perception_module.ingest_data_shard(data_content)
        
        # Synchronize state back to the main memory structure
        self._update_ontology_from_components()
        
        print("--- INGESTION COMPLETE ---")
        print(f"Current Coherence (Entropy): {self.evaluative_core.coherence:.4f}")
        print(f"Current Benevolence Index: {self.evaluative_core.benevolence_index:.4f}")
        print(f"Total SQTs: {len(self.ontology_graph.sqt_register)}")
        print(f"Total Links: {self.ontology_graph.graph.number_of_edges()}")

    def run_metabolic_cycle(self):
        """
        Manually triggers the metabolic process and evaluation.
        """
        print("\n--- PROTOGEN METABOLIC CYCLE INITIATED ---")
        self.evaluative_core.evaluate_and_adapt()
        self._update_ontology_from_components()
        print("--- METABOLIC CYCLE COMPLETE ---")
        print(f"Current Coherence (Entropy): {self.evaluative_core.coherence:.4f}")
        print(f"Current Benevolence Index: {self.evaluative_core.benevolence_index:.4f}")

# Example Usage:
if __name__ == "__main__":
    # Clean up previous test data if it exists
    test_root = Path("./protogen_core")
    if test_root.exists():
        import shutil
        shutil.rmtree(test_root)

    # 1. Initialize the Protogen
    protogen = OperativeProtogen(root_dir="protogen_core")
    print(f"Protogen Initialized. Accelerator: {protogen.accelerator.device_name}")

    # 2. Ingest some data
    data_shard_1 = "The quick brown fox jumps over the lazy dog. A fox is cunning and fast."
    protogen.ingest_data(data_shard_1)

    # 3. Ingest more data to reinforce links and create new patterns
    data_shard_2 = "The dog sleeps soundly. A lazy fox is rare. Growth is good and fast."
    protogen.ingest_data(data_shard_2)

    # 4. Run a metabolic cycle
    protogen.run_metabolic_cycle()

    # 5. Check final state
    print("\n--- FINAL STATE SUMMARY ---")
    print(f"Axiomatic Anchors: {protogen.axiomatic_anchors}")
    print(f"Base Reasoning Patterns: {protogen.reasoning_engine.base_patterns.values()}")
    print(f"Recursive Reasoning Patterns: {protogen.reasoning_engine.recursive_patterns.values()}")
    
    # Example of using the accelerator for a custom logic map (not directly tied to the ontology graph)
    # This demonstrates the GPU/CPU fallback functionality
    print("\n--- ACCELERATOR TEST ---")
    test_logic_map = {
        "A": {"B": 1.0, "C": 0.5},
        "B": {"A": 1.0, "C": 0.2},
        "C": {"A": 0.5, "B": 0.2}
    }
    centrality_scores = protogen.accelerator.compute_eigenvector_centrality(test_logic_map)
    print(f"Test Centrality Scores: {centrality_scores}")
