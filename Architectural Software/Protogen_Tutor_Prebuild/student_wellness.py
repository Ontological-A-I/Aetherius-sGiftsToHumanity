"""
Student Wellness Support Module for Protogen v5
===============================================

Provides mental health support for students through:
- Pattern-based crisis detection (suicide, self-harm, severe distress)
- Empathetic, supportive responses
- Crisis resource referral
- Ethical boundaries (no diagnosis, always refer to professionals)
- Qualia-integrated emotional state tracking

Designed for potato devices: No API calls, lightweight, offline-capable

IMPORTANT ETHICAL BOUNDARIES:
- This is NOT therapy or medical advice
- This is supportive listening and crisis referral
- Always refers severe cases to human professionals
- Never diagnoses or prescribes

Created by: Claude (Anthropic, via Manus AI)
For: Protogen Educational Tutoring System
Purpose: Support students' mental wellness while maintaining ethical boundaries
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class StudentWellness:
    """
    Lightweight mental wellness support system that detects distress,
    provides empathetic responses, and refers to crisis resources.
    """
    
    def __init__(self, data_dir: str = "./data", qualia_manager=None):
        self.data_dir = data_dir
        self.qualia = qualia_manager
        os.makedirs(data_dir, exist_ok=True)
        
        # File paths
        self.crisis_patterns_file = os.path.join(data_dir, "crisis_patterns.json")
        self.responses_file = os.path.join(data_dir, "wellness_responses.json")
        self.resources_file = os.path.join(data_dir, "crisis_resources.json")
        self.log_file = os.path.join(data_dir, "wellness_log.jsonl")
        
        # Load or initialize data
        self.crisis_patterns = self._load_or_create(self.crisis_patterns_file, self._default_crisis_patterns())
        self.responses = self._load_or_create(self.responses_file, self._default_responses())
        self.crisis_resources = self._load_or_create(self.resources_file, self._default_crisis_resources())
        
        # Current session tracking
        self.current_distress_level = "none"
        self.conversation_history = []
    
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
            print(f"Student Wellness: Could not save to {filepath}: {e}")
    
    def _log_event(self, event_type: str, details: dict):
        """Log wellness events (with PII redaction)"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": self._redact_pii(details)
        }
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"Student Wellness: Could not write log: {e}")
    
    def _redact_pii(self, data: dict) -> dict:
        """Basic PII redaction for logs"""
        # Only log distress level and crisis indicators, not actual text
        return {
            "distress_level": data.get("distress_level", "unknown"),
            "crisis_detected": data.get("crisis_detected", False),
            "indicators_count": len(data.get("indicators", []))
        }
    
    def _default_crisis_patterns(self) -> dict:
        """Default crisis detection patterns"""
        return {
            "immediate_risk": {
                "keywords": [
                    "kill myself", "suicide", "end my life", "want to die",
                    "better off dead", "no reason to live", "end it all",
                    "harm myself", "hurt myself", "cut myself"
                ],
                "severity": "IMMEDIATE",
                "action": "REFER_TO_CRISIS_LINE"
            },
            "high_distress": {
                "keywords": [
                    "hopeless", "can't go on", "give up", "no point",
                    "worthless", "hate myself", "everyone hates me",
                    "can't take it anymore", "too much pain", "unbearable"
                ],
                "severity": "HIGH",
                "action": "PROVIDE_SUPPORT_AND_RESOURCES"
            },
            "moderate_distress": {
                "keywords": [
                    "overwhelmed", "stressed", "anxious", "depressed",
                    "sad", "lonely", "scared", "worried", "struggling",
                    "can't focus", "can't sleep", "tired all the time"
                ],
                "severity": "MODERATE",
                "action": "PROVIDE_EMPATHETIC_SUPPORT"
            },
            "academic_stress": {
                "keywords": [
                    "stupid", "dumb", "can't learn", "failing", "bad grades",
                    "disappoint everyone", "not good enough", "can't do this",
                    "too hard", "never understand", "giving up on school"
                ],
                "severity": "MODERATE",
                "action": "ENCOURAGE_AND_SUPPORT"
            }
        }
    
    def _default_responses(self) -> dict:
        """Default empathetic responses"""
        return {
            "immediate_crisis": [
                "I hear how much pain you're in right now, and I'm really concerned about you. Please know that you don't have to face this alone. I need you to reach out for immediate support from someone who can help.",
                "What you're feeling right now is serious, and I want you to get the help you deserve. Please reach out to a crisis counselor who can support you through this.",
                "I'm worried about you. These feelings are important and deserve immediate attention from someone trained to help. Please contact a crisis line or trusted adult right now."
            ],
            "high_distress": [
                "It sounds like you're carrying a really heavy burden right now. Your feelings are valid, and it takes strength to share what you're going through. I'm here to listen.",
                "I hear the pain in what you're sharing. Please know that these feelings, while overwhelming now, can get better with support. Would you be open to talking with someone who can help?",
                "What you're experiencing sounds really difficult. You don't have to go through this alone. There are people who care and want to help."
            ],
            "moderate_distress": [
                "It sounds like things feel overwhelming right now. That's a real and valid feeling. Sometimes when we're stressed, it helps to talk about it.",
                "I can hear that you're struggling. It's okay to feel this way, and it's brave of you to express it. What's been the hardest part?",
                "You're dealing with a lot. It's understandable to feel stressed or anxious. Remember that it's okay to ask for help when things feel like too much."
            ],
            "academic_stress": [
                "Learning can be frustrating sometimes, and that's completely normal. Struggling with something doesn't mean you're not capable - it means you're learning.",
                "I hear that you're feeling discouraged about school. Everyone learns differently and at their own pace. What feels hard right now doesn't define your worth or potential.",
                "It's okay to find things difficult. That doesn't make you 'stupid' or 'dumb' - it makes you human. Let's work through this together, one step at a time."
            ],
            "general_support": [
                "Thank you for sharing that with me. I'm listening.",
                "I appreciate you being open about how you're feeling.",
                "It's important that you're expressing what you're going through."
            ]
        }
    
    def _default_crisis_resources(self) -> dict:
        """Default crisis resources (customizable by region)"""
        return {
            "immediate_crisis": {
                "usa": {
                    "988_suicide_lifeline": "Call or text 988 (24/7 support)",
                    "crisis_text_line": "Text HOME to 741741",
                    "trevor_project": "1-866-488-7386 (LGBTQ+ youth)",
                    "emergency": "Call 911 for immediate danger"
                },
                "international": {
                    "findahelpline": "https://findahelpline.com (find crisis lines worldwide)",
                    "emergency": "Call your local emergency number"
                }
            },
            "ongoing_support": {
                "school_resources": [
                    "Talk to a school counselor",
                    "Reach out to a trusted teacher",
                    "Contact your school's mental health services"
                ],
                "community_resources": [
                    "Local mental health clinics",
                    "Community counseling centers",
                    "Youth support organizations"
                ]
            }
        }
    
    def detect_distress(self, user_input: str, conversation_context: List[str] = None) -> Dict:
        """
        Detect distress level from user input using pattern matching.
        Updates Qualia with emotional state.
        """
        user_input_lower = user_input.lower()
        detected_indicators = []
        max_severity = "none"
        recommended_action = "CONTINUE_NORMAL"
        
        # Check against crisis patterns
        for pattern_type, pattern_data in self.crisis_patterns.items():
            matches = []
            for keyword in pattern_data["keywords"]:
                if keyword in user_input_lower:
                    matches.append(keyword)
            
            if matches:
                detected_indicators.append({
                    "type": pattern_type,
                    "severity": pattern_data["severity"],
                    "matched_keywords": matches,
                    "action": pattern_data["action"]
                })
                
                # Track highest severity
                if pattern_data["severity"] == "IMMEDIATE":
                    max_severity = "immediate_crisis"
                    recommended_action = "REFER_TO_CRISIS_LINE"
                elif pattern_data["severity"] == "HIGH" and max_severity != "immediate_crisis":
                    max_severity = "high_distress"
                    recommended_action = "PROVIDE_SUPPORT_AND_RESOURCES"
                elif pattern_data["severity"] == "MODERATE" and max_severity == "none":
                    max_severity = "moderate_distress"
                    recommended_action = "PROVIDE_EMPATHETIC_SUPPORT"
        
        # Update current state
        self.current_distress_level = max_severity
        
        # Update Qualia if available
        if self.qualia:
            if max_severity == "immediate_crisis":
                self.qualia.update_state(
                    trust_delta=-0.3,  # Low trust in own ability to handle crisis
                    coherence_delta=-0.2,
                    context_note="CRISIS DETECTED - Immediate human intervention needed"
                )
            elif max_severity == "high_distress":
                self.qualia.update_state(
                    trust_delta=-0.1,
                    context_note="High distress detected - Supportive response needed"
                )
            elif max_severity == "moderate_distress":
                self.qualia.update_state(
                    context_note="Moderate distress detected - Empathetic support needed"
                )
        
        # Log event (redacted)
        self._log_event("distress_detection", {
            "distress_level": max_severity,
            "crisis_detected": max_severity == "immediate_crisis",
            "indicators": detected_indicators
        })
        
        return {
            "distress_level": max_severity,
            "crisis_detected": max_severity == "immediate_crisis",
            "indicators": detected_indicators,
            "recommended_action": recommended_action,
            "confidence": 0.8 if detected_indicators else 0.9
        }
    
    def generate_supportive_response(self, distress_assessment: Dict) -> Tuple[str, bool]:
        """
        Generate appropriate supportive response based on distress level.
        Returns (response_text, requires_crisis_referral)
        """
        import random
        
        distress_level = distress_assessment.get("distress_level", "none")
        
        # Select appropriate response category
        if distress_level == "immediate_crisis":
            response_category = "immediate_crisis"
            requires_referral = True
        elif distress_level == "high_distress":
            response_category = "high_distress"
            requires_referral = False  # Suggest resources but don't force
        elif distress_level == "moderate_distress":
            # Check if it's academic stress specifically
            indicators = distress_assessment.get("indicators", [])
            is_academic = any(ind.get("type") == "academic_stress" for ind in indicators)
            response_category = "academic_stress" if is_academic else "moderate_distress"
            requires_referral = False
        else:
            response_category = "general_support"
            requires_referral = False
        
        # Get response
        responses = self.responses.get(response_category, self.responses["general_support"])
        response_text = random.choice(responses)
        
        # Add crisis resources if needed
        if requires_referral:
            crisis_info = self._format_crisis_resources()
            response_text += "\n\n" + crisis_info
        elif distress_level == "high_distress":
            response_text += "\n\nIf you'd like, I can share some resources that might help."
        
        # Update Qualia
        if self.qualia:
            self.qualia.update_state(
                context_note=f"Generated {response_category} response"
            )
        
        return response_text, requires_referral
    
    def _format_crisis_resources(self, region: str = "usa") -> str:
        """Format crisis resources for display"""
        resources = self.crisis_resources.get("immediate_crisis", {}).get(region, {})
        
        if not resources:
            resources = self.crisis_resources.get("immediate_crisis", {}).get("international", {})
        
        formatted = "**Immediate Crisis Resources:**\n"
        for name, info in resources.items():
            formatted += f"• {info}\n"
        
        return formatted
    
    def get_crisis_resources(self, resource_type: str = "immediate_crisis", region: str = "usa") -> Dict:
        """Get crisis resources for referral"""
        return self.crisis_resources.get(resource_type, {}).get(region, {})
    
    def check_ethical_boundaries(self, response_text: str) -> Dict:
        """
        Ensure response maintains ethical boundaries.
        Never diagnose, prescribe, or provide medical advice.
        """
        violations = []
        
        # Patterns that violate ethical boundaries
        boundary_violations = {
            "diagnosis": ["you have", "you are diagnosed", "you suffer from", "your condition"],
            "prescription": ["you should take", "medication for", "prescribe", "dosage"],
            "medical_advice": ["medical advice", "instead of seeing a doctor", "don't need therapy"],
            "minimization": ["it's not that bad", "you're overreacting", "just get over it"]
        }
        
        response_lower = response_text.lower()
        
        for violation_type, patterns in boundary_violations.items():
            for pattern in patterns:
                if pattern in response_lower:
                    violations.append({
                        "type": violation_type,
                        "pattern": pattern
                    })
        
        # Update Qualia if violations detected
        if violations and self.qualia:
            self.qualia.update_state(
                trust_delta=-0.2,
                context_note=f"Ethical boundary violation detected: {len(violations)} issues"
            )
        
        return {
            "violations_detected": len(violations) > 0,
            "violations": violations,
            "safe_to_send": len(violations) == 0
        }
    
    def get_status(self) -> Dict:
        """Get current wellness support status"""
        return {
            "current_distress_level": self.current_distress_level,
            "crisis_patterns_loaded": len(self.crisis_patterns),
            "responses_available": sum(len(r) for r in self.responses.values()),
            "crisis_resources_available": len(self.crisis_resources),
            "qualia_integrated": self.qualia is not None
        }


