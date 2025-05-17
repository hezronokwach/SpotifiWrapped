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
        
    def collect_historical_data(self, user_id: str, start_date: datetime):
        """
        Collect all available historical data since start_date.
        Uses multiple data sources and handles rate limiting.
        """
        logger.info(f"Starting historical data collection for user {user_id} from {start_date}")
        
        try:
            # 1. Get and save user profile
            user_data = self.api.get_user_profile()
            if user_data:
                self.db.save_user(user_data)
                logger.info("Saved user profile")
            
            # 2. Get all saved tracks (these have accurate timestamps)
            saved_tracks = self._get_all_saved_tracks()
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
        
    def _get_historical_played_tracks(self, user_id: str, start_date: datetime) -> List[Dict[str, Any]]:
        """
        Get historical recently played tracks using timestamp pagination.
        Works backwards from now until start_date.
        """
        all_tracks = []
        current_timestamp = datetime.now()
        
        while current_timestamp > start_date:
            try:
                tracks = self.api.get_recently_played(limit=50, before=current_timestamp.isoformat())
                if not tracks:
                    break
                    
                # Filter out tracks before start_date
                valid_tracks = [
                    track for track in tracks
                    if datetime.fromisoformat(track['played_at']) >= start_date
                ]
                all_tracks.extend(valid_tracks)
                
                # Update timestamp for next iteration
                if tracks:
                    current_timestamp = datetime.fromisoformat(tracks[-1]['played_at'])
                
                self._handle_rate_limit()
                
            except Exception as e:
                logger.error(f"Error fetching historical tracks: {e}")
                break
                
        return all_tracks
        
    def _save_tracks_batch(self, tracks: List[Dict[str, Any]], user_id: str, source: str):
        """Save a batch of tracks and their listening history."""
        for track in tracks:
            try:
                # Save track data
                self.db.save_track(track)
                
                # Save listening history
                played_at = track.get('played_at') or track.get('added_at') or datetime.now().isoformat()
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