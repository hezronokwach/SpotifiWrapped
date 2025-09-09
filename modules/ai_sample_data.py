"""
Sample data generator for AI insights matching Dash implementation.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
import numpy as np

class AISampleDataGenerator:
    """Generate realistic sample data for AI insights components."""
    
    def __init__(self):
        self.sample_genres = [
            'Pop', 'Hip Hop', 'R&B', 'Afrobeats', 'Electronic', 'Indie', 
            'Rock', 'Jazz', 'Classical', 'Reggae', 'Country', 'Folk'
        ]
        
        self.sample_artists = [
            'Taylor Swift', 'Drake', 'Burna Boy', 'The Weeknd', 'Billie Eilish',
            'Kendrick Lamar', 'Ariana Grande', 'Ed Sheeran', 'Dua Lipa', 'Travis Scott',
            'SZA', 'Bad Bunny', 'Olivia Rodrigo', 'Harry Styles', 'Lorde'
        ]
        
        self.sample_tracks = [
            'Anti-Hero', 'God\'s Plan', 'Last Last', 'Blinding Lights', 'Bad Guy',
            'HUMBLE.', 'Thank U, Next', 'Shape of You', 'Levitating', 'SICKO MODE',
            'Good Days', 'Tití Me Preguntó', 'drivers license', 'As It Was', 'Solar Power'
        ]
    
    def generate_personality_analysis(self) -> Dict[str, Any]:
        """Generate sample personality analysis data."""
        personality_types = [
            {
                'name': 'The Sonic Explorer',
                'description': 'You have an adventurous spirit when it comes to music, constantly seeking new sounds and artists. Your playlist is a journey through different genres and eras, reflecting your curious and open-minded personality.',
                'confidence': 0.87,
                'traits': ['Curious', 'Open-minded', 'Creative', 'Adventurous']
            },
            {
                'name': 'The Mood Curator',
                'description': 'You use music as an emotional compass, carefully selecting tracks that match or enhance your current state of mind. Your listening patterns show sophisticated emotional intelligence.',
                'confidence': 0.82,
                'traits': ['Emotionally Intelligent', 'Introspective', 'Empathetic', 'Thoughtful']
            },
            {
                'name': 'The Rhythm Enthusiast',
                'description': 'Beat and rhythm drive your musical choices. You gravitate toward danceable, high-energy tracks that get your body moving and your spirit lifted.',
                'confidence': 0.79,
                'traits': ['Energetic', 'Social', 'Optimistic', 'Active']
            }
        ]
        
        selected_type = random.choice(personality_types)
        
        # Generate recommendations
        recommendations = []
        for i in range(5):
            recommendations.append({
                'name': random.choice(self.sample_tracks),
                'artist': random.choice(self.sample_artists),
                'image_url': f'https://picsum.photos/300/300?random={i+10}',
                'similarity_score': random.uniform(0.7, 0.95),
                'reason': random.choice([
                    'Matches your adventurous music taste',
                    'Similar energy to your top tracks',
                    'Complements your mood preferences',
                    'Fits your genre exploration pattern',
                    'Aligns with your emotional listening style'
                ])
            })
        
        return {
            'personality_type': selected_type['name'],
            'ai_description': selected_type['description'],
            'confidence_score': selected_type['confidence'],
            'traits': selected_type['traits'],
            'recommendations': recommendations,
            'audio_features': {
                'danceability': random.uniform(0.4, 0.8),
                'energy': random.uniform(0.5, 0.9),
                'valence': random.uniform(0.4, 0.8),
                'acousticness': random.uniform(0.1, 0.6)
            }
        }
    
    def generate_wellness_analysis(self) -> Dict[str, Any]:
        """Generate sample wellness analysis data."""
        wellness_score = random.randint(65, 90)
        
        mood_indicators = ['Very Positive', 'Positive', 'Balanced', 'Reflective']
        energy_levels = ['Very High', 'High', 'Moderate', 'Balanced']
        listening_frequencies = ['Very Active', 'Active', 'Moderate', 'Regular']
        
        recommendations = [
            'Your music choices show excellent emotional balance',
            'Continue exploring diverse genres for mental stimulation',
            'Consider creating playlists for different moods and activities',
            'Your listening patterns indicate healthy stress management',
            'Music is positively contributing to your overall wellness'
        ]
        
        return {
            'wellness_score': wellness_score,
            'mood_indicator': random.choice(mood_indicators),
            'energy_level': random.choice(energy_levels),
            'listening_frequency': random.choice(listening_frequencies),
            'recommendations': random.sample(recommendations, 3)
        }
    
    def generate_stress_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive sample stress analysis data."""
        stress_score = random.randint(15, 45)  # Generally low stress for sample
        
        # Generate stress indicators
        stress_indicators = {
            'agitated_listening': {
                'frequency': random.randint(2, 8),
                'intensity': random.uniform(0.3, 0.7),
                'severity': random.choice(['low', 'mild', 'moderate']),
                'confidence': random.uniform(0.6, 0.9),
                'research_basis': 'Dimitriev et al., 2023 - HRV studies showing stress response'
            },
            'repetitive_behavior': {
                'unique_repeated_tracks': random.randint(3, 12),
                'stress_repetitive_tracks': random.randint(0, 3),
                'happy_repetitive_tracks': random.randint(2, 8),
                'max_repetitions': random.randint(5, 15),
                'severity': random.choice(['low', 'mild']),
                'research_basis': 'Sachs et al., 2015; Groarke & Hogan, 2018'
            },
            'late_night_patterns': {
                'frequency': random.randint(1, 6),
                'avg_mood': random.uniform(0.4, 0.7),
                'avg_energy': random.uniform(0.3, 0.6),
                'severity': random.choice(['low', 'mild']),
                'research_basis': 'Hirotsu et al., 2015 - Cortisol nadir studies'
            },
            'mood_volatility': {
                'daily_volatility': random.uniform(0.1, 0.3),
                'mood_swings': random.randint(1, 5),
                'severity': random.choice(['low', 'mild']),
                'confidence': random.uniform(0.7, 0.9)
            },
            'energy_crashes': {
                'crash_frequency': random.randint(2, 8),
                'avg_crash_magnitude': random.uniform(0.2, 0.5)
            }
        }
        
        # Generate stress timeline
        stress_timeline = []
        base_date = datetime.now() - timedelta(days=30)
        for i in range(30):
            date = base_date + timedelta(days=i)
            daily_stress = max(10, stress_score + random.randint(-15, 15))
            
            stress_timeline.append({
                'date': date.strftime('%Y-%m-%d'),
                'stress_score': daily_stress,
                'avg_mood': random.uniform(0.4, 0.8),
                'avg_energy': random.uniform(0.4, 0.8),
                'listening_intensity': random.randint(10, 50)
            })
        
        # Generate personal triggers
        personal_triggers = [
            {
                'type': 'temporal',
                'trigger': 'High stress listening typically occurs at 22:00, 23:00',
                'recommendation': 'Consider calming music during these hours'
            },
            {
                'type': 'artist',
                'trigger': 'Listening to intense artists often correlates with agitated states',
                'recommendation': 'Balance with calmer artists when feeling stressed'
            }
        ]
        
        # Generate recommendations
        recommendations = [
            {
                'type': 'calming',
                'title': 'Calming Transition Technique',
                'description': 'When feeling agitated, gradually transition to lower energy music over 15-20 minutes',
                'action': 'Create a "Cool Down" playlist with decreasing energy levels'
            },
            {
                'type': 'sleep',
                'title': 'Sleep Hygiene Music',
                'description': 'Use ambient music 1 hour before bed to improve sleep quality',
                'action': 'Set up automated "Wind Down" playlist for evening hours'
            },
            {
                'type': 'stability',
                'title': 'Mood Stabilization Playlist',
                'description': 'Create consistent, moderate-mood playlists to help regulate emotional swings',
                'action': 'Build playlists with valence between 0.5-0.7 and energy 0.4-0.6'
            }
        ]
        
        return {
            'stress_score': stress_score,
            'stress_level': 'Low Stress Indicators' if stress_score < 30 else 'Mild Stress Indicators',
            'stress_indicators': stress_indicators,
            'stress_timeline': stress_timeline,
            'personal_triggers': personal_triggers,
            'recommendations': recommendations,
            'confidence': random.randint(75, 90),
            'scientific_disclaimer': 'This analysis is based on music listening patterns and should not replace professional mental health assessment.'
        }
    
    def generate_genre_evolution(self) -> Dict[str, Any]:
        """Generate sample genre evolution data."""
        # Generate timeline data for last 6 months
        timeline_data = []
        base_date = datetime.now() - timedelta(days=180)
        
        # Select 5-6 genres for evolution
        selected_genres = random.sample(self.sample_genres, 6)
        
        for i in range(6):
            month_date = base_date + timedelta(days=30 * i)
            month_str = month_date.strftime('%Y-%m')
            
            month_genres = {}
            for j, genre in enumerate(selected_genres):
                # Create realistic evolution patterns
                base_count = random.randint(8, 25)
                
                # Some genres trend up, others down, others stable
                if j == 0:  # First genre trends up
                    count = base_count + (i * 3)
                elif j == 1:  # Second genre stable
                    count = base_count + random.randint(-2, 2)
                elif j == 2:  # Third genre trends down
                    count = max(5, base_count - (i * 2))
                else:  # Others vary
                    count = base_count + random.randint(-5, 5)
                
                month_genres[genre] = max(1, count)
            
            timeline_data.append({
                'month': month_str,
                'genres': month_genres,
                'total_plays': sum(month_genres.values())
            })
        
        # Generate insights
        insights = [
            f'📈 {selected_genres[0]} has been your fastest growing genre this year',
            f'🎯 {selected_genres[1]} remains consistently in your rotation',
            f'🌟 Your taste shows healthy diversity across {len(selected_genres)} main genres',
            f'🔄 You\'ve been exploring more {random.choice(selected_genres)} lately'
        ]
        
        # Current top genres
        current_top_genres = []
        latest_month = timeline_data[-1]['genres']
        sorted_genres = sorted(latest_month.items(), key=lambda x: x[1], reverse=True)
        
        for genre, plays in sorted_genres[:5]:
            current_top_genres.append({'genre': genre, 'plays': plays})
        
        # Biggest changes
        biggest_changes = []
        first_month = timeline_data[0]['genres']
        last_month = timeline_data[-1]['genres']
        
        for genre in selected_genres:
            change = last_month.get(genre, 0) - first_month.get(genre, 0)
            if abs(change) >= 5:
                biggest_changes.append({
                    'genre': genre,
                    'change': change,
                    'direction': 'increased' if change > 0 else 'decreased'
                })
        
        return {
            'timeline_data': timeline_data,
            'insights': random.sample(insights, 3),
            'current_top_genres': current_top_genres,
            'biggest_changes': biggest_changes[:3]
        }
    
    def generate_advanced_recommendations(self) -> Dict[str, Any]:
        """Generate sample advanced recommendations with music DNA."""
        # Generate music DNA profile
        music_dna = {
            'danceability': random.uniform(0.5, 0.8),
            'energy': random.uniform(0.6, 0.9),
            'valence': random.uniform(0.5, 0.8),
            'tempo': random.uniform(110, 140),
            'acousticness': random.uniform(0.1, 0.4),
            'instrumentalness': random.uniform(0.0, 0.2)
        }
        
        # Generate recommendations
        recommendations = []
        for i in range(8):
            recommendations.append({
                'name': random.choice(self.sample_tracks),
                'artist': random.choice(self.sample_artists),
                'image_url': f'https://picsum.photos/300/300?random={i+20}',
                'similarity_score': random.uniform(0.75, 0.95),
                'reason': random.choice([
                    'Perfect match for your energy preferences',
                    'Complements your danceability profile',
                    'Matches your mood and tempo preferences',
                    'Similar to your top artists but undiscovered',
                    'Fits your acoustic-electronic balance',
                    'Aligns with your valence patterns'
                ])
            })
        
        return {
            'recommendations': recommendations,
            'music_dna': music_dna,
            'total_count': len(recommendations)
        }
    
    def generate_music_dna(self) -> Dict[str, Any]:
        """Generate sample music DNA profile."""
        return {
            'danceability': random.uniform(0.4, 0.8),
            'energy': random.uniform(0.5, 0.9),
            'valence': random.uniform(0.4, 0.8),
            'tempo': random.uniform(100, 150),
            'acousticness': random.uniform(0.1, 0.6),
            'instrumentalness': random.uniform(0.0, 0.3),
            'top_genre': random.choice(self.sample_genres),
            'diversity_score': random.uniform(0.6, 0.9),
            'total_tracks': random.randint(150, 500)
        }
    
    def generate_insights_summary(self) -> Dict[str, Any]:
        """Generate comprehensive AI insights summary."""
        personality_data = self.generate_personality_analysis()
        stress_data = self.generate_stress_analysis()
        wellness_data = self.generate_wellness_analysis()
        
        return {
            'personality': {
                'type': personality_data['personality_type'],
                'confidence': personality_data['confidence_score']
            },
            'stress': {
                'score': stress_data['stress_score'],
                'level': stress_data['stress_level']
            },
            'wellness': {
                'score': wellness_data['wellness_score'],
                'mood': wellness_data['mood_indicator']
            }
        }

# Global instance for easy access
ai_sample_generator = AISampleDataGenerator()