"""
AI insights endpoints for personality analysis, wellness, and recommendations
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from modules.ai_personality_enhancer import EnhancedPersonalityAnalyzer
from modules.enhanced_stress_detector import EnhancedStressDetector
from modules.genre_evolution_tracker import GenreEvolutionTracker
from modules.wellness_analyzer import WellnessAnalyzer
from modules.analyzer import ListeningPersonalityAnalyzer

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/personality')
@jwt_required()
def get_personality():
    """Get AI-enhanced personality analysis"""
    try:
        user_id = get_jwt_identity()
        db_path = f'data/user_{user_id}_spotify_data.db'
        
        # Initialize personality analyzer
        analyzer = EnhancedPersonalityAnalyzer(db_path=db_path)
        
        # Generate personality analysis
        personality_result = analyzer.generate_enhanced_personality(user_id)
        
        if not personality_result:
            return jsonify({'error': 'Unable to generate personality analysis'}), 500
        
        return jsonify({
            'personality': personality_result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/wellness')
@jwt_required()
def get_wellness():
    """Get wellness and stress analysis"""
    try:
        user_id = get_jwt_identity()
        db_path = f'data/user_{user_id}_spotify_data.db'
        
        # Initialize stress detector
        stress_detector = EnhancedStressDetector(db_path=db_path)
        
        # Analyze stress patterns
        stress_analysis = stress_detector.analyze_stress_patterns(user_id)
        
        if not stress_analysis:
            return jsonify({'error': 'Unable to generate wellness analysis'}), 500
        
        return jsonify({
            'wellness': stress_analysis
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/genre-evolution')
@jwt_required()
def get_genre_evolution():
    """Get genre evolution timeline"""
    try:
        user_id = get_jwt_identity()
        db_path = f'data/user_{user_id}_spotify_data.db'
        
        # Initialize genre evolution tracker
        tracker = GenreEvolutionTracker(db_path)
        
        # Get evolution data
        evolution_data = tracker.get_genre_evolution_timeline()
        
        return jsonify({
            'genre_evolution': evolution_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/recommendations')
@jwt_required()
def get_recommendations():
    """Get AI-powered content recommendations"""
    try:
        user_id = get_jwt_identity()
        db_path = f'data/user_{user_id}_spotify_data.db'
        
        # Initialize basic personality analyzer for recommendations
        analyzer = ListeningPersonalityAnalyzer(db_path)
        
        # Get listening personality
        personality = analyzer.analyze_personality(user_id)
        
        if not personality:
            return jsonify({'recommendations': []})
        
        # Generate basic recommendations based on personality
        recommendations = {
            'mood_based': [],
            'genre_exploration': [],
            'artist_discovery': [],
            'playlist_suggestions': []
        }
        
        # This would be enhanced with actual recommendation logic
        # For now, return structure for frontend development
        
        return jsonify({
            'recommendations': recommendations,
            'personality_insights': personality
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/insights/summary')
@jwt_required()
def get_ai_summary():
    """Get comprehensive AI insights summary"""
    try:
        user_id = get_jwt_identity()
        db_path = f'data/user_{user_id}_spotify_data.db'
        
        # Initialize analyzers
        personality_analyzer = EnhancedPersonalityAnalyzer(db_path=db_path)
        stress_detector = EnhancedStressDetector(db_path=db_path)
        
        # Get all AI insights
        personality = personality_analyzer.generate_enhanced_personality(user_id)
        wellness = stress_detector.analyze_stress_patterns(user_id)
        
        summary = {
            'personality_type': personality.get('personality_type') if personality else 'Unknown',
            'stress_level': wellness.get('overall_stress_level') if wellness else 'Unknown',
            'dominant_mood': personality.get('dominant_mood') if personality else 'Unknown',
            'listening_diversity': personality.get('diversity_score') if personality else 0,
            'ai_description': personality.get('ai_description') if personality else 'No description available'
        }
        
        return jsonify({
            'ai_summary': summary
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
