import React from 'react'
import { hasValidCredentials, getStoredCredentials, type SpotifyCredentials } from '../lib/credentials.ts'
import { useAuth } from '../contexts/AuthContext'

const DebugCredentials: React.FC = () => {
  const { isAuthenticated, isLoading, login } = useAuth()
  const [debugInfo, setDebugInfo] = React.useState<{
    hasCredentials: boolean
    storedCredentials: SpotifyCredentials | null
    oauthCredentials: SpotifyCredentials | null
    timestamp: number
  }>({
    hasCredentials: false,
    storedCredentials: null,
    oauthCredentials: null,
    timestamp: Date.now()
  })

  // Manual OAuth callback trigger for testing
  const triggerOAuthCallback = () => {
    const urlParams = new URLSearchParams(window.location.search)
    const code = urlParams.get('code')
    if (code) {
      console.log('🔍 Debug: Manually triggering OAuth callback with code:', code)
      // Force a re-render of AuthContext by dispatching a custom event
      window.dispatchEvent(new CustomEvent('forceOAuthCheck'))
    } else {
      console.log('❌ Debug: No OAuth code found in URL')
    }
  }

  // Manual login trigger for testing
  const triggerLogin = () => {
    console.log('🔍 Debug: Manually triggering login...')
    login()
  }

  // Update debug info
  React.useEffect(() => {
    const updateDebugInfo = () => {
      setDebugInfo({
        hasCredentials: hasValidCredentials(),
        storedCredentials: getStoredCredentials(),
        oauthCredentials: getStoredCredentials(),
        timestamp: Date.now()
      })
    }

    updateDebugInfo()

    // Listen for credential changes
    const handleCredentialsChange = () => {
      console.log('🔍 Credentials changed event received')
      updateDebugInfo()
    }

    window.addEventListener('credentialsChanged', handleCredentialsChange)

    // Update every 2 seconds
    const interval = setInterval(updateDebugInfo, 2000)

    return () => {
      window.removeEventListener('credentialsChanged', handleCredentialsChange)
      clearInterval(interval)
    }
  }, [])

  // Only show in development
  if (!import.meta.env.DEV) {
    return null
  }

  return (
    <div className="fixed bottom-4 right-4 bg-background-card p-4 rounded-lg border border-default text-xs max-w-sm">
      <h4 className="font-bold text-primary mb-2">Debug: Auth Status</h4>
      <div className="space-y-1 text-secondary">
        <div>Has Valid: {debugInfo.hasCredentials ? '✅' : '❌'}</div>
        <div>Stored: {debugInfo.storedCredentials ? '✅' : '❌'}</div>
        <div>OAuth: {debugInfo.oauthCredentials ? '✅' : '❌'}</div>
        <div>Authenticated: {isAuthenticated ? '✅' : '❌'}</div>
        <div>Loading: {isLoading ? '⏳' : '✅'}</div>
        <div>URL: {window.location.pathname}</div>
        <div>Search: {window.location.search.substring(0, 30)}...</div>
        <div>Updated: {new Date(debugInfo.timestamp).toLocaleTimeString()}</div>
        <div className="flex gap-1 mt-2">
          {window.location.search.includes('code=') && (
            <button
              onClick={triggerOAuthCallback}
              className="px-2 py-1 bg-primary text-primary-foreground rounded text-xs"
            >
              🔄 Retry OAuth
            </button>
          )}
          {window.location.pathname === '/login' && debugInfo.hasCredentials && (
            <button
              onClick={triggerLogin}
              className="px-2 py-1 bg-green-600 text-white rounded text-xs"
            >
              🚀 Test Login
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default DebugCredentials
