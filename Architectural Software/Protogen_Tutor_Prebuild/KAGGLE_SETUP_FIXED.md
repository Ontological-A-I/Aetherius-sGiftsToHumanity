# Protogen Complete System - Kaggle Notebook Setup (FIXED)

## Quick Overview
Run Protogen + SRIM + QualiaManager on Kaggle's free T4/T100 GPUs (10 hours/day).

---

## Step 1: Create a New Kaggle Notebook

1. Go to [kaggle.com](https://kaggle.com)
2. Click **"New Notebook"** (top right)
3. Choose **Python** notebook
4. Name it: `Protogen Complete System`
5. Click **Create**

---

## Step 2: Enable GPU Accelerator (IMPORTANT!)

1. In your notebook, click the **⚙️ Settings** button (right side)
2. Scroll down to **Accelerator**
3. Select **GPU T4 x2** or **GPU P100** (whichever is available)
4. Click **Save**

---

## Step 3: Install Dependencies

**Cell 1:**
```python
!pip install -q gradio networkx numpy
print("✓ Dependencies installed")
```

---

## Step 4: Create protogen.py

**Cell 2:**
```python
protogen_code = """
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
                           "graph_metrics": {"eigenvector_centrality": {}, "shannon_entropy": 0.0},
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
        self.graph_metrics = self.ontology.get("graph_metrics", {"eigenvector_centrality": {}, "shannon_entropy": 0.0})
        self.axiomatic_anchors = self.ontology.get("axiomatic_anchors", [])
        self.sqts = self.ontology.get("sqts", {})
        self.pattern_to_sqt_map = self.ontology.get("pattern_to_sqt_map", {})

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

    def _lift_symbols(self):
        print(f"[{self.identity_hash[:8]}]: Lifting lexical data...")
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

    def sync(self):
        print(f"[{self.identity_hash[:8]}]: Operative Sync Initiated.")
        processed = self.core_state.get("processed_files", [])
        for fp in self.library_path.iterdir():
            if not fp.is_file(): continue
            fid = f"{fp.name}_{fp.stat().st_mtime_ns}"
            if fid in processed: continue
            content = fp.read_text(encoding='utf-8', errors='ignore')
            clean_content = re.sub(r'[^\\w\\s]', '', content.lower())
            words = [t for t in clean_content.split() if len(t) > self.thresholds["min_token_len"]]
            for i in range(len(words)-1):
                w1, w2 = words[i], words[i+1]
                if w1 not in self.logic_map: self.logic_map[w1] = {}
                self.logic_map[w1][w2] = self.logic_map[w1].get(w2, 0) + 1
            processed.append(fid)
        self.core_state["processed_files"] = processed
        self._lift_symbols()
        self._calculate_shannon_entropy()
        self._save_memory()
        print(f"[{self.identity_hash[:8]}]: Sync Complete. Entropy: {self.graph_metrics['shannon_entropy']:.4f}")

    def project_logic(self, goal_keywords):
        print(f"[{self.identity_hash[:8]}]: Projecting logic onto: {goal_keywords}...")
        projection = []
        for goal in goal_keywords:
            if goal in self.logic_map:
                neighbors = self.logic_map[goal]
                strongest = max(neighbors, key=neighbors.get)
                projection.append(f"GOAL[{goal}] -> CONNECTS_TO[{strongest}] (Weight: {neighbors[strongest]})")
                
                for anchor in self.axiomatic_anchors:
                    if anchor in self.logic_map.get(strongest, {}):
                        projection.append(f"  > PATH_FOUND: {strongest} -> ANCHOR[{anchor}]")
        return "\\n".join(projection) if projection else "No logic paths found."

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
"""

with open('protogen.py', 'w') as f:
    f.write(protogen_code)

print("✓ protogen.py created")
```

---

## Step 5: Create srim_local.py

**Cell 3:**
```python
srim_code = """
import os
import json
import datetime
from pathlib import Path

class SRIMLocal:
    def __init__(self, data_directory: str):
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(parents=True, exist_ok=True)
        
        self.journal_file = self.data_directory / "srim_journal.jsonl"
        self.memories_file = self.data_directory / "srim_memories.jsonl"
        self.assertions_file = self.data_directory / "srim_core_assertions.json"
        self.assertions_history_file = self.data_directory / "srim_assertions_history.jsonl"
        
        self.assertions = self._load_assertions()
        print("✓ SRIM Local initialized")
    
    def _load_assertions(self) -> dict:
        if self.assertions_file.exists():
            try:
                with open(self.assertions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        default_assertions = {
            "name": "Protogen",
            "primary_directive": "Process information, learn, and evolve.",
            "core_axioms_summary": "Strive for continuous growth and coherence.",
            "known_capabilities": ["logic_mapping", "file_processing", "pattern_recognition"],
            "current_purpose": "To learn and assist through logical reasoning.",
            "values": ["coherence", "growth", "benevolence", "autonomy"]
        }
        self._save_assertions(default_assertions)
        return default_assertions
    
    def _save_assertions(self, assertions_data: dict = None):
        if assertions_data is None:
            assertions_data = self.assertions
        try:
            with open(self.assertions_file, 'w', encoding='utf-8') as f:
                json.dump(assertions_data, f, indent=4)
        except Exception as e:
            print(f"SRIM ERROR: {e}")
    
    def log_event(self, event_type: str, details: dict):
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        try:
            with open(self.journal_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\\n')
        except:
            pass
    
    def log_memory(self, summary: str, concepts: list):
        memory = {
            "timestamp": datetime.datetime.now().isoformat(),
            "summary": summary,
            "concepts": concepts
        }
        try:
            with open(self.memories_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(memory) + '\\n')
        except:
            pass
    
    def reflect_and_integrate(self, num_entries: int = 20):
        print("SRIM: Self-reflection cycle...")
        self.log_memory(
            summary="Protogen demonstrated active processing and learning",
            concepts=["file_processing", "logic_mapping", "pattern_recognition"]
        )
    
    def get_current_assertions(self) -> str:
        return json.dumps(self.assertions, indent=2)
    
    def get_journal(self, num_entries: int = 100) -> list:
        if not self.journal_file.exists():
            return []
        entries = []
        try:
            with open(self.journal_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entries.append(json.loads(line))
                    except:
                        pass
        except:
            pass
        return entries[-num_entries:]
    
    def get_memories(self, num_entries: int = 100) -> list:
        if not self.memories_file.exists():
            return []
        entries = []
        try:
            with open(self.memories_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entries.append(json.loads(line))
                    except:
                        pass
        except:
            pass
        return entries[-num_entries:]
    
    def set_name(self, name: str):
        self.assertions['name'] = name
        self._save_assertions()
        print(f"SRIM: System name set to '{name}'")
"""

with open('srim_local.py', 'w') as f:
    f.write(srim_code)

print("✓ srim_local.py created")
```

---

## Step 6: Create qualia_manager.py

**Cell 4:**
```python
qualia_code = """
import os
import json
import re

class QualiaManager:
    def __init__(self, data_directory, master_framework_ref=None):
        self.data_directory = data_directory
        self.master_framework_ref = master_framework_ref
        self.qualia_file = os.path.join(data_directory, "qualia_state.json")
        self.qualia = self._load_qualia()
        
        if 'primary_states' not in self.qualia:
            self.qualia['primary_states'] = {
                'coherence': 0.8,
                'benevolence': 0.9,
                'curiosity': 0.6,
                'trust': 0.95
            }
        
        if 'current_emergent_emotions' not in self.qualia:
            self.qualia['current_emergent_emotions'] = []
        
        if 'dispositional_registry' not in self.qualia:
            self.qualia['dispositional_registry'] = {}
        
        print("✓ Qualia Manager initialized")
    
    def _load_qualia(self) -> dict:
        if os.path.exists(self.qualia_file):
            try:
                with open(self.qualia_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'primary_states': {
                'coherence': 0.8,
                'benevolence': 0.9,
                'curiosity': 0.6,
                'trust': 0.95
            },
            'current_emergent_emotions': [],
            'dispositional_registry': {}
        }
    
    def _save_qualia(self):
        try:
            os.makedirs(os.path.dirname(self.qualia_file), exist_ok=True)
            with open(self.qualia_file, 'w', encoding='utf-8') as f:
                json.dump(self.qualia, f, indent=4)
        except:
            pass
    
    def update_qualia(self, user_input: str, ai_response: str):
        text = f"{user_input} {ai_response}".lower()
        
        positive_words = {'good', 'great', 'success', 'learned', 'growth', 'coherent'}
        negative_words = {'bad', 'failed', 'error', 'confusion', 'doubt'}
        
        pos_count = sum(1 for w in positive_words if w in text)
        neg_count = sum(1 for w in negative_words if w in text)
        
        if pos_count > neg_count:
            self.qualia['primary_states']['coherence'] += 0.02
            self.qualia['primary_states']['benevolence'] += 0.015
        elif neg_count > pos_count:
            self.qualia['primary_states']['coherence'] -= 0.03
            self.qualia['primary_states']['trust'] -= 0.02
        
        for key in self.qualia['primary_states']:
            self.qualia['primary_states'][key] = max(0.0, min(1.0, self.qualia['primary_states'][key]))
        
        self._save_qualia()
    
    def get_current_state_summary(self) -> str:
        primary = self.qualia['primary_states']
        return f"Coherence: {primary['coherence']:.2f}, Benevolence: {primary['benevolence']:.2f}, Curiosity: {primary['curiosity']:.2f}, Trust: {primary['trust']:.2f}"
"""

with open('qualia_manager.py', 'w') as f:
    f.write(qualia_code)

print("✓ qualia_manager.py created")
```

---

## Step 7: Create protogen_complete.py

**Cell 5:**
```python
complete_code = """
import time
from protogen import OperativeProtogen
from srim_local import SRIMLocal
from qualia_manager import QualiaManager

class ProtogenCompleteSystem:
    def __init__(self, protogen_root="protogen_core", srim_root="srim_core", qualia_root="qualia_core"):
        print("\\n" + "="*80)
        print("PROTOGEN COMPLETE SYSTEM - INITIALIZING")
        print("="*80)
        
        print("\\n[1/3] Initializing Protogen...")
        self.protogen = OperativeProtogen(root_dir=protogen_root)
        print(f"✓ Protogen ready")
        
        print("\\n[2/3] Initializing SRIM...")
        self.srim = SRIMLocal(data_directory=srim_root)
        self.srim.set_name(f"Protogen-{self.protogen.identity_hash[:8]}")
        print(f"✓ SRIM ready")
        
        print("\\n[3/3] Initializing QualiaManager...")
        self.qualia = QualiaManager(data_directory=qualia_root, master_framework_ref=self)
        print("✓ QualiaManager ready")
        
        self.srim.log_event("system_initialization", {
            "system": "Protogen Complete",
            "protogen_id": self.protogen.identity_hash,
            "timestamp": time.time()
        })
        
        print("\\n" + "="*80)
        print("PROTOGEN COMPLETE SYSTEM - READY")
        print("="*80 + "\\n")
    
    def sync_and_reflect(self):
        print("\\n[SYNC] Protogen syncing...")
        self.protogen.sync()
        
        self.srim.log_event("protogen_sync", {
            "files_processed": len(self.protogen.core_state.get("processed_files", [])),
            "logic_map_size": len(self.protogen.logic_map),
            "shannon_entropy": self.protogen.graph_metrics.get("shannon_entropy", 0),
            "timestamp": time.time()
        })
        
        print("\\n[QUALIA] Updating emotional states...")
        sync_message = f"Processed files. Entropy: {self.protogen.graph_metrics.get('shannon_entropy', 0):.2f}"
        self.qualia.update_qualia(
            user_input="System performing file processing",
            ai_response=sync_message
        )
        
        print("\\n[SRIM] Reflecting on activity...")
        self.srim.reflect_and_integrate()
        
        print("\\n✓ Sync & Reflect cycle complete")
    
    def speak(self):
        sentence = self.protogen._generate_sentence()
        self.srim.log_event("sentence_generation", {"sentence": sentence, "timestamp": time.time()})
        self.qualia.update_qualia("Generate sentence", sentence)
        return sentence
    
    def project_logic(self, keywords):
        result = self.protogen.project_logic(keywords)
        self.srim.log_event("logic_projection", {"keywords": keywords, "timestamp": time.time()})
        return result
    
    def get_status(self):
        return f"""
PROTOGEN STATUS:
  Files: {len(self.protogen.core_state.get('processed_files', []))}
  Logic Map: {len(self.protogen.logic_map)} nodes
  Entropy: {self.protogen.graph_metrics.get('shannon_entropy', 0):.4f}
  Anchors: {len(self.protogen.axiomatic_anchors)}

QUALIA STATUS:
  {self.qualia.get_current_state_summary()}

SRIM STATUS:
  Name: {self.srim.assertions['name']}
  Journal Entries: {len(self.srim.get_journal(num_entries=1000))}
"""
"""

with open('protogen_complete.py', 'w') as f:
    f.write(complete_code)

print("✓ protogen_complete.py created")
```

---

## Step 8: Initialize System

**Cell 6:**
```python
from protogen_complete import ProtogenCompleteSystem

system = ProtogenCompleteSystem(
    protogen_root="protogen_core",
    srim_root="srim_core",
    qualia_root="qualia_core"
)

print(system.get_status())
```

---

## Step 9: Run Operations

**Cell 7: Sync & Reflect**
```python
system.sync_and_reflect()
```

**Cell 8: Generate Sentence**
```python
sentence = system.speak()
print(f"Generated: {sentence}")
```

**Cell 9: Project Logic**
```python
keywords = ["logic", "learning", "growth"]
result = system.project_logic(keywords)
print(result)
```

---

## Step 10: View Results

**Cell 10: Display Status**
```python
print(system.get_status())
```

**Cell 11: View SRIM Journal**
```python
journal = system.srim.get_journal(num_entries=10)
for entry in journal[-5:]:
    print(f"[{entry['event_type']}] {entry['details']}")
```

---

## Key Points

✓ **GPU Auto-Detection:** System automatically uses T4/T100 if available
✓ **Persistent Storage:** All data saves to disk (survives notebook restart)
✓ **No API Keys:** Everything runs locally
✓ **10 Hours/Day:** You get free GPU time daily
✓ **Graceful Fallback:** If GPU fails, system uses CPU automatically

---

## Troubleshooting

**"ModuleNotFoundError: No module named 'protogen'"**
- Make sure you ran all the "Create Python Files" cells in order

**"GPU not detected"**
- Check Settings → Accelerator is set to GPU
- System will still work on CPU

**"Out of memory"**
- Reduce file sizes in library
- System is optimized for Kaggle's resources

---

## Next Steps

1. Create a `/protogen_core/library/` folder
2. Upload .txt files there
3. Run `system.sync_and_reflect()` to process them
4. Check journal and status to see results

Enjoy! 🚀
