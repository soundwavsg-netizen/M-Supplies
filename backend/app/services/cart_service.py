from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.core.config import settings
from fastapi import HTTPException, status
from typing import Dict, Any, Optional, List

class CartService:
    def __init__(self, cart_repo: CartRepository, product_repo: ProductRepository):
        self.cart_repo = cart_repo
        self.product_repo = product_repo
    
    async def get_or_create_cart(self, user_id: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        cart = await self.cart_repo.get_cart(user_id, session_id)
        if not cart:
            cart = await self.cart_repo.create_cart(user_id, session_id)
        return cart
    
    async def add_to_cart(self, variant_id: str, quantity: int, user_id: Optional[str] = None, 
                         session_id: Optional[str] = None) -> Dict[str, Any]:
        # Get or create cart
        cart = await self.get_or_create_cart(user_id, session_id)
        
        # Get variant details
        variant = await self.product_repo.get_variant_by_id(variant_id)
        if not variant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product variant not found"
            )
        
        # Check stock
        if variant.get('stock_qty', 0) < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock"
            )
        
        # Get product details
        product = await self.product_repo.get_product_by_id(variant['product_id'])
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Determine price based on quantity
        price = self._get_price_for_quantity(variant, quantity)
        
        # Check if variant already in cart
        items = cart.get('items', [])
        existing_item = next((item for item in items if item['variant_id'] == variant_id), None)
        
        if existing_item:
            existing_item['quantity'] += quantity
            existing_item['price'] = price
        else:
            items.append({
                'variant_id': variant_id,
                'product_id': variant['product_id'],
                'quantity': quantity,
                'price': price
            })
        
        # Update cart
        await self.cart_repo.update_cart(cart['id'], items)
        
        # Return cart with full details
        return await self.get_cart_with_details(cart['id'], user_id, session_id)
    
    def _get_price_for_quantity(self, variant: Dict[str, Any], quantity: int) -> float:
        """Get the appropriate price based on quantity and price tiers"""
        price_tiers = variant.get('price_tiers', [])
        if not price_tiers:
            return 0.0
        
        # Sort tiers by min_quantity descending
        sorted_tiers = sorted(price_tiers, key=lambda x: x['min_quantity'], reverse=True)
        
        # Find the applicable tier
        for tier in sorted_tiers:
            if quantity >= tier['min_quantity']:
                return tier['price']
        
        # If no tier matches, return the lowest tier price
        return sorted_tiers[-1]['price']
    
    async def get_cart_with_details(self, cart_id: str, user_id: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get cart with full product details and calculated totals"""
        cart = await self.cart_repo.get_cart(user_id, session_id)
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart not found"
            )
        
        # Get full details for each item
        detailed_items = []
        subtotal = 0.0
        
        for item in cart.get('items', []):
            variant = await self.product_repo.get_variant_by_id(item['variant_id'])
            if not variant:
                continue
            
            product = await self.product_repo.get_product_by_id(variant['product_id'])
            if not product:
                continue
            
            line_total = item['price'] * item['quantity']
            subtotal += line_total
            
            detailed_items.append({
                'variant_id': item['variant_id'],
                'product_name': product['name'],
                'product_image': product.get('images', [None])[0],
                'sku': variant['sku'],
                'attributes': variant['attributes'],
                'quantity': item['quantity'],
                'price': item['price'],
                'line_total': line_total
            })
        
        # Calculate GST and total
        gst = subtotal * (settings.gst_percent / 100)
        total = subtotal + gst
        
        return {
            'id': cart['id'],
            'user_id': cart.get('user_id'),
            'session_id': cart.get('session_id'),
            'items': detailed_items,
            'subtotal': round(subtotal, 2),
            'gst': round(gst, 2),
            'total': round(total, 2),
            'updated_at': cart['updated_at']
        }
    
    async def update_cart_item(self, variant_id: str, quantity: int, user_id: Optional[str] = None,
                              session_id: Optional[str] = None) -> Dict[str, Any]:
        cart = await self.cart_repo.get_cart(user_id, session_id)
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart not found"
            )
        
        items = cart.get('items', [])
        item = next((item for item in items if item['variant_id'] == variant_id), None)
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found in cart"
            )
        
        if quantity <= 0:
            # Remove item
            items = [i for i in items if i['variant_id'] != variant_id]
        else:
            # Check stock
            variant = await self.product_repo.get_variant_by_id(variant_id)
            if variant and variant.get('stock_qty', 0) < quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient stock"
                )
            
            # Update quantity and price
            item['quantity'] = quantity
            if variant:
                item['price'] = self._get_price_for_quantity(variant, quantity)
        
        await self.cart_repo.update_cart(cart['id'], items)
        return await self.get_cart_with_details(cart['id'])
    
    async def clear_cart(self, user_id: Optional[str] = None, session_id: Optional[str] = None) -> bool:
        cart = await self.cart_repo.get_cart(user_id, session_id)
        if not cart:
            return False
        
        return await self.cart_repo.clear_cart(cart['id'])
