"""AI-powered personality enhancement and content-based recommendations."""
import google.generativeai as genai
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class EnhancedPersonalityAnalyzer:
    """AI-enhanced personality analyzer with LLM-powered descriptions and content-based recommendations."""
    
    def __init__(self, db_path: str = 'data/spotify_data.db'):
        """Initialize the analyzer with database path and Gemini client."""
        self.db_path = db_path

        # Initialize Gemini client
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.llm_available = True
            print("✅ Gemini AI initialized successfully!")
        else:
            self.model = None
            self.llm_available = False
            print("⚠️  GEMINI_API_KEY not found. Using enhanced fallback descriptions.")
    
    def generate_enhanced_personality(self, user_id: str) -> Dict:
        """Generate AI-enhanced personality description."""
        # Get user data from database
        user_data = self._get_user_listening_data(user_id)
        
        # Generate LLM description
        ai_description = self._generate_llm_description(user_data)
        
        # Get smart content-based recommendations
        recommendations = self._get_content_based_recommendations(user_id)
        
        return {
            'ai_description': ai_description,
            'recommendations': recommendations,
            'personality_type': user_data.get('personality_type', 'Music Explorer'),
            'confidence_score': self._calculate_confidence(user_data)
        }
    
    def _get_user_listening_data(self, user_id: str) -> Dict:
        """Get comprehensive user listening data from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get basic user stats
            cursor.execute('''
                SELECT 
                    COUNT(DISTINCT h.track_id) as unique_tracks,
                    COUNT(*) as total_plays,
                    AVG(t.energy) as avg_energy,
                    AVG(t.valence) as avg_valence,
                    AVG(t.danceability) as avg_danceability
                FROM listening_history h
                JOIN tracks t ON h.track_id = t.track_id
                WHERE h.user_id = ?
                AND t.energy IS NOT NULL
            ''', (user_id,))
            
            stats = cursor.fetchone()
            
            # Get top artist
            cursor.execute('''
                SELECT t.artist, COUNT(*) as play_count
                FROM listening_history h
                JOIN tracks t ON h.track_id = t.track_id
                WHERE h.user_id = ?
                GROUP BY t.artist
                ORDER BY play_count DESC
                LIMIT 1
            ''', (user_id,))
            
            top_artist_result = cursor.fetchone()
            top_artist = top_artist_result[0] if top_artist_result else 'Various Artists'
            
            # Get top genre
            cursor.execute('''
                SELECT g.genre_name, COUNT(*) as genre_count
                FROM listening_history h
                JOIN tracks t ON h.track_id = t.track_id
                JOIN genres g ON t.artist = g.artist_name
                WHERE h.user_id = ?
                GROUP BY g.genre_name
                ORDER BY genre_count DESC
                LIMIT 1
            ''', (user_id,))
            
            top_genre_result = cursor.fetchone()
            top_genre = top_genre_result[0] if top_genre_result else 'Mixed'
            
            # Calculate listening hours (estimate)
            total_hours = (stats[1] * 3.5) / 60 if stats[1] else 0  # Assume 3.5 min avg song length
            
            # Calculate variety score
            variety_score = min((stats[0] / max(stats[1], 1)) * 100, 100) if stats[0] else 50
            
            # Determine peak listening time (simplified)
            cursor.execute('''
                SELECT strftime('%H', h.played_at) as hour, COUNT(*) as count
                FROM listening_history h
                WHERE h.user_id = ?
                GROUP BY hour
                ORDER BY count DESC
                LIMIT 1
            ''', (user_id,))
            
            peak_hour_result = cursor.fetchone()
            if peak_hour_result:
                hour = int(peak_hour_result[0])
                if 6 <= hour < 12:
                    peak_time = 'Morning'
                elif 12 <= hour < 18:
                    peak_time = 'Afternoon'
                elif 18 <= hour < 22:
                    peak_time = 'Evening'
                else:
                    peak_time = 'Night'
            else:
                peak_time = 'Evening'
            
            # Determine recent mood based on valence
            recent_mood = 'Balanced'
            if stats[3]:  # avg_valence
                if stats[3] > 0.7:
                    recent_mood = 'Upbeat'
                elif stats[3] < 0.3:
                    recent_mood = 'Mellow'
            
            return {
                'top_artist': top_artist,
                'top_genre': top_genre,
                'total_hours': round(total_hours, 1),
                'variety_score': round(variety_score, 1),
                'peak_listening_time': peak_time,
                'recent_mood': recent_mood,
                'unique_tracks': stats[0] or 0,
                'total_plays': stats[1] or 0,
                'avg_energy': stats[2] or 0.5,
                'avg_valence': stats[3] or 0.5,
                'avg_danceability': stats[4] or 0.5
            }
            
        except Exception as e:
            print(f"Error getting user listening data: {e}")
            return {
                'top_artist': 'Various Artists',
                'top_genre': 'Mixed',
                'total_hours': 0,
                'variety_score': 50,
                'peak_listening_time': 'Evening',
                'recent_mood': 'Balanced',
                'unique_tracks': 0,
                'total_plays': 0,
                'avg_energy': 0.5,
                'avg_valence': 0.5,
                'avg_danceability': 0.5
            }
        finally:
            conn.close()
    
    def _generate_llm_description(self, user_data: Dict) -> str:
        """Generate personality description using Gemini."""
        if not self.llm_available:
            return self._fallback_description(user_data)

        prompt = f"""
        Create a personalized, engaging music personality description for this user:

        Data:
        - Top artist: {user_data.get('top_artist', 'Various')}
        - Dominant genre: {user_data.get('top_genre', 'Mixed')}
        - Listening hours: {user_data.get('total_hours', 0)}
        - Variety score: {user_data.get('variety_score', 50)}/100
        - Most active time: {user_data.get('peak_listening_time', 'Evening')}
        - Recent mood: {user_data.get('recent_mood', 'Balanced')}
        - Average energy: {user_data.get('avg_energy', 0.5):.2f}
        - Average valence: {user_data.get('avg_valence', 0.5):.2f}

        Write 2-3 sentences that are:
        - Personal and specific (not generic)
        - Encouraging and positive
        - Insightful about their music taste
        - Written like a knowledgeable music friend
        - Focus on their unique listening patterns

        Keep it under 150 words and make it sound natural and engaging.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini generation failed: {e}")
            return self._fallback_description(user_data)
    
    def _fallback_description(self, user_data: Dict) -> str:
        """Generate enhanced fallback description when LLM is not available."""
        top_artist = user_data.get('top_artist', 'various artists')
        top_genre = user_data.get('top_genre', 'mixed genres')
        hours = user_data.get('total_hours', 0)
        variety = user_data.get('variety_score', 50)
        energy = user_data.get('avg_energy', 0.5)
        valence = user_data.get('avg_valence', 0.5)
        peak_time = user_data.get('peak_listening_time', 'Evening')

        # Determine listening personality based on data
        if variety > 80:
            personality = "musical adventurer"
            trait = "constantly seeking new sonic territories"
        elif variety > 60:
            personality = "eclectic explorer"
            trait = "balancing discovery with familiar favorites"
        elif variety > 40:
            personality = "balanced curator"
            trait = "carefully selecting music that resonates"
        else:
            personality = "devoted enthusiast"
            trait = "deeply connected to your chosen sounds"

        # Determine mood preference
        if valence > 0.7:
            mood_desc = "gravitating toward uplifting, positive vibes"
        elif valence > 0.4:
            mood_desc = "enjoying a balanced emotional spectrum"
        else:
            mood_desc = "drawn to deeper, more contemplative moods"

        # Determine energy preference
        if energy > 0.7:
            energy_desc = "high-energy tracks that fuel your day"
        elif energy > 0.4:
            energy_desc = "moderate energy that matches your rhythm"
        else:
            energy_desc = "mellow, laid-back soundscapes"

        # Create personalized description
        description = f"You're a {personality}, {trait}. Your {hours:.1f} hours with {top_artist} " \
                     f"showcase your love for {top_genre}, while {mood_desc} and preferring {energy_desc}. " \
                     f"Your {peak_time.lower()} listening sessions reveal someone who uses music as both " \
                     f"companion and soundtrack to life's moments."

        return description
    
    def _calculate_confidence(self, user_data: Dict) -> float:
        """Calculate confidence score for the personality analysis."""
        total_plays = user_data.get('total_plays', 0)
        unique_tracks = user_data.get('unique_tracks', 0)

        # Base confidence on amount of data
        if total_plays > 100 and unique_tracks > 50:
            return 0.9
        elif total_plays > 50 and unique_tracks > 25:
            return 0.75
        elif total_plays > 20 and unique_tracks > 10:
            return 0.6
        else:
            return 0.4

    def _get_content_based_recommendations(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Get recommendations based on user's personal music DNA (content-based filtering)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Get user's audio feature preferences from listening history
            cursor.execute('''
                SELECT
                    AVG(t.danceability) as avg_danceability,
                    AVG(t.energy) as avg_energy,
                    AVG(t.valence) as avg_valence,
                    AVG(t.acousticness) as avg_acousticness,
                    AVG(t.tempo) as avg_tempo
                FROM tracks t
                JOIN listening_history h ON t.track_id = h.track_id
                WHERE h.user_id = ?
                AND t.danceability IS NOT NULL
            ''', (user_id,))

            user_profile = cursor.fetchone()
            if not user_profile or not any(user_profile):
                return []

            # Get user's top genres
            cursor.execute('''
                SELECT g.genre_name, COUNT(*) as genre_count
                FROM genres g
                JOIN tracks t ON g.artist_name = t.artist
                JOIN listening_history h ON t.track_id = h.track_id
                WHERE h.user_id = ?
                GROUP BY g.genre_name
                ORDER BY genre_count DESC
                LIMIT 3
            ''', (user_id,))

            top_genres = [row[0] for row in cursor.fetchall()]

            # Find tracks similar to user's preferences that they haven't heard
            # Try genre-matched tracks first, then fall back to all tracks
            candidate_tracks = []

            # First attempt: Try genre-matched tracks
            if top_genres:
                genre_placeholders = ','.join(['?' for _ in top_genres])
                cursor.execute(f'''
                    SELECT DISTINCT t.track_id, t.name, t.artist, t.image_url,
                           t.danceability, t.energy, t.valence, t.acousticness, t.tempo,
                           t.popularity
                    FROM tracks t
                    LEFT JOIN genres g ON t.artist = g.artist_name
                    WHERE t.track_id NOT IN (
                        SELECT DISTINCT track_id
                        FROM listening_history
                        WHERE user_id = ?
                    )
                    AND t.danceability IS NOT NULL
                    AND t.energy IS NOT NULL
                    AND t.valence IS NOT NULL
                    AND g.genre_name IN ({genre_placeholders})
                    ORDER BY t.popularity DESC
                    LIMIT 50
                ''', (user_id, *top_genres))

                candidate_tracks = cursor.fetchall()

            # Fallback: If no genre matches, use all unheard tracks with audio features
            if not candidate_tracks:
                print(f"No genre-matched tracks found, using all unheard tracks for user {user_id}")
                cursor.execute('''
                    SELECT DISTINCT t.track_id, t.name, t.artist, t.image_url,
                           t.danceability, t.energy, t.valence, t.acousticness, t.tempo,
                           t.popularity
                    FROM tracks t
                    WHERE t.track_id NOT IN (
                        SELECT DISTINCT track_id
                        FROM listening_history
                        WHERE user_id = ?
                    )
                    AND t.danceability IS NOT NULL
                    AND t.energy IS NOT NULL
                    AND t.valence IS NOT NULL
                    ORDER BY t.popularity DESC
                    LIMIT 50
                ''', (user_id,))

                candidate_tracks = cursor.fetchall()

            candidate_tracks = cursor.fetchall()

            if not candidate_tracks:
                return []

            # Calculate similarity scores based on audio features
            recommendations = []
            user_features = np.array([
                user_profile[0] or 0.5,  # danceability
                user_profile[1] or 0.5,  # energy
                user_profile[2] or 0.5,  # valence
                user_profile[3] or 0.5,  # acousticness
                (user_profile[4] or 120) / 200  # tempo (normalized)
            ])

            for track in candidate_tracks:
                track_features = np.array([
                    track[4] or 0.5,  # danceability
                    track[5] or 0.5,  # energy
                    track[6] or 0.5,  # valence
                    track[7] or 0.5,  # acousticness
                    (track[8] or 120) / 200  # tempo (normalized)
                ])

                # Calculate cosine similarity
                similarity = np.dot(user_features, track_features) / (
                    np.linalg.norm(user_features) * np.linalg.norm(track_features)
                )

                # Add popularity boost
                popularity_boost = (track[9] or 50) / 100 * 0.1
                final_score = similarity + popularity_boost

                # Check if this track is from user's preferred genres
                is_genre_match = False
                if top_genres:
                    cursor.execute('''
                        SELECT COUNT(*) FROM genres g
                        WHERE g.artist_name = ? AND g.genre_name IN ({})
                    '''.format(','.join(['?' for _ in top_genres])), (track[2], *top_genres))
                    is_genre_match = cursor.fetchone()[0] > 0

                recommendations.append({
                    'name': track[1],
                    'artist': track[2],
                    'image_url': track[3],
                    'similarity_score': round(final_score, 3),
                    'reason': self._generate_recommendation_reason(similarity, user_features, track_features, is_genre_match)
                })

            # Sort by similarity and return top recommendations
            recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
            return recommendations[:limit]

        except Exception as e:
            print(f"Error generating content-based recommendations: {e}")
            return []
        finally:
            conn.close()

    def _generate_recommendation_reason(self, similarity: float, user_features: np.array, track_features: np.array, is_genre_match: bool = False) -> str:
        """Generate a personalized reason for the recommendation."""
        if similarity > 0.9:
            reason = "Perfect match for your music DNA!"
        elif similarity > 0.8:
            reason = "Very similar to your favorite tracks"
        elif similarity > 0.7:
            # Find the most similar feature
            feature_names = ['danceability', 'energy', 'mood', 'acousticness', 'tempo']
            feature_similarities = 1 - np.abs(user_features - track_features)
            best_feature = feature_names[np.argmax(feature_similarities)]
            reason = f"Matches your preferred {best_feature}"
        elif similarity > 0.6:
            reason = "Good fit based on your listening patterns"
        else:
            reason = "Might expand your musical horizons"

        # Add genre context
        if is_genre_match:
            reason += " (from your favorite genres)"
        else:
            reason += " (new genre exploration)"

        return reason
