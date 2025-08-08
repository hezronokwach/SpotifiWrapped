"""
Unit tests for the database module.
"""

import unittest
import os
import sys
import tempfile
import sqlite3
from unittest.mock import patch, MagicMock

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.database import SpotifyDatabase


class TestSpotifyDatabase(unittest.TestCase):
    """Test cases for SpotifyDatabase class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = SpotifyDatabase(db_path=self.temp_db.name)

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_init_creates_database(self):
        """Test that database initialization creates the file."""
        self.assertTrue(os.path.exists(self.temp_db.name))

    def test_ensure_tables_exist(self):
        """Test that ensure_tables_exist creates necessary tables."""
        self.db.ensure_tables_exist()
        
        # Check that tables exist
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['users', 'tracks', 'listening_history', 'genres', 'collection_status']
        for table in expected_tables:
            self.assertIn(table, tables)
        
        conn.close()

    def test_save_user_valid_data(self):
        """Test save_user with valid user data."""
        user_data = {
            'id': 'user123',
            'display_name': 'Test User',
            'followers': 100
        }
        
        # Should not raise an exception
        self.db.save_user(user_data)
        
        # Verify user was saved
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_data['id'],))
        result = cursor.fetchone()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], user_data['id'])  # user_id
        self.assertEqual(result[1], user_data['display_name'])  # display_name
        
        conn.close()

    def test_save_user_missing_optional_fields(self):
        """Test save_user with missing optional fields."""
        user_data = {
            'id': 'user123'
            # missing display_name and followers
        }
        
        # Should not raise an exception
        self.db.save_user(user_data)
        
        # Verify user was saved with defaults
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute("SELECT display_name, followers FROM users WHERE user_id = ?", (user_data['id'],))
        result = cursor.fetchone()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'Unknown')  # default display_name
        self.assertEqual(result[1], 0)  # default followers
        
        conn.close()

    def test_save_track_valid_data(self):
        """Test save_track with valid track data."""
        track_data = {
            'id': 'track123',
            'name': 'Test Track',
            'artists': [{'name': 'Test Artist'}],
            'album': {'name': 'Test Album'},
            'duration_ms': 240000,
            'popularity': 80,
            'release_date': '2023-01-01'
        }
        
        # Should not raise an exception
        self.db.save_track(track_data)
        
        # Verify track was saved
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tracks WHERE track_id = ?", (track_data['id'],))
        result = cursor.fetchone()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], track_data['id'])  # track_id
        self.assertEqual(result[1], track_data['name'])  # track_name
        
        conn.close()

    def test_save_track_missing_id(self):
        """Test save_track with missing track ID."""
        track_data = {
            'name': 'Test Track'
            # missing 'id'
        }
        
        # Should handle missing ID gracefully
        self.db.save_track(track_data)
        
        # Since there's no ID, track should not be saved
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tracks")
        count = cursor.fetchone()[0]
        
        self.assertEqual(count, 0)
        
        conn.close()

    def test_save_listening_history_valid_data(self):
        """Test save_listening_history with valid data."""
        user_id = 'user123'
        track_id = 'track123'
        played_at = '2023-01-01T10:30:00'
        
        # First save a user and track
        self.db.save_user({'id': user_id, 'display_name': 'Test User'})
        self.db.save_track({'id': track_id, 'name': 'Test Track'})
        
        # Save listening history
        self.db.save_listening_history(user_id, track_id, played_at)
        
        # Verify listening history was saved
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM listening_history WHERE user_id = ? AND track_id = ?", 
                      (user_id, track_id))
        result = cursor.fetchone()
        
        self.assertIsNotNone(result)
        # result columns: history_id, user_id, track_id, played_at, source
        self.assertEqual(result[1], user_id)  # user_id is column 1
        self.assertEqual(result[2], track_id)  # track_id is column 2
        
        conn.close()

    def test_get_collection_status_existing_user(self):
        """Test get_collection_status for existing user."""
        user_id = 'user123'
        
        # Save a user first
        self.db.save_user({'id': user_id, 'display_name': 'Test User'})
        
        # Get collection status
        result = self.db.get_collection_status(user_id)
        
        self.assertIsInstance(result, dict)
        self.assertIn('last_collection', result)
        self.assertIn('earliest_known', result)
        self.assertIn('latest_known', result)

    def test_get_collection_status_nonexistent_user(self):
        """Test get_collection_status for nonexistent user."""
        result = self.db.get_collection_status('nonexistent_user')
        
        # Should return None for nonexistent user
        self.assertIsNone(result)

    def test_get_listening_history_valid_user(self):
        """Test get_listening_history for valid user."""
        user_id = 'user123'
        track_id = 'track123'
        played_at = '2023-01-01T10:30:00'
        
        # Set up test data
        self.db.save_user({'id': user_id, 'display_name': 'Test User'})
        self.db.save_track({'id': track_id, 'name': 'Test Track', 'artists': [{'name': 'Test Artist'}]})
        self.db.save_listening_history(user_id, track_id, played_at)
        
        # Get listening history
        result = self.db.get_listening_history(user_id)
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        # Check that we have the expected fields (played_at, name, artist, album, source)
        first_record = result[0]
        self.assertIn('played_at', first_record)
        self.assertIn('name', first_record)  
        self.assertIn('artist', first_record)
        self.assertIn('album', first_record)

    def test_get_listening_history_empty_user(self):
        """Test get_listening_history for user with no history."""
        result = self.db.get_listening_history('empty_user')
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_save_genre_valid_data(self):
        """Test save_genre with valid genre data."""
        genre_name = 'rock'
        artist_name = 'Test Artist'
        
        # Should not raise an exception
        self.db.save_genre(genre_name, artist_name)
        
        # Verify genre was saved
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM genres WHERE genre_name = ?", (genre_name,))
        result = cursor.fetchone()
        
        self.assertIsNotNone(result)
        # The result should contain the genre data
        self.assertEqual(result[1], genre_name)  # genre_name is in column 1
        
        conn.close()

    def test_get_top_genres_with_data(self):
        """Test get_top_genres with existing genre data."""
        # Add some test genres
        self.db.save_genre('rock', 'Artist 1')
        self.db.save_genre('pop', 'Artist 2')
        self.db.save_genre('rock', 'Artist 3')  # Duplicate genre
        
        result = self.db.get_top_genres(limit=5)
        
        self.assertIsInstance(result, list)
        # Should have genres with counts
        if len(result) > 0:
            self.assertIn('genre', result[0])  # Database returns 'genre', not 'genre_name'
            self.assertIn('count', result[0])

    def test_get_top_genres_empty_database(self):
        """Test get_top_genres with no genre data."""
        result = self.db.get_top_genres()
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_cleanup_listening_history_valid_user(self):
        """Test cleanup_listening_history for valid user."""
        user_id = 'user123'
        
        # Create some test data
        self.db.save_user({'id': user_id, 'display_name': 'Test User'})
        
        result = self.db.cleanup_listening_history(user_id)
        
        self.assertIsInstance(result, dict)
        # Check for actual fields returned by cleanup method
        self.assertIn('initial_count', result)
        self.assertIn('final_count', result)
        self.assertIn('total_removed', result)

    def test_get_listening_statistics_valid_user(self):
        """Test get_listening_statistics for valid user."""
        user_id = 'user123'
        track_id = 'track123'
        played_at = '2023-01-01T10:30:00'
        
        # Set up test data
        self.db.save_user({'id': user_id, 'display_name': 'Test User'})
        self.db.save_track({
            'id': track_id, 
            'name': 'Test Track', 
            'artists': [{'name': 'Test Artist'}],
            'duration_ms': 240000
        })
        self.db.save_listening_history(user_id, track_id, played_at)
        
        result = self.db.get_listening_statistics(user_id)
        
        self.assertIsInstance(result, dict)
        # Check for actual fields returned by get_listening_statistics
        self.assertIn('total_plays', result)
        self.assertIn('unique_tracks', result)
        self.assertIn('unique_artists', result)
        self.assertIn('total_minutes', result)
        self.assertIn('total_hours', result)
        self.assertIn('average_track_minutes', result)

    def test_get_listening_statistics_no_data(self):
        """Test get_listening_statistics for user with no data."""
        result = self.db.get_listening_statistics('empty_user')
        
        expected = {
            'total_plays': 0,
            'unique_tracks': 0,
            'unique_artists': 0,
            'total_minutes': 0.0,
            'total_hours': 0.0,
            'average_track_minutes': 0.0
        }
        
        self.assertEqual(result, expected)

    @patch('modules.database.logger')
    def test_database_error_handling(self, mock_logger):
        """Test database error handling and logging."""
        # Close the database to cause an error
        if os.path.exists(self.temp_db.name):
            os.chmod(self.temp_db.name, 0o000)  # Remove all permissions
        
        try:
            # This should trigger an error and log it
            with self.assertRaises(Exception):
                self.db.save_user({'id': 'test'})
        finally:
            # Restore permissions for cleanup
            if os.path.exists(self.temp_db.name):
                os.chmod(self.temp_db.name, 0o666)


if __name__ == '__main__':
    unittest.main()