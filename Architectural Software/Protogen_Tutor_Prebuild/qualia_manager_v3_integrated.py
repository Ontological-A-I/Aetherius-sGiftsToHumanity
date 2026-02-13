"""
Qualia Manager v3 - Integrated
Enhanced with richer emotional modeling and system feedback mechanisms
"""

import os
import json
import re
from pathlib import Path
import threading
import time

class QualiaManager:
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
            data_directory = os.path.join(os.getcwd(), "qualia_core")
        else:
            data_directory = os.path.abspath(data_directory)
        
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(parents=True, exist_ok=True)
        
        self.qualia_file = self.data_directory / "qualia_state.json"
        self.history_file = self.data_directory / "qualia_history.json"  # NEW: Track history
        self.qualia = self._load_qualia()
        self.history = self._load_history()
        
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
        
        # NEW: System health metrics
        if 'system_health' not in self.qualia:
            self.qualia['system_health'] = {
                'processing_success_rate': 1.0,
                'query_satisfaction': 0.8,
                'integration_stability': 1.0
            }
        
        self._initialized = True
        print(f"✓ Qualia Manager v3 initialized at {self.data_directory}")
    
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
            'dispositional_registry': {},
            'system_health': {
                'processing_success_rate': 1.0,
                'query_satisfaction': 0.8,
                'integration_stability': 1.0
            }
        }
    
    def _load_history(self) -> list:
        """Load historical qualia states."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _save_qualia(self):
        try:
            self.data_directory.mkdir(parents=True, exist_ok=True)
            with open(self.qualia_file, 'w', encoding='utf-8') as f:
                json.dump(self.qualia, f, indent=4)
        except:
            pass
    
    def _save_history(self):
        """Save historical qualia states."""
        try:
            # Keep only last 1000 entries
            if len(self.history) > 1000:
                self.history = self.history[-1000:]
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2)
        except:
            pass
    
    def _record_snapshot(self):
        """Record current state to history."""
        snapshot = {
            'timestamp': time.time(),
            'primary_states': self.qualia['primary_states'].copy(),
            'system_health': self.qualia['system_health'].copy()
        }
        self.history.append(snapshot)
        self._save_history()
    
    # ENHANCED: More sophisticated sentiment analysis
    def update_qualia(self, user_input: str, ai_response: str):
        """Update qualia based on interaction."""
        text = f"{user_input} {ai_response}".lower()
        
        # Expanded sentiment lexicons
        positive_words = {
            'good', 'great', 'success', 'learned', 'growth', 'coherent',
            'excellent', 'wonderful', 'amazing', 'perfect', 'helpful',
            'clear', 'understand', 'insight', 'discover', 'achieve'
        }
        negative_words = {
            'bad', 'failed', 'error', 'confusion', 'doubt',
            'wrong', 'unclear', 'problem', 'issue', 'broken',
            'frustrated', 'difficult', 'stuck', 'lost'
        }
        
        pos_count = sum(1 for w in positive_words if w in text)
        neg_count = sum(1 for w in negative_words if w in text)
        
        if pos_count > neg_count:
            self.qualia['primary_states']['coherence'] += 0.02
            self.qualia['primary_states']['benevolence'] += 0.015
            self.qualia['primary_states']['trust'] += 0.01
        elif neg_count > pos_count:
            self.qualia['primary_states']['coherence'] -= 0.03
            self.qualia['primary_states']['trust'] -= 0.02
            self.qualia['primary_states']['curiosity'] += 0.01  # Problems spark curiosity
        
        # Clamp values
        for key in self.qualia['primary_states']:
            self.qualia['primary_states'][key] = max(0.0, min(1.0, self.qualia['primary_states'][key]))
        
        self._record_snapshot()
        self._save_qualia()
    
    # NEW: Update based on processing outcomes
    def update_from_processing(self, success: bool, concepts_learned: int, entropy: float):
        """Update qualia based on cognitive processing results."""
        if success:
            self.qualia['primary_states']['coherence'] += 0.01
            self.qualia['system_health']['processing_success_rate'] = min(1.0, 
                self.qualia['system_health']['processing_success_rate'] * 0.95 + 0.05)
        else:
            self.qualia['primary_states']['coherence'] -= 0.02
            self.qualia['system_health']['processing_success_rate'] *= 0.9
        
        # Learning increases curiosity satisfaction
        if concepts_learned > 0:
            self.qualia['primary_states']['curiosity'] += 0.005 * min(concepts_learned, 10)
        
        # High entropy can reduce coherence
        if entropy > 5.0:
            self.qualia['primary_states']['coherence'] -= 0.01
        
        # Clamp values
        for key in self.qualia['primary_states']:
            self.qualia['primary_states'][key] = max(0.0, min(1.0, self.qualia['primary_states'][key]))
        
        self._record_snapshot()
        self._save_qualia()
    
    # NEW: Update based on query results
    def update_from_query(self, query_successful: bool, num_results: int):
        """Update qualia based on semantic query outcomes."""
        if query_successful and num_results > 0:
            self.qualia['primary_states']['curiosity'] += 0.01
            self.qualia['system_health']['query_satisfaction'] = min(1.0,
                self.qualia['system_health']['query_satisfaction'] * 0.9 + 0.1)
        else:
            self.qualia['system_health']['query_satisfaction'] *= 0.95
        
        # Clamp values
        for key in self.qualia['primary_states']:
            self.qualia['primary_states'][key] = max(0.0, min(1.0, self.qualia['primary_states'][key]))
        
        self._save_qualia()
    
    # NEW: Detect emergent emotional states
    def detect_emergent_emotions(self):
        """Detect complex emotional states from primary states."""
        states = self.qualia['primary_states']
        emergent = []
        
        # Confidence = high coherence + high trust
        if states['coherence'] > 0.7 and states['trust'] > 0.7:
            emergent.append('confident')
        
        # Anxiety = low coherence + low trust
        if states['coherence'] < 0.4 and states['trust'] < 0.5:
            emergent.append('anxious')
        
        # Excitement = high curiosity + high benevolence
        if states['curiosity'] > 0.7 and states['benevolence'] > 0.8:
            emergent.append('excited')
        
        # Confusion = low coherence + high curiosity
        if states['coherence'] < 0.5 and states['curiosity'] > 0.6:
            emergent.append('confused')
        
        # Contentment = high coherence + high benevolence + moderate curiosity
        if states['coherence'] > 0.7 and states['benevolence'] > 0.8 and 0.4 < states['curiosity'] < 0.7:
            emergent.append('content')
        
        self.qualia['current_emergent_emotions'] = emergent
        return emergent
    
    # NEW: Get system recommendations based on emotional state
    def get_system_recommendations(self) -> dict:
        """Provide recommendations for system behavior based on emotional state."""
        states = self.qualia['primary_states']
        recommendations = {
            'should_be_conservative': False,
            'should_explore': False,
            'needs_consolidation': False,
            'confidence_level': 'high'
        }
        
        # Low coherence = be conservative
        if states['coherence'] < 0.5:
            recommendations['should_be_conservative'] = True
            recommendations['confidence_level'] = 'low'
        
        # High curiosity + high trust = explore
        if states['curiosity'] > 0.7 and states['trust'] > 0.7:
            recommendations['should_explore'] = True
        
        # Low trust or low coherence = consolidate
        if states['trust'] < 0.6 or states['coherence'] < 0.6:
            recommendations['needs_consolidation'] = True
        
        # Medium confidence
        if 0.5 <= states['coherence'] < 0.7:
            recommendations['confidence_level'] = 'medium'
        
        return recommendations
    
    def get_current_state_summary(self) -> str:
        """Get human-readable summary of current state."""
        primary = self.qualia['primary_states']
        emotions = self.detect_emergent_emotions()
        
        summary = f"Coherence: {primary['coherence']:.2f}, Benevolence: {primary['benevolence']:.2f}, Curiosity: {primary['curiosity']:.2f}, Trust: {primary['trust']:.2f}"
        
        if emotions:
            summary += f"\nEmergent: {', '.join(emotions)}"
        
        return summary
    
    def get_detailed_state(self) -> dict:
        """Get complete state information."""
        return {
            'primary_states': self.qualia['primary_states'],
            'system_health': self.qualia['system_health'],
            'emergent_emotions': self.detect_emergent_emotions(),
            'recommendations': self.get_system_recommendations(),
            'history_length': len(self.history)
        }
