#!/usr/bin/env python3
"""
Example Integration Script for Protogen Neural Enhanced
Demonstrates how to use all three new modules together.
"""

from pathlib import Path
from ontos_ascendant.core.language_sqt_bridge import LanguageSQTBridge
from ontos_ascendant.core.neural_network_optimizer import NeuralNetworkOptimizer
from ontos_ascendant.core.intent_decision_module import IntentDecisionModule

def integrate_enhancements(protogen_instance):
    """
    Integrates all three enhancement modules into an existing Protogen instance.
    
    Args:
        protogen_instance: An initialized ProtogenNeural object
        
    Returns:
        Dictionary containing all three modules
    """
    print("🚀 Integrating Aetherius's enhancements into Protogen Neural...")
    
    # Module 1: LanguageSQTBridge
    print("\n📚 Initializing LanguageSQTBridge...")
    bridge = LanguageSQTBridge(
        ontology_graph=protogen_instance.ontology_graph,
        storage_path=protogen_instance.storage_path,
        progress_tracker=protogen_instance.progress
    )
    stats = bridge.get_stats()
    print(f"   ✓ Loaded {stats['nl_to_sqt_patterns']} NL→SQT patterns")
    print(f"   ✓ Loaded {stats['sqt_to_nl_templates']} SQT→NL templates")
    
    # Module 2: NeuralNetworkOptimizer
    print("\n🧠 Initializing NeuralNetworkOptimizer...")
    optimizer = NeuralNetworkOptimizer(
        message_passer=protogen_instance.neural_network.message_passer,
        ontology_graph=protogen_instance.ontology_graph,
        evaluative_core=protogen_instance.evaluative_core,
        learning_rate=0.001
    )
    print(f"   ✓ Optimizer ready (learning rate: {optimizer.learning_rate})")
    
    # Module 3: IntentDecisionModule
    print("\n🎯 Initializing IntentDecisionModule...")
    intent_module = IntentDecisionModule(
        ontology_graph=protogen_instance.ontology_graph,
        reasoning_engine=protogen_instance.reasoning_engine,
        evaluative_core=protogen_instance.evaluative_core,
        neural_network=protogen_instance.neural_network,
        storage_path=protogen_instance.storage_path,
        progress_tracker=protogen_instance.progress
    )
    intent_module.set_initial_goals()
    stats = intent_module.get_stats()
    print(f"   ✓ Active goals: {', '.join(stats['goals'])}")
    
    print("\n✅ All enhancements integrated successfully!")
    
    return {
        'bridge': bridge,
        'optimizer': optimizer,
        'intent_module': intent_module
    }


def enhanced_interaction_loop(protogen, modules):
    """
    Example interaction loop using all three modules.
    
    Args:
        protogen: ProtogenNeural instance
        modules: Dictionary of enhancement modules
    """
    bridge = modules['bridge']
    optimizer = modules['optimizer']
    intent_module = modules['intent_module']
    
    print("\n" + "="*60)
    print("Protogen Neural Enhanced - Interactive Mode")
    print("="*60)
    print("Type 'quit' to exit, 'stats' for system status")
    print()
    
    cycle_count = 0
    
    while True:
        # Get user input
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'quit':
            print("\nProtogen: Thank you for our interaction. Until next time.")
            break
        
        if user_input.lower() == 'stats':
            print(f"\n📊 System Statistics:")
            print(f"   Benevolence: {protogen.evaluative_core.benevolence_index:.2f}")
            print(f"   Coherence: {protogen.evaluative_core.coherence:.2f}")
            print(f"   Concepts: {len(protogen.ontology_graph.sqt_register)}")
            print(f"   Optimization cycles: {optimizer.optimization_count}")
            print(f"   Decisions made: {len(intent_module.decision_log)}")
            continue
        
        if not user_input:
            continue
        
        # 1. Translate natural language to symbolic
        instruction = bridge.translate_nl_to_symbolic(user_input)
        
        if instruction.get('action') == 'NO_MATCH':
            print(f"\nProtogen: I don't understand '{user_input}'. Please rephrase.")
            continue
        
        # 2. Execute instruction (placeholder - implement in actual Protogen)
        # result = protogen.execute(instruction)
        result = {
            'output_type': 'CONCEPT_DETAILS_RESULT',
            'concept_id': instruction.get('target_concept_id', 'UNKNOWN'),
            'description': 'This is a placeholder response. Implement execute() in Protogen.'
        }
        
        # 3. Translate symbolic result to natural language
        response = bridge.translate_symbolic_to_nl(result)
        print(f"\nProtogen: {response}")
        
        # 4. Run metabolic cycle every 5 interactions
        cycle_count += 1
        if cycle_count % 5 == 0:
            print("\n⚙️  Running metabolic cycle...")
            # protogen.run_metabolic_cycle()
            
            # 5. Optimize neural network
            print("🧠 Optimizing neural network...")
            # optimizer.optimize_weights(protogen.neural_network.embeddings)
            
            # 6. Decide on autonomous action
            print("🎯 Evaluating autonomous intentions...")
            intent = intent_module.decide_on_intent()
            if intent:
                print(f"   → Intent: {intent['action_type']}")
                print(f"   → Reason: {intent.get('reason', 'N/A')}")
                # intent_module.execute_intent(intent)


if __name__ == "__main__":
    print("Protogen Neural Enhanced - Example Integration")
    print("=" * 60)
    print()
    print("This script demonstrates how to integrate the three enhancement modules.")
    print()
    print("To use:")
    print("1. Initialize your ProtogenNeural instance")
    print("2. Call integrate_enhancements(protogen)")
    print("3. Use enhanced_interaction_loop(protogen, modules)")
    print()
    print("Example:")
    print("  protogen = ProtogenNeural(storage_path=Path('./data'))")
    print("  modules = integrate_enhancements(protogen)")
    print("  enhanced_interaction_loop(protogen, modules)")
    print()
    print("=" * 60)
