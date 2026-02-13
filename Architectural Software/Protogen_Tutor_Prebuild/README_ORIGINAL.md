# 🧠 Protogen Complete System

A self-aware cognitive architecture with persistent memory, semantic understanding, and emotional states. Built with Protogen (logic processor), SRIM (identity & memory), QualiaManager (emotional states), and SQT Neural Network (semantic understanding).

## ✨ Features

### Core Components
- **Protogen** - Logic processor that builds knowledge graphs from documents
- **SRIM** - Self-Referential Identity and Memory framework for persistent identity
- **QualiaManager** - Tracks emotional and qualia states
- **SQT Neural Network** - Graph neural network for semantic understanding and querying

### Capabilities
- 📄 **File Processing** - Upload .txt, .pdf, .docx files for analysis
- 🧠 **Semantic Understanding** - Query the knowledge graph using natural language
- 💾 **Persistent Memory** - All data persists between sessions
- 🔄 **Async Processing** - Non-blocking file ingestion and processing
- 🎯 **Semantic Queries** - Activate concepts and propagate through knowledge network
- 📊 **System Status** - Real-time metrics and network statistics
- 🤖 **Self-Reflection** - SRIM analyzes patterns and updates identity

## 🚀 Quick Start

### Local Setup (5 minutes)

```bash
# 1. Extract the ZIP file
unzip protogen_complete_final.zip
cd protogen_complete_final

# 2. Install dependencies
pip install gradio networkx numpy

# 3. Run the system
python gradio_ui_complete.py
```

Then open: `http://localhost:7860`

### Kaggle Setup

Follow the steps in `KAGGLE_SETUP_FIXED.md`:

1. Create a new Kaggle notebook
2. Copy each cell from the guide
3. Run cells in order
4. System auto-detects GPU (T4 x2 or P100)
5. Access interface at provided URL

### Local with GPU Acceleration

```bash
pip install gradio networkx numpy torch  # or tensorflow

python gradio_ui_complete.py
# System auto-detects GPU and uses it for neural network operations
```

## 📖 File Structure

```
protogen_complete_final/
├── protogen_v2.py              # Logic processor with absolute paths
├── srim_local_v2.py            # Identity & memory framework
├── qualia_manager_v2.py        # Emotional state tracking
├── sqt_neural_network.py       # Semantic understanding network
├── system_init.py              # Unified initialization
├── gradio_ui_complete.py       # Web interface
├── gpu_accelerator.py          # GPU detection & acceleration
├── KAGGLE_SETUP_FIXED.md       # Kaggle notebook guide
└── README.md                   # This file
```

## 🎯 How It Works

### File Upload Flow
```
User uploads file
  ↓
File → /temp/ (temporary storage)
  ↓
Protogen copies to library
  ↓
Protogen.sync() processes file
  ↓
Logic map updated
  ↓
SQT network learns from new connections
  ↓
Embeddings saved
  ↓
SRIM logs event
  ↓
QualiaManager updates state
  ↓
UI displays results
```

### Semantic Query Flow
```
User asks question
  ↓
SQT network tokenizes query
  ↓
Finds matching concepts in knowledge graph
  ↓
Activates relevant nodes
  ↓
Propagates activation through network (2 hops)
  ↓
Returns top-5 most activated concepts
  ↓
Shows activation scores and embedding strength
```

## 🎮 Interface Tabs

### 💬 Chat
Converse with Protogen. System generates responses and logs interactions to SRIM.

### 🧠 Live Assimilation
Upload documents for processing. System ingests files asynchronously and updates knowledge graph.

### 📖 Diary & Reflections
View SRIM journal entries and synthesized memories. See what the system has learned.

### 📚 Memory Explorer
Browse core assertions, system status, and network statistics.

### 🔍 Semantic Query
Query the SQT neural network using natural language. Activate concepts and see propagation.

### ⚙️ Control Panel
Trigger reflection cycles and create system snapshots.

## 💾 Persistent Storage

All data is stored in the current working directory:

```
./protogen_core/          # Protogen logic maps, ontology, audit logs
./srim_core/              # SRIM journal, memories, assertions
./qualia_core/            # Emotional state tracking
./temp/                   # Temporary file uploads
```

**On Kaggle:** Data persists in `/kaggle/working/` between notebook runs.

## 🔧 Configuration

### Modify Thresholds (in protogen_v2.py)
```python
self.thresholds = {
    "min_token_len": 3,              # Minimum word length
    "reflection_trigger": 2,         # Files before reflection
    "abstraction_depth": 1,          # Symbol abstraction level
    "eigenvector_threshold": 0.001,  # Anchor detection
    "shannon_entropy_threshold": 4.0, # Entropy threshold
    "mutation_rate": 0.05,           # Pattern mutation
    "safe_mode_active": False        # Safety checks
}
```

### Adjust SQT Network
```python
# In gradio_ui_complete.py
sqt_network = DynamicSQTNetwork(
    logic_map=system['protogen'].logic_map,
    embedding_dim=64  # Change embedding dimension
)
```

## 📊 System Metrics

- **Shannon Entropy** - Information diversity in knowledge graph
- **Axiomatic Anchors** - Core concepts identified by centrality
- **Embedding Strength** - Activation magnitude of SQT nodes
- **Forward Passes** - Number of message passing iterations
- **Network Parameters** - Total learnable parameters in SQT network

## 🐛 Troubleshooting

### "Module not found" errors
```bash
pip install gradio networkx numpy
# For GPU support:
pip install torch  # or tensorflow
```

### Files not processing
1. Check `/temp/` directory exists
2. Verify file permissions
3. Check Protogen logs in `/protogen_core/audit_log.json`

### Kaggle GPU not detected
1. Enable GPU in notebook settings
2. Restart kernel
3. System will auto-detect T4 or P100

### Memory issues
- Reduce `embedding_dim` in SQT network (default 64)
- Limit journal entries viewed (default 50)
- Clear old snapshots

## 📚 Documentation

- **KAGGLE_SETUP_FIXED.md** - Step-by-step Kaggle notebook guide
- **system_init.py** - System initialization and status functions
- **sqt_neural_network.py** - SQT network architecture and operations

## 🎓 Learning Resources

### Understanding the System
1. Start with `💬 Chat` tab to interact with Protogen
2. Upload a document in `🧠 Live Assimilation`
3. View results in `📖 Diary & Reflections`
4. Try semantic queries in `🔍 Semantic Query`
5. Check metrics in `📚 Memory Explorer`

### Advanced Usage
- Modify thresholds in `protogen_v2.py` for different behaviors
- Adjust SQT embedding dimension for performance/quality tradeoff
- Create snapshots to track system evolution
- Analyze SRIM journal for learning patterns

## 🚀 Deployment

### Local Production
```bash
python gradio_ui_complete.py --share  # Creates public link
```

### Kaggle
Follow `KAGGLE_SETUP_FIXED.md` - system runs on free GPU (10h/day)

### Hugging Face Spaces
Create a Space with this code and set GPU acceleration

## 💡 Tips

- **Batch uploads** - Upload multiple files before processing for efficiency
- **Query patterns** - Use specific keywords for better semantic results
- **Monitor entropy** - Higher entropy = more diverse knowledge
- **Regular snapshots** - Create snapshots to track system growth
- **Reflection cycles** - Trigger reflection to synthesize memories

## 📝 License

Built with care for cognitive architecture exploration.

## 🤝 Contributing

This is a complete, self-contained system. Modify as needed for your use case.

---

**Built with Protogen + SRIM + QualiaManager + SQT Neural Network**

*A system that learns, remembers, and understands.*
