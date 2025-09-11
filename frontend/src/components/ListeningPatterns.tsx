import React, { useState, useEffect } from 'react'
import api from '../api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { useDemoMode } from '../contexts/DemoModeContext'

interface PatternData {
  day: string
  day_num: number
  hour: number
  count: number
}

interface PatternsSummary {
  total_plays: number
  most_active_hour: number | null
  most_active_day: string | null
}

interface PatternsResponse {
  listening_patterns: PatternData[]
  summary: PatternsSummary
}

interface ListeningPatternsProps {
  refreshTrigger?: number
}

const ListeningPatterns: React.FC<ListeningPatternsProps> = ({ refreshTrigger }) => {
  const { isDemoMode } = useDemoMode()
  const [patternsData, setPatternsData] = useState<PatternsResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isCollecting, setIsCollecting] = useState(false)

  useEffect(() => {
    fetchPatternsData()
  }, [isDemoMode])
  
  // Refresh when refreshTrigger changes
  useEffect(() => {
    if (refreshTrigger && refreshTrigger > 0) {
      fetchPatternsData()
    }
  }, [refreshTrigger])

  const fetchPatternsData = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      if (isDemoMode) {
        // Generate sample listening patterns for demo mode
        const samplePatterns = []
        const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for (let dayIndex = 0; dayIndex < 7; dayIndex++) {
          for (let hour = 0; hour < 24; hour++) {
            let count = 0
            // Simulate realistic listening patterns
            if (dayIndex < 5) { // Weekdays
              if (hour >= 7 && hour <= 9) count = Math.floor(Math.random() * 15) + 5 // Morning commute
              else if (hour >= 12 && hour <= 14) count = Math.floor(Math.random() * 10) + 2 // Lunch
              else if (hour >= 17 && hour <= 22) count = Math.floor(Math.random() * 20) + 8 // Evening
              else if (hour >= 22 || hour <= 1) count = Math.floor(Math.random() * 8) + 1 // Late night
              else count = Math.floor(Math.random() * 5)
            } else { // Weekends
              if (hour >= 10 && hour <= 14) count = Math.floor(Math.random() * 18) + 5 // Late morning
              else if (hour >= 15 && hour <= 23) count = Math.floor(Math.random() * 25) + 10 // Afternoon/evening
              else count = Math.floor(Math.random() * 8)
            }
            
            samplePatterns.push({
              day: days[dayIndex],
              day_num: dayIndex === 6 ? 0 : dayIndex + 1, // Convert to Sunday=0 format
              hour,
              count
            })
          }
        }
        
        const totalPlays = samplePatterns.reduce((sum, p) => sum + p.count, 0)
        const maxPattern = samplePatterns.reduce((max, p) => p.count > max.count ? p : max)
        
        setPatternsData({
          listening_patterns: samplePatterns,
          summary: {
            total_plays: totalPlays,
            most_active_hour: maxPattern.hour,
            most_active_day: maxPattern.day
          }
        })
        setIsLoading(false)
        return
      }
      
      const response = await api.get('/analytics/patterns')
      console.log('🔍 Patterns response:', response.data)
      setPatternsData(response.data)
    } catch (err) {
      console.error('Failed to fetch listening patterns:', err)
      setError('Failed to load listening patterns')
    } finally {
      setIsLoading(false)
    }
  }

  const collectData = async () => {
    try {
      setIsCollecting(true)
      console.log('🔄 Collecting listening data...')
      
      // First refresh recent listening data
      await api.post('/music/refresh-data')
      console.log('✅ Recent data refreshed')
      
      // Then try to collect additional data if endpoint exists
      try {
        const response = await api.get('/analytics/collect-data')
        console.log('✅ Data collection result:', response.data)
      } catch (collectError) {
        console.log('⚠️ Analytics collect endpoint not available, using refresh only')
      }
      
      await fetchPatternsData()
    } catch (err) {
      console.error('Failed to collect data:', err)
      setError('Failed to collect listening data')
    } finally {
      setIsCollecting(false)
    }
  }

  const getHeatmapColor = (count: number, maxCount: number) => {
    if (count === 0) return 'bg-gray-900/80'  // Dark background like original
    const intensity = count / maxCount
    if (intensity < 0.1) return 'bg-spotify-green/20'      // Light green
    if (intensity < 0.3) return 'bg-spotify-green/40'      // Medium green
    if (intensity < 0.5) return 'bg-spotify-green/60'      // Bright green
    if (intensity < 0.7) return 'bg-cyan-400/60'           // Cyan like original
    if (intensity < 0.9) return 'bg-purple-500/80'         // Purple like original
    return 'bg-pink-400'                                    // Pink like original
  }

  const formatHour = (hour: number) => {
    if (hour === 0) return '12 AM'
    if (hour < 12) return `${hour} AM`
    if (hour === 12) return '12 PM'
    return `${hour - 12} PM`
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
        <div className="mb-6">
          <h3 className="text-2xl font-bold mb-2 font-orbitron"
              style={{
                background: 'linear-gradient(45deg, #1DB954, #00D4FF, #8b5cf6)',
                backgroundSize: '200% 200%',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                textTransform: 'uppercase',
                letterSpacing: '1.5px'
              }}>
            🕒 Listening Patterns
          </h3>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400"></div>
        </div>
      </div>
    )
  }

  if (error || !patternsData) {
    return (
      <div className="relative p-6 rounded-3xl border transition-all duration-300 hover:transform hover:scale-[1.01] hover:-translate-y-1"
           style={{
             background: 'linear-gradient(135deg, rgba(26,26,26,0.95), rgba(18,18,18,0.95))',
             border: '1px solid rgba(29, 185, 84, 0.3)',
             boxShadow: '0 8px 32px rgba(0,0,0,0.3), 0 0 40px rgba(29, 185, 84, 0.1)',
             backdropFilter: 'blur(10px)'
           }}>
        <div className="mb-6">
          <h3 className="text-2xl font-bold mb-2 font-orbitron"
              style={{
                background: 'linear-gradient(45deg, #1DB954, #00D4FF, #8b5cf6)',
                backgroundSize: '200% 200%',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                textTransform: 'uppercase',
                letterSpacing: '1.5px'
              }}>
            🕒 Listening Patterns
          </h3>
        </div>
        <div className="text-center py-8" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
          {error || 'No listening patterns data available'}
        </div>
      </div>
    )
  }

  const { listening_patterns, summary } = patternsData
  const maxCount = Math.max(...listening_patterns.map(p => p.count), 1)
  // Use same day order as original Dash app (Monday first)
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
  const hours = Array.from({ length: 24 }, (_, i) => i)

  // Create a lookup for pattern data - convert Sunday=0 to Monday=0 ordering
  const patternLookup = new Map<string, number>()
  listening_patterns.forEach(pattern => {
    // Convert from Sunday=0 to Monday=0 ordering
    const adjustedDayNum = pattern.day_num === 0 ? 6 : pattern.day_num - 1
    patternLookup.set(`${adjustedDayNum}-${pattern.hour}`, pattern.count)
  })

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
          🕒 Listening Patterns
        </h3>
        <p className="text-sm" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
          When you listen to music most frequently
        </p>
        <div className="text-sm font-medium" style={{ color: '#1DB954', marginTop: '4px' }}>
          📅 {(() => {
            const endDate = new Date()
            const startDate = new Date(endDate)
            startDate.setDate(startDate.getDate() - 7)
            return `${startDate.toLocaleDateString()} - ${endDate.toLocaleDateString()}`
          })()
          } (Last 7 days)
        </div>
      </div>
      <div className="space-y-4">
        {/* Summary Stats */}
        {summary.total_plays === 0 && (
          <div className="text-center mb-4">
            <button
              onClick={collectData}
              disabled={isCollecting}
              className="px-4 py-2 text-sm rounded-lg transition-colors"
              style={{
                background: isCollecting ? 'rgba(139, 92, 246, 0.3)' : 'rgba(29, 185, 84, 0.2)',
                border: '1px solid rgba(29, 185, 84, 0.5)',
                color: '#1DB954'
              }}
            >
              {isCollecting ? (
                <>⏳ Collecting Data...</>
              ) : (
                <>📥 Collect Recent Listening Data</>
              )}
            </button>
          </div>
        )}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="text-center p-3 bg-black/20 rounded-lg">
            <div className="text-xl font-bold text-spotify-green">
              {summary.total_plays.toLocaleString()}
            </div>
            <div className="text-xs text-spotify-light-gray">Total Plays</div>
          </div>
          
          <div className="text-center p-3 bg-black/20 rounded-lg">
            <div className="text-xl font-bold text-purple-400">
              {summary.most_active_hour !== null ? formatHour(summary.most_active_hour) : 'N/A'}
            </div>
            <div className="text-xs text-spotify-light-gray">Peak Hour</div>
          </div>
          
          <div className="text-center p-3 bg-black/20 rounded-lg">
            <div className="text-xl font-bold text-blue-400">
              {summary.most_active_day || 'N/A'}
            </div>
            <div className="text-xs text-spotify-light-gray">Peak Day</div>
          </div>
        </div>

        {/* Heatmap */}
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-spotify-white mb-3">Activity Heatmap</h3>
          
          {/* Hour labels */}
          <div className="flex gap-1 text-xs text-spotify-light-gray mb-2">
            <div className="w-16"></div> {/* Empty space for day labels */}
            <div className="flex-1 flex justify-between">
              {[0, 6, 12, 18].map(hour => (
                <div key={hour} className="text-center">
                  {formatHour(hour)}
                </div>
              ))}
            </div>
          </div>

          {/* Heatmap grid */}
          <div className="space-y-1">
            {days.map((day, dayIndex) => (
              <div key={day} className="flex gap-1 items-center">
                <div className="text-xs text-spotify-light-gray font-medium w-16">
                  {day.slice(0, 3)}
                </div>
                <div className="flex gap-1 flex-1">

                </div>
              </div>
            ))}
          </div>
          
          {/* Legend - matching original's sophisticated colorscale */}
          <div className="flex items-center justify-center space-x-2 mt-4">
            <span className="text-xs text-spotify-light-gray">Less</span>
            <div className="flex space-x-1">
              <div className="h-3 w-3 bg-gray-900/80 rounded-sm"></div>
              <div className="h-3 w-3 bg-spotify-green/20 rounded-sm"></div>
              <div className="h-3 w-3 bg-spotify-green/40 rounded-sm"></div>
              <div className="h-3 w-3 bg-spotify-green/60 rounded-sm"></div>
              <div className="h-3 w-3 bg-cyan-400/60 rounded-sm"></div>
              <div className="h-3 w-3 bg-purple-500/80 rounded-sm"></div>
              <div className="h-3 w-3 bg-pink-400 rounded-sm"></div>
            </div>
            <span className="text-xs text-spotify-light-gray">More</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ListeningPatterns
