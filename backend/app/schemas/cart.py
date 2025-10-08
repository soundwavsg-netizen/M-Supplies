from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CartItemBase(BaseModel):
    variant_id: str
    quantity: int
    price: float  # Price at time of adding to cart

class CartItemResponse(CartItemBase):
    product_name: str
    product_image: Optional[str] = None
    sku: str
    attributes: dict
    line_total: float

class CartResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    items: List[CartItemResponse]
    subtotal: float
    shipping_fee: float = Field(default=0.0, description="Shipping cost based on weight")
    shipping_method: Optional[str] = Field(None, description="Shipping method name")
    total_weight_grams: Optional[float] = Field(None, description="Total cart weight in grams")
    delivery_estimate: Optional[str] = Field(None, description="Estimated delivery time")
    gst: float = Field(default=0.0, description="GST amount (currently 0.0)")
    total: float
    updated_at: datetime

class AddToCartRequest(BaseModel):
    variant_id: str
    quantity: int = 1

class UpdateCartItemRequest(BaseModel):
    quantity: int
