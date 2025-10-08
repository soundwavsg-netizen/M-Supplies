from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import math

@dataclass
class ShippingItem:
    variant_id: str
    quantity: int
    weight_grams: float
    value: float
    name: str

@dataclass
class ShippingRateResult:
    shipping_fee: float
    total_weight_grams: float
    delivery_estimate: str = "2-3 business days"
    method: str = "Standard Shipping"
    
class BasicShippingService:
    """Basic weight-based shipping service before EasyParcel integration"""
    
    def __init__(self):
        # Basic shipping rates (SGD) based on weight
        self.weight_tiers = [
            {"min_weight": 0, "max_weight": 100, "rate": 3.00},     # Up to 100g
            {"min_weight": 100, "max_weight": 250, "rate": 4.50},   # 100-250g
            {"min_weight": 250, "max_weight": 500, "rate": 6.00},   # 250-500g
            {"min_weight": 500, "max_weight": 1000, "rate": 8.00},  # 500g-1kg
            {"min_weight": 1000, "max_weight": 2000, "rate": 12.00}, # 1-2kg
            {"min_weight": 2000, "max_weight": 5000, "rate": 18.00}, # 2-5kg
            {"min_weight": 5000, "max_weight": 10000, "rate": 25.00}, # 5-10kg
        ]
        
        self.free_shipping_threshold = 50.00  # Free shipping over $50
        self.max_weight_grams = 10000  # 10kg maximum
        
    def calculate_shipping(self, items: List[ShippingItem], subtotal: float) -> ShippingRateResult:
        """Calculate shipping cost based on total weight and subtotal"""
        
        # Check for free shipping
        if subtotal >= self.free_shipping_threshold:
            return ShippingRateResult(
                shipping_fee=0.0,
                total_weight_grams=sum(item.weight_grams * item.quantity for item in items),
                delivery_estimate="2-3 business days (Free shipping)",
                method="Free Standard Shipping"
            )
        
        # Calculate total weight
        total_weight = sum(item.weight_grams * item.quantity for item in items)
        
        if total_weight > self.max_weight_grams:
            # For very heavy orders, use premium rate
            return ShippingRateResult(
                shipping_fee=35.00,
                total_weight_grams=total_weight,
                delivery_estimate="3-5 business days",
                method="Heavy Item Shipping"
            )
        
        # Find appropriate shipping rate
        shipping_fee = self._get_rate_for_weight(total_weight)
        
        return ShippingRateResult(
            shipping_fee=shipping_fee,
            total_weight_grams=total_weight,
            delivery_estimate="2-3 business days",
            method="Standard Shipping"
        )
    
    def _get_rate_for_weight(self, weight_grams: float) -> float:
        """Get shipping rate for given weight"""
        for tier in self.weight_tiers:
            if tier["min_weight"] <= weight_grams < tier["max_weight"]:
                return tier["rate"]
        
        # If weight exceeds all tiers, use the highest tier rate
        return self.weight_tiers[-1]["rate"]
    
    def get_shipping_estimate_for_cart(self, cart_items: List[Dict[str, Any]], subtotal: float) -> ShippingRateResult:
        """Get shipping estimate for cart items"""
        shipping_items = []
        
        for item in cart_items:
            # Extract weight from variant attributes
            weight = item.get('variant', {}).get('attributes', {}).get('weight_grams', 0)
            if weight <= 0:
                # Default weights if not specified (we'll populate these later)
                weight = self._get_default_weight(item.get('sku', ''))
            
            shipping_items.append(ShippingItem(
                variant_id=item.get('variant_id'),
                quantity=item.get('quantity', 1),
                weight_grams=weight,
                value=item.get('line_total', 0),
                name=item.get('product_name', 'Unknown Product')
            ))
        
        return self.calculate_shipping(shipping_items, subtotal)
    
    def _get_default_weight(self, sku: str) -> float:
        """Get default weight based on SKU patterns (temporary until real weights are added)"""
        sku_lower = sku.lower()
        
        # Default weights based on product type
        if 'polymailer' in sku_lower:
            if '100' in sku_lower:  # 100-pack
                return 200.0  # grams
            elif '50' in sku_lower:  # 50-pack
                return 120.0  # grams
            elif '25' in sku_lower:  # 25-pack
                return 80.0   # grams
            else:
                return 150.0  # default
        elif 'bubble' in sku_lower:
            return 180.0  # bubble wrap is heavier
        elif 'scissors' in sku_lower:
            return 85.0   # scissors weight
        elif 'tape' in sku_lower:
            return 45.0   # tape roll weight
        else:
            return 100.0  # default unknown product weight

# Default product weights (temporary - user will provide real weights)
DEFAULT_PRODUCT_WEIGHTS = {
    # Premium Polymailers (grams)
    'polymailer_25x35_50': 120,
    'polymailer_25x35_100': 200, 
    'polymailer_32x43_50': 150,
    'polymailer_32x43_100': 250,
    'polymailer_45x60_25': 180,
    'polymailer_45x60_50': 320,
    
    # Bubble wrap polymailers (heavier due to bubble wrap)
    'bubble_polymailer_25x35_50': 180,
    'bubble_polymailer_32x43_50': 220,
    'bubble_polymailer_45x60_25': 280,
    
    # Tools and accessories
    'scissors': 85,
    'tape_roll': 45,
}