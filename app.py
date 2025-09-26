from flask import Flask, jsonify, request, redirect, url_for, session
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies, get_jwt
from datetime import timedelta, datetime
import os
import json
import logging
import secrets
import time
import glob
import sqlite3

# Import blueprints
from api.auth import auth_bp
from api.user import user_bp
from api.music import music_bp
from api.analytics import analytics_bp
from api.ai_insights import ai_bp

# Import modules
from modules.database import SpotifyDatabase
from modules.api import SpotifyAPI
from modules.sample_data_generator import SampleDataGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load configuration from environment variables
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', secrets.token_urlsafe(32)) # Change this in production!
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_urlsafe(32)) # Flask session secret
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies'] # Allow tokens in headers and cookies
app.config['JWT_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production' # Only send cookies over HTTPS in production
app.config['JWT_COOKIE_CSRF_PROTECT'] = True # Enable CSRF protection for cookies
app.config['JWT_COOKIE_SAMESITE'] = 'Lax' # Adjust as needed for your frontend deployment

# Initialize Flask extensions
jwt = JWTManager(app)

# CORS Configuration
# Allow all origins for development, specify for production
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
if os.getenv('FLASK_ENV') == 'production':
    # Add Vercel frontend URL for production
    vercel_url = os.getenv('VERCEL_FRONTEND_URL')
    if vercel_url and vercel_url not in cors_origins:
        cors_origins.append(vercel_url)
    # Add Leapcell backend URL for production (if different from frontend)
    leapcell_url = os.getenv('LEAPCELL_BACKEND_URL')
    if leapcell_url and leapcell_url not in cors_origins:
        cors_origins.append(leapcell_url)

CORS(app, resources={r"/api/*": {"origins": cors_origins}}, supports_credentials=True)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(music_bp, url_prefix='/api/music')
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
app.register_blueprint(ai_bp, url_prefix='/api/ai')

# --- JWT Callbacks ---
@jwt.user_identity_loader
def user_identity_callback(user):
    return user

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data['sub']
    return identity # Just return the identity, no user object needed for this app

@jwt.token_verification_loader
def token_verification_callback(jwt_header, jwt_payload):
    # Custom logic if needed, otherwise default verification is fine
    return True

@jwt.unauthorized_loader
def unauthorized_response(callback):
    return jsonify({'error': 'Missing or invalid token'}), 401

@jwt.invalid_token_loader
def invalid_token_response(callback):
    return jsonify({'error': 'Signature verification failed'}), 401

@jwt.expired_token_loader
def expired_token_response(callback):
    return jsonify({'error': 'Token has expired'}), 401

# --- Helper Functions ---

def get_db_for_user(user_id):
    """Helper to get user-specific database instance"""
    if user_id == 'demo-user':
        return SpotifyDatabase(db_path='/tmp/sample_spotify_data.db'), 'demo-user-spotify-wrapped'
    else:
        return SpotifyDatabase(db_path=f'/tmp/user_{user_id}_spotify_data.db'), user_id

# --- Routes ---
@app.route('/api/status')
def status():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/api/debug-sentry')
def debug_sentry():
    # This route is for testing Sentry error reporting
    raise Exception("This is a test error from Flask")

@app.route('/api/demo-mode', methods=['POST'])
def enable_demo_mode():
    try:
        # Generate a temporary user ID for the demo session
        demo_user_id = f"demo-{secrets.token_urlsafe(8)}"
        
        # Create a sample database for the demo user
        sample_generator = SampleDataGenerator()
        sample_generator.populate_sample_database(db_path=f'/tmp/user_{demo_user_id}_spotify_data.db')
        
        # Create a JWT for the demo user
        access_token = create_access_token(
            identity=demo_user_id,
            additional_claims={
                'spotify_access_token': 'DEMO_TOKEN',
                'spotify_refresh_token': 'DEMO_REFRESH',
                'display_name': 'Demo User',
                'email': 'demo@example.com',
                'client_id': 'DEMO_CLIENT_ID',
                'client_secret': 'DEMO_CLIENT_SECRET',
                'user_session_token': secrets.token_urlsafe(16),
                'spotify_user_id': demo_user_id
            }
        )
        
        response = jsonify({
            'access_token': access_token,
            'user': {
                'id': demo_user_id,
                'display_name': 'Demo User',
                'email': 'demo@example.com',
                'images': []
            }
        })
        
        # Set access token in cookies for demo mode
        set_access_cookies(response, access_token)
        
        return response
    except Exception as e:
        logger.error(f"Error enabling demo mode: {e}")
        return jsonify({'error': 'Failed to enable demo mode'}), 500

@app.route('/api/clear-all-data', methods=['POST'])
@jwt_required()
def clear_all_data():
    """Clears all user-specific data and cache files."""
    try:
        user_id = get_jwt_identity()
        
        # Clear user-specific database
        user_db_path = f'/tmp/user_{user_id}_spotify_data.db'
        if os.path.exists(user_db_path):
            os.remove(user_db_path)
            logger.info(f"Removed user database: {user_db_path}")

        # Clear Spotify API cache files for this user
        # The cache path is constructed in modules/api.py, so we need to replicate it
        client_id_prefix = get_jwt().get('client_id', '')[:8]
        user_cache_pattern = f'/tmp/.spotify_cache_{user_id}_{client_id_prefix}*'
        for cache_file in glob.glob(user_cache_pattern):
            try:
                os.remove(cache_file)
                logger.info(f"Removed user Spotify cache file: {cache_file}")
            except Exception as e:
                logger.warning(f"Could not remove cache file {cache_file}: {e}")

        # Clear any temporary auth code files
        auth_code_pattern = f'/tmp/spotify_auth_code_{user_id}_{client_id_prefix}*'
        for code_file in glob.glob(auth_code_pattern):
            try:
                os.remove(code_file)
                logger.info(f"Removed user auth code file: {code_file}")
            except Exception as e:
                logger.warning(f"Could not remove auth code file {code_file}: {e}")

        # Clear the main sample database if it exists (only if user is demo)
        if user_id.startswith('demo-'):
            sample_db_path = '/tmp/sample_spotify_data.db'
            if os.path.exists(sample_db_path):
                os.remove(sample_db_path)
                logger.info(f"Removed sample database: {sample_db_path}")

        response = jsonify({'message': 'All user data and cache cleared successfully'})
        unset_jwt_cookies(response) # Clear JWT cookies as well
        return response
    except Exception as e:
        logger.error(f"Error clearing user data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/cleanup-old-dbs', methods=['POST'])
@jwt_required()
def cleanup_old_dbs():
    """Admin endpoint to clean up old user databases and cache files from /tmp."""
    try:
        # This should only be accessible by an admin user or internal process
        # For now, we'll just allow any authenticated user to trigger it for testing
        
        # Clean up old user databases
        main_db_path = '/tmp/spotify_data.db'
        if os.path.exists(main_db_path):
            os.remove(main_db_path)
            logger.info(f"Removed main database: {main_db_path}")

        user_db_pattern = '/tmp/user_*.db'
        for db_file in glob.glob(user_db_pattern):
            try:
                # Only remove if older than 7 days (or some other policy)
                # For now, remove all old ones
                os.remove(db_file)
                logger.info(f"Removed old user database: {db_file}")
            except Exception as e:
                logger.warning(f"Could not remove old user database {db_file}: {e}")

        # Clean up old Spotify cache files
        spotify_cache_pattern = '/tmp/.spotify_cache_*'
        for cache_file in glob.glob(spotify_cache_pattern):
            try:
                os.remove(cache_file)
                logger.info(f"Removed old Spotify cache file: {cache_file}")
            except Exception as e:
                logger.warning(f"Could not remove old Spotify cache file {cache_file}: {e}")

        # Clean up old Spotify auth code files
        spotify_auth_code_pattern = '/tmp/spotify_auth_code_*.txt'
        for code_file in glob.glob(spotify_auth_code_pattern):
            try:
                os.remove(code_file)
                logger.info(f"Removed old Spotify auth code file: {code_file}")
            except Exception as e:
                logger.warning(f"Could not remove old Spotify auth code file {code_file}: {e}")

        return jsonify({'message': 'Old databases and cache files cleaned up from /tmp'})
    except Exception as e:
        logger.error(f"Error cleaning up old databases: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # In a production environment like Leapcell, this block might not be directly executed
    # as the server is typically run by a WSGI server (e.g., Gunicorn).
    # However, for local testing or specific deployment setups, it's useful.
    logger.info("Starting Flask app in development mode")
    app.run(debug=True, host='0.0.0.0', port=5000)