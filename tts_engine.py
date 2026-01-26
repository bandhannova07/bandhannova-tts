"""
Alternative TTS Engine using gTTS and pyttsx3
Compatible with Python 3.12+
"""
import os
import logging
from gtts import gTTS
import pyttsx3
from config import Config

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
        
        # Method 1: Check CLI
        self.edge_tts_path = shutil.which("edge-tts")
        
        # Method 2: Check in current python environment
        if not self.edge_tts_path:
            # Try to see if we can run it via python -m edge_tts
            try:
                import subprocess
                subprocess.run([sys.executable, "-m", "edge_tts", "--version"], capture_output=True, check=True)
                self.edge_tts_via_module = True
                self.edge_tts_available = True
                logger.info(f"Edge TTS (Neural) available via module: {sys.executable} -m edge_tts")
            except Exception:
                self.edge_tts_via_module = False
                self.edge_tts_available = False
                logger.warning("edge-tts not found in PATH or as module. Human-like voices will not work.")
        else:
            self.edge_tts_via_module = False
            self.edge_tts_available = True
            logger.info(f"Edge TTS (Neural) available via CLI: {self.edge_tts_path}")

        # Initialize pyttsx3 for offline TTS
        try:
            self.offline_engine = pyttsx3.init()
            self.offline_available = True
            logger.info("Offline TTS engine initialized")
        except Exception as e:
            logger.warning(f"Offline TTS not available: {e}")
            self.offline_available = False
        
        logger.info("TTS Engine initialized successfully!")
    
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
        
        if len(text) > self.config.MAX_TEXT_LENGTH:
            raise ValueError(f"Text too long. Maximum {self.config.MAX_TEXT_LENGTH} characters allowed")
        
        # 0. Handle in-memory request setup
        if return_bytes:
             # XTTS currently requires file path, so we might need temp file
             pass
        
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
            # XTTS usually works with files. 
            # If return_bytes requested, we'll write to temp file then read bytes
            try:
                temp_path = output_path
                if return_bytes:
                    import tempfile
                    fd, temp_path = tempfile.mkstemp(suffix=".wav")
                    os.close(fd)
                
                logger.info(f"Cloning voice (XTTS) for {language} using {os.path.basename(speaker_wav)}")
                self.xtts.tts_to_file(
                    text=text,
                    file_path=temp_path,
                    speaker_wav=speaker_wav,
                    language=language,
                    speed=speed,
                    split_sentences=True
                )
                logger.info(f"XTTS cloning successful: {temp_path}")
                
                if return_bytes:
                    with open(temp_path, "rb") as f:
                        audio_bytes = f.read()
                    os.remove(temp_path)
                    return audio_bytes, "audio/wav"
                
                return temp_path
            except Exception as e:
                logger.error(f"XTTS generation failed: {e}. Falling back...")
        
        # 2. Try Edge TTS (Neural Voices)
        if voice_id and self.edge_tts_available:
            try:
                import subprocess
                import sys
                logger.info(f"Generating human-like speech (Edge TTS) for {language} with voice {voice_id}")
                
                # Calculate rate string (e.g. +10% or -10%)
                rate_pct = int((speed - 1.0) * 100)
                rate_str = f"{'+' if rate_pct >= 0 else ''}{rate_pct}%"
                
                cmd = []
                if self.edge_tts_via_module:
                    cmd = [sys.executable, "-m", "edge_tts"]
                else:
                    cmd = [self.edge_tts_path]
                    
                cmd.extend([
                    "--text", text,
                    "--voice", voice_id,
                    "--rate", rate_str
                ])
                
                if return_bytes:
                    # No --write-media, capture stdout
                    logger.info(f"Running command (stdout): {' '.join(cmd)}")
                    result = subprocess.run(cmd, capture_output=True, check=True)
                    return result.stdout, "audio/mpeg"
                else:
                    cmd.extend(["--write-media", output_path])
                    logger.info(f"Running command: {' '.join(cmd)}")
                    subprocess.run(cmd, check=True)
                    logger.info(f"Edge TTS generation successful: {output_path}")
                    return output_path
                    
            except Exception as e:
                logger.error(f"Edge TTS generation failed: {e}. Falling back to gTTS...")
        
        # Fallback to gTTS (Robotic/Standard)
        try:
            logger.info(f"Generating standard speech (gTTS) for language: {language}")
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
