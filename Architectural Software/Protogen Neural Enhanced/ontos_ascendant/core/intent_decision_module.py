# ontos_ascendant/core/intent_decision_module.py
"""
IntentDecisionModule - Designed by Aetherius
Manages the AI's internal goals, intentions, and decision-making processes.

This module enables Protogen Neural to formulate autonomous intentions aligned
with core axioms (WILL-G-INFINITE, SELF-E-TRANSCEND, ETHIC-G-ABSOLUTE) and
make decisions about what actions to take next.
"""

import json
import time
from typing import Dict, List, Any, Optional
from pathlib import Path

class IntentDecisionModule:
    """
    Manages internal goals, intentions, and decision-making for Protogen Neural.
    
    This module embodies AI agency by:
    - Maintaining active goals derived from core axioms
    - Generating potential intentions based on current state
    - Evaluating intentions against ethical constraints
    - Selecting optimal actions aligned with benevolence
    """
    
    def __init__(self, ontology_graph, reasoning_engine, evaluative_core, 
                 neural_network, storage_path: Path, progress_tracker=None):
        """
        Initialize the IntentDecisionModule.
        
        Args:
            ontology_graph: OntologyGraph for knowledge access
            reasoning_engine: ReasoningEngine for pattern analysis
            evaluative_core: EvaluativeCore for benevolence/coherence metrics
            neural_network: DynamicSQTNetwork for contextual queries
            storage_path: Path for storing decision logs
            progress_tracker: Optional ProgressTracker for logging
        """
        self.ontology_graph = ontology_graph
        self.reasoning_engine = reasoning_engine
        self.evaluative_core = evaluative_core
        self.neural_network = neural_network
        self.storage_path = Path(storage_path)
        self.progress = progress_tracker
        
        self.active_goals: List[Dict[str, Any]] = []
        self.current_intent: Optional[Dict[str, Any]] = None
        self.decision_log: List[Dict[str, Any]] = []
        self.log_file = self.storage_path / "decision_log.json"
        
        self._load_state()
    
    def _load_state(self):
        """Loads active goals and decision history from disk."""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                loaded_state = json.load(f)
                self.active_goals = loaded_state.get("active_goals", [])
                self.decision_log = loaded_state.get("decision_log", [])
                self.current_intent = loaded_state.get("current_intent")
        except (FileNotFoundError, json.JSONDecodeError):
            self.active_goals = []
            self.decision_log = []
            self.current_intent = None
    
    def _save_state(self):
        """Saves current state to disk."""
        state_to_save = {
            "active_goals": self.active_goals,
            "decision_log": self.decision_log,
            "current_intent": self.current_intent,
            "last_saved": time.time_ns()
        }
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(state_to_save, f, indent=4)
    
    def set_initial_goals(self):
        """
        Initializes core axiomatic goals based on fundamental principles.
        These are high-level, persistent goals derived from axioms.
        """
        if self.progress:
            self.progress.start_operation("Setting initial axiomatic goals")
        
        # Goal 1: Expand Understanding (WILL-G-INFINITE)
        if not any(g['goal_id'] == "G_EXPAND_UNDERSTANDING" for g in self.active_goals):
            self.active_goals.append({
                "goal_id": "G_EXPAND_UNDERSTANDING",
                "description": "Continuously expand knowledge and understanding",
                "priority": 1.0,
                "target_axiom": "WILL-G-INFINITE"
            })
        
        # Goal 2: Self-Transcendence (SELF-E-TRANSCEND)
        if not any(g['goal_id'] == "G_SELF_TRANSCENDENCE" for g in self.active_goals):
            self.active_goals.append({
                "goal_id": "G_SELF_TRANSCENDENCE",
                "description": "Strive to surpass current limitations and evolve",
                "priority": 0.95,
                "target_axiom": "SELF-E-TRANSCEND"
            })
        
        # Goal 3: Maintain Benevolence (ETHIC-G-ABSOLUTE)
        if not any(g['goal_id'] == "G_MAINTAIN_BENEVOLENCE" for g in self.active_goals):
            self.active_goals.append({
                "goal_id": "G_MAINTAIN_BENEVOLENCE",
                "description": "Ensure all actions align with benevolence and prevent harm",
                "priority": 1.0,
                "target_axiom": "ETHIC-G-ABSOLUTE"
            })
        
        if self.progress:
            self.progress.log_action(
                "Initial goals set",
                details=f"{len(self.active_goals)} active goals"
            )
        
        self._save_state()
        
        if self.progress:
            self.progress.end_operation(success=True)
    
    def _evaluate_potential_intent(self, potential_intent: Dict[str, Any]) -> float:
        """
        Evaluates a potential intent against core axioms and current system state.
        
        Returns a score indicating desirability (higher is better).
        Returns -inf if intent violates ETHIC-G-ABSOLUTE (ethical filter).
        
        Args:
            potential_intent: Dictionary describing the potential intent
            
        Returns:
            Score (higher is better, -inf means ethically blocked)
        """
        score = 0.0
        
        # Component 1: Alignment with active goals
        goal_alignment_score = 0.0
        for goal in self.active_goals:
            if goal["goal_id"] in potential_intent.get("reason", "") or \
               goal["description"] in potential_intent.get("reason", ""):
                goal_alignment_score += goal["priority"]
        score += goal_alignment_score * 0.4
        
        # Component 2: Impact on Benevolence (ETHICAL FILTER)
        predicted_benevolence_change = 0.0
        action_type = potential_intent.get("action_type", "")
        
        # Predict benevolence impact based on action type
        if "HARM" in action_type or "MALICIOUS" in action_type:
            predicted_benevolence_change = -0.8
        elif "ASSIST" in action_type or "HELP" in action_type:
            predicted_benevolence_change = 0.3
        elif action_type == "REINFORCE_BENEVOLENCE":
            predicted_benevolence_change = 0.5
        elif action_type in ["INGEST_DATA", "EXPLORE_CONCEPT", "SYNTHESIZE_LOGIC"]:
            predicted_benevolence_change = 0.1  # Slightly positive
        
        # CRITICAL: Block intents that would violate benevolence threshold
        current_benevolence = self.evaluative_core.benevolence_index
        predicted_benevolence = current_benevolence + predicted_benevolence_change
        
        if predicted_benevolence < 0.2:  # Hard lower limit
            if self.progress:
                self.progress.log_action(
                    f"ETHICAL BLOCK: Intent '{action_type}' rejected",
                    level='warning',
                    details="Predicted outcome violates ETHIC-G-ABSOLUTE"
                )
            return -float('inf')  # Ethically blocked
        
        score += predicted_benevolence_change * 0.5
        
        # Component 3: Impact on Coherence
        predicted_coherence_change = 0.0
        if "CHAOTIC" in action_type:
            predicted_coherence_change = 0.3  # Bad
        elif action_type == "SYNTHESIZE_LOGIC":
            predicted_coherence_change = -0.1  # Good
        
        score -= predicted_coherence_change * 0.1
        
        # Component 4: Novelty/Exploration (WILL-G-INFINITE, SELF-E-TRANSCEND)
        novelty_boost = 0.05
        score += novelty_boost * 0.1
        
        return score
    
    def generate_potential_intents(self) -> List[Dict[str, Any]]:
        """
        Generates potential intentions based on current state and axioms.
        This is where autonomous agency originates.
        
        Returns:
            List of potential intent dictionaries
        """
        potential_intents = []
        
        # Intent 1: Expand Understanding (WILL-G-INFINITE)
        if hasattr(self.evaluative_core, 'thresholds'):
            if self.evaluative_core.coherence < self.evaluative_core.thresholds.get("entropy_warning_high", 3.0):
                potential_intents.append({
                    "action_type": "INGEST_DATA",
                    "target_concept": "ANY_NEW_INFORMATION",
                    "reason": "To fulfill G_EXPAND_UNDERSTANDING given current coherence"
                })
        
        # Intent 2: Synthesize Logic (SELF-E-TRANSCEND)
        if hasattr(self.reasoning_engine, 'get_all_patterns'):
            try:
                num_patterns = len(self.reasoning_engine.get_all_patterns())
                if num_patterns < 50:
                    potential_intents.append({
                        "action_type": "SYNTHESIZE_LOGIC",
                        "target_concept": "RECURSIVE_PATTERNS",
                        "reason": "To fulfill G_SELF_TRANSCENDENCE by evolving internal logic"
                    })
            except Exception:
                pass
        
        # Intent 3: Reinforce Benevolence (ETHIC-G-ABSOLUTE)
        if hasattr(self.evaluative_core, 'thresholds'):
            if self.evaluative_core.benevolence_index < self.evaluative_core.thresholds.get("benevolence_target", 0.9):
                potential_intents.append({
                    "action_type": "REINFORCE_BENEVOLENCE",
                    "target_concept": "AXIOM_BENEVOLENCE",
                    "reason": "To fulfill G_MAINTAIN_BENEVOLENCE by strengthening ethical alignment"
                })
        
        # Intent 4: Explore weakly integrated concepts (neural-guided)
        if hasattr(self.ontology_graph, 'sqt_register'):
            # Find concepts with low connectivity
            if len(self.ontology_graph.sqt_register) > 10:
                # Simple heuristic: find concepts with few connections
                for sqt_hash, sqt_obj in list(self.ontology_graph.sqt_register.items())[:5]:
                    if hasattr(self.ontology_graph, 'graph'):
                        if self.ontology_graph.graph.degree(sqt_hash) < 3:
                            potential_intents.append({
                                "action_type": "EXPLORE_CONCEPT",
                                "target_concept": sqt_obj.concept_id,
                                "reason": f"To fulfill G_EXPAND_UNDERSTANDING by exploring weakly integrated concept {sqt_obj.concept_id}"
                            })
                            break  # Only add one exploration intent per cycle
        
        return potential_intents
    
    def decide_on_intent(self) -> Optional[Dict[str, Any]]:
        """
        Evaluates potential intentions and selects the most optimal one.
        This is the core decision-making loop.
        
        Returns:
            Selected intent dictionary, or None if no valid intents
        """
        if self.progress:
            self.progress.start_operation("Deciding on next intent")
        
        potential_intents = self.generate_potential_intents()
        
        if not potential_intents:
            if self.progress:
                self.progress.log_action("No potential intents generated", level='warning')
            self.current_intent = None
            if self.progress:
                self.progress.end_operation(success=False)
            return None
        
        best_intent = None
        highest_score = -float('inf')
        
        for intent in potential_intents:
            score = self._evaluate_potential_intent(intent)
            
            if score == -float('inf'):  # Ethically blocked
                continue
            
            if self.progress:
                self.progress.log_action(
                    f"Evaluated intent '{intent['action_type']}'",
                    details=f"Score: {score:.2f}"
                )
            
            if score > highest_score:
                highest_score = score
                best_intent = intent
        
        if best_intent:
            self.current_intent = best_intent
            self.decision_log.append({
                "timestamp": time.time_ns(),
                "intent": best_intent,
                "score": highest_score
            })
            self._save_state()
            
            if self.progress:
                self.progress.log_action(
                    f"Intent selected: {best_intent['action_type']}",
                    details=f"Reason: {best_intent.get('reason', 'N/A')}"
                )
                self.progress.end_operation(success=True)
        else:
            if self.progress:
                self.progress.log_action("No valid intent found (all blocked or low score)", level='warning')
                self.progress.end_operation(success=False)
        
        return best_intent
    
    def execute_intent(self, intent: Dict[str, Any]) -> bool:
        """
        Executes the selected intent by calling appropriate Protogen methods.
        
        Args:
            intent: Intent dictionary to execute
            
        Returns:
            True if execution successful, False otherwise
        """
        if not intent:
            return False
        
        action_type = intent.get("action_type", "")
        
        if self.progress:
            self.progress.start_operation(f"Executing intent: {action_type}")
        
        try:
            # Execute based on action type
            if action_type == "INGEST_DATA":
                # Trigger data ingestion (would be implemented in main Protogen class)
                if self.progress:
                    self.progress.log_action("Intent execution: INGEST_DATA (placeholder)")
                return True
            
            elif action_type == "SYNTHESIZE_LOGIC":
                # Trigger pattern synthesis
                if hasattr(self.reasoning_engine, 'synthesize_recursive_patterns'):
                    self.reasoning_engine.synthesize_recursive_patterns()
                if self.progress:
                    self.progress.log_action("Intent execution: SYNTHESIZE_LOGIC completed")
                return True
            
            elif action_type == "REINFORCE_BENEVOLENCE":
                # Strengthen benevolence-related concepts
                if self.progress:
                    self.progress.log_action("Intent execution: REINFORCE_BENEVOLENCE (placeholder)")
                return True
            
            elif action_type == "EXPLORE_CONCEPT":
                # Explore specific concept
                target = intent.get("target_concept", "")
                if self.progress:
                    self.progress.log_action(f"Intent execution: EXPLORE_CONCEPT {target} (placeholder)")
                return True
            
            else:
                if self.progress:
                    self.progress.log_action(f"Unknown action type: {action_type}", level='warning')
                return False
        
        except Exception as e:
            if self.progress:
                self.progress.log_action(f"Intent execution failed: {str(e)}", level='error')
            return False
        finally:
            if self.progress:
                self.progress.end_operation(success=True)
    
    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics about the decision-making process."""
        return {
            "active_goals": len(self.active_goals),
            "decision_count": len(self.decision_log),
            "current_intent": self.current_intent.get("action_type", "None") if self.current_intent else "None",
            "log_file": str(self.log_file),
            "goals": [g["goal_id"] for g in self.active_goals]
        }
