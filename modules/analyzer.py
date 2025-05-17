import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import Counter
from typing import Dict, List, Any, Tuple

class ListeningPersonalityAnalyzer:
    """
    Analyzes a user's listening habits to determine their music personality.
    """
    
    def __init__(self, spotify_api):
        """
        Initialize with a SpotifyAPI instance.
        
        Args:
            spotify_api: SpotifyAPI instance
        """
        self.spotify_api = spotify_api
        
    def analyze(self) -> Dict[str, Any]:
        """
        Perform a comprehensive analysis of listening habits.
        
        Returns:
            Dictionary with personality traits and metrics
        """
        try:
            # Collect all necessary data
            recently_played = self.spotify_api.get_recently_played(limit=50)
            top_tracks = self.spotify_api.get_top_tracks(limit=50)
            top_artists = self.spotify_api.get_top_artists(limit=20)
            audio_features = self.spotify_api.get_audio_features_for_top_tracks(limit=50)
            
            # Check if we have enough data
            if not recently_played or not top_tracks or not top_artists:
                return {
                    'primary_type': 'Unknown',
                    'secondary_type': 'Unknown',
                    'metrics': {
                        'variety_score': 0,
                        'discovery_score': 0,
                        'consistency_score': 0,
                        'mood_score': 0,
                        'time_pattern_score': 0,
                        'album_completion_rate': 0,
                        'sequential_listening_score': 0
                    },
                    'listening_style': 'Unknown',
                    'description': 'Not enough listening data to determine your personality.',
                    'recommendations': ['Listen to more music to get personalized recommendations.']
                }
            
            # Calculate various metrics
            variety_score = self._calculate_variety_score(top_artists, top_tracks)
            discovery_score = self._calculate_discovery_score(recently_played, top_tracks)
            consistency_score = self._calculate_consistency_score(recently_played)
            mood_score = self._calculate_mood_score(audio_features)
            time_pattern_score = self._calculate_time_pattern_score(recently_played)
            album_listening_patterns = self._calculate_album_listening_patterns(recently_played)
            
            # Determine primary and secondary personality types
            personality_types = self._determine_personality_types(
                variety_score, discovery_score, consistency_score, 
                mood_score, time_pattern_score, album_listening_patterns
            )
            
            # Compile results
            return {
                'primary_type': personality_types[0],
                'secondary_type': personality_types[1],
                'metrics': {
                    'variety_score': round(variety_score * 100, 2),
                    'discovery_score': round(discovery_score * 100, 2),
                    'consistency_score': round(consistency_score * 100, 2),
                    'mood_score': round(mood_score * 100, 2),
                    'time_pattern_score': round(time_pattern_score * 100, 2),
                    'album_completion_rate': album_listening_patterns.get('album_completion_rate', 0),
                    'sequential_listening_score': album_listening_patterns.get('sequential_listening_score', 0),
                    'listening_style': album_listening_patterns.get('listening_style', 'Unknown')
                },
                'description': self._get_personality_description(personality_types[0]),
                'recommendations': self._get_recommendations(personality_types[0])
            }
        except Exception as e:
            print(f"Error in personality analysis: {e}")
            # Return a default response if analysis fails
            return {
                'primary_type': 'Data Analyzer',
                'secondary_type': 'Music Explorer',
                'metrics': {
                    'variety_score': 50,
                    'discovery_score': 50,
                    'consistency_score': 50,
                    'mood_score': 50,
                    'time_pattern_score': 50,
                    'album_completion_rate': 0,
                    'sequential_listening_score': 0,
                    'listening_style': 'Unknown'
                },
                'description': 'We encountered an issue analyzing your listening habits. This is a default personality profile.',
                'recommendations': [
                    'Try refreshing your data',
                    'Listen to more music to improve analysis accuracy',
                    'Check your Spotify connection'
                ]
            }
    
    def _calculate_variety_score(self, top_artists, top_tracks) -> float:
        """
        Calculate how varied the user's music taste is.
        
        Args:
            top_artists: List of user's top artists
            top_tracks: List of user's top tracks
            
        Returns:
            Variety score between 0 and 1
        """
        if not top_artists or not top_tracks:
            return 0.5
        
        # Count unique artists in top tracks
        track_artists = [track.get('artist', '') for track in top_tracks]
        unique_track_artists = len(set(track_artists))
        
        # Count unique genres
        genres = []
        for artist in top_artists:
            if isinstance(artist, dict):
                artist_genres = artist.get('genres', '').split(', ')
                genres.extend([g for g in artist_genres if g and g != 'Unknown'])
        
        unique_genres = len(set(genres))
        
        # Calculate variety metrics
        artist_variety = unique_track_artists / len(top_tracks) if top_tracks else 0
        genre_variety = min(unique_genres / 10, 1.0) if genres else 0
        
        # Combine metrics
        return (artist_variety * 0.6) + (genre_variety * 0.4)
    
    def _calculate_discovery_score(self, recently_played, top_tracks) -> float:
        """
        Calculate how much the user discovers new music.
        
        Args:
            recently_played: List of recently played tracks
            top_tracks: List of top tracks
            
        Returns:
            Discovery score between 0 and 1
        """
        if not recently_played or not top_tracks:
            return 0.5
        
        # Get artists from top tracks
        top_artists = set(track.get('artist', '') for track in top_tracks)
        
        # Count recently played tracks from non-top artists
        recent_artists = [track.get('artist', '') for track in recently_played]
        non_top_artist_count = sum(1 for artist in recent_artists if artist not in top_artists)
        
        # Calculate discovery ratio
        discovery_ratio = non_top_artist_count / len(recently_played) if recently_played else 0
        
        return discovery_ratio
    
    def _calculate_consistency_score(self, recently_played) -> float:
        """
        Calculate how consistent the user's listening patterns are.
        
        Args:
            recently_played: List of recently played tracks
            
        Returns:
            Consistency score between 0 and 1
        """
        if not recently_played:
            return 0.5
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(recently_played)
            
            # Check if required columns exist
            if 'played_at' not in df.columns:
                return 0.5
            
            # Add datetime column if not already present
            if 'played_at_dt' not in df.columns:
                df['played_at_dt'] = pd.to_datetime(df['played_at'])
            
            # Extract day of week and hour of day
            df['day_of_week'] = df['played_at_dt'].dt.day_name()
            df['hour_of_day'] = df['played_at_dt'].dt.hour
            
            # Calculate daily listening patterns
            day_counts = df['day_of_week'].value_counts()
            day_consistency = 1 - (day_counts.std() / day_counts.mean() if day_counts.mean() > 0 else 0)
            day_consistency = max(0, min(day_consistency, 1))  # Clamp between 0 and 1
            
            # Calculate hourly listening patterns
            hour_counts = df['hour_of_day'].value_counts()
            hour_consistency = 1 - (hour_counts.std() / hour_counts.mean() if hour_counts.mean() > 0 else 0)
            hour_consistency = max(0, min(hour_consistency, 1))  # Clamp between 0 and 1
            
            # Combine metrics
            return (day_consistency * 0.4) + (hour_consistency * 0.6)
        except Exception as e:
            print(f"Error calculating consistency score: {e}")
            return 0.5
    
    def _calculate_mood_score(self, audio_features) -> float:
        """
        Calculate the user's mood preference based on audio features.
        
        Args:
            audio_features: List of audio features for tracks
            
        Returns:
            Mood score between 0 and 1 (0 = melancholic, 1 = upbeat)
        """
        if not audio_features:
            return 0.5
        
        try:
            # Calculate average valence and energy
            valence_values = []
            energy_values = []
            
            for features in audio_features:
                if isinstance(features, dict):
                    valence_values.append(features.get('valence', 0))
                    energy_values.append(features.get('energy', 0))
            
            if not valence_values or not energy_values:
                return 0.5
                
            avg_valence = sum(valence_values) / len(valence_values)
            avg_energy = sum(energy_values) / len(energy_values)
            
            # Combine valence and energy for mood score
            mood_score = (avg_valence * 0.6) + (avg_energy * 0.4)
            
            return mood_score
        except Exception as e:
            print(f"Error calculating mood score: {e}")
            return 0.5
    
    def _calculate_time_pattern_score(self, recently_played) -> float:
        """
        Calculate how much the user's listening is tied to specific times.
        
        Args:
            recently_played: List of recently played tracks
            
        Returns:
            Time pattern score between 0 and 1
        """
        if not recently_played:
            return 0.5
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(recently_played)
            
            # Add datetime column if not already present
            if 'played_at_dt' not in df.columns:
                df['played_at_dt'] = pd.to_datetime(df['played_at'])
            
            # Extract hour of day
            df['hour_of_day'] = df['played_at_dt'].dt.hour
            
            # Calculate concentration of listening during specific hours
            hour_counts = df['hour_of_day'].value_counts()
            
            if len(hour_counts) <= 1:
                return 0.5
                
            # Calculate Gini coefficient as measure of concentration
            hour_counts_sorted = sorted(hour_counts.values)
            cumsum = np.cumsum(hour_counts_sorted)
            cumsum = np.insert(cumsum, 0, 0)
            n = len(hour_counts_sorted)
            
            if n == 0 or sum(hour_counts_sorted) == 0:
                return 0.5
            
            # Calculate Gini coefficient
            gini = (np.sum((2 * np.arange(1, n + 1) - n - 1) * hour_counts_sorted)) / (n * np.sum(hour_counts_sorted))
            
            # Normalize to 0-1
            time_pattern_score = (gini + 1) / 2
            
            return time_pattern_score
        except Exception as e:
            print(f"Error calculating time pattern score: {e}")
            return 0.5
    
    def _calculate_album_listening_patterns(self, recently_played) -> Dict[str, Any]:
        """
        Analyze if user tends to listen to full albums or individual tracks.
        
        Args:
            recently_played: List of recently played tracks
            
        Returns:
            Dictionary with album listening pattern metrics
        """
        if not recently_played:
            return {
                'album_completion_rate': 0,
                'sequential_listening_score': 0,
                'album_focused': False,
                'listening_style': 'Unknown'
            }
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(recently_played)
            
            # Check if album column exists
            if 'album' not in df.columns:
                return {
                    'album_completion_rate': 0,
                    'sequential_listening_score': 0,
                    'album_focused': False,
                    'listening_style': 'Unknown'
                }
            
            # Add datetime column if not already present
            if 'played_at_dt' not in df.columns:
                df['played_at_dt'] = pd.to_datetime(df['played_at'])
            
            # Sort by played_at
            df = df.sort_values('played_at_dt')
            
            # Group by album
            album_groups = df.groupby('album')
            
            # Calculate metrics
            total_albums = len(album_groups)
            albums_with_multiple_tracks = sum(1 for _, group in album_groups if len(group) > 1)
            
            # Calculate sequential listening (tracks from same album played consecutively)
            sequential_count = 0
            for i in range(1, len(df)):
                if df.iloc[i]['album'] == df.iloc[i-1]['album']:
                    sequential_count += 1
            
            # Calculate metrics
            if total_albums > 0:
                album_completion_rate = albums_with_multiple_tracks / total_albums
            else:
                album_completion_rate = 0
                
            if len(df) > 1:
                sequential_listening_score = sequential_count / (len(df) - 1)
            else:
                sequential_listening_score = 0
            
            # Determine listening style
            album_focused = sequential_listening_score > 0.4 or album_completion_rate > 0.3
            
            if album_focused:
                if sequential_listening_score > 0.7:
                    listening_style = "Album Purist"
                else:
                    listening_style = "Album Explorer"
            else:
                if sequential_listening_score < 0.2:
                    listening_style = "Track Hopper"
                else:
                    listening_style = "Mood Curator"
            
            return {
                'album_completion_rate': round(album_completion_rate * 100, 2),
                'sequential_listening_score': round(sequential_listening_score * 100, 2),
                'album_focused': album_focused,
                'listening_style': listening_style
            }
        except Exception as e:
            print(f"Error calculating album listening patterns: {e}")
            return {
                'album_completion_rate': 0,
                'sequential_listening_score': 0,
                'album_focused': False,
                'listening_style': 'Unknown'
            }
    
    def _estimate_dj_mode_usage(self, recently_played) -> Dict[str, Any]:
        """
        Estimate how much the user uses Spotify's DJ mode.
        
        Args:
            recently_played: List of recently played tracks
            
        Returns:
            Dictionary with DJ mode usage metrics
        """
        if not recently_played:
            return {
                'estimated_minutes': 0,
                'percentage_of_listening': 0,
                'dj_mode_user': False
            }
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(recently_played)
            
            # Add datetime column if not already present
            if 'played_at_dt' not in df.columns and 'played_at' in df.columns:
                df['played_at_dt'] = pd.to_datetime(df['played_at'])
            
            # Check if we have the necessary columns
            if 'played_at_dt' not in df.columns or 'artist' not in df.columns:
                return {
                    'estimated_minutes': 0,
                    'percentage_of_listening': 0,
                    'dj_mode_user': False
                }
            
            # Sort by played_at
            df = df.sort_values('played_at_dt')
            
            # Calculate time differences between consecutive tracks
            df['time_diff'] = df['played_at_dt'].diff().dt.total_seconds().fillna(0)
            
            # Calculate artist changes (1 if artist changed from previous track)
            df['artist_change'] = (df['artist'] != df['artist'].shift(1)).astype(int)
            
            # Identify potential DJ mode sessions
            # Criteria: Consistent time gaps (within 10% of average) and varied artists
            avg_time_diff = df['time_diff'].mean()
            df['consistent_timing'] = (
                (df['time_diff'] > 0.9 * avg_time_diff) & 
                (df['time_diff'] < 1.1 * avg_time_diff)
            )
            
            # A session is considered DJ mode if:
            # 1. At least 3 consecutive tracks with consistent timing
            # 2. At least 2 artist changes in those tracks
            session_length = 3
            potential_dj_sessions = []
            
            for i in range(len(df) - session_length + 1):
                window = df.iloc[i:i+session_length]
                if (window['consistent_timing'].sum() >= session_length - 1 and 
                    window['artist_change'].sum() >= 2):
                    potential_dj_sessions.append(i)
            
            # Calculate total DJ mode minutes
            total_dj_tracks = len(potential_dj_sessions)
            avg_track_duration_ms = df['duration_ms'].mean() if 'duration_ms' in df.columns else 210000  # Default 3:30
            total_dj_minutes = (total_dj_tracks * avg_track_duration_ms) / 60000
            
            # Calculate percentage of listening
            total_tracks = len(df)
            dj_percentage = (total_dj_tracks / total_tracks) * 100 if total_tracks > 0 else 0
            
            return {
                'estimated_minutes': round(total_dj_minutes, 2),
                'percentage_of_listening': round(dj_percentage, 2),
                'dj_mode_user': dj_percentage > 15  # Consider a DJ mode user if >15% of listening
            }
        except Exception as e:
            print(f"Error estimating DJ mode usage: {e}")
            return {
                'estimated_minutes': 0,
                'percentage_of_listening': 0,
                'dj_mode_user': False
            }
    
    def _determine_personality_types(self, variety_score, discovery_score, 
                                    consistency_score, mood_score, 
                                    time_pattern_score, album_patterns) -> Tuple[str, str]:
        """
        Determine primary and secondary personality types based on scores.
        
        Returns:
            Tuple of (primary_type, secondary_type)
        """
        try:
            # Get album-focused status
            album_focused = album_patterns.get('album_focused', False)
            
            # Define personality types and their score thresholds
            personality_scores = {
                'The Explorer': variety_score * 0.7 + discovery_score * 0.3,
                'The Enthusiast': discovery_score * 0.8 + variety_score * 0.2,
                'The Loyalist': (1 - variety_score) * 0.6 + consistency_score * 0.4,
                'The Curator': variety_score * 0.5 + (1 - discovery_score) * 0.5,
                'The Time Traveler': consistency_score * 0.3 + time_pattern_score * 0.7,
                'The Mood Master': mood_score * 0.5 + (1 - mood_score) * 0.5,
                'The Analyzer': consistency_score * 0.6 + (1 - discovery_score) * 0.4,
                'The Adventurer': discovery_score * 0.6 + (1 - consistency_score) * 0.4
            }
            
            # Add album-specific personalities if album-focused
            if album_focused:
                album_score = album_patterns.get('sequential_listening_score', 0) / 100
                personality_scores['The Album Purist'] = album_score * 0.8 + (1 - variety_score) * 0.2
            
            # Sort by score
            sorted_personalities = sorted(personality_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Return top two
            return sorted_personalities[0][0], sorted_personalities[1][0]
        except Exception as e:
            print(f"Error determining personality types: {e}")
            return "The Music Explorer", "The Listener"
    
    def _get_personality_description(self, personality_type: str) -> str:
        """
        Get description for a personality type.
        
        Args:
            personality_type: The personality type
            
        Returns:
            Description string
        """
        descriptions = {
            'The Explorer': "You're always on the hunt for new sounds and genres. Your playlist is a diverse tapestry of musical styles, and you're not afraid to venture into uncharted territory. You value musical discovery above all else.",
            
            'The Enthusiast': "You dive deep into new music with passion and excitement. When you discover a new artist or genre, you immerse yourself completely. Your friends often come to you for the latest musical recommendations.",
            
            'The Loyalist': "You know what you like and you stick with it. Your listening habits show strong loyalty to favorite artists and genres. You'd rather go deeper into music you love than constantly seek out new sounds.",
            
            'The Curator': "You're selective about what makes it into your rotation. Like a museum curator, you carefully choose each addition to your musical collection. Quality over quantity is your mantra.",
            
            'The Time Traveler': "Your listening habits are strongly tied to specific times and routines. Whether it's your morning commute playlist or evening wind-down tracks, your music is synchronized with your daily life.",
            
            'The Mood Master': "Your music choices are driven by emotion and atmosphere. You have an intuitive sense for selecting the perfect soundtrack for any mood or moment. Your playlists are emotional journeys.",
            
            'The Analyzer': "You approach music with a thoughtful, analytical mindset. You appreciate technical skill and complexity in your music. You likely enjoy discussing the finer points of production, composition, and arrangement.",
            
            'The Adventurer': "You're always looking for the next big thing. You're not afraid to take risks and try new, experimental music. Your playlist is a reflection of your adventurous spirit and love for pushing boundaries."
        }
        
        return descriptions.get(personality_type, "Unknown personality type.")

    def _get_personality_traits(self, personality_type: str) -> List[str]:
        """
        Get traits for a personality type.
        
        Args:
            personality_type: The personality type
            
        Returns:
            List of traits
        """
        traits = {
            'The Explorer': ["Diverse musical tastes", "Constantly seeking new music", "Broadens horizons"],
            'The Enthusiast': ["Passionate about new music", "Immersion in new genres", "Shares discoveries with others"],
            'The Loyalist': ["Strong loyalty to favorite artists", "Repeats listens to favorite tracks", "Consistency in musical choices"],
            'The Curator': ["Selective about music choices", "Quality over quantity", "Careful curation of playlists"],
            'The Time Traveler': ["Listening habits tied to routines", "Specific playlists for different times", "Music as a reflection of daily life"],
            'The Mood Master': ["Music driven by emotion", "Intuitive in selecting playlists", "Creates emotional atmospheres"],
            'The Analyzer': ["Analytical approach to music", "Enjoys discussing music", "Appreciation for technical aspects"],
            'The Adventurer': ["Risk-taking in music choices", "Loves experimental music", "Pushes boundaries in musical exploration"]
        }
        
        return traits.get(personality_type, [])

    def _get_personality_insights(self, personality_type: str) -> str:
        """
        Get insights for a personality type.
        
        Args:
            personality_type: The personality type
            
        Returns:
            Insights string
        """
        insights = {
            'The Explorer': "You might find it challenging to settle down with one genre or artist. However, this diversity can make your listening experience richer and more fulfilling.",

            'The Enthusiast': "Your love for new music is infectious. However, it's important to balance your eagerness to try new things with the need to appreciate and enjoy the music you already love.",

            'The Loyalist': "Your loyalty to your favorite artists and genres is admirable. However, it's important to occasionally step out of your comfort zone and explore new sounds. This can broaden your musical horizons and keep your listening experience fresh.",

            'The Curator': "Your careful curation of playlists is a testament to your discerning taste. However, it's important to remember that sometimes, the best music is the music you discover by chance.",

            'The Time Traveler': "Your listening habits are deeply ingrained in your daily routines. This can make your listening experience very personalized and fulfilling. However, it's important to occasionally break free from your routines and explore new music.",

            'The Mood Master': "Your intuitive sense for selecting the perfect soundtrack for any mood or moment is impressive. However, it's important to remember that sometimes, the best music is the music you didn't expect.",
            
                'The Analyzer': "Your analytical approach to music is refreshing. However, it's important to remember that sometimes, the best music is the music you love, regardless of its technical aspects.",

            'The Adventurer': "Your love for experimental and new music is admirable. However, it's important to remember that sometimes, the best music is the music that resonates with you on a personal level."
        }
        
        return insights.get(personality_type, "No insights available.")

    def _get_recommendations(self, personality_type: str) -> str:
        """
        Get recommendations for a personality type.
        
        Args:
            personality_type: The personality type
            
        Returns:
            Recommendations string
        """
        recommendations = {
            'The Explorer': "Try branching out into genres you're not familiar with. You never know what you might discover.",

            'The Enthusiast': "Don't forget to take a step back and appreciate the music you already love. Sometimes, the best music is the music you already know.",

            'The Loyalist': "Challenge yourself to try new artists within your favorite genres. You might discover new favorites you never knew existed.",

            'The Curator': "Don't be afraid to take risks and try new music. Sometimes, the best music is the music you didn't expect.",

            'The Time Traveler': "Try creating playlists that aren't tied to specific times or routines. You might discover new music that you love.",

            'The Mood Master': "Don't be afraid to try new genres or artists. Sometimes, the best music is the music you didn't expect.",

            'The Analyzer': "Don't forget to appreciate the music you love, regardless of its technical aspects. Sometimes, the best music is the music that resonates with you on a personal level.",

            'The Adventurer': "Don't be afraid to try new genres or artists. Sometimes, the best music is the music you didn't expect."
        }
        
        return recommendations.get(personality_type, "No recommendations available.") 
     
     
    
    