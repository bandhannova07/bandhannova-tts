"""
Configuration file for TTS Generator
"""
import os

class Config:
    # Server Configuration
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = True
    
    # Audio Configuration
    SAMPLE_RATE = 22050
    AUDIO_FORMAT = 'wav'
    MAX_TEXT_LENGTH = 5000
    
    # Language Configuration
    SUPPORTED_LANGUAGES = {
        'bn': {
            'name': 'Bengali',
            'code': 'bn',
            'model': 'tts_models/multilingual/multi-dataset/xtts_v2',
            'flag': '🇮🇳'
        },
        'hi': {
            'name': 'Hindi',
            'code': 'hi',
            'model': 'tts_models/multilingual/multi-dataset/xtts_v2',
            'flag': '🇮🇳'
        },
        'mr': {
            'name': 'Marathi',
            'code': 'mr',
            'model': 'tts_models/multilingual/multi-dataset/xtts_v2',
            'flag': '🇮🇳'
        },
        'gu': {
            'name': 'Gujarati',
            'code': 'gu',
            'model': 'tts_models/multilingual/multi-dataset/xtts_v2',
            'flag': '🇮🇳'
        },
        'kn': {
            'name': 'Kannada',
            'code': 'kn',
            'model': 'tts_models/multilingual/multi-dataset/xtts_v2',
            'flag': '🇮🇳'
        },
        'ml': {
            'name': 'Malayalam',
            'code': 'ml',
            'model': 'tts_models/multilingual/multi-dataset/xtts_v2',
            'flag': '🇮🇳'
        },
        'pa': {
            'name': 'Punjabi',
            'code': 'pa',
            'model': 'tts_models/multilingual/multi-dataset/xtts_v2',
            'flag': '🇮🇳'
        },
        'ur': {
            'name': 'Urdu',
            'code': 'ur',
            'model': 'tts_models/multilingual/multi-dataset/xtts_v2',
            'flag': '🇮🇳'
        },
        'or': {
            'name': 'Odia',
            'code': 'or',
            'model': 'tts_models/multilingual/multi-dataset/xtts_v2',
            'flag': '🇮🇳'
        },
        'as': {
            'name': 'Assamese',
            'code': 'as',
            'model': 'tts_models/multilingual/multi-dataset/xtts_v2',
            'flag': '🇮🇳'
        },
        'ta': {
            'name': 'Tamil',
            'code': 'ta',
            'model': 'tts_models/multilingual/multi-dataset/xtts_v2',
            'flag': '🇮🇳'
        },
        'te': {
            'name': 'Telugu',
            'code': 'te',
            'model': 'tts_models/multilingual/multi-dataset/xtts_v2',
            'flag': '🇮🇳'
        },
        'en': {
            'name': 'English',
            'code': 'en',
            'model': 'tts_models/multilingual/multi-dataset/xtts_v2',
            'flag': '🇬🇧'
        }
    }
    
    # Voice Customization Defaults
    DEFAULT_SPEED = 1.0
    MIN_SPEED = 0.5
    MAX_SPEED = 2.0
    
    DEFAULT_PITCH = 0
    MIN_PITCH = -20
    MAX_PITCH = 20
    
    # Cache Configuration
    CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')
    ENABLE_CACHE = True
    MAX_CACHE_SIZE_MB = 500
    
    # Model Configuration
    MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
    USE_GPU = False  # Set to True if CUDA is available
    
    # Output Configuration
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
    
    # Voice Profiles (Human-like settings)
    # Using Edge TTS Neural Voices
    VOICE_PROFILES = {
        'bn_male': 'bn-BD-PradeepNeural',
        'bn_female': 'bn-IN-TanishaaNeural', 
        'hi_male': 'hi-IN-MadhurNeural',
        'hi_female': 'hi-IN-SwaraNeural',
        'en_male': 'en-US-ChristopherNeural',
        'en_female': 'en-US-AriaNeural'
    }
    
    # Prosody Default Settings
    # Edge TTS supports rate and pitch changes
    DEFAULT_RATE = "+0%"
    DEFAULT_PITCH = "+0Hz"

