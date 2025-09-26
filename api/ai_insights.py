"""
AI insights endpoints for personality analysis, wellness, and recommendations
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/personality', methods=['GET'])
@jwt_required()
def get_personality():
    """Get enhanced personality analysis using Gemini AI"""
    try:
        user_id = get_jwt_identity()
        
        # Check if this is a demo user
        if user_id == 'demo-user' or user_id.startswith('demo'):
            from modules.ai_sample_data import ai_sample_generator
            return jsonify(ai_sample_generator.generate_personality_analysis())
        
        db_path = f'/tmp/user_{user_id}_spotify_data.db'
        
        try:
            # Use the Gemini-powered EnhancedPersonalityAnalyzer
            from modules.ai_personality_enhancer import EnhancedPersonalityAnalyzer
            analyzer = EnhancedPersonalityAnalyzer(db_path)
            analysis = analyzer.generate_enhanced_personality(user_id)
            
            print(f"Personality analysis result: confidence={analysis.get('confidence_score', 0)}")
            
            # NEVER return sample data for authenticated users - return error for low confidence
            if analysis.get('confidence_score', 0) < 0.3:
                return jsonify({
                    'error': 'Insufficient data for personality analysis',
                    'message': 'We need more listening data to provide accurate personality analysis. Please listen to more music on Spotify.',
                    'confidence_score': analysis.get('confidence_score', 0),
                    'personality_type': 'Insufficient Data',
                    'ai_description': 'Keep listening to more music to unlock deeper personality insights!'
                }), 400
            
            return jsonify(analysis)
            
        except Exception as e:
            print(f"Enhanced personality analysis failed: {e}")
            import traceback
            traceback.print_exc()
            
            # NEVER return sample data for authenticated users - return error instead
            return jsonify({
                'error': 'Failed to generate personality analysis',
                'message': f'Unable to analyze your music data: {str(e)}',
                'personality_type': 'Analysis Failed',
                'ai_description': 'Unable to generate AI analysis at the moment. Please try again later.'
            }), 500
            
    except Exception as e:
        print(f"Personality endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/wellness', methods=['GET'])
@jwt_required()
def get_wellness():
    """Get wellness analysis"""
    try:
        user_id = get_jwt_identity()
        
        # Check if this is a demo user
        if user_id == 'demo-user' or user_id.startswith('demo'):
            from modules.ai_sample_data import ai_sample_generator
            return jsonify(ai_sample_generator.generate_wellness_analysis())
        
        db_path = f'/tmp/user_{user_id}_spotify_data.db'
        
        try:
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
            print(f"Wellness analysis failed: {e}")
            # NEVER return sample data for authenticated users - return error instead
            return jsonify({
                'error': 'Failed to generate wellness analysis',
                'message': f'Unable to analyze your wellness data: {str(e)}'
            }), 500
            
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

@ai_bp.route('/stress-timeline', methods=['GET'])
@jwt_required()
def get_stress_timeline():
    """Get detailed stress timeline data"""
    try:
        user_id = get_jwt_identity()
        db_path = f'/tmp/user_{user_id}_spotify_data.db'
        
        from modules.enhanced_stress_detector import EnhancedStressDetector
        detector = EnhancedStressDetector(db_path)
        stress_data = detector.analyze_stress_patterns(user_id, days=30)
        
        return jsonify({
            'timeline': stress_data.get('stress_timeline', []),
            'indicators': stress_data.get('stress_indicators', {}),
            'confidence': stress_data.get('confidence', 60)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/wellness-recommendations', methods=['GET'])
@jwt_required()
def get_wellness_recommendations():
    """Get therapeutic music recommendations"""
    try:
        user_id = get_jwt_identity()
        db_path = f'/tmp/user_{user_id}_spotify_data.db'
        
        from modules.wellness_analyzer import WellnessAnalyzer
        analyzer = WellnessAnalyzer(db_path)
        analysis = analyzer.analyze_wellness_patterns(user_id)
        
        return jsonify({
            'therapeutic_suggestions': analysis.get('therapeutic_suggestions', []),
            'focus_recommendations': analysis.get('focus_recommendations', []),
            'relaxation_tracks': analysis.get('relaxation_tracks', [])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/genre-evolution', methods=['GET'])
@jwt_required()
def get_genre_evolution():
    """Get comprehensive genre evolution analysis"""
    try:
        user_id = get_jwt_identity()
        
        # Check if this is a demo user
        if user_id == 'demo-user' or user_id.startswith('demo'):
            from modules.ai_sample_data import ai_sample_generator
            return jsonify(ai_sample_generator.generate_genre_evolution())
        
        db_path = f'/tmp/user_{user_id}_spotify_data.db'
        
        try:
            from modules.genre_evolution_tracker import GenreEvolutionTracker
            tracker = GenreEvolutionTracker(db_path)
            evolution_data = tracker.get_genre_evolution_data(user_id)
            
            # Check if we have sufficient data - return error instead of sample data
            if not evolution_data.get('timeline_data') or len(evolution_data.get('timeline_data', [])) < 2:
                return jsonify({
                    'error': 'Insufficient data for genre evolution',
                    'message': 'We need more listening history to track your genre evolution. Please listen to more music on Spotify.',
                    'timeline_data': [],
                    'insights': ['Keep listening to see your genre evolution!'],
                    'current_top_genres': [],
                    'biggest_changes': []
                }), 400
            
            # Ensure all required fields are present
            if not evolution_data.get('insights'):
                evolution_data['insights'] = ['Keep listening to see your genre evolution!']
            if not evolution_data.get('current_top_genres'):
                evolution_data['current_top_genres'] = []
            if not evolution_data.get('biggest_changes'):
                evolution_data['biggest_changes'] = []
            
            return jsonify(evolution_data)
        except Exception as e:
            print(f"Genre evolution analysis failed: {e}")
            # NEVER return sample data for authenticated users - return error instead
            return jsonify({
                'error': 'Failed to generate genre evolution analysis',
                'message': f'Unable to analyze your genre evolution: {str(e)}'
            }), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/stress', methods=['GET'])
@jwt_required()
def get_stress_analysis():
    """Get enhanced stress analysis with comprehensive insights"""
    try:
        user_id = get_jwt_identity()
        
        # Check if this is a demo user
        if user_id == 'demo-user' or user_id.startswith('demo'):
            from modules.ai_sample_data import ai_sample_generator
            return jsonify(ai_sample_generator.generate_stress_analysis())
        
        db_path = f'/tmp/user_{user_id}_spotify_data.db'
        
        # Try enhanced stress detector first, fallback to wellness analyzer
        try:
            from modules.enhanced_stress_detector import EnhancedStressDetector
            detector = EnhancedStressDetector(db_path)
            stress_data = detector.analyze_stress_patterns(user_id)
            
            # Ensure all required fields are present for React component
            if not stress_data.get('stress_timeline'):
                stress_data['stress_timeline'] = []
            if not stress_data.get('personal_triggers'):
                stress_data['personal_triggers'] = []
            if not stress_data.get('recommendations'):
                stress_data['recommendations'] = []
            if not stress_data.get('confidence'):
                stress_data['confidence'] = 60
                
            return jsonify(stress_data)
            
        except Exception as enhanced_error:
            print(f"Enhanced stress detector failed: {enhanced_error}")
            
            # Fallback to wellness analyzer and convert format
            try:
                from modules.wellness_analyzer import WellnessAnalyzer
                analyzer = WellnessAnalyzer(db_path)
                wellness_data = analyzer.analyze_wellness_patterns(user_id)
                
                # Convert wellness data to stress format
                wellness_score = wellness_data.get('wellness_score', 75)
                stress_score = max(0, 100 - wellness_score)
                
                stress_data = {
                    'stress_score': stress_score,
                    'stress_level': 'Moderate Stress Indicators' if stress_score > 50 else 'Low Stress Indicators',
                    'stress_indicators': wellness_data.get('stress_indicators', {}),
                    'stress_timeline': [],
                    'personal_triggers': [],
                    'recommendations': wellness_data.get('therapeutic_suggestions', []),
                    'confidence': wellness_data.get('confidence', 60)
                }
                
                return jsonify(stress_data)
            except Exception as wellness_error:
                print(f"Wellness analyzer also failed: {wellness_error}")
                # NEVER return sample data for authenticated users - return error instead
                return jsonify({
                    'error': 'Failed to generate stress analysis',
                    'message': f'Unable to analyze your stress patterns: {str(wellness_error)}'
                }), 500
        
    except Exception as e:
        print(f"All stress analysis methods failed: {e}")
        # NEVER return sample data for authenticated users - return error instead
        return jsonify({
            'error': 'Failed to generate stress analysis',
            'message': f'Unable to analyze your stress patterns: {str(e)}'
        }), 500

@ai_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    """Get advanced AI-powered recommendations"""
    try:
        user_id = get_jwt_identity()
        
        # Check if this is a demo user
        if user_id == 'demo-user' or user_id.startswith('demo'):
            from modules.ai_sample_data import ai_sample_generator
            return jsonify(ai_sample_generator.generate_advanced_recommendations())
        
        db_path = f'/tmp/user_{user_id}_spotify_data.db'
        
        try:
            from modules.ai_personality_enhancer import EnhancedPersonalityAnalyzer
            analyzer = EnhancedPersonalityAnalyzer(db_path)
            recommendations = analyzer._get_content_based_recommendations(user_id, limit=10)
            
            # Get user's music DNA for additional context
            try:
                user_listening_data = analyzer._get_user_listening_data(user_id)
                music_dna = {
                    'danceability': user_listening_data.get('avg_danceability', 0.5),
                    'energy': user_listening_data.get('avg_energy', 0.5),
                    'valence': user_listening_data.get('avg_valence', 0.5),
                    'tempo': user_listening_data.get('avg_tempo', 120)
                }
            except:
                music_dna = None
            
            # NEVER return sample data for authenticated users - return error instead
            if len(recommendations) < 1:
                return jsonify({
                    'error': 'Insufficient data for recommendations',
                    'message': 'We need more listening data to generate personalized recommendations. Please listen to more music on Spotify.',
                    'recommendations': [],
                    'music_dna': music_dna,
                    'total_count': 0
                }), 400
            
            return jsonify({
                'recommendations': recommendations,
                'music_dna': music_dna,
                'total_count': len(recommendations)
            })
            
        except Exception as e:
            print(f"Recommendations analysis failed: {e}")
            # NEVER return sample data for authenticated users - return error instead
            return jsonify({
                'error': 'Failed to generate recommendations',
                'message': f'Unable to analyze your music data: {str(e)}',
                'recommendations': [],
                'total_count': 0
            }), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/music-dna', methods=['GET'])
@jwt_required()
def get_music_dna():
    """Get user's music DNA profile"""
    try:
        user_id = get_jwt_identity()
        db_path = f'/tmp/user_{user_id}_spotify_data.db'
        
        from modules.ai_personality_enhancer import EnhancedPersonalityAnalyzer
        analyzer = EnhancedPersonalityAnalyzer(db_path)
        
        # Get comprehensive listening data
        listening_data = analyzer._get_user_listening_data(user_id)
        
        music_dna = {
            'danceability': listening_data.get('avg_danceability', 0.5),
            'energy': listening_data.get('avg_energy', 0.5),
            'valence': listening_data.get('avg_valence', 0.5),
            'tempo': listening_data.get('avg_tempo', 120),
            'acousticness': listening_data.get('avg_acousticness', 0.5),
            'instrumentalness': listening_data.get('avg_instrumentalness', 0.1),
            'top_genre': listening_data.get('top_genre', 'Mixed'),
            'diversity_score': listening_data.get('genre_diversity', 0.5),
            'total_tracks': listening_data.get('total_tracks', 0)
        }
        
        return jsonify(music_dna)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/insights-summary', methods=['GET'])
