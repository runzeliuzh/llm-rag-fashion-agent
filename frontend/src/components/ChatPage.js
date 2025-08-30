import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faPaperPlane, 
  faTshirt, 
  faLightbulb, 
  faMagic,
  faShieldAlt,
  faClock,
  faChartBar,
  faExclamationTriangle
} from '@fortawesome/free-solid-svg-icons';
import { apiService } from '../helpers/apiService';

const ChatPage = () => {
  // State for chat messages (initial welcome message)
  const [messages, setMessages] = useState([
    { 
      text: "Hello! I'm an AI fashion assistant built with RAG technology. Ask me about outfits, trends, or styling advice. This is a demonstration of my full-stack AI application.", 
      sender: 'bot' 
    }
  ]);
  // State for user input and loading status
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  // Ref for auto-scrolling chat history
  const chatHistoryRef = useRef(null);
  // Usage tracking
  const [usage, setUsage] = useState(apiService.getUsageSync());
  const [timeUntilReset, setTimeUntilReset] = useState(apiService.formatTimeUntilResetSync());
  // Connection status
  const [isServerConnected, setIsServerConnected] = useState(true);
  const [connectionMessage, setConnectionMessage] = useState("");

  // Load initial usage data
  useEffect(() => {
    const loadUsageData = async () => {
      try {
        const currentUsage = await apiService.getUsage();
        const resetTime = await apiService.formatTimeUntilReset();
        console.log('✅ Loaded usage data:', currentUsage);
        console.log('✅ Reset time:', resetTime);
        console.log('🔍 Server sync status:', currentUsage.serverSync);
        setUsage(currentUsage);
        setTimeUntilReset(resetTime);
        
        // Check if we got server data
        if (currentUsage.serverSync) {
          console.log('✅ Server connected');
          setIsServerConnected(true);
          setConnectionMessage("");
        } else {
          console.log('❌ Server disconnected');
          setIsServerConnected(false);
          setConnectionMessage("⚠️ Backend server is not reachable. Using offline mode.");
        }
      } catch (error) {
        console.log('Failed to load usage data:', error);
        // Fallback to default values
        setUsage({ count: 0, limit: 20, serverSync: false });
        setTimeUntilReset("Unable to connect");
        setIsServerConnected(false);
        setConnectionMessage("❌ Cannot connect to backend server. Please check if the server is running.");
      }
    };
    loadUsageData();
  }, []);

  // Update usage info periodically
  useEffect(() => {
    const updateUsageData = async () => {
      try {
        const currentUsage = await apiService.getUsage();
        const resetTime = await apiService.formatTimeUntilReset();
        setUsage(currentUsage);
        setTimeUntilReset(resetTime);
        
        // Update connection status
        if (currentUsage.serverSync) {
          setIsServerConnected(true);
          setConnectionMessage("");
        } else {
          setIsServerConnected(false);
          setConnectionMessage("⚠️ Backend server is not reachable. Using offline mode.");
        }
      } catch (error) {
        console.log('Failed to update usage data:', error);
        setIsServerConnected(false);
        setConnectionMessage("❌ Cannot connect to backend server. Please check if the server is running.");
      }
    };

    const interval = setInterval(() => {
      updateUsageData();
    }, 10000); // Update every 10 seconds for better connection detection

    return () => clearInterval(interval);
  }, []);

  // Auto-scroll to the bottom of the chat history when messages update
  useEffect(() => {
    if (chatHistoryRef.current) {
      chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [messages]);

  // Handle sending a message
  const handleSendMessage = async () => {
    if (!userInput.trim() || isLoading) return;

    const userMessage = userInput.trim();
    setUserInput('');
    setIsLoading(true);

    // Add user message to chat history
    setMessages(prev => [...prev, { text: userMessage, sender: 'user' }]);

    try {
      const response = await apiService.query(userMessage);
      
      // Add bot response to chat history
      setMessages(prev => [...prev, { 
        text: response.response, 
        sender: 'bot' 
      }]);

      // Update usage info
      if (response.usage) {
        setUsage(response.usage);
      }

    } catch (error) {
      console.error('Chat error:', error);
      let errorMessage = "Sorry, I couldn't process your request. Please try again.";
      
      if (error.message.includes('Rate limit reached')) {
        errorMessage = error.message;
      } else if (error.message.includes('Failed to fetch')) {
        errorMessage = "Connection error. Please check your internet connection and try again.";
      }
      
      setMessages(prev => [...prev, { 
        text: errorMessage, 
        sender: 'bot' 
      }]);
    } finally {
      setIsLoading(false);
      // Refresh usage after request
      const refreshUsageData = async () => {
        try {
          const currentUsage = await apiService.getUsage();
          const resetTime = await apiService.formatTimeUntilReset();
          setUsage(currentUsage);
          setTimeUntilReset(resetTime);
        } catch (error) {
          console.log('Failed to refresh usage data:', error);
        }
      };
      refreshUsageData();
    }
  };

  // Handle Enter key press for sending messages
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const quickPrompts = [
    { icon: faTshirt, text: "What should I wear to a business meeting?" },
    { icon: faLightbulb, text: "What are the latest fashion trends?" },
    { icon: faMagic, text: "Help me style a casual weekend outfit" }
  ];

  const isLimitReached = usage.count >= usage.limit;
  const remainingQueries = usage.limit - usage.count;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-indigo-100">
      <div className="max-w-4xl mx-auto p-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-800 flex items-center">
                <FontAwesomeIcon icon={faShieldAlt} className="text-purple-600 mr-3" />
                AI Fashion Assistant Demo
              </h1>
              <p className="text-gray-600 mt-1">RAG-powered fashion advice with semantic search and LLM generation</p>
            </div>
            
            {/* Usage Information */}
            <div className="text-right">
              <div className="flex items-center space-x-4">
                <div className="bg-purple-50 rounded-lg p-3">
                  <div className="flex items-center text-purple-700">
                    <FontAwesomeIcon icon={faChartBar} className="mr-2" />
                    <span className="font-semibold">{remainingQueries}/{usage.limit}</span>
                  </div>
                  <p className="text-xs text-purple-600">Queries remaining</p>
                </div>
                
                {timeUntilReset !== "Available now" && (
                  <div className="bg-blue-50 rounded-lg p-3">
                    <div className="flex items-center text-blue-700">
                      <FontAwesomeIcon icon={faClock} className="mr-2" />
                      <span className="font-semibold">{timeUntilReset}</span>
                    </div>
                    <p className="text-xs text-blue-600">Until reset</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Connection Status */}
        {!isServerConnected && connectionMessage && (
          <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mb-6 rounded-r-lg">
            <div className="flex items-center">
              <FontAwesomeIcon icon={faExclamationTriangle} className="mr-3 text-lg" />
              <div>
                <p className="font-semibold">Server Connection Status</p>
                <p className="text-sm">{connectionMessage}</p>
                <p className="text-xs mt-1">
                  💡 To start the backend server: Run <code className="bg-yellow-200 px-1 rounded">python start_server.py</code> in the backend folder
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Chat Container */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {/* Chat History */}
          <div 
            ref={chatHistoryRef}
            className="h-[40vh] p-4 overflow-y-auto bg-gray-50 border-b"
          >
            {messages.map((message, index) => (
              <div 
                key={index} 
                className={`mb-3 flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div 
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.sender === 'user' 
                      ? 'bg-purple-600 text-white' 
                      : 'bg-white text-gray-800 border border-gray-200'
                  }`}
                >
                  {message.sender === 'bot' ? (
                    <ReactMarkdown 
                      components={{
                        p: ({children}) => <p className="mb-2 last:mb-0">{children}</p>,
                        strong: ({children}) => <strong className="font-semibold">{children}</strong>,
                        em: ({children}) => <em className="italic">{children}</em>,
                        ul: ({children}) => <ul className="list-disc list-inside mb-2">{children}</ul>,
                        ol: ({children}) => <ol className="list-decimal list-inside mb-2">{children}</ol>,
                        li: ({children}) => <li className="mb-1">{children}</li>
                      }}
                    >
                      {message.text}
                    </ReactMarkdown>
                  ) : (
                    <p>{message.text}</p>
                  )}
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start mb-3">
                <div className="bg-white text-gray-800 border border-gray-200 px-4 py-2 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    <span className="text-sm text-gray-600 ml-2">AI is thinking...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Quick Prompts */}
          <div className="p-4 bg-purple-50 border-b">
            <p className="text-sm text-gray-600 mb-3">Try these example questions:</p>
            <div className="flex flex-wrap gap-2">
              {quickPrompts.map((prompt, index) => (
                <button
                  key={index}
                  onClick={() => setUserInput(prompt.text)}
                  className="flex items-center px-3 py-1 bg-white text-gray-700 rounded-full text-sm hover:bg-purple-100 transition-colors border border-gray-200"
                  disabled={isLoading || isLimitReached || !isServerConnected}
                >
                  <FontAwesomeIcon icon={prompt.icon} className="mr-2 text-purple-600" />
                  {prompt.text}
                </button>
              ))}
            </div>
          </div>

          {/* Input Area */}
          <div className="p-4 bg-white">
            <div className="flex space-x-3">
              <input
                type="text"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={
                  !isServerConnected ? "Backend server not connected..." :
                  isLimitReached ? `Limit reached. Reset in ${timeUntilReset}` : 
                  "Ask about fashion, trends, or styling tips..."
                }
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                disabled={isLoading || isLimitReached || !isServerConnected}
                maxLength={500}
              />
              <button
                onClick={handleSendMessage}
                disabled={isLoading || !userInput.trim() || isLimitReached || !isServerConnected}
                className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center"
              >
                <FontAwesomeIcon icon={faPaperPlane} className="mr-2" />
                Send
              </button>
            </div>
            
            {/* Character count */}
            <div className="mt-2 text-right">
              <span className={`text-xs ${userInput.length > 450 ? 'text-red-500' : 'text-gray-500'}`}>
                {userInput.length}/500 characters
              </span>
            </div>
          </div>
        </div>

        {/* Limit reached notice */}
        {isLimitReached && (
          <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-center">
              <FontAwesomeIcon icon={faClock} className="text-yellow-600 mr-3" />
              <div>
                <h3 className="font-semibold text-yellow-800">Demo Limit Reached</h3>
                <p className="text-yellow-700 text-sm mt-1">
                  You've used all 20 queries in this 5-hour period. Usage resets in {timeUntilReset}.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatPage;
