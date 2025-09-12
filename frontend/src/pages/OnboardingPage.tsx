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
    
    // Go directly to login page
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-6">
      <div className="max-w-4xl w-full">
        {/* Header */}
        <div className="text-center mb-12">
          <i className="fab fa-spotify text-6xl text-spotify-green mb-6 animate-pulse"></i>
          <h1 className="text-5xl font-bold text-white mb-4 bg-gradient-to-r from-white to-spotify-green bg-clip-text text-transparent">
            Connect Your Spotify
          </h1>
          <p className="text-xl text-gray-400">
            Choose how you'd like to experience SpotifiWrapped
          </p>
        </div>

        {/* Option Cards */}
        <div className="grid md:grid-cols-2 gap-8 mb-8">
          {/* Spotify Connection Card */}
          <div className="option-card group">
            <div className="text-center mb-6">
              <i className="fab fa-spotify text-5xl text-spotify-green mb-4"></i>
              <h3 className="text-2xl font-semibold text-white mb-2">
                Connect with Spotify
              </h3>
              <p className="text-gray-400">
                Access your real music data and personalized insights
              </p>
            </div>
            
            <div className="space-y-3 mb-6">
              <div className="flex items-center text-gray-300">
                <i className="fas fa-check text-spotify-green mr-3"></i>
                Real-time music data
              </div>
              <div className="flex items-center text-gray-300">
                <i className="fas fa-check text-spotify-green mr-3"></i>
                Personalized analytics
              </div>
              <div className="flex items-center text-gray-300">
                <i className="fas fa-check text-spotify-green mr-3"></i>
                Full functionality
              </div>
            </div>
            
            <button
              onClick={handleSpotifyAuth}
              className="w-full bg-spotify-green hover:bg-green-500 text-black font-semibold py-4 px-6 rounded-xl transition-all duration-300 hover:transform hover:scale-105"
            >
              Connect Spotify Account
            </button>
          </div>

          {/* Demo Mode Card */}
          <div className="option-card group">
            <div className="text-center mb-6">
              <i className="fas fa-play-circle text-5xl text-blue-500 mb-4"></i>
              <h3 className="text-2xl font-semibold text-white mb-2">
                Try Demo Mode
              </h3>
              <p className="text-gray-400">
                Explore with sample data to see what SpotifiWrapped can do
              </p>
            </div>
            
            <div className="space-y-3 mb-6">
              <div className="flex items-center text-gray-300">
                <i className="fas fa-check text-blue-500 mr-3"></i>
                Sample data included
              </div>
              <div className="flex items-center text-gray-300">
                <i className="fas fa-check text-blue-500 mr-3"></i>
                Full feature preview
              </div>
              <div className="flex items-center text-gray-300">
                <i className="fas fa-check text-blue-500 mr-3"></i>
                No account needed
              </div>
            </div>
            
            <button
              onClick={handleDemoMode}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-4 px-6 rounded-xl transition-all duration-300 hover:transform hover:scale-105"
            >
              Enter Demo Mode
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-gray-500">
          <p className="mb-2">
            Need help? Visit the{' '}
            <a 
              href="https://developer.spotify.com/dashboard" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-spotify-green hover:underline"
            >
              Spotify Developer Portal
            </a>
          </p>
          <p className="text-sm">
            Your data is secure and never stored permanently
          </p>
        </div>
      </div>
    </div>
  )
}

export default OnboardingPage