import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Button } from './ui/button'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout } = useAuth()
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', href: '/', icon: '🏠' },
    { name: 'AI Insights', href: '/ai-insights', icon: '🧠' },
  ]

  return (
    <div className="min-h-screen bg-spotify-black">
      {/* Header */}
      <header className="bg-spotify-dark-gray border-b border-spotify-gray">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-xl font-bold text-spotify-white">
                  Spotify Analytics
                </h1>
              </div>
            </div>

            {/* Navigation */}
            <nav className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-4">
                {navigation.map((item) => {
                  const isActive = location.pathname === item.href
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                        isActive
                          ? 'bg-spotify-green text-white'
                          : 'text-spotify-light-gray hover:text-white hover:bg-spotify-gray'
                      }`}
                    >
                      <span className="mr-2">{item.icon}</span>
                      {item.name}
                    </Link>
                  )
                })}
              </div>
            </nav>

            {/* User menu */}
            <div className="flex items-center space-x-4">
              {user && (
                <div className="flex items-center space-x-3">
                  <div className="text-right">
                    <p className="text-sm font-medium text-spotify-white">
                      {user.display_name}
                    </p>
                  </div>
                  {user.images && user.images.length > 0 && (
                    <img
                      className="h-8 w-8 rounded-full"
                      src={user.images[0].url}
                      alt={user.display_name}
                    />
                  )}
                  <Button
                    onClick={logout}
                    variant="outline"
                    size="sm"
                    className="text-spotify-light-gray border-spotify-gray hover:bg-spotify-gray"
                  >
                    Logout
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Mobile navigation */}
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 border-t border-spotify-gray">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`block px-3 py-2 rounded-md text-base font-medium transition-colors ${
                    isActive
                      ? 'bg-spotify-green text-white'
                      : 'text-spotify-light-gray hover:text-white hover:bg-spotify-gray'
                  }`}
                >
                  <span className="mr-2">{item.icon}</span>
                  {item.name}
                </Link>
              )
            })}
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {children}
        </div>
      </main>
    </div>
  )
}

export default Layout
