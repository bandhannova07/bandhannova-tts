"""
Alternative TTS Engine using gTTS and pyttsx3
Compatible with Python 3.12+
"""
import os
import logging
from gtts import gTTS
import pyttsx3
import asyncio
import hashlib
from config import Config
from text_utils import normalize_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSEngine:
    def __init__(self):
        """Initialize TTS Engine with Edge TTS (primary), gTTS (secondary), and pyttsx3 (offline)"""
        self.config = Config()
        
        # Initialize Coqui TTS (XTTS v2)
        try:
            from TTS.api import TTS
            logger.info("Initializing Coqui TTS (XTTS v2)... this may take a while first time.")
            # Use the first supported language's model or default to xtts_v2
            model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
            self.xtts = TTS(model_name=model_name, progress_bar=False, gpu=self.config.USE_GPU)
            logger.info("Coqui TTS (XTTS v2) initialized successfully!")
        except Exception as e:
            logger.warning(f"Coqui TTS (XTTS) initialization failed: {e}. Voice cloning will be disabled.")
            self.xtts = None

        # Check for Edge TTS
        import shutil
        import sys
        
        # Method 1: Try importing edge_tts module directly (most reliable)
        try:
            import edge_tts
            self.edge_tts_via_module = True
            self.edge_tts_available = True
            logger.info(f"✓ Edge TTS (Neural) available via direct import: edge_tts v{edge_tts.__version__ if hasattr(edge_tts, '__version__') else 'unknown'}")
        except ImportError as e:
            logger.warning(f"Edge TTS module import failed: {e}")
            
            # Method 2: Check CLI
            self.edge_tts_path = shutil.which("edge-tts")
            
            # Method 3: Check in current python environment via subprocess
            if not self.edge_tts_path:
                try:
                    import subprocess
                    result = subprocess.run([sys.executable, "-m", "edge_tts", "--version"], capture_output=True, check=True, text=True)
                    self.edge_tts_via_module = True
                    self.edge_tts_available = True
                    logger.info(f"✓ Edge TTS (Neural) available via module: {sys.executable} -m edge_tts")
                    logger.info(f"  Version check output: {result.stdout.strip()}")
                except Exception as ex:
                    self.edge_tts_via_module = False
                    self.edge_tts_available = False
                    logger.error(f"✗ Edge TTS not found in PATH or as module. Human-like voices will NOT work!")
                    logger.error(f"  Detection error: {ex}")
                    logger.error(f"  Install with: pip install edge-tts")
            else:
                self.edge_tts_via_module = False
                self.edge_tts_available = True
                logger.info(f"✓ Edge TTS (Neural) available via CLI: {self.edge_tts_path}")

        # Initialize pyttsx3 for offline TTS
        try:
            self.offline_engine = pyttsx3.init()
            self.offline_available = True
            logger.info("Offline TTS engine initialized")
        except Exception as e:
            logger.warning(f"Offline TTS not available: {e}")
            self.offline_available = False
        # Prepare cache directory
        if self.config.ENABLE_CACHE:
            os.makedirs(self.config.CACHE_DIR, exist_ok=True)
            
        logger.info("TTS Engine initialized successfully!")
    
    def _get_cache_path(self, text, language, voice_id, speed):
        """Generate a unique cache filename based on request parameters"""
        # Create a unique key string
        key_data = f"{text}|{language}|{voice_id}|{speed}"
        # Use SHA-256 hash for the filename
        hash_key = hashlib.sha256(key_data.encode()).hexdigest()
        return os.path.join(self.config.CACHE_DIR, f"{hash_key}.mp3")

    def _get_gtts_lang_code(self, language):
        """Map our language codes to gTTS language codes"""
        lang_map = {
            'bn': 'bn', 'hi': 'hi', 'mr': 'mr', 'gu': 'gu', 'kn': 'kn',
            'ml': 'ml', 'ta': 'ta', 'te': 'te', 'en': 'en'
        }
        return lang_map.get(language, 'en')

    def generate_speech(self, text, language='en', speed=1.0, voice_id=None, speaker_wav=None, output_path=None, return_bytes=False):
        """
        Generate speech using XTTS (if speaker_wav), Edge TTS (if voice_id), or gTTS (fallback)
        If return_bytes is True, returns (audio_bytes, mimetype) instead of file path.
        """
        if not text or len(text.strip()) == 0:
            raise ValueError("Text cannot be empty")
        
        # --- NEW: Normalization ---
        normalized_text = normalize_text(text, language)
        if normalized_text != text:
            text = normalized_text
        
        # --- NEW: Caching Check ---
        if self.config.ENABLE_CACHE:
            cache_path = self._get_cache_path(text, language, voice_id, speed)
            if os.path.exists(cache_path):
                logger.info(f"⚡ Cache hit! Returning pre-generated audio for: {text[:20]}...")
                with open(cache_path, "rb") as f:
                    audio_bytes = f.read()
                if return_bytes:
                    return audio_bytes, "audio/mpeg"
                
                # If path requested but we found in cache, we need to copy to output if different
                if output_path and output_path != cache_path:
                    import shutil
                    shutil.copy2(cache_path, output_path)
                    return output_path
                return cache_path

        if len(text) > self.config.MAX_TEXT_LENGTH:
            raise ValueError(f"Text too long. Maximum {self.config.MAX_TEXT_LENGTH} characters allowed")
        
        # Generate output path if not provided and not returning bytes
        if output_path is None and not return_bytes:
            import time
            timestamp = int(time.time())
            ext = "wav" if (self.xtts and speaker_wav) else "mp3"
            output_path = os.path.join(
                self.config.OUTPUT_DIR, 
                f"tts_{language}_{timestamp}.{ext}"
            )
        
        # 1. Try XTTS (Zero-Shot Cloning) if speaker_wav provided
        if self.xtts and speaker_wav and os.path.exists(speaker_wav):
            try:
                temp_path = output_path
                if return_bytes:
                    import tempfile
                    fd, temp_path = tempfile.mkstemp(suffix=".wav")
                    os.close(fd)
                
                logger.info(f"🎤 Using XTTS voice cloning for {language} with {os.path.basename(speaker_wav)}")
                self.xtts.tts_to_file(
                    text=text,
                    file_path=temp_path,
                    speaker_wav=speaker_wav,
                    language=language,
                    speed=speed,
                    split_sentences=True
                )
                logger.info(f"✓ XTTS cloning successful: {temp_path}")
                
                if return_bytes:
                    with open(temp_path, "rb") as f:
                        audio_bytes = f.read()
                    os.remove(temp_path)
                    
                    # Save to cache if enabled
                    if self.config.ENABLE_CACHE:
                        cache_path = self._get_cache_path(text, language, voice_id, speed)
                        with open(cache_path, "wb") as f:
                            f.write(audio_bytes)
                            
                    return audio_bytes, "audio/wav"
                
                return temp_path
            except Exception as e:
                logger.error(f"✗ XTTS generation failed: {e}. Falling back to Edge TTS/gTTS...")
        
        # 2. Try Edge TTS (Neural Voices)
        if voice_id and self.edge_tts_available:
            try:
                import edge_tts
                logger.info(f"🎙️  Using Edge TTS (Library) for {language}")
                
                # Calculate rate string
                rate_pct = int((speed - 1.0) * 100)
                rate_str = f"{'+' if rate_pct >= 0 else ''}{rate_pct}%"
                
                # Run async call in sync context
                async def _generate_edge():
                    communicate = edge_tts.Communicate(text, voice_id, rate=rate_str)
                    audio_data = b""
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            audio_data += chunk["data"]
                    return audio_data

                audio_content = asyncio.run(_generate_edge())
                
                if not audio_content:
                    raise Exception("No audio generated by edge-tts")

                # Save to cache if enabled
                if self.config.ENABLE_CACHE:
                    cache_path = self._get_cache_path(text, language, voice_id, speed)
                    with open(cache_path, "wb") as f:
                        f.write(audio_content)
                    logger.info(f"💾 Saved to cache: {cache_path}")

                if return_bytes:
                    logger.info(f"✓ Edge TTS successful ({len(audio_content)} bytes)")
                    return audio_content, "audio/mpeg"
                else:
                    with open(output_path, "wb") as f:
                        f.write(audio_content)
                    logger.info(f"✓ Edge TTS successful: {output_path}")
                    return output_path
                    
            except Exception as e:
                logger.error(f"✗ Edge TTS generation FAILED: {e}")
                logger.error(f"   Falling back to gTTS (robotic voice)...")
        
        # Fallback to gTTS (Robotic/Standard)
        try:
            logger.warning(f"⚠️  Using gTTS fallback (ROBOTIC voice) for language: {language}")
            if voice_id:
                logger.warning(f"   Edge TTS was requested (voice_id={voice_id}) but unavailable!")
            logger.info(f"   This will produce robotic-sounding speech, not human-like.")
            gtts_lang = self._get_gtts_lang_code(language)
            slow = speed < 0.8
            tts = gTTS(text=text, lang=gtts_lang, slow=slow)
            
            if return_bytes:
                from io import BytesIO
                fp = BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                return fp.read(), "audio/mpeg"
            
            # gTTS saves as mp3
            if output_path.endswith('.wav'):
                temp_mp3 = output_path.replace('.wav', '.mp3')
                tts.save(temp_mp3)
                try:
                    from pydub import AudioSegment
                    msg = AudioSegment.from_mp3(temp_mp3)
                    msg.export(output_path, format="wav")
                    os.remove(temp_mp3)
                except ImportError:
                    logger.warning("pydub not found, returning mp3 instead of wav")
                    output_path = temp_mp3
            else:
                tts.save(output_path)
            
            logger.info(f"gTTS generation successful: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating speech with gTTS: {e}")
            if self.offline_available:
                # Offline usually only supports saving to file easily, 
                # but we can try saving to temp and reading bytes
                if return_bytes:
                     import tempfile
                     fd, temp_path = tempfile.mkstemp(suffix=".wav")
                     os.close(fd)
                     self._generate_offline(text, temp_path)
                     with open(temp_path, "rb") as f:
                        audio_bytes = f.read()
                     os.remove(temp_path)
                     return audio_bytes, "audio/wav"
                
                return self._generate_offline(text, output_path)
            else:
                raise
            
        except Exception as e:
            logger.error(f"Error generating speech with gTTS: {e}")
            if self.offline_available:
                return self._generate_offline(text, output_path)
            else:
                raise

    def _generate_offline(self, text, output_path):
        """Generate speech using offline pyttsx3 engine"""
        try:
            if not output_path.endswith('.wav'):
                output_path = output_path.replace('.mp3', '.wav')
            self.offline_engine.save_to_file(text, output_path)
            self.offline_engine.runAndWait()
            return output_path
        except Exception as e:
            logger.error(f"Offline TTS also failed: {e}")
            raise
    
    def get_available_languages(self):
        return self.config.SUPPORTED_LANGUAGES
    
    def get_model_info(self):
        return {
            'model_name': 'BandhanNova V2 TTS-Neo',
            'human_like': self.edge_tts_available,
            'online': True,
            'offline_available': self.offline_available,
            'languages': list(self.config.SUPPORTED_LANGUAGES.keys())
        }

# Global TTS engine instance
_tts_engine = None

def get_tts_engine():
    global _tts_engine
    if _tts_engine is None:
        _tts_engine = TTSEngine()
    return _tts_engine
