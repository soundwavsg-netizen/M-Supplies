import { useState, useCallback } from 'react';

/**
 * Hook to integrate with Emergent Custom Agent
 * This is where you'll connect to your M Supplies agent
 */
export const useEmergentAgent = () => {
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');

  // Replace these with your actual Emergent agent configuration
  const EMERGENT_AGENT_CONFIG = {
    // Add your agent endpoint or configuration here
    agentId: process.env.REACT_APP_EMERGENT_AGENT_ID || 'msupplies-agent',
    apiKey: process.env.REACT_APP_EMERGENT_API_KEY,
    baseUrl: process.env.REACT_APP_EMERGENT_BASE_URL || 'https://api.emergent.sh'
  };

  /**
   * Send message to Emergent Custom Agent
   * @param {string} message - User message
   * @param {object} context - Context information (page, product, cart, etc.)
   * @returns {Promise<object>} Agent response
   */
  const sendToAgent = useCallback(async (message, context = {}) => {
    try {
      setIsConnecting(true);
      setConnectionStatus('connecting');

      // Prepare the request payload for your Emergent agent
      const payload = {
        message: message,
        context: {
          ...context,
          timestamp: new Date().toISOString(),
          userAgent: navigator.userAgent,
          url: window.location.href
        },
        agentType: context.agentType || 'main',
        sessionId: context.sessionId
      };

      // Example API call structure - adjust based on your Emergent agent setup
      const response = await fetch(`${EMERGENT_AGENT_CONFIG.baseUrl}/agent/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${EMERGENT_AGENT_CONFIG.apiKey}`,
          'X-Agent-ID': EMERGENT_AGENT_CONFIG.agentId
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`Agent request failed: ${response.status}`);
      }

      const data = await response.json();
      setConnectionStatus('connected');

      return {
        content: data.response || data.message,
        actions: data.actions || [],
        suggestions: data.suggestions || [],
        metadata: data.metadata || {}
      };

    } catch (error) {
      console.error('Emergent Agent Error:', error);
      setConnectionStatus('error');
      
      // Fallback to local responses if agent is unavailable
      return getFallbackResponse(message, context);
    } finally {
      setIsConnecting(false);
    }
  }, []);

  /**
   * Get specialized sub-agent response based on context
   * @param {string} message - User message
   * @param {object} context - Context with agentType
   * @returns {Promise<object>} Sub-agent response
   */
  const sendToSubAgent = useCallback(async (message, context = {}) => {
    const subAgentContext = {
      ...context,
      isSubAgent: true,
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
   * Fallback responses when Emergent agent is unavailable
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
        ]
      };
    }

    if (lowerMessage.includes('price') || lowerMessage.includes('cost')) {
      return {
        content: "Our polymailers start from $7.99 with excellent bulk discounts available! Let me help you find the best pricing for your needs.",
        actions: [
          { type: 'view_pricing', label: 'View Pricing' },
          { type: 'bulk_quote', label: 'Get Bulk Quote' }
        ]
      };
    }

    if (lowerMessage.includes('track') || lowerMessage.includes('order')) {
      return {
        content: "I can help you track your order! Please provide your order number or email address and I'll get you the latest shipping updates.",
        actions: [
          { type: 'track_order', label: 'Track Order' }
        ]
      };
    }

    // Default fallback
    return {
      content: `Thanks for your question! I'm here to help with M Supplies ${context.page === 'product' ? 'product information' : 'and packaging solutions'}. Could you provide more details about what you're looking for?`,
      suggestions: context.page === 'product' 
        ? ['Product specifications', 'Size recommendations', 'Quantity advice']
        : ['Browse products', 'Bulk pricing', 'Customer support']
    };
  };

  /**
   * Initialize agent session with context
   */
  const initializeAgent = useCallback(async (context) => {
    try {
      const initMessage = `User visiting ${context.page} page${context.product ? ` for ${context.product.name}` : ''}`;
      await sendToAgent(initMessage, { ...context, isInitialization: true });
    } catch (error) {
      console.error('Agent initialization error:', error);
    }
  }, [sendToAgent]);

  return {
    sendToAgent,
    sendToSubAgent,
    initializeAgent,
    isConnecting,
    connectionStatus,
    config: EMERGENT_AGENT_CONFIG
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