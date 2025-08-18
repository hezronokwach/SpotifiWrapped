"""
Analytics endpoints for audio features, genres, and listening patterns
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from modules.database import SpotifyDatabase
from modules.api import SpotifyAPI
from modules.genre_extractor import GenreExtractor
from modules.data_processing import DataProcessor
import pandas as pd
import json

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/audio-features')
@jwt_required()
def get_audio_features():
    """Get audio features analysis for user's top tracks"""
    try:
        user_id = get_jwt_identity()
        time_range = request.args.get('time_range', 'medium_term')
        
        spotify_api = SpotifyAPI()
        
        # Get top tracks
        top_tracks = spotify_api.get_top_tracks(time_range=time_range, limit=50)
        if not top_tracks or not top_tracks['items']:
            return jsonify({'audio_features': {}})
        
        # Get audio features for tracks
        track_ids = [track['id'] for track in top_tracks['items']]
        audio_features = spotify_api.get_audio_features(track_ids)
        
        if not audio_features:
            return jsonify({'audio_features': {}})
        
        # Calculate average features
        features_sum = {
            'danceability': 0,
            'energy': 0,
            'speechiness': 0,
            'acousticness': 0,
            'instrumentalness': 0,
            'liveness': 0,
            'valence': 0,
            'tempo': 0
        }
        
        valid_features = 0
        for feature in audio_features:
            if feature:  # Skip None values
                for key in features_sum.keys():
                    features_sum[key] += feature.get(key, 0)
                valid_features += 1
        
        # Calculate averages
        if valid_features > 0:
            avg_features = {key: round(value / valid_features, 3) for key, value in features_sum.items()}
        else:
            avg_features = features_sum
        
        return jsonify({
            'audio_features': avg_features,
            'tracks_analyzed': valid_features
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/genres')
@jwt_required()
def get_genres():
    """Get genre analysis from user's listening history"""
    try:
        user_id = get_jwt_identity()
        db_path = f'data/user_{user_id}_spotify_data.db'
        
        # Use existing genre extractor
        genre_extractor = GenreExtractor(db_path)
        genre_data = genre_extractor.get_genre_distribution()
        
        return jsonify({'genres': genre_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/patterns')
@jwt_required()
def get_listening_patterns():
    """Get listening patterns analysis"""
    try:
        user_id = get_jwt_identity()
        db_path = f'data/user_{user_id}_spotify_data.db'
        
        # Initialize database
        db = SpotifyDatabase(db_path)
        
        # Get listening patterns by hour and day
        patterns_query = """
        SELECT 
            strftime('%H', played_at) as hour,
            strftime('%w', played_at) as day_of_week,
            COUNT(*) as play_count
        FROM tracks 
        WHERE played_at IS NOT NULL
        GROUP BY hour, day_of_week
        ORDER BY day_of_week, hour
        """
        
        results = db.execute_query(patterns_query)
        
        # Format data for heatmap
        patterns = {}
        for row in results:
            hour, day, count = row
            if day not in patterns:
                patterns[day] = {}
            patterns[day][hour] = count
        
        # Convert to format expected by frontend
        heatmap_data = []
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        
        for day_num in range(7):
            day_name = days[day_num]
            for hour in range(24):
                count = patterns.get(str(day_num), {}).get(f'{hour:02d}', 0)
                heatmap_data.append({
                    'day': day_name,
                    'hour': hour,
                    'count': count
                })
        
        return jsonify({
            'listening_patterns': heatmap_data,
            'summary': {
                'total_plays': sum(row[2] for row in results),
                'most_active_hour': max(results, key=lambda x: x[2])[0] if results else None,
                'most_active_day': max(results, key=lambda x: x[2])[1] if results else None
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/wrapped')
@jwt_required()
def get_wrapped_summary():
    """Get Spotify Wrapped-style summary"""
    try:
        user_id = get_jwt_identity()
        db_path = f'data/user_{user_id}_spotify_data.db'
        
        # Initialize components
        db = SpotifyDatabase(db_path)
        spotify_api = SpotifyAPI()
        
        # Get top tracks and artists from API
        top_tracks = spotify_api.get_top_tracks(time_range='long_term', limit=5)
        top_artists = spotify_api.get_top_artists(time_range='long_term', limit=5)
        
        # Get database statistics
        stats_queries = {
            'total_minutes': "SELECT SUM(duration_ms) / 60000 FROM tracks",
            'total_tracks': "SELECT COUNT(*) FROM tracks",
            'unique_artists': "SELECT COUNT(DISTINCT artist_name) FROM tracks",
            'unique_albums': "SELECT COUNT(DISTINCT album_name) FROM tracks"
        }
        
        stats = {}
        for key, query in stats_queries.items():
            result = db.execute_query(query)
            stats[key] = result[0][0] if result and result[0][0] else 0
        
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
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'play_count': 'N/A'  # Would need play count from database
                }
                for track in (top_tracks['items'] if top_tracks else [])
            ],
            'top_artists': [
                {
                    'name': artist['name'],
                    'genres': artist['genres'][:3],  # Top 3 genres
                    'play_count': 'N/A'  # Would need play count from database
                }
                for artist in (top_artists['items'] if top_artists else [])
            ]
        }
        
        return jsonify({'wrapped': wrapped_summary})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
