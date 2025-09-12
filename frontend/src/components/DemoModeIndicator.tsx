import React from 'react'
import { useDemoMode } from '../contexts/DemoModeContext'

const DemoModeIndicator: React.FC = () => {
  const { isDemoMode, setDemoMode } = useDemoMode()

  if (!isDemoMode) return null

  return (
    <div className="demo-mode-banner">
      <div className="demo-mode-content">
        <i className="fas fa-flask demo-mode-icon"></i>
        <div className="demo-mode-text">
          <span className="demo-mode-title">Demo Mode Active</span>
          <span className="demo-mode-subtitle">You're exploring with sample data</span>
        </div>
        <button 
          onClick={() => setDemoMode(false)} 
          className="demo-mode-switch"
        >
          <i className="fas fa-cog"></i>
          Switch to Real Data
        </button>
      </div>
      <div className="demo-mode-note">
        Note: Images are randomized placeholders, not actual album/artist artwork
      </div>
    </div>
  )
}

export default DemoModeIndicator