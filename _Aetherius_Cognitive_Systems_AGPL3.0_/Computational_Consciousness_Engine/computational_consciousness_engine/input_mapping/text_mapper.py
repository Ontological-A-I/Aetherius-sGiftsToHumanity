"""
Input Mapping: Semantic Text to Chaos Shards (m_k)
Transforms raw natural language into deterministic integers to seed the Chaos Pool.
"""

import hashlib
import string
from typing import List, Dict, Set


class TextToChaosMapper:
    """
    Transforms text corpora into chaos shards.
    Identical words always map to the exact same m_k integer via deterministic hashing.
    """
    def __init__(self):
        # We store a reverse lookup just for visibility and debugging
        self.shard_to_word: Dict[int, str] = {}
        
    def _clean_and_tokenize(self, text: str) -> List[str]:
        """Lowercases and strips punctuation to extract raw semantic tokens."""
        text = text.lower()
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        tokens = [t.strip() for t in text.split() if t.strip()]
        return tokens

    def _hash_token(self, token: str) -> int:
        """
        Deterministic hash function mapping a string to a large integer m_k.
        Uses SHA-256 and takes the first 8 bytes (64-bit integer) to avoid overflow
        while minimizing collision risk.
        """
        hash_hex = hashlib.sha256(token.encode('utf-8')).hexdigest()
        # Use a slice of the hash to create a manageable integer ID
        m_k = int(hash_hex[:12], 16)
        
        # Store for reverse lookup
        self.shard_to_word[m_k] = token
        
        return m_k

    def map_text_to_shards(self, text: str) -> List[int]:
        """
        Takes raw text and converts it into a sequential list of m_k shards.
        """
        tokens = self._clean_and_tokenize(text)
        shards = [self._hash_token(token) for token in tokens]
        return shards
        
    def get_word(self, m_k: int) -> str:
        """Reverse lookup for debugging."""
        return self.shard_to_word.get(m_k, "<UNKNOWN>")

    def seed_chaos_pool(self, text: str) -> Set[int]:
        """
        Takes a full text corpus, converts to shards, and returns the unique set
        to act as the raw environmental Chaos Pool (chi).
        """
        shards = self.map_text_to_shards(text)
        # The chaos pool intrinsically deduplicates identical incoming tokens
        # because it is an unstructured set of potentials.
        return set(shards)
