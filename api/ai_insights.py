"""
AI insights endpoints for personality analysis, wellness, and recommendations
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from modules.ai_insights import get_personality_analysis, get_wellness_analysis

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
        analysis = get_wellness_analysis(user_id)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
