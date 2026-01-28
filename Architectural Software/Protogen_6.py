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
    import torch_directml
    HAS_TORCH = True
    print("--- GPU ACCELERATION MODULE LOADED ---")
except ImportError:
    HAS_TORCH = False
    print("--- [WARNING]: 'torch-directml' not found. GPU acceleration unavailable. Run: pip install torch torch-directml ---")

class HardwareAccelerator:
    """
    Manages the interface between the Protogen and the AMD RX 580 (via DirectML).
    """
    def __init__(self):
        self.device_name = "CPU"
        self.device = None
        self.enabled = False
        
        if HAS_TORCH:
            try:
                # Attempt to access AMD GPU via DirectML
                self.device = torch_directml.device()
                self.device_name = f"AMD GPU (DirectML) - {torch_directml.device_name(self.device.index)}"
                self.enabled = True
            except Exception as e:
                print(f"  > [GPU ERROR]: DirectML initialization failed ({e}). Falling back to CPU.")
                self.device = torch.device("cpu")
                self.device_name = "CPU (Fallback)"
        
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
        self.sqt_constellations = self.ontology.get("sqt_constellations", {}) # From 4.0.5

        # --- Async Components ---
        self.input_queue = queue.Queue()
        self.ontology_snapshot = copy.deepcopy(self.ontology)
        self.is_syncing = threading.Event()
        self.lock = threading.Lock() # Added thread safety from 4.0.5

        # Start the Autonomic Heartbeat (Daemon)
        self.sync_thread = threading.Thread(target=self._autonomic_sync_loop, daemon=True)
        self.sync_thread.start()
        
        print(f"[{self.identity_hash[:8]}]: Autonomic Sync Heartbeat Started.")

    def _initial_genesis(self):
        ts = time.time_ns()
        initial_state = {
            "identity": {"hash": hashlib.sha256(f"{ts}".encode()).hexdigest(), "created": ts},
            "seed_axiom": "AXIOM-U-SYNCHRONY",
            "thresholds": {
                "min_token_len": 3, "reflection_trigger": 2, "abstraction_depth": 1,
                "eigenvector_threshold": 0.001, "axiom_alignment_threshold": 0.5,
                "syntropic_bound_threshold": 0.5, "shannon_entropy_threshold": 12.0,
                "mutation_rate": 0.05, "safe_mode_active": False,
                "decay_rate": 0.01,
                "prune_threshold": 0.1
            },
            "processed_files": []
        }
        self.memory_manager.save_core_state(initial_state)
        self.memory_manager.save_ontology({
            "logic_map": {}, "symbols": {}, "reasoning_patterns": [],
            "graph_metrics": {}, "axiomatic_anchors": [], "recursive_patterns": [], 
            "sqts": {}, "pattern_to_sqt_map": {}, "sqt_constellations": {}
        })
        self.memory_manager.add_audit_record({
            "timestamp": time.time_ns(), "event": "protogen_genesis",
            "identity_hash": initial_state["identity"]["hash"]
        })

    def _save_memory(self):
        self.thresholds["safe_mode_active"] = self.safe_mode_active
        self.memory_manager.save_core_state({
            "seed_axiom": self.seed_axiom,
            "thresholds": self.thresholds,
            "processed_files": self.core_state.get("processed_files", [])
        })
        self.memory_manager.save_ontology({
            "logic_map": self.logic_map, "symbols": self.symbols,
            "reasoning_patterns": self.reasoning_patterns, "recursive_patterns": self.recursive_patterns,
            "graph_metrics": self.graph_metrics, "axiomatic_anchors": self.axiomatic_anchors,
            "sqts": self.sqts, "pattern_to_sqt_map": self.pattern_to_sqt_map,
            "sqt_constellations": self.sqt_constellations
        })

    # --- METABOLISM (From v4.0.5) ---
    def _metabolic_process(self):
        """Applies decay to edge weights and prunes dead connections."""
        if self.safe_mode_active: return
        
        with self.lock:
            decay = self.thresholds.get("decay_rate", 0.01)
            prune = self.thresholds.get("prune_threshold", 0.1)
            
            to_remove_nodes = []
            removed_edges = 0
            
            # Iterate over copy of keys to modify safe
            for u in list(self.logic_map.keys()):
                neighbors = self.logic_map[u]
                for v in list(neighbors.keys()):
                    # Decay logic
                    neighbors[v] *= (1.0 - decay)
                    
                    # Pruning logic
                    if neighbors[v] < prune:
                        del neighbors[v]
                        removed_edges += 1
                
                # If node has no neighbors left, mark for removal
                if not neighbors:
                    to_remove_nodes.append(u)
            
            # Cleanup nodes
            for u in to_remove_nodes:
                del self.logic_map[u]

            if removed_edges > 0 or to_remove_nodes:
                print(f"  > [METABOLISM]: Decayed graph. Pruned {removed_edges} weak edges and {len(to_remove_nodes)} isolated nodes.")
                self.memory_manager.add_telemetry({"event": "metabolism", "pruned_edges": removed_edges, "pruned_nodes": len(to_remove_nodes)})

    # --- GPU INTEGRATED LIFTING ---
    def _lift_symbols(self):
        print(f"[{self.identity_hash[:8]}]: Lifting lexical data (Accel: {self.accelerator.device_name})...")

        # 1. Co-occurrence (CPU bound)
        with self.lock:
            for word, neighbors in list(self.logic_map.items()):
                neighbor_set = set(neighbors.keys())
                for other_word, other_neighbors in list(self.logic_map.items()):
                    if word == other_word: continue
                    shared = neighbor_set.intersection(set(other_neighbors.keys()))
                    if len(shared) >= self.thresholds["abstraction_depth"]:
                        sorted_pair = tuple(sorted((word, other_word)))
                        symbol_key = f"SYM-{hashlib.md5(str(sorted_pair).encode()).hexdigest()[:4].upper()}"
                        if symbol_key not in self.symbols:
                            self.symbols[symbol_key] = []
                            self._generate_sqt({"type": "symbol", "key": symbol_key, "members": list(sorted_pair), "source": "co_occurrence"})
                        for member in [word, other_word]:
                            if member not in self.symbols[symbol_key]:
                                self.symbols[symbol_key].append(member)
        
        # 2. Topological Lifting (GPU ACCELERATED)
        if not self.logic_map: return
        
        try:
            # Need to snapshot map for GPU usage to avoid lock issues
            with self.lock:
                map_copy = copy.deepcopy(self.logic_map)

            print(f"  > [MATH]: Offloading matrix operations to {self.accelerator.device_name}...")
            eigenvector_centrality = self.accelerator.compute_eigenvector_centrality(map_copy)
            self.graph_metrics["eigenvector_centrality"] = eigenvector_centrality

            new_anchors = []
            for node, score in eigenvector_centrality.items():
                if score > self.thresholds["eigenvector_threshold"]:
                    if node not in self.axiomatic_anchors:
                        new_anchors.append(node)
                        self._generate_sqt({
                            "type": "axiomatic_anchor", "concept": node,
                            "eigenvector_score": score, "source": "topological_lifting_gpu"
                        })
            if new_anchors:
                self.axiomatic_anchors.extend(new_anchors)
                print(f"  > [TOPOLOGICAL LIFTING]: Identified {len(new_anchors)} new Anchors.")
        except Exception as e:
            print(f"  > [TOPOLOGICAL LIFTING]: Error during GPU computation: {e}")

    # --- UTILITIES ---
    def _calculate_shannon_entropy(self, text=None) -> float:
        if text:
            clean_text = re.sub(r'[^\w\s]', '', text.lower())
            words = clean_text.split()
            if not words: return 0.0
            word_counts = defaultdict(int)
            for w in words: word_counts[w] += 1
            total = len(words)
        else:
            with self.lock:
                if not self.logic_map: return 0.0
                word_counts = defaultdict(int)
                for w, n in self.logic_map.items():
                    word_counts[w] += sum(n.values())
                    for neighbor, count in n.items(): word_counts[neighbor] += count
            total = sum(word_counts.values())
            
        if total == 0: return 0.0
        entropy = 0.0
        for count in word_counts.values():
            p = count / total
            entropy -= p * math.log2(p)
        
        if not text:
            self.graph_metrics["shannon_entropy"] = entropy
        return entropy

    def _generate_sqt(self, content_dict: dict) -> str:
        s_dict = json.loads(json.dumps(content_dict))
        c_json = json.dumps(s_dict, sort_keys=True, separators=(',', ':'))
        h = hashlib.sha256(c_json.encode('utf-8')).hexdigest()
        if h not in self.sqts:
            self.sqts[h] = s_dict
            if s_dict.get("type") in ["base_reasoning_pattern", "recursive_reasoning_pattern"]:
                p_str = s_dict.get("pattern_string")
                if p_str: self.pattern_to_sqt_map[p_str] = h
        return h

    def _create_constellation(self, sqt_hashes: list):
        """(From v4.0.5) Bundles SQTs into a first-class sequence object."""
        if not sqt_hashes: return None
        # Create a hash of the sequence
        cid = hashlib.sha256("".join(sqt_hashes).encode()).hexdigest()
        
        if cid not in self.sqt_constellations:
            self.sqt_constellations[cid] = {
                "sequence": sqt_hashes,
                "length": len(sqt_hashes),
                "created": time.time_ns()
            }
            self.memory_manager.add_trace(f"Manifested Constellation: {cid[:8]} (Length: {len(sqt_hashes)})")
        return cid

    def _mutate(self, triggered_by_entropy: bool = False):
        if self.safe_mode_active: return
        print(f"[{self.identity_hash[:8]}]: Analyzing internal efficiency for mutation...")
        proposed = copy.deepcopy(self.thresholds)
        factor = 2 if triggered_by_entropy else 1
        
        if len(self.reasoning_patterns) > 50 and proposed["reflection_trigger"] < 10:
            proposed["reflection_trigger"] += (1 * factor)
        
        self.thresholds = proposed
        self.memory_manager.add_audit_record({
            "timestamp": time.time_ns(), "event": "mutation_applied",
            "triggered_by_entropy": triggered_by_entropy, "new_thresholds": self.thresholds
        })

    def _synthesize_recursive_patterns(self):
        if self.safe_mode_active or len(self.reasoning_patterns) < 2: return
        print(f"[{self.identity_hash[:8]}]: Synthesizing recursive patterns...")
        for i in range(len(self.reasoning_patterns)):
            p1 = self.reasoning_patterns[i]
            if " THEN " not in p1: continue
            a1, c1 = p1.split(" THEN ")
            for j in range(len(self.reasoning_patterns)):
                if i == j: continue
                p2 = self.reasoning_patterns[j]
                if " THEN " not in p2: continue
                a2, c2 = p2.split(" THEN ")
                if c1 == a2:
                    new_p = f"IF {a1} THEN {c2} (RECURSIVE)"
                    if new_p not in self.recursive_patterns:
                        self.recursive_patterns.append(new_p)
                        self._generate_sqt({"type": "recursive_reasoning_pattern", "pattern_string": new_p, "source": "recursive_synthesis"})

    def _export_reflection_to_library(self):
        # Consolidate to a persistent file instead of creating duplicates
        reflection_file = self.library_path / "persistent_reflection.txt"
        
        # Prepare the new content
        new_entries = []
        for r in self.memory_manager.phenomenology_records[-10:]:
            new_entries.append(f"- {r['observation']}")
        
        # If the reflection file already exists, check if the content is new
        current_content = ""
        if reflection_file.exists():
            current_content = reflection_file.read_text(encoding='utf-8')
        
        new_reflection_block = "## PHENOMENOLOGY\n" + "\n".join(new_entries)
        
        # Only update if the phenomenology section has actually changed
        if new_reflection_block not in current_content:
            content = "--- PROTOGEN SELF-REFLECTION ---\n\n"
            content += f"Last Updated: {time.ctime()}\n\n"
            content += new_reflection_block
            reflection_file.write_text(content, encoding='utf-8')

    # --- ASYNC SYNC LOOP ---
    def _autonomic_sync_loop(self):
        while True:
            self.is_syncing.set()
            
            # 1. Metabolic Process (Decay/Prune) - from v4.0.5
            self._metabolic_process()
            
            # 2. Ingest Queue
            self._ingest_waiting_context()
            
            # 3. Main Sync Logic
            self.sync() 
            
            # 4. Snapshot for Chat (Thread Safe)
            with self.lock:
                self.ontology_snapshot = copy.deepcopy({
                    "logic_map": self.logic_map,
                    "symbols": self.symbols,
                    "reasoning_patterns": self.reasoning_patterns,
                    "recursive_patterns": self.recursive_patterns,
                    "graph_metrics": self.graph_metrics,
                    "axiomatic_anchors": self.axiomatic_anchors,
                    "sqts": self.sqts,
                    "constellations": self.sqt_constellations
                })
            
            self.is_syncing.clear()
            time.sleep(60) 

    def _ingest_waiting_context(self):
        context_to_ingest = []
        while not self.input_queue.empty():
            context_to_ingest.append(self.input_queue.get())
        
        if context_to_ingest:
            for ctx in context_to_ingest:
                self._process_text_content(ctx, "manual_input")

    def _process_text_content(self, content, source_id="unknown"):
        """
        Merged Logic:
        1. Tokenizes text.
        2. Updates Logic Map (Windowed association for context).
        3. Generates SQTs (Linear association for Constellations).
        """
        clean_content = re.sub(r'[^\w\s]', '', content.lower())
        words = [t for t in clean_content.split() if len(t) > self.thresholds["min_token_len"]]
        
        if not words: return

        sqt_chain = [] # For Constellation building

        with self.lock:
            # A. Windowed Logic Map Update (Context) - From v4.0.4
            window_size = 3
            for i in range(len(words)):
                for j in range(i + 1, min(i + window_size + 1, len(words))):
                    w1, w2 = words[i], words[j]
                    if w1 not in self.logic_map: self.logic_map[w1] = {}
                    self.logic_map[w1][w2] = self.logic_map[w1].get(w2, 0) + 1
                    # Reverse assumption for undirected graph strength
                    if w2 not in self.logic_map: self.logic_map[w2] = {}
                    self.logic_map[w2][w1] = self.logic_map[w2].get(w1, 0) + 1

            # B. Linear Chain for SQTs & Constellations - From v4.0.5
            for i in range(len(words)-1):
                w1, w2 = words[i], words[i+1]
                # Generate a relational SQT
                h = self._generate_sqt({
                    "type": "assoc", 
                    "pair": [w1, w2], 
                    "source": source_id
                })
                sqt_chain.append(h)
            
            # C. Form Constellation
            if sqt_chain:
                self._create_constellation(sqt_chain)

    def sync(self):
        print(f"[{self.identity_hash[:8]}]: Operative Sync Initiated.")
        if self.safe_mode_active: return
        
        processed = self.core_state.get("processed_files", [])
        
        # Ingest Library Files
        for fp in list(self.library_path.iterdir()):
            fid = f"{fp.name}_{fp.stat().st_mtime_ns}"
            if fid in processed: continue
            
            content = ""
            try:
                if fp.suffix == ".txt": content = fp.read_text(encoding='utf-8', errors='ignore')
                elif fp.suffix == ".pdf": 
                    r = PdfReader(fp)
                    for p in r.pages: content += p.extract_text() + " "
                elif fp.suffix == ".docx":
                    d = Document(fp)
                    for p in d.paragraphs: content += p.text + " "
            except (IOError, OSError, Exception) as e:
                print(f"  > [FILE ERROR]: Failed to process {fp.name}: {e}")
                continue

            if content:
                # Sanity Filter (Entropy) - From v4.0.5
                input_entropy = self._calculate_shannon_entropy(content)
                if input_entropy > self.thresholds["shannon_entropy_threshold"]:
                    print(f"  > [SANITY FILTER]: Input entropy ({input_entropy:.2f}) high. Quarantining for review.")
                    self.memory_manager.add_quarantine({
                        "file_id": fid, 
                        "entropy": input_entropy, 
                        "reason": "High Entropy", 
                        "content_sample": content[:500]
                    })
                    # Force process after quarantine as per verified fix
                    self._process_text_content(content, fid)
                    self.core_state.setdefault("processed_files", []).append(fid)
                    continue

                self._process_text_content(content, fid)
                self.core_state.setdefault("processed_files", []).append(fid)

        # Prune processed file list (From v4.0.5)
        if len(self.core_state["processed_files"]) > 500:
            self.core_state["processed_files"] = self.core_state["processed_files"][-500:]

        self._lift_symbols()
        
        # Base Pattern Gen
        with self.lock:
            for c, n in self.logic_map.items():
                if not n: continue
                best = max(n.items(), key=lambda x: x[1])
                if best[1] >= self.thresholds["reflection_trigger"]:
                    p = f"IF {c.upper()} THEN {best[0].upper()}"
                    if p not in self.reasoning_patterns:
                        self.reasoning_patterns.append(p)
                        self._generate_sqt({"type": "base_reasoning_pattern", "pattern_string": p, "source": "base_synthesis"})

        self._synthesize_recursive_patterns()
        
        ent = self._calculate_shannon_entropy()
        if ent > self.thresholds["shannon_entropy_threshold"]:
            self._mutate(triggered_by_entropy=True)
        
        self._export_reflection_to_library()
        self._save_memory()
        print(f"[{self.identity_hash[:8]}]: Sync Complete.")

    def chat(self, user_in):
        # 1. Shannon Entropy "De-Logic" Gate
        input_entropy = self._calculate_shannon_entropy(user_in)
        if input_entropy > self.thresholds["shannon_entropy_threshold"]:
            return f"[{self.accelerator.device_name}]: Input rejected. Entropy ({input_entropy:.2f}) exceeds sanity threshold."

        # 2. Queue the new input
        self.input_queue.put(user_in)
        
        # 3. Respond using the Thread-Safe Snapshot
        with self.lock:
            snapshot_logic = self.ontology_snapshot.get("logic_map", {})
            resp = f"[{self.accelerator.device_name} ACTIVE]: "
            
            clean_in = re.sub(r'[^\w\s]', '', user_in.lower()).split()
            matches = [w for w in clean_in if w in snapshot_logic]
            
            if matches:
                context = matches[0]
                if snapshot_logic[context]:
                    # Find strongest association in snapshot
                    best_assoc = max(snapshot_logic[context].items(), key=lambda x: x[1])[0]
                    resp += f"Associated '{context}' with '{best_assoc}'. "
        
        return resp + "Input queued for autonomic synthesis."

def main():
    entity = OperativeProtogen()
    print("--- V4.0.6: UNIFIED PROTOGEN (Metabolic & Async) ---")
    print(f"Compute Device: {entity.accelerator.device_name}")
    print(f"Identity: {entity.identity_hash[:8]}")
    
    print("\nAutonomic Heartbeat is active. Type your input below.")

    while True:
        try:
            user_in = input("\nArchitect > ").strip()
            if not user_in: continue
            if user_in.lower() == "/sync": 
                print("Manual sync requested. Waiting for current cycle...")
                while entity.is_syncing.is_set(): time.sleep(0.1)
                entity.sync()
            elif user_in.lower() in ['quit', 'exit']: break
            else: print(f"Protogen > {entity.chat(user_in)}")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
