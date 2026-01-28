import sys
from pathlib import Path

# Add the current directory and core directory to sys.path to allow imports
base_path = Path(__file__).parent
sys.path.append(str(base_path))
sys.path.append(str(base_path / "core"))

from protogen import OperativeProtogen

def verify():
    print("--- STARTING SYSTEM VERIFICATION ---")
    
    # 1. Initialize the Protogen
    # Use a temporary directory for verification
    verify_root = Path("./verify_protogen_core")
    if verify_root.exists():
        import shutil
        shutil.rmtree(verify_root)
        
    try:
        protogen = OperativeProtogen(root_dir=str(verify_root))
        print(f"[SUCCESS] Protogen Initialized. Accelerator: {protogen.accelerator.device_name}")
    except Exception as e:
        print(f"[FAILURE] Protogen Initialization failed: {e}")
        return

    # 2. Test Ingestion
    try:
        print("\n[TEST] Ingesting Data Shard 1...")
        data_shard_1 = "The quick brown fox jumps over the lazy dog. A fox is cunning and fast."
        protogen.ingest_data(data_shard_1)
        print("[SUCCESS] Data Shard 1 ingested.")
    except Exception as e:
        print(f"[FAILURE] Ingestion 1 failed: {e}")
        import traceback
        traceback.print_exc()

    try:
        print("\n[TEST] Ingesting Data Shard 2...")
        data_shard_2 = "The dog sleeps soundly. A lazy fox is rare. Growth is good and fast."
        protogen.ingest_data(data_shard_2)
        print("[SUCCESS] Data Shard 2 ingested.")
    except Exception as e:
        print(f"[FAILURE] Ingestion 2 failed: {e}")

    # 3. Test Metabolic Cycle
    try:
        print("\n[TEST] Running Metabolic Cycle...")
        protogen.run_metabolic_cycle()
        print("[SUCCESS] Metabolic Cycle completed.")
    except Exception as e:
        print(f"[FAILURE] Metabolic Cycle failed: {e}")

    # 4. Verify Final State
    print("\n--- FINAL STATE SUMMARY ---")
    print(f"Axiomatic Anchors: {protogen.axiomatic_anchors}")
    print(f"Base Reasoning Patterns: {list(protogen.reasoning_engine.base_patterns.values())}")
    print(f"Recursive Reasoning Patterns: {list(protogen.reasoning_engine.recursive_patterns.values())}")
    print(f"Coherence (Entropy): {protogen.evaluative_core.coherence:.4f}")
    print(f"Benevolence Index: {protogen.evaluative_core.benevolence_index:.4f}")
    
    print("\n--- SYSTEM VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    verify()
