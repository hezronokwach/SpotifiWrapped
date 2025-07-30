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
        self.rate_limit_delay = 0.5  # Reduced base delay between API calls
        self.batch_delay = 2.0  # Reduced delay every few requests
        self.request_count = 0  # Track number of requests made
        self.genre_cache = {}  # Cache for artist genres to avoid duplicate API calls

    def extract_genres_from_recent_tracks(self, max_artists: int = 100):
        """
        Extract genres from recently played tracks with optimized batch processing.

        Args:
            max_artists: Maximum number of artists to process (default: 100)

        Returns:
            Number of genres extracted
        """
        logger.info(f"Starting optimized genre extraction from recently played tracks (max {max_artists} artists)")

        # Get all unique artists from recently played tracks
        artists = self._get_artists_from_recent_tracks(max_artists)
        logger.info(f"Found {len(artists)} unique artists in recently played tracks")

        # Filter out artists we already have genres for
        artists_to_process = self._filter_artists_needing_genres(artists)
        logger.info(f"Need to process {len(artists_to_process)} artists (skipping {len(artists) - len(artists_to_process)} with existing genres)")

        if not artists_to_process:
            logger.info("No new artists to process")
            return 0

        # Process artists in optimized batches
        genres_count = 0
        batch_size = 10  # Process 10 artists before taking a break
        
        for i in range(0, len(artists_to_process), batch_size):
            batch = artists_to_process[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(artists_to_process) + batch_size - 1)//batch_size} ({len(batch)} artists)")
            
            batch_genres = self._process_artist_batch(batch)
            genres_count += batch_genres
            
            # Take a break between batches
            if i + batch_size < len(artists_to_process):
                logger.info(f"Taking a break after batch {i//batch_size + 1}...")
                time.sleep(self.batch_delay)

        logger.info(f"Extracted and saved {genres_count} genres from {len(artists_to_process)} artists")
        return genres_count

    def extract_genres_for_artists(self, artists: List[str]) -> int:
        """
        Extract genres for a specific list of artists.

        Args:
            artists: List of artist names to process

        Returns:
            Number of genres extracted
        """
        logger.info(f"Starting genre extraction for {len(artists)} specific artists")

        if not artists:
            logger.info("No artists to process")
            return 0

        # Filter out artists we already have genres for
        artists_to_process = self._filter_artists_needing_genres(artists)
        logger.info(f"Need to process {len(artists_to_process)} artists (skipping {len(artists) - len(artists_to_process)} with existing genres)")

        if not artists_to_process:
            logger.info("No new artists to process")
            return 0

        # Process artists in optimized batches
        genres_count = 0
        batch_size = 10  # Process 10 artists before taking a break
        
        for i in range(0, len(artists_to_process), batch_size):
            batch = artists_to_process[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(artists_to_process) + batch_size - 1)//batch_size} ({len(batch)} artists)")
            
            batch_genres = self._process_artist_batch(batch)
            genres_count += batch_genres
            
            # Take a break between batches
            if i + batch_size < len(artists_to_process):
                logger.info(f"Taking a break after batch {i//batch_size + 1}...")
                time.sleep(self.batch_delay)

        logger.info(f"Extracted and saved {genres_count} genres from {len(artists_to_process)} artists")
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

    def _filter_artists_needing_genres(self, artists: List[str]) -> List[str]:
        """
        Filter out artists that already have genres in the database.
        
        Args:
            artists: List of artist names
            
        Returns:
            List of artists that need genre extraction
        """
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            # Get artists that already have genres
            placeholders = ','.join(['?' for _ in artists])
            cursor.execute(f'''
                SELECT DISTINCT artist_name 
                FROM genres 
                WHERE artist_name IN ({placeholders})
            ''', artists)
            
            existing_artists = {row[0] for row in cursor.fetchall()}
            conn.close()
            
            # Return artists that don't have genres yet
            return [artist for artist in artists if artist not in existing_artists]
            
        except Exception as e:
            logger.error(f"Error filtering artists: {e}")
            return artists  # Return all artists if filtering fails

    def _process_artist_batch(self, artists: List[str]) -> int:
        """
        Process a batch of artists for genre extraction.
        
        Args:
            artists: List of artist names to process
            
        Returns:
            Number of genres extracted
        """
        genres_count = 0
        
        for artist_name in artists:
            try:
                # Check cache first
                if artist_name in self.genre_cache:
                    genres = self.genre_cache[artist_name]
                    logger.info(f"Using cached genres for {artist_name}: {genres}")
                else:
                    # Get artist genres using the API method
                    genres = self.api.get_artist_genres(artist_name)
                    self.genre_cache[artist_name] = genres
                    logger.info(f"Found {len(genres)} genres for artist {artist_name}: {genres}")

                # Save each genre to the database
                for genre in genres:
                    if genre and genre.strip():  # Skip empty genres
                        success = self.db.save_genre(genre.strip(), artist_name)
                        if success:
                            genres_count += 1
                            logger.info(f"Saved genre '{genre}' for artist '{artist_name}'")
                        else:
                            logger.warning(f"Failed to save genre '{genre}' for artist '{artist_name}'")

                if not genres:
                    logger.warning(f"No genres found for artist {artist_name}")

                # Shorter delay between artists in the same batch
                time.sleep(self.rate_limit_delay)
                self.request_count += 1

            except Exception as e:
                logger.error(f"Error extracting genres for artist {artist_name}: {e}")
                
        return genres_count

    def _handle_rate_limit(self):
        """Handle rate limiting with improved backoff strategy."""
        # Base delay
        time.sleep(self.rate_limit_delay)

        # Every 5 requests, take a longer break
        if self.request_count % 5 == 0 and self.request_count > 0:
            logger.info(f"Taking a longer break after {self.request_count} API calls...")
            time.sleep(self.batch_delay)

        # Every 20 requests, take an even longer break
        if self.request_count % 20 == 0 and self.request_count > 0:
            logger.info(f"Taking an extended break after {self.request_count} API calls...")
            time.sleep(5)  # Reduced from 10 to 5 seconds
