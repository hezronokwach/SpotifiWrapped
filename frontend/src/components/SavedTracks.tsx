import React, { useState, useEffect } from 'react'
import api from '../api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { formatDuration } from '../lib/utils.ts'
import { useDemoMode } from '../contexts/DemoModeContext'

interface SavedTrack {
  id: string
  name: string
  artist: string
  album: string
  duration_ms: number
  added_at: string
  images: Array<{ url: string }>
  external_urls: { spotify: string }
}

interface SavedTracksResponse {
  saved_tracks: SavedTrack[]
  total: number
}

const SavedTracks: React.FC = () => {
  const { isDemoMode } = useDemoMode()
  const [savedTracks, setSavedTracks] = useState<SavedTracksResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchSavedTracks()
  }, [isDemoMode])

  const fetchSavedTracks = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      if (isDemoMode) {
        // Use sample saved tracks for demo mode
        const sampleSavedTracks = {
          saved_tracks: [
            {
              id: 'demo_saved_1',
              name: 'Blinding Lights',
              artist: 'The Weeknd',
              album: 'After Hours',
              duration_ms: 200040,
              added_at: '2024-01-15T10:30:00Z',
              images: [{ url: 'https://picsum.photos/300/300?random=30' }],
              external_urls: { spotify: '#' }
            },
            {
              id: 'demo_saved_2',
              name: 'Watermelon Sugar',
              artist: 'Harry Styles',
              album: 'Fine Line',
              duration_ms: 174000,
              added_at: '2024-01-10T14:20:00Z',
              images: [{ url: 'https://picsum.photos/300/300?random=31' }],
              external_urls: { spotify: '#' }
            },
            {
              id: 'demo_saved_3',
              name: 'Good 4 U',
              artist: 'Olivia Rodrigo',
              album: 'SOUR',
              duration_ms: 178147,
              added_at: '2024-01-05T09:15:00Z',
              images: [{ url: 'https://picsum.photos/300/300?random=32' }],
              external_urls: { spotify: '#' }
            }
          ],
          total: 3
        }
        setSavedTracks(sampleSavedTracks)
        setIsLoading(false)
        return
      }
      
      const response = await api.get('/music/tracks/saved?limit=10')
      setSavedTracks(response.data)
    } catch (err) {
      console.error('Failed to fetch saved tracks:', err)
      setError('Failed to load saved tracks')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <Card className="bg-spotify-dark-gray border-spotify-gray">
        <CardHeader>
          <CardTitle className="text-spotify-white">Your Saved Tracks</CardTitle>
          <CardDescription className="text-spotify-light-gray">
            Loading your liked songs...
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-spotify-green"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error || !savedTracks || !savedTracks.saved_tracks || savedTracks.saved_tracks.length === 0) {
    return (
      <Card className="bg-spotify-dark-gray border-spotify-gray">
        <CardHeader>
          <CardTitle className="text-spotify-white">Your Saved Tracks</CardTitle>
          <CardDescription className="text-spotify-light-gray">
            Your recently liked songs
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center text-spotify-light-gray py-8">
            {error || 'No saved tracks found'}
          </div>
        </CardContent>
      </Card>
    )
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now.getTime() - date.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays === 1) return 'Yesterday'
    if (diffDays < 7) return `${diffDays} days ago`
    if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`
    if (diffDays < 365) return `${Math.ceil(diffDays / 30)} months ago`
    return `${Math.ceil(diffDays / 365)} years ago`
  }

  return (
    <div className="relative p-6 rounded-3xl border transition-all duration-300 hover:transform hover:scale-[1.01] hover:-translate-y-1"
         style={{
           background: 'linear-gradient(135deg, rgba(26,26,26,0.95), rgba(18,18,18,0.95))',
           border: '1px solid rgba(29, 185, 84, 0.3)',
           boxShadow: '0 8px 32px rgba(0,0,0,0.3), 0 0 40px rgba(29, 185, 84, 0.1)',
           backdropFilter: 'blur(10px)'
         }}>

      {/* Animated border gradient */}
      <div className="absolute inset-0 rounded-3xl opacity-0 hover:opacity-100 transition-opacity duration-300"
           style={{
             background: 'linear-gradient(45deg, rgba(29, 185, 84, 0.3), rgba(0, 212, 255, 0.3), rgba(139, 92, 246, 0.3), rgba(29, 185, 84, 0.3))',
             backgroundSize: '400% 400%',
             animation: 'gradientShift 8s ease infinite',
             zIndex: -1
           }}>
      </div>

      {/* Header */}
      <div className="mb-6">
        <h3 className="text-2xl font-bold mb-2"
            style={{
              background: 'linear-gradient(45deg, #1DB954, #00D4FF, #8b5cf6)',
              backgroundSize: '200% 200%',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              fontFamily: "'Orbitron', monospace",
              textTransform: 'uppercase',
              letterSpacing: '1.5px',
              textShadow: '0 0 20px rgba(29, 185, 84, 0.3)'
            }}>
          Your Saved Tracks
        </h3>
        <p className="text-sm" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
          {savedTracks.total} liked songs • Showing recent 10
        </p>
      </div>

      {/* Content */}
      <div>
        <div className="space-y-3">
          {savedTracks.saved_tracks.map((track, index) => (
            <div key={track.id}
                 className="flex items-center space-x-4 group p-3 rounded-xl transition-all duration-300 hover:transform hover:scale-[1.02]"
                 style={{
                   background: 'linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02))',
                   border: '1px solid rgba(255, 255, 255, 0.1)',
                   backdropFilter: 'blur(10px)'
                 }}
                 onMouseEnter={(e) => {
                   e.currentTarget.style.borderColor = 'rgba(29, 185, 84, 0.5)'
                   e.currentTarget.style.boxShadow = '0 8px 25px rgba(29, 185, 84, 0.2)'
                 }}
                 onMouseLeave={(e) => {
                   e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)'
                   e.currentTarget.style.boxShadow = 'none'
                 }}>
              <span className="font-mono text-sm w-8 text-center"
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
                  className="w-12 h-12 rounded-lg object-cover transition-transform duration-300 group-hover:scale-110"
                  style={{
                    border: '2px solid rgba(29, 185, 84, 0.3)',
                    boxShadow: '0 4px 15px rgba(0, 0, 0, 0.3)'
                  }}
                />
              )}
              
              <div className="flex-1 min-w-0">
                <p className="font-semibold truncate transition-colors duration-300"
                   style={{
                     color: '#ffffff',
                     textShadow: '0 0 10px rgba(255, 255, 255, 0.3)'
                   }}
                   onMouseEnter={(e) => (e.target as HTMLElement).style.color = '#1DB954'}
                   onMouseLeave={(e) => (e.target as HTMLElement).style.color = '#ffffff'}>
                  {track.name}
                </p>
                <p className="text-sm truncate" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  {track.artist} • {track.album}
                </p>
              </div>
              
              <div className="text-right">
                <p className="text-spotify-light-gray text-sm">
                  {formatDuration(track.duration_ms)}
                </p>
                <p className="text-spotify-light-gray text-xs">
                  {formatDate(track.added_at)}
                </p>
              </div>
              
              {/* Heart icon to indicate it's saved */}
              <div className="text-spotify-green">
                <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
                  <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                </svg>
              </div>
            </div>
          ))}
        </div>
        
        {savedTracks.total > 10 && (
          <div className="mt-4 text-center">
            <button 
              onClick={fetchSavedTracks}
              className="text-spotify-green hover:text-spotify-white text-sm font-medium transition-colors"
            >
              View all {savedTracks.total} saved tracks
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default SavedTracks
