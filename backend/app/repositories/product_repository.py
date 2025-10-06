from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
from app.schemas.product import ProductFilters, ProductSortOptions

class ProductRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.products = db.products
        self.variants = db.variants
    
    async def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        product_id = str(uuid.uuid4())
        product_data['id'] = product_id
        product_data['created_at'] = datetime.now(timezone.utc)
        product_data['updated_at'] = datetime.now(timezone.utc)
        
        await self.products.insert_one(product_data)
        return product_data
    
    async def create_variant(self, variant_data: Dict[str, Any]) -> Dict[str, Any]:
        variant_data['id'] = str(uuid.uuid4())
        variant_data['created_at'] = datetime.now(timezone.utc)
        
        await self.variants.insert_one(variant_data)
        return variant_data
    
    async def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        return await self.products.find_one({'id': product_id})
    
    async def get_variant_by_id(self, variant_id: str) -> Optional[Dict[str, Any]]:
        return await self.variants.find_one({'id': variant_id})
    
    async def get_variants_by_product(self, product_id: str) -> List[Dict[str, Any]]:
        cursor = self.variants.find({'product_id': product_id})
        return await cursor.to_list(length=100)
    
    async def list_products(self, skip: int = 0, limit: int = 50, category: Optional[str] = None, 
                           search: Optional[str] = None, is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
        query = {}
        if category:
            query['category'] = category
        if is_active is not None:
            query['is_active'] = is_active
        if search:
            query['$or'] = [
                {'name': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}}
            ]
        
        cursor = self.products.find(query).skip(skip).limit(limit).sort('created_at', -1)
        return await cursor.to_list(length=limit)
    
    async def update_product(self, product_id: str, update_data: Dict[str, Any]) -> bool:
        update_data['updated_at'] = datetime.now(timezone.utc)
        result = await self.products.update_one(
            {'id': product_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    async def update_variant(self, variant_id: str, update_data: Dict[str, Any]) -> bool:
        result = await self.variants.update_one(
            {'id': variant_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    async def delete_product(self, product_id: str) -> bool:
        # Soft delete - just mark as inactive
        result = await self.products.update_one(
            {'id': product_id},
            {'$set': {'is_active': False, 'updated_at': datetime.now(timezone.utc)}}
        )
        return result.modified_count > 0
    
    async def get_categories(self) -> List[str]:
        categories = await self.products.distinct('category')
        return categories
