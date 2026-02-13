# Migration Guide: Protogen v2 → v3 (Integrated)

## Overview

This guide helps you migrate from the original Protogen v2 system to the new v3 integrated version with bidirectional connections.

## Breaking Changes

### 1. Import Paths

**v2:**
```python
from protogen_v2 import OperativeProtogen
from sqt_neural_network import DynamicSQTNetwork
from qualia_manager_v2 import QualiaManager
from system_init import initialize_protogen_system
```

**v3:**
```python
from protogen_v3_integrated import OperativeProtogen
from sqt_neural_network_v3_integrated import DynamicSQTNetwork
from qualia_manager_v3_integrated import QualiaManager
from system_init_v3_integrated import initialize_protogen_system
```

### 2. QualiaManager Constructor

**v2:**
```python
qualia = QualiaManager(
    data_directory=qualia_root,
    master_framework_ref=None  # Unused parameter
)
```

**v3:**
```python
qualia = QualiaManager(
    data_directory=qualia_root
    # master_framework_ref removed
)
```

### 3. System Initialization

**v2:** Components initialized but not connected.

**v3:** Components initialized AND connected bidirectionally.

```python
# v3 automatically establishes connections
system = initialize_protogen_system(base_dir="./protogen")

# Connections are already established:
# - protogen.sqt_network → sqt_network
# - protogen.qualia_manager → qualia
# - sqt_network.protogen → protogen
# - sqt_network.qualia_manager → qualia
```

## New Features to Adopt

### 1. Use Integrated Sync

**v2 Pattern:**
```python
# Old way: manual steps
protogen.sync()
sqt_network.update_logic_map(protogen.logic_map)
sqt_network.forward_pass()
```

**v3 Pattern:**
```python
# New way: integrated sync with feedback
protogen.sync()  # Now adjusts thresholds and updates Qualia
sqt_network.update_logic_map(protogen.logic_map)
sqt_network.sync_with_protogen_ontology()  # NEW: bidirectional sync
sqt_network.forward_pass()  # Now modulated by Qualia
protogen.enrich_from_sqt_network()  # NEW: feedback loop
```

### 2. Use Confidence Scores

**v2 Pattern:**
```python
results = sqt_network.query("learning", top_k=5)
# No confidence information
```

**v3 Pattern:**
```python
results = sqt_network.query("learning", top_k=5)
for result in results:
    confidence = result['confidence']  # NEW: Qualia-based confidence
    print(f"{result['concept']}: {confidence:.2f}")
```

### 3. Monitor Emotional State

**v2 Pattern:**
```python
# Qualia was updated but not used
qualia.update_qualia(user_input, response)
# No way to check emotional state impact
```

**v3 Pattern:**
```python
# Update Qualia
qualia.update_qualia(user_input, response)

# Check emergent emotions
emotions = qualia.detect_emergent_emotions()  # NEW
print(f"System feels: {emotions}")

# Get recommendations
recommendations = qualia.get_system_recommendations()  # NEW
if recommendations['should_be_conservative']:
    print("System recommends conservative behavior")
```

### 4. Use Semantic Similarity

**v2:** Not available

**v3:**
```python
# Find semantically similar concepts
similar = sqt_network.find_similar_concepts(
    "learning",
    threshold=0.7,
    top_k=5
)
print(f"Similar concepts: {similar}")
```

## Step-by-Step Migration

### Step 1: Backup Your Data

```bash
# Backup your existing Protogen data
cp -r protogen_core protogen_core_backup
cp -r qualia_core qualia_core_backup
cp -r srim_core srim_core_backup
```

### Step 2: Update Imports

Replace all imports in your code:

```python
# Find and replace:
# protogen_v2 → protogen_v3_integrated
# sqt_neural_network → sqt_neural_network_v3_integrated
# qualia_manager_v2 → qualia_manager_v3_integrated
# system_init → system_init_v3_integrated
```

### Step 3: Remove Unused Parameters

```python
# Remove master_framework_ref from QualiaManager calls
# OLD:
qualia = QualiaManager(data_directory=path, master_framework_ref=None)

# NEW:
qualia = QualiaManager(data_directory=path)
```

### Step 4: Update Processing Loop

**Old Processing Loop:**
```python
def process_files():
    protogen.sync()
    sqt_network.update_logic_map(protogen.logic_map)
    sqt_network.forward_pass()
    qualia.update_qualia("processing", "complete")
```

**New Processing Loop:**
```python
def process_files():
    # Sync with Qualia integration
    protogen.sync()  # Adjusts thresholds, updates Qualia
    
    # Update and sync SQT
    sqt_network.update_logic_map(protogen.logic_map)
    sqt_network.sync_with_protogen_ontology()  # NEW
    
    # Forward pass with Qualia modulation
    sqt_network.forward_pass()  # Learning rate modulated
    
    # Enrich Protogen from SQT
    protogen.enrich_from_sqt_network()  # NEW
    
    # Update Qualia from processing
    qualia.update_from_processing(
        success=True,
        concepts_learned=len(protogen.logic_map),
        entropy=protogen.graph_metrics['shannon_entropy']
    )  # NEW
```

### Step 5: Update Query Handling

**Old Query Handler:**
```python
def handle_query(query):
    results = sqt_network.query(query)
    return results
```

**New Query Handler:**
```python
def handle_query(query):
    results = sqt_network.query(query)  # Now includes confidence
    
    # Update Qualia based on query success
    qualia.update_from_query(
        query_successful=len(results) > 0,
        num_results=len(results)
    )  # NEW
    
    return results
```

### Step 6: Add Integration Monitoring

