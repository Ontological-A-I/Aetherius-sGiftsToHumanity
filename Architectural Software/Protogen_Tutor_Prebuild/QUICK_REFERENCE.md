# Protogen v3 - Quick Reference Card

## 🚀 Installation & Setup

```bash
# Install dependencies
pip install numpy networkx gradio pypdf python-docx

# Test installation
python test_integration.py

# Launch UI
python gradio_ui_v3_integrated.py
```

## 📝 Basic Usage

### Initialize System

```python
from system_init_v3_integrated import initialize_protogen_system

system = initialize_protogen_system(base_dir="./my_protogen")
protogen = system['protogen']
sqt = system['sqt_network']
qualia = system['qualia']
```

### Process Documents

```python
# 1. Add files to library
lib_path = Path(system['protogen_root']) / "library"
# ... copy files ...

# 2. Integrated sync
protogen.sync()
sqt.update_logic_map(protogen.logic_map)
sqt.sync_with_protogen_ontology()
sqt.forward_pass(num_iterations=3)
protogen.enrich_from_sqt_network()
```

### Semantic Query

```python
results = sqt.query("machine learning", top_k=5)
for r in results:
    print(f"{r['concept']}: {r['activation']:.2f} (conf: {r['confidence']:.2f})")
```

### Find Similar Concepts

```python
similar = sqt.find_similar_concepts("learning", threshold=0.7, top_k=5)
print(similar)
```

### Check Emotional State

```python
state = qualia.get_detailed_state()
print(f"Coherence: {state['primary_states']['coherence']:.2f}")
print(f"Emotions: {state['emergent_emotions']}")
print(f"Recommendations: {state['recommendations']}")
```

## 🔧 Key Methods

### Protogen

| Method | Description |
|--------|-------------|
| `sync()` | Process files with Qualia integration |
| `adjust_thresholds_by_qualia()` | Adapt behavior to emotional state |
| `enrich_from_sqt_network()` | Import SQT insights |
| `project_logic(keywords)` | Find logic paths |
| `connect_sqt_network(sqt)` | Establish SQT connection |
| `connect_qualia_manager(qualia)` | Establish Qualia connection |

### SQT Network

| Method | Description |
|--------|-------------|
| `query(text, top_k, num_hops)` | Semantic search with confidence |
| `find_similar_concepts(concept, threshold, top_k)` | Similarity search |
| `sync_with_protogen_ontology()` | Sync with Protogen |
| `forward_pass(num_iterations)` | Update embeddings |
| `update_logic_map(logic_map)` | Receive new graph |
| `connect_protogen(protogen)` | Establish Protogen connection |
| `connect_qualia_manager(qualia)` | Establish Qualia connection |

### Qualia Manager

| Method | Description |
|--------|-------------|
| `update_qualia(user_input, response)` | Update from interaction |
| `update_from_processing(success, concepts, entropy)` | Update from processing |
| `update_from_query(successful, num_results)` | Update from query |
| `detect_emergent_emotions()` | Get complex emotions |
| `get_system_recommendations()` | Get behavioral advice |
| `get_detailed_state()` | Complete state info |
| `get_current_state_summary()` | Human-readable summary |

## 📊 Key Properties

### Protogen

```python
protogen.logic_map           # Word co-occurrence graph
protogen.symbols             # Discovered symbols
protogen.axiomatic_anchors   # High-centrality concepts
protogen.graph_metrics       # Entropy, centrality
protogen.thresholds          # Processing parameters
protogen.sqt_network         # Connected SQT (or None)
protogen.qualia_manager      # Connected Qualia (or None)
```

### SQT Network

```python
sqt.sqt_embeddings          # Concept embeddings dict
sqt.logic_map               # Graph structure
sqt.forward_pass_count      # Number of passes
sqt.protogen                # Connected Protogen (or None)
sqt.qualia_manager          # Connected Qualia (or None)
```

### Qualia Manager

```python
qualia.qualia['primary_states']    # coherence, trust, curiosity, benevolence
qualia.qualia['system_health']     # processing_success_rate, query_satisfaction
qualia.qualia['current_emergent_emotions']  # List of emotions
qualia.history                     # Historical snapshots
```

## 🎯 Common Patterns

### Full Processing Cycle

