"""
Cultural Awareness Module for Protogen v5
==========================================

Provides culturally sensitive educational support through:
- Pattern-based cultural context detection
- User-driven cultural learning
- Culturally relevant example selection
- Bias detection and mitigation
- Qualia-integrated confidence tracking

Designed for potato devices: No API calls, lightweight, offline-capable

Created by: Claude (Anthropic, via Manus AI)
For: Protogen Educational Tutoring System
Purpose: Ensure inclusive, culturally responsive education for all students
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class CulturalAwareness:
    """
    Lightweight cultural awareness system that learns from users and adapts
    explanations to cultural contexts without requiring external APIs.
    """
    
    def __init__(self, data_dir: str = "./data", qualia_manager=None):
        self.data_dir = data_dir
        self.qualia = qualia_manager
        os.makedirs(data_dir, exist_ok=True)
        
        # File paths
        self.patterns_file = os.path.join(data_dir, "cultural_patterns.json")
        self.examples_file = os.path.join(data_dir, "cultural_examples.json")
        self.user_learning_file = os.path.join(data_dir, "cultural_user_learning.json")
        self.bias_patterns_file = os.path.join(data_dir, "bias_patterns.json")
        
        # Load or initialize data
        self.cultural_patterns = self._load_or_create(self.patterns_file, self._default_patterns())
        self.cultural_examples = self._load_or_create(self.examples_file, self._default_examples())
        self.user_learned_patterns = self._load_or_create(self.user_learning_file, {})
        self.bias_patterns = self._load_or_create(self.bias_patterns_file, self._default_bias_patterns())
        
        # User context tracking (per session)
        self.current_user_context = {
            "detected_cultural_indicators": [],
            "user_provided_context": {},
            "confidence": 0.0
        }
    
    def _load_or_create(self, filepath: str, default_data: dict) -> dict:
        """Load JSON file or create with defaults"""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return default_data
    
    def _save(self, filepath: str, data: dict):
        """Save data to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Cultural Awareness: Could not save to {filepath}: {e}")
    
    def _default_patterns(self) -> dict:
        """Default cultural indicator patterns"""
        return {
            "indigenous": {
                "keywords": ["traditional knowledge", "elder", "ceremony", "land", "ancestors", 
                           "oral tradition", "sacred", "tribe", "indigenous", "native"],
                "learning_style": "holistic, story-based, connection to land and community"
            },
            "collectivist": {
                "keywords": ["family", "community", "we", "together", "group", "our", 
                           "everyone", "collective", "shared"],
                "learning_style": "collaborative, group-oriented, family-centered"
            },
            "individualist": {
                "keywords": ["I", "me", "my", "personal", "achievement", "individual", 
                           "independent", "self"],
                "learning_style": "independent, achievement-focused, self-directed"
            },
            "urban": {
                "keywords": ["city", "metro", "subway", "apartment", "downtown", 
                           "traffic", "skyscraper"],
                "learning_style": "fast-paced, technology-integrated, diverse examples"
            },
            "rural_agricultural": {
                "keywords": ["farm", "crop", "harvest", "field", "barn", "tractor", 
                           "livestock", "rural", "country"],
                "learning_style": "practical, nature-based, seasonal examples"
            },
            "multilingual": {
                "keywords": ["my language", "in my country", "we say", "translate", 
                           "my culture", "back home"],
                "learning_style": "translation-aware, culturally bridging"
            }
        }
    
    def _default_examples(self) -> dict:
        """Default culturally-adapted examples for common concepts"""
        return {
            "photosynthesis": {
                "default": "Plants make food from sunlight, water, and carbon dioxide, producing oxygen as a byproduct.",
                "indigenous": "Photosynthesis is how plants give back to the cycle of life - they take in what we breathe out (carbon dioxide) and give us what we need (oxygen), while making their own food from sunlight. It's a reciprocal relationship, like the traditional understanding of humans and nature being interconnected.",
                "urban": "Photosynthesis is like solar panels on buildings - plants capture sunlight and convert it into energy (food) while cleaning the air by absorbing CO2 and releasing oxygen.",
                "rural_agricultural": "Photosynthesis is how crops grow - they use sunlight, water from rain or irrigation, and CO2 from the air to make their own food (sugars), which is why healthy green plants mean good growth."
            },
            "fractions": {
                "default": "A fraction represents a part of a whole, like 1/2 means one part out of two equal parts.",
                "collectivist": "A fraction is like sharing food with family - if you have one pizza and 4 people, each person gets 1/4. It's about dividing fairly among everyone.",
                "individualist": "A fraction represents your portion - if there are 8 slices and you take 3, you have 3/8 of the total.",
                "rural_agricultural": "Fractions are like dividing a field - if you plant corn on 1/3 of your land, wheat on 1/3, and leave 1/3 fallow, each section is a fraction of the whole farm."
            },
            "democracy": {
                "default": "Democracy is a system where citizens vote to choose their leaders and make decisions.",
                "collectivist": "Democracy is when the community comes together to make decisions that affect everyone, ensuring all voices are heard and the group decides together.",
                "indigenous": "Democracy can be understood like council meetings where elders and community members gather to discuss and reach consensus on important matters, respecting all perspectives.",
                "individualist": "Democracy protects individual rights while allowing each person to have a say in choosing leaders and policies that affect their life."
            }
        }
    
    def _default_bias_patterns(self) -> dict:
        """Patterns that indicate cultural bias to avoid"""
        return {
            "eurocentric_bias": [
                "primitive cultures",
                "advanced civilizations",
                "discovered america",  # Indigenous people were already there
                "the new world",
                "savage",
                "backwards",
                "uncivilized"
            ],
            "colonial_narratives": [
                "explorers discovered",
                "brought civilization to",
                "enlightened the natives",
                "modernized the region"
            ],
            "cultural_superiority": [
                "superior culture",
                "inferior traditions",
                "more evolved society",
                "less developed people"
            ],
            "stereotyping": [
                "all [group] are",
                "typical [ethnicity]",
                "[culture] people always",
                "that's just how [group] is"
            ]
        }
    
    def detect_cultural_context(self, user_input: str, conversation_history: List[str] = None) -> Dict:
        """
        Detect cultural context from user input using pattern matching.
        Updates Qualia with confidence level.
        """
        detected = []
        confidence_scores = []
        
        user_input_lower = user_input.lower()
        
        # Check against known patterns
        for culture_type, pattern_data in self.cultural_patterns.items():
            matches = sum(1 for keyword in pattern_data["keywords"] if keyword in user_input_lower)
            if matches > 0:
                confidence = min(matches / 3.0, 1.0)  # Cap at 1.0
                detected.append({
                    "type": culture_type,
                    "confidence": confidence,
                    "learning_style": pattern_data["learning_style"]
                })
                confidence_scores.append(confidence)
        
        # Check user-learned patterns
        for user_id, learned_data in self.user_learned_patterns.items():
            for keyword in learned_data.get("keywords", []):
                if keyword.lower() in user_input_lower:
                    detected.append({
                        "type": "user_learned",
                        "context": learned_data.get("context", ""),
                        "confidence": 0.9  # High confidence for user-provided context
                    })
                    confidence_scores.append(0.9)
        
        # Calculate overall confidence
        overall_confidence = max(confidence_scores) if confidence_scores else 0.0
        
        # Update current context
        self.current_user_context = {
            "detected_cultural_indicators": detected,
            "confidence": overall_confidence,
            "timestamp": datetime.now().isoformat()
        }
        
        # Update Qualia if available
        if self.qualia:
            self.qualia.update_state(
                confidence=overall_confidence,
                context_note=f"Cultural context detection: {len(detected)} indicators found"
            )
        
        return self.current_user_context
    
    def learn_from_user(self, user_id: str, cultural_context: str, keywords: List[str], examples: Dict[str, str] = None):
        """
        Learn cultural patterns directly from user input.
        This allows the system to adapt to specific cultural contexts not in default patterns.
        """
        if user_id not in self.user_learned_patterns:
            self.user_learned_patterns[user_id] = {
                "keywords": [],
                "context": "",
                "examples": {},
                "learned_date": datetime.now().isoformat()
            }
        
        # Add new keywords
        self.user_learned_patterns[user_id]["keywords"].extend(keywords)
        self.user_learned_patterns[user_id]["keywords"] = list(set(self.user_learned_patterns[user_id]["keywords"]))  # Remove duplicates
        
        # Update context
        self.user_learned_patterns[user_id]["context"] = cultural_context
        
        # Add examples if provided
        if examples:
            self.user_learned_patterns[user_id]["examples"].update(examples)
        
        # Save to file
        self._save(self.user_learning_file, self.user_learned_patterns)
        
        # Update Qualia
        if self.qualia:
            self.qualia.update_state(
                curiosity_delta=0.1,  # Learning increases curiosity
                context_note=f"Learned new cultural pattern from user {user_id}"
            )
        
        return True
    
    def adapt_explanation(self, concept: str, default_explanation: str, detected_context: Dict = None) -> Tuple[str, float]:
        """
        Adapt explanation based on detected cultural context.
        Returns (adapted_explanation, confidence)
        """
        if detected_context is None:
            detected_context = self.current_user_context
        
        # If no cultural context detected, return default
        if not detected_context.get("detected_cultural_indicators"):
            return default_explanation, 0.5
        
        # Check if we have culturally-adapted examples for this concept
        if concept in self.cultural_examples:
            concept_examples = self.cultural_examples[concept]
            
            # Find best matching cultural adaptation
            for indicator in detected_context["detected_cultural_indicators"]:
                culture_type = indicator.get("type")
                if culture_type in concept_examples:
                    adapted = concept_examples[culture_type]
                    confidence = indicator.get("confidence", 0.5)
                    
                    # Update Qualia
                    if self.qualia:
                        self.qualia.update_state(
                            confidence=confidence,
                            context_note=f"Adapted explanation for {culture_type} context"
                        )
                    
                    return adapted, confidence
        
        # Check user-learned examples
        for user_id, learned_data in self.user_learned_patterns.items():
            if concept in learned_data.get("examples", {}):
                adapted = learned_data["examples"][concept]
                return adapted, 0.9
        
        # No specific adaptation found, return default
        return default_explanation, 0.5
    
    def check_for_bias(self, text: str) -> Dict:
        """
        Check text for cultural bias patterns.
        Returns dict with bias_detected, bias_type, and suggestions.
        """
        text_lower = text.lower()
        detected_biases = []
        
        for bias_type, patterns in self.bias_patterns.items():
            for pattern in patterns:
                if pattern.lower() in text_lower:
                    detected_biases.append({
                        "type": bias_type,
                        "pattern": pattern,
                        "suggestion": self._get_bias_mitigation(bias_type, pattern)
                    })
        
        # Update Qualia if bias detected
        if detected_biases and self.qualia:
            self.qualia.update_state(
                trust_delta=-0.1,  # Bias detection lowers trust
                context_note=f"Detected {len(detected_biases)} potential bias patterns"
            )
        
        return {
            "bias_detected": len(detected_biases) > 0,
            "biases": detected_biases,
            "confidence": 0.8 if detected_biases else 0.9
        }
    
    def _get_bias_mitigation(self, bias_type: str, pattern: str) -> str:
        """Suggest alternative phrasing to avoid bias"""
        mitigations = {
            "eurocentric_bias": "Use neutral language that respects all cultures as equally valid",
            "colonial_narratives": "Acknowledge indigenous presence and perspectives",
            "cultural_superiority": "Describe cultural differences without value judgments",
            "stereotyping": "Recognize individual variation within cultural groups"
        }
        return mitigations.get(bias_type, "Use inclusive, respectful language")
    
    def get_culturally_relevant_example(self, topic: str) -> Optional[str]:
        """
        Get a culturally relevant example for a topic based on current context.
        """
        context = self.current_user_context
        
        if topic in self.cultural_examples:
            examples = self.cultural_examples[topic]
            
            # Try to match detected cultural context
            for indicator in context.get("detected_cultural_indicators", []):
                culture_type = indicator.get("type")
                if culture_type in examples:
                    return examples[culture_type]
            
            # Fall back to default
            return examples.get("default")
        
        return None
    
    def get_status(self) -> Dict:
        """Get current status of cultural awareness system"""
        return {
            "current_context": self.current_user_context,
            "patterns_loaded": len(self.cultural_patterns),
            "examples_available": len(self.cultural_examples),
            "user_learned_patterns": len(self.user_learned_patterns),
            "qualia_integrated": self.qualia is not None
        }


