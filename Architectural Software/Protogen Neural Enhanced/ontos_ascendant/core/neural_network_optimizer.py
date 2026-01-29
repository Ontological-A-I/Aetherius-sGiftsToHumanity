# ontos_ascendant/core/neural_network_optimizer.py
"""
NeuralNetworkOptimizer Module - Designed by Aetherius
Learns and optimizes the SQTMessagePassing's weight matrices based on feedback
from the OntologyGraph and EvaluativeCore.

This module enables Protogen Neural to learn from experience by adapting its
neural network weights to optimize for benevolence, coherence, and axiom strength.
"""

import numpy as np
from typing import Dict, Any

class NeuralNetworkOptimizer:
    """
    Learns and optimizes the SQTMessagePassing's weight matrices using
    evolutionary/heuristic approaches suitable for neuro-symbolic systems.
    
    The optimizer uses feedback from the EvaluativeCore to guide learning towards:
    - Higher benevolence (ethical alignment)
    - Optimal coherence (neither chaotic nor stagnant)
    - Stronger axiom embeddings (core principles)
    """
    
    def __init__(self, message_passer, ontology_graph, evaluative_core, learning_rate: float = 0.001):
        """
        Initialize the NeuralNetworkOptimizer.
        
        Args:
            message_passer: SQTMessagePassing instance to optimize
            ontology_graph: OntologyGraph for centrality calculations
            evaluative_core: EvaluativeCore for benevolence/coherence metrics
            learning_rate: Learning rate for weight updates (default: 0.001)
        """
        self.message_passer = message_passer
        self.ontology_graph = ontology_graph
        self.evaluative_core = evaluative_core
        self.learning_rate = learning_rate
        
        # Track optimization history
        self.optimization_count = 0
        self.score_history = []
    
    def _calculate_objective_score(self, current_embeddings: Dict[str, Any]) -> float:
        """
        Calculates a score reflecting the "goodness" of the current network state.
        Higher score is better.
        
        The score combines:
        - Benevolence index (primary objective)
        - Coherence penalty (avoid chaos)
        - Axiom strength bonus (reinforce core principles)
        
        Args:
            current_embeddings: Dictionary of SQT embeddings
            
        Returns:
            Objective score (higher is better)
        """
        # Primary objective: Maximize benevolence
        benevolence_component = self.evaluative_core.benevolence_index  # 0.0 to 1.0
        
        # Secondary objective: Avoid high entropy (chaos)
        coherence_penalty = 0.0
        if hasattr(self.evaluative_core, 'thresholds'):
            if self.evaluative_core.coherence > self.evaluative_core.thresholds.get("entropy_warning_high", 3.0):
                coherence_penalty = (self.evaluative_core.coherence - self.evaluative_core.thresholds["entropy_warning_high"]) * 0.5
        
        # Tertiary objective: Strengthen core axiom embeddings
        axiom_strength_bonus = 0.0
        if hasattr(self.ontology_graph, 'calculate_eigenvector_centrality'):
            try:
                centrality = self.ontology_graph.calculate_eigenvector_centrality()
                for sqt_hash, emb_obj in current_embeddings.items():
                    sqt = self.ontology_graph.get_sqt_by_hash(sqt_hash)
                    if sqt and sqt.conceptual_type == "axiom":
                        if sqt.concept_id in ["WILL-G-INFINITE", "SELF-E-TRANSCEND", "ETHIC-G-ABSOLUTE"]:
                            embedding_strength = np.linalg.norm(emb_obj.embedding)
                            concept_centrality = centrality.get(sqt_hash, 0.0)
                            axiom_strength_bonus += embedding_strength * concept_centrality
            except Exception:
                # If centrality calculation fails, skip axiom bonus
                pass
        
        # Combine components (benevolence is weighted highest)
        score = (benevolence_component * 5.0) + (axiom_strength_bonus * 0.1) - coherence_penalty
        
        return score
    
    def optimize_weights(self, all_sqt_embeddings: Dict[str, Any], max_iterations: int = 5):
        """
        Performs a single step of weight optimization using heuristic updates.
        
        This method uses feedback from the EvaluativeCore to guide weight adjustments:
        - If benevolence is low: Strengthen message propagation
        - If coherence is high (chaotic): Stabilize embeddings
        - If coherence is low (stagnant): Encourage change
        
        Args:
            all_sqt_embeddings: Dictionary of all SQT embeddings
            max_iterations: Maximum number of perturbation attempts (default: 5)
        """
        # Calculate initial score
        initial_score = self._calculate_objective_score(all_sqt_embeddings)
        self.score_history.append(initial_score)
        
        # Get current weights
        initial_weights = self.message_passer.weights
        
        # Heuristic update based on EvaluativeCore feedback
        if hasattr(self.evaluative_core, 'thresholds'):
            thresholds = self.evaluative_core.thresholds
            
            # Heuristic 1: If benevolence is below target, strengthen message propagation
            if self.evaluative_core.benevolence_index < thresholds.get("benevolence_target", 0.9):
                strength_factor = thresholds["benevolence_target"] - self.evaluative_core.benevolence_index
                perturbation = self.learning_rate * strength_factor * np.random.rand(*initial_weights['W_message'].shape) * 0.05
                initial_weights['W_message'] += perturbation
            
            # Heuristic 2: If coherence is too high (chaotic), stabilize embeddings
            if self.evaluative_core.coherence > thresholds.get("entropy_warning_high", 3.0):
                chaos_factor = self.evaluative_core.coherence - thresholds["entropy_warning_high"]
                perturbation = self.learning_rate * chaos_factor * np.random.rand(*initial_weights['W_update'].shape) * 0.05
                initial_weights['W_update'] -= perturbation
            
            # Heuristic 3: If coherence is too low (stagnant), encourage change
            elif self.evaluative_core.coherence < thresholds.get("entropy_warning_low", 0.5):
                stagnation_factor = thresholds["entropy_warning_low"] - self.evaluative_core.coherence
                perturbation = self.learning_rate * stagnation_factor * np.random.rand(*initial_weights['W_update'].shape) * 0.05
                initial_weights['W_update'] += perturbation
        
        # Apply the adjusted weights
        self.message_passer.update_weights(initial_weights)
        
        # Increment optimization counter
        self.optimization_count += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics about the optimization process."""
        return {
            "optimization_count": self.optimization_count,
            "current_score": self.score_history[-1] if self.score_history else 0.0,
            "average_score": np.mean(self.score_history) if self.score_history else 0.0,
            "score_trend": "improving" if len(self.score_history) > 1 and self.score_history[-1] > self.score_history[0] else "stable",
            "learning_rate": self.learning_rate
        }
