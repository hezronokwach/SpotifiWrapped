import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import time
import pandas as pd

class SpotifyAPI:
    def __init__(self):
        """Initialize Spotify API with credentials from environment variables."""
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.redirect_uri = os.getenv('REDIRECT_URI')
        self.scopes = 'user-top-read user-library-read playlist-read-private user-read-currently-playing user-read-recently-played'
        self.sp = None
        self.initialize_connection()
        
    def initialize_connection(self):
        """Create Spotify API connection with proper authentication."""
        try:
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=self.scopes,
                open_browser=False
            ))
            print("Successfully connected to Spotify API")
        except Exception as e:
            print(f"Error connecting to Spotify API: {e}")
            self.sp = None
    
    def get_top_tracks(self, limit=10, time_range='short_term'):
        """
        Fetch user's top tracks.
        
        Args:
            limit: Number of tracks to fetch
            time_range: 'short_term' (4 weeks), 'medium_term' (6 months), or 'long_term' (years)
        
        Returns:
            List of track dictionaries or empty list if error
        """
        if not self.sp:
            return []
            
        try:
            results = self.sp.current_user_top_tracks(limit=limit, time_range=time_range)
            tracks_data = []
            
            for idx, track in enumerate(results['items'], 1):
                # Get audio features for each track
                audio_features = self.sp.audio_features(track['id'])[0] if track['id'] else {}
                
                tracks_data.append({
                    'track': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album': track['album']['name'],
                    'rank': idx,
                    'popularity': track['popularity'],
                    'id': track['id'],
                    'duration_ms': track['duration_ms'],
                    'explicit': track['explicit'],
                    'preview_url': track['preview_url'],
                    'image_url': track['album']['images'][0]['url'] if track['album']['images'] else '',
                    # Audio features
                    'danceability': audio_features.get('danceability', 0) if audio_features else 0,
                    'energy': audio_features.get('energy', 0) if audio_features else 0,
                    'tempo': audio_features.get('tempo', 0) if audio_features else 0,
                    'valence': audio_features.get('valence', 0) if audio_features else 0,
                    'acousticness': audio_features.get('acousticness', 0) if audio_features else 0
                })
            
            return tracks_data
        except Exception as e:
            print(f"Error fetching top tracks: {e}")
            return []
    
    def get_saved_tracks(self, limit=10):
        """Fetch user's saved tracks."""
        if not self.sp:
            return []
            
        try:
            results = self.sp.current_user_saved_tracks(limit=limit)
            tracks_data = []
            
            for idx, item in enumerate(results['items'], 1):
                track = item['track']
                # Calculate end date for timeline (added_at + 1 day)
                added_at = pd.to_datetime(item['added_at'])
                end_date = added_at + pd.Timedelta(days=1)
                
                tracks_data.append({
                    'track': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album': track['album']['name'],
                    'added_at': item['added_at'],
                    'end_date': end_date.isoformat(),  # For timeline visualization
                    'id': track['id'],
                    'popularity': track['popularity'],
                    'duration_ms': track['duration_ms'],
                    'image_url': track['album']['images'][0]['url'] if track['album']['images'] else ''
                })
            
            return tracks_data
        except Exception as e:
            print(f"Error fetching saved tracks: {e}")
            return []
    
    def get_playlists(self, limit=10):
        """Fetch user's playlists."""
        if not self.sp:
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
            
            return playlists_data
        except Exception as e:
            print(f"Error fetching playlists: {e}")
            return []
    
    def get_currently_playing(self):
        """Fetch currently playing track."""
        if not self.sp:
            return None
            
        try:
            current_track = self.sp.currently_playing()
            
            if current_track and current_track.get('is_playing', False) and current_track.get('item'):
                track = current_track['item']
                
                # Get audio features
                audio_features = self.sp.audio_features(track['id'])[0] if track['id'] else {}
                
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
                    'danceability': audio_features.get('danceability', 0) if audio_features else 0,
                    'energy': audio_features.get('energy', 0) if audio_features else 0,
                    'tempo': audio_features.get('tempo', 0) if audio_features else 0
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
            
            return {
                'display_name': user_profile.get('display_name', 'Unknown'),
                'id': user_profile.get('id', 'Unknown'),
                'followers': user_profile.get('followers', {}).get('total', 0),
                'image_url': user_profile.get('images', [{}])[0].get('url', '') if user_profile.get('images') else '',
                'country': user_profile.get('country', 'Unknown'),
                'product': user_profile.get('product', 'Unknown')  # subscription level
            }
        except Exception as e:
            print(f"Error fetching user profile: {e}")
            return None
    
    def get_recently_played(self, limit=10):
        """Fetch recently played tracks."""
        if not self.sp:
            return []
            
        try:
            results = self.sp.current_user_recently_played(limit=limit)
            tracks_data = []
            
            for idx, item in enumerate(results['items'], 1):
                track = item['track']
                played_at = pd.to_datetime(item['played_at'])
                # Estimate end time (played_at + track duration)
                end_time = played_at + pd.Timedelta(milliseconds=track['duration_ms'])
                
                tracks_data.append({
                    'track': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album': track['album']['name'],
                    'played_at': item['played_at'],
                    'end_time': end_time.isoformat(),
                    'id': track['id'],
                    'duration_ms': track['duration_ms'],
                    'image_url': track['album']['images'][0]['url'] if track['album']['images'] else ''
                })
            
            return tracks_data
        except Exception as e:
            print(f"Error fetching recently played tracks: {e}")
            return []
    
    def get_audio_features_for_top_tracks(self, time_range='short_term', limit=10):
        """Get detailed audio features for top tracks."""
        if not self.sp:
            return []
            
        try:
            top_tracks = self.sp.current_user_top_tracks(limit=limit, time_range=time_range)
            track_ids = [track['id'] for track in top_tracks['items']]
            
            if not track_ids:
                return []
                
            # Get audio features for all tracks in one request
            audio_features = self.sp.audio_features(track_ids)
            
            features_data = []
            for i, features in enumerate(audio_features):
                if features:
                    track = top_tracks['items'][i]
                    features_data.append({
                        'track': track['name'],
                        'artist': track['artists'][0]['name'],
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
                        'id': features['id'],
                        'duration_ms': features['duration_ms']
                    })
            
            return features_data
        except Exception as e:
            print(f"Error fetching audio features: {e}")
            return []
    
    def get_top_artists(self, limit=10, time_range='short_term'):
        """Fetch user's top artists."""
        if not self.sp:
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
            
            return artists_data
        except Exception as e:
            print(f"Error fetching top artists: {e}")
            return []