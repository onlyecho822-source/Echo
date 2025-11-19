import { Link } from 'react-router-dom'
import {
  Heart, Shield, Globe, Users, Award, Target,
  CheckCircle, Mail, MapPin, Phone
} from 'lucide-react'

export default function About() {
  const values = [
    {
      icon: Shield,
      title: 'Safety First',
      description: 'We verify all veteran profiles and provide secure communication tools to protect our members.'
    },
    {
      icon: Heart,
      title: 'Authentic Connections',
      description: 'We focus on meaningful relationships built on shared values, not just surface-level matching.'
    },
    {
      icon: Globe,
      title: 'Cultural Understanding',
      description: 'We bridge cultures with bilingual support and resources to help couples navigate differences.'
    },
    {
      icon: Users,
      title: 'Community Support',
      description: 'We provide resources and support for both veterans and their partners throughout their journey.'
    }
  ]

  const team = [
    {
      name: 'Sarah Mitchell',
      role: 'Founder & CEO',
      bio: 'Army veteran and relationship counselor with a passion for helping others find love.',
      image: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=300&h=300&fit=crop'
    },
    {
      name: 'Carlos Ramirez',
      role: 'Head of Community',
      bio: 'Born in Dominican Republic, Carlos bridges cultures and ensures our platform serves both communities.',
      image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop'
    },
    {
      name: 'Jennifer Wong',
      role: 'Safety Director',
      bio: 'Former cybersecurity specialist ensuring our platform remains safe and secure for all members.',
      image: 'https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=300&h=300&fit=crop'
    }
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-600 to-accent-600 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl sm:text-5xl font-bold mb-6">
            About VetLove
          </h1>
          <p className="text-xl text-white/90 max-w-3xl mx-auto">
            We're on a mission to connect Latin American hearts with American heroes,
            creating meaningful relationships built on respect, honor, and love.
          </p>
        </div>
      </section>

      {/* Our Story */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-6">Our Story</h2>
              <div className="space-y-4 text-gray-600">
                <p>
                  VetLove was founded in 2020 by Sarah Mitchell, a U.S. Army veteran who
                  witnessed firsthand the challenges veterans face in finding meaningful
                  relationships after service.
                </p>
                <p>
                  During her deployment in Latin America, Sarah was struck by the warmth,
                  family values, and genuine nature of the women she met. She realized that
                  many veterans share these same values and could find compatible partners
                  among Latin American women seeking stability and commitment.
                </p>
                <p>
                  Today, VetLove has helped thousands of couples find love, with a special
                  focus on connecting Dominican and Latin American women with American
                  veterans who are ready for serious, committed relationships.
                </p>
              </div>
            </div>
            <div className="relative">
              <img
                src="https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=600&h=400&fit=crop"
                alt="Happy couple"
                className="rounded-2xl shadow-xl"
              />
              <div className="absolute -bottom-6 -left-6 bg-white p-4 rounded-xl shadow-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                    <Heart className="h-6 w-6 text-primary-600 fill-primary-600" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-gray-900">10,000+</p>
                    <p className="text-sm text-gray-600">Success Stories</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Our Mission */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <Target className="h-12 w-12 text-primary-600 mx-auto mb-6" />
          <h2 className="text-3xl font-bold text-gray-900 mb-6">Our Mission</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-12">
            To provide a safe, respectful platform that honors the service of American
            veterans while celebrating the rich culture of Latin America, creating lasting
            relationships built on shared values.
          </p>

          <div className="grid md:grid-cols-4 gap-8">
            {values.map((value, index) => (
              <div key={index} className="text-center">
                <div className="inline-flex items-center justify-center w-14 h-14 bg-primary-100 rounded-xl mb-4">
                  <value.icon className="h-7 w-7 text-primary-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{value.title}</h3>
                <p className="text-sm text-gray-600">{value.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Why Veterans & Latinas */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
            Why This Connection Works
          </h2>

          <div className="grid md:grid-cols-2 gap-12">
            <div className="card p-8">
              <div className="flex items-center mb-6">
                <Shield className="h-8 w-8 text-accent-600 mr-3" />
                <h3 className="text-xl font-semibold text-gray-900">American Veterans</h3>
              </div>
              <ul className="space-y-3">
                {[
                  'Value loyalty and commitment',
                  'Appreciate strong family bonds',
                  'Seek genuine, lasting relationships',
                  'Offer stability and security',
                  'Respect traditional values'
                ].map((item, i) => (
                  <li key={i} className="flex items-center text-gray-600">
                    <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            <div className="card p-8">
              <div className="flex items-center mb-6">
                <Heart className="h-8 w-8 text-primary-600 mr-3" />
                <h3 className="text-xl font-semibold text-gray-900">Latin American Women</h3>
              </div>
              <ul className="space-y-3">
                {[
                  'Strong family-oriented values',
                  'Warm and caring nature',
                  'Appreciate dedication and honor',
                  'Seek committed relationships',
                  'Value respect and communication'
                ].map((item, i) => (
                  <li key={i} className="flex items-center text-gray-600">
                    <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Team */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Meet Our Team</h2>
            <p className="text-gray-600">
              Dedicated professionals committed to helping you find love
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {team.map((member, index) => (
              <div key={index} className="card p-6 text-center">
                <img
                  src={member.image}
                  alt={member.name}
                  className="w-24 h-24 rounded-full mx-auto mb-4 object-cover"
                />
                <h3 className="text-lg font-semibold text-gray-900">{member.name}</h3>
                <p className="text-primary-600 text-sm mb-3">{member.role}</p>
                <p className="text-gray-600 text-sm">{member.bio}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-6">Get in Touch</h2>
              <p className="text-gray-600 mb-8">
                Have questions about VetLove? We're here to help. Reach out to our
                support team and we'll get back to you as soon as possible.
              </p>

              <div className="space-y-4">
                <div className="flex items-center">
                  <Mail className="h-5 w-5 text-primary-600 mr-3" />
                  <span className="text-gray-600">support@vetlove.com</span>
                </div>
                <div className="flex items-center">
                  <Phone className="h-5 w-5 text-primary-600 mr-3" />
                  <span className="text-gray-600">1-800-VET-LOVE</span>
                </div>
                <div className="flex items-center">
                  <MapPin className="h-5 w-5 text-primary-600 mr-3" />
                  <span className="text-gray-600">Austin, Texas, USA</span>
                </div>
              </div>
            </div>

            <div className="card p-8">
              <form className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Name
                  </label>
                  <input type="text" className="input-field" placeholder="Your name" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <input type="email" className="input-field" placeholder="your@email.com" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Message
                  </label>
                  <textarea
                    rows={4}
                    className="input-field resize-none"
                    placeholder="How can we help?"
                  ></textarea>
                </div>
                <button type="submit" className="w-full btn-primary">
                  Send Message
                </button>
              </form>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 bg-gradient-to-r from-primary-600 to-accent-600 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <Award className="h-12 w-12 mx-auto mb-4 text-gold-300" />
          <h2 className="text-2xl sm:text-3xl font-bold mb-4">
            Ready to Start Your Journey?
          </h2>
          <p className="text-white/90 mb-8">
            Join thousands who have found love on VetLove
          </p>
          <Link to="/register" className="btn-gold">
            Create Free Account
          </Link>
        </div>
      </section>
    </div>
  )
}
