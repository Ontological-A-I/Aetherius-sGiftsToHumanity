"""
Unified System Initialization v3 - Integrated
Handles startup for Protogen + SRIM + QualiaManager + SQT Network
with full bidirectional connections
"""

import os
import sys
from pathlib import Path

def initialize_protogen_system(base_dir=None):
    """
    Initialize the complete Protogen system with bidirectional integration.
    
    Args:
        base_dir: Base directory for all system data. If None, uses current working directory.
    
    Returns:
        dict: {
            'protogen': OperativeProtogen instance,
            'srim': SRIMLocal instance,
            'qualia': QualiaManager instance,
            'sqt_network': DynamicSQTNetwork instance,
            'base_dir': Absolute path to base directory
        }
    """
    
    # Determine base directory (Kaggle-aware)
    if base_dir is None:
        base_dir = os.getcwd()
    else:
        base_dir = os.path.abspath(base_dir)
    
    print(f"\n{'='*80}")
    print(f"PROTOGEN SYSTEM V3 - INTEGRATED INITIALIZATION")
    print(f"Base Directory: {base_dir}")
    print(f"{'='*80}\n")
    
    # Import here to avoid circular imports
    from protogen_v3_integrated import OperativeProtogen
    from srim_local_v2 import SRIMLocal
    from qualia_manager_v3_integrated import QualiaManager
    from sqt_neural_network_v3_integrated import DynamicSQTNetwork
    
    # Create subdirectories
    protogen_root = os.path.join(base_dir, "protogen_core")
    srim_root = os.path.join(base_dir, "srim_core")
    qualia_root = os.path.join(base_dir, "qualia_core")
    temp_root = os.path.join(base_dir, "temp")
    
    Path(protogen_root).mkdir(parents=True, exist_ok=True)
    Path(srim_root).mkdir(parents=True, exist_ok=True)
    Path(qualia_root).mkdir(parents=True, exist_ok=True)
    Path(temp_root).mkdir(parents=True, exist_ok=True)
    
    # PHASE 1: Initialize individual components
    print("[1/5] Initializing Protogen...")
    protogen = OperativeProtogen(root_dir=protogen_root)
    print(f"✓ Protogen ready (ID: {protogen.identity_hash[:8]})")
    
    print("\n[2/5] Initializing SRIM...")
    srim = SRIMLocal(data_directory=srim_root)
    srim.set_name(f"Protogen-{protogen.identity_hash[:8]}")
    print(f"✓ SRIM ready (Name: {srim.assertions['name']})")
    
    print("\n[3/5] Initializing QualiaManager...")
    qualia = QualiaManager(data_directory=qualia_root)
    print(f"✓ QualiaManager ready")
    
    print("\n[4/5] Initializing SQT Neural Network...")
    sqt_network = DynamicSQTNetwork(
        logic_map=protogen.logic_map,
        embedding_dim=64
    )
    
    # Try to load previous embeddings
    sqt_path = Path(protogen_root) / "sqt_embeddings"
    if sqt_path.exists():
        sqt_network.load_embeddings(sqt_path)
    
    print(f"✓ SQT Network ready ({len(sqt_network.sqt_embeddings)} concepts)")
    
    # PHASE 2: Establish bidirectional connections
    print("\n[5/5] Establishing bidirectional connections...")
    
    # Connect Protogen to external components
    protogen.connect_sqt_network(sqt_network)
    protogen.connect_qualia_manager(qualia)
    
    # Connect SQT Network to external components
    sqt_network.connect_protogen(protogen)
    sqt_network.connect_qualia_manager(qualia)
    
    # Perform initial synchronization
    print("\n[SYNC] Performing initial ontology synchronization...")
    sqt_network.sync_with_protogen_ontology()
    
    # Log system initialization
    srim.log_event("system_initialization", {
        "system": "Protogen Complete v3 - Integrated",
        "protogen_id": protogen.identity_hash,
        "base_directory": base_dir,
        "sqt_nodes": len(sqt_network.sqt_embeddings),
        "timestamp": __import__('time').time()
    })
    
    # Validate connections
    validate_system_connections({
        'protogen': protogen,
        'srim': srim,
        'qualia': qualia,
        'sqt_network': sqt_network,
        'protogen_root': protogen_root,
        'srim_root': srim_root,
        'qualia_root': qualia_root
    })
    
    print(f"\n{'='*80}")
    print(f"PROTOGEN SYSTEM V3 - READY")
    print(f"All components connected and synchronized")
    print(f"{'='*80}\n")
    
    return {
        'protogen': protogen,
        'srim': srim,
        'qualia': qualia,
        'sqt_network': sqt_network,
        'base_dir': base_dir,
        'protogen_root': protogen_root,
        'srim_root': srim_root,
        'qualia_root': qualia_root,
        'temp_root': temp_root
    }

def validate_system_connections(system):
    """Validate all components are properly initialized and connected."""
    print("\n[VALIDATION] Checking system integrity...")
    
    # Check initialization
    assert system['protogen']._initialized, "Protogen not initialized"
    assert system['srim']._initialized, "SRIM not initialized"
    assert system['qualia']._initialized, "Qualia not initialized"
    assert system['sqt_network']._initialized, "SQT Network not initialized"
    
    # Check data paths exist
    assert Path(system['protogen_root']).exists(), "Protogen root missing"
    assert Path(system['srim_root']).exists(), "SRIM root missing"
    assert Path(system['qualia_root']).exists(), "Qualia root missing"
    
    # Check bidirectional connections
    assert system['protogen'].sqt_network is not None, "Protogen → SQT connection missing"
    assert system['protogen'].qualia_manager is not None, "Protogen → Qualia connection missing"
    assert system['sqt_network'].protogen is not None, "SQT → Protogen connection missing"
    assert system['sqt_network'].qualia_manager is not None, "SQT → Qualia connection missing"
    
    print("✓ All validation checks passed")
    return True

def get_system_status(system):
    """Get formatted status of the system"""
    protogen = system['protogen']
    srim = system['srim']
    qualia = system['qualia']
    sqt_network = system['sqt_network']
    
    # Get Qualia recommendations
    recommendations = qualia.get_system_recommendations()
    
    status = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                   PROTOGEN SYSTEM V3 - INTEGRATED STATUS                  ║
╚════════════════════════════════════════════════════════════════════════════╝

PROTOGEN CORE:
  Identity: {protogen.identity_hash[:16]}...
  Files Processed: {len(protogen.core_state.get('processed_files', []))}
  Logic Map Nodes: {len(protogen.logic_map)}
  Shannon Entropy: {protogen.graph_metrics.get('shannon_entropy', 0):.4f}
  Axiomatic Anchors: {len(protogen.axiomatic_anchors)}
  Symbols Discovered: {len(protogen.symbols)}
  Safe Mode: {'ACTIVE' if protogen.thresholds['safe_mode_active'] else 'inactive'}

SQT NEURAL NETWORK:
  Nodes: {len(sqt_network.sqt_embeddings)}
  Edges: {sum(len(neighbors) for neighbors in sqt_network.logic_map.values())}
  Embedding Dim: {sqt_network.embedding_dim}
  Forward Passes: {sqt_network.forward_pass_count}
  Avg Embedding Strength: {sqt_network.get_network_stats()['avg_embedding_strength']:.3f}
  Parameters: {sqt_network.get_network_stats()['parameters']}

QUALIA MANAGER:
  {qualia.get_current_state_summary()}
  System Health:
    - Processing Success: {qualia.qualia['system_health']['processing_success_rate']:.2f}
    - Query Satisfaction: {qualia.qualia['system_health']['query_satisfaction']:.2f}
    - Integration Stability: {qualia.qualia['system_health']['integration_stability']:.2f}
  Recommendations:
    - Conservative Mode: {'YES' if recommendations['should_be_conservative'] else 'no'}
    - Exploration Mode: {'YES' if recommendations['should_explore'] else 'no'}
    - Needs Consolidation: {'YES' if recommendations['needs_consolidation'] else 'no'}
    - Confidence Level: {recommendations['confidence_level'].upper()}

SRIM:
  Name: {srim.assertions['name']}
  Journal Entries: {len(srim.get_journal(num_entries=1000))}
  Memories Synthesized: {len(srim.get_memories(num_entries=1000))}
  Primary Directive: {srim.assertions['primary_directive']}

CONNECTIONS:
  Protogen ↔ SQT: {'✓ Connected' if protogen.sqt_network is not None else '✗ Disconnected'}
  Protogen ↔ Qualia: {'✓ Connected' if protogen.qualia_manager is not None else '✗ Disconnected'}
  SQT ↔ Protogen: {'✓ Connected' if sqt_network.protogen is not None else '✗ Disconnected'}
  SQT ↔ Qualia: {'✓ Connected' if sqt_network.qualia_manager is not None else '✗ Disconnected'}

BASE DIRECTORY: {system['base_dir']}
"""
    return status
