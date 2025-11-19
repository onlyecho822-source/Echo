import { useState } from 'react'
import {
  Heart, X, Star, MapPin, Briefcase, GraduationCap, Shield,
  ChevronLeft, ChevronRight, Info, RefreshCw
} from 'lucide-react'

export default function Discover() {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [showDetails, setShowDetails] = useState(false)
  const [swipeDirection, setSwipeDirection] = useState(null)

  const profiles = [
    {
      id: 1,
      name: 'James Wilson',
      age: 35,
      location: 'Austin, Texas',
      occupation: 'Software Engineer',
      education: "Bachelor's in Computer Science",
      branch: 'U.S. Army',
      yearsServed: '8 years',
      bio: 'Proud Army veteran who served two tours overseas. Now working in tech and looking for someone special to share life with. I value loyalty, family, and adventure.',
      interests: ['Hiking', 'Technology', 'Cooking', 'Travel', 'Fitness'],
      photos: [
        'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&h=800&fit=crop',
        'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=600&h=800&fit=crop',
        'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=600&h=800&fit=crop'
      ],
      verified: true
    },
    {
      id: 2,
      name: 'Michael Rodriguez',
      age: 38,
      location: 'San Diego, California',
      occupation: 'Physical Therapist',
      education: 'Doctorate in Physical Therapy',
      branch: 'U.S. Marine Corps',
      yearsServed: '12 years',
      bio: 'Former Marine Corps Sergeant who now helps veterans recover through physical therapy. Family-oriented and ready to settle down. Fluent in Spanish!',
      interests: ['Beach', 'Sports', 'Family', 'Music', 'Volunteering'],
      photos: [
        'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=600&h=800&fit=crop',
        'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=600&h=800&fit=crop',
        'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=600&h=800&fit=crop'
      ],
      verified: true
    },
    {
      id: 3,
      name: 'David Thompson',
      age: 32,
      location: 'Miami, Florida',
      occupation: 'Firefighter',
      education: 'Fire Science Degree',
      branch: 'U.S. Navy',
      yearsServed: '6 years',
      bio: 'Navy veteran turned firefighter. I love helping people and making a difference. Looking for a kind-hearted woman who values commitment and wants to build a future together.',
      interests: ['Fitness', 'Cooking', 'Dogs', 'Movies', 'Dancing'],
      photos: [
        'https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=600&h=800&fit=crop',
        'https://images.unsplash.com/photo-1463453091185-61582044d556?w=600&h=800&fit=crop',
        'https://images.unsplash.com/photo-1528892952291-009c663ce843?w=600&h=800&fit=crop'
      ],
      verified: true
    }
  ]

  const [photoIndex, setPhotoIndex] = useState(0)
  const currentProfile = profiles[currentIndex]

  const handleSwipe = (direction) => {
    setSwipeDirection(direction)
    setTimeout(() => {
      setSwipeDirection(null)
      setPhotoIndex(0)
      setShowDetails(false)
      if (currentIndex < profiles.length - 1) {
        setCurrentIndex(currentIndex + 1)
      } else {
        setCurrentIndex(0) // Loop back
      }
    }, 300)
  }

  const handleSuperLike = () => {
    console.log('Super liked:', currentProfile.name)
    handleSwipe('right')
  }

  if (!currentProfile) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-12 w-12 text-primary-500 mx-auto mb-4 animate-spin" />
          <h2 className="text-xl font-semibold text-gray-900">Finding more matches...</h2>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="max-w-md mx-auto px-4">
        {/* Card */}
        <div className={`relative swipe-card ${swipeDirection === 'left' ? 'swipe-left' : ''} ${swipeDirection === 'right' ? 'swipe-right' : ''}`}>
          <div className="card overflow-hidden">
            {/* Photo */}
            <div className="relative aspect-[3/4]">
              <img
                src={currentProfile.photos[photoIndex]}
                alt={currentProfile.name}
                className="w-full h-full object-cover"
              />

              {/* Photo navigation */}
              <div className="absolute top-4 left-0 right-0 flex justify-center gap-1 px-4">
                {currentProfile.photos.map((_, index) => (
                  <div
                    key={index}
                    className={`h-1 flex-1 rounded-full ${
                      index === photoIndex ? 'bg-white' : 'bg-white/50'
                    }`}
                  />
                ))}
              </div>

              {/* Photo navigation buttons */}
              {photoIndex > 0 && (
                <button
                  onClick={() => setPhotoIndex(photoIndex - 1)}
                  className="absolute left-2 top-1/2 -translate-y-1/2 p-2 bg-black/30 rounded-full text-white hover:bg-black/50"
                >
                  <ChevronLeft className="h-5 w-5" />
                </button>
              )}
              {photoIndex < currentProfile.photos.length - 1 && (
                <button
                  onClick={() => setPhotoIndex(photoIndex + 1)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-black/30 rounded-full text-white hover:bg-black/50"
                >
                  <ChevronRight className="h-5 w-5" />
                </button>
              )}

              {/* Verified badge */}
              {currentProfile.verified && (
                <div className="absolute top-4 right-4 bg-accent-500 text-white px-2 py-1 rounded-full flex items-center text-xs font-medium">
                  <Shield className="h-3 w-3 mr-1" />
                  Verified Veteran
                </div>
              )}

              {/* Info overlay */}
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent p-6 text-white">
                <div className="flex items-end justify-between">
                  <div>
                    <h2 className="text-2xl font-bold">
                      {currentProfile.name}, {currentProfile.age}
                    </h2>
                    <div className="flex items-center text-sm mt-1">
                      <MapPin className="h-4 w-4 mr-1" />
                      {currentProfile.location}
                    </div>
                    <div className="flex items-center text-sm mt-1">
                      <Shield className="h-4 w-4 mr-1" />
                      {currentProfile.branch} • {currentProfile.yearsServed}
                    </div>
                  </div>
                  <button
                    onClick={() => setShowDetails(!showDetails)}
                    className="p-2 bg-white/20 rounded-full hover:bg-white/30 transition-colors"
                  >
                    <Info className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>

            {/* Details Panel */}
            {showDetails && (
              <div className="p-6 border-t">
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">About</h3>
                    <p className="text-gray-600 text-sm">{currentProfile.bio}</p>
                  </div>

                  <div>
                    <div className="flex items-center text-sm text-gray-600 mb-1">
                      <Briefcase className="h-4 w-4 mr-2" />
                      {currentProfile.occupation}
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <GraduationCap className="h-4 w-4 mr-2" />
                      {currentProfile.education}
                    </div>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Interests</h3>
                    <div className="flex flex-wrap gap-2">
                      {currentProfile.interests.map((interest, index) => (
                        <span
                          key={index}
                          className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-xs"
                        >
                          {interest}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-center gap-4 mt-6">
          <button
            onClick={() => handleSwipe('left')}
            className="w-14 h-14 bg-white rounded-full shadow-lg flex items-center justify-center text-gray-400 hover:text-red-500 hover:scale-110 transition-all"
          >
            <X className="h-7 w-7" />
          </button>
          <button
            onClick={handleSuperLike}
            className="w-12 h-12 bg-white rounded-full shadow-lg flex items-center justify-center text-accent-500 hover:text-accent-600 hover:scale-110 transition-all"
          >
            <Star className="h-6 w-6" />
          </button>
          <button
            onClick={() => handleSwipe('right')}
            className="w-14 h-14 bg-white rounded-full shadow-lg flex items-center justify-center text-green-400 hover:text-green-500 hover:scale-110 transition-all"
          >
            <Heart className="h-7 w-7" />
          </button>
        </div>

        <p className="text-center text-sm text-gray-500 mt-4">
          Swipe right to like, left to pass
        </p>
      </div>
    </div>
  )
}
