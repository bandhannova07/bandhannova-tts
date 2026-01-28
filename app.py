"""
Flask API Server for TTS Generator
"""
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
import logging
from tts_engine import get_tts_engine
from audio_processor import AudioProcessor
from config import Config
from api_keys import create_api_key, is_valid_key, get_first_key
import traceback

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize config
config = Config()

# Initialize TTS engine (lazy loading)
tts_engine = None

def _extract_api_key(req):
    auth_header = req.headers.get('Authorization', '')
    if auth_header.lower().startswith('bearer '):
        return auth_header.split(' ', 1)[1].strip()
    return req.headers.get('X-API-Key', '').strip()

def _require_api_key(req):
    api_key = _extract_api_key(req)
    if not is_valid_key(api_key):
        return jsonify({
            'success': False,
            'error': 'Invalid or missing API key'
        }), 401
    return None

def get_engine():
    """Get or initialize TTS engine"""
    global tts_engine
    if tts_engine is None:
        logger.info("Initializing TTS engine...")
        tts_engine = get_tts_engine()
    return tts_engine

@app.route('/')
def index():
    """Serve the main page"""
    # Get a valid API key for the frontend
    api_key = get_first_key()
    if not api_key:
        # Create one if missing/deleted
        api_key = create_api_key(label="public_web")
        
    return render_template('index.html', api_key=api_key)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        engine = get_engine()
        model_info = engine.get_model_info()
        return jsonify({
            'status': 'healthy',
            'model': model_info
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/engine-status', methods=['GET'])
def engine_status():
    """Get detailed TTS engine status for diagnostics"""
    try:
        engine = get_engine()
        model_info = engine.get_model_info()
        
        status = {
            'success': True,
            'engine_info': model_info,
            'edge_tts_available': engine.edge_tts_available,
            'edge_tts_via_module': engine.edge_tts_via_module,
            'offline_available': engine.offline_available,
            'xtts_available': engine.xtts is not None,
            'voice_profiles': config.VOICE_PROFILES,
            'supported_languages': list(config.SUPPORTED_LANGUAGES.keys())
        }
        
        # Add warnings if Edge TTS is not available
        if not engine.edge_tts_available:
            status['warning'] = 'Edge TTS (Neural voices) NOT available - using gTTS fallback (robotic voice)'
            status['recommendation'] = 'Install edge-tts package: pip install edge-tts'
        
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting engine status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get available languages"""
    try:
        engine = get_engine()
        languages = engine.get_available_languages()
        return jsonify({
            'success': True,
            'languages': languages
        })
    except Exception as e:
        logger.error(f"Error getting languages: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/keys/create', methods=['POST'])
def create_key():
    """Create a free API key for public access"""
    try:
        payload = request.get_json(silent=True) or {}
        label = payload.get('label', 'public')
        api_key = create_api_key(label=label)
        return jsonify({
            'success': True,
            'api_key': api_key
        })
    except Exception as e:
        logger.error(f"Error creating API key: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_voice_id(lang_code, gender):
    """Get Voice ID based on language code and gender"""
    if not gender:
        gender = 'female' # Default to female
    
    gender = gender.lower()
    if gender not in ['male', 'female']:
        gender = 'female'
        
    key = f"{lang_code}_{gender}"
    return config.VOICE_PROFILES.get(key)

from io import BytesIO
from flask import Response

def process_generate_request(text, lang_code, speed, pitch, gender, stream=False):
    """Common logic for processing generation request"""
    # Validate input
    if not text:
        return jsonify({
            'success': False,
            'error': 'Text cannot be empty'
        }), 400
    
    if len(text) > config.MAX_TEXT_LENGTH:
        return jsonify({
            'success': False,
            'error': f'Text too long. Maximum {config.MAX_TEXT_LENGTH} characters allowed'
        }), 400
    
    # Validate speed and pitch
    speed = max(config.MIN_SPEED, min(config.MAX_SPEED, speed))
    pitch = max(config.MIN_PITCH, min(config.MAX_PITCH, pitch))
    
    # Get Voice ID
    voice_id = get_voice_id(lang_code, gender)
    
    logger.info(f"📝 Request: lang={lang_code}, gender={gender}, speed={speed}, stream={stream}")
    logger.info(f"   Voice ID selected: {voice_id}")
    logger.info(f"   Text length: {len(text)} chars")
    
    engine = get_engine()
    
    # --- Option 1: Streaming Response (Low Latency) ---
    if stream:
        try:
            return Response(
                engine.generate_speech_stream(
                    text=text,
                    language=lang_code,
                    speed=speed,
                    voice_id=voice_id
                ),
                mimetype='audio/mpeg',
                headers={
                    'Content-Disposition': f'inline; filename="speech_{lang_code}.mp3"',
                    'Cache-Control': 'no-cache'
                }
            )
        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            # Fallback to non-streaming if requested stream fails
            pass

    # --- Option 2: Full Buffer Response (Standard) ---
    try:
        audio_content, mimetype = engine.generate_speech(
            text=text,
            language=lang_code,
            speed=speed,
            voice_id=voice_id,
            return_bytes=True
        )
        
        # Return audio stream
        return send_file(
            BytesIO(audio_content),
            mimetype=mimetype,
            as_attachment=False,
            download_name=f'speech_{lang_code}.mp3'
        )
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/<language_name>/<gender>/generate', methods=['POST'])
def generate_by_language_and_gender(language_name, gender):
    """
    Generate speech using language and gender in URL 
    e.g. /bengali/male/generate
    """
    try:
        auth_error = _require_api_key(request)
        if auth_error:
            return auth_error
            
        # Find language code from name
        language_name = language_name.lower()
        lang_code = None
        
        for code, info in config.SUPPORTED_LANGUAGES.items():
            if info['name'].lower() == language_name:
                lang_code = code
                break
        
        if not lang_code:
            return jsonify({
                'success': False,
                'error': f"Language '{language_name}' not supported"
            }), 404
            
        # Validate gender from URL
        gender = gender.lower()
        if gender not in ['male', 'female']:
            return jsonify({
                'success': False,
                'error': "Gender must be 'male' or 'female'"
            }), 400
            
        # Get request data for text/speed/pitch
        data = request.get_json(silent=True) or {}
        text = data.get('text', '').strip()
        speed = float(data.get('speed', 1.0))
        pitch = int(data.get('pitch', 0))
        stream = data.get('stream', True)  # Default to TRUE for better UX
        
        # URL gender overrides JSON gender if both provided (URL is source of truth here)
        logger.info(f"🌐 Endpoint: /{language_name}/{gender}/generate")
        
        return process_generate_request(text, lang_code, speed, pitch, gender, stream=stream)

    except Exception as e:
        logger.error(f"Error in language/gender route: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/<language_name>/generate', methods=['POST'])
def generate_by_language_name(language_name):
    """Generate speech using language name in URL (e.g. /bengali/generate)"""
    try:
        auth_error = _require_api_key(request)
        if auth_error:
            return auth_error
            
        # Find language code from name
        language_name = language_name.lower()
        lang_code = None
        
        for code, info in config.SUPPORTED_LANGUAGES.items():
            if info['name'].lower() == language_name:
                lang_code = code
                break
        
        if not lang_code:
            return jsonify({
                'success': False,
                'error': f"Language '{language_name}' not supported"
            }), 404
            
        # Get request data
        data = request.get_json(silent=True) or {}
        text = data.get('text', '').strip()
        speed = float(data.get('speed', 1.0))
        pitch = int(data.get('pitch', 0))
        gender = data.get('gender', 'female')
        stream = data.get('stream', True)  # Default to TRUE
        
        return process_generate_request(text, lang_code, speed, pitch, gender, stream=stream)

    except Exception as e:
        logger.error(f"Error in language route: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate', methods=['POST'])
def generate_speech():
    """Generate speech from text (Legacy/Generic Endpoint)"""
    try:
        auth_error = _require_api_key(request)
        if auth_error:
            return auth_error

        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        text = data.get('text', '').strip()
        language = data.get('language', 'en')
        speed = float(data.get('speed', 1.0))
        pitch = int(data.get('pitch', 0))
        gender = data.get('gender', 'female')
        stream = data.get('stream', True)  # Default to TRUE
        
        # Check if voice_profile is passed (legacy support)
        # If voice_profile is passed, we might ignore gender logic, or try to decode it
        # But for consistency, let's use the new logic if language is supported
        
        if language not in config.SUPPORTED_LANGUAGES:
            return jsonify({
                'success': False,
                'error': f'Language {language} not supported'
            }), 400
            
        return process_generate_request(text, language, speed, pitch, gender, stream=stream)
        
    except Exception as e:
        logger.error(f"Error generating speech: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_audio(filename):
    """Download generated audio file"""
    try:
        file_path = os.path.join(config.OUTPUT_DIR, filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        return send_file(
            file_path,
            mimetype='audio/wav',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    os.makedirs(config.CACHE_DIR, exist_ok=True)
    os.makedirs(config.MODEL_DIR, exist_ok=True)
    
    # Create templates directory
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    logger.info(f"Starting TTS server on {config.HOST}:{config.PORT}")
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
