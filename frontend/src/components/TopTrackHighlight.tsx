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
      <div className="top-track-card">
        <div className="spotify-loading">
          <div className="spotify-spinner"></div>
        </div>
      </div>
    )
  }

  if (error || !topTrack) {
    return (
      <div className="top-track-card">
        <div className="spotify-error">
          {error || 'No top track data available'}
        </div>
      </div>
    )
  }

  return (
    <div className="top-track-card">

      <div className="content-layer flex items-center space-x-5">
        <div className="flex-shrink-0">
          {topTrack.image_url ? (
            <img
              src={topTrack.image_url}
              alt={topTrack.album}
              className="track-image"
            />
          ) : (
            <div className="track-image flex items-center justify-center bg-gradient-to-br from-spotify-green/20 to-cyan-400/20">
              <span className="text-4xl">👑</span>
            </div>
          )}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center mb-2">
            <span className="rank-badge">👑</span>
            <span className="rank-text">#1 TRACK</span>
          </div>

          <h3 className="spotify-title">
            {getTrackName(topTrack)}
          </h3>

          <p className="spotify-subtitle">
            by {topTrack.artist || 'Unknown Artist'}
          </p>

          <div className="flex items-center space-x-6">
            <div className="text-center">
              <div className="stat-number text-spotify-green">#1</div>
              <div className="stat-label">RANK</div>
            </div>
            <div className="text-center">
              <div className="stat-number text-cyan-400">{topTrack.popularity}</div>
              <div className="stat-label">POPULARITY</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TopTrackHighlight
