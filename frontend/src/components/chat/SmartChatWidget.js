import React from 'react';
import { useLocation } from 'react-router-dom';
import ChatWidget from '@/components/chat/ChatWidget';

/**
 * Smart Chat Widget that automatically determines agent type and context based on current page
 */
const SmartChatWidget = ({ 
  productContext = null, 
  cartContext = null,
  overrideAgentType = null,
  overridePageContext = null 
}) => {
  const location = useLocation();
  
  // Determine page context and agent type based on current route
  const getContextFromRoute = () => {
    const pathname = location.pathname;
    
    // Allow manual overrides
    if (overridePageContext && overrideAgentType) {
      return {
        pageContext: overridePageContext,
        agentType: overrideAgentType
      };
    }
    
    // Homepage - Sales expert for conversion and business solutions
    if (pathname === '/' || pathname === '/home') {
      return {
        pageContext: 'homepage',
        agentType: 'sales'
      };
    }
    
    // Product pages - Sizing specialist for product-specific guidance
    if (pathname.startsWith('/products/') || pathname === '/products') {
      return {
        pageContext: 'product',
        agentType: 'sizing'
      };
    }
    
    // Support pages - Customer care specialist
    if (pathname.includes('/contact') || pathname.includes('/faq') || pathname.includes('/support')) {
      return {
        pageContext: 'support',
        agentType: 'care'
      };
    }
    
    // Cart/Checkout - Sales expert to help with final conversion
    if (pathname.includes('/cart') || pathname.includes('/checkout')) {
      return {
        pageContext: 'homepage', // Use homepage config for sales context
        agentType: 'sales'
      };
    }
    
    // Admin pages - Main assistant
    if (pathname.includes('/admin')) {
      return {
        pageContext: 'support',
        agentType: 'main'
      };
    }
    
    // About page - Main assistant
    if (pathname.includes('/about')) {
      return {
        pageContext: 'homepage',
        agentType: 'main'
      };
    }
    
    // Default fallback
    return {
      pageContext: 'homepage',
      agentType: 'main'
    };
  };
  
  const { pageContext, agentType } = getContextFromRoute();
  
  return (
    <ChatWidget
      agentType={agentType}
      currentPage={pageContext}
      productContext={productContext}
      cartContext={cartContext}
    />
  );
};

export default SmartChatWidget;