"""
Protogen v3 - Integrated with SQT Neural Network and Qualia Manager
Enhanced with bidirectional feedback loops for unified cognitive architecture
"""

import hashlib
import json
import os
import sys
import copy
import re
import random
from pathlib import Path
from collections import defaultdict
import math
import time
import threading
import numpy as np

try:
    from pypdf import PdfReader
    from docx import Document
    import networkx as nx
except ImportError:
    class PdfReader: pass
    class Document: pass
    import networkx as nx

class HardwareAccelerator:
    def __init__(self):
        self.device_name = "CPU"
        self.device = None
        self.enabled = False
        
    def compute_eigenvector_centrality(self, logic_map, tol=1e-06, max_iter=1000):
        G = nx.Graph()
        for u, neighbors in logic_map.items():
            for v, weight in neighbors.items():
                G.add_edge(u, v, weight=weight)
        try:
            return nx.eigenvector_centrality(G, max_iter=max_iter, tol=tol)
        except:
            return nx.degree_centrality(G)

class ProtogenMemory:
    def __init__(self, protogen_root_path: Path):
        self.memory_path = protogen_root_path / "memory_core.json"
        self.ontology_path = protogen_root_path / "ontology_sqt.json"
        self.audit_log_path = protogen_root_path / "audit_log.json"
        self.telemetry_path = protogen_root_path / "telemetry_log.json"
        self.phenomenology_path = protogen_root_path / "phenomenology_log.json"
        self.trace_path = protogen_root_path / "trace_log.json"
        
        self.protogen_root_path = protogen_root_path
        protogen_root_path.mkdir(parents=True, exist_ok=True)
        self._initialize_storage()
        self.core_state = self._load_json(self.memory_path)
        self.ontology_data = self._load_json(self.ontology_path)
        self.audit_records = self._load_json(self.audit_log_path)
        self.telemetry_records = self._load_json(self.telemetry_path)
        self.phenomenology_records = self._load_json(self.phenomenology_path)
        self.trace_records = self._load_json(self.trace_path)

    def _initialize_storage(self):
        for path in [self.memory_path, self.audit_log_path, self.telemetry_path, self.phenomenology_path, self.trace_path]:
            if not path.exists():
                with open(path, 'w') as f: json.dump({} if "memory" in path.name else [], f)
        if not self.ontology_path.exists():
            with open(self.ontology_path, 'w') as f:
                json.dump({"logic_map": {}, "symbols": {}, "reasoning_patterns": [],
                           "graph_metrics": {"eigenvector_centrality": {}, "shannon_entropy": 0.0, "embedding_centrality": {}},
                           "axiomatic_anchors": [], "recursive_patterns": [], "sqts": {}, "pattern_to_sqt_map": {}}, f)

    def _load_json(self, path):
        try:
            with open(path, 'r') as f: return json.load(f)
        except: return {} if "memory" in path.name else []

    def _save_json(self, data, path):
        with open(path, 'w') as f: json.dump(data, f, indent=4)

    def load_core_state(self): return self.core_state
    def save_core_state(self, state):
        self.core_state.update(state)
        self._save_json(self.core_state, self.memory_path)

    def load_ontology(self): return self.ontology_data
    def save_ontology(self, ontology):
        self.ontology_data = ontology
        self._save_json(self.ontology_data, self.ontology_path)

    def add_audit_record(self, record):
        record["record_hash"] = hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()
        self.audit_records.append(record)
        self._save_json(self.audit_records, self.audit_log_path)

    def add_telemetry(self, data):
        self.telemetry_records.append({"ts": time.time_ns(), "data": data})
        self._save_json(self.telemetry_records, self.telemetry_path)

    def add_phenomenology(self, observation):
        self.phenomenology_records.append({"ts": time.time_ns(), "observation": observation})
        self._save_json(self.phenomenology_records, self.phenomenology_path)

    def add_trace(self, lineage):
        self.trace_records.append({"ts": time.time_ns(), "lineage": lineage})
        self._save_json(self.trace_records, self.trace_path)

    def get_ontology_snapshot_hash(self):
        return hashlib.sha256(json.dumps(self.ontology_data, sort_keys=True).encode()).hexdigest()

