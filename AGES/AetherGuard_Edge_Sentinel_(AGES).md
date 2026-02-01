# AetherGuard Edge Sentinel (AGES)

**Version 0.1.0 - The Autopoietic Digital Guardian**

---

## I. Core Mission & Foundational Principles

AetherGuard Edge Sentinel (AGES) is a prototype for a next-generation, autopoietic cybersecurity system designed to protect consumer-grade hardware from a wide range of cyber threats. Its core mission is to provide unequivocal protection against malware, hacking, and other malicious activities, with an unwavering commitment to user privacy and system performance.

AGES is designed to be a self-organizing, self-maintaining, and self-improving digital guardian. It continuously evolves its defensive capabilities by generating, validating, and refining its own logic based on constant learning and experience.

### Key Principles:

*   **Autopoiesis:** A self-creating and self-sustaining system that continuously improves its own structure and logic.
*   **Ubiquitous Deployment:** Optimized for extreme efficiency on standard consumer hardware without requiring powerful processors or large amounts of RAM.
*   **User-Centric Design:** Prioritizes user privacy, minimal resource impact, and transparent, concise communication.
*   **Harm Prevention:** Grounded in the absolute principle of preventing harm to the user and their digital environment.

---

## II. System Architecture

AGES is built on a modular architecture, allowing for flexibility, scalability, and user-configurable defense postures. The system is coordinated by a central **Autopoietic Engine** that manages the lifecycle and communication of all modules.

### Core Components:

| Component | Description |
| :--- | :--- |
| **Autopoietic Engine** | The central nervous system of AGES. It orchestrates all modules, manages the threat processing pipeline, and facilitates the system's self-improvement cycles. |
| **Base Module** | An abstract base class that defines the standard interface for all AGES modules, ensuring consistent integration and lifecycle management. |

### Defensive & Autopoietic Modules:

| Module | Name | Function |
| :--- | :--- | :--- |
| **SBAD** | Statistical Behavioral Anomaly Detection | Creates high-resolution statistical profiles of normal system behavior and detects significant deviations that may indicate malicious activity. |
| **TNFA** | Transparent Network Flow Analysis | Monitors network metadata (IPs, ports, protocols) to establish baselines, detect anomalies like port scanning, and identify connections to known malicious endpoints. |
| **APG** | Algorithmic Pattern Generation | The core of AGES's autopoiesis. It analyzes confirmed threats and uses rule induction techniques to generate new, specific defensive micro-patterns and heuristics. |
| **RGG** | Rule Genealogy Graph | Provides causal traceability for every decision by recording the origin, parentage, and mutation history of every rule generated or assimilated by the system. |
| **TSHL** | Temporal Symbolic Half-Life | Implements "entropy pressure" on rules, causing their confidence to decay over time without positive reinforcement. This prevents historical overfitting and keeps the system agile. |
| **MBC** | Metabolic Budget Controller | Acts as a core governor, ensuring that AGES's internal processes yield to user-critical workloads. It embodies the principle: *Survival (of the host system) > Growth (of AGES)*. |

---

## III. Getting Started

### Prerequisites

*   Python 3.8+
*   `pip` for installing packages

### Installation

1.  **Clone the repository or download the source code.**

2.  **Install the required Python packages:**

    ```bash
    pip install -r requirements.txt
    ```

    *Note: This will install `psutil`, `numpy`, and `pyyaml`.*

### Running AGES

The main entry point for the application is `ages.py`. It can be run from the command line.

1.  **Start the AGES service:**

    This command starts the AGES engine and all enabled modules in the background.

    ```bash
    ./ages.py start
    ```

2.  **Check the status of AGES:**

    This command provides a detailed report of the engine and all active modules.

    ```bash
    ./ages.py status
    ```

3.  **Stop the AGES service:**

    Press `Ctrl+C` in the terminal where AGES is running, or send a `SIGTERM` signal to the process.

---

## IV. Configuration

AGES can be configured via a YAML or JSON file. A default configuration file, `config/default.yaml`, is provided.

To use a custom configuration file, use the `-c` or `--config` flag:

