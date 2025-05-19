"""Module for extracting genres from tracks."""
import logging
import time
import sqlite3
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class GenreExtractor:
    def __init__(self, spotify_api, database):
        """Initialize extractor with API and database instances."""
        self.api = spotify_api
        self.db = database
        self.rate_limit_delay = 1  # Base delay between API calls

    def extract_genres_from_recent_tracks(self, max_artists: int = 100):
        """
        Extract genres from recently played tracks.

        Args:
            max_artists: Maximum number of artists to process (default: 100)

        Returns:
            Number of genres extracted
        """
        logger.info(f"Starting genre extraction from recently played tracks (max {max_artists} artists)")

        # Get all unique artists from recently played tracks
        artists = self._get_artists_from_recent_tracks(max_artists)
        logger.info(f"Found {len(artists)} unique artists in recently played tracks")

        # Extract genres for each artist
        genres_count = 0
        for artist_name in artists:
            try:
                # Get artist genres using the API method with longer timeout
                genres = self.api.get_artist_genres(artist_name)

                logger.info(f"Found {len(genres)} genres for artist {artist_name}: {genres}")

                # Save each genre to the database
                for genre in genres:
                    if genre:  # Skip empty genres
                        success = self.db.save_genre(genre, artist_name)
                        if success:
                            genres_count += 1
                            logger.info(f"Saved genre '{genre}' for artist '{artist_name}'")
                        else:
                            logger.warning(f"Failed to save genre '{genre}' for artist '{artist_name}'")

                if not genres:
                    logger.warning(f"No genres found for artist {artist_name}")

                # Add a delay to avoid rate limiting
                self._handle_rate_limit()

            except Exception as e:
                logger.error(f"Error extracting genres for artist {artist_name}: {e}")

        logger.info(f"Extracted and saved {genres_count} genres from {len(artists)} artists")
        return genres_count

    def _get_artists_from_recent_tracks(self, max_artists: int = 100) -> List[str]:
        """
        Get unique artists from recently played tracks.

        Args:
            max_artists: Maximum number of artists to return (default: 100)

        Returns:
            List of unique artist names
        """
        try:
            # Connect to the database
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()

            # Query for unique artists from recently played tracks
            cursor.execute('''
                SELECT DISTINCT t.artist
                FROM listening_history h
                JOIN tracks t ON h.track_id = t.track_id
                WHERE h.source = 'played'
                LIMIT ?
            ''', (max_artists,))

            artists = [row[0] for row in cursor.fetchall()]
            conn.close()

            return artists

        except Exception as e:
            logger.error(f"Error getting artists from recent tracks: {e}")
            return []

    def _handle_rate_limit(self):
        """Handle rate limiting with exponential backoff."""
        time.sleep(self.rate_limit_delay)
        # Increase delay if we're getting close to rate limit
        # Reset it periodically
        if self.rate_limit_delay < 5:  # Max 5 second delay
            self.rate_limit_delay *= 1.5

        # Every 10 calls, add a longer pause to avoid hitting rate limits
        if hasattr(self, '_api_call_count'):
            self._api_call_count += 1
            if self._api_call_count % 10 == 0:
                print(f"Taking a longer break after {self._api_call_count} API calls...")
                time.sleep(5)  # Take a 5-second break every 10 calls
        else:
            self._api_call_count = 1
