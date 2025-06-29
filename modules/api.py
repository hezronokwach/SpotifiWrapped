import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import time
import pandas as pd
import random
import logging
from functools import lru_cache
from typing import Dict, List, Optional, Union, Any

# Import the AI audio feature extractor
from modules.ai_audio_features import get_track_audio_features

# Configure logging
logging.basicConfig(level=logging.WARNING,  # Changed from INFO to WARNING
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('spotify_api')

class SpotifyAPI:
    def __init__(self):
        """Initialize Spotify API with credentials from environment variables."""
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.redirect_uri = os.getenv('REDIRECT_URI')
        self.scopes = 'user-top-read user-library-read playlist-read-private user-read-currently-playing user-read-recently-played'
        self.sp = None
        # Flag to enable AI-based audio features instead of Spotify API
        self.use_ai_audio_features = True
        # Cache for audio features to reduce API calls
        self.audio_features_cache = {}
        self.initialize_connection()

    def initialize_connection(self):
        """Create Spotify API connection with proper authentication."""
        try:
            auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=self.scopes,
                open_browser=True,  # Show browser for authentication
                show_dialog=True,  # Always show auth dialog
                cache_path='.spotify_cache'  # Cache tokens
            )

            # Try to get token, but don't force if not available
            try:
                auth_manager.get_access_token(as_dict=False)
            except Exception as e:
                logger.warning(f"Could not get access token during initialization: {e}")
                # Continue without token - will be requested when needed

            # Create Spotify client with increased timeout (default is 5 seconds)
            self.sp = spotipy.Spotify(auth_manager=auth_manager, requests_timeout=15)

            # Test connection (but don't fail if not authenticated yet)
            try:
                user = self.sp.current_user()
                if user:
                    logger.warning(f"Successfully connected as {user.get('display_name', 'Unknown')}")
                else:
                    logger.warning("No user profile available - authentication may be needed")
            except Exception as e:
                logger.warning(f"Could not test connection during initialization: {e}")
                # Keep the client - authentication will happen when needed
        except Exception as e:
            logger.error(f"Error connecting to Spotify API: {e}")
            self.sp = None

    @lru_cache(maxsize=100)
    def get_audio_features_safely(self, track_id: str) -> Dict[str, Any]:
        """
        Safely get audio features for a track, using AI-based extraction when possible.
        Uses caching to reduce API calls for the same track.

        Args:
            track_id: Spotify track ID

        Returns:
            Audio features dictionary or generated fallback data
        """
        if not track_id:
            return self._generate_fallback_audio_features()

        # Check cache first
        if track_id in self.audio_features_cache:
            return self.audio_features_cache[track_id]

        try:
            # If using AI-based extraction, try to get the preview URL and analyze it
            if self.use_ai_audio_features:
                try:
                    # Get track info to get the preview URL
                    track_info = self.sp.track(track_id)
                    preview_url = track_info.get('preview_url')

                    # If we have a preview URL, use AI to extract features
                    if preview_url:
                        features = get_track_audio_features(track_id, preview_url)
                        # Cache the result
                        self.audio_features_cache[track_id] = features
                        return features
                    else:
                        logger.info(f"No preview URL available for track {track_id}")
                        fallback = self._generate_fallback_audio_features()
                        self.audio_features_cache[track_id] = fallback
                        return fallback
                except Exception as e:
                    logger.warning(f"Error using AI audio features for track {track_id}: {e}")
                    # Fall back to Spotify API if AI fails

            # If not using AI or AI failed, try Spotify API
            # Add retry mechanism with backoff
            max_retries = 3
            retry_count = 0

            while retry_count < max_retries:
                try:
                    features = self.sp.audio_features(track_id)
                    if features and features[0]:
                        # Cache the result
                        self.audio_features_cache[track_id] = features[0]
                        return features[0]

                    fallback = self._generate_fallback_audio_features()
                    self.audio_features_cache[track_id] = fallback
                    return fallback
                except Exception as e:
                    # Check if it's a 403 error
                    if "403" in str(e):
                        # For 403 errors, return fallback data rather than retrying
                        fallback = self._generate_fallback_audio_features()
                        self.audio_features_cache[track_id] = fallback
                        return fallback

                    retry_count += 1
                    if retry_count < max_retries:
                        # Exponential backoff
                        wait_time = 2 ** retry_count
                        logger.info(f"Retrying in {wait_time} seconds (attempt {retry_count}/{max_retries})")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"Max retries reached for track {track_id}")
                        raise

            fallback = self._generate_fallback_audio_features()
            self.audio_features_cache[track_id] = fallback
            return fallback
        except Exception as e:
            logger.error(f"Error fetching audio features for track {track_id}: {e}")
            fallback = self._generate_fallback_audio_features()
            self.audio_features_cache[track_id] = fallback
            return fallback

    def get_audio_features_batch(self, track_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get audio features for multiple tracks efficiently.

        Args:
            track_ids: List of Spotify track IDs

        Returns:
            Dictionary mapping track IDs to their audio features
        """
        if not track_ids:
            return {}

        # Filter out IDs that are already in cache
        uncached_ids = [tid for tid in track_ids if tid not in self.audio_features_cache]

        # If all IDs are cached, return from cache
        if not uncached_ids:
            return {tid: self.audio_features_cache[tid] for tid in track_ids}

        # If using AI features, we need to process one by one
        if self.use_ai_audio_features:
            for track_id in uncached_ids:
                self.get_audio_features_safely(track_id)
        else:
            # Process in batches of 100 (Spotify API limit)
            for i in range(0, len(uncached_ids), 100):
                batch = uncached_ids[i:i+100]
                try:
                    features_batch = self.sp.audio_features(batch)
                    for j, features in enumerate(features_batch):
                        if features:
                            self.audio_features_cache[batch[j]] = features
                        else:
                            self.audio_features_cache[batch[j]] = self._generate_fallback_audio_features()
                except Exception as e:
                    logger.error(f"Error fetching batch audio features: {e}")
                    # If batch request fails, fall back to individual requests
                    for track_id in batch:
                        self.get_audio_features_safely(track_id)

        # Return all requested features from cache
        return {tid: self.audio_features_cache.get(tid, self._generate_fallback_audio_features())
                for tid in track_ids}

    def _generate_fallback_audio_features(self) -> Dict[str, Any]:
        """
        Generate realistic fallback audio features when API fails.

        Returns:
            Dictionary with realistic audio feature values
        """
        # Generate somewhat realistic values instead of zeros
        return {
            'danceability': round(random.uniform(0.3, 0.8), 2),
            'energy': round(random.uniform(0.4, 0.9), 2),
            'key': random.randint(0, 11),
            'loudness': round(random.uniform(-12, -5), 2),
            'mode': random.randint(0, 1),
            'speechiness': round(random.uniform(0.03, 0.2), 2),
            'acousticness': round(random.uniform(0.1, 0.8), 2),
            'instrumentalness': round(random.uniform(0, 0.4), 2),
            'liveness': round(random.uniform(0.05, 0.3), 2),
            'valence': round(random.uniform(0.2, 0.8), 2),
            'tempo': round(random.uniform(80, 160), 2),
            'duration_ms': random.randint(180000, 240000)
        }

    def get_top_tracks(self, limit: int = 10, time_range: str = 'short_term') -> List[Dict[str, Any]]:
        """
        Fetch user's top tracks.

        Args:
            limit: Number of tracks to fetch
            time_range: 'short_term' (4 weeks), 'medium_term' (6 months), or 'long_term' (years)

        Returns:
            List of track dictionaries or empty list if error
        """
        if not self.sp:
            return self._generate_sample_top_tracks(limit)

        try:
            results = self.sp.current_user_top_tracks(limit=limit, time_range=time_range)
            tracks_data = []

            # Get all track IDs for batch processing
            track_ids = [track['id'] for track in results['items']]

            # Get audio features in batch
            audio_features_map = self.get_audio_features_batch(track_ids)

            for idx, track in enumerate(results['items'], 1):
                # Get audio features from the batch results
                audio_features = audio_features_map.get(track['id'], self._generate_fallback_audio_features())

                tracks_data.append({
                    'track': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album': track['album']['name'],
                    'rank': idx,
                    'popularity': track['popularity'],
                    'id': track['id'],
                    'name': track['name'],  # Add this to satisfy NOT NULL constraint
                    'duration_ms': track['duration_ms'],
                    'explicit': track['explicit'],
                    'preview_url': track['preview_url'],
                    'image_url': track['album']['images'][0]['url'] if track['album']['images'] else '',
                    # Audio features
                    'danceability': audio_features.get('danceability', 0),
                    'energy': audio_features.get('energy', 0),
                    'tempo': audio_features.get('tempo', 0),
                    'valence': audio_features.get('valence', 0),
                    'acousticness': audio_features.get('acousticness', 0)
                })

            return tracks_data
        except Exception as e:
            logger.error(f"Error fetching top tracks: {e}")
            return self._generate_sample_top_tracks(limit)

    def _generate_sample_top_tracks(self, limit=10):
        """Generate sample top tracks when API fails."""
        sample_tracks = [
            {"track": "Top Track 1", "artist": "Popular Artist 1", "album": "Hit Album 1"},
            {"track": "Top Track 2", "artist": "Popular Artist 2", "album": "Hit Album 2"},
            {"track": "Top Track 3", "artist": "Popular Artist 3", "album": "Hit Album 3"},
            {"track": "Top Track 4", "artist": "Popular Artist 4", "album": "Hit Album 4"},
            {"track": "Top Track 5", "artist": "Popular Artist 5", "album": "Hit Album 5"},
            {"track": "Top Track 6", "artist": "Popular Artist 6", "album": "Hit Album 6"},
            {"track": "Top Track 7", "artist": "Popular Artist 7", "album": "Hit Album 7"},
            {"track": "Top Track 8", "artist": "Popular Artist 8", "album": "Hit Album 8"},
            {"track": "Top Track 9", "artist": "Popular Artist 9", "album": "Hit Album 9"},
            {"track": "Top Track 10", "artist": "Popular Artist 10", "album": "Hit Album 10"}
        ]

        tracks_data = []
        for idx, track in enumerate(sample_tracks[:limit], 1):
            # Get fallback audio features
            audio_features = self._generate_fallback_audio_features()

            tracks_data.append({
                'track': track['track'],
                'artist': track['artist'],
                'album': track['album'],
                'rank': idx,
                'popularity': random.randint(70, 95),
                'id': f"sample-top-{idx}",
                'duration_ms': random.randint(180000, 240000),
                'explicit': random.choice([True, False]),
                'preview_url': '',
                'image_url': '',
                # Audio features
                'danceability': audio_features['danceability'],
                'energy': audio_features['energy'],
                'tempo': audio_features['tempo'],
                'valence': audio_features['valence'],
                'acousticness': audio_features['acousticness']
            })

        return tracks_data

    def get_saved_tracks(self, limit=50, offset=0):
        """
        Fetch user's saved tracks.

        Args:
            limit: Number of tracks to fetch
            offset: The index of the first track to return
        """
        if not self.sp:
            return self._generate_sample_saved_tracks(limit)

        try:
            results = self.sp.current_user_saved_tracks(limit=limit, offset=offset)
            tracks_data = []

            for idx, item in enumerate(results['items'], 1):
                track = item['track']

                tracks_data.append({
                    'track': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album': track['album']['name'],
                    'added_at': item['added_at'],
                    'id': track['id'],
                    'popularity': track['popularity'],
                    'duration_ms': track['duration_ms'],
                    'name': track['name'],  # Add this to satisfy NOT NULL constraint
                    'image_url': track['album']['images'][0]['url'] if track['album']['images'] else '',
                    'preview_url': track.get('preview_url', '')
                })

            # If we got no data, return sample data
            if not tracks_data:
                return self._generate_sample_saved_tracks(limit)

            return tracks_data
        except Exception as e:
            print(f"Error fetching saved tracks: {e}")
            return self._generate_sample_saved_tracks(limit)

    def _generate_sample_saved_tracks(self, limit=10):
        """Generate sample saved tracks when API fails."""
        sample_tracks = [
            {"track": "Sample Track 1", "artist": "Sample Artist 1", "album": "Sample Album 1"},
            {"track": "Sample Track 2", "artist": "Sample Artist 2", "album": "Sample Album 2"},
            {"track": "Sample Track 3", "artist": "Sample Artist 3", "album": "Sample Album 3"},
            {"track": "Sample Track 4", "artist": "Sample Artist 4", "album": "Sample Album 4"},
            {"track": "Sample Track 5", "artist": "Sample Artist 5", "album": "Sample Album 5"},
            {"track": "Sample Track 6", "artist": "Sample Artist 6", "album": "Sample Album 6"},
            {"track": "Sample Track 7", "artist": "Sample Artist 7", "album": "Sample Album 7"},
            {"track": "Sample Track 8", "artist": "Sample Artist 8", "album": "Sample Album 8"},
            {"track": "Sample Track 9", "artist": "Sample Artist 9", "album": "Sample Album 9"},
            {"track": "Sample Track 10", "artist": "Sample Artist 10", "album": "Sample Album 10"}
        ]

        tracks_data = []
        for idx, track in enumerate(sample_tracks[:limit], 1):
            # Generate dates within the last month
            days_ago = idx * 2
            added_at = pd.Timestamp.now() - pd.Timedelta(days=days_ago)

            tracks_data.append({
                'track': track['track'],
                'artist': track['artist'],
                'album': track['album'],
                'added_at': added_at.isoformat(),
                'id': f"sample-id-{idx}",
                'popularity': random.randint(50, 90),
                'duration_ms': random.randint(180000, 240000),
                'name': track['track'],  # Add this to satisfy NOT NULL constraint
                'image_url': '',
                'preview_url': ''
            })

        return tracks_data

    def get_playlists(self, limit=10):
        """Fetch user's playlists."""
        if not self.sp:
            return self._generate_sample_playlists(limit)

        try:
            results = self.sp.current_user_playlists(limit=limit)
            playlists_data = []

            for idx, playlist in enumerate(results['items'], 1):
                playlists_data.append({
                    'playlist': playlist['name'],
                    'total_tracks': playlist['tracks']['total'],
                    'public': playlist['public'],
                    'collaborative': playlist['collaborative'],
                    'id': playlist['id'],
                    'image_url': playlist['images'][0]['url'] if playlist['images'] else '',
                    'owner': playlist['owner']['display_name']
                })

            # If we got no data, return sample data
            if not playlists_data:
                return self._generate_sample_playlists(limit)

            return playlists_data
        except Exception as e:
            print(f"Error fetching playlists: {e}")
            return self._generate_sample_playlists(limit)

    def _generate_sample_playlists(self, limit=10):
        """Generate sample playlists when API fails."""
        sample_playlists = [
            {"name": "Favorites", "tracks": 25, "public": True},
            {"name": "Workout Mix", "tracks": 18, "public": False},
            {"name": "Chill Vibes", "tracks": 32, "public": True},
            {"name": "Road Trip", "tracks": 45, "public": False},
            {"name": "Party Playlist", "tracks": 28, "public": True},
            {"name": "Study Music", "tracks": 15, "public": False},
            {"name": "Throwbacks", "tracks": 50, "public": True},
            {"name": "New Discoveries", "tracks": 22, "public": True},
            {"name": "Morning Coffee", "tracks": 12, "public": False},
            {"name": "Weekend Vibes", "tracks": 30, "public": True}
        ]

        playlists_data = []
        for idx, playlist in enumerate(sample_playlists[:limit], 1):
            playlists_data.append({
                'playlist': playlist['name'],
                'total_tracks': playlist['tracks'],
                'public': playlist['public'],
                'collaborative': False,
                'id': f"sample-playlist-{idx}",
                'image_url': '',
                'owner': 'Sample User'
            })

        return playlists_data

    def get_currently_playing(self):
        """Fetch currently playing track."""
        if not self.sp:
            return None

        try:
            current_track = self.sp.currently_playing()

            if current_track and current_track.get('is_playing', False) and current_track.get('item'):
                track = current_track['item']

                # Get audio features - using the safe method
                audio_features = self.get_audio_features_safely(track['id'])

                return {
                    'track': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album': track['album']['name'],
                    'duration_ms': track['duration_ms'],
                    'progress_ms': current_track['progress_ms'],
                    'id': track['id'],
                    'image_url': track['album']['images'][0]['url'] if track['album']['images'] else '',
                    'is_playing': current_track['is_playing'],
                    # Audio features
                    'danceability': audio_features.get('danceability', 0),
                    'energy': audio_features.get('energy', 0),
                    'tempo': audio_features.get('tempo', 0)
                }
            return None
        except Exception as e:
            print(f"Error fetching currently playing track: {e}")
            return None

    def get_user_profile(self):
        """Fetch user profile information."""
        if not self.sp:
            return None

        try:
            user_profile = self.sp.current_user()

            # Get the number of artists the user is following
            following_count = 0
            try:
                # Get followed artists
                followed_artists = self.sp.current_user_followed_artists(limit=1)
                following_count = followed_artists['artists']['total'] if followed_artists and 'artists' in followed_artists else 0
            except Exception as e:
                print(f"Error fetching followed artists: {e}")
                following_count = 0

            return {
                'display_name': user_profile.get('display_name', 'Unknown'),
                'id': user_profile.get('id', 'Unknown'),
                'followers': user_profile.get('followers', {}).get('total', 0),
                'following': following_count,  # Add following count
                'image_url': user_profile.get('images', [{}])[0].get('url', '') if user_profile.get('images') else '',
                'product': user_profile.get('product', 'Unknown')  # subscription level
            }
        except Exception as e:
            print(f"Error fetching user profile: {e}")
            return {
                'display_name': 'Sample User',
                'id': 'sample-user-id',
                'followers': 123,
                'following': 45,  # Add sample following count
                'image_url': '',
                'country': 'US',
                'product': 'premium'
            }

    def get_recently_played(self, limit=50, before=None, after=None, max_retries=3):
        """
        Fetch recently played tracks with retry logic.

        Args:
            limit: Number of tracks to fetch
            before: Unix timestamp in milliseconds - returns all items before this timestamp
            after: Unix timestamp in milliseconds - returns all items after this timestamp
            max_retries: Maximum number of retry attempts
        """
        if not self.sp:
            print("No Spotify connection available")
            return []

        for attempt in range(max_retries + 1):
            try:
                params = {'limit': limit}
                if before:
                    params['before'] = before
                elif after:
                    params['after'] = after

                results = self.sp.current_user_recently_played(**params)
                tracks_data = []

                for idx, item in enumerate(results['items'], 1):
                    track = item['track']
                    played_at = pd.to_datetime(item['played_at'], format='ISO8601')

                    tracks_data.append({
                        'track': track['name'],
                        'artist': track['artists'][0]['name'],
                        'album': track['album']['name'],
                        'played_at': item['played_at'],
                        'id': track['id'],
                        'duration_ms': track['duration_ms'],
                        'name': track['name'],  # Add this to satisfy NOT NULL constraint
                        'image_url': track['album']['images'][0]['url'] if track['album']['images'] else '',
                        'preview_url': track.get('preview_url', ''),
                        'popularity': track.get('popularity', 0),
                        'day_of_week': played_at.day_name(),
                        'hour_of_day': played_at.hour
                    })

                print(f"Retrieved {len(tracks_data)} recently played tracks")
                return tracks_data

            except Exception as e:
                print(f"Error fetching recently played tracks (attempt {attempt + 1}/{max_retries + 1}): {e}")

                # Check if it's a rate limit error
                if "429" in str(e) or "rate limit" in str(e).lower():
                    if attempt < max_retries:
                        wait_time = (attempt + 1) * 5  # Progressive backoff: 5, 10, 15 seconds
                        print(f"Rate limit detected, waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print("Max retries reached for rate limit")
                        return []
                elif attempt < max_retries:
                    # For other errors, wait a shorter time
                    wait_time = (attempt + 1) * 2  # 2, 4, 6 seconds
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    print("Max retries reached")
                    return []

        return []  # If all retries failed

    def _generate_sample_recently_played(self, limit=50):
        """Generate sample recently played tracks when API fails."""
        sample_tracks = [
            {"track": "Sample Recent 1", "artist": "Sample Artist 1", "album": "Sample Album 1"},
            {"track": "Sample Recent 2", "artist": "Sample Artist 2", "album": "Sample Album 2"},
            {"track": "Sample Recent 3", "artist": "Sample Artist 3", "album": "Sample Album 3"},
            {"track": "Sample Recent 4", "artist": "Sample Artist 4", "album": "Sample Album 4"},
            {"track": "Sample Recent 5", "artist": "Sample Artist 5", "album": "Sample Album 5"},
            {"track": "Sample Recent 6", "artist": "Sample Artist 6", "album": "Sample Album 6"},
            {"track": "Sample Recent 7", "artist": "Sample Artist 7", "album": "Sample Album 7"},
            {"track": "Sample Recent 8", "artist": "Sample Artist 8", "album": "Sample Album 8"},
            {"track": "Sample Recent 9", "artist": "Sample Artist 9", "album": "Sample Album 9"},
            {"track": "Sample Recent 10", "artist": "Sample Artist 10", "album": "Sample Album 10"}
        ]

        # Extend the sample tracks to reach the limit
        extended_tracks = []
        while len(extended_tracks) < limit:
            extended_tracks.extend(sample_tracks)
        extended_tracks = extended_tracks[:limit]

        tracks_data = []
        for idx, track in enumerate(extended_tracks, 1):
            # Generate timestamps across different days and hours for better pattern visualization
            days_ago = random.randint(0, 6)  # Last week
            hour = random.randint(0, 23)  # Any hour
            played_at = pd.Timestamp.now() - pd.Timedelta(days=days_ago, hours=random.randint(0, 23))
            played_at = played_at.replace(hour=hour)

            tracks_data.append({
                'track': track['track'],
                'artist': track['artist'],
                'album': track['album'],
                'played_at': played_at.isoformat(),
                'id': f"sample-recent-{idx}",
                'duration_ms': 210000,  # 3:30
                'name': track['track'],  # Add this to satisfy NOT NULL constraint
                'image_url': '',
                'preview_url': '',
                'popularity': random.randint(50, 90),
                'day_of_week': played_at.day_name(),
                'hour_of_day': played_at.hour
            })

        return tracks_data

    def get_audio_features_for_top_tracks(self, time_range='short_term', limit=10):
        """Get detailed audio features for top tracks."""
        if not self.sp:
            return self._generate_sample_audio_features(limit)

        try:
            top_tracks = self.sp.current_user_top_tracks(limit=limit, time_range=time_range)
            track_ids = [track['id'] for track in top_tracks['items']]

            if not track_ids:
                return self._generate_sample_audio_features(limit)

            features_data = []

            # Process tracks individually to handle potential 403 errors
            for i, track_id in enumerate(track_ids):
                if i >= len(top_tracks['items']):
                    continue

                track = top_tracks['items'][i]
                preview_url = track.get('preview_url')
                features = self.get_audio_features_safely(track_id)

                features_data.append({
                    'track': track['name'],
                    'artist': track['artists'][0]['name'],
                    'danceability': features.get('danceability', 0),
                    'energy': features.get('energy', 0),
                    'key': features.get('key', 0),
                    'loudness': features.get('loudness', 0),
                    'mode': features.get('mode', 0),
                    'speechiness': features.get('speechiness', 0),
                    'acousticness': features.get('acousticness', 0),
                    'instrumentalness': features.get('instrumentalness', 0),
                    'liveness': features.get('liveness', 0),
                    'valence': features.get('valence', 0),
                    'tempo': features.get('tempo', 0),
                    'id': track_id,
                    'duration_ms': features.get('duration_ms', track.get('duration_ms', 0))
                })

            # If we got no data, return sample data
            if not features_data:
                return self._generate_sample_audio_features(limit)

            return features_data
        except Exception as e:
            print(f"Error fetching audio features: {e}")
            return self._generate_sample_audio_features(limit)

    def _generate_sample_audio_features(self, limit=5):
        """Generate sample audio features when API fails."""
        sample_tracks = [
            {"track": "Sample Feature 1", "artist": "Sample Artist 1"},
            {"track": "Sample Feature 2", "artist": "Sample Artist 2"},
            {"track": "Sample Feature 3", "artist": "Sample Artist 3"},
            {"track": "Sample Feature 4", "artist": "Sample Artist 4"},
            {"track": "Sample Feature 5", "artist": "Sample Artist 5"},
            {"track": "Sample Feature 6", "artist": "Sample Artist 6"},
            {"track": "Sample Feature 7", "artist": "Sample Artist 7"},
            {"track": "Sample Feature 8", "artist": "Sample Artist 8"},
            {"track": "Sample Feature 9", "artist": "Sample Artist 9"},
            {"track": "Sample Feature 10", "artist": "Sample Artist 10"}
        ]

        features_data = []
        for idx, track in enumerate(sample_tracks[:limit], 1):
            # Generate realistic audio features
            features = self._generate_fallback_audio_features()

            features_data.append({
                'track': track['track'],
                'artist': track['artist'],
                'danceability': features['danceability'],
                'energy': features['energy'],
                'key': features['key'],
                'loudness': features['loudness'],
                'mode': features['mode'],
                'speechiness': features['speechiness'],
                'acousticness': features['acousticness'],
                'instrumentalness': features['instrumentalness'],
                'liveness': features['liveness'],
                'valence': features['valence'],
                'tempo': features['tempo'],
                'id': f"sample-feature-{idx}",
                'duration_ms': features['duration_ms']
            })

        return features_data

    def get_top_artists(self, limit=10, time_range='short_term'):
        """Fetch user's top artists."""
        if not self.sp:
            return self._generate_sample_artists(limit)

        try:
            results = self.sp.current_user_top_artists(limit=limit, time_range=time_range)
            artists_data = []

            for idx, artist in enumerate(results['items'], 1):
                artists_data.append({
                    'artist': artist['name'],
                    'rank': idx,
                    'popularity': artist['popularity'],
                    'genres': ', '.join(artist['genres']) if artist['genres'] else 'Unknown',
                    'followers': artist['followers']['total'],
                    'id': artist['id'],
                    'image_url': artist['images'][0]['url'] if artist['images'] else ''
                })

            # If we got no data, return sample data
            if not artists_data:
                return self._generate_sample_artists(limit)

            return artists_data
        except Exception as e:
            print(f"Error fetching top artists: {e}")
            return self._generate_sample_artists(limit)

    def _generate_sample_artists(self, limit=10):
        """Generate sample artists when API fails."""
        sample_artists = [
            {"name": "Sample Artist 1", "genres": "Pop, Dance"},
            {"name": "Sample Artist 2", "genres": "Rock, Alternative"},
            {"name": "Sample Artist 3", "genres": "Hip Hop, Rap"},
            {"name": "Sample Artist 4", "genres": "Electronic, Dance"},
            {"name": "Sample Artist 5", "genres": "R&B, Soul"},
            {"name": "Sample Artist 6", "genres": "Indie, Folk"},
            {"name": "Sample Artist 7", "genres": "Jazz, Blues"},
            {"name": "Sample Artist 8", "genres": "Classical, Instrumental"},
            {"name": "Sample Artist 9", "genres": "Reggae, World"},
            {"name": "Sample Artist 10", "genres": "Metal, Hard Rock"}
        ]

        artists_data = []
        for idx, artist in enumerate(sample_artists[:limit], 1):
            artists_data.append({
                'artist': artist['name'],
                'rank': idx,
                'popularity': random.randint(60, 95),
                'genres': artist['genres'],
                'followers': random.randint(10000, 1000000),
                'id': f"sample-artist-{idx}",
                'image_url': ''
            })

        return artists_data

    def get_artists_by_genre(self, genre_name, limit=5):
        """
        Get artists for a specific genre.

        Args:
            genre_name: Name of the genre to search for
            limit: Maximum number of artists to return

        Returns:
            List of artist dictionaries with name and image_url
        """
        if not self.sp or not genre_name or genre_name == 'unknown':
            return []

        try:
            # Search for artists by genre
            results = self.sp.search(q=f'genre:"{genre_name}"', type='artist', limit=limit)

            if not results or 'artists' not in results or 'items' not in results['artists']:
                return []

            artists = []
            for artist in results['artists']['items']:
                artist_data = {
                    'name': artist['name'],
                    'id': artist['id'],
                    'image_url': artist['images'][0]['url'] if artist['images'] else '',
                    'popularity': artist.get('popularity', 0),
                    'genres': artist.get('genres', [])
                }
                artists.append(artist_data)

            return artists

        except Exception as e:
            print(f"Error getting artists for genre {genre_name}: {e}")
            return []

    def get_artist_genres(self, artist_name):
        """
        Get genres for a specific artist.

        Args:
            artist_name: Name of the artist to search for

        Returns:
            List of genres for the artist or empty list if not found
        """
        if not self.sp or not artist_name:
            return []

        # Normalize artist name
        artist_name = artist_name.strip()
        if not artist_name:
            return []

        # Add retry mechanism with backoff
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                # First try with exact artist name search
                artist_data = self.sp.search(q=f'artist:"{artist_name}"', type='artist', limit=1)

                # If no results, try a more general search
                if not artist_data or not artist_data.get('artists', {}).get('items'):
                    print(f"No exact match for artist '{artist_name}', trying general search")
                    artist_data = self.sp.search(q=artist_name, type='artist', limit=5)

                # Process results
                if artist_data and 'artists' in artist_data and 'items' in artist_data['artists'] and artist_data['artists']['items']:
                    # Try to find an exact or close match
                    matched_artist = None

                    # First look for exact match
                    for artist in artist_data['artists']['items']:
                        if artist['name'].lower() == artist_name.lower():
                            matched_artist = artist
                            break

                    # If no exact match, use the first result
                    if not matched_artist and artist_data['artists']['items']:
                        matched_artist = artist_data['artists']['items'][0]
                        print(f"Using closest match: '{matched_artist['name']}' for '{artist_name}'")

                    if matched_artist:
                        genres = matched_artist.get('genres', [])
                        print(f"Found {len(genres)} genres for artist {artist_name}: {genres}")
                        return genres

                print(f"No artist data found for {artist_name}")
                return []

            except Exception as e:
                retry_count += 1
                if "429" in str(e):  # Rate limiting error
                    wait_time = 2 ** retry_count  # Exponential backoff
                    print(f"Rate limit hit, retrying in {wait_time} seconds (attempt {retry_count}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    print(f"Error getting genres for artist {artist_name}: {e}")
                    if retry_count < max_retries:
                        wait_time = 1
                        print(f"Retrying in {wait_time} seconds (attempt {retry_count}/{max_retries})")
                        time.sleep(wait_time)
                    else:
                        return []

        return []

    def get_artists_by_genre(self, genre_name, limit=10):
        """
        Search for artists by genre.

        Args:
            genre_name: The genre to search for
            limit: Maximum number of artists to return

        Returns:
            List of artist dictionaries with name and image_url
        """
        if not self.sp:
            return []

        if not genre_name or genre_name == 'unknown' or genre_name == 'Exploring New Genres':
            return []

        try:
            # Search for artists with this genre
            # Note: Spotify doesn't have a direct genre search, so we search for the genre name
            # and then filter results that have the genre in their genres list
            search_results = self.sp.search(q=f'genre:{genre_name}', type='artist', limit=50)

            if not search_results or 'artists' not in search_results or 'items' not in search_results['artists']:
                return []

            # Filter artists that actually have this genre
            matching_artists = []
            for artist in search_results['artists']['items']:
                if genre_name.lower() in [g.lower() for g in artist.get('genres', [])]:
                    matching_artists.append({
                        'name': artist['name'],
                        'image_url': artist['images'][0]['url'] if artist['images'] else '',
                        'popularity': artist['popularity'],
                        'genres': artist['genres']
                    })

                    if len(matching_artists) >= limit:
                        break

            # If we didn't find enough artists with exact genre match, add some from the search results
            if len(matching_artists) < limit:
                for artist in search_results['artists']['items']:
                    if artist['name'] not in [a['name'] for a in matching_artists]:
                        matching_artists.append({
                            'name': artist['name'],
                            'image_url': artist['images'][0]['url'] if artist['images'] else '',
                            'popularity': artist['popularity'],
                            'genres': artist['genres']
                        })

                        if len(matching_artists) >= limit:
                            break

            return matching_artists

        except Exception as e:
            logger.error(f"Error searching for artists by genre {genre_name}: {e}")
            return []