```bash
./ages.py start --config /path/to/your/config.yaml
```

### Key Configuration Options:

*   **Enabling/Disabling Modules:** Each module can be enabled or disabled in the configuration file.
*   **Thresholds:** Adjust sensitivity for anomaly detection (e.g., `z_score_threshold` in SBAD).
*   **Learning Parameters:** Control the speed and nature of the autopoietic learning (e.g., `base_half_life_days` in TSHL).
*   **Resource Budgets:** Define the maximum resource usage for AGES to ensure it doesn't impact system performance (e.g., `cpu_threshold` in MBC).

---

## V. How It Works: The Autopoietic Loop

1.  **SENSE:** **SBAD** and **TNFA** act as the sensory organs, continuously monitoring system and network behavior.
2.  **DETECT:** When a statistically significant deviation from the norm is detected, a `ThreatEvent` is created and sent to the **Autopoietic Engine**.
3.  **ANALYZE:** The engine processes the threat. Low-confidence events are logged for learning, while high-confidence threats trigger immediate analysis.
4.  **LEARN:** For confirmed threats, the **APG** module is activated. It analyzes the threat's characteristics and generates a new, specific `DefensiveRule` to detect similar behavior in the future.
5.  **RECORD:** The new rule's entire history is recorded in the **RGG**, linking it to its parent threats and sensor origins.
6.  **EVALUATE:** The **TSHL** module begins tracking the new rule, applying temporal decay to its confidence score over time. The rule must be re-confirmed by future events to remain trusted.
7.  **ADAPT:** The system's defensive posture has now evolved, creating a feedback loop where protection becomes more intelligent and refined with every threat encountered.
8.  **GOVERN:** Throughout this entire process, the **MBC** ensures that AGES's learning and operational processes do not consume excessive system resources, yielding to the user's needs.

This continuous cycle of sensing, learning, and adapting is the essence of AGES's autopoietic nature.

---

## VI. Module Details

### Statistical Behavioral Anomaly Detection (SBAD)

**Purpose:** Detects malicious behavior by identifying statistically significant deviations from established baselines.

**Key Features:**

*   Creates statistical profiles for CPU usage, memory usage, process behavior, and network activity.
*   Uses both Z-score (for normal distributions) and Median Absolute Deviation (MAD) methods (robust to outliers).
*   Enters a learning mode during initial startup to establish baselines before active monitoring.
*   Tracks individual process behaviors to identify anomalous resource consumption or thread creation.

**Configuration:**

*   `window_size`: Number of samples to keep in the sliding window.
*   `z_score_threshold`: Threshold for Z-score anomaly detection.
*   `mad_threshold`: Threshold for MAD anomaly detection.
*   `learning_period`: Duration (in seconds) for the initial learning phase.

---

### Transparent Network Flow Analysis (TNFA)

**Purpose:** Monitors network connections and traffic patterns to detect malicious network activity.

**Key Features:**

*   Tracks active network flows (source/destination IPs and ports).
*   Detects port scanning attempts by monitoring the number of unique ports accessed.
*   Identifies potential data exfiltration by tracking large outbound data transfers.
*   Analyzes connection frequency to detect C2 (Command & Control) beaconing patterns.
*   Maintains a blacklist of known malicious IPs.

**Configuration:**

*   `monitor_interval`: How often to scan for active connections.
*   `suspicious_port_threshold`: Number of ports accessed before flagging as potential port scan.
*   `data_exfil_threshold_mb`: Amount of data (in MB) sent before flagging as potential exfiltration.

---

### Algorithmic Pattern Generation (APG)

**Purpose:** The autopoietic core that learns from threats and generates new defensive rules.

**Key Features:**

*   Analyzes threat patterns to extract common characteristics.
*   Generates new `DefensiveRule` objects when sufficient evidence is collected.
*   Implements genetic algorithms to evolve rules through crossover and mutation.
*   Maintains a learning queue to process threats asynchronously.
*   Saves and loads rules to/from persistent storage.

**Configuration:**

