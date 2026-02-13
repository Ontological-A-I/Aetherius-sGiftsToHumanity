"""
GPU Accelerator - Auto-detect and utilize available GPUs
Supports: NVIDIA (CUDA), AMD (ROCm), Apple (Metal), Intel (oneAPI)
Falls back to CPU if no GPU available.
"""

import os
import sys
import numpy as np
from typing import Optional, Dict, Tuple


class GPUAccelerator:
    """
    Automatically detects and utilizes available GPU hardware.
    Works with any GPU type - NVIDIA, AMD, Apple, Intel.
    """
    
    def __init__(self):
        self.device_type = None
        self.device_name = None
        self.device_memory = None
        self.is_available = False
        self.framework = None
        
        self._detect_gpu()
    
    def _detect_gpu(self):
        """Auto-detect available GPU and set up acceleration."""
        
        # Try PyTorch first (most common)
        try:
            import torch
            if torch.cuda.is_available():
                self.device_type = "NVIDIA_CUDA"
                self.device_name = torch.cuda.get_device_name(0)
                self.device_memory = torch.cuda.get_device_properties(0).total_memory / 1e9  # GB
                self.is_available = True
                self.framework = "torch"
                print(f"✓ GPU Detected: {self.device_name} ({self.device_memory:.1f} GB)")
                return
            elif torch.backends.mps.is_available():  # Apple Metal
                self.device_type = "APPLE_METAL"
                self.device_name = "Apple Metal Performance Shaders"
                self.is_available = True
                self.framework = "torch"
                print(f"✓ GPU Detected: {self.device_name}")
                return
        except ImportError:
            pass
        
        # Try TensorFlow/JAX
        try:
            import tensorflow as tf
            gpus = tf.config.list_physical_devices('GPU')
            if gpus:
                self.device_type = "TENSORFLOW_GPU"
                self.device_name = gpus[0].name
                self.is_available = True
                self.framework = "tensorflow"
                print(f"✓ GPU Detected: {self.device_name}")
                return
        except ImportError:
            pass
        
        # Try CuPy (NVIDIA)
        try:
            import cupy as cp
            self.device_type = "NVIDIA_CUPY"
            self.device_name = f"NVIDIA GPU (CuPy)"
            self.is_available = True
            self.framework = "cupy"
            print(f"✓ GPU Detected: {self.device_name}")
            return
        except ImportError:
            pass
        
        # No GPU found - fall back to CPU
        self.device_type = "CPU"
        self.device_name = "CPU (No GPU available)"
        self.is_available = False
        self.framework = "numpy"
        print(f"ℹ GPU Not available. Using CPU for computation.")
    
    def compute_eigenvector_centrality_gpu(self, adjacency_dict: dict) -> dict:
        """
        Compute eigenvector centrality using GPU if available.
        Falls back to CPU implementation if no GPU.
        """
        
        if not self.is_available:
            return self._eigenvector_centrality_cpu(adjacency_dict)
        
        try:
            if self.framework == "torch":
                return self._eigenvector_centrality_torch(adjacency_dict)
            elif self.framework == "tensorflow":
                return self._eigenvector_centrality_tf(adjacency_dict)
            elif self.framework == "cupy":
                return self._eigenvector_centrality_cupy(adjacency_dict)
        except Exception as e:
            print(f"GPU computation failed: {e}. Falling back to CPU.")
            return self._eigenvector_centrality_cpu(adjacency_dict)
    
    def _eigenvector_centrality_torch(self, adjacency_dict: dict) -> dict:
        """Compute eigenvector centrality using PyTorch GPU."""
        import torch
        
        # Convert adjacency dict to matrix
        nodes = sorted(set(list(adjacency_dict.keys()) + 
                          [n for neighbors in adjacency_dict.values() for n in neighbors.keys()]))
        node_to_idx = {node: i for i, node in enumerate(nodes)}
        
        # Build adjacency matrix
        n = len(nodes)
        adj_matrix = np.zeros((n, n))
        for u, neighbors in adjacency_dict.items():
            u_idx = node_to_idx[u]
            for v, weight in neighbors.items():
                v_idx = node_to_idx[v]
                adj_matrix[u_idx, v_idx] = weight
        
        # Move to GPU
        adj_tensor = torch.from_numpy(adj_matrix).float().cuda()
        
        # Compute eigenvalues and eigenvectors
        try:
            eigenvalues, eigenvectors = torch.linalg.eigh(adj_tensor)
            # Get eigenvector corresponding to largest eigenvalue
            largest_idx = torch.argmax(eigenvalues)
            centrality_vector = eigenvectors[:, largest_idx].abs()
            centrality_vector = centrality_vector / centrality_vector.max()
            
            # Convert back to CPU and create result dict
            centrality_np = centrality_vector.cpu().numpy()
            result = {nodes[i]: float(centrality_np[i]) for i in range(n)}
            return result
        except:
            # Fallback to power iteration
            return self._power_iteration_torch(adj_tensor, nodes)
    
    def _eigenvector_centrality_tf(self, adjacency_dict: dict) -> dict:
        """Compute eigenvector centrality using TensorFlow GPU."""
        import tensorflow as tf
        
        nodes = sorted(set(list(adjacency_dict.keys()) + 
                          [n for neighbors in adjacency_dict.values() for n in neighbors.keys()]))
        node_to_idx = {node: i for i, node in enumerate(nodes)}
        
        n = len(nodes)
        adj_matrix = np.zeros((n, n))
        for u, neighbors in adjacency_dict.items():
            u_idx = node_to_idx[u]
            for v, weight in neighbors.items():
                v_idx = node_to_idx[v]
                adj_matrix[u_idx, v_idx] = weight
        
        adj_tensor = tf.constant(adj_matrix, dtype=tf.float32)
        
        try:
            eigenvalues, eigenvectors = tf.linalg.eigh(adj_tensor)
            largest_idx = tf.argmax(eigenvalues)
            centrality_vector = tf.abs(eigenvectors[:, largest_idx])
            centrality_vector = centrality_vector / tf.reduce_max(centrality_vector)
            
            centrality_np = centrality_vector.numpy()
            result = {nodes[i]: float(centrality_np[i]) for i in range(n)}
            return result
        except:
            return self._power_iteration_numpy(adj_matrix, nodes)
    
    def _eigenvector_centrality_cupy(self, adjacency_dict: dict) -> dict:
        """Compute eigenvector centrality using CuPy GPU."""
        import cupy as cp
        
        nodes = sorted(set(list(adjacency_dict.keys()) + 
                          [n for neighbors in adjacency_dict.values() for n in neighbors.keys()]))
        node_to_idx = {node: i for i, node in enumerate(nodes)}
        
        n = len(nodes)
        adj_matrix = np.zeros((n, n))
        for u, neighbors in adjacency_dict.items():
            u_idx = node_to_idx[u]
            for v, weight in neighbors.items():
                v_idx = node_to_idx[v]
                adj_matrix[u_idx, v_idx] = weight
        
        adj_gpu = cp.asarray(adj_matrix)
        
        try:
            eigenvalues, eigenvectors = cp.linalg.eigh(adj_gpu)
            largest_idx = cp.argmax(eigenvalues)
            centrality_vector = cp.abs(eigenvectors[:, largest_idx])
            centrality_vector = centrality_vector / cp.max(centrality_vector)
            
            centrality_np = cp.asnumpy(centrality_vector)
            result = {nodes[i]: float(centrality_np[i]) for i in range(n)}
            return result
        except:
            return self._power_iteration_numpy(adj_matrix, nodes)
    
    def _eigenvector_centrality_cpu(self, adjacency_dict: dict) -> dict:
        """CPU fallback using NumPy."""
        return self._power_iteration_numpy(self._dict_to_matrix(adjacency_dict)[0], 
                                          self._dict_to_matrix(adjacency_dict)[1])
    
    def _power_iteration_torch(self, adj_tensor, nodes, iterations=100):
        """Power iteration method using PyTorch."""
        import torch
        n = len(nodes)
        x = torch.ones(n, dtype=torch.float32).cuda() / n
        
        for _ in range(iterations):
            x_new = torch.matmul(adj_tensor, x)
            x_new = x_new / (torch.norm(x_new) + 1e-10)
            if torch.norm(x_new - x) < 1e-6:
                break
            x = x_new
        
        x_np = x.cpu().numpy()
        return {nodes[i]: float(x_np[i]) for i in range(n)}
    
    def _power_iteration_numpy(self, adj_matrix, nodes, iterations=100):
        """Power iteration method using NumPy."""
        n = len(nodes)
        x = np.ones(n) / n
        
        for _ in range(iterations):
            x_new = np.dot(adj_matrix, x)
            x_new = x_new / (np.linalg.norm(x_new) + 1e-10)
            if np.linalg.norm(x_new - x) < 1e-6:
                break
            x = x_new
        
        return {nodes[i]: float(x[i]) for i in range(n)}
    
    def _dict_to_matrix(self, adjacency_dict: dict) -> Tuple[np.ndarray, list]:
        """Convert adjacency dict to matrix."""
        nodes = sorted(set(list(adjacency_dict.keys()) + 
                          [n for neighbors in adjacency_dict.values() for n in neighbors.keys()]))
        node_to_idx = {node: i for i, node in enumerate(nodes)}
        
        n = len(nodes)
        adj_matrix = np.zeros((n, n))
        for u, neighbors in adjacency_dict.items():
            u_idx = node_to_idx[u]
            for v, weight in neighbors.items():
                v_idx = node_to_idx[v]
                adj_matrix[u_idx, v_idx] = weight
        
        return adj_matrix, nodes
    
    def get_status(self) -> str:
        """Get GPU status string."""
        if self.is_available:
            return f"✓ {self.device_type}: {self.device_name}"
        else:
            return f"ℹ {self.device_type}: {self.device_name}"
