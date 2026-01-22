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
        """Initialize TTS Engine with gTTS for online and pyttsx3 for offline"""
        self.config = Config()
        
        # Create necessary directories
        os.makedirs(self.config.MODEL_DIR, exist_ok=True)
        os.makedirs(self.config.OUTPUT_DIR, exist_ok=True)
        os.makedirs(self.config.CACHE_DIR, exist_ok=True)
        
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
            'bn': 'bn',  # Bengali
            'hi': 'hi',  # Hindi
            'mr': 'mr',  # Marathi
            'gu': 'gu',  # Gujarati
            'kn': 'kn',  # Kannada
            'ml': 'ml',  # Malayalam
            'pa': 'pa',  # Punjabi
            'ur': 'ur',  # Urdu
            'or': 'or',  # Odia
            'as': 'as',  # Assamese
            'ta': 'ta',  # Tamil
            'te': 'te',  # Telugu
            'en': 'en'   # English
        }
        return lang_map.get(language, 'en')
    
    def generate_speech(self, text, language='en', speed=1.0, output_path=None):
        """
        Generate speech from text using gTTS
        
        Args:
            text (str): Text to convert to speech
            language (str): Language code (bn, hi, ta, te, en)
            speed (float): Speech speed multiplier (gTTS has limited speed control)
            output_path (str): Path to save audio file
            
        Returns:
            str: Path to generated audio file
        """
        if not text or len(text.strip()) == 0:
            raise ValueError("Text cannot be empty")
        
        if len(text) > self.config.MAX_TEXT_LENGTH:
            raise ValueError(f"Text too long. Maximum {self.config.MAX_TEXT_LENGTH} characters allowed")
        
        # Generate output path if not provided
        if output_path is None:
            import time
            timestamp = int(time.time())
            output_path = os.path.join(
                self.config.OUTPUT_DIR, 
                f"tts_{language}_{timestamp}.mp3"
            )
        
        try:
            logger.info(f"Generating speech for language: {language}")
            
            # Get gTTS language code
            gtts_lang = self._get_gtts_lang_code(language)
            
            # Adjust speed for gTTS (it only supports slow=True/False)
            slow = speed < 0.8
            
            # Generate speech using gTTS (keep as MP3)
            tts = gTTS(text=text, lang=gtts_lang, slow=slow)
            tts.save(output_path)
            
            logger.info(f"Speech generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating speech with gTTS: {e}")
            
            # Fallback to offline TTS if available
            if self.offline_available:
                logger.info("Trying offline TTS as fallback...")
                return self._generate_offline(text, output_path)
            else:
                raise
    
    def _generate_offline(self, text, output_path):
        """Generate speech using offline pyttsx3 engine"""
        try:
            # Convert to WAV for pyttsx3
            if not output_path.endswith('.wav'):
                output_path = output_path.replace('.mp3', '.wav')
            
            self.offline_engine.save_to_file(text, output_path)
            self.offline_engine.runAndWait()
            
            logger.info(f"Offline speech generated: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Offline TTS also failed: {e}")
            raise

    
    def get_available_languages(self):
        """Get list of available languages"""
        return self.config.SUPPORTED_LANGUAGES
    
    def get_model_info(self):
        """Get information about loaded model"""
        return {
            'model_name': 'BandhanNova V1 TTS',
            'online': True,
            'offline_available': self.offline_available,
            'languages': list(self.config.SUPPORTED_LANGUAGES.keys())
        }

# Global TTS engine instance
_tts_engine = None

def get_tts_engine():
    """Get or create TTS engine singleton"""
    global _tts_engine
    if _tts_engine is None:
        _tts_engine = TTSEngine()
    return _tts_engine
