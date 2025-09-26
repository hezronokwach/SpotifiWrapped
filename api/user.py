"""
User profile and statistics endpoints
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from modules.database import SpotifyDatabase
from modules.api import SpotifyAPI
import os
import sqlite3

user_bp = Blueprint('user', __name__)

def validate_user_access(user_id, claims):
    """Validate user has access to their own data only"""
    if not user_id:
        raise Exception('No user ID provided')
    
    jwt_user_id = claims.get('spotify_user_id')
    if user_id != jwt_user_id:
        raise Exception(f'User access violation: {user_id} != {jwt_user_id}')
    
    session_token = claims.get('user_session_token')
    if not session_token:
        raise Exception('Missing session token')
    
    return True

def get_secure_database_path(user_id):
    """Get secure database path for user with validation"""
    if not user_id or not isinstance(user_id, str) or len(user_id) < 3:
        raise Exception('Invalid user ID for database access')
    
    # Sanitize user ID to prevent path traversal
    import re
    safe_user_id = re.sub(r'[^a-zA-Z0-9_-]', '', user_id)
    if safe_user_id != user_id:
        raise Exception('User ID contains invalid characters')
    
    # Use /tmp for writable storage on serverless platforms
    return f'/tmp/user_{safe_user_id}_spotify_data.db'

def get_user_spotify_api():
    """Get SpotifyAPI instance for current user, relying on the cache."""
    try:
        claims = get_jwt()
        user_id = claims.get('spotify_user_id')
        client_id = claims.get('client_id')
        client_secret = claims.get('client_secret')
        redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:3000/auth/callback')

        if not all([user_id, client_id, client_secret]):
            raise Exception('Missing user_id, client_id, or client_secret in JWT token')

        # Initialize SpotifyAPI with user_id to use the correct cache
        spotify_api = SpotifyAPI(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            user_id=user_id
        )
        return spotify_api

    except Exception as e:
        print(f"❌ Error creating SpotifyAPI: {e}")
        return None

def get_spotify_api_for_user():
    """Initialize SpotifyAPI using the user's ID from the JWT to leverage the cached token."""
    try:
        claims = get_jwt()
        user_id = claims.get('spotify_user_id')
        client_id = claims.get('client_id')
        client_secret = claims.get('client_secret')
        redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:3000/auth/callback')

        if not all([user_id, client_id, client_secret]):
            raise Exception('Missing user_id, client_id, or client_secret in JWT token')

        # Initialize SpotifyAPI with user_id to use the correct cache
        spotify_api = SpotifyAPI(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            user_id=user_id
        )

        # The SpotifyAPI instance will now automatically use the cached token
        # managed by SpotifyOAuth, which handles refreshing.
        return spotify_api

    except Exception as e:
        print(f"❌ DEBUG: Error initializing SpotifyAPI: {e}")
        raise

@user_bp.route('/profile')
@jwt_required()
def get_profile():
    """Get user profile information - EXACT copy from Dash app"""
    try:
        # Get user-specific Spotify API instance (exactly like Dash)
        spotify_api = get_user_spotify_api()
        if not spotify_api:
            return jsonify({'error': 'Failed to initialize Spotify API'}), 500

        # Call get_user_profile() exactly like Dash does
        user_data = spotify_api.get_user_profile()

        if not user_data:
            return jsonify({'error': 'Failed to get user profile'}), 500

        # Return exactly what SpotifyAPI.get_user_profile() returns
        return jsonify(user_data)

    except Exception as e:
        print(f"❌ Profile error: {e}")
        return jsonify({'error': str(e)}), 500

@user_bp.route('/collect-data', methods=['POST'])
@jwt_required()
def collect_initial_data():
    """Collect initial user data from Spotify API including genre extraction"""
    try:
        user_id = get_jwt_identity()
        db_path = get_secure_database_path(user_id)
        
        # Initialize components
        from modules.data_collector import SpotifyDataCollector
        from modules.database import SpotifyDatabase
        spotify_api = get_spotify_api_for_user()
        
        if not spotify_api:
            return jsonify({'error': 'Failed to initialize Spotify API'}), 500
            
        # Initialize database and data collector
        user_db = SpotifyDatabase(db_path)
        collector = SpotifyDataCollector(spotify_api, user_db)
        
        # Collect basic data using the correct method
        success = collector.collect_historical_data(user_id)
        
        if success:
            return jsonify({'message': 'Data collection and genre extraction completed successfully'})
        else:
            return jsonify({'error': 'Data collection failed'}), 500
        
    except Exception as e:
        print(f"❌ Data collection error: {e}")
        return jsonify({'error': str(e)}), 500

