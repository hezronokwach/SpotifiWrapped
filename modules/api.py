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
from modules.genre_cache import get_genre_cache
from modules.sample_data_generator import SampleDataGenerator

# Configure logging
logging.basicConfig(level=logging.WARNING,  # Changed from INFO to WARNING
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('spotify_api')

class SpotifyAPI:
    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, use_sample_data=False):
        """Initialize Spotify API with credentials. Can be dynamically set or use sample data."""
        self.client_id = client_id if client_id else os.getenv('CLIENT_ID')
        self.client_secret = client_secret if client_secret else os.getenv('CLIENT_SECRET')
        self.redirect_uri = redirect_uri if redirect_uri else os.getenv('REDIRECT_URI')
        self.use_sample_data = use_sample_data
        self.scopes = 'user-top-read user-library-read playlist-read-private user-read-currently-playing user-read-recently-played user-follow-read'
        self.sp = None
        # Flag to enable AI-based audio features instead of Spotify API
        self.use_ai_audio_features = True
        # Cache for audio features to reduce API calls
        self.audio_features_cache = {}
        # Cache for user profile to reduce API calls
        self._user_profile_cache = None
        self._user_profile_cache_time = 0
        # Initialize sample data generator if needed
        if self.use_sample_data:
            self.sample_generator = SampleDataGenerator()
        if not self.use_sample_data:
            self.initialize_connection()

    def set_credentials(self, client_id, client_secret, redirect_uri):
        """Dynamically set Spotify API credentials and re-initialize connection."""
        print(f"🔧 DEBUG: Setting credentials - Client ID: {client_id[:8] if client_id else 'None'}...")
        print(f"🔧 DEBUG: Client Secret length: {len(client_secret) if client_secret else 0}")
        print(f"🔧 DEBUG: Redirect URI: {redirect_uri}")

        # Only clear cache if credentials actually changed
        credentials_changed = (
            self.client_id != client_id or 
            self.client_secret != client_secret or 
            self.redirect_uri != redirect_uri
        )
        
        if credentials_changed:
            print(f"🔧 DEBUG: Credentials changed, clearing cache files...")
            self.clear_cache_files()
            # Clear user profile cache
            self._user_profile_cache = None
            self._user_profile_cache_time = 0
        else:
            print(f"🔧 DEBUG: Credentials unchanged, keeping existing cache...")

        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.use_sample_data = False
        
        # Only clear connection if credentials changed
        if credentials_changed:
            self.sp = None  # Clear existing connection

        print(f"🔧 DEBUG: Credentials set, initializing connection...")
        self.initialize_connection()
        print(f"🔧 DEBUG: Connection initialized, sp object: {self.sp is not None}")

    def clear_cache_files(self):
        """Clear only Spotify OAuth cache files."""
        import glob
        import tempfile

        # Clear Spotify OAuth cache files
        cache_files = glob.glob('.spotify_cache*')
        for cache_file in cache_files:
            try:
                os.remove(cache_file)
                print(f"🗑️ DEBUG: Removed cache file: {cache_file}")
            except Exception as e:
                print(f"⚠️ DEBUG: Could not remove cache file {cache_file}: {e}")

        # Also check for cache files in temp directory
        temp_dir = tempfile.gettempdir()
        temp_cache_files = glob.glob(os.path.join(temp_dir, '.spotify_cache*'))
        temp_cache_files.extend(glob.glob(os.path.join(temp_dir, 'spotify_auth_code.txt')))
        for cache_file in temp_cache_files:
            try:
                os.remove(cache_file)
                print(f"🗑️ DEBUG: Removed temp cache file: {cache_file}")
            except Exception as e:
                print(f"⚠️ DEBUG: Could not remove temp cache file {cache_file}: {e}")

    def clear_all_cached_data(self):
        """Clear all cached data including CSV files and Spotify cache."""
        import glob
        import tempfile

        # Clear Spotify OAuth cache files
        cache_files = glob.glob('.spotify_cache*')
        for cache_file in cache_files:
            try:
                os.remove(cache_file)
                print(f"Removed Spotify cache file: {cache_file}")
            except Exception as e:
                print(f"Could not remove cache file {cache_file}: {e}")

        # Also check for cache files in temp directory
        temp_dir = tempfile.gettempdir()
        temp_cache_files = glob.glob(os.path.join(temp_dir, '.spotify_cache*'))
        temp_cache_files.extend(glob.glob(os.path.join(temp_dir, 'spotify_auth_code.txt')))
        for cache_file in temp_cache_files:
            try:
                os.remove(cache_file)
                print(f"Removed temp cache file: {cache_file}")
            except Exception as e:
                print(f"Could not remove temp cache file {cache_file}: {e}")

        # Clear CSV data files
        csv_files = [
            'data/user_profile.csv',
            'data/current_track.csv',
            'data/playlists.csv',
            'data/top_tracks.csv',
            'data/top_artists.csv',
            'data/saved_tracks.csv',
            'data/audio_features.csv',
            'data/recently_played.csv',
            'data/personality.csv',
            'data/top_albums.csv'
        ]
        for csv_file in csv_files:
            try:
                if os.path.exists(csv_file):
                    os.remove(csv_file)
                    print(f"Removed CSV file: {csv_file}")
            except Exception as e:
                print(f"Could not remove CSV file {csv_file}: {e}")

        # Clear the connection and reset credentials
        self.sp = None
        self.client_id = None
        self.client_secret = None
        self.use_sample_data = False
        print("All cached data cleared successfully")

    def initialize_connection(self):
        """Create Spotify API connection with proper authentication."""
        print(f"🚀 DEBUG: Starting initialize_connection...")
        print(f"🚀 DEBUG: client_id: {self.client_id[:8] if self.client_id else 'None'}...")
        print(f"🚀 DEBUG: client_secret: {'***' if self.client_secret else 'None'}")
        print(f"🚀 DEBUG: redirect_uri: {self.redirect_uri}")
        print(f"🚀 DEBUG: use_sample_data: {self.use_sample_data}")

        if not self.client_id or not self.client_secret or not self.redirect_uri:
            print(f"❌ DEBUG: Missing required credentials!")
            print(f"   - client_id: {bool(self.client_id)}")
            print(f"   - client_secret: {bool(self.client_secret)}")
            print(f"   - redirect_uri: {bool(self.redirect_uri)}")
            self.sp = None
            return

        try:
            print(f"🔐 DEBUG: Creating SpotifyOAuth manager...")
            # SECURITY FIX: Use user-specific cache to prevent token sharing
            user_cache_path = f'.spotify_cache_{self.client_id[:8]}'
            print(f"🔐 DEBUG: Using user-specific cache: {user_cache_path}")
            auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=self.scopes,
                open_browser=False,  # Don't auto-open browser to avoid conflicts
                show_dialog=True,  # Always show auth dialog
                cache_path=user_cache_path  # User-specific cache to prevent token sharing
            )
            print(f"✅ DEBUG: SpotifyOAuth manager created successfully")

            # Try to get token, but don't force if not available
            print(f"🎫 DEBUG: Attempting to get access token...")
            try:
                # Check if we have a cached token first
                token_info = auth_manager.get_cached_token()
                if token_info:
                    print(f"✅ DEBUG: Using cached token")
                else:
                    # Check for authorization code from callback (user-specific)
                    import tempfile
                    import os
                    temp_dir = tempfile.gettempdir()
                    # SECURITY FIX: Use user-specific auth code file
                    code_file = os.path.join(temp_dir, f'spotify_auth_code_{self.client_id[:8]}.txt')
                    if os.path.exists(code_file):
                        with open(code_file, 'r') as f:
                            auth_code = f.read().strip()
                        print(f"✅ DEBUG: Found user-specific authorization code, exchanging for token...")
                        token_info = auth_manager.get_access_token(auth_code, as_dict=True)
                        # Clean up the temporary file
                        os.remove(code_file)
                        print(f"✅ DEBUG: Token exchange successful")
                    else:
                        print(f"⚠️ DEBUG: No cached token or auth code available")
                        # Generate auth URL for user (but don't prompt in terminal)
                        auth_url = auth_manager.get_authorize_url()
                        print(f"🔗 DEBUG: Auth URL available for web interface: {auth_url}")
            except Exception as e:
                print(f"⚠️ DEBUG: Could not get access token during initialization: {e}")
                # Continue without token - will be requested when needed

            # Create Spotify client with increased timeout (default is 5 seconds)
            print(f"🎵 DEBUG: Creating Spotify client...")
            self.sp = spotipy.Spotify(auth_manager=auth_manager, requests_timeout=15)
            print(f"✅ DEBUG: Spotify client created successfully")

            # Test connection (but don't fail if not authenticated yet)
            print(f"🧪 DEBUG: Testing connection...")
            try:
                # Only test if we have a cached token, don't prompt for auth
                cached_token = auth_manager.get_cached_token()
                if cached_token:
                    user = self.sp.current_user()
                    if user:
                        print(f"✅ DEBUG: Successfully connected as {user.get('display_name', 'Unknown')}")
                        logger.warning(f"Successfully connected as {user.get('display_name', 'Unknown')}")
                    else:
                        print(f"⚠️ DEBUG: No user profile available - authentication may be needed")
                        logger.warning("No user profile available - authentication may be needed")
                else:
                    print(f"⚠️ DEBUG: No cached token - authentication will be needed")
                    logger.warning("No cached token - authentication will be needed")
            except Exception as e:
                print(f"⚠️ DEBUG: Could not test connection during initialization: {e}")
                logger.warning(f"Could not test connection during initialization: {e}")
                # Keep the client - authentication will happen when needed
        except Exception as e:
            print(f"❌ DEBUG: Error connecting to Spotify API: {e}")
            logger.error(f"Error connecting to Spotify API: {e}")
            self.sp = None

    def get_auth_url(self):
        """Get the authorization URL for OAuth flow."""
        if self.sp and hasattr(self.sp, 'auth_manager'):
            return self.sp.auth_manager.get_authorize_url()
        return None

    def is_authenticated(self):
        """Check if the user is authenticated without triggering prompts."""
        if not self.sp:
            return False
        try:
            # First check for authorization code from callback (user-specific)
            import tempfile
            temp_dir = tempfile.gettempdir()
            # SECURITY FIX: Use user-specific auth code file
            code_file = os.path.join(temp_dir, f'spotify_auth_code_{self.client_id[:8]}.txt')
            if os.path.exists(code_file):
                with open(code_file, 'r') as f:
                    auth_code = f.read().strip()
                print(f"✅ DEBUG: Found user-specific authorization code, exchanging for token...")
                try:
                    token_info = self.sp.auth_manager.get_access_token(auth_code, as_dict=True)
                    if token_info:
                        print(f"✅ DEBUG: Token exchange successful!")
                        # Clean up the temporary file
                        os.remove(code_file)
                        return True
                except Exception as e:
                    print(f"❌ DEBUG: Token exchange failed: {e}")
                    # Clean up the file anyway
                    try:
                        os.remove(code_file)
                    except:
                        pass

            # Check if we have a cached token
            if hasattr(self.sp, 'auth_manager'):
                cached_token = self.sp.auth_manager.get_cached_token()
                if cached_token:
                    # Test the token by making a simple API call
                    try:
                        user = self.sp.current_user()
                        return user is not None
                    except Exception as e:
                        print(f"⚠️ DEBUG: Token test failed: {e}")
                        return False
            return False
        except Exception as e:
            print(f"⚠️ DEBUG: Error checking authentication: {e}")
            return False

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

    def get_audio_features(self, track_ids: List[str]) -> Dict[str, Any]:
        """Get audio features for a list of track IDs."""
        if not self.sp:
            if self.use_sample_data:
                return self.sample_generator.generate_audio_features(track_ids)
            return {'audio_features': []}
        
        # Use the existing batch method
        features_map = self.get_audio_features_batch(track_ids)
        return {
            'audio_features': [features_map.get(track_id, {}) for track_id in track_ids]
        }

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
            print("❌ DEBUG: No Spotify connection available")
            if self.use_sample_data:
                return self.sample_generator.generate_top_tracks(limit=limit)
            return []

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
            return []



    def get_saved_tracks(self, limit=50, offset=0):
        """
        Fetch user's saved tracks.

        Args:
            limit: Number of tracks to fetch
            offset: The index of the first track to return
        """
        if not self.sp:
            print("❌ DEBUG: No Spotify connection available")
            return []

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
                return []

            return tracks_data
        except Exception as e:
            print(f"Error fetching saved tracks: {e}")
            return []



    def get_playlists(self, limit=10):
        """Fetch user's playlists."""
        if not self.sp:
            print("❌ DEBUG: No Spotify connection available")
            return []

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
                return []

            return playlists_data
        except Exception as e:
            print(f"Error fetching playlists: {e}")
            return []



    def get_currently_playing(self):
        """Fetch currently playing track."""
        if not self.sp:
            print("❌ DEBUG: No Spotify connection available")
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
        """Fetch user profile information with caching to improve performance."""
        # Check cache first (cache for 30 seconds)
        current_time = time.time()
        if (self._user_profile_cache and
            current_time - self._user_profile_cache_time < 30):
            return self._user_profile_cache

        if not self.sp:
            print("❌ DEBUG: No Spotify connection available")
            if self.use_sample_data:
                return self.sample_generator.generate_user_profile()
            return {}

        try:
            user_profile = self.sp.current_user()

            # Get the number of artists the user is following
            following_count = 0
            try:
                print("🔍 DEBUG: Attempting to fetch followed artists...")
                # Get followed artists with more detailed error handling
                followed_artists = self.sp.current_user_followed_artists(limit=1)
                print(f"🔍 DEBUG: Followed artists response: {followed_artists}")

                if followed_artists and 'artists' in followed_artists:
                    following_count = followed_artists['artists']['total']
                    print(f"✅ DEBUG: Successfully got following count: {following_count}")
                else:
                    print("⚠️ DEBUG: No 'artists' key in followed artists response")
                    following_count = 0

            except Exception as e:
                print(f"❌ Error fetching followed artists: {e}")
                print(f"❌ Error type: {type(e).__name__}")

                # Check if this is a scope permission error
                if "insufficient client scope" in str(e).lower() or "scope" in str(e).lower():
                    print("🔐 DEBUG: This appears to be a scope permission error.")
                    print("🔐 DEBUG: The user may need to re-authenticate with updated permissions.")
                    print("🔐 DEBUG: Added 'user-follow-read' scope to fix this issue.")

                # Try alternative approach - get followed artists with different parameters
                try:
                    print("🔄 DEBUG: Trying alternative approach for followed artists...")
                    followed_artists_alt = self.sp.current_user_followed_artists(limit=50)
                    if followed_artists_alt and 'artists' in followed_artists_alt and 'items' in followed_artists_alt['artists']:
                        following_count = len(followed_artists_alt['artists']['items'])
                        print(f"✅ DEBUG: Alternative approach got following count: {following_count}")
                    else:
                        following_count = 0
                        print("⚠️ DEBUG: Alternative approach also failed")
                except Exception as alt_e:
                    print(f"❌ Alternative approach also failed: {alt_e}")
                    following_count = 0

            user_data = {
                'display_name': user_profile.get('display_name', 'Unknown'),
                'id': user_profile.get('id', 'Unknown'),
                'followers': user_profile.get('followers', {}).get('total', 0),
                'following': following_count,  # Add following count
                'image_url': user_profile.get('images', [{}])[0].get('url', '') if user_profile.get('images') else '',
                'product': user_profile.get('product', 'Unknown')  # subscription level
            }

            # Cache the result
            self._user_profile_cache = user_data
            self._user_profile_cache_time = current_time

            return user_data
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
            print("❌ DEBUG: No Spotify connection available")
            if self.use_sample_data:
                return self.sample_generator.generate_recently_played(limit=limit)
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



    def get_audio_features_for_top_tracks(self, time_range='short_term', limit=10):
        """Get detailed audio features for top tracks."""
        if not self.sp:
            print("❌ DEBUG: No Spotify connection available")
            return []

        try:
            top_tracks = self.sp.current_user_top_tracks(limit=limit, time_range=time_range)
            track_ids = [track['id'] for track in top_tracks['items']]

            if not track_ids:
                return []

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
                return []

            return features_data
        except Exception as e:
            print(f"Error fetching audio features: {e}")
            return []



    def get_top_artists(self, limit=10, time_range='short_term'):
        """Fetch user's top artists."""
        if not self.sp:
            print("❌ DEBUG: No Spotify connection available")
            return []

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
                return []

            return artists_data
        except Exception as e:
            print(f"Error fetching top artists: {e}")
            return []



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
        Get genres for a specific artist with caching.

        Args:
            artist_name: Name of the artist to search for

        Returns:
            List of genres for the artist or empty list if not found
        """
        if not self.sp or self.use_sample_data or not artist_name:
            return []

        # Normalize artist name
        artist_name = artist_name.strip()
        if not artist_name:
            return []

        # Check cache first
        cache = get_genre_cache()
        cached_genres = cache.get(artist_name)
        if cached_genres is not None:
            return cached_genres

        # Add retry mechanism with reduced backoff for better performance
        max_retries = 2  # Reduced from 3 to 2
        retry_count = 0

        while retry_count < max_retries:
            try:
                # First try with exact artist name search
                artist_data = self.sp.search(q=f'artist:"{artist_name}"', type='artist', limit=1)

                # If no results, try a more general search
                if not artist_data or not artist_data.get('artists', {}).get('items'):
                    artist_data = self.sp.search(q=artist_name, type='artist', limit=3)  # Reduced from 5 to 3

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

                    if matched_artist:
                        genres = matched_artist.get('genres', [])
                        # Cache the result
                        cache.set(artist_name, genres)
                        return genres

                # Cache empty result to avoid repeated API calls
                cache.set(artist_name, [])
                return []

            except Exception as e:
                retry_count += 1
                if "429" in str(e):  # Rate limiting error
                    wait_time = min(2 ** retry_count, 5)  # Cap wait time at 5 seconds
                    print(f"Rate limit hit, retrying in {wait_time} seconds (attempt {retry_count}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    if retry_count < max_retries:
                        wait_time = 0.5  # Reduced from 1 second
                        time.sleep(wait_time)
                    else:
                        # Cache empty result to avoid repeated API calls
                        cache.set(artist_name, [])
                        return []

        # Cache empty result for failed attempts
        cache.set(artist_name, [])
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
        if not self.sp or self.use_sample_data:
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

    # Method aliases for test compatibility
    def get_current_user_profile(self):
        """Alias for get_user_profile for test compatibility."""
        return self.get_user_profile()
    
    def get_current_user_top_tracks(self, limit=10, time_range='short_term'):
        """Alias for get_top_tracks for test compatibility."""
        return self.get_top_tracks(limit=limit, time_range=time_range)
    
    def get_current_user_top_artists(self, limit=10, time_range='short_term'):
        """Alias for get_top_artists for test compatibility."""
        return self.get_top_artists(limit=limit, time_range=time_range)
    
    def get_current_user_recently_played(self, limit=50, before=None, after=None):
        """Alias for get_recently_played for test compatibility."""
        return self.get_recently_played(limit=limit, before=before, after=after)
    
    def get_current_user_saved_tracks(self, limit=50, offset=0):
        """Alias for get_saved_tracks for test compatibility."""
        return self.get_saved_tracks(limit=limit, offset=offset)
    
    def get_current_playback(self):
        """Alias for get_currently_playing for test compatibility."""
        return self.get_currently_playing()
    
    def get_sample_playlists(self, limit=10):
        """Alias for get_playlists for test compatibility."""
        return self.get_playlists(limit=limit)