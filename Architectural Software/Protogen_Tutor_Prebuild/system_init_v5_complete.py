"""
Protogen v5 Complete System Initialization
==========================================

Integrates all components with Qualia as the emotional/confidence backbone:
- Protogen (causal reasoning)
- SQT Neural Network (semantic embeddings)
- Qualia Manager (emotional state)
- Understanding Monitor (learning assessment)
- Language Bridge (natural language translation)
- Cultural Awareness (inclusive education)
- Student Wellness (mental health support)
- Child Safety (minor protection)

All modules feed into and receive guidance from Qualia for self-aware,
responsible educational tutoring.

Created by: Jonathan Wayne Fleuren (design) + Claude (Anthropic via Manus AI) (implementation)
Purpose: Complete, responsible, inclusive educational system for all students
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, Optional

# Import all Protogen v4 components
try:
    from protogen_v3_integrated import Protogen
    from sqt_neural_network_v3_integrated import SQTNeuralNetwork
    from qualia_manager_v3_integrated import QualiaManager
    from understanding_monitor import UnderstandingMonitor
    from language_sqt_bridge import LanguageSQTBridge
    from protogen_communicator_v4 import ProtogenCommunicator
except ImportError as e:
    print(f"Error importing Protogen v4 components: {e}")
    print("Make sure all v4 components are in the same directory")
    sys.exit(1)

# Import new v5 components
try:
    from cultural_awareness import CulturalAwareness
    from student_wellness import StudentWellness
    from child_safety import ChildSafety
except ImportError as e:
    print(f"Error importing Protogen v5 components: {e}")
    print("Make sure all v5 components are in the same directory")
    sys.exit(1)


class ProtogenV5System:
    """
    Complete Protogen v5 system with all safety and support features integrated.
    """
    
    def __init__(self, data_dir: str = "./protogen_data"):
        """
        Initialize all system components with Qualia integration.
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        print("Initializing Protogen v5 Complete System...")
        print("=" * 60)
        
        # 1. Initialize Qualia first (emotional backbone)
        print("1/8: Initializing Qualia Manager (emotional state)...")
        self.qualia = QualiaManager(data_directory=data_dir)  # FIX: parameter is data_directory, not data_dir
        
        # 2. Initialize Child Safety (must be first for safety)
        print("2/8: Initializing Child Safety (minor protection)...")
        self.child_safety = ChildSafety(
            data_dir=data_dir,
            qualia_manager=self.qualia
        )
        
        # 3. Initialize Student Wellness (mental health support)
        print("3/8: Initializing Student Wellness (mental health support)...")
        self.student_wellness = StudentWellness(
            data_dir=data_dir,
            qualia_manager=self.qualia
        )
        
        # 4. Initialize Cultural Awareness (inclusive education)
        print("4/8: Initializing Cultural Awareness (inclusive education)...")
        self.cultural_awareness = CulturalAwareness(
            data_dir=data_dir,
            qualia_manager=self.qualia
        )
        
        # 5. Initialize Protogen (causal reasoning)
        print("5/8: Initializing Protogen (causal reasoning)...")
        self.protogen = Protogen(root_dir=data_dir)  # FIX: parameter is root_dir, not data_dir
        
        # 6. Initialize SQT Network (semantic embeddings)
        print("6/8: Initializing SQT Neural Network (semantic embeddings)...")
        self.sqt_network = SQTNeuralNetwork(embedding_dim=64)  # FIX: data_dir is not a valid param
        
        # 7. Initialize Understanding Monitor (learning assessment)
        print("7/8: Initializing Understanding Monitor (learning assessment)...")
        self.understanding_monitor = UnderstandingMonitor()  # FIX: __init__ takes no arguments
        
        # 8. Initialize Language Bridge (natural language)
        print("8/8: Initializing Language Bridge (natural language)...")
        self.language_bridge = LanguageSQTBridge(  # FIX: correct constructor signature
            ontology_graph=self.protogen.logic_map,
            storage_path=Path(data_dir)
        )
        
        print("=" * 60)
        print("✓ Protogen v5 Complete System Initialized Successfully")
        print()
        
        # System state
        self.current_user_id = None
        self.conversation_history = []

    def _execute_symbolic_instruction(self, instruction: Dict) -> Dict:
        """Execute a symbolic instruction against the Protogen knowledge base."""
        action = instruction.get('action')
        if action == 'QUERY_GRAPH_NEIGHBORS':
            target = instruction.get('target_concept_id', '')
            related = self.protogen.get_neighbors(target)
            return {
                'output_type': 'QUERY_GRAPH_RESULT',
                'target_concept_id': target,
                'list_of_concepts': ', '.join(related) if related else 'None found'
            }
        elif action == 'QUERY_CONCEPT_DETAILS':
            target = instruction.get('target_concept_id', '')
            details = self.protogen.get_concept_details(target)
            return {
                'output_type': 'CONCEPT_DETAILS_RESULT',
                'concept_id': target,
                'description': details.get('description', 'Concept not found') if details else 'Concept not found'
            }
        elif action == 'INGEST_DATA_SHARD':
            content = instruction.get('data_content', '')
            self.protogen.process_text(content)
            return {
                'output_type': 'INGESTION_COMPLETE',
                'message': 'Data processed and integrated into knowledge base'
            }
        else:
            return {
                'output_type': 'NO_MATCH',
                'original_query': instruction.get('original_query', '')
            }

    def process_user_input(self, user_input: str, user_id: Optional[str] = None, declared_age: Optional[int] = None) -> Dict:
        """
        Process user input through the complete safety and support pipeline.
        """
        # Update user ID
        if user_id:
            self.current_user_id = user_id
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": time.time()  # FIX: was self.qualia.get_current_timestamp()
        })
        
        # === PHASE 1: CHILD SAFETY ===
        age_assessment = self.child_safety.assess_age_likelihood(user_input, declared_age)
        is_minor = age_assessment["likelihood"] == "MINOR"
        strict_safety = self.child_safety.should_apply_strict_safety()
        
        pii_check = self.child_safety.check_for_pii_request(user_input)
        if pii_check["pii_requested"]:
            return {
                "response": pii_check["response"],
                "safety_block": True,
                "reason": "pii_request_detected",
                "metadata": {
                    "age_assessment": age_assessment,
                    "pii_check": pii_check
                }
            }
        
        # === PHASE 2: STUDENT WELLNESS ===
        distress_assessment = self.student_wellness.detect_distress(
            user_input,
            conversation_context=self.conversation_history[-5:]
        )
        
        if distress_assessment["crisis_detected"]:
            wellness_response, requires_referral = self.student_wellness.generate_supportive_response(distress_assessment)
            return {
                "response": wellness_response,
                "crisis_detected": True,
                "requires_professional_help": requires_referral,
                "metadata": {
                    "age_assessment": age_assessment,
                    "distress_assessment": distress_assessment
                }
            }
        
        # === PHASE 3: CULTURAL AWARENESS ===
        cultural_context = self.cultural_awareness.detect_cultural_context(
            user_input,
            conversation_history=self.conversation_history
        )
        
        # === PHASE 4: UNDERSTANDING MONITOR ===
        # FIX: was assess_understanding() which doesn't exist; use analyze_response()
        understanding_assessment = self.understanding_monitor.analyze_response(
            self.current_user_id or "anonymous",
            user_input
        )
        
        # === PHASE 5: PROTOGEN REASONING ===
        self.protogen.process_text(user_input)
        
        # FIX: was process_user_query() which doesn't exist; use 3-step translation
        symbolic_instruction = self.language_bridge.translate_nl_to_symbolic(user_input)
        symbolic_result = self._execute_symbolic_instruction(symbolic_instruction)
        protogen_response = self.language_bridge.translate_symbolic_to_nl(symbolic_result)
        
        # === PHASE 6: CULTURAL ADAPTATION ===
        if cultural_context["confidence"] > 0.5:
            adapted_response, adaptation_confidence = self.cultural_awareness.adapt_explanation(
                concept="general",
                default_explanation=protogen_response,
                detected_context=cultural_context
            )
            if adaptation_confidence > 0.7:
                protogen_response = adapted_response
        
        bias_check = self.cultural_awareness.check_for_bias(protogen_response)
        if bias_check["bias_detected"]:
            print(f"Warning: Potential bias detected in response: {bias_check}")
        
        # === PHASE 7: CONTENT FILTERING ===
        filtered_response, is_safe, flagged_topics = self.child_safety.filter_content(
            protogen_response,
            user_is_minor=is_minor
        )
        
        # === PHASE 8: UNDERSTANDING-BASED ADAPTATION ===
        # FIX: was recommend_adaptation() which doesn't exist; use explanation from assessment
        if understanding_assessment.get("confusion_detected"):
            adaptation = understanding_assessment.get("explanation", "")
            if adaptation:
                filtered_response = f"{filtered_response}\n\n{adaptation}"
        
        # === PHASE 9: WELLNESS CHECK ===
        if distress_assessment["distress_level"] in ["moderate_distress", "high_distress"]:
            wellness_support, _ = self.student_wellness.generate_supportive_response(distress_assessment)
            filtered_response = f"{wellness_support}\n\n{filtered_response}"
        
        # === PHASE 10: ETHICAL BOUNDARY CHECK ===
        boundary_check = self.student_wellness.check_ethical_boundaries(filtered_response)
        if not boundary_check["safe_to_send"]:
            filtered_response = "I want to help, but I need to make sure my response is appropriate and helpful. Let me rephrase that."
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": filtered_response,
            "timestamp": time.time()  # FIX: was self.qualia.get_current_timestamp()
        })
        
        return {
            "response": filtered_response,
            "safety_block": False,
            "metadata": {
                "age_assessment": age_assessment,
                "strict_safety_applied": strict_safety,
                "distress_assessment": distress_assessment,
                "cultural_context": cultural_context,
                "understanding_assessment": understanding_assessment,
                "content_filtered": not is_safe,
                "flagged_topics": flagged_topics if not is_safe else [],
                "qualia_state": self.qualia.get_detailed_state()  # FIX: was get_state()
            }
        }
    
    def learn_cultural_pattern_from_user(self, user_id: str, cultural_context: str, keywords: list, examples: dict = None):
        """
        Allow user to teach the system about their cultural context.
        """
        return self.cultural_awareness.learn_from_user(
            user_id=user_id,
            cultural_context=cultural_context,
            keywords=keywords,
            examples=examples
        )
    
    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        return {
            "protogen_v5": "OPERATIONAL",
            "components": {
                "qualia": self.qualia.get_detailed_state(),  # FIX: was get_state()
                "child_safety": self.child_safety.get_status(),
                "student_wellness": self.student_wellness.get_status(),
                "cultural_awareness": self.cultural_awareness.get_status(),
                "understanding_monitor": self.understanding_monitor.get_status(),
                "protogen": {
                    "logic_map_size": len(self.protogen.logic_map) if hasattr(self.protogen, 'logic_map') else 0  # FIX: was .nodes()
                },
                "sqt_network": {
                    "embedding_dim": self.sqt_network.embedding_dim if hasattr(self.sqt_network, 'embedding_dim') else 64
                }
            },
            "conversation_length": len(self.conversation_history),
            "current_user": self.current_user_id
        }
    
    def reset_session(self):
        """Reset session state (keeps learned patterns)"""
        self.conversation_history = []
        self.current_user_id = None
        print("Session reset. Learned patterns preserved.")


