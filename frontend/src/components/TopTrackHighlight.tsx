import React, { useState, useEffect, useCallback } from 'react'
import { Track, getTrackName } from '../types/spotify'
import { musicApi } from '../api'
import '../spotify-components.css'

const TopTrackHighlight: React.FC = () => {
  const [topTrack, setTopTrack] = useState<Track | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchTopTrack = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await musicApi.getTopTracks(1)
      if (response.tracks && response.tracks.length > 0) {
        setTopTrack(response.tracks[0])
      }
    } catch (err) {
      console.error('Failed to fetch top track:', err)
      setError('Failed to load top track')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchTopTrack()
  }, [fetchTopTrack])

  if (isLoading) {
    return (
      <div className="spotify-card top-track-highlight fade-in">
        <div className="loading-shimmer" style={{ height: '200px', borderRadius: '16px' }}></div>
      </div>
    )
  }

  if (error || !topTrack) {
    return (
      <div className="spotify-card top-track-highlight fade-in">
        <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <i className="fas fa-music" style={{ fontSize: '48px', marginBottom: '20px', color: 'var(--accent-primary)' }}></i>
          <p>{error || 'No top track data available'}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="spotify-card top-track-highlight fade-in highlight-bg-animation">
      <div style={{ padding: '30px', position: 'relative', zIndex: 2 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ flexShrink: 0 }}>
            {topTrack.image_url ? (
              <img
                src={topTrack.image_url}
                alt={topTrack.album}
                style={{
                  width: '100px',
                  height: '100px',
                  borderRadius: '12px',
                  border: '2px solid rgba(29, 185, 84, 0.3)',
                  transition: 'all 0.3s ease'
                }}
              />
            ) : (
              <div style={{
                width: '100px',
                height: '100px',
                borderRadius: '12px',
                background: 'linear-gradient(135deg, rgba(29, 185, 84, 0.2), rgba(0, 212, 255, 0.1))',
                border: '2px solid rgba(29, 185, 84, 0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '40px'
              }}>
                👑
              </div>
            )}
          </div>

          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
              <i className="fas fa-crown" style={{
                fontSize: '20px',
                color: 'var(--accent-primary)',
                marginRight: '10px',
                filter: 'drop-shadow(0 0 10px rgba(29, 185, 84, 0.5))'
              }}></i>
              <span style={{
                fontFamily: "'Orbitron', monospace",
                fontSize: '12px',
                fontWeight: 600,
                color: 'var(--accent-primary)',
                textTransform: 'uppercase',
                letterSpacing: '1px'
              }}>
                #1 TRACK
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
              {getTrackName(topTrack)}
            </h3>

            <p style={{
              fontSize: '16px',
              color: 'var(--text-secondary)',
              margin: '0 0 20px 0'
            }}>
              by {topTrack.artist || 'Unknown Artist'}
            </p>

            <div style={{ display: 'flex', gap: '30px' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{
                  fontSize: '28px',
                  fontWeight: 700,
                  fontFamily: "'Orbitron', monospace",
                  background: 'linear-gradient(45deg, #1DB954, #00D4FF)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  textShadow: '0 0 20px rgba(29, 185, 84, 0.3)'
                }}>
                  {Math.round((topTrack.duration_ms || 0) / 60000)}:{String(Math.round(((topTrack.duration_ms || 0) % 60000) / 1000)).padStart(2, '0')}
                </div>
                <div style={{
                  fontSize: '11px',
                  fontWeight: 600,
                  color: 'var(--text-muted)',
                  textTransform: 'uppercase',
                  letterSpacing: '1px',
                  fontFamily: "'Orbitron', monospace"
                }}>
                  DURATION
                </div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{
                  fontSize: '28px',
                  fontWeight: 700,
                  fontFamily: "'Orbitron', monospace",
                  background: 'linear-gradient(45deg, #00D4FF, #8b5cf6)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  textShadow: '0 0 20px rgba(0, 212, 255, 0.3)'
                }}>
                  {topTrack.popularity || '—'}
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

export default TopTrackHighlight
