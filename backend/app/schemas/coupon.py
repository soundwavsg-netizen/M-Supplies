from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class CouponType(str, Enum):
    percent = "percent"
    fixed = "fixed"

class CouponBase(BaseModel):
    code: str
    type: CouponType
    value: float  # Percentage (e.g., 10 for 10%) or fixed amount
    min_order_amount: float = 0
    max_uses: Optional[int] = None
    valid_from: datetime
    valid_to: datetime
    is_active: bool = True

class CouponCreate(CouponBase):
    pass

class CouponUpdate(BaseModel):
    code: Optional[str] = None
    type: Optional[CouponType] = None
    value: Optional[float] = None
    min_order_amount: Optional[float] = None
    max_uses: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: Optional[bool] = None

class CouponResponse(CouponBase):
    id: str
    used_count: int
    created_at: datetime

class CouponValidation(BaseModel):
    code: str
    order_amount: float
