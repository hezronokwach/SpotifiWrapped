import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'

const AuthCallback: React.FC = () => {
  const navigate = useNavigate()
  const { isAuthenticated, isLoading, user } = useAuth()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // This component now relies on the AuthContext to handle the callback.
    // We just need to react to the state changes.

    if (!isLoading) {
      if (isAuthenticated && user) {
        console.log('✅ AuthCallback: Authentication successful, navigating to dashboard...')
        navigate('/dashboard', { replace: true })
      } else {
        // If authentication fails, the user will be redirected by the App component
        // or we can show an error here.
        console.error('❌ AuthCallback: Authentication failed.')
        setError('Authentication failed. You will be redirected shortly.')
        setTimeout(() => {
          navigate('/onboarding', { replace: true })
        }, 3000)
      }
    }
  }, [isAuthenticated, isLoading, user, navigate])

  if (error) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center p-6">
        <div className="max-w-md w-full text-center">
          <div className="bg-red-900 border border-red-700 rounded-lg p-6">
            <h2 className="text-xl font-bold text-red-300 mb-2">Authentication Error</h2>
            <p className="text-red-200">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  return <LoadingSpinner message="Finalizing authentication..." />
}

export default AuthCallback
