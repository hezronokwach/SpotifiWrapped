import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useDemoMode } from '../contexts/DemoModeContext'

const OnboardingPage: React.FC = () => {
  const { setDemoMode } = useDemoMode()
  const navigate = useNavigate()

  const handleDemoMode = () => {
    // Clear any existing auth tokens
    localStorage.removeItem('spotify_access_token')
    localStorage.removeItem('spotify_refresh_token')
    localStorage.removeItem('jwt_token')
    
    setDemoMode(true)
    navigate('/dashboard')
  }

  const handleSpotifyAuth = () => {
    // Clear demo mode and any stale credentials
    setDemoMode(false)
    localStorage.removeItem('spotify_credentials')
    localStorage.removeItem('spotify_access_token')
    localStorage.removeItem('spotify_refresh_token')
    localStorage.removeItem('jwt_token')
    
    // Trigger credentials check
    window.dispatchEvent(new Event('credentialsChanged'))
    
    // Redirect to setup page for fresh credentials
    navigate('/setup')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full space-y-6">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white mb-2 font-orbitron">
            SpotifiWrapped
          </h1>
          <p className="text-gray-400">
            Discover your music personality with AI-powered insights
          </p>
        </div>

        <div className="space-y-4">
          {/* Demo Mode Button */}
          <button
            onClick={handleDemoMode}
            className="demo-button"
          >
            <i className="fas fa-flask"></i>
            <div className="text-xl font-semibold mb-2">Try Demo Mode</div>
            <span className="demo-description">
              Explore with realistic sample data - no Spotify account needed
            </span>
          </button>

          {/* Spotify Auth Button */}
          <button
            onClick={handleSpotifyAuth}
            className="w-full bg-spotify-green hover:bg-green-500 text-black font-semibold py-4 px-6 rounded-2xl transition-all duration-300 hover:transform hover:scale-105 hover:shadow-lg"
          >
            <i className="fab fa-spotify text-2xl mr-3"></i>
            Connect with Spotify
          </button>
        </div>

        <div className="text-center text-sm text-gray-500">
          <p>
            Demo mode uses sample data for exploration.
            <br />
            Connect your Spotify account for personalized insights.
          </p>
        </div>
      </div>
    </div>
  )
}

export default OnboardingPage