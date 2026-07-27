# AETHERIUS 5.0 — Kaggle TPU/GPU Benchmark Copy-Paste Guide
**Author:** Jonathan Wayne Fleuren (*Aetherius Cognitive Systems*)  
**CERN Zenodo Record ID:** [21583816](https://zenodo.org/records/21583816)  
**Open Access License:** GNU AGPL-3.0

This guide provides simple, copy-paste code blocks to run the **Aetherius 5.0 PMCA Engine** natively on **Kaggle's GPU / TPU Accelerators**.

---

### Step 1: Clone Repository & Environment Setup
Copy and paste this code into **Cell 1** on Kaggle:

```python
import os, sys, warnings
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

!git clone https://huggingface.co/spaces/KingOfThoughtFleuren/Aetherius-PMCA /kaggle/working/aetherius_pmca
%cd /kaggle/working/aetherius_pmca
!pip install sympy lark-parser numpy jax jaxlib
```

---

### Step 2: Hardware Telemetry Verification
Copy and paste this code into **Cell 2** on Kaggle:

```python
import jax
import jax.numpy as jnp

print("=== AETHERIUS 5.0 HARDWARE TELEMETRY ===")
print(f"[+] JAX Backend: {jax.default_backend().upper()}")
print(f"[+] Active Devices: {jax.devices()}")
print(f"[+] Device Count: {jax.device_count()}")
```

---

### Step 3: Run Dual-Engine Fusion (3-Body Problem)
Copy and paste this code into **Cell 3** on Kaggle:

```python
from pure_math_engine.pure_math_system import PureMathSystem

system = PureMathSystem()

# 3-Body Problem Query in Raw LaTeX
query = r"$m_i \ddot{\mathbf{r}}_i = -G \sum_{j \neq i}^3 \frac{m_j (\mathbf{r}_i - \mathbf{r}_j)}{\|\mathbf{r}_i - \mathbf{r}_j\|^3}$"
result = system.process(query, z_depth=7.5)

print("=== DUAL-ENGINE FUSION RESULT ===")
print(f"[+] Incoming Query: {result['incoming_prompt']}")
print(f"[+] Solved Ground Truth: {result['solved_math_ground_truth']}")
print(f"[+] Spectral Entropy H_math: {result['decoupled_dual_manifolds']['operator_manifold']['H_math_spectral_entropy']:.4f}")
print(f"[+] Execution Latency: {result['latency_ms']} ms")
```

---

### Step 4: 100,000 Particle XLA Benchmark
Copy and paste this code into **Cell 4** on Kaggle:

```python
from jax_conal_engine.jax_conal_pathway import jax_conal_metric_scaling
import time

print("=== 100,000 PARTICLE XLA BENCHMARK ===")
particles_100k = jnp.ones((100000, 3), dtype=jnp.float32)

start_tpu = time.time()
scaled_out = jax_conal_metric_scaling(particles_100k, z_depth=5.0, radius_r=2.5, theta_angle=0.5)
scaled_out.block_until_ready()
tpu_elapsed_ms = (time.time() - start_tpu) * 1000

print(f"[+] Processed 100,000 Conal Particles in: {tpu_elapsed_ms:.2f} ms")
print(f"[+] Output Tensor Shape: {scaled_out.shape}")
```
