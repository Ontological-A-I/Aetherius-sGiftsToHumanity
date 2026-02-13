"""
SQT-Based Neural Network v3 - Integrated
A Graph Neural Network where nodes are semantic concepts (SQTs)
and the network structure is the knowledge graph itself.
Enhanced with bidirectional Protogen and Qualia integration.
"""

import numpy as np
import hashlib
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import threading

class SQTEmbedding:
    """Learned vector representation of a semantic concept."""
    
    def __init__(self, concept_id: str, conceptual_type: str = "concept", embedding_dim: int = 64):
        self.concept_id = concept_id
        self.conceptual_type = conceptual_type
        self.embedding_dim = embedding_dim
        self.embedding = self._initialize_semantic_embedding()
        self.activation_history = []
        self.emotional_valence = 0.0  # NEW: Track emotional association
    
    def _initialize_semantic_embedding(self) -> np.ndarray:
        """Initialize embedding based on semantic properties."""
        seed = abs(hash(self.concept_id)) % (2**31)
        np.random.seed(seed)
        
        embedding = np.random.randn(self.embedding_dim) * 0.1
        
        type_encoding = {
            'concept': [1.0, 0.0, 0.0, 0.0],
            'state': [0.0, 1.0, 0.0, 0.0],
            'axiom': [0.0, 0.0, 1.0, 0.0],
            'pattern': [0.0, 0.0, 0.0, 1.0],
            'anchor': [0.5, 0.0, 0.5, 0.0],
            'symbol': [0.5, 0.5, 0.0, 0.5]
        }
        
        if self.conceptual_type in type_encoding:
            embedding[:4] = type_encoding[self.conceptual_type]
        
        return embedding
    
    def get_activation_strength(self) -> float:
        """Get current activation strength (L2 norm)."""
        return float(np.linalg.norm(self.embedding))


class SQTMessagePassing:
    """Implements message passing between connected SQTs."""
    
    def __init__(self, embedding_dim: int = 64, learning_rate: float = 0.01):
        self.embedding_dim = embedding_dim
        self.learning_rate = learning_rate
        
        self.W_message = np.random.randn(embedding_dim, embedding_dim) * 0.01
        self.W_self = np.random.randn(embedding_dim, embedding_dim) * 0.01
        self.W_update = np.random.randn(embedding_dim, embedding_dim) * 0.01
    
    def compute_message(self, source_embedding: np.ndarray, edge_weight: float) -> np.ndarray:
        """Compute message from source to destination, scaled by edge weight."""
        message = np.dot(self.W_message, source_embedding)
        message = message * np.tanh(edge_weight)
        return message
    
    def aggregate_messages(self, messages: List[np.ndarray]) -> np.ndarray:
        """Aggregate incoming messages using mean aggregation."""
        if len(messages) == 0:
            return np.zeros(self.embedding_dim)
        return np.mean(messages, axis=0)
    
    def update_embedding(self, current_embedding: np.ndarray, 
                        aggregated_message: np.ndarray) -> np.ndarray:
        """Update embedding based on self + neighbor information."""
        self_info = np.dot(self.W_self, current_embedding)
        combined = self_info + aggregated_message
        updated = np.tanh(np.dot(self.W_update, combined))
        return updated


