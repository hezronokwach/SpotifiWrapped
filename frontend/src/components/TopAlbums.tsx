import React, { useState, useEffect } from 'react'
import api from '../api'
import '../spotify-components.css'
import { useDemoMode } from '../contexts/DemoModeContext'

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
  const { isDemoMode } = useDemoMode()
  const [topAlbums, setTopAlbums] = useState<TopAlbumsResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchTopAlbums()
  }, [isDemoMode])

  const fetchTopAlbums = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      if (isDemoMode) {
        // Use sample albums for demo mode
        const sampleAlbums = {
          albums: [
            {
              album: 'After Hours',
              artist: 'The Weeknd',
              total_count: 45,
              image_url: 'https://picsum.photos/200/200?random=40',
              rank: 1
            },
            {
              album: 'Fine Line',
              artist: 'Harry Styles',
              total_count: 38,
              image_url: 'https://picsum.photos/200/200?random=41',
              rank: 2
            },
            {
              album: 'SOUR',
              artist: 'Olivia Rodrigo',
              total_count: 32,
              image_url: 'https://picsum.photos/200/200?random=42',
              rank: 3
            },
            {
              album: 'Future Nostalgia',
              artist: 'Dua Lipa',
              total_count: 28,
              image_url: 'https://picsum.photos/200/200?random=43',
              rank: 4
            }
          ]
        }
        setTopAlbums(sampleAlbums)
        setIsLoading(false)
        return
      }
      
      const response = await api.get('/music/albums/top?limit=10')
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
      <div className="spotify-card fade-in">
        <div style={{ padding: '30px' }}>
          <div style={{ marginBottom: '20px' }}>
            <h3 style={{
              fontSize: '24px',
              fontWeight: 700,
              fontFamily: "'Orbitron', monospace",
              background: 'linear-gradient(45deg, #1DB954, #00D4FF, #8b5cf6)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              textTransform: 'uppercase',
              letterSpacing: '1.5px',
              margin: '0 0 8px 0'
            }}>
              Your Top Albums
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px', margin: 0 }}>
              Loading your most played albums...
            </p>
          </div>
          <div className="loading-shimmer" style={{ height: '300px', borderRadius: '16px' }}></div>
        </div>
      </div>
    )
  }

  if (error || !topAlbums || topAlbums.albums.length === 0) {
    return (
      <div className="spotify-card fade-in">
        <div style={{ padding: '30px' }}>
          <div style={{ marginBottom: '20px' }}>
            <h3 style={{
              fontSize: '24px',
              fontWeight: 700,
              fontFamily: "'Orbitron', monospace",
              background: 'linear-gradient(45deg, #1DB954, #00D4FF, #8b5cf6)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              textTransform: 'uppercase',
              letterSpacing: '1.5px',
              margin: '0 0 8px 0'
            }}>
              Your Top Albums
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px', margin: 0 }}>
              Your most listened to albums
            </p>
          </div>
          <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-secondary)' }}>
            <i className="fas fa-compact-disc" style={{ fontSize: '48px', marginBottom: '20px', color: 'var(--accent-primary)' }}></i>
            <p style={{ marginBottom: '20px' }}>
              {error ? `Error: ${error}` : 'Start listening to music to see your top albums here!'}
            </p>
            <button 
              onClick={fetchTopAlbums}
              className="spotify-button"
              style={{ fontSize: '14px', padding: '10px 20px' }}
            >
              Refresh
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="spotify-card fade-in">
      <div style={{ padding: '30px' }}>
        <div style={{ marginBottom: '30px' }}>
          <h3 style={{
            fontSize: '24px',
            fontWeight: 700,
            fontFamily: "'Orbitron', monospace",
            background: 'linear-gradient(45deg, #1DB954, #00D4FF, #8b5cf6)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            textTransform: 'uppercase',
            letterSpacing: '1.5px',
            margin: '0 0 8px 0',
            textShadow: '0 0 20px rgba(29, 185, 84, 0.3)'
          }}>
            Your Top Albums
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px', margin: 0 }}>
            Albums you've played the most
          </p>
        </div>

        <div className="top-albums-container">
          {topAlbums.albums.map((album, index) => (
            <div key={`${album.artist}-${album.album}`} className="album-card">
              <div className="album-rank">#{index + 1}</div>
              
              <div className="album-image">
                {album.image_url ? (
                  <img src={album.image_url} alt={album.album} />
                ) : (
                  <div style={{
                    width: '100%',
                    height: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: 'linear-gradient(135deg, rgba(29, 185, 84, 0.2), rgba(0, 212, 255, 0.1))',
                    fontSize: '30px',
                    color: 'rgba(29, 185, 84, 0.6)'
                  }}>
                    ♪
                  </div>
                )}
              </div>
              
              <div className="album-info">
                <h4>{album.album}</h4>
                <p>{album.artist}</p>
                <div className="album-score">{album.total_count} plays</div>
              </div>
            </div>
          ))}
        </div>
        

      </div>
    </div>
  )
}

export default TopAlbums
