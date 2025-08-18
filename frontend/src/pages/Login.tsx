import React from 'react'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'

const Login: React.FC = () => {
  const { login, isLoading } = useAuth()

  return (
    <div className="min-h-screen bg-spotify-black flex items-center justify-center p-4">
      <Card className="w-full max-w-md bg-spotify-dark-gray border-spotify-gray">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-spotify-white">
            Spotify Wrapped Analytics
          </CardTitle>
          <CardDescription className="text-spotify-light-gray">
            Connect your Spotify account to get personalized insights
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center">
            <div className="w-16 h-16 bg-spotify-green rounded-full flex items-center justify-center mx-auto mb-4">
              <svg
                className="w-8 h-8 text-white"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.42 1.56-.299.421-1.02.599-1.559.3z"/>
              </svg>
            </div>
            <p className="text-spotify-light-gray mb-6">
              Discover your music personality, analyze your listening patterns, and get AI-powered insights about your musical journey.
            </p>
          </div>
          
          <Button
            onClick={login}
            disabled={isLoading}
            variant="spotify"
            className="w-full h-12 text-lg font-semibold"
          >
            {isLoading ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Connecting...
              </div>
            ) : (
              'Connect with Spotify'
            )}
          </Button>
          
          <div className="text-xs text-spotify-light-gray text-center mt-4">
            <p>
              By connecting, you agree to let us analyze your Spotify data to provide personalized insights.
              We don't store your music data permanently.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Login
