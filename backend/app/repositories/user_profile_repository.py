import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas.user import UserProfile, UserAddress, AddressCreate, AddressUpdate

class UserProfileRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.users = database.users
        self.addresses = database.user_addresses

    async def create_user_profile(
        self,
        email: str,
        display_name: str,
        phone: Optional[str] = None,
        role: str = "customer"
    ) -> UserProfile:
        """Create a new user profile with Firebase-compatible structure"""
        uid = str(uuid.uuid4())
        
        user_profile = UserProfile(
            uid=uid,
            displayName=display_name,
            email=email,
            phone=phone,
            role=role,
            createdAt=datetime.now(timezone.utc),
            updatedAt=datetime.now(timezone.utc)
        )
        
        # Prepare data for MongoDB
        user_data = user_profile.model_dump()
        user_data['createdAt'] = user_data['createdAt'].isoformat()
        user_data['updatedAt'] = user_data['updatedAt'].isoformat()
        
        await self.users.insert_one(user_data)
        return user_profile

    async def get_user_profile(self, uid: str) -> Optional[UserProfile]:
        """Get user profile by UID"""
        user_data = await self.users.find_one({"id": uid})  # Use 'id' field, same as auth
        if not user_data:
            return None
        
        # Transform legacy data to Firebase format if needed
        firebase_data = self._transform_legacy_to_firebase(user_data)
        return UserProfile(**firebase_data)

    async def get_user_by_email(self, email: str) -> Optional[UserProfile]:
        """Get user profile by email"""
        user_data = await self.users.find_one({"email": email})
        if not user_data:
            return None
        
        firebase_data = self._transform_legacy_to_firebase(user_data)
        return UserProfile(**firebase_data)

    def _transform_legacy_to_firebase(self, user_data: dict) -> dict:
        """Transform legacy user data to Firebase-compatible format"""
        return {
            "uid": user_data.get("id"),
            "displayName": f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
            "email": user_data.get("email"),
            "phone": user_data.get("phone"),
            "role": user_data.get("role", "customer"),
            "defaultAddressId": user_data.get("defaultAddressId"),
            "lastUsedAddressId": user_data.get("lastUsedAddressId"),
            "is_active": user_data.get("is_active", True),
            "createdAt": user_data.get("created_at") if isinstance(user_data.get("created_at"), datetime) else datetime.fromisoformat(user_data["created_at"]) if user_data.get("created_at") else datetime.now(timezone.utc),
            "updatedAt": user_data.get("updated_at") if isinstance(user_data.get("updated_at"), datetime) else datetime.fromisoformat(user_data["updated_at"]) if user_data.get("updated_at") else datetime.now(timezone.utc)
        }

    async def update_user_profile(self, uid: str, updates: Dict[str, Any]) -> bool:
        """Update user profile"""
        updates['updatedAt'] = datetime.now(timezone.utc).isoformat()
        
        result = await self.users.update_one(
            {"id": uid},  # Use 'id' field, same as auth
            {"$set": updates}
        )
        return result.modified_count > 0

    async def delete_user_profile(self, uid: str) -> bool:
        """Soft delete user profile"""
        return await self.update_user_profile(uid, {"is_active": False})

    async def list_users(self, limit: int = 50, offset: int = 0, search: Optional[str] = None, country_filter: Optional[str] = None) -> List[UserProfile]:
        """List users with filtering and pagination"""
        query = {"is_active": True}
        
        # Add search filter
        if search:
            search_regex = {"$regex": search, "$options": "i"}
            query["$or"] = [
                {"displayName": search_regex},
                {"email": search_regex},
                {"phone": search_regex}
            ]
        
        cursor = self.users.find(query).sort("createdAt", -1)
        
        if offset > 0:
            cursor = cursor.skip(offset)
        if limit > 0:
            cursor = cursor.limit(limit)
        
        users_data = await cursor.to_list(length=None)
        users = []
        
        for user_data in users_data:
            # Parse datetime fields
            if isinstance(user_data.get('createdAt'), str):
                user_data['createdAt'] = datetime.fromisoformat(user_data['createdAt'])
            if isinstance(user_data.get('updatedAt'), str):
                user_data['updatedAt'] = datetime.fromisoformat(user_data['updatedAt'])
            
            users.append(UserProfile(**user_data))
        
        return users


class AddressRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.addresses = database.user_addresses

    async def create_address(self, uid: str, address_data: AddressCreate) -> UserAddress:
        """Create a new address for a user"""
        address_id = str(uuid.uuid4())
        
        # If this is set as default, unset other defaults for this user
        if address_data.isDefault:
            await self.clear_default_addresses(uid)
        
        address = UserAddress(
            id=address_id,
            uid=uid,
            **address_data.model_dump(),
            createdAt=datetime.now(timezone.utc),
            updatedAt=datetime.now(timezone.utc)
        )
        
        # Prepare data for MongoDB
        address_data_dict = address.model_dump()
        address_data_dict['createdAt'] = address_data_dict['createdAt'].isoformat()
        address_data_dict['updatedAt'] = address_data_dict['updatedAt'].isoformat()
        
        await self.addresses.insert_one(address_data_dict)
        return address

    async def get_user_addresses(self, uid: str) -> List[UserAddress]:
        """Get all addresses for a user"""
        addresses_data = await self.addresses.find({"uid": uid}).sort("isDefault", -1).to_list(length=None)
        addresses = []
        
        for addr_data in addresses_data:
            # Parse datetime fields
            if isinstance(addr_data.get('createdAt'), str):
                addr_data['createdAt'] = datetime.fromisoformat(addr_data['createdAt'])
            if isinstance(addr_data.get('updatedAt'), str):
                addr_data['updatedAt'] = datetime.fromisoformat(addr_data['updatedAt'])
            
            addresses.append(UserAddress(**addr_data))
        
        return addresses

    async def get_address_by_id(self, address_id: str, uid: str) -> Optional[UserAddress]:
        """Get specific address by ID and user"""
        addr_data = await self.addresses.find_one({"id": address_id, "uid": uid})
        if not addr_data:
            return None
        
        # Parse datetime fields
        if isinstance(addr_data.get('createdAt'), str):
            addr_data['createdAt'] = datetime.fromisoformat(addr_data['createdAt'])
        if isinstance(addr_data.get('updatedAt'), str):
            addr_data['updatedAt'] = datetime.fromisoformat(addr_data['updatedAt'])
        
        return UserAddress(**addr_data)

    async def get_default_address(self, uid: str) -> Optional[UserAddress]:
        """Get user's default address"""
        addr_data = await self.addresses.find_one({"uid": uid, "isDefault": True})
        if not addr_data:
            return None
        
        # Parse datetime fields
        if isinstance(addr_data.get('createdAt'), str):
            addr_data['createdAt'] = datetime.fromisoformat(addr_data['createdAt'])
        if isinstance(addr_data.get('updatedAt'), str):
            addr_data['updatedAt'] = datetime.fromisoformat(addr_data['updatedAt'])
        
        return UserAddress(**addr_data)

    async def update_address(self, address_id: str, uid: str, updates: AddressUpdate) -> bool:
        """Update an address"""
        update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
        update_data['updatedAt'] = datetime.now(timezone.utc).isoformat()
        
        # If setting as default, clear other defaults
        if update_data.get('isDefault'):
            await self.clear_default_addresses(uid)
        
        result = await self.addresses.update_one(
            {"id": address_id, "uid": uid},
            {"$set": update_data}
        )
        return result.modified_count > 0

    async def delete_address(self, address_id: str, uid: str) -> bool:
        """Delete an address"""
        # Check if this is the default address
        address = await self.get_address_by_id(address_id, uid)
        if address and address.isDefault:
            # Set another address as default if available
            await self.promote_next_default_address(uid, address_id)
        
        result = await self.addresses.delete_one({"id": address_id, "uid": uid})
        return result.deleted_count > 0

    async def clear_default_addresses(self, uid: str):
        """Clear all default flags for a user"""
        await self.addresses.update_many(
            {"uid": uid, "isDefault": True},
            {"$set": {"isDefault": False, "updatedAt": datetime.now(timezone.utc).isoformat()}}
        )

    async def promote_next_default_address(self, uid: str, excluding_id: str):
        """Set the next available address as default when current default is deleted"""
        next_address = await self.addresses.find_one({
            "uid": uid,
            "id": {"$ne": excluding_id}
        })
        
        if next_address:
            await self.addresses.update_one(
                {"id": next_address["id"]},
                {"$set": {"isDefault": True, "updatedAt": datetime.now(timezone.utc).isoformat()}}
            )

    async def count_user_addresses(self, uid: str) -> int:
        """Count addresses for a user"""
        return await self.addresses.count_documents({"uid": uid})

    async def set_default_address(self, address_id: str, uid: str) -> bool:
        """Set an address as default"""
        # First clear all defaults
        await self.clear_default_addresses(uid)
        
        # Set the specified address as default
        result = await self.addresses.update_one(
            {"id": address_id, "uid": uid},
            {"$set": {"isDefault": True, "updatedAt": datetime.now(timezone.utc).isoformat()}}
        )
        
        return result.modified_count > 0