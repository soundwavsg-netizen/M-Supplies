from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid

class CartRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.carts
    
    async def get_cart(self, user_id: Optional[str] = None, session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        query = {}
        if user_id:
            query['user_id'] = user_id
        elif session_id:
            query['session_id'] = session_id
        else:
            return None
        
        return await self.collection.find_one(query)
    
    async def create_cart(self, user_id: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        cart_data = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'session_id': session_id,
            'items': [],
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        }
        await self.collection.insert_one(cart_data)
        return cart_data
    
    async def update_cart(self, cart_id: str, items: List[Dict[str, Any]]) -> bool:
        result = await self.collection.update_one(
            {'id': cart_id},
            {'$set': {'items': items, 'updated_at': datetime.now(timezone.utc)}}
        )
        return result.modified_count > 0
    
    async def clear_cart(self, cart_id: str) -> bool:
        result = await self.collection.update_one(
            {'id': cart_id},
            {'$set': {'items': [], 'updated_at': datetime.now(timezone.utc)}}
        )
        return result.modified_count > 0
    
    async def delete_cart(self, cart_id: str) -> bool:
        result = await self.collection.delete_one({'id': cart_id})
        return result.deleted_count > 0
