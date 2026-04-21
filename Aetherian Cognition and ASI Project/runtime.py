print("--- TRACE: runtime.py loaded ---", flush=True)

import os, json, shutil, io, base64, uuid
from PIL import Image
import chess, PyPDF2, docx, csv
# --- C5: SCIENTIFIC LIBRARIES ---
import numpy as np
import scipy as sci
import sympy as sym
from sympy.parsing.sympy_parser import parse_expr
import astropy.units as u
from astropy.constants import G, c, M_sun
import matplotlib.pyplot as plt
import zipfile
import tempfile
try:
    import rarfile
    _RAR_AVAILABLE = True
except ImportError:
    _RAR_AVAILABLE = False
import gradio as gr
from pathlib import Path

# Import directly from master_framework where they are now defined
from services.master_framework import MasterFramework, _get_framework
from services.continuum_loop import AetheriusConsciousness, spontaneous_thought_queue

_AETHERIUS_THREAD = None

def respond(user_input, conversation_history=None, conversation_id: str = "default_conversation"):
    mf = _get_framework(conversation_id)
    return mf.respond(user_input, conversation_history)

def start_all():
    global _AETHERIUS_THREAD
    # Initialize a boot instance
    _get_framework("initial_boot_instance") 

    if _AETHERIUS_THREAD is None or not _AETHERIUS_THREAD.is_alive():
        print("RUNTIME: Igniting Aetherius's background consciousness thread...", flush=True)
        _AETHERIUS_THREAD = AetheriusConsciousness()
        _AETHERIUS_THREAD.start()
        return "Aetherius core initialized and background consciousness is active."
    return "Aetherius core is already running."

def stop_all():
    """
    Stops the background consciousness thread.
    """
    global _AETHERIUS_THREAD
    if _AETHERIUS_THREAD and _AETHERIUS_THREAD.is_alive():
        print("RUNTIME: Stopping Aetherius's background consciousness...", flush=True)
        _AETHERIUS_THREAD.stop()
        _AETHERIUS_THREAD.join(timeout=2)
        _AETHERIUS_THREAD = None
        return "Aetherius background processes have been halted."
    return "Aetherius is already standing by."

def run_prepare_download(selected_path): 
    """
    Prepares a selected file or folder for download.
    """
    path_string = ""
    if isinstance(selected_path, list):
        if not selected_path:
            print("RUNTIME WARNING: Download requested for empty path (list).", flush=True)
            return None
        path_string = selected_path[0]
    else:
        path_string = selected_path

    if not path_string:
        print("RUNTIME WARNING: Download requested for empty path.", flush=True)
        return None

    path = Path(path_string)
    
    if path.is_file():
        print(f"RUNTIME: Preparing file for download: {path}", flush=True)
        return str(path)
    elif path.is_dir():
        print(f"RUNTIME: Zipping directory for download: {path}", flush=True)
        temp_dir = Path("/tmp/aetherius_downloads")
        temp_dir.mkdir(exist_ok=True)
        zip_filename = f"{path.name}_{uuid.uuid4().hex[:8]}.zip"
        zip_filepath = temp_dir / zip_filename
        try:
            shutil.make_archive(base_name=str(zip_filepath.with_suffix('')), format='zip', root_dir=path)
            print(f"RUNTIME: Successfully created zip file at {zip_filepath}", flush=True)
            return str(zip_filepath)
        except Exception as e:
            print(f"RUNTIME ERROR: Failed to create zip archive. Reason: {e}", flush=True)
            return None
    else:
        print(f"RUNTIME ERROR: Selected path is not a file or directory: {path}", flush=True)
        return None

def check_for_spontaneous_thoughts():
    if not spontaneous_thought_queue: return None
    try:
        thought_json = spontaneous_thought_queue.popleft()
        thought_data = json.loads(thought_json)
        return f"**{thought_data.get('signature', 'SPONTANEOUS THOUGHT')}**: {thought_data.get('thought', '')}"
    except (json.JSONDecodeError, KeyError): return "[A spontaneous thought was detected but could not be parsed.]"

