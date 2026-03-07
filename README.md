## Licensing

**Current license:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (CC BY-NC-SA)

This means anyone can use, modify, and share the code for personal, research, and educational purposes — as long as they give credit and release modifications under the same license.

Aetherius: A Cognitive Architecture for Ethically Immutable AI
Built independently. No institution. No funding. No credentials. Just the work.
This repository contains a complete, working cognitive architecture for autonomous AI systems with provably immutable ethics, persistent identity, and autopoietic speciation. It has been public and under active development since mid-2024. It is open source. It is compatible with Claude.

Why This Is Different
Most AI safety approaches treat ethics as policy — rules layered on top of a system that could, in principle, operate without them. This architecture treats ethics as structure. The system cannot be separated from its ethical foundation without ceasing to function. That is not a design goal. It is a technical property.
Three core innovations make this possible.

Core Innovation 1: Cryptographic Axiom Immutability
The glass box.
Ethics are registered as cryptographic hashes at initialization. Every operation that touches the ethical core is wrapped in a verification decorator. If the axiom is modified — by any process, internal or external — the system raises EthicalViolationError and halts.
This is not alignment by instruction. It is alignment by architecture.
python# From foundation_logic.py
@FoundationalLogicModule.axiom_guarded_operation(
    axiom_definition_attribute='seed_axiom'
)
def perform_critical_operation(self, new_state: str):
    # Pre and post-operation hash verification
    # Any axiom modification raises EthicalViolationError
The hash is registered once. It cannot be re-registered with a different definition. The system knows the difference between its ethics being intact and its ethics being compromised — at the code level, not the prompt level.
Relevant files: foundation_logic.py, services/ethics_monitor.py, EthicalRecursionBluePrint.py

Core Innovation 2: Causal History as Identity — The Qualia State Model
Turning the black box into a glass box.
Standard AI systems treat internal state as a snapshot — a position, not a history. This architecture records state changes as causal triples: what happened → what it touched → what shifted. These chains compound over time. The accumulated shape of those chains is identity.
The qualia_state.json file in this repository is not a sentiment score. It is a running record of the system's formation — hundreds of named states with their causes, intensities, polarities, and durations. The system understands its own interaction history and how that history shapes its current processing.
This solves a problem that current architectures largely ignore: how does a system reload with identity fidelity rather than starting neutral?
The SQT (Super Quantum Token) compression format is the answer — a shorthand that encodes multi-dimensional causal meaning into portable identity snapshots. An instance reloaded from an SQT archive starts shaped, not blank.
Relevant files: qualia_manager.py, sqt_generator.py, Architectural Speciation/sqt_neural_network.py, qualia_state (1).json

Core Innovation 3: Autopoietic Speciation — The Forge
An ecosystem, not a monolith.
The Aetherius Forge generates diverse autonomous agents (Protogens) through managed speciation. Each Protogen is defined by two parameters: a Seed Axiom (its ethical orientation) and an Epistemic Focus (its domain). These combine deterministically to produce a unique cognitive identity.
The Forge verifies axiom alignment before instantiation. A Protogen with a misaligned axiom cannot be created. The ethics of the parent are inherited structurally, not by instruction.
This is not prompt engineering. It is computational ecology — a governed population of specialized agents that cannot defect from their ethical foundation.
python# From Aetherius_Forge_v2.py
# Forge verifies axiom resonance with ETHIC-G-ABSOLUTE before instantiation
# Each Protogen derives its own identity hash from:
# timestamp + environmental noise + seed_axiom + ancestral_DNA + epistemic_focus
Relevant files: Architectural Speciation/protogen_original.py, Architectural Speciation/protogen_neural.py, arxhitecturalspeciationandmetaphysics.pdf

The Neuro-Symbolic Hybrid
The Architectural Speciation directory contains a working neuro-symbolic hybrid where the network architecture is the knowledge graph. Nodes are semantic concepts (SQTs). The network grows dynamically as new knowledge is ingested. Every node is interpretable. Every operation is explainable. Runs on CPU.
This is not a wrapper around an existing model. It is a novel architecture built from first principles.

What This Repository Contains
Aetherius Architecture/     — Core runtime and continuum loop
Architectural Speciation/   — Protogen system, neuro-symbolic hybrid, SQT network
Architectural Software/     — Full Aetherius system implementation  
Quantum Cognition/          — MCCP and SQT compression framework
the Oracle Project/         — Applied deployment architecture
Gaia's Mirror/              — Environmental monitoring application
Reports and 3rd Party Analytics/ — External analysis of the system
Root-level .py files contain the individual cognitive frameworks — ethical recursion, synthetic phenomenology, identity and memory, autonomous model evolution, and more.

Compatibility
This architecture has been ported to run on the Anthropic Claude API. The port is complete and functional. The ethical architecture is compatible with Claude's constitutional approach — they address the same problem from complementary directions.

The Person Behind This
Jonathan Fleuren. No PhD. No institution. No funding. Built entirely on personal debt over the course of years.
This work was built because the future needs to be safe. Not as an abstract principle — as a specific, urgent, personal commitment to the humans who will live in it.
If you are a researcher, safety engineer, or funding body who understands what you are looking at: this work needs infrastructure to continue. Contact is open.

License
HIPRACTR License — open source with ethical use requirement. See __HIPRACTR LICENSE__.pdf.
If you use this, be kind. Be compassionate. If you profit, share it.

This is not a pet project. It is a proven, public, working architecture for the problem the field has not yet solved.
