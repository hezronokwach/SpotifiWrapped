import React, { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'

const AuthCallback: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { handleOAuthCallback } = useAuth()
  const [processingComplete, setProcessingComplete] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  const [isProcessing, setIsProcessing] = React.useState(false)

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code')
      const error = searchParams.get('error')

      console.log('🔍 AuthCallback: Processing callback...')
      console.log('🔍 AuthCallback: Code:', code ? 'Present' : 'None')
      console.log('🔍 AuthCallback: Error:', error)

      if (error) {
        console.error('❌ AuthCallback: OAuth error:', error)
        navigate('/login', { replace: true })
        return
      }

      if (code) {
        console.log('✅ AuthCallback: OAuth code received, calling handleOAuthCallback directly...')

        // Call handleOAuthCallback directly
        handleOAuthCallback(code)
          .then(() => {
            console.log('✅ AuthCallback: OAuth callback completed successfully')
            setProcessingComplete(true)
            setIsProcessing(false)
            // Small delay to ensure state is updated
            setTimeout(() => {
              navigate('/dashboard', { replace: true })
            }, 100)
          })
          .catch((error) => {
            console.error('❌ AuthCallback: OAuth callback failed:', error)
            setProcessingComplete(true)
            setIsProcessing(false)
            setError(error.message || 'Authentication failed')
            // Don't redirect immediately, show error for 5 seconds
            setTimeout(() => {
              navigate('/onboarding', { replace: true })
            }, 5000)
          })
      } else {
        console.error('❌ AuthCallback: No code received, redirecting to login')
        setIsProcessing(false)
        navigate('/login', { replace: true })
      }
    }

    if (!processingComplete && !isProcessing) {
      setIsProcessing(true)
      handleCallback()
    }
  }, [searchParams, navigate, handleOAuthCallback, processingComplete, isProcessing])

  if (error) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center p-6">
        <div className="max-w-md w-full text-center">
          <div className="bg-red-900 border border-red-700 rounded-lg p-6 mb-4">
            <h2 className="text-xl font-bold text-red-300 mb-2">Authentication Error</h2>
            <p className="text-red-200 mb-4">{error}</p>
            <p className="text-red-400 text-sm">Redirecting to onboarding in 5 seconds...</p>
          </div>
          <button 
            onClick={() => navigate('/onboarding', { replace: true })}
            className="bg-spotify-green text-black px-4 py-2 rounded font-semibold"
          >
            Go to Onboarding Now
          </button>
        </div>
      </div>
    )
  }

  return (
    <LoadingSpinner message="Completing authentication with Spotify..." />
  )
}

export default AuthCallback