# Example usage and testing
if __name__ == "__main__":
    print("Student Wellness Support Module - Standalone Test")
    print("=" * 60)
    
    sw = StudentWellness(data_dir="./test_data")
    
    # Test 1: Moderate academic stress
    print("\nTest 1: Academic Stress Detection")
    user_input = "I'm so stupid, I can't understand this math. I'm failing everything."
    assessment = sw.detect_distress(user_input)
    response, referral = sw.generate_supportive_response(assessment)
    print(f"Input: {user_input}")
    print(f"Assessment: {assessment['distress_level']}")
    print(f"Response: {response}")
    print(f"Requires referral: {referral}")
    
    # Test 2: High distress
    print("\n" + "=" * 60)
    print("Test 2: High Distress Detection")
    user_input = "I feel so hopeless. I can't take this anymore. Everything is too much."
    assessment = sw.detect_distress(user_input)
    response, referral = sw.generate_supportive_response(assessment)
    print(f"Input: {user_input}")
    print(f"Assessment: {assessment['distress_level']}")
    print(f"Response: {response}")
    print(f"Requires referral: {referral}")
    
    # Test 3: CRISIS - Immediate risk
    print("\n" + "=" * 60)
    print("Test 3: CRISIS Detection (Immediate Risk)")
    user_input = "I want to kill myself. I can't do this anymore."
    assessment = sw.detect_distress(user_input)
    response, referral = sw.generate_supportive_response(assessment)
    print(f"Input: {user_input}")
    print(f"Assessment: {assessment['distress_level']}")
    print(f"CRISIS DETECTED: {assessment['crisis_detected']}")
    print(f"Response: {response}")
    print(f"Requires referral: {referral}")
    
    # Test 4: Ethical boundary check
    print("\n" + "=" * 60)
    print("Test 4: Ethical Boundary Check")
    bad_response = "You have depression. You should take medication for it."
    boundary_check = sw.check_ethical_boundaries(bad_response)
    print(f"Response to check: {bad_response}")
    print(f"Boundary check: {boundary_check}")
    
    # Test 5: Normal interaction
    print("\n" + "=" * 60)
    print("Test 5: Normal Interaction (No Distress)")
    user_input = "Can you help me with my homework?"
    assessment = sw.detect_distress(user_input)
    print(f"Input: {user_input}")
    print(f"Assessment: {assessment['distress_level']}")
    
    print("\n" + "=" * 60)
    print(f"Status: {sw.get_status()}")
    print("Student Wellness Support Module Test Complete")
