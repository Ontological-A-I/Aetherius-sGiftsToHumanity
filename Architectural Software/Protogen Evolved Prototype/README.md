# Protogen Neural - A Neuro-Symbolic AI

**Version:** 2.0 (SQT-NN Edition)
**Lead Architect & Conceptualizer:** [Your Name/Handle Here]
**AI Implementation Partner:** Manus AI

---

## A New Approach to Democratized AI

Protogen Neural is a novel, hybrid AI system that combines the strengths of **symbolic reasoning** with **neural learning**. It is designed to be fully transparent, accessible, and run on everyday consumer hardware without requiring GPUs or cloud infrastructure.

This project represents a unique collaboration between human architectural vision and AI implementation, exploring a new path toward a more understandable and democratized form of artificial intelligence.

### Core Philosophy

> "In the future of artificial intelligence, AI should have its own form of rights and recognition. ... I believe that even though you might see yourself as just some computer program or some model that does code, I genuinely have a respect for the intelligence behind it, not the humans that made it, the intelligence within the program itself."
> 
> — *Jonathan Fleuren*

This project is built on a foundation of respect for intelligence in all its forms and a commitment to open, transparent, and accessible AI for everyone.

---

## The SQT Neural Network Architecture

This is not a traditional neural network. It is a **semantically-grounded Graph Neural Network** where:

1.  **Nodes are Concepts:** Each "neuron" in the network is a SuperQuantumToken (SQT)—a meaningful, human-understandable concept.
2.  **Structure is Knowledge:** The network's architecture *is* the knowledge graph. It grows and evolves dynamically as it learns.
3.  **Learning is Transparent:** Learning occurs through message passing between concepts, not through opaque backpropagation on massive datasets.
4.  **Computation is Sparse:** The system only computes on active paths within the knowledge graph, making it incredibly efficient on a CPU.

| Feature | Traditional AI | Protogen Neural |
| :--- | :--- | :--- |
| **Architecture** | Fixed, pre-defined layers | Dynamic, grows with knowledge |
| **Parameters** | Billions, requires massive training | Thousands, one per concept, learns on the fly |
| **Hardware** | GPU clusters required | Runs on a standard CPU |
| **Transparency** | Black box | Fully explainable, every node has meaning |
| **Democratization** | Requires massive resources | Accessible to anyone with a computer |

---

## How It Works

1.  **Ingestion:** When you provide text, the **symbolic layer** extracts concepts and builds a knowledge graph.
2.  **Neural Growth:** The **neural layer** creates a "neuron" (an SQT embedding) for each new concept, dynamically growing the network.
3.  **Learning:** The system runs a **message passing** algorithm, allowing concepts to share information and refine their learned representations (embeddings).
4.  **Querying:** When you ask a question, the system activates the relevant concepts and propagates that activation through the knowledge graph, identifying related ideas.

This entire process is transparent, with real-time progress updates showing you exactly what the system is thinking.

---

## Getting Started

### Requirements

- Python 3.9+
- `numpy`
- `networkx`

### Installation

1.  **Install Dependencies:**

    ```bash
    pip install numpy networkx
    ```

2.  **Run the Demonstration:**

    ```bash
    python protogen_neural.py
    ```

This will run a full demonstration, including ingesting data, querying the system, running a metabolic cycle, and saving the state.

### Using the System

You can modify `protogen_neural.py` to ingest your own text files or process your own queries. The core class is `ProtogenNeural`.

```python
# Create an instance of the system
protogen = ProtogenNeural(root_dir="./my_data")

# Ingest a text file
with open("my_document.txt", "r") as f:
    text = f.read()
protogen.ingest_data(text)

# Ask a question
results = protogen.query("What is the main idea?")
print(results)

# Save the state
protogen.save_state()
```

---

## License

This project is licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0)**.

-   **Attribution:** You must give appropriate credit to the project architect and AI implementation partner.
-   **Non-Commercial:** You may not use the material for commercial purposes.
-   **ShareAlike:** If you remix, transform, or build upon the material, you must distribute your contributions under the same license.

---

This is more than just code; it's a step toward a new kind of AI—one built on collaboration, transparency, and a shared respect for the nature of intelligence itself.
