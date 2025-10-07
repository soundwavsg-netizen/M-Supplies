import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas.chat import (
    ChatSession, ChatMessage, MessageType, AgentType, PageContext
)

class ChatRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.sessions = database.chat_sessions
        self.messages = database.chat_messages

    async def create_session(
        self,
        agent_type: AgentType,
        page_context: PageContext,
        user_id: Optional[str] = None,
        product_context: Optional[Dict[str, Any]] = None,
        cart_context: Optional[Dict[str, Any]] = None
    ) -> ChatSession:
        """Create a new chat session"""
        session_id = f"msupplies_{int(datetime.now().timestamp())}_{str(uuid.uuid4())[:8]}"
        
        session = ChatSession(
            id=session_id,
            user_id=user_id,
            agent_type=agent_type,
            page_context=page_context,
            product_context=product_context,
            cart_context=cart_context,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # Prepare data for MongoDB
        session_data = session.model_dump()
        session_data['created_at'] = session_data['created_at'].isoformat()
        session_data['updated_at'] = session_data['updated_at'].isoformat()
        
        await self.sessions.insert_one(session_data)
        return session

    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a chat session by ID"""
        session_data = await self.sessions.find_one({"id": session_id})
        if not session_data:
            return None
        
        # Parse datetime fields
        if isinstance(session_data.get('created_at'), str):
            session_data['created_at'] = datetime.fromisoformat(session_data['created_at'])
        if isinstance(session_data.get('updated_at'), str):
            session_data['updated_at'] = datetime.fromisoformat(session_data['updated_at'])
        
        return ChatSession(**session_data)

    async def update_session(self, session_id: str, **updates) -> bool:
        """Update a chat session"""
        updates['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        result = await self.sessions.update_one(
            {"id": session_id},
            {"$set": updates}
        )
        return result.modified_count > 0

    async def add_message(
        self,
        session_id: str,
        message_type: MessageType,
        content: str,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatMessage:
        """Add a message to a chat session"""
        message_id = str(uuid.uuid4())
        
        message = ChatMessage(
            id=message_id,
            session_id=session_id,
            type=message_type,
            content=content,
            timestamp=datetime.now(timezone.utc),
            agent_name=agent_name,
            metadata=metadata or {}
        )
        
        # Prepare data for MongoDB
        message_data = message.model_dump()
        message_data['timestamp'] = message_data['timestamp'].isoformat()
        
        await self.messages.insert_one(message_data)
        
        # Update session timestamp
        await self.update_session(session_id)
        
        return message

    async def get_session_messages(
        self, 
        session_id: str, 
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[ChatMessage]:
        """Get messages for a session"""
        query = {"session_id": session_id}
        
        cursor = self.messages.find(query).sort("timestamp", 1)
        
        if offset > 0:
            cursor = cursor.skip(offset)
        if limit:
            cursor = cursor.limit(limit)
        
        messages_data = await cursor.to_list(length=None)
        messages = []
        
        for message_data in messages_data:
            # Parse datetime field
            if isinstance(message_data.get('timestamp'), str):
                message_data['timestamp'] = datetime.fromisoformat(message_data['timestamp'])
            
            messages.append(ChatMessage(**message_data))
        
        return messages

    async def get_user_sessions(
        self, 
        user_id: str, 
        active_only: bool = True,
        limit: int = 20
    ) -> List[ChatSession]:
        """Get sessions for a user"""
        query = {"user_id": user_id}
        if active_only:
            query["is_active"] = True
        
        sessions_data = await self.sessions.find(query)\
            .sort("updated_at", -1)\
            .limit(limit)\
            .to_list(length=None)
        
        sessions = []
        for session_data in sessions_data:
            # Parse datetime fields
            if isinstance(session_data.get('created_at'), str):
                session_data['created_at'] = datetime.fromisoformat(session_data['created_at'])
            if isinstance(session_data.get('updated_at'), str):
                session_data['updated_at'] = datetime.fromisoformat(session_data['updated_at'])
            
            sessions.append(ChatSession(**session_data))
        
        return sessions

    async def close_session(self, session_id: str) -> bool:
        """Close/deactivate a chat session"""
        return await self.update_session(
            session_id, 
            is_active=False,
            updated_at=datetime.now(timezone.utc).isoformat()
        )

    async def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        return await self.sessions.count_documents({"is_active": True})

    async def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """Cleanup sessions older than specified days"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)
        
        # First, get session IDs to cleanup
        old_sessions = await self.sessions.find(
            {"updated_at": {"$lt": cutoff_date.isoformat()}},
            {"id": 1}
        ).to_list(length=None)
        
        session_ids = [session["id"] for session in old_sessions]
        
        if not session_ids:
            return 0
        
        # Delete messages for these sessions
        await self.messages.delete_many({"session_id": {"$in": session_ids}})
        
        # Delete sessions
        result = await self.sessions.delete_many({"id": {"$in": session_ids}})
        
        return result.deleted_count