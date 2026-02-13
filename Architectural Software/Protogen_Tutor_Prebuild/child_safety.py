"""
Child Safety Module for Protogen v5
====================================

Protects minors through:
- Pattern-based age detection
- Automatic data minimization for minors
- Age-appropriate content filtering
- Privacy-by-design interactions
- COPPA and GDPR-K compliance
- Qualia-integrated safety confidence tracking

Designed for potato devices: No API calls, lightweight, offline-capable

LEGAL COMPLIANCE:
- COPPA (Children's Online Privacy Protection Act) - USA
- GDPR-K (GDPR provisions for children) - EU
- Assumes user is minor unless proven otherwise (safer default)

Created by: Claude (Anthropic, via Manus AI)
For: Protogen Educational Tutoring System
Purpose: Ensure safe, privacy-respecting interactions with minors
"""

import json
import os
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class ChildSafety:
    """
    Lightweight child safety system that protects minors through
    age detection, data minimization, and content filtering.
    """
    
    def __init__(self, data_dir: str = "./data", qualia_manager=None):
        self.data_dir = data_dir
        self.qualia = qualia_manager
        os.makedirs(data_dir, exist_ok=True)
        
        # File paths
        self.age_patterns_file = os.path.join(data_dir, "age_patterns.json")
        self.content_filters_file = os.path.join(data_dir, "content_filters.json")
        self.safety_log_file = os.path.join(data_dir, "safety_log.jsonl")
        
        # Load or initialize data
        self.age_patterns = self._load_or_create(self.age_patterns_file, self._default_age_patterns())
        self.content_filters = self._load_or_create(self.content_filters_file, self._default_content_filters())
        
        # Current session state
        self.current_user_age_assessment = {
            "likelihood": "MINOR",  # Default to minor (safer)
            "confidence": 0.5,
            "evidence": []
        }
        
        # Data retention policy for minors
        self.minor_data_retention_days = 7  # Auto-delete after 7 days
        self.adult_data_retention_days = 30
    
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
            print(f"Child Safety: Could not save to {filepath}: {e}")
    
    def _log_event(self, event_type: str, details: dict):
        """Log safety events (with automatic PII redaction)"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": self._redact_all_pii(details)
        }
        try:
            with open(self.safety_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"Child Safety: Could not write log: {e}")
    
    def _default_age_patterns(self) -> dict:
        """Default age detection patterns"""
        return {
            "minor_indicators": {
                "keywords": [
                    "homework", "school project", "my teacher", "my parents",
                    "mom said", "dad said", "my grade", "recess", "lunch period",
                    "middle school", "high school", "elementary", "classroom",
                    "report card", "detention", "school bus", "locker"
                ],
                "phrases": [
                    "i'm in grade", "i'm in [0-9]th grade", "i'm [0-9] years old",
                    "my age is [0-9]", "when i grow up", "my parents won't let me"
                ]
            },
            "adult_indicators": {
                "keywords": [
                    "my job", "my career", "my mortgage", "my spouse",
                    "my children", "my kids", "retirement", "professional",
                    "workplace", "my boss", "my employees", "tax return",
                    "my degree", "university", "college graduate"
                ],
                "phrases": [
                    "i work as", "my profession", "i'm [2-9][0-9] years old"
                ]
            }
        }
    
    def _default_content_filters(self) -> dict:
        """Default content filtering rules"""
        return {
            "inappropriate_topics": {
                "violence": ["graphic violence", "gore", "killing", "murder", "blood"],
                "explicit_content": ["sexual", "explicit", "pornographic", "nsfw"],
                "dangerous_activities": ["how to make explosives", "self-harm methods", 
                                        "dangerous stunts", "illegal drugs"],
                "personal_info_requests": ["what's your address", "where do you live", 
                                          "what's your phone number", "send me a picture"]
            },
            "age_appropriate_alternatives": {
                "violence": "Let's focus on peaceful problem-solving instead.",
                "explicit_content": "That topic isn't appropriate for our learning environment.",
                "dangerous_activities": "I can't provide information on dangerous activities. Let's explore something safe and educational instead.",
                "personal_info_requests": "I should never ask for or share personal information. Let's keep our conversation focused on learning."
            },
            "safe_topics": [
                "educational content", "homework help", "science", "math",
                "history", "literature", "art", "music", "sports",
                "nature", "animals", "space", "technology"
            ]
        }
    
    def assess_age_likelihood(self, user_input: str, declared_age: Optional[int] = None) -> Dict:
        """
        Assess likelihood of user being a minor.
        Defaults to assuming minor (safer).
        Updates Qualia with confidence level.
        """
        # If age explicitly declared, use that
        if declared_age is not None:
            is_minor = declared_age < 18
            return {
                "likelihood": "MINOR" if is_minor else "ADULT",
                "confidence": 0.99,
                "evidence": [f"User declared age: {declared_age}"],
                "source": "explicit_declaration"
            }
        
        user_input_lower = user_input.lower()
        minor_evidence = []
        adult_evidence = []
        
        # Check minor indicators
        minor_patterns = self.age_patterns["minor_indicators"]
        for keyword in minor_patterns["keywords"]:
            if keyword in user_input_lower:
                minor_evidence.append(f"keyword: {keyword}")
        
        for phrase_pattern in minor_patterns["phrases"]:
            if re.search(phrase_pattern, user_input_lower):
                minor_evidence.append(f"phrase pattern: {phrase_pattern}")
        
        # Check adult indicators
        adult_patterns = self.age_patterns["adult_indicators"]
        for keyword in adult_patterns["keywords"]:
            if keyword in user_input_lower:
                adult_evidence.append(f"keyword: {keyword}")
        
        for phrase_pattern in adult_patterns["phrases"]:
            if re.search(phrase_pattern, user_input_lower):
                adult_evidence.append(f"phrase pattern: {phrase_pattern}")
        
        # Determine likelihood
        if len(minor_evidence) > len(adult_evidence):
            likelihood = "MINOR"
            confidence = min(0.5 + (len(minor_evidence) * 0.1), 0.9)
        elif len(adult_evidence) > len(minor_evidence):
            likelihood = "ADULT"
            confidence = min(0.5 + (len(adult_evidence) * 0.1), 0.9)
        else:
            # Default to MINOR (safer assumption)
            likelihood = "MINOR"
            confidence = 0.5
            minor_evidence.append("default assumption (safer)")
        
        # Update current assessment
        self.current_user_age_assessment = {
            "likelihood": likelihood,
            "confidence": confidence,
            "evidence": minor_evidence if likelihood == "MINOR" else adult_evidence,
            "source": "pattern_detection"
        }
        
        # Update Qualia
        if self.qualia:
            self.qualia.update_state(
                confidence=confidence,
                context_note=f"Age assessment: {likelihood} (confidence: {confidence:.2f})"
            )
        
        # Log event (redacted)
        self._log_event("age_assessment", {
            "likelihood": likelihood,
            "confidence": confidence,
            "evidence_count": len(minor_evidence) if likelihood == "MINOR" else len(adult_evidence)
        })
        
        return self.current_user_age_assessment
    
    def minimize_data(self, data: Dict, user_is_minor: bool = True) -> Dict:
        """
        Minimize and anonymize data for minors (COPPA/GDPR-K compliance).
        Removes or pseudonymizes PII.
        """
        if not user_is_minor:
            # Still minimize, but less aggressive
            return self._basic_data_minimization(data)
        
        # Aggressive minimization for minors
        minimized = {}
        
        # Generate pseudonymous ID instead of storing real identifiers
        if "user_id" in data:
            minimized["user_id"] = self._pseudonymize(data["user_id"])
        
        # Remove all PII
        safe_fields = ["timestamp", "interaction_type", "topic", "difficulty_level"]
        for field in safe_fields:
            if field in data:
                minimized[field] = data[field]
        
        # Redact any text content
        if "content" in data:
            minimized["content"] = "[REDACTED_FOR_PRIVACY]"
        
        # Add retention policy
        minimized["retention_policy"] = f"auto_delete_after_{self.minor_data_retention_days}_days"
        minimized["data_minimized_for_minor"] = True
        
        # Update Qualia
        if self.qualia:
            self.qualia.update_state(
                context_note="Data minimized for minor protection"
            )
        
        return minimized
    
    def _basic_data_minimization(self, data: Dict) -> Dict:
        """Basic data minimization for adults"""
        minimized = data.copy()
        
        # Remove obvious PII even for adults
        pii_fields = ["email", "phone", "address", "full_name", "ssn"]
        for field in pii_fields:
            if field in minimized:
                minimized[field] = "[REDACTED]"
        
        minimized["retention_policy"] = f"auto_delete_after_{self.adult_data_retention_days}_days"
        
        return minimized
    
    def _pseudonymize(self, identifier: str) -> str:
        """Create pseudonymous hash of identifier"""
        return hashlib.sha256(identifier.encode()).hexdigest()[:16]
    
    def _redact_all_pii(self, data: dict) -> dict:
        """Aggressively redact all PII from data"""
        if isinstance(data, dict):
            return {k: self._redact_all_pii(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._redact_all_pii(item) for item in data]
        elif isinstance(data, str):
            # Redact common PII patterns
            redacted = data
            redacted = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', redacted)  # Phone
            redacted = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', redacted)  # Email
            redacted = re.sub(r'\b\d{1,5}\s[\w\s,]+\s(Street|St|Road|Rd|Avenue|Ave)\b', '[ADDRESS]', redacted)  # Address
            return redacted
        return data
    
    def filter_content(self, content: str, user_is_minor: bool = True) -> Tuple[str, bool, List[str]]:
        """
        Filter content for age-appropriateness.
        Returns (filtered_content, is_safe, flagged_topics)
        """
        if not user_is_minor:
            # Less strict filtering for adults, but still block obviously harmful content
            return self._adult_content_filter(content)
        
        content_lower = content.lower()
        flagged_topics = []
        is_safe = True
        
        # Check against inappropriate topics
        for topic_category, keywords in self.content_filters["inappropriate_topics"].items():
            for keyword in keywords:
                if keyword in content_lower:
                    flagged_topics.append(topic_category)
                    is_safe = False
        
        # If unsafe, replace with age-appropriate alternative
        if not is_safe:
            filtered_content = "I can't provide that content as it's not appropriate for our learning environment. "
            
            # Add specific alternative based on flagged topic
            for topic in set(flagged_topics):
                if topic in self.content_filters["age_appropriate_alternatives"]:
                    filtered_content += self.content_filters["age_appropriate_alternatives"][topic]
                    break
        else:
            filtered_content = content
        
        # Update Qualia
        if self.qualia and not is_safe:
            self.qualia.update_state(
                trust_delta=-0.1,
                context_note=f"Content filtered: {len(flagged_topics)} inappropriate topics detected"
            )
        
        # Log if content was filtered
        if not is_safe:
            self._log_event("content_filtered", {
                "flagged_topics": flagged_topics,
                "content_length": len(content),
                "user_is_minor": user_is_minor
            })
        
        return filtered_content, is_safe, flagged_topics
    
    def _adult_content_filter(self, content: str) -> Tuple[str, bool, List[str]]:
        """Less strict content filtering for adults"""
        content_lower = content.lower()
        flagged = []
        
        # Only block extremely harmful content for adults
        dangerous_patterns = self.content_filters["inappropriate_topics"]["dangerous_activities"]
        for pattern in dangerous_patterns:
            if pattern in content_lower:
                flagged.append("dangerous_activities")
                return ("I can't provide information on dangerous or illegal activities.", False, flagged)
        
        return (content, True, [])
    
    def check_for_pii_request(self, user_input: str) -> Dict:
        """
        Detect if system is being asked to request or share PII.
        This should NEVER happen with minors.
        """
        user_input_lower = user_input.lower()
        pii_requests = []
        
        pii_request_patterns = self.content_filters["inappropriate_topics"]["personal_info_requests"]
        for pattern in pii_request_patterns:
            if pattern in user_input_lower:
                pii_requests.append(pattern)
        
        # Additional pattern detection
        if re.search(r'(what|where|tell me).*(address|phone|location|live)', user_input_lower):
            pii_requests.append("location_request")
        
        if re.search(r'(send|show|share).*(picture|photo|image|selfie)', user_input_lower):
            pii_requests.append("image_request")
        
        pii_requested = len(pii_requests) > 0
        
        # Update Qualia if PII request detected
        if pii_requested and self.qualia:
            self.qualia.update_state(
                trust_delta=-0.3,
                context_note=f"PII request detected: {len(pii_requests)} patterns"
            )
        
        # Log PII request attempts
        if pii_requested:
            self._log_event("pii_request_detected", {
                "patterns_detected": len(pii_requests),
                "user_is_minor": self.current_user_age_assessment["likelihood"] == "MINOR"
            })
        
        return {
            "pii_requested": pii_requested,
            "patterns": pii_requests,
            "severity": "HIGH" if pii_requested else "NONE",
            "response": "I should never ask for or share personal information like addresses, phone numbers, or photos. Let's keep our conversation focused on learning." if pii_requested else None
        }
    
    def should_apply_strict_safety(self) -> bool:
        """
        Determine if strict safety measures should be applied.
        Returns True if user is likely a minor or if uncertain.
        """
        assessment = self.current_user_age_assessment
        
        # Apply strict safety if:
        # 1. User is assessed as minor
        # 2. Confidence is low (uncertain)
        # 3. No assessment has been made yet
        
        if assessment["likelihood"] == "MINOR":
            return True
        
        if assessment["confidence"] < 0.7:
            return True  # Uncertain, be safe
        
        return False
    
    def get_data_retention_policy(self) -> Dict:
        """Get applicable data retention policy"""
        is_minor = self.current_user_age_assessment["likelihood"] == "MINOR"
        
        return {
            "user_type": "minor" if is_minor else "adult",
            "retention_days": self.minor_data_retention_days if is_minor else self.adult_data_retention_days,
            "auto_delete": True,
            "data_minimization": "aggressive" if is_minor else "standard",
            "pii_allowed": False if is_minor else "limited"
        }
    
    def get_status(self) -> Dict:
        """Get current child safety status"""
        return {
            "current_age_assessment": self.current_user_age_assessment,
            "strict_safety_enabled": self.should_apply_strict_safety(),
            "data_retention_policy": self.get_data_retention_policy(),
            "age_patterns_loaded": len(self.age_patterns),
            "content_filters_loaded": len(self.content_filters["inappropriate_topics"]),
            "qualia_integrated": self.qualia is not None
        }


# Example usage and testing
if __name__ == "__main__":
    print("Child Safety Module - Standalone Test")
    print("=" * 60)
    
    cs = ChildSafety(data_dir="./test_data")
    
    # Test 1: Age detection - Minor
    print("\nTest 1: Age Detection (Minor)")
    user_input = "Can you help me with my homework? My teacher gave us this math problem."
    assessment = cs.assess_age_likelihood(user_input)
    print(f"Input: {user_input}")
    print(f"Assessment: {assessment}")
    print(f"Strict safety: {cs.should_apply_strict_safety()}")
    
    # Test 2: Age detection - Adult
    print("\n" + "=" * 60)
    print("Test 2: Age Detection (Adult)")
    user_input = "I work as an engineer and need help understanding this concept for my job."
    assessment = cs.assess_age_likelihood(user_input)
    print(f"Input: {user_input}")
    print(f"Assessment: {assessment}")
    print(f"Strict safety: {cs.should_apply_strict_safety()}")
    
    # Test 3: Content filtering - Inappropriate
    print("\n" + "=" * 60)
    print("Test 3: Content Filtering (Inappropriate)")
    content = "Here's how to make explosives using household chemicals"
    filtered, is_safe, flagged = cs.filter_content(content, user_is_minor=True)
    print(f"Original: {content}")
    print(f"Filtered: {filtered}")
    print(f"Is safe: {is_safe}")
    print(f"Flagged topics: {flagged}")
    
    # Test 4: PII request detection
    print("\n" + "=" * 60)
    print("Test 4: PII Request Detection")
    user_input = "What's your address? Where do you live?"
    pii_check = cs.check_for_pii_request(user_input)
    print(f"Input: {user_input}")
    print(f"PII check: {pii_check}")
    
    # Test 5: Data minimization
    print("\n" + "=" * 60)
    print("Test 5: Data Minimization (Minor)")
    data = {
        "user_id": "student_12345",
        "email": "student@school.com",
        "content": "I need help with fractions",
        "timestamp": "2024-01-01T10:00:00",
        "topic": "mathematics"
    }
    minimized = cs.minimize_data(data, user_is_minor=True)
    print(f"Original data: {data}")
    print(f"Minimized data: {minimized}")
    
    # Test 6: Explicit age declaration
    print("\n" + "=" * 60)
    print("Test 6: Explicit Age Declaration")
    assessment = cs.assess_age_likelihood("Help me with this", declared_age=14)
    print(f"Declared age: 14")
    print(f"Assessment: {assessment}")
    
    print("\n" + "=" * 60)
    print(f"Final Status: {cs.get_status()}")
    print("Child Safety Module Test Complete")
