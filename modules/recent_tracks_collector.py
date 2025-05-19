"""Module for collecting a larger number of recently played tracks."""
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class RecentTracksCollector:
    def __init__(self, spotify_api, database):
        """Initialize collector with API and database instances."""
        self.api = spotify_api
        self.db = database
        self.rate_limit_delay = 1  # Base delay between API calls

    def collect_recent_tracks(self, user_id: str, max_tracks: int = 200):
        """
        Collect up to max_tracks recently played tracks.
        Uses pagination to get more than the 50 track limit per API call.
        
        Args:
            user_id: The Spotify user ID
            max_tracks: Maximum number of tracks to collect (default: 200)
            
        Returns:
            Number of tracks collected
        """
        logger.info(f"Starting collection of up to {max_tracks} recently played tracks for user {user_id}")
        
        all_tracks = []
        before_timestamp = None
        
        # Spotify API has a limit of 50 tracks per call, so we need to paginate
        while len(all_tracks) < max_tracks:
            try:
                # Get recently played tracks
                tracks = self.api.get_recently_played(limit=50, before=before_timestamp)
                
                if not tracks or len(tracks) == 0:
                    logger.info("No more tracks available")
                    break
                
                logger.info(f"Retrieved {len(tracks)} tracks")
                all_tracks.extend(tracks)
                
                # Update the timestamp for the next request
                # We use the played_at time of the last track as the 'before' parameter
                last_track = tracks[-1]
                played_at = last_track.get('played_at')
                
                if played_at:
                    try:
                        # Parse the timestamp
                        if 'Z' in played_at:
                            dt = datetime.fromisoformat(played_at.replace('Z', '+00:00'))
                        elif 'T' in played_at and ('+' in played_at or '-' in played_at.split('T')[1]):
                            dt = datetime.fromisoformat(played_at)
                        else:
                            dt = datetime.fromisoformat(played_at)
                        
                        # Convert to timestamp for the next request
                        # Subtract 1 millisecond to avoid getting the same track again
                        before_timestamp = dt.timestamp() * 1000 - 1
                        logger.info(f"Next request will fetch tracks before {dt}")
                    except ValueError as e:
                        logger.error(f"Error parsing timestamp: {e}")
                        break
                else:
                    logger.error("Last track has no played_at timestamp")
                    break
                
                # Add a delay to avoid rate limiting
                self._handle_rate_limit()
                
            except Exception as e:
                logger.error(f"Error fetching recently played tracks: {e}")
                break
        
        # Limit to max_tracks
        all_tracks = all_tracks[:max_tracks]
        
        # Save tracks to database
        self._save_tracks_batch(all_tracks, user_id, 'played')
        
        logger.info(f"Collected and saved {len(all_tracks)} recently played tracks")
        return len(all_tracks)
    
    def _save_tracks_batch(self, tracks: List[Dict[str, Any]], user_id: str, source: str):
        """Save a batch of tracks and their listening history."""
        for track in tracks:
            try:
                # Save track data
                self.db.save_track(track)
                
                # Get timestamp (played_at)
                timestamp = track.get('played_at')
                
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
