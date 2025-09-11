import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDemoMode } from '../contexts/DemoModeContext'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'

const Settings: React.FC = () => {
  const { isDemoMode, setDemoMode } = useDemoMode()
  const navigate = useNavigate()
  const [status, setStatus] = useState('')
  const [clientId, setClientId] = useState('')
  const [clientSecret, setClientSecret] = useState('')

  const handleDataModeChange = (mode: 'live' | 'demo') => {
    if (mode === 'demo') {
      setDemoMode(true)
      setStatus('✅ Switched to demo mode')
    } else {
      setDemoMode(false)
      setStatus('✅ Switched to live data mode')
    }
  }

  const handleClearData = () => {
    localStorage.clear()
    sessionStorage.clear()
    setDemoMode(false)
    setStatus('✅ All data cleared. Redirecting to onboarding...')
    setTimeout(() => navigate('/'), 2000)
  }

  const handleUpdateCredentials = () => {
    if (!clientId || !clientSecret) {
      setStatus('❌ Please provide both Client ID and Secret')
      return
    }
    
    localStorage.setItem('spotify_credentials', JSON.stringify({
      clientId,
      clientSecret
    }))
    setStatus('✅ Credentials updated successfully!')
    setClientId('')
    setClientSecret('')
  }

  return (
    <div className="min-h-screen bg-black p-6">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">⚙️ Settings</h1>
          <p className="text-gray-400">Manage your application settings and data preferences</p>
        </div>

        <div className="space-y-6">
          {/* Data Mode Card */}
          <Card className="bg-gray-900 border-gray-700">
            <CardHeader>
              <CardTitle className="text-spotify-green">Data Mode</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-gray-300">Switch between using your live Spotify data or sample data</p>
              
              <div className="flex gap-4">
                <Button
                  variant={!isDemoMode ? "default" : "outline"}
                  onClick={() => handleDataModeChange('live')}
                  className={!isDemoMode ? "bg-spotify-green text-black" : ""}
                >
                  Live Spotify Data
                </Button>
                <Button
                  variant={isDemoMode ? "default" : "outline"}
                  onClick={() => handleDataModeChange('demo')}
                  className={isDemoMode ? "bg-blue-600" : ""}
                >
                  Demo Mode
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Credentials Card */}
          <Card className="bg-gray-900 border-gray-700">
            <CardHeader>
              <CardTitle className="text-spotify-green">Spotify API Credentials</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-gray-300">Update your Spotify API credentials</p>
              
              <div className="space-y-3">
                <div>
                  <Label htmlFor="clientId" className="text-white">Client ID</Label>
                  <Input
                    id="clientId"
                    type="text"
                    value={clientId}
                    onChange={(e) => setClientId(e.target.value)}
                    placeholder="Enter Spotify Client ID"
                    className="bg-gray-800 border-gray-600 text-white"
                  />
                </div>
                
                <div>
                  <Label htmlFor="clientSecret" className="text-white">Client Secret</Label>
                  <Input
                    id="clientSecret"
                    type="password"
                    value={clientSecret}
                    onChange={(e) => setClientSecret(e.target.value)}
                    placeholder="Enter Spotify Client Secret"
                    className="bg-gray-800 border-gray-600 text-white"
                  />
                </div>
                
                <Button 
                  onClick={handleUpdateCredentials}
                  className="bg-spotify-green text-black hover:bg-green-500"
                >
                  Update Credentials
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Data Management Card */}
          <Card className="bg-gray-900 border-gray-700">
            <CardHeader>
              <CardTitle className="text-red-400">Data Management</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-gray-300">Clear all stored data and logout</p>
              
              <Button 
                onClick={handleClearData}
                variant="destructive"
                className="bg-red-600 hover:bg-red-700"
              >
                🗑️ Clear All Data & Logout
              </Button>
            </CardContent>
          </Card>

          {/* Status Message */}
          {status && (
            <div className="p-4 bg-gray-800 border border-gray-600 rounded-lg">
              <p className="text-white">{status}</p>
            </div>
          )}

          {/* Back Button */}
          <div className="text-center">
            <Button 
              onClick={() => navigate('/dashboard')}
              variant="outline"
              className="border-gray-600 text-gray-300 hover:bg-gray-800"
            >
              ← Back to Dashboard
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings