"""Module for collecting historical Spotify data and storing it in the database."""
import logging
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class SpotifyDataCollector:
    def __init__(self, spotify_api, database):
        """Initialize collector with API and database instances."""
        self.api = spotify_api
        self.db = database
        self.rate_limit_delay = 1  # Base delay between API calls

    def collect_historical_data(self, user_id: str, start_date: datetime = None):
        """
        Collect available historical data.
        If start_date is None, collects data for the past two weeks.
        Uses multiple data sources and handles rate limiting.
        """
        # If no start_date provided, use two weeks ago for testing
        if start_date is None:
            start_date = datetime.now() - timedelta(days=14)

        logger.info(f"Starting historical data collection for user {user_id} from {start_date}")

        try:
            # 1. Get and save user profile
            user_data = self.api.get_user_profile()
            if user_data:
                self.db.save_user(user_data)
                logger.info("Saved user profile")

            # 2. Get saved tracks from the past two weeks
            saved_tracks = self._get_recent_saved_tracks(start_date)
            if saved_tracks:
                self._save_tracks_batch(saved_tracks, user_id, 'saved')
                logger.info(f"Saved {len(saved_tracks)} saved tracks")

            # 3. Get historical recently played tracks
            played_tracks = self._get_historical_played_tracks(user_id, start_date)
            if played_tracks:
                self._save_tracks_batch(played_tracks, user_id, 'played')
                logger.info(f"Saved {len(played_tracks)} played tracks")

            # 4. Get top tracks for different time ranges
            for time_range in ['short_term', 'medium_term', 'long_term']:
                top_tracks = self.api.get_top_tracks(limit=50, time_range=time_range)
                if top_tracks:
                    self._save_tracks_batch(top_tracks, user_id, f'top_{time_range}')
                    logger.info(f"Saved {len(top_tracks)} top tracks for {time_range}")

                self._handle_rate_limit()

            # 5. Extract genres for collected artists
            logger.info("Starting genre extraction...")
            try:
                from modules.genre_extractor import GenreExtractor
                genre_extractor = GenreExtractor(self.api, self.db)
                
                # Extract genres from recently played tracks (limit to avoid long delays)
                genres_extracted = genre_extractor.extract_genres_from_recent_tracks(max_artists=50)
                logger.info(f"Extracted {genres_extracted} genres from recent tracks")
                
            except Exception as e:
                logger.error(f"Error during genre extraction: {e}")
                # Continue anyway - genre extraction is not critical

            logger.info("Historical data collection completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error collecting historical data: {e}")
            return False

    def _get_all_saved_tracks(self) -> List[Dict[str, Any]]:
        """Get all saved tracks using pagination."""
        all_tracks = []
        offset = 0
        limit = 50  # Spotify's max limit per request

        while True:
            try:
                tracks = self.api.get_saved_tracks(limit=limit, offset=offset)
                if not tracks:
                    break

                all_tracks.extend(tracks)

                if len(tracks) < limit:
                    break

                offset += limit
                self._handle_rate_limit()

            except Exception as e:
                logger.error(f"Error fetching saved tracks at offset {offset}: {e}")
                break

        return all_tracks

    def _get_recent_saved_tracks(self, start_date: datetime) -> List[Dict[str, Any]]:
        """Get saved tracks since start_date."""
        all_tracks = []
        offset = 0
        limit = 50  # Spotify's max limit per request

        # Ensure start_date is timezone-naive for consistent comparison
        if start_date.tzinfo is not None:
            start_date = start_date.replace(tzinfo=None)

        while True:
            try:
                tracks = self.api.get_saved_tracks(limit=limit, offset=offset)
                if not tracks:
                    break

                # Filter tracks by date
                recent_tracks = []
                for track in tracks:
                    added_at = track.get('added_at')
                    if added_at:
                        # Convert to datetime and remove timezone info for comparison
                        try:
                            # Handle different datetime formats
                            if 'Z' in added_at:
                                # ISO format with Z (UTC)
                                dt = datetime.fromisoformat(added_at.replace('Z', '+00:00'))
                            elif 'T' in added_at and '+' in added_at:
                                # ISO format with timezone offset
                                dt = datetime.fromisoformat(added_at)
                            else:
                                # Simple ISO format
                                dt = datetime.fromisoformat(added_at)

                            # Remove timezone info for comparison
                            dt = dt.replace(tzinfo=None)

                            if dt >= start_date:
                                recent_tracks.append(track)
                        except ValueError:
                            # If parsing fails, include the track anyway
                            recent_tracks.append(track)

                all_tracks.extend(recent_tracks)

                # If we got fewer tracks than requested, we can stop fetching
                if len(tracks) < limit:
                    break

                # Check if the last track is older than start_date
                if tracks and 'added_at' in tracks[-1]:
                    try:
                        last_added_at = tracks[-1]['added_at']
                        if 'Z' in last_added_at:
                            last_dt = datetime.fromisoformat(last_added_at.replace('Z', '+00:00'))
                        elif 'T' in last_added_at and '+' in last_added_at:
                            last_dt = datetime.fromisoformat(last_added_at)
                        else:
                            last_dt = datetime.fromisoformat(last_added_at)

                        last_dt = last_dt.replace(tzinfo=None)

                        if last_dt < start_date:
                            break
                    except ValueError:
                        # If parsing fails, continue fetching
                        pass

                offset += limit
                self._handle_rate_limit()

            except Exception as e:
                logger.error(f"Error fetching recent saved tracks at offset {offset}: {e}")
                break

        return all_tracks

    def _get_historical_played_tracks(self, user_id: str, start_date: datetime) -> List[Dict[str, Any]]:
        """
        Get historical recently played tracks using timestamp pagination.
        Works backwards from now until start_date.
        """
        all_tracks = []
        current_timestamp = datetime.now()

        # Ensure start_date is timezone-naive for consistent comparison
        if start_date.tzinfo is not None:
            start_date = start_date.replace(tzinfo=None)

        while current_timestamp > start_date:
            try:
                tracks = self.api.get_recently_played(limit=50, before=current_timestamp.isoformat())
                if not tracks:
                    break

                # Filter out tracks before start_date
                valid_tracks = []
                for track in tracks:
                    played_at = track.get('played_at')
                    if played_at:
                        try:
                            # Handle different datetime formats
                            if 'Z' in played_at:
                                # ISO format with Z (UTC)
                                dt = datetime.fromisoformat(played_at.replace('Z', '+00:00'))
                            elif 'T' in played_at and '+' in played_at:
                                # ISO format with timezone offset
                                dt = datetime.fromisoformat(played_at)
                            else:
                                # Simple ISO format
                                dt = datetime.fromisoformat(played_at)

                            # Remove timezone info for comparison
                            dt = dt.replace(tzinfo=None)

                            if dt >= start_date:
                                valid_tracks.append(track)
                        except ValueError:
                            # If parsing fails, include the track anyway
                            valid_tracks.append(track)

                all_tracks.extend(valid_tracks)

                # Update timestamp for next iteration
                if tracks:
                    last_played_at = tracks[-1].get('played_at')
                    if last_played_at:
                        try:
                            if 'Z' in last_played_at:
                                last_dt = datetime.fromisoformat(last_played_at.replace('Z', '+00:00'))
                            elif 'T' in last_played_at and '+' in last_played_at:
                                last_dt = datetime.fromisoformat(last_played_at)
                            else:
                                last_dt = datetime.fromisoformat(last_played_at)

                            current_timestamp = last_dt.replace(tzinfo=None)
                        except ValueError:
                            # If parsing fails, use a fallback approach
                            current_timestamp = current_timestamp - timedelta(days=1)
                    else:
                        # If no played_at, move back by a day
                        current_timestamp = current_timestamp - timedelta(days=1)
                else:
                    # If no tracks, move back by a day
                    current_timestamp = current_timestamp - timedelta(days=1)

                self._handle_rate_limit()

            except Exception as e:
                logger.error(f"Error fetching historical tracks: {e}")
                break

        return all_tracks

    def _save_tracks_batch(self, tracks: List[Dict[str, Any]], user_id: str, source: str):
        """Save a batch of tracks and their listening history."""
        for track in tracks:
            try:
                # Ensure track has audio features - get them if missing
                if not track.get('energy'):
                    audio_features = self.api.get_audio_features_safely(track['id'])
                    track.update(audio_features)
                
                # Save track data (now includes audio features)
                self.db.save_track(track)

                # Get timestamp (played_at or added_at)
                timestamp = track.get('played_at') or track.get('added_at')

                # Normalize timestamp to ISO format without timezone info
                if timestamp:
                    try:
                        # Parse the timestamp
                        if 'Z' in timestamp:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        elif 'T' in timestamp and ('+' in timestamp or '-' in timestamp.split('T')[1]):
                            dt = datetime.fromisoformat(timestamp)
                        else:
                            dt = datetime.fromisoformat(timestamp)

                        # Convert to naive datetime in ISO format
                        played_at = dt.replace(tzinfo=None).isoformat()
                    except ValueError:
                        # If parsing fails, use the original timestamp
                        played_at = timestamp
                else:
                    # If no timestamp, use current time
                    played_at = datetime.now().isoformat()

                # Save listening history
                self.db.save_listening_history(
                    user_id=user_id,
                    track_id=track['id'],
                    played_at=played_at,
                    source=source
                )

            except Exception as e:
                logger.error(f"Error saving track {track.get('id')}: {e}")

    def _handle_rate_limit(self):
        """Handle rate limiting with exponential backoff."""
        time.sleep(self.rate_limit_delay)
        # Increase delay if we're getting close to rate limit
        # Reset it periodically
        if self.rate_limit_delay < 4:  # Max 4 second delay
            self.rate_limit_delay *= 1.5