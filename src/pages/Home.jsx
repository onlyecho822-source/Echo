import { Link } from 'react-router-dom'
import {
  Heart, Shield, Globe, Star, Users, MessageCircle,
  CheckCircle, ArrowRight, Sparkles, Award, MapPin
} from 'lucide-react'

export default function Home() {
  const features = [
    {
      icon: Shield,
      title: 'Verified Veterans',
      description: 'All veteran profiles are verified to ensure authenticity and security for everyone.'
    },
    {
      icon: Globe,
      title: 'Cultural Bridge',
      description: 'Connect across cultures with bilingual support and cultural understanding.'
    },
    {
      icon: Heart,
      title: 'Real Connections',
      description: 'Our matching algorithm focuses on compatibility for lasting relationships.'
    },
    {
      icon: MessageCircle,
      title: 'Safe Communication',
      description: 'Secure messaging with translation support to help you communicate.'
    }
  ]

  const testimonials = [
    {
      name: 'María García',
      location: 'Santo Domingo, RD',
      text: 'I found my soulmate through VetLove. He served in the Army and is the most caring person I\'ve ever met. We\'re now happily married!',
      image: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&h=150&fit=crop&crop=face'
    },
    {
      name: 'James Wilson',
      location: 'Texas, USA',
      text: 'After my service, I wanted to find someone who valued family and commitment. VetLove connected me with my beautiful wife from Colombia.',
      image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face'
    },
    {
      name: 'Carolina Mendez',
      location: 'Bogotá, Colombia',
      text: 'The respect and dedication veterans have is exactly what I was looking for. Thank you VetLove for this blessing!',
      image: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face'
    }
  ]

  const stats = [
    { number: '50K+', label: 'Active Members' },
    { number: '10K+', label: 'Successful Matches' },
    { number: '25+', label: 'Countries' },
    { number: '98%', label: 'Satisfaction Rate' }
  ]

  return (
    <div className="overflow-hidden">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-primary-600 via-primary-700 to-accent-700 text-white py-20 lg:py-32">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="absolute top-20 left-10 w-72 h-72 bg-gold-400/20 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-accent-400/20 rounded-full blur-3xl"></div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="text-center lg:text-left">
              <div className="inline-flex items-center px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full mb-6">
                <Sparkles className="h-4 w-4 text-gold-400 mr-2" />
                <span className="text-sm font-medium">Join thousands finding love</span>
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6 leading-tight">
                Where Latin Hearts Meet
                <span className="block text-gold-300">American Heroes</span>
              </h1>

              <p className="text-lg sm:text-xl text-white/90 mb-8 max-w-xl">
                Connect with verified American veterans looking for meaningful relationships.
                Especially designed for Dominican and Latin American women seeking love with honor.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                <Link to="/register" className="btn-gold inline-flex items-center justify-center">
                  Start Your Journey
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
                <Link to="/about" className="btn-secondary bg-white/10 border-white/30 text-white hover:bg-white/20">
                  Learn More
                </Link>
              </div>

              <div className="mt-8 flex items-center justify-center lg:justify-start space-x-6 text-sm">
                <div className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-400 mr-2" />
                  <span>Free to Join</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-green-400 mr-2" />
                  <span>Verified Profiles</span>
                </div>
              </div>
            </div>

            <div className="hidden lg:block relative">
              <div className="relative w-full h-[500px]">
                {/* Decorative cards */}
                <div className="absolute top-0 right-0 w-64 h-80 bg-white rounded-2xl shadow-2xl transform rotate-6 overflow-hidden">
                  <img
                    src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&h=500&fit=crop"
                    alt="Profile"
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="absolute top-20 left-0 w-64 h-80 bg-white rounded-2xl shadow-2xl transform -rotate-6 overflow-hidden">
                  <img
                    src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=500&fit=crop"
                    alt="Profile"
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2">
                  <Heart className="h-16 w-16 text-primary-300 fill-primary-300 animate-pulse-heart" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-white py-12 -mt-8 relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              {stats.map((stat, index) => (
                <div key={index} className="text-center">
                  <div className="text-3xl sm:text-4xl font-bold text-primary-600 mb-2">
                    {stat.number}
                  </div>
                  <div className="text-gray-600 text-sm sm:text-base">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Why Choose <span className="gradient-text">VetLove</span>?
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              We provide a safe, secure, and culturally-aware platform for meaningful connections
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="card p-6 text-center group hover:-translate-y-2 transition-transform duration-300">
                <div className="inline-flex items-center justify-center w-14 h-14 bg-primary-100 rounded-xl mb-4 group-hover:bg-primary-500 transition-colors">
                  <feature.icon className="h-7 w-7 text-primary-600 group-hover:text-white transition-colors" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600 text-sm">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-lg text-gray-600">
              Finding your perfect match is easy with VetLove
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center mx-auto mb-4 text-white text-2xl font-bold">
                1
              </div>
              <h3 className="text-xl font-semibold mb-2">Create Your Profile</h3>
              <p className="text-gray-600">
                Sign up for free and create a detailed profile that showcases who you are and what you're looking for.
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-accent-500 to-accent-600 rounded-full flex items-center justify-center mx-auto mb-4 text-white text-2xl font-bold">
                2
              </div>
              <h3 className="text-xl font-semibold mb-2">Discover Matches</h3>
              <p className="text-gray-600">
                Browse verified profiles and use our smart matching to find compatible partners who share your values.
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-gold-500 to-gold-600 rounded-full flex items-center justify-center mx-auto mb-4 text-white text-2xl font-bold">
                3
              </div>
              <h3 className="text-xl font-semibold mb-2">Connect & Chat</h3>
              <p className="text-gray-600">
                Start conversations with your matches using our secure messaging system with translation support.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 bg-gradient-to-br from-gray-50 to-primary-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Love Stories
            </h2>
            <p className="text-lg text-gray-600">
              Real couples who found their match on VetLove
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="card p-6">
                <div className="flex items-center mb-4">
                  <img
                    src={testimonial.image}
                    alt={testimonial.name}
                    className="w-12 h-12 rounded-full object-cover mr-4"
                  />
                  <div>
                    <h4 className="font-semibold text-gray-900">{testimonial.name}</h4>
                    <div className="flex items-center text-sm text-gray-500">
                      <MapPin className="h-3 w-3 mr-1" />
                      {testimonial.location}
                    </div>
                  </div>
                </div>
                <div className="flex mb-3">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-4 w-4 text-gold-400 fill-gold-400" />
                  ))}
                </div>
                <p className="text-gray-600 text-sm italic">"{testimonial.text}"</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-primary-600 to-accent-600 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <Award className="h-16 w-16 mx-auto mb-6 text-gold-300" />
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Ready to Find Your Hero?
          </h2>
          <p className="text-lg text-white/90 mb-8 max-w-2xl mx-auto">
            Join thousands of Latin American women who have found love with American veterans.
            Your story could be next!
          </p>
          <Link to="/register" className="btn-gold text-lg px-8 py-4 inline-flex items-center">
            Create Free Account
            <Heart className="ml-2 h-5 w-5" />
          </Link>
          <p className="mt-4 text-sm text-white/70">
            No credit card required. 100% free to join.
          </p>
        </div>
      </section>
    </div>
  )
}
