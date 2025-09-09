import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Dashboard from './pages/Dashboard'
import AIInsights from './pages/AIInsights'
import Login from './pages/Login'
import Onboarding from './pages/Onboarding'
import AuthCallback from './pages/AuthCallback'
import Layout from './components/Layout'
import LoadingSpinner from './components/LoadingSpinner'
import DebugCredentials from './components/DebugCredentials'
import { hasValidCredentials } from './lib/credentials'
import './index.css'

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return <LoadingSpinner message="Authenticating..." />
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
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

    // Also listen for custom events when credentials change
    window.addEventListener('credentialsChanged', handleStorageChange)

    return () => {
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('credentialsChanged', handleStorageChange)
    }
  }, [])

  // Show loading while checking credentials
  if (needsOnboarding === null || isLoading) {
    return <LoadingSpinner message="Initializing application..." />
  }

  return (
    <Routes>
      <Route
        path="/onboarding"
        element={needsOnboarding ? <Onboarding /> : <Navigate to="/login" replace />}
      />
      <Route
        path="/login"
        element={
          needsOnboarding ? <Navigate to="/onboarding" replace /> :
          isAuthenticated ? <Navigate to="/" replace /> : <Login />
        }
      />
      <Route
        path="/auth/callback"
        element={<AuthCallback />}
      />
      <Route
        path="/"
        element={
          needsOnboarding ? <Navigate to="/onboarding" replace /> :
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
          needsOnboarding ? <Navigate to="/onboarding" replace /> :
          <ProtectedRoute>
            <Layout>
              <AIInsights />
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
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-spotify-black">
          <AppRoutes />
          <DebugCredentials />
        </div>
      </Router>
    </AuthProvider>
  )
}

export default App
