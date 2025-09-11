import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface DemoModeContextType {
  isDemoMode: boolean
  setDemoMode: (enabled: boolean) => void
}

const DemoModeContext = createContext<DemoModeContextType | undefined>(undefined)

export const useDemoMode = () => {
  const context = useContext(DemoModeContext)
  if (context === undefined) {
    throw new Error('useDemoMode must be used within a DemoModeProvider')
  }
  return context
}

interface DemoModeProviderProps {
  children: ReactNode
}

export const DemoModeProvider: React.FC<DemoModeProviderProps> = ({ children }) => {
  const [isDemoMode, setIsDemoMode] = useState(false)

  useEffect(() => {
    const savedMode = localStorage.getItem('demo_mode') === 'true'
    setIsDemoMode(savedMode)
  }, [])

  const setDemoMode = (enabled: boolean) => {
    setIsDemoMode(enabled)
    localStorage.setItem('demo_mode', enabled.toString())
    
    if (enabled) {
      // Clear any existing auth tokens when switching to demo mode
      localStorage.removeItem('spotify_access_token')
      localStorage.removeItem('spotify_refresh_token')
    }
  }

  return (
    <DemoModeContext.Provider value={{ isDemoMode, setDemoMode }}>
      {children}
    </DemoModeContext.Provider>
  )
}