"""
Music data endpoints for tracks, artists, albums, and playlists
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from modules.database import SpotifyDatabase
from modules.api import SpotifyAPI
from modules.top_albums import get_top_albums
import pandas as pd
import os

music_bp = Blueprint('music', __name__)

@music_bp.route('/test')
@jwt_required()
def test_jwt():
    """Test endpoint to check JWT token contents"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()

        return jsonify({
            'user_id': user_id,
            'has_client_id': 'client_id' in claims,
            'has_client_secret': 'client_secret' in claims,
            'has_spotify_access_token': 'spotify_access_token' in claims,
            'claims_keys': list(claims.keys())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_spotify_api_for_user():
    """Initialize SpotifyAPI with user credentials and access token from JWT token"""
    try:
        claims = get_jwt()
        client_id = claims.get('client_id')
        client_secret = claims.get('client_secret')
        spotify_access_token = claims.get('spotify_access_token')
        redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:3000/auth/callback')

        print(f"🔍 DEBUG: JWT claims - client_id: {client_id[:8] if client_id else 'None'}...")
        print(f"🔍 DEBUG: JWT claims - access_token: {'Present' if spotify_access_token else 'Missing'}")

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
            print("✅ DEBUG: Access token set in SpotifyAPI")

        return spotify_api

    except Exception as e:
        print(f"❌ DEBUG: Error initializing SpotifyAPI: {e}")
        raise

@music_bp.route('/tracks/top')
@jwt_required()
def get_top_tracks():
    """Get user's top tracks"""
    try:
        print("🔍 DEBUG: Top tracks endpoint called")
        user_id = get_jwt_identity()
        time_range = request.args.get('time_range', 'medium_term')  # short_term, medium_term, long_term
        limit = min(int(request.args.get('limit', 20)), 50)

        print(f"🔍 DEBUG: Getting top tracks for user: {user_id}, time_range: {time_range}, limit: {limit}")

        spotify_api = get_spotify_api_for_user()
        print("✅ DEBUG: SpotifyAPI initialized for top tracks")

        top_tracks = spotify_api.get_top_tracks(time_range=time_range, limit=limit)
        print(f"🔍 DEBUG: Top tracks response: {top_tracks is not None}")

        if not top_tracks:
            print("⚠️ DEBUG: No top tracks returned")
            return jsonify({'tracks': []})

        print(f"🔍 DEBUG: Top tracks structure: {type(top_tracks)}")

        # Format tracks for frontend
        # Note: SpotifyAPI.get_top_tracks() returns a list of processed tracks, not raw Spotify API format
        formatted_tracks = []
        for track in top_tracks:  # top_tracks is already a list, not a dict with 'items'
            formatted_tracks.append({
                'id': track['id'],
                'name': track['name'],
                'artist': track['artist'],  # SpotifyAPI already processes this as a string
                'album': track['album'],
                'popularity': track['popularity'],
                'duration_ms': track['duration_ms'],
                'preview_url': track.get('preview_url'),
                'external_urls': {'spotify': f"https://open.spotify.com/track/{track['id']}"},  # Construct URL
                'images': [{'url': track['image_url']}] if track.get('image_url') else []
            })
        
        return jsonify({'tracks': formatted_tracks})
        
    except Exception as e:
        print(f"❌ DEBUG: Top tracks error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@music_bp.route('/artists/top')
@jwt_required()
def get_top_artists():
    """Get user's top artists"""
    try:
        print("🔍 DEBUG: Top artists endpoint called")
        user_id = get_jwt_identity()
        time_range = request.args.get('time_range', 'medium_term')
        limit = min(int(request.args.get('limit', 20)), 50)

        print(f"🔍 DEBUG: Getting top artists for user: {user_id}, time_range: {time_range}, limit: {limit}")

        spotify_api = get_spotify_api_for_user()
        print("✅ DEBUG: SpotifyAPI initialized for top artists")

        top_artists = spotify_api.get_top_artists(time_range=time_range, limit=limit)
        print(f"🔍 DEBUG: Top artists response: {top_artists is not None}")

        if not top_artists:
            return jsonify({'artists': []})

        # Format artists for frontend
        # Note: SpotifyAPI.get_top_artists() returns a list of processed artists, not raw Spotify API format
        formatted_artists = []
        for artist in top_artists:  # top_artists is already a list, not a dict with 'items'
            formatted_artists.append({
                'id': artist['id'],
                'name': artist['artist'],  # SpotifyAPI uses 'artist' key for name
                'genres': artist['genres'].split(', ') if artist['genres'] != 'Unknown' else [],  # Convert back to list
                'popularity': artist['popularity'],
                'followers': artist['followers'],  # SpotifyAPI already extracts the total
                'external_urls': {'spotify': f"https://open.spotify.com/artist/{artist['id']}"},  # Construct URL
                'images': [{'url': artist['image_url']}] if artist.get('image_url') else []
            })
        
        return jsonify({'artists': formatted_artists})
        
    except Exception as e:
        print(f"❌ DEBUG: Top artists error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@music_bp.route('/albums/top')
@jwt_required()
def get_top_albums():
    """Get user's top albums from database analysis"""
    try:
        user_id = get_jwt_identity()
        db_path = f'data/user_{user_id}_spotify_data.db'
        
        # Use existing top albums function
        top_albums_data = get_top_albums(db_path, limit=20)
        
        return jsonify({'albums': top_albums_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@music_bp.route('/tracks/saved')
@jwt_required()
def get_saved_tracks():
    """Get user's saved tracks"""
    try:
        user_id = get_jwt_identity()
        limit = min(int(request.args.get('limit', 20)), 50)
        offset = int(request.args.get('offset', 0))
        
        spotify_api = SpotifyAPI()
        saved_tracks = spotify_api.get_saved_tracks(limit=limit, offset=offset)
        
        if not saved_tracks:
            return jsonify({'tracks': []})
        
        # Format saved tracks
        formatted_tracks = []
        for item in saved_tracks['items']:
            track = item['track']
            formatted_tracks.append({
                'id': track['id'],
                'name': track['name'],
                'artist': ', '.join([artist['name'] for artist in track['artists']]),
                'album': track['album']['name'],
                'added_at': item['added_at'],
                'duration_ms': track['duration_ms'],
                'popularity': track['popularity'],
                'preview_url': track.get('preview_url'),
                'external_urls': track['external_urls'],
                'images': track['album']['images']
            })
        
        return jsonify({
            'tracks': formatted_tracks,
            'total': saved_tracks['total'],
            'limit': saved_tracks['limit'],
            'offset': saved_tracks['offset']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@music_bp.route('/playlists')
@jwt_required()
def get_playlists():
    """Get user's playlists"""
    try:
        user_id = get_jwt_identity()
        limit = min(int(request.args.get('limit', 20)), 50)
        offset = int(request.args.get('offset', 0))
        
        spotify_api = SpotifyAPI()
        playlists = spotify_api.get_user_playlists(limit=limit, offset=offset)
        
        if not playlists:
            return jsonify({'playlists': []})
        
        # Format playlists
        formatted_playlists = []
        for playlist in playlists['items']:
            formatted_playlists.append({
                'id': playlist['id'],
                'name': playlist['name'],
                'description': playlist.get('description'),
                'tracks_total': playlist['tracks']['total'],
                'public': playlist['public'],
                'collaborative': playlist['collaborative'],
                'owner': playlist['owner']['display_name'],
                'external_urls': playlist['external_urls'],
                'images': playlist['images']
            })
        
        return jsonify({
            'playlists': formatted_playlists,
            'total': playlists['total'],
            'limit': playlists['limit'],
            'offset': playlists['offset']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@music_bp.route('/tracks/current')
@jwt_required()
def get_current_track():
    """Get currently playing track"""
    try:
        user_id = get_jwt_identity()
        print(f"🔍 DEBUG: Getting current track for user: {user_id}")

        spotify_api = get_spotify_api_for_user()
        print("✅ DEBUG: SpotifyAPI initialized for current track")

        current_track = spotify_api.get_currently_playing()
        print(f"🔍 DEBUG: Current track response: {current_track is not None}")
        
        if not current_track or not current_track.get('item'):
            return jsonify({'currently_playing': None})
        
        track = current_track['item']
        formatted_track = {
            'id': track['id'],
            'name': track['name'],
            'artist': ', '.join([artist['name'] for artist in track['artists']]),
            'album': track['album']['name'],
            'duration_ms': track['duration_ms'],
            'progress_ms': current_track.get('progress_ms', 0),
            'is_playing': current_track.get('is_playing', False),
            'preview_url': track.get('preview_url'),
            'external_urls': track['external_urls'],
            'images': track['album']['images']
        }
        
        return jsonify({'currently_playing': formatted_track})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
