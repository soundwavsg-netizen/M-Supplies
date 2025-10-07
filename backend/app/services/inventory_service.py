from app.repositories.inventory_repository import InventoryLedgerRepository, ChannelMappingRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.inventory import InventoryLedgerCreate, StockAdjustment, ExternalOrderImport, ChannelMappingCreate
from fastapi import HTTPException, status
from typing import Dict, Any, List, Optional

class InventoryService:
    def __init__(self, ledger_repo: InventoryLedgerRepository, product_repo: ProductRepository,
                 mapping_repo: ChannelMappingRepository):
        self.ledger_repo = ledger_repo
        self.product_repo = product_repo
        self.mapping_repo = mapping_repo
    
    async def get_variant_inventory(self, variant_id: str) -> Dict[str, Any]:
        """Get current inventory status for a variant"""
        variant = await self.product_repo.get_variant_by_id(variant_id)
        if not variant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Variant not found"
            )
        
        on_hand = variant.get('on_hand', 0)
        allocated = variant.get('allocated', 0)
        safety_stock = variant.get('safety_stock', 0)
        available = on_hand - allocated - safety_stock
        
        product = await self.product_repo.get_product_by_id(variant['product_id'])
        
        return {
            'variant_id': variant_id,
            'sku': variant['sku'],
            'product_name': product['name'] if product else 'Unknown',
            'on_hand': on_hand,
            'allocated': allocated,
            'available': max(0, available),
            'safety_stock': safety_stock,
            'low_stock_threshold': variant.get('low_stock_threshold', 10),
            'is_low_stock': available < variant.get('low_stock_threshold', 10),
            'channel_buffers': variant.get('channel_buffers', {})
        }
    
    async def allocate_stock(self, variant_id: str, quantity: int, reason: str, channel: Optional[str] = None,
                            reference_id: Optional[str] = None, reference_type: Optional[str] = None,
                            user_id: Optional[str] = None) -> Dict[str, Any]:
        """Allocate stock (increase allocated count)"""
        variant = await self.product_repo.get_variant_by_id(variant_id)
        if not variant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Variant not found"
            )
        
        on_hand = variant.get('on_hand', 0)
        allocated = variant.get('allocated', 0)
        safety_stock = variant.get('safety_stock', 0)
        available = on_hand - allocated - safety_stock
        
        if quantity > available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Available: {max(0, available)}, Requested: {quantity}"
            )
        
        # Create ledger entry
        ledger_entry = {
            'variant_id': variant_id,
            'sku': variant['sku'],
            'reason': reason,
            'channel': channel,
            'on_hand_before': on_hand,
            'on_hand_after': on_hand,
            'on_hand_change': 0,
            'allocated_before': allocated,
            'allocated_after': allocated + quantity,
            'allocated_change': quantity,
            'reference_id': reference_id,
            'reference_type': reference_type,
            'notes': f"Allocated {quantity} units for {reason}",
            'created_by': user_id
        }
        
        await self.ledger_repo.create_entry(ledger_entry)
        
        # Update variant
        await self.product_repo.update_variant(variant_id, {
            'allocated': allocated + quantity
        })
        
        return await self.get_variant_inventory(variant_id)
    
    async def deallocate_stock(self, variant_id: str, quantity: int, reason: str, channel: Optional[str] = None,
                               reference_id: Optional[str] = None, reference_type: Optional[str] = None,
                               user_id: Optional[str] = None) -> Dict[str, Any]:
        """Deallocate stock (decrease allocated count)"""
        variant = await self.product_repo.get_variant_by_id(variant_id)
        if not variant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Variant not found"
            )
        
        allocated = variant.get('allocated', 0)
        on_hand = variant.get('on_hand', 0)
        
        # Create ledger entry
        ledger_entry = {
            'variant_id': variant_id,
            'sku': variant['sku'],
            'reason': reason,
            'channel': channel,
            'on_hand_before': on_hand,
            'on_hand_after': on_hand,
            'on_hand_change': 0,
            'allocated_before': allocated,
            'allocated_after': max(0, allocated - quantity),
            'allocated_change': -quantity,
            'reference_id': reference_id,
            'reference_type': reference_type,
            'notes': f"Deallocated {quantity} units for {reason}",
            'created_by': user_id
        }
        
        await self.ledger_repo.create_entry(ledger_entry)
        
        # Update variant
        await self.product_repo.update_variant(variant_id, {
            'allocated': max(0, allocated - quantity)
        })
        
        return await self.get_variant_inventory(variant_id)
    
    async def fulfill_stock(self, variant_id: str, quantity: int, reason: str, channel: Optional[str] = None,
                           reference_id: Optional[str] = None, reference_type: Optional[str] = None,
                           user_id: Optional[str] = None) -> Dict[str, Any]:
        """Fulfill stock (decrease both on_hand and allocated)"""
        variant = await self.product_repo.get_variant_by_id(variant_id)
        if not variant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Variant not found"
            )
        
        on_hand = variant.get('on_hand', 0)
        allocated = variant.get('allocated', 0)
        
        # Create ledger entry
        ledger_entry = {
            'variant_id': variant_id,
            'sku': variant['sku'],
            'reason': reason,
            'channel': channel,
            'on_hand_before': on_hand,
            'on_hand_after': max(0, on_hand - quantity),
            'on_hand_change': -quantity,
            'allocated_before': allocated,
            'allocated_after': max(0, allocated - quantity),
            'allocated_change': -quantity,
            'reference_id': reference_id,
            'reference_type': reference_type,
            'notes': f"Fulfilled {quantity} units for {reason}",
            'created_by': user_id
        }
        
        await self.ledger_repo.create_entry(ledger_entry)
        
        # Update variant
        await self.product_repo.update_variant(variant_id, {
            'on_hand': max(0, on_hand - quantity),
            'allocated': max(0, allocated - quantity)
        })
        
        return await self.get_variant_inventory(variant_id)
    
    async def adjust_stock(self, adjustment: StockAdjustment, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Manual stock adjustment"""
        variant = await self.product_repo.get_variant_by_id(adjustment.variant_id)
        if not variant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Variant not found"
            )
        
        on_hand = variant.get('on_hand', 0)
        allocated = variant.get('allocated', 0)
        
        # Initialize changes
        on_hand_change = 0
        allocated_change = 0
        new_on_hand = on_hand
        new_allocated = allocated
        
        # Handle on_hand adjustments
        if adjustment.on_hand_value is not None or adjustment.on_hand_change is not None:
            if adjustment.adjustment_type == 'set':
                if adjustment.on_hand_value is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="on_hand_value is required for 'set' adjustment type"
                    )
                new_on_hand = adjustment.on_hand_value
                on_hand_change = new_on_hand - on_hand
            else:  # change
                if adjustment.on_hand_change is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="on_hand_change is required for 'change' adjustment type"
                    )
                on_hand_change = adjustment.on_hand_change
                new_on_hand = on_hand + on_hand_change
        
        # Handle allocated adjustments
        if adjustment.allocated_value is not None or adjustment.allocated_change is not None:
            if adjustment.adjustment_type == 'set':
                if adjustment.allocated_value is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="allocated_value is required for 'set' adjustment type"
                    )
                new_allocated = adjustment.allocated_value
                allocated_change = new_allocated - allocated
            else:  # change
                if adjustment.allocated_change is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="allocated_change is required for 'change' adjustment type"
                    )
                allocated_change = adjustment.allocated_change
                new_allocated = allocated + allocated_change
        
        # Create ledger entry
        ledger_entry = {
            'variant_id': adjustment.variant_id,
            'sku': variant['sku'],
            'reason': adjustment.reason,
            'channel': 'manual',
            'on_hand_before': on_hand,
            'on_hand_after': new_on_hand,
            'on_hand_change': on_hand_change,
            'allocated_before': allocated,
            'allocated_after': new_allocated,
            'allocated_change': allocated_change,
            'reference_id': None,
            'reference_type': 'manual_adjustment',
            'notes': adjustment.notes,
            'created_by': user_id
        }
        
        await self.ledger_repo.create_entry(ledger_entry)
        
        # Update variant
        update_data = {}
        if on_hand_change != 0:
            update_data['on_hand'] = new_on_hand
        if allocated_change != 0:
            update_data['allocated'] = new_allocated
            
        if update_data:
            await self.product_repo.update_variant(adjustment.variant_id, update_data)
        
        return await self.get_variant_inventory(adjustment.variant_id)
    
    async def get_ledger_history(self, variant_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get inventory ledger history for a variant"""
        return await self.ledger_repo.get_by_variant(variant_id, skip, limit)
    
    async def import_external_order(self, external_order: ExternalOrderImport, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Import an external order from another channel (e.g., Shopee)"""
        allocations = []
        errors = []
        
        for item in external_order.items:
            # Find internal variant via channel mapping
            mapping = await self.mapping_repo.get_by_external_sku(external_order.channel, item.external_sku)
            
            if not mapping:
                errors.append(f"No mapping found for {external_order.channel} SKU: {item.external_sku}")
                continue
            
            try:
                result = await self.allocate_stock(
                    variant_id=mapping['internal_variant_id'],
                    quantity=item.quantity,
                    reason='order_created',
                    channel=external_order.channel,
                    reference_id=external_order.external_order_id,
                    reference_type='external_order',
                    user_id=user_id
                )
                allocations.append(result)
            except HTTPException as e:
                errors.append(f"{item.external_sku}: {e.detail}")
        
        return {
            'external_order_id': external_order.external_order_id,
            'channel': external_order.channel,
            'allocations': allocations,
            'errors': errors
        }
    
    async def create_channel_mapping(self, mapping: ChannelMappingCreate) -> Dict[str, Any]:
        """Create a new channel mapping"""
        # Check if variant exists
        variant = await self.product_repo.get_variant_by_id(mapping.internal_variant_id)
        if not variant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Internal variant not found"
            )
        
        mapping_data = mapping.model_dump()
        mapping_data['internal_sku'] = variant['sku']
        
        return await self.mapping_repo.create(mapping_data)
    
    async def list_all_inventory(self) -> List[Dict[str, Any]]:
        """List all variants with inventory status"""
        # Get all variants
        # Note: This is a simplified version; in production, you'd want pagination
        from app.repositories.product_repository import ProductRepository
        product_repo = self.product_repo
        
        # This would need to be implemented properly with product fetching
        # For now, return empty list
        return []