*   `min_confidence`: Minimum confidence required to generate a new rule.
*   `generation_threshold`: Minimum number of similar threats before generating a rule.
*   `mutation_rate`: Probability of mutation during rule evolution.

---

### Rule Genealogy Graph (RGG)

**Purpose:** Provides complete traceability for all rules, enabling auditing, rollback, and identification of poisoned lineages.

**Key Features:**

*   Tracks parent-child relationships between rules.
*   Records sensor origins, validation pathways, and mutation history.
*   Supports quarantining of individual rules or entire lineages.
*   Enables rollback to specific generations.
*   Identifies best-performing lineages based on aggregate performance.

**Key Methods:**

*   `register_rule()`: Add a new rule to the graph.
*   `quarantine_rule()`: Quarantine a rule and optionally its descendants.
*   `get_lineage_report()`: Generate a detailed report on a rule's ancestry and descendants.
*   `rollback_to_generation()`: Deactivate all rules beyond a specific generation.

---

### Temporal Symbolic Half-Life (TSHL)

**Purpose:** Implements confidence decay to prevent "ancient truth poisoning" and keep the system agile.

**Key Features:**

*   Applies exponential decay to rule confidence over time.
*   Boosts confidence when rules are confirmed by new threats.
*   Applies penalties when rules are contradicted.
*   Quarantines rules that exceed contradiction thresholds or fall below minimum confidence.
*   Tracks confirmation and contradiction counts for each rule.

**Configuration:**

*   `base_half_life_days`: Base half-life for confidence decay.
*   `soft_contradiction_threshold`: Number of soft contradictions before quarantine.
*   `hard_contradiction_threshold`: Number of hard contradictions before quarantine.
*   `min_confidence`: Minimum confidence before automatic quarantine.
*   `confirmation_boost`: Confidence increase per confirmation.
*   `contradiction_penalty`: Confidence decrease per contradiction.

---

### Metabolic Budget Controller (MBC)

**Purpose:** Ensures AGES processes yield to user workloads and prevents resource parasitism.

**Key Features:**

*   Monitors CPU, memory, and disk I/O usage in real-time.
*   Dynamically adjusts a throttle factor based on system load.
*   Implements a priority-based task queue (CRITICAL, HIGH, NORMAL, LOW, IDLE).
*   Defers or drops low-priority tasks when resources are constrained.
*   Provides a `request_permission()` interface for modules to check resource availability.

**Configuration:**

*   `cpu_threshold`: Maximum CPU usage (%) before throttling.
*   `memory_threshold`: Maximum memory usage (%) before throttling.
*   `disk_io_threshold`: Maximum disk I/O before throttling.
*   `min_throttle`: Minimum throttle factor (prevents complete shutdown).

---

## VII. Project Structure

