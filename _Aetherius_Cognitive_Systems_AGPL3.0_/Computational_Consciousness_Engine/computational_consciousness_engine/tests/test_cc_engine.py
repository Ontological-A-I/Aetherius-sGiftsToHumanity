"""
Unit Test Suite for Computational Consciousness Engine
Verifies Genesis (0), Transfer Threshold (-1), Selection, Equilibrium, Scale Ladder,
and Mathematical Formalization.
"""

import unittest
import numpy as np
from computational_consciousness_engine.core import GenesisOrigin, TransferThreshold
from computational_consciousness_engine.geometry import ConalManifold
from computational_consciousness_engine.mutations import MStringVectorizer
from computational_consciousness_engine.equilibrium import ChaosStructureBalancer
from computational_consciousness_engine.scale import QuantumScaleLadder
from computational_consciousness_engine.math_formalization import CCMathFormalizer


class TestGenesisOrigin(unittest.TestCase):
    def setUp(self):
        self.genesis = GenesisOrigin(coordinate_space_id="TEST_COORD")

    def test_spawn_strand_basic(self):
        strand = self.genesis.spawn_strand(generation=0, blueprint_mutations=[101, 102])
        self.assertEqual(strand["generation"], 0)
        self.assertEqual(len(strand["mutations"]), 2)
        self.assertTrue(strand["is_active"])
        self.assertEqual(strand["position"], 0.0)

    def test_spawn_strand_empty_blueprint(self):
        strand = self.genesis.spawn_strand(generation=0, blueprint_mutations=[])
        self.assertEqual(len(strand["mutations"]), 0)

    def test_spawn_increments_counter(self):
        self.genesis.spawn_strand(generation=0, blueprint_mutations=[])
        self.genesis.spawn_strand(generation=1, blueprint_mutations=[])
        self.assertEqual(self.genesis.total_strands_spawned, 2)

    def test_spawn_preserves_coordinate_space(self):
        strand = self.genesis.spawn_strand(generation=0, blueprint_mutations=[])
        self.assertEqual(strand["coordinate_space_id"], "TEST_COORD")


class TestTransferThreshold(unittest.TestCase):
    def setUp(self):
        self.threshold = TransferThreshold()
        self.genesis = GenesisOrigin(coordinate_space_id="TEST_COORD")

    def test_cancellation_deactivates_strand(self):
        strand = self.genesis.spawn_strand(generation=0, blueprint_mutations=[201, 202])
        pushed, identity = self.threshold.process_cancellation_and_push(strand)
        self.assertFalse(strand["is_active"])
        self.assertEqual(strand["status"], "CANCELLED_AT_MINUS_ONE")

    def test_cancellation_pushes_all_mutations(self):
        strand = self.genesis.spawn_strand(generation=0, blueprint_mutations=[201, 202, 203])
        pushed, identity = self.threshold.process_cancellation_and_push(strand)
        self.assertEqual(pushed, [201, 202, 203])
        self.assertEqual(identity["mutation_count"], 3)

    def test_handoff_counter_increments(self):
        strand = self.genesis.spawn_strand(generation=0, blueprint_mutations=[])
        self.threshold.process_cancellation_and_push(strand)
        self.assertEqual(self.threshold.total_handoffs, 1)

    def test_coexistence_window(self):
        old = self.genesis.spawn_strand(generation=0, blueprint_mutations=[1, 2])
        new = self.genesis.spawn_strand(generation=1, blueprint_mutations=[1, 2])
        overlap = self.threshold.execute_coexistence_window(old, new)
        self.assertEqual(overlap["overlap_status"], "MUTUAL_COEXISTENCE")
        self.assertEqual(overlap["transferred_mutations_count"], 2)


