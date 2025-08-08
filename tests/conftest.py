"""
Test configuration and shared fixtures for SpotifiWrapped tests.
"""

import os
import sys
import tempfile
import shutil
from unittest.mock import MagicMock

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestConfig:
    """Test configuration settings."""
    
    # Test database settings
    TEST_DB_NAME = 'test_spotify.db'
    
    # Sample data settings
    DEFAULT_TRACK_LIMIT = 10
    DEFAULT_ARTIST_LIMIT = 5
    DEFAULT_HISTORY_DAYS = 30
    
    # Test timeout settings
    API_TIMEOUT = 30
    DATABASE_TIMEOUT = 10
    
    # Mock data settings
    MOCK_USER_ID = 'test_user_123'
    MOCK_USER_NAME = 'Test User'
    MOCK_TRACK_ID = 'test_track_123'
    MOCK_ARTIST_ID = 'test_artist_123'


class TestFixtures:
    """Reusable test fixtures and mock data."""
    
    @staticmethod
    def create_mock_spotify_api():
        """Create a mock Spotify API instance."""
        mock_api = MagicMock()
        
        # Mock user profile
        mock_api.get_current_user_profile.return_value = {
            'id': TestConfig.MOCK_USER_ID,
            'display_name': TestConfig.MOCK_USER_NAME,
            'followers': 100,
            'country': 'US'
        }
        
        # Mock top tracks
        mock_api.get_current_user_top_tracks.return_value = {
            'items': [
                {
                    'id': f'{TestConfig.MOCK_TRACK_ID}_{i}',
                    'name': f'Test Track {i}',
                    'artists': [{'name': f'Test Artist {i}'}],
                    'album': {'name': f'Test Album {i}'},
                    'duration_ms': 240000,
                    'popularity': 80
                }
                for i in range(5)
            ]
        }
        
        # Mock top artists
        mock_api.get_current_user_top_artists.return_value = {
            'items': [
                {
                    'id': f'{TestConfig.MOCK_ARTIST_ID}_{i}',
                    'name': f'Test Artist {i}',
                    'genres': ['pop', 'rock'],
                    'popularity': 75,
                    'followers': {'total': 50000}
                }
                for i in range(3)
            ]
        }
        
        # Mock recently played
        mock_api.get_current_user_recently_played.return_value = {
            'items': [
                {
                    'track': {
                        'id': f'{TestConfig.MOCK_TRACK_ID}_recent_{i}',
                        'name': f'Recent Track {i}',
                        'artists': [{'name': f'Recent Artist {i}'}],
                        'album': {'name': f'Recent Album {i}'},
                        'duration_ms': 180000
                    },
                    'played_at': f'2023-01-0{i+1}T10:00:00Z'
                }
                for i in range(3)
            ]
        }
        
        # Mock audio features
        mock_api.get_audio_features.return_value = {
            'audio_features': [
                {
                    'id': f'{TestConfig.MOCK_TRACK_ID}_{i}',
                    'danceability': 0.7,
                    'energy': 0.8,
                    'valence': 0.6,
                    'tempo': 120.0,
                    'loudness': -5.0,
                    'speechiness': 0.1,
                    'acousticness': 0.2,
                    'instrumentalness': 0.0,
                    'liveness': 0.1
                }
                for i in range(3)
            ]
        }
        
        return mock_api
    
    @staticmethod
    def create_mock_database():
        """Create a mock database instance."""
        mock_db = MagicMock()
        
        # Mock database methods
        mock_db.save_user.return_value = None
        mock_db.save_track.return_value = None
        mock_db.save_listening_history.return_value = None
        
        mock_db.get_collection_status.return_value = {
            'last_collection_timestamp': '2023-01-01T10:00:00',
            'total_tracks_collected': 10,
            'last_listening_history_update': '2023-01-01T10:00:00',
            'total_listening_history': 50
        }
        
        mock_db.get_listening_history.return_value = [
            {
                'track_id': f'{TestConfig.MOCK_TRACK_ID}_history_{i}',
                'track_name': f'History Track {i}',
                'artist_name': f'History Artist {i}',
                'played_at': f'2023-01-0{i+1}T10:00:00',
                'duration_ms': 200000
            }
            for i in range(5)
        ]
        
        mock_db.get_listening_statistics.return_value = {
            'total_tracks': 50,
            'unique_tracks': 45,
            'unique_artists': 25,
            'total_listening_time_minutes': 180.0,
            'average_track_length_minutes': 3.6,
            'most_played_track': 'Favorite Song',
            'most_played_artist': 'Favorite Artist'
        }
        
        mock_db.get_top_genres.return_value = [
            {'genre_name': 'pop', 'count': 15},
            {'genre_name': 'rock', 'count': 12},
            {'genre_name': 'electronic', 'count': 8}
        ]
        
        return mock_db
    
    @staticmethod
    def create_sample_track_data():
        """Create sample track data for testing."""
        return {
            'id': TestConfig.MOCK_TRACK_ID,
            'name': 'Sample Track',
            'artists': [{'name': 'Sample Artist'}],
            'album': {'name': 'Sample Album'},
            'duration_ms': 240000,
            'popularity': 85,
            'release_date': '2023-01-01'
        }
    
    @staticmethod
    def create_sample_artist_data():
        """Create sample artist data for testing."""
        return {
            'id': TestConfig.MOCK_ARTIST_ID,
            'name': 'Sample Artist',
            'genres': ['pop', 'indie'],
            'popularity': 75,
            'followers': {'total': 100000}
        }
    
    @staticmethod
    def create_sample_user_data():
        """Create sample user data for testing."""
        return {
            'id': TestConfig.MOCK_USER_ID,
            'display_name': TestConfig.MOCK_USER_NAME,
            'followers': 150,
            'country': 'US'
        }
    
    @staticmethod
    def create_sample_audio_features():
        """Create sample audio features data for testing."""
        return {
            'id': TestConfig.MOCK_TRACK_ID,
            'danceability': 0.75,
            'energy': 0.85,
            'valence': 0.65,
            'tempo': 128.0,
            'loudness': -4.5,
            'speechiness': 0.05,
            'acousticness': 0.15,
            'instrumentalness': 0.02,
            'liveness': 0.12,
            'key': 7,
            'mode': 1,
            'time_signature': 4
        }


