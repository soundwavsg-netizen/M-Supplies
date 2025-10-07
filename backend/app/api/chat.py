from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

from app.services.chat_service import ChatService
from app.repositories.chat_repository import ChatRepository
from app.core.database import get_database
from app.schemas.chat import (
    CreateSessionRequest, CreateSessionResponse, ChatRequest, ChatResponse,
    ChatHistory, ChatMessage
)

router = APIRouter()

async def get_chat_service() -> ChatService:
    """Dependency to get chat service"""
    db = await get_database()
    chat_repository = ChatRepository(db)
    return ChatService(chat_repository)

@router.post("/sessions", response_model=CreateSessionResponse)
async def create_chat_session(
    request: CreateSessionRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Create a new chat session"""
    try:
        session_id, welcome_message = await chat_service.create_session(request)
        return CreateSessionResponse(
            session_id=session_id,
            welcome_message=welcome_message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@router.post("/sessions/{session_id}/messages", response_model=ChatResponse)
async def send_message(
    session_id: str,
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Send a message in a chat session"""
    # Ensure session_id matches
    request.session_id = session_id
    
    try:
        response = await chat_service.send_message(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

@router.get("/sessions/{session_id}/history", response_model=List[ChatMessage])
async def get_chat_history(
    session_id: str,
    limit: Optional[int] = 50,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get chat history for a session"""
    try:
        messages = await chat_service.get_chat_history(session_id, limit)
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@router.delete("/sessions/{session_id}")
async def close_chat_session(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Close a chat session"""
    try:
        success = await chat_service.chat_repository.close_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Session closed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to close session: {str(e)}")

# Health check endpoint
@router.get("/health")
async def chat_health_check():
    """Health check for chat system"""
    return {"status": "healthy", "service": "chat"}