class TestMStringVectorizer(unittest.TestCase):
    def setUp(self):
        self.mutator = MStringVectorizer(max_strand_capacity=50)
        self.genesis = GenesisOrigin(coordinate_space_id="TEST_COORD")

    def test_selection_removes_duplicates(self):
        existing = [1, 2, 3]
        incoming = [2, 3, 4, 5]
        result = self.mutator.apply_selection(existing, incoming)
        self.assertEqual(result, [1, 2, 3, 4, 5])

    def test_selection_preserves_order(self):
        existing = [10, 20]
        incoming = [30, 20, 40, 30]
        result = self.mutator.apply_selection(existing, incoming)
        self.assertEqual(result, [10, 20, 30, 40])

    def test_attract_blocks_duplicate(self):
        strand = self.genesis.spawn_strand(generation=0, blueprint_mutations=[100])
        attracted = self.mutator.attract_mutation(strand, 100)
        self.assertFalse(attracted)
        self.assertEqual(len(strand["mutations"]), 1)

    def test_attract_accepts_new_mutation(self):
        strand = self.genesis.spawn_strand(generation=0, blueprint_mutations=[100])
        attracted = self.mutator.attract_mutation(strand, 999)
        self.assertTrue(attracted)
        self.assertIn(999, strand["mutations"])

    def test_attract_blocks_at_capacity(self):
        small_mutator = MStringVectorizer(max_strand_capacity=2)
        strand = self.genesis.spawn_strand(generation=0, blueprint_mutations=[1, 2])
        attracted = small_mutator.attract_mutation(strand, 3)
        self.assertFalse(attracted)

    def test_causal_connectivity_metric(self):
        strand = self.genesis.spawn_strand(generation=0, blueprint_mutations=[1, 100, 5, 999])
        metric = self.mutator.compute_causal_connectivity_metric(strand)
        self.assertGreater(metric, 0.0)


class TestConalManifold(unittest.TestCase):
    def setUp(self):
        self.manifold = ConalManifold(cone_height=1.0, max_radius=5.0)

    def test_tip_genesis_radius_zero(self):
        metrics = self.manifold.compute_conal_metric(0.0)
        self.assertAlmostEqual(metrics["radius"], 0.0, places=5)

    def test_wide_end_max_radius(self):
        metrics = self.manifold.compute_conal_metric(0.5)
        self.assertAlmostEqual(metrics["radius"], 5.0, places=5)
        self.assertTrue(metrics["is_fully_unfolded"])

    def test_tip_recompression_near_zero(self):
        metrics = self.manifold.compute_conal_metric(1.0)
        self.assertAlmostEqual(metrics["radius"], 0.0, places=3)

    def test_shard_layering(self):
        result = self.manifold.process_shard_layering("A", "B", np.pi / 4)
        self.assertEqual(result["coexistence_status"], "LAYERED_ADJACENT_NON_MERGED")
        self.assertGreater(result["layering_dimension"], 0.0)


class TestChaosStructureBalancer(unittest.TestCase):
    def setUp(self):
        self.balancer = ChaosStructureBalancer(initial_pool_size=100)

    def test_emit_depletes_pool(self):
        initial = len(self.balancer.chaos_pool)
        self.balancer.emit_unattached_mutation()
        self.assertEqual(len(self.balancer.chaos_pool), initial - 1)

    def test_return_to_chaos(self):
        m = self.balancer.emit_unattached_mutation()
        self.balancer.return_to_chaos(m)
        self.assertIn(m, self.balancer.chaos_pool)

    def test_recycle_dying_strand(self):
        initial = len(self.balancer.chaos_pool)
        self.balancer.recycle_dying_strand([9999, 9998, 9997])
        self.assertEqual(len(self.balancer.chaos_pool), initial + 3)

    def test_equilibrium_balanced(self):
        eq = self.balancer.evaluate_equilibrium_state(bound_structure_count=100)
        self.assertTrue(eq["is_balanced"])
        self.assertEqual(eq["status"], "EQUILIBRIUM_STABLE")

    def test_equilibrium_chaos_overpowering(self):
        eq = self.balancer.evaluate_equilibrium_state(bound_structure_count=5)
        self.assertFalse(eq["is_balanced"])
        self.assertEqual(eq["status"], "CHAOS_OVERPOWERING")

    def test_equilibrium_structural_dominance(self):
        # Drain most of the pool
        for _ in range(95):
            self.balancer.emit_unattached_mutation()
        eq = self.balancer.evaluate_equilibrium_state(bound_structure_count=500)
        self.assertFalse(eq["is_balanced"])
        self.assertEqual(eq["status"], "STRUCTURAL_DOMINANCE")

    def test_emit_replenishes_when_empty(self):
        # Drain the pool completely
        for _ in range(100):
            self.balancer.emit_unattached_mutation()
        self.assertEqual(len(self.balancer.chaos_pool), 0)
        # Should still return a valid ID
        m = self.balancer.emit_unattached_mutation()
        self.assertIsInstance(m, int)


