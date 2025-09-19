/**
 * Session management utilities
 */

export interface TokenData {
  access_token: string
  refresh_token?: string
  expires_at: number
  user: any
}

export interface SessionData {
  token: string
  user: any
  expiresAt: number
  isAuthenticated: boolean
}

/**
 * Initialize session management
 */
export function initializeSession(): void {
  // Setup axios interceptors or other initialization
  console.log('Session management initialized')
}

/**
 * Get session data from localStorage
 */
export function getSession(): SessionData {
  try {
    const stored = localStorage.getItem('auth_session')
    if (!stored) {
      return { token: '', user: null, expiresAt: 0, isAuthenticated: false }
    }
    
    const session = JSON.parse(stored)
    
    // Check if session is expired
    if (session.expiresAt && Date.now() > session.expiresAt) {
      clearSession()
      return { token: '', user: null, expiresAt: 0, isAuthenticated: false }
    }
    
    return { ...session, isAuthenticated: true }
  } catch {
    return { token: '', user: null, expiresAt: 0, isAuthenticated: false }
  }
}

/**
 * Store session data from token data
 */
export function storeSession(tokenData: TokenData): void {
  const sessionData: SessionData = {
    token: tokenData.access_token,
    user: tokenData.user,
    expiresAt: tokenData.expires_at,
    isAuthenticated: true
  }
  localStorage.setItem('auth_session', JSON.stringify(sessionData))
  localStorage.setItem('auth_token', tokenData.access_token)
}

/**
 * Clear session data securely
 */
export function clearSession(): void {
  // Clear all possible auth-related items
  const authKeys = [
    'auth_session',
    'auth_token', 
    'spotify_credentials',
    'spotify_access_token',
    'spotify_refresh_token',
    'jwt_token',
    'user_session'
  ]
  
  authKeys.forEach(key => {
    localStorage.removeItem(key)
    sessionStorage.removeItem(key)
  })
  
  // Clear any keys that might contain user data
  Object.keys(localStorage).forEach(key => {
    if (key.includes('user_') || key.includes('spotify_') || key.includes('auth_')) {
      localStorage.removeItem(key)
    }
  })
}

/**
 * Validate if session is still valid
 */
export function validateSession(): boolean {
  const session = getSession()
  return session.isAuthenticated && session.expiresAt > Date.now()
}

/**
 * Get auth token from session
 */
export function getAuthToken(): string | null {
  const session = getSession()
  return session.token || localStorage.getItem('auth_token')
}