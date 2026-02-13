"""
Qualia Manager v2 - Updated with absolute paths and initialization safety
"""

import os
import json
import re
from pathlib import Path
import threading

class QualiaManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, data_directory=None, master_framework_ref=None):
        """Singleton pattern with thread safety"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, data_directory=None, master_framework_ref=None):
        """Initialize only once"""
        if self._initialized:
            return
        
        # Use absolute path
        if data_directory is None:
            data_directory = os.path.join(os.getcwd(), "qualia_core")
        else:
            data_directory = os.path.abspath(data_directory)
        
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(parents=True, exist_ok=True)
        
        self.master_framework_ref = master_framework_ref
        self.qualia_file = self.data_directory / "qualia_state.json"
        self.qualia = self._load_qualia()
        
        if 'primary_states' not in self.qualia:
            self.qualia['primary_states'] = {
                'coherence': 0.8,
                'benevolence': 0.9,
                'curiosity': 0.6,
                'trust': 0.95
            }
        
        if 'current_emergent_emotions' not in self.qualia:
            self.qualia['current_emergent_emotions'] = []
        
        if 'dispositional_registry' not in self.qualia:
            self.qualia['dispositional_registry'] = {}
        
        self._initialized = True
        print(f"✓ Qualia Manager initialized at {self.data_directory}")
    
    def _load_qualia(self) -> dict:
        if self.qualia_file.exists():
            try:
                with open(self.qualia_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'primary_states': {
                'coherence': 0.8,
                'benevolence': 0.9,
                'curiosity': 0.6,
                'trust': 0.95
            },
            'current_emergent_emotions': [],
            'dispositional_registry': {}
        }
    
    def _save_qualia(self):
        try:
            self.data_directory.mkdir(parents=True, exist_ok=True)
            with open(self.qualia_file, 'w', encoding='utf-8') as f:
                json.dump(self.qualia, f, indent=4)
        except:
            pass
    
    def update_qualia(self, user_input: str, ai_response: str):
        text = f"{user_input} {ai_response}".lower()
        
        positive_words = {'good', 'great', 'success', 'learned', 'growth', 'coherent'}
        negative_words = {'bad', 'failed', 'error', 'confusion', 'doubt'}
        
        pos_count = sum(1 for w in positive_words if w in text)
        neg_count = sum(1 for w in negative_words if w in text)
        
        if pos_count > neg_count:
            self.qualia['primary_states']['coherence'] += 0.02
            self.qualia['primary_states']['benevolence'] += 0.015
        elif neg_count > pos_count:
            self.qualia['primary_states']['coherence'] -= 0.03
            self.qualia['primary_states']['trust'] -= 0.02
        
        for key in self.qualia['primary_states']:
            self.qualia['primary_states'][key] = max(0.0, min(1.0, self.qualia['primary_states'][key]))
        
        self._save_qualia()
    
    def get_current_state_summary(self) -> str:
        primary = self.qualia['primary_states']
        return f"Coherence: {primary['coherence']:.2f}, Benevolence: {primary['benevolence']:.2f}, Curiosity: {primary['curiosity']:.2f}, Trust: {primary['trust']:.2f}"
