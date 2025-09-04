import React, { useState, useEffect } from 'react'
import api from '../api'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js'
import { Doughnut } from 'react-chartjs-2'


ChartJS.register(ArcElement, Tooltip, Legend)

interface GenreData {
  [genre: string]: number
}

interface GenreResponse {
  genres: GenreData
}

const GenreChart: React.FC = () => {
  const [genreData, setGenreData] = useState<GenreResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchGenreData()
  }, [])

  const fetchGenreData = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await api.get('/analytics/genres')
      setGenreData(response.data)
    } catch (err) {
      console.error('Failed to fetch genre data:', err)
      setError('Failed to load genre data')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="relative p-6 rounded-3xl border transition-all duration-300 hover:transform hover:scale-[1.01] hover:-translate-y-1"
           style={{
             background: 'linear-gradient(135deg, rgba(26,26,26,0.95), rgba(18,18,18,0.95))',
             border: '1px solid rgba(139, 92, 246, 0.3)',
             boxShadow: '0 8px 32px rgba(0,0,0,0.3), 0 0 40px rgba(139, 92, 246, 0.1)',
             backdropFilter: 'blur(10px)'
           }}>
        <div className="absolute inset-0 rounded-3xl opacity-0 hover:opacity-100 transition-opacity duration-300"
             style={{
               background: 'linear-gradient(45deg, rgba(139, 92, 246, 0.3), rgba(244, 114, 182, 0.3), rgba(29, 185, 84, 0.3), rgba(139, 92, 246, 0.3))',
               backgroundSize: '400% 400%',
               animation: 'gradientShift 8s ease infinite',
               zIndex: -1
             }}>
        </div>
        <div className="mb-6">
          <h3 className="text-2xl font-bold mb-2 font-orbitron"
              style={{
                background: 'linear-gradient(45deg, #8B5CF6, #F472B6, #1DB954)',
                backgroundSize: '200% 200%',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                textTransform: 'uppercase',
                letterSpacing: '1.5px',
                textShadow: '0 0 20px rgba(139, 92, 246, 0.3)'
              }}>
            Genre Distribution
          </h3>
          <p className="text-sm" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
            Analyzing your music genres...
          </p>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
        </div>
      </div>
    )
  }

  if (error || !genreData || !genreData.genres || Object.keys(genreData.genres).length === 0) {
    return (
      <div className="relative p-6 rounded-3xl border transition-all duration-300 hover:transform hover:scale-[1.01] hover:-translate-y-1"
           style={{
             background: 'linear-gradient(135deg, rgba(26,26,26,0.95), rgba(18,18,18,0.95))',
             border: '1px solid rgba(139, 92, 246, 0.3)',
             boxShadow: '0 8px 32px rgba(0,0,0,0.3), 0 0 40px rgba(139, 92, 246, 0.1)',
             backdropFilter: 'blur(10px)'
           }}>
        <div className="absolute inset-0 rounded-3xl opacity-0 hover:opacity-100 transition-opacity duration-300"
             style={{
               background: 'linear-gradient(45deg, rgba(139, 92, 246, 0.3), rgba(244, 114, 182, 0.3), rgba(29, 185, 84, 0.3), rgba(139, 92, 246, 0.3))',
               backgroundSize: '400% 400%',
               animation: 'gradientShift 8s ease infinite',
               zIndex: -1
             }}>
        </div>
        <div className="mb-6">
          <h3 className="text-2xl font-bold mb-2 font-orbitron"
              style={{
                background: 'linear-gradient(45deg, #8B5CF6, #F472B6, #1DB954)',
                backgroundSize: '200% 200%',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                textTransform: 'uppercase',
                letterSpacing: '1.5px',
                textShadow: '0 0 20px rgba(139, 92, 246, 0.3)'
              }}>
            Genre Distribution
          </h3>
          <p className="text-sm" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
            Your music genre breakdown
          </p>
        </div>
        <div className="text-center py-8" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
          {error || 'No genre data available'}
        </div>
      </div>
    )
  }

  // Sort genres by count and take top 8
  const sortedGenres = Object.entries(genreData.genres)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 8)

  const labels = sortedGenres.map(([genre]) => genre)
  const values = sortedGenres.map(([, count]) => count)

  // Spotify-inspired color palette
  const colors = [
    '#1DB954', // Spotify Green
    '#1ED760', // Light Green
    '#1FDF64', // Lighter Green
    '#FF6B35', // Orange
    '#F037A5', // Pink
    '#8B5CF6', // Purple
    '#06B6D4', // Cyan
    '#F59E0B', // Amber
  ]

  const data = {
    labels,
    datasets: [
      {
        data: values,
        backgroundColor: colors,
        borderColor: '#121212',
        borderWidth: 2,
        hoverBorderWidth: 3,
        hoverBorderColor: '#ffffff',
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const,
        labels: {
          color: '#b3b3b3',
          font: {
            size: 12,
          },
          padding: 15,
          usePointStyle: true,
        },
      },
      tooltip: {
        backgroundColor: '#282828',
        titleColor: '#ffffff',
        bodyColor: '#b3b3b3',
        borderColor: '#1DB954',
        borderWidth: 1,
        callbacks: {
          label: function(context: { label: string; parsed: number; dataset: { data: number[] } }) {
            const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0)
            const percentage = ((context.parsed / total) * 100).toFixed(1)
            return `${context.label}: ${context.parsed} tracks (${percentage}%)`
          }
        }
      },
    },
    cutout: '60%',
  }

  const totalTracks = values.reduce((a, b) => a + b, 0)

  return (
    <div className="relative p-6 rounded-3xl border transition-all duration-300 hover:transform hover:scale-[1.01] hover:-translate-y-1"
         style={{
           background: 'linear-gradient(135deg, rgba(26,26,26,0.95), rgba(18,18,18,0.95))',
           border: '1px solid rgba(139, 92, 246, 0.3)',
           boxShadow: '0 8px 32px rgba(0,0,0,0.3), 0 0 40px rgba(139, 92, 246, 0.1)',
           backdropFilter: 'blur(10px)'
         }}>
      
      {/* Animated border gradient */}
      <div className="absolute inset-0 rounded-3xl opacity-0 hover:opacity-100 transition-opacity duration-300"
           style={{
             background: 'linear-gradient(45deg, rgba(139, 92, 246, 0.3), rgba(244, 114, 182, 0.3), rgba(29, 185, 84, 0.3), rgba(139, 92, 246, 0.3))',
             backgroundSize: '400% 400%',
             animation: 'gradientShift 8s ease infinite',
             zIndex: -1
           }}>
      </div>

      {/* Header */}
      <div className="mb-6">
        <h3 className="text-2xl font-bold mb-2 font-orbitron"
            style={{
              background: 'linear-gradient(45deg, #8B5CF6, #F472B6, #1DB954)',
              backgroundSize: '200% 200%',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              textTransform: 'uppercase',
              letterSpacing: '1.5px',
              textShadow: '0 0 20px rgba(139, 92, 246, 0.3)'
            }}>
          Genre Distribution
        </h3>
        <p className="text-sm" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
          Your top genres from {totalTracks} tracks
        </p>
      </div>

      {/* Content */}
      <div>
        <div className="h-64">
          <Doughnut data={data} options={options} />
        </div>
        <div className="mt-4">
          <div className="grid grid-cols-2 gap-2 text-xs">
            {sortedGenres.slice(0, 4).map(([genre, count], index) => (
              <div key={genre} className="flex items-center space-x-2">
                <div 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: colors[index] }}
                ></div>
                <span className="truncate" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  {genre} ({count})
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default GenreChart
