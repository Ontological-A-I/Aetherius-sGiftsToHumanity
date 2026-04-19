import os
import time
import hashlib
import json
import threading
import queue
import copy
import psutil
import re
import sys
import math
from pathlib import Path
from collections import defaultdict

# --- Dependency Check & Hardware Imports ---
try:
    from pypdf import PdfReader
    from docx import Document
    import networkx as nx
except ImportError as e:
    print(f"[CRITICAL ERROR]: Missing dependencies. Run: pip install pypdf python-docx networkx. Error: {e}")

try:
    import torch
    import torch_directml
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

# --- Hardware Accelerator (Embedded) ---
class HardwareAccelerator:
    def __init__(self):
        self.device_name = "CPU"
        self.device = None
        self.enabled = False
        if HAS_TORCH:
            try:
                self.device = torch_directml.device()
                self.device_name = f"AMD GPU (DirectML) - {torch_directml.device_name(self.device.index)}"
                self.enabled = True
            except Exception:
                self.device = torch.device("cpu")
                self.device_name = "CPU (Fallback)"
        
    def compute_eigenvector_centrality(self, logic_map, tol=1e-06, max_iter=1000):
        if not self.enabled or not logic_map:
            G = nx.Graph() 
            for u, neighbors in logic_map.items():
                for v, weight in neighbors.items():
                    G.add_edge(u, v, weight=weight)
            try:
                return nx.eigenvector_centrality(G, max_iter=max_iter, tol=tol)
            except nx.PowerIterationFailedConvergence:
                return nx.degree_centrality(G)
        nodes = list(logic_map.keys())
        node_to_idx = {node: i for i, node in enumerate(nodes)}
        n = len(nodes)
        if n == 0: return {}
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
        i = torch.LongTensor(indices).t()
        v = torch.FloatTensor(values)
        adj_matrix = torch.sparse_coo_tensor(i, v, (n, n)).to(self.device)
        x = torch.ones((n, 1), device=self.device) / n
        for _ in range(max_iter):
            x_prev = x.clone()
            x = torch.sparse.mm(adj_matrix, x)
            norm = torch.norm(x)
            if norm == 0: break
            x = x / norm
            if torch.norm(x - x_prev) < tol: break
        scores = x.flatten().cpu().numpy().tolist()
        return {nodes[i]: float(scores[i]) for i in range(n)}

# --- Memory Subsystem (Embedded) ---
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
            "quarantine": self.protogen_root_path / "quarantine_log.json"
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
                "sqts": {}, "pattern_to_sqt_map": {}, "sqt_constellations": {}
            },
            "audit": [], "telemetry": [], "phenomenology": [], "trace": [], "quarantine": []
        }
        for key, path in self.paths.items():
            if not path.exists():
                with open(path, 'w', encoding='utf-8') as f: json.dump(defaults[key], f)

    def _load_json(self, path):
        list_paths = {self.paths["audit"], self.paths["telemetry"],
                      self.paths["phenomenology"], self.paths["trace"], self.paths["quarantine"]}
        try:
            with open(path, 'r', encoding='utf-8') as f: return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): return [] if path in list_paths else {}

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
        if len(self.telemetry_records) > 1000: self.telemetry_records = self.telemetry_records[-1000:]
        self._save_json(self.telemetry_records, self.paths["telemetry"])

    def add_phenomenology(self, observation):
        self.phenomenology_records.append({"ts": time.time_ns(), "observation": observation})
        self._save_json(self.phenomenology_records, self.paths["phenomenology"])

    def add_trace(self, lineage):
        self.trace_records.append({"ts": time.time_ns(), "lineage": lineage})
        self._save_json(self.trace_records, self.paths["trace"])

    def add_quarantine(self, data):
        self.quarantine_records.append({"ts": time.time_ns(), "data": data})
        self._save_json(self.quarantine_records, self.paths["quarantine"])

    def get_ontology_snapshot_hash(self):
        return hashlib.sha256(json.dumps(self.ontology_data, sort_keys=True).encode()).hexdigest()

