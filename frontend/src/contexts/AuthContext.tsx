import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react'
import { authApi } from '../api'
import {
  initializeSession,
  storeSession,
  getSession,
  clearSession,
  validateSession,
  type TokenData
} from '@/lib/session'
import { getStoredCredentials } from '@/lib/credentials'

interface User {
  id: string
  display_name: string
  email: string
  images?: Array<{ url: string }>
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: () => Promise<void>
  logout: () => void
  isLoading: boolean
  isAuthenticated: boolean
  handleOAuthCallback: (code: string) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Initialize secure session management
    initializeSession()

    // Check for existing session
    const session = getSession()
    if (session.isAuthenticated && validateSession()) {
      setUser(session.user)
      setToken(session.token)
      setIsLoading(false)
    } else {
      // No valid session, check credentials for onboarding
      const credentials = getStoredCredentials()
      if (!credentials) {
        // Redirect to onboarding will be handled by App.tsx
      }
      setIsLoading(false)
    }
  }, [])



  const login = async () => {
    try {
      console.log('🔍 AuthContext: Starting login process...')
      setIsLoading(true)

      // Get stored credentials
      const credentials = getStoredCredentials()
      if (!credentials) {
        throw new Error('No credentials found. Please complete onboarding first.')
      }
      console.log('✅ AuthContext: Credentials found for login')

      // Get auth URL from backend with credentials
      console.log('🔍 AuthContext: Requesting auth URL from backend...')
      const response = await authApi.login(credentials.clientId, credentials.clientSecret)
      const authUrl = response.data.auth_url
      console.log('✅ AuthContext: Auth URL received:', authUrl)

      // Redirect to Spotify auth
      console.log('🔍 AuthContext: Redirecting to Spotify...')
      window.location.href = authUrl
    } catch (error) {
      console.error('❌ AuthContext: Login failed:', error)
      setIsLoading(false)
    }
  }

  const logout = () => {
    // Check if in demo mode before clearing
    const isDemoMode = localStorage.getItem('demo_mode') === 'true'
    
    // Clear secure session
    clearSession()

    // Update local state
    setUser(null)
    setToken(null)

    // Clear demo mode
    localStorage.removeItem('demo_mode')

    // Only notify backend if not in demo mode
    if (!isDemoMode) {
      // Note: logout endpoint not implemented in authApi yet
      console.log('Logout - demo mode check passed')
    }
  }

  const handleOAuthCallback = useCallback(async (code: string) => {
    try {
      console.log('🔍 AuthContext: Starting OAuth callback processing...')
      setIsLoading(true)

      // Get stored credentials for the callback
      console.log('🔍 AuthContext: Looking for stored credentials...')
      let credentials = getStoredCredentials()
      
      if (!credentials) {
        // Try alternative storage locations
        const altCreds = localStorage.getItem('spotify_credentials')
        if (altCreds) {
          try {
            credentials = JSON.parse(altCreds)
            console.log('✅ AuthContext: Found credentials in alternative storage')
          } catch (e) {
            console.error('❌ AuthContext: Failed to parse alternative credentials')
          }
        }
      }
      
      if (!credentials) {
        console.error('❌ AuthContext: No credentials found during OAuth callback')
        console.log('🔍 AuthContext: Available localStorage keys:', Object.keys(localStorage))
        throw new Error('No credentials found during OAuth callback')
      }
      console.log('✅ AuthContext: Credentials found for callback')

      console.log('🔍 AuthContext: Sending callback request to backend...')
      const response = await authApi.callback(code, credentials.clientId, credentials.clientSecret)

      console.log('✅ AuthContext: Callback response received:', response.status)

      const tokenData: TokenData = {
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token,
        expires_at: Date.now() + (response.data.expires_in * 1000),
        user: response.data.user
      }

      console.log('🔍 AuthContext: Storing session data...')
      // Store session securely
      storeSession(tokenData)

      // Update local state
      setToken(tokenData.access_token)
      setUser(tokenData.user)
      
      // Trigger a credentials check update
      window.dispatchEvent(new Event('credentialsChanged'))

      console.log('✅ AuthContext: Authentication completed successfully')
      console.log('🔍 AuthContext: User set to:', tokenData.user)
      console.log('🔍 AuthContext: Token set to:', tokenData.access_token ? 'Present' : 'Missing')

      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname)
    } catch (error) {
      console.error('OAuth callback failed:', error)
      // Clear any partial session data
      clearSession()
    } finally {
      setIsLoading(false)
    }
  }, []) // No dependencies needed as it only uses stable state setters

  // Handle OAuth callback - check on every render and when token changes
  useEffect(() => {
    const checkForOAuthCallback = () => {
      const urlParams = new URLSearchParams(window.location.search)
      const code = urlParams.get('code')
      const error = urlParams.get('error')

      console.log('🔍 AuthContext: Checking URL for OAuth callback')
      console.log('🔍 AuthContext: Current URL:', window.location.href)
      console.log('🔍 AuthContext: Code:', code ? 'Present' : 'None')
      console.log('🔍 AuthContext: Error:', error)
      console.log('🔍 AuthContext: Current token:', token ? 'Present' : 'None')

      if (error) {
        console.error('OAuth error:', error)
        setIsLoading(false)
        return
      }

      if (code && !token) {
        console.log('🔍 AuthContext: Processing OAuth callback...')
        handleOAuthCallback(code)
      }
    }

    checkForOAuthCallback()

    // Listen for manual OAuth trigger
    const handleForceOAuthCheck = () => {
      console.log('🔍 AuthContext: Manual OAuth check triggered')
      checkForOAuthCallback()
    }

    window.addEventListener('forceOAuthCheck', handleForceOAuthCheck)

    return () => {
      window.removeEventListener('forceOAuthCheck', handleForceOAuthCheck)
    }
  }, [token, handleOAuthCallback]) // Depend on token and handleOAuthCallback

  // Also check for OAuth callback when component mounts or URL changes
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const code = urlParams.get('code')

    if (code && !token) {
      console.log('🔍 AuthContext: URL change detected with OAuth code, processing...')
      handleOAuthCallback(code)
    }
  }, [token, handleOAuthCallback]) // Depend on token and handleOAuthCallback


  const value: AuthContextType = {
    user,
    token,
    login,
    logout,
    isLoading,
    isAuthenticated: !!user && !!token,
    handleOAuthCallback,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
