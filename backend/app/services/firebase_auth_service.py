"""
Firebase Authentication Service

This service handles user authentication using Firebase Auth
"""
from app.repositories.user_repository import UserRepository
from app.services.email_service import email_service
from app.core.firebase import create_firebase_user, get_firebase_auth, verify_firebase_token
from app.schemas.user import UserCreate, UserLogin
from fastapi import HTTPException, status, BackgroundTasks
from typing import Dict, Any
from datetime import datetime, timezone
import uuid


class FirebaseAuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        self.firebase_auth = get_firebase_auth()
    
    async def register(self, user_data: UserCreate, background_tasks: BackgroundTasks = None) -> Dict[str, Any]:
        """
        Register a new user with Firebase Auth and Firestore
        
        Args:
            user_data: User registration data
            background_tasks: FastAPI background tasks for sending emails
            
        Returns:
            Dict with user data and Firebase custom token
        """
        try:
            # Check if user already exists in Firestore
            existing_user = await self.user_repo.get_by_email(user_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Create display name
            display_name = f"{user_data.first_name} {user_data.last_name}".strip()
            
            # Format phone number for Firebase (must start with +)
            phone = user_data.phone
            if phone and not phone.startswith('+'):
                if phone.startswith('65'):
                    phone = f'+{phone}'
                elif phone.startswith('60'):
                    phone = f'+{phone}'
                else:
                    phone = f'+65{phone}'  # Default to Singapore
            
            # Create Firebase Auth user
            try:
                firebase_user_data = {
                    'email': user_data.email,
                    'password': user_data.password,
                    'display_name': display_name
                }
                
                # Only add phone if provided
                if phone:
                    try:
                        firebase_user_data['phone_number'] = phone
                    except:
                        # Skip phone if invalid format
                        pass
                
                firebase_user = create_firebase_user(**firebase_user_data)
                uid = firebase_user['uid']
            
            except Exception as e:
                error_msg = str(e)
                if 'EMAIL_EXISTS' in error_msg:
                    # User already exists in Firebase Auth (probably from Google Sign-In)
                    # Get the existing user's UID and create Firestore profile
                    try:
                        existing_firebase_user = self.firebase_auth.get_user_by_email(user_data.email)
                        uid = existing_firebase_user.uid
                    except Exception as get_error:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email already registered"
                        )
                elif 'PHONE_NUMBER_EXISTS' in error_msg:
                    # Create user without phone number
                    firebase_user_data.pop('phone_number', None)
                    firebase_user = create_firebase_user(**firebase_user_data)
                    uid = firebase_user['uid']
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to create Firebase user: {error_msg}"
                    )
            
            # Create user document in Firestore
            user_id = str(uuid.uuid4())
            user_doc = {
                'id': user_id,
                'uid': uid,  # Firebase Auth UID
                'email': user_data.email,
                'first_name': user_data.first_name,
                'last_name': user_data.last_name,
                'displayName': display_name,
                'phone': user_data.phone,
                'role': user_data.role,
                'is_active': True,
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat(),
                'firebase_migrated': True
            }
            
            await self.user_repo.create(user_doc)
            
            # Generate Firebase custom token for immediate login
            custom_token = self.firebase_auth.create_custom_token(uid)
            
            # Send email notifications in background if available
            if background_tasks:
                # Send signup notification to admin
                background_tasks.add_task(
                    email_service.send_signup_notification,
                    display_name=display_name,
                    email=user_data.email,
                    phone=user_data.phone
                )
                
                # Send welcome email to user
                background_tasks.add_task(
                    email_service.send_welcome_email,
                    email=user_data.email,
                    display_name=display_name
                )
            
            return {
                'user': {
                    'id': user_id,
                    'uid': uid,
                    'email': user_data.email,
                    'displayName': display_name,
                    'phone': user_data.phone,
                    'role': user_data.role,
                    'createdAt': user_doc['createdAt'],
                    'updatedAt': user_doc['updatedAt']
                },
                'custom_token': custom_token.decode('utf-8') if isinstance(custom_token, bytes) else custom_token,
                'message': 'Registration successful. Please sign in with your email and password on the client.'
            }
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {str(e)}"
            )
    
    async def verify_id_token(self, id_token: str) -> Dict[str, Any]:
        """
        Verify Firebase ID token and return user data
        
        Args:
            id_token: Firebase ID token from client
            
        Returns:
            User data from Firestore
        """
        try:
            # Verify Firebase ID token
            decoded_token = verify_firebase_token(id_token)
            uid = decoded_token['uid']
            
            # Get user from Firestore by Firebase UID
            user = await self.user_repo.get_by_uid(uid)
            
            if not user:
                # User exists in Firebase but not in Firestore
                # This shouldn't happen but handle gracefully
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )
            
            # Check if user is active
            if not user.get('is_active', True):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is disabled"
                )
            
            # Remove password if it exists (legacy field)
            user.pop('password', None)
            
            return user
        
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Token verification failed: {str(e)}"
            )
    
    async def get_user_by_uid(self, uid: str) -> Dict[str, Any]:
        """Get user by Firebase UID"""
        user = await self.user_repo.get_by_uid(uid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.pop('password', None)
        return user
