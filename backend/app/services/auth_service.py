from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.schemas.user import UserCreate, UserLogin
from fastapi import HTTPException, status
from typing import Dict, Any
from datetime import datetime, timezone

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def _transform_user_to_firebase_format(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Transform legacy user data to Firebase-compatible format"""
        return {
            "id": user.get("id"),
            "uid": user.get("id"),  # Firebase-style UID field
            "displayName": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
            "email": user.get("email"),
            "phone": user.get("phone"),
            "role": user.get("role", "customer"),
            "defaultAddressId": user.get("defaultAddressId"),
            "lastUsedAddressId": user.get("lastUsedAddressId"),
            "is_active": user.get("is_active", True),
            "createdAt": user.get("created_at", datetime.now(timezone.utc)),
            "updatedAt": user.get("updated_at", datetime.now(timezone.utc))
        }
    
    async def register(self, user_data: UserCreate) -> Dict[str, Any]:
        # Check if user exists
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        user_dict = user_data.model_dump()
        user_dict['password'] = hash_password(user_data.password)
        
        # Create user
        user = await self.user_repo.create(user_dict)
        
        # Remove password from response
        user.pop('password', None)
        
        # Generate tokens
        access_token = create_access_token({"sub": user['id'], "email": user['email']})
        refresh_token = create_refresh_token({"sub": user['id']})
        
        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    async def login(self, credentials: UserLogin) -> Dict[str, Any]:
        # Find user
        user = await self.user_repo.get_by_email(credentials.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.get('is_active', True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled"
            )
        
        # Verify password
        if not verify_password(credentials.password, user['password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Remove password from response
        user.pop('password', None)
        
        # Generate tokens
        access_token = create_access_token({"sub": user['id'], "email": user['email']})
        refresh_token = create_refresh_token({"sub": user['id']})
        
        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    async def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.pop('password', None)
        return user