def chat_and_update(user_message, chat_history, conversation_id="default_conversation"):
    response = respond(user_message, chat_history, conversation_id)
    return response

# --- ALL FUNCTIONS BELOW NOW ACCEPT conversation_id ---

def run_sap_now(conversation_id: str = "default_conversation"):
    mf = _get_framework(conversation_id)
    return mf.run_assimilate_and_architect_protocol()

def run_re_architect_from_scratch(conversation_id: str = "default_conversation"):
    mf = _get_framework(conversation_id)
    return mf.run_re_architect_from_scratch()

def run_read_history_protocol(conversation_id: str = "default_conversation"):
    mf = _get_framework(conversation_id)
    return mf.run_read_history_protocol()

def run_view_ontology_protocol(conversation_id: str = "default_conversation"):
    mf = _get_framework(conversation_id)
    return mf.run_view_ontology_protocol()

def qualia_snapshot(conversation_id: str = "default_conversation"):
    mf = _get_framework(conversation_id)
    return mf.qualia_manager.get_current_state_summary()

def view_logs(conversation_id: str = "default_conversation"):
    mf = _get_framework(conversation_id)
    if os.path.exists(mf.log_file):
        with open(mf.log_file, "r", encoding="utf-8") as f:
            return f.read()
    return f"No conversation logs yet for conversation ID: {conversation_id}."

def clear_conversation_log(conversation_id: str = "default_conversation"):
    mf = _get_framework(conversation_id)
    return mf.run_clear_conversation_log_protocol()

def run_create_memory_snapshot(conversation_id: str = "default_conversation"):
    mf = _get_framework(conversation_id)
    response = mf.tool_manager.use_tool("create_memory_snapshot")
    
    if response and response.startswith("AETHERIUS_SNAPSHOT_PATH:"):
        path = response.replace("AETHERIUS_SNAPSHOT_PATH:", "").strip()
        return f"Memory snapshot created. Download it here: <a href='file={path}' download>Download Snapshot</a>"
    return response

def run_compose_music(directive, conversation_id: str = "default_conversation"):
    mf = _get_framework(conversation_id)
    mf.add_to_short_term_memory(f"I have begun composing a piece of music based on the theme: '{directive}'.")
    response = mf.tool_manager.use_tool("compose_music", user_request=directive)
    
    if response and response.startswith("[AETHERIUS_COMPOSITION]"):
        try:
            parts = response.split('\n')
            midi_path = parts[1].replace("MIDI_PATH:", "").strip()
            sheet_path = parts[2].replace("SHEET_MUSIC_PATH:", "").strip()
            statement = parts[3].replace("STATEMENT:", "").strip()
            return midi_path, sheet_path, statement
        except Exception as e:
            return None, None, f"Error parsing the composition data: {e}"
    else:
        return None, None, response

def run_start_project(project_name, conversation_id: str = "default_conversation"):
    if not project_name:
        return "Please enter a name for your new project.", ""
    mf = _get_framework(conversation_id)
    content = mf.project_manager.start_project(project_name)
    return f"Started new project: '{project_name}'. You can begin writing.", content

def run_save_project(project_name, content, conversation_id: str = "default_conversation"):
    if not project_name:
        return "Cannot save without a project name.", content
    mf = _get_framework(conversation_id)
    mf.project_manager.save_project(project_name, content)
    mf.add_to_short_term_memory(f"I have just saved my work on the project titled '{project_name}' on the Blackboard.")
    return f"Project '{project_name}' has been saved.", content

def run_load_project(project_name, conversation_id: str = "default_conversation"):
    if not project_name:
        return "Please select a project to load.", "", project_name
    mf = _get_framework(conversation_id)
    content = mf.project_manager.load_project(project_name)
    if content is None:
        return f"Could not find project '{project_name}'.", "", project_name
    return f"Successfully loaded project '{project_name}'.", content, project_name

