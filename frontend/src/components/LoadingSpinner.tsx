import React from 'react'

interface LoadingSpinnerProps {
  message?: string
  size?: 'sm' | 'md' | 'lg'
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  message = 'Loading...', 
  size = 'md' 
}) => {
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-12 h-12',
    lg: 'w-16 h-16'
  }

  return (
    <div className="min-h-screen surface-main flex items-center justify-center">
      <div className="text-center">
        <div className={`loading-spinner ${sizeClasses[size]} mx-auto mb-4`} />
        <p className="text-primary">{message}</p>
      </div>
    </div>
  )
}

export default LoadingSpinner
