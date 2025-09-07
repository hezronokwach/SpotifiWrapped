import React, { useState, useEffect, useCallback } from 'react'
import { Artist, getArtistName } from '../types/spotify'
import { musicApi } from '../api'
import '../spotify-components.css'

const TopArtistHighlight: React.FC = () => {
  const [topArtist, setTopArtist] = useState<Artist | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchTopArtist = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await musicApi.getTopArtists(1)
      if (response.artists && response.artists.length > 0) {
        setTopArtist(response.artists[0])
      }
    } catch (err) {
      console.error('Failed to fetch top artist:', err)
      setError('Failed to load top artist')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchTopArtist()
  }, [fetchTopArtist])

  if (isLoading) {
    return (
      <div className="spotify-card top-artist-highlight fade-in">
        <div className="loading-shimmer" style={{ height: '200px', borderRadius: '16px' }}></div>
      </div>
    )
  }

  if (error || !topArtist) {
    return (
      <div className="spotify-card top-artist-highlight fade-in">
        <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <i className="fas fa-microphone" style={{ fontSize: '48px', marginBottom: '20px', color: 'var(--accent-purple)' }}></i>
          <p>{error || 'No top artist data available'}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="spotify-card top-artist-highlight fade-in highlight-bg-animation">
      <div style={{ padding: '30px', position: 'relative', zIndex: 2 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ flexShrink: 0 }}>
            {topArtist.image_url ? (
              <img
                src={topArtist.image_url}
                alt={getArtistName(topArtist)}
                style={{
                  width: '100px',
                  height: '100px',
                  borderRadius: '50%',
                  border: '2px solid rgba(139, 92, 246, 0.3)',
                  transition: 'all 0.3s ease'
                }}
              />
            ) : (
              <div style={{
                width: '100px',
                height: '100px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(244, 114, 182, 0.1))',
                border: '2px solid rgba(139, 92, 246, 0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '40px'
              }}>
                ⭐
              </div>
            )}
          </div>

          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
              <i className="fas fa-star" style={{
                fontSize: '20px',
                color: 'var(--accent-purple)',
                marginRight: '10px',
                filter: 'drop-shadow(0 0 10px rgba(139, 92, 246, 0.5))'
              }}></i>
              <span style={{
                fontFamily: "'Orbitron', monospace",
                fontSize: '12px',
                fontWeight: 600,
                color: 'var(--accent-purple)',
                textTransform: 'uppercase',
                letterSpacing: '1px'
              }}>
                #1 ARTIST
              </span>
            </div>

            <h3 style={{
              fontSize: '24px',
              fontWeight: 700,
              color: 'var(--text-primary)',
              margin: '0 0 8px 0',
              lineHeight: 1.2,
              textShadow: '0 0 20px rgba(255, 255, 255, 0.1)'
            }}>
              {getArtistName(topArtist)}
            </h3>

            <p style={{
              fontSize: '16px',
              color: 'var(--text-secondary)',
              margin: '0 0 20px 0'
            }}>
              Your most listened artist
            </p>

            <div style={{ display: 'flex', gap: '30px' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{
                  fontSize: '28px',
                  fontWeight: 700,
                  fontFamily: "'Orbitron', monospace",
                  background: 'linear-gradient(45deg, #8b5cf6, #f472b6)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  textShadow: '0 0 20px rgba(139, 92, 246, 0.3)'
                }}>
                  #1
                </div>
                <div style={{
                  fontSize: '11px',
                  fontWeight: 600,
                  color: 'var(--text-muted)',
                  textTransform: 'uppercase',
                  letterSpacing: '1px',
                  fontFamily: "'Orbitron', monospace"
                }}>
                  RANK
                </div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{
                  fontSize: '28px',
                  fontWeight: 700,
                  fontFamily: "'Orbitron', monospace",
                  background: 'linear-gradient(45deg, #f472b6, #a855f7)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  textShadow: '0 0 20px rgba(244, 114, 182, 0.3)'
                }}>
                  {topArtist.popularity || '—'}
                </div>
                <div style={{
                  fontSize: '11px',
                  fontWeight: 600,
                  color: 'var(--text-muted)',
                  textTransform: 'uppercase',
                  letterSpacing: '1px',
                  fontFamily: "'Orbitron', monospace"
                }}>
                  POPULARITY
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TopArtistHighlight
