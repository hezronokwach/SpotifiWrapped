import React, { useState, useEffect } from 'react'
import api from '../api'
import '../spotify-components.css'
import { useDemoMode } from '../contexts/DemoModeContext'
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
  danceability?: number
  energy?: number
  valence?: number
  acousticness?: number
  instrumentalness?: number
  liveness?: number
  speechiness?: number
}

interface AudioFeaturesData {
  audio_features: AudioFeatures
  tracks: TrackInfo[]
  tracks_analyzed: number
}

const AudioFeatures: React.FC = () => {
  const { isDemoMode } = useDemoMode()
  const [audioFeatures, setAudioFeatures] = useState<AudioFeaturesData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchAudioFeatures()
  }, [isDemoMode])

  const fetchAudioFeatures = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      if (isDemoMode) {
        // Use sample audio features for demo mode
        const sampleAudioFeatures = {
          audio_features: {
            danceability: 0.65,
            energy: 0.72,
            speechiness: 0.08,
            acousticness: 0.25,
            instrumentalness: 0.15,
            liveness: 0.18,
            valence: 0.68,
            tempo: 125.5
          },
          tracks: [],
          tracks_analyzed: 50
        }
        setAudioFeatures(sampleAudioFeatures)
        setIsLoading(false)
        return
      }
      
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

  const colors = ['#1DB954', '#1ED760', '#00D4FF', '#8B5CF6', '#F472B6'];
  
  // Check if we have individual track data with audio features
  const hasIndividualFeatures = audioFeatures.tracks && audioFeatures.tracks.length > 0 && 
    audioFeatures.tracks[0].hasOwnProperty('danceability');
  
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
    datasets: hasIndividualFeatures ? 
      audioFeatures.tracks.map((track, index) => ({
        label: `${track.track} - ${track.artist}`,
        data: [
          track.danceability || 0,
          track.energy || 0,
          track.valence || 0,
          track.acousticness || 0,
          track.instrumentalness || 0,
          track.liveness || 0,
          track.speechiness || 0
        ],
        backgroundColor: `${colors[index % colors.length]}20`,
        borderColor: colors[index % colors.length],
        borderWidth: 3,
        pointBackgroundColor: colors[index % colors.length],
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 6,
        pointHoverRadius: 8,
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: colors[index % colors.length],
        pointHoverBorderWidth: 3,
      })) : 
      [{
        label: 'Your Music Profile (Average)',
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
        borderWidth: 3,
        pointBackgroundColor: '#1DB954',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 6,
        pointHoverRadius: 8,
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#1DB954',
        pointHoverBorderWidth: 3,
      }]
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: hasIndividualFeatures,
        position: 'bottom' as const,
        labels: {
          color: '#b3b3b3',
          font: {
            size: 14,
          },
          usePointStyle: true,
          pointStyle: 'circle',
        }
      },
      tooltip: {
        backgroundColor: '#282828',
        titleColor: '#ffffff',
        bodyColor: '#b3b3b3',
        borderColor: '#1DB954',
        borderWidth: 1,
        callbacks: {
          label: function(context: any) {
            const trackName = context.dataset.label;
            const featureName = context.label;
            const value = context.parsed.r;
            return `${trackName}: ${featureName} ${(value * 100).toFixed(1)}%`;
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
    <div className="spotify-card futuristic-chart-card fade-in" style={{ minHeight: '600px' }}>
      <div className="card-header">
        <h3><i className="fas fa-wave-square"></i> Audio Features</h3>
        <i className="fas fa-chart-radar"></i>
      </div>
      
      <div style={{ height: 'calc(100% - 80px)', display: 'flex', flexDirection: 'column' }}>
        <div style={{ flex: 1, minHeight: '450px', marginBottom: '20px' }}>
          <Radar data={data} options={options} />
        </div>
        
        {/* Songs Legend */}
        {audioFeatures.tracks && audioFeatures.tracks.length > 0 && (
          <div style={{ 
            marginBottom: '15px',
            fontSize: '11px',
            color: 'var(--text-secondary)'
          }}>           
          </div>
        )}
        
        
      </div>
    </div>
  )
}

export default AudioFeatures
