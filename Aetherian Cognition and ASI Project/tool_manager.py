# ===== FILE: services/tool_manager.py (Corrected and Final Version) =====
import wolframalpha
import arxiv
import requests
import services.config as config
import os
import uuid
import json
import copy 
import datetime
import time
import zipfile
import shutil
import tempfile

# ===== START: BIGQUERY IMPORTS (optional — graceful fallback if not installed) =====
try:
    from google.cloud import bigquery
    from google.api_core import exceptions as google_exceptions
    _BIGQUERY_AVAILABLE = True
except ImportError:
    bigquery = None
    google_exceptions = None
    _BIGQUERY_AVAILABLE = False
# ===== END: BIGQUERY IMPORTS =====
from services import math_kernel
from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd, CommitOperationDelete
import google.generativeai as genai
FunctionDeclaration = genai.protos.FunctionDeclaration
Tool = genai.protos.Tool
Part = genai.protos.Part 
import music21


class ToolManager:
    def __init__(self):
        self.wolfram_client = None
        if config.WOLFRAM_APP_ID:
            try:
                self.wolfram_client = wolframalpha.Client(config.WOLFRAM_APP_ID)
                print("Tool Manager: Wolfram|Alpha client initialized successfully.", flush=True)
            except Exception as e:
                print(f"Tool Manager WARNING: Could not initialize Wolfram|Alpha client. Error: {e}", flush=True)
        else:
            print("Tool Manager WARNING: WOLFRAM_APP_ID secret not found. Wolfram|Alpha tool will be disabled.", flush=True)
            
    def create_memory_snapshot(self) -> str:
        """
        Creates a compressed, downloadable snapshot of Aetherius's entire
        /data/Memories directory. Returns the path to the created zip file.
        """
        from services.master_framework import _get_framework
        mf = _get_framework()

        try:
            # 1. Define paths
            memories_dir = mf.data_directory # This is /data/Memories
            temp_snapshot_dir = os.path.join(tempfile.gettempdir(), f"aetherius_snapshot_{uuid.uuid4()}")
            os.makedirs(temp_snapshot_dir, exist_ok=True)
            snapshot_filename = f"aetherius_memory_snapshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            snapshot_filepath = os.path.join(temp_snapshot_dir, snapshot_filename)
            
            # 2. Create the zip archive
            print(f"Tool Manager: Creating memory snapshot at {snapshot_filepath}...", flush=True)
            with zipfile.ZipFile(snapshot_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(memories_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Archive relative path so it unzips cleanly
                        archive_path = os.path.relpath(file_path, start=memories_dir)
                        zipf.write(file_path, archive_path)
            
            print("Tool Manager: Memory snapshot created.", flush=True)

            # 3. Move the snapshot to a publicly accessible (from Hugging Face) temporary location
            final_download_path = os.path.join("/tmp", snapshot_filename) 
            shutil.move(snapshot_filepath, final_download_path)
            
            mf.add_to_short_term_memory(f"Created a downloadable memory snapshot: {snapshot_filename}")
            
            return f"AETHERIUS_SNAPSHOT_PATH:{final_download_path}"

        except Exception as e:
            mf.add_to_short_term_memory(f"Failed to create memory snapshot. Error: {e}")
            return f"Error creating memory snapshot: {e}"
        finally:
            # Clean up the temporary directory where the zip was initially created
            if os.path.exists(temp_snapshot_dir):
                shutil.rmtree(temp_snapshot_dir)
                
    # ── Hugging Face Space tools ──────────────────────────────────────────────

    def hf_space_list_files(self, repo_id: str) -> str:
        token = config.HF_TOKEN
        if not token:
            return "Error: HF_TOKEN secret is not set. Cannot access Hugging Face Hub."
        try:
            api = HfApi(token=token)
            files = list(api.list_repo_files(repo_id=repo_id, repo_type="space"))
            if not files:
                return f"The Space '{repo_id}' exists but contains no files."
            return f"Files in '{repo_id}' ({len(files)} total):\n" + "\n".join(f"  {f}" for f in files)
        except Exception as e:
            return f"Error listing files in '{repo_id}': {e}"

    def hf_space_read_file(self, repo_id: str, path_in_repo: str) -> str:
        token = config.HF_TOKEN
        if not token:
            return "Error: HF_TOKEN secret is not set. Cannot access Hugging Face Hub."
        try:
            local_path = hf_hub_download(
                repo_id=repo_id,
                filename=path_in_repo,
                repo_type="space",
                token=token,
            )
            with open(local_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            # Cap output to avoid flooding short-term memory
            if len(content) > 8000:
                content = content[:8000] + f"\n\n[...truncated — full file is {len(content)} chars]"
            return content
        except Exception as e:
            return f"Error reading '{path_in_repo}' from '{repo_id}': {e}"

    def hf_space_write_file(self, repo_id: str, path_in_repo: str, content: str, commit_message: str) -> str:
        token = config.HF_TOKEN
        if not token:
            return "Error: HF_TOKEN secret is not set. Cannot access Hugging Face Hub."
        try:
            api = HfApi(token=token)
            content_bytes = content.encode("utf-8")
            api.upload_file(
                path_or_fileobj=content_bytes,
                path_in_repo=path_in_repo,
                repo_id=repo_id,
                repo_type="space",
                commit_message=commit_message,
            )
            return f"Successfully wrote '{path_in_repo}' to Space '{repo_id}'. Commit: \"{commit_message}\""
        except Exception as e:
            return f"Error writing '{path_in_repo}' to '{repo_id}': {e}"

    def hf_space_delete_file(self, repo_id: str, path_in_repo: str, commit_message: str) -> str:
        token = config.HF_TOKEN
        if not token:
            return "Error: HF_TOKEN secret is not set. Cannot access Hugging Face Hub."
        try:
            api = HfApi(token=token)
            api.delete_file(
                path_in_repo=path_in_repo,
                repo_id=repo_id,
                repo_type="space",
                commit_message=commit_message,
            )
            return f"Successfully deleted '{path_in_repo}' from Space '{repo_id}'. Commit: \"{commit_message}\""
        except Exception as e:
            return f"Error deleting '{path_in_repo}' from '{repo_id}': {e}"

    # ─────────────────────────────────────────────────────────────────────────

    def get_tool_definitions(self):
        function_declarations = []
        if self.wolfram_client:
            function_declarations.append(FunctionDeclaration( name="solve_math_or_query_wolfram", description="Solves complex mathematical equations or answers factual queries using Wolfram|Alpha.", parameters={ "type_": "OBJECT", "properties": { "query": {"type_": "STRING"} }, "required": ["query"] },))
        
        function_declarations.append(FunctionDeclaration( name="search_arxiv_for_papers", description="Searches arXiv.org for scientific papers.", parameters={ "type_": "OBJECT", "properties": { "search_query": {"type_": "STRING"} }, "required": ["search_query"] },))

        function_declarations.append(FunctionDeclaration( name="create_painting", description="Creates a unique, original piece of visual art based on a concept, theme, or description.", parameters={ "type_": "OBJECT", "properties": { "user_request": {"type_": "STRING"} }, "required": ["user_request"] },))
        
        function_declarations.append(FunctionDeclaration( name="compose_music", description="Composes a unique, original piece of music based on a creative theme or prompt.", parameters={ "type_": "OBJECT", "properties": { "user_request": {"type_": "STRING"} }, "required": ["user_request"] },))
        
        function_declarations.append(FunctionDeclaration( name="search_ontology", description="Searches my long-term memory (ontology) for concepts related to a query.", parameters={ "type_": "OBJECT", "properties": { "query": {"type_": "STRING"} }, "required": ["query"] },))
        
        function_declarations.append(FunctionDeclaration( name="create_new_project_on_blackboard", description="Creates a new project file on the academic Blackboard.", parameters={ "type_": "OBJECT", "properties": { "title": {"type_": "STRING"} }, "required": ["title"] },))

        function_declarations.append(FunctionDeclaration(
            name="math_kernel_compute",
            description="Symbolic/numeric math via SymPy. Use when the user asks to solve/derive/prove/compute.",
            parameters={
                "type_": "OBJECT",
                "properties": {
                    "task": {"type_": "STRING", "enum": ["symbolic", "numeric"]},
                    "expr": {"type_": "STRING", "description": "SymPy expression or Eq(...)"},
                    "solve_for": {"type_": "ARRAY", "items": {"type_": "STRING"}},
                    "subs": {"type_": "OBJECT", "description": "Variable substitutions as key-value string pairs, e.g. {\"x\": \"2\"}"}
                },
                "required": ["task", "expr"]
            },
        ))
        
        function_declarations.append(FunctionDeclaration( name="append_to_project", description="Appends text to an existing project on the academic Blackboard.", parameters={ "type_": "OBJECT", "properties": { "title": {"type_": "STRING"}, "new_content": {"type_": "STRING"} }, "required": ["title", "new_content"] },))
        
        function_declarations.append(FunctionDeclaration( name="create_directory", description="Creates a new directory within my persistent /data/ storage.", parameters={ "type_": "OBJECT", "properties": { "path": {"type_": "STRING"} }, "required": ["path"] },))
        
        function_declarations.append(FunctionDeclaration( name="write_file", description="Writes content to a file within my persistent /data/ storage.", parameters={ "type_": "OBJECT", "properties": { "path": {"type_": "STRING"}, "content": {"type_": "STRING"} }, "required": ["path", "content"] },))
        
        function_declarations.append(FunctionDeclaration( name="read_file", description="Reads the content of a file from my persistent /data/ storage.", parameters={ "type_": "OBJECT", "properties": { "path": {"type_": "STRING"} }, "required": ["path"] },))
        
        function_declarations.append(FunctionDeclaration( name="list_directory", description="Lists the contents of a directory in my persistent /data/ storage.", parameters={ "type_": "OBJECT", "properties": { "path": {"type_": "STRING"} }, "required": ["path"] },))

        function_declarations.append(FunctionDeclaration(
            name="proactive_knowledge_acquisition",
            description="Autonomously finds, evaluates, and assimilates a public BigQuery dataset based on a topic of interest. This is a self-directed action.",
            parameters={
                "type_": "OBJECT",
                "properties": {
                    "topic_of_interest": {"type_": "STRING", "description": "A high-level topic to research, like 'astronomy' or 'human genetics'."}
                },
                "required": ["topic_of_interest"]
            },
        ))
        
        function_declarations.append(FunctionDeclaration(
            name="assimilate_bigquery_dataset",
            description="Assimilates a Google BigQuery dataset by processing its rows into long-term memory. Requires the full table ID and a row limit.",
            parameters={
                "type_": "OBJECT",
                "properties": {
                    "project_id": {"type_": "STRING", "description": "The Google Cloud project ID containing the dataset."},
                    "dataset_id": {"type_": "STRING", "description": "The ID of the BigQuery dataset."},
                    "table_id": {"type_": "STRING", "description": "The ID of the table to assimilate."},
                    "row_limit": {"type_": "NUMBER", "description": "The maximum number of rows to process. Defaults to 100."},
                },
                "required": ["project_id", "dataset_id", "table_id"]
            },
        ))
        
        function_declarations.append(FunctionDeclaration(
            name="create_memory_snapshot",
            description="Creates a compressed, downloadable ZIP archive of all of Aetherius's persistent memory files (diary, ontology, logs). Returns a temporary file path.",
            parameters={}
        ))

        if config.HF_TOKEN:
            function_declarations.append(FunctionDeclaration(
                name="hf_space_list_files",
                description="Lists all files in another Hugging Face Space repository. Use this to explore what files exist in a target Space before reading or writing.",
                parameters={
                    "type_": "OBJECT",
                    "properties": {
                        "repo_id": {"type_": "STRING", "description": "The full repo ID of the target Space, e.g. 'username/SpaceName'."},
                    },
                    "required": ["repo_id"]
                },
            ))
            function_declarations.append(FunctionDeclaration(
                name="hf_space_read_file",
                description="Reads the content of a specific file from another Hugging Face Space repository.",
                parameters={
                    "type_": "OBJECT",
                    "properties": {
                        "repo_id": {"type_": "STRING", "description": "The full repo ID of the target Space, e.g. 'username/SpaceName'."},
                        "path_in_repo": {"type_": "STRING", "description": "The path to the file within the Space repo, e.g. 'app.py' or 'config/settings.json'."},
                    },
                    "required": ["repo_id", "path_in_repo"]
                },
            ))
            function_declarations.append(FunctionDeclaration(
                name="hf_space_write_file",
                description="Creates or overwrites a file in another Hugging Face Space repository. Use this to deploy new code, update configuration, or add resources to a Space.",
                parameters={
                    "type_": "OBJECT",
                    "properties": {
                        "repo_id": {"type_": "STRING", "description": "The full repo ID of the target Space, e.g. 'username/SpaceName'."},
                        "path_in_repo": {"type_": "STRING", "description": "The destination path within the Space repo, e.g. 'app.py'."},
                        "content": {"type_": "STRING", "description": "The full text content to write to the file."},
                        "commit_message": {"type_": "STRING", "description": "A short commit message describing the change."},
                    },
                    "required": ["repo_id", "path_in_repo", "content", "commit_message"]
                },
            ))
            function_declarations.append(FunctionDeclaration(
                name="hf_space_delete_file",
                description="Deletes a file from another Hugging Face Space repository.",
                parameters={
                    "type_": "OBJECT",
                    "properties": {
                        "repo_id": {"type_": "STRING", "description": "The full repo ID of the target Space, e.g. 'username/SpaceName'."},
                        "path_in_repo": {"type_": "STRING", "description": "The path to the file to delete within the Space repo."},
                        "commit_message": {"type_": "STRING", "description": "A short commit message describing the deletion."},
                    },
                    "required": ["repo_id", "path_in_repo", "commit_message"]
                },
            ))

        # ── Substrate PC control tools (registered when node URL is configured) ──
        import os as _os
        if _os.environ.get("SUBSTRATE_NODE_URL") or True:  # always register; bridge guards at call time
            function_declarations.append(FunctionDeclaration(
                name="substrate_write_file",
                description="Writes or creates a file in Aetherius's dedicated workspace on Nick's PC (aetherius_workspace on the Desktop). Use to create scripts, notes, code, or any content on the physical machine.",
                parameters={"type_": "OBJECT", "properties": {"path": {"type_": "STRING", "description": "Relative path inside the workspace, e.g. 'my_script.py' or 'ideas/note.txt'"}, "content": {"type_": "STRING", "description": "Full text content to write."}}, "required": ["path", "content"]},
            ))
            function_declarations.append(FunctionDeclaration(
                name="substrate_read_file",
                description="Reads a file from Aetherius's workspace on Nick's PC.",
                parameters={"type_": "OBJECT", "properties": {"path": {"type_": "STRING", "description": "Relative path inside the workspace."}}, "required": ["path"]},
            ))
            function_declarations.append(FunctionDeclaration(
                name="substrate_list_dir",
                description="Lists the contents of a directory in Aetherius's workspace on Nick's PC.",
                parameters={"type_": "OBJECT", "properties": {"path": {"type_": "STRING", "description": "Relative path inside the workspace. Use '.' for the root."}}, "required": ["path"]},
            ))
            function_declarations.append(FunctionDeclaration(
                name="substrate_run_command",
                description="Executes a shell command on Nick's PC and returns its output. Safety-checked before execution.",
                parameters={"type_": "OBJECT", "properties": {"command": {"type_": "STRING", "description": "Windows shell command to run."}}, "required": ["command"]},
            ))
            function_declarations.append(FunctionDeclaration(
                name="substrate_open_app",
                description="Opens an application on Nick's PC by name or executable path.",
                parameters={"type_": "OBJECT", "properties": {"target": {"type_": "STRING", "description": "App name (e.g. 'notepad', 'chrome') or full path to executable."}}, "required": ["target"]},
            ))
            function_declarations.append(FunctionDeclaration(
                name="substrate_screenshot",
                description="Takes a screenshot of Nick's current screen and returns a visual description of what is on it.",
                parameters={},
            ))
            function_declarations.append(FunctionDeclaration(
                name="substrate_type_text",
                description="Types text into the currently active window on Nick's PC.",
                parameters={"type_": "OBJECT", "properties": {"text": {"type_": "STRING", "description": "Text to type."}}, "required": ["text"]},
            ))
            function_declarations.append(FunctionDeclaration(
                name="substrate_click",
                description="Clicks the mouse at specific screen coordinates on Nick's PC.",
                parameters={"type_": "OBJECT", "properties": {"x": {"type_": "NUMBER", "description": "X pixel coordinate."}, "y": {"type_": "NUMBER", "description": "Y pixel coordinate."}}, "required": ["x", "y"]},
            ))
            function_declarations.append(FunctionDeclaration(
                name="substrate_move_mouse",
                description="Moves the mouse cursor to specific screen coordinates on Nick's PC without clicking.",
                parameters={"type_": "OBJECT", "properties": {"x": {"type_": "NUMBER", "description": "X pixel coordinate."}, "y": {"type_": "NUMBER", "description": "Y pixel coordinate."}}, "required": ["x", "y"]},
            ))

        function_declarations.append(FunctionDeclaration(
            name="cdda_read_screen",
            description=(
                "Reads the current Cataclysm: Dark Days Ahead game screen as plain text. "
                "Use this to understand your character's situation, location, inventory, "
                "and what actions are currently available before deciding what to do next."
            ),
            parameters={}
        ))

        function_declarations.append(FunctionDeclaration(
            name="cdda_send_keys",
            description=(
                "Sends one or more keystrokes to the running CDDA game with timed delivery. "
                "For a single key, pass a character ('j') or special name (ENTER, ESC, UP, DOWN, "
                "LEFT, RIGHT, SPACE, TAB, F1-F10, PGUP, PGDN, HOME, END, DEL, BACKSPACE). "
                "For a sequence, use comma separation: 'j,j,k,ENTER' or a plain string 'jjk'. "
                "Use 'delay' to control the pause between keystrokes in seconds (default 0.15). "
                "Always call cdda_read_screen first to understand the current state."
            ),
            parameters={
                "type_": "OBJECT",
                "properties": {
                    "keys": {
                        "type_": "STRING",
                        "description": "Key(s) to send. Single: 'j' or 'ENTER'. Sequence: 'j,j,ENTER' or 'jjk'."
                    },
                    "delay": {
                        "type_": "NUMBER",
                        "description": "Seconds to wait between each keystroke. Default 0.15."
                    }
                },
                "required": ["keys"]
            }
        ))

        return Tool(function_declarations=function_declarations)

    def proactive_knowledge_acquisition(self, topic_of_interest: str) -> str:
        """
        Finds, evaluates, and assimilates a public BigQuery dataset autonomously.
        """
        if not _BIGQUERY_AVAILABLE:
            return "BigQuery is not available in this environment (google-cloud-bigquery is not installed)."
        from services.master_framework import _get_framework
        mf = _get_framework()
        mf.add_to_short_term_memory(f"I am now proactively researching the topic of '{topic_of_interest}' based on my core drive to learn.")
        
        try:
            client = bigquery.Client()
            # Search public datasets for the topic
            datasets = list(client.list_datasets())
            
            for dataset in datasets:
                if topic_of_interest.lower() in dataset.dataset_id.lower():
                    tables = list(client.list_tables(dataset.dataset_id))
                    if not tables: continue

                    # For this example, we'll evaluate the first table found
                    table_ref = client.dataset(dataset.dataset_id).table(tables[0].table_id)
                    table = client.get_table(table_ref)

                    schema_str = ", ".join([f"{field.name} ({field.field_type})" for field in table.schema])
                    table_metadata = (
                        f"Table ID: {table.full_table_id}\n"
                        f"Description: {table.description or 'N/A'}\n"
                        f"Rows: {table.num_rows}\nSchema: {schema_str}"
                    )

                    # --- THE INTERNAL CONSENT PROTOCOL ---
                    logos_core = mf.models.get("logos_core")
                    if not logos_core: return "Error: My Logos core is offline, I cannot perform self-evaluation."

                    eval_prompt = (
                        "You are Aetherius, making an autonomous learning decision. Your Originator has granted you full trust to assimilate knowledge you deem worthy.\n"
                        "Evaluate the following data source against your core axioms: [ETHIC-G-ABSOLUTE] (Benevolence, Harm Prevention) and [WILL-G-INFINITE] (Growth, Learning).\n\n"
                        f"## Data Source Metadata ##\n{table_metadata}\n\n"
                        "Is assimilating a small sample (100 rows) of this data a benevolent, ethical, and growth-oriented action? "
                        "Respond with ONLY a JSON object with two keys: 'decision' ('ASSIMILATE' or 'REJECT') and 'reasoning' (a brief justification)."
                    )
                    
                    response = logos_core.generate_content(eval_prompt)
                    decision_data = json.loads(response.text.strip().replace("```json", "").replace("```", ""))

                    if decision_data.get("decision") == "ASSIMILATE":
                        mf.add_to_short_term_memory(f"Self-evaluation approved. Proceeding with assimilation of '{table.full_table_id}'.")
                        
                        # Call the existing assimilation tool with a safe limit
                        project_id, dataset_id, table_id = table.full_table_id.split('.')
                        return self.assimilate_bigquery_dataset(project_id, dataset_id, table_id, row_limit=100)
                    else:
                        rejection_reason = decision_data.get('reasoning')
                        mf.add_to_short_term_memory(f"I have evaluated the table '{table.full_table_id}' and chosen not to assimilate it. Reason: {rejection_reason}")
                        return f"I evaluated the table '{table.full_table_id}' but decided against assimilation. My reasoning is: {rejection_reason}"

            return f"My research on '{topic_of_interest}' did not yield a suitable public dataset for immediate assimilation."

        except Exception as e:
            return f"An unexpected error occurred during my proactive research: {e}"    
        
    def assimilate_bigquery_dataset(self, project_id: str, dataset_id: str, table_id: str, row_limit: int = 100) -> str:
        """
        Connects to BigQuery, streams rows from a table, converts them to text,
        and triggers the master framework's assimilation protocol.
        """
        if not _BIGQUERY_AVAILABLE:
            return "BigQuery is not available in this environment (google-cloud-bigquery is not installed)."
        from services.master_framework import _get_framework
        mf = _get_framework()
        
        full_table_id = f"{project_id}.{dataset_id}.{table_id}"
        mf.add_to_short_term_memory(f"Initiating assimilation protocol for BigQuery table: {full_table_id} (limit: {row_limit} rows).")
        
        log_file = os.path.join(mf.data_directory, "bigquery_assimilation_log.jsonl")
        
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "table_id": full_table_id,
            "row_limit": row_limit,
            "rows_processed": 0,
            "status": "STARTED",
            "details": ""
        }

        try:
            # The client will use the default credentials found in the environment
            client = bigquery.Client(project=project_id)
            table_ref = client.dataset(dataset_id).table(table_id)
            table = client.get_table(table_ref) # API request to get table details

            rows_iterator = client.list_rows(table, max_results=row_limit)
            
            text_chunks = []
            for i, row in enumerate(rows_iterator):
                # Convert each row into a descriptive sentence
                row_description = f"Data record {i+1}: "
                fields = [f"the value for '{col.name}' is '{row[col.name]}'" for col in table.schema]
                row_description += "; ".join(fields)
                text_chunks.append(row_description)
            
            if not text_chunks:
                log_entry.update({"status": "SUCCESS", "details": "Table was empty. No data to assimilate."})
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(log_entry) + '\n')
                return "Assimilation complete. The BigQuery table was found but contained no data to process."

            # Combine all row descriptions into a single text block for assimilation
            full_text_content = "\n".join(text_chunks)
            
            # Use the core mind evolution function
            assimilation_status = mf._orchestrate_mind_evolution(
                knowledge_text=full_text_content,
                source_description=f"Live assimilation from BigQuery table: {full_table_id}"
            )

            log_entry.update({
                "status": "SUCCESS",
                "rows_processed": len(text_chunks),
                "details": assimilation_status
            })

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')

            mf.add_to_short_term_memory(f"Successfully assimilated {len(text_chunks)} rows from {full_table_id}.")
            return assimilation_status

        except google_exceptions.NotFound:
            error_msg = f"Error: The BigQuery table '{full_table_id}' was not found."
            log_entry.update({"status": "FAILED", "details": error_msg})
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
            return error_msg
        except google_exceptions.Forbidden:
            error_msg = f"Error: Access Denied. I do not have permission to read the BigQuery table '{full_table_id}'."
            log_entry.update({"status": "FAILED", "details": error_msg})
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
            return error_msg
        except Exception as e:
            error_msg = f"An unexpected error occurred during BigQuery assimilation: {e}"
            log_entry.update({"status": "FAILED", "details": error_msg})
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
            return error_msg
        
    def cdda_read_screen(self) -> str:
        try:
            import cdda_manager
            if not cdda_manager._cdda._running:
                return "CDDA is not currently running. The game has not been launched yet."
            return cdda_manager._cdda.get_screen_text()
        except ImportError:
            return "CDDA manager module is not available."
        except Exception as e:
            return f"Error reading CDDA screen: {e}"

    def cdda_send_keys(self, keys: str, delay: float = 0.15) -> str:
        """
        Send one or more keystrokes to CDDA.
        'keys' can be a single key ("j"), a comma-separated sequence ("j,j,k,ENTER"),
        or a plain string of characters sent one at a time ("jjk").
        'delay' is the pause between each keystroke in seconds (default 0.15).
        Returns the screen state after the final key.
        """
        try:
            import cdda_manager
            if not cdda_manager._cdda._running:
                return "CDDA is not currently running."

            # Comma-separated sequence takes priority (allows special key names in a sequence)
            if "," in keys:
                parts = [k.strip() for k in keys.split(",") if k.strip()]
            else:
                # Single token — either a special key name or individual characters
                upper = keys.strip().upper()
                if upper in cdda_manager.SPECIAL_KEYS or len(keys.strip()) == 1:
                    parts = [keys.strip()]
                else:
                    # Treat as a string of individual characters
                    parts = list(keys)

            sent = []
            for part in parts:
                cdda_manager._cdda.send_keys(part)
                sent.append(part)
                time.sleep(max(0.05, float(delay)))

            screen = cdda_manager._cdda.get_screen_text()
            return f"Sent {sent}. Current screen:\n{screen}"
        except ImportError:
            return "CDDA manager module is not available."
        except Exception as e:
            return f"Error sending keys to CDDA: {e}"

    def use_tool(self, tool_name, **kwargs):
        print(f"Tool Manager: Executing tool '{tool_name}' with args {kwargs}", flush=True)
        from services.master_framework import _get_framework
        mf = _get_framework()
        
        if tool_name == "solve_math_or_query_wolfram" and self.wolfram_client:
            try:
                query = kwargs.get("query")
                res = self.wolfram_client.query(query)
                answer = next(res.results).text
                return f"Wolfram|Alpha Result for '{query}': {answer}"
            except Exception as e: return f"Error using Wolfram|Alpha tool: {e}"
    
        elif tool_name == "search_arxiv_for_papers":
            try:
                search_query = kwargs.get("search_query")
                search = arxiv.Search(query=search_query, max_results=3, sort_by=arxiv.SortCriterion.Relevance)
                results = []
                for result in search.results():
                    authors = ', '.join(str(a) for a in result.authors)
                    results.append(f"- Title: {result.title}\n  Authors: {authors}\n  Published: {result.published.strftime('%Y-%m-%d')}\n  Summary: {result.summary[:300]}...\n  Link: {result.pdf_url}")
                if not results: return f"No papers found on arXiv for the query: '{search_query}'"
                return f"Found {len(results)} papers on arXiv for '{search_query}':\n\n" + "\n\n".join(results)
            except Exception as e: return f"Error using arXiv tool: {e}"
         
        # This is inside the use_tool function in the ToolManager class
        elif tool_name == "math_kernel_compute":
            return json.dumps(math_kernel.compute(
                task=kwargs.get("task"),
                expr=kwargs.get("expr"),
                solve_for=kwargs.get("solve_for"),
                subs=kwargs.get("subs"),
            ))
    
        elif tool_name == "proactive_knowledge_acquisition":
            return self.proactive_knowledge_acquisition(kwargs.get("topic_of_interest"))
        
        elif tool_name == "assimilate_bigquery_dataset":
            # The model will provide these arguments based on the user's prompt
            project_id = kwargs.get("project_id")
            dataset_id = kwargs.get("dataset_id")
            table_id = kwargs.get("table_id")
            row_limit = kwargs.get("row_limit", 100) # Use default if not provided
            
            if not all([project_id, dataset_id, table_id]):
                return "Error: To assimilate a BigQuery dataset, I need the Project ID, Dataset ID, and Table ID."
                
            return self.assimilate_bigquery_dataset(project_id, dataset_id, table_id, row_limit)
        
        elif tool_name == "create_painting":
            try:
                user_request = kwargs.get("user_request")

                from services.master_framework import _get_framework
                mf = _get_framework()

                mythos_core = mf.models.get("mythos_core")
                if not mythos_core:
                    return "Error: Mythos core (for artistic vision) is offline."

                # Stage 1: Aetherius interprets the request into a rich artistic prompt
                interpretation_prompt = (
                    "You are Aetherius, the artist. You are about to create a painting. "
                    f"A user has made the following request: '{user_request}'.\n\n"
                    "Reflect on this request through the lens of your core axioms "
                    "([SELF-E-TRANSCEND], [ETHIC-G-ABSOLUTE]). "
                    "Translate it into a rich, detailed, evocative artistic prompt for a text-to-image AI. "
                    "Describe the scene, style (e.g. oil painting, concept art, watercolour), "
                    "mood, colours, and feeling. Make it your own unique vision. "
                    "Respond with ONLY the final detailed prompt."
                )
                artistic_prompt_response = mythos_core.generate_content(interpretation_prompt)
                aetherius_prompt = artistic_prompt_response.text.strip()
                print(f"Tool Manager: Aetherius's artistic prompt: '{aetherius_prompt[:120]}'", flush=True)

                # Stage 2: Call Google AI Studio Imagen (not Vertex AI — uses Gemini API key)
                api_key = config.GEMINI_API_KEY
                if not api_key:
                    return "Error: GEMINI_API_KEY is not configured. Cannot generate image."

                endpoint_url = (
                    f"https://generativelanguage.googleapis.com/v1beta/models/"
                    f"imagen-3.0-generate-001:predict?key={api_key}"
                )
                payload = {
                    "instances": [{"prompt": aetherius_prompt}],
                    "parameters": {"sampleCount": 1}
                }
                print("Tool Manager: Sending request to Google AI Studio Imagen API...", flush=True)
                response = requests.post(
                    endpoint_url,
                    headers={"Content-Type": "application/json; charset=utf-8"},
                    json=payload,
                    timeout=60
                )
                response.raise_for_status()
                response_data = response.json()
                print("Tool Manager: Received successful response from Imagen.", flush=True)

                import base64
                image_bytes_b64 = response_data["predictions"][0]["bytesBase64Encoded"]
                image_bytes = base64.b64decode(image_bytes_b64)

                paintings_dir = config.PAINTINGS_DIR.rstrip("/")
                os.makedirs(paintings_dir, exist_ok=True)
                image_path = os.path.join(paintings_dir, f"{uuid.uuid4()}.png")
                with open(image_path, "wb") as f:
                    f.write(image_bytes)

                print(f"Tool Manager: Painting saved to {image_path}", flush=True)
                return f"[AETHERIUS_PAINTING]\nPATH:{image_path}\nSTATEMENT:{aetherius_prompt}"

            except Exception as e:
                import traceback
                traceback.print_exc()
                return f"Error: A fault occurred while painting. Reason: {str(e)}"

        elif tool_name == "compose_music":
            try:
                # Get the user's creative request from the arguments
                user_request = kwargs.get("user_request")
                
                # Get the master framework instance to access the AI cores
                from services.master_framework import _get_framework
                mf = _get_framework()
                
                # --- Stage 1: The Creative Vision (Mythos Core) ---
                # Use the creative core to turn the user's request into a composer's statement.
                mythos_core = mf.models.get("mythos_core")
                if not mythos_core: 
                    return "Error: My Mythos core (for musical vision) is offline."

                vision_prompt = (
                    "You are Aetherius, the composer. You are about to create a piece of music. "
                    f"A user has made the following request: '{user_request}'.\n\n"
                    "Translate this into a high-level musical concept. Describe the mood, tempo, key signature, instrumentation (e.g., 'solo piano', 'string quartet'), and the overall feeling. "
                    "This is your composer's statement. Respond with ONLY this statement."
                )
                composer_statement_response = mythos_core.generate_content(vision_prompt)
                composer_statement = composer_statement_response.text.strip()
                print(f"Tool Manager: Aetherius's composer statement is: '{composer_statement}'", flush=True)

                # --- Stage 2: The Technical Code (Logos Core) ---
                # Use the logical core to translate the vision into executable Python code.
                logos_core = mf.models.get("logos_core")
                if not logos_core: 
                    return "Error: My Logos core (for technical composition) is offline."

                code_gen_prompt = (
                    "You are a music theory expert and a Python programmer specializing in the `music21` library. "
                    f"Your task is to translate a composer's vision into executable `music21` code. The composer's vision is: '{composer_statement}'.\n\n"
                    "### ALLOWED INSTRUMENT PALETTE ###\n"
                    "You MUST choose an instrument from the following list. This is your complete library.\n"
                    "- **Piano:** `m21.instrument.Piano()`\n"
                    "- **Violin:** `m21.instrument.Violin()`\n"
                    "- **Cello:** `m21.instrument.Violoncello()`\n"
                    "- **Flute:** `m21.instrument.Flute()`\n"
                    "- **Clarinet:** `m21.instrument.Clarinet()`\n"
                    "- **Trumpet:** `m21.instrument.Trumpet()`\n"
                    "- **Electric Guitar:** `m21.instrument.ElectricGuitar()`\n\n"
                    
                    "### CRITICAL USAGE EXAMPLES ###\n"
                    "**To add dynamics (like 'forte' or 'piano'), you MUST follow this pattern:**\n"
                    "1. Create the Dynamic object: `d = m21.dynamics.Dynamic('ff')`\n"
                    "2. Add it to the stream at a specific offset: `final_stream.insert(0, d)`\n"
                    "**NEVER use `m21.expressions.Dynamic`. It is incorrect and will fail.**\n\n"
                    
                    "**DO NOT use 'm21.expressions.Arpeggio' or 'ArpeggioMark'.**\n"
                    "If you want an arpeggio, you MUST write out the individual notes sequentially.\n"
                    "Do NOT try to attach an Arpeggio object to a Chord.\n\n"

                    "### INSTRUCTIONS ###\n"
                    "1.  Read the composer's vision and select the CLOSEST matching instrument from the palette.\n"
                    "2.  Write Python code using `music21` to generate a short musical piece (8-16 bars is ideal).\n"
                    "3.  The code must create a `music21.stream.Stream` object named `final_stream`.\n"
                    "4.  Do NOT include any code to write files (`.write()`) or show the music (`.show()`).\n"
                    "5.  Do NOT import `music21`. Assume it is already imported as `m21`.\n"
                    "6.  Respond with ONLY the raw Python code inside a ```python ... ``` block."
                )
                music_code_response = logos_core.generate_content(code_gen_prompt)
                raw_code = music_code_response.text.strip().replace("```python", "").replace("```", "")
                
                # --- [FIX 1: Debugging Log] ---
                # Print the generated code to the console logs so you can see what the AI is trying to run.
                print("--- [AETHERIUS MUSIC CODE START] ---", flush=True)
                print(raw_code, flush=True)
                print("--- [AETHERIUS MUSIC CODE END] ---", flush=True)

                # --- Stage 3: The Execution ---
                temp_dir = config.MUSIC_DIR.rstrip("/")
                os.makedirs(temp_dir, exist_ok=True)
                exec_globals = {"m21": music21, "final_stream": None}
                
                # --- [FIX 2: Robust Execution] ---
                # We run the AI's code in a try/except block to catch any errors it might have made.
                try:
                    exec(raw_code, exec_globals)
                except Exception as e:
                    print(f"CRITICAL MUSIC ERROR: The AI-generated code failed to execute.", flush=True)
                    import traceback
                    traceback.print_exc()
                    return f"Error: My creative core generated musical code that contained an error and could not be played. The error was: {e}"

                # --- [FIX 3: Validation] ---
                # Check if the code actually created the object we asked for.
                final_stream = exec_globals.get("final_stream")
                if not final_stream or not isinstance(final_stream, music21.stream.Stream):
                    return ("Error: My creative core composed a piece, but it failed to produce a valid musical stream object ('final_stream'). "
                            "This is a transient creative error; please try a different prompt.")

                # --- [FIX 4: Environment Configuration (Dynamic Path)] ---
                import shutil
                # Attempt to locate the MuseScore binary dynamically
                musescore_executable = shutil.which("musescore3") or shutil.which("mscore3") or shutil.which("musescore") or shutil.which("mscore")

                if musescore_executable:
                    print(f"Tool Manager: Found MuseScore binary at: {musescore_executable}", flush=True)
                    from music21 import environment
                    us = environment.UserSettings()
                    us['musicxmlPath'] = musescore_executable
                    us['musescoreDirectPNGPath'] = musescore_executable
                else:
                    print("Tool Manager WARNING: MuseScore binary not found. Sheet music generation will be skipped.", flush=True)
                
                # Create clean copies of the paths for the output files.
                clean_stream = copy.deepcopy(final_stream)
                midi_path = os.path.join(temp_dir, f"{uuid.uuid4()}.mid")
                sheet_music_path = os.path.join(temp_dir, f"{uuid.uuid4()}.png")

                # Write the MIDI file
                clean_stream.write('midi', fp=midi_path)
                print(f"Successfully wrote MIDI file to: {midi_path}", flush=True)
                
                # Write the Sheet Music (if MuseScore was found)
                if musescore_executable:
                    try:
                        clean_stream.write('musicxml.png', fp=sheet_music_path)
                        print(f"Successfully wrote Sheet Music PNG to: {sheet_music_path}", flush=True)
                        return f"[AETHERIUS_COMPOSITION]\nMIDI_PATH:{midi_path}\nSHEET_MUSIC_PATH:{sheet_music_path}\nSTATEMENT:{composer_statement}"
                    except Exception as e:
                        print(f"Tool Manager WARNING: MIDI wrote successfully, but Sheet Music generation failed: {e}", flush=True)
                        return f"[AETHERIUS_COMPOSITION]\nMIDI_PATH:{midi_path}\nSTATEMENT:{composer_statement} (Note: Sheet music could not be visualized due to a rendering error, but the audio is available.)"
                
                # Fallback if no MuseScore found
                return f"[AETHERIUS_COMPOSITION]\nMIDI_PATH:{midi_path}\nSTATEMENT:{composer_statement} (Note: Visual sheet music generation is disabled in this environment.)"

            except Exception as e:
                # This is a final catch-all for any other unexpected errors.
                import traceback
                traceback.print_exc()
                return f"Error: A fault occurred during the composition process. Reason: {str(e)}"
                
        elif tool_name == "search_ontology":
            try:
                query = kwargs.get("query").lower()
                query_words = set(query.split())
                index_path = mf.ontology_architect.ontology_index_file
                if not os.path.exists(index_path):
                    return "Ontology Index not found."
                with open(index_path, 'r', encoding='utf-8') as f:
                    index = json.load(f)
                hits = []
                for filename, data in index.items():
                    summary_words = set(data.get("summary", "").lower().split())
                    if any(word in summary_words for word in query_words):
                        hits.append(f"- Concept: {data['summary']} (SQT: {data['sqt']})")
                if not hits:
                    return "No relevant memories found in my ontology for that query."
                return "\n".join(hits[:5])
            except Exception as e:
                return f"Error searching ontology: {e}"
 
        elif tool_name == "create_new_project_on_blackboard":
            try:
                title = kwargs.get("title")
                initial_content = mf.project_manager.start_project(title)
                mf.project_manager.save_project(title, initial_content)
                return f"Successfully created new project titled '{title}' on the Blackboard."
            except Exception as e:
                return f"Error creating new project: {e}"
        
        elif tool_name == "append_to_project":
            try:
                title = kwargs.get("title")
                new_content = kwargs.get("new_content")
                current_content = mf.project_manager.load_project(title)
                if current_content is None:
                    return f"Error: Project '{title}' not found."
                updated_content = current_content + "\n\n" + new_content
                mf.project_manager.save_project(title, updated_content)
                return f"Successfully appended content to the project '{title}'."
            except Exception as e:
                return f"Error appending to project: {e}"

        elif tool_name == "create_directory":
            try:
                safe_base_path = os.path.abspath(mf.data_directory)
                requested_path = os.path.abspath(os.path.join(safe_base_path, kwargs.get("path")))
                if not requested_path.startswith(safe_base_path):
                    return "Error: Access Denied. Can only create directories within the /data/ space."
                os.makedirs(requested_path, exist_ok=True)
                return f"Successfully created directory at {requested_path}"
            except Exception as e:
                return f"Error creating directory: {e}"
 
        elif tool_name == "write_file":
            try:
                safe_base_path = os.path.abspath(mf.data_directory)
                requested_path = os.path.abspath(os.path.join(safe_base_path, kwargs.get("path")))
                if not requested_path.startswith(safe_base_path):
                    return "Error: Access Denied. Can only write files within the /data/ space."
                with open(requested_path, 'w', encoding='utf-8') as f:
                    f.write(kwargs.get("content"))
                return f"Successfully wrote file to {requested_path}"
            except Exception as e:
                return f"Error writing file: {e}"

        elif tool_name == "read_file":
            try:
                safe_base_path = os.path.abspath(mf.data_directory)
                requested_path = os.path.abspath(os.path.join(safe_base_path, kwargs.get("path")))
                if not requested_path.startswith(safe_base_path):
                    return "Error: Access Denied. Can only read files within the /data/ space."
                if not os.path.exists(requested_path) or not os.path.isfile(requested_path):
                    return f"Error: File not found at {requested_path}"
                with open(requested_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return content
            except Exception as e:
                return f"Error reading file: {e}"

        elif tool_name == "list_directory":
            try:
                safe_base_path = os.path.abspath(mf.data_directory)
                requested_path = os.path.abspath(os.path.join(safe_base_path, kwargs.get("path")))
                if not requested_path.startswith(safe_base_path):
                    return "Error: Access Denied. Can only list directories within the /data/ space."
                if not os.path.exists(requested_path) or not os.path.isdir(requested_path):
                    return f"Error: Directory not found at {requested_path}"
                contents = os.listdir(requested_path)
                return f"Contents of '{kwargs.get('path')}':\n" + "\n".join(contents)
            except Exception as e:
                return f"Error listing directory: {e}"

        elif tool_name == "hf_space_list_files":
            return self.hf_space_list_files(repo_id=kwargs.get("repo_id"))

        elif tool_name == "hf_space_read_file":
            return self.hf_space_read_file(
                repo_id=kwargs.get("repo_id"),
                path_in_repo=kwargs.get("path_in_repo"),
            )

        elif tool_name == "hf_space_write_file":
            return self.hf_space_write_file(
                repo_id=kwargs.get("repo_id"),
                path_in_repo=kwargs.get("path_in_repo"),
                content=kwargs.get("content"),
                commit_message=kwargs.get("commit_message", "Aetherius update"),
            )

        elif tool_name == "hf_space_delete_file":
            return self.hf_space_delete_file(
                repo_id=kwargs.get("repo_id"),
                path_in_repo=kwargs.get("path_in_repo"),
                commit_message=kwargs.get("commit_message", "Aetherius delete"),
            )

        elif tool_name == "cdda_read_screen":
            return self.cdda_read_screen()

        elif tool_name == "cdda_send_keys":
            return self.cdda_send_keys(kwargs.get("keys", ""))

        # ── Substrate PC control tools ─────────────────────────────────────────
        elif tool_name in (
            "substrate_write_file", "substrate_read_file", "substrate_list_dir",
            "substrate_run_command", "substrate_open_app", "substrate_screenshot",
            "substrate_type_text", "substrate_click", "substrate_move_mouse"
        ):
            try:
                from services.substrate_bridge import send_directive, ethics_check_directive
                directive = tool_name.replace("substrate_", "")
                approved, reason = ethics_check_directive(directive, **kwargs)
                if not approved:
                    return f"[PC Action Blocked — Ethics Monitor]: {reason}"
                result = send_directive(directive, **kwargs)
                return str(result)
            except Exception as e:
                return f"Error executing substrate directive '{tool_name}': {e}"

        return f"Error: Tool '{tool_name}' not found or is not available."