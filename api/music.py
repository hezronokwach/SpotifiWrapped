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

def get_user_database_path(user_id):
    """Get secure database path for user with validation"""
    if not user_id or not isinstance(user_id, str) or len(user_id) < 3:
        raise Exception('Invalid user ID for database access')
    
    # Sanitize user ID to prevent path traversal
    import re
    safe_user_id = re.sub(r'[^a-zA-Z0-9_-]', '', user_id)
    if safe_user_id != user_id:
        raise Exception('User ID contains invalid characters')
    
    return f'/tmp/user_{safe_user_id}_spotify_data.db'

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
    """Initialize SpotifyAPI with strict user isolation and validation"""
    try:
        # Get current user ID from JWT
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        
        # Validate user identity matches JWT claims
        jwt_spotify_user_id = claims.get('spotify_user_id')
        if jwt_spotify_user_id != current_user_id:
            raise Exception('User identity mismatch - security violation')
        
        # Validate session token exists
        user_session_token = claims.get('user_session_token')
        if not user_session_token:
            raise Exception('Missing user session token - security violation')
        
        client_id = claims.get('client_id')
        client_secret = claims.get('client_secret')
        spotify_access_token = claims.get('spotify_access_token')
        redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', 'http://127.0.0.1:3000/auth/callback')

        print(f"🔍 DEBUG: Validated user: {current_user_id}")
        print(f"🔍 DEBUG: Session token: {user_session_token[:8]}...")
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
    """Get user's top tracks with strict user isolation"""
    try:
        print("🔍 DEBUG: Top tracks endpoint called")
        
        # Get and validate user identity
        user_id = get_jwt_identity()
        claims = get_jwt()
        
        # Security validation
        if not user_id or user_id != claims.get('spotify_user_id'):
            print(f"❌ SECURITY: User ID mismatch - JWT: {user_id}, Claims: {claims.get('spotify_user_id')}")
            return jsonify({'error': 'Unauthorized access'}), 403
        
        time_range = request.args.get('time_range', 'medium_term')
        limit = min(int(request.args.get('limit', 20)), 50)

        print(f"🔍 DEBUG: Validated user {user_id} requesting top tracks: time_range={time_range}, limit={limit}")

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
                'track': track.get('track', track.get('name', 'Unknown Track')),  # PRIMARY field for React
                'name': track.get('name', track.get('track', 'Unknown Track')),   # Compatibility field
                'artist': track['artist'],  # SpotifyAPI already processes this as a string
                'album': track['album'],
                'popularity': track['popularity'],
                'duration_ms': track['duration_ms'],
                'preview_url': track.get('preview_url'),
                'external_urls': {'spotify': f"https://open.spotify.com/track/{track['id']}"},  # Construct URL
                'images': [{'url': track['image_url']}] if track.get('image_url') else [],
                'image_url': track.get('image_url', '')  # Add direct image_url field
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
    """Get user's top artists with strict user isolation"""
    try:
        print("🔍 DEBUG: Top artists endpoint called")
        
        # Get and validate user identity
        user_id = get_jwt_identity()
        claims = get_jwt()
        
        # Security validation
        if not user_id or user_id != claims.get('spotify_user_id'):
            print(f"❌ SECURITY: User ID mismatch - JWT: {user_id}, Claims: {claims.get('spotify_user_id')}")
            return jsonify({'error': 'Unauthorized access'}), 403
        
        time_range = request.args.get('time_range', 'medium_term')
        limit = min(int(request.args.get('limit', 20)), 50)

        print(f"🔍 DEBUG: Validated user {user_id} requesting top artists: time_range={time_range}, limit={limit}")

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
                'artist': artist['artist'],  # Keep consistent with React types - PRIMARY field
                'name': artist['artist'],    # Also provide 'name' for compatibility
                'genres': artist['genres'].split(', ') if artist['genres'] != 'Unknown' else [],  # Convert back to list
                'popularity': artist['popularity'],
                'followers': artist['followers'],  # SpotifyAPI already extracts the total
                'external_urls': {'spotify': f"https://open.spotify.com/artist/{artist['id']}"},  # Construct URL
                'images': [{'url': artist['image_url']}] if artist.get('image_url') else [],
                'image_url': artist.get('image_url', '')  # Add direct image_url field
            })
        
        return jsonify({'artists': formatted_artists})
        
    except Exception as e:
        print(f"❌ DEBUG: Top artists error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@music_bp.route('/albums/top')
@jwt_required()
def get_top_albums_endpoint():
    """Get user's top albums with strict user isolation"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        
        # Security validation
        validate_user_access(user_id, claims)
        
        limit = int(request.args.get('limit', 10))

        # Get user-specific database with secure path
        from modules.database import SpotifyDatabase
        db_path = get_user_database_path(user_id)
        user_db = SpotifyDatabase(db_path)

        # Get Spotify API for user
        spotify_api = get_spotify_api_for_user()

        # Use the same function as Dash app
        top_albums_df = get_top_albums(spotify_api, limit=limit, user_db=user_db)

        if top_albums_df.empty:
            return jsonify({'albums': []})

        # Convert DataFrame to list
        albums_list = []
        for _, album in top_albums_df.iterrows():
            albums_list.append({
                'album': album.get('album', 'Unknown Album'),
                'artist': album.get('artist', 'Unknown Artist'),
                'total_count': int(album.get('total_count', 0)),
                'image_url': album.get('image_url', ''),
                'rank': int(album.get('rank', len(albums_list) + 1))
            })

        return jsonify({'albums': albums_list})

    except Exception as e:
        print(f"❌ DEBUG: Top albums error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@music_bp.route('/tracks/saved')
@jwt_required()
def get_saved_tracks():
    """Get user's saved tracks"""
    try:
        user_id = get_jwt_identity()
        limit = min(int(request.args.get('limit', 20)), 50)
        offset = int(request.args.get('offset', 0))
        
        spotify_api = get_spotify_api_for_user()
        saved_tracks_data = spotify_api.get_saved_tracks(limit=limit)

        if not saved_tracks_data:
            return jsonify({'saved_tracks': [], 'total': 0})

        # Format saved tracks
        # Note: SpotifyAPI.get_saved_tracks() returns a list of track dictionaries
        formatted_tracks = []
        for track in saved_tracks_data:
            formatted_tracks.append({
                'id': track.get('id', ''),
                'track': track.get('track', track.get('name', 'Unknown Track')),  # PRIMARY field
                'name': track.get('name', track.get('track', 'Unknown Track')),   # Compatibility
                'artist': track.get('artist', 'Unknown Artist'),
                'album': track.get('album', 'Unknown Album'),
                'duration_ms': track.get('duration_ms', 0),
                'added_at': track.get('added_at', ''),
                'images': [{'url': track.get('image_url', '')}] if track.get('image_url') else [],
                'image_url': track.get('image_url', ''),  # Add direct field
                'external_urls': {'spotify': f"https://open.spotify.com/track/{track.get('id', '')}"}
            })

        return jsonify({
            'saved_tracks': formatted_tracks,
            'total': len(formatted_tracks)
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
        
        spotify_api = get_spotify_api_for_user()
        playlists_data = spotify_api.get_playlists(limit=limit)

        if not playlists_data:
            return jsonify({'playlists': [], 'total': 0})

        # Format playlists
        # Note: SpotifyAPI.get_playlists() returns a list of playlist dictionaries
        formatted_playlists = []
        for playlist in playlists_data:
            formatted_playlists.append({
                'id': playlist.get('id', ''),
                'name': playlist.get('playlist', playlist.get('name', 'Unknown Playlist')),  # Use 'playlist' key first
                'description': playlist.get('description', ''),
                'tracks_total': playlist.get('total_tracks', playlist.get('tracks_total', 0)),  # Use 'total_tracks' key first
                'public': playlist.get('public', True),
                'owner': playlist.get('owner', 'Unknown'),
                'external_urls': {'spotify': f"https://open.spotify.com/playlist/{playlist.get('id', '')}"},
                'images': [{'url': playlist.get('image_url', '')}] if playlist.get('image_url') else [],
                'image_url': playlist.get('image_url', '')  # Add direct field
            })

        return jsonify({
            'playlists': formatted_playlists,
            'total': len(formatted_playlists)
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
        
        if not current_track or not current_track.get('track'):
            return jsonify({'currently_playing': None})
        
        # SpotifyAPI.get_currently_playing() returns processed format, not raw Spotify API
        formatted_track = {
            'id': current_track.get('id', ''),
            'track': current_track.get('track', 'Unknown Track'),  # PRIMARY field
            'name': current_track.get('track', 'Unknown Track'),   # Compatibility
            'artist': current_track.get('artist', 'Unknown Artist'),
            'album': current_track.get('album', 'Unknown Album'),
            'duration_ms': current_track.get('duration_ms', 0),
            'progress_ms': current_track.get('progress_ms', 0),
            'is_playing': current_track.get('is_playing', False),
            'preview_url': current_track.get('preview_url'),
            'external_urls': {'spotify': f"https://open.spotify.com/track/{current_track.get('id', '')}"},
            'images': [{'url': current_track.get('image_url', '')}] if current_track.get('image_url') else [],
            'image_url': current_track.get('image_url', '')
        }
        
        return jsonify({'currently_playing': formatted_track})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@music_bp.route('/refresh-data', methods=['POST'])
@jwt_required()
def refresh_listening_data():
    """Refresh user's listening data from Spotify API"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        
        # Security validation
        validate_user_access(user_id, claims)
        
        # Get user-specific database
        db_path = get_user_database_path(user_id)
        db = SpotifyDatabase(db_path)
        
        # Get Spotify API
        spotify_api = get_spotify_api_for_user()
        
        # Get recent listening data
        recently_played = spotify_api.get_recently_played(limit=50)
        
        if not recently_played:
            return jsonify({
                'message': 'No recent listening data found',
                'updated_count': 0
            })
        
        updated_count = 0
        from datetime import datetime
        
        for track in recently_played:
            try:
                # Save track to database
                db.save_track(track)
                
                # Save listening history
                db.save_listening_history(
                    user_id=user_id,
                    track_id=track['id'],
                    played_at=track.get('played_at', datetime.now().isoformat()),
                    source='recently_played'
                )
                
                updated_count += 1
                
            except Exception as e:
                print(f"Error updating track {track.get('id', 'unknown')}: {e}")
                continue
        
        return jsonify({
            'message': f'Updated {updated_count} recent tracks',
            'updated_count': updated_count
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@music_bp.route('/audio-features/fix', methods=['POST'])
@jwt_required()
def fix_missing_audio_features():
    """Fix missing audio features for existing tracks"""
    try:
        user_id = get_jwt_identity()
        
        # Get user-specific database
        db_path = get_user_database_path(user_id)
        db = SpotifyDatabase(db_path)
        
        # Get Spotify API
        spotify_api = get_spotify_api_for_user()
        
        # Get tracks without audio features
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT track_id, name, artist 
            FROM tracks 
            WHERE energy IS NULL 
            AND track_id NOT LIKE 'genre-%'
            LIMIT 50
        """)
        
        tracks_without_features = cursor.fetchall()
        
        if not tracks_without_features:
            return jsonify({
                'message': 'All tracks already have audio features',
                'updated_count': 0
            })
        
        updated_count = 0
        
        # Get audio features for each track and update database
        for track_id, name, artist in tracks_without_features:
            try:
                # Get audio features using the API method
                audio_features = spotify_api.get_audio_features_safely(track_id)
                
                # Update the track in database
                cursor.execute("""
                    UPDATE tracks SET
                        danceability = ?,
                        energy = ?,
                        key = ?,
                        loudness = ?,
                        mode = ?,
                        speechiness = ?,
                        acousticness = ?,
                        instrumentalness = ?,
                        liveness = ?,
                        valence = ?,
                        tempo = ?
                    WHERE track_id = ?
                """, (
                    audio_features.get('danceability'),
                    audio_features.get('energy'),
                    audio_features.get('key'),
                    audio_features.get('loudness'),
                    audio_features.get('mode'),
                    audio_features.get('speechiness'),
                    audio_features.get('acousticness'),
                    audio_features.get('instrumentalness'),
                    audio_features.get('liveness'),
                    audio_features.get('valence'),
                    audio_features.get('tempo'),
                    track_id
                ))
                
                updated_count += 1
                
            except Exception as e:
                print(f"Error updating audio features for {track_id}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': f'Updated audio features for {updated_count} tracks',
            'updated_count': updated_count
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500