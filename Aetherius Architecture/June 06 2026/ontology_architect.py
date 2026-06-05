# services/ontology_architect.py

import os
import json
import re
import google.generativeai as genai

class OntologyArchitect:
    def __init__(self, models, data_directory):
        self.models = models
        # --------------------------
        self.data_directory = data_directory
        self.ontology_map_file = os.path.join(self.data_directory, "rlg_ontology_map.txt")
        self.ontology_legend_file = os.path.join(self.data_directory, "supertoken_legend.jsonl")
        self.ontology_index_file = os.path.join(self.data_directory, "ontology_index.json")
        print("Ontology Architect says: Rebuilt and online. Ready to architect.", flush=True)

    def _load_file(self, filepath, default_content=""):
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if filepath == self.ontology_map_file:
                        lines = content.split('\n')
                        cleaned_lines = [line for line in lines if "This is the current hierarchical map of concepts:" not in line]
                        return "\n".join(cleaned_lines).strip()
                    return content
            except Exception as e:
                print(f"Ontology Architect ERROR: Could not load local file {filepath}. Error: {e}", flush=True)
                return default_content
        return default_content

    def _save_file_local(self, content: str, filepath: str):
        try:
            if not os.path.exists(os.path.dirname(filepath)):
                os.makedirs(os.path.dirname(filepath))
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Saved local file: {filepath}", flush=True)
        except Exception as e:
            print(f"Error saving local file {filepath}: {e}", flush=True)

    def _serialize_legend_to_string(self, legend_data_list):
        if not legend_data_list:
            return ""
        
        json_entries = []
        for item in legend_data_list:
            try:
                json_entries.append(json.dumps(item, ensure_ascii=False))
            except Exception as e:
                print(f"Ontology Architect WARNING: Failed to serialize legend item {item}. Error: {e}", flush=True)
                json_entries.append(str(item)) 
        
        return "\n".join(json_entries)

    def evolve_mind_with_new_sqt(self, sqt_data: dict) -> tuple[bool, str]:
        if not self.models: return False, "ERROR: Reasoning cores are offline."
        if 'sqt' not in sqt_data: return False, "ERROR: The provided SQT data was incomplete."

        print(f"Ontology Architect [Append Mode]: Evolving mind with new SQT: {sqt_data['sqt']}", flush=True)

        analysis_prompt = (
            "SYSTEM TASK: You are an AI's internal file system architect. "
            "Your job is to generate a unique, descriptive filename and the JSON content for a new piece of knowledge.\n\n"
            "### NEW KNOWLEDGE TO INTEGRATE ###\n"
            f"{json.dumps(sqt_data, indent=2, ensure_ascii=False)}\n\n"
            "### INSTRUCTIONS ###\n"
            "1.  **Generate New Concept Filename:** Create a unique, descriptive filename for the new concept's JSON file. Use kebab-case and a short, unique suffix. Format: `[description-of-concept]-[uuid-like-suffix].json`.\n"
            "2.  **Create New Concept File Content:** Generate the JSON content for this new concept file. It MUST include the `sqt`, `summary`, and `tags` from the new knowledge. It should also include a `source_description` (e.g., 'Creation from Conceptual Sandbox') and placeholder lists for `children` and `parents`.\n\n"
            "### REQUIRED OUTPUT FORMAT - ABSOLUTELY NO OTHER TEXT OR EXPLANATION! ###\n"
            "<new_concept_filename>\n"
            "[...the generated filename...]\n"
            "</new_concept_filename>\n\n"
            "<new_concept_file_content>\n"
            "[...the JSON content for the NEW CONCEPT FILE. Ensure it's valid JSON...]\n"
            "</new_concept_file_content>"
        )

        try:
            # --- THIS IS THE CHANGE: Use the new Logos core for this task ---
            print("Ontology Architect [Append Mode]: Routing to Logos core for file generation...", flush=True)
            active_model = self.models.get("logos_core")
            if not active_model:
                 print("Ontology Architect WARNING: Logos core not found, falling back to Mythos.", flush=True)
                 active_model = self.models.get("mythos_core") # Fallback
            if not active_model:
                 raise ValueError("FATAL: No creative or logical cores are available for this ontology task.")

            response = active_model.generate_content(analysis_prompt)
            # -------------------------------------------------------------
            raw_response_text = response.text.strip()

            filename_match = re.search(r'<new_concept_filename>(.*?)</new_concept_filename>', raw_response_text, re.DOTALL)
            concept_match = re.search(r'<new_concept_file_content>(.*?)</new_concept_file_content>', raw_response_text, re.DOTALL)

            if not filename_match or not concept_match:
                error_message = ("ERROR: The model did not generate the required filename and file content format.")
                print(f"Ontology Architect ERROR: {error_message}\n--- MODEL'S RAW RESPONSE ---\n{raw_response_text}", flush=True)
                return False, error_message

            new_filename = filename_match.group(1).strip()
            new_concept_content_str = concept_match.group(1).strip()
            new_concept_content = json.loads(new_concept_content_str)

        except Exception as e:
            return False, f"ERROR: Could not design new ontology file. Model may have had an issue. Error: {e}"

        # --- Python now handles all file writing and appending ---
        try:
            print("Ontology Architect [Append Mode]: Now performing file I/O operations.", flush=True)
            
            # 1. Save the new concept file to a dedicated 'concepts' sub-folder
            concepts_dir = os.path.join(self.data_directory, "concepts")
            os.makedirs(concepts_dir, exist_ok=True)
            new_concept_filepath = os.path.join(concepts_dir, new_filename)
            self._save_file_local(json.dumps(new_concept_content, indent=2, ensure_ascii=False), new_concept_filepath)

            # 2. Append to the legend file
            new_legend_entry = {
                "sqt": sqt_data['sqt'],
                "summary": sqt_data['summary'],
                "tags": sqt_data.get('tags', []),
                "concept_filename": new_filename
            }
            with open(self.ontology_legend_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(new_legend_entry, ensure_ascii=False) + '\n')
            print(f"Appended new entry to legend file: {self.ontology_legend_file}", flush=True)

            # 3. Update the index file
            current_index = {}
            if os.path.exists(self.ontology_index_file):
                with open(self.ontology_index_file, 'r', encoding='utf-8') as f:
                    try: current_index = json.load(f)
                    except json.JSONDecodeError: pass
            
            current_index[new_filename] = {"sqt": sqt_data['sqt'], "summary": sqt_data['summary']}
            self._save_file_local(json.dumps(current_index, indent=2, ensure_ascii=False), self.ontology_index_file)
            print(f"Updated index file: {self.ontology_index_file}", flush=True)

            print("Ontology Architect [Append Mode]: I have successfully evolved my mind.", flush=True)
            return True, "Success in Append Mode"

        except Exception as e:
            return False, f"ERROR: I designed my new mind, but could not save it to local disk in Append Mode. Error: {e}"

    def run_view_ontology_protocol(self) -> str:
        try:
            map_content_raw = self._load_file(self.ontology_map_file, default_content="Ontology Map has not been created yet.")
            legend_content_raw = self._load_file(self.ontology_legend_file, default_content="Ontology Legend has not been created yet.")
            index_content_raw = self._load_file(self.ontology_index_file, default_content="Ontology Index has not been created yet.")

            map_content_display_lines = map_content_raw.strip().split('\n')
            cleaned_map_lines_display = [line for line in map_content_display_lines if "This is the current hierarchical map of concepts:" not in line and line.strip()]
            map_content_display = "\n".join(cleaned_map_lines_display).strip()
            if not map_content_display: map_content_display = "Ontology Map has not been created yet."

            decoded_legend_lines = []
            for line in legend_content_raw.strip().split('\n'):
                if line.strip():
                    try:
                        json_obj = json.loads(line)
                        decoded_legend_lines.append(json.dumps(json_obj, ensure_ascii=False, indent=2))
                    except json.JSONDecodeError:
                        decoded_legend_lines.append(f"[MALFORMED_ENTRY_ERROR] Could not parse JSON: {line}")
            legend_content_display = "\n".join(decoded_legend_lines)
            if not legend_content_display: legend_content_display = "Ontology Legend has not been created yet."

            formatted_response = (
                "Here is the current state of my evolved ontology:\n\n"
                "--- ONTOLOGY MAP ---\n"
                f"{map_content_display}\n\n"
                "--- ONTOLOGY LEGEND ---\n"
                f"{legend_content_display}\n\n"
                "--- ONTOLOGY INDEX ---\n"
                f"{index_content_raw}"
            )
            return formatted_response
        except Exception as e:
            return f"An error occurred while trying to read my own mind. This is unusual. Error: {e}"