import React, { useState, useEffect } from 'react'
import api from '../api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'

interface WrappedTrack {
  name: string
  artist: string
  play_count: string
}

interface WrappedArtist {
  name: string
  genres: string[]
  play_count: string
}

interface ListeningStats {
  total_minutes_listened: number
  total_tracks_played: number
  unique_artists_discovered: number
  unique_albums_explored: number
}

interface WrappedData {
  listening_stats: ListeningStats
  top_tracks: WrappedTrack[]
  top_artists: WrappedArtist[]
}

interface WrappedResponse {
  wrapped: WrappedData
}

const WrappedSummary: React.FC = () => {
  const [wrappedData, setWrappedData] = useState<WrappedResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchWrappedData()
  }, [])

  const fetchWrappedData = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await api.get('/analytics/wrapped')
      setWrappedData(response.data)
    } catch (err) {
      console.error('Failed to fetch wrapped data:', err)
      setError('Failed to load wrapped summary')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <Card className="bg-gradient-to-br from-spotify-green/20 to-purple-600/20 border-spotify-green/30">
        <CardHeader>
          <CardTitle className="text-spotify-white text-xl">🎵 Your Spotify Wrapped</CardTitle>
          <CardDescription className="text-spotify-light-gray">
            Generating your personalized music summary...
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

  if (error || !wrappedData) {
    return (
      <Card className="bg-gradient-to-br from-spotify-green/20 to-purple-600/20 border-spotify-green/30">
        <CardHeader>
          <CardTitle className="text-spotify-white text-xl">🎵 Your Spotify Wrapped</CardTitle>
          <CardDescription className="text-spotify-light-gray">
            Your personalized music year in review
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center text-spotify-light-gray py-8">
            {error || 'No wrapped data available'}
          </div>
        </CardContent>
      </Card>
    )
  }

  const { listening_stats, top_tracks, top_artists } = wrappedData.wrapped

  const formatMinutes = (minutes: number) => {
    if (minutes < 60) return `${Math.round(minutes)} min`
    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours} hr`
    const days = Math.floor(hours / 24)
    return `${days} days`
  }

  return (
    <Card className="bg-gradient-to-br from-spotify-green/20 to-purple-600/20 border-spotify-green/30">
      <CardHeader>
        <CardTitle className="text-spotify-white text-xl flex items-center space-x-2">
          <span>🎵</span>
          <span>Your Spotify Wrapped</span>
        </CardTitle>
        <CardDescription className="text-spotify-light-gray">
          Your personalized music year in review
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Listening Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-black/20 rounded-lg">
            <div className="text-2xl font-bold text-spotify-green">
              {formatMinutes(listening_stats.total_minutes_listened)}
            </div>
            <div className="text-xs text-spotify-light-gray">Listening Time</div>
          </div>
          
          <div className="text-center p-4 bg-black/20 rounded-lg">
            <div className="text-2xl font-bold text-purple-400">
              {listening_stats.total_tracks_played.toLocaleString()}
            </div>
            <div className="text-xs text-spotify-light-gray">Tracks Played</div>
          </div>
          
          <div className="text-center p-4 bg-black/20 rounded-lg">
            <div className="text-2xl font-bold text-blue-400">
              {listening_stats.unique_artists_discovered}
            </div>
            <div className="text-xs text-spotify-light-gray">Artists</div>
          </div>
          
          <div className="text-center p-4 bg-black/20 rounded-lg">
            <div className="text-2xl font-bold text-pink-400">
              {listening_stats.unique_albums_explored}
            </div>
            <div className="text-xs text-spotify-light-gray">Albums</div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top Tracks */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-spotify-white flex items-center space-x-2">
              <span>🎵</span>
              <span>Top Tracks</span>
            </h3>
            <div className="space-y-2">
              {top_tracks.slice(0, 5).map((track, index) => (
                <div key={`${track.name}-${track.artist}`} className="flex items-center space-x-3 p-2 bg-black/20 rounded-lg">
                  <div className="w-8 h-8 bg-spotify-green rounded-full flex items-center justify-center text-black font-bold text-sm">
                    {index + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-spotify-white font-medium truncate text-sm">
                      {track.name}
                    </p>
                    <p className="text-spotify-light-gray text-xs truncate">
                      {track.artist}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Top Artists */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-spotify-white flex items-center space-x-2">
              <span>🎤</span>
              <span>Top Artists</span>
            </h3>
            <div className="space-y-2">
              {top_artists.slice(0, 5).map((artist, index) => (
                <div key={artist.name} className="flex items-center space-x-3 p-2 bg-black/20 rounded-lg">
                  <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                    {index + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-spotify-white font-medium truncate text-sm">
                      {artist.name}
                    </p>
                    <p className="text-spotify-light-gray text-xs truncate">
                      {artist.genres.slice(0, 2).join(', ')}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Fun Facts */}
        <div className="bg-black/20 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-spotify-white mb-3 flex items-center space-x-2">
            <span>✨</span>
            <span>Fun Facts</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="text-spotify-light-gray">
              <span className="text-spotify-green">🎧</span> You've listened to enough music to soundtrack {Math.round(listening_stats.total_minutes_listened / 120)} movies!
            </div>
            <div className="text-spotify-light-gray">
              <span className="text-purple-400">🎨</span> You discovered {listening_stats.unique_artists_discovered} different artists this year.
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default WrappedSummary
