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
    pack_size: int = 50  # Number of pieces per pack (50, 100, etc.) - For bubble wrap, this represents individual pieces
    stock_qty: int = 0  # Legacy field, use on_hand instead
    cost_price: Optional[float] = None
    
    # Centralized inventory fields - units depend on product type
    # For regular products: represents number of packs
    # For bubble wrap: represents individual pieces
    on_hand: int = 0  # Number of units in stock (packs or pieces)
    allocated: int = 0  # Number of units allocated
    safety_stock: int = 0  # Safety stock in units
    low_stock_threshold: int = 10  # Low stock threshold in units
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
    color: Optional[str] = "white"  # Product-level color
    type: Optional[str] = "normal"  # Product-level type
    images: List[str] = []
    specifications: Dict[str, str] = {}  # e.g., {"material": "LDPE", "feature": "Self-sealing"}
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: List[str] = []
    is_active: bool = True
    featured: bool = False

class ProductCreate(ProductBase):
    variants: List[VariantCreate]

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    color: Optional[str] = None
    type: Optional[str] = None
    images: Optional[List[str]] = None
    specifications: Optional[Dict[str, str]] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[List[str]] = None
    is_active: Optional[bool] = None
    featured: Optional[bool] = None
    variants: Optional[List[VariantCreate]] = None

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

# Product filtering and sorting schemas
class ProductFilters(BaseModel):
    categories: Optional[List[str]] = None  # ["polymailers", "accessories"]
    colors: Optional[List[str]] = None  # ["white", "pastel pink", "milktea"]
    sizes: Optional[List[str]] = None  # ["25x35", "17x30", "32x43"]
    type: Optional[str] = None  # "normal" or "bubble wrap"
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    in_stock_only: Optional[bool] = False
    search: Optional[str] = None  # Keyword search

class ProductSortOptions(BaseModel):
    sort_by: Literal["best_sellers", "price_low_high", "price_high_low", "newest"] = "best_sellers"

class ProductListRequest(BaseModel):
    filters: Optional[ProductFilters] = None
    sort: Optional[ProductSortOptions] = None
    page: int = 1
    limit: int = 20