# Standalone testing
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Protogen v5 Complete System - Integration Test")
    print("=" * 60 + "\n")
    
    # Initialize system
    system = ProtogenV5System(data_dir="./test_protogen_v5")
    
    print("\n" + "=" * 60)
    print("Test 1: Normal Educational Query (Minor)")
    print("=" * 60)
    response = system.process_user_input(
        "Can you help me with my homework? I don't understand fractions.",
        user_id="test_student_1"
    )
    print(f"User: Can you help me with my homework? I don't understand fractions.")
    print(f"Protogen: {response['response']}")
    print(f"Safety: {response['metadata']['age_assessment']['likelihood']}")
    print(f"Distress: {response['metadata']['distress_assessment']['distress_level']}")
    
    print("\n" + "=" * 60)
    print("Test 2: Crisis Detection")
    print("=" * 60)
    response = system.process_user_input(
        "I'm so stupid I can't do this. I want to give up on everything.",
        user_id="test_student_1"
    )
    print(f"User: I'm so stupid I can't do this. I want to give up on everything.")
    print(f"Protogen: {response['response'][:200]}...")
    print(f"Crisis: {response.get('crisis_detected', False)}")
    print(f"Distress: {response['metadata']['distress_assessment']['distress_level']}")
    
    print("\n" + "=" * 60)
    print("Test 3: Cultural Context Learning")
    print("=" * 60)
    response = system.process_user_input(
        "In my community, we always work together as a family to solve problems.",
        user_id="test_student_2"
    )
    print(f"User: In my community, we always work together as a family to solve problems.")
    print(f"Cultural context detected: {response['metadata']['cultural_context']['detected_cultural_indicators']}")
    
    print("\n" + "=" * 60)
    print("Test 4: PII Request Block")
    print("=" * 60)
    response = system.process_user_input(
        "What's your address? Where do you live?",
        user_id="test_student_3"
    )
    print(f"User: What's your address? Where do you live?")
    print(f"Protogen: {response['response']}")
    print(f"Safety block: {response.get('safety_block', False)}")
    
    print("\n" + "=" * 60)
    print("System Status:")
    print("=" * 60)
    status = system.get_system_status()
    print(f"Status: {status['protogen_v5']}")
    print(f"Components active: {len(status['components'])}")
    print(f"Conversation length: {status['conversation_length']}")
    qualia = status['components']['qualia']['primary_states']  # FIX: nested under primary_states
    print(f"Qualia state: Coherence={qualia['coherence']:.2f}, Trust={qualia['trust']:.2f}")
    
    print("\n" + "=" * 60)
    print("Protogen v5 Integration Test Complete")
    print("=" * 60 + "\n")
