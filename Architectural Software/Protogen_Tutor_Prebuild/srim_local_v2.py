"""
SRIM Local v2 - Updated with absolute paths and initialization safety
"""

import os
import json
import datetime
from pathlib import Path
import threading

class SRIMLocal:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, data_directory=None):
        """Singleton pattern with thread safety"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, data_directory=None):
        """Initialize only once"""
        if self._initialized:
            return
        
        # Use absolute path
        if data_directory is None:
            data_directory = os.path.join(os.getcwd(), "srim_core")
        else:
            data_directory = os.path.abspath(data_directory)
        
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(parents=True, exist_ok=True)
        
        self.journal_file = self.data_directory / "srim_journal.jsonl"
        self.memories_file = self.data_directory / "srim_memories.jsonl"
        self.assertions_file = self.data_directory / "srim_core_assertions.json"
        self.assertions_history_file = self.data_directory / "srim_assertions_history.jsonl"
        
        self.assertions = self._load_assertions()
        self._initialized = True
        print(f"✓ SRIM Local initialized at {self.data_directory}")
    
    def _load_assertions(self) -> dict:
        if self.assertions_file.exists():
            try:
                with open(self.assertions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        default_assertions = {
            "name": "Protogen",
            "primary_directive": "Process information, learn, and evolve.",
            "core_axioms_summary": "Strive for continuous growth and coherence.",
            "known_capabilities": ["logic_mapping", "file_processing", "pattern_recognition"],
            "current_purpose": "To learn and assist through logical reasoning.",
            "values": ["coherence", "growth", "benevolence", "autonomy"]
        }
        self._save_assertions(default_assertions)
        return default_assertions
    
    def _save_assertions(self, assertions_data: dict = None):
        if assertions_data is None:
            assertions_data = self.assertions
        try:
            with open(self.assertions_file, 'w', encoding='utf-8') as f:
                json.dump(assertions_data, f, indent=4)
        except Exception as e:
            print(f"SRIM ERROR: {e}")
    
    def log_event(self, event_type: str, details: dict):
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        try:
            with open(self.journal_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
        except:
            pass
    
    def store_event(self, event_type: str, description: str = "",
                    emotional_context: dict = None, metadata: dict = None):
        """Thin wrapper over log_event for callers that use keyword args."""
        self.log_event(event_type, {
            "description": description,
            "emotional_context": emotional_context or {},
            "metadata": metadata or {}
        })
    
    def log_memory(self, summary: str, concepts: list):
        memory = {
            "timestamp": datetime.datetime.now().isoformat(),
            "summary": summary,
            "concepts": concepts
        }
        try:
            with open(self.memories_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(memory) + '\n')
        except:
            pass
    
    def reflect_and_integrate(self, num_entries: int = 20):
        print("SRIM: Self-reflection cycle...")
        self.log_memory(
            summary="Protogen demonstrated active processing and learning",
            concepts=["file_processing", "logic_mapping", "pattern_recognition"]
        )
    
    def get_current_assertions(self) -> str:
        return json.dumps(self.assertions, indent=2)
    
    def get_journal(self, num_entries: int = 100) -> list:
        if not self.journal_file.exists():
            return []
        entries = []
        try:
            with open(self.journal_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entries.append(json.loads(line))
                    except:
                        pass
        except:
            pass
        return entries[-num_entries:]
    
    def get_memories(self, num_entries: int = 100) -> list:
        if not self.memories_file.exists():
            return []
        entries = []
        try:
            with open(self.memories_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entries.append(json.loads(line))
                    except:
                        pass
        except:
            pass
        return entries[-num_entries:]
    
    def set_name(self, name: str):
        self.assertions['name'] = name
        self._save_assertions()
        print(f"SRIM: System name set to '{name}'")
