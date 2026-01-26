"""
Configuration file for TTS Generator
"""
import os

class Config:
    # Server Configuration
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5000))
    DEBUG = os.environ.get('FLASK_1ENV') == 'development'
    
    # Audio Configuration
    SAMPLE_RATE = 22050
    AUDIO_FORMAT = 'wav'
    MAX_TEXT_LENGTH = 5000
    
    # Language Configuration
    SUPPORTED_LANGUAGES = {
        'bn': {
            'name': 'Bengali',
            'code': 'bn',
            'flag': '🇮🇳'
        },
        'hi': {
            'name': 'Hindi',
            'code': 'hi',
            'flag': '🇮🇳'
        },
        'ta': {
            'name': 'Tamil',
            'code': 'ta',
            'flag': '🇮🇳'
        },
        'te': {
            'name': 'Telugu',
            'code': 'te',
            'flag': '🇮🇳'
        },
        'mr': {
            'name': 'Marathi',
            'code': 'mr',
            'flag': '🇮🇳'
        },
        'gu': {
            'name': 'Gujarati',
            'code': 'gu',
            'flag': '🇮🇳'
        },
        'kn': {
            'name': 'Kannada',
            'code': 'kn',
            'flag': '🇮🇳'
        },
        'ml': {
            'name': 'Malayalam',
            'code': 'ml',
            'flag': '🇮🇳'
        },
        'en': {
            'name': 'English',
            'code': 'en',
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
        # Bengali
        'bn_male': 'bn-BD-PradeepNeural',
        'bn_female': 'bn-IN-TanishaaNeural', 
        
        # Hindi
        'hi_male': 'hi-IN-MadhurNeural',
        'hi_female': 'hi-IN-SwaraNeural',
        
        # Tamil
        'ta_male': 'ta-IN-ValluvarNeural',
        'ta_female': 'ta-IN-PallaviNeural',
        
        # Telugu
        'te_male': 'te-IN-MohanNeural',
        'te_female': 'te-IN-ShrutiNeural',
        
        # Marathi
        'mr_male': 'mr-IN-ManoharNeural',
        'mr_female': 'mr-IN-AarohiNeural',
        
        # Gujarati
        'gu_male': 'gu-IN-NiranjanNeural',
        'gu_female': 'gu-IN-DhwaniNeural',
        
        # Kannada
        'kn_male': 'kn-IN-GaganNeural',
        'kn_female': 'kn-IN-SapnaNeural',
        
        # Malayalam
        'ml_male': 'ml-IN-MidhunNeural',
        'ml_female': 'ml-IN-SobhanaNeural',
        
        # English (India)
        'en_male': 'en-IN-PrabhatNeural',
        'en_female': 'en-IN-NeerjaNeural'
    }
    
    # Prosody Default Settings
    # Edge TTS supports rate and pitch changes
    DEFAULT_RATE = "+0%"
    DEFAULT_PITCH = "+0Hz"