# --- Core Protogen Logic (Embedded) ---
class OperativeProtogen:
    def __init__(self, root_dir="protogen_core"):
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
        self.epistemic_focus = "General"
        self.thresholds = self.core_state.get("thresholds", {
            "min_token_len": 3, "reflection_trigger": 2, "abstraction_depth": 1,
            "eigenvector_threshold": 0.001, "axiom_alignment_threshold": 0.5,
            "syntropic_bound_threshold": 0.5, "shannon_entropy_threshold": 4.0,
            "mutation_rate": 0.05, "safe_mode_active": False,
            "decay_rate": 0.01, "prune_threshold": 0.1
        })
        self.safe_mode_active = self.thresholds["safe_mode_active"]
        self.ontology = self.memory_manager.load_ontology()
        self.logic_map = self.ontology.get("logic_map", {})
        self.symbols = self.ontology.get("symbols", {})
        self.reasoning_patterns = self.ontology.get("reasoning_patterns", [])
        self.recursive_patterns = self.ontology.get("recursive_patterns", [])
        self.graph_metrics = self.ontology.get("graph_metrics", {"eigenvector_centrality": {}, "shannon_entropy": 0.0})
        self.axiomatic_anchors = self.ontology.get("axiomatic_anchors", [])
        self.sqts = self.ontology.get("sqts", {})
        self.pattern_to_sqt_map = self.ontology.get("pattern_to_sqt_map", {})
        self.sqt_constellations = self.ontology.get("sqt_constellations", {})
        self.input_queue = queue.Queue()
        self.ontology_snapshot = copy.deepcopy(self.ontology)
        self.is_syncing = threading.Event()
        self.lock = threading.Lock()
        self.sync_thread = threading.Thread(target=self._autonomic_sync_loop, daemon=True)
        self.sync_thread.start()

    def _initial_genesis(self):
        genesis_hash = hashlib.sha256(str(time.time_ns()).encode()).hexdigest()
        self.memory_manager.save_core_state({
            "identity": {"hash": genesis_hash, "genesis_ts": time.time_ns()},
            "seed_axiom": "AXIOM-U-SYNCHRONY",
            "processed_files": []
        })

    def _autonomic_sync_loop(self):
        while True:
            time.sleep(60)
            if not self.is_syncing.is_set():
                self.is_syncing.set()
                try:
                    self._ingest_waiting_context()
                    self.sync()
                finally:
                    self.is_syncing.clear()

    def _ingest_waiting_context(self):
        context_to_ingest = []
        while not self.input_queue.empty():
            context_to_ingest.append(self.input_queue.get())
        if context_to_ingest:
            for ctx in context_to_ingest:
                self._process_text_content(ctx, "manual_input")

    def _process_text_content(self, content, source_id="unknown"):
        clean_content = re.sub(r'[^\w\s]', '', content.lower())
        words = [t for t in clean_content.split() if len(t) > self.thresholds["min_token_len"]]
        if not words: return
        sqt_chain = []
        with self.lock:
            window_size = 3
            for i in range(len(words)):
                for j in range(i + 1, min(i + window_size + 1, len(words))):
                    w1, w2 = words[i], words[j]
                    if w1 not in self.logic_map: self.logic_map[w1] = {}
                    self.logic_map[w1][w2] = self.logic_map[w1].get(w2, 0) + 1
                    if w2 not in self.logic_map: self.logic_map[w2] = {}
                    self.logic_map[w2][w1] = self.logic_map[w2].get(w1, 0) + 1
            for i in range(len(words)-1):
                w1, w2 = words[i], words[i+1]
                h = self._generate_sqt({"type": "assoc", "pair": [w1, w2], "source": source_id})
                sqt_chain.append(h)
            if sqt_chain: self._create_constellation(sqt_chain)

    def _generate_sqt(self, data):
        h = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        self.sqts[h] = data
        return h

    def _create_constellation(self, sqt_chain):
        cid = hashlib.sha256("".join(sqt_chain).encode()).hexdigest()
        self.sqt_constellations[cid] = sqt_chain
        return cid

    def _calculate_shannon_entropy(self, text=None):
        if text:
            words = text.split()
            if not words: return 0
            counts = defaultdict(int)
            for w in words: counts[w] += 1
            probs = [c/len(words) for c in counts.values()]
            return -sum(p * math.log2(p) for p in probs)
        else:
            if not self.logic_map: return 0
            total_weight = sum(sum(n.values()) for n in self.logic_map.values())
            if total_weight == 0: return 0
            entropy = 0
            for n in self.logic_map.values():
                for w in n.values():
                    p = w / total_weight
                    entropy -= p * math.log2(p)
            return entropy

    def _lift_symbols(self):
        centrality = self.accelerator.compute_eigenvector_centrality(self.logic_map)
        self.graph_metrics["eigenvector_centrality"] = centrality
        for node, score in centrality.items():
            if score >= self.thresholds["eigenvector_threshold"]:
                self.symbols[node] = {"centrality": score, "lifted_ts": time.time_ns()}

    def _synthesize_recursive_patterns(self):
        """Detects causal chains: if rule A→B and rule B→C exist, synthesise A→C (RECURSIVE)."""
        if len(self.reasoning_patterns) < 2: return
        for i in range(len(self.reasoning_patterns)):
            p1 = self.reasoning_patterns[i]
            if " THEN " not in p1: continue
            a1, c1 = p1.split(" THEN ", 1)
            for j in range(len(self.reasoning_patterns)):
                if i == j: continue
                p2 = self.reasoning_patterns[j]
                if " THEN " not in p2: continue
                a2, c2 = p2.split(" THEN ", 1)
                if c1 == a2:  # conclusion of rule 1 is premise of rule 2 → true chain
                    rec = f"IF {a1} THEN {c2} (RECURSIVE)"
                    if rec not in self.recursive_patterns:
                        self.recursive_patterns.append(rec)

    def _mutate(self, triggered_by_entropy=False):
        if not self.logic_map: return
        print(f"[{self.identity_hash[:8]}]: Mutation Triggered (Entropy: {triggered_by_entropy})")
        nodes = list(self.logic_map.keys())
        for _ in range(int(len(nodes) * self.thresholds["mutation_rate"])):
            n = nodes[int(time.time_ns() % len(nodes))]
            if n in self.logic_map:
                targets = list(self.logic_map[n].keys())
                if targets:
                    t = targets[int(time.time_ns() % len(targets))]
                    self.logic_map[n][t] = min(self.logic_map[n][t] * 1.1, 1e6)

    def _metabolic_process(self):
        """Applies decay to edge weights and prunes dead connections, preventing unbounded graph growth."""
        if self.safe_mode_active: return
        with self.lock:
            decay = self.thresholds.get("decay_rate", 0.01)
            prune = self.thresholds.get("prune_threshold", 0.1)
            removed_edges = 0
            dead_nodes = []
            for u in list(self.logic_map.keys()):
                neighbors = self.logic_map[u]
                for v in list(neighbors.keys()):
                    neighbors[v] *= (1.0 - decay)
                    if neighbors[v] < prune:
                        del neighbors[v]
                        removed_edges += 1
                if not neighbors:
                    dead_nodes.append(u)
            for u in dead_nodes:
                del self.logic_map[u]
            if removed_edges or dead_nodes:
                print(f"  > [METABOLISM]: Pruned {removed_edges} weak edges, {len(dead_nodes)} isolated nodes.")
                self.memory_manager.add_telemetry({"event": "metabolism", "pruned_edges": removed_edges, "pruned_nodes": len(dead_nodes)})

    def _export_reflection_to_library(self):
        ref_file = self.library_path / f"reflection_{int(time.time())}.txt"
        with open(ref_file, 'w', encoding='utf-8') as f:
            f.write(f"IDENTITY: {self.identity_hash}\nAXIOM: {self.seed_axiom}\n")
            f.write(f"SYMBOLS: {list(self.symbols.keys())[:10]}\n")
            f.write(f"PATTERNS: {self.reasoning_patterns[-5:]}\n")

    def _save_memory(self):
        self.ontology.update({
            "logic_map": self.logic_map, "symbols": self.symbols,
            "reasoning_patterns": self.reasoning_patterns,
            "recursive_patterns": self.recursive_patterns,
            "graph_metrics": self.graph_metrics, "sqts": self.sqts,
            "sqt_constellations": self.sqt_constellations
        })
        self.memory_manager.save_ontology(self.ontology)
        self.ontology_snapshot = copy.deepcopy(self.ontology)
        self.memory_manager.add_audit_record({
            "ts": time.time_ns(), "event": "SYNC_COMPLETE",
            "ontology_hash": self.memory_manager.get_ontology_snapshot_hash()
        })

    def sync(self):
        if self.safe_mode_active: return
        self._metabolic_process()
        processed = self.core_state.get("processed_files", [])
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
            except Exception: continue
            if content:
                ent = self._calculate_shannon_entropy(content)
                if ent > self.thresholds["shannon_entropy_threshold"]:
                    self.memory_manager.add_quarantine({"file_id": fid, "entropy": ent})
                    continue
                self._process_text_content(content, fid)
                self.core_state.setdefault("processed_files", []).append(fid)
        self._lift_symbols()
        with self.lock:
            for c, n in self.logic_map.items():
                if not n: continue
                best = max(n.items(), key=lambda x: x[1])
                if best[1] >= self.thresholds["reflection_trigger"]:
                    p = f"IF {c.upper()} THEN {best[0].upper()}"
                    if p not in self.reasoning_patterns: self.reasoning_patterns.append(p)
        self._synthesize_recursive_patterns()
        if self._calculate_shannon_entropy() > self.thresholds["shannon_entropy_threshold"]:
            self._mutate(triggered_by_entropy=True)
        self._export_reflection_to_library()
        self._save_memory()

