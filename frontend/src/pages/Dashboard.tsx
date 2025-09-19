import React, { useState, useEffect } from 'react'

import { Button } from '../components/ui/button'
import { formatNumber, formatDuration } from '../lib/utils'
import AudioFeatures from '../components/AudioFeatures'
import GenreChart from '../components/GenreChart'
import SavedTracks from '../components/SavedTracks'
import Playlists from '../components/Playlists'
import TopAlbums from '../components/TopAlbums'

import ListeningPatterns from '../components/ListeningPatterns'
import UserProfile from '../components/UserProfile'
import TopTrackHighlight from '../components/TopTrackHighlight'
import TopArtistHighlight from '../components/TopArtistHighlight'
import DemoModeIndicator from '../components/DemoModeIndicator'
import { useDemoMode } from '../contexts/DemoModeContext'
import { sampleStats, sampleTracks, sampleArtists, sampleCurrentTrack } from '../data/sampleData'

interface UserStats {
  total_tracks: number
  total_artists: number
  total_albums: number
  total_playlists: number
  listening_time_minutes: number
}

interface Track {
  id: string
  name: string
  artist: string
  album: string
  popularity: number
  duration_ms: number
  progress_ms?: number
  is_playing?: boolean
  images: Array<{ url: string }>
}

interface Artist {
  id: string
  name: string
  genres: string[]
  popularity: number
  followers: number
  images: Array<{ url: string }>
}

