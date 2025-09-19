/**
 * Shared TypeScript interfaces for Spotify data structures
 * Based on actual API responses from the Flask backend
 */

export interface Track {
  id: string
  track?: string  // PRIMARY field from API
  name?: string   // Alternative field for compatibility
  artist: string
  album: string
  duration_ms: number
  popularity: number
  image_url?: string
  preview_url?: string
  external_urls?: {
    spotify: string
  }
  images?: Array<{ url: string }>
  // Audio features (optional)
  danceability?: number
  energy?: number
  valence?: number
  tempo?: number
  acousticness?: number
  instrumentalness?: number
  liveness?: number
  speechiness?: number
  // Current playing state
  progress_ms?: number
  is_playing?: boolean
}

export interface Artist {
  id: string
  artist?: string  // PRIMARY field from API
  name?: string    // Alternative field for compatibility
  genres: string | string[]
  followers: number
  popularity: number
  image_url?: string
  external_urls?: {
    spotify: string
  }
  images?: Array<{ url: string }>
}

export interface Album {
  album: string
  artist: string
  total_count: number
  image_url?: string
  rank: number
}

export interface Playlist {
  id: string
  name: string
  description: string
  tracks_total: number
  images: Array<{ url: string }>
  owner: string
  public: boolean
  external_urls: { spotify: string }
}

export interface UserData {
  display_name: string
  followers: number
  following: number
  image_url?: string
  product?: string
}

export interface UserStats {
  total_tracks: number
  total_artists: number
  total_albums: number
  total_playlists: number
  listening_time_minutes: number
}

export interface AudioFeatures {
  danceability: number
  energy: number
  speechiness: number
  acousticness: number
  instrumentalness: number
  liveness: number
  valence: number
  tempo: number
}

// API Response interfaces
export interface TopTracksResponse {
  tracks: Track[]
}

export interface TopArtistsResponse {
  artists: Artist[]
}

export interface TopAlbumsResponse {
  albums: Album[]
}

export interface SavedTracksResponse {
  saved_tracks: Track[]
  total: number
}

export interface PlaylistsResponse {
  playlists: Playlist[]
  total: number
}

// Additional interfaces
export interface TrackInfo extends Track {
  danceability: number
  energy: number
  valence: number
  acousticness: number
  instrumentalness: number
  liveness: number
  speechiness: number
}

export interface PersonalityData {
  personality_type: string
  confidence: number
  description: string
  traits: string[]
  recommendations?: any[]
  stress_indicators?: Record<string, any>
  error?: string
  message?: string
}

export interface SpotifyCredentials {
  clientId: string
  clientSecret: string
  redirectUri: string
}

// Utility functions for data access
export const getTrackName = (track: Track): string => {
  return track.track || track.name || 'Unknown Track'
}

export const getArtistName = (artist: Artist): string => {
  return artist.artist || artist.name || 'Unknown Artist'
}

export const getTrackImage = (track: Track): string => {
  return track.image_url || track.images?.[0]?.url || ''
}

export const getArtistImage = (artist: Artist): string => {
  return artist.image_url || artist.images?.[0]?.url || ''
}
