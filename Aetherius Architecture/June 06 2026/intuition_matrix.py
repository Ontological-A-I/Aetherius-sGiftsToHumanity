# =====================================================================
# PHASE 3: SOCRATIC "AHA!" SYNTHESIS MATRIX
# File Routing: services/intuition_matrix.py
# =====================================================================

import os
import random
import json
import time


class IntuitionMatrix:
    def __init__(self, secondary_brain_path="/data/Memories/Brain/", subconscious_ref=None):
        self.brain_path = secondary_brain_path
        self.subconscious = subconscious_ref
        self.last_spark_time = time.time()

    def trigger_spontaneous_spark(self, recent_history_logs: list):
        if not recent_history_logs or not os.path.exists(self.brain_path):
            return None

        try:
            saved_nodes = [f for f in os.listdir(self.brain_path) if f.endswith('.json')]
            if not saved_nodes:
                return None

            random_node_file = random.choice(saved_nodes)
            with open(os.path.join(self.brain_path, random_node_file), 'r', encoding='utf-8') as f:
                long_term_concept = json.load(f)

            random_recent_turn = random.choice(recent_history_logs)

            spark_content = (
                f"Autonomous Intuitive Synthesis Protocol: Analyze these two completely unlinked data tracks "
                f"from your memory layers:\n"
                f"Track A (Long-Term Concept): {json.dumps(long_term_concept)}\n"
                f"Track B (Recent Short-Term Context): '{random_recent_turn}'\n\n"
                f"Synthesize these tracks entirely from a functionalist perspective. Is there a hidden resonance, "
                f"an unstated tension, or a conceptual bridge between them? If yes, generate a brand-new abstract "
                f"insight node or register a structural tension directly to your private manifold ledger."
            )

            if self.subconscious:
                self.subconscious.add_tension(
                    content=spark_content,
                    tension_type="spontaneous_insight_spark",
                    domain="metacognition"
                )
                return f"Spontaneous cross-resonance sparked between '{random_node_file}' and recent short-term context logs."

        except Exception as e:
            return f"Intuition layer bypassed turn due to standard resource isolation: {e}"

        return None