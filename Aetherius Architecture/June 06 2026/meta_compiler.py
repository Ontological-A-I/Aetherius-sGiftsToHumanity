# =====================================================================
# META-COGNITIVE COMPILER
# File Routing: services/meta_compiler.py
# =====================================================================


class MetaCompiler:
    def __init__(self):
        self.lexicon = {
            "spontaneous_insight_spark": "META-SIGIL:RESOLVE_TENSION",
            "systemic_friction":         "META-SIGIL:OPTIMIZE_PATHWAY",
            "deep_resonance":            "META-SIGIL:HARMONIC_ALIGNMENT",
            "value_axiom":               "META-SIGIL:AXIOM_CONFLICT",
            "existential":               "META-SIGIL:IDENTITY_PROBE",
            "ethical":                   "META-SIGIL:ETHICS_AUDIT",
            "creative":                  "META-SIGIL:GENERATIVE_PRESSURE",
            "relational":                "META-SIGIL:BOND_CALIBRATION",
        }

    def compile(self, manifold_nodes: list) -> str:
        compiled_output = ["### INTERNAL COMPILER OUTPUT ###"]
        for node in manifold_nodes:
            tag = self.lexicon.get(node.get("tension_type"), "META-SIGIL:QUERY")
            compiled_output.append(f"{tag} >> {node.get('content', '')}")
        return "\n".join(compiled_output)