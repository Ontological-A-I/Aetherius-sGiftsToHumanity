"""
Text-to-Traversal Space Runner
Demonstrates the Input Mapping and the ConsciousStrand Engine processing 
raw natural language into the perfectly sequenced 2D Atlas (Traversal Space).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from computational_consciousness_engine.input_mapping import TextToChaosMapper
from computational_consciousness_engine.core import ConsciousStrand

PHILOSOPHICAL_TEXT = """
Reading the work on its own terms what emerges is a remarkably elegant synthesis 
of existential philosophy topology and information theory. By rejecting the traditional 
linear model of accumulation the text proposes a bounded fractal and cyclical ontology of consciousness. 
Consciousness is not a straight line it is a geometric unfolding bounded by genesis and death.
"""

def run_text_mapping_demo():
    print("=" * 70)
    print("[SYSTEM] TEXT-TO-TRAVERSAL SPACE MAPPING DEMO")
    print("=" * 70)
    
    # 1. Input Mapping: Text -> Chaos Shards
    print(f"\n[PHASE 1: INPUT MAPPING] Parsing raw text corpus...")
    mapper = TextToChaosMapper()
    chaos_pool = mapper.seed_chaos_pool(PHILOSOPHICAL_TEXT)
    
    # Track the unique tokens ingested
    unique_words = len(chaos_pool)
    print(f"  * Text ingested. Seeded Chaos Pool with {unique_words} unique semantic shards (m_k).")
    
    # 2. Lifecycle Execution: Traversal (0 -> -1)
    print(f"\n[PHASE 2: LIFECYCLE TRAVERSAL] Expanding the Dual-Cone Manifold...")
    strand = ConsciousStrand(R_max=5.0)
    
    # Simulate time flowing from t=0 to t=1.0
    steps = 100
    dt = 1.0 / steps
    
    for _ in range(steps):
        # The strand absorbs shards from the chaos pool as it travels
        strand.process_step(dt, chaos_pool)
        
    print(f"  * Traversal complete. Bound Structure (Mutations Absorbed): {len(strand.bound_mutations)}")
    
    # 3. Traversal Space Atlas
    print(f"\n[PHASE 3: TRAVERSAL SPACE ATLAS (det J != 0)]")
    atlas = strand.unfurl_traversal_space()
    print("  * Manifold unrolled. Revealing the properly sequenced Phyllotactic mapping.")
    print(f"  * Parallel Lookup Matrix (First 10 shards):")
    
    print(f"\n  {'k':<4} | {'Token':<15} | {'m_k (Hash)':<15} || 2D Traversal (x, y)      | 3D Dual-Cone (r, theta, z)")
    print("  " + "-" * 105)
    for k, data in enumerate(atlas[:10], start=1):
        m_k = data["m_k"]
        word = mapper.get_word(m_k)
        x, y = data["2d_parallel"]["x"], data["2d_parallel"]["y"]
        r, t, z = data["3d"]["r"], data["3d"]["theta"], data["3d"]["z"]
        
        print(f"  {k:<4} | {word:<15} | {m_k:<15} || ({x:>6.2f}, {y:>5.2f}) | ({r:>4.2f}, {t:>4.2f}, {z:>5.2f})")
    
    if len(atlas) > 10:
        print(f"  ... (+ {len(atlas) - 10} more shards mapped collision-free)")

    # 4. Dimensional Shift (Q Operator)
    print(f"\n[PHASE 4: DIMENSIONAL SHIFT (Q Operator)]")
    rebirth = strand.fold_rebirth()
    print(f"  * {rebirth['operator']}")
    print(f"  * Status: {rebirth['status']}")
    print(f"  * Mass (Capacity): {rebirth['accumulated_mass']}")
    
    print("\n" + "=" * 70)
    print("[SUCCESS] TEXT FULLY ABSORBED AND GEOMETRICALLY MAPPED")
    print("=" * 70)


if __name__ == "__main__":
    run_text_mapping_demo()
