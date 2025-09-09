import React, { useState, useEffect } from 'react'
import api from '../api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'

interface Playlist {
  id: string
  name: string
  description: string
  tracks_total: number
  images: Array<{ url: string }>
  owner: string
  public: boolean
  external_urls: { spotify: string }
}

interface PlaylistsResponse {
  playlists: Playlist[]
  total: number
}

const Playlists: React.FC = () => {
  const [playlists, setPlaylists] = useState<PlaylistsResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchPlaylists()
  }, [])

  const fetchPlaylists = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await api.get('/music/playlists?limit=8')
      console.log('Playlists response:', response.data)
      setPlaylists(response.data)
    } catch (err) {
      console.error('Failed to fetch playlists:', err)
      setError('Failed to load playlists')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="relative p-6 rounded-3xl border transition-all duration-300 hover:transform hover:scale-[1.01] hover:-translate-y-1"
           style={{
             background: 'linear-gradient(135deg, rgba(26,26,26,0.95), rgba(18,18,18,0.95))',
             border: '1px solid rgba(0, 212, 255, 0.3)',
             boxShadow: '0 8px 32px rgba(0,0,0,0.3), 0 0 40px rgba(0, 212, 255, 0.1)',
             backdropFilter: 'blur(10px)'
           }}>
        <div className="absolute inset-0 rounded-3xl opacity-0 hover:opacity-100 transition-opacity duration-300"
             style={{
               background: 'linear-gradient(45deg, rgba(0, 212, 255, 0.3), rgba(29, 185, 84, 0.3), rgba(139, 92, 246, 0.3), rgba(0, 212, 255, 0.3))',
               backgroundSize: '400% 400%',
               animation: 'gradientShift 8s ease infinite',
               zIndex: -1
             }}>
        </div>
        <div className="mb-6">
          <h3 className="text-2xl font-bold mb-2 font-orbitron"
              style={{
                background: 'linear-gradient(45deg, #00D4FF, #1DB954, #8b5cf6)',
                backgroundSize: '200% 200%',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                textTransform: 'uppercase',
                letterSpacing: '1.5px',
                textShadow: '0 0 20px rgba(0, 212, 255, 0.3)'
              }}>
            Your Playlists
          </h3>
          <p className="text-sm" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
            Loading your playlists...
          </p>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400"></div>
        </div>
      </div>
    )
  }

  if (error || !playlists || playlists.playlists.length === 0) {
    return (
      <Card className="bg-spotify-dark-gray border-spotify-gray">
        <CardHeader>
          <CardTitle className="text-spotify-white">Your Playlists</CardTitle>
          <CardDescription className="text-spotify-light-gray">
            Your music collections
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center text-spotify-light-gray py-8">
            {error || 'No playlists found'}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="relative p-6 rounded-3xl border transition-all duration-300 hover:transform hover:scale-[1.01] hover:-translate-y-1"
         style={{
           background: 'linear-gradient(135deg, rgba(26,26,26,0.95), rgba(18,18,18,0.95))',
           border: '1px solid rgba(0, 212, 255, 0.3)',
           boxShadow: '0 8px 32px rgba(0,0,0,0.3), 0 0 40px rgba(0, 212, 255, 0.1)',
           backdropFilter: 'blur(10px)'
         }}>
      <div className="absolute inset-0 rounded-3xl opacity-0 hover:opacity-100 transition-opacity duration-300"
           style={{
             background: 'linear-gradient(45deg, rgba(0, 212, 255, 0.3), rgba(29, 185, 84, 0.3), rgba(139, 92, 246, 0.3), rgba(0, 212, 255, 0.3))',
             backgroundSize: '400% 400%',
             animation: 'gradientShift 8s ease infinite',
             zIndex: -1
           }}>
      </div>
      <div className="mb-6">
        <h3 className="text-2xl font-bold mb-2 font-orbitron"
            style={{
              background: 'linear-gradient(45deg, #00D4FF, #1DB954, #8b5cf6)',
              backgroundSize: '200% 200%',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              textTransform: 'uppercase',
              letterSpacing: '1.5px',
              textShadow: '0 0 20px rgba(0, 212, 255, 0.3)'
            }}>
          Your Playlists
        </h3>
        <p className="text-sm" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
          {playlists.total} playlists • Showing {Math.min(8, playlists.playlists.length)}
        </p>
      </div>
      <div>
        <div className="space-y-3">
          {playlists.playlists.slice(0, 8).map((playlist) => (
            <div 
              key={playlist.id} 
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-spotify-gray/20 transition-colors group cursor-pointer"
              onClick={() => window.open(playlist.external_urls.spotify, '_blank')}
            >
              {/* Playlist Image */}
              <div className="flex-shrink-0">
                {playlist.images && playlist.images.length > 0 ? (
                  <img
                    src={playlist.images[0].url}
                    alt={playlist.name}
                    className="w-12 h-12 rounded-md shadow-md"
                  />
                ) : (
                  <div className="w-12 h-12 rounded-md bg-spotify-gray flex items-center justify-center">
                    <svg className="w-6 h-6 text-spotify-light-gray" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
                    </svg>
                  </div>
                )}
              </div>
              
              {/* Playlist Info */}
              <div className="flex-1 min-w-0">
                <h4 className="text-spotify-white font-medium truncate group-hover:text-spotify-green transition-colors">
                  {playlist.name}
                </h4>
                <div className="flex items-center space-x-2 text-xs text-spotify-light-gray">
                  <span>{playlist.tracks_total} tracks</span>
                  {playlist.owner && (
                    <>
                      <span>•</span>
                      <span>by {playlist.owner}</span>
                    </>
                  )}
                  {!playlist.public && (
                    <>
                      <span>•</span>
                      <span className="text-spotify-green">Private</span>
                    </>
                  )}
                </div>
                {playlist.description && (
                  <p className="text-xs text-spotify-light-gray mt-1 truncate">
                    {playlist.description}
                  </p>
                )}
              </div>
              
              {/* Play button on hover */}
              <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                <div className="w-8 h-8 bg-spotify-green rounded-full flex items-center justify-center hover:scale-105 transition-transform">
                  <svg className="w-4 h-4 text-black ml-0.5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z"/>
                  </svg>
                </div>
              </div>
            </div>
          ))}
        </div>
        
        {playlists.total > 8 && (
          <div className="mt-4 text-center">
            <button 
              onClick={fetchPlaylists}
              className="text-spotify-green hover:text-spotify-white text-sm font-medium transition-colors"
            >
              View all {playlists.total} playlists
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default Playlists
