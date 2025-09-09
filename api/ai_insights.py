"""
AI insights endpoints for personality analysis, wellness, and recommendations
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/personality', methods=['GET'])
@jwt_required()
def get_personality():
    """Get personality analysis"""
    try:
        user_id = get_jwt_identity()
        db_path = f'data/user_{user_id}_spotify_data.db'
        
        from modules.ai_personality_enhancer import EnhancedPersonalityAnalyzer
        analyzer = EnhancedPersonalityAnalyzer(db_path)
        analysis = analyzer.generate_enhanced_personality(user_id)
        
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/wellness', methods=['GET'])
@jwt_required()
def get_wellness():
    """Get wellness analysis"""
    try:
        user_id = get_jwt_identity()
        db_path = f'data/user_{user_id}_spotify_data.db'
        
        from modules.wellness_analyzer import WellnessAnalyzer
        analyzer = WellnessAnalyzer(db_path)
        analysis = analyzer.analyze_wellness_patterns(user_id)
        
        # Transform to match React component expectations
        wellness_data = {
            'wellness_score': analysis.get('wellness_score', 75),
            'mood_indicator': _get_mood_indicator(analysis),
            'energy_level': _get_energy_level(analysis),
            'listening_frequency': _get_listening_frequency(analysis),
            'recommendations': [suggestion.get('description', suggestion.get('title', '')) 
                             for suggestion in analysis.get('therapeutic_suggestions', [])]
        }
        
        return jsonify(wellness_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _get_mood_indicator(analysis):
    """Extract mood indicator from wellness analysis"""
    wellness_score = analysis.get('wellness_score', 75)
    if wellness_score >= 80:
        return 'Very Positive'
    elif wellness_score >= 60:
        return 'Positive'
    elif wellness_score >= 40:
        return 'Neutral'
    else:
        return 'Reflective'

def _get_energy_level(analysis):
    """Extract energy level from wellness analysis"""
    stress_indicators = analysis.get('stress_indicators', {})
    agitated = stress_indicators.get('agitated_listening', {}).get('detected', False)
    late_night = stress_indicators.get('late_night_patterns', {}).get('detected', False)
    
    if agitated:
        return 'High Energy'
    elif late_night:
        return 'Low Energy'
    else:
        return 'Balanced Energy'

def _get_listening_frequency(analysis):
    """Extract listening frequency from wellness analysis"""
    data_quality = analysis.get('data_quality', {})
    total_tracks = data_quality.get('total_tracks', 0)
    
    if total_tracks > 100:
        return 'Very Active'
    elif total_tracks > 50:
        return 'Active'
    elif total_tracks > 20:
        return 'Moderate'
    else:
        return 'Light'

@ai_bp.route('/genre-evolution')
@jwt_required()
def get_genre_evolution():
    """Get genre evolution timeline"""
    try:
        user_id = get_jwt_identity()
        db_path = f'data/user_{user_id}_spotify_data.db'
        
        from modules.genre_evolution_tracker import GenreEvolutionTracker
        tracker = GenreEvolutionTracker(db_path)
        evolution_data = tracker.get_genre_evolution_data(user_id)
        
        return jsonify(evolution_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/stress')
@jwt_required()
def get_stress_analysis():
    """Get enhanced stress analysis"""
    try:
        user_id = get_jwt_identity()
        db_path = f'data/user_{user_id}_spotify_data.db'
        
        from modules.enhanced_stress_detector import EnhancedStressDetector
        detector = EnhancedStressDetector(db_path)
        stress_data = detector.analyze_stress_patterns(user_id)
        
        return jsonify(stress_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/recommendations')
@jwt_required()
def get_recommendations():
    """Get content-based recommendations"""
    try:
        user_id = get_jwt_identity()
        db_path = f'data/user_{user_id}_spotify_data.db'
        
        from modules.ai_personality_enhancer import EnhancedPersonalityAnalyzer
        analyzer = EnhancedPersonalityAnalyzer(db_path)
        recommendations = analyzer._get_content_based_recommendations(user_id, limit=10)
        
        return jsonify({'recommendations': recommendations})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