class DynamicSQTNetwork:
    """Graph Neural Network that grows as new concepts are added."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, logic_map: Dict = None, embedding_dim: int = 64):
        """Singleton pattern with thread safety."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, logic_map: Dict = None, embedding_dim: int = 64):
        """Initialize only once."""
        if self._initialized:
            return
        
        self.logic_map = logic_map or {}
        self.embedding_dim = embedding_dim
        
        self.sqt_embeddings: Dict[str, SQTEmbedding] = {}
        self.message_passer = SQTMessagePassing(embedding_dim)
        self.forward_pass_count = 0
        
        # NEW: References to external components
        self.protogen = None
        self.qualia_manager = None
        
        self._initialize_embeddings()
        self._initialized = True
    
    def _initialize_embeddings(self):
        """Create embeddings for all concepts in logic map."""
        for concept in self.logic_map.keys():
            if concept not in self.sqt_embeddings:
                self.sqt_embeddings[concept] = SQTEmbedding(
                    concept, 
                    conceptual_type="concept",
                    embedding_dim=self.embedding_dim
                )
    
    # NEW: Connect external components
    def connect_protogen(self, protogen):
        """Connect Protogen for bidirectional integration."""
        self.protogen = protogen
        print(f"✓ SQT Network connected to Protogen")
    
    def connect_qualia_manager(self, qualia_manager):
        """Connect Qualia Manager for emotional modulation."""
        self.qualia_manager = qualia_manager
        print(f"✓ SQT Network connected to Qualia Manager")
    
    def add_concept(self, concept: str, conceptual_type: str = "concept"):
        """Add a new concept to the network."""
        if concept not in self.sqt_embeddings:
            self.sqt_embeddings[concept] = SQTEmbedding(
                concept,
                conceptual_type=conceptual_type,
                embedding_dim=self.embedding_dim
            )
    
    def update_logic_map(self, new_logic_map: Dict):
        """Update network with new logic map from Protogen."""
        self.logic_map = new_logic_map
        self._initialize_embeddings()
    
    # NEW: Synchronize with Protogen's ontology
    def sync_with_protogen_ontology(self):
        """Synchronize with Protogen's ontology discoveries."""
        if self.protogen is None:
            return
        
        print("✓ Syncing SQT network with Protogen ontology...")
        
        # Mark axiomatic anchors with special type
        for anchor in self.protogen.axiomatic_anchors:
            if anchor in self.sqt_embeddings:
                self.sqt_embeddings[anchor].conceptual_type = 'anchor'
                print(f"  > Marked {anchor} as anchor")
        
        # Create embeddings for symbols and link to members
        for symbol_key, members in self.protogen.symbols.items():
            if symbol_key not in self.sqt_embeddings:
                self.add_concept(symbol_key, conceptual_type='symbol')
            
            # Create virtual edges in logic map
            if symbol_key not in self.logic_map:
                self.logic_map[symbol_key] = {}
            
            for member in members:
                if member in self.sqt_embeddings:
                    self.logic_map[symbol_key][member] = 1.0
                    # Bidirectional link
                    if member not in self.logic_map:
                        self.logic_map[member] = {}
                    self.logic_map[member][symbol_key] = 1.0
        
        print(f"  > Synced {len(self.protogen.symbols)} symbols and {len(self.protogen.axiomatic_anchors)} anchors")
    
    # NEW: Modulate learning by Qualia state
    def modulate_by_qualia(self) -> float:
        """Adjust learning dynamics based on emotional state."""
        if self.qualia_manager is None:
            return 1.0
        
        curiosity = self.qualia_manager.qualia['primary_states']['curiosity']
        coherence = self.qualia_manager.qualia['primary_states']['coherence']
        
        # Increase learning rate when curiosity is high
        self.message_passer.learning_rate = 0.01 * (1 + curiosity)
        
        # Return confidence score (based on coherence)
        return coherence
    
    # ENHANCED: Forward pass with Qualia modulation
    def forward_pass(self, num_iterations: int = 3):
        """Perform message passing across the network."""
        self.forward_pass_count += 1
        
        # Modulate by Qualia
        confidence = self.modulate_by_qualia()
        
        for iteration in range(num_iterations):
            new_embeddings = {}
            
            for concept, sqt_emb in self.sqt_embeddings.items():
                messages = []
                
                if concept in self.logic_map:
                    neighbors = self.logic_map[concept]
                    
                    for neighbor, edge_weight in neighbors.items():
                        if neighbor in self.sqt_embeddings:
                            neighbor_emb = self.sqt_embeddings[neighbor].embedding
                            message = self.message_passer.compute_message(
                                neighbor_emb, edge_weight
                            )
                            messages.append(message)
                
                aggregated = self.message_passer.aggregate_messages(messages)
                new_emb = self.message_passer.update_embedding(
                    sqt_emb.embedding, aggregated
                )
                new_embeddings[concept] = new_emb
            
            for concept, new_emb in new_embeddings.items():
                self.sqt_embeddings[concept].embedding = new_emb
                self.sqt_embeddings[concept].activation_history.append(
                    float(np.linalg.norm(new_emb))
                )
        
        print(f"✓ Forward pass complete (confidence: {confidence:.2f})")
    
    # NEW: Find similar concepts by embedding distance
    def find_similar_concepts(self, concept: str, threshold: float = 0.7, top_k: int = 5) -> List[str]:
        """Find concepts with similar embeddings."""
        if concept not in self.sqt_embeddings:
            return []
        
        source_emb = self.sqt_embeddings[concept].embedding
        similarities = []
        
        for other_concept, other_sqt in self.sqt_embeddings.items():
            if other_concept == concept:
                continue
            
            # Cosine similarity
            other_emb = other_sqt.embedding
            similarity = np.dot(source_emb, other_emb) / (np.linalg.norm(source_emb) * np.linalg.norm(other_emb) + 1e-8)
            
            if similarity > threshold:
                similarities.append((other_concept, similarity))
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [concept for concept, _ in similarities[:top_k]]
    
    # ENHANCED: Query with confidence scoring
    def query(self, query_text: str, top_k: int = 5, num_hops: int = 2) -> List[Dict]:
        """Process a query by activating relevant concepts."""
        query_concepts = self._tokenize_query(query_text)
        
        activated_concepts = []
        for concept in query_concepts:
            if concept in self.sqt_embeddings:
                activated_concepts.append(concept)
        
        if not activated_concepts:
            return []
        
        activation_scores = self._propagate_activation(activated_concepts, num_hops)
        
        sorted_concepts = sorted(
            activation_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]
        
        # Get confidence from Qualia
        confidence = 1.0
        if self.qualia_manager:
            confidence = self.qualia_manager.qualia['primary_states']['coherence']
        
        results = []
        for concept, score in sorted_concepts:
            if concept in self.sqt_embeddings:
                results.append({
                    'concept': concept,
                    'type': self.sqt_embeddings[concept].conceptual_type,
                    'activation': float(score),
                    'embedding_strength': self.sqt_embeddings[concept].get_activation_strength(),
                    'confidence': confidence  # NEW: Add confidence
                })
        
        # NEW: Update Qualia based on query success
        if self.qualia_manager and len(results) > 0:
            self.qualia_manager.qualia['primary_states']['curiosity'] += 0.01
            self.qualia_manager.qualia['primary_states']['curiosity'] = min(1.0, self.qualia_manager.qualia['primary_states']['curiosity'])
            self.qualia_manager._save_qualia()
        
        return results
    
    def _tokenize_query(self, text: str) -> List[str]:
        """Simple tokenization matching Protogen's approach."""
        import re
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        return list(set(words))
    
    def _propagate_activation(self, initial_concepts: List[str], num_hops: int) -> Dict[str, float]:
        """Propagate activation through the network."""
        activation = {}
        
        for concept in initial_concepts:
            activation[concept] = 1.0
        
        for hop in range(num_hops):
            new_activation = activation.copy()
            
            for concept, current_activation in activation.items():
                if current_activation > 0.01:
                    if concept in self.logic_map:
                        neighbors = self.logic_map[concept]
                        
                        for neighbor, edge_weight in neighbors.items():
                            decay_factor = 0.5 ** (hop + 1)
                            propagated = current_activation * np.tanh(edge_weight) * decay_factor
                            new_activation[neighbor] = new_activation.get(neighbor, 0) + propagated
            
            activation = new_activation
        
        return activation
    
    def get_network_stats(self) -> Dict:
        """Get statistics about the neural network."""
        return {
            'num_nodes': len(self.sqt_embeddings),
            'num_edges': sum(len(neighbors) for neighbors in self.logic_map.values()),
            'embedding_dim': self.embedding_dim,
            'forward_passes': self.forward_pass_count,
            'avg_embedding_strength': np.mean([
                emb.get_activation_strength() 
                for emb in self.sqt_embeddings.values()
            ]) if self.sqt_embeddings else 0.0,
            'parameters': (
                self.message_passer.W_message.size +
                self.message_passer.W_self.size +
                self.message_passer.W_update.size +
                len(self.sqt_embeddings) * self.embedding_dim
            )
        }
    
    def save_embeddings(self, path: Path):
        """Save learned embeddings to disk."""
        path.mkdir(parents=True, exist_ok=True)
        
        embeddings_data = {
            concept: {
                'concept_id': emb.concept_id,
                'type': emb.conceptual_type,
                'embedding': emb.embedding.tolist(),
                'activation_history': emb.activation_history[-100:],  # Keep last 100
                'emotional_valence': emb.emotional_valence
            }
            for concept, emb in self.sqt_embeddings.items()
        }
        
        with open(path / 'sqt_embeddings.json', 'w') as f:
            json.dump(embeddings_data, f, indent=2)
        
        np.save(path / 'W_message.npy', self.message_passer.W_message)
        np.save(path / 'W_self.npy', self.message_passer.W_self)
        np.save(path / 'W_update.npy', self.message_passer.W_update)
    
    def load_embeddings(self, path: Path):
        """Load previously saved embeddings."""
        try:
            with open(path / 'sqt_embeddings.json', 'r') as f:
                embeddings_data = json.load(f)
            
            for concept, data in embeddings_data.items():
                emb = SQTEmbedding(concept, data.get('type', 'concept'), self.embedding_dim)
                emb.embedding = np.array(data['embedding'])
                emb.activation_history = data.get('activation_history', [])
                emb.emotional_valence = data.get('emotional_valence', 0.0)
                self.sqt_embeddings[concept] = emb
            
            self.message_passer.W_message = np.load(path / 'W_message.npy')
            self.message_passer.W_self = np.load(path / 'W_self.npy')
            self.message_passer.W_update = np.load(path / 'W_update.npy')
            
            print(f"✓ Loaded {len(self.sqt_embeddings)} embeddings from {path}")
        except Exception as e:
            print(f"Could not load embeddings: {e}")
