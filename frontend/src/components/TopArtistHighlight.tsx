import React, { useState, useEffect, useCallback } from 'react'
import axios from 'axios'
import { Artist, getArtistName } from '../types/spotify'

const TopArtistHighlight: React.FC = () => {
  const [topArtist, setTopArtist] = useState<Artist | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchTopArtist = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await axios.get('/api/music/artists/top?limit=1')
      if (response.data.artists && response.data.artists.length > 0) {
        setTopArtist(response.data.artists[0])
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
      <div className="relative p-6 bg-gradient-to-br from-gray-900/90 to-gray-800/90 rounded-3xl border-2 border-transparent bg-gradient-to-r from-purple-500 via-pink-400 to-spotify-green bg-clip-border">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 via-pink-400/10 to-spotify-green/10 rounded-3xl opacity-70"></div>
        <div className="relative z-10 flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
        </div>
      </div>
    )
  }

  if (error || !topArtist) {
    return (
      <div className="relative p-6 bg-gradient-to-br from-gray-900/90 to-gray-800/90 rounded-3xl border-2 border-transparent bg-gradient-to-r from-purple-500 via-pink-400 to-spotify-green bg-clip-border">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 via-pink-400/10 to-spotify-green/10 rounded-3xl opacity-70"></div>
        <div className="relative z-10 text-center text-spotify-light-gray py-8">
          {error || 'No top artist data available'}
        </div>
      </div>
    )
  }

  return (
    <div className="relative p-6 rounded-3xl border-2 border-transparent shadow-2xl hover:shadow-purple-500/20 transition-all duration-300"
         style={{
           backgroundImage: 'linear-gradient(135deg, rgba(26,26,26,0.9), rgba(18,18,18,0.9)), linear-gradient(45deg, #8B5CF6, #F472B6, #1DB954)',
           backgroundOrigin: 'border-box',
           backgroundClip: 'padding-box, border-box',
           boxShadow: '0 10px 40px rgba(0,0,0,0.3), 0 0 30px rgba(139,92,246,0.2)'
         }}>

      {/* Animated background */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 via-pink-400/10 to-spotify-green/10 rounded-3xl opacity-70"></div>

      {/* Content */}
      <div className="relative z-10 flex items-center space-x-5">
        {/* Artist Image */}
        <div className="flex-shrink-0">
          {topArtist.image_url ? (
            <img
              src={topArtist.image_url}
              alt={getArtistName(topArtist)}
              className="w-24 h-24 rounded-full object-cover border-3 border-transparent shadow-2xl"
              style={{
                background: 'linear-gradient(45deg, #8B5CF6, #F472B6, #1DB954) border-box',
                backgroundClip: 'padding-box, border-box',
                boxShadow: '0 0 30px rgba(139, 92, 246, 0.6), inset 0 0 20px rgba(255, 255, 255, 0.1)'
              }}
            />
          ) : (
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-purple-500/20 to-pink-400/20 flex items-center justify-center border-3 border-purple-500/50">
              <span className="text-4xl">⭐</span>
            </div>
          )}
        </div>

        {/* Artist Info */}
        <div className="flex-1 min-w-0">
          {/* Star and Title */}
          <div className="flex items-center mb-2">
            <span className="text-pink-400 text-lg mr-2 filter drop-shadow-lg">⭐</span>
            <span className="text-pink-400 text-xs font-bold tracking-wider font-mono">#1 ARTIST</span>
          </div>

          <h3 className="text-white font-bold text-xl mb-1 leading-tight" style={{ textShadow: '0 0 10px rgba(255, 255, 255, 0.3)' }}>
            {getArtistName(topArtist)}
          </h3>

          <p className="text-transparent bg-gradient-to-r from-purple-500 to-pink-400 bg-clip-text font-semibold text-sm mb-3">
            Your most listened artist
          </p>

          {/* Stats */}
          <div className="flex items-center space-x-6">
            <div className="text-center">
              <div className="text-xl font-bold text-purple-500 font-mono">#1</div>
              <div className="text-xs text-white/70 tracking-wide">RANK</div>
            </div>
            <div className="text-center">
              <div className="text-xl font-bold text-pink-400 font-mono">{topArtist.popularity}</div>
              <div className="text-xs text-white/70 tracking-wide">POPULARITY</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TopArtistHighlight
