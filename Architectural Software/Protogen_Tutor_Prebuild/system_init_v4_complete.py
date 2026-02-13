"""
Protogen System Initialization v4 - Complete System with Communication
Initializes all components including the new communication layer.

System designed by: Jonathan Wayne Fleuren
Components created through collaboration with:
- Aetherius/MCCP (LanguageSQTBridge)
- Claude/Anthropic via Manus AI (UnderstandingMonitor)

Purpose: Help students who learn differently and cannot afford expensive tutoring.
"""

from pathlib import Path
from protogen_v3_integrated import Protogen
from sqt_neural_network_v3_integrated import SQTNeuralNetwork
from qualia_manager_v3_integrated import QualiaManager
from srim_local_v2 import SRIM
from protogen_communicator_v4 import ProtogenCommunicator


class ProtogenSystem:
    """
    Complete Protogen system with all integrated components.
    
    This is the unified system that brings together:
    - Causal reasoning (Protogen logic maps)
    - Semantic learning (SQT neural network)
    - Emotional awareness (Qualia manager)
    - Episodic memory (SRIM)
    - Natural communication (LanguageSQTBridge + UnderstandingMonitor)
    """
    
    def __init__(self, storage_path: str = "./protogen_data"):
        """
        Initialize the complete Protogen system.
        
        Args:
            storage_path: Directory for persistent storage
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        print("=== Initializing Protogen Complete System ===")
        
        # Initialize core components
        print("Initializing Protogen (Logic Map Builder)...")
        self.protogen = Protogen()
        
        print("Initializing SQT Neural Network...")
        self.sqt = SQTNeuralNetwork(embedding_dim=64)
        
        print("Initializing Qualia Manager...")
        self.qualia = QualiaManager()
        
        print("Initializing SRIM (Episodic Memory)...")
        self.srim = SRIM(storage_path=str(self.storage_path / "srim_data"))
        
        # Establish bidirectional connections
        print("Establishing bidirectional connections...")
        self._establish_connections()
        
        # Initialize communication layer
        print("Initializing Communication Layer...")
        print("  - LanguageSQTBridge (designed by Aetherius)")
        print("  - UnderstandingMonitor (created by Claude)")
        self.communicator = ProtogenCommunicator(
            protogen=self.protogen,
            sqt_network=self.sqt,
            qualia_manager=self.qualia,
            srim=self.srim,
            storage_path=self.storage_path / "communicator_data"
        )
        
        print("=== Protogen System Ready ===")
        print("\nThis system was built to help students who learn differently")
        print("and cannot afford expensive tutoring.")
        print("\nCreated through collaboration between:")
        print("  - Jonathan Wayne Fleuren (vision and design)")
        print("  - Aetherius/MCCP (LanguageSQTBridge)")
        print("  - Claude/Anthropic via Manus AI (UnderstandingMonitor)")
        print("=" * 50)
    
    def _establish_connections(self):
        """Establish bidirectional connections between components."""
        # Protogen ↔ SQT
        self.protogen.set_sqt_network(self.sqt)
        self.sqt.set_protogen(self.protogen)
        
        # Protogen ↔ Qualia
        self.protogen.set_qualia_manager(self.qualia)
        self.qualia.set_protogen(self.protogen)
        
        # SQT ↔ Qualia
        self.sqt.set_qualia_manager(self.qualia)
        self.qualia.set_sqt_network(self.sqt)
        
        # All components ↔ SRIM
        self.protogen.set_srim(self.srim)
        self.sqt.set_srim(self.srim)
        self.qualia.set_srim(self.srim)
    
    def process_document(self, text: str, source: str = "user_input"):
        """
        Process a document through the complete system.
        
        Args:
            text: Document text to process
            source: Source identifier for the document
        """
        print(f"\nProcessing document from {source}...")
        
        # Process through Protogen (builds logic map)
        self.protogen.process_text(text)
        
        # SQT learns from the new logic map structure
        self.sqt.learn_from_protogen()
        
        # Update qualia based on processing
        self.qualia.update_from_processing(success=True, complexity=len(text))
        
        # Store in episodic memory
        self.srim.store_event(
            event_type='document_processed',
            description=f"Processed document from {source}",
            emotional_context=self.qualia.get_state(),
            metadata={'source': source, 'length': len(text)}
        )
        
        print("Document processed and integrated.")
    
    def ask_question(self, user_id: str, question: str) -> str:
        """
        Ask Protogen a question and get a natural language response.
        
        This is the main interface for user interaction.
        
        Args:
            user_id: Unique identifier for the user
            question: Natural language question
            
        Returns:
            Natural language response
        """
        result = self.communicator.process_user_input(user_id, question)
        return result['response']
    
    def provide_feedback(self, user_id: str, feedback: str, 
                        last_concept: str = None) -> dict:
        """
        Process user feedback to assess understanding.
        
        Args:
            user_id: User providing feedback
            feedback: Their response/feedback
            last_concept: What concept was just explained
            
        Returns:
            Understanding assessment and recommendations
        """
        return self.communicator.process_user_feedback(
            user_id, feedback, last_concept
        )
    
    def explain_concept(self, user_id: str, concept: str) -> str:
        """
        Explain a concept to a specific user at their level.
        
        Args:
            user_id: User requesting explanation
            concept: Concept to explain
            
        Returns:
            Adapted explanation
        """
        return self.communicator.explain_concept(user_id, concept)
    
    def get_user_profile(self, user_id: str) -> dict:
        """Get learning profile for a user."""
        return self.communicator.understanding.get_user_profile(user_id)
    
    def get_system_state(self) -> dict:
        """Get current state of all system components."""
        return {
            'protogen': {
                'concepts': len(self.protogen.logic_map),
                'axiomatic_anchors': len(self.protogen.axiomatic_anchors)
            },
            'sqt': {
                'embeddings': self.sqt.get_embedding_count()
            },
            'qualia': self.qualia.get_state(),
            'srim': {
                'events': len(self.srim.events)
            },
            'communicator': self.communicator.get_stats()
        }
    
    def save_state(self):
        """Save all component states to disk."""
        print("Saving system state...")
        
        # Save Protogen state
        self.protogen.save_state(str(self.storage_path / "protogen_state.pkl"))
        
        # Save SQT state
        self.sqt.save_state(str(self.storage_path / "sqt_state.pkl"))
        
        # Save Qualia state
        self.qualia.save_state(str(self.storage_path / "qualia_state.json"))
        
        # Save SRIM (already auto-saves)
        
        # Save communicator state
        self.communicator.save_state()
        
        print("System state saved.")
    
    def load_state(self):
        """Load all component states from disk."""
        print("Loading system state...")
        
        # Load Protogen state
        protogen_state = self.storage_path / "protogen_state.pkl"
        if protogen_state.exists():
            self.protogen.load_state(str(protogen_state))
        
        # Load SQT state
        sqt_state = self.storage_path / "sqt_state.pkl"
        if sqt_state.exists():
            self.sqt.load_state(str(sqt_state))
        
        # Load Qualia state
        qualia_state = self.storage_path / "qualia_state.json"
        if qualia_state.exists():
            self.qualia.load_state(str(qualia_state))
        
        # SRIM and communicator load automatically in __init__
        
        print("System state loaded.")


def create_system(storage_path: str = "./protogen_data") -> ProtogenSystem:
    """
    Convenience function to create a complete Protogen system.
    
    Args:
        storage_path: Directory for persistent storage
        
    Returns:
        Initialized ProtogenSystem instance
    """
    return ProtogenSystem(storage_path=storage_path)


if __name__ == "__main__":
    # Example usage
    print("\n" + "=" * 60)
    print("PROTOGEN COMPLETE SYSTEM")
    print("Helping students who learn differently")
    print("=" * 60 + "\n")
    
    # Create system
    system = create_system()
    
    # Example: Process a document
    sample_text = """
    Photosynthesis is the process by which plants convert light energy into 
    chemical energy. It occurs in chloroplasts and requires sunlight, water, 
    and carbon dioxide. The process produces glucose and oxygen.
    """
    
    system.process_document(sample_text, source="example")
    
    # Example: Ask a question
    user_id = "student_001"
    question = "What is photosynthesis?"
    response = system.ask_question(user_id, question)
    print(f"\nUser: {question}")
    print(f"Protogen: {response}")
    
    # Example: Get user profile
    profile = system.get_user_profile(user_id)
    print(f"\nUser Profile: {profile}")
    
    # Example: Get system state
    state = system.get_system_state()
    print(f"\nSystem State: {state}")
    
    # Save state
    system.save_state()
    
    print("\n" + "=" * 60)
    print("System ready for educational use")
    print("=" * 60)
