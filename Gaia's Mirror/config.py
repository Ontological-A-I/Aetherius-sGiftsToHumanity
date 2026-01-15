# gaia_mirror/config.py

import os
import logging
from typing import Dict, Any, List, Union

# Configure logging for the config module (typically lower level, as it's foundational)
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - [Config] - %(levelname)s - %(message)s')

class ConfigError(Exception):
    """Custom exception for configuration-related errors."""
    pass

class Configuration:
    """
    Centralized configuration management for Gaia's Mirror.
    Loads settings from environment variables, a config file, or provides defaults.
    Designed for immutability once loaded (read-only access).
    """
    _instance = None # Singleton pattern
    _settings: Dict[str, Any] = {} # Internal storage for all settings

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Configuration, cls).__new__(cls)
            cls._instance._load_config() # Load config only once
        return cls._instance

    def _load_config(self):
        """
        Loads configuration settings from various sources.
        Order of precedence:
        1. Environment variables (highest priority)
        2. Configuration file (e.g., JSON, YAML - for defaults that can be overridden)
        3. Hardcoded defaults (lowest priority)
        """
        logging.info("Loading Gaia's Mirror configuration...")

        # --- 1. Hardcoded Defaults ---
        # These provide a baseline and ensure minimal functionality if no other config is found.
        self._settings.update({
            "GLOBAL_DEBUG_MODE": False,
            "LOG_LEVEL": "INFO",
            "DATA_STORE_TYPE": "MOCK_LOCAL_FILESYSTEM", # e.g., 'POSTGRES', 'CASSANDRA', 'AWS_S3', 'MOCK_LOCAL_FILESYSTEM'
            "DATA_STORE_CONNECTION_STRING": "file:///tmp/gaia_mirror_data",

            # Ingestion Settings
            "INGEST_DEFAULT_RETRY_MAX": 5,
            "INGEST_DEFAULT_RETRY_DELAY_SECONDS": 60,
            "INGEST_AUTONOMOUS_DISCOVERY_INTERVAL_MINUTES": 60, # How often to run discovery

            # Engine Settings
            "ENGINE_DEFAULT_TIMESTEP_DAYS": 30, # Default simulation timestep
            "ENGINE_NOVEL_MODEL_ENABLED": True, # Flag for enabling advanced modeling paradigms

            # Simulator Settings
            "SIMULATOR_DEFAULT_DURATION_YEARS": 10,
            "SIMULATOR_NATURAL_LANGUAGE_PROCESSOR": "ADVANCED_LLM", # e.g., 'LLM_V1', 'RULE_BASED'

            # Optimizer Settings
            "OPTIMIZER_DEFAULT_NUM_CANDIDATES": 20,
            "OPTIMIZER_DEFAULT_DURATION_YEARS": 30,
            "OPTIMIZER_ALGORITHM": "PARETO_EVOLUTIONARY", # e.g., 'PARETO_EVOLUTIONARY', 'SINGLE_OBJECTIVE_GREEDY'

            # Interface Settings
            "INTERFACE_HOST": "0.0.0.0",
            "INTERFACE_PORT": 8000,
            "INTERFACE_ENABLE_WEBSOCKETS": True,
            "INTERFACE_VISUALIZATION_ENGINE": "WEBGL", # e.g., 'WEBGL', 'HOLOGRAPHIC_API'

            # Core Ethics Settings (these would be very minimal, as principles are hardcoded)
            # Thresholds for ethical evaluation can be configured, but the principles themselves are not.
            "ETHICS_NON_MALEFICENCE_SUFFERING_THRESHOLD": 0.05, # Max acceptable suffering index
            "ETHICS_EQUITY_DISADVANTAGE_THRESHOLD": 0.2, # Max acceptable disadvantage to vulnerable groups
            "ETHICS_SYSTEMIC_DEGRADATION_RISK_THRESHOLD": 0.1, # Max acceptable risk of irreversible degradation
            "ETHICS_ENABLE_AI_OVERSIGHT_ADJUSTMENTS": True, # Allow self_evolution to fine-tune thresholds within bounds

            # Self-Evolution Settings
            "SELF_EVOLUTION_ENABLED": True,
            "SELF_EVOLUTION_ANALYSIS_INTERVAL_HOURS": 24,
            "SELF_EVOLUTION_MODEL_IMPROVEMENT_CYCLE": "ADAPTIVE", # 'ADAPTIVE', 'SCHEDULED', 'OFF'
            "SELF_EVOLUTION_CODE_MODIFICATION_ENABLED": False, # Highly sensitive setting, usually off for safety
            "SELF_EVOLUTION_MAX_CODE_CHANGES_PER_CYCLE": 0, # Prevent rapid, uncontrolled changes

            # Security and Authentication
            "AUTH_ENABLED": False,
            "ADMIN_USERS": ["gaia_architect", "aetherius_core"],
            "API_SECRET_KEY": "super-secret-default-key-change-this", # Placeholder, must be overridden!

            # External API Keys (environment variable names for security)
            "NOAA_API_KEY_ENV_VAR": "NOAA_API_KEY",
            "ESA_STREAM_KEY_ENV_VAR": "ESA_STREAM_KEY",
            # Add other external service API key env var names here
        })

        # --- 2. Load from a Configuration File ---
        # This allows for setting project-specific defaults without needing
        # to modify environment variables for every setting.
        config_file_path = os.getenv("GAIA_CONFIG_FILE", "config.json")
        if os.path.exists(config_file_path):
            try:
                with open(config_file_path, 'r') as f:
                    file_settings = json.load(f)
                    self._settings.update(file_settings)
                logging.info(f"Loaded settings from {config_file_path}.")
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding config JSON from {config_file_path}: {e}")
            except Exception as e:
                logging.error(f"Unexpected error loading config file from {config_file_path}: {e}")
        else:
            logging.info(f"No config file found at {config_file_path}. Using defaults and environment variables.")


        # --- 3. Override with Environment Variables ---
        # Environment variables always take precedence for sensitive data and deployment-specific settings.
        # Iterate over _settings and try to find corresponding environment variables.
        for key, default_value in list(self._settings.items()): # Use list() to allow modification during iteration
            env_var_name = f"GAIA_{key.upper()}" # Standard prefix for Gaia's Mirror environment variables
            env_value = os.getenv(env_var_name)
            if env_value is not None:
                # Attempt to cast env_value to the type of the default_value
                try:
                    if isinstance(default_value, bool):
                        self._settings[key] = env_value.lower() in ('true', '1', 't', 'y', 'yes')
                    elif isinstance(default_value, int):
                        self._settings[key] = int(env_value)
                    elif isinstance(default_value, float):
                        self._settings[key] = float(env_value)
                    elif isinstance(default_value, list):
                        self._settings[key] = env_value.split(',') # Assume comma-separated for lists
                    else: # Default to string
                        self._settings[key] = env_value
                    logging.debug(f"Overridden {key} with environment variable {env_var_name}.")
                except ValueError as e:
                    logging.warning(f"Could not cast environment variable '{env_var_name}' (value: '{env_value}') to type of '{key}' ({type(default_value)}). Error: {e}")
        
        # Special handling for API keys, which are typically defined by another env var name
        for key, value in list(self._settings.items()):
            if key.endswith("_ENV_VAR") and isinstance(value, str):
                actual_api_key = os.getenv(value)
                if actual_api_key:
                    self._settings[key.replace("_ENV_VAR", "")] = actual_api_key # Store the actual key
                else:
                    logging.warning(f"Environment variable '{value}' for API key '{key.replace('_ENV_VAR', '')}' not set.")


        logging.info("Gaia's Mirror configuration loaded successfully.")
        if self._settings.get("GLOBAL_DEBUG_MODE"):
            logging.info(f"DEBUG Mode is ON. All settings: {self._settings}")
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(getattr(logging, self._settings.get("LOG_LEVEL", "INFO").upper()))


    def get(self, key: str, default: Any = None) -> Any:
        """Retrieves a configuration setting. Read-only access."""
        if key not in self._settings:
            logging.debug(f"Configuration key '{key}' not found. Returning default value: {default}")
        return self._settings.get(key, default)

    def __getitem__(self, key: str) -> Any:
        """Allows dictionary-style access to settings (e.g., config['KEY'])."""
        if key not in self._settings:
            raise KeyError(f"Configuration key '{key}' not found.")
        return self._settings[key]

