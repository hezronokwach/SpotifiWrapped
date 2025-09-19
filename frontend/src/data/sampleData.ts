// Sample data for demo mode
export const sampleUserProfile = {
  id: 'demo_user_123',
  display_name: 'Demo User',
  email: 'demo@spotifiwrapped.com',
  followers: { total: 42 },
  images: [{ url: 'https://picsum.photos/200/200?random=1' }],
  country: 'US',
  product: 'premium'
}

export const sampleTracks = [
  {
    id: 'demo_track_1',
    name: 'Blinding Lights',
    artist: 'The Weeknd',
    album: 'After Hours',
    duration_ms: 200040,
    popularity: 95,
    images: [{ url: 'https://picsum.photos/300/300?random=2' }],
    audio_features: {
      danceability: 0.514,
      energy: 0.730,
      valence: 0.334,
      tempo: 171.005
    }
  },
  {
    id: 'demo_track_2',
    name: 'Watermelon Sugar',
    artist: 'Harry Styles',
    album: 'Fine Line',
    duration_ms: 174000,
    popularity: 92,
    images: [{ url: 'https://picsum.photos/300/300?random=3' }],
    audio_features: {
      danceability: 0.548,
      energy: 0.816,
      valence: 0.557,
      tempo: 95.039
    }
  },
  {
    id: 'demo_track_3',
    name: 'Good 4 U',
    artist: 'Olivia Rodrigo',
    album: 'SOUR',
    duration_ms: 178147,
    popularity: 89,
    images: [{ url: 'https://picsum.photos/300/300?random=4' }],
    audio_features: {
      danceability: 0.563,
      energy: 0.664,
      valence: 0.688,
      tempo: 166.928
    }
  },
  {
    id: 'demo_track_4',
    name: 'Levitating',
    artist: 'Dua Lipa',
    album: 'Future Nostalgia',
    duration_ms: 203064,
    popularity: 88,
    images: [{ url: 'https://picsum.photos/300/300?random=5' }],
    audio_features: {
      danceability: 0.702,
      energy: 0.825,
      valence: 0.915,
      tempo: 103.001
    }
  },
  {
    id: 'demo_track_5',
    name: 'Stay',
    artist: 'The Kid LAROI & Justin Bieber',
    album: 'F*CK LOVE 3: OVER YOU',
    duration_ms: 141806,
    popularity: 87,
    images: [{ url: 'https://picsum.photos/300/300?random=6' }],
    audio_features: {
      danceability: 0.591,
      energy: 0.764,
      valence: 0.478,
      tempo: 169.928
    }
  }
]

export const sampleArtists = [
  {
    id: 'demo_artist_1',
    name: 'The Weeknd',
    genres: ['pop', 'r&b', 'alternative r&b'],
    popularity: 95,
    followers: 29847691,
    images: [{ url: 'https://picsum.photos/300/300?random=7' }]
  },
  {
    id: 'demo_artist_2',
    name: 'Harry Styles',
    genres: ['pop', 'rock', 'indie pop'],
    popularity: 92,
    followers: 18234567,
    images: [{ url: 'https://picsum.photos/300/300?random=8' }]
  },
  {
    id: 'demo_artist_3',
    name: 'Olivia Rodrigo',
    genres: ['pop', 'indie pop', 'pop rock'],
    popularity: 89,
    followers: 12456789,
    images: [{ url: 'https://picsum.photos/300/300?random=9' }]
  },
  {
    id: 'demo_artist_4',
    name: 'Dua Lipa',
    genres: ['pop', 'dance pop', 'electropop'],
    popularity: 88,
    followers: 15678901,
    images: [{ url: 'https://picsum.photos/300/300?random=10' }]
  }
]

export const sampleCurrentTrack = {
  id: 'demo_current_1',
  name: 'As It Was',
  artist: 'Harry Styles',
  album: "Harry's House",
  duration_ms: 167303,
  progress_ms: 45000,
  is_playing: true,
  images: [{ url: 'https://picsum.photos/300/300?random=11' }]
}

export const sampleStats = {
  total_tracks: 1247,
  total_artists: 342,
  total_albums: 156,
  total_playlists: 23,
  listening_time_minutes: 18420
}