import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'

const Login: React.FC = () => {
  const navigate = useNavigate()
  const [clientId, setClientId] = useState('')
  const [clientSecret, setClientSecret] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleLogin = async () => {
    if (!clientId || !clientSecret) {
      setError('Please provide both Client ID and Client Secret')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      // Store credentials for the OAuth flow
      localStorage.setItem('spotify_credentials', JSON.stringify({
        clientId,
        clientSecret
      }))

      // Call the Flask API to get the auth URL
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          client_id: clientId,
          client_secret: clientSecret
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to get authorization URL')
      }

      const data = await response.json()
      window.location.href = data.auth_url
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to initiate Spotify authentication')
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-6">
      <div className="max-w-md w-full space-y-6">
        <div className="text-center">
          <i className="fab fa-spotify text-6xl text-spotify-green mb-4"></i>
          <h1 className="text-3xl font-bold text-white mb-2">Connect to Spotify</h1>
          <p className="text-gray-400">Enter your Spotify app credentials to get started</p>
        </div>

        <div className="bg-gray-900 p-6 rounded-2xl border border-gray-700">
          <div className="space-y-4">
            <div>
              <Label htmlFor="clientId" className="text-white mb-2 block">Spotify Client ID</Label>
              <Input
                id="clientId"
                type="text"
                value={clientId}
                onChange={(e) => setClientId(e.target.value)}
                placeholder="Enter your Spotify Client ID"
                className="bg-gray-800 border-gray-600 text-white"
              />
            </div>
            
            <div>
              <Label htmlFor="clientSecret" className="text-white mb-2 block">Spotify Client Secret</Label>
              <Input
                id="clientSecret"
                type="password"
                value={clientSecret}
                onChange={(e) => setClientSecret(e.target.value)}
                placeholder="Enter your Spotify Client Secret"
                className="bg-gray-800 border-gray-600 text-white"
              />
            </div>

            {error && (
              <div className="p-3 bg-red-900 border border-red-700 rounded-lg">
                <p className="text-red-300 text-sm">{error}</p>
              </div>
            )}

            <Button
              onClick={handleLogin}
              disabled={isLoading}
              className="w-full bg-spotify-green hover:bg-green-500 text-black font-semibold py-3"
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-black mr-2"></div>
                  Connecting...
                </div>
              ) : (
                'Connect with Spotify'
              )}
            </Button>
          </div>
        </div>

        <div className="text-center text-sm text-gray-500">
          <p className="mb-2">
            Need Spotify credentials?{' '}
            <a 
              href="https://developer.spotify.com/dashboard" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-spotify-green hover:underline"
            >
              Create a Spotify App
            </a>
          </p>
          <p>
            Set redirect URI to: <code className="bg-gray-800 px-2 py-1 rounded text-xs">{window.location.origin}/auth/callback</code>
          </p>
        </div>

        <div className="text-center">
          <Button 
            onClick={() => navigate('/')}
            variant="outline"
            className="border-gray-600 text-gray-300 hover:bg-gray-800"
          >
            ← Back to Home
          </Button>
        </div>
      </div>
    </div>
  )
}

export default Login