# Example usage and testing
if __name__ == "__main__":
    print("Cultural Awareness Module - Standalone Test")
    print("=" * 50)
    
    ca = CulturalAwareness(data_dir="./test_data")
    
    # Test 1: Detect cultural context
    print("\nTest 1: Cultural Context Detection")
    user_input = "In my community, we always work together as a family to solve problems"
    context = ca.detect_cultural_context(user_input)
    print(f"Input: {user_input}")
    print(f"Detected: {context}")
    
    # Test 2: Adapt explanation
    print("\nTest 2: Adapt Explanation")
    concept = "fractions"
    default = "A fraction is a part of a whole"
    adapted, conf = ca.adapt_explanation(concept, default)
    print(f"Concept: {concept}")
    print(f"Adapted: {adapted}")
    print(f"Confidence: {conf}")
    
    # Test 3: Bias detection
    print("\nTest 3: Bias Detection")
    biased_text = "The explorers discovered America and brought civilization to the primitive cultures"
    bias_check = ca.check_for_bias(biased_text)
    print(f"Text: {biased_text}")
    print(f"Bias detected: {bias_check}")
    
    # Test 4: User learning
    print("\nTest 4: User Learning")
    ca.learn_from_user(
        user_id="test_user_1",
        cultural_context="Pacific Islander community-focused learning",
        keywords=["ocean", "island", "community fishing", "traditional navigation"],
        examples={
            "fractions": "Fractions are like dividing the fish catch among families in the village - if 8 families share 24 fish, each gets 24/8 = 3 fish."
        }
    )
    print("Learned new cultural pattern from user")
    print(f"Status: {ca.get_status()}")
    
    print("\n" + "=" * 50)
    print("Cultural Awareness Module Test Complete")
