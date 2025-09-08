import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api'
import '../spotify-components.css'

interface PersonalityData {
  ai_description: string
  personality_type: string
  confidence_score: number
  recommendations: Array<{
    name: string
    artist: string
    image_url?: string
    similarity_score: number
    reason: string
  }>
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
  const [personalityData, setPersonalityData] = useState<PersonalityData | null>(null)
  const [wellnessData, setWellnessData] = useState<WellnessData | null>(null)
  const [stressData, setStressData] = useState<StressData | null>(null)
  const [genreEvolution, setGenreEvolution] = useState<GenreEvolutionData | null>(null)
  const [recommendations, setRecommendations] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    fetchAIInsights()
  }, [])

  const fetchAIInsights = async () => {
    try {
      setIsLoading(true)
      
      // Fetch all AI insights in parallel
      const [personalityRes, wellnessRes, stressRes, genreRes, recRes] = await Promise.all([
        api.get('/ai/personality'),
        api.get('/ai/wellness'),
        api.get('/ai/stress'),
        api.get('/ai/genre-evolution'),
        api.get('/ai/recommendations')
      ])
      
      setPersonalityData(personalityRes.data)
      setWellnessData(wellnessRes.data)
      setStressData(stressRes.data)
      setGenreEvolution(genreRes.data)
      setRecommendations(recRes.data.recommendations || [])
      
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
        {recommendations && recommendations.length > 0 && (
          <div style={{ marginTop: '40px' }}>
            <RecommendationsCard recommendations={recommendations} />
          </div>
        )}

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
const PersonalityCard: React.FC<{ data: PersonalityData }> = ({ data }) => {
  const confidenceScore = data.confidence_score || 0
  const hasInsufficientData = confidenceScore < 0.5
  
  return (
    <div className="ai-insights-card ai-card-personality">
      <div className="ai-card-header">
        <h3 className="ai-card-title">
          <i className="ai-card-icon fas fa-brain"></i>
          Personality Analysis
        </h3>
        <i className="fas fa-user-circle"></i>
      </div>
      
      <div style={{ marginBottom: '20px' }}>
        <div style={{
          fontSize: '1.5rem',
          fontWeight: 700,
          color: 'var(--accent-purple)',
          marginBottom: '10px',
          fontFamily: "'Orbitron', monospace"
        }}>
          {data.personality_type || 'Music Explorer'}
        </div>
        <div className="ai-description">
          {hasInsufficientData 
            ? "Keep listening to more music to unlock deeper personality insights! We need more data to provide accurate analysis."
            : (data.ai_description || "Your unique music taste is still being analyzed. Keep exploring!")}
        </div>
        <div className="confidence-badge">
          {hasInsufficientData 
            ? "Insufficient Data" 
            : `${Math.round(confidenceScore * 100)}% Confidence`}
        </div>
      </div>
      
      {!hasInsufficientData && data.recommendations && data.recommendations.length > 0 && (
        <div>
          <h5 style={{ color: 'var(--accent-primary)', marginBottom: '15px' }}>Recommended for You</h5>
          <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
            {data.recommendations.slice(0, 3).map((rec, index) => (
              <div key={index} style={{
                display: 'flex',
                alignItems: 'center',
                padding: '10px',
                marginBottom: '10px',
                background: 'rgba(255,255,255,0.05)',
                borderRadius: '8px',
                border: '1px solid rgba(255,255,255,0.1)'
              }}>
                {rec.image_url && (
                  <img src={rec.image_url} alt={rec.name} style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '4px',
                    marginRight: '12px'
                  }} />
                )}
                <div style={{ flex: 1 }}>
                  <div style={{ color: 'var(--text-primary)', fontWeight: 600, fontSize: '14px' }}>
                    {rec.name}
                  </div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>
                    {rec.artist}
                  </div>
                  <div style={{ color: 'var(--accent-tertiary)', fontSize: '11px' }}>
                    {rec.reason}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {hasInsufficientData && (
        <div style={{
          textAlign: 'center',
          padding: '20px',
          background: 'rgba(255,193,7,0.1)',
          borderRadius: '8px',
          border: '1px solid rgba(255,193,7,0.3)'
        }}>
          <i className="fas fa-music" style={{ fontSize: '2rem', color: '#FFC107', marginBottom: '10px' }}></i>
          <div style={{ color: 'var(--text-primary)', fontWeight: 600, marginBottom: '5px' }}>
            Keep Exploring Music!
          </div>
          <div style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>
            Listen to more tracks to unlock personalized recommendations
          </div>
        </div>
      )}
    </div>
  )
}

const WellnessCard: React.FC<{ data: WellnessData }> = ({ data }) => (
  <div className="ai-insights-card ai-card-wellness">
    <div className="ai-card-header">
      <h3 className="ai-card-title">
        <i className="ai-card-icon fas fa-heart"></i>
        Wellness Analysis
      </h3>
      <i className="fas fa-leaf"></i>
    </div>
    
    <div style={{ textAlign: 'center', marginBottom: '20px' }}>
      <div className="wellness-score">
        {data.wellness_score}
      </div>
      <div style={{ color: 'var(--text-secondary)' }}>Wellness Score</div>
    </div>
    
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '20px' }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ color: 'var(--accent-primary)', fontWeight: 600 }}>{data.mood_indicator}</div>
        <div style={{ color: 'var(--text-muted)', fontSize: '12px' }}>Mood</div>
      </div>
      <div style={{ textAlign: 'center' }}>
        <div style={{ color: 'var(--accent-tertiary)', fontWeight: 600 }}>{data.energy_level}</div>
        <div style={{ color: 'var(--text-muted)', fontSize: '12px' }}>Energy</div>
      </div>
    </div>
    
    <div>
      <h5 style={{ color: 'var(--accent-primary)', marginBottom: '10px' }}>Recommendations</h5>
      {data.recommendations && data.recommendations.map((rec, index) => (
        <div key={index} className="therapeutic-suggestion">
          {rec}
        </div>
      ))}
    </div>
  </div>
)

const StressAnalysisCard: React.FC<{ data: StressData }> = ({ data }) => {
  const getStressColor = (score: number) => {
    if (score >= 70) return '#FF6B6B'
    if (score >= 40) return '#FFD93D'
    return '#1DB954'
  }
  
  return (
    <div className="ai-insights-card ai-card-stress">
      <div className="ai-card-header">
        <h3 className="ai-card-title">
          <i className="ai-card-icon fas fa-brain"></i>
          Stress Analysis
        </h3>
        <i className="fas fa-chart-line"></i>
      </div>
      
      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
        <div style={{
          fontSize: '3rem',
          fontWeight: 700,
          color: getStressColor(data.stress_score),
          fontFamily: "'Orbitron', monospace"
        }}>
          {Math.round(data.stress_score)}
        </div>
        <div style={{ color: 'var(--text-secondary)' }}>{data.stress_level}</div>
        <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '5px' }}>
          {Math.round(data.confidence)}% Confidence
        </div>
      </div>
      
      {data.stress_timeline && data.stress_timeline.length > 0 && (
        <div style={{ marginBottom: '20px' }}>
          <h5 style={{ color: 'var(--accent-primary)', marginBottom: '10px' }}>Recent Timeline</h5>
          <div style={{ height: '100px', overflowY: 'auto' }}>
            {data.stress_timeline.slice(-7).map((day, index) => (
              <div key={index} style={{
                display: 'flex',
                justifyContent: 'space-between',
                padding: '5px 0',
                borderBottom: '1px solid rgba(255,255,255,0.1)'
              }}>
                <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                  {new Date(day.date).toLocaleDateString()}
                </span>
                <span style={{
                  fontSize: '12px',
                  color: getStressColor(day.stress_score),
                  fontWeight: 600
                }}>
                  {Math.round(day.stress_score)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {data.personal_triggers && data.personal_triggers.length > 0 && (
        <div style={{ marginBottom: '20px' }}>
          <h5 style={{ color: 'var(--accent-primary)', marginBottom: '10px' }}>Personal Triggers</h5>
          {data.personal_triggers.slice(0, 2).map((trigger, index) => (
            <div key={index} style={{
              padding: '8px',
              marginBottom: '8px',
              background: 'rgba(255,69,0,0.1)',
              borderRadius: '6px',
              border: '1px solid rgba(255,69,0,0.3)'
            }}>
              <div style={{ fontSize: '12px', color: '#FF4500', fontWeight: 600 }}>
                {trigger.trigger}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                {trigger.recommendation}
              </div>
            </div>
          ))}
        </div>
      )}
      
      {data.recommendations && data.recommendations.length > 0 && (
        <div>
          <h5 style={{ color: 'var(--accent-primary)', marginBottom: '10px' }}>Recommendations</h5>
          {data.recommendations.slice(0, 2).map((rec, index) => (
            <div key={index} style={{
              padding: '10px',
              marginBottom: '10px',
              background: 'rgba(29,185,84,0.1)',
              borderRadius: '8px',
              border: '1px solid rgba(29,185,84,0.3)'
            }}>
              <div style={{ color: 'var(--accent-primary)', fontWeight: 600, fontSize: '13px' }}>
                {rec.title}
              </div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '12px', marginTop: '4px' }}>
                {rec.description}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

const GenreEvolutionCard: React.FC<{ data: GenreEvolutionData }> = ({ data }) => (
  <div className="ai-insights-card ai-card-genre-evolution">
    <div className="ai-card-header">
      <h3 className="ai-card-title">
        <i className="ai-card-icon fas fa-chart-line"></i>
        Genre Evolution
      </h3>
      <i className="fas fa-music"></i>
    </div>
    
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
    
    {data.insights && data.insights.length > 0 && (
      <div style={{ marginBottom: '20px' }}>
        <h5 style={{ color: 'var(--accent-primary)', marginBottom: '10px' }}>Insights</h5>
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

const RecommendationsCard: React.FC<{ recommendations: any[] }> = ({ recommendations }) => (
  <div className="ai-insights-card">
    <div className="ai-card-header">
      <h3 className="ai-card-title">
        <i className="ai-card-icon fas fa-magic"></i>
        AI Recommendations
      </h3>
      <i className="fas fa-stars"></i>
    </div>
    
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
  </div>
)

export default AIInsights