class TestUtils:
    """Utility functions for testing."""
    
    @staticmethod
    def create_temp_directory():
        """Create a temporary directory for testing."""
        return tempfile.mkdtemp()
    
    @staticmethod
    def cleanup_temp_directory(temp_dir):
        """Clean up a temporary directory."""
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    @staticmethod
    def assert_dict_subset(subset, superset, msg=None):
        """Assert that subset is a subset of superset."""
        for key, value in subset.items():
            if key not in superset:
                raise AssertionError(f"Key '{key}' not found in superset")
            if superset[key] != value:
                raise AssertionError(f"Value for key '{key}' differs: expected {value}, got {superset[key]}")
    
    @staticmethod
    def assert_valid_timestamp(timestamp_str):
        """Assert that a string is a valid ISO timestamp."""
        from datetime import datetime
        try:
            datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except ValueError:
            raise AssertionError(f"Invalid timestamp format: {timestamp_str}")
    
    @staticmethod
    def assert_audio_features_valid(features):
        """Assert that audio features are within valid ranges."""
        for feature_name, (min_val, max_val) in {
            'danceability': (0.0, 1.0),
            'energy': (0.0, 1.0),
            'valence': (0.0, 1.0),
            'speechiness': (0.0, 1.0),
            'acousticness': (0.0, 1.0),
            'instrumentalness': (0.0, 1.0),
            'liveness': (0.0, 1.0),
            'loudness': (-60.0, 0.0),
            'tempo': (0.0, 300.0)
        }.items():
            if feature_name in features:
                value = features[feature_name]
                if not (min_val <= value <= max_val):
                    raise AssertionError(
                        f"Audio feature '{feature_name}' value {value} "
                        f"not in valid range [{min_val}, {max_val}]"
                    )


# Global test configuration instance
test_config = TestConfig()
test_fixtures = TestFixtures()
test_utils = TestUtils()