"""
Firebase Admin SDK initialization and configuration
"""
import os
import firebase_admin
from firebase_admin import credentials, firestore, auth as firebase_auth
from typing import Optional

_firebase_app: Optional[firebase_admin.App] = None
_firestore_client = None


def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    global _firebase_app, _firestore_client
    
    if _firebase_app is not None:
        return _firestore_client
    
    try:
        cred_path = os.environ.get('FIREBASE_CREDENTIALS_PATH', '/app/backend/firebase-credentials.json')
        
        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"Firebase credentials file not found at {cred_path}")
        
        cred = credentials.Certificate(cred_path)
        _firebase_app = firebase_admin.initialize_app(cred)
        _firestore_client = firestore.client()
        
        print(f"✅ Firebase initialized successfully with project: {os.environ.get('FIREBASE_PROJECT_ID', 'Unknown')}")
        return _firestore_client
    
    except Exception as e:
        print(f"❌ Firebase initialization failed: {str(e)}")
        raise


def get_firestore_client():
    """Get Firestore client instance"""
    global _firestore_client
    
    if _firestore_client is None:
        initialize_firebase()
    
    return _firestore_client


def get_firebase_auth():
    """Get Firebase Auth instance"""
    if _firebase_app is None:
        initialize_firebase()
    
    return firebase_auth


def verify_firebase_token(id_token: str) -> dict:
    """
    Verify Firebase ID token and return decoded token
    
    Args:
        id_token: Firebase ID token from client
        
    Returns:
        Decoded token with user information
        
    Raises:
        ValueError: If token is invalid
    """
    try:
        auth = get_firebase_auth()
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        raise ValueError(f"Invalid Firebase token: {str(e)}")


def create_firebase_user(email: str, password: str, display_name: str = None, phone: str = None) -> dict:
    """
    Create a new Firebase Auth user
    
    Args:
        email: User email
        password: User password
        display_name: User display name (optional)
        phone: User phone number (optional)
        
    Returns:
        User record information
    """
    try:
        auth = get_firebase_auth()
        
        user_data = {
            'email': email,
            'password': password,
            'email_verified': False,
        }
        
        if display_name:
            user_data['display_name'] = display_name
        
        if phone:
            user_data['phone_number'] = phone
        
        user_record = auth.create_user(**user_data)
        
        return {
            'uid': user_record.uid,
            'email': user_record.email,
            'display_name': user_record.display_name,
            'phone_number': user_record.phone_number,
            'email_verified': user_record.email_verified,
        }
    
    except Exception as e:
        raise ValueError(f"Failed to create Firebase user: {str(e)}")


def get_firebase_user(uid: str) -> dict:
    """Get Firebase user by UID"""
    try:
        auth = get_firebase_auth()
        user_record = auth.get_user(uid)
        
        return {
            'uid': user_record.uid,
            'email': user_record.email,
            'display_name': user_record.display_name,
            'phone_number': user_record.phone_number,
            'email_verified': user_record.email_verified,
        }
    
    except Exception as e:
        raise ValueError(f"Failed to get Firebase user: {str(e)}")


def update_firebase_user(uid: str, **kwargs) -> dict:
    """Update Firebase user"""
    try:
        auth = get_firebase_auth()
        user_record = auth.update_user(uid, **kwargs)
        
        return {
            'uid': user_record.uid,
            'email': user_record.email,
            'display_name': user_record.display_name,
            'phone_number': user_record.phone_number,
            'email_verified': user_record.email_verified,
        }
    
    except Exception as e:
        raise ValueError(f"Failed to update Firebase user: {str(e)}")


def delete_firebase_user(uid: str):
    """Delete Firebase user"""
    try:
        auth = get_firebase_auth()
        auth.delete_user(uid)
    
    except Exception as e:
        raise ValueError(f"Failed to delete Firebase user: {str(e)}")
