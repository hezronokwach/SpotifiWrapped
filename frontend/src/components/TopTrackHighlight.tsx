import React, { useState, useEffect, useCallback } from 'react'
import axios from 'axios'
import { Track, getTrackName } from '../types/spotify'

const TopTrackHighlight: React.FC = () => {
  const [topTrack, setTopTrack] = useState<Track | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchTopTrack = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await axios.get('/api/music/tracks/top?limit=1')
      if (response.data.tracks && response.data.tracks.length > 0) {
        setTopTrack(response.data.tracks[0])
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
      <div className="relative p-6 bg-gradient-to-br from-gray-900/90 to-gray-800/90 rounded-3xl border-2 border-transparent bg-gradient-to-r from-spotify-green via-cyan-400 to-purple-500 bg-clip-border">
        <div className="absolute inset-0 bg-gradient-to-br from-spotify-green/10 via-cyan-400/10 to-purple-500/10 rounded-3xl opacity-70"></div>
        <div className="relative z-10 flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-spotify-green"></div>
        </div>
      </div>
    )
  }

  if (error || !topTrack) {
    return (
      <div className="relative p-6 bg-gradient-to-br from-gray-900/90 to-gray-800/90 rounded-3xl border-2 border-transparent bg-gradient-to-r from-spotify-green via-cyan-400 to-purple-500 bg-clip-border">
        <div className="absolute inset-0 bg-gradient-to-br from-spotify-green/10 via-cyan-400/10 to-purple-500/10 rounded-3xl opacity-70"></div>
        <div className="relative z-10 text-center text-spotify-light-gray py-8">
          {error || 'No top track data available'}
        </div>
      </div>
    )
  }

  return (
    <div className="relative p-6 rounded-3xl border-2 border-transparent shadow-2xl hover:shadow-spotify-green/20 transition-all duration-300"
         style={{
           backgroundImage: 'linear-gradient(135deg, rgba(26,26,26,0.9), rgba(18,18,18,0.9)), linear-gradient(45deg, #1DB954, #00D4FF, #8B5CF6)',
           backgroundOrigin: 'border-box',
           backgroundClip: 'padding-box, border-box',
           boxShadow: '0 10px 40px rgba(0,0,0,0.3), 0 0 30px rgba(29,185,84,0.2)'
         }}>

      {/* Animated background */}
      <div className="absolute inset-0 bg-gradient-to-br from-spotify-green/10 via-cyan-400/10 to-purple-500/10 rounded-3xl opacity-70"></div>

      {/* Content */}
      <div className="relative z-10 flex items-center space-x-5">
        {/* Track Image */}
        <div className="flex-shrink-0">
          {topTrack.image_url ? (
            <img
              src={topTrack.image_url}
              alt={topTrack.album}
              className="w-24 h-24 rounded-2xl object-cover border-3 border-transparent shadow-2xl"
              style={{
                background: 'linear-gradient(45deg, #1DB954, #00D4FF, #8B5CF6) border-box',
                backgroundClip: 'padding-box, border-box',
                boxShadow: '0 0 30px rgba(29, 185, 84, 0.6), inset 0 0 20px rgba(255, 255, 255, 0.1)'
              }}
            />
          ) : (
            <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-spotify-green/20 to-cyan-400/20 flex items-center justify-center border-3 border-spotify-green/50">
              <span className="text-4xl">👑</span>
            </div>
          )}
        </div>

        {/* Track Info */}
        <div className="flex-1 min-w-0">
          {/* Crown and Title */}
          <div className="flex items-center mb-2">
            <span className="text-yellow-400 text-lg mr-2 filter drop-shadow-lg">👑</span>
            <span className="text-yellow-400 text-xs font-bold tracking-wider font-mono">#1 TRACK</span>
          </div>

          <h3 className="text-white font-bold text-xl mb-1 leading-tight" style={{ textShadow: '0 0 10px rgba(255, 255, 255, 0.3)' }}>
            {getTrackName(topTrack)}
          </h3>

          <p className="text-transparent bg-gradient-to-r from-spotify-green to-cyan-400 bg-clip-text font-semibold text-sm mb-3">
            by {topTrack.artist || 'Unknown Artist'}
          </p>

          {/* Stats */}
          <div className="flex items-center space-x-6">
            <div className="text-center">
              <div className="text-xl font-bold text-spotify-green font-mono">#1</div>
              <div className="text-xs text-white/70 tracking-wide">RANK</div>
            </div>
            <div className="text-center">
              <div className="text-xl font-bold text-cyan-400 font-mono">{topTrack.popularity}</div>
              <div className="text-xs text-white/70 tracking-wide">POPULARITY</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TopTrackHighlight
