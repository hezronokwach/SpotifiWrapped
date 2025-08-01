import pandas as pd
import os
import json
import sqlite3
from datetime import datetime, timezone
from typing import Optional, Union

def normalize_timestamp(timestamp: Union[str, datetime, None]) -> Optional[str]:
    """
    Normalize various timestamp formats to ISO format string.

    Args:
        timestamp: Timestamp in various formats (ISO string, datetime object, etc.)

    Returns:
        Normalized ISO format string or None if invalid
    """
    if timestamp is None:
        return None

    if isinstance(timestamp, datetime):
        # Convert datetime to naive UTC and return ISO format
        if timestamp.tzinfo is not None:
            timestamp = timestamp.astimezone(timezone.utc).replace(tzinfo=None)
        return timestamp.replace(microsecond=0).isoformat()

    if isinstance(timestamp, str):
        try:
            # Handle various string formats
            if 'Z' in timestamp:
                # UTC format with Z
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            elif 'T' in timestamp and ('+' in timestamp or '-' in timestamp.split('T')[1]):
                # ISO format with timezone
                dt = datetime.fromisoformat(timestamp)
            else:
                # Assume ISO format without timezone
                dt = datetime.fromisoformat(timestamp)

            # Convert to naive UTC
            if dt.tzinfo is not None:
                dt = dt.astimezone(timezone.utc).replace(tzinfo=None)

            return dt.replace(microsecond=0).isoformat()
        except (ValueError, TypeError):
            # If parsing fails, return None
            return None

    return None

def calculate_duration_minutes(duration_ms: Optional[int]) -> float:
    """
    Calculate duration in minutes from milliseconds.

    Args:
        duration_ms: Duration in milliseconds

    Returns:
        Duration in minutes (rounded to 2 decimal places)
    """
    if duration_ms is None or duration_ms <= 0:
        return 0.0
    return round(duration_ms / 60000, 2)

