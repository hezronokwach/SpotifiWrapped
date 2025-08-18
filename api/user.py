"""
User profile and statistics endpoints
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from modules.database import SpotifyDatabase
from modules.api import SpotifyAPI
import os

user_bp = Blueprint('user', __name__)

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
    """Get user profile information"""
    try:
        user_id = get_jwt_identity()
        
        # Get profile from Spotify API
        spotify_api = get_spotify_api_for_user()
        profile = spotify_api.get_user_profile()
        
        if not profile:
            return jsonify({'error': 'Failed to get user profile'}), 500
        
        return jsonify({
            'id': profile['id'],
            'display_name': profile.get('display_name'),
            'email': profile.get('email'),
            'country': profile.get('country'),
            'followers': profile.get('followers', {}).get('total', 0),
            'images': profile.get('images', []),
            'product': profile.get('product')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/stats')
@jwt_required()
def get_stats():
    """Get basic user statistics"""
    try:
        user_id = get_jwt_identity()
        db_path = f'data/user_{user_id}_spotify_data.db'
        
        # Initialize database connection
        db = SpotifyDatabase(db_path)
        
        # Get basic statistics
        stats = {
            'total_tracks': 0,
            'total_artists': 0,
            'total_albums': 0,
            'total_playlists': 0,
            'listening_time_minutes': 0
        }
        
        # Query database for statistics
        try:
            # Count tracks
            tracks_query = "SELECT COUNT(*) FROM tracks"
            stats['total_tracks'] = db.execute_query(tracks_query)[0][0] if db.execute_query(tracks_query) else 0
            
            # Count unique artists
            artists_query = "SELECT COUNT(DISTINCT artist_name) FROM tracks"
            stats['total_artists'] = db.execute_query(artists_query)[0][0] if db.execute_query(artists_query) else 0
            
            # Count unique albums
            albums_query = "SELECT COUNT(DISTINCT album_name) FROM tracks"
            stats['total_albums'] = db.execute_query(albums_query)[0][0] if db.execute_query(albums_query) else 0
            
            # Calculate total listening time
            duration_query = "SELECT SUM(duration_ms) FROM tracks"
            total_duration_ms = db.execute_query(duration_query)[0][0] if db.execute_query(duration_query) else 0
            stats['listening_time_minutes'] = round(total_duration_ms / 60000, 2) if total_duration_ms else 0
            
        except Exception as db_error:
            print(f"Database query error: {db_error}")
            # Return empty stats if database queries fail
            pass
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
