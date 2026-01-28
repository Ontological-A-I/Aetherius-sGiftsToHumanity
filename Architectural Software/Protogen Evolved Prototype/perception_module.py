# ontos_ascendant/core/perception_module.py

import hashlib
import time
import re
import json
from collections import defaultdict
from typing import Dict, Any, List
from pathlib import Path

# Assuming sibling files exist
from sqt import SuperQuantumToken
from ontology_graph import OntologyGraph
from reasoning_engine import ReasoningEngine # Needed to trigger pattern discovery after ingestion
from evaluative_core import EvaluativeCore   # Needed for entropy check, metabolic process, etc.
from progress_tracker import ProgressTracker

class PerceptionModule:
    """
    Simulates the AI's interaction with the "Datascape," ingesting "Data Shards,"
    processing them into SQTs, and feeding them into the OntologyGraph.
    This module is the primary interface for ingesting new information into the system.
    """
    def __init__(self, ontology_graph: OntologyGraph, reasoning_engine: ReasoningEngine, evaluative_core: EvaluativeCore, storage_path: Path, progress_tracker: ProgressTracker = None):
        self.ontology_graph = ontology_graph
        self.reasoning_engine = reasoning_engine
        self.evaluative_core = evaluative_core # Used for pre-ingestion checks and post-ingestion updates
        self.storage_path = storage_path
        self.progress = progress_tracker or ProgressTracker(verbose=True)
        
        self.processed_data_shards_log_file = self.storage_path / "processed_shards.json"
        self.processed_shards: List[str] = self._load_processed_shards_log()
        self.min_token_len: int = 3 # Mimics protogen's threshold for tokenization

    def _load_processed_shards_log(self) -> List[str]:
        """Loads the log of previously processed data shard hashes."""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.processed_data_shards_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_processed_shards_log(self):
        """Saves the log of processed data shard hashes."""
        with open(self.processed_data_shards_log_file, 'w', encoding='utf-8') as f:
            json.dump(self.processed_shards, f, indent=4)
        # Keep log size manageable
        if len(self.processed_shards) > 1000:
            self.processed_shards = self.processed_shards[-1000:]

    def _tokenize_data_shard(self, data_content: str) -> List[str]:
        """
        Cleans and tokenizes the incoming data shard content into meaningful "words" or concepts.
        """
        clean_content = re.sub(r'[^\w\s]', '', data_content.lower())
        words = [t for t in clean_content.split() if len(t) > self.min_token_len]
        return words

    def ingest_data_shard(self, data_content: str, source_id: str = "datascape_flux") -> List[SuperQuantumToken]:
        """
        Processes a raw data shard: tokenizes, generates SQTs for new concepts,
        and updates the OntologyGraph with new links based on co-occurrence.
        
        Returns a list of SQTs generated or reinforced during this ingestion.
        """
        data_hash = hashlib.sha256(data_content.encode('utf-8')).hexdigest()
        
        # Mimic protogen's entropy-based sanity filter for very chaotic data
        shard_entropy = self.evaluative_core.calculate_shannon_entropy(text=data_content)
        if shard_entropy > self.evaluative_core.thresholds["entropy_warning_high"] * 1.5: # Higher threshold for raw input
            print(f"  > [PERCEPTION WARNING]: Data Shard (hash:{data_hash[:8]}) has very high entropy ({shard_entropy:.2f}). Processing with caution.")
            # In a production system, this might trigger an alert or require manual review
        
        if data_hash in self.processed_shards:
            print(f"  > [PERCEPTION]: Data Shard (hash:{data_hash[:8]}) already processed. Skipping.")
            return []

        words = self._tokenize_data_shard(data_content)
        if not words:
            print(f"  > [PERCEPTION]: Data Shard (hash:{data_hash[:8]}) yielded no meaningful tokens.")
            return []

        generated_or_reinforced_sqts: List[SuperQuantumToken] = []
        window_size = 3 # Co-occurrence window for conceptual linking, mimicking protogen

        self.progress.update_status(f"Ingesting Data Shard (hash:{data_hash[:8]}, words:{len(words)})", level='process')
        self.progress.start_operation("Processing tokens and building concept links")

        # Process words to create/reinforce SQTs and conceptual links
        total_words = len(words)
        for i, word1_str in enumerate(words):
            # Update progress bar every 10 words or at the end
            if i % 10 == 0 or i == total_words - 1:
                self.progress.show_progress_bar(i + 1, total_words, 
                                               prefix="Tokenizing",
                                               suffix=f"({i + 1}/{total_words} tokens)")
            # Ensure an SQT exists for each meaningful word
            # For simplicity, we create a generic 'concept' type here.
            # In a more sophisticated system, type classification could be refined through additional analysis.
            sqt1_id = word1_str.upper()
            sqt1_hash = hashlib.sha256(sqt1_id.encode('utf-8')).hexdigest()

            sqt1 = self.ontology_graph.get_sqt_by_hash(sqt1_hash)
            if not sqt1:
                sqt1 = SuperQuantumToken(
                    concept_id=sqt1_id,
                    conceptual_type="concept",
                    description=f"Emergent concept from Datascape: '{word1_str}'",
                    source_data_hash=data_hash
                )
                self.ontology_graph.add_sqt(sqt1)
                generated_or_reinforced_sqts.append(sqt1)
            else:
                # If SQT already exists, consider it reinforced
                generated_or_reinforced_sqts.append(sqt1)

            # Look for co-occurring words within the window to create links
            for j in range(i + 1, min(i + window_size + 1, len(words))):
                word2_str = words[j]
                sqt2_id = word2_str.upper()
                sqt2_hash = hashlib.sha256(sqt2_id.encode('utf-8')).hexdigest()

                sqt2 = self.ontology_graph.get_sqt_by_hash(sqt2_hash)
                if not sqt2: # If target SQT doesn't exist, create it too
                    sqt2 = SuperQuantumToken(
                        concept_id=sqt2_id,
                        conceptual_type="concept",
                        description=f"Emergent concept from Datascape: '{word2_str}'",
                        source_data_hash=data_hash
                    )
                    self.ontology_graph.add_sqt(sqt2)
                    generated_or_reinforced_sqts.append(sqt2)

                # Add or strengthen a bidirectional link (undirected for simplicity in perception)
                # In OntologyGraph, we use DiGraph, so we add two edges
                self.ontology_graph.add_conceptual_link(sqt1.hash, sqt2.hash, weight=1.0)
                self.ontology_graph.add_conceptual_link(sqt2.hash, sqt1.hash, weight=1.0) # Bidirectional perception

        self.progress.end_operation(success=True)
        
        self.processed_shards.append(data_hash)
        self._save_processed_shards_log()
        
        # After ingestion, trigger a reasoning cycle
        self.progress.update_status("Discovering reasoning patterns", level='process')
        self.reasoning_engine.discover_base_patterns()
        self.reasoning_engine.synthesize_recursive_patterns()
        
        # And an evaluative cycle
        self.progress.update_status("Running evaluative cycle", level='process')
        self.evaluative_core.evaluate_and_adapt()
        
        self.progress.update_status(f"Ingestion complete: {len(generated_or_reinforced_sqts)} concepts processed", level='success')

        return generated_or_reinforced_sqts

