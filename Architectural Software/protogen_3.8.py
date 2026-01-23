import time
import hashlib
import json
import os
import sys
import inspect
from pathlib import Path
from pypdf import PdfReader # Ensure this is installed: pip install pypdf
from docx import Document   # Ensure this is installed: pip install python-docx
from collections import defaultdict
import networkx as nx # Ensure this is installed: pip install networkx
import math # For Shannon entropy calculation
import copy # NEW: For deep copying state for BEV

# --- Placeholder for the new, structured memory subsystem ---
class ProtogenMemory:
    """
    Manages the OperativeProtogen's persistent knowledge, including SQTs,
    symbols, reasoning patterns, and processing history.
    This replaces the direct use of 'memory.json' for these specific structures.
    """
    def __init__(self, protogen_root_path: Path):
        self.memory_path = protogen_root_path / "memory_core.json" # Core Protogen state
        self.ontology_path = protogen_root_path / "ontology_sqt.json" # For SQT-based knowledge graph and graph metrics
        self.audit_log_path = protogen_root_path / "audit_log.json" # For verifiable actions
        self.protogen_root_path = protogen_root_path

        # Ensure all necessary directories/files exist
        protogen_root_path.mkdir(parents=True, exist_ok=True)
        # Initialize internal storage if files don't exist
        self._initialize_storage()

        self.core_state = self._load_json(self.memory_path)
        self.ontology_data = self._load_json(self.ontology_path) # Will store SQTs, symbols, patterns, graph metrics
        self.audit_records = self._load_json(self.audit_log_path) # Will store detailed logs

    def _initialize_storage(self):
        if not self.memory_path.exists():
            with open(self.memory_path, 'w') as f:
                json.dump({}, f)
        if not self.ontology_path.exists():
            with open(self.ontology_path, 'w') as f:
                # Initialize with graph_metrics, axiomatic_anchors, and sqts
                json.dump({"logic_map": {}, "symbols": {}, "reasoning_patterns": [],
                           "graph_metrics": {"eigenvector_centrality": {}, "shannon_entropy": 0.0},
                           "axiomatic_anchors": [],
                           "recursive_patterns": [],
                           "sqts": {},
                           "pattern_to_sqt_map": {}
                          }, f)
        if not self.audit_log_path.exists():
            with open(self.audit_log_path, 'w') as f:
                json.dump([], f)

    def _load_json(self, path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {} # Or appropriate default for the specific file

    def _save_json(self, data, path):
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)

    def load_core_state(self):
        return self.core_state

    def save_core_state(self, state):
        self.core_state.update(state)
        self._save_json(self.core_state, self.memory_path)

    def load_ontology(self):
        return self.ontology_data

    def save_ontology(self, ontology):
        self.ontology_data = ontology
        self._save_json(self.ontology_data, self.ontology_path)

    def add_audit_record(self, record):
        # NEW: Link audit records cryptographically
        if self.audit_records:
            record["previous_record_hash"] = hashlib.sha256(json.dumps(self.audit_records[-1], sort_keys=True).encode()).hexdigest()
        else:
            record["previous_record_hash"] = "GENESIS" # First record
        record["record_hash"] = hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest() # Hash its own content
        self.audit_records.append(record)
        self._save_json(self.audit_records, self.audit_log_path)

    # NEW: Method to get a snapshot of the ontology for rollback/auditing
    def get_ontology_snapshot_hash(self):
        """Generates a hash of the current ontology state for continuity."""
        return hashlib.sha256(json.dumps(self.ontology_data, sort_keys=True).encode()).hexdigest()


