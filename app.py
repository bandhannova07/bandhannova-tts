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
from api_keys import create_api_key, is_valid_key
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
    return render_template('index.html')

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

@app.route('/api/generate', methods=['POST'])
def generate_speech():
    """Generate speech from text"""
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
        
        if language not in config.SUPPORTED_LANGUAGES:
            return jsonify({
                'success': False,
                'error': f'Language {language} not supported'
            }), 400
        
        # Validate speed and pitch
        speed = max(config.MIN_SPEED, min(config.MAX_SPEED, speed))
        pitch = max(config.MIN_PITCH, min(config.MAX_PITCH, pitch))
        
        logger.info(f"Generating speech: lang={language}, speed={speed}, pitch={pitch}")
        
        # Generate speech
        engine = get_engine()
        audio_path = engine.generate_speech(
            text=text,
            language=language,
            speed=speed
        )
        
        # Skip pitch shift and enhancement for now (requires ffmpeg)
        # Just serve the generated MP3 file directly
        
        # Determine mimetype
        mimetype = 'audio/mpeg' if audio_path.endswith('.mp3') else 'audio/wav'
        
        # Return audio file
        return send_file(
            audio_path,
            mimetype=mimetype,
            as_attachment=False,
            download_name=f'speech_{language}.mp3'
        )
        
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
