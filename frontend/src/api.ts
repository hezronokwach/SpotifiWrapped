/**
 * Optimized API utilities with caching and error handling
 */

import axios, { AxiosResponse } from 'axios'

// Cache configuration
const CACHE_DURATION = 5 * 60 * 1000 // 5 minutes
const cache = new Map<string, { data: any; timestamp: number }>()

// API base configuration - Force Leepcell backend in production
const API_BASE_URL = window.location.hostname.includes('localhost') 
  ? 'http://localhost:5000/api'
  : 'https://potifirapped-hezronokwach2523-4txz7dqh.leapcell.dev/api'

console.log('🔍 API Base URL:', API_BASE_URL)

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 second timeout for album analysis
  withCredentials: false, // Don't send cookies to external API
})

// Check if token is expired
function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.exp * 1000 < Date.now()
  } catch {
    return true
  }
}

// Get valid token with expiration check
function getValidToken(): string | null {
  let token = null
  
  // Try auth_session first (primary storage)
  try {
    const sessionData = localStorage.getItem('auth_session')
    if (sessionData) {
      const session = JSON.parse(sessionData)
      token = session.token
    }
  } catch (error) {
    // Fallback to direct token storage
    token = localStorage.getItem('auth_token')
  }
  
  // Check if token is expired
  if (token && isTokenExpired(token)) {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_session')
    return null
  }
  
  return token
}

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  // Skip auth for login and callback endpoints
  const skipAuth = [
    '/auth/login',
    '/auth/callback',
    '/auth/validate-credentials'
  ].some(path => config.url?.includes(path))
  
  if (!skipAuth) {
    const token = getValidToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  
  return config
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    console.error('API Error:', error.response?.data || error.message)
    
    if (error.response?.status === 401) {
      // Token expired or invalid, clear session and redirect to login
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_session')
      localStorage.removeItem('spotify_credentials')
      console.log('🔍 API: 401 error - redirecting to login')
      
      // Redirect to onboarding page
      if (window.location.pathname !== '/login' && window.location.pathname !== '/' && window.location.pathname !== '/onboarding') {
        window.location.href = '/onboarding'
      }
    }
    
    return Promise.reject(error)
  }
)

/**
 * Cached API call with automatic retry
 */
async function cachedApiCall<T>(
  key: string,
  apiCall: () => Promise<AxiosResponse<T>>,
  useCache = true
): Promise<T> {
  // Check cache first
  if (useCache) {
    const cached = cache.get(key)
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
      return cached.data
    }
  }

  try {
    const response = await apiCall()
    const data = response.data

    // Cache the result
    if (useCache) {
      cache.set(key, { data, timestamp: Date.now() })
    }

    return data
  } catch (error) {
    // If we have cached data, return it as fallback
    if (useCache) {
      const cached = cache.get(key)
      if (cached) {
        console.warn(`API call failed, using cached data for ${key}`)
        return cached.data
      }
    }
    throw error
  }
}

/**
 * Clear cache for specific key or all keys
 */
export function clearCache(key?: string) {
  if (key) {
    cache.delete(key)
  } else {
    cache.clear()
  }
}

/**
 * Refresh JWT token
 */
export async function refreshToken(): Promise<string | null> {
  try {
    const response = await api.post('/auth/refresh')
    const newToken = response.data.access_token
    
    // Update stored token
    try {
      const sessionData = localStorage.getItem('auth_session')
      if (sessionData) {
        const session = JSON.parse(sessionData)
        session.token = newToken
        localStorage.setItem('auth_session', JSON.stringify(session))
      } else {
        localStorage.setItem('auth_token', newToken)
      }
    } catch {
      localStorage.setItem('auth_token', newToken)
    }
    
    return newToken
  } catch (error) {
    console.error('Token refresh failed:', error)
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_session')
    window.location.href = '/onboarding'
    return null
  }
}

/**
 * Authentication API calls
 */
export const authApi = {
  refresh: () => refreshToken(),
  
  validateCredentials: (clientId: string, clientSecret: string) =>
    api.post('/auth/validate-credentials', { clientId, clientSecret }),
    
  login: (clientId: string, clientSecret: string) =>
    api.post('/auth/login', { client_id: clientId, client_secret: clientSecret }),
    
  callback: (code: string, clientId: string, clientSecret: string) =>
    api.post('/auth/callback', { code, client_id: clientId, client_secret: clientSecret }),
    
  status: () => api.get('/auth/status')
}

/**
 * Music API calls
 */
export const musicApi = {
  getTopTracks: (limit = 20, timeRange = 'medium_term', useCache = true) =>
    cachedApiCall(
      `top-tracks-${limit}-${timeRange}`,
      () => api.get(`/music/tracks/top?limit=${limit}&time_range=${timeRange}`),
      useCache
    ),

  getTopArtists: (limit = 20, timeRange = 'medium_term', useCache = true) =>
    cachedApiCall(
      `top-artists-${limit}-${timeRange}`,
      () => api.get(`/music/artists/top?limit=${limit}&time_range=${timeRange}`),
      useCache
    ),

  getTopAlbums: (limit = 10, useCache = true) =>
    cachedApiCall(
      `top-albums-${limit}`,
      () => api.get(`/music/albums/top?limit=${limit}`),
      useCache
    ),

  getSavedTracks: (limit = 20, offset = 0, useCache = true) =>
    cachedApiCall(
      `saved-tracks-${limit}-${offset}`,
      () => api.get(`/music/tracks/saved?limit=${limit}&offset=${offset}`),
      useCache
    ),

  getPlaylists: (limit = 20, offset = 0, useCache = true) =>
    cachedApiCall(
      `playlists-${limit}-${offset}`,
      () => api.get(`/music/playlists?limit=${limit}&offset=${offset}`),
      useCache
    ),

  getCurrentTrack: (useCache = false) =>
    cachedApiCall(
      'current-track',
      () => api.get('/music/tracks/current'),
      useCache // Don't cache current track by default
    ),
}

/**
 * User API calls
 */
export const userApi = {
  getProfile: (useCache = true) =>
    cachedApiCall(
      'user-profile',
      () => api.get('/user/profile'),
      useCache
    ),

  getStats: (useCache = true) =>
    cachedApiCall(
      'user-stats',
      () => api.get('/user/stats'),
      useCache
    ),
}

/**
 * AI Insights API calls
 */
export const aiApi = {
  getPersonality: (useCache = true) =>
    cachedApiCall(
      'ai-personality',
      () => api.get('/ai/personality'),
      useCache
    ),

  getWellness: (useCache = true) =>
    cachedApiCall(
      'ai-wellness',
      () => api.get('/ai/wellness'),
      useCache
    ),
}

/**
 * Batch API calls for dashboard
 */
export async function fetchDashboardData() {
  try {
    const [
      topTracks,
      topArtists,
      userProfile,
      userStats,
      currentTrack
    ] = await Promise.allSettled([
      musicApi.getTopTracks(1),
      musicApi.getTopArtists(1),
      userApi.getProfile(),
      userApi.getStats(),
      musicApi.getCurrentTrack()
    ])

    return {
      topTrack: topTracks.status === 'fulfilled' ? topTracks.value.tracks?.[0] : null,
      topArtist: topArtists.status === 'fulfilled' ? topArtists.value.artists?.[0] : null,
      userProfile: userProfile.status === 'fulfilled' ? userProfile.value : null,
      userStats: userStats.status === 'fulfilled' ? userStats.value : null,
      currentTrack: currentTrack.status === 'fulfilled' ? currentTrack.value.currently_playing : null,
    }
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
    throw error
  }
}

export default api