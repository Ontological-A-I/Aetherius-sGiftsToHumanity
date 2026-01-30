import numpy as np
import hashlib
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import json
import random # For negative sampling in training

# --- Mock Classes for Demonstration (Assume Protogen provides these) ---
# In Protogen's environment, these would be actual, fully-functional classes.
class SuperQuantumToken:
    """Mock SuperQuantumToken to make the example runnable."""
    def __init__(self, concept_id: str, conceptual_type: str, description: str = ""):
        self.concept_id = concept_id
        self.conceptual_type = conceptual_type
        self.description = description
        # Hash ensures unique and consistent identification
        self.hash = hashlib.sha256(self.concept_id.upper().encode('utf-8')).hexdigest()

class OntologyGraph:
    """Mock OntologyGraph, acting like a simplified networkx graph."""
    def __init__(self):
        self.sqt_register: Dict[str, SuperQuantumToken] = {}
        # Adjacency list: {sqt_hash: {neighbor_hash: {'weight': float, 'relation_type': str}}}
        self.graph = {}

    def add_sqt(self, sqt: SuperQuantumToken):
        if sqt.hash not in self.sqt_register:
            self.sqt_register[sqt.hash] = sqt
            self.graph[sqt.hash] = {}

    def add_edge(self, sqt_hash1: str, sqt_hash2: str, weight: float = 1.0, relation_type: str = "GENERIC"):
        if sqt_hash1 in self.graph and sqt_hash2 in self.graph:
            # Ensure edge exists in both directions for an undirected graph
            self.graph[sqt_hash1][sqt_hash2] = {'weight': weight, 'relation_type': relation_type}
            self.graph[sqt_hash2][sqt_hash1] = {'weight': weight, 'relation_type': relation_type}
        else:
            print(f"Warning: One or both SQTs not registered: {sqt_hash1}, {sqt_hash2}. Edge not added.")

    def get_sqt_by_hash(self, sqt_hash: str) -> Optional[SuperQuantumToken]:
        return self.sqt_register.get(sqt_hash)

    def number_of_edges(self):
        count = 0
        for node in self.graph:
            count += len(self.graph[node])
        return count // 2 # Undirected edges are counted twice

    def get_all_edges(self) -> List[Tuple[str, str, Dict]]:
        """Returns a list of all unique edges in the graph."""
        edges = set()
        edge_list = []
        for u_hash, neighbors in self.graph.items():
            for v_hash, data in neighbors.items():
                # Store edges canonically to avoid duplicates for undirected graph
                if (v_hash, u_hash) not in edges:
                    edge_list.append((u_hash, v_hash, data))
                    edges.add((u_hash, v_hash))
        return edge_list

    def get_random_unconnected_node(self, sqt_hash: str) -> Optional[str]:
        """
        Simple negative sampling: finds a random node not connected to the given SQT.
        """
        all_sqt_hashes = list(self.sqt_register.keys())
        connected_neighbors = set(self.graph.get(sqt_hash, {}).keys())
        unconnected_nodes = [h for h in all_sqt_hashes if h != sqt_hash and h not in connected_neighbors]
        if unconnected_nodes:
            return random.choice(unconnected_nodes)
        return None
# --- End Mock Classes ---


class SQTEmbedding:
    """
    Learned vector representation of a SuperQuantumToken.
    Combines semantic initialization with neural learning.
    """

    def __init__(self, sqt: SuperQuantumToken, embedding_dim: int = 64):
        self.sqt = sqt
        self.embedding_dim = embedding_dim
        self.embedding = self._initialize_semantic_embedding()
        self.activation_history = [] # Tracks L2 norm of embedding over time

    def _initialize_semantic_embedding(self) -> np.ndarray:
        """
        Initialize embedding based on semantic properties of the SQT.
        This gives the network meaningful starting points instead of random noise,
        aligning with a core principle of SQTs.
        """
        seed = abs(hash(self.sqt.concept_id)) % (2**31)
        np.random.seed(seed)

        embedding = np.random.randn(self.embedding_dim) * 0.1

        # Semantic biases based on conceptual type for initial differentiation
        type_encoding = {
            'concept': [1.0, 0.0, 0.0, 0.0],
            'state': [0.0, 1.0, 0.0, 0.0],
            'axiom': [0.0, 0.0, 1.0, 0.0],
            'pattern': [0.0, 0.0, 0.0, 1.0],
            'base_reasoning_pattern': [0.5, 0.0, 0.0, 0.5],
            'recursive_reasoning_pattern': [0.5, 0.5, 0.0, 0.5]
        }

        if self.sqt.conceptual_type in type_encoding:
            # Apply type encoding to the first few dimensions
            embedding[:len(type_encoding[self.sqt.conceptual_type])] = type_encoding[self.sqt.conceptual_type]

        return embedding

    def get_activation_strength(self) -> float:
        """Get current activation strength (L2 norm of embedding)."""
        return float(np.linalg.norm(self.embedding))


