import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Heart, Menu, X, User, MessageCircle, Compass, Users } from 'lucide-react'

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)
  const location = useLocation()
  const isLoggedIn = false // This would come from auth context

  const navLinks = isLoggedIn ? [
    { path: '/discover', label: 'Discover', icon: Compass },
    { path: '/matches', label: 'Matches', icon: Users },
    { path: '/messages', label: 'Messages', icon: MessageCircle },
    { path: '/profile', label: 'Profile', icon: User },
  ] : [
    { path: '/', label: 'Home' },
    { path: '/about', label: 'About' },
  ]

  return (
    <nav className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="relative">
              <Heart className="h-8 w-8 text-primary-500 fill-primary-500 animate-pulse-heart" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-gold-400 rounded-full"></div>
            </div>
            <span className="text-xl font-bold">
              <span className="text-primary-600">Vet</span>
              <span className="text-accent-600">Love</span>
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors
                  ${location.pathname === link.path
                    ? 'text-primary-600 bg-primary-50'
                    : 'text-gray-600 hover:text-primary-600 hover:bg-gray-50'
                  }`}
              >
                {link.icon && <link.icon className="h-4 w-4" />}
                <span>{link.label}</span>
              </Link>
            ))}

            {!isLoggedIn && (
              <div className="flex items-center space-x-3">
                <Link to="/login" className="text-gray-600 hover:text-primary-600 font-medium">
                  Sign In
                </Link>
                <Link to="/register" className="btn-primary text-sm">
                  Join Free
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="text-gray-600 hover:text-primary-600"
            >
              {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isOpen && (
        <div className="md:hidden bg-white border-t">
          <div className="px-2 pt-2 pb-3 space-y-1">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                onClick={() => setIsOpen(false)}
                className={`block px-3 py-2 rounded-md text-base font-medium
                  ${location.pathname === link.path
                    ? 'text-primary-600 bg-primary-50'
                    : 'text-gray-600 hover:text-primary-600 hover:bg-gray-50'
                  }`}
              >
                {link.label}
              </Link>
            ))}
            {!isLoggedIn && (
              <>
                <Link
                  to="/login"
                  onClick={() => setIsOpen(false)}
                  className="block px-3 py-2 text-gray-600 hover:text-primary-600"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  onClick={() => setIsOpen(false)}
                  className="block mx-3 mt-2 btn-primary text-center text-sm"
                >
                  Join Free
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  )
}
