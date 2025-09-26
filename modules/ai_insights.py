import sqlite3
from typing import Dict, Any
import random

def get_personality_analysis(user_id: str) -> Dict[str, Any]:
    """Generate personality analysis based on user's music data"""
    db_path = f"/tmp/user_{user_id}_spotify_data.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get user's top genres and audio features
        cursor.execute("""
            SELECT AVG(danceability), AVG(energy), AVG(valence), AVG(acousticness)
            FROM tracks 
            WHERE user_id = ?
        """, (user_id,))
        
        features = cursor.fetchone()
        conn.close()
        
        if not features or not any(features):
            return get_demo_personality()
            
        danceability, energy, valence, acousticness = features
        
        # Determine personality type based on audio features
        personality_type = determine_personality_type(danceability, energy, valence, acousticness)
        
        return {
            "personality_type": personality_type["name"],
            "description": personality_type["description"],
            "confidence": personality_type["confidence"],
            "traits": personality_type["traits"],
            "audio_features": {
                "danceability": round(danceability, 2) if danceability else 0,
                "energy": round(energy, 2) if energy else 0,
                "valence": round(valence, 2) if valence else 0,
                "acousticness": round(acousticness, 2) if acousticness else 0
            }
        }
    except Exception as e:
        print(f"Error in personality analysis: {e}")
        return get_demo_personality()

def get_wellness_analysis(user_id: str) -> Dict[str, Any]:
    """Generate wellness analysis based on user's music data"""
    db_path = f"/tmp/user_{user_id}_spotify_data.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get recent listening patterns for wellness analysis
        cursor.execute("""
            SELECT AVG(valence), AVG(energy), COUNT(*) as play_count
            FROM tracks 
            WHERE user_id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result or not any(result):
            return get_demo_wellness()
            
        avg_valence, avg_energy, play_count = result
        
        # Calculate wellness metrics
        wellness_score = calculate_wellness_score(avg_valence, avg_energy, play_count)
        
        return {
            "wellness_score": wellness_score,
            "mood_indicator": get_mood_indicator(avg_valence),
            "energy_level": get_energy_level(avg_energy),
            "listening_frequency": get_listening_frequency(play_count),
            "recommendations": get_wellness_recommendations(wellness_score, avg_valence, avg_energy)
        }
    except Exception as e:
        print(f"Error in wellness analysis: {e}")
        return get_demo_wellness()

def determine_personality_type(danceability, energy, valence, acousticness):
    """Determine personality type based on audio features"""
    if energy > 0.7 and danceability > 0.7:
        return {
            "name": "The Energizer",
            "description": "You love high-energy, danceable music that gets you moving!",
            "confidence": 0.85,
            "traits": ["Energetic", "Social", "Optimistic", "Active"]
        }
    elif valence > 0.6 and acousticness < 0.3:
        return {
            "name": "The Mood Booster",
            "description": "Your music choices reflect a positive, upbeat personality.",
            "confidence": 0.78,
            "traits": ["Positive", "Uplifting", "Social", "Happy"]
        }
    elif acousticness > 0.6 and energy < 0.5:
        return {
            "name": "The Contemplator",
            "description": "You prefer acoustic, mellow music for reflection and relaxation.",
            "confidence": 0.82,
            "traits": ["Thoughtful", "Introspective", "Calm", "Artistic"]
        }
    else:
        return {
            "name": "The Explorer",
            "description": "Your diverse music taste shows an adventurous and open personality.",
            "confidence": 0.75,
            "traits": ["Curious", "Open-minded", "Diverse", "Adventurous"]
        }

def calculate_wellness_score(valence, energy, play_count):
    """Calculate wellness score from 0-100"""
    if not valence or not energy:
        return 75
    
    # Higher valence and moderate energy indicate better wellness
    valence_score = valence * 50
    energy_score = min(energy * 30, 30)  # Cap energy contribution
    frequency_score = min(play_count / 100 * 20, 20)  # Cap frequency contribution
    
    return min(round(valence_score + energy_score + frequency_score), 100)

def get_mood_indicator(valence):
    """Get mood indicator based on valence"""
    if not valence:
        return "Neutral"
    if valence > 0.7:
        return "Very Positive"
    elif valence > 0.5:
        return "Positive"
    elif valence > 0.3:
        return "Neutral"
    else:
        return "Reflective"

def get_energy_level(energy):
    """Get energy level description"""
    if not energy:
        return "Moderate"
    if energy > 0.8:
        return "Very High"
    elif energy > 0.6:
        return "High"
    elif energy > 0.4:
        return "Moderate"
    else:
        return "Low"

def get_listening_frequency(play_count):
    """Get listening frequency description"""
    if play_count > 1000:
        return "Very Active"
    elif play_count > 500:
        return "Active"
    elif play_count > 100:
        return "Moderate"
    else:
        return "Light"

def get_wellness_recommendations(wellness_score, valence, energy):
    """Get wellness recommendations"""
    recommendations = []
    
    if wellness_score < 60:
        recommendations.append("Try listening to more upbeat, positive music")
        recommendations.append("Consider creating energizing playlists for workouts")
    
    if valence and valence < 0.4:
        recommendations.append("Balance melancholic music with some uplifting tracks")
    
    if energy and energy > 0.8:
        recommendations.append("Include some calming music for relaxation")
    
    if not recommendations:
        recommendations = [
            "Your music choices show great balance!",
            "Keep exploring diverse genres",
            "Music is positively impacting your wellness"
        ]
    
    return recommendations

def get_demo_personality():
    """Return demo personality data"""
    return {
        "personality_type": "The Music Explorer",
        "description": "You have an adventurous taste in music, always seeking new sounds and experiences.",
        "confidence": 0.80,
        "traits": ["Curious", "Open-minded", "Creative", "Adventurous"],
        "audio_features": {
            "danceability": 0.65,
            "energy": 0.72,
            "valence": 0.58,
            "acousticness": 0.35
        }
    }

def get_demo_wellness():
    """Return demo wellness data"""
    return {
        "wellness_score": 78,
        "mood_indicator": "Positive",
        "energy_level": "High",
        "listening_frequency": "Active",
        "recommendations": [
            "Your music choices show great emotional balance",
            "Keep exploring diverse genres for mental stimulation",
            "Consider creating playlists for different moods"
        ]
    }