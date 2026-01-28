
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies required for TTS, SoundFile, etc.
RUN apt-get update && apt-get install -y \
    git \
    libsndfile1 \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage cache
COPY requirements.txt .

# Install Python dependencies
# XTTS (Coqui) requires specific versions sometimes, but we'll try from requirements
RUN pip install --no-cache-dir -r requirements.txt

# Verify Edge TTS installation (critical for human-like voices)
RUN python -m edge_tts --version || echo "WARNING: edge-tts not installed properly!"

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run the application with Gunicorn
CMD gunicorn --bind 0.0.0.0:${PORT:-5000} app:app
