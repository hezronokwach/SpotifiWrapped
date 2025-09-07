"""
Flask REST API for Spotify Analytics Application
Replaces the Dash-based frontend with a proper REST API backend
"""

from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import timedelta, datetime

# Import existing modules
from modules.api import SpotifyAPI
from modules.database import SpotifyDatabase
from modules.data_collector import SpotifyDataCollector
from modules.analyzer import ListeningPersonalityAnalyzer
from modules.ai_personality_enhancer import EnhancedPersonalityAnalyzer
from modules.enhanced_stress_detector import EnhancedStressDetector
from modules.genre_evolution_tracker import GenreEvolutionTracker
from modules.wellness_analyzer import WellnessAnalyzer
from modules.top_albums import get_top_albums
from modules.genre_extractor import GenreExtractor

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Configuration
    secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this')
    app.config['SECRET_KEY'] = secret_key  # Required for Flask sessions
    app.config['JWT_SECRET_KEY'] = secret_key
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)  # Shorter expiry for security
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # Initialize extensions
    jwt = JWTManager(app)

    # CORS configuration for production
    CORS(app,
         origins=os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(','),
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

    # Token validation middleware
    @app.before_request
    def check_token():
        # Skip token validation for auth endpoints and health checks
        if (request.endpoint and 
            ('auth' in request.endpoint or 
             request.endpoint in ['health_check', 'debug_info'] or
             request.method == 'OPTIONS')):
            return
        
        # Only validate tokens for API endpoints
        if request.path.startswith('/api/') and not request.path.startswith('/api/auth'):
            try:
                verify_jwt_in_request()
            except Exception as e:
                return jsonify({'error': 'Invalid or expired token'}), 401
    
    # Security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://api.spotify.com https://accounts.spotify.com"
        return response
    
    # Import and register blueprints
    from api.auth import auth_bp
    from api.user import user_bp
    from api.music import music_bp
    from api.analytics import analytics_bp
    from api.ai_insights import ai_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(music_bp, url_prefix='/api/music')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'healthy', 'message': 'Spotify Analytics API is running'})

    @app.route('/api/debug')
    def debug_info():
        return jsonify({
            'status': 'running',
            'environment': os.getenv('FLASK_ENV', 'development'),
            'spotify_redirect_uri': os.getenv('SPOTIFY_REDIRECT_URI'),
            'allowed_origins': os.getenv('ALLOWED_ORIGINS'),
            'timestamp': str(datetime.now())
        })
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ 500 Error: {error_details}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(error) if app.debug else 'Check server logs'
        }), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
