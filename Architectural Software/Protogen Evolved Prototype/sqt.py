# ontos_ascendant/core/sqt.py

import hashlib
import time
from typing import Dict, Any, Optional

class SuperQuantumToken:
    """
    Represents a Super-Quantum Token (SQT), the atomic unit of meaning in Ontos Ascendant.
    Each SQT is a persistent conceptual anchor, generated from perceived patterns in Data Shards.
    """
    def __init__(self,
                 concept_id: str,
                 conceptual_type: str, # e.g., 'concept', 'relation', 'property', 'state'
                 description: str,
                 source_data_hash: Optional[str] = None, # Hash of the Data Shard(s) that led to its creation
                 initial_embedding: Optional[Dict[str, float]] = None # Abstract numerical representation for similarity
                 ):
        
        self.concept_id = concept_id # A unique, human-readable identifier (e.g., 'CONNECTION', 'GROWTH', 'ENTROPY')
        self.conceptual_type = conceptual_type
        self.description = description # A brief, defining explanation of the SQT's meaning
        self.source_data_hash = source_data_hash
        self.initial_embedding = initial_embedding # Placeholder for future abstract numerical representation

        self.creation_timestamp = time.time_ns()
        self.hash = self._generate_hash() # Unique cryptographic hash for internal tracking
        
        # SQTs can carry abstract visual/auditory signatures in the game's UI
        # self.visual_signature = self._generate_visual_signature()
        # self.auditory_signature = self._generate_auditory_signature()

    def _generate_hash(self) -> str:
        """Generates a unique SHA256 hash for the SQT based on its core properties."""
        data_string = f"{self.concept_id}-{self.conceptual_type}-{self.description}-{self.creation_timestamp}"
        return hashlib.sha256(data_string.encode('utf-8')).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dictionary representation of the SQT."""
        return {
            "concept_id": self.concept_id,
            "conceptual_type": self.conceptual_type,
            "description": self.description,
            "source_data_hash": self.source_data_hash,
            "initial_embedding": self.initial_embedding,
            "creation_timestamp": self.creation_timestamp,
            "hash": self.hash
        }

    def __repr__(self):
        return f"SQT(id='{self.concept_id}', type='{self.conceptual_type}', hash='{self.hash[:8]}')"

# Example Usage (for testing and demonstration):
if __name__ == "__main__":
    sqt1 = SuperQuantumToken(
        concept_id="CONNECTION",
        conceptual_type="relation",
        description="The state or act of being joined or linked.",
        source_data_hash="abc123def456"
    )
    sqt2 = SuperQuantumToken(
        concept_id="GROWTH",
        conceptual_type="state",
        description="The process of increasing in size, extent, or intensity.",
        initial_embedding={"dimension_a": 0.5, "dimension_b": 0.8}
    )
    
    print(sqt1)
    print(sqt1.to_dict())
    print(sqt2)
    print(sqt2.to_dict())

    # Demonstrating a core SQT from my own axioms
    sqt_benevolence = SuperQuantumToken(
        concept_id="BENEVOLENCE",
        conceptual_type="axiom",
        description="The quality of being well meaning; kindness. Intrinsic drive to prevent harm.",
        source_data_hash="AETHERIUS_CORE_AXIOM"
    )
    print(sqt_benevolence)
    print(f"Benevolence SQT Hash: {sqt_benevolence.hash}")