def calculate_total_listening_time(tracks_data: list) -> dict:
    """
    Calculate total listening time statistics from tracks data.

    Args:
        tracks_data: List of track dictionaries with duration_ms

    Returns:
        Dictionary with listening time statistics
    """
    if not tracks_data:
        return {
            'total_minutes': 0,
            'total_hours': 0,
            'total_tracks': 0,
            'average_track_length': 0
        }

    total_ms = sum(track.get('duration_ms', 0) for track in tracks_data if track.get('duration_ms'))
    total_minutes = calculate_duration_minutes(total_ms)
    total_hours = round(total_minutes / 60, 2)
    total_tracks = len(tracks_data)
    average_track_length = round(total_minutes / total_tracks, 2) if total_tracks > 0 else 0

    return {
        'total_minutes': total_minutes,
        'total_hours': total_hours,
        'total_tracks': total_tracks,
        'average_track_length': average_track_length
    }

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
        """Process saved tracks data with improved timestamp handling."""
        df = self.save_data(data, 'saved_tracks.csv')

        # Convert date columns to datetime with proper normalization
        if not df.empty and 'added_at' in df.columns:
            # Normalize timestamps
            df['added_at'] = df['added_at'].apply(normalize_timestamp)
            df['added_at'] = pd.to_datetime(df['added_at'], errors='coerce')

            # Remove rows with invalid timestamps
            df = df.dropna(subset=['added_at'])

            # Calculate duration in minutes if duration_ms exists
            if 'duration_ms' in df.columns:
                df['duration_minutes'] = df['duration_ms'].apply(calculate_duration_minutes)

            # Remove artificial end_date if it exists (we don't need it for timeline)
            if 'end_date' in df.columns:
                df = df.drop(columns=['end_date'])

            # Sort by added_at date (most recent first)
            df = df.sort_values('added_at', ascending=False)

            # Save the processed data
            df.to_csv(os.path.join(self.data_dir, 'saved_tracks.csv'), index=False)

        return df

    def _process_playlists(self):
        """Process playlists data."""
        try:
            df = pd.read_csv(os.path.join(self.data_dir, 'playlists.csv'))
            df['added_at'] = pd.to_datetime(df['added_at'], format='ISO8601')
            if 'end_date' in df.columns:
                df['end_date'] = pd.to_datetime(df['end_date'], format='ISO8601')

            # Sort by added_at date
            df = df.sort_values('added_at', ascending=False)

            # Save the processed data
            df.to_csv(os.path.join(self.data_dir, 'playlists.csv'), index=False)
        except Exception as e:
            print(f"Error processing playlists data: {e}")

    def _process_history(self):
        """Process listening history data."""
        try:
            df = pd.read_csv(os.path.join(self.data_dir, 'recently_played.csv'))
            df['played_at'] = pd.to_datetime(df['played_at'], format='ISO8601')
            if 'end_time' in df.columns:
                df['end_time'] = pd.to_datetime(df['end_time'], format='ISO8601')

            # Sort by played_at date
            df = df.sort_values('played_at', ascending=False)

            # Calculate day of week and hour of day for time pattern analysis
            df['day_of_week'] = df['played_at'].dt.day_name()
            df['hour_of_day'] = df['played_at'].dt.hour

            # Save the processed data
            df.to_csv(os.path.join(self.data_dir, 'recently_played.csv'), index=False)
        except Exception as e:
            print(f"Error processing listening history data: {e}")

    def process_recently_played(self, data):
        """Process recently played tracks data with improved timestamp handling."""
        df = self.save_data(data, 'recently_played.csv')

        # Convert date columns to datetime with proper normalization
        if not df.empty and 'played_at' in df.columns:
            # Normalize timestamps
            df['played_at'] = df['played_at'].apply(normalize_timestamp)
            df['played_at'] = pd.to_datetime(df['played_at'], errors='coerce')

            # Remove rows with invalid timestamps
            df = df.dropna(subset=['played_at'])

            # Calculate duration in minutes if duration_ms exists
            if 'duration_ms' in df.columns:
                df['duration_minutes'] = df['duration_ms'].apply(calculate_duration_minutes)

            # Remove artificial end_time if it exists
            if 'end_time' in df.columns:
                df = df.drop(columns=['end_time'])

            # Sort by played_at date (most recent first)
            df = df.sort_values('played_at', ascending=False)

            # Calculate day of week and hour of day for time pattern analysis
            # Use local time for user-friendly display
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
            history_df['timestamp'] = pd.to_datetime(history_df['timestamp'], format='ISO8601')
            history_df = history_df.sort_values('timestamp', ascending=False)
            history_df.to_csv(os.path.join(self.data_dir, 'listening_history.csv'), index=False)
            return history_df

        return pd.DataFrame(columns=['track', 'artist', 'timestamp', 'type', 'album'])

    def generate_spotify_wrapped_summary(self):
        """Generate a Spotify Wrapped style summary of user's listening habits."""
        conn = sqlite3.connect(os.path.join(self.data_dir, 'spotify_data.db'))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        summary = {
            'timestamp': datetime.now().isoformat(),
            'top_track': None,
            'top_artist': None,
            'total_minutes': 0,
            'music_mood': None,
            'genre_highlight': None
        }

        try:
            # Get top track from Spotify's official API instead of database calculations
            from modules.api import SpotifyAPI
            spotify_api = SpotifyAPI()

            # Try to get top tracks from Spotify's official rankings
            top_tracks = spotify_api.get_top_tracks(limit=1, time_range='short_term')
            if not top_tracks:
                top_tracks = spotify_api.get_top_tracks(limit=1, time_range='medium_term')
            if not top_tracks:
                top_tracks = spotify_api.get_top_tracks(limit=1, time_range='long_term')

            if top_tracks:
                top_track = top_tracks[0]
                summary['top_track'] = {
                    'name': top_track['name'],
                    'artist': top_track['artist']
                }
            else:
                # Fallback to database if Spotify API fails
                cursor.execute('''
                    SELECT t.track_id as id,
                        t.name as track,
                        t.artist,
                        COUNT(h.history_id) as play_count
                    FROM tracks t
                    JOIN listening_history h ON t.track_id = h.track_id
                    WHERE t.track_id NOT LIKE 'artist-%' AND t.track_id NOT LIKE 'genre-%'
                    GROUP BY t.track_id
                    ORDER BY play_count DESC
                    LIMIT 1
                ''')
                top_track_row = cursor.fetchone()
                if top_track_row:
                    track = dict(top_track_row)
                    summary['top_track'] = {
                        'name': track['track'],
                        'artist': track['artist']
                    }

            # Get top artist from Spotify's official API
            top_artists = spotify_api.get_top_artists(limit=1, time_range='short_term')
            if not top_artists:
                top_artists = spotify_api.get_top_artists(limit=1, time_range='medium_term')
            if not top_artists:
                top_artists = spotify_api.get_top_artists(limit=1, time_range='long_term')

            if top_artists:
                artist_name = top_artists[0]['artist']
                summary['top_artist'] = artist_name

                # Get genres for this artist from database
                cursor.execute('''
                    SELECT genre_name
                    FROM genres
                    WHERE artist_name = ?
                    GROUP BY genre_name
                    ORDER BY count DESC
                    LIMIT 5
                ''', (artist_name,))
                genres = [dict(row)['genre_name'] for row in cursor.fetchall()]
                summary['top_genres'] = genres[:3] if genres else ['Unknown']
            else:
                # Fallback to database if Spotify API fails
                cursor.execute('''
                    SELECT t.artist,
                        COUNT(h.history_id) as play_count
                    FROM tracks t
                    JOIN listening_history h ON t.track_id = h.track_id
                    WHERE t.artist IS NOT NULL AND t.artist != ''
                    GROUP BY t.artist
                    ORDER BY play_count DESC
                    LIMIT 1
                ''')
                top_artist_row = cursor.fetchone()
                if top_artist_row:
                    artist = dict(top_artist_row)
                    artist_name = artist['artist']
                    summary['top_artist'] = artist_name
                    # Get genres for this artist
                    cursor.execute('''
                        SELECT genre_name
                        FROM genres
                        WHERE artist_name = ?
                        GROUP BY genre_name
                        ORDER BY count DESC
                        LIMIT 5
                    ''', (artist_name,))
                    genres = [dict(row)['genre_name'] for row in cursor.fetchall()]
                    summary['top_genres'] = genres[:3] if genres else ['Unknown']

            # Calculate music mood based on audio features
            cursor.execute('''
                SELECT
                    AVG(CASE WHEN t.valence IS NULL THEN 0.5 ELSE t.valence END) as avg_valence,
                    AVG(CASE WHEN t.energy IS NULL THEN 0.5 ELSE t.energy END) as avg_energy,
                    COUNT(*) as track_count
                FROM tracks t
                JOIN listening_history h ON t.track_id = h.track_id
            ''')
            features_row = cursor.fetchone()
            if features_row and features_row['track_count'] > 0:
                features = dict(features_row)
                avg_valence = features.get('avg_valence', 0.5) or 0.5
                avg_energy = features.get('avg_energy', 0.5) or 0.5

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

            # Get top genre from genres table linked to listening history (consistent with other components)
            cursor.execute('''
                SELECT g.genre_name as genre,
                    COUNT(DISTINCT h.history_id) as play_count
                FROM genres g
                JOIN tracks t ON g.artist_name = t.artist
                JOIN listening_history h ON t.track_id = h.track_id
                WHERE g.genre_name IS NOT NULL
                AND g.genre_name != ''
                AND g.genre_name != 'unknown'
                AND h.source IN ('played', 'recently_played', 'current')
                GROUP BY g.genre_name
                ORDER BY play_count DESC
                LIMIT 1
            ''')
            top_genre_row = cursor.fetchone()
            if top_genre_row:
                genre = dict(top_genre_row)
                summary['genre_highlight'] = {
                    'name': genre['genre'],
                    'count': int(genre['play_count'])
                }

            # Calculate total listening minutes from track durations
            cursor.execute('''
                SELECT SUM(t.duration_ms) / 60000.0 as total_minutes
                FROM tracks t
                JOIN listening_history h ON t.track_id = h.track_id
            ''')
            minutes_row = cursor.fetchone()
            if minutes_row:
                summary['total_minutes'] = round(minutes_row['total_minutes'] or 0)

        finally:
            cursor.close()
            conn.close()

        # Save summary to JSON for caching
        with open(os.path.join(self.data_dir, 'wrapped_summary.json'), 'w') as f:
            json.dump(summary, f, indent=2)

        return summary