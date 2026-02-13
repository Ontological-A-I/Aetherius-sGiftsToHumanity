# Protogen v3 - Integrated Cognitive Architecture

## Overview

This is the **enhanced version** of your Protogen system with **full bidirectional integration** between all cognitive components. The original system had loosely coupled components that operated in parallel. This version creates a **unified cognitive architecture** with circular causality and feedback loops.

## What's New in v3

### 1. **Bidirectional Protogen ↔ SQT Integration**

**Original Problem:** SQT received data from Protogen but never fed insights back.

**Solution:**
- Protogen now uses SQT embeddings for **semantic symbol discovery**
- SQT synchronizes with Protogen's ontology (symbols, anchors, patterns)
- Protogen enriches its graph metrics with **embedding-based centrality**
- New method: `find_similar_concepts()` enables semantic clustering

**Key Methods:**
- `Protogen.enrich_from_sqt_network()` - Import SQT insights
- `SQTNetwork.sync_with_protogen_ontology()` - Export Protogen discoveries
- `SQTNetwork.find_similar_concepts()` - Semantic similarity search

### 2. **Bidirectional Protogen ↔ Qualia Integration**

**Original Problem:** Protogen operated independently of emotional state.

**Solution:**
- Qualia state now **modulates Protogen's processing thresholds**
- Low coherence activates **safe mode** (conservative processing)
- High trust increases **abstraction depth**
- Curiosity adjusts **eigenvector threshold** for exploration
- Protogen updates Qualia based on **processing outcomes**

**Key Methods:**
- `Protogen.adjust_thresholds_by_qualia()` - Adapt behavior to emotional state
- `Protogen.update_qualia_from_processing()` - Report processing results
- `QualiaManager.update_from_processing()` - Track cognitive health

### 3. **Bidirectional SQT ↔ Qualia Integration**

**Original Problem:** Neural network and emotional state were isolated.

**Solution:**
- Qualia coherence provides **confidence scores** for queries
- Curiosity modulates **SQT learning rate**
- Query success updates **Qualia curiosity**
- Failed queries reduce **query satisfaction** metric

**Key Methods:**
- `SQTNetwork.modulate_by_qualia()` - Adjust learning dynamics
- `QualiaManager.update_from_query()` - Track query outcomes

### 4. **Enhanced Qualia Manager**

**New Features:**
- **Emergent emotion detection** (confident, anxious, excited, confused, content)
- **System health metrics** (processing success, query satisfaction, integration stability)
- **Behavioral recommendations** (conservative mode, exploration mode, consolidation needs)
- **Historical tracking** with state snapshots
- **Richer sentiment analysis** with expanded lexicons

**Key Methods:**
- `QualiaManager.detect_emergent_emotions()` - Complex emotional states
- `QualiaManager.get_system_recommendations()` - Behavioral guidance
- `QualiaManager.get_detailed_state()` - Complete state information

### 5. **Integration Validation**

**New System Initialization:**
- Sequential component initialization
- Explicit connection establishment
- Bidirectional link verification
- Initial ontology synchronization
- Connection validation checks

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    PROTOGEN CORE                            │
│  - Logic Map                                                │
│  - Symbols                                                  │
│  - Axiomatic Anchors                                        │
│  - Graph Metrics                                            │
└───────┬─────────────────────────────────────────┬───────────┘
        │                                         │
        │ ↓ Logic Map                            │ ↑ Embeddings
        │ ↑ Semantic Clusters                    │ ↓ Centrality
        │                                         │
┌───────▼─────────────────────────────────────────▼───────────┐
│              SQT NEURAL NETWORK                             │
│  - Concept Embeddings                                       │
│  - Message Passing                                          │
│  - Semantic Similarity                                      │
│  - Activation Propagation                                   │
└───────┬─────────────────────────────────────────┬───────────┘
        │                                         │
        │ ↓ Confidence Scores                    │ ↑ Learning Rate
        │ ↑ Query Results                        │ ↓ Modulation
        │                                         │
┌───────▼─────────────────────────────────────────▼───────────┐
│                 QUALIA MANAGER                              │
│  - Primary States (coherence, trust, curiosity, benevolence)│
│  - Emergent Emotions                                        │
│  - System Health                                            │
│  - Behavioral Recommendations                               │
└───────┬─────────────────────────────────────────────────────┘
        │
        │ ↑ Processing Outcomes
        │ ↓ Threshold Adjustments
        │
┌───────▼─────────────────────────────────────────────────────┐
│                    PROTOGEN CORE                            │
│              (Circular Causality)                           │
└─────────────────────────────────────────────────────────────┘
```

## Installation & Setup

### Prerequisites

```bash
pip install numpy networkx gradio pypdf python-docx
```

### Quick Start

```python
from system_init_v3_integrated import initialize_protogen_system

# Initialize with full integration
system = initialize_protogen_system(base_dir="./my_protogen")

# Access components
protogen = system['protogen']
sqt_network = system['sqt_network']
qualia = system['qualia']
srim = system['srim']
```

### Run Gradio UI

```bash
python gradio_ui_v3_integrated.py
```

Access at: `http://localhost:7860`

### Run Integration Tests

```bash
python test_integration.py
```

## Usage Examples

### Example 1: Process Documents with Integration

```python
# Upload documents to library
lib_path = Path(system['protogen_root']) / "library"
# ... copy files to lib_path ...

# Sync with full integration
system['protogen'].sync()  # Adjusts thresholds by Qualia, updates Qualia after

# Update SQT network
system['sqt_network'].update_logic_map(system['protogen'].logic_map)
system['sqt_network'].sync_with_protogen_ontology()  # Bidirectional sync

# Run forward pass
system['sqt_network'].forward_pass(num_iterations=3)  # Modulated by Qualia

# Enrich Protogen from SQT
system['protogen'].enrich_from_sqt_network()  # Feedback loop
```

