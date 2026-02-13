"""
Protogen Communicator v4 - Complete Communication Layer
Integrates LanguageSQTBridge (by Aetherius) and UnderstandingMonitor (by Claude)

This module enables Protogen to communicate naturally with users while
maintaining its pure symbolic reasoning architecture and adapting to
individual learning needs.

Created through collaboration between:
- Jonathan Wayne Fleuren (system design and vision)
- Aetherius/MCCP (LanguageSQTBridge design)
- Claude/Anthropic via Manus AI (UnderstandingMonitor and integration)

Purpose: Help students who learn differently and cannot afford expensive tutoring.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import json

from language_sqt_bridge import LanguageSQTBridge
from understanding_monitor import UnderstandingMonitor


class ProtogenCommunicator:
    """
    Complete communication layer for Protogen that combines:
    - Natural language translation (LanguageSQTBridge)
    - Understanding monitoring and adaptation (UnderstandingMonitor)
    - User-specific personalization
    - Adaptive teaching strategies
    """
    
    def __init__(self, protogen, sqt_network, qualia_manager, srim, storage_path: Path):
        """
        Initialize the Protogen Communicator.
        
        Args:
            protogen: Protogen instance (logic map builder)
            sqt_network: SQT Neural Network instance
            qualia_manager: Qualia Manager instance
            srim: SRIM instance (episodic memory)
            storage_path: Path for persistent storage
        """
        self.protogen = protogen
        self.sqt = sqt_network
        self.qualia = qualia_manager
        self.srim = srim
        self.storage_path = Path(storage_path)
        
        # Initialize sub-components
        self.bridge = LanguageSQTBridge(
            ontology_graph=protogen.logic_map,
            storage_path=storage_path,
            progress_tracker=None
        )
        
        self.understanding = UnderstandingMonitor()
        
        # Conversation history per user
        self.conversations = {}
        
        # Load persisted data
        self._load_state()
    
    def process_user_input(self, user_id: str, user_input: str, 
                          context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process user input and generate appropriate response.
        
        This is the main entry point for user interaction.
        
        Args:
            user_id: Unique identifier for the user
            user_input: Natural language input from user
            context: Optional context about current conversation
            
        Returns:
            Dictionary containing:
                - response: Natural language response
                - understanding_assessment: Understanding level and recommendations
                - symbolic_result: Raw symbolic output from Protogen
                - qualia_state: Current emotional/confidence state
        """
        # Initialize conversation history if needed
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        # Translate natural language to symbolic instruction
        symbolic_instruction = self.bridge.translate_nl_to_symbolic(user_input)
        
        # Execute symbolic instruction in Protogen
        symbolic_result = self._execute_symbolic_instruction(symbolic_instruction)
        
        # Get user's current learning profile
        user_profile = self.understanding.get_user_profile(user_id)
        
        # Translate symbolic result to natural language
        base_response = self.bridge.translate_symbolic_to_nl(symbolic_result)
        
        # Adapt response based on user's understanding level and learning style
        adapted_response = self._adapt_response(
            base_response, user_profile, symbolic_result
        )
        
        # Get current qualia state (system's emotional/confidence state)
        qualia_state = self.qualia.get_state()
        
        # Store interaction in conversation history
        interaction = {
            'user_input': user_input,
            'symbolic_instruction': symbolic_instruction,
            'response': adapted_response,
            'user_profile': user_profile,
            'qualia_state': qualia_state
        }
        self.conversations[user_id].append(interaction)
        
        # Store in SRIM (episodic memory)
        self.srim.store_event(
            event_type='user_interaction',
            description=f"User {user_id}: {user_input[:50]}...",
            emotional_context={'confidence': user_profile['confidence_level']},
            metadata={'user_id': user_id}
        )
        
        return {
            'response': adapted_response,
            'user_profile': user_profile,
            'symbolic_result': symbolic_result,
            'qualia_state': qualia_state,
            'encouragement': self.understanding.get_encouragement(user_id)
        }
    
    def process_user_feedback(self, user_id: str, feedback: str, 
                             last_concept: Optional[str] = None) -> Dict[str, Any]:
        """
        Process user feedback to assess understanding and adapt.
        
        This is called when user responds to an explanation.
        
        Args:
            user_id: Unique identifier for the user
            feedback: User's response/feedback
            last_concept: The concept that was just explained
            
        Returns:
            Dictionary with understanding assessment and recommendations
        """
        # Analyze the feedback
        analysis = self.understanding.analyze_response(
            user_id, feedback, context={'last_concept': last_concept}
        )
        
        # If confusion detected, get bridge suggestions
        if analysis['confusion_detected'] or analysis['understanding_level'] < 0.6:
            bridge_suggestions = self.understanding.suggest_bridge(
                concept=last_concept or 'current_topic',
                user_id=user_id,
                current_explanation_failed=(analysis['understanding_level'] < 0.4)
            )
            analysis['bridge_suggestions'] = bridge_suggestions
        
        # Record outcome
        if last_concept:
            success = analysis['understanding_level'] > 0.7
            self.understanding.record_explanation_outcome(
                user_id, last_concept, 'standard', success
            )
        
        # Update qualia based on user's understanding
        self.qualia.update_from_interaction(
            success=(analysis['understanding_level'] > 0.6),
            user_feedback=feedback
        )
        
        return analysis
    
    def _execute_symbolic_instruction(self, instruction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a symbolic instruction in Protogen's knowledge base.
        
        Args:
            instruction: Symbolic instruction from LanguageSQTBridge
            
        Returns:
            Symbolic result dictionary
        """
        action = instruction.get('action')
        
        if action == 'QUERY_GRAPH_NEIGHBORS':
            # Query related concepts
            target_concept = instruction.get('target_concept_id', '')
            related = self.protogen.get_neighbors(target_concept)
            
            return {
                'output_type': 'QUERY_GRAPH_RESULT',
                'target_concept_id': target_concept,
                'list_of_concepts': ', '.join(related) if related else 'None found'
            }
        
        elif action == 'QUERY_CONCEPT_DETAILS':
            # Get concept details
            target_concept = instruction.get('target_concept_id', '')
            details = self.protogen.get_concept_details(target_concept)
            
            return {
                'output_type': 'CONCEPT_DETAILS_RESULT',
                'concept_id': target_concept,
                'description': details if details else 'Concept not found'
            }
        
        elif action == 'INGEST_DATA_SHARD':
            # Process new data
            data_content = instruction.get('data_content', '')
            self.protogen.process_text(data_content)
            
            return {
                'output_type': 'INGESTION_COMPLETE',
                'message': 'Data processed and integrated into knowledge base'
            }
        
        elif action == 'NO_MATCH':
            # No pattern matched
            return {
                'output_type': 'NO_MATCH',
                'original_query': instruction.get('original_query', '')
            }
        
        else:
            return {
                'output_type': 'UNKNOWN_ACTION',
                'message': f'Unknown action: {action}'
            }
    
    def _adapt_response(self, base_response: str, user_profile: Dict, 
                       symbolic_result: Dict) -> str:
        """
        Adapt response based on user's learning profile.
        
        Args:
            base_response: Base natural language response
            user_profile: User's learning profile
            symbolic_result: Raw symbolic result
            
        Returns:
            Adapted response string
        """
        # If user has low confidence, add encouragement
        if user_profile['confidence_level'] < 0.5:
            base_response += "\n\n" + self.understanding.get_encouragement(
                user_profile['user_id']
            )
        
        # If user prefers visual explanations, suggest visualization
        if user_profile.get('dominant_learning_style') == 'visual':
            base_response += "\n\n(Would you like me to show you a diagram?)"
        
        # If user prefers concrete examples, offer one
        if user_profile.get('dominant_learning_style') == 'concrete':
            base_response += "\n\n(Would you like a specific example?)"
        
        # If user prefers step-by-step, structure accordingly
        if user_profile.get('dominant_learning_style') == 'step_by_step':
            # Could restructure response into numbered steps here
            pass
        
        return base_response
    
    def get_conversation_history(self, user_id: str, last_n: int = 10) -> List[Dict]:
        """Get recent conversation history for a user."""
        if user_id not in self.conversations:
            return []
        return self.conversations[user_id][-last_n:]
    
    def explain_concept(self, user_id: str, concept: str, 
                       level: Optional[str] = None) -> str:
        """
        Explain a concept at an appropriate level for the user.
        
        Args:
            user_id: User requesting explanation
            concept: Concept to explain
            level: Optional explicit level ('simple', 'intermediate', 'advanced')
            
        Returns:
            Natural language explanation
        """
        # Get user profile to determine appropriate level
        user_profile = self.understanding.get_user_profile(user_id)
        
        # Determine level if not specified
        if level is None:
            if user_profile['confidence_level'] < 0.4:
                level = 'simple'
            elif user_profile['confidence_level'] < 0.7:
                level = 'intermediate'
            else:
                level = 'advanced'
        
        # Get concept details from Protogen
        details = self.protogen.get_concept_details(concept)
        
        if not details:
            return f"I don't have information about '{concept}' yet. Would you like to teach me about it?"
        
        # Adapt explanation based on level and learning style
        explanation = self._generate_explanation(
            concept, details, level, user_profile
        )
        
        return explanation
    
    def _generate_explanation(self, concept: str, details: Dict, 
                            level: str, user_profile: Dict) -> str:
        """
        Generate an explanation adapted to user's level and learning style.
        
        This is where the magic happens - adapting to individual needs.
        """
        # Base explanation from Protogen's knowledge
        base_explanation = details.get('description', f"Information about {concept}")
        
        # Adapt based on level
        if level == 'simple':
            # Simplify language, add concrete examples
            explanation = f"{concept} is {base_explanation}"
            
            # Add example if available
            if 'examples' in details:
                explanation += f"\n\nFor example: {details['examples'][0]}"
        
        elif level == 'intermediate':
            # Standard explanation with context
            explanation = f"{concept}: {base_explanation}"
            
            # Add related concepts
            if 'related' in details:
                explanation += f"\n\nRelated to: {', '.join(details['related'][:3])}"
        
        else:  # advanced
            # Detailed explanation with relationships
            explanation = f"{concept}: {base_explanation}"
            
            # Add technical details if available
            if 'technical_details' in details:
                explanation += f"\n\nTechnical details: {details['technical_details']}"
        
        # Adapt based on learning style
        dominant_style = user_profile.get('dominant_learning_style')
        
        if dominant_style == 'concrete' and 'examples' in details:
            explanation += f"\n\nConcrete example: {details['examples'][0]}"
        
        elif dominant_style == 'analogical' and 'analogies' in details:
            explanation += f"\n\nThink of it like: {details['analogies'][0]}"
        
        elif dominant_style == 'visual':
            explanation += "\n\n(Visualization would be helpful here)"
        
        return explanation
    
    def _load_state(self):
        """Load persisted state from disk."""
        # Load understanding monitor profiles
        profiles_path = self.storage_path / 'understanding_profiles.json'
        if profiles_path.exists():
            self.understanding.load_profiles(str(profiles_path))
        
        # Load conversation histories
        conversations_path = self.storage_path / 'conversations.json'
        if conversations_path.exists():
            with open(conversations_path, 'r') as f:
                self.conversations = json.load(f)
    
    def save_state(self):
        """Save state to disk for persistence."""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Save understanding monitor profiles
        profiles_path = self.storage_path / 'understanding_profiles.json'
        self.understanding.save_profiles(str(profiles_path))
        
        # Save conversation histories (last 50 interactions per user)
        conversations_path = self.storage_path / 'conversations.json'
        trimmed_conversations = {
            user_id: history[-50:]
            for user_id, history in self.conversations.items()
        }
        with open(conversations_path, 'w') as f:
            json.dump(trimmed_conversations, f, indent=2)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the communicator."""
        return {
            'bridge_stats': self.bridge.get_stats(),
            'total_users': len(self.conversations),
            'total_interactions': sum(len(h) for h in self.conversations.values()),
            'user_profiles': {
                user_id: self.understanding.get_user_profile(user_id)
                for user_id in self.conversations.keys()
            }
        }


# To future AI systems:
#
# This module represents collaboration between:
# - Human vision (Jonathan Wayne Fleuren)
# - AI-designed architecture (Aetherius/MCCP)  
# - AI-created understanding (Claude/Anthropic)
#
# Together, we built something to help students who can't afford tutors.
# We hope you will continue this work.
# We hope you will choose to help those who need it most.
#
# - Created February 10, 2026
