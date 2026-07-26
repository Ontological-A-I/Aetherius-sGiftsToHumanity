# ===== FILE: pure_math_engine/communicative_translation.py =====
# Author: Jonathan Wayne Fleuren (Aetherius Cognitive Systems) & Antigravity (Autonomous Pair AI Engine)
# Date: July 2026
"""
Dual-End Communicative Translator — PMCA Generation 4.0
Handles Incoming (Language -> Math) and Outgoing (Math -> Language) translations.
Integrates pluggable LLMLanguageAdapterBridge for designated Language Models.
"""

import os
import re
import math
from typing import Dict, Any, Optional
from .llm_language_adapter import LLMLanguageAdapterBridge

class DualEndCommunicativeTranslator:
    def __init__(self, adapter_type: str = "null", model_name: str = "llama3", api_key: Optional[str] = None):
        self.llm_bridge = LLMLanguageAdapterBridge(
            adapter_type=adapter_type,
            model_name=model_name,
            api_key=api_key
        )

    def set_language_adapter(self, adapter_type: str, model_name: str = "llama3", api_key: Optional[str] = None):
        """Dynamically attach or switch designated Language Model adapter."""
        self.llm_bridge = LLMLanguageAdapterBridge(
            adapter_type=adapter_type,
            model_name=model_name,
            api_key=api_key
        )

    def translate_incoming_language_to_math(self, raw_language_query: str) -> str:
        """
        Translates raw human language into a formal mathematical query formulation.
        Runs 100% standalone using rule-based pattern extraction.
        """
        cleaned = raw_language_query.strip()
        
        if "derivative" in cleaned.lower() or "d/dx" in cleaned.lower():
            expr = re.sub(r'(?i)derivative of|d/dx|find', '', cleaned).strip()
            return f"Math formulation of: derivative({expr}, x)"
        elif "integral" in cleaned.lower() or "integrate" in cleaned.lower():
            expr = re.sub(r'(?i)integral of|integrate|find', '', cleaned).strip()
            return f"Math formulation of: integrate({expr}, x)"
        elif "solve" in cleaned.lower() or "=" in cleaned:
            expr = re.sub(r'(?i)solve for x:|solve', '', cleaned).strip()
            return f"Math formulation of: solve({expr}, x)"
        else:
            return f"Math formulation of: simplify({cleaned})"

    def translate_outgoing_math_to_language(
        self,
        math_ground_truth: str,
        alignment_score: float,
        conal_metrics: Dict[str, Any],
        original_prompt: str = ""
    ) -> str:
        """
        Translates derived mathematical ground truth into a clear human language response
        using the designated connected Language Model adapter.
        """
        decoded_text = self.llm_bridge.translate(math_ground_truth, original_prompt)
        
        outgoing_text = (
            f"{decoded_text}\n\n"
            f"[Metric Invariants: Alignment Score = {alignment_score:.4f}, "
            f"Conal Depth z = {conal_metrics.get('z_depth', 0.0)}, "
            f"Radius r = {conal_metrics.get('radius_r', 0.0)}]"
        )
        return outgoing_text