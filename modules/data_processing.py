import pandas as pd
import os
import json
from datetime import datetime

class DataProcessor:
    def __init__(self, data_dir='data'):
        """Initialize data processor with data directory."""
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
    
    def save_data(self, data, filename, index=False):
        """Save data to CSV file."""
        if not data:
            # Create empty DataFrame with appropriate columns
            if filename == 'top_tracks.csv':
                df = pd.DataFrame(columns=['track', 'artist', 'album', 'rank', 'popularity', 'id', 
                                          'danceability', 'energy', 'tempo', 'valence', 'acousticness'])
            elif filename == 'saved_tracks.csv':
                df = pd.DataFrame(columns=['track', 'artist', 'album', 'added_at', 'end_date', 'id', 'popularity'])
            elif filename == 'playlists.csv':
                df = pd.DataFrame(columns=['playlist', 'total_tracks', 'public', 'collaborative', 'id', 'owner'])
            elif filename == 'current_track.csv':
                df = pd.DataFrame([{'track': 'None', 'artist': 'None', 'album': 'None', 
                                   'duration_ms': 0, 'progress_ms': 0, 'is_playing': False}])
            elif filename == 'user_profile.csv':
                df = pd.DataFrame([{'display_name': 'Unknown', 'id': 'Unknown', 'followers': 0, 'image_url': ''}])
            elif filename == 'recently_played.csv':
                df = pd.DataFrame(columns=['track', 'artist', 'album', 'played_at', 'end_time', 'id'])
            elif filename == 'audio_features.csv':
                df = pd.DataFrame(columns=['track', 'artist', 'danceability', 'energy', 'key', 
                                          'loudness', 'mode', 'speechiness', 'acousticness', 
                                          'instrumentalness', 'liveness', 'valence', 'tempo'])
            elif filename == 'top_artists.csv':
                df = pd.DataFrame(columns=['artist', 'rank', 'popularity', 'genres', 'followers', 'id'])
            else:
                df = pd.DataFrame()
        else:
            df = pd.DataFrame(data)
        
        file_path = os.path.join(self.data_dir, filename)
        df.to_csv(file_path, index=index)
        return df
    
    def load_data(self, filename):
        """Load data from CSV file."""
        file_path = os.path.join(self.data_dir, filename)
        try:
            if os.path.exists(file_path):
                return pd.read_csv(file_path)
            else:
                print(f"File not found: {file_path}")
                return pd.DataFrame()
        except Exception as e:
            print(f"Error loading data from {file_path}: {e}")
            return pd.DataFrame()
    
    def process_top_tracks(self, data):
        """Process top tracks data."""
        df = self.save_data(data, 'top_tracks.csv')
        
        # Create additional derived metrics
        if not df.empty and 'danceability' in df.columns and 'energy' in df.columns:
            # Calculate "vibe score" (custom metric)
            df['vibe_score'] = (df['danceability'] * 0.6 + df['energy'] * 0.4) * 100
            
            # Save the enhanced data
            df.to_csv(os.path.join(self.data_dir, 'top_tracks.csv'), index=False)
        
        return df
    
    def process_saved_tracks(self, data):
        """Process saved tracks data."""
        df = self.save_data(data, 'saved_tracks.csv')
        
        # Convert date columns to datetime
        if not df.empty and 'added_at' in df.columns:
            df['added_at'] = pd.to_datetime(df['added_at'])
            if 'end_date' in df.columns:
                df['end_date'] = pd.to_datetime(df['end_date'])
            
            # Sort by added_at date
            df = df.sort_values('added_at', ascending=False)
            
            # Save the processed data
            df.to_csv(os.path.join(self.data_dir, 'saved_tracks.csv'), index=False)
        
        return df
    
    def process_recently_played(self, data):
        """Process recently played tracks data."""
        df = self.save_data(data, 'recently_played.csv')
        
        # Convert date columns to datetime
        if not df.empty and 'played_at' in df.columns:
            df['played_at'] = pd.to_datetime(df['played_at'])
            if 'end_time' in df.columns:
                df['end_time'] = pd.to_datetime(df['end_time'])
            
            # Sort by played_at date
            df = df.sort_values('played_at', ascending=False)
            
            # Calculate day of week and hour of day for time pattern analysis
            df['day_of_week'] = df['played_at'].dt.day_name()
            df['hour_of_day'] = df['played_at'].dt.hour
            
            # Save the processed data
            df.to_csv(os.path.join(self.data_dir, 'recently_played.csv'), index=False)
        
        return df
    
    def process_audio_features(self, data):
        """Process audio features data."""
        df = self.save_data(data, 'audio_features.csv')
        
        # Create radar chart data format
        if not df.empty:
            # Select features for radar chart
            radar_features = ['danceability', 'energy', 'speechiness', 
                             'acousticness', 'instrumentalness', 'liveness', 'valence']
            
            if all(feature in df.columns for feature in radar_features):
                # Create a separate file for radar chart data
                radar_data = []
                
                for _, row in df.iterrows():
                    for feature in radar_features:
                        radar_data.append({
                            'track': row['track'],
                            'feature': feature,
                            'value': row[feature]
                        })
                
                radar_df = pd.DataFrame(radar_data)
                radar_df.to_csv(os.path.join(self.data_dir, 'radar_chart_data.csv'), index=False)
        
        return df
    
    def process_top_artists(self, data):
        """Process top artists data."""
        df = self.save_data(data, 'top_artists.csv')
        
        # Extract genres for genre analysis
        if not df.empty and 'genres' in df.columns:
            all_genres = []
            
            for _, row in df.iterrows():
                genres = row['genres'].split(', ') if row['genres'] != 'Unknown' else []
                for genre in genres:
                    all_genres.append({
                        'genre': genre,
                        'artist': row['artist'],
                        'count': 1
                    })
            
            if all_genres:
                genres_df = pd.DataFrame(all_genres)
                # Aggregate by genre
                genre_counts = genres_df.groupby('genre')['count'].sum().reset_index()
                genre_counts = genre_counts.sort_values('count', ascending=False)
                genre_counts.to_csv(os.path.join(self.data_dir, 'genre_analysis.csv'), index=False)
        
        return df
    
    def create_listening_history(self):
        """Create a combined listening history from saved and recently played tracks."""
        saved_df = self.load_data('saved_tracks.csv')
        recent_df = self.load_data('recently_played.csv')
        
        history_data = []
        
        # Process saved tracks
        if not saved_df.empty and 'added_at' in saved_df.columns:
            for _, row in saved_df.iterrows():
                history_data.append({
                    'track': row['track'],
                    'artist': row['artist'],
                    'timestamp': row['added_at'],
                    'type': 'Saved',
                    'album': row.get('album', 'Unknown')
                })
        
        # Process recently played
        if not recent_df.empty and 'played_at' in recent_df.columns:
            for _, row in recent_df.iterrows():
                history_data.append({
                    'track': row['track'],
                    'artist': row['artist'],
                    'timestamp': row['played_at'],
                    'type': 'Played',
                    'album': row.get('album', 'Unknown')
                })
        
        if history_data:
            history_df = pd.DataFrame(history_data)
            history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
            history_df = history_df.sort_values('timestamp', ascending=False)
            history_df.to_csv(os.path.join(self.data_dir, 'listening_history.csv'), index=False)
            return history_df
        
        return pd.DataFrame(columns=['track', 'artist', 'timestamp', 'type', 'album'])
    
    def generate_spotify_wrapped_summary(self):
        """Generate a Spotify Wrapped style summary of user's listening habits."""
        top_tracks_df = self.load_data('top_tracks.csv')
        top_artists_df = self.load_data('top_artists.csv')
        audio_features_df = self.load_data('audio_features.csv')
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'top_track': None,
            'top_artist': None,
            'total_minutes': 0,
            'music_mood': None,
            'genre_highlight': None
        }
        
        # Get top track
        if not top_tracks_df.empty and 'rank' in top_tracks_df.columns:
            top_track = top_tracks_df.sort_values('rank').iloc[0]
            summary['top_track'] = {
                'name': top_track['track'],
                'artist': top_track['artist']
            }
        
        # Get top artist
        if not top_artists_df.empty and 'rank' in top_artists_df.columns:
            top_artist = top_artists_df.sort_values('rank').iloc[0]
            summary['top_artist'] = {
                'name': top_artist['artist'],
                'genres': top_artist.get('genres', 'Unknown')
            }
        
        # Calculate music mood based on audio features
        if not audio_features_df.empty:
            avg_valence = audio_features_df['valence'].mean() if 'valence' in audio_features_df.columns else 0
            avg_energy = audio_features_df['energy'].mean() if 'energy' in audio_features_df.columns else 0
            
            # Determine mood quadrant
            if avg_valence > 0.5 and avg_energy > 0.5:
                mood = "Happy & Energetic"
            elif avg_valence > 0.5 and avg_energy <= 0.5:
                mood = "Peaceful & Positive"
            elif avg_valence <= 0.5 and avg_energy > 0.5:
                mood = "Angry & Intense"
            else:
                mood = "Sad & Chill"
            
            summary['music_mood'] = {
                'mood': mood,
                'valence': avg_valence,
                'energy': avg_energy
            }
        
        # Get genre highlight
        genre_df = self.load_data('genre_analysis.csv')
        if not genre_df.empty and 'genre' in genre_df.columns:
            top_genre = genre_df.sort_values('count', ascending=False).iloc[0]
            summary['genre_highlight'] = {
                'name': top_genre['genre'],
                'count': int(top_genre['count'])
            }
        
        # Save summary to JSON
        with open(os.path.join(self.data_dir, 'wrapped_summary.json'), 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary