import { useState } from 'react'
import {
  User, Mail, MapPin, Calendar, Camera, Heart, Edit2, Save,
  Shield, Award, Briefcase, GraduationCap, Languages
} from 'lucide-react'

export default function Profile() {
  const [isEditing, setIsEditing] = useState(false)
  const [profile, setProfile] = useState({
    firstName: 'María',
    lastName: 'González',
    email: 'maria.gonzalez@email.com',
    birthDate: '1992-03-15',
    country: 'Dominican Republic',
    city: 'Santo Domingo',
    bio: 'Soy una mujer cariñosa y familiar que valora la honestidad y el respeto. Me encanta cocinar, bailar y pasar tiempo con mi familia. Busco un hombre comprometido y serio para una relación duradera.',
    occupation: 'Teacher',
    education: "Bachelor's Degree",
    languages: ['Spanish', 'English (Basic)'],
    interests: ['Cooking', 'Dancing', 'Family time', 'Beach', 'Music'],
    lookingFor: 'Long-term relationship',
    photos: [
      'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=400&fit=crop',
      'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&h=400&fit=crop',
      'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400&h=400&fit=crop'
    ]
  })

  const handleSave = () => {
    setIsEditing(false)
    // Save profile logic
    console.log('Profile saved:', profile)
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Profile Header */}
        <div className="card mb-6 overflow-hidden">
          <div className="h-32 bg-gradient-to-r from-primary-500 to-accent-500"></div>
          <div className="px-6 pb-6">
            <div className="flex flex-col sm:flex-row items-center sm:items-end -mt-16 sm:-mt-12">
              <div className="relative">
                <img
                  src={profile.photos[0]}
                  alt={profile.firstName}
                  className="w-32 h-32 rounded-full border-4 border-white object-cover shadow-lg"
                />
                <button className="absolute bottom-0 right-0 p-2 bg-primary-500 text-white rounded-full hover:bg-primary-600 transition-colors">
                  <Camera className="h-4 w-4" />
                </button>
              </div>
              <div className="mt-4 sm:mt-0 sm:ml-6 text-center sm:text-left flex-grow">
                <h1 className="text-2xl font-bold text-gray-900">
                  {profile.firstName} {profile.lastName}
                </h1>
                <div className="flex items-center justify-center sm:justify-start text-gray-600 mt-1">
                  <MapPin className="h-4 w-4 mr-1" />
                  <span>{profile.city}, {profile.country}</span>
                </div>
              </div>
              <button
                onClick={() => isEditing ? handleSave() : setIsEditing(true)}
                className={`mt-4 sm:mt-0 ${isEditing ? 'btn-gold' : 'btn-secondary'} flex items-center`}
              >
                {isEditing ? (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Save Changes
                  </>
                ) : (
                  <>
                    <Edit2 className="h-4 w-4 mr-2" />
                    Edit Profile
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {/* Left Column - Photos */}
          <div className="md:col-span-1">
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Photos</h2>
              <div className="grid grid-cols-2 gap-2">
                {profile.photos.map((photo, index) => (
                  <div key={index} className="relative aspect-square rounded-lg overflow-hidden">
                    <img src={photo} alt={`Photo ${index + 1}`} className="w-full h-full object-cover" />
                  </div>
                ))}
                <button className="aspect-square rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center hover:border-primary-500 transition-colors">
                  <Camera className="h-6 w-6 text-gray-400" />
                </button>
              </div>
            </div>

            {/* Verification Status */}
            <div className="card p-6 mt-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Verification</h2>
              <div className="space-y-3">
                <div className="flex items-center text-green-600">
                  <Shield className="h-5 w-5 mr-2" />
                  <span className="text-sm">Email Verified</span>
                </div>
                <div className="flex items-center text-green-600">
                  <Shield className="h-5 w-5 mr-2" />
                  <span className="text-sm">Phone Verified</span>
                </div>
                <div className="flex items-center text-gray-400">
                  <Shield className="h-5 w-5 mr-2" />
                  <span className="text-sm">ID Pending</span>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Details */}
          <div className="md:col-span-2 space-y-6">
            {/* About Me */}
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">About Me</h2>
              {isEditing ? (
                <textarea
                  value={profile.bio}
                  onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                  className="input-field h-32 resize-none"
                  placeholder="Tell others about yourself..."
                />
              ) : (
                <p className="text-gray-600">{profile.bio}</p>
              )}
            </div>

            {/* Basic Info */}
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
              <div className="grid sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">
                    <Mail className="h-4 w-4 inline mr-1" />
                    Email
                  </label>
                  {isEditing ? (
                    <input
                      type="email"
                      value={profile.email}
                      onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                      className="input-field"
                    />
                  ) : (
                    <p className="text-gray-900">{profile.email}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">
                    <Calendar className="h-4 w-4 inline mr-1" />
                    Birthday
                  </label>
                  {isEditing ? (
                    <input
                      type="date"
                      value={profile.birthDate}
                      onChange={(e) => setProfile({ ...profile, birthDate: e.target.value })}
                      className="input-field"
                    />
                  ) : (
                    <p className="text-gray-900">{new Date(profile.birthDate).toLocaleDateString()}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">
                    <Briefcase className="h-4 w-4 inline mr-1" />
                    Occupation
                  </label>
                  {isEditing ? (
                    <input
                      type="text"
                      value={profile.occupation}
                      onChange={(e) => setProfile({ ...profile, occupation: e.target.value })}
                      className="input-field"
                    />
                  ) : (
                    <p className="text-gray-900">{profile.occupation}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">
                    <GraduationCap className="h-4 w-4 inline mr-1" />
                    Education
                  </label>
                  {isEditing ? (
                    <input
                      type="text"
                      value={profile.education}
                      onChange={(e) => setProfile({ ...profile, education: e.target.value })}
                      className="input-field"
                    />
                  ) : (
                    <p className="text-gray-900">{profile.education}</p>
                  )}
                </div>
              </div>
            </div>

            {/* Languages */}
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                <Languages className="h-5 w-5 inline mr-2" />
                Languages
              </h2>
              <div className="flex flex-wrap gap-2">
                {profile.languages.map((lang, index) => (
                  <span key={index} className="px-3 py-1 bg-accent-100 text-accent-700 rounded-full text-sm">
                    {lang}
                  </span>
                ))}
              </div>
            </div>

            {/* Interests */}
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                <Heart className="h-5 w-5 inline mr-2" />
                Interests
              </h2>
              <div className="flex flex-wrap gap-2">
                {profile.interests.map((interest, index) => (
                  <span key={index} className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm">
                    {interest}
                  </span>
                ))}
              </div>
            </div>

            {/* Looking For */}
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                <Award className="h-5 w-5 inline mr-2" />
                Looking For
              </h2>
              <p className="text-gray-600">{profile.lookingFor}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
