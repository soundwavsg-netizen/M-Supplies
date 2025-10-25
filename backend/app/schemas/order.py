from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"
    refunded = "refunded"

# Firebase-compatible shipping address
class FirebaseShippingAddress(BaseModel):
    fullName: str = Field(..., max_length=100)
    phone: str = Field(...)
    addressLine1: str = Field(..., max_length=200)
    addressLine2: Optional[str] = Field(None, max_length=200)
    unit: Optional[str] = Field(None, max_length=50)
    postalCode: str = Field(...)
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    country: str = Field(..., description="Country code (SG, MY)")

# Legacy shipping address (keep for compatibility)
class ShippingAddress(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str = "Singapore"

class OrderItem(BaseModel):
    product_id: str
    variant_id: str
    product_name: str
    sku: str
    attributes: dict
    quantity: int
    unit_price: float
    line_total: float

class OrderCreate(BaseModel):
    shipping_address: ShippingAddress
    coupon_code: Optional[str] = None
    payment_method: str = "stripe"  # stripe, paynow, grabpay

class OrderResponse(BaseModel):
    id: str
    order_number: str
    user_id: Optional[str] = None
    guest_email: Optional[str] = None
    items: List[OrderItem]
    shipping_address: ShippingAddress
    subtotal: float
    discount: float
    gst: float
    shipping_fee: float
    total: float
    status: OrderStatus
    payment_intent_id: Optional[str] = None
    tracking_number: Optional[str] = None
    coupon_code: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    tracking_number: Optional[str] = None
    notes: Optional[str] = None
