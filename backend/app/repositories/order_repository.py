from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid

class OrderRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.orders
    
    async def create(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        order_data['id'] = str(uuid.uuid4())
        order_data['order_number'] = self._generate_order_number()
        order_data['created_at'] = datetime.now(timezone.utc)
        order_data['updated_at'] = datetime.now(timezone.utc)
        order_data['status'] = order_data.get('status', 'pending')
        
        await self.collection.insert_one(order_data)
        return order_data
    
    def _generate_order_number(self) -> str:
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        random_suffix = str(uuid.uuid4())[:6].upper()
        return f"ORD-{timestamp}-{random_suffix}"
    
    async def get_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({'id': order_id})
    
    async def get_by_order_number(self, order_number: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({'order_number': order_number})
    
    async def list_user_orders(self, user_id: str, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        return await self.collection.find(
            query={'user_id': user_id},
            skip=skip,
            limit=limit,
            sort=[('created_at', -1)]
        )
    
    async def list_orders(self, skip: int = 0, limit: int = 50, status: Optional[str] = None,
                         search: Optional[str] = None) -> List[Dict[str, Any]]:
        query = {}
        if status:
            query['status'] = status
        if search:
            query['$or'] = [
                {'order_number': {'$regex': search, '$options': 'i'}},
                {'guest_email': {'$regex': search, '$options': 'i'}},
                {'shipping_address.email': {'$regex': search, '$options': 'i'}}
            ]
        
        cursor = self.collection.find(query).skip(skip).limit(limit).sort('created_at', -1)
        return await cursor.to_list(length=limit)
    
    async def update(self, order_id: str, update_data: Dict[str, Any]) -> bool:
        update_data['updated_at'] = datetime.now(timezone.utc)
        result = await self.collection.update_one(
            {'id': order_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    async def count(self, status: Optional[str] = None) -> int:
        query = {}
        if status:
            query['status'] = status
        return await self.collection.count_documents(query)