@jwt_required()
def get_insights_summary():
    """Get comprehensive AI insights summary"""
    try:
        user_id = get_jwt_identity()
        db_path = f'/tmp/user_{user_id}_spotify_data.db'
        
        # Collect all insights in parallel
        summary = {}
        
        # Personality analysis
        try:
            from modules.ai_personality_enhancer import EnhancedPersonalityAnalyzer
            analyzer = EnhancedPersonalityAnalyzer(db_path)
            personality = analyzer.generate_enhanced_personality(user_id)
            summary['personality'] = {
                'type': personality.get('personality_type', 'Music Explorer'),
                'confidence': personality.get('confidence_score', 0.5)
            }
        except:
            summary['personality'] = {'type': 'Music Explorer', 'confidence': 0.5}
        
        # Stress analysis
        try:
            from modules.enhanced_stress_detector import EnhancedStressDetector
            detector = EnhancedStressDetector(db_path)
            stress_data = detector.analyze_stress_patterns(user_id)
            summary['stress'] = {
                'score': stress_data.get('stress_score', 25),
                'level': stress_data.get('stress_level', 'Low Stress Indicators')
            }
        except:
            summary['stress'] = {'score': 25, 'level': 'Low Stress Indicators'}
        
        # Wellness analysis
        try:
            from modules.wellness_analyzer import WellnessAnalyzer
            wellness_analyzer = WellnessAnalyzer(db_path)
            wellness_data = wellness_analyzer.analyze_wellness_patterns(user_id)
            summary['wellness'] = {
                'score': wellness_data.get('wellness_score', 75),
                'mood': _get_mood_indicator(wellness_data)
            }
        except:
            summary['wellness'] = {'score': 75, 'mood': 'Positive'}
        
        return jsonify(summary)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@ai_bp.route('/stress-enhanced', methods=['GET'])
