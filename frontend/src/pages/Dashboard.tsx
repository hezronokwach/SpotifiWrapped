import React, { useState, useEffect } from 'react'
import axios from 'axios'

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
  const [stats, setStats] = useState<UserStats | null>(null)
  const [topTracks, setTopTracks] = useState<Track[]>([])
  const [topArtists, setTopArtists] = useState<Artist[]>([])
  const [currentTrack, setCurrentTrack] = useState<Track | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true)

      // Import the configured API client
      const { default: api } = await import('../api')
      
      // First test the JWT token
      console.log('🔍 Dashboard: Testing JWT token...')
      const testRes = await api.get('/music/test')
      console.log('🔍 Dashboard: JWT test result:', testRes.data)

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

  return (
    <div className="space-y-6">
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
      {currentTrack && (
        <div className="relative p-6 rounded-3xl border transition-all duration-300 hover:transform hover:scale-[1.01] hover:-translate-y-1"
             style={{
               background: 'linear-gradient(135deg, rgba(26,26,26,0.95), rgba(18,18,18,0.95))',
               border: '1px solid rgba(29, 185, 84, 0.3)',
               boxShadow: '0 8px 32px rgba(0,0,0,0.3), 0 0 40px rgba(29, 185, 84, 0.1)',
               backdropFilter: 'blur(10px)'
             }}>
          <div className="absolute inset-0 rounded-3xl opacity-0 hover:opacity-100 transition-opacity duration-300"
               style={{
                 background: 'linear-gradient(45deg, rgba(29, 185, 84, 0.3), rgba(0, 212, 255, 0.3), rgba(139, 92, 246, 0.3), rgba(29, 185, 84, 0.3))',
                 backgroundSize: '400% 400%',
                 animation: 'gradientShift 8s ease infinite',
                 zIndex: -1
               }}>
          </div>
          <div className="mb-4">
            <h3 className="text-2xl font-bold font-orbitron"
                style={{
                  background: 'linear-gradient(45deg, #1DB954, #00D4FF)',
                  backgroundSize: '200% 200%',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  textTransform: 'uppercase',
                  letterSpacing: '1.5px',
                  textShadow: '0 0 20px rgba(29, 185, 84, 0.3)'
                }}>
              Currently Playing
            </h3>
          </div>
          <div className="flex items-center space-x-4">
            {currentTrack.images && currentTrack.images.length > 0 && (
              <img
                src={currentTrack.images[0].url}
                alt={currentTrack.album}
                className="w-16 h-16 rounded-md transition-transform duration-300 hover:scale-110"
                style={{
                  border: '2px solid rgba(29, 185, 84, 0.3)',
                  boxShadow: '0 4px 15px rgba(0, 0, 0, 0.3)'
                }}
              />
            )}
            <div className="flex-1">
              <h3 className="font-semibold font-orbitron" style={{ color: '#ffffff', textShadow: '0 0 10px rgba(255, 255, 255, 0.3)' }}>{currentTrack.name}</h3>
              <p style={{ color: 'rgba(255, 255, 255, 0.7)' }}>{currentTrack.artist}</p>
              <p className="text-sm" style={{ color: 'rgba(255, 255, 255, 0.5)' }}>{currentTrack.album}</p>
            </div>
          </div>
        </div>
      )}

      {/* Top Highlights Row - matches original Dash layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TopTrackHighlight />
        <TopArtistHighlight />
      </div>

      {/* Top Content Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Tracks */}
        <div className="relative p-6 rounded-3xl border transition-all duration-300 hover:transform hover:scale-[1.01] hover:-translate-y-1"
             style={{
               background: 'linear-gradient(135deg, rgba(26,26,26,0.95), rgba(18,18,18,0.95))',
               border: '1px solid rgba(29, 185, 84, 0.3)',
               boxShadow: '0 8px 32px rgba(0,0,0,0.3), 0 0 40px rgba(29, 185, 84, 0.1)',
               backdropFilter: 'blur(10px)'
             }}>
          <div className="absolute inset-0 rounded-3xl opacity-0 hover:opacity-100 transition-opacity duration-300"
               style={{
                 background: 'linear-gradient(45deg, rgba(29, 185, 84, 0.3), rgba(0, 212, 255, 0.3), rgba(139, 92, 246, 0.3), rgba(29, 185, 84, 0.3))',
                 backgroundSize: '400% 400%',
                 animation: 'gradientShift 8s ease infinite',
                 zIndex: -1
               }}>
          </div>
          <div className="mb-6">
            <h3 className="text-2xl font-bold mb-2 font-orbitron"
                style={{
                  background: 'linear-gradient(45deg, #1DB954, #00D4FF, #8b5cf6)',
                  backgroundSize: '200% 200%',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  textTransform: 'uppercase',
                  letterSpacing: '1.5px',
                  textShadow: '0 0 20px rgba(29, 185, 84, 0.3)'
                }}>
              Your Top Tracks
            </h3>
            <p className="text-sm" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
              Most played songs recently
            </p>
          </div>
          <div className="space-y-3 max-h-96 overflow-y-auto pr-2 scrollable-list">
            {topTracks.slice(0, 10).map((track, index) => (
              <div key={track.id} 
                   className="flex items-center space-x-3 p-3 rounded-xl transition-all duration-300 hover:transform hover:scale-[1.02]"
                   style={{
                     background: 'linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02))',
                     border: '1px solid rgba(255, 255, 255, 0.1)',
                     backdropFilter: 'blur(10px)'
                   }}>
                <span className="font-orbitron text-sm w-6 text-center"
                      style={{
                        color: 'rgba(29, 185, 84, 0.8)',
                        textShadow: '0 0 5px rgba(29, 185, 84, 0.3)'
                      }}>
                  {index + 1}
                </span>
                {track.images && track.images.length > 0 && (
                  <img
                    src={track.images[0].url}
                    alt={track.album}
                    className="w-10 h-10 rounded transition-transform duration-300 hover:scale-110"
                    style={{
                      border: '2px solid rgba(29, 185, 84, 0.3)',
                      boxShadow: '0 4px 15px rgba(0, 0, 0, 0.3)'
                    }}
                  />
                )}
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate" style={{ color: '#ffffff', textShadow: '0 0 10px rgba(255, 255, 255, 0.3)' }}>
                    {track.name}
                  </p>
                  <p className="text-sm truncate" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                    {track.artist}
                  </p>
                </div>
                <span className="text-sm" style={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                  {formatDuration(track.duration_ms)}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Top Artists */}
        <div className="relative p-6 rounded-3xl border transition-all duration-300 hover:transform hover:scale-[1.01] hover:-translate-y-1"
             style={{
               background: 'linear-gradient(135deg, rgba(26,26,26,0.95), rgba(18,18,18,0.95))',
               border: '1px solid rgba(139, 92, 246, 0.3)',
               boxShadow: '0 8px 32px rgba(0,0,0,0.3), 0 0 40px rgba(139, 92, 246, 0.1)',
               backdropFilter: 'blur(10px)'
             }}>
          <div className="absolute inset-0 rounded-3xl opacity-0 hover:opacity-100 transition-opacity duration-300"
               style={{
                 background: 'linear-gradient(45deg, rgba(139, 92, 246, 0.3), rgba(244, 114, 182, 0.3), rgba(29, 185, 84, 0.3), rgba(139, 92, 246, 0.3))',
                 backgroundSize: '400% 400%',
                 animation: 'gradientShift 8s ease infinite',
                 zIndex: -1
               }}>
          </div>
          <div className="mb-6">
            <h3 className="text-2xl font-bold mb-2 font-orbitron"
                style={{
                  background: 'linear-gradient(45deg, #8B5CF6, #F472B6, #1DB954)',
                  backgroundSize: '200% 200%',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  textTransform: 'uppercase',
                  letterSpacing: '1.5px',
                  textShadow: '0 0 20px rgba(139, 92, 246, 0.3)'
                }}>
              Your Top Artists
            </h3>
            <p className="text-sm" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
              Most listened to artists
            </p>
          </div>
          <div className="space-y-3 max-h-96 overflow-y-auto pr-2 scrollable-list artist-list">
            {topArtists.slice(0, 10).map((artist, index) => (
              <div key={artist.id} 
                   className="flex items-center space-x-3 p-3 rounded-xl transition-all duration-300 hover:transform hover:scale-[1.02]"
                   style={{
                     background: 'linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02))',
                     border: '1px solid rgba(255, 255, 255, 0.1)',
                     backdropFilter: 'blur(10px)'
                   }}>
                <span className="font-orbitron text-sm w-6 text-center"
                      style={{
                        color: 'rgba(139, 92, 246, 0.8)',
                        textShadow: '0 0 5px rgba(139, 92, 246, 0.3)'
                      }}>
                  {index + 1}
                </span>
                {artist.images && artist.images.length > 0 && (
                  <img
                    src={artist.images[0].url}
                    alt={artist.name}
                    className="w-10 h-10 rounded-full transition-transform duration-300 hover:scale-110"
                    style={{
                      border: '2px solid rgba(139, 92, 246, 0.3)',
                      boxShadow: '0 4px 15px rgba(0, 0, 0, 0.3)'
                    }}
                  />
                )}
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate" style={{ color: '#ffffff', textShadow: '0 0 10px rgba(255, 255, 255, 0.3)' }}>
                    {artist.name}
                  </p>
                  <p className="text-sm truncate" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                    {artist.genres.slice(0, 2).join(', ')}
                  </p>
                </div>
                <span className="text-sm" style={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                  {formatNumber(artist.followers)} followers
                </span>
              </div>
            ))}
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
      <ListeningPatterns />

      {/* Library Content Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SavedTracks />
        <Playlists />
      </div>

      {/* Refresh Button */}
      <div className="text-center">
        <Button
          onClick={fetchDashboardData}
          variant="spotify"
          disabled={isLoading}
        >
          {isLoading ? 'Refreshing...' : 'Refresh Data'}
        </Button>
      </div>
    </div>
  )
}

export default Dashboard
