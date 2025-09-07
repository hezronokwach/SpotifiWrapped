import React, { useState, useEffect } from 'react'
import api from '../api'
import '../spotify-components.css'
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
      const response = await api.get('/analytics/audio-features')
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
      <div className="spotify-card futuristic-chart-card fade-in">
        <div className="card-header">
          <h3><i className="fas fa-wave-square"></i> Audio Features</h3>
        </div>
        <div className="chart-content">
          <div className="loading-shimmer" style={{ height: '300px', borderRadius: '16px' }}></div>
        </div>
      </div>
    )
  }

  if (error || !audioFeatures) {
    return (
      <div className="spotify-card futuristic-chart-card fade-in">
        <div className="card-header">
          <h3><i className="fas fa-wave-square"></i> Audio Features</h3>
        </div>
        <div className="chart-content">
          <i className="fas fa-chart-radar" style={{ fontSize: '48px', marginBottom: '20px', color: 'var(--accent-primary)' }}></i>
          <p>{error || 'No audio features data available'}</p>
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
    <div className="spotify-card futuristic-chart-card fade-in consistent-height-card">
      <div className="card-header">
        <h3><i className="fas fa-wave-square"></i> Audio Features</h3>
        <i className="fas fa-chart-radar"></i>
      </div>
      
      <div style={{ height: 'calc(100% - 80px)', display: 'flex', flexDirection: 'column' }}>
        <div style={{ flex: 1, minHeight: '300px', marginBottom: '20px' }}>
          <Radar data={data} options={options} />
        </div>
        
        <div style={{ 
          fontSize: '12px', 
          color: 'var(--text-secondary)', 
          textAlign: 'center',
          fontFamily: "'Orbitron', monospace",
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          Analysis of {audioFeatures.tracks_analyzed} tracks
        </div>
      </div>
    </div>
  )
}

export default AudioFeatures