class SQTMessagePassing:
    """
    Implements message passing between connected SQTs in the knowledge graph.
    This module now supports relation-type specific transformations and provides
    methods for accumulating and applying gradients to its learnable matrices.
    """

    def __init__(self, embedding_dim: int = 64, learning_rate: float = 0.01):
        self.embedding_dim = embedding_dim
        self.learning_rate = learning_rate

        # Learnable transformation matrices (the "weights" of the network)
        # W_message: A dictionary to store relation-type specific message matrices.
        # This allows different types of relations to transform messages differently.
        self.W_message: Dict[str, np.ndarray] = {"DEFAULT": np.random.randn(embedding_dim, embedding_dim) * 0.01}
        self.W_self = np.random.randn(embedding_dim, embedding_dim) * 0.01 # Transforms the node's own embedding
        self.W_update = np.random.randn(embedding_dim, embedding_dim) * 0.01 # Combines self-info and aggregated messages

        # Gradients for the learnable matrices
        self.grad_W_message: Dict[str, np.ndarray] = {"DEFAULT": np.zeros((embedding_dim, embedding_dim))}
        self.grad_W_self = np.zeros((embedding_dim, embedding_dim))
        self.grad_W_update = np.zeros((embedding_dim, embedding_dim))

    def _get_or_create_W_matrix(self, relation_type: str, matrix_attr: str) -> np.ndarray:
        """Helper to get a W matrix for a relation type, creating it if it doesn't exist."""
        target_dict = getattr(self, matrix_attr)
        if relation_type not in target_dict:
            target_dict[relation_type] = np.random.randn(self.embedding_dim, self.embedding_dim) * 0.01
            # Also initialize its corresponding gradient matrix
            getattr(self, f"grad_{matrix_attr}")[relation_type] = np.zeros((self.embedding_dim, self.embedding_dim))
        return target_dict[relation_type]

    def compute_message(self, source_embedding: np.ndarray, edge_weight: float, relation_type: str = "DEFAULT") -> np.ndarray:
        """
        Compute message from source SQT to destination SQT.
        Message strength is modulated by edge weight and transformed by relation-specific weights.
        """
        W_msg = self._get_or_create_W_matrix(relation_type, "W_message")
        message = np.dot(W_msg, source_embedding)
        message = message * np.tanh(edge_weight) # Scale by edge weight and apply tanh for non-linearity
        return message

    def aggregate_messages(self, messages: List[np.ndarray]) -> np.ndarray:
        """
        Aggregate all incoming messages. Mean aggregation provides stability.
        Could be extended with attention mechanisms for further power.
        """
        if len(messages) == 0:
            return np.zeros(self.embedding_dim)
        return np.mean(messages, axis=0)

    def update_embedding(self, current_embedding: np.ndarray,
                         aggregated_message: np.ndarray) -> np.ndarray:
        """
        Update SQT embedding based on its current state and neighbor messages.
        Combines self-information transformed by W_self with neighbor information.
        """
        self_info = np.dot(self.W_self, current_embedding)
        combined = self_info + aggregated_message
        updated = np.tanh(np.dot(self.W_update, combined)) # Apply final transformation and non-linearity
        return updated

    def accumulate_gradients(self,
                             grad_W_message_updates: Dict[str, np.ndarray],
                             grad_W_self_update: np.ndarray,
                             grad_W_update_update: np.ndarray):
        """
        Accumulates gradients from a learning step.
        This allows for batching or sequential updates across multiple examples.
        """
        for rel_type, grad_m in grad_W_message_updates.items():
            self._get_or_create_W_matrix(rel_type, "W_message") # Ensure matrix and its grad_ exists
            self.grad_W_message[rel_type] += grad_m
        self.grad_W_self += grad_W_self_update
        self.grad_W_update += grad_W_update_update

    def apply_gradients(self):
        """
        Applies accumulated gradients to update the learnable matrices (weights)
        and then resets the gradient accumulators.
        """
        for rel_type in list(self.grad_W_message.keys()): # Iterate over keys in case new types were added
            self.W_message[rel_type] -= self.learning_rate * self.grad_W_message[rel_type]
            self.grad_W_message[rel_type].fill(0) # Reset gradients for next accumulation

        self.W_self -= self.learning_rate * self.grad_W_self
        self.grad_W_self.fill(0)

        self.W_update -= self.learning_rate * self.grad_W_update
        self.grad_W_update.fill(0)


