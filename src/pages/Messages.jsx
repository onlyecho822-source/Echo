import { useState } from 'react'
import {
  Send, Image, Smile, Phone, Video, MoreVertical,
  ChevronLeft, Shield, Search
} from 'lucide-react'

export default function Messages() {
  const [selectedChat, setSelectedChat] = useState(null)
  const [message, setMessage] = useState('')

  const conversations = [
    {
      id: 1,
      name: 'James Wilson',
      photo: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop',
      lastMessage: 'Hey! Nice to match with you!',
      time: '2:30 PM',
      unread: 2,
      online: true,
      verified: true,
      messages: [
        { id: 1, text: 'Hi there! I saw we matched.', sender: 'them', time: '2:15 PM' },
        { id: 2, text: 'Hello! Yes, nice to meet you!', sender: 'me', time: '2:20 PM' },
        { id: 3, text: 'How are you doing today?', sender: 'them', time: '2:25 PM' },
        { id: 4, text: 'Hey! Nice to match with you!', sender: 'them', time: '2:30 PM' }
      ]
    },
    {
      id: 2,
      name: 'Michael Rodriguez',
      photo: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150&h=150&fit=crop',
      lastMessage: 'I would love to learn more about Dominican culture!',
      time: '11:45 AM',
      unread: 0,
      online: false,
      verified: true,
      messages: [
        { id: 1, text: 'Hola! I speak some Spanish too.', sender: 'them', time: '11:00 AM' },
        { id: 2, text: 'That is wonderful! Where did you learn?', sender: 'me', time: '11:15 AM' },
        { id: 3, text: 'I learned during my service and have been practicing.', sender: 'them', time: '11:30 AM' },
        { id: 4, text: 'I would love to learn more about Dominican culture!', sender: 'them', time: '11:45 AM' }
      ]
    },
    {
      id: 3,
      name: 'David Thompson',
      photo: 'https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=150&h=150&fit=crop',
      lastMessage: 'Would you like to video chat sometime?',
      time: 'Yesterday',
      unread: 1,
      online: true,
      verified: true,
      messages: [
        { id: 1, text: 'I see you like dancing! What kind of music?', sender: 'them', time: 'Yesterday' },
        { id: 2, text: 'I love merengue and bachata!', sender: 'me', time: 'Yesterday' },
        { id: 3, text: 'That is great! I have been learning salsa.', sender: 'them', time: 'Yesterday' },
        { id: 4, text: 'Would you like to video chat sometime?', sender: 'them', time: 'Yesterday' }
      ]
    }
  ]

  const handleSendMessage = (e) => {
    e.preventDefault()
    if (!message.trim()) return
    console.log('Sending message:', message)
    setMessage('')
  }

  const currentConversation = conversations.find(c => c.id === selectedChat)

  return (
    <div className="min-h-[calc(100vh-200px)] bg-gray-50">
      <div className="max-w-6xl mx-auto h-[calc(100vh-200px)]">
        <div className="flex h-full card overflow-hidden">
          {/* Conversation List */}
          <div className={`w-full md:w-1/3 border-r bg-white ${selectedChat ? 'hidden md:block' : ''}`}>
            {/* Search Header */}
            <div className="p-4 border-b">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search messages..."
                  className="w-full pl-10 pr-4 py-2 bg-gray-100 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-primary-200"
                />
              </div>
            </div>

            {/* Conversations */}
            <div className="overflow-y-auto h-[calc(100%-73px)]">
              {conversations.map((conv) => (
                <button
                  key={conv.id}
                  onClick={() => setSelectedChat(conv.id)}
                  className={`w-full p-4 flex items-center hover:bg-gray-50 transition-colors border-b
                    ${selectedChat === conv.id ? 'bg-primary-50' : ''}`}
                >
                  <div className="relative flex-shrink-0">
                    <img
                      src={conv.photo}
                      alt={conv.name}
                      className="w-12 h-12 rounded-full object-cover"
                    />
                    {conv.online && (
                      <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
                    )}
                  </div>
                  <div className="ml-3 flex-grow text-left min-w-0">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold text-gray-900 flex items-center">
                        {conv.name}
                        {conv.verified && (
                          <Shield className="h-3 w-3 text-accent-500 ml-1" />
                        )}
                      </h3>
                      <span className="text-xs text-gray-500">{conv.time}</span>
                    </div>
                    <p className="text-sm text-gray-600 truncate">{conv.lastMessage}</p>
                  </div>
                  {conv.unread > 0 && (
                    <div className="ml-2 w-5 h-5 bg-primary-500 rounded-full flex items-center justify-center">
                      <span className="text-xs text-white font-medium">{conv.unread}</span>
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Chat Area */}
          <div className={`flex-1 flex flex-col ${!selectedChat ? 'hidden md:flex' : ''}`}>
            {currentConversation ? (
              <>
                {/* Chat Header */}
                <div className="p-4 border-b bg-white flex items-center justify-between">
                  <div className="flex items-center">
                    <button
                      onClick={() => setSelectedChat(null)}
                      className="md:hidden mr-2 p-1 hover:bg-gray-100 rounded"
                    >
                      <ChevronLeft className="h-5 w-5" />
                    </button>
                    <img
                      src={currentConversation.photo}
                      alt={currentConversation.name}
                      className="w-10 h-10 rounded-full object-cover"
                    />
                    <div className="ml-3">
                      <h3 className="font-semibold text-gray-900 flex items-center">
                        {currentConversation.name}
                        {currentConversation.verified && (
                          <Shield className="h-3 w-3 text-accent-500 ml-1" />
                        )}
                      </h3>
                      <p className="text-xs text-gray-500">
                        {currentConversation.online ? 'Online' : 'Offline'}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button className="p-2 hover:bg-gray-100 rounded-full text-gray-600">
                      <Phone className="h-5 w-5" />
                    </button>
                    <button className="p-2 hover:bg-gray-100 rounded-full text-gray-600">
                      <Video className="h-5 w-5" />
                    </button>
                    <button className="p-2 hover:bg-gray-100 rounded-full text-gray-600">
                      <MoreVertical className="h-5 w-5" />
                    </button>
                  </div>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
                  {currentConversation.messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`flex ${msg.sender === 'me' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[70%] px-4 py-2 rounded-2xl ${
                          msg.sender === 'me'
                            ? 'bg-primary-500 text-white rounded-br-md'
                            : 'bg-white text-gray-900 rounded-bl-md shadow-sm'
                        }`}
                      >
                        <p className="text-sm">{msg.text}</p>
                        <p className={`text-xs mt-1 ${
                          msg.sender === 'me' ? 'text-primary-100' : 'text-gray-500'
                        }`}>
                          {msg.time}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Message Input */}
                <div className="p-4 bg-white border-t">
                  <form onSubmit={handleSendMessage} className="flex items-center gap-2">
                    <button type="button" className="p-2 hover:bg-gray-100 rounded-full text-gray-600">
                      <Image className="h-5 w-5" />
                    </button>
                    <button type="button" className="p-2 hover:bg-gray-100 rounded-full text-gray-600">
                      <Smile className="h-5 w-5" />
                    </button>
                    <input
                      type="text"
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      placeholder="Type a message..."
                      className="flex-1 px-4 py-2 bg-gray-100 rounded-full focus:outline-none focus:ring-2 focus:ring-primary-200"
                    />
                    <button
                      type="submit"
                      disabled={!message.trim()}
                      className="p-2 bg-primary-500 text-white rounded-full hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      <Send className="h-5 w-5" />
                    </button>
                  </form>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-center p-8">
                <div>
                  <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Send className="h-8 w-8 text-gray-400" />
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Select a conversation
                  </h3>
                  <p className="text-gray-600">
                    Choose from your existing matches to start chatting
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