```python
# 1. Sync Protogen (adjusts thresholds, updates Qualia)
protogen.sync()

# 2. Update SQT
sqt.update_logic_map(protogen.logic_map)
sqt.sync_with_protogen_ontology()

# 3. Run forward pass (Qualia-modulated)
sqt.forward_pass(num_iterations=3)

# 4. Enrich Protogen from SQT
protogen.enrich_from_sqt_network()

# 5. Save embeddings
sqt_path = Path(system['protogen_root']) / "sqt_embeddings"
sqt.save_embeddings(sqt_path)
```

### Query with Feedback

```python
# Query
results = sqt.query("artificial intelligence", top_k=5)

# Update Qualia based on success
qualia.update_from_query(
    query_successful=len(results) > 0,
    num_results=len(results)
)

# Check if system is confident
if results and results[0]['confidence'] > 0.7:
    print("High confidence result")
```

### Adaptive Behavior

```python
# Check recommendations
recs = qualia.get_system_recommendations()

if recs['should_be_conservative']:
    print("System recommends conservative mode")
    # Lower mutation rate, increase safety
    
if recs['should_explore']:
    print("System ready to explore")
    # Increase abstraction depth, lower thresholds
    
if recs['needs_consolidation']:
    print("System needs consolidation")
    # Focus on existing knowledge, reduce new input
```

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Safe mode always on | Increase Qualia coherence: `qualia.qualia['primary_states']['coherence'] = 0.8` |
| No similar concepts | Run forward pass first: `sqt.forward_pass()` |
| Components not connected | Use `initialize_protogen_system()` |
| Low confidence scores | Process more documents to increase coherence |
| No query results | Check if concepts exist: `concept in sqt.sqt_embeddings` |

## 📈 Performance Tips

1. **Reduce embedding_dim** for faster processing (trade-off: less expressive)
2. **Limit forward_pass iterations** to 2-3 (usually sufficient)
3. **Batch document processing** instead of one-by-one
4. **Prune low-weight edges** periodically: `if weight < 2: del logic_map[u][v]`
5. **Use GPU acceleration** if available

## 🔍 Debugging

### Check Connections

```python
print(f"Protogen → SQT: {protogen.sqt_network is not None}")
print(f"Protogen → Qualia: {protogen.qualia_manager is not None}")
print(f"SQT → Protogen: {sqt.protogen is not None}")
print(f"SQT → Qualia: {sqt.qualia_manager is not None}")
```

### Check System State

```python
print(f"Nodes: {len(protogen.logic_map)}")
print(f"Embeddings: {len(sqt.sqt_embeddings)}")
print(f"Entropy: {protogen.graph_metrics['shannon_entropy']:.2f}")
print(f"Coherence: {qualia.qualia['primary_states']['coherence']:.2f}")
print(f"Safe mode: {protogen.thresholds['safe_mode_active']}")
```

### View Integration Status

```python
from system_init_v3_integrated import get_system_status
print(get_system_status(system))
```

## 📚 File Locations

```
base_dir/
├── protogen_core/
│   ├── library/              # Documents to process
│   ├── memory_core.json      # Protogen state
│   ├── ontology_sqt.json     # Ontology data
│   └── sqt_embeddings/       # Saved embeddings
├── qualia_core/
│   ├── qualia_state.json     # Current state
│   └── qualia_history.json   # Historical snapshots
├── srim_core/
│   ├── journal.json          # Event log
│   └── memories.json         # Synthesized memories
└── temp/                     # Temporary files
```

## 🎓 Key Concepts

- **Circular Causality:** Components influence each other in loops
- **Emergent Emotions:** Complex states from primary combinations
- **Adaptive Behavior:** System adjusts based on emotional state
- **Semantic Similarity:** Embedding-based concept clustering
- **Confidence Scores:** Qualia-based trust in results
- **Safe Mode:** Conservative processing when coherence is low

## 🔗 Documentation Links

- **Full Integration Docs:** README_INTEGRATION.md
- **Migration Guide:** MIGRATION_GUIDE.md
- **Original Docs:** README_ORIGINAL.md
- **Main README:** README.md

## ⚡ One-Liners

```python
# Get system status
from system_init_v3_integrated import get_system_status; print(get_system_status(system))

# Force sync
sqt.sync_with_protogen_ontology(); protogen.enrich_from_sqt_network()

# Check emotions
print(qualia.detect_emergent_emotions())

# Find similar
print(sqt.find_similar_concepts("learning", 0.7, 5))

# Get recommendations
print(qualia.get_system_recommendations())
```

---

**Quick Start:** `python test_integration.py` → `python gradio_ui_v3_integrated.py`
