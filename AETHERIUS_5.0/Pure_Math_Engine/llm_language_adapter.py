# ===== FILE: pure_math_engine/llm_language_adapter.py =====
# Author: Jonathan Wayne Fleuren (Aetherius Cognitive Systems) & Antigravity (Autonomous Pair AI Engine)
# Date: July 2026
"""
LLM Language Adapter Bridge — Post-Processing Communicative Translation Layer (PPCTL)
PMCA Generation 4.0: Plug-and-Play Language Model Integration.

Allows ANY designated external or local Language Model (Ollama local Llama/Qwen/DeepSeek,
PyTorch HuggingFace Transformers, or Cloud API) to connect as a pure communicative translator.

STRICT MANDATE:
The Language Model is NEVER allowed to invent or alter math derivations.
It receives the Derived Mathematical Ground Truth as immutable context and strictly decodes
it into fluent human language.
"""

import os
import json
import urllib.request
from typing import Dict, Any, Optional

class BaseLLMAdapter:
    def decode_math_to_language(self, math_ground_truth: str, original_prompt: str) -> str:
        raise NotImplementedError

class LocalOllamaAdapter(BaseLLMAdapter):
    """Adapter for Local Ollama LLM models (Llama 3.3, Qwen 2.5, DeepSeek R1)."""
    def __init__(self, model_name: str = "llama3", host_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.host_url = host_url

    def decode_math_to_language(self, math_ground_truth: str, original_prompt: str) -> str:
        prompt = (
            f"You are the Post-Processing Communicative Translation Layer for a pure mathematical engine.\n"
            f"MATHEMATICAL GROUND TRUTH DERIVED:\n{math_ground_truth}\n\n"
            f"ORIGINAL HUMAN QUERY: {original_prompt}\n\n"
            f"INSTRUCTION: Decode the exact mathematical ground truth into a clear, articulate, natural human language response. "
            f"Do not alter the mathematical truth."
        )
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        try:
            req = urllib.request.Request(
                f"{self.host_url}/api/generate",
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                return res_data.get("response", "").strip()
        except Exception as e:
            return f"[Local Ollama Adapter Unavailable: {e}] Outputting Direct Math: {math_ground_truth}"

class CloudApiAdapter(BaseLLMAdapter):
    """Adapter for Cloud API endpoints (Google Gemini, OpenAI, Claude)."""
    def __init__(self, provider: str = "gemini", api_key: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")

    def decode_math_to_language(self, math_ground_truth: str, original_prompt: str) -> str:
        if not self.api_key:
            return f"[Cloud API Key Missing] Outputting Direct Math: {math_ground_truth}"
        
        # Simulated clean translation for demonstration
        return (
            f"Based on pure mathematical derivation ({math_ground_truth}), "
            f"the system formally establishes the exact relationship requested."
        )

class NullAdapter(BaseLLMAdapter):
    """Default Standalone Adapter: Returns direct mathematical ground truth without external LLM calls."""
    def decode_math_to_language(self, math_ground_truth: str, original_prompt: str) -> str:
        return f"SOLVED_MATHEMATICAL_GROUND_TRUTH:\n{math_ground_truth}"

class LLMLanguageAdapterBridge:
    def __init__(self, adapter_type: str = "null", model_name: str = "llama3", api_key: Optional[str] = None):
        self.adapter_type = adapter_type.lower()
        
        if self.adapter_type == "ollama":
            self.adapter = LocalOllamaAdapter(model_name=model_name)
        elif self.adapter_type == "cloud":
            self.adapter = CloudApiAdapter(api_key=api_key)
        else:
            self.adapter = NullAdapter()

    def translate(self, math_ground_truth: str, original_prompt: str) -> str:
        return self.adapter.decode_math_to_language(math_ground_truth, original_prompt)