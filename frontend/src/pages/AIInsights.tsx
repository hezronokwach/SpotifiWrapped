import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'

interface PersonalityData {
  personality_type: string
  ai_description: string
  dominant_mood: string
  diversity_score: number
}

interface StressPattern {
  pattern: string
  frequency: number
  severity: string
}

interface WellnessData {
  overall_stress_level: string
  stress_patterns: StressPattern[]
  recommendations: string[]
}

const AIInsights: React.FC = () => {
  const [personality, setPersonality] = useState<PersonalityData | null>(null)
  const [wellness, setWellness] = useState<WellnessData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchAIInsights()
  }, [])

  const fetchAIInsights = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      // Fetch AI insights data
      const [personalityRes, wellnessRes] = await Promise.all([
        axios.get('/api/ai/personality'),
        axios.get('/api/ai/wellness')
      ])

      setPersonality(personalityRes.data.personality)
      setWellness(wellnessRes.data.wellness)
    } catch (error) {
      console.error('Failed to fetch AI insights:', error)
      setError('Failed to load AI insights. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-spotify-green mx-auto mb-4"></div>
          <p className="text-spotify-white">Analyzing your music personality...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-400 mb-4">{error}</div>
        <Button onClick={fetchAIInsights} variant="spotify">
          Try Again
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-spotify-white mb-2">
          AI-Powered Music Insights
        </h1>
        <p className="text-spotify-light-gray">
          Discover your musical personality and wellness patterns
        </p>
      </div>

      {/* Personality Analysis */}
      {personality && (
        <Card className="bg-spotify-dark-gray border-spotify-gray">
          <CardHeader>
            <CardTitle className="text-spotify-white flex items-center">
              🧠 Music Personality Analysis
            </CardTitle>
            <CardDescription className="text-spotify-light-gray">
              AI-generated insights about your musical preferences
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-spotify-black rounded-lg">
                <h3 className="text-spotify-green font-semibold mb-2">Personality Type</h3>
                <p className="text-spotify-white text-lg">{personality.personality_type}</p>
              </div>
              <div className="text-center p-4 bg-spotify-black rounded-lg">
                <h3 className="text-spotify-green font-semibold mb-2">Dominant Mood</h3>
                <p className="text-spotify-white text-lg">{personality.dominant_mood}</p>
              </div>
              <div className="text-center p-4 bg-spotify-black rounded-lg">
                <h3 className="text-spotify-green font-semibold mb-2">Diversity Score</h3>
                <p className="text-spotify-white text-lg">{personality.diversity_score}/10</p>
              </div>
            </div>
            
            <div className="mt-6">
              <h3 className="text-spotify-white font-semibold mb-3">AI Description</h3>
              <p className="text-spotify-light-gray leading-relaxed">
                {personality.ai_description}
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Wellness Analysis */}
      {wellness && (
        <Card className="bg-spotify-dark-gray border-spotify-gray">
          <CardHeader>
            <CardTitle className="text-spotify-white flex items-center">
              💚 Music Wellness Analysis
            </CardTitle>
            <CardDescription className="text-spotify-light-gray">
              How your music reflects your emotional well-being
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-center p-6 bg-spotify-black rounded-lg">
              <h3 className="text-spotify-green font-semibold mb-2">Overall Stress Level</h3>
              <p className="text-spotify-white text-2xl font-bold">{wellness.overall_stress_level}</p>
            </div>
            
            {wellness.recommendations && wellness.recommendations.length > 0 && (
              <div className="mt-6">
                <h3 className="text-spotify-white font-semibold mb-3">Wellness Recommendations</h3>
                <ul className="space-y-2">
                  {wellness.recommendations.map((recommendation, index) => (
                    <li key={index} className="text-spotify-light-gray flex items-start">
                      <span className="text-spotify-green mr-2">•</span>
                      {recommendation}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Coming Soon Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="bg-spotify-dark-gray border-spotify-gray opacity-75">
          <CardHeader>
            <CardTitle className="text-spotify-white flex items-center">
              📈 Genre Evolution
              <span className="ml-2 text-xs bg-spotify-green text-white px-2 py-1 rounded">
                Coming Soon
              </span>
            </CardTitle>
            <CardDescription className="text-spotify-light-gray">
              Track how your music taste has evolved over time
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-spotify-light-gray">
              Visualize your musical journey and see how your preferences have changed.
            </p>
          </CardContent>
        </Card>

        <Card className="bg-spotify-dark-gray border-spotify-gray opacity-75">
          <CardHeader>
            <CardTitle className="text-spotify-white flex items-center">
              🎯 Smart Recommendations
              <span className="ml-2 text-xs bg-spotify-green text-white px-2 py-1 rounded">
                Coming Soon
              </span>
            </CardTitle>
            <CardDescription className="text-spotify-light-gray">
              AI-powered music recommendations based on your personality
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-spotify-light-gray">
              Get personalized music suggestions that match your unique listening patterns.
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Refresh Button */}
      <div className="text-center">
        <Button
          onClick={fetchAIInsights}
          variant="spotify"
          disabled={isLoading}
        >
          {isLoading ? 'Analyzing...' : 'Refresh Analysis'}
        </Button>
      </div>
    </div>
  )
}

export default AIInsights
