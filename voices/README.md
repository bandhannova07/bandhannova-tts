# Voices Directory

This directory is intended to store reference audio files (.wav) for Voice Cloning (XTTS).

**Current Status:**
The system is currently configured to use **Edge TTS** (Neural Voices) by default, which provides high-quality human-like speech without needing reference audio files.

To use XTTS and Voice Cloning:
1. Install `TTS` package manually (requires heavy dependencies).
2. Uncomment the XTTS code in `tts_engine.py`.
3. Place `.wav` files here and update `config.py` to point to them.