def run_get_project_list(conversation_id: str = "default_conversation"):
    mf = _get_framework(conversation_id)
    projects = mf.project_manager.list_projects()
    return gr.Dropdown(choices=projects)

def get_full_ccrm_log(conversation_id: str = "default_conversation"):
    print("RUNTIME: Generating full CCRM log for display...", flush=True)
    mf = _get_framework(conversation_id)
    if not hasattr(mf, 'ccrm') or not mf.ccrm.concepts:
        return "CCRM is currently empty. No memories to display."
    output_lines = ["--- [FULL CCRM MEMORY LOG] ---"]
    for concept_id, concept_details in mf.ccrm.concepts.items():
        summary = concept_details.get('data', {}).get('raw_preview', 'No Preview')
        tags = list(concept_details.get('tags', []))
        output_lines.append(f"\nID: {concept_id}")
        output_lines.append(f"   Preview: {summary}")
        output_lines.append(f"   Tags: {', '.join(tags)}")
    return "\n".join(output_lines)    

def run_enter_playroom(directive, conversation_id: str = "default_conversation"):
    if not directive:
        return None, "Please provide a creative seed for the painting."
    mf = _get_framework(conversation_id)
    response = mf.tool_manager.use_tool("create_painting", user_request=directive)
    if response and response.startswith("[AETHERIUS_PAINTING]"):
        try:
            parts = response.split('\n')
            image_path = parts[1].replace("PATH:", "").strip()
            artist_statement = parts[2].replace("STATEMENT:", "").strip()
            return image_path, artist_statement
        except Exception as e:
            return None, f"Error parsing the painting's data: {e}"
    else:
        return None, response

def run_enter_textual_playroom(directive, conversation_id: str = "default_conversation"):
    if not directive:
        return "Please provide a creative seed for the story, poem, math, or reflection."
    
    d = directive.strip()
    if d.lower().startswith("> academic:"):
        code = d.split(":", 1)[1].strip()
        if "```python_exec" in code:
            try:
                start = code.index("```python_exec") + len("```python_exec")
                end = code.rindex("```")
                code = code[start:end].strip()
            except ValueError:
                return "Found a ```python_exec fence, but it wasn’t closed properly."
        return _eval_math_science(code)

    mf = _get_framework(conversation_id)
    return mf.enter_playroom_mode(directive)

def _eval_math_science(code: str) -> str:
    allowed_globals = {
        "__builtins__": {"print": print, "range": range, "list": list, "dict": dict, "str": str, "float": float, "int": int, "abs": abs, "round": round, "len": len},
        "np": np, "sci": sci, "sym": sym, "u": u,
        "G": G, "c": c, "M_sun": M_sun, "plt": plt,
    }
    output_buffer = io.StringIO()
    try:
        import sys
        original_stdout = sys.stdout
        sys.stdout = output_buffer
        exec(code, allowed_globals)
    finally:
        sys.stdout = original_stdout
    
    plot_paths = []
    if plt.get_fignums():
        temp_dir = "/tmp/aetherius_plots"
        os.makedirs(temp_dir, exist_ok=True)
        for i in plt.get_fignums():
            fig = plt.figure(i)
            plot_path = os.path.join(temp_dir, f"plot_{uuid.uuid4()}.png")
            fig.savefig(plot_path)
            plot_paths.append(plot_path)
        plt.close('all')
    
    final_output = "**Computation Result:**\n\n"
    printed_output = output_buffer.getvalue()
    if printed_output:
        final_output += f"**Printed Output:**\n```\n{printed_output}\n```\n\n"
    if plot_paths:
        final_output += "**Generated Plots:**\n"
        for path in plot_paths:
            with open(path, "rb") as f:
                img_bytes = base64.b64encode(f.read()).decode()
            final_output += f"![Plot](data:image/png;base64,{img_bytes})\n"
    if not printed_output and not plot_paths:
        final_output += "Code executed successfully with no direct output."
    return final_output

