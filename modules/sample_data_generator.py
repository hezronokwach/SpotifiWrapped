"""
Comprehensive Sample Data Generator for Spotify Wrapped Remix
Generates realistic sample data for users without Spotify accounts.
"""

import random
import json
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid


class SampleDataGenerator:
    """Generate comprehensive, realistic sample data for the Spotify dashboard."""
    
    def __init__(self):
        """Initialize the sample data generator with realistic data pools."""

        # Placeholder image URLs for demo purposes
        self.placeholder_images = [
            "https://picsum.photos/300/300?random=1",
            "https://picsum.photos/300/300?random=2",
            "https://picsum.photos/300/300?random=3",
            "https://picsum.photos/300/300?random=4",
            "https://picsum.photos/300/300?random=5",
            "https://picsum.photos/300/300?random=6",
            "https://picsum.photos/300/300?random=7",
            "https://picsum.photos/300/300?random=8",
            "https://picsum.photos/300/300?random=9",
            "https://picsum.photos/300/300?random=10",
            "https://picsum.photos/300/300?random=11",
            "https://picsum.photos/300/300?random=12",
            "https://picsum.photos/300/300?random=13",
            "https://picsum.photos/300/300?random=14",
            "https://picsum.photos/300/300?random=15",
            "https://picsum.photos/300/300?random=16",
            "https://picsum.photos/300/300?random=17",
            "https://picsum.photos/300/300?random=18",
            "https://picsum.photos/300/300?random=19",
            "https://picsum.photos/300/300?random=20"
        ]

        # Sample artists with realistic genres and popularity
        self.sample_artists = [
            {"name": "The Midnight", "genres": ["synthwave", "electronic", "retrowave"], "popularity": 75, "followers": 850000},
            {"name": "Tame Impala", "genres": ["psychedelic rock", "indie rock", "neo-psychedelia"], "popularity": 85, "followers": 2100000},
            {"name": "Billie Eilish", "genres": ["pop", "electropop", "alternative pop"], "popularity": 95, "followers": 8500000},
            {"name": "Daft Punk", "genres": ["electronic", "house", "french house"], "popularity": 88, "followers": 4200000},
            {"name": "Arctic Monkeys", "genres": ["indie rock", "alternative rock", "garage rock"], "popularity": 82, "followers": 3100000},
            {"name": "Lorde", "genres": ["electropop", "indie pop", "art pop"], "popularity": 78, "followers": 1800000},
            {"name": "Glass Animals", "genres": ["indie rock", "psychedelic pop", "electronic"], "popularity": 80, "followers": 1500000},
            {"name": "ODESZA", "genres": ["electronic", "future bass", "chillwave"], "popularity": 76, "followers": 1200000},
            {"name": "Mac Miller", "genres": ["hip hop", "alternative hip hop", "jazz rap"], "popularity": 79, "followers": 2800000},
            {"name": "FKA twigs", "genres": ["alternative r&b", "experimental pop", "electronic"], "popularity": 72, "followers": 950000},
            {"name": "Radiohead", "genres": ["alternative rock", "experimental rock", "art rock"], "popularity": 84, "followers": 3800000},
            {"name": "Flume", "genres": ["electronic", "future bass", "experimental"], "popularity": 77, "followers": 1400000},
            {"name": "Tyler, The Creator", "genres": ["hip hop", "alternative hip hop", "neo-soul"], "popularity": 86, "followers": 3200000},
            {"name": "Phoebe Bridgers", "genres": ["indie rock", "indie folk", "singer-songwriter"], "popularity": 74, "followers": 1100000},
            {"name": "Bon Iver", "genres": ["indie folk", "experimental", "electronic"], "popularity": 73, "followers": 1300000}
        ]
        
        # Sample tracks with realistic audio features
        self.sample_tracks = [
            {
                "name": "Synthwave Dreams", "artist": "The Midnight", "album": "Endless Summer",
                "duration_ms": 245000, "popularity": 78,
                "audio_features": {"danceability": 0.65, "energy": 0.72, "valence": 0.68, "tempo": 118, "acousticness": 0.15}
            },
            {
                "name": "Elephant", "artist": "Tame Impala", "album": "Lonerism", 
                "duration_ms": 208000, "popularity": 85,
                "audio_features": {"danceability": 0.58, "energy": 0.81, "valence": 0.45, "tempo": 116, "acousticness": 0.08}
            },
            {
                "name": "bad guy", "artist": "Billie Eilish", "album": "WHEN WE ALL FALL ASLEEP, WHERE DO WE GO?",
                "duration_ms": 194000, "popularity": 92,
                "audio_features": {"danceability": 0.70, "energy": 0.43, "valence": 0.56, "tempo": 135, "acousticness": 0.11}
            },
            {
                "name": "One More Time", "artist": "Daft Punk", "album": "Discovery",
                "duration_ms": 320000, "popularity": 89,
                "audio_features": {"danceability": 0.88, "energy": 0.82, "valence": 0.91, "tempo": 123, "acousticness": 0.02}
            },
            {
                "name": "Do I Wanna Know?", "artist": "Arctic Monkeys", "album": "AM",
                "duration_ms": 272000, "popularity": 87,
                "audio_features": {"danceability": 0.67, "energy": 0.76, "valence": 0.35, "tempo": 85, "acousticness": 0.05}
            },
            {
                "name": "Royals", "artist": "Lorde", "album": "Pure Heroine",
                "duration_ms": 190000, "popularity": 83,
                "audio_features": {"danceability": 0.59, "energy": 0.44, "valence": 0.41, "tempo": 85, "acousticness": 0.35}
            },
            {
                "name": "Heat Waves", "artist": "Glass Animals", "album": "Dreamland",
                "duration_ms": 238000, "popularity": 91,
                "audio_features": {"danceability": 0.76, "energy": 0.74, "valence": 0.83, "tempo": 80, "acousticness": 0.44}
            },
            {
                "name": "Say My Name", "artist": "ODESZA", "album": "A Moment Apart",
                "duration_ms": 264000, "popularity": 75,
                "audio_features": {"danceability": 0.71, "energy": 0.68, "valence": 0.72, "tempo": 95, "acousticness": 0.18}
            },
            {
                "name": "Self Care", "artist": "Mac Miller", "album": "Swimming",
                "duration_ms": 583000, "popularity": 76,
                "audio_features": {"danceability": 0.42, "energy": 0.31, "valence": 0.28, "tempo": 68, "acousticness": 0.52}
            },
            {
                "name": "Two Weeks", "artist": "FKA twigs", "album": "LP1",
                "duration_ms": 247000, "popularity": 71,
                "audio_features": {"danceability": 0.63, "energy": 0.55, "valence": 0.38, "tempo": 96, "acousticness": 0.22}
            }
        ]
        
        # Sample playlists with realistic metadata
        self.sample_playlists = [
            {"name": "Chill Vibes", "total_tracks": 47, "public": True, "collaborative": False, "description": "Perfect for studying and relaxing"},
            {"name": "Workout Energy", "total_tracks": 32, "public": False, "collaborative": False, "description": "High-energy tracks for the gym"},
            {"name": "Indie Discoveries", "total_tracks": 89, "public": True, "collaborative": True, "description": "New indie finds and hidden gems"},
            {"name": "Late Night Drives", "total_tracks": 28, "public": False, "collaborative": False, "description": "Atmospheric music for nighttime journeys"},
            {"name": "Focus Flow", "total_tracks": 156, "public": True, "collaborative": False, "description": "Instrumental and ambient tracks for deep work"},
            {"name": "Throwback Hits", "total_tracks": 73, "public": False, "collaborative": True, "description": "Nostalgic favorites from the past"},
            {"name": "Electronic Explorations", "total_tracks": 64, "public": True, "collaborative": False, "description": "Cutting-edge electronic music"},
            {"name": "Acoustic Sessions", "total_tracks": 41, "public": False, "collaborative": False, "description": "Stripped-down acoustic performances"}
        ]
        
        # Realistic listening patterns
        self.listening_patterns = {
            "morning": {"peak_hours": [7, 8, 9], "energy_preference": 0.7, "valence_preference": 0.6},
            "afternoon": {"peak_hours": [13, 14, 15], "energy_preference": 0.6, "valence_preference": 0.5},
            "evening": {"peak_hours": [18, 19, 20], "energy_preference": 0.5, "valence_preference": 0.7},
            "night": {"peak_hours": [22, 23, 0], "energy_preference": 0.3, "valence_preference": 0.4}
        }
    
    def generate_user_profile(self) -> Dict[str, Any]:
        """Generate a realistic sample user profile."""
        return {
            'display_name': 'Demo User',
            'id': 'demo-user-spotify-wrapped',
            'followers': random.randint(15, 150),
            'following': random.randint(25, 200),
            'image_url': 'https://picsum.photos/150/150?random=user',  # Demo user avatar
            'product': 'premium',
            'country': 'US'
        }
    
    def generate_top_tracks(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Generate realistic top tracks with proper ranking and audio features."""
        tracks = []
        
        # Ensure we have enough tracks by cycling through and adding variations
        base_tracks = self.sample_tracks.copy()
        while len(tracks) < limit:
            for i, track in enumerate(base_tracks):
                if len(tracks) >= limit:
                    break
                    
                # Create variations for additional tracks
                variation_suffix = f" (Remix)" if len(tracks) >= len(base_tracks) else ""
                
                track_data = {
                    'track': track['name'] + variation_suffix,
                    'artist': track['artist'],
                    'album': track['album'],
                    'rank': len(tracks) + 1,
                    'popularity': max(50, track['popularity'] - random.randint(0, 10)),
                    'id': f"sample-track-{len(tracks) + 1}",
                    'name': track['name'] + variation_suffix,
                    'duration_ms': track['duration_ms'] + random.randint(-30000, 30000),
                    'explicit': random.choice([True, False]),
                    'preview_url': '',  # No preview for sample data
                    'image_url': random.choice(self.placeholder_images),  # Random album art
                    # Audio features with slight variations
                    'danceability': min(1.0, max(0.0, track['audio_features']['danceability'] + random.uniform(-0.1, 0.1))),
                    'energy': min(1.0, max(0.0, track['audio_features']['energy'] + random.uniform(-0.1, 0.1))),
                    'tempo': max(60, track['audio_features']['tempo'] + random.randint(-10, 10)),
                    'valence': min(1.0, max(0.0, track['audio_features']['valence'] + random.uniform(-0.1, 0.1))),
                    'acousticness': min(1.0, max(0.0, track['audio_features']['acousticness'] + random.uniform(-0.1, 0.1))),
                    'key': random.randint(0, 11),
                    'loudness': round(random.uniform(-12, -5), 2),
                    'mode': random.randint(0, 1),
                    'speechiness': round(random.uniform(0.03, 0.2), 3),
                    'instrumentalness': round(random.uniform(0, 0.4), 3),
                    'liveness': round(random.uniform(0.05, 0.3), 3)
                }
                tracks.append(track_data)
        
        return tracks[:limit]

    def generate_top_artists(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Generate realistic top artists with proper ranking."""
        artists = []

        # Shuffle artists for variety
        shuffled_artists = self.sample_artists.copy()
        random.shuffle(shuffled_artists)

        for i, artist in enumerate(shuffled_artists[:limit]):
            artist_data = {
                'artist': artist['name'],
                'name': artist['name'],  # For compatibility
                'rank': i + 1,
                'popularity': artist['popularity'] + random.randint(-5, 5),
                'genres': ', '.join(artist['genres']),
                'followers': artist['followers'] + random.randint(-50000, 50000),
                'id': f"sample-artist-{i + 1}",
                'image_url': random.choice(self.placeholder_images)  # Random artist photo
            }
            artists.append(artist_data)

        return artists

    def generate_playlists(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Generate realistic playlists."""
        playlists = []

        for i, playlist in enumerate(self.sample_playlists[:limit]):
            playlist_data = {
                'playlist': playlist['name'],
                'name': playlist['name'],  # For compatibility
                'total_tracks': playlist['total_tracks'] + random.randint(-5, 15),
                'public': playlist['public'],
                'collaborative': playlist['collaborative'],
                'id': f"sample-playlist-{i + 1}",
                'image_url': random.choice(self.placeholder_images),  # Random playlist cover
                'owner': 'Demo User',
                'description': playlist['description']
            }
            playlists.append(playlist_data)

        return playlists

    def generate_current_track(self) -> Dict[str, Any]:
        """Generate a currently playing track."""
        track = random.choice(self.sample_tracks)

        # Simulate playback progress
        progress_ms = random.randint(30000, track['duration_ms'] - 30000)

        return {
            'track': track['name'],
            'artist': track['artist'],
            'album': track['album'],
            'duration_ms': track['duration_ms'],
            'progress_ms': progress_ms,
            'is_playing': random.choice([True, False]),
            'id': f"current-sample-track",
            'name': track['name'],
            'popularity': track['popularity'],
            'preview_url': '',
            'image_url': random.choice(self.placeholder_images),
            'user_id': 'demo-user-spotify-wrapped'
        }

    def generate_listening_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Generate realistic listening history for the past N days."""
        history = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Generate 5-15 tracks per day with realistic patterns
        current_date = start_date
        while current_date <= end_date:
            # Determine listening pattern for this day
            is_weekend = current_date.weekday() >= 5
            daily_tracks = random.randint(8, 20) if is_weekend else random.randint(5, 15)

            for _ in range(daily_tracks):
                # Choose time of day based on realistic patterns
                time_period = random.choices(
                    ['morning', 'afternoon', 'evening', 'night'],
                    weights=[0.2, 0.3, 0.35, 0.15]
                )[0]

                pattern = self.listening_patterns[time_period]
                hour = random.choice(pattern['peak_hours'])
                minute = random.randint(0, 59)
                second = random.randint(0, 59)

                # Choose track based on time preferences
                suitable_tracks = [
                    t for t in self.sample_tracks
                    if abs(t['audio_features']['energy'] - pattern['energy_preference']) < 0.3
                ]
                if not suitable_tracks:
                    suitable_tracks = self.sample_tracks

                track = random.choice(suitable_tracks)

                played_at = current_date.replace(hour=hour, minute=minute, second=second)

                history_entry = {
                    'track_id': f"sample-track-{random.randint(1, 100)}",
                    'track': track['name'],
                    'artist': track['artist'],
                    'album': track['album'],
                    'played_at': played_at.isoformat(),
                    'end_time': (played_at + timedelta(milliseconds=track['duration_ms'])).isoformat(),
                    'id': track['name'],  # For compatibility
                    'duration_ms': track['duration_ms'],
                    'user_id': 'demo-user-spotify-wrapped'
                }
                history.append(history_entry)

            current_date += timedelta(days=1)

        # Sort by played_at
        history.sort(key=lambda x: x['played_at'])
        return history

    def generate_audio_features(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Generate audio features for tracks."""
        features = []

        for i, track in enumerate(self.sample_tracks[:limit]):
            # Add some variation to the base features
            base_features = track['audio_features']

            feature_data = {
                'track': track['name'],
                'artist': track['artist'],
                'danceability': min(1.0, max(0.0, base_features['danceability'] + random.uniform(-0.1, 0.1))),
                'energy': min(1.0, max(0.0, base_features['energy'] + random.uniform(-0.1, 0.1))),
                'key': random.randint(0, 11),
                'loudness': round(random.uniform(-12, -5), 2),
                'mode': random.randint(0, 1),
                'speechiness': round(random.uniform(0.03, 0.2), 3),
                'acousticness': min(1.0, max(0.0, base_features['acousticness'] + random.uniform(-0.1, 0.1))),
                'instrumentalness': round(random.uniform(0, 0.4), 3),
                'liveness': round(random.uniform(0.05, 0.3), 3),
                'valence': min(1.0, max(0.0, base_features['valence'] + random.uniform(-0.1, 0.1))),
                'tempo': max(60, base_features['tempo'] + random.randint(-10, 10)),
                'id': f"sample-track-{i + 1}",
                'duration_ms': track['duration_ms']
            }
            features.append(feature_data)

        return features

    def generate_wrapped_summary(self) -> Dict[str, Any]:
        """Generate a comprehensive Spotify Wrapped style summary."""
        # Calculate realistic metrics
        total_minutes = random.randint(8000, 25000)  # 133-416 hours per year
        hours = total_minutes // 60

        # Select top artist and track
        top_artist = random.choice(self.sample_artists)
        top_track = random.choice(self.sample_tracks)

        # Generate personality insights
        listening_styles = [
            "The Adventurous Explorer", "The Mood Curator", "The Genre Hopper",
            "The Deep Diver", "The Nostalgic Listener", "The Trend Setter"
        ]

        # Calculate music mood based on average audio features
        avg_valence = sum(t['audio_features']['valence'] for t in self.sample_tracks) / len(self.sample_tracks)
        avg_energy = sum(t['audio_features']['energy'] for t in self.sample_tracks) / len(self.sample_tracks)

        if avg_valence > 0.6 and avg_energy > 0.6:
            mood = "Energetic & Positive"
        elif avg_valence > 0.6:
            mood = "Happy & Chill"
        elif avg_energy > 0.6:
            mood = "Intense & Focused"
        else:
            mood = "Contemplative & Mellow"

        # Generate genre insights
        all_genres = []
        for artist in self.sample_artists:
            all_genres.extend(artist['genres'])

        from collections import Counter
        genre_counts = Counter(all_genres)
        top_genre = genre_counts.most_common(1)[0][0] if genre_counts else "indie rock"

        summary = {
            'timestamp': datetime.now().isoformat(),
            'top_track': {
                'name': top_track['name'],
                'artist': top_track['artist']
            },
            'top_artist': {
                'name': top_artist['name'],
                'genres': ', '.join(top_artist['genres'][:2])  # Top 2 genres
            },
            'total_minutes': total_minutes,
            'music_mood': {
                'mood': mood,
                'valence': round(avg_valence, 2),
                'energy': round(avg_energy, 2)
            },
            'genre_highlight': {
                'primary_genre': top_genre,
                'genre_diversity': len(set(all_genres))
            },
            'personality_type': random.choice(listening_styles),
            'metrics': {
                'listening_style': random.choice(listening_styles),
                'discovery_score': random.randint(65, 95),
                'variety_score': random.randint(70, 90),
                'total_hours': hours,
                'unique_artists': len(self.sample_artists),
                'unique_tracks': len(self.sample_tracks) * 3,  # Simulate more variety
                'top_listening_day': random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']),
                'peak_listening_time': random.choice(['Morning', 'Afternoon', 'Evening', 'Late Night'])
            },
            'dj_stats': {
                'estimated_minutes': max(1, int(total_minutes * 0.15)),  # 15% of listening
                'percentage_of_listening': 15,
                'dj_mode_user': True,
                'is_premium': True
            },
            'insights': {
                'most_skipped_genre': random.choice(['pop', 'country', 'classical']),
                'longest_listening_session': f"{random.randint(2, 8)} hours",
                'favorite_discovery_method': random.choice(['Discover Weekly', 'Release Radar', 'Daily Mix']),
                'music_exploration_score': random.randint(75, 95)
            }
        }

        return summary

    def _initialize_sample_database(self, db_path: str):
        """Initialize the sample database with the required schema."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    followers INTEGER DEFAULT 0,
                    last_updated TIMESTAMP
                )
            ''')

            # Tracks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tracks (
                    track_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    artist TEXT NOT NULL,
                    album TEXT,
                    duration_ms INTEGER,
                    popularity INTEGER,
                    preview_url TEXT,
                    image_url TEXT,
                    added_at TIMESTAMP,
                    last_seen TIMESTAMP,
                    danceability REAL,
                    energy REAL,
                    key INTEGER,
                    loudness REAL,
                    mode INTEGER,
                    speechiness REAL,
                    acousticness REAL,
                    instrumentalness REAL,
                    liveness REAL,
                    valence REAL,
                    tempo REAL
                )
            ''')

            # Listening history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS listening_history (
                    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    track_id TEXT NOT NULL,
                    played_at TIMESTAMP NOT NULL,
                    source TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (track_id) REFERENCES tracks (track_id),
                    UNIQUE (user_id, track_id, played_at)
                )
            ''')

            conn.commit()
            print("✅ Sample database schema initialized")

        except Exception as e:
            print(f"❌ Error initializing sample database: {e}")
            conn.rollback()
        finally:
            conn.close()

    def clear_sample_data_from_database(self, db_path: str = 'data/spotify_data.db'):
        """Remove all sample data from the database."""
        if not os.path.exists(db_path):
            return

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            print("🧹 Cleaning sample data from database...")

            # Remove sample user
            cursor.execute("DELETE FROM users WHERE user_id = 'demo-user-spotify-wrapped'")

            # Remove sample tracks
            cursor.execute("DELETE FROM tracks WHERE track_id LIKE 'sample-%'")

            # Remove sample listening history
            cursor.execute("DELETE FROM listening_history WHERE source = 'sample'")

            conn.commit()
            print("✅ Sample data cleaned from database")

        except Exception as e:
            print(f"❌ Error cleaning sample data: {e}")
            conn.rollback()
        finally:
            conn.close()

    def populate_sample_database(self, db_path: str = 'data/sample_spotify_data.db'):
        """Populate the database with comprehensive sample data."""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Initialize the sample database with proper schema
        self._initialize_sample_database(db_path)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            # Generate sample data
            user_profile = self.generate_user_profile()
            top_tracks = self.generate_top_tracks(50)
            top_artists = self.generate_top_artists(30)
            listening_history = self.generate_listening_history(90)  # 3 months of history

            # Insert user profile (matching existing schema)
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, display_name, followers)
                VALUES (?, ?, ?)
            ''', (
                user_profile['id'], user_profile['display_name'], user_profile['followers']
            ))

            # Insert tracks with audio features
            for track in top_tracks:
                cursor.execute('''
                    INSERT OR REPLACE INTO tracks (
                        track_id, name, artist, album, duration_ms, popularity,
                        preview_url, image_url, added_at, last_seen,
                        danceability, energy, key, loudness, mode,
                        speechiness, acousticness, instrumentalness,
                        liveness, valence, tempo
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP,
                              ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    track['id'], track['name'], track['artist'], track['album'],
                    track['duration_ms'], track['popularity'], track.get('preview_url', ''),
                    track.get('image_url', ''), datetime.now().isoformat(),
                    track['danceability'], track['energy'], track['key'],
                    track['loudness'], track['mode'], track['speechiness'],
                    track['acousticness'], track['instrumentalness'],
                    track['liveness'], track['valence'], track['tempo']
                ))

            # Insert listening history (matching existing schema)
            for entry in listening_history:
                cursor.execute('''
                    INSERT OR REPLACE INTO listening_history (
                        user_id, track_id, played_at, source
                    ) VALUES (?, ?, ?, ?)
                ''', (
                    entry['user_id'], entry['track_id'], entry['played_at'], 'sample'
                ))

            conn.commit()
            print(f"✅ Sample database populated with {len(top_tracks)} tracks and {len(listening_history)} listening entries")

        except Exception as e:
            print(f"❌ Error populating sample database: {e}")
            conn.rollback()
        finally:
            conn.close()

    def get_all_sample_data(self) -> Dict[str, Any]:
        """Get all sample data in a single call for easy integration."""
        return {
            'user_profile': self.generate_user_profile(),
            'top_tracks': self.generate_top_tracks(20),
            'top_artists': self.generate_top_artists(20),
            'playlists': self.generate_playlists(8),
            'current_track': self.generate_current_track(),
            'audio_features': self.generate_audio_features(20),
            'wrapped_summary': self.generate_wrapped_summary(),
            'listening_history': self.generate_listening_history(30)
        }


# Global instance for easy access
sample_data_generator = SampleDataGenerator()
