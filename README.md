# TTS Service (Render Ready)

Text-to-Speech (TTS) service for Indian languages.

## Local Run

```bash
python app.py
```

Access: http://localhost:5000

## Render Deploy

Render service settings:

- **Root Directory:** `TTS Service`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`
- **Env Var:** `PYTHON_VERSION=3.12.0`

If you use the root-level `render.yaml`, this service is already configured.

## Model

**BandhanNova V1 TTS**

## Supported Languages

- 🇧🇩 Bengali (bn)
- 🇮🇳 Hindi (hi)
- 🇮🇳 Tamil (ta)
- 🇮🇳 Telugu (te)
- 🇬🇧 English (en)

## API Integration

### TTS API
```javascript
// Create a free API key
const keyResponse = await fetch('https://your-tts-service.onrender.com/api/keys/create', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ label: 'my-app' })
});
const { api_key } = await keyResponse.json();

// Generate speech from text
const response = await fetch('https://your-tts-service.onrender.com/api/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'X-API-Key': api_key },
  body: JSON.stringify({
    text: "আমি বাংলায় কথা বলতে পারি",
    language: "bn",
    speed: 1.0
  })
});
const audioBlob = await response.blob();
```


## Installation

### Prerequisites
- Python 3.12+
- ffmpeg (for audio processing)

### Install ffmpeg
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Project Structure

```
TTS Service/
├── app.py
├── tts_engine.py
├── audio_processor.py
├── config.py
├── templates/
│   └── index.html
├── static/
│   ├── css/style.css
│   └── js/app.js
└── output/
```

## Features

### TTS Features
- ✅ Natural human-like voice
- ✅ Speed control (0.5x - 2.0x)
- ✅ MP3 output format
- ✅ Download capability
- ✅ Waveform visualization

## Performance

**TTS:**
- Generation time: 2-3 seconds
- Audio quality: 22kHz MP3
- File size: ~20KB per sentence

## Troubleshooting

### TTS Issues
- **Error: No such file or directory** - Run `mkdir -p output cache models`
- **ffmpeg warnings** - Optional, app works without ffmpeg


## License

MIT License - Free to use and modify

---

**Made with ❤️ for Indian Languages**
