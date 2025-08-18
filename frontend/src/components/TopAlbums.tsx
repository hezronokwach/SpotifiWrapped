import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'

interface Album {
  album: string
  artist: string
  total_count: number
  image_url?: string
  rank: number
}

interface TopAlbumsResponse {
  albums: Album[]
}

const TopAlbums: React.FC = () => {
  const [topAlbums, setTopAlbums] = useState<TopAlbumsResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchTopAlbums()
  }, [])

  const fetchTopAlbums = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await axios.get('/api/music/albums/top?limit=6')
      setTopAlbums(response.data)
    } catch (err) {
      console.error('Failed to fetch top albums:', err)
      setError('Failed to load top albums')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <Card className="bg-spotify-dark-gray border-spotify-gray">
        <CardHeader>
          <CardTitle className="text-spotify-white">Your Top Albums</CardTitle>
          <CardDescription className="text-spotify-light-gray">
            Loading your most played albums...
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

  if (error || !topAlbums || topAlbums.albums.length === 0) {
    return (
      <div className="relative p-6 rounded-3xl border transition-all duration-300"
           style={{
             background: 'linear-gradient(135deg, rgba(26,26,26,0.95), rgba(18,18,18,0.95))',
             border: '1px solid rgba(29, 185, 84, 0.3)',
             boxShadow: '0 8px 32px rgba(0,0,0,0.3), 0 0 40px rgba(29, 185, 84, 0.1)',
             backdropFilter: 'blur(10px)'
           }}>
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
                letterSpacing: '1.5px'
              }}>
            Your Top Albums
          </h3>
          <p className="text-sm" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
            Your most listened to albums
          </p>
        </div>
        <div className="text-center py-12" style={{ color: 'rgba(255, 255, 255, 0.6)' }}>
          {error || 'No album data available'}
        </div>
      </div>
    )
  }

  return (
    <div className="relative p-6 rounded-3xl border transition-all duration-300 hover:transform hover:scale-[1.02] hover:-translate-y-2"
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
          Your Top Albums
        </h3>
        <p className="text-sm" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
          Albums you've played the most
        </p>
      </div>

      {/* Content */}
      <div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {topAlbums.albums.map((album, index) => (
            <div
              key={`${album.artist}-${album.album}`}
              className="group relative rounded-2xl p-4 transition-all duration-300 cursor-pointer hover:transform hover:scale-105 hover:-translate-y-3"
              style={{
                background: 'linear-gradient(135deg, rgba(26,26,26,0.9), rgba(18,18,18,0.9))',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)',
                boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
                overflow: 'hidden'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'rgba(29, 185, 84, 0.5)'
                e.currentTarget.style.boxShadow = '0 20px 60px rgba(0,0,0,0.4), 0 0 40px rgba(29, 185, 84, 0.3)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)'
                e.currentTarget.style.boxShadow = '0 8px 32px rgba(0,0,0,0.3)'
              }}
            >
              {/* Rank Badge */}
              <div className="absolute top-3 left-3 z-10">
                <div className="text-xs font-bold px-3 py-1 rounded-full font-mono"
                     style={{
                       background: 'linear-gradient(45deg, #1DB954, #00D4FF)',
                       color: '#000',
                       boxShadow: '0 0 15px rgba(29, 185, 84, 0.5)',
                       border: '1px solid rgba(255, 255, 255, 0.2)'
                     }}>
                  #{index + 1}
                </div>
              </div>
              
              {/* Album Cover */}
              <div className="relative mb-4 overflow-hidden rounded-xl">
                {album.image_url ? (
                  <img
                    src={album.image_url}
                    alt={album.album}
                    className="w-full aspect-square object-cover group-hover:scale-110 transition-transform duration-500"
                    style={{
                      filter: 'brightness(0.9) contrast(1.1)',
                      border: '2px solid rgba(29, 185, 84, 0.3)'
                    }}
                  />
                ) : (
                  <div className="w-full aspect-square flex items-center justify-center rounded-xl"
                       style={{
                         background: 'linear-gradient(135deg, rgba(29, 185, 84, 0.2), rgba(0, 212, 255, 0.1))',
                         border: '2px solid rgba(29, 185, 84, 0.3)'
                       }}>
                    <span className="text-5xl" style={{ color: 'rgba(29, 185, 84, 0.6)' }}>♪</span>
                  </div>
                )}

                {/* Play overlay with enhanced styling */}
                <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-all duration-300 flex items-center justify-center rounded-xl"
                     style={{
                       background: 'linear-gradient(135deg, rgba(0,0,0,0.7), rgba(29,185,84,0.1))'
                     }}>
                  <div className="w-14 h-14 rounded-full flex items-center justify-center transition-transform duration-300 hover:scale-110"
                       style={{
                         background: 'linear-gradient(45deg, #1DB954, #00D4FF)',
                         boxShadow: '0 0 20px rgba(29, 185, 84, 0.6)'
                       }}>
                    <svg className="w-6 h-6 text-black ml-1" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                  </div>
                </div>
              </div>
              
              {/* Album Info */}
              <div className="space-y-2">
                <h4 className="font-bold text-base truncate transition-colors duration-300"
                    style={{
                      color: '#ffffff',
                      textShadow: '0 0 10px rgba(255, 255, 255, 0.3)'
                    }}
                    onMouseEnter={(e) => e.target.style.color = '#1DB954'}
                    onMouseLeave={(e) => e.target.style.color = '#ffffff'}>
                  {album.album}
                </h4>
                <p className="text-sm truncate" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  {album.artist}
                </p>
                <div className="flex items-center justify-between pt-2">
                  <span className="text-xs font-mono" style={{ color: 'rgba(29, 185, 84, 0.8)' }}>
                    {album.total_count} plays
                  </span>
                  <div className="flex items-center space-x-1">
                    {/* Enhanced play count visualization */}
                    {[...Array(Math.min(5, Math.ceil(album.total_count / 10)))].map((_, i) => (
                      <div
                        key={i}
                        className="rounded-full transition-all duration-300"
                        style={{
                          width: '4px',
                          height: `${8 + (i * 3)}px`,
                          background: `linear-gradient(to top, #1DB954, #00D4FF)`,
                          opacity: 0.6 + (i * 0.1),
                          boxShadow: '0 0 5px rgba(29, 185, 84, 0.5)'
                        }}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
        
        {topAlbums.albums.length === 6 && (
          <div className="mt-8 text-center">
            <button
              onClick={fetchTopAlbums}
              className="px-6 py-3 rounded-xl font-medium transition-all duration-300 hover:transform hover:scale-105"
              style={{
                background: 'linear-gradient(45deg, #1DB954, #00D4FF)',
                color: '#000',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                boxShadow: '0 4px 15px rgba(29, 185, 84, 0.3)'
              }}
              onMouseEnter={(e) => {
                e.target.style.boxShadow = '0 8px 25px rgba(29, 185, 84, 0.5)'
              }}
              onMouseLeave={(e) => {
                e.target.style.boxShadow = '0 4px 15px rgba(29, 185, 84, 0.3)'
              }}
            >
              Load more albums
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default TopAlbums
