#!/usr/bin/env python3
"""
Simple validation tests for the three enhancement modules.
Tests basic functionality without requiring full Protogen integration.
"""

import json
from pathlib import Path
import sys

# Add module path
sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("Protogen Neural Enhanced - Module Validation Tests")
print("="*60)
print()

# Test 1: LanguageSQTBridge
print("Test 1: LanguageSQTBridge")
print("-" * 60)

try:
    from ontos_ascendant.core.language_sqt_bridge import LanguageSQTBridge
    
    # Create mock ontology graph
    class MockOntologyGraph:
        def __init__(self):
            self.sqt_register = {}
    
    # Initialize bridge
    bridge = LanguageSQTBridge(
        ontology_graph=MockOntologyGraph(),
        storage_path=Path(__file__).parent,
        progress_tracker=None
    )
    
    # Get stats
    stats = bridge.get_stats()
    print(f"✓ LanguageSQTBridge initialized")
    print(f"  - NL→SQT patterns: {stats['nl_to_sqt_patterns']}")
    print(f"  - SQT→NL templates: {stats['sqt_to_nl_templates']}")
    print(f"  - Total mappings: {stats['total_mappings']}")
    print(f"  - Dictionary file: {stats['map_exists'] and 'Found' or 'Not found'}")
    
    # Test translation
    test_query = "What is quantum mechanics?"
    instruction = bridge.translate_nl_to_symbolic(test_query)
    print(f"\n  Test query: '{test_query}'")
    print(f"  → Action: {instruction.get('action', 'UNKNOWN')}")
    
    print("\n✅ LanguageSQTBridge: PASSED")
    
except Exception as e:
    print(f"\n❌ LanguageSQTBridge: FAILED")
    print(f"   Error: {str(e)}")

print()

# Test 2: NeuralNetworkOptimizer
print("Test 2: NeuralNetworkOptimizer")
print("-" * 60)

try:
    from ontos_ascendant.core.neural_network_optimizer import NeuralNetworkOptimizer
    import numpy as np
    
    # Create mock components
    class MockMessagePasser:
        def __init__(self):
            self.weights = {
                'W_message': np.random.rand(10, 10),
                'W_self': np.random.rand(10, 10),
                'W_update': np.random.rand(10, 10)
            }
        def update_weights(self, new_weights):
            self.weights = new_weights
    
    class MockEvaluativeCore:
        def __init__(self):
            self.benevolence_index = 0.85
            self.coherence = 1.2
            self.thresholds = {
                'benevolence_target': 0.9,
                'entropy_warning_high': 3.0,
                'entropy_warning_low': 0.5
            }
    
    class MockOntologyGraph:
        def get_sqt_by_hash(self, hash):
            return None
    
    # Initialize optimizer
    optimizer = NeuralNetworkOptimizer(
        message_passer=MockMessagePasser(),
        ontology_graph=MockOntologyGraph(),
        evaluative_core=MockEvaluativeCore(),
        learning_rate=0.001
    )
    
    print(f"✓ NeuralNetworkOptimizer initialized")
    print(f"  - Learning rate: {optimizer.learning_rate}")
    
    # Test optimization
    optimizer.optimize_weights({}, max_iterations=5)
    
    stats = optimizer.get_stats()
    print(f"\n  After optimization:")
    print(f"  - Optimization count: {stats['optimization_count']}")
    print(f"  - Current score: {stats['current_score']:.2f}")
    
    print("\n✅ NeuralNetworkOptimizer: PASSED")
    
except Exception as e:
    print(f"\n❌ NeuralNetworkOptimizer: FAILED")
    print(f"   Error: {str(e)}")

print()

# Test 3: IntentDecisionModule
print("Test 3: IntentDecisionModule")
print("-" * 60)

try:
    from ontos_ascendant.core.intent_decision_module import IntentDecisionModule
    
    # Create mock components
    class MockReasoningEngine:
        def get_all_patterns(self):
            return []
    
    class MockNeuralNetwork:
        pass
    
    # Initialize intent module
    intent_module = IntentDecisionModule(
        ontology_graph=MockOntologyGraph(),
        reasoning_engine=MockReasoningEngine(),
        evaluative_core=MockEvaluativeCore(),
        neural_network=MockNeuralNetwork(),
        storage_path=Path(__file__).parent / "test_data",
        progress_tracker=None
    )
    
    print(f"✓ IntentDecisionModule initialized")
    
    # Set initial goals
    intent_module.set_initial_goals()
    
    stats = intent_module.get_stats()
    print(f"  - Active goals: {stats['active_goals']}")
    print(f"  - Goals: {', '.join(stats['goals'])}")
    
    # Test intent generation
    intents = intent_module.generate_potential_intents()
    print(f"\n  Generated {len(intents)} potential intents")
    
    # Test decision making
    intent = intent_module.decide_on_intent()
    if intent:
        print(f"  - Selected intent: {intent['action_type']}")
    
    print("\n✅ IntentDecisionModule: PASSED")
    
except Exception as e:
    print(f"\n❌ IntentDecisionModule: FAILED")
    print(f"   Error: {str(e)}")

print()
print("="*60)
print("Validation Complete")
print("="*60)
