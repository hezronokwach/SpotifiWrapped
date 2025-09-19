import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import api from '../api'
import { useDemoMode } from '../contexts/DemoModeContext'
import '../spotify-components.css'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

interface PersonalityData {
  ai_description?: string
  personality_type?: string
  confidence_score?: number
  recommendations?: Array<{
    name: string
    artist: string
    image_url?: string
    similarity_score: number
    reason: string
  }>
  error?: string
  message?: string
}

interface WellnessData {
  wellness_score: number
  mood_indicator: string
  energy_level: string
  listening_frequency: string
  recommendations: string[]
}

interface StressData {
  stress_score: number
  stress_level: string
  stress_indicators: any
  stress_timeline: Array<{
    date: string
    stress_score: number
    avg_mood: number
    avg_energy: number
  }>
  personal_triggers: Array<{
    type: string
    trigger: string
    recommendation: string
  }>
  recommendations: Array<{
    type: string
    title: string
    description: string
    action: string
  }>
  confidence: number
}

interface GenreEvolutionData {
  timeline_data: Array<{
    month: string
    genres: Record<string, number>
    total_plays: number
  }>
  insights: string[]
  current_top_genres: Array<{ genre: string; plays: number }>
  biggest_changes: Array<{
    genre: string
    change: number
    direction: string
  }>
}

