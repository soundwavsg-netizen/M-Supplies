from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid

class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.users
    
    async def create(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        user_data['id'] = str(uuid.uuid4())
        user_data['created_at'] = datetime.now(timezone.utc)
        user_data['is_active'] = True
        user_data['role'] = user_data.get('role', 'customer')
        
        await self.collection.insert_one(user_data)
        return user_data
    
    async def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({'id': user_id})
    
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({'email': email})
    
    async def get_by_uid(self, uid: str) -> Optional[Dict[str, Any]]:
        """Get user by Firebase UID"""
        return await self.collection.find_one({'uid': uid})
    
    async def update(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        result = await self.collection.update_one(
            {'id': user_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    async def list_users(self, skip: int = 0, limit: int = 50, search: Optional[str] = None) -> List[Dict[str, Any]]:
        query = {}
        # Note: Firestore doesn't support $or/$regex - simplified for now
        
        return await self.collection.find(query=query if query else None, skip=skip, limit=limit, sort=[('created_at', -1)])
    
    async def count(self, search: Optional[str] = None) -> int:
        query = {}
        if search:
            query['$or'] = [
                {'email': {'$regex': search, '$options': 'i'}},
                {'first_name': {'$regex': search, '$options': 'i'}},
                {'last_name': {'$regex': search, '$options': 'i'}}
            ]
        return await self.collection.count_documents(query)
