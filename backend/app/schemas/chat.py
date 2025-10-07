from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"

class AgentType(str, Enum):
    MAIN = "main"
    SALES = "sales"
    SIZING = "sizing"
    SUPPORT = "support"
    CARE = "care"

class PageContext(str, Enum):
    HOMEPAGE = "homepage"
    PRODUCT = "product"
    SUPPORT = "support"
    CART = "cart"
    ADMIN = "admin"
    OTHER = "other"

class ChatMessage(BaseModel):
    id: str = Field(..., description="Unique message ID")
    session_id: str = Field(..., description="Chat session ID")
    type: MessageType = Field(..., description="Message type")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    agent_name: Optional[str] = Field(None, description="Agent name for agent messages")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional message metadata")

class ChatSession(BaseModel):
    id: str = Field(..., description="Unique session ID")
    user_id: Optional[str] = Field(None, description="User ID if authenticated")
    agent_type: AgentType = Field(AgentType.MAIN, description="Agent type for this session")
    page_context: PageContext = Field(PageContext.HOMEPAGE, description="Page context")
    product_context: Optional[Dict[str, Any]] = Field(None, description="Product context if on product page")
    cart_context: Optional[Dict[str, Any]] = Field(None, description="Cart context if relevant")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session creation time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    is_active: bool = Field(True, description="Session status")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional session metadata")

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    session_id: str = Field(..., description="Chat session ID")
    agent_type: AgentType = Field(AgentType.MAIN, description="Agent type")
    page_context: PageContext = Field(PageContext.HOMEPAGE, description="Current page context")
    product_context: Optional[Dict[str, Any]] = Field(None, description="Product context")
    cart_context: Optional[Dict[str, Any]] = Field(None, description="Cart context")

class ChatResponse(BaseModel):
    content: str = Field(..., description="Agent response content")
    actions: Optional[List[Dict[str, str]]] = Field(default_factory=list, description="Suggested actions")
    suggestions: Optional[List[str]] = Field(default_factory=list, description="Quick reply suggestions")
    agent_name: str = Field(..., description="Agent name")
    agent_avatar: str = Field(..., description="Agent avatar emoji")
    session_id: str = Field(..., description="Session ID")
    message_id: str = Field(..., description="Response message ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional response metadata")

class ChatHistory(BaseModel):
    session_id: str = Field(..., description="Session ID")
    messages: List[ChatMessage] = Field(..., description="List of messages")
    session_info: ChatSession = Field(..., description="Session information")

# Request/Response models for API endpoints
class CreateSessionRequest(BaseModel):
    agent_type: AgentType = Field(AgentType.MAIN, description="Agent type")
    page_context: PageContext = Field(PageContext.HOMEPAGE, description="Page context")
    product_context: Optional[Dict[str, Any]] = Field(None, description="Product context")
    cart_context: Optional[Dict[str, Any]] = Field(None, description="Cart context")
    user_id: Optional[str] = Field(None, description="User ID if authenticated")

class CreateSessionResponse(BaseModel):
    session_id: str = Field(..., description="Created session ID")
    welcome_message: ChatResponse = Field(..., description="Initial welcome message")