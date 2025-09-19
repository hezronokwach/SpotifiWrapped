import React, { useState, useEffect, useCallback } from 'react'
import api from '../api'
import { useDemoMode } from '../contexts/DemoModeContext'
import { sampleUserProfile } from '../data/sampleData'

interface UserData {
  display_name: string
  followers: number
  following: number
  image_url?: string
  product?: string
}

const UserProfile: React.FC = () => {
  const { isDemoMode } = useDemoMode()
  const [userData, setUserData] = useState<UserData | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const fetchUserData = useCallback(async () => {
    try {
      if (isDemoMode) {
        // Use sample user data for demo mode
        setUserData({
          display_name: sampleUserProfile.display_name,
          followers: sampleUserProfile.followers.total,
          following: 42, // Sample following count
          image_url: sampleUserProfile.images[0]?.url,
          product: sampleUserProfile.product
        })
        setIsLoading(false)
        return
      }
      
      const response = await api.get('/user/profile')
      setUserData(response.data)
    } catch (err) {
      console.error('Failed to fetch user profile:', err)
      // Use fallback data if API fails
      setUserData({
        display_name: 'Spotify User',
        followers: 0,
        following: 0
      })
    } finally {
      setIsLoading(false)
    }
  }, [isDemoMode])

  useEffect(() => {
    fetchUserData()
  }, [fetchUserData, isDemoMode])

  if (isLoading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-spotify-green mx-auto"></div>
      </div>
    )
  }

  const getInitials = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
  }

  return (
    <div className="text-center py-8">
      {/* User Avatar - EXACT copy from Dash */}
      <div className="flex justify-center mb-6">
        {userData?.image_url ? (
          <img
            src={userData.image_url}
            alt={userData.display_name}
            className="w-32 h-32 rounded-full border-4 transition-all duration-300"
            style={{
              borderColor: 'rgba(29, 185, 84, 0.8)',
              boxShadow: '0 0 30px rgba(29, 185, 84, 0.4), 0 0 60px rgba(29, 185, 84, 0.2)',
              filter: 'brightness(1.1)'
            }}
          />
        ) : (
          <div
            className="w-32 h-32 rounded-full flex items-center justify-center border-4 transition-all duration-300 text-black text-5xl font-bold font-orbitron"
            style={{
              background: 'linear-gradient(135deg, #1DB954, #00D4FF)',
              borderColor: 'rgba(29, 185, 84, 0.8)',
              boxShadow: '0 0 30px rgba(29, 185, 84, 0.4), 0 0 60px rgba(29, 185, 84, 0.2)',
              textShadow: '0 0 10px rgba(0, 0, 0, 0.5)'
            }}
          >
            {userData ? getInitials(userData.display_name) : 'S'}
          </div>
        )}
      </div>

      {/* User Info - EXACT copy from Dash */}
      <div className="mb-6">
        <h1
          className="text-4xl font-bold mb-4 font-orbitron"
          style={{
            color: 'rgba(255, 255, 255, 0.95)',
            textShadow: '0 0 20px rgba(29, 185, 84, 0.3)',
            background: 'linear-gradient(45deg, #FFFFFF, #1DB954)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}
        >
          Welcome, {userData?.display_name || 'Spotify User'}
        </h1>

        {/* Stats - EXACT copy from Dash */}
        <div className="flex justify-center space-x-5">
          <div
            className="text-center p-4 rounded-xl transition-all duration-300"
            style={{
              background: 'linear-gradient(135deg, rgba(29, 185, 84, 0.1), rgba(29, 185, 84, 0.05))',
              border: '1px solid rgba(29, 185, 84, 0.3)',
              boxShadow: '0 4px 15px rgba(29, 185, 84, 0.1)'
            }}
          >
            <div
              className="text-3xl font-bold font-orbitron"
              style={{
                color: '#1DB954',
                textShadow: '0 0 10px rgba(29, 185, 84, 0.5)'
              }}
            >
              {userData?.followers?.toLocaleString() || '0'}
            </div>
            <div
              className="text-sm font-medium font-orbitron tracking-wider mt-1"
              style={{
                color: 'rgba(255, 255, 255, 0.7)'
              }}
            >
              FOLLOWERS
            </div>
          </div>

          <div
            className="text-center p-4 rounded-xl transition-all duration-300"
            style={{
              background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 212, 255, 0.05))',
              border: '1px solid rgba(0, 212, 255, 0.3)',
              boxShadow: '0 4px 15px rgba(0, 212, 255, 0.1)'
            }}
          >
            <div
              className="text-3xl font-bold font-orbitron"
              style={{
                color: '#00D4FF',
                textShadow: '0 0 10px rgba(0, 212, 255, 0.5)'
              }}
            >
              {userData?.following?.toLocaleString() || '0'}
            </div>
            <div
              className="text-sm font-medium font-orbitron tracking-wider mt-1"
              style={{
                color: 'rgba(255, 255, 255, 0.7)'
              }}
            >
              FOLLOWING
            </div>
          </div>
        </div>
      </div>

      {/* Dashboard Title */}
      <div className="mt-8">
        <h2 className="text-2xl font-bold text-spotify-green uppercase tracking-wider font-orbitron">
          Your Personal Spotify Dashboard
        </h2>
      </div>
    </div>
  )
}

export default UserProfile
