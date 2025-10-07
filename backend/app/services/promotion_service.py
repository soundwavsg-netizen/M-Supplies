from app.repositories.promotion_repository import PromotionRepository
from app.schemas.promotion import (
    Coupon, CouponCreate, CouponUpdate,
    GiftItem, GiftItemCreate, GiftItemUpdate,
    GiftTier, GiftTierCreate, GiftTierUpdate,
    PromotionValidation, PromotionResult,
    AppliedPromotion, CouponUsageCreate
)
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import HTTPException, status

class PromotionService:
    def __init__(self, promotion_repo: PromotionRepository):
        self.promotion_repo = promotion_repo

    # ==================== COUPON MANAGEMENT ====================

    async def create_coupon(self, coupon_data: CouponCreate) -> Coupon:
        """Create a new coupon with validation"""
        # Validate discount value based on type
        if coupon_data.discount_type == "percentage" and coupon_data.discount_value > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Percentage discount cannot exceed 100%"
            )

        return await self.promotion_repo.create_coupon(coupon_data)

    async def get_all_coupons(self) -> List[Coupon]:
        """Get all coupons"""
        return await self.promotion_repo.list_coupons()

    async def get_coupon(self, coupon_id: str) -> Coupon:
        """Get coupon by ID"""
        coupon = await self.promotion_repo.get_coupon_by_id(coupon_id)
        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coupon not found"
            )
        return coupon

    async def update_coupon(self, coupon_id: str, update_data: CouponUpdate) -> Coupon:
        """Update coupon"""
        coupon = await self.promotion_repo.update_coupon(coupon_id, update_data)
        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coupon not found"
            )
        return coupon

    async def delete_coupon(self, coupon_id: str) -> bool:
        """Delete coupon"""
        deleted = await self.promotion_repo.delete_coupon(coupon_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coupon not found"
            )
        return True

    # ==================== GIFT MANAGEMENT ====================

    async def create_gift_item(self, gift_data: GiftItemCreate) -> GiftItem:
        """Create a new gift item"""
        return await self.promotion_repo.create_gift_item(gift_data)

    async def get_all_gift_items(self) -> List[GiftItem]:
        """Get all gift items"""
        return await self.promotion_repo.list_gift_items()

    async def get_gift_item(self, gift_id: str) -> GiftItem:
        """Get gift item by ID"""
        gift = await self.promotion_repo.get_gift_item_by_id(gift_id)
        if not gift:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gift item not found"
            )
        return gift

    async def update_gift_item(self, gift_id: str, update_data: GiftItemUpdate) -> GiftItem:
        """Update gift item"""
        gift = await self.promotion_repo.update_gift_item(gift_id, update_data)
        if not gift:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gift item not found"
            )
        return gift

    async def delete_gift_item(self, gift_id: str) -> bool:
        """Delete gift item"""
        deleted = await self.promotion_repo.delete_gift_item(gift_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gift item not found"
            )
        return True

    # ==================== GIFT TIER MANAGEMENT ====================

    async def create_gift_tier(self, tier_data: GiftTierCreate) -> GiftTier:
        """Create a new gift tier"""
        return await self.promotion_repo.create_gift_tier(tier_data)

    async def get_all_gift_tiers(self) -> List[GiftTier]:
        """Get all gift tiers"""
        return await self.promotion_repo.list_gift_tiers()

    async def get_gift_tier(self, tier_id: str) -> GiftTier:
        """Get gift tier by ID"""
        tier = await self.promotion_repo.get_gift_tier_by_id_with_items(tier_id)
        if not tier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gift tier not found"
            )
        return tier

    async def update_gift_tier(self, tier_id: str, update_data: GiftTierUpdate) -> GiftTier:
        """Update gift tier"""
        tier = await self.promotion_repo.update_gift_tier(tier_id, update_data)
        if not tier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gift tier not found"
            )
        return tier

    async def delete_gift_tier(self, tier_id: str) -> bool:
        """Delete gift tier"""
        deleted = await self.promotion_repo.delete_gift_tier(tier_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gift tier not found"
            )
        return True

    # ==================== PROMOTION VALIDATION ====================

    async def validate_promotion(self, validation_data: PromotionValidation) -> PromotionResult:
        """Validate coupon and determine available gift tiers"""
        result = PromotionResult(
            valid=True,
            discount_amount=0,
            available_gift_tiers=[],
            applied_coupon=None
        )

        # Validate coupon if provided
        if validation_data.coupon_code:
            coupon_result = await self._validate_coupon(
                validation_data.coupon_code,
                validation_data.order_subtotal,
                validation_data.user_id
            )
            
            if not coupon_result["valid"]:
                result.valid = False
                result.error_message = coupon_result["error"]
                return result
            
            result.discount_amount = coupon_result["discount_amount"]
            result.applied_coupon = coupon_result["coupon"]

        # Calculate final order total after discount
        final_total = validation_data.order_subtotal - result.discount_amount

        # Get available gift tiers based on final total
        result.available_gift_tiers = await self.promotion_repo.get_available_gift_tiers_for_amount(final_total)

        return result

    async def _validate_coupon(self, coupon_code: str, order_total: float, user_id: Optional[str]) -> dict:
        """Internal coupon validation logic"""
        # Get coupon
        coupon = await self.promotion_repo.get_coupon_by_code(coupon_code)
        if not coupon:
            return {"valid": False, "error": f"Coupon '{coupon_code}' not found"}

        # Check if active
        if not coupon.is_active:
            return {"valid": False, "error": f"Coupon '{coupon_code}' is not active"}

        # Check expiry
        if coupon.expires_at:
            # Handle both timezone-aware and naive datetimes
            current_time = datetime.now(timezone.utc)
            expires_at = coupon.expires_at
            
            # If expires_at is naive, assume it's UTC
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            
            if expires_at < current_time:
                return {"valid": False, "error": f"Coupon '{coupon_code}' has expired"}

        # Check minimum order amount
        if coupon.minimum_order_amount and order_total < coupon.minimum_order_amount:
            return {
                "valid": False, 
                "error": f"Minimum order amount ${coupon.minimum_order_amount:.2f} required for this coupon"
            }

        # Check usage limits
        if coupon.usage_type == "single_use":
            if user_id:
                user_usage = await self.promotion_repo.get_user_coupon_usage(user_id, coupon.id)
                if user_usage > 0:
                    return {"valid": False, "error": f"Coupon '{coupon_code}' has already been used"}
            else:
                return {"valid": False, "error": "Login required to use this coupon"}

        if coupon.usage_type == "limited_use" and coupon.usage_limit:
            total_usage = await self.promotion_repo.get_coupon_usage_count(coupon.id)
            if total_usage >= coupon.usage_limit:
                return {"valid": False, "error": f"Coupon '{coupon_code}' usage limit exceeded"}

        # Calculate discount amount
        if coupon.discount_type == "fixed":
            discount_amount = min(coupon.discount_value, order_total)
        else:  # percentage
            discount_amount = order_total * (coupon.discount_value / 100)
            if coupon.maximum_discount_amount:
                discount_amount = min(discount_amount, coupon.maximum_discount_amount)

        return {
            "valid": True,
            "coupon": coupon,
            "discount_amount": round(discount_amount, 2)
        }

    async def apply_promotion_to_order(self, order_id: str, validation_data: PromotionValidation, selected_gifts: List[dict] = None) -> AppliedPromotion:
        """Apply validated promotion to order and record usage"""
        validation_result = await self.validate_promotion(validation_data)
        
        if not validation_result.valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation_result.error_message
            )

        applied_promotion = AppliedPromotion(
            discount_amount=validation_result.discount_amount,
            selected_gifts=selected_gifts or []
        )

        # Record coupon usage if coupon was applied
        if validation_result.applied_coupon:
            applied_promotion.coupon_code = validation_result.applied_coupon.code
            
            # Record usage
            usage_data = CouponUsageCreate(
                coupon_id=validation_result.applied_coupon.id,
                user_id=validation_data.user_id,
                order_id=order_id,
                discount_applied=validation_result.discount_amount,
                order_total=validation_data.order_subtotal
            )
            await self.promotion_repo.record_coupon_usage(usage_data)
            
            # Increment usage counter
            await self.promotion_repo.increment_coupon_usage(validation_result.applied_coupon.id)

        return applied_promotion

    # ==================== ADMIN STATS ====================

    async def get_promotion_stats(self) -> dict:
        """Get promotion usage statistics"""
        coupons = await self.promotion_repo.list_coupons()
        gift_items = await self.promotion_repo.list_gift_items()
        gift_tiers = await self.promotion_repo.list_gift_tiers()

        return {
            "total_coupons": len(coupons),
            "active_coupons": len([c for c in coupons if c.is_active]),
            "total_gift_items": len(gift_items),
            "active_gift_items": len([g for g in gift_items if g.is_active]),
            "total_gift_tiers": len(gift_tiers),
            "active_gift_tiers": len([t for t in gift_tiers if t.is_active])
        }