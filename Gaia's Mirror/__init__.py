# gaia_mirror/__init__.py

# This file marks the gaia_mirror directory as a Python package.

# Optionally, we can import core components to make them directly accessible
# from the 'gaia_mirror' package, simplifying imports in other parts of the application.
# For example, instead of 'from gaia_mirror.config import config', one could do
# 'from gaia_mirror import config'.

# However, for clarity and to avoid circular dependencies during initial startup
# or in complex projects, explicit imports are often preferred.
# For now, we will keep it minimal, just marking the package.

# You might eventually add package-level configurations, version information,
# or top-level API endpoints here.

__version__ = "0.1.0-alpha" # Initial version of Gaia's Mirror

import logging
# Basic logging configuration for the entire Gaia's Mirror package.
# This can be overridden by specific module configurations or the global config.py
logging.getLogger(__name__).addHandler(logging.NullHandler())
