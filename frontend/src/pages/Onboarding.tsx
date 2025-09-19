import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Alert, AlertDescription } from '../components/ui/alert'
import {
  validateCredentials,
  storeCredentials,
  validateCredentialsWithAPI,
  hasValidCredentials,
  type SpotifyCredentials
} from '../lib/credentials'

const Onboarding: React.FC = () => {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [step, setStep] = useState<'welcome' | 'credentials' | 'validation'>('welcome')
  const [credentials, setCredentials] = useState({
    clientId: '',
    clientSecret: ''
  })
  const [errors, setErrors] = useState<string[]>([])
  const [isValidating, setIsValidating] = useState(false)
  const [validationError, setValidationError] = useState<string | null>(null)

  useEffect(() => {
    // Skip onboarding if credentials are already valid (check only once on mount)
    const checkCredentials = () => {
      if (hasValidCredentials()) {
        navigate('/login', { replace: true })
      }
    }

    checkCredentials()
  }, [navigate]) // navigate is stable from React Router

  const handleInputChange = (field: 'clientId' | 'clientSecret', value: string) => {
    setCredentials(prev => ({ ...prev, [field]: value }))
    setErrors([]) // Clear errors when user types
    setValidationError(null)
  }

  const handleCredentialsSubmit = async () => {
    // Validate format first
    const fullCredentials: SpotifyCredentials = {
      clientId: credentials.clientId || '',
      clientSecret: credentials.clientSecret || ''
    }
    
    const validation = validateCredentials(fullCredentials)
    if (!validation.isValid) {
      setErrors(validation.errors)
      return
    }

    setIsValidating(true)
    setValidationError(null)

    try {
      // Validate with Spotify API
      const apiValidation = await validateCredentialsWithAPI(fullCredentials)
      
      if (apiValidation.isValid) {
        // Store credentials securely
        storeCredentials(fullCredentials)
        setStep('validation')

        // Start login process directly instead of navigating
        console.log('🔍 Onboarding: Credentials stored, starting login...')
        setTimeout(() => {
          login() // Call login directly
        }, 1500)
      } else {
        setValidationError(apiValidation.error || 'Invalid credentials')
      }
    } catch (error) {
      setValidationError('Failed to validate credentials. Please try again.')
    } finally {
      setIsValidating(false)
    }
  }

  const renderWelcomeStep = () => (
    <Card variant="elevated" className="max-w-2xl mx-auto">
      <CardHeader className="text-center">
        <CardTitle className="text-3xl mb-4">Welcome to Spotify Analytics</CardTitle>
        <CardDescription className="text-lg">
          Get deep insights into your music listening habits with AI-powered analysis
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 surface-card rounded-lg">
            <div className="text-2xl mb-2">🎵</div>
            <h3 className="font-semibold text-primary mb-2">Music Analysis</h3>
            <p className="text-sm text-secondary">Discover patterns in your listening habits</p>
          </div>
          <div className="text-center p-4 surface-card rounded-lg">
            <div className="text-2xl mb-2">🧠</div>
            <h3 className="font-semibold text-primary mb-2">AI Insights</h3>
            <p className="text-sm text-secondary">Get personality analysis from your music</p>
          </div>
          <div className="text-center p-4 surface-card rounded-lg">
            <div className="text-2xl mb-2">📊</div>
            <h3 className="font-semibold text-primary mb-2">Visualizations</h3>
            <p className="text-sm text-secondary">Beautiful charts and interactive dashboards</p>
          </div>
        </div>

        <Alert>
          <AlertDescription>
            <strong>Privacy First:</strong> Your Spotify data is processed locally and never stored permanently. 
            We only analyze your music to provide insights.
          </AlertDescription>
        </Alert>

        <div className="text-center">
          <Button 
            onClick={() => setStep('credentials')} 
            variant="spotify" 
            size="lg"
            className="w-full md:w-auto"
          >
            Get Started
          </Button>
        </div>
      </CardContent>
    </Card>
  )

  const renderCredentialsStep = () => (
    <Card variant="elevated" className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Connect Your Spotify App</CardTitle>
        <CardDescription>
          You'll need to create a Spotify app to access your data securely
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Instructions */}
        <div className="surface-card p-4 rounded-lg space-y-3">
          <h3 className="font-semibold text-primary">How to get your Spotify credentials:</h3>
          <ol className="list-decimal list-inside space-y-2 text-sm text-secondary">
            <li>Go to <a href="https://developer.spotify.com/dashboard" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">Spotify Developer Dashboard</a></li>
            <li>Click "Create App" and fill in the details</li>
            <li>Set the redirect URI to: <code className="bg-background-elevated px-2 py-1 rounded text-xs">http://localhost:3000/auth/callback</code></li>
            <li>Copy your Client ID and Client Secret from the app settings</li>
          </ol>
        </div>

        {/* Form */}
        <div className="space-y-4">
          <div>
            <Label htmlFor="clientId">Spotify Client ID</Label>
            <Input
              id="clientId"
              type="text"
              placeholder="Enter your Spotify Client ID"
              value={credentials.clientId}
              onChange={(e) => handleInputChange('clientId', e.target.value)}
              className="mt-1"
            />
          </div>
          
          <div>
            <Label htmlFor="clientSecret">Spotify Client Secret</Label>
            <Input
              id="clientSecret"
              type="password"
              placeholder="Enter your Spotify Client Secret"
              value={credentials.clientSecret}
              onChange={(e) => handleInputChange('clientSecret', e.target.value)}
              className="mt-1"
            />
          </div>
        </div>

        {/* Errors */}
        {errors.length > 0 && (
          <Alert variant="destructive">
            <AlertDescription>
              <ul className="list-disc list-inside">
                {errors.map((error, index) => (
                  <li key={index}>{error}</li>
                ))}
              </ul>
            </AlertDescription>
          </Alert>
        )}

        {validationError && (
          <Alert variant="destructive">
            <AlertDescription>{validationError}</AlertDescription>
          </Alert>
        )}

        {/* Actions */}
        <div className="flex gap-3">
          <Button 
            variant="outline" 
            onClick={() => setStep('welcome')}
            disabled={isValidating}
          >
            Back
          </Button>
          <Button 
            onClick={handleCredentialsSubmit}
            disabled={isValidating || !credentials.clientId || !credentials.clientSecret}
            variant="spotify"
            className="flex-1"
          >
            {isValidating ? (
              <>
                <div className="loading-spinner w-4 h-4 mr-2" />
                Validating...
              </>
            ) : (
              'Validate & Continue'
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  )

  const renderValidationStep = () => (
    <Card variant="elevated" className="max-w-md mx-auto text-center">
      <CardContent className="pt-6">
        <div className="text-6xl mb-4">✅</div>
        <h2 className="text-2xl font-bold text-primary mb-2">Success!</h2>
        <p className="text-secondary mb-4">
          Your Spotify credentials have been validated and stored securely.
        </p>
        <p className="text-sm text-muted">
          Starting Spotify authentication...
        </p>
      </CardContent>
    </Card>
  )

  return (
    <div className="min-h-screen surface-main flex items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        {step === 'welcome' && renderWelcomeStep()}
        {step === 'credentials' && renderCredentialsStep()}
        {step === 'validation' && renderValidationStep()}
      </div>
    </div>
  )
}

export default Onboarding