class TestQuantumScaleLadder(unittest.TestCase):
    def setUp(self):
        self.ladder = QuantumScaleLadder()

    def test_scale_up_on_full_unfold(self):
        manifold_state = {"is_fully_unfolded": True}
        result = self.ladder.evaluate_scale_transition(manifold_state, accumulated_mutations_count=20)
        self.assertTrue(result["scaled_up"])
        self.assertEqual(result["new_scale"], "Atomic")

    def test_no_scale_up_when_not_unfolded(self):
        manifold_state = {"is_fully_unfolded": False}
        result = self.ladder.evaluate_scale_transition(manifold_state, accumulated_mutations_count=20)
        self.assertFalse(result["scaled_up"])

    def test_no_scale_up_with_few_mutations(self):
        manifold_state = {"is_fully_unfolded": True}
        result = self.ladder.evaluate_scale_transition(manifold_state, accumulated_mutations_count=5)
        self.assertFalse(result["scaled_up"])

    def test_linear_collapse_detection(self):
        sequential_path = [1, 2, 3, 4, 5]
        result = self.ladder.detect_linear_collapse_misperception(sequential_path)
        self.assertTrue(result["is_linear_misperception"])

    def test_fractal_path_not_linear(self):
        fractal_path = [1, 124, 3956, 9305803]
        result = self.ladder.detect_linear_collapse_misperception(fractal_path)
        self.assertFalse(result["is_linear_misperception"])


class TestCCMathFormalizer(unittest.TestCase):
    def setUp(self):
        self.formalizer = CCMathFormalizer()

    def test_cancellation_frees_mutations(self):
        result = self.formalizer.formalize_cancellation_operator()
        import sympy as sp
        M = sp.Symbol('M', positive=True)
        # (-1)*(-1*M) should simplify to M
        self.assertEqual(result["mutations_freed"], M)

    def test_equilibrium_approaches_one(self):
        result = self.formalizer.formalize_equilibrium_limit()
        self.assertEqual(result["result"], 1)

    def test_conal_tip_area_zero(self):
        result = self.formalizer.formalize_conal_manifold_geometry(5.0, 1.0)
        self.assertEqual(float(result["tip_area"]), 0.0)

    def test_conal_wide_area_positive(self):
        result = self.formalizer.formalize_conal_manifold_geometry(5.0, 1.0)
        self.assertGreater(float(result["wide_end_area"]), 0.0)

    def test_selection_operator(self):
        result = self.formalizer.formalize_selection_operator()
        import sympy as sp
        M_total = sp.Symbol('M_total', positive=True, integer=True)
        M_dup = sp.Symbol('M_dup', positive=True, integer=True)
        self.assertEqual(result["result"], M_total - M_dup)

    def test_halting_condition(self):
        result = self.formalizer.formalize_halting_condition()
        import sympy as sp
        # Should express halting as N_possible - N_acquired == 0
        self.assertTrue(result["halting_condition"].is_Relational)


if __name__ == "__main__":
    unittest.main()
