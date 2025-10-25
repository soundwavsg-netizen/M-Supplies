from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.schemas.user import UserProfile, UserResponse, UserUpdate, AddressCreate, AddressUpdate, AddressResponse
from app.services.user_profile_service import UserProfileService
from app.repositories.user_profile_repository import UserProfileRepository, AddressRepository
from app.core.database import get_database
from app.core.security import get_current_user_id

router = APIRouter()

async def get_user_profile_service() -> UserProfileService:
    """Dependency to get user profile service"""
    db = get_database()
    user_repo = UserProfileRepository(db)
    address_repo = AddressRepository(db)
    return UserProfileService(user_repo, address_repo)

# Profile Management
@router.get("/me", response_model=UserProfile)
async def get_my_profile(
    user_id: str = Depends(get_current_user_id),
    service: UserProfileService = Depends(get_user_profile_service)
):
    """Get current user's profile"""
    return await service.get_user_profile(user_id)

@router.put("/me", response_model=UserProfile)
async def update_my_profile(
    updates: UserUpdate,
    user_id: str = Depends(get_current_user_id),
    service: UserProfileService = Depends(get_user_profile_service)
):
    """Update current user's profile"""
    return await service.update_user_profile(user_id, updates)

# Address Management
@router.get("/me/addresses", response_model=List[AddressResponse])
async def get_my_addresses(
    user_id: str = Depends(get_current_user_id),
    service: UserProfileService = Depends(get_user_profile_service)
):
    """Get current user's addresses"""
    return await service.get_user_addresses(user_id)

@router.post("/me/addresses", response_model=AddressResponse)
async def create_address(
    address_data: AddressCreate,
    user_id: str = Depends(get_current_user_id),
    service: UserProfileService = Depends(get_user_profile_service)
):
    """Create a new address"""
    return await service.create_address(user_id, address_data)

@router.get("/me/addresses/{address_id}", response_model=AddressResponse)
async def get_address(
    address_id: str,
    user_id: str = Depends(get_current_user_id),
    service: UserProfileService = Depends(get_user_profile_service)
):
    """Get specific address"""
    return await service.get_address(address_id, user_id)

@router.put("/me/addresses/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: str,
    updates: AddressUpdate,
    user_id: str = Depends(get_current_user_id),
    service: UserProfileService = Depends(get_user_profile_service)
):
    """Update an address"""
    return await service.update_address(address_id, user_id, updates)

@router.delete("/me/addresses/{address_id}")
async def delete_address(
    address_id: str,
    user_id: str = Depends(get_current_user_id),
    service: UserProfileService = Depends(get_user_profile_service)
):
    """Delete an address"""
    success = await service.delete_address(address_id, user_id)
    if success:
        return {"message": "Address deleted successfully"}
    raise HTTPException(status_code=400, detail="Failed to delete address")

@router.post("/me/addresses/{address_id}/set-default", response_model=AddressResponse)
async def set_default_address(
    address_id: str,
    user_id: str = Depends(get_current_user_id),
    service: UserProfileService = Depends(get_user_profile_service)
):
    """Set an address as default"""
    return await service.set_default_address(address_id, user_id)

@router.get("/me/addresses/default", response_model=AddressResponse)
async def get_default_address(
    user_id: str = Depends(get_current_user_id),
    service: UserProfileService = Depends(get_user_profile_service)
):
    """Get user's default address"""
    address = await service.get_default_address(user_id)
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No default address found"
        )
    return address