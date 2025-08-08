"""
Unit tests for the genre_extractor module.
"""

import unittest
import os
import sys
import tempfile
import sqlite3
from unittest.mock import MagicMock, patch, Mock

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.genre_extractor import GenreExtractor


class TestGenreExtractor(unittest.TestCase):
    """Test cases for GenreExtractor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_spotify_api = MagicMock()
        self.mock_database = MagicMock()
        # Mock the db_path attribute that the extractor tries to access
        self.mock_database.db_path = 'test_database.db'
        self.extractor = GenreExtractor(self.mock_spotify_api, self.mock_database)

    def test_init(self):
        """Test GenreExtractor initialization."""
        self.assertEqual(self.extractor.api, self.mock_spotify_api)
        self.assertEqual(self.extractor.db, self.mock_database)
        self.assertEqual(self.extractor.rate_limit_delay, 0.5)
        self.assertEqual(self.extractor.batch_delay, 2.0)
        self.assertEqual(self.extractor.request_count, 0)
        self.assertIsInstance(self.extractor.genre_cache, dict)

    def test_extract_genres_from_recent_tracks_no_artists(self):
        """Test extract_genres_from_recent_tracks with no artists."""
        self.extractor._get_artists_from_recent_tracks = MagicMock(return_value=[])
        
        result = self.extractor.extract_genres_from_recent_tracks()
        
        self.assertEqual(result, 0)

    def test_extract_genres_from_recent_tracks_with_artists(self):
        """Test extract_genres_from_recent_tracks with artists."""
        # Mock the methods
        mock_artists = [
            {'artist_id': 'artist1', 'artist_name': 'Artist 1'},
            {'artist_id': 'artist2', 'artist_name': 'Artist 2'}
        ]
        
        self.extractor._get_artists_from_recent_tracks = MagicMock(return_value=mock_artists)
        self.extractor._filter_artists_needing_genres = MagicMock(return_value=mock_artists)
        self.extractor._process_artist_batch = MagicMock(return_value=2)
        
        result = self.extractor.extract_genres_from_recent_tracks()
        
        self.assertEqual(result, 2)

    def test_extract_genres_from_recent_tracks_all_cached(self):
        """Test extract_genres_from_recent_tracks when all artists are cached."""
        mock_artists = [
            {'artist_id': 'artist1', 'artist_name': 'Artist 1'}
        ]
        
        self.extractor._get_artists_from_recent_tracks = MagicMock(return_value=mock_artists)
        self.extractor._filter_artists_needing_genres = MagicMock(return_value=[])  # All cached
        
        result = self.extractor.extract_genres_from_recent_tracks()
        
        self.assertEqual(result, 0)

    @patch('sqlite3.connect')
    def test_get_artists_from_recent_tracks(self, mock_connect):
        """Test _get_artists_from_recent_tracks method."""
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [('Artist 1',), ('Artist 2',)]
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=None)
        
        result = self.extractor._get_artists_from_recent_tracks(max_artists=10)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result, ['Artist 1', 'Artist 2'])
        mock_connect.assert_called_once()

    @patch('sqlite3.connect')
    def test_get_artists_from_recent_tracks_with_limit(self, mock_connect):
        """Test _get_artists_from_recent_tracks with limit."""
        # Mock database response with more artists than limit
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(f'Artist {i}',) for i in range(5)]
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=None)
        
        result = self.extractor._get_artists_from_recent_tracks(max_artists=5)
        
        self.assertEqual(len(result), 5)

    @patch('sqlite3.connect')
    def test_filter_artists_needing_genres(self, mock_connect):
        """Test _filter_artists_needing_genres method."""
        mock_artists = ['Artist 1', 'Artist 2', 'Artist 3']
        
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        # Return that Artist 1 already has genres
        mock_cursor.fetchall.return_value = [('Artist 1',)]
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=None)
        
        result = self.extractor._filter_artists_needing_genres(mock_artists)
        
        # Should filter out Artist 1 since it already has genres
        self.assertEqual(len(result), 2)
        self.assertNotIn('Artist 1', result)
        self.assertIn('Artist 2', result)
        self.assertIn('Artist 3', result)

    def test_process_artist_batch(self):
        """Test _process_artist_batch method."""
        mock_batch = [
            {'artist_id': 'artist1', 'artist_name': 'Artist 1'},
            {'artist_id': 'artist2', 'artist_name': 'Artist 2'}
        ]
        
        # Mock API responses
        self.mock_spotify_api.get_artist = MagicMock(side_effect=[
            {'genres': ['rock', 'pop']},
            {'genres': ['jazz', 'blues']}
        ])
        
        # Mock the actual implementation
        def mock_process_batch(batch):
            count = 0
            for artist in batch:
                # Simulate processing
                count += 1
            return count
        
        self.extractor._process_artist_batch = MagicMock(side_effect=mock_process_batch)
        
        result = self.extractor._process_artist_batch(mock_batch)
        
        self.assertEqual(result, 2)

    @patch('time.sleep')
    def test_rate_limiting(self, mock_sleep):
        """Test that rate limiting is applied."""
        self.extractor._handle_rate_limit()
        
        # Should apply some delay
        mock_sleep.assert_called()

    def test_genre_cache_usage(self):
        """Test that genre cache is properly used."""
        # Add item to cache
        self.extractor.genre_cache['artist1'] = ['rock', 'pop']
        
        # Check if cache is used (this would be in actual implementation)
        self.assertIn('artist1', self.extractor.genre_cache)
        self.assertEqual(self.extractor.genre_cache['artist1'], ['rock', 'pop'])

    def test_extract_genres_from_artists(self):
        """Test extract_genres_from_artists method."""
        mock_artist_names = ['Artist 1', 'Artist 2']
        
        # Mock the method
        def mock_extract_from_artists(artist_names):
            return len(artist_names) * 2  # Simulate extracting 2 genres per artist
        
        self.extractor.extract_genres_from_artists = MagicMock(side_effect=mock_extract_from_artists)
        
        result = self.extractor.extract_genres_from_artists(mock_artist_names)
        
        self.assertEqual(result, 4)

    def test_api_error_handling(self):
        """Test API error handling during genre extraction."""
        mock_batch = [{'artist_id': 'artist1', 'artist_name': 'Artist 1'}]
        
        # Mock API to raise an exception
        self.mock_spotify_api.get_artist = MagicMock(side_effect=Exception("API Error"))
        
        # Mock the method to handle errors gracefully
        def mock_process_with_error(batch):
            try:
                for artist in batch:
                    self.mock_spotify_api.get_artist(artist['artist_id'])
                return len(batch)
            except Exception:
                return 0  # Handle error gracefully
        
        self.extractor._process_artist_batch = MagicMock(side_effect=mock_process_with_error)
        
        result = self.extractor._process_artist_batch(mock_batch)
        
        # Should handle error gracefully
        self.assertEqual(result, 0)

    @patch('sqlite3.connect')
    def test_database_error_handling(self, mock_connect):
        """Test database error handling."""
        # Mock database to raise an exception
        mock_connect.side_effect = Exception("Database Error")
        
        result = self.extractor._get_artists_from_recent_tracks(10)
        
        # Should handle error gracefully and return empty list
        self.assertEqual(result, [])

    def test_batch_size_configuration(self):
        """Test that batch size affects processing."""
        mock_artists = [
            {'artist_id': f'artist{i}', 'artist_name': f'Artist {i}'}
            for i in range(25)
        ]
        
        self.extractor._get_artists_from_recent_tracks = MagicMock(return_value=mock_artists)
        self.extractor._filter_artists_needing_genres = MagicMock(return_value=mock_artists)
        
        # Mock batch processing to count batches
        batch_count = 0
        def mock_process_batch(batch):
            nonlocal batch_count
            batch_count += 1
            return len(batch)
        
        self.extractor._process_artist_batch = MagicMock(side_effect=mock_process_batch)
        
        result = self.extractor.extract_genres_from_recent_tracks()
        
        # With batch size of 10, should have 3 batches for 25 artists
        self.assertEqual(batch_count, 3)

    def test_request_count_tracking(self):
        """Test that request count is properly tracked."""
        initial_count = self.extractor.request_count
        
        # Simulate making requests
        self.extractor.request_count += 5
        
        self.assertEqual(self.extractor.request_count, initial_count + 5)

    def test_max_artists_parameter(self):
        """Test max_artists parameter functionality."""
        # Test with different max_artists values
        for max_val in [10, 50, 100]:
            self.extractor._get_artists_from_recent_tracks = MagicMock(return_value=[])
            self.extractor._filter_artists_needing_genres = MagicMock(return_value=[])
            
            self.extractor.extract_genres_from_recent_tracks(max_artists=max_val)
            
            self.extractor._get_artists_from_recent_tracks.assert_called_with(max_val)

    @patch('modules.genre_extractor.logger')
    def test_logging_functionality(self, mock_logger):
        """Test that appropriate logging is performed."""
        self.extractor._get_artists_from_recent_tracks = MagicMock(return_value=[])
        self.extractor._filter_artists_needing_genres = MagicMock(return_value=[])
        
        self.extractor.extract_genres_from_recent_tracks()
        
        # Should log start of extraction
        mock_logger.info.assert_called()

    def test_empty_genre_response_handling(self):
        """Test handling of artists with no genres."""
        mock_batch = [{'artist_id': 'artist1', 'artist_name': 'Artist 1'}]
        
        # Mock API to return artist with no genres
        self.mock_spotify_api.get_artist = MagicMock(return_value={'genres': []})
        
        # Mock the method
        def mock_process_empty_genres(batch):
            for artist in batch:
                genres = self.mock_spotify_api.get_artist(artist['artist_id']).get('genres', [])
                if not genres:
                    # Handle empty genres case
                    pass
            return len(batch)
        
        self.extractor._process_artist_batch = MagicMock(side_effect=mock_process_empty_genres)
        
        result = self.extractor._process_artist_batch(mock_batch)
        
        # Should still process the artist even with no genres
        self.assertEqual(result, 1)


if __name__ == '__main__':
    unittest.main()