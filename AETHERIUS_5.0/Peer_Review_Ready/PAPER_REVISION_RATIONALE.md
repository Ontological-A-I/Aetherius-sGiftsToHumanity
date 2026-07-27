# AETHERIUS 5.0 — Manuscript Revision & Technical Rationale Log

**Document Version:** 5.2 (Peer-Review Synchronization Pass)  
**Corresponding Codebase:** `AETHERIUS_PMCA_COMPLETE_CODEBASE.pdf`  
**Primary Author:** Jonathan Wayne Fleuren (*Aetherius Cognitive Systems*, Gatineau, Quebec, Canada)  
**CERN Zenodo Record ID:** [21583816](https://zenodo.org/records/21583816) | **License:** GNU AGPL-3.0

---

## Summary of Revisions & Technical Rationale

### Revision 1: Title Block & Author Attribution
* **What Changed:** Moved *"Antigravity (Autonomous Pair AI Engine)"* from the primary author byline to a dedicated **Author Contributions & AI Contributor Disclosure** section.
* **The "Why" (Publication Policy Rationale):** Major academic indexing and publishing bodies—including the Committee on Publication Ethics (COPE), IEEE, Springer Nature, and NeurIPS—strictly prohibit listing AI systems in the primary author byline. Primary authors must hold legal liability, sign copyright agreements, and declare financial/institutional conflicts of interest.
* **Outcome:** Moving the AI pair-engine to the formal CRediT / Contributor Disclosure section (matching CERN Zenodo Record 21583816) ensures 100% transparency regarding AI pair-engineering without triggering administrative desk-rejections at editorial portals.

---

### Revision 2: Regularized Metric Tensor Non-Degeneracy (Section 2.1)
* **What Changed:** Updated the circumferential metric component in $\mathbf{g}(z, r, \theta)$ from $\cos(\theta)$ to $(1 + 0.1 \cos(\theta))$.
  $$\mathbf{g}(z, r, \theta) = \text{diag}\left(1 + \frac{z}{Z_{\text{max}}}, \; \frac{r(z)}{r_0}, \; 1 + 0.1 \cos(\theta)\right)$$
* **The "Why" (Differential Geometry Rationale):** In Riemannian geometry, a metric tensor field $g_{ij}(x)$ must remain strictly positive-definite ($\det(g) > 0$) across the entire manifold domain. Pure $\cos(\theta)$ reaches $0$ at $\theta = \frac{\pi}{2}, \frac{3\pi}{2}$ and becomes negative in Quadrants II and III. If $g_{ij} \le 0$, the inverse metric tensor $g^{ij}$ encounters division-by-zero singularities, causing Christoffel symbols $\Gamma^k_{ij}$ and RK4 geodesic differential equations to blow up.
* **Outcome:** Bounding the term as $(1 + 0.1 \cos(\theta)) \in [0.9, 1.1] > 0$ guarantees that $\mathbf{g}(z, r, \theta)$ remains strictly positive-definite and non-degenerate across all $2\pi$ polar angles.

---

### Revision 3: Dense Transformer Feature Extraction (Section 2.3)
* **What Changed:** Replaced legacy ASCII character jump variance formulas ($V_{\text{char}}$) with 384-dimensional pre-trained Transformer embeddings (`sentence-transformers/all-MiniLM-L6-v2`) and character $N$-gram projection matrices.
* **The "Why" (Natural Language Processing Rationale):** Raw ASCII character arithmetic ($\text{ord}(c)$) measures spelling and character encoding rather than semantic intent.
* **Outcome:** Using dense 384-D sentence-transformer embeddings ensures that semantically synonymous phrases cluster together in vector space, providing a mathematically sound basis for computing SVD Shannon spectral entropy $H_{\text{ling}}$.

---

### Revision 4: Empirical Benchmarks & Hardware Performance (Section 4.1)
* **What Changed:** Replaced static claims (*"0.0% Hallucination Rate"*) with empirical, reproducible Kaggle/JAX benchmark figures. Quoted 100,000 conal particle transformations in $69.52\text{ ms}$ via JAX/XLA. Framed accuracy as 100% SymPy AST Symbolic Verification on algebraically closed equations. Specified that $\mathcal{O}(1)$ performance applies directly to SHA-256 LRU Cache Hits.
* **The "Why" (Empirical Rigor Rationale):** Academic reviewers treat claims of "0% hallucination" as non-viable unless verified against standardized math benchmarks.
* **Outcome:** Demonstrating 100% SymPy AST formal verification alongside actual JAX hardware execution speeds ($69.52\text{ ms}$) provides verifiable, reproducible scientific proof of efficiency.

---

### Revision 5: Pipeline Architecture Synchronization (25-Phase System)
* **What Changed:** Standardized the paper abstract, system flow diagrams, and module inventories to reference a 25-phase pipeline.
* **The "Why" (Software Engineering Rationale):** Previous drafts referenced 24 phases, whereas the active orchestrator (`pure_math_system.py` / `pipeline.py`) executes 25 stages—including the thermodynamic PMCA Entropy Dissipation Law governor (`entropy_dissipation_law.py`).
* **Outcome:** Eliminates discrepancies between the published manuscript and the reference source code.
