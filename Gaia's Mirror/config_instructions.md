Explanation and Key Design Decisions for config.py:
Singleton Pattern (_instance = None, __new__):
Ensures that there is only one instance of the Configuration class throughout the application's lifecycle. This is crucial for consistent access to global settings.
The configuration is loaded only once upon the first instantiation.
Tiered Loading Mechanism (_load_config):
Hardcoded Defaults (Lowest Priority): Provides sensible fallback values for all settings. These are built-in and always available.
Configuration File (config.json): Allows administrators or developers to define project-wide defaults that override the hardcoded values. The path to this file can itself be an environment variable (GAIA_CONFIG_FILE).
Environment Variables (Highest Priority): Designed for deployment-specific and sensitive settings (like API keys). Any setting found as an environment variable (prefixed with GAIA_) will override values from both the config file and hardcoded defaults. This is a best practice for secure and flexible deployments.
Type Casting: Attempts to cast environment variable strings to the appropriate type (boolean, int, float, list) based on the type of the default value.
API Key Management:
Instead of directly storing API keys in the config file, it stores the name of the environment variable where the actual API key can be found (e.g., NOAA_API_KEY_ENV_VAR: "NOAA_API_KEY"). This promotes security by keeping sensitive credentials out of code and config files, relying on the operating system's environment.
Read-Only Access (get, __getitem__):
Once loaded, the configuration settings are intended to be read-only. This prevents accidental modification of global settings during runtime.
Provides both .get() method (safer, returns None or default if key not found) and dictionary-style [] access (raises KeyError if key not found).
Logging Integration:
The LOG_LEVEL setting directly influences the Python logging module's level, allowing dynamic control over verbosity.
GLOBAL_DEBUG_MODE acts as an overarching toggle, automatically setting log levels to DEBUG if enabled.
Ethical Thresholds:
ETHICS_NON_MALEFICENCE_SUFFERING_THRESHOLD, etc.: These parameters allow for tuning the sensitivity of the ethical guardrails within core_ethics.py. The fundamental principles remain immutable, but the exact thresholds for what constitutes "too much harm" or "too much inequality" might need to be fine-tuned. This also provides a hook for self_evolution.py to potentially adjust these within defined safe bounds.
config = Configuration() (Singleton Export):
The module provides a ready-to-use singleton instance named config. Other modules can simply from gaia_mirror.config import config to access all settings.
This config.py provides the robust, centralized, and secure configuration management that a project of "Gaia's Mirror's" scale demands. It ensures that the framework can be deployed, customized, and maintained with clarity and control.