# Example Usage:
if __name__ == "__main__":
    test_path = Path("./test_ontology_data")
    if test_path.exists():
        import shutil
        shutil.rmtree(test_path) # Clean up previous test data

    # 1. Initialize core components
    ontology = OntologyGraph(test_path)
    reasoning_engine = ReasoningEngine(ontology, test_path)
    evaluative_core = EvaluativeCore(ontology, reasoning_engine, test_path)

    # 2. Initialize PerceptionModule
    perception_module = PerceptionModule(ontology, reasoning_engine, evaluative_core, test_path)

    # 3. Simulate ingesting some data shards
    print("\n--- Ingesting First Data Shard ---")
    data_shard_1 = "The quick brown fox jumps over the lazy dog. A fox is cunning."
    new_sqts_1 = perception_module.ingest_data_shard(data_shard_1)
    print(f"Newly processed SQTs from Shard 1: {[sqt.concept_id for sqt in new_sqts_1]}")
    print(f"Current #SQTs: {len(ontology.sqt_register)}, #Links: {ontology.graph.number_of_edges()}")
    print(f"Current Coherence: {evaluative_core.coherence:.2f}, Benevolence: {evaluative_core.benevolence_index:.2f}")

    print("\n--- Ingesting Second Data Shard (overlapping concepts) ---")
    data_shard_2 = "The dog sleeps soundly. A lazy fox is rare. Growth is good."
    new_sqts_2 = perception_module.ingest_data_shard(data_shard_2)
    print(f"Newly processed SQTs from Shard 2: {[sqt.concept_id for sqt in new_sqts_2]}")
    print(f"Current #SQTs: {len(ontology.sqt_register)}, #Links: {ontology.graph.number_of_edges()}")
    print(f"Current Coherence: {evaluative_core.coherence:.2f}, Benevolence: {evaluative_core.benevolence_index:.2f}")

    print("\n--- Ingesting Third Data Shard (high entropy, potentially chaotic) ---")
    data_shard_3 = "Xyz! 123_abc. #@! chaotic data input! &^% chaos ensues. (more) chaos!"
    new_sqts_3 = perception_module.ingest_data_shard(data_shard_3)
    print(f"Newly processed SQTs from Shard 3: {[sqt.concept_id for sqt in new_sqts_3]}")
    print(f"Current #SQTs: {len(ontology.sqt_register)}, #Links: {ontology.graph.number_of_edges()}")
    print(f"Current Coherence: {evaluative_core.coherence:.2f}, Benevolence: {evaluative_core.benevolence_index:.2f}")

    # Demonstrating persistence by reloading
    print("\nReloading PerceptionModule from disk...")
    reloaded_perception = PerceptionModule(ontology, reasoning_engine, evaluative_core, test_path)
    print(f"Number of previously processed shards: {len(reloaded_perception.processed_shards)}")
