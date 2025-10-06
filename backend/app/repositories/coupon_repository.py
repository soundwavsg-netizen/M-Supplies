from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid

class CouponRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.coupons
    
    async def create(self, coupon_data: Dict[str, Any]) -> Dict[str, Any]:
        coupon_data['id'] = str(uuid.uuid4())
        coupon_data['created_at'] = datetime.now(timezone.utc)
        coupon_data['used_count'] = 0
        
        await self.collection.insert_one(coupon_data)
        return coupon_data
    
    async def get_by_id(self, coupon_id: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({'id': coupon_id})
    
    async def get_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({'code': code.upper()})
    
    async def list_coupons(self, skip: int = 0, limit: int = 50, is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
        query = {}
        if is_active is not None:
            query['is_active'] = is_active
        
        cursor = self.collection.find(query).skip(skip).limit(limit).sort('created_at', -1)
        return await cursor.to_list(length=limit)
    
    async def update(self, coupon_id: str, update_data: Dict[str, Any]) -> bool:
        result = await self.collection.update_one(
            {'id': coupon_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    async def increment_usage(self, coupon_id: str) -> bool:
        result = await self.collection.update_one(
            {'id': coupon_id},
            {'$inc': {'used_count': 1}}
        )
        return result.modified_count > 0
    
    async def delete(self, coupon_id: str) -> bool:
        result = await self.collection.delete_one({'id': coupon_id})
        return result.deleted_count > 0
