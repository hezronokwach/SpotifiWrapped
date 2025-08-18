import React, { useState, useEffect } from 'react'
import axios from 'axios'
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js'
import { Radar } from 'react-chartjs-2'


ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
)

interface AudioFeatures {
  danceability: number
  energy: number
  speechiness: number
  acousticness: number
  instrumentalness: number
  liveness: number
  valence: number
  tempo: number
}

interface TrackInfo {
  track: string
  artist: string
}

interface AudioFeaturesData {
  audio_features: AudioFeatures
  tracks: TrackInfo[]
  tracks_analyzed: number
}

const AudioFeatures: React.FC = () => {
  const [audioFeatures, setAudioFeatures] = useState<AudioFeaturesData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchAudioFeatures()
  }, [])

  const fetchAudioFeatures = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await axios.get('/api/analytics/audio-features')
      setAudioFeatures(response.data)
    } catch (err) {
      console.error('Failed to fetch audio features:', err)
      setError('Failed to load audio features')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="relative p-6 rounded-3xl border transition-all duration-300 hover:transform hover:scale-[1.01] hover:-translate-y-1"
           style={{
             background: 'linear-gradient(135deg, rgba(26,26,26,0.95), rgba(18,18,18,0.95))',
             border: '1px solid rgba(29, 185, 84, 0.3)',
             boxShadow: '0 8px 32px rgba(0,0,0,0.3), 0 0 40px rgba(29, 185, 84, 0.1)',
             backdropFilter: 'blur(10px)'
           }}>
        <div className="absolute inset-0 rounded-3xl opacity-0 hover:opacity-100 transition-opacity duration-300"
             style={{
               background: 'linear-gradient(45deg, rgba(29, 185, 84, 0.3), rgba(0, 212, 255, 0.3), rgba(139, 92, 246, 0.3), rgba(29, 185, 84, 0.3))',
               backgroundSize: '400% 400%',
               animation: 'gradientShift 8s ease infinite',
               zIndex: -1
             }}>
        </div>
        <div className="mb-6">
          <h3 className="text-2xl font-bold mb-2 font-orbitron"
              style={{
                background: 'linear-gradient(45deg, #1DB954, #00D4FF, #8b5cf6)',
                backgroundSize: '200% 200%',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                textTransform: 'uppercase',
                letterSpacing: '1.5px',
                textShadow: '0 0 20px rgba(29, 185, 84, 0.3)'
              }}>
            Audio Features
          </h3>
          <p className="text-sm" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
            Analyzing your music preferences...
          </p>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-spotify-green"></div>
        </div>
      </div>
    )
  }

  if (error || !audioFeatures) {
    return (
      <div className="relative p-6 rounded-3xl border transition-all duration-300 hover:transform hover:scale-[1.01] hover:-translate-y-1"
           style={{
             background: 'linear-gradient(135deg, rgba(26,26,26,0.95), rgba(18,18,18,0.95))',
             border: '1px solid rgba(29, 185, 84, 0.3)',
             boxShadow: '0 8px 32px rgba(0,0,0,0.3), 0 0 40px rgba(29, 185, 84, 0.1)',
             backdropFilter: 'blur(10px)'
           }}>
        <div className="absolute inset-0 rounded-3xl opacity-0 hover:opacity-100 transition-opacity duration-300"
             style={{
               background: 'linear-gradient(45deg, rgba(29, 185, 84, 0.3), rgba(0, 212, 255, 0.3), rgba(139, 92, 246, 0.3), rgba(29, 185, 84, 0.3))',
               backgroundSize: '400% 400%',
               animation: 'gradientShift 8s ease infinite',
               zIndex: -1
             }}>
        </div>
        <div className="mb-6">
          <h3 className="text-2xl font-bold mb-2 font-orbitron"
              style={{
                background: 'linear-gradient(45deg, #1DB954, #00D4FF, #8b5cf6)',
                backgroundSize: '200% 200%',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                textTransform: 'uppercase',
                letterSpacing: '1.5px',
                textShadow: '0 0 20px rgba(29, 185, 84, 0.3)'
              }}>
            Audio Features
          </h3>
          <p className="text-sm" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
            Analysis of your music characteristics
          </p>
        </div>
        <div className="text-center py-8" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
          {error || 'No audio features data available'}
        </div>
      </div>
    )
  }

  const features = audioFeatures.audio_features

  const data = {
    labels: [
      'Danceability',
      'Energy',
      'Valence',
      'Acousticness',
      'Instrumentalness',
      'Liveness',
      'Speechiness'
    ],
    datasets: [
      {
        label: 'Your Music Profile',
        data: [
          features.danceability,
          features.energy,
          features.valence,
          features.acousticness,
          features.instrumentalness,
          features.liveness,
          features.speechiness
        ],
        backgroundColor: 'rgba(29, 185, 84, 0.2)',
        borderColor: '#1DB954',
        borderWidth: 2,
        pointBackgroundColor: '#1DB954',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#1DB954',
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: '#282828',
        titleColor: '#ffffff',
        bodyColor: '#b3b3b3',
        borderColor: '#1DB954',
        borderWidth: 1,
        callbacks: {
          label: function(context: { label: string; parsed: { r: number } }) {
            return `${context.label}: ${(context.parsed.r * 100).toFixed(1)}%`
          }
        }
      },
    },
    scales: {
      r: {
        beginAtZero: true,
        max: 1,
        ticks: {
          display: false,
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        angleLines: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        pointLabels: {
          color: '#b3b3b3',
          font: {
            size: 12,
          },
        },
      },
    },
  }

  return (
    <div className="relative p-6 rounded-3xl border transition-all duration-300 hover:transform hover:scale-[1.01] hover:-translate-y-1"
         style={{
           background: 'linear-gradient(135deg, rgba(26,26,26,0.95), rgba(18,18,18,0.95))',
           border: '1px solid rgba(29, 185, 84, 0.3)',
           boxShadow: '0 8px 32px rgba(0,0,0,0.3), 0 0 40px rgba(29, 185, 84, 0.1)',
           backdropFilter: 'blur(10px)'
         }}>
      
      {/* Animated border gradient */}
      <div className="absolute inset-0 rounded-3xl opacity-0 hover:opacity-100 transition-opacity duration-300"
           style={{
             background: 'linear-gradient(45deg, rgba(29, 185, 84, 0.3), rgba(0, 212, 255, 0.3), rgba(139, 92, 246, 0.3), rgba(29, 185, 84, 0.3))',
             backgroundSize: '400% 400%',
             animation: 'gradientShift 8s ease infinite',
             zIndex: -1
           }}>
      </div>

      {/* Header */}
      <div className="mb-6">
        <h3 className="text-2xl font-bold mb-2 font-orbitron"
            style={{
              background: 'linear-gradient(45deg, #1DB954, #00D4FF, #8b5cf6)',
              backgroundSize: '200% 200%',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              textTransform: 'uppercase',
              letterSpacing: '1.5px',
              textShadow: '0 0 20px rgba(29, 185, 84, 0.3)'
            }}>
          Audio Features
        </h3>
        <p className="text-sm" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
          Analysis of {audioFeatures.tracks_analyzed} tracks
        </p>
      </div>

      {/* Content */}
      <div className="space-y-6">
        <div className="h-64">
          <Radar data={data} options={options} />
        </div>

        {/* Tracks analyzed */}
        {audioFeatures.tracks && audioFeatures.tracks.length > 0 && (
          <div className="space-y-3">
            <h3 className="text-sm font-medium font-orbitron" style={{ color: 'rgba(255, 255, 255, 0.9)' }}>Tracks Analyzed</h3>
            <div className="space-y-2">
              {audioFeatures.tracks.map((track, index) => (
                <div key={`${track.track}-${track.artist}`} 
                     className="flex items-center space-x-3 p-2 rounded-lg transition-all duration-300 hover:transform hover:scale-[1.02]"
                     style={{
                       background: 'linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02))',
                       border: '1px solid rgba(255, 255, 255, 0.1)',
                       backdropFilter: 'blur(10px)'
                     }}>
                  <div className="w-6 h-6 bg-spotify-green rounded-full flex items-center justify-center text-black font-bold text-xs">
                    {index + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate text-sm" style={{ color: '#ffffff' }}>
                      {track.track}
                    </p>
                    <p className="text-xs truncate" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                      {track.artist}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="text-xs" style={{ color: 'rgba(255, 255, 255, 0.6)' }}>
          <p>This radar chart shows the average audio characteristics of your top tracks.</p>
        </div>
      </div>
    </div>
  )
}

export default AudioFeatures