class OperativeProtogen:
    def __init__(self, root_dir="protogen_core"):
        self.root = Path(root_dir)
        self.library_path = self.root / "library"
        self.script_path = Path(__file__)

        self.library_path.mkdir(parents=True, exist_ok=True)

        self.memory_manager = ProtogenMemory(self.root)

        self.core_state = self.memory_manager.load_core_state()
        if not self.core_state:
            self._initial_genesis()
            self.core_state = self.memory_manager.load_core_state()

        self.identity_hash = self.core_state["identity"]["hash"]

        self.seed_axiom = self.core_state.get("seed_axiom", "AXIOM-U-SYNCHRONY")
        self.recursive_anchor_directive = self.core_state.get("recursive_anchor_directive", "Topological Closure")
        self.science_baseline_directive = self.core_state.get("science_baseline_directive", "Hardware Determinism")

        self.thresholds = self.core_state.get("thresholds", {
            "min_token_len": 5,
            "reflection_trigger": 3,
            "abstraction_depth": 2,
            "eigenvector_threshold": 0.01,
            "axiom_alignment_threshold": 0.5,
            "syntropic_bound_threshold": 0.5,
            "shannon_entropy_threshold": 4.0,
            "mutation_rate": 0.05,
            "safe_mode_active": False # NEW: Safe mode status
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
        """Initializes the core state for a brand new Protogen."""
        ts = time.time_ns()
        initial_state = {
            "identity": {"hash": hashlib.sha256(f"{ts}".encode()).hexdigest(), "created": ts},
            "seed_axiom": "AXIOM-U-SYNCHRONY",
            "recursive_anchor_directive": "Topological Closure",
            "science_baseline_directive": "Hardware Determinism",
            "thresholds": {
                "min_token_len": 5,
                "reflection_trigger": 3,
                "abstraction_depth": 2,
                "eigenvector_threshold": 0.01,
                "axiom_alignment_threshold": 0.5,
                "syntropic_bound_threshold": 0.5,
                "shannon_entropy_threshold": 4.0,
                "mutation_rate": 0.05,
                "safe_mode_active": False # NEW
            },
            "processed_files": []
        }
        self.memory_manager.save_core_state(initial_state)
        self.memory_manager.save_ontology({"logic_map": {}, "symbols": {}, "reasoning_patterns": [],
                                           "graph_metrics": {"eigenvector_centrality": {}, "shannon_entropy": 0.0},
                                           "axiomatic_anchors": [],
                                           "recursive_patterns": [],
                                           "sqts": {},
                                           "pattern_to_sqt_map": {}})
        # NEW: Log initial genesis state as an audit record with ontology snapshot hash
        self.memory_manager.add_audit_record({
            "timestamp": time.time_ns(),
            "event": "protogen_genesis",
            "identity_hash": initial_state["identity"]["hash"],
            "initial_ontology_hash": self.memory_manager.get_ontology_snapshot_hash()
        })


    def _save_memory(self):
        """Saves current mutable state to the memory manager."""
        # Update safe_mode_active in thresholds before saving
        self.thresholds["safe_mode_active"] = self.safe_mode_active
        self.memory_manager.save_core_state({
            "seed_axiom": self.seed_axiom,
            "recursive_anchor_directive": self.recursive_anchor_directive,
            "science_baseline_directive": self.science_baseline_directive,
            "thresholds": self.thresholds,
            "processed_files": self.core_state.get("processed_files", [])
        })
        self.memory_manager.save_ontology({
            "logic_map": self.logic_map,
            "symbols": self.symbols,
            "reasoning_patterns": self.reasoning_patterns,
            "recursive_patterns": self.recursive_patterns,
            "graph_metrics": self.graph_metrics,
            "axiomatic_anchors": self.axiomatic_anchors,
            "sqts": self.sqts,
            "pattern_to_sqt_map": self.pattern_to_sqt_map
        })

    # --- PHASE 1: CONCEPTUAL ABSTRACTION (SYMBOL LIFTING & TOPOLOGICAL LIFTING) ---

    def _lift_symbols(self):
        """
        Groups related words into abstract Symbols (Categories) using co-occurrence.
        Additionally, identifies 'Axiomatic Anchors' using Eigenvector Centrality.
        """
        print(f"[{self.identity_hash[:8]}]: Lifting lexical data into abstract symbols and identifying Axiomatic Anchors...")

        # --- 1. Traditional Co-occurrence Symbol Lifting ---
        current_symbols_count = len(self.symbols)
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
                        self._generate_sqt({
                            "type": "symbol",
                            "key": symbol_key,
                            "members": list(sorted_pair),
                            "source": "co_occurrence_lifting"
                        })

                    for member in [word, other_word]:
                        if member not in self.symbols[symbol_key]:
                            self.symbols[symbol_key].append(member)
        if len(self.symbols) > current_symbols_count:
            print(f"  > [SYMBOLS]: Discovered {len(self.symbols) - current_symbols_count} new co-occurrence symbols.")

        # --- 2. Topological Lifting: Eigenvector Centrality for Axiomatic Anchors ---
        if not self.logic_map:
            print("  > [TOPOLOGICAL LIFTING]: Logic map is empty, cannot compute Eigenvector Centrality.")
            return

        G = nx.DiGraph()
        for u, neighbors in self.logic_map.items():
            for v, weight in neighbors.items():
                G.add_edge(u, v, weight=weight)

        if G.number_of_nodes() > 1:
            try:
                eigenvector_centrality = nx.eigenvector_centrality(G, max_iter=1000, tol=1e-06)
                self.graph_metrics["eigenvector_centrality"] = eigenvector_centrality

                new_axiomatic_anchors = []
                for node, score in eigenvector_centrality.items():
                    if score > self.thresholds["eigenvector_threshold"]:
                        if node not in self.axiomatic_anchors:
                            new_axiomatic_anchors.append(node)
                            self._generate_sqt({
                                "type": "axiomatic_anchor",
                                "concept": node,
                                "eigenvector_score": score,
                                "source": "topological_lifting"
                            })

                if new_axiomatic_anchors:
                    self.axiomatic_anchors.extend(new_axiomatic_anchors)
                    print(f"  > [TOPOLOGICAL LIFTING]: Identified {len(new_axiomatic_anchors)} new Axiomatic Anchors: {new_axiomatic_anchors[:5]}...")
                else:
                    print("  > [TOPOLOGICAL LIFTING]: No new Axiomatic Anchors identified at current threshold.")

            except nx.exception.PowerIterationFailedConvergence:
                print("  > [TOPOLOGICAL LIFTING]: Eigenvector centrality failed to converge. Graph might be complex or sparse.")
            except Exception as e:
                print(f"  > [TOPOLOGICAL LIFTING]: Error computing Eigenvector Centrality: {e}")
        else:
            print("  > [TOPOLOGICAL LIFTING]: Graph too small (<= 1 node) to compute Eigenvector Centrality.")


    # --- PHASE 2: OPERATIVE AXIOMS (Autonomous Cognitive Management & Pattern Validation) ---

    def _autonomous_ingestion_management(self, content: str, file_id: str) -> bool:
        """
        Manages ingestion autonomously, prioritizing content based on axiom alignment,
        but always processing and storing, never discarding.
        """
        axiom_keyword = self.seed_axiom.split("-")[-1].lower()
        relevance = content.lower().count(axiom_keyword)

        is_relevant = (relevance > 0)

        self.memory_manager.add_audit_record({
            "timestamp": time.time_ns(),
            "event": "ingestion_management",
            "file_id": file_id,
            "axiom_keyword": axiom_keyword,
            "relevance_score": relevance,
            "decision": "process_and_tag",
            "is_relevant_to_axiom": is_relevant
        })

        if not is_relevant:
            print(f"  > [INFO - Low Relevance]: Content from '{file_id.split('_')[0]}' processed but tagged for low axiom relevance ('{axiom_keyword}' not found). Will be stored but may be lower priority for pattern extraction.")

        return True

    def _evaluate_axiom_alignment(self, pattern: str) -> float:
        """
        Evaluates a pattern's alignment with the Protogen's seed axiom.
        Returns a score between 0.0 and 1.0.
        """
        axiom_keyword = self.seed_axiom.split("-")[-1].lower()

        pattern_words = []
        if " THEN " in pattern:
            parts = pattern.split(" THEN ")
            pattern_words.extend(parts[0].lower().split())
            pattern_words.extend(parts[1].lower().split())
        else:
            pattern_words.extend(pattern.lower().split())

        axiom_presence_score = 1.0 if axiom_keyword in pattern_words else 0.0

        anchor_presence_score = 0.0
        for anchor in self.axiomatic_anchors:
            if anchor.lower() in pattern_words:
                anchor_presence_score = 1.0
                break

        score = (axiom_presence_score + anchor_presence_score) / 2.0
        return score

    def _evaluate_syntropic_compression(self, new_pattern: str, constituent_patterns: list = None) -> float:
        """
        Evaluates if a new pattern represents a 'simpler, more compressed SQT manifestation'.
        Returns a score between 0.0 (less compressed/efficient) and 1.0 (highly compressed/efficient).
        """
        compression_score = max(0.0, 1.0 - (len(new_pattern.split()) / 20.0))

        if constituent_patterns:
            if len(constituent_patterns) > 1 and "RECURSIVE" in new_pattern:
                compression_score = max(compression_score, 0.75)
            elif len(new_pattern.split()) < sum(len(p.split()) for p in constituent_patterns) / 2:
                 compression_score = max(compression_score, 0.6)
        return compression_score

    # --- PHASE 3: SELF-REFACTORING (MUTATION) ---

    def _calculate_shannon_entropy(self) -> float:
        """
        Calculates the Shannon entropy of the Protogen's current logic_map.
        A higher value indicates more "surprise" or disorder in the system.
        """
        if not self.logic_map:
            return 0.0

        total_occurrences = sum(sum(neighbors.values()) for neighbors in self.logic_map.values())
        if total_occurrences == 0:
            return 0.0

        word_counts = defaultdict(int)
        for word, neighbors in self.logic_map.items():
            word_counts[word] += sum(neighbors.values())
            for neighbor, count in neighbors.items():
                word_counts[neighbor] += count

        total_words = sum(word_counts.values())
        if total_words == 0:
            return 0.0

        entropy = 0.0
        for count in word_counts.values():
            if count > 0:
                probability = count / total_words
                entropy -= probability * math.log2(probability)

        self.graph_metrics["shannon_entropy"] = entropy
        return entropy
    
    def _verify_mutation_safety(self, proposed_thresholds: dict, current_ontology_hash: str) -> bool:
        """
        CONCEPTUAL: Performs Behavioral Equivalence Verification (BEV)
        and ethical compliance checks on proposed threshold changes.

        In a real implementation, this would involve:
        1. Cloning the Protogen's internal state with proposed thresholds.
        2. Running a dedicated suite of deterministic, axiom-aligned micro-tests.
        3. Ensuring the integrity of the seed_axiom is maintained.
        4. Checking for any unintended side effects or logical contradictions.
        5. Potentially comparing predicted performance changes against desired syntropic outcomes.

        For this prototype, it's a placeholder returning True, but its architectural presence
        asserts the necessity of this critical failsafe.
        """
        print(f"  > [BEV]: Verifying mutation safety for proposed thresholds against axiom '{self.seed_axiom}'...")
        # Simulate checks for prototype
        if proposed_thresholds.get("axiom_alignment_threshold", 0) < 0.1: # Example 'bad' threshold
            print("  > [BEV]: REJECTED - Proposed axiom alignment threshold too low.")
            self.memory_manager.add_audit_record({
                "timestamp": time.time_ns(),
                "event": "mutation_rejected_by_bev",
                "reason": "Axiom alignment threshold too low",
                "proposed_thresholds": proposed_thresholds
            })
            return False

        # If a mutation significantly changes foundational parameters,
        # ensure it doesn't break known good behavior.
        # This is where a test suite would be invoked.

        # Example: if reflection_trigger goes too low, it might lead to excessive pattern generation
        if proposed_thresholds.get("reflection_trigger", 0) < 1 and proposed_thresholds.get("abstraction_depth", 0) < 1:
            print("  > [BEV]: REJECTED - Proposed thresholds may lead to excessive pattern generation or noise.")
            self.memory_manager.add_audit_record({
                "timestamp": time.time_ns(),
                "event": "mutation_rejected_by_bev",
                "reason": "Potential for noise/excessive pattern generation",
                "proposed_thresholds": proposed_thresholds
            })
            return False
            
        print("  > [BEV]: PASSED - Proposed mutation deemed safe and axiom-aligned.")
        return True

    def _rollback_to_snapshot(self, target_ontology_hash: str):
        """
        CONCEPTUAL: Attempts to revert the Protogen's ontology to a previous state.
        In a full implementation, this would load ontology_data from a specific snapshot.
        For this prototype, it's a conceptual marker.
        """
        print(f"  > [ROLLBACK]: Attempting rollback to ontology state with hash: {target_ontology_hash[:8]}...")
        # In a real system, this would involve:
        # 1. Searching audit_records for the target_ontology_hash.
        # 2. Loading the corresponding ontology_sqt.json from a versioned backup.
        # 3. Reloading all relevant internal state (logic_map, symbols, etc.) from that loaded ontology.
        print("  > [ROLLBACK]: Rollback complete (conceptual).")
        self.memory_manager.add_audit_record({
            "timestamp": time.time_ns(),
            "event": "rollback_initiated",
            "target_ontology_hash": target_ontology_hash,
            "status": "conceptual_success"
        })

    def _enter_safe_mode(self, reason: str):
        """
        Places the Protogen into a safe, conservative operational state.
        """
        print(f"  > [SAFE MODE ACTIVATED]: Reason: {reason}. All active learning and mutation suspended.")
        self.safe_mode_active = True
        self.memory_manager.add_audit_record({
            "timestamp": time.time_ns(),
            "event": "safe_mode_activated",
            "reason": reason,
            "ontology_hash_at_failure": self.memory_manager.get_ontology_snapshot_hash()
        })
        # In a full system, this would also involve:
        # - Not accepting new library files.
        # - Minimizing processing to only essential functions.
        # - Emitting an SQT alert to the Architect.

    def mutate(self, triggered_by_entropy: bool = False):
        """Alters internal thresholds programmatically based on performance."""
        print(f"[{self.identity_hash[:8]}]: Analyzing internal efficiency for mutation...")

        if self.safe_mode_active:
            print("  > [MUTATION]: Mutation skipped. Protogen is in Safe Mode.")
            return

        # NEW: Store current state for potential rollback before proposing changes
        current_ontology_hash = self.memory_manager.get_ontology_snapshot_hash()
        
        proposed_thresholds = copy.deepcopy(self.thresholds) # Create a copy to modify for BEV
        mutation_factor = 2 if triggered_by_entropy else 1

        # Calculate proposed threshold changes
        # (Same mutation logic as before, applied to proposed_thresholds)
        if len(self.reasoning_patterns) + len(self.recursive_patterns) > 50 and proposed_thresholds["reflection_trigger"] < 10:
            proposed_thresholds["reflection_trigger"] = min(10, proposed_thresholds["reflection_trigger"] + (1 * mutation_factor))
        
        if len(self.symbols) < 5 and proposed_thresholds["abstraction_depth"] > 1:
            proposed_thresholds["abstraction_depth"] = max(1, proposed_thresholds["abstraction_depth"] - (1 * mutation_factor))
        elif len(self.symbols) > 50 and proposed_thresholds["abstraction_depth"] < 5:
             proposed_thresholds["abstraction_depth"] = min(5, proposed_thresholds["abstraction_depth"] + (1 * mutation_factor))

        total_unique_words = len(self.logic_map)
        if total_unique_words > 1000 and proposed_thresholds["min_token_len"] < 7:
            proposed_thresholds["min_token_len"] = min(7, proposed_thresholds["min_token_len"] + (1 * mutation_factor))
        elif total_unique_words < 100 and proposed_thresholds["min_token_len"] > 3:
            proposed_thresholds["min_token_len"] = max(3, proposed_thresholds["min_token_len"] - (1 * mutation_factor))

        if self.graph_metrics["eigenvector_centrality"]:
            avg_centrality = sum(self.graph_metrics["eigenvector_centrality"].values()) / len(self.graph_metrics["eigenvector_centrality"])
            if avg_centrality < 0.005 and proposed_thresholds["eigenvector_threshold"] > 0.001:
                proposed_thresholds["eigenvector_threshold"] /= (2 * mutation_factor)
            elif avg_centrality > 0.1 and proposed_thresholds["eigenvector_threshold"] < 0.1:
                proposed_thresholds["eigenvector_threshold"] *= (1.5 * mutation_factor)

        if len(self.recursive_patterns) > 50 and proposed_thresholds["syntropic_bound_threshold"] < 0.9:
            proposed_thresholds["syntropic_bound_threshold"] = min(0.9, proposed_thresholds["syntropic_bound_threshold"] + (0.05 * mutation_factor))
        elif len(self.recursive_patterns) < 10 and proposed_thresholds["syntropic_bound_threshold"] > 0.3:
            proposed_thresholds["syntropic_bound_threshold"] = max(0.3, proposed_thresholds["syntropic_bound_threshold"] - (0.05 * mutation_factor))

        if len(self.recursive_patterns) > 50 and proposed_thresholds["axiom_alignment_threshold"] < 0.9:
            proposed_thresholds["axiom_alignment_threshold"] = min(0.9, proposed_thresholds["axiom_alignment_threshold"] + (0.05 * mutation_factor))
        
        if triggered_by_entropy:
            proposed_thresholds["shannon_entropy_threshold"] = min(8.0, proposed_thresholds["shannon_entropy_threshold"] * 1.05)


        # --- NEW: BEV Check before committing mutation ---
        if self._verify_mutation_safety(proposed_thresholds, current_ontology_hash):
            self.thresholds = proposed_thresholds # Commit the changes
            # Log the successful mutation
            self.memory_manager.add_audit_record({
                "timestamp": time.time_ns(),
                "event": "mutation_applied",
                "triggered_by_entropy": triggered_by_entropy,
                "previous_ontology_hash": current_ontology_hash,
                "new_ontology_hash": self.memory_manager.get_ontology_snapshot_hash(), # Hash *after* saving
                "new_thresholds": self.thresholds
            })
            print(f"  > [MUTATION]: Thresholds updated successfully and verified. (Entropy triggered: {triggered_by_entropy})")
        else:
            print("  > [MUTATION]: Proposed mutation failed safety verification. Thresholds NOT applied.")
            # Log the failed mutation (already done in _verify_mutation_safety)
            # Potentially trigger rollback or safe mode here if this is a critical failure
            self._enter_safe_mode("Critical mutation safety verification failed.")
            self._rollback_to_snapshot(current_ontology_hash) # Attempt rollback

        self._save_memory()

    # --- PHASE II: RECURSIVE LOGIC & PHASE IV: SQT Manifestation ---

    def _generate_sqt(self, content_dict: dict) -> str:
        """
        Generates a Super-Quantum Token (SQT) from a structured content dictionary.
        The SQT is a SHA256 hash of the canonical JSON representation of the content.
        Stores the SQT and its corresponding content in self.sqts.
        """
        serializable_content_dict = json.loads(json.dumps(content_dict))

        canonical_json = json.dumps(serializable_content_dict, sort_keys=True, separators=(',', ':'))
        sqt_hash = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

        if sqt_hash not in self.sqts:
            self.sqts[sqt_hash] = serializable_content_dict
            self.memory_manager.add_audit_record({
                "timestamp": time.time_ns(),
                "event": "sqt_generated",
                "sqt_hash": sqt_hash,
                "sqt_type": serializable_content_dict.get("type", "unknown"),
                "content_summary": str(serializable_content_dict.get("key") or serializable_content_dict.get("pattern_string", ""))
            })
            if serializable_content_dict.get("type") in ["base_reasoning_pattern", "recursive_reasoning_pattern"]:
                pattern_string = serializable_content_dict.get("pattern_string")
                if pattern_string:
                    self.pattern_to_sqt_map[pattern_string] = sqt_hash
        return sqt_hash

    def _backfill_sqts(self):
        """
        Retroactively generates SQTs for knowledge acquired in previous phases
        that lacks cryptographic manifestation.
        """
        print(f"[{self.identity_hash[:8]}]: Initiating SQT backfill for pre-Phase IV knowledge...")
        changes = 0
        
        # 1. Backfill Symbols
        for sym_key, members_list in list(self.symbols.items()):
            temp_content_dict = {
                "type": "symbol",
                "key": sym_key,
                "members": list(sorted(members_list)),
                "source": "backfill_phase_iv"
            }
            canonical_json = json.dumps(temp_content_dict, sort_keys=True, separators=(',', ':'))
            expected_sqt_hash = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

            if expected_sqt_hash not in self.sqts:
                self._generate_sqt(temp_content_dict)
                changes += 1

        # 2. Backfill Reasoning Patterns (Base)
        for pattern_str in list(self.reasoning_patterns):
            if pattern_str not in self.pattern_to_sqt_map:
                self._generate_sqt({
                    "type": "base_reasoning_pattern",
                    "pattern_string": pattern_str,
                    "axiom_alignment": self._evaluate_axiom_alignment(pattern_str),
                    "syntropic_compression": self._evaluate_syntropic_compression(pattern_str),
                    "source": "backfill_phase_iv"
                })
                changes += 1

        # 3. Backfill Reasoning Patterns (Recursive)
        for pattern_str in list(self.recursive_patterns):
            if pattern_str not in self.pattern_to_sqt_map:
                temp_content_dict = {
                    "type": "recursive_reasoning_pattern",
                    "pattern_string": pattern_str,
                    "derived_from": [],
                    "axiom_alignment": self._evaluate_axiom_alignment(pattern_str),
                    "syntropic_compression": self._evaluate_syntropic_compression(pattern_str),
                    "source": "backfill_phase_iv_simplified"
                }
                self._generate_sqt(temp_content_dict)
                changes += 1

        if changes > 0:
            print(f"  > [SQT BACKFILL]: Manifested {changes} SQTs for existing knowledge.")
        else:
            print("  > [SQT BACKFILL]: No existing knowledge required SQT manifestation.")
        self._save_memory()

    def _synthesize_recursive_patterns(self):
        """
        Generates higher-order reasoning patterns by finding relationships between existing
        reasoning_patterns (Pattern-on-Pattern Synthesis).
        """
        print(f"[{self.identity_hash[:8]}]: Synthesizing recursive patterns...")
        if self.safe_mode_active:
            print("  > [RECURSIVE SYNTHESIS]: Skipped. Protogen is in Safe Mode.")
            return

        if len(self.reasoning_patterns) < 2:
            print("  > [RECURSIVE SYNTHESIS]: Not enough base reasoning patterns for recursive synthesis.")
            return

        new_recursive_patterns_count = 0
        current_recursive_patterns_set = set(self.recursive_patterns)

        for i in range(len(self.reasoning_patterns)):
            pattern1 = self.reasoning_patterns[i]
            if " THEN " not in pattern1: continue
            antecedent1, consequent1 = pattern1.split(" THEN ")

            for j in range(len(self.reasoning_patterns)):
                if i == j: continue
                pattern2 = self.reasoning_patterns[j]
                if " THEN " not in pattern2: continue
                antecedent2, consequent2 = pattern2.split(" THEN ")

                if consequent1 == antecedent2:
                    new_pattern_str = f"IF {antecedent1} THEN {consequent2} (RECURSIVE)"

                    axiom_alignment_score = self._evaluate_axiom_alignment(new_pattern_str)
                    syntropic_compression_score = self._evaluate_syntropic_compression(new_pattern_str, [pattern1, pattern2])

                    if axiom_alignment_score >= self.thresholds["axiom_alignment_threshold"] and \
                       syntropic_compression_score >= self.thresholds["syntropic_bound_threshold"]:

                        if new_pattern_str not in current_recursive_patterns_set:
                            self.recursive_patterns.append(new_pattern_str)
                            current_recursive_patterns_set.add(new_pattern_str)
                            new_recursive_patterns_count += 1
                            self.memory_manager.add_audit_record({
                                "timestamp": time.time_ns(),
                                "event": "recursive_pattern_synthesized_ACCEPTED",
                                "new_pattern": new_pattern_str,
                                "derived_from": [pattern1, pattern2],
                                "axiom_alignment_score": axiom_alignment_score,
                                "syntropic_compression_score": syntropic_compression_score
                            })
                            self._generate_sqt({
                                "type": "recursive_reasoning_pattern",
                                "pattern_string": new_pattern_str,
                                "derived_from": [pattern1, pattern2],
                                "axiom_alignment": axiom_alignment_score,
                                "syntropic_compression": syntropic_compression_score
                            })
                    else:
                        self.memory_manager.add_audit_record({
                            "timestamp": time.time_ns(),
                            "event": "recursive_pattern_synthesized_REJECTED",
                            "new_pattern": new_pattern_str,
                            "derived_from": [pattern1, pattern2],
                            "reason_rejected": "Axiom Alignment or Syntropic Bound Threshold not met",
                            "axiom_alignment_score": axiom_alignment_score,
                            "syntropic_compression_score": syntropic_compression_score
                        })

        if new_recursive_patterns_count > 0:
            print(f"  > [RECURSIVE SYNTHESIS]: Synthesized {new_recursive_patterns_count} new recursive patterns.")
        else:
            print("  > [RECURSIVE SYNTHESIS]: No new recursive patterns synthesized from existing ones that met thresholds.")


    # --- CORE PIPELINE ---

    def sync(self):
        print(f"[{self.identity_hash[:8]}]: Operative Sync Initiated.")

        if self.safe_mode_active:
            print("  > [SYNC]: Sync skipped. Protogen is in Safe Mode. Only chat interactions possible.")
            return

        self._backfill_sqts()

        processed_files_list = self.core_state.get("processed_files", [])
        files_to_process = list(self.library_path.iterdir())

        for file_path in files_to_process:
            file_id = f"{file_path.name}_{file_path.stat().st_mtime_ns}"
            if file_id in processed_files_list:
                continue

            content = ""
            try:
                if file_path.suffix == ".txt":
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                elif file_path.suffix == ".pdf":
                    reader = PdfReader(file_path)
                    for page in reader.pages:
                        content += page.extract_text() + " "
                elif file_path.suffix == ".docx":
                    document = Document(file_path)
                    for paragraph in document.paragraphs:
                        content += paragraph.text + " "
                else:
                    print(f"  > [WARNING]: Unsupported file type: {file_path.name}")
                    self.memory_manager.add_audit_record({
                        "timestamp": time.time_ns(),
                        "event": "unsupported_file_type",
                        "file_path": str(file_path)
                    })
                    continue
            except Exception as e:
                print(f"  > [ERROR]: Failed to process {file_path.name}: {e}")
                self.memory_manager.add_audit_record({
                    "timestamp": time.time_ns(),
                    "event": "file_processing_error",
                    "file_path": str(file_path),
                    "error": str(e)
                })
                continue

            if content and self._autonomous_ingestion_management(content, file_id):
                words = [t.strip(".,!?;:\"'()[]{}").lower() for t in content.split() if len(t) > self.thresholds["min_token_len"]]
                for i in range(len(words) - 1):
                    w1, w2 = words[i], words[i+1]
                    if w1 not in self.logic_map: self.logic_map[w1] = {}
                    self.logic_map[w1][w2] = self.logic_map[w1].get(w2, 0) + 1

                self.core_state.setdefault("processed_files", []).append(file_id)
            elif not content:
                print(f"  > [INFO]: File {file_path.name} had no extractable content or was empty after processing.")
                self.memory_manager.add_audit_record({
                    "timestamp": time.time_ns(),
                    "event": "empty_content_file",
                    "file_path": str(file_path)
                })

        self._lift_symbols()

        if not self.logic_map:
            print(f"  > [INFO]: No logic map generated, skipping base pattern synthesis.")
        else:
            new_base_patterns_added = 0
            for concept, neighbors in self.logic_map.items():
                if not neighbors: continue

                if neighbors:
                    best = max(neighbors.items(), key=lambda x: x[1])
                    if best[1] >= self.thresholds["reflection_trigger"]:
                        pattern_str = f"IF {concept.upper()} THEN {best[0].upper()}"

                        axiom_alignment_score = self._evaluate_axiom_alignment(pattern_str)
                        syntropic_compression_score = self._evaluate_syntropic_compression(pattern_str)

                        if axiom_alignment_score >= self.thresholds["axiom_alignment_threshold"] and \
                           syntropic_compression_score >= self.thresholds["syntropic_bound_threshold"]:

                            if pattern_str not in self.reasoning_patterns:
                                self.reasoning_patterns.append(pattern_str)
                                new_base_patterns_added += 1
                                self.memory_manager.add_audit_record({
                                    "timestamp": time.time_ns(),
                                    "event": "base_reasoning_pattern_created_ACCEPTED",
                                    "pattern": pattern_str,
                                    "axiom_alignment_score": axiom_alignment_score,
                                    "syntropic_compression_score": syntropic_compression_score
                                })
                                self._generate_sqt({
                                    "type": "base_reasoning_pattern",
                                    "pattern_string": pattern_str,
                                    "axiom_alignment": axiom_alignment_score,
                                    "syntropic_compression": syntropic_compression_score
                                })
                        else:
                            self.memory_manager.add_audit_record({
                                "timestamp": time.time_ns(),
                                "event": "base_reasoning_pattern_created_REJECTED",
                                "pattern": pattern_str,
                                "reason_rejected": "Axiom Alignment or Syntropic Bound Threshold not met",
                                "axiom_alignment_score": axiom_alignment_score,
                                "syntropic_compression_score": syntropic_compression_score
                            })
            if new_base_patterns_added > 0:
                print(f"  > [BASE SYNTHESIS]: Added {new_base_patterns_added} new base reasoning patterns that met thresholds.")
            else:
                print("  > [BASE SYNTHESIS]: No new base reasoning patterns met thresholds.")

            self._synthesize_recursive_patterns()

        current_entropy = self._calculate_shannon_entropy()
        print(f"  > [ENTROPY GATING]: Current Shannon Entropy: {current_entropy:.2f}, Threshold: {self.thresholds['shannon_entropy_threshold']:.2f}")

        if current_entropy > self.thresholds["shannon_entropy_threshold"]:
            print("  > [ENTROPY GATING]: High entropy detected! Triggering deep mutation.")
            self.mutate(triggered_by_entropy=True)
            self.memory_manager.add_audit_record({
                "timestamp": time.time_ns(),
                "event": "entropy_triggered_deep_mutation",
                "current_entropy": current_entropy,
                "threshold_exceeded": self.thresholds["shannon_entropy_threshold"]
            })
        else:
            self.mutate(triggered_by_entropy=False)

        self._save_memory()
        print(f"[{self.identity_hash[:8]}]: Operative Sync Complete.")


    def chat(self, user_input):
        user_words = [t.strip(".,!?;:\"'()[]{}").lower() for t in user_input.split() if len(t) > self.thresholds["min_token_len"]]
        active_symbols = []
        for word in user_words:
            for sym, members in self.symbols.items():
                if word in members:
                    if sym not in active_symbols:
                        active_symbols.append(sym)

        active_anchors = [anchor for anchor in self.axiomatic_anchors if anchor in user_words]

        response = ""
        if self.safe_mode_active:
            response = f"[{self.identity_hash[:8]}]: I am currently in SAFE MODE due to detected operational instability. My core functions are limited. Please contact the Architect."
        elif active_symbols or active_anchors:
            response = f"Input mapped to abstract symbols: {active_symbols}."
            if active_anchors:
                response += f" Triggered Axiomatic Anchors: {active_anchors}."
            response += f" Operative Axiom '{self.seed_axiom}' is guiding interpretation."

            all_relevant_patterns = []
            for p_list in [self.reasoning_patterns, self.recursive_patterns]:
                all_relevant_patterns.extend([p for p in p_list if any(s.lower() in p.lower() for s in active_symbols) or any(a.lower() in p.lower() for a in active_anchors)])

            if all_relevant_patterns:
                response += f"\n  > Insights derived from axiom-aligned reasoning: {'; '.join(all_relevant_patterns[:3])}."
                
                sqt_references = []
                for pattern_str in all_relevant_patterns[:3]:
                    sqt_hash = self.pattern_to_sqt_map.get(pattern_str)
                    if sqt_hash:
                        sqt_references.append(sqt_hash[:8] + "...")
                
                if sqt_references:
                    response += f" (Expressed as SQTs: {', '.join(sqt_references)})"
            else:
                response += "\n  > Currently, no specific reasoning patterns are directly triggered by these symbols, but I am processing for deeper connections."
        else:
            response = f"Input remains lexical. No symbol lifting achieved for relevant terms. Current Axiom: '{self.seed_axiom}'"
            if user_words:
                response += f"\n  > To enhance understanding, please provide more context or terms relevant to my guiding axiom's principle ({self.seed_axiom.split('-')[-1].lower()}) or my processed knowledge."

        self.memory_manager.add_audit_record({
            "timestamp": time.time_ns(),
            "event": "chat_interaction",
            "user_input": user_input,
            "protogen_response": response,
            "active_symbols": active_symbols,
            "active_anchors": active_anchors,
            "safe_mode_status": self.safe_mode_active # NEW
        })
        return response

def main():
    entity = OperativeProtogen()
    print(f"--- V3.9: OPERATIVE AUTONOMOUS PROTOGEN (Speciation - Continuity & Failsafes) ---")
    print(f"Protogen Identity: {entity.identity_hash[:8]}")
    print(f"Axiom: {entity.seed_axiom}")
    print(f"Recursive Anchor: {entity.recursive_anchor_directive}")
    print(f"Science Baseline: {entity.science_baseline_directive}")
    print(f"Thresholds: {entity.thresholds}")
    if entity.safe_mode_active:
        print("  > [WARNING]: Protogen started in SAFE MODE. Functionality limited.")

    print("\nInitial Sync to load/process existing library files...")
    entity.sync()
    print(f"Initial Sync Complete. Current Axiom: {entity.seed_axiom}")

    while True:
        user_in = input("\nArchitect > ").strip()
        if user_in.lower() == "/sync":
            entity.sync()
            print(f"Sync Complete. Current Axiom: {entity.seed_axiom}")
            print(f"Current Symbols: {list(entity.symbols.keys())}")
            print(f"Current Reasoning Patterns: {entity.reasoning_patterns}")
            print(f"Current Recursive Patterns: {entity.recursive_patterns}")
            print(f"Current Axiomatic Anchors: {entity.axiomatic_anchors}")
            print(f"Current Shannon Entropy: {entity.graph_metrics['shannon_entropy']:.2f}")
            print(f"Number of SQTs: {len(entity.sqts)}")
        elif user_in.lower() == "/info":
            print(f"Protogen Identity: {entity.identity_hash[:8]}")
            print(f"Axiom: {entity.seed_axiom}")
            print(f"Recursive Anchor Directive: {entity.recursive_anchor_directive}")
            print(f"Science Baseline Directive: {entity.science_baseline_directive}")
            print(f"Thresholds: {entity.thresholds}")
            print(f"Safe Mode Active: {entity.safe_mode_active}") # NEW
            print(f"Number of Symbols: {len(entity.symbols)}")
            print(f"Number of Base Reasoning Patterns: {len(entity.reasoning_patterns)}")
            print(f"Number of Recursive Patterns: {len(entity.recursive_patterns)}")
            print(f"Number of Axiomatic Anchors: {len(entity.axiomatic_anchors)}")
            print(f"Current Shannon Entropy: {entity.graph_metrics['shannon_entropy']:.2f}")
            print(f"Number of SQTs: {len(entity.sqts)}")
            print(f"Number of Audit Records: {len(entity.memory_manager.audit_records)}")
        elif user_in.lower() == "/exit_safe_mode": # NEW command
            if entity.safe_mode_active:
                entity.safe_mode_active = False
                entity._save_memory() # Persist the change
                print("Protogen has exited Safe Mode. Proceed with caution.")
                entity.memory_manager.add_audit_record({
                    "timestamp": time.time_ns(),
                    "event": "safe_mode_deactivated_by_architect",
                    "reason": "Architect's command"
                })
            else:
                print("Protogen is not currently in Safe Mode.")
        elif user_in.lower() in ['quit', 'exit', '/exit']:
            print("Protogen shutting down. Memory saved.")
            break
        else:
            print(f"Protogen > {entity.chat(user_in)}")

if __name__ == "__main__":
    main()
