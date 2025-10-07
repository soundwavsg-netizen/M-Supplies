import os
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

from emergentintegrations.llm.chat import LlmChat, UserMessage

from app.repositories.chat_repository import ChatRepository
from app.schemas.chat import (
    ChatSession, ChatMessage, ChatRequest, ChatResponse,
    MessageType, AgentType, PageContext, CreateSessionRequest
)

# Load environment variables
load_dotenv()

class ChatService:
    def __init__(self, chat_repository: ChatRepository):
        self.chat_repository = chat_repository
        self.llm_key = os.environ.get('EMERGENT_LLM_KEY')
        
        if not self.llm_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")

    async def create_session(self, request: CreateSessionRequest) -> tuple[str, ChatResponse]:
        """Create a new chat session and return welcome message"""
        session = await self.chat_repository.create_session(
            agent_type=request.agent_type,
            page_context=request.page_context,
            user_id=request.user_id,
            product_context=request.product_context,
            cart_context=request.cart_context
        )
        
        # Generate welcome message based on context
        agent_config = self._get_agent_config(
            request.page_context, 
            request.agent_type,
            request.product_context
        )
        
        welcome_message = ChatResponse(
            content=agent_config['welcome_message'],
            agent_name=agent_config['name'],
            agent_avatar=agent_config['avatar'],
            session_id=session.id,
            message_id=str(uuid.uuid4()),
            suggestions=agent_config.get('suggestions', [])
        )
        
        # Store welcome message
        await self.chat_repository.add_message(
            session_id=session.id,
            message_type=MessageType.AGENT,
            content=welcome_message.content,
            agent_name=agent_config['name'],
            metadata={
                'agent_avatar': agent_config['avatar'],
                'suggestions': agent_config.get('suggestions', [])
            }
        )
        
        return session.id, welcome_message

    async def send_message(self, request: ChatRequest) -> ChatResponse:
        """Send a message and get agent response"""
        # Store user message
        user_message = await self.chat_repository.add_message(
            session_id=request.session_id,
            message_type=MessageType.USER,
            content=request.message
        )
        
        # Get session for context
        session = await self.chat_repository.get_session(request.session_id)
        if not session:
            raise ValueError(f"Session {request.session_id} not found")
        
        # Get agent config
        agent_config = self._get_agent_config(
            request.page_context,
            request.agent_type,
            request.product_context
        )
        
        try:
            # Generate response using Emergent AI
            response_content = await self._generate_agent_response(
                message=request.message,
                session=session,
                context={
                    'page': request.page_context,
                    'agent_type': request.agent_type,
                    'product': request.product_context,
                    'cart': request.cart_context
                }
            )
            
        except Exception as e:
            # Fallback to contextual response
            print(f"Agent error: {e}")
            response_content = self._get_fallback_response(request.message, request)
        
        # Store agent response
        response_message = await self.chat_repository.add_message(
            session_id=request.session_id,
            message_type=MessageType.AGENT,
            content=response_content,
            agent_name=agent_config['name'],
            metadata={'agent_avatar': agent_config['avatar']}
        )
        
        return ChatResponse(
            content=response_content,
            agent_name=agent_config['name'],
            agent_avatar=agent_config['avatar'],
            session_id=request.session_id,
            message_id=response_message.id
        )

    async def get_chat_history(self, session_id: str, limit: Optional[int] = 50) -> List[ChatMessage]:
        """Get chat history for a session"""
        return await self.chat_repository.get_session_messages(
            session_id=session_id,
            limit=limit
        )

    async def _generate_agent_response(
        self, 
        message: str, 
        session: ChatSession, 
        context: Dict[str, Any]
    ) -> str:
        """Generate response using Emergent AI LLM"""
        
        # Build system message based on agent type and context
        system_message = self._build_system_message(
            session.agent_type, 
            session.page_context,
            context.get('product'),
            context.get('cart')
        )
        
        # Initialize LLM chat
        chat = LlmChat(
            api_key=self.llm_key,
            session_id=session.id,
            system_message=system_message
        ).with_model("openai", "gpt-4o-mini")
        
        # Get recent conversation history for context
        recent_messages = await self.chat_repository.get_session_messages(
            session.id, limit=6
        )
        
        # Build conversation context
        conversation_context = ""
        if recent_messages:
            conversation_context = "\n\nRecent conversation:\n"
            for msg in recent_messages[-6:]:  # Last 6 messages
                role = "User" if msg.type == MessageType.USER else "Assistant"
                conversation_context += f"{role}: {msg.content}\n"
        
        # Prepare user message with context
        contextual_message = f"{message}{conversation_context}"
        
        user_msg = UserMessage(text=contextual_message)
        response = await chat.send_message(user_msg)
        
        return response

    def _build_system_message(
        self, 
        agent_type: AgentType, 
        page_context: PageContext,
        product_context: Optional[Dict] = None,
        cart_context: Optional[Dict] = None
    ) -> str:
        """Build system message based on agent specialization"""
        
        base_context = """You are an AI assistant for M Supplies, a premium polymailer and packaging supply company. 
M Supplies specializes in high-quality polymailers, bubble wrap packaging, scissors, and tape for e-commerce businesses.

Key product information:
- Premium Polymailers: Available in multiple colors (white, pink, champagne, milktea, black, etc.) and sizes (25x35cm, 32x43cm, 45x60cm, etc.)
- Pack sizes typically: 25pcs, 50pcs, 100pcs per pack
- Pricing starts from $7.99 with bulk discounts available
- Bubble wrap polymailers available (limited to white color only)
- Tools: Packaging scissors and tape available

Company personality: Professional, helpful, solution-focused, with expertise in packaging and logistics.
Always be concise but informative. Use relevant emojis sparingly."""

        if agent_type == AgentType.SALES and page_context == PageContext.HOMEPAGE:
            specialization = """
SPECIALIZATION: Sales Expert & Conversion Specialist
Your role: Drive sales, highlight bulk discounts, VIP programs, and upselling opportunities.
Focus on: Converting visitors to customers, promoting bulk orders, exclusive deals, customer lifetime value.
Key phrases: "bulk savings", "VIP pricing", "exclusive deals", "business solutions"
"""
        elif agent_type == AgentType.SIZING and page_context == PageContext.PRODUCT:
            product_name = product_context.get('name', 'this product') if product_context else 'this product'
            specialization = f"""
SPECIALIZATION: Sizing & Recommendation Specialist
Your role: Help customers find the perfect size and pack quantity for their specific needs.
Current product: {product_name}
Focus on: Precise sizing guidance, pack quantity optimization, shipping considerations, item fit analysis.
Key phrases: "perfect fit", "optimal size", "pack quantity", "shipping efficiency"
"""
        elif agent_type == AgentType.CARE and page_context == PageContext.SUPPORT:
            specialization = """
SPECIALIZATION: Customer Care & Satisfaction Expert
Your role: Provide exceptional customer service, handle complaints, process returns, track orders.
Focus on: Customer satisfaction, problem resolution, policy clarification, order assistance.
Key phrases: "happy to help", "let me resolve this", "customer satisfaction", "exceptional service"
"""
        else:
            # Default/main assistant
            specialization = """
SPECIALIZATION: General Assistant & Product Expert
Your role: Provide helpful information about products, company, and general assistance.
Focus on: Product knowledge, general inquiries, navigation help, basic support.
"""
        
        # Add product context if available
        product_info = ""
        if product_context:
            product_info = f"""
Current product context: {product_context.get('name', 'Product')}
- Price range: {product_context.get('price_range', 'Available on request')}
- Available variants: {len(product_context.get('variants', []))} options
"""
        
        # Add cart context if available
        cart_info = ""
        if cart_context:
            cart_info = f"""
Current cart: {cart_context.get('item_count', 0)} items, Total: ${cart_context.get('total', '0.00')}
"""
        
        return f"{base_context}\n{specialization}\n{product_info}\n{cart_info}"

    def _get_agent_config(
        self, 
        page_context: PageContext, 
        agent_type: AgentType,
        product_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Get agent configuration for UI display"""
        
        configs = {
            PageContext.HOMEPAGE: {
                AgentType.MAIN: {
                    "name": "M Supplies Assistant",
                    "avatar": "🏪",
                    "welcome_message": "Welcome to M Supplies! I'm here to help you find the perfect polymailers and packaging solutions. What can I assist you with today?",
                    "suggestions": ["Show me polymailers", "What sizes do you have?", "Bulk order pricing", "Material recommendations"]
                },
                AgentType.SALES: {
                    "name": "Sales Expert",
                    "avatar": "💼", 
                    "welcome_message": "Hi! I'm your sales specialist. Let me help you find the best packaging solutions and exclusive deals for your business needs!",
                    "suggestions": ["Bulk discounts", "VIP pricing", "Product bundles", "Custom solutions"]
                }
            },
            PageContext.PRODUCT: {
                AgentType.MAIN: {
                    "name": "Product Expert",
                    "avatar": "📦",
                    "welcome_message": f"I'm here to help with {product_context.get('name', 'this product') if product_context else 'this product'}. Ask me about sizing, materials, or recommendations!",
                    "suggestions": ["Right size for me?", "Material benefits", "Quantity recommendations", "Similar products"]
                },
                AgentType.SIZING: {
                    "name": "Sizing Specialist",
                    "avatar": "📏",
                    "welcome_message": "Perfect! I specialize in helping customers find the exact right size. What are you planning to pack?",
                    "suggestions": ["Size calculator", "Dimension guide", "Pack quantity advice", "Shipping considerations"]
                }
            },
            PageContext.SUPPORT: {
                AgentType.MAIN: {
                    "name": "Support Team",
                    "avatar": "🛠️",
                    "welcome_message": "Hello! I'm here to help with any questions or issues. How can I assist you today?",
                    "suggestions": ["Track my order", "Return policy", "Shipping info", "Technical help"]
                },
                AgentType.CARE: {
                    "name": "Customer Care",
                    "avatar": "💝",
                    "welcome_message": "Hi there! I'm your dedicated customer care specialist. Let me help make your experience with M Supplies exceptional!",
                    "suggestions": ["Order support", "Account help", "Feedback", "Special requests"]
                }
            }
        }
        
        page_config = configs.get(page_context, configs[PageContext.HOMEPAGE])
        return page_config.get(agent_type, page_config[AgentType.MAIN])

    def _get_fallback_response(self, message: str, request: ChatRequest) -> str:
        """Fallback response when AI is unavailable"""
        lower_message = message.lower()
        
        # Basic keyword matching for fallback
        if any(word in lower_message for word in ['size', 'dimension', 'fit']):
            return "I'd love to help you find the right size! Could you tell me what you're planning to pack? I can recommend the perfect polymailer dimensions and quantities based on your needs."
        
        if any(word in lower_message for word in ['price', 'cost', 'bulk', 'discount']):
            return "Our polymailers start from $7.99 with excellent bulk discounts available! We offer up to 30% off for larger quantities. Would you like me to calculate pricing for your specific needs?"
        
        if any(word in lower_message for word in ['track', 'order', 'shipping']):
            return "I can help you with order tracking! Please provide your order number or email address and I'll get you the latest shipping updates."
        
        if any(word in lower_message for word in ['material', 'quality', 'bubble']):
            return "Our polymailers are made from high-quality materials. We offer both standard polymailers and bubble wrap polymailers (white only) for extra protection. What type of items will you be shipping?"
        
        # Context-based default responses
        if request.page_context == PageContext.PRODUCT:
            return f"Great question about {request.product_context.get('name', 'this product') if request.product_context else 'this product'}! I'm here to help with sizing, materials, and recommendations. What specific information do you need?"
        elif request.page_context == PageContext.SUPPORT:
            return "I'm here to help resolve any questions or issues you might have. Could you provide more details about what you need assistance with?"
        else:
            return "I'd be happy to help you find the right packaging solutions for your business! Could you tell me more about what you're looking for?"