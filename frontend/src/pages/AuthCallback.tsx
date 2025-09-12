import React, { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'

const AuthCallback: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { handleOAuthCallback } = useAuth()
  const [processingComplete, setProcessingComplete] = React.useState(false)

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
            // Small delay to ensure state is updated
            setTimeout(() => {
              navigate('/dashboard', { replace: true })
            }, 100)
          })
          .catch((error) => {
            console.error('❌ AuthCallback: OAuth callback failed:', error)
            setProcessingComplete(true)
            navigate('/onboarding', { replace: true })
          })
      } else {
        console.error('❌ AuthCallback: No code received, redirecting to login')
        navigate('/login', { replace: true })
      }
    }

    if (!processingComplete) {
      handleCallback()
    }
  }, [searchParams, navigate, handleOAuthCallback, processingComplete])

  return (
    <LoadingSpinner message="Completing authentication with Spotify..." />
  )
}

export default AuthCallback