```python
# Add to your status display
def show_status():
    # Original status
    print(f"Nodes: {len(protogen.logic_map)}")
    print(f"Entropy: {protogen.graph_metrics['shannon_entropy']:.2f}")
    
    # NEW: Integration status
    print(f"\nQualia State: {qualia.get_current_state_summary()}")
    print(f"Emergent Emotions: {qualia.detect_emergent_emotions()}")
    
    recommendations = qualia.get_system_recommendations()
    print(f"System Mode: {recommendations['confidence_level']}")
    print(f"Safe Mode: {protogen.thresholds['safe_mode_active']}")
```

### Step 7: Test Integration

```bash
# Run integration tests
python test_integration.py

# Should see:
# ✓ All 12 tests passed
# ✓ Bidirectional integration: WORKING
```

## Data Compatibility

### Good News: Full Backward Compatibility

Your existing data files are **fully compatible** with v3:

- ✓ `memory_core.json` - Compatible
- ✓ `ontology_sqt.json` - Compatible (new fields added automatically)
- ✓ `qualia_state.json` - Compatible (new fields added automatically)
- ✓ `sqt_embeddings.json` - Compatible (new field added automatically)
- ✓ All SRIM files - Compatible

### Automatic Upgrades

When you first run v3 with existing data:

1. **Ontology:** Adds `embedding_centrality` field if missing
2. **Qualia:** Adds `system_health` field if missing
3. **SQT Embeddings:** Adds `emotional_valence` field if missing

No manual intervention required!

## Common Migration Issues

### Issue 1: "AttributeError: 'OperativeProtogen' object has no attribute 'sqt_network'"

**Cause:** Using old initialization without connections.

**Solution:** Use `initialize_protogen_system()` from v3, which establishes connections automatically.

### Issue 2: "TypeError: __init__() got an unexpected keyword argument 'master_framework_ref'"

**Cause:** Passing old parameter to QualiaManager.

**Solution:** Remove `master_framework_ref` parameter.

### Issue 3: "KeyError: 'confidence'"

**Cause:** Expecting confidence in query results but SQT not connected to Qualia.

**Solution:** Ensure `sqt_network.connect_qualia_manager(qualia)` was called during initialization.

### Issue 4: Safe mode always active

**Cause:** Qualia coherence is low (< 0.5).

**Solution:** This is expected behavior! Process successful documents to increase coherence, or manually adjust:

```python
qualia.qualia['primary_states']['coherence'] = 0.8
qualia._save_qualia()
protogen.adjust_thresholds_by_qualia()
```

## Gradio UI Migration

### v2 UI Structure

```python
# v2: Basic tabs
- Chat
- Live Assimilation
- Diary & Reflections
- Memory Explorer
- Semantic Query
- Control Panel
```

### v3 UI Structure

```python
# v3: Enhanced with integration tabs
- Chat
- Live Assimilation (shows integration status)
- Semantic Query (shows confidence scores)
- Diary & Reflections
- Memory Explorer
- Qualia State (NEW)
- Integration Status (NEW)
- Control Panel (added Force Sync button)
```

### Update Your UI Code

If you have custom UI code, add the new tabs:

```python
with gr.Tab("💭 Qualia State"):
    qualia_btn = gr.Button("View Detailed Qualia State")
    qualia_output = gr.Textbox(lines=20)
    qualia_btn.click(view_qualia_details_handler, outputs=qualia_output)

with gr.Tab("🔗 Integration Status"):
    integration_btn = gr.Button("View Integration Status")
    integration_output = gr.Textbox(lines=20)
    integration_btn.click(view_integration_status_handler, outputs=integration_output)
```

## Performance Impact

### Expected Changes

- **Initialization:** ~10% slower (connection establishment)
- **Sync:** ~5% slower (Qualia updates)
- **Forward Pass:** ~2% slower (Qualia modulation)
- **Query:** ~1% slower (confidence calculation)

### Benefits

- **Adaptive behavior:** System self-regulates based on state
- **Better symbol discovery:** Semantic + topological
- **Confidence scores:** Know when to trust results
- **Emotional awareness:** System "knows" when it's confused

## Rollback Plan

If you need to rollback to v2:

```bash
# 1. Restore backup
rm -rf protogen_core qualia_core srim_core
mv protogen_core_backup protogen_core
mv qualia_core_backup qualia_core
mv srim_core_backup srim_core

# 2. Use v2 files
python gradio_ui_complete.py  # v2 UI
```

Your data will still work with v2 (new fields are ignored).

## Testing Checklist

After migration, verify:

- [ ] System initializes without errors
- [ ] File processing works
- [ ] Semantic queries return confidence scores
- [ ] Qualia state updates during operations
- [ ] Safe mode activates when coherence is low
- [ ] SQT synchronizes with Protogen ontology
- [ ] Protogen enriches from SQT embeddings
- [ ] Integration test passes all 12 tests
- [ ] Gradio UI loads and all tabs work
- [ ] Existing data loads correctly

## Need Help?

1. Run `python test_integration.py` to diagnose issues
2. Check Integration Status tab in Gradio UI
3. Review connection validation output during initialization
4. Examine Qualia recommendations for system behavior

## Summary

**Key Changes:**
1. Import paths updated (add `_v3_integrated`)
2. Remove `master_framework_ref` parameter
3. Use integrated sync pattern
4. Adopt new features (confidence, emotions, recommendations)
5. Monitor integration status

**Benefits:**
- Unified cognitive architecture
- Self-regulating behavior
- Better semantic understanding
- Emotional awareness
- Circular causality

**Compatibility:**
- ✓ Data files fully compatible
- ✓ Automatic field upgrades
- ✓ Can rollback if needed

---

**Migration Time:** ~15-30 minutes for typical setup

**Difficulty:** Easy to Moderate

**Risk:** Low (full backward compatibility)
