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

  // Debug logging to identify the data structure issue
  useEffect(() => {
    if (topArtist) {
      console.log('🔍 Artist data structure:', topArtist);
      console.log('🔍 Available fields:', Object.keys(topArtist));
      console.log('🔍 Artist field value:', topArtist.artist);
      console.log('🔍 Name field value:', topArtist.name);
    }
  }, [topArtist])



  if (isLoading) {
    return (
      <div className="top-artist-card">
        <div className="spotify-loading">
          <div className="spotify-spinner"></div>
        </div>
      </div>
    )
  }

  if (error || !topArtist) {
    return (
      <div className="top-artist-card">
        <div className="spotify-error">
          {error || 'No top artist data available'}
        </div>
      </div>
    )
  }

  return (
    <div className="top-artist-card">

      <div className="content-layer flex items-center space-x-5">
        <div className="flex-shrink-0">
          {topArtist.image_url ? (
            <img
              src={topArtist.image_url}
              alt={getArtistName(topArtist)}
              className="artist-image"
            />
          ) : (
            <div className="artist-image flex items-center justify-center bg-gradient-to-br from-purple-500/20 to-pink-400/20">
              <span className="text-4xl">⭐</span>
            </div>
          )}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center mb-2">
            <span className="artist-rank-badge">⭐</span>
            <span className="artist-rank-text">#1 ARTIST</span>
          </div>

          <h3 className="spotify-title">
            {getArtistName(topArtist)}
          </h3>

          <p className="artist-subtitle">
            Your most listened artist
          </p>

          <div className="flex items-center space-x-6">
            <div className="text-center">
              <div className="stat-number text-purple-500">#1</div>
              <div className="stat-label">RANK</div>
            </div>
            <div className="text-center">
              <div className="stat-number text-pink-400">{topArtist.popularity}</div>
              <div className="stat-label">POPULARITY</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TopArtistHighlight
