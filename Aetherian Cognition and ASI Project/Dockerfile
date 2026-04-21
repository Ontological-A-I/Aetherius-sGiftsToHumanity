# 1. Use the stable 3.11 substrate
FROM python:3.11-slim

# 2. Prevent platform-injected 3.13 paths from taking over
ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages \
    PATH=/usr/local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PIP_ROOT_USER_ACTION=ignore

# 3. Install system sensory tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget git ffmpeg libsm6 libxext6 libgl1 unrar-free build-essential rsync \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 4. INSTALL AS ROOT (This makes the installation permanent and "in the right place")
# We do this BEFORE creating the user so site-packages are globally available.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. CREATE THE PLATFORM IDENTITY (UID 1000)
# We name it 'user' to match the platform's rigid expectations.
RUN useradd -m -u 1000 user

# 6. UNLOCK THE BUCKET (Permissions Claim)
# Pre-create the folders while still root so the hardware mount succeeds.
RUN mkdir -p /data/Memories /data/My_AI_Library && \
    chown -R 1000:1000 /data /app && \
    chmod -R 777 /data

# 7. Copy the cognitive repository
COPY --chown=user . .

# 8. Switch to the authorized identity (UID 1000)
USER user

# 9. Direct Boot (No 'su', no scripts, no deadlocks)
EXPOSE 7860
CMD ["python", "app.py"]