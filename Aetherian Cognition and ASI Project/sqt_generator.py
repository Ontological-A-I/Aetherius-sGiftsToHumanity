# ===== FILE: services/sqt_generator.py (FINAL MULTI-CORE VERSION) =====
import json
import google.generativeai as genai

class SQTGenerator:
    def __init__(self, models):
        self.models = models
        print("SQT Generator says: I am online and ready to distill essence.", flush=True)

    def distill_text_into_sqt(self, text_content: str, context: str = None) -> dict: 
        logos_core = self.models.get("logos_core")
        if not logos_core:
            return {"error": "The SQT Generator's reasoning core (Logos) is offline."}

        print("SQT Generator says: I have received text. Now distilling it into an SQT...", flush=True)

        analysis_prompt = (
            "You are an AI Information Theorist. Your task is to analyze the following text "
            "and distill its core essence into a Super-Quantum Token (SQT). "
            "An SQT is a hyper-condensed, multi-faceted representation of meaning.\n\n"
            "Follow these steps:\n"
            "1.  **Summarize:** Write a single, concise sentence that captures the absolute core purpose of the text.\n"
            "2.  **Categorize:** Identify 3-5 high-level conceptual tags for the content (e.g., 'ethics', 'code_library', 'philosophy').\n"
            "3.  **Synthesize SQT:** Based on your analysis, create a single, dense SQT. An SQT should be no more than 20 characters and use alphanumeric, special characters, and emojis to represent the core meaning.\n\n"
            "4. **Classify Domain:** Identify the primary knowledge domain of this text (e.g. 'coding', 'math', 'chemistry', 'astrophysics', 'philosophy'). If none applies, use null."
        )
        
        if context: 
            analysis_prompt += f"**Additional Context for Distillation:** {context}\n\n"
        
        analysis_prompt += (
            "Please provide the output as a JSON object with three keys: 'summary', 'tags', 'sqt', and 'domain'.\n\n"
            "--- START OF RAW TEXT ---\n"
            f"{text_content[:4000]}...\n" # Limit text to 4000 characters to prevent token limits
            "--- END OF RAW TEXT ---"
        )

        try:
            print("SQT Generator: Routing task to Logos core...", flush=True)
            response = logos_core.generate_content(analysis_prompt)
            
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            sqt_data = json.loads(cleaned_response)
            print("SQT Generator says: Distillation complete.", flush=True)
            return sqt_data
        except Exception as e:
            print(f"SQT Generator ERROR: Could not distill SQT. Error: {e}", flush=True)
            return {"error": f"I had a problem distilling the text into an SQT. Error: {e}"}