from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class DiscountType(str, Enum):
    FIXED = "fixed"  # Fixed amount ($5 off)
    PERCENTAGE = "percentage"  # Percentage (10% off)

class CouponUsageType(str, Enum):
    UNLIMITED = "unlimited"  # Same code for all VIPs (like "VIP10")
    SINGLE_USE = "single_use"  # Unique codes for each customer
    LIMITED_USE = "limited_use"  # Code can be used X times total

class CouponStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    DISABLED = "disabled"

# ==================== COUPON SCHEMAS ====================

class CouponBase(BaseModel):
    code: str = Field(..., min_length=3, max_length=20)
    description: str = Field(..., max_length=200)
    discount_type: DiscountType
    discount_value: float = Field(..., gt=0)  # Amount ($5) or percentage (10)
    usage_type: CouponUsageType
    minimum_order_amount: Optional[float] = Field(default=0, ge=0)
    maximum_discount_amount: Optional[float] = Field(default=None, gt=0)  # Cap for percentage discounts
    usage_limit: Optional[int] = Field(default=None, gt=0)  # Total usage limit for limited_use
    expires_at: Optional[datetime] = None
    is_active: bool = Field(default=True)

class CouponCreate(CouponBase):
    pass

class CouponUpdate(BaseModel):
    description: Optional[str] = None
    discount_type: Optional[DiscountType] = None
    discount_value: Optional[float] = None
    minimum_order_amount: Optional[float] = None
    maximum_discount_amount: Optional[float] = None
    usage_limit: Optional[int] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None

class Coupon(CouponBase):
    id: str
    created_at: datetime
    updated_at: datetime
    usage_count: int = 0
    status: CouponStatus

# ==================== GIFT ITEM SCHEMAS ====================

class GiftItemBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: str = Field(..., max_length=300)
    image_url: Optional[str] = None
    stock_quantity: int = Field(default=0, ge=0)
    is_active: bool = Field(default=True)

class GiftItemCreate(GiftItemBase):
    pass

class GiftItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    stock_quantity: Optional[int] = None
    is_active: Optional[bool] = None

class GiftItem(GiftItemBase):
    id: str
    created_at: datetime
    updated_at: datetime

# ==================== GIFT TIER SCHEMAS ====================

class GiftTierBase(BaseModel):
    name: str = Field(..., max_length=50)  # "Bronze Tier", "Gold Tier", etc.
    spending_threshold: float = Field(..., gt=0)  # $100, $150, $200
    gift_limit: int = Field(default=1, gt=0)  # How many gifts customer can select
    is_active: bool = Field(default=True)

class GiftTierCreate(GiftTierBase):
    gift_item_ids: List[str] = []  # List of gift items available in this tier

class GiftTierUpdate(BaseModel):
    name: Optional[str] = None
    spending_threshold: Optional[float] = None
    gift_limit: Optional[int] = None
    is_active: Optional[bool] = None
    gift_item_ids: Optional[List[str]] = None

class GiftTier(GiftTierBase):
    id: str
    created_at: datetime
    updated_at: datetime
    gift_items: List[GiftItem] = []  # Populated gift items

# ==================== COUPON USAGE TRACKING ====================

class CouponUsageBase(BaseModel):
    coupon_id: str
    user_id: Optional[str] = None  # For logged in users
    order_id: str
    discount_applied: float
    order_total: float

class CouponUsageCreate(CouponUsageBase):
    pass

class CouponUsage(CouponUsageBase):
    id: str
    used_at: datetime

# ==================== ORDER INTEGRATION SCHEMAS ====================

class AppliedPromotion(BaseModel):
    """For storing promotion details in orders"""
    coupon_code: Optional[str] = None
    discount_amount: float = 0
    selected_gifts: List[dict] = []  # List of selected gift items with details

class PromotionValidation(BaseModel):
    """For validating promotions during checkout"""
    coupon_code: Optional[str] = None
    order_subtotal: float
    user_id: Optional[str] = None

class PromotionResult(BaseModel):
    """Result of promotion validation"""
    valid: bool
    error_message: Optional[str] = None
    discount_amount: float = 0
    available_gift_tiers: List[GiftTier] = []
    applied_coupon: Optional[Coupon] = None