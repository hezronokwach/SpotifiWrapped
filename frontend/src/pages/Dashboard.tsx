import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { formatNumber, formatDuration } from '../lib/utils'
import AudioFeatures from '../components/AudioFeatures'
import GenreChart from '../components/GenreChart'
import SavedTracks from '../components/SavedTracks'
import Playlists from '../components/Playlists'
import TopAlbums from '../components/TopAlbums'
import WrappedSummary from '../components/WrappedSummary'
import ListeningPatterns from '../components/ListeningPatterns'
import UserProfile from '../components/UserProfile'
import TopTrackHighlight from '../components/TopTrackHighlight'
import TopArtistHighlight from '../components/TopArtistHighlight'

interface UserStats {
  total_tracks: number
  total_artists: number
  total_albums: number
  total_playlists: number
  listening_time_minutes: number
}

interface Track {
  id: string
  name: string
  artist: string
  album: string
  popularity: number
  duration_ms: number
  images: Array<{ url: string }>
}

interface Artist {
  id: string
  name: string
  genres: string[]
  popularity: number
  followers: number
  images: Array<{ url: string }>
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<UserStats | null>(null)
  const [topTracks, setTopTracks] = useState<Track[]>([])
  const [topArtists, setTopArtists] = useState<Artist[]>([])
  const [currentTrack, setCurrentTrack] = useState<Track | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true)

      // First test the JWT token
      console.log('🔍 Dashboard: Testing JWT token...')
      const testRes = await axios.get('/api/music/test')
      console.log('🔍 Dashboard: JWT test result:', testRes.data)

      // Fetch all dashboard data in parallel
      const [statsRes, tracksRes, artistsRes, currentRes] = await Promise.all([
        axios.get('/api/user/stats'),
        axios.get('/api/music/tracks/top?limit=10'),
        axios.get('/api/music/artists/top?limit=10'),
        axios.get('/api/music/tracks/current')
      ])

      setStats(statsRes.data)
      setTopTracks(tracksRes.data.tracks)
      setTopArtists(artistsRes.data.artists)
      setCurrentTrack(currentRes.data.currently_playing)
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-spotify-green mx-auto mb-4"></div>
          <p className="text-spotify-white">Loading your music data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* User Profile Header - matches original Dash layout */}
      <UserProfile />

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="bg-spotify-dark-gray border-spotify-gray">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-spotify-light-gray">
                Total Tracks
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-spotify-white">
                {formatNumber(stats.total_tracks)}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-spotify-dark-gray border-spotify-gray">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-spotify-light-gray">
                Unique Artists
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-spotify-white">
                {formatNumber(stats.total_artists)}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-spotify-dark-gray border-spotify-gray">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-spotify-light-gray">
                Albums Explored
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-spotify-white">
                {formatNumber(stats.total_albums)}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-spotify-dark-gray border-spotify-gray">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-spotify-light-gray">
                Listening Time
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-spotify-white">
                {Math.round(stats.listening_time_minutes / 60)}h
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Currently Playing */}
      {currentTrack && (
        <Card className="bg-spotify-dark-gray border-spotify-gray">
          <CardHeader>
            <CardTitle className="text-spotify-white">Currently Playing</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-4">
              {currentTrack.images && currentTrack.images.length > 0 && (
                <img
                  src={currentTrack.images[0].url}
                  alt={currentTrack.album}
                  className="w-16 h-16 rounded-md"
                />
              )}
              <div className="flex-1">
                <h3 className="font-semibold text-spotify-white">{currentTrack.name}</h3>
                <p className="text-spotify-light-gray">{currentTrack.artist}</p>
                <p className="text-sm text-spotify-light-gray">{currentTrack.album}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Top Highlights Row - matches original Dash layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TopTrackHighlight />
        <TopArtistHighlight />
      </div>

      {/* Top Content Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Tracks */}
        <Card className="bg-spotify-dark-gray border-spotify-gray">
          <CardHeader>
            <CardTitle className="text-spotify-white">Your Top Tracks</CardTitle>
            <CardDescription className="text-spotify-light-gray">
              Most played songs recently
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {topTracks.slice(0, 5).map((track, index) => (
                <div key={track.id} className="flex items-center space-x-3">
                  <span className="text-spotify-light-gray font-mono text-sm w-6">
                    {index + 1}
                  </span>
                  {track.images && track.images.length > 0 && (
                    <img
                      src={track.images[0].url}
                      alt={track.album}
                      className="w-10 h-10 rounded"
                    />
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="text-spotify-white font-medium truncate">
                      {track.name}
                    </p>
                    <p className="text-spotify-light-gray text-sm truncate">
                      {track.artist}
                    </p>
                  </div>
                  <span className="text-spotify-light-gray text-sm">
                    {formatDuration(track.duration_ms)}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Top Artists */}
        <Card className="bg-spotify-dark-gray border-spotify-gray">
          <CardHeader>
            <CardTitle className="text-spotify-white">Your Top Artists</CardTitle>
            <CardDescription className="text-spotify-light-gray">
              Most listened to artists
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {topArtists.slice(0, 5).map((artist, index) => (
                <div key={artist.id} className="flex items-center space-x-3">
                  <span className="text-spotify-light-gray font-mono text-sm w-6">
                    {index + 1}
                  </span>
                  {artist.images && artist.images.length > 0 && (
                    <img
                      src={artist.images[0].url}
                      alt={artist.name}
                      className="w-10 h-10 rounded-full"
                    />
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="text-spotify-white font-medium truncate">
                      {artist.name}
                    </p>
                    <p className="text-spotify-light-gray text-sm truncate">
                      {artist.genres.slice(0, 2).join(', ')}
                    </p>
                  </div>
                  <span className="text-spotify-light-gray text-sm">
                    {formatNumber(artist.followers)} followers
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top Albums Section */}
      <TopAlbums />

      {/* Wrapped Summary Section */}
      <WrappedSummary />

      {/* Audio Analysis Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AudioFeatures />
        <GenreChart />
      </div>

      {/* Listening Patterns Row */}
      <ListeningPatterns />

      {/* Library Content Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SavedTracks />
        <Playlists />
      </div>

      {/* Refresh Button */}
      <div className="text-center">
        <Button
          onClick={fetchDashboardData}
          variant="spotify"
          disabled={isLoading}
        >
          {isLoading ? 'Refreshing...' : 'Refresh Data'}
        </Button>
      </div>
    </div>
  )
}

export default Dashboard