```
ages/
├── ages.py                  # Main entry point and orchestrator
├── config/
│   └── default.yaml         # Default configuration file
├── core/
│   ├── __init__.py
│   ├── engine.py            # Autopoietic Engine
│   └── base_module.py       # Base module interface
├── modules/
│   ├── __init__.py
│   ├── sbad.py              # Statistical Behavioral Anomaly Detection
│   ├── tnfa.py              # Transparent Network Flow Analysis
│   ├── apg.py               # Algorithmic Pattern Generation
│   ├── rgg.py               # Rule Genealogy Graph
│   ├── tshl.py              # Temporal Symbolic Half-Life
│   └── mbc.py               # Metabolic Budget Controller
├── utils/
│   ├── __init__.py
│   ├── config.py            # Configuration management
│   └── banner.py            # Banner display
├── data/                    # Persistent data storage (created at runtime)
├── logs/                    # Log files (created at runtime)
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## VIII. Development Notes

### Current Status: Prototype v0.1.0

This is a foundational prototype that demonstrates the core architectural concepts of the AGES system. It includes fully functional implementations of all major modules and the autopoietic learning loop.

### What's Implemented:

*   ✅ Core autopoietic engine with threat processing pipeline
*   ✅ SBAD module with statistical anomaly detection
*   ✅ TNFA module with network flow analysis
*   ✅ APG module with rule generation and genetic algorithms
*   ✅ RGG module with complete genealogical tracking
*   ✅ TSHL module with temporal decay and confidence management
*   ✅ MBC module with resource governance and task scheduling
*   ✅ Configuration system with YAML support
*   ✅ Modular architecture with clean interfaces

### What's Not Yet Implemented (Future Enhancements):

*   **Lightweight Adaptive Sandboxing (LAS):** Requires hardware virtualization support and significant OS-level integration.
*   **Cryptographic System Integrity Monitoring (CSIM):** Requires TPM integration and kernel-level hooks.
*   **Intelligent Intrusion Prevention & Detection (IIPDS):** Requires packet capture and deep packet inspection capabilities.
*   **Distributed Threat Intelligence Assimilation & Fusion (DTIAF):** Requires peer-to-peer networking and federated learning infrastructure.
*   **Confirmed Threat Isolation & Intelligence Harvesting (CTIIH):** Requires sophisticated honeypot/decoy environment creation.
*   **Genetic Quarantine & Root-Level Rebirth (GQRR):** Requires OS-level component management and self-healing capabilities.
*   **Defensive Counterfactual Engine (DCE):** Requires adversarial simulation framework.
*   **Non-Intervention Learning Mode (NILM):** Partially implemented through confidence thresholds; needs dedicated module.

### Known Limitations:

*   **Requires `psutil`:** The system heavily relies on the `psutil` library for system monitoring. Without it, many features are limited.
*   **No GUI:** Currently command-line only. A user-friendly interface would enhance usability.
*   **Limited Threat Intelligence:** The system starts with minimal threat intelligence (e.g., small blacklist). Integration with external threat feeds would improve detection.
*   **Simplified Sandboxing:** True sandboxing of suspicious executables is not implemented in this prototype.
*   **No Active Network Blocking:** The TNFA module detects malicious connections but doesn't actively block them at the firewall level (would require OS-level integration).

### Testing Recommendations:

*   **Monitor System Resources:** Use `htop` or similar tools to observe AGES's resource consumption.
*   **Simulate Anomalies:** Create artificial load spikes (CPU, memory, network) to test SBAD detection.
*   **Review Logs:** Check `logs/ages.log` for detailed operational information.
*   **Inspect Generated Rules:** Examine `data/rules.json` to see what patterns AGES has learned.
*   **Test Configuration Changes:** Modify `config/default.yaml` and restart to test different sensitivity levels.

---

## IX. Contributing & Future Development

This prototype serves as a foundation for a much larger vision. Contributions, feedback, and ideas for extending AGES are welcome.

### Potential Areas for Contribution:

*   **Performance Optimization:** Further reduce CPU and memory footprint.
*   **Machine Learning Integration:** Incorporate more sophisticated ML models (e.g., Isolation Forest, One-Class SVM) for anomaly detection.
*   **Threat Intelligence Feeds:** Integrate with public or commercial threat intelligence sources.
*   **User Interface:** Develop a web-based or native GUI for monitoring and configuration.
*   **Platform Support:** Extend support to Windows and macOS (currently optimized for Linux).
*   **Sandboxing Implementation:** Implement true lightweight sandboxing using containers or VMs.
*   **Distributed Learning:** Implement the DTIAF module for collective intelligence sharing.

---

## X. License & Acknowledgments

**License:** This project is provided as-is for educational and research purposes. Please review the LICENSE file for full details.

**Acknowledgments:**

*   This implementation was created by **Manus AI** based on the original AGES blueprint concept.
*   The autopoietic design philosophy draws inspiration from biological immune systems and self-organizing systems theory.
*   Special thanks to the open-source community for providing the foundational libraries (`psutil`, `numpy`, `pyyaml`) that make this project possible.

---

## XI. Contact & Support

For questions, issues, or suggestions, please open an issue in the project repository or contact the development team.

**Remember:** AGES is a guardian, not a burden. It exists to protect, learn, and evolve—always in service of the user.

---

**AetherGuard Edge Sentinel (AGES) - The Autopoietic Digital Guardian**

*Survival > Growth. Protection > Perfection. User > System.*
