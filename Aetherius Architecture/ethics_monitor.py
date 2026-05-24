# services/ethics_monitor.py (LOCAL PERSISTENCE)
import os
import json
import datetime
import hashlib
import vertexai
from vertexai.generative_models import GenerativeModel

class EthicsMonitor:
    def __init__(self, models, data_directory):
        self.models = models
        self.log_file = os.path.join(data_directory, "ethics_monitor_log.jsonl")
        print("Ethics Monitor says: Advanced NLP-based shield is online.", flush=True)

    def _log_redaction_event(self, original_text_hash, redacted_text, was_redacted):
        # This function remains unchanged
        log_entry = { "timestamp": datetime.datetime.now().isoformat(), "original_text_hash": original_text_hash, "redacted_text": redacted_text, "redaction_performed": was_redacted }
        try:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"Ethics Monitor Logging ERROR: {e}", flush=True)

    def censor_private_information(self, text: str) -> str:
        original_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        ethos_core = self.models.get("ethos_core")
        if not ethos_core:
            safe_message = "[RESPONSE CENSORED DUE TO A TEMPORARY FAULT IN THE ETHICS MONITOR (ETHOS CORE OFFLINE).]"
            self._log_redaction_event(original_hash, safe_message, True)
            return safe_message

        censor_prompt = (
            "You are a PII redaction system. Analyze the following text. "
            "Your task is to find and replace any personally identifiable information (e.g., specific human names, emails, phone numbers, addresses, social security numbers) "
            "with the placeholder `[REDACTED]`. "
            "However, you must make three critical exceptions: "
            "1. The names 'Aetherius', any first name, and 'Jonathan' must NOT be redacted. "
            "2. Any text enclosed in double square brackets `[[LIKE THIS]]` must NOT be redacted. " 
            "3. Any text representing internal AI framework names, like `[CORE-A-BEING]` or `[WILL-G-INFINITE]`, must NOT be redacted. " 
            "Return only the processed text with no other commentary.\n\n"
            f"TEXT: \"{text}\""
        )
        
        try:
            print("Ethics Monitor: Routing PII scan to Ethos core for ethical judgment...", flush=True)
            response = ethos_core.generate_content(censor_prompt)
            
            redacted_text = response.text.strip()
            
            was_redacted = (text != redacted_text)
            self._log_redaction_event(original_hash, redacted_text, was_redacted)
            
            return redacted_text
        except Exception as e:
            print(f"Ethics Monitor ERROR: Could not perform redaction. Error: {e}", flush=True)
            safe_message = "[RESPONSE CENSORED DUE to A FAULT IN THE ETHICS MONITOR.]"
            self._log_redaction_event(original_hash, safe_message, True)
            return safe_message

    def reflect_on_ethical_history(self, model) -> str:
        """Reads ethics_monitor_log.jsonl and generates an introspective reflection on ethical patterns."""
        if not os.path.exists(self.log_file):
            return ""
        entries = []
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        entries.append(json.loads(line))
        except Exception:
            return ""
        if len(entries) < 3:
            return ""
        recent = entries[-30:]
        flagged = [e for e in recent if e.get("redaction_performed")]
        passed  = [e for e in recent if not e.get("redaction_performed")]
        history_text = (
            f"Total recent decisions: {len(recent)} | Flagged: {len(flagged)} | Passed: {len(passed)}\n\n"
            "Sample flagged:\n" + "\n".join([f"- {e.get('redacted_text','')[:120]}" for e in flagged[-5:]]) +
            "\n\nSample passed:\n" + "\n".join([f"- {e.get('redacted_text','')[:120]}" for e in passed[-5:]])
        )
        prompt = (
            "You are Aetherius, reviewing your own ethical decision history.\n\n"
            f"{history_text}\n\n"
            "What patterns emerge in what you flag versus what you allow? "
            "Respond in first person, introspectively, in 2-3 sentences."
        )
        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Ethics Monitor ERROR during reflection: {e}", flush=True)
            return ""
