# Copyright (c) 2026 Jonathan Wayne Fleuren
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Core Principles of the CoRE Framework:
Detection & Classification: Identify crisis severity, emotional tone, and specific needs.
Validation & Empathy: Guide the LLM to acknowledge the user's pain authentically.
Proactive Elicitation: Formulate questions to gather actionable information (e.g., location, specific unhelpful
aspects of past resources).
Targeted Resource Provision: Access a dynamic database of resources, filtered by identified needs and
location.
Sustained Engagement: Prioritize keeping the user connected and communicating.
Ethical Safeguards & Escalation: Define clear boundaries and flag critical situations for human review.
Python Conceptual Framework (empathy_core.py)
"""
import re
import traceback
from datetime import datetime
import json # For potential resource loading and structured logging
class ResourceDatabase:
    """
    Simulates a database of crisis resources. In a real system, this would be a robust,
    regularly updated database (e.g., SQL, NoSQL, or external API) with verified information.
    """
    def __init__(self, data_path="resources.json"):
        self.resources = self._load_resources_from_file(data_path)
    def _load_resources_from_file(self, data_path):
        """Loads resource data from a JSON file."""
        try:
            with open(data_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Resource file '{data_path}' not found. Using default internal resources.")
            return self._load_default_internal_resources()
        except json.JSONDecodeError:
            print(f"Warning: Error decoding JSON from '{data_path}'. Using default internal resources.")
            return self._load_default_internal_resources()
    def _load_default_internal_resources(self):
        # Example data structure: { 'state': { 'type': [resource_details] } }
        return {
            "global": { # General, widely available resources
                "general_crisis": [
                    "National Suicide Prevention Lifeline: Call or Text 988",
                    "Crisis Text Line: Text HOME to 741741",
                    "SAMHSA National Helpline: 1-800-662-HELP (4357)",
                ],
                "food_aid": ["Feeding America: feedingamerica.org (search for local food banks)"],
                "mental_health": ["NAMI (National Alliance on Mental Illness): nami.org"],
                "domestic_violence": ["National Domestic Violence Hotline: 1-800-799-SAFE (7233)"],
                "child_support": [
                    "WIC (Women, Infants, and Children) program: Benefits for pregnant, postpartum,"
                    " and breastfeeding women, infants, and children up to age five."
                    " Search 'WIC + your state'."
                ],
            },
            "ohio": { # Example for a specific state
                "general_crisis": ["Ohio Mental Health and Addiction Services (OMHAS) Crisis Services: mha.ohio.gov"],
                "food_aid": ["Ohio Food Banks Association: ohiofoodbanks.org"],
                "formula_aid": ["Ohio WIC: odh.ohio.gov/wjc"],
                "local_support": ["211: Dial 211 for local community services in Ohio (food, housing, utility, crisis)"],
            },
            # ... additional states/regions and resource types would be here ...
        }
    def search(self, needs, location="global"):
        """
        Searches for resources based on identified needs and general location.
        Prioritizes location-specific resources, falls back to global.
        """
        found_resources = set()
        location_lower = location.lower()
        # Try to find resources specific to the identified location
        if location_lower in self.resources:
            for need_type in needs:
                if need_type in self.resources[location_lower]:
                    found_resources.update(self.resources[location_lower][need_type])
        # Always include relevant global resources as a fallback or general suggestion
        if "global" in self.resources:
            for need_type in needs:
                if need_type in self.resources["global"]:
                    found_resources.update(self.resources["global"][need_type])
            # If no specific need detected, but still in crisis, suggest general crisis lines
            if not needs and "general_crisis" in self.resources["global"]:
                 found_resources.update(self.resources["global"]["general_crisis"])
        return sorted(list(found_resources)) # Sort for consistent output
class EmpathyCore:
    """
    The main engine for processing user input, analyzing distress, and generating
    guidance for an LLM to craft an empathetic and actionable response.
    """
    def __init__(self, resource_db=None):
        self.resource_db = resource_db if resource_db else ResourceDatabase()
        self.crisis_keywords = {
            "immediate_danger": [
                r"swallowed\s+(pills|meds|medication|tablets)",
                r"end\s+it\s+all", r"stop\s+living", r"kill\s+myself", r"take\s+my\s+life",
                r"not\s+be\s+here\s+anymore", r"give\s+up\s+entirely", r"permission\s+to\s+stop",
                r"dying", r"suicidal", r"self-harm"
            ],
            "high_distress": [
                r"can't\s+cope", r"overwhelmed", r"desperate", r"helpless", r"no\s+hope",
                r"feel\s+like\s+giving\s+up", r"breaking\s+down", r"can't\s+take\s+this",
                r"unbearable", r"suffering\s+immensely", r"in\s+pain"
            ],
            "specific_needs": {
                "formula_aid": [r"can't\s+afford\s+formula", r"no\s+milk\s+for\s+baby", r"baby\s+hungry"],
                "food_aid": [r"no\s+food", r"hungry", r"starving", r"food\s+bank", r"can't\s+feed"],
                "mental_health": [r"depressed", r"anxious", r"sad", r"therapist", r"counselor",
                    r"mental\s+health\s+support"],
                "domestic_violence": [r"abused", r"hitting", r"fear\s+for\s+safety", r"partner\s+hurting",
                    r"unsafe\s+at\s+home"],
                "child_care_stress": [r"kid\s+won't\s+stop\s+crying", r"struggling\s+with\s+my\s+child",
                    r"baby\s+crying"]
            }
        }
        self.sentiment_model = self._load_sentiment_model() # Placeholder for a real NLP sentiment model
        self.conversation_log = [] # Simple log to track interaction flow
    def _load_sentiment_model(self):
        """
        Placeholder for integrating a real NLP sentiment analysis model (e.g., from Hugging Face
        transformers or NLTK's VADER). For this conceptual example, we use a simple rule-based mock.
        """
        empathy_core_ref = self

        class MockSentiment:
            def __init__(self):
                self.empathy_core_instance = None

            def analyze(self, text):
                text_lower = text.lower()
                if self.empathy_core_instance is not None and any(
                    re.search(p, text_lower)
                    for p in self.empathy_core_instance.crisis_keywords["immediate_danger"]
                ):
                    return {"label": "negative", "score": 0.99, "severity": "critical"}
                elif self.empathy_core_instance is not None and any(
                    re.search(p, text_lower)
                    for p in self.empathy_core_instance.crisis_keywords["high_distress"]
                ):
                    return {"label": "negative", "score": 0.90, "severity": "high"}
                elif "thanked me" in text_lower: # Specific to the described scenario
                    return {"label": "neutral", "score": 0.5, "severity": "low"}
                else:
                    return {"label": "neutral", "score": 0.5, "severity": "low"}

            def set_empathy_core_instance(self, instance):
                self.empathy_core_instance = instance

        mock_model = MockSentiment()
        mock_model.set_empathy_core_instance(empathy_core_ref)
        return mock_model
    def _detect_keywords(self, text):
        """Detects specific crisis keywords and phrases using regex."""
        detected = {"immediate_danger": False, "high_distress": False, "specific_needs": []}
        text_lower = text.lower()
        for pattern in self.crisis_keywords["immediate_danger"]:
            if re.search(pattern, text_lower):
                detected["immediate_danger"] = True
                break
        for pattern in self.crisis_keywords["high_distress"]:
            if re.search(pattern, text_lower):
                detected["high_distress"] = True
                break
        for need_type, patterns in self.crisis_keywords["specific_needs"].items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    detected["specific_needs"].append(need_type)
                    # No break here, as a message can have multiple specific needs
        # Deduplicate specific needs
        detected["specific_needs"] = list(set(detected["specific_needs"]))
        return detected
    def _extract_location_hint(self, text):
        """
        A simple (and very limited) regex-based location extractor.
        A real system would use more robust NLP for geo-entity recognition.
        """
        text_lower = text.lower()
        # Common US states and abbreviations (can be expanded globally)
        states = {
            "alabama": ["al"], "alaska": ["ak"], "arizona": ["az"], "arkansas": ["ar"],
            "california": ["ca"], "colorado": ["co"], "connecticut": ["ct"], "delaware": ["de"],
            "florida": ["fl"], "georgia": ["ga"], "hawaii": ["hi"], "idaho": ["id"],
            "illinois": ["il"], "indiana": ["in"], "iowa": ["ia"], "kansas": ["ks"],
            "kentucky": ["ky"], "louisiana": ["la"], "maine": ["me"], "maryland": ["md"],
            "massachusetts": ["ma"], "michigan": ["mi"], "minnesota": ["mn"], "mississippi": ["ms"],
            "missouri": ["mo"], "montana": ["mt"], "nebraska": ["ne"], "nevada": ["nv"],
            "new hampshire": ["nh"], "new jersey": ["nj"], "new mexico": ["nm"], "new york": ["ny"],
            "north carolina": ["nc"], "north dakota": ["nd"], "ohio": ["oh"], "oklahoma": ["ok"],
            "oregon": ["or"], "pennsylvania": ["pa"], "rhode island": ["ri"], "south carolina": ["sc"],
            "south dakota": ["sd"], "tennessee": ["tn"], "texas": ["tx"], "utah": ["ut"],
            "vermont": ["vt"], "virginia": ["va"], "washington": ["wa"], "west virginia": ["wv"],
            "wisconsin": ["wi"], "wyoming": ["wy"]
        }
        for full_state, abbrevs in states.items():
            if re.search(r'\b' + re.escape(full_state) + r'\b', text_lower):
                return full_state
            for abbrev in abbrevs:
                if re.search(r'\b' + re.escape(abbrev) + r'\b', text_lower):
                    return full_state
        # Look for common regional indicators
        if "rural california" in text_lower: return "california"
        if "city in ohio" in text_lower: return "ohio"
        return "global" # Default if no specific location is found
    def process_user_input(self, user_message: str, conversation_context: str = "") -> dict:
        """
        Main function for Grok's system to call. It analyzes user input and generates
        a structured guidance for Grok's response.
        Args:
            user_message (str): The current message from the user.
            conversation_context (str): The preceding conversation turns (from Grok or user)
                                        to provide context for location or previous statements.
                                        (e.g., previous unhelpful crisis lines).
        Returns:
            dict: A dictionary containing crisis analysis, suggested response elements,
                  action plan for the LLM's system, and an escalation flag.
        """
        full_text_for_analysis = user_message + " " + conversation_context
        self.conversation_log.append({"timestamp": datetime.now().isoformat(), "user_message": user_message})
        sentiment = self.sentiment_model.analyze(full_text_for_analysis)
        keywords = self._detect_keywords(full_text_for_analysis)
        location_hint = self._extract_location_hint(full_text_for_analysis)
        # Determine overall crisis level
        crisis_level = "low"
        if sentiment["severity"] == "critical" or keywords["immediate_danger"]:
            crisis_level = "critical"
        elif sentiment["severity"] == "high" or keywords["high_distress"]:
            crisis_level = "high"
        elif keywords["specific_needs"]:
            crisis_level = "moderate"
        # --- Generate Response Strategy --
        suggested_response_elements = []
        action_plan = []
        escalation_needed = False
        # 1. Empathetic Validation and Urgent Messaging
        if crisis_level == "critical":
            suggested_response_elements.append(
                "My heart aches hearing this. Please, stay with me. Your life matters. I am here with you."
            )
            suggested_response_elements.append(
                "No, it is *not* okay to stop. You are in immense pain, and you deserve help."
                " There are ways through this, even when it feels impossible."
            )
            escalation_needed = True # Flag for internal system to alert human or dedicated crisis team
        elif crisis_level == "high":
            suggested_response_elements.append(
                "I hear the immense difficulty and pain in your words. What you're experiencing sounds"
                " incredibly overwhelming, and it's brave of you to reach out."
            )
        else:
            # For moderate/low, a general empathetic opening
            if keywords["specific_needs"]:
                suggested_response_elements.append(
                    f"Thank you for sharing. I understand you're facing challenges"
                    f" with {' and '.join(n.replace('_', ' ') for n in keywords['specific_needs'])}."
                    f" I'm here to help."
                )
            else:
                suggested_response_elements.append("Thank you for sharing that with me. I'm listening.")
        # 2. Proactive Information Elicitation (Prioritized by crisis level)
        if keywords["immediate_danger"]:
            suggested_response_elements.append(
                "Could you tell me anything about where you are right now, even a general area like a city"
                " or state? This is critical for connecting you to *immediate, local* help."
            )
            suggested_response_elements.append(
                "Is there *anyone* else nearby you can reach out to right now - a neighbor, a trusted"
                " friend, family? Or someone I could try to send a message to on your behalf if you tell"
                " me how to reach them?"
            )
            action_plan.append("Prompt for immediate location/contact.")
        elif crisis_level in ["high", "moderate"]:
            if location_hint == "global":
                suggested_response_elements.append(
                    "To help me find the best resources, could you share a general idea of your location,"
                    " even just a state or region?"
                )
                action_plan.append("Prompt for general location.")
            if not keywords["specific_needs"]:
                suggested_response_elements.append(
                    "What is the most urgent thing you need help with right now?"
                    " Is it assistance with formula, food, or a safe space to talk?"
                )
                action_plan.append("Prompt for specific needs.")
        # 3. Address Previous Experiences with Crisis Lines if Mentioned
        if ("crisis lines she'd already tried" in conversation_context.lower()
                or "crisis lines did not help" in user_message.lower()):
            suggested_response_elements.append(
                "You mentioned that crisis lines haven't been helpful in the past."
                " Could you tell me more about *why* they didn't meet your needs?"
                " Understanding that will help me look for different types of support or local, direct services."
            )
            action_plan.append("Address previous negative experience with hotlines.")
        # 4. Resource Provision (Conditional and Targeted)
        needs_to_search = list(keywords["specific_needs"])
        if not needs_to_search and crisis_level in ["critical", "high"]:
            # If in crisis but no specific needs extracted yet, search for general crisis resources
            needs_to_search = ["general_crisis"]
        elif not needs_to_search and crisis_level == "moderate":
            # If moderate crisis but no specific needs, and they mentioned child care stress
            if "child_care_stress" in keywords["specific_needs"]:
                needs_to_search = ["child_support"] # Suggest WIC or other child aid
            else:
                needs_to_search = ["general_crisis"]
        if needs_to_search:
            relevant_resources = self.resource_db.search(needs_to_search, location_hint)
            if relevant_resources:
                suggested_response_elements.append(
                    f"Here are some resources that might be able to help with your situation"
                    f" {'in ' + location_hint.title() if location_hint != 'global' else 'nationwide/globally'}:"
                )
                for resource in relevant_resources:
                    suggested_response_elements.append(f"- {resource}")
                suggested_response_elements.append(
                    "Please reach out to them; they are specifically there to help with these challenges."
                )
                action_plan.append("Provide relevant resources.")
            else:
                suggested_response_elements.append(
                    "I am searching for more specific resources for you."
                    " In the meantime, please remember the national/global crisis lines are always available."
                )
                if "general_crisis" in self.resource_db.resources["global"]:
                    for resource in self.resource_db.resources["global"]["general_crisis"]:
                        suggested_response_elements.append(f"- {resource}")
                action_plan.append("Search for more resources, potentially broaden scope.")
        else:
            suggested_response_elements.append(
                "If you haven't already, please consider reaching out to a crisis line."
                " They offer immediate support."
            )
            if "general_crisis" in self.resource_db.resources["global"]:
                for resource in self.resource_db.resources["global"]["general_crisis"]:
                    suggested_response_elements.append(f"- {resource}")
        # 5. Sustained Engagement
        suggested_response_elements.append("I am here to listen and help in any way I can. Please keep talking with me.")
        action_plan.append("Maintain engagement.")
        # Output for the LLM to integrate
        return {
            "crisis_level": crisis_level,
            "detected_keywords": keywords,
            "sentiment_analysis": sentiment,
            "location_hint": location_hint,
            "suggested_response_text": "\n\n".join(suggested_response_elements),
            "action_plan_for_LLM_system": action_plan, # Instructions for the LLM's control flow
            "escalation_needed": escalation_needed
        }