@jwt_required()
def get_enhanced_stress_analysis():
    """Get comprehensive enhanced stress analysis with all visualization data"""
    try:
        user_id = get_jwt_identity()
        
        # Check if this is a demo user
        if user_id == 'demo-user' or user_id.startswith('demo'):
            from modules.ai_sample_data import ai_sample_generator
            return jsonify(ai_sample_generator.generate_enhanced_stress_analysis())
        
        db_path = f'/tmp/user_{user_id}_spotify_data.db'
        
        from modules.stress_analysis_api import StressAnalysisAPI
        stress_api = StressAnalysisAPI(db_path)
        
        # Get comprehensive stress analysis with all visualization components
        enhanced_stress_data = stress_api.get_comprehensive_stress_analysis(user_id)
        
        return jsonify(enhanced_stress_data)
        
    except Exception as e:
        print(f"Enhanced stress analysis failed: {e}")
        return jsonify({'error': str(e)}), 500
@ai_bp.route('/genre-evolution-chart', methods=['GET'])
@jwt_required()
def get_genre_evolution_chart():
    """Get genre evolution chart data for React Chart.js"""
    try:
        user_id = get_jwt_identity()
        db_path = f'/tmp/user_{user_id}_spotify_data.db'
        
        from modules.genre_evolution_tracker import GenreEvolutionTracker
        tracker = GenreEvolutionTracker(db_path)
        chart_data = tracker.get_genre_evolution_chart_data(user_id)
        
        return jsonify(chart_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
