import { Link } from 'react-router-dom'
import { Heart, MessageCircle, MapPin, Shield, Clock, Sparkles } from 'lucide-react'

export default function Matches() {
  const newMatches = [
    {
      id: 1,
      name: 'James',
      age: 35,
      photo: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop',
      matchedAt: '2 hours ago',
      isNew: true
    },
    {
      id: 2,
      name: 'Michael',
      age: 38,
      photo: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150&h=150&fit=crop',
      matchedAt: '1 day ago',
      isNew: true
    },
    {
      id: 3,
      name: 'David',
      age: 32,
      photo: 'https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=150&h=150&fit=crop',
      matchedAt: '3 days ago',
      isNew: false
    }
  ]

  const allMatches = [
    {
      id: 1,
      name: 'James Wilson',
      age: 35,
      location: 'Austin, Texas',
      photo: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop',
      branch: 'U.S. Army',
      matchedAt: '2 hours ago',
      lastMessage: null,
      verified: true
    },
    {
      id: 2,
      name: 'Michael Rodriguez',
      age: 38,
      location: 'San Diego, California',
      photo: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=300&h=300&fit=crop',
      branch: 'U.S. Marine Corps',
      matchedAt: '1 day ago',
      lastMessage: 'Hey! Nice to match with you!',
      verified: true
    },
    {
      id: 3,
      name: 'David Thompson',
      age: 32,
      location: 'Miami, Florida',
      photo: 'https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=300&h=300&fit=crop',
      branch: 'U.S. Navy',
      matchedAt: '3 days ago',
      lastMessage: 'How are you doing?',
      verified: true
    },
    {
      id: 4,
      name: 'Robert Johnson',
      age: 40,
      location: 'Denver, Colorado',
      photo: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=300&h=300&fit=crop',
      branch: 'U.S. Air Force',
      matchedAt: '1 week ago',
      lastMessage: 'I would love to learn more about you',
      verified: true
    }
  ]

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Your Matches</h1>
          <p className="text-gray-600 mt-1">Start conversations with your connections</p>
        </div>

        {/* New Matches Carousel */}
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Sparkles className="h-5 w-5 text-gold-500 mr-2" />
            New Matches
          </h2>
          <div className="flex gap-4 overflow-x-auto pb-4">
            {newMatches.map((match) => (
              <Link
                key={match.id}
                to={`/messages?user=${match.id}`}
                className="flex-shrink-0 text-center group"
              >
                <div className="relative">
                  <div className={`w-20 h-20 rounded-full p-1 ${match.isNew ? 'bg-gradient-to-br from-primary-500 to-accent-500' : 'bg-gray-200'}`}>
                    <img
                      src={match.photo}
                      alt={match.name}
                      className="w-full h-full rounded-full object-cover"
                    />
                  </div>
                  {match.isNew && (
                    <div className="absolute -top-1 -right-1 w-4 h-4 bg-primary-500 rounded-full border-2 border-white"></div>
                  )}
                </div>
                <p className="mt-2 text-sm font-medium text-gray-900 group-hover:text-primary-600">
                  {match.name}
                </p>
                <p className="text-xs text-gray-500">{match.age}</p>
              </Link>
            ))}
          </div>
        </div>

        {/* All Matches */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Heart className="h-5 w-5 text-primary-500 mr-2" />
            All Matches ({allMatches.length})
          </h2>
          <div className="space-y-4">
            {allMatches.map((match) => (
              <Link
                key={match.id}
                to={`/messages?user=${match.id}`}
                className="card p-4 flex items-center hover:shadow-lg transition-shadow"
              >
                <div className="relative flex-shrink-0">
                  <img
                    src={match.photo}
                    alt={match.name}
                    className="w-16 h-16 rounded-full object-cover"
                  />
                  {match.verified && (
                    <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-accent-500 rounded-full flex items-center justify-center">
                      <Shield className="h-3 w-3 text-white" />
                    </div>
                  )}
                </div>
                <div className="ml-4 flex-grow min-w-0">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-gray-900">
                      {match.name}, {match.age}
                    </h3>
                    <span className="text-xs text-gray-500 flex items-center">
                      <Clock className="h-3 w-3 mr-1" />
                      {match.matchedAt}
                    </span>
                  </div>
                  <div className="flex items-center text-sm text-gray-500 mt-1">
                    <MapPin className="h-3 w-3 mr-1" />
                    {match.location}
                  </div>
                  <p className="text-xs text-gray-400 mt-1">{match.branch}</p>
                  {match.lastMessage && (
                    <p className="text-sm text-gray-600 mt-2 truncate">
                      {match.lastMessage}
                    </p>
                  )}
                </div>
                <div className="ml-4 flex-shrink-0">
                  <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 hover:bg-primary-200 transition-colors">
                    <MessageCircle className="h-5 w-5" />
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Empty State */}
        {allMatches.length === 0 && (
          <div className="text-center py-12">
            <Heart className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No matches yet</h3>
            <p className="text-gray-600 mb-4">
              Keep swiping to find your perfect match!
            </p>
            <Link to="/discover" className="btn-primary">
              Discover People
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}
