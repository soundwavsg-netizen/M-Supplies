from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum

class InventoryMovementReason(str, Enum):
    order_created = "order_created"
    order_cancelled = "order_cancelled"
    order_shipped = "order_shipped"
    manual_adjustment = "manual_adjustment"
    purchase_received = "purchase_received"
    customer_return = "return"
    damaged = "damaged"
    lost = "lost"
    found = "found"
    recount = "recount"

class ChannelType(str, Enum):
    website = "website"
    shopee = "shopee"
    lazada = "lazada"
    amazon = "amazon"
    manual = "manual"

class InventoryLedgerEntry(BaseModel):
    id: str
    variant_id: str
    sku: str
    reason: InventoryMovementReason
    channel: Optional[ChannelType] = None
    
    # Changes
    on_hand_before: int
    on_hand_after: int
    on_hand_change: int
    
    allocated_before: int
    allocated_after: int
    allocated_change: int
    
    # Reference
    reference_id: Optional[str] = None  # order_id, adjustment_id, etc.
    reference_type: Optional[str] = None  # order, purchase_order, adjustment
    
    notes: Optional[str] = None
    created_by: Optional[str] = None  # user_id who made the change
    created_at: datetime

class InventoryLedgerCreate(BaseModel):
    variant_id: str
    reason: InventoryMovementReason
    channel: Optional[ChannelType] = None
    on_hand_change: int = 0
    allocated_change: int = 0
    reference_id: Optional[str] = None
    reference_type: Optional[str] = None
    notes: Optional[str] = None

class InventoryStatus(BaseModel):
    variant_id: str
    sku: str
    product_name: str
    on_hand: int
    allocated: int
    available: int
    safety_stock: int
    low_stock_threshold: int
    is_low_stock: bool
    channel_buffers: Dict[str, int] = {}

class StockAdjustment(BaseModel):
    variant_id: str
    adjustment_type: str  # "set" or "change"
    on_hand_value: Optional[int] = None
    on_hand_change: Optional[int] = None
    reason: InventoryMovementReason
    notes: str

class ChannelMapping(BaseModel):
    id: str
    channel: ChannelType
    external_sku: str
    external_listing_id: Optional[str] = None
    internal_variant_id: str
    internal_sku: str
    is_active: bool = True
    created_at: datetime

class ChannelMappingCreate(BaseModel):
    channel: ChannelType
    external_sku: str
    external_listing_id: Optional[str] = None
    internal_variant_id: str

class ExternalOrderItem(BaseModel):
    external_sku: str
    quantity: int
    unit_price: float

class ExternalOrderImport(BaseModel):
    channel: ChannelType
    external_order_id: str
    items: list[ExternalOrderItem]
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    notes: Optional[str] = None

class BusinessSettings(BaseModel):
    business_name: str = "M Supplies"
    currency: str = "SGD"
    gst_percent: float = 9.0
    default_safety_stock: int = 5
    low_stock_threshold: int = 10
    channel_buffers: Dict[str, int] = {
        "website": 0,
        "shopee": 2,
        "lazada": 2
    }
    # Product configuration
    available_colors: List[str] = [
        "white", "pastel pink", "champagne pink", "milktea", "black", "clear"
    ]
    available_types: List[str] = [
        "normal", "bubble wrap", "tool", "consumable"
    ]
