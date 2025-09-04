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

def get_user_spotify_api():
    """Get SpotifyAPI instance for current user"""
    try:
        claims = get_jwt()
        client_id = claims.get('client_id')
        client_secret = claims.get('client_secret')
        spotify_access_token = claims.get('spotify_access_token')
        redirect_uri = 'http://127.0.0.1:3000/auth/callback'

        if not all([client_id, client_secret, spotify_access_token]):
            return None

        # Initialize SpotifyAPI
        spotify_api = SpotifyAPI(client_id, client_secret, redirect_uri)

        # Set the access token directly
        if hasattr(spotify_api, 'sp') and spotify_api.sp and hasattr(spotify_api.sp, 'auth_manager'):
            token_info = {
                'access_token': spotify_access_token,
                'token_type': 'Bearer',
                'expires_in': 3600,
                'refresh_token': claims.get('spotify_refresh_token'),
                'scope': spotify_api.scopes
            }
            spotify_api.sp.auth_manager.token_info = token_info

        return spotify_api
    except Exception as e:
        print(f"❌ Error creating SpotifyAPI: {e}")
        return None

def get_spotify_api_for_user():
    """Initialize SpotifyAPI with user credentials and access token from JWT token"""
    try:
        claims = get_jwt()
        client_id = claims.get('client_id')
        client_secret = claims.get('client_secret')
        spotify_access_token = claims.get('spotify_access_token')
        redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:3000/auth/callback')

        if not client_id or not client_secret:
            raise Exception('Missing Spotify credentials in JWT token')

        if not spotify_access_token:
            raise Exception('Missing Spotify access token in JWT token')

        # Initialize SpotifyAPI with credentials
        spotify_api = SpotifyAPI(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri
        )

        # Manually set the access token in the spotipy client
        if spotify_api.sp and hasattr(spotify_api.sp, 'auth_manager'):
            # Create a token info dict that spotipy expects
            token_info = {
                'access_token': spotify_access_token,
                'token_type': 'Bearer',
                'expires_in': 3600,  # 1 hour
                'refresh_token': claims.get('spotify_refresh_token'),
                'scope': spotify_api.scopes
            }

            # Set the token in the auth manager
            spotify_api.sp.auth_manager.token_info = token_info

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
    """Collect initial user data from Spotify API"""
    try:
        user_id = get_jwt_identity()
        db_path = f'data/user_{user_id}_spotify_data.db'
        
        # Initialize components
        from modules.data_collector import SpotifyDataCollector
        spotify_api = get_spotify_api_for_user()
        
        if not spotify_api:
            return jsonify({'error': 'Failed to initialize Spotify API'}), 500
            
        # Initialize data collector
        collector = SpotifyDataCollector(spotify_api, db_path)
        
        # Collect basic data using the correct method
        collector.collect_historical_data(user_id)
        
        return jsonify({'message': 'Data collection completed successfully'})
        
    except Exception as e:
        print(f"❌ Data collection error: {e}")
        return jsonify({'error': str(e)}), 500

@user_bp.route('/stats')
@jwt_required()
def get_stats():
    """Get basic user statistics from both database and Spotify API"""
    try:
        user_id = get_jwt_identity()
        db_path = f'data/user_{user_id}_spotify_data.db'

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

            # If database is empty, get some stats from API
            if db_stats['total_tracks'] == 0:
                # Get top tracks to show some data
                top_tracks = spotify_api.get_top_tracks(limit=50)
                if top_tracks:
                    api_stats['total_tracks'] = len(top_tracks)
                    # Extract unique artists and albums from top tracks
                    artists = set()
                    albums = set()
                    total_duration = 0

                    for track in top_tracks:
                        artists.add(track.get('artist', ''))
                        albums.add(track.get('album', ''))
                        total_duration += track.get('duration_ms', 0)

                    api_stats['total_artists'] = len(artists)
                    api_stats['total_albums'] = len(albums)
                    api_stats['listening_time_minutes'] = round(total_duration / 60000, 2)

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
