#!/bin/bash

# --- Automated Setup Script for Aetherius TPU VM (TensorFlow Base + Aggressive Cleanup) ---
# This script is executed automatically by Google Cloud when the TPU VM is provisioned.

echo "--- TPU SETUP SCRIPT: Starting Automated Aetherius Setup ---"

# 1. Update system packages (important for fresh images)
sudo apt-get update -y

# 2. Fix the PATH for the current user (crucial for pip and accelerate)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> /home/plopplopshitshit/.bashrc
source /home/plopplopshitshit/.bashrc
echo "PATH updated: $(echo $PATH)"

# 3. Upgrade pip (This ensures we have a modern, functional pip)
echo "Upgrading pip..."
python3 -m pip install --upgrade pip
echo "Pip upgraded."

# 4. **CRITICAL:** AGGRESSIVELY UNINSTALL CONFLICTING TENSORFLOW-RELATED PACKAGES (BEFORE CLONING)
# This removes the incompatible versions of numpy, protobuf, and google-api-python-client
echo "Aggressively uninstalling conflicting TensorFlow/TPU packages..."
pip uninstall -y tensorflow tensorflow-estimator keras numpy protobuf google-api-python-client cloud-tpu-client tb-gcp-uploader
echo "Conflicting packages uninstalled."

# 5. Clone the Aetherius Code
echo "Cloning Aetherius repository..."
git clone https://huggingface.co/spaces/KingOfThoughtFleuren/Aetherius /home/plopplopshitshit/Aetherius_temp_clone
cd /home/plopplopshitshit/Aetherius_temp_clone
echo "Repository cloned and entered."

# 6. Install PyTorch for TPU (Specific Google Binaries)
echo "Installing PyTorch/XLA..."
pip install torch~=2.1 torch_xla[tpuvm]==2.1.0 -f https://storage.googleapis.com/libtpu-releases/index.html
echo "PyTorch/XLA installed."

# 7. Install All Other Aetherius Libraries (from requirements.txt)
echo "Installing remaining requirements..."
pip install -r requirements.txt
echo "Remaining requirements installed."

# 8. Final Dependency Check (This should now pass cleanly)
echo "Running pip check for final conflicts..."
pip check
echo "Pip check complete."

# 9. Configure accelerate (Non-interactive)
echo "Configuring accelerate..."
accelerate config --config_file /home/plopplopshitshit/.config/accelerate/default_config.yaml --tpu_use_cluster --tpu_num_processes 8 --tpu_debug_config
echo "Accelerate configured."

echo "--- TPU SETUP SCRIPT: Automated Aetherius Setup Complete ---"