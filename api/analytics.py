"""
Analytics endpoints for audio features, genres, and listening patterns
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from modules.database import SpotifyDatabase
from modules.api import SpotifyAPI
import pandas as pd
import json
import os
import sqlite3

analytics_bp = Blueprint('analytics', __name__)

def get_user_spotify_api():
    """Get SpotifyAPI instance for current user - simplified version"""
    try:
        claims = get_jwt()
        client_id = claims.get('client_id')
        client_secret = claims.get('client_secret')
        spotify_access_token = claims.get('spotify_access_token')
        redirect_uri = 'http://127.0.0.1:3000/auth/callback'

        if not all([client_id, client_secret, spotify_access_token]):
            print(f"❌ Missing credentials for SpotifyAPI")
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

@analytics_bp.route('/audio-features')
@jwt_required()
def get_audio_features():
    """Get audio features analysis for user's top tracks"""
    try:
        print("🔍 DEBUG: Starting audio features endpoint...")
        user_id = get_jwt_identity()
        time_range = request.args.get('time_range', 'medium_term')
        print(f"🔍 DEBUG: User ID: {user_id}, Time range: {time_range}")

        # Get user-specific SpotifyAPI instance
        spotify_api = get_user_spotify_api()
        if not spotify_api:
            print("❌ DEBUG: Could not get SpotifyAPI instance")
            return jsonify({'audio_features': {}})

        print("✅ DEBUG: SpotifyAPI instance created")

        # Get top tracks using the same method as original (limit 5 for performance)
        top_tracks = spotify_api.get_top_tracks(time_range=time_range, limit=5)
        if not top_tracks:
            return jsonify({'audio_features': {}})

        # Process tracks individually using get_audio_features_safely like original
        audio_features_data = []
        track_details = []

        for track in top_tracks:
            if track.get('id'):
                # Use the safe method like the original implementation
                features = spotify_api.get_audio_features_safely(track['id'])
                if features:
                    # Store individual track data for display
                    track_info = {
                        'track': track.get('track', track.get('name', 'Unknown')),
                        'artist': track.get('artist', 'Unknown'),
                        'danceability': features.get('danceability', 0),
                        'energy': features.get('energy', 0),
                        'speechiness': features.get('speechiness', 0),
                        'acousticness': features.get('acousticness', 0),
                        'instrumentalness': features.get('instrumentalness', 0),
                        'liveness': features.get('liveness', 0),
                        'valence': features.get('valence', 0),
                        'tempo': features.get('tempo', 0)
                    }

                    audio_features_data.append(track_info)
                    track_details.append({
                        'track': track_info['track'],
                        'artist': track_info['artist']
                    })

        if not audio_features_data:
            return jsonify({'audio_features': {}, 'tracks': [], 'tracks_analyzed': 0})

        # Calculate averages like the original
        features_to_analyze = ['danceability', 'energy', 'speechiness', 'acousticness',
                              'instrumentalness', 'liveness', 'valence', 'tempo']

        averages = {}
        for feature in features_to_analyze:
            values = [track[feature] for track in audio_features_data if track.get(feature) is not None]
            averages[feature] = round(sum(values) / len(values), 3) if values else 0

        return jsonify({
            'audio_features': averages,
            'tracks': track_details,
            'tracks_analyzed': len(audio_features_data)
        })
        
    except Exception as e:
        print(f"❌ DEBUG: Audio features error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/genres')
@jwt_required()
def get_genres():
    """Get genre analysis from user's listening history - based on original Dash implementation"""
    try:
        user_id = get_jwt_identity()
        db_path = f'data/user_{user_id}_spotify_data.db'

        # Check if database exists and has genre data (like original)
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM genres")
                total_genres = cursor.fetchone()[0]

                if total_genres > 0:
                    # Use simple fallback query like original
                    cursor.execute('''
                        SELECT genre_name as genre, SUM(count) as count
                        FROM genres
                        WHERE genre_name IS NOT NULL AND genre_name != ''
                        GROUP BY genre_name
                        ORDER BY count DESC
                        LIMIT 10
                    ''')
                    results = cursor.fetchall()
                    if results:
                        genre_data = {row[0]: row[1] for row in results}
                        return jsonify({'genres': genre_data})
        except sqlite3.Error:
            pass  # Fall through to API method

        # Fallback: Get genres from top artists via API (like original)
        spotify_api = get_user_spotify_api()
        if not spotify_api:
            return jsonify({'genres': {}})

        # Get top artists and extract genres
        top_artists = spotify_api.get_top_artists(limit=20)
        if not top_artists:
            return jsonify({'genres': {}})

        # Count genres from top artists
        genre_counts = {}
        for artist in top_artists:
            genres = artist.get('genres', '')
            if genres and genres != 'Unknown':
                # Handle both string and list formats
                if isinstance(genres, str):
                    genre_list = genres.split(', ')
                else:
                    genre_list = genres

                for genre in genre_list:
                    genre = genre.strip()
                    if genre:
                        genre_counts[genre] = genre_counts.get(genre, 0) + 1

        return jsonify({'genres': genre_counts})

    except Exception as e:
        print(f"❌ Genres error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/patterns')
@jwt_required()
def get_listening_patterns():
    """Get listening patterns analysis - based on original Dash implementation"""
    try:
        user_id = get_jwt_identity()
        db_path = f'data/user_{user_id}_spotify_data.db'

        # Use direct SQLite connection like original
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # Use the exact same query as original Dash app
                cursor.execute('''
                    SELECT
                        strftime('%w', datetime(played_at, 'localtime')) as day_of_week,
                        strftime('%H', datetime(played_at, 'localtime')) as hour_of_day,
                        COUNT(*) as play_count
                    FROM listening_history h
                    JOIN tracks t ON h.track_id = t.track_id
                    WHERE h.user_id = ?
                    AND h.played_at IS NOT NULL
                    AND h.source IN ('played', 'recently_played', 'current')
                    AND datetime(h.played_at) <= datetime('now')
                    AND datetime(h.played_at) >= datetime('now', '-7 days')
                    GROUP BY day_of_week, hour_of_day
                    ORDER BY day_of_week, hour_of_day
                ''', (user_id,))

                results = cursor.fetchall()

                if not results:
                    # Return empty pattern data
                    return jsonify({
                        'listening_patterns': [],
                        'summary': {
                            'total_plays': 0,
                            'most_active_hour': None,
                            'most_active_day': None
                        }
                    })

                # Format data for heatmap like original
                heatmap_data = []
                days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

                # Create lookup for existing data
                patterns_lookup = {}
                for day_of_week, hour_of_day, play_count in results:
                    patterns_lookup[(int(day_of_week), int(hour_of_day))] = play_count

                # Generate complete heatmap data (7 days x 24 hours)
                for day_num in range(7):
                    for hour in range(24):
                        count = patterns_lookup.get((day_num, hour), 0)
                        heatmap_data.append({
                            'day': days[day_num],
                            'day_num': day_num,
                            'hour': hour,
                            'count': count
                        })

                # Calculate summary stats
                total_plays = sum(row[2] for row in results)
                most_active = max(results, key=lambda x: x[2]) if results else None

                return jsonify({
                    'listening_patterns': heatmap_data,
                    'summary': {
                        'total_plays': total_plays,
                        'most_active_hour': int(most_active[1]) if most_active else None,
                        'most_active_day': days[int(most_active[0])] if most_active else None
                    }
                })

        except sqlite3.Error as e:
            print(f"Database error in listening patterns: {e}")
            return jsonify({
                'listening_patterns': [],
                'summary': {
                    'total_plays': 0,
                    'most_active_hour': None,
                    'most_active_day': None
                }
            })

    except Exception as e:
        print(f"❌ Listening patterns error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/wrapped')
@jwt_required()
def get_wrapped_summary():
    """Get Spotify Wrapped-style summary"""
    try:
        user_id = get_jwt_identity()
        db_path = f'data/user_{user_id}_spotify_data.db'
        
        # Initialize components
        spotify_api = get_user_spotify_api()
        if not spotify_api:
            return jsonify({'wrapped': {'listening_stats': {'total_minutes_listened': 0, 'total_tracks_played': 0, 'unique_artists_discovered': 0, 'unique_albums_explored': 0}, 'top_tracks': [], 'top_artists': []}})

        # Get top tracks and artists from API
        top_tracks = spotify_api.get_top_tracks(time_range='long_term', limit=5)
        top_artists = spotify_api.get_top_artists(time_range='long_term', limit=5)
        
        # Get database statistics
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        stats = {}
        try:
            # Get total listening time in minutes
            cursor.execute("SELECT SUM(duration_ms) / 60000 FROM tracks")
            result = cursor.fetchone()
            stats['total_minutes'] = result[0] if result and result[0] else 0

            # Get total tracks
            cursor.execute("SELECT COUNT(*) FROM tracks")
            result = cursor.fetchone()
            stats['total_tracks'] = result[0] if result and result[0] else 0

            # Get unique artists
            cursor.execute("SELECT COUNT(DISTINCT artist) FROM tracks")
            result = cursor.fetchone()
            stats['unique_artists'] = result[0] if result and result[0] else 0

            # Get unique albums
            cursor.execute("SELECT COUNT(DISTINCT album) FROM tracks")
            result = cursor.fetchone()
            stats['unique_albums'] = result[0] if result and result[0] else 0

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            stats = {'total_minutes': 0, 'total_tracks': 0, 'unique_artists': 0, 'unique_albums': 0}
        finally:
            conn.close()
        
        # Format wrapped summary
        wrapped_summary = {
            'listening_stats': {
                'total_minutes_listened': round(stats['total_minutes'], 0),
                'total_tracks_played': stats['total_tracks'],
                'unique_artists_discovered': stats['unique_artists'],
                'unique_albums_explored': stats['unique_albums']
            },
            'top_tracks': [
                {
                    'name': track['name'],
                    'artist': track['artist'],  # SpotifyAPI already processes this as a string
                    'play_count': 'N/A'  # Would need play count from database
                }
                for track in (top_tracks if top_tracks else [])
            ],
            'top_artists': [
                {
                    'name': artist['artist'],  # SpotifyAPI uses 'artist' key for name
                    'genres': artist['genres'].split(', ') if artist['genres'] != 'Unknown' else [],  # Convert back to list
                    'play_count': 'N/A'  # Would need play count from database
                }
                for artist in (top_artists if top_artists else [])
            ]
        }
        
        return jsonify({'wrapped': wrapped_summary})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
