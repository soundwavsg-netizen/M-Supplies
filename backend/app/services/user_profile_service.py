from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from app.repositories.user_profile_repository import UserProfileRepository, AddressRepository
from app.schemas.user import UserProfile, UserAddress, AddressCreate, AddressUpdate, UserUpdate

class UserProfileService:
    def __init__(self, user_repo: UserProfileRepository, address_repo: AddressRepository):
        self.user_repo = user_repo
        self.address_repo = address_repo

    async def get_user_profile(self, uid: str) -> UserProfile:
        """Get user profile by UID"""
        user = await self.user_repo.get_user_profile(uid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        return user

    async def update_user_profile(self, uid: str, updates: UserUpdate) -> UserProfile:
        """Update user profile"""
        # Check if user exists
        user = await self.get_user_profile(uid)
        
        # Prepare updates
        update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
        
        if not update_data:
            return user
        
        success = await self.user_repo.update_user_profile(uid, update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update profile"
            )
        
        return await self.get_user_profile(uid)

    # Address Management
    async def create_address(self, uid: str, address_data: AddressCreate) -> UserAddress:
        """Create a new address for user"""
        # Check address limit (max 5)
        address_count = await self.address_repo.count_user_addresses(uid)
        if address_count >= 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 5 addresses allowed per user"
            )
        
        # If user has no addresses, automatically set as default
        if address_count == 0:
            address_data.isDefault = True
        
        address = await self.address_repo.create_address(uid, address_data)
        
        # Update user's defaultAddressId if this is their first or default address
        if address.isDefault:
            await self.user_repo.update_user_profile(uid, {
                "defaultAddressId": address.id,
                "lastUsedAddressId": address.id
            })
        
        return address

    async def get_user_addresses(self, uid: str) -> List[UserAddress]:
        """Get all addresses for a user"""
        return await self.address_repo.get_user_addresses(uid)

    async def get_address(self, address_id: str, uid: str) -> UserAddress:
        """Get specific address"""
        address = await self.address_repo.get_address_by_id(address_id, uid)
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found"
            )
        return address

    async def update_address(self, address_id: str, uid: str, updates: AddressUpdate) -> UserAddress:
        """Update an address"""
        # Verify address exists
        await self.get_address(address_id, uid)
        
        success = await self.address_repo.update_address(address_id, uid, updates)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update address"
            )
        
        updated_address = await self.get_address(address_id, uid)
        
        # Update user's defaultAddressId if this was set as default
        if updated_address.isDefault:
            await self.user_repo.update_user_profile(uid, {
                "defaultAddressId": updated_address.id,
                "lastUsedAddressId": updated_address.id
            })
        
        return updated_address

    async def delete_address(self, address_id: str, uid: str) -> bool:
        """Delete an address"""
        # Verify address exists
        address = await self.get_address(address_id, uid)
        
        success = await self.address_repo.delete_address(address_id, uid)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete address"
            )
        
        # If deleted address was default, update user profile
        if address.isDefault:
            # Find new default (repository handles promotion)
            new_default = await self.address_repo.get_default_address(uid)
            if new_default:
                await self.user_repo.update_user_profile(uid, {
                    "defaultAddressId": new_default.id
                })
            else:
                await self.user_repo.update_user_profile(uid, {
                    "defaultAddressId": None
                })
        
        return True

    async def set_default_address(self, address_id: str, uid: str) -> UserAddress:
        """Set an address as default"""
        # Verify address exists and belongs to user
        await self.get_address(address_id, uid)
        
        success = await self.address_repo.set_default_address(address_id, uid)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to set default address"
            )
        
        # Update user profile
        await self.user_repo.update_user_profile(uid, {
            "defaultAddressId": address_id,
            "lastUsedAddressId": address_id
        })
        
        return await self.get_address(address_id, uid)

    async def get_default_address(self, uid: str) -> Optional[UserAddress]:
        """Get user's default address"""
        return await self.address_repo.get_default_address(uid)

    # Admin functionality
    async def list_all_users_for_admin(
        self, 
        limit: int = 100, 
        offset: int = 0, 
        search: Optional[str] = None,
        country_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """List users for admin with additional info"""
        users = await self.user_repo.list_users(limit, offset, search, country_filter)
        
        # Enhance with address and order info
        enhanced_users = []
        for user in users:
            default_address = await self.get_default_address(user.uid)
            
            # Get order count (placeholder - implement when order system is updated)
            order_count = 0  # TODO: Implement order counting
            
            enhanced_users.append({
                "profile": user,
                "defaultAddress": default_address,
                "orderCount": order_count,
                "lastOrderDate": None  # TODO: Implement last order date
            })
        
        total_count = await self.user_repo.users.count_documents({"is_active": True})
        
        return {
            "users": enhanced_users,
            "totalCount": total_count,
            "currentPage": (offset // limit) + 1 if limit > 0 else 1,
            "totalPages": (total_count + limit - 1) // limit if limit > 0 else 1
        }