### Example 2: Semantic Query with Confidence

```python
# Query with integrated confidence scoring
results = system['sqt_network'].query(
    "artificial intelligence learning",
    top_k=5,
    num_hops=2
)

for result in results:
    print(f"{result['concept']}: activation={result['activation']:.3f}, confidence={result['confidence']:.2f}")
```

### Example 3: Monitor Emotional State

```python
# Get detailed Qualia state
state = system['qualia'].get_detailed_state()

print(f"Coherence: {state['primary_states']['coherence']:.2f}")
print(f"Emergent emotions: {state['emergent_emotions']}")
print(f"Recommendations: {state['recommendations']}")

# Check if system should be conservative
if state['recommendations']['should_be_conservative']:
    print("System recommends conservative behavior")
```

### Example 4: Find Similar Concepts

```python
# Find semantically similar concepts
similar = system['sqt_network'].find_similar_concepts(
    "learning",
    threshold=0.7,
    top_k=5
)

print(f"Concepts similar to 'learning': {similar}")
```

## File Structure

```
protogen_enhanced/
├── protogen_v3_integrated.py           # Enhanced Protogen core
├── sqt_neural_network_v3_integrated.py # Enhanced SQT network
├── qualia_manager_v3_integrated.py     # Enhanced Qualia manager
├── system_init_v3_integrated.py        # Integrated initialization
├── gradio_ui_v3_integrated.py          # Enhanced UI
├── srim_local_v2.py                    # SRIM (unchanged)
├── gpu_accelerator.py                  # GPU support (unchanged)
├── test_integration.py                 # Integration tests
└── README_INTEGRATION.md               # This file
```

## Key Differences from v2

| Feature | v2 (Original) | v3 (Integrated) |
|---------|---------------|-----------------|
| Protogen → SQT | One-way (logic map) | Bidirectional (logic map + enrichment) |
| SQT → Protogen | None | Semantic clusters + centrality |
| Protogen → Qualia | None | Processing outcomes + updates |
| Qualia → Protogen | None | Threshold modulation |
| SQT → Qualia | None | Confidence scoring |
| Qualia → SQT | None | Learning rate modulation |
| Symbol Discovery | Topology only | Topology + semantic similarity |
| Query Confidence | Not available | Qualia-based confidence |
| Emergent Emotions | Not detected | 5 emotion types detected |
| System Recommendations | None | Conservative/explore/consolidate |
| Validation | None | Full connection validation |

## Integration Test Results

The integration test validates:

1. ✓ System initialization
2. ✓ Component validation
3. ✓ Bidirectional connections
4. ✓ Document processing
5. ✓ Integrated sync
6. ✓ SQT-Protogen synchronization
7. ✓ Forward pass with Qualia modulation
8. ✓ Semantic query with confidence
9. ✓ Qualia influence on thresholds
10. ✓ Protogen enrichment from SQT
11. ✓ Emergent emotion detection
12. ✓ Semantic similarity search

## Performance Considerations

### Memory Usage

- **SQT Embeddings:** ~64 floats per concept (default embedding_dim=64)
- **Message Passing Matrices:** 3 × (64 × 64) = 12,288 floats
- **Qualia History:** Last 1000 snapshots stored

### Computational Complexity

- **Forward Pass:** O(E × D²) where E = edges, D = embedding_dim
- **Similarity Search:** O(N × D) where N = number of concepts
- **Sync Operations:** O(N + S + A) where N = nodes, S = symbols, A = anchors

### Optimization Tips

1. **Reduce embedding_dim** for faster processing (trade-off: less expressive)
2. **Limit forward pass iterations** (3 is usually sufficient)
3. **Use GPU acceleration** if available (gpu_accelerator.py)
4. **Prune low-weight edges** in logic map periodically

## Troubleshooting

### Issue: "Component not connected"

**Solution:** Ensure you call `initialize_protogen_system()` which establishes all connections.

### Issue: "Safe mode always active"

**Solution:** Check Qualia coherence. If < 0.5, safe mode activates. Process successful documents to increase coherence.

### Issue: "No semantic similarity found"

**Solution:** Run `forward_pass()` first to update embeddings, then search for similar concepts.

### Issue: "SQT embeddings not syncing"

**Solution:** Call `sqt_network.sync_with_protogen_ontology()` after Protogen sync.

## Future Enhancements

Potential areas for further development:

1. **Attention Mechanisms:** Add attention weights to message passing
2. **Temporal Dynamics:** Track how concepts evolve over time
3. **Meta-Learning:** Learn optimal threshold adjustments
4. **Multi-Modal Integration:** Add image/audio concept embeddings
5. **Distributed Processing:** Scale to multiple machines
6. **Reinforcement Learning:** Optimize behavior based on outcomes

## Credits

**Original System:** Protogen v2 with SQT, Qualia, and SRIM components

**Enhanced by:** Manus AI Agent

**Version:** 3.0 - Integrated

**Date:** 2026-02-10

## License

Same as original Protogen system.

## Support

For issues or questions about the integration:
1. Run `test_integration.py` to verify setup
2. Check connection status in Gradio UI → Integration Status tab
3. Review Qualia state for behavioral recommendations
4. Examine SRIM journal for event logs

---

**The key insight:** A cognitive system needs circular causality. Information must flow in loops, not just forward. This version transforms your parallel components into a unified, self-regulating cognitive architecture.
