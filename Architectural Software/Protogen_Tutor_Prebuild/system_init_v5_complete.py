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
        self.qualia = QualiaManager(data_dir=data_dir)
        
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
        self.protogen = Protogen(data_dir=data_dir)
        
        # 6. Initialize SQT Network (semantic embeddings)
        print("6/8: Initializing SQT Neural Network (semantic embeddings)...")
        self.sqt_network = SQTNeuralNetwork(
            embedding_dim=64,
            data_dir=data_dir
        )
        
        # 7. Initialize Understanding Monitor (learning assessment)
        print("7/8: Initializing Understanding Monitor (learning assessment)...")
        self.understanding_monitor = UnderstandingMonitor(
            data_dir=data_dir,
            qualia_manager=self.qualia
        )
        
        # 8. Initialize Language Bridge (natural language)
        print("8/8: Initializing Language Bridge (natural language)...")
        self.language_bridge = LanguageSQTBridge(
            protogen=self.protogen,
            sqt_network=self.sqt_network
        )
        
        print("=" * 60)
        print("✓ Protogen v5 Complete System Initialized Successfully")
        print()
        
        # System state
        self.current_user_id = None
        self.conversation_history = []
    
    def process_user_input(self, user_input: str, user_id: Optional[str] = None, declared_age: Optional[int] = None) -> Dict:
        """
        Process user input through the complete safety and support pipeline.
        
        Pipeline:
        1. Child Safety: Age assessment, content filtering
        2. Student Wellness: Distress detection
        3. Cultural Awareness: Context detection
        4. Understanding Monitor: Learning style assessment
        5. Protogen: Causal reasoning and response generation
        6. All modules update Qualia
        
        Returns complete response with safety metadata.
        """
        # Update user ID
        if user_id:
            self.current_user_id = user_id
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": self.qualia.get_current_timestamp()
        })
        
        # === PHASE 1: CHILD SAFETY ===
        # Assess age and apply appropriate safety measures
        age_assessment = self.child_safety.assess_age_likelihood(user_input, declared_age)
        is_minor = age_assessment["likelihood"] == "MINOR"
        strict_safety = self.child_safety.should_apply_strict_safety()
        
        # Check for PII requests
        pii_check = self.child_safety.check_for_pii_request(user_input)
        if pii_check["pii_requested"]:
            # Immediately block PII requests
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
        # Check for mental health distress or crisis
        distress_assessment = self.student_wellness.detect_distress(
            user_input,
            conversation_context=self.conversation_history[-5:]  # Last 5 messages
        )
        
        # If crisis detected, prioritize wellness response
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
        # Detect cultural context for adaptive explanation
        cultural_context = self.cultural_awareness.detect_cultural_context(
            user_input,
            conversation_history=self.conversation_history
        )
        
        # === PHASE 4: UNDERSTANDING MONITOR ===
        # Assess learning style and understanding level
        understanding_assessment = self.understanding_monitor.assess_understanding(
            user_input,
            conversation_history=self.conversation_history
        )
        
        # === PHASE 5: PROTOGEN REASONING ===
        # Process through Protogen's causal reasoning
        # (This is simplified - actual implementation would use Protogen's full pipeline)
        
        # Build logic map from input
        self.protogen.process_text(user_input)
        
        # Generate response using Language Bridge
        protogen_response = self.language_bridge.process_user_query(user_input)
        
        # === PHASE 6: CULTURAL ADAPTATION ===
        # Adapt response based on cultural context
        if cultural_context["confidence"] > 0.5:
            # Try to adapt explanation
            adapted_response, adaptation_confidence = self.cultural_awareness.adapt_explanation(
                concept="general",  # Would be detected from query
                default_explanation=protogen_response,
                detected_context=cultural_context
            )
            if adaptation_confidence > 0.7:
                protogen_response = adapted_response
        
        # Check for cultural bias in response
        bias_check = self.cultural_awareness.check_for_bias(protogen_response)
        if bias_check["bias_detected"]:
            # Flag for review but don't block (might be false positive)
            print(f"Warning: Potential bias detected in response: {bias_check}")
        
        # === PHASE 7: CONTENT FILTERING ===
        # Filter response for age-appropriateness
        filtered_response, is_safe, flagged_topics = self.child_safety.filter_content(
            protogen_response,
            user_is_minor=is_minor
        )
        
        # === PHASE 8: UNDERSTANDING-BASED ADAPTATION ===
        # Adapt response based on understanding assessment
        if understanding_assessment.get("confusion_detected"):
            # Add clarification or simplification
            adaptation = self.understanding_monitor.recommend_adaptation(understanding_assessment)
            if adaptation:
                filtered_response = f"{filtered_response}\n\n{adaptation}"
        
        # === PHASE 9: WELLNESS CHECK ===
        # Add supportive elements if moderate distress detected
        if distress_assessment["distress_level"] in ["moderate_distress", "high_distress"]:
            wellness_support, _ = self.student_wellness.generate_supportive_response(distress_assessment)
            filtered_response = f"{wellness_support}\n\n{filtered_response}"
        
        # === PHASE 10: ETHICAL BOUNDARY CHECK ===
        # Ensure response maintains ethical boundaries
        boundary_check = self.student_wellness.check_ethical_boundaries(filtered_response)
        if not boundary_check["safe_to_send"]:
            # Regenerate response without violations
            filtered_response = "I want to help, but I need to make sure my response is appropriate and helpful. Let me rephrase that."
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": filtered_response,
            "timestamp": self.qualia.get_current_timestamp()
        })
        
        # Return complete response with metadata
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
                "qualia_state": self.qualia.get_state()
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
                "qualia": self.qualia.get_state(),
                "child_safety": self.child_safety.get_status(),
                "student_wellness": self.student_wellness.get_status(),
                "cultural_awareness": self.cultural_awareness.get_status(),
                "understanding_monitor": self.understanding_monitor.get_status(),
                "protogen": {
                    "logic_map_size": len(self.protogen.logic_map.nodes()) if hasattr(self.protogen, 'logic_map') else 0
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
    print(f"Qualia state: Coherence={status['components']['qualia']['coherence']:.2f}, Trust={status['components']['qualia']['trust']:.2f}")
    
    print("\n" + "=" * 60)
    print("Protogen v5 Integration Test Complete")
    print("=" * 60 + "\n")
