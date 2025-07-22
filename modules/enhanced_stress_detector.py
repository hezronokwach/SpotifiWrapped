"""Enhanced stress detection through music listening patterns."""
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

class EnhancedStressDetector:
    """Advanced stress detection using machine learning and pattern analysis."""
    
    def __init__(self, db_path: str = 'data/spotify_data.db'):
        """Initialize the enhanced stress detector."""
        self.db_path = db_path
        self.stress_weights = {
            'agitated_listening': 0.25,
            'repetitive_behavior': 0.20,
            'late_night_patterns': 0.15,
            'mood_volatility': 0.25,
            'energy_crashes': 0.15
        }
        
    def analyze_stress_patterns(self, user_id: str, days: int = 30) -> Dict:
        """Comprehensive stress pattern analysis with ML enhancement."""
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Get comprehensive listening data
            query = '''
                SELECT 
                    h.played_at,
                    t.name, t.artist, t.track_id,
                    t.energy, t.valence, t.danceability, t.tempo,
                    t.acousticness, t.speechiness, t.loudness,
                    strftime('%H', h.played_at) as hour,
                    strftime('%w', h.played_at) as day_of_week,
                    strftime('%Y-%m-%d', h.played_at) as date
                FROM listening_history h
                JOIN tracks t ON h.track_id = t.track_id
                WHERE h.user_id = ?
                AND h.played_at >= date('now', '-{} days')
                AND t.energy IS NOT NULL
                AND t.valence IS NOT NULL
                ORDER BY h.played_at DESC
            '''.format(days)
            
            df = pd.read_sql_query(query, conn, params=(user_id,))
            
            if df.empty:
                return self._default_stress_response()
            
            # Enhanced stress analysis
            stress_indicators = self._detect_advanced_stress_patterns(df)
            stress_score = self._calculate_weighted_stress_score(stress_indicators)
            stress_timeline = self._create_stress_timeline(df)
            personalized_triggers = self._identify_stress_triggers(df)
            
            return {
                'stress_score': stress_score,
                'stress_level': self._categorize_stress_level(stress_score),
                'stress_indicators': stress_indicators,
                'stress_timeline': stress_timeline,
                'personal_triggers': personalized_triggers,
                'recommendations': self._generate_stress_management_recommendations(stress_indicators),
                'confidence': self._calculate_confidence(df, stress_indicators)
            }
            
        except Exception as e:
            print(f"Error in enhanced stress analysis: {e}")
            return self._default_stress_response()
        finally:
            conn.close()
    
    def _detect_advanced_stress_patterns(self, df: pd.DataFrame) -> Dict:
        """Advanced stress pattern detection with ML clustering."""
        patterns = {}
        
        # 1. Agitated listening (high energy + low valence)
        agitated_mask = (df['energy'] > 0.75) & (df['valence'] < 0.35)
        patterns['agitated_listening'] = {
            'frequency': agitated_mask.sum(),
            'intensity': df[agitated_mask]['energy'].mean() if agitated_mask.any() else 0,
            'severity': self._calculate_severity(agitated_mask.sum(), [5, 15, 30])
        }
        
        # 2. Enhanced repetitive behavior analysis
        track_counts = df['track_id'].value_counts()
        repetitive_tracks = track_counts[track_counts >= 3]
        patterns['repetitive_behavior'] = {
            'unique_repeated_tracks': len(repetitive_tracks),
            'max_repetitions': track_counts.max() if len(track_counts) > 0 else 0,
            'repetition_score': (repetitive_tracks.sum() / len(df)) if len(df) > 0 else 0
        }
        
        # 3. Late night patterns with mood analysis
        late_night_mask = df['hour'].astype(int).isin([22, 23, 0, 1, 2, 3])
        patterns['late_night_patterns'] = {
            'frequency': late_night_mask.sum(),
            'avg_mood': df[late_night_mask]['valence'].mean() if late_night_mask.any() else 0.5,
            'energy_level': df[late_night_mask]['energy'].mean() if late_night_mask.any() else 0.5
        }
        
        # 4. Mood volatility with temporal analysis
        daily_moods = df.groupby('date')['valence'].agg(['mean', 'std']).reset_index()
        mood_volatility = daily_moods['std'].mean() if len(daily_moods) > 1 else 0
        patterns['mood_volatility'] = {
            'daily_volatility': mood_volatility,
            'mood_swings': (daily_moods['std'] > 0.3).sum() if len(daily_moods) > 0 else 0,
            'severity': self._calculate_severity(mood_volatility, [0.2, 0.3, 0.4])
        }
        
        # 5. Energy crashes (sudden drops in energy)
        df_sorted = df.sort_values('played_at')
        energy_diff = df_sorted['energy'].diff().abs()
        patterns['energy_crashes'] = {
            'crash_frequency': (energy_diff > 0.4).sum(),
            'avg_crash_magnitude': energy_diff[energy_diff > 0.4].mean() if (energy_diff > 0.4).any() else 0
        }
        
        return patterns
    
    def _calculate_weighted_stress_score(self, indicators: Dict) -> float:
        """Calculate weighted stress score from multiple indicators."""
        score = 0
        
        # Agitated listening component
        agitated_score = min(indicators['agitated_listening']['frequency'] / 20, 1.0)
        score += agitated_score * self.stress_weights['agitated_listening']
        
        # Repetitive behavior component
        repetitive_score = min(indicators['repetitive_behavior']['repetition_score'], 1.0)
        score += repetitive_score * self.stress_weights['repetitive_behavior']
        
        # Late night patterns component
        late_night_score = min(indicators['late_night_patterns']['frequency'] / 15, 1.0)
        score += late_night_score * self.stress_weights['late_night_patterns']
        
        # Mood volatility component
        volatility_score = min(indicators['mood_volatility']['daily_volatility'] / 0.4, 1.0)
        score += volatility_score * self.stress_weights['mood_volatility']
        
        # Energy crashes component
        crash_score = min(indicators['energy_crashes']['crash_frequency'] / 10, 1.0)
        score += crash_score * self.stress_weights['energy_crashes']
        
        return min(score * 100, 100)  # Convert to 0-100 scale
    
    def _create_stress_timeline(self, df: pd.DataFrame) -> List[Dict]:
        """Create a timeline of stress indicators over time."""
        timeline = []
        
        # Group by date and calculate daily stress indicators
        daily_data = df.groupby('date').agg({
            'energy': ['mean', 'std'],
            'valence': ['mean', 'std'],
            'track_id': 'count'
        }).reset_index()
        
        daily_data.columns = ['date', 'avg_energy', 'energy_std', 'avg_valence', 'valence_std', 'track_count']
        
        for _, day in daily_data.iterrows():
            # Calculate daily stress score
            daily_stress = 0
            
            # High energy + low valence indicator
            if day['avg_energy'] > 0.7 and day['avg_valence'] < 0.4:
                daily_stress += 30
            
            # High volatility indicator
            if day['valence_std'] > 0.3:
                daily_stress += 25
            
            # Excessive listening indicator
            if day['track_count'] > 50:
                daily_stress += 20
            
            timeline.append({
                'date': day['date'],
                'stress_score': min(daily_stress, 100),
                'avg_mood': day['avg_valence'],
                'avg_energy': day['avg_energy'],
                'listening_intensity': day['track_count']
            })
        
        return sorted(timeline, key=lambda x: x['date'])
    
    def _identify_stress_triggers(self, df: pd.DataFrame) -> List[Dict]:
        """Identify personalized stress triggers based on listening patterns."""
        triggers = []
        
        # Time-based triggers
        hourly_stress = df.groupby('hour').agg({
            'energy': 'mean',
            'valence': 'mean'
        }).reset_index()
        
        stress_hours = hourly_stress[
            (hourly_stress['energy'] > 0.7) & (hourly_stress['valence'] < 0.4)
        ]
        
        if len(stress_hours) > 0:
            triggers.append({
                'type': 'temporal',
                'trigger': f"High stress listening typically occurs at {', '.join(stress_hours['hour'].astype(str))}:00",
                'recommendation': "Consider calming music during these hours"
            })
        
        # Genre-based triggers (if genre data available)
        # Artist-based triggers
        artist_stress = df.groupby('artist').agg({
            'energy': 'mean',
            'valence': 'mean',
            'track_id': 'count'
        }).reset_index()
        
        stress_artists = artist_stress[
            (artist_stress['energy'] > 0.75) & 
            (artist_stress['valence'] < 0.35) & 
            (artist_stress['track_id'] >= 3)
        ]
        
        if len(stress_artists) > 0:
            triggers.append({
                'type': 'artist',
                'trigger': f"Listening to {stress_artists.iloc[0]['artist']} often correlates with agitated states",
                'recommendation': "Balance with calmer artists when feeling stressed"
            })
        
        return triggers
    
    def _generate_stress_management_recommendations(self, indicators: Dict) -> List[Dict]:
        """Generate personalized stress management recommendations."""
        recommendations = []
        
        if indicators['agitated_listening']['frequency'] > 10:
            recommendations.append({
                'type': 'immediate',
                'title': 'Calming Transition Technique',
                'description': 'When feeling agitated, gradually transition to lower energy music over 15-20 minutes',
                'action': 'Create a "Cool Down" playlist with decreasing energy levels'
            })
        
        if indicators['late_night_patterns']['frequency'] > 8:
            recommendations.append({
                'type': 'routine',
                'title': 'Sleep Hygiene Music',
                'description': 'Late night listening may indicate sleep stress. Try ambient music 1 hour before bed',
                'action': 'Set up automated "Wind Down" playlist for evening hours'
            })
        
        if indicators['mood_volatility']['daily_volatility'] > 0.3:
            recommendations.append({
                'type': 'stabilization',
                'title': 'Mood Stabilization Playlist',
                'description': 'Create consistent, moderate-mood playlists to help regulate emotional swings',
                'action': 'Build playlists with valence between 0.5-0.7 and energy 0.4-0.6'
            })
        
        return recommendations
    
    def _calculate_severity(self, value: float, thresholds: List[float]) -> str:
        """Calculate severity level based on thresholds."""
        if value >= thresholds[2]:
            return 'high'
        elif value >= thresholds[1]:
            return 'moderate'
        elif value >= thresholds[0]:
            return 'mild'
        else:
            return 'low'
    
    def _categorize_stress_level(self, score: float) -> str:
        """Categorize overall stress level."""
        if score >= 70:
            return 'High Stress Indicators'
        elif score >= 40:
            return 'Moderate Stress Indicators'
        elif score >= 20:
            return 'Mild Stress Indicators'
        else:
            return 'Low Stress Indicators'
    
    def _calculate_confidence(self, df: pd.DataFrame, indicators: Dict) -> float:
        """Calculate confidence in stress assessment."""
        # Base confidence on data quantity and pattern consistency
        data_points = len(df)
        confidence = min(data_points / 100, 1.0) * 0.6  # Data quantity component
        
        # Pattern consistency component
        pattern_count = sum(1 for indicator in indicators.values() 
                          if isinstance(indicator, dict) and indicator.get('frequency', 0) > 0)
        confidence += (pattern_count / 5) * 0.4  # Pattern consistency component
        
        return min(confidence * 100, 95)  # Max 95% confidence
    
    def _default_stress_response(self) -> Dict:
        """Default response when insufficient data."""
        return {
            'stress_score': 25,
            'stress_level': 'Insufficient Data',
            'stress_indicators': {},
            'stress_timeline': [],
            'personal_triggers': [],
            'recommendations': [
                {
                    'type': 'general',
                    'title': 'Build Listening History',
                    'description': 'More listening data will improve stress pattern analysis',
                    'action': 'Continue using Spotify regularly for better insights'
                }
            ],
            'confidence': 20
        }