@user_bp.route('/stats')
@jwt_required()
def get_stats():
    """Get basic user statistics with strict user isolation"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        
        # Security validation
        validate_user_access(user_id, claims)
        
        db_path = get_secure_database_path(user_id)

        # Initialize components
        db = SpotifyDatabase(db_path)
        spotify_api = get_spotify_api_for_user()

        # Get basic statistics from database
        db_stats = {
            'total_tracks': 0,
            'total_artists': 0,
            'total_albums': 0,
            'listening_time_minutes': 0
        }

        # Query database for statistics using proper database connection
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Count tracks
            cursor.execute("SELECT COUNT(*) FROM tracks")
            result = cursor.fetchone()
            db_stats['total_tracks'] = result[0] if result and result[0] else 0

            # Count unique artists
            cursor.execute("SELECT COUNT(DISTINCT artist) FROM tracks")
            result = cursor.fetchone()
            db_stats['total_artists'] = result[0] if result and result[0] else 0

            # Count unique albums
            cursor.execute("SELECT COUNT(DISTINCT album) FROM tracks")
            result = cursor.fetchone()
            db_stats['total_albums'] = result[0] if result and result[0] else 0

            # Calculate total listening time
            cursor.execute("SELECT SUM(duration_ms) FROM tracks")
            result = cursor.fetchone()
            total_duration_ms = result[0] if result and result[0] else 0
            db_stats['listening_time_minutes'] = round(total_duration_ms / 60000, 2) if total_duration_ms else 0

            conn.close()

        except Exception as db_error:
            print(f"Database query error: {db_error}")

        # Get additional stats from Spotify API
        api_stats = {}
        try:
            # Get playlists count
            playlists = spotify_api.get_playlists()
            api_stats['total_playlists'] = len(playlists) if playlists else 0

            # Get top tracks for real-time display
            top_tracks = spotify_api.get_top_tracks(limit=20)
            if top_tracks:
                api_stats['api_tracks'] = len(top_tracks)
                artists = set(track.get('artist', '') for track in top_tracks)
                albums = set(track.get('album', '') for track in top_tracks)
                api_stats['api_artists'] = len(artists)
                api_stats['api_albums'] = len(albums)
                
            # If database is empty, use API data as fallback
            if db_stats['total_tracks'] == 0 and api_stats.get('api_tracks'):
                db_stats.update({
                    'total_tracks': api_stats['api_tracks'],
                    'total_artists': api_stats['api_artists'], 
                    'total_albums': api_stats['api_albums']
                })
                
        except Exception as api_error:
            print(f"API query error: {api_error}")

        # Combine stats (prefer database stats if available, otherwise use API stats)
        final_stats = {
            'total_tracks': db_stats['total_tracks'] or api_stats.get('total_tracks', 0),
            'total_artists': db_stats['total_artists'] or api_stats.get('total_artists', 0),
            'total_albums': db_stats['total_albums'] or api_stats.get('total_albums', 0),
            'total_playlists': api_stats.get('total_playlists', 0),
            'listening_time_minutes': db_stats['listening_time_minutes'] or api_stats.get('listening_time_minutes', 0)
        }

        return jsonify(final_stats)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/extract-genres', methods=['POST'])
@jwt_required()
def extract_genres():
    """Extract genres for user's artists"""
    try:
        user_id = get_jwt_identity()
        db_path = get_secure_database_path(user_id)
        
        # Initialize components
        from modules.genre_extractor import GenreExtractor
        from modules.database import SpotifyDatabase
        spotify_api = get_spotify_api_for_user()
        
        if not spotify_api:
            return jsonify({'error': 'Failed to initialize Spotify API'}), 500
            
        # Initialize database and genre extractor
        user_db = SpotifyDatabase(db_path)
        genre_extractor = GenreExtractor(spotify_api, user_db)
        
        # Extract genres from recent tracks
        genres_extracted = genre_extractor.extract_genres_from_recent_tracks(max_artists=50)
        
        return jsonify({
            'message': f'Successfully extracted {genres_extracted} genres',
            'genres_extracted': genres_extracted
        })
        
    except Exception as e:
        print(f"❌ Genre extraction error: {e}")
        return jsonify({'error': str(e)}), 500