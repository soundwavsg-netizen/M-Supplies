import { useState, useCallback } from 'react';

/**
 * Hook to integrate with Emergent Custom Agent via our backend
 */
export const useEmergentAgent = () => {
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');

  // Get backend URL from environment
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

  /**
   * Create a new chat session
   * @param {object} context - Session context (agentType, page, product, cart)
   * @returns {Promise<object>} Session info with welcome message
   */
  const createSession = useCallback(async (context = {}) => {
    try {
      setIsConnecting(true);
      setConnectionStatus('connecting');

      const response = await fetch(`${BACKEND_URL}/api/chat/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          agent_type: context.agentType || 'main',
          page_context: context.page || 'homepage',
          product_context: context.product || null,
          cart_context: context.cart || null,
          user_id: context.userId || null
        })
      });

      if (!response.ok) {
        throw new Error(`Session creation failed: ${response.status}`);
      }

      const data = await response.json();
      setConnectionStatus('connected');

      return {
        sessionId: data.session_id,
        welcomeMessage: data.welcome_message
      };

    } catch (error) {
      console.error('Session creation error:', error);
      setConnectionStatus('error');
      throw error;
    } finally {
      setIsConnecting(false);
    }
  }, [BACKEND_URL]);

  /**
   * Send message to agent
   * @param {string} message - User message
   * @param {object} context - Context information (sessionId, page, product, cart, etc.)
   * @returns {Promise<object>} Agent response
   */
  const sendToAgent = useCallback(async (message, context = {}) => {
    try {
      setIsConnecting(true);
      setConnectionStatus('connecting');

      if (!context.sessionId) {
        throw new Error('Session ID is required');
      }

      const response = await fetch(`${BACKEND_URL}/api/chat/sessions/${context.sessionId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: message,
          session_id: context.sessionId,
          agent_type: context.agentType || 'main',
          page_context: context.page || 'homepage',
          product_context: context.product || null,
          cart_context: context.cart || null
        })
      });

      if (!response.ok) {
        throw new Error(`Message send failed: ${response.status}`);
      }

      const data = await response.json();
      setConnectionStatus('connected');

      return {
        content: data.content,
        actions: data.actions || [],
        suggestions: data.suggestions || [],
        agentName: data.agent_name,
        agentAvatar: data.agent_avatar,
        messageId: data.message_id,
        timestamp: data.timestamp
      };

    } catch (error) {
      console.error('Message send error:', error);
      setConnectionStatus('error');
      
      // Fallback to local responses if backend is unavailable
      return getFallbackResponse(message, context);
    } finally {
      setIsConnecting(false);
    }
  }, [BACKEND_URL]);

  /**
   * Get chat history
   * @param {string} sessionId - Session ID
   * @param {number} limit - Message limit
   * @returns {Promise<Array>} Chat messages
   */
  const getChatHistory = useCallback(async (sessionId, limit = 50) => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/chat/sessions/${sessionId}/history?limit=${limit}`
      );

      if (!response.ok) {
        throw new Error(`History fetch failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('History fetch error:', error);
      return [];
    }
  }, [BACKEND_URL]);

  /**
   * Close chat session
   * @param {string} sessionId - Session ID
   * @returns {Promise<boolean>} Success status
   */
  const closeSession = useCallback(async (sessionId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/chat/sessions/${sessionId}`, {
        method: 'DELETE'
      });

      return response.ok;
    } catch (error) {
      console.error('Session close error:', error);
      return false;
    }
  }, [BACKEND_URL]);

  /**
   * Get specialized sub-agent response based on context
   * @param {string} message - User message
   * @param {object} context - Context with agentType
   * @returns {Promise<object>} Sub-agent response
   */
  const sendToSubAgent = useCallback(async (message, context = {}) => {
    const subAgentContext = {
      ...context,
      specialization: getAgentSpecialization(context.agentType, context.page)
    };

    return sendToAgent(message, subAgentContext);
  }, [sendToAgent]);

  /**
   * Get agent specialization based on page and agent type
   */
  const getAgentSpecialization = (agentType, page) => {
    const specializations = {
      homepage: {
        main: 'general_sales_support',
        sales: 'upsell_and_conversion_expert'
      },
      product: {
        main: 'product_information_expert', 
        sizing: 'sizing_and_recommendation_specialist'
      },
      support: {
        main: 'technical_support_specialist',
        care: 'customer_care_and_satisfaction_expert'
      }
    };

    return specializations[page]?.[agentType] || 'general_assistant';
  };

  /**
   * Fallback responses when backend is unavailable
   */
  const getFallbackResponse = (message, context) => {
    const lowerMessage = message.toLowerCase();
    
    // Basic keyword matching for fallback
    if (lowerMessage.includes('size') || lowerMessage.includes('dimension')) {
      return {
        content: "I'd love to help you find the right size! Could you tell me what you're planning to pack? I can recommend the perfect polymailer dimensions and quantities.",
        actions: [
          { type: 'size_guide', label: 'View Size Guide' },
          { type: 'contact', label: 'Speak to Expert' }
        ],
        agentName: 'M Supplies Assistant',
        agentAvatar: '🏪'
      };
    }

    if (lowerMessage.includes('price') || lowerMessage.includes('cost')) {
      return {
        content: "Our polymailers start from $7.99 with excellent bulk discounts available! Let me help you find the best pricing for your needs.",
        actions: [
          { type: 'view_pricing', label: 'View Pricing' },
          { type: 'bulk_quote', label: 'Get Bulk Quote' }
        ],
        agentName: 'M Supplies Assistant',
        agentAvatar: '🏪'
      };
    }

    if (lowerMessage.includes('track') || lowerMessage.includes('order')) {
      return {
        content: "I can help you track your order! Please provide your order number or email address and I'll get you the latest shipping updates.",
        actions: [
          { type: 'track_order', label: 'Track Order' }
        ],
        agentName: 'M Supplies Assistant',
        agentAvatar: '🏪'
      };
    }

    // Default fallback
    return {
      content: `Thanks for your question! I'm here to help with M Supplies ${context.page === 'product' ? 'product information' : 'and packaging solutions'}. Could you provide more details about what you're looking for?`,
      suggestions: context.page === 'product' 
        ? ['Product specifications', 'Size recommendations', 'Quantity advice']
        : ['Browse products', 'Bulk pricing', 'Customer support'],
      agentName: 'M Supplies Assistant',
      agentAvatar: '🏪'
    };
  };

  /**
   * Initialize agent session with context - creates session and returns welcome message
   */
  const initializeAgent = useCallback(async (context) => {
    try {
      return await createSession(context);
    } catch (error) {
      console.error('Agent initialization error:', error);
      return null;
    }
  }, [createSession]);

  return {
    createSession,
    sendToAgent,
    sendToSubAgent,
    getChatHistory,
    closeSession,
    initializeAgent,
    isConnecting,
    connectionStatus
  };
};

/**
 * Helper hook for getting current page context
 */
export const usePageContext = () => {
  const getPageType = () => {
    const path = window.location.pathname;
    
    if (path === '/' || path === '/home') return 'homepage';
    if (path.startsWith('/products/')) return 'product';
    if (path.includes('/cart') || path.includes('/checkout')) return 'cart';
    if (path.includes('/contact') || path.includes('/faq') || path.includes('/support')) return 'support';
    if (path.includes('/admin')) return 'admin';
    
    return 'other';
  };

  return {
    page: getPageType(),
    path: window.location.pathname,
    params: new URLSearchParams(window.location.search)
  };
};