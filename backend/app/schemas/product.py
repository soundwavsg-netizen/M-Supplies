from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Literal
from datetime import datetime

class PriceTier(BaseModel):
    min_quantity: int
    price: float

class VariantAttributes(BaseModel):
    # New explicit dimensions for filtering
    width_cm: int  # Width in centimeters
    height_cm: int  # Height in centimeters
    size_code: str  # e.g., "25x35", "17x30" 
    type: str  # "normal" or "bubble wrap"
    color: str  # e.g., "white", "pastel pink", "champagne pink", "milktea"
    
    # Optional legacy fields
    thickness: Optional[str] = None  # e.g., "60 micron"

class VariantBase(BaseModel):
    sku: str
    attributes: VariantAttributes
    price_tiers: List[PriceTier]
    stock_qty: int = 0  # Legacy field, use on_hand instead
    cost_price: Optional[float] = None
    
    # Centralized inventory fields
    on_hand: int = 0
    allocated: int = 0
    safety_stock: int = 0
    low_stock_threshold: int = 10
    channel_buffers: Dict[str, int] = {}

class VariantCreate(VariantBase):
    pass

class VariantResponse(VariantBase):
    id: str
    product_id: str
    created_at: datetime

class ProductBase(BaseModel):
    name: str
    description: str
    category: str  # e.g., "Polymailers", "Custom Printing"
    images: List[str] = []
    specifications: Dict[str, str] = {}  # e.g., {"material": "LDPE", "feature": "Self-sealing"}
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    is_active: bool = True
    featured: bool = False

class ProductCreate(ProductBase):
    variants: List[VariantCreate]

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    images: Optional[List[str]] = None
    specifications: Optional[Dict[str, str]] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    is_active: Optional[bool] = None
    featured: Optional[bool] = None

class ProductResponse(ProductBase):
    id: str
    variants: List[VariantResponse]
    created_at: datetime
    updated_at: datetime

class ProductListItem(BaseModel):
    id: str
    name: str
    category: str
    images: List[str]
    price_range: Dict[str, float]  # {"min": 10.50, "max": 25.00}
    in_stock: bool
    featured: bool