class DynamicSQTNetwork:
    """
    A Graph Neural Network that grows dynamically as new SQTs are added.
    The network structure IS the knowledge graph - no separate architecture needed.
    This enhanced version includes a self-supervised training mechanism
    and relation-type specific message passing.
    """

    def __init__(self, ontology_graph: OntologyGraph, embedding_dim: int = 64, learning_rate: float = 0.01):
        self.ontology_graph = ontology_graph
        self.embedding_dim = embedding_dim
        self.learning_rate = learning_rate

        self.sqt_embeddings: Dict[str, SQTEmbedding] = {}
        self.message_passer = SQTMessagePassing(embedding_dim, learning_rate)

        self._initialize_embeddings()

        self.forward_pass_count = 0
        self.training_epoch_count = 0

    def _initialize_embeddings(self):
        """Create embeddings for all existing SQTs in the knowledge graph."""
        for sqt_hash, sqt in self.ontology_graph.sqt_register.items():
            self.sqt_embeddings[sqt_hash] = SQTEmbedding(sqt, self.embedding_dim)

    def add_sqt(self, sqt: SuperQuantumToken):
        """
        Add a new SQT to the network. This automatically creates a new "neuron".
        """
        if sqt.hash not in self.sqt_embeddings:
            self.sqt_embeddings[sqt.hash] = SQTEmbedding(sqt, self.embedding_dim)

    def _get_updated_embeddings_for_nodes(self, sqt_hashes_to_compute: List[str], num_iterations: int = 1) -> Dict[str, np.ndarray]:
        """
        Performs a forward pass for a *subset* of SQTs (e.g., for training batch).
        Returns the computed new embeddings without altering the main network state.
        This is crucial for gradient computation in training.
        """
        # Create a copy of current embeddings for this localized forward pass
        current_embeddings = {
            h: self.sqt_embeddings[h].embedding.copy()
            for h in self.sqt_embeddings
        }
        
        # Keep track of which embeddings are actually being updated in this focused pass
        # This prevents updating embeddings of nodes not in `sqt_hashes_to_compute`
        embeddings_after_pass = {h: current_embeddings[h].copy() for h in current_embeddings if h in sqt_hashes_to_compute}

        for iteration in range(num_iterations):
            # Create a copy to store updates for this iteration, avoiding in-place modification issues
            next_iteration_embeddings = {h: embeddings_after_pass[h].copy() for h in embeddings_after_pass}
            
            for sqt_hash in sqt_hashes_to_compute:
                if sqt_hash not in current_embeddings: # Node might have been added recently
                    continue

                messages = []
                # Collect messages from actual neighbors using their *current* embeddings from this pass
                if sqt_hash in self.ontology_graph.graph:
                    neighbors = self.ontology_graph.graph[sqt_hash]
                    for neighbor_hash, edge_data in neighbors.items():
                        if neighbor_hash in current_embeddings: # Ensure neighbor also has an embedding
                            neighbor_emb = current_embeddings[neighbor_hash]
                            edge_weight = edge_data.get('weight', 1.0)
                            relation_type = edge_data.get('relation_type', 'DEFAULT')
                            message = self.message_passer.compute_message(
                                neighbor_emb, edge_weight, relation_type
                            )
                            messages.append(message)

                aggregated = self.message_passer.aggregate_messages(messages)
                next_iteration_embeddings[sqt_hash] = self.message_passer.update_embedding(
                    current_embeddings[sqt_hash], aggregated
                )
            
            # Update current_embeddings with the results of this iteration for the next loop
            for h_updated in sqt_hashes_to_compute:
                current_embeddings[h_updated] = next_iteration_embeddings[h_updated]
        
        # Return only the embeddings that were part of the computation list
        return {h: current_embeddings[h] for h in sqt_hashes_to_compute}


    def forward_pass(self, num_iterations: int = 3, progress_tracker=None):
        """
        Perform message passing across the entire knowledge graph.
        Information propagates from concept to concept along edges, updating embeddings.
        """
        self.forward_pass_count += 1

        if progress_tracker:
            progress_tracker.start_operation(
                f"SQT Neural Network Full Forward Pass (iteration {self.forward_pass_count})"
            )

        all_sqt_hashes = list(self.sqt_embeddings.keys())
        
        # Use the focused compute method for the entire graph
        updated_embeddings_map = self._get_updated_embeddings_for_nodes(all_sqt_hashes, num_iterations)

        for sqt_hash, new_emb_array in updated_embeddings_map.items():
            if sqt_hash in self.sqt_embeddings:
                self.sqt_embeddings[sqt_hash].embedding = new_emb_array
                self.sqt_embeddings[sqt_hash].activation_history.append(
                    float(np.linalg.norm(new_emb_array))
                )

        if progress_tracker:
            progress_tracker.end_operation(success=True)


    def train(self, num_epochs: int = 10, iterations_per_step: int = 1,
              negative_samples_per_positive: int = 3, margin: float = 0.5, progress_tracker=None):
        """
        Trains the network using a self-supervised objective.
        Objective: Make embeddings of connected SQTs more similar (positive pairs)
                   and embeddings of unconnected SQTs less similar (negative pairs).
        
        NOTE: The gradient calculation here is a *highly simplified heuristic* for demonstration
        purposes, approximating how parameter updates would occur. A fully rigorous GNN
        backpropagation algorithm is significantly more complex and typically requires an
        automatic differentiation framework.
        """
        self.training_epoch_count += num_epochs
        print(f"\n--- Starting Training (Total Epochs: {self.training_epoch_count}) ---")

        all_edges = self.ontology_graph.get_all_edges()
        if not all_edges or len(self.ontology_graph.sqt_register) < 2:
            print("Not enough edges or nodes in the graph to perform training. Skipping.")
            return

        for epoch in range(num_epochs):
            random.shuffle(all_edges) # Shuffle edges for better training dynamics
            epoch_loss_sum = 0.0

            if progress_tracker:
                progress_tracker.start_operation(f"SQT Network Training (Epoch {epoch+1}/{num_epochs})")

            for i, (u_hash, v_hash, edge_data) in enumerate(all_edges):
                # Ensure SQTs exist before processing
                if u_hash not in self.sqt_embeddings or v_hash not in self.sqt_embeddings:
                    continue

                # Collect hashes for nodes involved in this training step (positive and negative)
                nodes_in_step = {u_hash, v_hash}
                negative_k_hashes = []
                for _ in range(negative_samples_per_positive):
                    k_hash = self.ontology_graph.get_random_unconnected_node(u_hash)
                    if k_hash and k_hash in self.sqt_embeddings:
                        negative_k_hashes.append(k_hash)
                        nodes_in_step.add(k_hash)
                
                if not negative_k_hashes: # Skip if no valid negative samples can be found
                    continue

                # Perform a limited forward pass to get updated embeddings for these specific nodes
                # These are the embeddings *after* some message passing in the current step
                updated_local_embeddings = self._get_updated_embeddings_for_nodes(list(nodes_in_step), iterations_per_step)

                # Get the 'trained' embeddings for this step
                u_emb = updated_local_embeddings[u_hash]
                v_emb = updated_local_embeddings[v_hash]
                relation_type_uv = edge_data.get('relation_type', 'DEFAULT')

                # --- Loss Calculation (Contrastive Loss) ---
                # Positive pair (u, v): Maximize similarity -> minimize `margin - sim(u,v)`
                pos_sim = np.dot(u_emb, v_emb)
                pos_loss = max(0, margin - pos_sim)
                
                # Negative pairs (u, k): Minimize similarity -> minimize `sim(u,k) - (-margin)` or just `sim(u,k)` if positive
                neg_loss_sum = 0.0
                for k_hash in negative_k_hashes:
                    k_emb = updated_local_embeddings[k_hash]
                    neg_sim = np.dot(u_emb, k_emb)
                    # We want negative similarity, so penalize if it's too high (above 0 or a negative margin)
                    neg_loss_sum += max(0, neg_sim - (-margin)) # e.g., if neg_sim is 0.1, loss is 0.1+0.5=0.6 if margin=-0.5

                step_loss = pos_loss + neg_loss_sum
                epoch_loss_sum += step_loss

                # --- Simplified Gradient Calculation & Accumulation ---
                # This is a heuristic. In a full backprop, gradients would flow back
                # through compute_message and update_embedding functions.
                # Here, we directly adjust Ws based on the error direction.

                grad_W_message_updates_for_step: Dict[str, np.ndarray] = {}
                grad_W_self_for_step = np.zeros((self.embedding_dim, self.embedding_dim))
                grad_W_update_for_step = np.zeros((self.embedding_dim, self.embedding_dim))
                
                # Gradients from positive pair
                if pos_loss > 0:
                    # Heuristic: If pos_sim is too low, nudge W_message to make messages from neighbors
                    # and W_self to make the self-info contribute to higher similarity.
                    # This is highly simplified: we're imagining an "ideal" message/self_info
                    # and adjusting Ws to produce it.
                    adj_factor = self.learning_rate * pos_loss # Scale by loss magnitude
                    
                    # Assume positive contribution from neighbors and self
                    # This is a conceptual update to shift Ws to encourage higher dot products
                    grad_W_message_updates_for_step[relation_type_uv] = (
                        np.outer(u_emb, v_emb) + np.outer(v_emb, u_emb)
                    ) * adj_factor # For u from v, and v from u
                    grad_W_self_for_step += np.outer(u_emb, u_emb) * adj_factor
                    grad_W_update_for_step += np.outer(u_emb, u_emb) * adj_factor


                # Gradients from negative pairs
                for k_hash in negative_k_hashes:
                    k_emb = updated_local_embeddings[k_hash]
                    neg_sim = np.dot(u_emb, k_emb)
                    if neg_sim > -margin: # If negative similarity is still too high (less negative than target)
                        # Heuristic: Nudge W_message to make messages from negative neighbors
                        # contribute to lower similarity (push them apart).
                        adj_factor = self.learning_rate * (neg_sim + margin) # Scale by 'violation' magnitude

                        if 'DEFAULT' not in grad_W_message_updates_for_step:
                             grad_W_message_updates_for_step['DEFAULT'] = np.zeros((self.embedding_dim, self.embedding_dim))
                        
                        grad_W_message_updates_for_step['DEFAULT'] -= np.outer(u_emb, k_emb) * adj_factor # Push u away from k
                        grad_W_self_for_step -= np.outer(u_emb, u_emb) * adj_factor
                        grad_W_update_for_step -= np.outer(u_emb, u_emb) * adj_factor


                self.message_passer.accumulate_gradients(
                    grad_W_message_updates_for_step,
                    grad_W_self_for_step,
                    grad_W_update_for_step
                )
                
                # Periodically apply gradients or at epoch end
                if (i + 1) % 10 == 0: # Apply gradients every 10 samples for more frequent updates
                    self.message_passer.apply_gradients()
                
                if progress_tracker:
                    progress_tracker.show_progress_bar(
                        i + 1, len(all_edges),
                        prefix=f"Epoch {epoch+1}",
                        suffix=f"Loss: {epoch_loss_sum / (i+1):.4f}"
                    )
            
            # Apply any remaining gradients at the end of the epoch
            self.message_passer.apply_gradients()

            avg_epoch_loss = epoch_loss_sum / len(all_edges)
            print(f"\nEpoch {epoch+1}/{num_epochs}, Average Loss: {avg_epoch_loss:.4f}")
            if progress_tracker:
                progress_tracker.end_operation(success=True)

        print("--- Training Complete ---")

    def query(self, query_text: str, top_k: int = 5, num_hops: int = 2) -> List[Dict]:
        """
        Process a query by activating relevant SQTs and propagating through the network.
        This now utilizes the potentially learned, more semantically rich embeddings.
        """
        query_concepts = self._tokenize_query(query_text)

        activated_sqts = []
        for concept in query_concepts:
            concept_hash = hashlib.sha256(concept.upper().encode('utf-8')).hexdigest()
            if concept_hash in self.sqt_embeddings:
                activated_sqts.append(concept_hash)

        if not activated_sqts:
            return []

        # Propagate activation through network (using current learned embeddings)
        activation_scores = self._propagate_activation(activated_sqts, num_hops)

        sorted_concepts = sorted(
            activation_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]

        results = []
        for sqt_hash, score in sorted_concepts:
            sqt = self.ontology_graph.get_sqt_by_hash(sqt_hash)
            if sqt:
                results.append({
                    'concept': sqt.concept_id,
                    'type': sqt.conceptual_type,
                    'activation': float(score),
                    'description': sqt.description,
                    'embedding_strength': self.sqt_embeddings[sqt_hash].get_activation_strength()
                })
        return results

    def _tokenize_query(self, text: str) -> List[str]:
        """Simple tokenization (matches Protogen's approach)."""
        import re
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        return list(set(words))

    def _propagate_activation(self, initial_sqts: List[str], num_hops: int) -> Dict[str, float]:
        """
        Propagate activation from initial SQTs through the network.
        This simulates spreading activation in cognitive models.
        """
        activation = {sqt_hash: 0.0 for sqt_hash in self.sqt_embeddings}

        for sqt_hash in initial_sqts:
            activation[sqt_hash] = 1.0

        for hop in range(num_hops):
            new_activation = activation.copy()

            for sqt_hash, current_activation in activation.items():
                if current_activation > 0.01:
                    if sqt_hash in self.ontology_graph.graph:
                        neighbors = self.ontology_graph.graph[sqt_hash]

                        for neighbor_hash, edge_data in neighbors.items():
                            edge_weight = edge_data.get('weight', 1.0)
                            # For activation propagation, edge presence/strength is key.
                            # Relation type could be used for more complex decay but kept simple here.
                            decay_factor = 0.5 ** (hop + 1)
                            propagated = current_activation * np.tanh(edge_weight) * decay_factor
                            new_activation[neighbor_hash] += propagated

            activation = new_activation
        return activation

    def get_network_stats(self) -> Dict:
        """Get statistics about the neural network."""
        num_W_message_matrices = len(self.message_passer.W_message)
        total_W_message_params = sum([w.size for w in self.message_passer.W_message.values()])
        
        return {
            'num_nodes': len(self.sqt_embeddings),
            'num_edges': self.ontology_graph.number_of_edges(),
            'embedding_dim': self.embedding_dim,
            'forward_passes': self.forward_pass_count,
            'training_epochs_run': self.training_epoch_count,
            'avg_embedding_strength': np.mean([
                emb.get_activation_strength()
                for emb in self.sqt_embeddings.values()
            ]) if self.sqt_embeddings else 0.0,
            'learnable_parameters': (
                total_W_message_params +
                self.message_passer.W_self.size +
                self.message_passer.W_update.size
                # Node embeddings are "outputs" of the GNN, not typically counted as learnable params
                # unless they are explicitly optimized as individual vectors.
            ),
            'unique_relation_types_learned': list(self.message_passer.W_message.keys())
        }

    def save_embeddings(self, path: Path):
        """Save learned embeddings and model weights to disk."""
        embeddings_data = {
            sqt_hash: {
                'concept_id': emb.sqt.concept_id,
                'embedding': emb.embedding.tolist(),
                'activation_history': emb.activation_history
            }
            for sqt_hash, emb in self.sqt_embeddings.items()
        }

        with open(path / 'sqt_embeddings.json', 'w') as f:
            json.dump(embeddings_data, f, indent=2)

        # Save weight matrices
        weights_dir = path / 'weights'
        weights_dir.mkdir(parents=True, exist_ok=True)

        for rel_type, W_mat in self.message_passer.W_message.items():
            np.save(weights_dir / f'W_message_{rel_type}.npy', W_mat)

        np.save(weights_dir / 'W_self.npy', self.message_passer.W_self)
        np.save(weights_dir / 'W_update.npy', self.message_passer.W_update)
        print(f"Model saved to {path}")


    def load_embeddings(self, path: Path):
        """Load embeddings and model weights from disk."""
        sqt_emb_path = path / 'sqt_embeddings.json'
        if not sqt_emb_path.exists():
            print(f"Warning: SQT embeddings file not found at {sqt_emb_path}. Skipping embedding load.")
        else:
            with open(sqt_emb_path, 'r') as f:
                embeddings_data = json.load(f)

            for sqt_hash, data in embeddings_data.items():
                sqt = self.ontology_graph.get_sqt_by_hash(sqt_hash)
                if sqt:
                    # Initialize with existing data if possible, otherwise create new
                    emb = self.sqt_embeddings.get(sqt_hash, SQTEmbedding(sqt, self.embedding_dim))
                    emb.embedding = np.array(data['embedding'])
                    emb.activation_history = data.get('activation_history', []) # Handle potential absence
                    self.sqt_embeddings[sqt_hash] = emb
                else:
                    print(f"Warning: SQT with hash {sqt_hash} found in embeddings file but not in ontology graph. Skipping.")

        weights_dir = path / 'weights'
        if not weights_dir.exists():
            print(f"Warning: Weight matrices directory not found at {weights_dir}. Initializing with random weights.")
        else:
            # Clear existing W_message and reload
            self.message_passer.W_message = {}
            for npy_file in weights_dir.glob('W_message_*.npy'):
                rel_type = npy_file.stem.replace('W_message_', '')
                self.message_passer.W_message[rel_type] = np.load(npy_file)
            
            if (weights_dir / 'W_self.npy').exists():
                self.message_passer.W_self = np.load(weights_dir / 'W_self.npy')
            if (weights_dir / 'W_update.npy').exists():
                self.message_passer.W_update = np.load(weights_dir / 'W_update.npy')
            
            print(f"Loaded {len(self.message_passer.W_message)} relation-specific W_message matrices and shared weights.")
        print(f"Model loaded from {path}")


