from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Cookie
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from app.core.config import settings
from app.core.firebase import verify_firebase_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """Decode JWT token (legacy auth)"""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def decode_firebase_token(token: str) -> Dict[str, Any]:
    """Decode and verify Firebase ID token"""
    try:
        decoded_token = verify_firebase_token(token)
        return decoded_token
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_id(authorization: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    """
    Extract user_id from token (supports both JWT and Firebase ID tokens)
    
    Tries Firebase ID token first, falls back to JWT for backward compatibility
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    token = authorization.credentials
    
    # Try Firebase ID token first
    try:
        firebase_payload = decode_firebase_token(token)
        # Get user_id from Firebase UID
        from app.core.database import get_database
        from app.repositories.user_repository import UserRepository
        
        db = get_database()
        user_repo = UserRepository(db)
        user = await user_repo.get_by_uid(firebase_payload['uid'])
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return user['id']
    
    except HTTPException as e:
        # If it's a 404 (user not found), re-raise it
        if e.status_code == status.HTTP_404_NOT_FOUND:
            raise
        
        # Otherwise, try JWT token (legacy auth)
        try:
            payload = decode_token(token)
            
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            return user_id
        
        except:
            # Both Firebase and JWT token verification failed
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

async def get_current_user_optional(authorization: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
    """Extract user_id from token (Firebase or JWT), but allow None (for guest checkout)"""
    if not authorization:
        return None
    
    try:
        return await get_current_user_id(authorization)
    except:
        return None

async def require_role(required_roles: list[str]):
    """Dependency to check if user has required role"""
    async def role_checker(user_id: str = Depends(get_current_user_id)):
        from app.repositories.user_repository import UserRepository
        from app.core.database import get_database
        
        db = get_database()
        user_repo = UserRepository(db)
        
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user['role'] not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        return user
    
    return role_checker
