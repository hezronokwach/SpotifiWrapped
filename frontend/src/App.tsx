import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { DemoModeProvider, useDemoMode } from './contexts/DemoModeContext'
import Dashboard from './pages/Dashboard'
import AIInsights from './pages/AIInsights'
import Login from './pages/Login'
import Onboarding from './pages/Onboarding'
import OnboardingPage from './pages/OnboardingPage'
import AuthCallback from './pages/AuthCallback'
import Settings from './pages/Settings'
import Layout from './components/Layout'
import LoadingSpinner from './components/LoadingSpinner'
import DebugCredentials from './components/DebugCredentials'
import { hasValidCredentials } from './lib/credentials.ts'
import './index.css'

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth()
  const { isDemoMode } = useDemoMode()

  if (isLoading && !isDemoMode) {
    return <LoadingSpinner message="Authenticating..." />
  }

  return (isAuthenticated || isDemoMode) ? <>{children}</> : <Navigate to="/onboarding" replace />
}

const AppRoutes: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth()
  const [needsOnboarding, setNeedsOnboarding] = useState<boolean | null>(null)

  // // Function to refresh credentials check
  // const refreshCredentialsCheck = () => {
  //   const hasCredentials = hasValidCredentials()
  //   setNeedsOnboarding(!hasCredentials)
  // }

  // Check credentials on mount and when storage changes
  useEffect(() => {
    const checkCredentials = () => {
      // Skip credential check if user is authenticated or in demo mode
      if (isAuthenticated) {
        setNeedsOnboarding(false)
        return
      }
      
      const hasCredentials = hasValidCredentials()
      console.log('🔍 App.tsx: Checking credentials:', hasCredentials)
      setNeedsOnboarding(!hasCredentials)
      console.log('🔍 App.tsx: Setting needsOnboarding to:', !hasCredentials)
    }

    checkCredentials()

    // Listen for storage changes (when credentials are stored)
    const handleStorageChange = () => {
      console.log('🔍 App.tsx: Storage change detected, rechecking credentials')
      checkCredentials()
    }

    window.addEventListener('storage', handleStorageChange)
    window.addEventListener('credentialsChanged', handleStorageChange)

    return () => {
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('credentialsChanged', handleStorageChange)
    }
  }, [isAuthenticated])

  // Show loading while checking credentials
  if (needsOnboarding === null || isLoading) {
    return <LoadingSpinner message="Initializing application..." />
  }

  return (
    <Routes>
      <Route
        path="/onboarding"
        element={<OnboardingPage />}
      />
      <Route
        path="/setup"
        element={needsOnboarding ? <Onboarding /> : <Navigate to="/login" replace />}
      />
      <Route
        path="/login"
        element={<Login />}
      />
      <Route
        path="/auth/callback"
        element={<AuthCallback />}
      />
      <Route
        path="/auth"
        element={<Navigate to="/onboarding" replace />}
      />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout>
              <Dashboard />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Layout>
              <Dashboard />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/ai-insights"
        element={
          <ProtectedRoute>
            <Layout>
              <AIInsights />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <Layout>
              <Settings />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to={needsOnboarding ? "/onboarding" : "/"} replace />} />
    </Routes>
  )
}

const App: React.FC = () => {
  return (
    <DemoModeProvider>
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-spotify-black">
            <AppRoutes />
            <DebugCredentials />
          </div>
        </Router>
      </AuthProvider>
    </DemoModeProvider>
  )
}

export default App
