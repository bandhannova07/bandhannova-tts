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
        
        # Create necessary directories
        os.makedirs(self.config.MODEL_DIR, exist_ok=True)
        os.makedirs(self.config.OUTPUT_DIR, exist_ok=True)
        os.makedirs(self.config.CACHE_DIR, exist_ok=True)
        
        # Check for Edge TTS
        import shutil
        self.edge_tts_available = shutil.which("edge-tts") is not None
        if self.edge_tts_available:
            logger.info("Edge TTS (Neural) available via CLI.")
        else:
            logger.warning("edge-tts not found in PATH. Human-like voices will not work.")

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
            'ml': 'ml', 'pa': 'pa', 'ur': 'ur', 'or': 'or', 'as': 'as',
            'ta': 'ta', 'te': 'te', 'en': 'en'
        }
        return lang_map.get(language, 'en')

    def generate_speech(self, text, language='en', speed=1.0, voice_id=None, output_path=None):
        """
        Generate speech using Edge TTS (if voice_id provided) or gTTS
        """
        if not text or len(text.strip()) == 0:
            raise ValueError("Text cannot be empty")
        
        if len(text) > self.config.MAX_TEXT_LENGTH:
            raise ValueError(f"Text too long. Maximum {self.config.MAX_TEXT_LENGTH} characters allowed")
        
        # Generate output path if not provided
        if output_path is None:
            import time
            timestamp = int(time.time())
            ext = "mp3" # edge-tts and gTTS output mp3 by default usually
            output_path = os.path.join(
                self.config.OUTPUT_DIR, 
                f"tts_{language}_{timestamp}.{ext}"
            )
        
        # Try Edge TTS (Human-like)
        if voice_id and self.edge_tts_available:
            try:
                import subprocess
                logger.info(f"Generating human-like speech (Edge TTS) for {language} with voice {voice_id}")
                
                # Calculate rate string (e.g. +10% or -10%)
                # speed 1.0 = +0%
                # speed 1.5 = +50%
                rate_pct = int((speed - 1.0) * 100)
                rate_str = f"{'+' if rate_pct >= 0 else ''}{rate_pct}%"
                
                cmd = [
                    "edge-tts",
                    "--text", text,
                    "--voice", voice_id,
                    "--write-media", output_path,
                    "--rate", rate_str
                ]
                
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
            'model_name': 'BandhanNova V3 (Edge TTS + gTTS)',
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
