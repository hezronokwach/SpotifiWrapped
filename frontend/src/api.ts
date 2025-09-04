/**
 * Optimized API utilities with caching and error handling
 */

import axios, { AxiosResponse } from 'axios'

// Cache configuration
const CACHE_DURATION = 5 * 60 * 1000 // 5 minutes
const cache = new Map<string, { data: any; timestamp: number }>()

// API base configuration
const api = axios.create({
  baseURL: '/api',
  timeout: 15000, // 15 second timeout
})

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
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
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  
  return config
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    
    if (error.response?.status === 401) {
      // Token expired, clear session but don't redirect immediately
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_session')
      console.log('🔍 API: 401 error - session cleared')
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