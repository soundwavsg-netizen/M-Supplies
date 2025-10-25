from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
import re

# Firebase-style User Profile Schema
class UserProfile(BaseModel):
    uid: str = Field(..., description="User unique identifier")
    displayName: str = Field(..., max_length=100, description="Display name")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    role: str = Field(default="customer", description="User role: customer or admin")
    defaultAddressId: Optional[str] = Field(None, description="Default address ID")
    lastUsedAddressId: Optional[str] = Field(None, description="Last used address ID")
    is_active: bool = Field(default=True, description="Account status")
    createdAt: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updatedAt: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[0-9\s\-\(\)]+$', v):
            raise ValueError('Invalid phone number format')
        return v

class UserAddress(BaseModel):
    id: str = Field(..., description="Address unique identifier")
    uid: str = Field(..., description="User ID this address belongs to")
    fullName: str = Field(..., max_length=100, description="Full name for delivery")
    phone: str = Field(..., description="Phone number for delivery")
    addressLine1: str = Field(..., max_length=200, description="Street address line 1")
    addressLine2: Optional[str] = Field(None, max_length=200, description="Street address line 2")
    unit: Optional[str] = Field(None, max_length=50, description="Unit number")
    postalCode: str = Field(..., description="Postal code")
    city: str = Field(..., max_length=100, description="City")
    state: str = Field(..., max_length=100, description="State/Region")
    country: str = Field(..., description="Country code (SG, MY)")
    isDefault: bool = Field(default=False, description="Is this the default address")
    createdAt: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updatedAt: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    @validator('postalCode')
    def validate_postal_code(cls, v, values):
        country = values.get('country', 'SG')
        if country == 'SG':
            if not re.match(r'^\d{6}$', v):
                raise ValueError('Singapore postal code must be 6 digits')
        elif country == 'MY':
            if not re.match(r'^\d{5}$', v):
                raise ValueError('Malaysia postal code must be 5 digits')
        return v
    
    @validator('country')
    def validate_country(cls, v):
        if v not in ['SG', 'MY']:
            raise ValueError('Country must be SG (Singapore) or MY (Malaysia)')
        return v

# Legacy User Schemas (for backward compatibility)
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    displayName: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: str
    displayName: str
    email: EmailStr
    phone: Optional[str] = None
    role: str
    defaultAddressId: Optional[str] = None
    lastUsedAddressId: Optional[str] = None
    is_active: bool
    createdAt: datetime
    updatedAt: datetime

# Address Management Schemas
class AddressCreate(BaseModel):
    fullName: str = Field(..., max_length=100)
    phone: str = Field(...)
    addressLine1: str = Field(..., max_length=200)
    addressLine2: Optional[str] = Field(None, max_length=200)
    unit: Optional[str] = Field(None, max_length=50)
    postalCode: str = Field(...)
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    country: str = Field(..., description="SG or MY")
    isDefault: bool = Field(default=False)

class AddressUpdate(BaseModel):
    fullName: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = None
    addressLine1: Optional[str] = Field(None, max_length=200)
    addressLine2: Optional[str] = Field(None, max_length=200)
    unit: Optional[str] = Field(None, max_length=50)
    postalCode: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = None
    isDefault: Optional[bool] = None

class AddressResponse(BaseModel):
    id: str
    fullName: str
    phone: str
    addressLine1: str
    addressLine2: Optional[str] = None
    unit: Optional[str] = None
    postalCode: str
    city: str
    state: str
    country: str
    isDefault: bool
    createdAt: datetime
    updatedAt: datetime

# Token and Legacy Responses (keep for compatibility)
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