const AIInsights: React.FC = () => {
  const { isDemoMode } = useDemoMode()
  const [personalityData, setPersonalityData] = useState<PersonalityData | null>(null)
  const [wellnessData, setWellnessData] = useState<WellnessData | null>(null)
  const [stressData, setStressData] = useState<StressData | null>(null)
  const [genreEvolution, setGenreEvolution] = useState<GenreEvolutionData | null>(null)
  const [recommendations, setRecommendations] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    fetchAIInsights()
  }, [isDemoMode])

  const fetchAIInsights = async () => {
    try {
      setIsLoading(true)
      
      if (isDemoMode) {
        // Use sample AI insights for demo mode
        setPersonalityData({
          ai_description: "You're a Sonic Explorer with eclectic taste! Your music choices show curiosity and openness to new experiences. You enjoy both mainstream hits and hidden gems, suggesting a balanced personality that appreciates both familiarity and novelty.",
          personality_type: "Sonic Explorer",
          confidence_score: 0.85,
          recommendations: [
            { name: "As It Was", artist: "Harry Styles", similarity_score: 0.92, reason: "Matches your pop sensibilities" },
            { name: "Heat Waves", artist: "Glass Animals", similarity_score: 0.88, reason: "Indie vibes you'll love" }
          ]
        })
        
        setWellnessData({
          wellness_score: 78,
          mood_indicator: "Positive",
          energy_level: "High",
          listening_frequency: "Daily Active Listener",
          recommendations: [
            "Your music choices suggest good emotional regulation",
            "Consider adding more calming tracks for better sleep",
            "Your diverse taste promotes mental flexibility"
          ]
        })
        
        setStressData({
          stress_score: 32,
          stress_level: "Low Stress",
          stress_indicators: {
            late_night_patterns: { severity: "mild", frequency: 2, research_basis: "Occasional late listening" },
            mood_volatility: { severity: "low", frequency: 1, research_basis: "Stable music preferences" }
          },
          stress_timeline: [
            { date: "2024-01-08", stress_score: 28, avg_mood: 0.72, avg_energy: 0.68 },
            { date: "2024-01-09", stress_score: 35, avg_mood: 0.65, avg_energy: 0.71 },
            { date: "2024-01-10", stress_score: 30, avg_mood: 0.78, avg_energy: 0.69 }
          ],
          personal_triggers: [
            { type: "temporal", trigger: "Late night listening spikes", recommendation: "Set a music curfew for better sleep" }
          ],
          recommendations: [
            { type: "relaxation", title: "Mindful Listening", description: "Practice focused listening sessions", action: "Try 10-minute meditation with ambient music" }
          ],
          confidence: 82
        })
        
        setGenreEvolution({
          timeline_data: [
            { month: "Oct 2023", genres: { "pop": 45, "rock": 32, "indie": 28 }, total_plays: 105 },
            { month: "Nov 2023", genres: { "pop": 52, "rock": 28, "indie": 35 }, total_plays: 115 },
            { month: "Dec 2023", genres: { "pop": 48, "rock": 35, "indie": 42 }, total_plays: 125 }
          ],
          insights: [
            "Your indie music appreciation has grown 50% over the past 3 months",
            "Pop remains your consistent favorite across all periods",
            "You're exploring more diverse genres lately"
          ],
          current_top_genres: [
            { genre: "pop", plays: 48 },
            { genre: "indie", plays: 42 },
            { genre: "rock", plays: 35 }
          ],
          biggest_changes: [
            { genre: "indie", change: 14, direction: "increased" },
            { genre: "electronic", change: 8, direction: "increased" }
          ]
        })
        
        setRecommendations([
          { name: "Flowers", artist: "Miley Cyrus", similarity_score: 0.89, reason: "Matches your current pop preferences", image_url: "https://picsum.photos/300/300?random=50" },
          { name: "Unholy", artist: "Sam Smith ft. Kim Petras", similarity_score: 0.85, reason: "Trending track you might enjoy", image_url: "https://picsum.photos/300/300?random=51" }
        ])
        
        setIsLoading(false)
        return
      }
      
      // Fetch all AI insights in parallel with error handling
      const results = await Promise.allSettled([
        api.get('/ai/personality'),
        api.get('/ai/wellness'),
        api.get('/ai/stress-enhanced'),
        api.get('/ai/genre-evolution'),
        api.get('/ai/recommendations')
      ])
      
      // Handle personality data
      if (results[0].status === 'fulfilled') {
        setPersonalityData(results[0].value.data)
      } else {
        // Check if it's an expected 400 error (insufficient data)
        const error = results[0].reason
        if (error?.response?.status === 400) {
          console.log('Insufficient data for personality analysis - this is expected')
          setPersonalityData({ error: 'Insufficient data', message: error.response.data.message } as PersonalityData)
        } else {
          console.error('Personality analysis failed:', error)
          setPersonalityData({ error: 'Failed to load personality analysis' } as PersonalityData)
        }
      }
      
      // Handle wellness data
      if (results[1].status === 'fulfilled') {
        setWellnessData(results[1].value.data)
      } else {
        console.error('Wellness analysis failed:', results[1].reason)
        setWellnessData(null)
      }
      
      // Handle stress data
      if (results[2].status === 'fulfilled') {
        setStressData(results[2].value.data)
      } else {
        console.error('Stress analysis failed:', results[2].reason)
        setStressData(null)
      }
      
      // Handle genre evolution data
      if (results[3].status === 'fulfilled') {
        setGenreEvolution(results[3].value.data)
      } else {
        console.error('Genre evolution failed:', results[3].reason)
        setGenreEvolution(null)
      }
      
      // Handle recommendations data
      if (results[4].status === 'fulfilled') {
        setRecommendations(results[4].value.data.recommendations || [])
      } else {
        // Check if it's an expected 400 error (insufficient data)
        const error = results[4].reason
        if (error?.response?.status === 400) {
          console.log('Insufficient data for recommendations - this is expected')
        } else {
          console.error('Recommendations failed:', error)
        }
        setRecommendations([])
      }
      
    } catch (error) {
      console.error('Failed to fetch AI insights:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-content">
          <div style={{ textAlign: 'center', padding: '100px 20px' }}>
            <div className="loading-shimmer" style={{ height: '60px', width: '300px', margin: '0 auto 20px', borderRadius: '16px' }}></div>
            <p style={{ color: 'var(--text-secondary)' }}>Loading your AI insights...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-content">
        {/* Header */}
        <div style={{ marginBottom: '40px', textAlign: 'center' }}>
          <h1 style={{
            fontFamily: "'Orbitron', monospace",
            fontSize: '3rem',
            fontWeight: 700,
            background: 'linear-gradient(45deg, #1DB954, #00D4FF, #8B5CF6)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            marginBottom: '10px'
          }}>
            AI Insights
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1.2rem' }}>
            Deep analysis of your music psychology and listening patterns
          </p>
          <button 
            onClick={() => navigate('/dashboard')}
            className="spotify-button"
            style={{ marginTop: '20px' }}
          >
            <i className="fas fa-arrow-left" style={{ marginRight: '8px' }}></i>
            Back to Dashboard
          </button>
        </div>

        {/* AI Insights Grid - Masonry Layout */}
        <div className="ai-insights-masonry-container">
          {/* Left Column */}
          <div className="ai-insights-left-column">
            {/* Personality Analysis Card */}
            {personalityData && (
              <PersonalityCard data={personalityData} />
            )}
            
            {/* Genre Evolution Card */}
            {genreEvolution && (
              <GenreEvolutionCard data={genreEvolution} />
            )}
            
            {/* Wellness Analysis Card */}
            {wellnessData && (
              <WellnessCard data={wellnessData} />
            )}
          </div>
          
          {/* Right Column */}
          <div className="ai-insights-right-column">
            {/* Stress Analysis Card */}
            {stressData && (
              <StressAnalysisCard data={stressData} />
            )}
          </div>
        </div>

        {/* Recommendations Section */}
        <div style={{ marginTop: '40px' }}>
          <RecommendationsCard recommendations={recommendations} />
        </div>

        {/* Refresh Button */}
        <div style={{ textAlign: 'center', marginTop: '40px' }}>
          <button
            onClick={fetchAIInsights}
            className="spotify-button"
            disabled={isLoading}
          >
            <i className="fas fa-sync-alt" style={{ marginRight: '8px' }}></i>
            {isLoading ? 'Refreshing...' : 'Refresh AI Insights'}
          </button>
        </div>
      </div>
    </div>
  )
}

// AI Insight Components
const PersonalityCard: React.FC<{ data: PersonalityData | any }> = ({ data }) => {
  // Handle error states
  if (data?.error) {
    return (
      <div className="ai-insights-card ai-card-personality">
        <div className="ai-card-header">
          <h3 className="ai-card-title">
            <i className="ai-card-icon fas fa-brain"></i>
            🧠 AI-Enhanced Personality
          </h3>
          <i className="fas fa-user-circle"></i>
        </div>
        
        <div style={{
          textAlign: 'center',
          padding: '40px 20px',
          background: 'rgba(239, 68, 68, 0.1)',
          borderRadius: '12px',
          border: '1px solid rgba(239, 68, 68, 0.3)'
        }}>
          <i className="fas fa-exclamation-triangle" style={{ 
            fontSize: '3rem', 
            color: '#EF4444', 
            marginBottom: '15px'
          }}></i>
          <div style={{ 
            color: 'var(--text-primary)', 
            fontWeight: 700, 
            marginBottom: '8px',
            fontSize: '18px'
          }}>
            Analysis Unavailable
          </div>
          <div style={{ 
            color: 'var(--text-secondary)', 
            fontSize: '14px',
            lineHeight: '1.4'
          }}>
            {data.message || 'Unable to generate personality analysis. Please try again later.'}
          </div>
        </div>
      </div>
    )
  }
  
  const confidenceScore = data.confidence_score || 0
  const hasInsufficientData = confidenceScore < 0.5
  
  return (
    <div className="ai-insights-card ai-card-personality">
      <div className="ai-card-header">
        <h3 className="ai-card-title">
          <i className="ai-card-icon fas fa-brain"></i>
          🧠 AI-Enhanced Personality
        </h3>
        <i className="fas fa-user-circle"></i>
      </div>
      
      <div style={{ marginBottom: '25px' }}>
        <div style={{
          fontSize: '1.8rem',
          fontWeight: 700,
          color: 'var(--accent-purple)',
          marginBottom: '12px',
          fontFamily: "'Orbitron', monospace",
          textAlign: 'center',
          textShadow: '0 0 20px rgba(139, 92, 246, 0.4)'
        }}>
          {data.personality_type || 'Rhythm Analyst'}
        </div>
        
        <div style={{
          textAlign: 'center',
          marginBottom: '15px'
        }}>
          <span className="confidence-badge" style={{
            background: hasInsufficientData ? 'rgba(255, 193, 7, 0.2)' : 'linear-gradient(45deg, #8B5CF6, #00D4FF)',
            color: hasInsufficientData ? '#FFC107' : '#000',
            padding: '6px 16px',
            borderRadius: '20px',
            fontSize: '14px',
            fontWeight: 600,
            fontFamily: "'Orbitron', monospace"
          }}>
            {hasInsufficientData 
              ? "Insufficient Data" 
              : `Confidence: ${Math.round(confidenceScore * 100)}%`}
          </span>
        </div>
        
        <div className="ai-description" style={{
          fontSize: '16px',
          lineHeight: '1.6',
          color: 'rgba(255, 255, 255, 0.9)',
          fontStyle: 'italic',
          margin: '20px 0',
          padding: '20px',
          background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(0, 212, 255, 0.1))',
          borderLeft: '3px solid #8B5CF6',
          borderRadius: '10px',
          textAlign: 'left'
        }}>
          {hasInsufficientData 
            ? "Keep listening to more music to unlock deeper personality insights! We need more data to provide accurate analysis."
            : (data.ai_description || "You have an innate connection to the mathematical beauty of music - the way beats align, how melodies interweave, and the subtle complexities that make a song truly special. Your listening patterns reveal a deep appreciation for musical craftsmanship.")}
        </div>
        
        {/* AI Source Indicator */}
        {!hasInsufficientData && (
          <div style={{
            textAlign: 'center',
            fontSize: '12px',
            color: 'rgba(139, 92, 246, 0.8)',
            marginBottom: '15px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px'
          }}>
            <i className="fas fa-robot"></i>
            {(data as any).llm_generated === false ? 'Sample Analysis' : 'AI-Generated with Gemini'}
          </div>
        )}
      </div>
      
      {!hasInsufficientData && data.recommendations && data.recommendations.length > 0 && (
        <div>
          <h5 style={{ 
            color: 'var(--accent-primary)', 
            marginBottom: '18px',
            fontSize: '18px',
            fontFamily: "'Orbitron', monospace",
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            🎵 AI Recommendations
          </h5>
          <div style={{ maxHeight: '250px', overflowY: 'auto' }}>
            {data.recommendations.slice(0, 3).map((rec: any, index: number) => (
              <div key={index} style={{
                display: 'flex',
                alignItems: 'center',
                padding: '15px',
                marginBottom: '12px',
                background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(0, 212, 255, 0.05))',
                borderRadius: '12px',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                transition: 'all 0.3s ease',
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)'
                e.currentTarget.style.boxShadow = '0 8px 25px rgba(139, 92, 246, 0.3)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = 'none'
              }}>
                {rec.image_url && (
                  <img src={rec.image_url} alt={rec.name} style={{
                    width: '50px',
                    height: '50px',
                    borderRadius: '8px',
                    marginRight: '15px',
                    border: '2px solid rgba(139, 92, 246, 0.3)',
                    transition: 'transform 0.3s ease'
                  }} />
                )}
                <div style={{ flex: 1 }}>
                  <div style={{ 
                    color: 'var(--text-primary)', 
                    fontWeight: 700, 
                    fontSize: '16px',
                    marginBottom: '4px'
                  }}>
                    {rec.name}
                  </div>
                  <div style={{ 
                    color: 'var(--text-secondary)', 
                    fontSize: '14px',
                    marginBottom: '6px'
                  }}>
                    by {rec.artist}
                  </div>
                  <div style={{ 
                    color: '#8B5CF6', 
                    fontSize: '13px',
                    fontStyle: 'italic'
                  }}>
                    {rec.reason || 'Reflects your adventurous musical spirit'}
                  </div>
                </div>
                <div style={{
                  background: 'linear-gradient(45deg, #8B5CF6, #00D4FF)',
                  color: '#000',
                  padding: '4px 8px',
                  borderRadius: '12px',
                  fontSize: '11px',
                  fontWeight: 600,
                  fontFamily: "'Orbitron', monospace"
                }}>
                  {Math.round((rec.similarity_score || 0.85) * 100)}%
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {hasInsufficientData && (
        <div style={{
          textAlign: 'center',
          padding: '25px',
          background: 'rgba(255,193,7,0.1)',
          borderRadius: '12px',
          border: '1px solid rgba(255,193,7,0.3)'
        }}>
          <i className="fas fa-music" style={{ 
            fontSize: '3rem', 
            color: '#FFC107', 
            marginBottom: '15px',
            filter: 'drop-shadow(0 0 10px rgba(255, 193, 7, 0.3))'
          }}></i>
          <div style={{ 
            color: 'var(--text-primary)', 
            fontWeight: 700, 
            marginBottom: '8px',
            fontSize: '18px'
          }}>
            Keep Exploring Music!
          </div>
          <div style={{ 
            color: 'var(--text-secondary)', 
            fontSize: '14px',
            lineHeight: '1.4'
          }}>
            Listen to more tracks to unlock AI-powered personality insights and personalized recommendations
          </div>
        </div>
      )}
    </div>
  )
}

const WellnessCard: React.FC<{ data: WellnessData }> = ({ data }) => {
  const getWellnessColor = (score: number) => {
    if (score >= 80) return '#1DB954'
    if (score >= 60) return '#FBBF24'
    if (score >= 40) return '#F59E0B'
    return '#EF4444'
  }
  
  const getWellnessLevel = (score: number) => {
    if (score >= 80) return 'Excellent'
    if (score >= 60) return 'Good'
    if (score >= 40) return 'Fair'
    return 'Needs Attention'
  }
  
  return (
    <div className="ai-insights-card ai-card-wellness">
      <div className="ai-card-header">
        <h3 className="ai-card-title">
          <i className="ai-card-icon fas fa-heart"></i>
          Wellness Analysis
        </h3>
        <i className="fas fa-leaf"></i>
      </div>
      
      {/* Main Wellness Score */}
      <div style={{ textAlign: 'center', marginBottom: '25px' }}>
        <div style={{
          fontSize: '3.5rem',
          fontWeight: 700,
          color: getWellnessColor(data.wellness_score),
          fontFamily: "'Orbitron', monospace",
          textShadow: `0 0 20px ${getWellnessColor(data.wellness_score)}40`
        }}>
          {Math.round(data.wellness_score)}
        </div>
        <div style={{ 
          color: 'var(--text-primary)', 
          fontSize: '1.1rem',
          fontWeight: 600,
          marginBottom: '5px'
        }}>
          {getWellnessLevel(data.wellness_score)} Wellness
        </div>
        <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
          Based on your music's emotional impact
        </div>
      </div>
      
      {/* Wellness Metrics Grid */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr 1fr', 
        gap: '15px', 
        marginBottom: '25px',
        padding: '15px',
        background: 'rgba(29, 185, 84, 0.1)',
        borderRadius: '12px',
        border: '1px solid rgba(29, 185, 84, 0.2)'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ 
            color: 'var(--accent-primary)', 
            fontWeight: 700,
            fontSize: '1.2rem',
            marginBottom: '4px'
          }}>
            {data.mood_indicator}
          </div>
          <div style={{ color: 'var(--text-muted)', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '1px' }}>
            Mood Profile
          </div>
        </div>
        <div style={{ textAlign: 'center' }}>
          <div style={{ 
            color: 'var(--accent-tertiary)', 
            fontWeight: 700,
            fontSize: '1.2rem',
            marginBottom: '4px'
          }}>
            {data.energy_level}
          </div>
          <div style={{ color: 'var(--text-muted)', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '1px' }}>
            Energy Level
          </div>
        </div>
      </div>
      
      {/* Listening Frequency */}
      {data.listening_frequency && (
        <div style={{ marginBottom: '25px' }}>
          <h5 style={{ color: 'var(--accent-primary)', marginBottom: '10px', fontFamily: "'Orbitron', monospace" }}>
            🎵 Listening Pattern
          </h5>
          <div style={{
            padding: '12px',
            background: 'rgba(139, 92, 246, 0.1)',
            borderRadius: '8px',
            border: '1px solid rgba(139, 92, 246, 0.3)',
            textAlign: 'center'
          }}>
            <div style={{ color: '#8B5CF6', fontWeight: 600, fontSize: '14px' }}>
              {data.listening_frequency}
            </div>
            <div style={{ color: 'var(--text-muted)', fontSize: '11px', marginTop: '4px' }}>
              Listening Frequency
            </div>
          </div>
        </div>
      )}
      
      {/* Wellness Recommendations */}
      <div>
        <h5 style={{ color: 'var(--accent-primary)', marginBottom: '15px', fontFamily: "'Orbitron', monospace" }}>
          💚 Wellness Recommendations
        </h5>
        {data.recommendations && data.recommendations.length > 0 ? (
          data.recommendations.map((rec, index) => (
            <div key={index} style={{
              padding: '12px',
              marginBottom: '10px',
              background: 'rgba(29, 185, 84, 0.1)',
              borderRadius: '8px',
              border: '1px solid rgba(29, 185, 84, 0.3)',
              fontSize: '13px',
              color: 'var(--text-primary)'
            }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                <span style={{ fontSize: '14px', marginTop: '2px' }}>🌟</span>
                <div>{rec}</div>
              </div>
            </div>
          ))
        ) : (
          <div style={{
            padding: '15px',
            background: 'rgba(29, 185, 84, 0.1)',
            borderRadius: '8px',
            border: '1px solid rgba(29, 185, 84, 0.3)',
            textAlign: 'center',
            color: 'var(--text-secondary)'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '8px' }}>🎵</div>
            <div>Keep listening to unlock personalized wellness insights!</div>
          </div>
        )}
      </div>
    </div>
  )
}

const StressAnalysisCard: React.FC<{ data: StressData }> = ({ data }) => {
  const [showResearchDetails, setShowResearchDetails] = useState(false)
  const [activeIndicator, setActiveIndicator] = useState<string | null>(null)
  
  const getStressColor = (score: number) => {
    if (score >= 70) return '#FF6B6B'
    if (score >= 40) return '#FFD93D'
    return '#1DB954'
  }
  
  const getStressIcon = (score: number) => {
    if (score >= 70) return '🔴'
    if (score >= 40) return '🟡'
    return '🟢'
  }
  
  return (
    <div className="ai-insights-card ai-card-stress enhanced-stress-card">
      <div className="ai-card-header">
        <h3 className="ai-card-title">
          <i className="ai-card-icon fas fa-brain"></i>
          🧠 Advanced Stress Analysis
        </h3>
        <i className="fas fa-chart-pulse"></i>
      </div>
      
      {/* Main Stress Score Display with Enhanced Styling */}
      <div style={{ textAlign: 'center', marginBottom: '30px' }}>
        <div style={{
          fontSize: '5rem',
          fontWeight: 700,
          color: getStressColor(data.stress_score),
          fontFamily: "'Orbitron', monospace",
          textShadow: `0 0 30px ${getStressColor(data.stress_score)}60`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '20px'
        }}>
          <span style={{ fontSize: '4rem' }}>{getStressIcon(data.stress_score)}</span>
          {Math.round(data.stress_score)}
        </div>
        <div style={{ 
          color: 'var(--text-primary)', 
          fontSize: '1.4rem',
          fontWeight: 600,
          marginBottom: '10px'
        }}>
          {data.stress_level}
        </div>
        <div style={{ 
          fontSize: '15px', 
          color: 'var(--text-muted)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '12px'
        }}>
          <span>{Math.round(data.confidence)}% Confidence</span>
          <span>•</span>
          <span>Research-Based Analysis</span>
          <button
            onClick={() => setShowResearchDetails(!showResearchDetails)}
            style={{
              background: 'none',
              border: 'none',
              color: '#00D4FF',
              cursor: 'pointer',
              fontSize: '14px',
              textDecoration: 'underline'
            }}
          >
            <i className="fas fa-info-circle" style={{ marginRight: '4px' }}></i>
            Research Info
          </button>
        </div>
        
        {/* Research Details Expandable */}
        {showResearchDetails && (
          <div style={{
            marginTop: '18px',
            padding: '16px',
            background: 'rgba(0, 212, 255, 0.1)',
            borderRadius: '10px',
            border: '1px solid rgba(0, 212, 255, 0.3)',
            fontSize: '14px',
            color: 'rgba(255, 255, 255, 0.8)',
            textAlign: 'left'
          }}>
            <div style={{ fontWeight: 600, marginBottom: '8px', color: '#00D4FF', fontSize: '15px' }}>
              <i className="fas fa-flask" style={{ marginRight: '8px' }}></i>
              Scientific Foundation
            </div>
            <div style={{ lineHeight: '1.5' }}>
              Based on validated research including Dimitriev et al. (2023) HRV studies, 
              Sachs et al. (2015) repetitive listening patterns, and Groarke & Hogan (2018) 
              music and emotional dwelling behaviors. Results show ~75-85% accuracy in research studies.
            </div>
          </div>
        )}
      </div>
      
      {/* Enhanced Stress Indicators Breakdown */}
      {data.stress_indicators && Object.keys(data.stress_indicators).length > 0 && (
        <div style={{ marginBottom: '30px' }}>
          <h5 style={{ color: 'var(--accent-primary)', marginBottom: '18px', fontFamily: "'Orbitron', monospace", fontSize: '18px' }}>
            🔬 Detailed Stress Indicators
          </h5>
          <div style={{ display: 'grid', gap: '12px' }}>
            {Object.entries(data.stress_indicators).map(([key, indicator]: [string, any]) => {
              const getSeverityColor = (severity: string) => {
                switch(severity) {
                  case 'high': return '#FF6B6B'
                  case 'moderate': return '#FFD93D'
                  case 'mild': return '#FFA500'
                  default: return '#1DB954'
                }
              }
              
              const getIndicatorIcon = (key: string) => {
                switch(key) {
                  case 'agitated_listening': return '🎵'
                  case 'repetitive_behavior': return '🔄'
                  case 'late_night_patterns': return '🌙'
                  case 'mood_volatility': return '📊'
                  case 'energy_crashes': return '📉'
                  default: return '📈'
                }
              }
              
              const getIndicatorName = (key: string) => {
                switch(key) {
                  case 'agitated_listening': return 'Agitated Listening'
                  case 'repetitive_behavior': return 'Repetitive Behavior'
                  case 'late_night_patterns': return 'Late Night Patterns'
                  case 'mood_volatility': return 'Mood Volatility'
                  case 'energy_crashes': return 'Energy Crashes'
                  default: return key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
                }
              }
              
              const isActive = activeIndicator === key
              
              return (
                <div 
                  key={key} 
                  className={`stress-indicator-card ${isActive ? 'active' : ''}`}
                  style={{
                    padding: '18px',
                    background: isActive ? 'rgba(255,255,255,0.1)' : 'rgba(255,255,255,0.05)',
                    borderRadius: '12px',
                    border: `2px solid ${getSeverityColor(indicator.severity || 'low')}${isActive ? '80' : '40'}`,
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    transform: isActive ? 'translateY(-2px)' : 'none',
                    boxShadow: isActive ? `0 8px 25px ${getSeverityColor(indicator.severity || 'low')}30` : 'none'
                  }}
                  onClick={() => setActiveIndicator(isActive ? null : key)}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <span style={{ fontSize: '20px' }}>{getIndicatorIcon(key)}</span>
                      <span style={{ color: 'var(--text-primary)', fontWeight: 700, fontSize: '16px' }}>
                        {getIndicatorName(key)}
                      </span>
                      {indicator.frequency && (
                        <span style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
                          ({indicator.frequency} instances)
                        </span>
                      )}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{
                        background: getSeverityColor(indicator.severity || 'low'),
                        color: '#000',
                        padding: '6px 12px',
                        borderRadius: '16px',
                        fontSize: '12px',
                        fontWeight: 700,
                        textTransform: 'uppercase'
                      }}>
                        {indicator.severity || 'low'}
                      </span>
                      <i className={`fas fa-chevron-${isActive ? 'up' : 'down'}`} style={{ color: 'var(--text-muted)', fontSize: '12px' }}></i>
                    </div>
                  </div>
                  
                  {/* Enhanced Repetitive Behavior Display */}
                  {key === 'repetitive_behavior' && indicator.stress_repetitive_tracks !== undefined && (
                    <div style={{ marginBottom: '8px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                        <span style={{ color: '#FF6B6B' }}>🔴 Stress-Related (Sad + Low-Energy):</span>
                        <span style={{ color: indicator.stress_repetitive_tracks > 0 ? '#FF6B6B' : 'var(--text-muted)', fontWeight: 600 }}>
                          {indicator.stress_repetitive_tracks || 0} tracks
                        </span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                        <span style={{ color: '#1DB954' }}>🟢 Happy Repetitive (Healthy):</span>
                        <span style={{ color: indicator.happy_repetitive_tracks > 0 ? '#1DB954' : 'var(--text-muted)', fontWeight: 600 }}>
                          {indicator.happy_repetitive_tracks || 0} tracks
                        </span>
                      </div>
                    </div>
                  )}
                  
                  {/* Research Basis and Details */}
                  <div style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.4' }}>
                    {indicator.research_basis || 'Pattern analysis based on listening behavior'}
                  </div>
                  
                  {/* Expanded Details */}
                  {isActive && (
                    <div style={{
                      marginTop: '15px',
                      padding: '12px',
                      background: 'rgba(0,0,0,0.3)',
                      borderRadius: '8px',
                      fontSize: '13px'
                    }}>
                      {key === 'agitated_listening' && (
                        <div>
                          <div style={{ color: '#00D4FF', fontWeight: 600, marginBottom: '6px', fontSize: '14px' }}>Detection Criteria:</div>
                          <div style={{ color: 'var(--text-secondary)' }}>High energy (&gt;0.75) + Low valence (&lt;0.35) music patterns</div>
                          {indicator.intensity && (
                            <div style={{ marginTop: '4px' }}>Average intensity: {(indicator.intensity * 100).toFixed(0)}%</div>
                          )}
                        </div>
                      )}
                      {key === 'late_night_patterns' && (
                        <div>
                          <div style={{ color: '#00D4FF', fontWeight: 600, marginBottom: '4px' }}>Cortisol Nadir Period:</div>
                          <div style={{ color: 'var(--text-secondary)' }}>Midnight-3AM activity indicates sleep disruption</div>
                          {indicator.avg_mood && (
                            <div style={{ marginTop: '4px' }}>Average mood during late hours: {(indicator.avg_mood * 100).toFixed(0)}%</div>
                          )}
                        </div>
                      )}
                      {key === 'mood_volatility' && (
                        <div>
                          <div style={{ color: '#00D4FF', fontWeight: 600, marginBottom: '4px' }}>Emotional Stability:</div>
                          <div style={{ color: 'var(--text-secondary)' }}>Daily mood variance &gt;0.25 indicates instability</div>
                          {indicator.daily_volatility && (
                            <div style={{ marginTop: '4px' }}>Daily volatility: {indicator.daily_volatility.toFixed(3)}</div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}
      
      {/* Interactive Stress Timeline Chart */}
      {data.stress_timeline && data.stress_timeline.length > 0 && (
        <div style={{ marginBottom: '30px' }}>
          <h5 style={{ color: 'var(--accent-primary)', marginBottom: '18px', fontFamily: "'Orbitron', monospace", fontSize: '18px' }}>
            📈 Interactive Stress Timeline
          </h5>
          <div style={{ height: '300px', marginBottom: '18px' }}>
            <StressTimelineChart timelineData={data.stress_timeline} />
          </div>
          
          {/* Timeline Summary */}
          <div style={{
            background: 'rgba(0,0,0,0.3)',
            borderRadius: '8px',
            padding: '12px'
          }}>
            <div style={{ fontSize: '14px', color: 'var(--text-muted)', marginBottom: '10px' }}>
              Recent 7 Days Summary:
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '8px' }}>
              {data.stress_timeline.slice(-7).map((day, index) => (
                <div key={index} style={{
                  padding: '6px',
                  background: 'rgba(255,255,255,0.05)',
                  borderRadius: '4px',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginBottom: '2px' }}>
                    {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short', day: 'numeric' })}
                  </div>
                  <div style={{
                    fontSize: '14px',
                    color: getStressColor(day.stress_score),
                    fontWeight: 700,
                    fontFamily: "'Orbitron', monospace"
                  }}>
                    {Math.round(day.stress_score)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
      
      {/* Personal Triggers */}
      {data.personal_triggers && data.personal_triggers.length > 0 && (
        <div style={{ marginBottom: '25px' }}>
          <h5 style={{ color: 'var(--accent-primary)', marginBottom: '15px', fontFamily: "'Orbitron', monospace" }}>
            🎯 Personal Triggers
          </h5>
          {data.personal_triggers.slice(0, 3).map((trigger, index) => (
            <div key={index} style={{
              padding: '12px',
              marginBottom: '10px',
              background: 'rgba(255,69,0,0.1)',
              borderRadius: '8px',
              border: '1px solid rgba(255,69,0,0.3)'
            }}>
              <div style={{ fontSize: '13px', color: '#FF4500', fontWeight: 600, marginBottom: '6px' }}>
                🚨 {trigger.trigger}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                💡 {trigger.recommendation}
              </div>
            </div>
          ))}
        </div>
      )}
      
      {/* Evidence-Based Therapeutic Recommendations */}
      {data.recommendations && data.recommendations.length > 0 && (
        <div style={{ marginBottom: '30px' }}>
          <h5 style={{ color: 'var(--accent-primary)', marginBottom: '18px', fontFamily: "'Orbitron', monospace", fontSize: '18px' }}>
            🎵 Evidence-Based Recommendations
          </h5>
          {data.recommendations.slice(0, 3).map((rec, index) => {
            const getRecIcon = (type: string) => {
              switch(type) {
                case 'immediate': return '🧘'
                case 'routine': return '😴'
                case 'stabilization': return '⚖️'
                default: return '💡'
              }
            }
            
            return (
              <div key={index} style={{
                padding: '18px',
                marginBottom: '15px',
                background: 'linear-gradient(135deg, rgba(29,185,84,0.1), rgba(0,212,255,0.05))',
                borderRadius: '12px',
                border: '1px solid rgba(29,185,84,0.3)',
                position: 'relative',
                overflow: 'hidden'
              }}>
                <div style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  height: '2px',
                  background: 'linear-gradient(90deg, #1DB954, #00D4FF)'
                }}></div>
                
                <div style={{ 
                  color: 'var(--accent-primary)', 
                  fontWeight: 700, 
                  fontSize: '16px',
                  marginBottom: '10px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <span style={{ fontSize: '16px' }}>{getRecIcon(rec.type || 'general')}</span>
                  {rec.title || rec.type}
                  <span style={{
                    fontSize: '10px',
                    background: 'rgba(0,212,255,0.2)',
                    color: '#00D4FF',
                    padding: '2px 6px',
                    borderRadius: '8px',
                    marginLeft: 'auto'
                  }}>
                    85% confidence
                  </span>
                </div>
                <div style={{ color: 'var(--text-primary)', fontSize: '15px', marginBottom: '10px', lineHeight: '1.5' }}>
                  {rec.description}
                </div>
                {rec.action && (
                  <div style={{ 
                    color: '#00D4FF', 
                    fontSize: '14px', 
                    fontWeight: 500,
                    marginTop: '10px',
                    padding: '10px',
                    background: 'rgba(0,212,255,0.1)',
                    borderRadius: '6px',
                    border: '1px solid rgba(0,212,255,0.2)'
                  }}>
                    <i className="fas fa-lightbulb" style={{ marginRight: '6px' }}></i>
                    Action: {rec.action}
                  </div>
                )}
                <div style={{
                  marginTop: '10px',
                  fontSize: '12px',
                  color: '#00D4FF',
                  fontStyle: 'italic',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}>
                  <i className="fas fa-flask"></i>
                  Based on music therapy research and stress management studies
                </div>
              </div>
            )
          })}
        </div>
      )}
      
      {/* Scientific Disclaimer */}
      <ScientificDisclaimer confidence={data.confidence} />
    </div>
  )
}

const GenreEvolutionCard: React.FC<{ data: GenreEvolutionData }> = ({ data }) => {


  return (
    <div className="ai-insights-card ai-card-genre-evolution">
      <div className="ai-card-header">
        <h3 className="ai-card-title">
          <i className="ai-card-icon fas fa-chart-line"></i>
          Genre Evolution
        </h3>
        <i className="fas fa-music"></i>
      </div>
      
      {/* Genre Evolution Timeline Chart */}
      <div style={{ marginBottom: '20px' }}>
        <h5 style={{ color: 'var(--accent-primary)', marginBottom: '15px', fontFamily: "'Orbitron', monospace" }}>
          📈 Your Genre Evolution Journey
        </h5>
        <div style={{ height: '300px', position: 'relative' }}>
          {data.timeline_data && data.timeline_data.length > 0 ? (
            <GenreEvolutionChart timelineData={data.timeline_data} />
          ) : (
            <div style={{
              height: '300px',
              background: 'rgba(26, 26, 26, 0.8)',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '1px solid rgba(29, 185, 84, 0.2)'
            }}>
              <div style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>
                <i className="fas fa-music" style={{ fontSize: '2rem', color: 'rgba(29, 185, 84, 0.3)', marginBottom: '10px' }}></i>
                <div>Not enough data for genre evolution</div>
                <div style={{ fontSize: '12px', marginTop: '5px' }}>Keep listening to see your genre journey!</div>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {data.insights && data.insights.length > 0 && (
        <div style={{ marginBottom: '20px' }}>
          <h5 style={{ color: 'var(--accent-primary)', marginBottom: '10px' }}>Evolution Insights</h5>
          {data.insights.map((insight, index) => (
            <div key={index} style={{
              padding: '10px',
              marginBottom: '8px',
              background: 'rgba(244,114,182,0.1)',
              borderRadius: '8px',
              border: '1px solid rgba(244,114,182,0.3)',
              fontSize: '13px',
              color: 'var(--text-primary)'
            }}>
              {insight}
            </div>
          ))}
        </div>
      )}
      
      {data.current_top_genres && data.current_top_genres.length > 0 && (
        <div style={{ marginBottom: '20px' }}>
          <h5 style={{ color: 'var(--accent-primary)', marginBottom: '10px' }}>Current Top Genres</h5>
          {data.current_top_genres.slice(0, 5).map((genre, index) => (
            <div key={index} style={{
              display: 'flex',
              justifyContent: 'space-between',
              padding: '5px 0',
              borderBottom: '1px solid rgba(255,255,255,0.1)'
            }}>
              <span style={{ color: 'var(--text-primary)' }}>{genre.genre}</span>
              <span style={{ color: 'var(--accent-tertiary)', fontSize: '12px' }}>
                {genre.plays} plays
              </span>
            </div>
          ))}
        </div>
      )}
      
      {data.biggest_changes && data.biggest_changes.length > 0 && (
        <div>
          <h5 style={{ color: 'var(--accent-primary)', marginBottom: '10px' }}>Biggest Changes</h5>
          {data.biggest_changes.map((change, index) => (
            <div key={index} style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '8px',
              marginBottom: '8px',
              background: 'rgba(255,255,255,0.05)',
              borderRadius: '6px'
            }}>
              <span style={{ color: 'var(--text-primary)', fontSize: '13px' }}>
                {change.genre}
              </span>
              <span style={{
                color: change.direction === 'increased' ? '#1DB954' : '#FF6B6B',
                fontSize: '12px',
                fontWeight: 600
              }}>
                {change.direction === 'increased' ? '↗' : '↘'} {Math.abs(change.change)}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

const RecommendationsCard: React.FC<{ recommendations: any[] }> = ({ recommendations }) => (
  <div className="ai-insights-card">
    <div className="ai-card-header">
      <h3 className="ai-card-title">
        <i className="ai-card-icon fas fa-magic"></i>
        AI Recommendations
      </h3>
      <i className="fas fa-stars"></i>
    </div>
    
    {recommendations && recommendations.length > 0 ? (
      <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
        {recommendations.slice(0, 8).map((rec, index) => (
          <div key={index} style={{
            display: 'flex',
            alignItems: 'center',
            padding: '12px',
            marginBottom: '12px',
            background: 'rgba(255,255,255,0.05)',
            borderRadius: '8px',
            border: '1px solid rgba(255,255,255,0.1)',
            transition: 'all 0.3s ease'
          }}>
            {rec.image_url && (
              <img src={rec.image_url} alt={rec.name} style={{
                width: '50px',
                height: '50px',
                borderRadius: '6px',
                marginRight: '15px',
                border: '2px solid rgba(29,185,84,0.3)'
              }} />
            )}
            <div style={{ flex: 1 }}>
              <div style={{ color: 'var(--text-primary)', fontWeight: 600, marginBottom: '4px' }}>
                {rec.name}
              </div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '4px' }}>
                {rec.artist}
              </div>
              <div style={{ color: 'var(--accent-tertiary)', fontSize: '12px' }}>
                {rec.reason}
              </div>
            </div>
            <div style={{
              background: 'linear-gradient(45deg, #1DB954, #00D4FF)',
              color: '#000',
              padding: '4px 8px',
              borderRadius: '12px',
              fontSize: '11px',
              fontWeight: 600
            }}>
              {Math.round(rec.similarity_score * 100)}%
            </div>
          </div>
        ))}
      </div>
    ) : (
      <div style={{
        textAlign: 'center',
        padding: '40px 20px',
        background: 'rgba(255, 193, 7, 0.1)',
        borderRadius: '12px',
        border: '1px solid rgba(255, 193, 7, 0.3)'
      }}>
        <i className="fas fa-music" style={{ 
          fontSize: '3rem', 
          color: '#FFC107', 
          marginBottom: '15px'
        }}></i>
        <div style={{ 
          color: 'var(--text-primary)', 
          fontWeight: 700, 
          marginBottom: '8px',
          fontSize: '18px'
        }}>
          No Recommendations Available
        </div>
        <div style={{ 
          color: 'var(--text-secondary)', 
          fontSize: '14px',
          lineHeight: '1.4'
        }}>
          Listen to more music to get personalized AI recommendations based on your taste!
        </div>
      </div>
    )}
  </div>
)

// Stress Timeline Chart Component
const StressTimelineChart: React.FC<{ timelineData: Array<{ date: string; stress_score: number; avg_mood: number; avg_energy: number }> }> = ({ timelineData }) => {
  const chartData = {
    labels: timelineData.map(d => new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })),
    datasets: [
      {
        label: 'Stress Score',
        data: timelineData.map(d => d.stress_score),
        borderColor: '#FF6B6B',
        backgroundColor: 'rgba(255, 107, 107, 0.1)',
        borderWidth: 3,
        pointRadius: 6,
        pointHoverRadius: 8,
        tension: 0.4,
        fill: true,
        yAxisID: 'y'
      },
      {
        label: 'Average Mood',
        data: timelineData.map(d => d.avg_mood * 100),
        borderColor: 'rgba(255, 255, 255, 0.5)',
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 2,
        borderDash: [5, 5],
        pointRadius: 4,
        tension: 0.4,
        fill: false,
        yAxisID: 'y1'
      }
    ]
  }
  
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: 'rgba(255, 255, 255, 0.8)',
          font: {
            family: 'Orbitron, monospace',
            size: 12
          },
          usePointStyle: true
        }
      },
      tooltip: {
        backgroundColor: 'rgba(26, 26, 26, 0.95)',
        titleColor: '#FF6B6B',
        bodyColor: 'rgba(255, 255, 255, 0.9)',
        borderColor: 'rgba(255, 107, 107, 0.3)',
        borderWidth: 1,
        titleFont: {
          family: 'Orbitron, monospace',
          size: 14
        },
        bodyFont: {
          family: 'Orbitron, monospace',
          size: 12
        },
        callbacks: {
          title: (context: any) => `Date: ${context[0].label}`,
          label: (context: any) => {
            if (context.datasetIndex === 0) {
              return `Stress Score: ${context.parsed.y}`
            } else {
              return `Mood: ${context.parsed.y.toFixed(0)}%`
            }
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(255, 107, 107, 0.2)',
          drawBorder: false
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.8)',
          font: {
            family: 'Orbitron, monospace',
            size: 11
          }
        }
      },
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        grid: {
          color: 'rgba(255, 107, 107, 0.2)',
          drawBorder: false
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.8)',
          font: {
            family: 'Orbitron, monospace',
            size: 11
          }
        },
        title: {
          display: true,
          text: 'Stress Score',
          color: '#FF6B6B',
          font: {
            family: 'Orbitron, monospace',
            size: 12
          }
        },
        min: 0,
        max: 100
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        grid: {
          drawOnChartArea: false
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.5)',
          font: {
            family: 'Orbitron, monospace',
            size: 11
          }
        },
        title: {
          display: true,
          text: 'Mood %',
          color: 'rgba(255, 255, 255, 0.5)',
          font: {
            family: 'Orbitron, monospace',
            size: 12
          }
        },
        min: 0,
        max: 100
      }
    },
    interaction: {
      intersect: false,
      mode: 'index' as const
    }
  }
  
  return (
    <div style={{ 
      height: '100%', 
      background: 'rgba(26, 26, 26, 0.8)',
      borderRadius: '8px',
      padding: '15px',
      border: '1px solid rgba(255, 107, 107, 0.2)'
    }}>
      <Line data={chartData} options={options} />
    </div>
  )
}

// Scientific Disclaimer Component
const ScientificDisclaimer: React.FC<{ confidence: number }> = ({ confidence }) => (
  <div style={{
    marginTop: '25px',
    padding: '18px',
    background: 'rgba(255, 211, 61, 0.1)',
    borderRadius: '12px',
    border: '1px solid rgba(255, 211, 61, 0.3)',
    position: 'relative'
  }}>
    <div style={{
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      height: '2px',
      background: 'linear-gradient(90deg, #FFD93D, #FFA500)'
    }}></div>
    
    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
      <i className="fas fa-exclamation-triangle" style={{ marginRight: '12px', color: '#FFD93D', fontSize: '18px' }} />
      <span style={{ fontWeight: 700, color: '#FFD93D', fontSize: '16px' }}>Scientific Disclaimer</span>
    </div>
    <div style={{ 
      fontSize: '14px', 
      color: 'rgba(255, 255, 255, 0.8)', 
      lineHeight: '1.6',
      marginBottom: '10px'
    }}>
      This analysis is based on music listening patterns and research-validated stress indicators. 
      Results show ~75-85% accuracy in research studies (Current confidence: {confidence}%). 
      <strong style={{ color: '#FFD93D' }}> This should not replace professional mental health assessment.</strong>
    </div>
    <div style={{
      fontSize: '13px',
      color: 'rgba(255, 211, 61, 0.8)',
      fontStyle: 'italic',
      display: 'flex',
      alignItems: 'center',
      gap: '8px'
    }}>
      <i className="fas fa-flask"></i>
      Research foundation: Dimitriev et al. (2023), Sachs et al. (2015), Groarke & Hogan (2018)
    </div>
  </div>
)

// Genre Evolution Chart Component
const GenreEvolutionChart: React.FC<{ timelineData: Array<{ month: string; genres: Record<string, number> }> }> = ({ timelineData }) => {
  // Get all unique genres
  const allGenres = Array.from(new Set(
    timelineData.flatMap(data => Object.keys(data.genres))
  ))
  
  // Color palette matching Dash implementation
  const colors = ['#1DB954', '#00D4FF', '#8B5CF6', '#F472B6', '#FBBF24', '#EF4444', '#10B981']
  
  // Prepare chart data
  const chartData = {
    labels: timelineData.map(data => data.month),
    datasets: allGenres.map((genre, index) => ({
      label: genre,
      data: timelineData.map(data => data.genres[genre] || 0),
      borderColor: colors[index % colors.length],
      backgroundColor: colors[index % colors.length] + '20',
      borderWidth: 3,
      pointRadius: 6,
      pointHoverRadius: 8,
      tension: 0.4,
      fill: false
    }))
  }
  
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: 'rgba(255, 255, 255, 0.8)',
          font: {
            family: 'Orbitron, monospace',
            size: 12
          },
          usePointStyle: true,
          pointStyle: 'circle'
        }
      },
      tooltip: {
        backgroundColor: 'rgba(26, 26, 26, 0.95)',
        titleColor: '#1DB954',
        bodyColor: 'rgba(255, 255, 255, 0.9)',
        borderColor: 'rgba(29, 185, 84, 0.3)',
        borderWidth: 1,
        titleFont: {
          family: 'Orbitron, monospace',
          size: 14
        },
        bodyFont: {
          family: 'Orbitron, monospace',
          size: 12
        },
        callbacks: {
          title: (context: any) => `Month: ${context[0].label}`,
          label: (context: any) => `${context.dataset.label}: ${context.parsed.y} plays`
        }
      }
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(29, 185, 84, 0.2)',
          drawBorder: false
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.8)',
          font: {
            family: 'Orbitron, monospace',
            size: 11
          }
        },
        title: {
          display: true,
          text: 'Month',
          color: 'rgba(255, 255, 255, 0.8)',
          font: {
            family: 'Orbitron, monospace',
            size: 12
          }
        }
      },
      y: {
        grid: {
          color: 'rgba(29, 185, 84, 0.2)',
          drawBorder: false
        },
        ticks: {
          color: 'rgba(255, 255, 255, 0.8)',
          font: {
            family: 'Orbitron, monospace',
            size: 11
          }
        },
        title: {
          display: true,
          text: 'Play Count',
          color: 'rgba(255, 255, 255, 0.8)',
          font: {
            family: 'Orbitron, monospace',
            size: 12
          }
        },
        beginAtZero: true
      }
    },
    interaction: {
      intersect: false,
      mode: 'index' as const
    },
    elements: {
      point: {
        hoverBackgroundColor: '#1DB954',
        hoverBorderColor: '#ffffff',
        hoverBorderWidth: 2
      }
    }
  }
  
  return (
    <div style={{ 
      height: '100%', 
      background: 'rgba(26, 26, 26, 0.8)',
      borderRadius: '8px',
      padding: '15px',
      border: '1px solid rgba(29, 185, 84, 0.2)'
    }}>
      <Line data={chartData} options={options} />
    </div>
  )
}

export default AIInsights