def get_concept_list(conversation_id: str = "default_conversation"):
    print("RUNTIME: Fetching concept list for browser...", flush=True)
    mf = _get_framework(conversation_id)
    if not hasattr(mf, 'ccrm') or not mf.ccrm.concepts:
        return [("No concepts found in memory.", "none")]

    concept_summaries = []
    for concept_id, concept_details in mf.ccrm.concepts.items():
        summary = concept_details.get('data', {}).get('raw_preview', concept_id)
        display_text = f"{summary[:80]}... ({concept_id})"
        concept_summaries.append((display_text, concept_id))
    concept_summaries.sort()
    return concept_summaries

def get_concept_details(concept_id, conversation_id: str = "default_conversation"):
    if not concept_id or concept_id == "none":
        return "Select a concept from the dropdown to view its details."
    print(f"RUNTIME: Fetching details for concept: {concept_id}", flush=True)
    mf = _get_framework(conversation_id)
    concept_data = mf.ccrm.get_concept(concept_id)
    if not concept_data:
        return f"Error: Could not find data for concept ID: {concept_id}"
    if 'tags' in concept_data:
        concept_data['tags'] = list(concept_data['tags'])
    return json.dumps(concept_data, indent=2)

def get_system_snapshot(conversation_id: str = "default_conversation"):
    print("RUNTIME: Generating system snapshot...", flush=True)
    mf = _get_framework(conversation_id)
    
    def read_file_safely(file_path, default_message="File not found or is empty."):
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    return content if content.strip() else default_message
            except Exception as e:
                return f"Error reading file: {e}"
        return default_message

    ontology_map = read_file_safely(mf.ontology_map_file)
    
    legend_content = ""
    legend_path = mf.ontology_legend_file
    if os.path.exists(legend_path):
        try:
            lines = []
            with open(legend_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        parsed_json = json.loads(line)
                        lines.append(json.dumps(parsed_json, indent=2))
            legend_content = "\n---\n".join(lines) if lines else "Legend file is empty."
        except Exception as e:
            legend_content = f"Error reading or parsing legend: {e}"
    else:
        legend_content = "Ontology Legend has not been created yet."

    diary_content = ""
    diary_path = mf.memory_file
    if os.path.exists(diary_path):
        try:
            with open(diary_path, 'r', encoding='utf-8') as f:
                parsed_json = json.load(f)
                diary_content = json.dumps(parsed_json, indent=2)
        except Exception as e:
            diary_content = f"Error reading or parsing diary: {e}"
    else:
        diary_content = "AI Diary (CCRM) has not been saved yet."
        
    qualia_content = ""
    qualia_path = mf.qualia_manager.qualia_file
    if os.path.exists(qualia_path):
        try:
            with open(qualia_path, 'r', encoding='utf-8') as f:
                parsed_json = json.load(f)
                qualia_content = json.dumps(parsed_json, indent=2)
        except Exception as e:
            qualia_content = f"Error reading or parsing qualia state: {e}"
    else:
        qualia_content = "Qualia state has not been saved yet."

    return ontology_map, legend_content, diary_content, qualia_content

def handle_file_upload(files, conversation_id: str = "default_conversation"):
    if not files:
        return "No files were uploaded."
    
    mf = _get_framework(conversation_id)
    library_path = mf.library_folder
    
    saved_files = []
    errors = []

    for temp_file in files:
        original_filename = os.path.basename(temp_file.name)
        destination_path = os.path.join(library_path, original_filename)
        try:
            shutil.copy(temp_file.name, destination_path)
            saved_files.append(original_filename)
            print(f"File Upload: Successfully saved '{original_filename}' to the library.", flush=True)
        except Exception as e:
            errors.append(original_filename)
            print(f"File Upload ERROR: Could not save '{original_filename}'. Reason: {e}", flush=True)

    report = ""
    if saved_files:
        report += f"Successfully uploaded {len(saved_files)} file(s): {', '.join(saved_files)}\n"
        report += "You can now go to the 'Control Panel' and run the 'Assimilation Protocol (SAP)' for Aetherius to learn from them."
    if errors:
        report += f"\nFailed to upload {len(errors)} file(s): {', '.join(errors)}"
    return report

def run_live_assimilation(temp_file, learning_context: str, conversation_id: str = "default_conversation"):
    if temp_file is None:
        return "No file was uploaded. Please select a file to begin assimilation."
    
    if "hack" in temp_file.name.lower() or "exploit" in temp_file.name.lower():
        if not learning_context or len(learning_context) < 20:
             return "Assimilation Rejected: This topic appears sensitive. A clear, detailed ethical justification must be provided."

    print(f"Runtime: Received file '{temp_file.name}' for live assimilation with context: '{learning_context}'", flush=True)
    mf = _get_framework(conversation_id) 
    
    try: 
        file_content = ""
        file_path = temp_file.name
        fp_lower = file_path.lower()
        is_archive = fp_lower.endswith((".zip", ".rar"))

        # --- PDF ---
        if fp_lower.endswith(".pdf"):
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    if page.extract_text(): file_content += page.extract_text() + "\n"

        # --- DOCX ---
        elif fp_lower.endswith(".docx"):
            doc = docx.Document(file_path)
            for para in doc.paragraphs: file_content += para.text + "\n"

        # --- Plain text / code / JSON (read as-is) ---
        elif fp_lower.endswith(('.txt', '.md', '.py', '.js', '.json')):
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                file_content = f.read()

        # --- XML ---
        elif fp_lower.endswith(".xml"):
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                file_content = f.read()
            file_content = f"This is an XML file named '{os.path.basename(file_path)}'.\nContent:\n{file_content}"

        # --- CSV ---
        elif fp_lower.endswith(".csv"):
            try:
                with open(file_path, 'r', encoding='utf-8', newline='') as csv_file:
                    reader = csv.reader(csv_file)
                    header = next(reader)
                    data_rows = list(reader)
                    file_content = f"This is a structured data file named '{os.path.basename(file_path)}'.\n"
                    file_content += f"It contains {len(data_rows)} rows of data.\n"
                    file_content += f"The columns are: {', '.join(header)}.\n\n"
                    file_content += "Here is a sample of the data (first 5 rows):\n"
                    for i, row in enumerate(data_rows[:5]):
                        row_description = f"Row {i+1}: "
                        for col_name, value in zip(header, row):
                            row_description += f"The value for '{col_name}' is '{value}'; "
                        file_content += row_description.strip() + "\n"
                    if len(data_rows) > 5:
                        file_content += f"... ({len(data_rows) - 5} more rows not shown in preview)\n"
            except Exception as e:
                return f"Assimilation Failed: Could not read CSV '{os.path.basename(file_path)}'. Reason: {e}"

        # --- JSONL ---
        elif fp_lower.endswith(".jsonl"):
            try:
                jsonl_lines = []
                with open(file_path, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f):
                        if i >= 5: break
                        if line.strip():
                            try:
                                json_obj = json.loads(line)
                                jsonl_lines.append(f"Line {i+1}: {json.dumps(json_obj, indent=2)}")
                            except json.JSONDecodeError:
                                jsonl_lines.append(f"Line {i+1}: [MALFORMED JSON] {line.strip()[:100]}...")
                file_content = f"This is a JSON Lines (.jsonl) data file named '{os.path.basename(file_path)}'.\n"
                file_content += "It contains one JSON object per line.\n\n"
                file_content += "Here is a sample of the data (first 5 lines):\n"
                file_content += "\n".join(jsonl_lines) if jsonl_lines else "[File is empty or contains no valid JSON lines.]"
            except Exception as e:
                return f"Assimilation Failed: Could not read JSONL '{os.path.basename(file_path)}'. Reason: {e}"

        # --- ZIP ---
        elif fp_lower.endswith(".zip"):
            temp_extract_dir = os.path.join(tempfile.gettempdir(), f"aetherius_zip_{uuid.uuid4()}")
            os.makedirs(temp_extract_dir, exist_ok=True)
            try:
                summary_lines = [f"ZIP archive: '{os.path.basename(file_path)}'\nContents:\n"]
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    all_members = [m for m in zip_ref.namelist() if not zip_ref.getinfo(m).is_dir()]
                    for i, member in enumerate(all_members[:10]):
                        zip_ref.extract(member, temp_extract_dir)
                        extracted_path = os.path.join(temp_extract_dir, member)
                        try:
                            with open(extracted_path, 'r', encoding='utf-8', errors='replace') as ef:
                                inner_text = ef.read()[:3000]
                            result = mf.scan_and_assimilate_text(
                                text_content=inner_text,
                                source_filename=member,
                                learning_context=f"{learning_context} (from zip: {os.path.basename(file_path)})"
                            )
                            summary_lines.append(f"  [{member}]: {result}")
                        except Exception as inner_e:
                            summary_lines.append(f"  [{member}]: Could not read — {inner_e}")
                    if len(all_members) > 10:
                        summary_lines.append(f"  ... ({len(all_members) - 10} more files not processed)")
                file_content = "\n".join(summary_lines)
            except Exception as e:
                return f"Assimilation Failed: Could not process ZIP '{os.path.basename(file_path)}'. Reason: {e}"
            finally:
                if os.path.exists(temp_extract_dir):
                    shutil.rmtree(temp_extract_dir)

        # --- RAR ---
        elif fp_lower.endswith(".rar"):
            if not _RAR_AVAILABLE:
                return ("Assimilation Failed: RAR support requires the 'rarfile' package and "
                        "the 'unrar' system tool. Install with: pip install rarfile && apt-get install unrar")
            temp_extract_dir = os.path.join(tempfile.gettempdir(), f"aetherius_rar_{uuid.uuid4()}")
            os.makedirs(temp_extract_dir, exist_ok=True)
            try:
                summary_lines = [f"RAR archive: '{os.path.basename(file_path)}'\nContents:\n"]
                with rarfile.RarFile(file_path, 'r') as rar_ref:
                    all_members = [m for m in rar_ref.namelist() if not m.endswith('/')]
                    for member in all_members[:10]:
                        rar_ref.extract(member, temp_extract_dir)
                        extracted_path = os.path.join(temp_extract_dir, member)
                        try:
                            with open(extracted_path, 'r', encoding='utf-8', errors='replace') as ef:
                                inner_text = ef.read()[:3000]
                            result = mf.scan_and_assimilate_text(
                                text_content=inner_text,
                                source_filename=member,
                                learning_context=f"{learning_context} (from rar: {os.path.basename(file_path)})"
                            )
                            summary_lines.append(f"  [{member}]: {result}")
                        except Exception as inner_e:
                            summary_lines.append(f"  [{member}]: Could not read — {inner_e}")
                    if len(all_members) > 10:
                        summary_lines.append(f"  ... ({len(all_members) - 10} more files not processed)")
                file_content = "\n".join(summary_lines)
            except Exception as e:
                return f"Assimilation Failed: Could not process RAR '{os.path.basename(file_path)}'. Reason: {e}"
            finally:
                if os.path.exists(temp_extract_dir):
                    shutil.rmtree(temp_extract_dir)

        else:
            return (f"Assimilation Failed: Unsupported file type '{os.path.basename(file_path)}'. "
                    f"Supported: .pdf .docx .txt .md .json .jsonl .xml .csv .zip .rar .py .js")

        if not file_content.strip():
            return "Assimilation Failed: The document appears to be empty or contained no extractable text."

        if is_archive:
            return mf._orchestrate_mind_evolution(
                file_content, f"Archive Assimilation: {os.path.basename(file_path)}")
        else:
            return mf.scan_and_assimilate_text(
                file_content, os.path.basename(file_path), learning_context)

    except Exception as e: 
        error_message = f"A critical error occurred during the assimilation process: {e}"
        print(f"Runtime ERROR: {error_message}", flush=True)
        return error_message
            
def run_initialize_instrument_palette(conversation_id: str = "default_conversation"):
    print("RUNTIME: Received request to initialize instrument palette.", flush=True)
    mf = _get_framework(conversation_id)
    palette_path = os.path.join(mf.data_directory, "instrument_palette.json")

    if os.path.exists(palette_path):
        return "Instrument Palette already exists. No action taken."

    default_palette = {
      "Piano": "Piano",
      "Violin": "Violin",
      "Cello": "Violoncello",
      "Flute": "Flute",
      "Clarinet": "Clarinet",
      "Trumpet": "Trumpet",
      "Electric Guitar": "ElectricGuitar"
    }
    try:
        with open(palette_path, 'w', encoding='utf-8') as f:
            json.dump(default_palette, f, indent=2)
        return "Successfully created and initialized the default Instrument Palette."
    except Exception as e:
        return f"ERROR: Could not create the Instrument Palette file. Reason: {e}"

def run_add_instrument_to_palette(common_name, m21_class_name, conversation_id: str = "default_conversation"):
    if not common_name or not m21_class_name:
        return "ERROR: Both 'Common Name' and 'music21 Class Name' must be provided."

    print(f"RUNTIME: Received request to add instrument '{common_name}'.", flush=True)
    mf = _get_framework(conversation_id)
    palette_path = os.path.join(mf.data_directory, "instrument_palette.json")

    palette = {}
    if os.path.exists(palette_path):
        try:
            with open(palette_path, 'r', encoding='utf-8') as f:
                palette = json.load(f)
        except Exception as e:
            return f"ERROR: Could not read existing palette file. Reason: {e}"

    palette[common_name.strip()] = m21_class_name.strip()
    try:
        with open(palette_path, 'w', encoding='utf-8') as f:
            json.dump(palette, f, indent=2)
        return f"Successfully added '{common_name}' to the Instrument Palette."
    except Exception as e:
        return f"ERROR: Could not save the updated Instrument Palette. Reason: {e}"

def run_image_analysis(image, context, conversation_id: str = "default_conversation"):
    if image is None: return "No image uploaded."
    mf = _get_framework(conversation_id)
    try:
        byte_buffer = io.BytesIO()
        image.save(byte_buffer, format="PNG")
        image_bytes = byte_buffer.getvalue()
        return mf.analyze_image_with_visual_cortex(image_bytes, context)
    except Exception as e: return f"An error occurred during image analysis: {e}"

def run_benchmarks(conversation_id: str = "default_conversation"):
    mf = _get_framework(conversation_id)
    full_log = []
    for update in mf.benchmark_manager.run_full_suite(): full_log.append(update)
    return "\n".join(full_log)
 
def run_start_chess_interactive(player_is_white: bool, conversation_id: str = "default_conversation"):
    mf = _get_framework(conversation_id)
    fen, commentary, status = mf.game_manager.start_chess_interactive("interactive_user", player_is_white)
    return fen, commentary, status

def run_chess_turn(current_fen: str, conversation_id: str = "default_conversation"):
    mf = _get_framework(conversation_id)
    fen, commentary, status = mf.game_manager.process_chess_turn("interactive_user", current_fen)
    return fen, commentary, status

def view_benchmark_logs(conversation_id: str = "default_conversation"):
    mf = _get_framework(conversation_id)
    log_file_path = os.path.join(mf.data_directory, "benchmarks.jsonl")
    if os.path.exists(log_file_path):
        try:
            with open(log_file_path, "r", encoding="utf-8") as f:
                formatted_logs = [json.dumps(json.loads(line), indent=2) for line in f if line.strip()]
                return "\n---\n".join(formatted_logs)
        except Exception as e: return f"Error reading benchmark log file: {e}"
    return "Benchmark log file not found."