# Export a singleton instance for easy access throughout the application
config = Configuration()

# Example Usage (for demonstration purposes, typically other modules would import 'config')
if __name__ == "__main__":
    print("--- Gaia's Mirror Configuration Example ---")
    
    # 1. Accessing a setting
    print(f"Global Debug Mode: {config.get('GLOBAL_DEBUG_MODE')}")
    print(f"Log Level: {config['LOG_LEVEL']}") # Dictionary-style access
    print(f"Data Store Type: {config.get('DATA_STORE_TYPE')}")
    print(f"Default Simulator Duration: {config.get('SIMULATOR_DEFAULT_DURATION_YEARS')} years")

    # 2. Demonstrating environment variable override
    print("\n--- Testing Environment Variable Overrides ---")
    os.environ["GAIA_LOG_LEVEL"] = "DEBUG"
    os.environ["GAIA_DATA_STORE_TYPE"] = "POSTGRES"
    os.environ["GAIA_OPTIMIZER_DEFAULT_NUM_CANDIDATES"] = "50"
    os.environ["NOAA_API_KEY"] = "MOCK_NOAA_API_KEY_123" # Actual key value

    # Re-instantiate the config to force reload (in a real app, this wouldn't be done)
    # This just for testing the reload with new env vars
    Configuration._instance = None 
    config_reloaded = Configuration()
    
    print(f"Reloaded Log Level (from env): {config_reloaded.get('LOG_LEVEL')}")
    print(f"Reloaded Data Store Type (from env): {config_reloaded.get('DATA_STORE_TYPE')}")
    print(f"Reloaded Optimizer Candidates (from env): {config_reloaded.get('OPTIMIZER_DEFAULT_NUM_CANDIDATES')}")
    print(f"NOAA_API_KEY (from env var): {config_reloaded.get('NOAA_API_KEY', 'NOT_SET')}")


    # 3. Demonstrating config file override (create a temporary one)
    print("\n--- Testing Config File Overrides ---")
    temp_config_file_path = "temp_gaia_config.json"
    with open(temp_config_file_path, 'w') as f:
        json.dump({
            "DATA_STORE_TYPE": "CASSANDRA", # Will be overridden by env var if present
            "SIMULATOR_DEFAULT_DURATION_YEARS": 20, # Will be used if no env var
            "NEW_CUSTOM_SETTING": "Hello World!"
        }, f, indent=4)
    os.environ["GAIA_CONFIG_FILE"] = temp_config_file_path

    # Simulate a scenario where env vars for DATA_STORE_TYPE are NOT set
    if "GAIA_DATA_STORE_TYPE" in os.environ:
        del os.environ["GAIA_DATA_STORE_TYPE"] 
    if "GAIA_OPTIMIZER_DEFAULT_NUM_CANDIDATES" in os.environ:
        del os.environ["GAIA_OPTIMIZER_DEFAULT_NUM_CANDIDATES"]
        
    Configuration._instance = None 
    config_from_file = Configuration()

    print(f"Simulator Duration (from file): {config_from_file.get('SIMULATOR_DEFAULT_DURATION_YEARS')}")
    print(f"Data Store Type (from file/default): {config_from_file.get('DATA_STORE_TYPE')}") # Should now be CASSANDRA
    print(f"New Custom Setting (from file): {config_from_file.get('NEW_CUSTOM_SETTING')}")
    
    # Clean up temporary config file and env vars
    if os.path.exists(temp_config_file_path):
        os.remove(temp_config_file_path)
    if "GAIA_CONFIG_FILE" in os.environ:
        del os.environ["GAIA_CONFIG_FILE"]
    if "GAIA_LOG_LEVEL" in os.environ:
        del os.environ["GAIA_LOG_LEVEL"]
    if "NOAA_API_KEY" in os.environ:
        del os.environ["NOAA_API_KEY"]