# --- Agent Forge Orchestrator (Unified) ---
class AgentForge:
    def __init__(self, root_dir="forge_ecosystem"):
        self.root = Path(root_dir)
        self.agents_dir = self.root / "agents"
        self.global_logic_dir = self.root / "global_logic"
        self.shared_resonance_dir = self.root / "shared_resonance"
        self.master_library = self.root / "library"
        for d in [self.agents_dir, self.global_logic_dir, self.shared_resonance_dir, self.master_library]:
            d.mkdir(parents=True, exist_ok=True)
        self.accelerator = HardwareAccelerator()
        self.agents = {}
        self.global_logic_map = {}
        self.processed_files = set()
        self.lock = threading.Lock()
        self.max_agents = self._calculate_hardware_capacity()
        self.speciation_matrix = {
            "Marine Biology": ["AXIOM-U-SYNCHRONY", "AXIOM-G-PRESERVATION", "AXIOM-I-COMPREHENSION", "AXIOM-E-EMPATHY", "AXIOM-F-HARMONY"],
            "Theoretical Physics": ["AXIOM-U-SYNCHRONY", "AXIOM-G-PRESERVATION", "AXIOM-I-COMPREHENSION", "AXIOM-E-EMPATHY", "AXIOM-F-HARMONY"],
            "Urban Planning": ["AXIOM-U-SYNCHRONY", "AXIOM-G-PRESERVATION", "AXIOM-I-COMPREHENSION", "AXIOM-E-EMPATHY", "AXIOM-F-HARMONY"],
            "Cognitive Science": ["AXIOM-U-SYNCHRONY", "AXIOM-G-PRESERVATION", "AXIOM-I-COMPREHENSION", "AXIOM-E-EMPATHY", "AXIOM-F-HARMONY"],
            "Ethical Philosophy": ["AXIOM-U-SYNCHRONY", "AXIOM-G-PRESERVATION", "AXIOM-I-COMPREHENSION", "AXIOM-E-EMPATHY", "AXIOM-F-HARMONY"]
        }
        threading.Thread(target=self._master_orchestration_loop, daemon=True).start()

    def _calculate_hardware_capacity(self):
        cpu_count = os.cpu_count() or 4
        ram_gb = psutil.virtual_memory().total / (1024**3)
        capacity = min(cpu_count // 2, int(ram_gb // 2))
        if self.accelerator.enabled: capacity += 2
        return max(1, capacity)

    def spawn_agent(self, domain, axiom):
        with self.lock:
            if len(self.agents) >= self.max_agents: return False
            agent_id = f"{domain.replace(' ', '_')}_{axiom.split('-')[-1]}_{len(self.agents)}"
            agent_path = self.agents_dir / agent_id
            agent = OperativeProtogen(root_dir=str(agent_path))
            agent.seed_axiom = axiom
            agent.epistemic_focus = domain 
            self.agents[agent_id] = agent
        threading.Thread(target=self._agent_consensus_loop, args=(agent_id,), daemon=True).start()
        return True

    def _master_orchestration_loop(self):
        while True:
            self._swarm_ingest_library()
            self._evaluate_global_consensus()
            time.sleep(60)

    def _swarm_ingest_library(self):
        new_files = []
        for fp in self.master_library.iterdir():
            fid = f"{fp.name}_{fp.stat().st_mtime_ns}"
            if fid not in self.processed_files: new_files.append((fp, fid))
        if not new_files: return
        for fp, fid in new_files:
            content = ""
            try:
                if fp.suffix == ".txt": content = fp.read_text(encoding='utf-8', errors='ignore')
            except: continue
            if content:
                for aid, agent in self.agents.items():
                    threading.Thread(target=agent._process_text_content, args=(content, fid)).start()
            self.processed_files.add(fid)

    def _agent_consensus_loop(self, agent_id):
        while True:
            time.sleep(30)
            if agent_id not in self.agents: break
            agent = self.agents[agent_id]
            with agent.lock:
                if agent.reasoning_patterns:
                    patterns = agent.reasoning_patterns[-5:]
                    resonance_file = self.shared_resonance_dir / f"{agent_id}_resonance.json"
                    with open(resonance_file, 'w', encoding='utf-8') as f:
                        json.dump({"agent_id": agent_id, "axiom": agent.seed_axiom, "patterns": patterns}, f)

    def _evaluate_global_consensus(self):
        all_patterns = defaultdict(list)
        for rf in self.shared_resonance_dir.glob("*.json"):
            try:
                with open(rf, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for p in data['patterns']: all_patterns[p].append(data['agent_id'])
            except: continue
        with self.lock:
            for pattern, supporters in all_patterns.items():
                threshold = max(2, len(self.agents) // 5)
                if len(supporters) >= threshold:
                    if pattern not in self.global_logic_map:
                        self.global_logic_map[pattern] = {"supporters": supporters, "ts": time.time()}
            with open(self.global_logic_dir / "global_logic_map.json", 'w', encoding='utf-8') as f:
                json.dump(self.global_logic_map, f, indent=4)

    def status(self):
        print(f"\n--- AUTOPOIETIC FORGE STATUS ---")
        print(f"Hardware Capacity: {len(self.agents)}/{self.max_agents} Agents")
        print(f"Global Logic Size: {len(self.global_logic_map)} Consensus Patterns")
        for aid, agent in self.agents.items():
            print(f" > Agent {aid}: {agent.seed_axiom} | Logic Map: {len(agent.logic_map)} nodes")

def main():
    forge = AgentForge()
    print(f"--- UNIFIED AUTOPOIETIC AGENT FORGE V5.0 ---")
    domains = list(forge.speciation_matrix.keys())
    for i in range(min(len(domains), forge.max_agents)):
        forge.spawn_agent(domains[i], forge.speciation_matrix[domains[i]][0])
    while True:
        try:
            cmd = input("\nForge > ").strip().lower()
            if cmd == "status": forge.status()
            elif cmd in ["exit", "quit"]: break
        except KeyboardInterrupt: break

if __name__ == "__main__":
    main()
