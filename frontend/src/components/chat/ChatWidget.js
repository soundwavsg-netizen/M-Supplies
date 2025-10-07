import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, X, Send, Bot, User, Minimize2, Maximize2, Package, ShoppingBag, HelpCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { toast } from 'sonner';
import { useEmergentAgent } from '@/hooks/useEmergentAgent';

const ChatWidget = ({ 
  agentType = 'main', 
  currentPage = 'homepage',
  productContext = null,
  cartContext = null 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);

  // Use the Emergent agent hook
  const { 
    createSession, 
    sendToAgent, 
    isConnecting, 
    connectionStatus 
  } = useEmergentAgent();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize chat with context-specific welcome message
  useEffect(() => {
    if (isOpen && messages.length === 0 && !sessionId) {
      initializeChat();
    }
  }, [isOpen, currentPage, agentType]);

  const initializeChat = async () => {
    try {
      setIsTyping(true);
      
      const context = {
        agentType: agentType,
        page: currentPage,
        product: productContext,
        cart: cartContext
      };

      const sessionData = await createSession(context);
      
      if (sessionData && sessionData.welcomeMessage) {
        setSessionId(sessionData.sessionId);
        
        const welcomeMessage = {
          id: sessionData.welcomeMessage.message_id || Date.now(),
          type: 'agent',
          content: sessionData.welcomeMessage.content,
          timestamp: new Date(sessionData.welcomeMessage.timestamp) || new Date(),
          agentName: sessionData.welcomeMessage.agent_name,
          avatar: sessionData.welcomeMessage.agent_avatar
        };

        setMessages([welcomeMessage]);

        // Add suggestions if available
        if (sessionData.welcomeMessage.suggestions?.length > 0) {
          setTimeout(() => {
            const suggestionsMessage = {
              id: Date.now() + 1,
              type: 'suggestions',
              suggestions: sessionData.welcomeMessage.suggestions,
              timestamp: new Date()
            };
            setMessages(prev => [...prev, suggestionsMessage]);
          }, 1000);
        }
      }
    } catch (error) {
      console.error('Failed to initialize chat:', error);
      // Fallback to basic welcome message
      const fallbackMessage = {
        id: Date.now(),
        type: 'agent',
        content: "Hello! I'm here to help with M Supplies. How can I assist you today?",
        timestamp: new Date(),
        agentName: "M Supplies Assistant",
        avatar: "🏪"
      };
      setMessages([fallbackMessage]);
      toast.error('Chat initialization failed, but I\'m still here to help!');
    } finally {
      setIsTyping(false);
    }
  };

  const sendMessage = async (messageContent = inputMessage) => {
    if (!messageContent.trim() || !sessionId) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: messageContent,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    try {
      const context = {
        sessionId: sessionId,
        page: currentPage,
        agentType: agentType,
        product: productContext,
        cart: cartContext
      };

      const response = await sendToAgent(messageContent, context);

      const agentMessage = {
        id: response.messageId || Date.now() + 1,
        type: 'agent',
        content: response.content,
        timestamp: new Date(response.timestamp) || new Date(),
        agentName: response.agentName,
        avatar: response.agentAvatar,
        actions: response.actions || []
      };

      setMessages(prev => [...prev, agentMessage]);
    } catch (error) {
      console.error('Agent error:', error);
      
      // Fallback response
      const fallbackMessage = {
        id: Date.now() + 1,
        type: 'agent',
        content: "I apologize, but I'm having trouble processing your request right now. Could you please try again?",
        timestamp: new Date(),
        agentName: "M Supplies Assistant",
        avatar: "🏪"
      };
      
      setMessages(prev => [...prev, fallbackMessage]);
      toast.error('Sorry, I encountered an error. Please try again.');
    } finally {
      setIsTyping(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    sendMessage(suggestion);
  };

  // Get agent config for UI display (fallback when session not ready)
  const getAgentConfig = () => {
    const configs = {
      homepage: {
        main: { name: "M Supplies Assistant", avatar: "🏪" },
        sales: { name: "Sales Expert", avatar: "💼" }
      },
      product: {
        main: { name: "Product Expert", avatar: "📦" },
        sizing: { name: "Sizing Specialist", avatar: "📏" }
      },
      support: {
        main: { name: "Support Team", avatar: "🛠️" },
        care: { name: "Customer Care", avatar: "💝" }
      }
    };
    
    const pageConfig = configs[currentPage] || configs.homepage;
    return pageConfig[agentType] || pageConfig.main;
  };

  const config = getAgentConfig();

  if (!isOpen) {
    return (
      <div className="fixed bottom-20 right-4 z-[9999] pointer-events-none">
        <Button
          onClick={() => setIsOpen(true)}
          className="w-14 h-14 rounded-full bg-teal-600 hover:bg-teal-700 shadow-lg flex items-center justify-center pointer-events-auto"
        >
          <MessageCircle className="w-6 h-6 text-white" />
        </Button>
        
        {/* Agent type indicator */}
        <div className="absolute -top-2 -left-2 pointer-events-auto">
          <Badge variant="secondary" className="text-xs px-2 py-1 bg-white shadow-md">
            {config.avatar} {agentType === 'main' ? 'Assistant' : agentType}
          </Badge>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 z-[9999] pointer-events-none">
      <Card className={`w-96 shadow-xl transition-all duration-300 ${isMinimized ? 'h-16' : 'h-[500px]'} pointer-events-auto`}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 bg-teal-600 text-white rounded-t-lg">
          <div className="flex items-center gap-2">
            <span className="text-lg">{config.avatar}</span>
            <div>
              <h3 className="font-semibold text-sm">{config.name}</h3>
              <p className="text-xs opacity-90">
                {currentPage === 'homepage' ? 'Sales & Support' : 
                 currentPage === 'product' ? 'Product Expert' : 'Customer Care'}
              </p>
            </div>
          </div>
          
          <div className="flex gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsMinimized(!isMinimized)}
              className="text-white hover:bg-white/20 h-8 w-8 p-0"
            >
              {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsOpen(false)}
              className="text-white hover:bg-white/20 h-8 w-8 p-0"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {!isMinimized && (
          <>
            {/* Messages */}
            <CardContent className="p-0 h-80 overflow-y-auto">
              <div className="p-4 space-y-4">
                {messages.map((message) => (
                  <div key={message.id}>
                    {message.type === 'user' ? (
                      <div className="flex justify-end">
                        <div className="max-w-xs bg-teal-600 text-white rounded-lg px-3 py-2 text-sm">
                          {message.content}
                        </div>
                      </div>
                    ) : message.type === 'agent' ? (
                      <div className="flex gap-2">
                        <div className="w-8 h-8 rounded-full bg-teal-100 flex items-center justify-center flex-shrink-0 text-sm">
                          {message.avatar}
                        </div>
                        <div className="flex-1">
                          <div className="bg-gray-100 rounded-lg px-3 py-2 text-sm whitespace-pre-line">
                            {message.content}
                          </div>
                          {message.actions?.length > 0 && (
                            <div className="mt-2 flex gap-2">
                              {message.actions.map((action, index) => (
                                <Button
                                  key={index}
                                  variant="outline"
                                  size="sm"
                                  className="text-xs"
                                >
                                  {action.label}
                                </Button>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    ) : (
                      <div className="flex gap-2 flex-wrap">
                        {message.suggestions.map((suggestion, index) => (
                          <Button
                            key={index}
                            variant="outline"
                            size="sm"
                            className="text-xs mb-1"
                            onClick={() => handleSuggestionClick(suggestion)}
                          >
                            {suggestion}
                          </Button>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
                
                {isTyping && (
                  <div className="flex gap-2">
                    <div className="w-8 h-8 rounded-full bg-teal-100 flex items-center justify-center text-sm">
                      {config.avatar}
                    </div>
                    <div className="bg-gray-100 rounded-lg px-3 py-2 text-sm">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </CardContent>

            {/* Input */}
            <div className="p-3 border-t bg-white rounded-b-lg">
              <div className="flex gap-2">
                <Input
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Type your message..."
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  className="flex-1"
                />
                <Button 
                  onClick={() => sendMessage()}
                  disabled={!inputMessage.trim() || isTyping}
                  size="sm"
                  className="bg-teal-600 hover:bg-teal-700"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </>
        )}
      </Card>
    </div>
  );
};

export default ChatWidget;