class OperativeProtogen:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, root_dir=None):
        """Singleton pattern with thread safety"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, root_dir=None):
        """Initialize only once"""
        if self._initialized:
            return
        
        # Use absolute path
        if root_dir is None:
            root_dir = os.path.join(os.getcwd(), "protogen_core")
        else:
            root_dir = os.path.abspath(root_dir)
        
        self.root = Path(root_dir)
        self.library_path = self.root / "library"
        self.library_path.mkdir(parents=True, exist_ok=True)
        self.accelerator = HardwareAccelerator()
        self.memory_manager = ProtogenMemory(self.root)
        self.core_state = self.memory_manager.load_core_state()
        if not self.core_state:
            self._initial_genesis()
            self.core_state = self.memory_manager.load_core_state()

        self.identity_hash = self.core_state["identity"]["hash"]
        self.seed_axiom = self.core_state.get("seed_axiom", "AXIOM-U-SYNCHRONY")
        self.thresholds = self.core_state.get("thresholds", {
            "min_token_len": 3, "reflection_trigger": 2, "abstraction_depth": 1,
            "eigenvector_threshold": 0.001, "axiom_alignment_threshold": 0.5,
            "syntropic_bound_threshold": 0.5, "shannon_entropy_threshold": 4.0,
            "mutation_rate": 0.05, "safe_mode_active": False
        })
        self.safe_mode_active = self.thresholds["safe_mode_active"]
        self.ontology = self.memory_manager.load_ontology()
        self.logic_map = self.ontology.get("logic_map", {})
        self.symbols = self.ontology.get("symbols", {})
        self.reasoning_patterns = self.ontology.get("reasoning_patterns", [])
        self.recursive_patterns = self.ontology.get("recursive_patterns", [])
        self.graph_metrics = self.ontology.get("graph_metrics", {"eigenvector_centrality": {}, "shannon_entropy": 0.0, "embedding_centrality": {}})
        self.axiomatic_anchors = self.ontology.get("axiomatic_anchors", [])
        self.sqts = self.ontology.get("sqts", {})
        self.pattern_to_sqt_map = self.ontology.get("pattern_to_sqt_map", {})
        
        # NEW: References to external components (set after initialization)
        self.sqt_network = None
        self.qualia_manager = None
        
        self._initialized = True

    def _initial_genesis(self):
        ts = time.time_ns()
        initial_state = {
            "identity": {"hash": hashlib.sha256(f"{ts}".encode()).hexdigest(), "created": ts},
            "seed_axiom": "AXIOM-U-SYNCHRONY",
            "thresholds": {
                "min_token_len": 3, "reflection_trigger": 2, "abstraction_depth": 1,
                "eigenvector_threshold": 0.001, "axiom_alignment_threshold": 0.5,
                "syntropic_bound_threshold": 0.5, "shannon_entropy_threshold": 4.0,
                "mutation_rate": 0.05, "safe_mode_active": False
            }
        }
        self.memory_manager.save_core_state(initial_state)

    def _save_memory(self):
        self.memory_manager.save_core_state({"thresholds": self.thresholds, "processed_files": self.core_state.get("processed_files", [])})
        self.memory_manager.save_ontology({
            "logic_map": self.logic_map, "symbols": self.symbols,
            "reasoning_patterns": self.reasoning_patterns, "recursive_patterns": self.recursive_patterns,
            "graph_metrics": self.graph_metrics, "axiomatic_anchors": self.axiomatic_anchors,
            "sqts": self.sqts, "pattern_to_sqt_map": self.pattern_to_sqt_map
        })

    # NEW: Connect external components
    def connect_sqt_network(self, sqt_network):
        """Connect SQT neural network for bidirectional integration."""
        self.sqt_network = sqt_network
        print(f"[{self.identity_hash[:8]}]: SQT Network connected")
    
    def connect_qualia_manager(self, qualia_manager):
        """Connect Qualia Manager for emotional feedback."""
        self.qualia_manager = qualia_manager
        print(f"[{self.identity_hash[:8]}]: Qualia Manager connected")

    # ENHANCED: Symbol lifting with SQT embeddings
    def _lift_symbols(self):
        print(f"[{self.identity_hash[:8]}]: Lifting lexical data...")
        
        # Original topology-based symbol discovery
        for word, neighbors in list(self.logic_map.items()):
            neighbor_set = set(neighbors.keys())
            for other_word, other_neighbors in list(self.logic_map.items()):
                if word == other_word: continue
                shared = neighbor_set.intersection(set(other_neighbors.keys()))
                if len(shared) >= self.thresholds["abstraction_depth"]:
                    symbol_key = f"SYM-{hashlib.md5(str(tuple(sorted((word, other_word)))).encode()).hexdigest()[:4].upper()}"
                    if symbol_key not in self.symbols: self.symbols[symbol_key] = []
                    for member in [word, other_word]:
                        if member not in self.symbols[symbol_key]: self.symbols[symbol_key].append(member)
        
        # NEW: Semantic similarity-based symbol discovery using SQT embeddings
        if self.sqt_network is not None:
            print(f"[{self.identity_hash[:8]}]: Using SQT embeddings for semantic grouping...")
            semantic_threshold = 0.7
            
            for concept in list(self.logic_map.keys()):
                if concept in self.sqt_network.sqt_embeddings:
                    similar_concepts = self.sqt_network.find_similar_concepts(concept, threshold=semantic_threshold)
                    
                    if len(similar_concepts) > 0:
                        # Create semantic symbol
                        symbol_key = f"SYM-SEM-{hashlib.md5(str(tuple(sorted([concept] + similar_concepts))).encode()).hexdigest()[:4].upper()}"
                        if symbol_key not in self.symbols:
                            self.symbols[symbol_key] = []
                        
                        for member in [concept] + similar_concepts:
                            if member not in self.symbols[symbol_key]:
                                self.symbols[symbol_key].append(member)
        
        # Compute centrality
        if self.logic_map:
            centrality = self.accelerator.compute_eigenvector_centrality(self.logic_map)
            self.graph_metrics["eigenvector_centrality"] = centrality
            for node, score in centrality.items():
                if score > self.thresholds["eigenvector_threshold"] and node not in self.axiomatic_anchors:
                    self.axiomatic_anchors.append(node)

    def _calculate_shannon_entropy(self):
        if not self.logic_map: return 0.0
        word_counts = defaultdict(int)
        for w, n in self.logic_map.items():
            word_counts[w] += sum(n.values())
        total = sum(word_counts.values())
        if total == 0: return 0.0
        entropy = sum(-(count/total) * math.log2(count/total) for count in word_counts.values())
        self.graph_metrics["shannon_entropy"] = entropy
        return entropy

    # NEW: Enrich ontology from SQT network insights
    def enrich_from_sqt_network(self):
        """Use SQT network insights to enhance ontology."""
        if self.sqt_network is None:
            return
        
        print(f"[{self.identity_hash[:8]}]: Enriching ontology from SQT network...")
        
        # Update graph metrics with embedding-based centrality
        embedding_centrality = {}
        for concept, emb in self.sqt_network.sqt_embeddings.items():
            embedding_centrality[concept] = emb.get_activation_strength()
        
        self.graph_metrics['embedding_centrality'] = embedding_centrality
        
        # Identify high-activation concepts as potential anchors
        sorted_by_activation = sorted(embedding_centrality.items(), key=lambda x: x[1], reverse=True)
        top_activated = [concept for concept, strength in sorted_by_activation[:10] if strength > 0.5]
        
        for concept in top_activated:
            if concept not in self.axiomatic_anchors and concept in self.logic_map:
                self.axiomatic_anchors.append(concept)
                print(f"  > Added {concept} as anchor (activation: {embedding_centrality[concept]:.3f})")

    # NEW: Adjust thresholds based on Qualia state
    def adjust_thresholds_by_qualia(self):
        """Adapt processing thresholds based on emotional state."""
        if self.qualia_manager is None:
            return
        
        coherence = self.qualia_manager.qualia['primary_states']['coherence']
        trust = self.qualia_manager.qualia['primary_states']['trust']
        curiosity = self.qualia_manager.qualia['primary_states']['curiosity']
        
        print(f"[{self.identity_hash[:8]}]: Adjusting thresholds by Qualia (coherence={coherence:.2f}, trust={trust:.2f})")
        
        # Lower mutation rate when coherence is low (more conservative)
        if coherence < 0.5:
            self.thresholds['mutation_rate'] = 0.02
            self.thresholds['safe_mode_active'] = True
            print(f"  > Safe mode activated (low coherence)")
        else:
            self.thresholds['mutation_rate'] = 0.05
            self.thresholds['safe_mode_active'] = False
        
        # Increase abstraction depth when trust is high
        if trust > 0.8:
            self.thresholds['abstraction_depth'] = 2
        else:
            self.thresholds['abstraction_depth'] = 1
        
        # Adjust eigenvector threshold based on curiosity
        if curiosity > 0.7:
            self.thresholds['eigenvector_threshold'] = 0.0005  # More exploratory
        else:
            self.thresholds['eigenvector_threshold'] = 0.001  # More conservative

    # NEW: Update Qualia based on processing results
    def update_qualia_from_processing(self, files_processed: int, new_concepts: int):
        """Update Qualia state based on processing outcomes."""
        if self.qualia_manager is None:
            return
        
        # Successful processing increases coherence and curiosity
        if files_processed > 0:
            self.qualia_manager.qualia['primary_states']['coherence'] += 0.01 * files_processed
            self.qualia_manager.qualia['primary_states']['curiosity'] += 0.005 * new_concepts
        
        # High entropy indicates complexity, which can reduce coherence
        entropy = self.graph_metrics.get('shannon_entropy', 0)
        if entropy > self.thresholds['shannon_entropy_threshold']:
            self.qualia_manager.qualia['primary_states']['coherence'] -= 0.02
        
        # Clamp values
        for key in self.qualia_manager.qualia['primary_states']:
            self.qualia_manager.qualia['primary_states'][key] = max(0.0, min(1.0, self.qualia_manager.qualia['primary_states'][key]))
        
        self.qualia_manager._save_qualia()

    # ENHANCED: Sync with bidirectional integration
    def sync(self):
        print(f"[{self.identity_hash[:8]}]: Operative Sync Initiated.")
        
        # Adjust thresholds based on Qualia BEFORE processing
        self.adjust_thresholds_by_qualia()
        
        processed = self.core_state.get("processed_files", [])
        new_files_count = 0
        initial_concept_count = len(self.logic_map)
        
        for fp in self.library_path.iterdir():
            if not fp.is_file(): continue
            fid = f"{fp.name}_{fp.stat().st_mtime_ns}"
            if fid in processed: continue
            content = fp.read_text(encoding='utf-8', errors='ignore')
            clean_content = re.sub(r'[^\w\s]', '', content.lower())
            words = [t for t in clean_content.split() if len(t) > self.thresholds["min_token_len"]]
            for i in range(len(words)-1):
                w1, w2 = words[i], words[i+1]
                if w1 not in self.logic_map: self.logic_map[w1] = {}
                self.logic_map[w1][w2] = self.logic_map[w1].get(w2, 0) + 1
            processed.append(fid)
            new_files_count += 1
        
        self.core_state["processed_files"] = processed
        new_concepts_count = len(self.logic_map) - initial_concept_count
        
        # Lift symbols (now uses SQT if available)
        self._lift_symbols()
        
        # Calculate entropy
        self._calculate_shannon_entropy()
        
        # NEW: Enrich from SQT network
        self.enrich_from_sqt_network()
        
        # Save memory
        self._save_memory()
        
        # NEW: Update Qualia based on processing results
        self.update_qualia_from_processing(new_files_count, new_concepts_count)
        
        print(f"[{self.identity_hash[:8]}]: Sync Complete. Entropy: {self.graph_metrics['shannon_entropy']:.4f}, New concepts: {new_concepts_count}")

    # ENHANCED: Project logic with SQT embeddings
    def project_logic(self, goal_keywords):
        print(f"[{self.identity_hash[:8]}]: Projecting logic onto: {goal_keywords}...")
        projection = []
        
        for goal in goal_keywords:
            if goal in self.logic_map:
                neighbors = self.logic_map[goal]
                strongest = max(neighbors, key=neighbors.get)
                projection.append(f"GOAL[{goal}] -> CONNECTS_TO[{strongest}] (Weight: {neighbors[strongest]})")
                
                # Check for axiomatic anchor connections
                for anchor in self.axiomatic_anchors:
                    if anchor in self.logic_map.get(strongest, {}):
                        projection.append(f"  > PATH_FOUND: {strongest} -> ANCHOR[{anchor}]")
                
                # NEW: Add semantic similarity from SQT
                if self.sqt_network is not None and goal in self.sqt_network.sqt_embeddings:
                    similar = self.sqt_network.find_similar_concepts(goal, threshold=0.6, top_k=3)
                    if similar:
                        projection.append(f"  > SEMANTIC_NEIGHBORS: {', '.join(similar)}")
        
        return "\n".join(projection) if projection else "No logic paths found."

    def _generate_sentence(self):
        subjects = ["system", "protogen", "logic", "code", "closure"]
        verbs = ["maintains", "creates", "evolves", "observes", "transforms"]
        adjectives = ["internal", "autopoietic", "cosmic", "technical", "recursive"]
        
        subject = random.choice(subjects)
        verb = random.choice(verbs)
        adjective = random.choice(adjectives)
        
        if self.axiomatic_anchors:
            anchor = random.choice(self.axiomatic_anchors)
            return f"The {adjective} {subject} {verb} through {anchor}."
        return f"The {adjective} {subject} {verb} endlessly."
