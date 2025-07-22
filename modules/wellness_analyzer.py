"""Wellness analysis and therapeutic music suggestions."""
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List

class WellnessAnalyzer:
    """Analyze listening patterns for wellness insights and therapeutic recommendations."""
    
    def __init__(self, db_path: str = 'data/spotify_data.db'):
        """Initialize the wellness analyzer."""
        self.db_path = db_path
        self.stress_indicators = {
            'high_energy_spike': {'energy': 0.8, 'valence': 0.3},  # High energy, low mood
            'repetitive_listening': {'repeat_threshold': 5},        # Same song many times
            'late_night_patterns': {'hour_start': 23, 'hour_end': 3}, # Late night listening
            'mood_volatility': {'valence_std_threshold': 0.3}       # Highly variable mood
        }
    
    def analyze_wellness_patterns(self, user_id: str) -> Dict:
        """Analyze user's listening patterns for wellness insights."""
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Get recent listening data (last 30 days)
            query = '''
                SELECT 
                    h.played_at,
                    t.name, t.artist,
                    t.energy, t.valence, t.danceability,
                    strftime('%H', h.played_at) as hour,
                    t.track_id
                FROM listening_history h
                JOIN tracks t ON h.track_id = t.track_id
                WHERE h.user_id = ?
                AND h.played_at >= date('now', '-30 days')
                AND t.energy IS NOT NULL
                AND t.valence IS NOT NULL
                ORDER BY h.played_at DESC
            '''
            
            df = pd.read_sql_query(query, conn, params=(user_id,))
            
            if df.empty:
                return self._default_wellness_response()
            
            # Calculate track frequency
            track_counts = df['track_id'].value_counts()
            df['track_frequency'] = df['track_id'].map(track_counts)
            
            # Analyze stress indicators
            stress_analysis = self._detect_stress_patterns(df)
            
            # Generate therapeutic recommendations
            therapeutic_suggestions = self._generate_therapeutic_suggestions(df, stress_analysis)
            
            # Calculate wellness score
            wellness_score = self._calculate_wellness_score(stress_analysis)
            
            return {
                'wellness_score': wellness_score,
                'stress_indicators': stress_analysis,
                'therapeutic_suggestions': therapeutic_suggestions,
                'focus_recommendations': self._get_focus_recommendations(user_id),
                'relaxation_tracks': self._get_relaxation_recommendations(user_id)
            }
            
        except Exception as e:
            print(f"Error analyzing wellness patterns: {e}")
            return self._default_wellness_response()
        finally:
            conn.close()
    
    def _detect_stress_patterns(self, df: pd.DataFrame) -> Dict:
        """Detect potential stress indicators in listening patterns."""
        stress_indicators = {}
        
        # 1. High energy + low valence spikes (agitated listening)
        agitated_sessions = df[(df['energy'] > 0.8) & (df['valence'] < 0.3)]
        stress_indicators['agitated_listening'] = {
            'detected': len(agitated_sessions) > 5,
            'frequency': len(agitated_sessions),
            'severity': 'high' if len(agitated_sessions) > 15 else 'moderate' if len(agitated_sessions) > 5 else 'low'
        }
        
        # 2. Repetitive listening (same songs on repeat)
        repetitive_tracks = df[df['track_frequency'] >= 5]
        stress_indicators['repetitive_behavior'] = {
            'detected': len(repetitive_tracks) > 0,
            'tracks': repetitive_tracks[['name', 'artist', 'track_frequency']].drop_duplicates().head(3).to_dict('records')
        }
        
        # 3. Late night listening patterns
        late_night_sessions = df[df['hour'].astype(int).isin([23, 0, 1, 2, 3])]
        stress_indicators['late_night_patterns'] = {
            'detected': len(late_night_sessions) > 10,
            'frequency': len(late_night_sessions),
            'avg_mood': late_night_sessions['valence'].mean() if len(late_night_sessions) > 0 else 0.5
        }
        
        # 4. Mood volatility
        df['date'] = pd.to_datetime(df['played_at']).dt.date
        daily_moods = df.groupby('date')['valence'].mean()
        mood_volatility = daily_moods.std() if len(daily_moods) > 1 else 0
        stress_indicators['mood_volatility'] = {
            'detected': mood_volatility > 0.25,
            'score': mood_volatility,
            'severity': 'high' if mood_volatility > 0.35 else 'moderate' if mood_volatility > 0.25 else 'low'
        }
        
        return stress_indicators
    
    def _generate_therapeutic_suggestions(self, df: pd.DataFrame, stress_analysis: Dict) -> List[Dict]:
        """Generate personalized therapeutic music suggestions."""
        suggestions = []
        
        # Based on stress indicators, suggest different approaches
        if stress_analysis['agitated_listening']['detected']:
            suggestions.append({
                'type': 'calming',
                'title': 'Calming Transition',
                'description': 'Try gradually shifting to lower energy music to help regulate intense emotions',
                'target_features': {'energy': 0.3, 'valence': 0.6, 'danceability': 0.4}
            })
        
        if stress_analysis['late_night_patterns']['detected']:
            suggestions.append({
                'type': 'sleep',
                'title': 'Better Sleep Routine',
                'description': 'Consider ambient or classical music before bed to improve sleep quality',
                'target_features': {'energy': 0.2, 'valence': 0.5, 'acousticness': 0.8}
            })
        
        if stress_analysis['mood_volatility']['detected']:
            suggestions.append({
                'type': 'stability',
                'title': 'Mood Stabilization',
                'description': 'Consistent, moderate-mood music can help create emotional balance',
                'target_features': {'valence': 0.6, 'energy': 0.5, 'danceability': 0.5}
            })
        
        # Always include focus and relaxation suggestions
        suggestions.extend([
            {
                'type': 'focus',
                'title': 'Deep Focus',
                'description': 'Instrumental music with steady rhythms for concentration',
                'target_features': {'instrumentalness': 0.8, 'energy': 0.4, 'valence': 0.6}
            },
            {
                'type': 'motivation',
                'title': 'Positive Energy',
                'description': 'Uplifting music to boost mood and motivation',
                'target_features': {'valence': 0.8, 'energy': 0.7, 'danceability': 0.6}
            }
        ])
        
        return suggestions[:4]  # Limit to 4 suggestions
    
    def _calculate_wellness_score(self, stress_analysis: Dict) -> float:
        """Calculate overall wellness score based on stress indicators."""
        base_score = 85  # Start with good baseline
        
        # Deduct points for stress indicators
        if stress_analysis['agitated_listening']['detected']:
            severity = stress_analysis['agitated_listening']['severity']
            if severity == 'high':
                base_score -= 20
            elif severity == 'moderate':
                base_score -= 10
        
        if stress_analysis['late_night_patterns']['detected']:
            base_score -= 10
        
        if stress_analysis['mood_volatility']['detected']:
            severity = stress_analysis['mood_volatility']['severity']
            if severity == 'high':
                base_score -= 15
            elif severity == 'moderate':
                base_score -= 8
        
        if stress_analysis['repetitive_behavior']['detected']:
            base_score -= 5
        
        return max(base_score, 30)  # Minimum score of 30
    
    def _get_focus_recommendations(self, user_id: str) -> List[Dict]:
        """Get music recommendations for focus and concentration."""
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Find instrumental tracks with moderate energy
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT t.name, t.artist, t.image_url
                FROM tracks t
                WHERE t.instrumentalness > 0.5
                AND t.energy BETWEEN 0.3 AND 0.6
                AND t.valence BETWEEN 0.4 AND 0.7
                AND t.track_id NOT IN (
                    SELECT track_id FROM listening_history WHERE user_id = ?
                )
                ORDER BY t.popularity DESC
                LIMIT 5
            ''', (user_id,))
            
            tracks = cursor.fetchall()
            return [{'name': track[0], 'artist': track[1], 'image_url': track[2]} for track in tracks]
            
        except Exception as e:
            print(f"Error getting focus recommendations: {e}")
            return []
        finally:
            conn.close()
    
    def _get_relaxation_recommendations(self, user_id: str) -> List[Dict]:
        """Get music recommendations for relaxation."""
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Find calm, acoustic tracks
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT t.name, t.artist, t.image_url
                FROM tracks t
                WHERE t.energy < 0.4
                AND t.valence BETWEEN 0.3 AND 0.7
                AND t.acousticness > 0.4
                AND t.track_id NOT IN (
                    SELECT track_id FROM listening_history WHERE user_id = ?
                )
                ORDER BY t.popularity DESC
                LIMIT 5
            ''', (user_id,))
            
            tracks = cursor.fetchall()
            return [{'name': track[0], 'artist': track[1], 'image_url': track[2]} for track in tracks]
            
        except Exception as e:
            print(f"Error getting relaxation recommendations: {e}")
            return []
        finally:
            conn.close()
    
    def _default_wellness_response(self) -> Dict:
        """Return default wellness response when no data is available."""
        return {
            'wellness_score': 75,
            'stress_indicators': {
                'agitated_listening': {'detected': False, 'frequency': 0, 'severity': 'low'},
                'repetitive_behavior': {'detected': False, 'tracks': []},
                'late_night_patterns': {'detected': False, 'frequency': 0, 'avg_mood': 0.5},
                'mood_volatility': {'detected': False, 'score': 0, 'severity': 'low'}
            },
            'therapeutic_suggestions': [
                {
                    'type': 'focus',
                    'title': 'Deep Focus',
                    'description': 'Instrumental music with steady rhythms for concentration',
                    'target_features': {'instrumentalness': 0.8, 'energy': 0.4, 'valence': 0.6}
                },
                {
                    'type': 'motivation',
                    'title': 'Positive Energy',
                    'description': 'Uplifting music to boost mood and motivation',
                    'target_features': {'valence': 0.8, 'energy': 0.7, 'danceability': 0.6}
                }
            ],
            'focus_recommendations': [],
            'relaxation_tracks': []
        }