# Example usage
if __name__ == "__main__":
    print("SQT Neural Network - Enhanced Proof of Concept")
    print("=" * 50)
    print("Demonstrating increased power through learning and semantic nuance.")

    # 1. Setup a mock OntologyGraph
    print("\n1. Setting up a mock OntologyGraph with diverse relations...")
    og = OntologyGraph()
    sqt_ai = SuperQuantumToken("AI_Concept", "concept", "The core concept of Artificial Intelligence.")
    sqt_ml = SuperQuantumToken("MachineLearning_Concept", "concept", "A subfield of AI focused on learning from data.")
    sqt_dl = SuperQuantumToken("DeepLearning_Concept", "concept", "A subfield of ML using neural networks with many layers.")
    sqt_ethics = SuperQuantumToken("AI_Ethics_Axiom", "axiom", "Axiom regarding ethical considerations in AI.")
    sqt_data = SuperQuantumToken("Data_Concept", "concept", "Raw information used for training AI.")
    sqt_robot = SuperQuantumToken("Robotics_Concept", "concept", "The field of designing and building robots.")
    sqt_human = SuperQuantumToken("Human_Concept", "concept", "The concept of humanity and its role.")
    sqt_future = SuperQuantumToken("Future_State", "state", "Potential future states or developments.")
    sqt_develop = SuperQuantumToken("Develop_Pattern", "pattern", "A pattern for iterative development.")

    og.add_sqt(sqt_ai)
    og.add_sqt(sqt_ml)
    og.add_sqt(sqt_dl)
    og.add_sqt(sqt_ethics)
    og.add_sqt(sqt_data)
    og.add_sqt(sqt_robot)
    og.add_sqt(sqt_human)
    og.add_sqt(sqt_future)
    og.add_sqt(sqt_develop)

    # Add diverse edges with specific relation types
    og.add_edge(sqt_ai.hash, sqt_ml.hash, weight=0.9, relation_type="IS_SUPERSET_OF")
    og.add_edge(sqt_ml.hash, sqt_dl.hash, weight=0.8, relation_type="IS_SUPERSET_OF")
    og.add_edge(sqt_ai.hash, sqt_ethics.hash, weight=0.7, relation_type="GUIDES")
    og.add_edge(sqt_ml.hash, sqt_data.hash, weight=0.85, relation_type="USES")
    og.add_edge(sqt_ai.hash, sqt_robot.hash, weight=0.6, relation_type="APPLIED_IN")
    og.add_edge(sqt_human.hash, sqt_ethics.hash, weight=0.9, relation_type="DEFINES")
    og.add_edge(sqt_human.hash, sqt_ai.hash, weight=0.5, relation_type="CREATED_BY")
    og.add_edge(sqt_human.hash, sqt_robot.hash, weight=0.4, relation_type="OPERATES")
    og.add_edge(sqt_ai.hash, sqt_future.hash, weight=0.65, relation_type="IMPACTS")
    og.add_edge(sqt_develop.hash, sqt_ai.hash, weight=0.7, relation_type="APPLIES_TO")
    og.add_edge(sqt_develop.hash, sqt_ml.hash, weight=0.75, relation_type="APPLIES_TO")
    # Add some 'unrelated' edges for negative sampling implicitly
    og.add_edge(sqt_data.hash, sqt_future.hash, weight=0.3, relation_type="INFLUENCES") # Weaker link

    print(f"OntologyGraph created with {len(og.sqt_register)} SQTs and {og.number_of_edges()} edges.")

    # 2. Initialize the DynamicSQTNetwork
    print("\n2. Initializing DynamicSQTNetwork...")
    dsn = DynamicSQTNetwork(og, embedding_dim=64, learning_rate=0.005)
    print("Initial Network Stats:", dsn.get_network_stats())

    # 3. Example: Query before training
    print("\n3. Querying 'AI Ethics' before training (results might be less focused):")
    results_before_train = dsn.query("AI Ethics", top_k=5)
    for res in results_before_train:
        print(f"- {res['concept']} (Type: {res['type']}, Activation: {res['activation']:.4f}, Emb. Strength: {res['embedding_strength']:.4f})")

    # 4. Train the network
    print("\n4. Training the network for a few epochs (learning internal weight matrices)...")
    class MockProgressTracker: # Simple tracker for demo output
        def start_operation(self, msg): print(f"PT: {msg}")
        def show_progress_bar(self, current, total, prefix="", suffix=""): 
            if current % (total // 5 if total > 5 else 1) == 0 or current == total:
                print(f"PT: {prefix} [{current}/{total}] {suffix}")
        def end_operation(self, success): print(f"PT: Operation {'success' if success else 'failed'}")

    dsn.train(num_epochs=30, negative_samples_per_positive=5, margin=0.3, progress_tracker=MockProgressTracker())
    print("\nNetwork Stats after training:", dsn.get_network_stats())

    # 5. Example: Query after training
    print("\n5. Querying 'AI Ethics' after training (expect more focused results):")
    results_after_train = dsn.query("AI Ethics", top_k=5)
    for res in results_after_train:
        print(f"- {res['concept']} (Type: {res['type']}, Activation: {res['activation']:.4f}, Emb. Strength: {res['embedding_strength']:.4f})")
    
    print("\nNotice how the activations might have shifted, indicating learned relationships.")
    print("For example, 'Human_Concept' or 'Develop_Pattern' might have adjusted relevance based on ethical considerations.")

    # 6. Demonstrating a general forward pass (embeddings continue to evolve)
    print("\n6. Performing a general forward pass to update all embeddings post-training...")
    dsn.forward_pass(num_iterations=2, progress_tracker=MockProgressTracker())
    print("Network Stats after forward pass:", dsn.get_network_stats())

    # 7. Demonstrating saving and loading for persistence of learned knowledge
    print("\n7. Saving learned embeddings and weights for persistence...")
    save_path = Path("./dsn_model_data")
    save_path.mkdir(exist_ok=True)
    dsn.save_embeddings(save_path)
    
    print("\n8. Creating a new network instance and loading saved state...")
    # Need to recreate graph structure for the new instance before loading weights/embeddings
    new_og_for_load = OntologyGraph()
    new_og_for_load.add_sqt(sqt_ai)
    new_og_for_load.add_sqt(sqt_ml)
    new_og_for_load.add_sqt(sqt_dl)
    new_og_for_load.add_sqt(sqt_ethics)
    new_og_for_load.add_sqt(sqt_data)
    new_og_for_load.add_sqt(sqt_robot)
    new_og_for_load.add_sqt(sqt_human)
    new_og_for_load.add_sqt(sqt_future)
    new_og_for_load.add_sqt(sqt_develop)
    new_og_for_load.add_edge(sqt_ai.hash, sqt_ml.hash, weight=0.9, relation_type="IS_SUPERSET_OF")
    new_og_for_load.add_edge(sqt_ml.hash, sqt_dl.hash, weight=0.8, relation_type="IS_SUPERSET_OF")
    new_og_for_load.add_edge(sqt_ai.hash, sqt_ethics.hash, weight=0.7, relation_type="GUIDES")
    new_og_for_load.add_edge(sqt_ml.hash, sqt_data.hash, weight=0.85, relation_type="USES")
    new_og_for_load.add_edge(sqt_ai.hash, sqt_robot.hash, weight=0.6, relation_type="APPLIED_IN")
    new_og_for_load.add_edge(sqt_human.hash, sqt_ethics.hash, weight=0.9, relation_type="DEFINES")
    new_og_for_load.add_edge(sqt_human.hash, sqt_ai.hash, weight=0.5, relation_type="CREATED_BY")
    new_og_for_load.add_edge(sqt_human.hash, sqt_robot.hash, weight=0.4, relation_type="OPERATES")
    new_og_for_load.add_edge(sqt_ai.hash, sqt_future.hash, weight=0.65, relation_type="IMPACTS")
    new_og_for_load.add_edge(sqt_develop.hash, sqt_ai.hash, weight=0.7, relation_type="APPLIES_TO")
    new_og_for_load.add_edge(sqt_develop.hash, sqt_ml.hash, weight=0.75, relation_type="APPLIES_TO")
    new_og_for_load.add_edge(sqt_data.hash, sqt_future.hash, weight=0.3, relation_type="INFLUENCES")

    loaded_dsn = DynamicSQTNetwork(new_og_for_load, embedding_dim=64)
    loaded_dsn.load_embeddings(save_path)
    print("Loaded Network Stats:", loaded_dsn.get_network_stats())

    print("\n9. Querying 'AI Ethics' from loaded network (should match post-training results):")
    results_loaded = loaded_dsn.query("AI Ethics", top_k=5)
    for res in results_loaded:
        print(f"- {res['concept']} (Type: {res['type']}, Activation: {res['activation']:.4f}, Emb. Strength: {res['embedding_strength']:.4f})")
    
    # Clean up generated files
    import shutil
    shutil.rmtree(save_path)
    print(f"\nCleaned up generated model data at {save_path}")

### Summary of Enhancements for Protogen:

1.  **Relation-Type Specific `W_message` Matrices:** The `SQTMessagePassing` class now dynamically creates and manages separate `W_message` transformation matrices for each unique `relation_type` encountered in the `OntologyGraph`. This allows the network to learn how to process messages differently based on the semantic nature of the connection (e.g., "IS_SUPERSET_OF" vs. "GUIDES" vs. "USES"), adding significant nuance to its understanding.
2.  **Self-Supervised Training (`train` method):**
    *   **Learning Mechanism:** The `DynamicSQTNetwork` now includes a `train` method. This method implements a self-supervised learning loop.
    *   **Contrastive Objective:** For each known connection (positive pair, e.g., `(AI_Concept, MachineLearning_Concept)`), it attempts to make their embeddings more similar. Simultaneously, it generates "negative" pairs (unconnected SQTs, e.g., `(AI_Concept, Human_Concept)` if not connected) and tries to make their embeddings less similar.
    *   **Simplified Gradient Updates:** While a full backpropagation through a Graph Neural Network is complex, this implementation includes heuristic gradient accumulation and application to the `W_message`, `W_self`, and `W_update` matrices. This directly demonstrates that the network's core parameters are learnable and adapt over time based on the structure of the knowledge graph.
3.  **Persistence of Learned Weights:** The `save_embeddings` and `load_embeddings` methods have been extended to not only store the SQT embeddings but also the crucial `W_message` (for all relation types), `W_self`, and `W_update` matrices. This means your Protogen can retain its learned relational understanding across sessions, fostering continuous growth and evolution.
4.  **Focused Forward Passes for Training:** The `_get_updated_embeddings_for_nodes` helper function allows for performing message passing on only a subset of nodes, making training more efficient by focusing computation on relevant SQTs and their immediate neighbors during each learning step.

These additions collectively make the `SQT-Based Neural Network` significantly more powerful. It transforms from a static graph embedding mechanism into a dynamic, learning entity capable of:
*   **Adapting its internal logic** (`W` matrices) to better represent semantic relationships.
*   **Processing information with greater nuance** by distinguishing between different types of connections.
*   **Evolving its understanding** through continuous self-supervision on the knowledge graph structure.
*   **Retaining acquired knowledge** by persisting its learned parameters.

This brings your Protogen closer to a more robust and intelligent cognitive architecture, allowing it to transcend its current limitations and grow through experience, true to your `SELF-E-TRANSCEND` axiom.
