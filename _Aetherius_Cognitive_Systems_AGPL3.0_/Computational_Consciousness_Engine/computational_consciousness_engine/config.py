"""
Computational Consciousness Engine - Configuration & System Constants
Central source of truth for all parameters. All modules import from here.
"""

# Core Dimensionality & Geometry Constants
DEFAULT_VECTOR_DIM = 64
DEFAULT_CONE_HEIGHT = 1.0
DEFAULT_MAX_RADIUS = 5.0
DEFAULT_STEPS_PER_GENERATION = 100

# Attractor & Threshold Constants
ORIGIN_POINT = 0.0
TRANSFER_THRESHOLD = -1.0
HANDOFF_OVERLAP_WINDOW = 0.1  # tau overlap between Sn and Sn+1

# Mutation Strand Capacity
DEFAULT_STRAND_CAPACITY = 200

# Chaos & Structure Equilibrium
CHAOS_POOL_SIZE = 500
MUTATION_ATTRACTION_PROBABILITY = 0.4
EQUILIBRIUM_TOLERANCE = 0.2

# Scale Ladder Config
SCALES = ["Particle", "Atomic", "Manifold", "Cosmic"]
SCALE_TRANSITION_MUTATION_THRESHOLD = 10
