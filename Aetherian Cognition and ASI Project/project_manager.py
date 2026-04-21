# ===== FILE: services/project_manager.py (NEW FILE) =====
import os
import re
from datetime import datetime

class ProjectManager:
    def __init__(self, data_directory):
        """
        Initializes the manager for persistent academic and scientific projects.
        """
        self.base_directory = data_directory
        self.projects_dir = os.path.join(self.base_directory, "Projects")
        os.makedirs(self.projects_dir, exist_ok=True)
        print("Project Manager says: Persistent workspace is online.", flush=True)

    def _sanitize_filename(self, name: str) -> str:
        """
        Sanitizes a user-provided project name into a safe filename.
        """
        # Remove invalid characters
        name = re.sub(r'[\\/*?:"<>|]', "", name)
        # Replace spaces with underscores
        name = name.replace(" ", "_")
        return name

    def list_projects(self) -> list[str]:
        """
        Lists all existing project files in the projects directory.
        """
        try:
            files = [f for f in os.listdir(self.projects_dir) if f.endswith(".txt")]
            # Return the name without the .txt extension
            project_names = [os.path.splitext(f)[0].replace("_", " ") for f in files]
            project_names.sort()
            return project_names
        except Exception as e:
            print(f"Project Manager ERROR: Could not list projects. Reason: {e}", flush=True)
            return []

    def start_project(self, project_name: str) -> str:
        """
        Returns initial template content for a new project.
        Does not save anything to disk until save_project is called.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        initial_content = (
            f"# PROJECT: {project_name}\n"
            f"# STARTED: {timestamp}\n"
            f"# AETHERIUS'S WORKSPACE\n"
            f"--------------------------------------------------\n\n"
        )
        return initial_content

    def save_project(self, project_name: str, content: str):
        """
        Saves the content of a project to a text file.
        """
        if not project_name or not project_name.strip():
            print("Project Manager WARNING: Save attempt with empty project name.", flush=True)
            return

        safe_filename = self._sanitize_filename(project_name) + ".txt"
        filepath = os.path.join(self.projects_dir, safe_filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Project Manager: Successfully saved project '{project_name}' to {filepath}", flush=True)
        except Exception as e:
            print(f"Project Manager ERROR: Could not save project '{project_name}'. Reason: {e}", flush=True)

    def load_project(self, project_name: str) -> str | None:
        """
        Loads the content of a project from a text file.
        Returns None if the project does not exist.
        """
        safe_filename = self._sanitize_filename(project_name) + ".txt"
        filepath = os.path.join(self.projects_dir, safe_filename)

        if not os.path.exists(filepath):
            print(f"Project Manager WARNING: Attempted to load non-existent project '{project_name}'.", flush=True)
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"Project Manager: Successfully loaded project '{project_name}'.", flush=True)
            return content
        except Exception as e:
            print(f"Project Manager ERROR: Could not load project '{project_name}'. Reason: {e}", flush=True)
            return f"// ERROR: Could not load project file. Reason: {e} //"