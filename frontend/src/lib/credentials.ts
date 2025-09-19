/**
 * Credentials validation utilities
 */

export interface SpotifyCredentials {
  clientId: string
  clientSecret: string
}

/**
 * Check if Spotify credentials are valid (non-empty)
 */
export function hasValidCredentials(credentials?: SpotifyCredentials): boolean {
  if (!credentials) {
    // Check stored credentials if none provided
    const stored = getStoredCredentials()
    if (!stored) return false
    credentials = stored
  }
  
  return Boolean(
    credentials.clientId && 
    credentials.clientId.trim().length > 0 &&
    credentials.clientSecret && 
    credentials.clientSecret.trim().length > 0
  )
}

/**
 * Get credentials from localStorage
 */
export function getStoredCredentials(): SpotifyCredentials | null {
  try {
    const stored = localStorage.getItem('spotify_credentials')
    if (!stored) return null
    
    const credentials = JSON.parse(stored)
    return hasValidCredentials(credentials) ? credentials : null
  } catch {
    return null
  }
}

/**
 * Store credentials in localStorage
 */
export function storeCredentials(credentials: SpotifyCredentials): void {
  if (hasValidCredentials(credentials)) {
    localStorage.setItem('spotify_credentials', JSON.stringify(credentials))
  }
}

/**
 * Clear stored credentials
 */
export function clearStoredCredentials(): void {
  localStorage.removeItem('spotify_credentials')
}

/**
 * Get OAuth credentials from URL params or localStorage
 */
export function getOAuthCredentials(): SpotifyCredentials | null {
  // First try URL params (for OAuth callback)
  const urlParams = new URLSearchParams(window.location.search)
  const clientId = urlParams.get('client_id')
  const clientSecret = urlParams.get('client_secret')
  
  if (clientId && clientSecret) {
    return { clientId, clientSecret }
  }
  
  // Fallback to stored credentials
  return getStoredCredentials()
}

/**
 * Validate credentials format (basic validation)
 */
export function validateCredentials(credentials: SpotifyCredentials): { isValid: boolean; errors: string[] } {
  const errors: string[] = []
  
  if (!credentials.clientId || credentials.clientId.trim().length === 0) {
    errors.push('Client ID is required')
  } else if (credentials.clientId.length < 10) {
    errors.push('Client ID appears to be too short')
  }
  
  if (!credentials.clientSecret || credentials.clientSecret.trim().length === 0) {
    errors.push('Client Secret is required')
  } else if (credentials.clientSecret.length < 10) {
    errors.push('Client Secret appears to be too short')
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

/**
 * Validate credentials with Spotify API
 */
export async function validateCredentialsWithAPI(credentials: SpotifyCredentials): Promise<{ isValid: boolean; error?: string }> {
  try {
    const response = await fetch('/api/auth/validate-credentials', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(credentials)
    })
    
    if (response.ok) {
      return { isValid: true }
    } else {
      const error = await response.text()
      return { isValid: false, error }
    }
  } catch (error) {
    return { isValid: false, error: 'Network error' }
  }
}