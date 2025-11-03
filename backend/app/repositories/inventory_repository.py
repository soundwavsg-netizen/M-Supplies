from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid

class InventoryLedgerRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.inventory_ledger
    
    async def create_entry(self, entry_data: Dict[str, Any]) -> Dict[str, Any]:
        entry_data['id'] = str(uuid.uuid4())
        entry_data['created_at'] = datetime.now(timezone.utc)
        
        await self.collection.insert_one(entry_data)
        return entry_data
    
    async def get_by_variant(self, variant_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        return await self.collection.find(query={'variant_id': variant_id}, skip=skip, limit=limit, sort=[('created_at', -1)])
    
    async def get_by_reference(self, reference_id: str) -> List[Dict[str, Any]]:
        return await self.collection.find(query={'reference_id': reference_id}, limit=100)
    
    async def get_recent(self, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        return await self.collection.find(query=None, skip=skip, limit=limit, sort=[('created_at', -1)])

class ChannelMappingRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.channel_mappings
    
    async def create(self, mapping_data: Dict[str, Any]) -> Dict[str, Any]:
        mapping_data['id'] = str(uuid.uuid4())
        mapping_data['created_at'] = datetime.now(timezone.utc)
        mapping_data['is_active'] = True
        
        await self.collection.insert_one(mapping_data)
        return mapping_data
    
    async def get_by_external_sku(self, channel: str, external_sku: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({
            'channel': channel,
            'external_sku': external_sku,
            'is_active': True
        })
    
    async def get_by_variant(self, variant_id: str) -> List[Dict[str, Any]]:
        return await self.collection.find(query={'internal_variant_id': variant_id, 'is_active': True}, limit=100)
    
    async def list_by_channel(self, channel: str) -> List[Dict[str, Any]]:
        return await self.collection.find(query={'channel': channel, 'is_active': True}, limit=1000)
    
    async def update(self, mapping_id: str, update_data: Dict[str, Any]) -> bool:
        result = await self.collection.update_one(
            {'id': mapping_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    async def delete(self, mapping_id: str) -> bool:
        result = await self.collection.update_one(
            {'id': mapping_id},
            {'$set': {'is_active': False}}
        )
        return result.modified_count > 0

class SettingsRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.settings
    
    async def get_settings(self) -> Dict[str, Any]:
        settings = await self.collection.find_one({'type': 'business'})
        if not settings:
            # Create default settings
            settings = {
                'id': str(uuid.uuid4()),
                'type': 'business',
                'business_name': 'M Supplies',
                'currency': 'SGD',
                'gst_percent': 9.0,
                'default_safety_stock': 5,
                'low_stock_threshold': 10,
                'channel_buffers': {
                    'website': 0,
                    'shopee': 2,
                    'lazada': 2
                },
                'created_at': datetime.now(timezone.utc)
            }
            await self.collection.insert_one(settings)
        return settings
    
    async def update_settings(self, update_data: Dict[str, Any]) -> bool:
        result = await self.collection.update_one(
            {'type': 'business'},
            {'$set': update_data}
        )
        return result.modified_count > 0
