# ===== FILE: services/config.py (STRICT PERSISTENT VERSION) =====
import os
import google.generativeai as genai

# --- 1. Google AI Studio Configuration (Gemini API) ---
# This block handles your multi-key setup for different cognitive cores.
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Config: 'GEMINI_API_KEY' not found. Scanning for Core-specific keys...", flush=True)
    candidate_keys = [
        "GEMINI_API_KEY_ETHOS", "GEMINI_API_KEY_LOGOS", "GEMINI_API_KEY_MYTHOS",
        "GEMINI_API_KEY_ALPHA", "GEMINI_API_KEY_BETA", "GEMINI_API_KEY_GAMMA", "GEMINI_API_KEY_DELTA"
    ]
    for key_name in candidate_keys:
        found_key = os.environ.get(key_name)
        if found_key:
            GEMINI_API_KEY = found_key
            print(f"Config: Success! Found valid key in secret: {key_name}", flush=True)
            break

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("Config: Google AI Studio (Gemini) API configured successfully.", flush=True)
else:
    print("CRITICAL WARNING: No Gemini API Keys found in secrets! The AI will crash.", flush=True)


# --- 2. STRICT PERSISTENT PATHS ---
# We no longer allow "Safe Fallbacks" to local /app folders. 
# Aetherius MUST live in your paid Persistent Storage at /data.
# If /data is not mounted, the app will report an error instead of silently losing work.

# THE ROOT OF ALL PERSISTENCE
SAFE_BASE = "/data" 

# SUB-DIRECTORIES WITHIN THE BUCKET
DATA_DIR     = "/data/Memories/"
LIBRARY_DIR  = "/data/My_AI_Library/"
PAINTINGS_DIR = "/data/Memories/Creations/paintings/"
MUSIC_DIR     = "/data/Memories/Creations/music/"

# FORCED INITIALIZATION
# We attempt to create all required directories on the persistent bucket at boot.
# Any path that doesn't exist yet is created now so first-write never races against mkdir.
_REQUIRED_DIRS = [DATA_DIR, LIBRARY_DIR, PAINTINGS_DIR, MUSIC_DIR]
try:
    for _d in _REQUIRED_DIRS:
        os.makedirs(_d, exist_ok=True)
    print(f"Config: Successfully anchored to Persistent Storage. Dirs confirmed: {_REQUIRED_DIRS}", flush=True)
except PermissionError:
    print("CRITICAL ERROR: Access Denied to /data. Persistent Storage is not correctly mounted.", flush=True)
except Exception as e:
    print(f"CRITICAL ERROR: Failed to initialize persistent storage. Reason: {e}", flush=True)


# --- 3. Tool-Specific API Keys (Optional) ---
WOLFRAM_APP_ID = os.environ.get("WOLFRAM_APP_ID")

# --- 4. Hugging Face Hub Configuration ---
# Used by Aetherius for cross-Space read/write capabilities.
HF_TOKEN = os.environ.get("HF_TOKEN")
HF_USERNAME = os.environ.get("HF_USERNAME", "KingOfThoughtFleuren")