const Dashboard: React.FC = () => {
  const { isDemoMode } = useDemoMode()
  const [stats, setStats] = useState<UserStats | null>(null)
  const [topTracks, setTopTracks] = useState<Track[]>([])
  const [topArtists, setTopArtists] = useState<Artist[]>([])
  const [currentTrack, setCurrentTrack] = useState<Track | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  useEffect(() => {
    fetchDashboardData()
  }, [isDemoMode])

  // Auto-refresh currently playing track every 30 seconds
  useEffect(() => {
    if (isDemoMode) return
    
    const refreshCurrentTrack = async () => {
      try {
        const { default: api } = await import('../api')
        const currentRes = await api.get('/music/tracks/current')
        setCurrentTrack(currentRes.data.currently_playing || null)
      } catch (error) {
        console.log('Failed to refresh current track:', error)
      }
    }
    
    const interval = setInterval(refreshCurrentTrack, 30000) // 30 seconds
    
    return () => clearInterval(interval)
  }, [isDemoMode])

  const refreshListeningData = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      const { default: api } = await import('../api')
      
      console.log('🔄 Refreshing recent listening data...')
      const refreshRes = await api.post('/music/refresh-data')
      console.log('✅ Listening data refreshed:', refreshRes.data)
      
      // After refreshing data, reload the dashboard and trigger component refreshes
      await fetchDashboardData()
      setRefreshTrigger(prev => prev + 1)
      
    } catch (error) {
      console.error('Failed to refresh listening data:', error)
      setError('Failed to refresh listening data. Please try again.')
      setIsLoading(false)
    }
  }

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true)
      setError(null)

      if (isDemoMode) {
        // Use sample data for demo mode - no API calls needed
        console.log('📊 Using demo data')
        setStats(sampleStats)
        setTopTracks(sampleTracks)
        setTopArtists(sampleArtists)
        setCurrentTrack({ ...sampleCurrentTrack, popularity: 85 })
        setIsLoading(false)
        return
      }

      // Import the configured API client for real data
      const { default: api } = await import('../api')
      
      // Fetch dashboard data sequentially to avoid overwhelming the backend
      console.log('🔍 Dashboard: Fetching user stats...')
      const statsRes = await api.get('/user/stats')
      console.log('🔍 Dashboard: Fetching top tracks...')
      const tracksRes = await api.get('/music/tracks/top?limit=10')
      console.log('🔍 Dashboard: Fetching top artists...')
      const artistsRes = await api.get('/music/artists/top?limit=10')
      console.log('🔍 Dashboard: Fetching current track...')
      const currentRes = await api.get('/music/tracks/current')
      console.log('🔍 Dashboard: All data fetched successfully')

      setStats(statsRes.data)
      setTopTracks(tracksRes.data.tracks || [])
      setTopArtists(artistsRes.data.artists || [])
      setCurrentTrack(currentRes.data.currently_playing || null)
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
      setError('Failed to load dashboard data. Please check your connection and try again.')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-spotify-green mx-auto mb-4"></div>
          <p className="text-spotify-white">Loading your music data...</p>
        </div>
      </div>
    )
  }

  if (error && !isDemoMode) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <i className="fas fa-exclamation-triangle text-red-500 text-4xl mb-4"></i>
          <h3 className="text-xl font-semibold text-white mb-2">Connection Error</h3>
          <p className="text-gray-400 mb-4">{error}</p>
          <Button onClick={fetchDashboardData} variant="spotify">
            Try Again
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Demo Mode Indicator */}
      <DemoModeIndicator />
      
      {/* User Profile Header - matches original Dash layout */}
      <UserProfile />

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="relative p-4 rounded-2xl border transition-all duration-300 hover:transform hover:scale-[1.02] hover:-translate-y-1"
               style={{
                 background: 'linear-gradient(135deg, rgba(26,26,26,0.95), rgba(18,18,18,0.95))',
                 border: '1px solid rgba(29, 185, 84, 0.3)',
                 boxShadow: '0 4px 20px rgba(0,0,0,0.3), 0 0 20px rgba(29, 185, 84, 0.1)',
                 backdropFilter: 'blur(10px)'
               }}>
            <div className="absolute inset-0 rounded-2xl opacity-0 hover:opacity-100 transition-opacity duration-300"
                 style={{
                   background: 'linear-gradient(45deg, rgba(29, 185, 84, 0.2), rgba(0, 212, 255, 0.2))',
                   backgroundSize: '400% 400%',
                   animation: 'gradientShift 8s ease infinite',
                   zIndex: -1
                 }}>
            </div>
            <div className="pb-2">
              <h3 className="text-sm font-medium font-orbitron" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                Total Tracks
              </h3>
            </div>
            <div className="text-2xl font-bold font-orbitron" style={{ color: '#1DB954', textShadow: '0 0 10px rgba(29, 185, 84, 0.5)' }}>
              {formatNumber(stats.total_tracks)}
            </div>
          </div>

          <div className="relative p-4 rounded-2xl border transition-all duration-300 hover:transform hover:scale-[1.02] hover:-translate-y-1"
               style={{
                 background: 'linear-gradient(135deg, rgba(26,26,26,0.95), rgba(18,18,18,0.95))',
                 border: '1px solid rgba(0, 212, 255, 0.3)',
                 boxShadow: '0 4px 20px rgba(0,0,0,0.3), 0 0 20px rgba(0, 212, 255, 0.1)',
                 backdropFilter: 'blur(10px)'
               }}>
            <div className="absolute inset-0 rounded-2xl opacity-0 hover:opacity-100 transition-opacity duration-300"
                 style={{
                   background: 'linear-gradient(45deg, rgba(0, 212, 255, 0.2), rgba(139, 92, 246, 0.2))',
                   backgroundSize: '400% 400%',
                   animation: 'gradientShift 8s ease infinite',
                   zIndex: -1
                 }}>
            </div>
            <div className="pb-2">
              <h3 className="text-sm font-medium font-orbitron" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                Unique Artists
              </h3>
            </div>
            <div className="text-2xl font-bold font-orbitron" style={{ color: '#00D4FF', textShadow: '0 0 10px rgba(0, 212, 255, 0.5)' }}>
              {formatNumber(stats.total_artists)}
            </div>
          </div>

          <div className="relative p-4 rounded-2xl border transition-all duration-300 hover:transform hover:scale-[1.02] hover:-translate-y-1"
               style={{
                 background: 'linear-gradient(135deg, rgba(26,26,26,0.95), rgba(18,18,18,0.95))',
                 border: '1px solid rgba(139, 92, 246, 0.3)',
                 boxShadow: '0 4px 20px rgba(0,0,0,0.3), 0 0 20px rgba(139, 92, 246, 0.1)',
                 backdropFilter: 'blur(10px)'
               }}>
            <div className="absolute inset-0 rounded-2xl opacity-0 hover:opacity-100 transition-opacity duration-300"
                 style={{
                   background: 'linear-gradient(45deg, rgba(139, 92, 246, 0.2), rgba(244, 114, 182, 0.2))',
                   backgroundSize: '400% 400%',
                   animation: 'gradientShift 8s ease infinite',
                   zIndex: -1
                 }}>
            </div>
            <div className="pb-2">
              <h3 className="text-sm font-medium font-orbitron" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                Albums Explored
              </h3>
            </div>
            <div className="text-2xl font-bold font-orbitron" style={{ color: '#8B5CF6', textShadow: '0 0 10px rgba(139, 92, 246, 0.5)' }}>
              {formatNumber(stats.total_albums)}
            </div>
          </div>

          <div className="relative p-4 rounded-2xl border transition-all duration-300 hover:transform hover:scale-[1.02] hover:-translate-y-1"
               style={{
                 background: 'linear-gradient(135deg, rgba(26,26,26,0.95), rgba(18,18,18,0.95))',
                 border: '1px solid rgba(244, 114, 182, 0.3)',
                 boxShadow: '0 4px 20px rgba(0,0,0,0.3), 0 0 20px rgba(244, 114, 182, 0.1)',
                 backdropFilter: 'blur(10px)'
               }}>
            <div className="absolute inset-0 rounded-2xl opacity-0 hover:opacity-100 transition-opacity duration-300"
                 style={{
                   background: 'linear-gradient(45deg, rgba(244, 114, 182, 0.2), rgba(29, 185, 84, 0.2))',
                   backgroundSize: '400% 400%',
                   animation: 'gradientShift 8s ease infinite',
                   zIndex: -1
                 }}>
            </div>
            <div className="pb-2">
              <h3 className="text-sm font-medium font-orbitron" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                Listening Time
              </h3>
            </div>
            <div className="text-2xl font-bold font-orbitron" style={{ color: '#F472B6', textShadow: '0 0 10px rgba(244, 114, 182, 0.5)' }}>
              {Math.round(stats.listening_time_minutes / 60)}h
            </div>
          </div>
        </div>
      )}

      {/* Currently Playing */}
      <div className="currently-playing-section">
        <div className="currently-playing-card">
          <div className="card-header">
            <h3><i className="fas fa-play"></i> Currently Playing</h3>
            <div className="playback-status">
              {currentTrack ? (
                <i className="fas fa-play" style={{ color: '#1DB954' }}></i>
              ) : (
                <i className="fas fa-pause" style={{ color: 'rgba(255,255,255,0.5)' }}></i>
              )}
            </div>
          </div>
          
          {currentTrack ? (
            <div className="track-content">
              <div className="album-art">
                {currentTrack.images && currentTrack.images.length > 0 ? (
                  <img 
                    src={currentTrack.images[0].url} 
                    alt={currentTrack.album}
                    className="album-image"
                  />
                ) : (
                  <div className="album-placeholder">
                    <i className="fas fa-music"></i>
                  </div>
                )}
              </div>
              
              <div className="track-details">
                <h4 className="track-name">{currentTrack.name}</h4>
                <p className="track-artist">by {currentTrack.artist}</p>
                <p className="track-album">from {currentTrack.album}</p>
                
                <div className="progress-section">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill"
                      style={{ 
                        width: currentTrack.duration_ms > 0 
                          ? `${Math.min(100, Math.max(0, (currentTrack.progress_ms || 0) / currentTrack.duration_ms * 100))}%`
                          : '0%'
                      }}
                    />
                  </div>
                  <div className="time-indicators">
                    <span className="current-time">
                      {formatDuration(currentTrack.progress_ms || 0)}
                    </span>
                    <span className="total-time">
                      {formatDuration(currentTrack.duration_ms)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="empty-state">
              <i className="fas fa-pause"></i>
              <h4>Nothing Playing</h4>
              <p>Play something on Spotify to see it here!</p>
            </div>
          )}
        </div>
      </div>

      {/* Top Highlights Row - matches original Dash layout */}
      <div className="highlights-row">
        <TopTrackHighlight />
        <TopArtistHighlight />
      </div>

      {/* Top Content Charts Row */}
      <div className="charts-row">
        {/* Top Tracks */}
        <div className="spotify-card soundwave-container fade-in">
          <div className="card-header">
            <h3><i className="fas fa-music"></i> Your Top Tracks</h3>
            <i className="fas fa-chart-bar"></i>
          </div>
          <div className="soundwave-scrollable">
            {topTracks.length > 0 ? (
              <div className="soundwave-list">
                {topTracks.slice(0, 10).map((track, index) => (
                  <div key={track.id} className="soundwave-item">
                    <div className="soundwave-rank">
                      <span className="rank-number">{index + 1}</span>
                      {index === 0 && <div className="status-badge status-top">🔥 Most Played</div>}
                      {index === 1 && <div className="status-badge status-high">⭐ Fan Favorite</div>}
                      {index === 2 && <div className="status-badge status-good">🎵 Top Hit</div>}
                    </div>
                    
                    <div className="soundwave-image">
                      {track.images && track.images.length > 0 ? (
                        <img
                          src={track.images[0].url}
                          alt={track.album}
                          className="track-image"
                        />
                      ) : (
                        <div className="track-image-placeholder">🎵</div>
                      )}
                    </div>

                    <div className="soundwave-content">
                      <div className="track-title">{track.name}</div>
                      <div className="track-subtitle">{track.artist} • {track.album}</div>
                      
                      <div className="track-stats">
                        <div className="stat-item">
                          <span className="stat-value">{formatDuration(track.duration_ms)}</span>
                          <span className="stat-label">Duration</span>
                        </div>
                        <div className="stat-item">
                          <span className="stat-value">{track.popularity || '—'}</span>
                          <span className="stat-label">Popularity</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="soundwave-empty">
                <div className="empty-soundwave-content">
                  <i className="fas fa-music"></i>
                  <p>No top tracks data available</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Top Artists */}
        <div className="spotify-card soundwave-container fade-in">
          <div className="card-header">
            <h3><i className="fas fa-microphone"></i> Your Top Artists</h3>
            <i className="fas fa-users"></i>
          </div>
          <div className="soundwave-scrollable">
            {topArtists.length > 0 ? (
              <div className="soundwave-list">
                {topArtists.slice(0, 10).map((artist, index) => (
                  <div key={artist.id} className="soundwave-item artist-item">
                    <div className="soundwave-rank">
                      <span className="rank-number">{index + 1}</span>
                      {index === 0 && <div className="status-badge status-top">⭐ Top Artist</div>}
                      {index === 1 && <div className="status-badge status-high">🎤 Fan Favorite</div>}
                      {index === 2 && <div className="status-badge status-good">🎵 Rising Star</div>}
                    </div>
                    
                    <div className="soundwave-image">
                      {artist.images && artist.images.length > 0 ? (
                        <img
                          src={artist.images[0].url}
                          alt={artist.name}
                          className="artist-image"
                        />
                      ) : (
                        <div className="artist-image-placeholder">🎤</div>
                      )}
                    </div>

                    <div className="soundwave-content">
                      <div className="track-title">{artist.name}</div>
                      <div className="track-subtitle">{artist.genres.slice(0, 2).join(', ') || 'Various Genres'}</div>
                      
                      <div className="track-stats">
                        <div className="stat-item">
                          <span className="stat-value">{formatNumber(artist.followers)}</span>
                          <span className="stat-label">Followers</span>
                        </div>
                        <div className="stat-item">
                          <span className="stat-value">{artist.popularity || '—'}</span>
                          <span className="stat-label">Popularity</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="soundwave-empty">
                <div className="empty-soundwave-content">
                  <i className="fas fa-microphone"></i>
                  <p>No top artists data available</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Top Albums Section */}
      <TopAlbums />



      {/* Audio Analysis Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AudioFeatures />
        <GenreChart />
      </div>

      {/* Listening Patterns Row */}
      <ListeningPatterns refreshTrigger={refreshTrigger} />

      {/* Library Content Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SavedTracks />
        <Playlists />
      </div>

      {/* AI Insights Link */}
      <div className="text-center" style={{ marginBottom: '20px' }}>
        <button
          onClick={() => window.location.href = '/ai-insights'}
          className="spotify-button"
          style={{ marginRight: '20px' }}
        >
          <i className="fas fa-brain" style={{ marginRight: '8px' }}></i>
          View AI Insights
        </button>
      </div>

      {/* Refresh Button */}
      <div className="text-center space-x-4">
        <Button
          onClick={fetchDashboardData}
          variant="spotify"
          disabled={isLoading}
        >
          {isLoading ? 'Refreshing...' : 'Refresh Dashboard'}
        </Button>
        
        {!isDemoMode && (
          <Button
            onClick={refreshListeningData}
            className="bg-blue-600 hover:bg-blue-500 text-white"
            disabled={isLoading}
          >
            {isLoading ? 'Updating...' : 'Update Recent Plays'}
          </Button>
        )}
      </div>
    </div>
  )
}

export default Dashboard
