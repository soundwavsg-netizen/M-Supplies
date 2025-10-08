from app.repositories.order_repository import OrderRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.coupon_repository import CouponRepository
from app.repositories.inventory_repository import InventoryLedgerRepository
from app.schemas.order import OrderCreate, OrderStatusUpdate
from app.core.config import settings
from fastapi import HTTPException, status
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

class OrderService:
    def __init__(self, order_repo: OrderRepository, cart_repo: CartRepository,
                 product_repo: ProductRepository, coupon_repo: CouponRepository,
                 ledger_repo: Optional[InventoryLedgerRepository] = None):
        self.order_repo = order_repo
        self.cart_repo = cart_repo
        self.product_repo = product_repo
        self.coupon_repo = coupon_repo
        self.ledger_repo = ledger_repo
    
    async def create_order(self, order_data: OrderCreate, user_id: Optional[str] = None,
                          session_id: Optional[str] = None) -> Dict[str, Any]:
        # Get cart
        cart = await self.cart_repo.get_cart(user_id, session_id)
        if not cart or not cart.get('items'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty"
            )
        
        # Build order items with full details
        order_items = []
        subtotal = 0.0
        
        for cart_item in cart['items']:
            variant = await self.product_repo.get_variant_by_id(cart_item['variant_id'])
            if not variant:
                continue
            
            product = await self.product_repo.get_product_by_id(variant['product_id'])
            if not product:
                continue
            
            # Check stock
            if variant.get('stock_qty', 0) < cart_item['quantity']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for {product['name']}"
                )
            
            line_total = cart_item['price'] * cart_item['quantity']
            subtotal += line_total
            
            order_items.append({
                'product_id': variant['product_id'],
                'variant_id': cart_item['variant_id'],
                'product_name': product['name'],
                'sku': variant['sku'],
                'attributes': variant['attributes'],
                'quantity': cart_item['quantity'],
                'unit_price': cart_item['price'],
                'line_total': line_total
            })
        
        # Validate and apply coupon
        discount = 0.0
        coupon_code = None
        if order_data.coupon_code:
            coupon = await self.coupon_repo.get_by_code(order_data.coupon_code)
            if coupon:
                discount = await self._calculate_discount(coupon, subtotal)
                if discount > 0:
                    coupon_code = coupon['code']
                    await self.coupon_repo.increment_usage(coupon['id'])
        
        # Calculate totals (no GST)
        after_discount = subtotal - discount
        gst = 0.0  # No GST for now
        shipping_fee = 0.0  # TODO: Calculate based on shipping rules
        total = after_discount + shipping_fee
        
        # Create order
        order_dict = {
            'user_id': user_id,
            'guest_email': order_data.shipping_address.email if not user_id else None,
            'items': order_items,
            'shipping_address': order_data.shipping_address.model_dump(),
            'subtotal': round(subtotal, 2),
            'discount': round(discount, 2),
            'gst': round(gst, 2),
            'shipping_fee': round(shipping_fee, 2),
            'total': round(total, 2),
            'status': 'pending',
            'coupon_code': coupon_code,
            'payment_intent_id': None
        }
        
        order = await self.order_repo.create(order_dict)
        
        # Allocate stock using new inventory system
        for item in order_items:
            variant = await self.product_repo.get_variant_by_id(item['variant_id'])
            if variant:
                # Get current inventory values
                on_hand = variant.get('on_hand', variant.get('stock_qty', 0))
                allocated = variant.get('allocated', 0)
                safety_stock = variant.get('safety_stock', 0)
                available = on_hand - allocated - safety_stock
                
                if item['quantity'] > available:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Insufficient stock for {item['product_name']}"
                    )
                
                # Allocate stock (increase allocated count)
                new_allocated = allocated + item['quantity']
                await self.product_repo.update_variant(item['variant_id'], {
                    'allocated': new_allocated,
                    'stock_qty': on_hand  # Keep legacy field in sync
                })
                
                # Create ledger entry if ledger_repo is available
                if self.ledger_repo:
                    ledger_entry = {
                        'variant_id': item['variant_id'],
                        'sku': item['sku'],
                        'reason': 'order_created',
                        'channel': 'website',
                        'on_hand_before': on_hand,
                        'on_hand_after': on_hand,
                        'on_hand_change': 0,
                        'allocated_before': allocated,
                        'allocated_after': new_allocated,
                        'allocated_change': item['quantity'],
                        'reference_id': order['id'],
                        'reference_type': 'order',
                        'notes': f"Order {order['order_number']} created",
                        'created_by': user_id
                    }
                    await self.ledger_repo.create_entry(ledger_entry)
        
        # Clear cart
        await self.cart_repo.clear_cart(cart['id'])
        
        return order
    
    async def _calculate_discount(self, coupon: Dict[str, Any], order_amount: float) -> float:
        """Calculate discount amount from coupon"""
        # Check if coupon is active
        if not coupon.get('is_active', False):
            return 0.0
        
        # Check validity dates
        now = datetime.now(timezone.utc)
        valid_from = coupon.get('valid_from')
        valid_to = coupon.get('valid_to')
        
        if valid_from and now < valid_from:
            return 0.0
        if valid_to and now > valid_to:
            return 0.0
        
        # Check min order amount
        if order_amount < coupon.get('min_order_amount', 0):
            return 0.0
        
        # Check usage limit
        max_uses = coupon.get('max_uses')
        if max_uses and coupon.get('used_count', 0) >= max_uses:
            return 0.0
        
        # Calculate discount
        if coupon['type'] == 'percent':
            return order_amount * (coupon['value'] / 100)
        else:  # fixed
            return min(coupon['value'], order_amount)
    
    async def get_order(self, order_id: str) -> Dict[str, Any]:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        return order
    
    async def list_user_orders(self, user_id: str, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        return await self.order_repo.list_user_orders(user_id, skip, limit)
    
    async def list_orders(self, skip: int = 0, limit: int = 50, status: Optional[str] = None,
                         search: Optional[str] = None) -> List[Dict[str, Any]]:
        return await self.order_repo.list_orders(skip, limit, status, search)
    
    async def update_order_status(self, order_id: str, status_update: OrderStatusUpdate) -> Dict[str, Any]:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        update_data = {'status': status_update.status.value}
        if status_update.tracking_number:
            update_data['tracking_number'] = status_update.tracking_number
        
        await self.order_repo.update(order_id, update_data)
        return await self.get_order(order_id)
    
    async def update_payment_intent(self, order_id: str, payment_intent_id: str) -> bool:
        return await self.order_repo.update(order_id, {
            'payment_intent_id': payment_intent_id,
            'status': 'paid'
        })
