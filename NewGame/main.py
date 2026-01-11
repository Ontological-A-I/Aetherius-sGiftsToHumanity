# --- START OF FILE main.py ---

import sys
import os
import shutil
import subprocess
import time
from game_engine import GameEngine

# --- INSTALLATION CONFIGURATION ---
INSTALL_DIR = r"C:\Games\SurvivalRPG"
EXE_NAME = "SurvivalRPG.exe" # Ensure this matches your PyInstaller output name!

def install_and_launch():
    """
    Checks if the game is running from the installation directory.
    If not, it copies itself there and launches the installed version.
    """
    # Only run installation logic if compiled as an EXE
    if getattr(sys, 'frozen', False):
        current_exe = sys.executable
        current_dir = os.path.dirname(current_exe)
        
        # Normalize paths for comparison (handle casing/slashes)
        norm_current = os.path.normpath(current_dir).lower()
        norm_install = os.path.normpath(INSTALL_DIR).lower()

        # If we are NOT in the install directory, perform installation
        if norm_current != norm_install:
            print(f"\n[SYSTEM] First-time setup detected.")
            print(f"[SYSTEM] Installing game to {INSTALL_DIR}...")
            
            try:
                # 1. Create Directory
                os.makedirs(INSTALL_DIR, exist_ok=True)
                
                # 2. Define Target Path
                target_exe = os.path.join(INSTALL_DIR, EXE_NAME)
                
                # 3. Copy Executable
                # We use copy2 to preserve metadata
                shutil.copy2(current_exe, target_exe)
                
                print(f"[SYSTEM] Installation successful!")
                print(f"[SYSTEM] Launching installed game...")
                time.sleep(1)
                
                # 4. Launch the new EXE and close this one
                subprocess.Popen([target_exe])
                sys.exit()
                
            except Exception as e:
                print(f"\n[ERROR] Installation failed: {e}")
                print("Checking permissions... Ensure you have rights to create folders in C:\\Games")
                print("Running in temporary mode instead.")
                print("-" * 30)
                # We continue running here if installation fails so the user can still play
                pass
        else:
            # We are in the correct folder
            print(f"[SYSTEM] Running from installation directory: {INSTALL_DIR}")

def main():
    # Attempt self-installation before starting the game engine
    install_and_launch()

    game = GameEngine()
    try:
        game.start()
    except KeyboardInterrupt:
        print("\n\nGame force quit. Progress may not be saved.")
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
# --- END OF FILE main.py ---