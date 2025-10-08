from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.schemas.promotion import (
    Coupon, CouponCreate, CouponUpdate,
    GiftItem, GiftItemCreate, GiftItemUpdate,
    GiftTier, GiftTierCreate, GiftTierUpdate,
    PromotionValidation, PromotionResult
)
from app.services.promotion_service import PromotionService
from app.repositories.promotion_repository import PromotionRepository
from app.core.database import get_database
from app.core.security import get_current_user_id, get_current_user_optional

router = APIRouter()

# Dependency to get promotion service
async def get_promotion_service():
    database = get_database()
    promotion_repo = PromotionRepository(database)
    return PromotionService(promotion_repo)

# ==================== ADMIN COUPON MANAGEMENT ====================

@router.post("/admin/coupons", response_model=Coupon, tags=["Admin - Promotions"])
async def create_coupon(
    coupon_data: CouponCreate,
    user_id: str = Depends(get_current_user_id),
    service: PromotionService = Depends(get_promotion_service)
):
    """Create a new coupon (Admin only)"""
    # TODO: Add admin role check
    return await service.create_coupon(coupon_data)

@router.get("/admin/coupons", response_model=List[Coupon], tags=["Admin - Promotions"])
async def list_coupons(
    user_id: str = Depends(get_current_user_id),
    service: PromotionService = Depends(get_promotion_service)
):
    """List all coupons (Admin only)"""
    # TODO: Add admin role check
    return await service.get_all_coupons()

@router.get("/admin/coupons/{coupon_id}", response_model=Coupon, tags=["Admin - Promotions"])
async def get_coupon(
    coupon_id: str,
    user_id: str = Depends(get_current_user_id),
    service: PromotionService = Depends(get_promotion_service)
):
    """Get coupon details (Admin only)"""
    # TODO: Add admin role check
    return await service.get_coupon(coupon_id)

@router.put("/admin/coupons/{coupon_id}", response_model=Coupon, tags=["Admin - Promotions"])
async def update_coupon(
    coupon_id: str,
    update_data: CouponUpdate,
    user_id: str = Depends(get_current_user_id),
    service: PromotionService = Depends(get_promotion_service)
):
    """Update coupon (Admin only)"""
    # TODO: Add admin role check
    return await service.update_coupon(coupon_id, update_data)

@router.delete("/admin/coupons/{coupon_id}", tags=["Admin - Promotions"])
async def delete_coupon(
    coupon_id: str,
    user_id: str = Depends(get_current_user_id),
    service: PromotionService = Depends(get_promotion_service)
):
    """Delete coupon (Admin only)"""
    # TODO: Add admin role check
    await service.delete_coupon(coupon_id)
    return {"message": "Coupon deleted successfully"}

# ==================== ADMIN GIFT ITEM MANAGEMENT ====================

@router.post("/admin/gift-items", response_model=GiftItem, tags=["Admin - Promotions"])
async def create_gift_item(
    gift_data: GiftItemCreate,
    user_id: str = Depends(get_current_user_id),
    service: PromotionService = Depends(get_promotion_service)
):
    """Create a new gift item (Admin only)"""
    # TODO: Add admin role check
    return await service.create_gift_item(gift_data)

@router.get("/admin/gift-items", response_model=List[GiftItem], tags=["Admin - Promotions"])
async def list_gift_items(
    user_id: str = Depends(get_current_user_id),
    service: PromotionService = Depends(get_promotion_service)
):
    """List all gift items (Admin only)"""
    # TODO: Add admin role check
    return await service.get_all_gift_items()

@router.get("/admin/gift-items/{gift_id}", response_model=GiftItem, tags=["Admin - Promotions"])
async def get_gift_item(
    gift_id: str,
    user_id: str = Depends(get_current_user_id),
    service: PromotionService = Depends(get_promotion_service)
):
    """Get gift item details (Admin only)"""
    # TODO: Add admin role check
    return await service.get_gift_item(gift_id)

@router.put("/admin/gift-items/{gift_id}", response_model=GiftItem, tags=["Admin - Promotions"])
async def update_gift_item(
    gift_id: str,
    update_data: GiftItemUpdate,
    user_id: str = Depends(get_current_user_id),
    service: PromotionService = Depends(get_promotion_service)
):
    """Update gift item (Admin only)"""
    # TODO: Add admin role check
    return await service.update_gift_item(gift_id, update_data)

@router.delete("/admin/gift-items/{gift_id}", tags=["Admin - Promotions"])
async def delete_gift_item(
    gift_id: str,
    user_id: str = Depends(get_current_user_id),
    service: PromotionService = Depends(get_promotion_service)
):
    """Delete gift item (Admin only)"""
    # TODO: Add admin role check
    await service.delete_gift_item(gift_id)
    return {"message": "Gift item deleted successfully"}

# ==================== ADMIN GIFT TIER MANAGEMENT ====================

@router.post("/admin/gift-tiers", response_model=GiftTier, tags=["Admin - Promotions"])
async def create_gift_tier(
    tier_data: GiftTierCreate,
    user_id: str = Depends(get_current_user_id),
    service: PromotionService = Depends(get_promotion_service)
):
    """Create a new gift tier (Admin only)"""
    # TODO: Add admin role check
    return await service.create_gift_tier(tier_data)

@router.get("/admin/gift-tiers", response_model=List[GiftTier], tags=["Admin - Promotions"])
async def list_gift_tiers(
    user_id: str = Depends(get_current_user_id),
    service: PromotionService = Depends(get_promotion_service)
):
    """List all gift tiers (Admin only)"""
    # TODO: Add admin role check
    return await service.get_all_gift_tiers()

@router.get("/admin/gift-tiers/{tier_id}", response_model=GiftTier, tags=["Admin - Promotions"])
async def get_gift_tier(
    tier_id: str,
    user_id: str = Depends(get_current_user_id),
    service: PromotionService = Depends(get_promotion_service)
):
    """Get gift tier details (Admin only)"""
    # TODO: Add admin role check
    return await service.get_gift_tier(tier_id)

@router.put("/admin/gift-tiers/{tier_id}", response_model=GiftTier, tags=["Admin - Promotions"])
async def update_gift_tier(
    tier_id: str,
    update_data: GiftTierUpdate,
    user_id: str = Depends(get_current_user_id),
    service: PromotionService = Depends(get_promotion_service)
):
    """Update gift tier (Admin only)"""
    # TODO: Add admin role check
    return await service.update_gift_tier(tier_id, update_data)

@router.delete("/admin/gift-tiers/{tier_id}", tags=["Admin - Promotions"])
async def delete_gift_tier(
    tier_id: str,
    user_id: str = Depends(get_current_user_id),
    service: PromotionService = Depends(get_promotion_service)
):
    """Delete gift tier (Admin only)"""
    # TODO: Add admin role check
    await service.delete_gift_tier(tier_id)
    return {"message": "Gift tier deleted successfully"}

# ==================== CUSTOMER PROMOTION VALIDATION ====================

@router.post("/promotions/validate", response_model=PromotionResult, tags=["Promotions"])
async def validate_promotion(
    validation_data: PromotionValidation,
    user_id: Optional[str] = Depends(get_current_user_optional),
    service: PromotionService = Depends(get_promotion_service)
):
    """Validate coupon code and get available gift tiers"""
    # Add user_id to validation if user is logged in
    if user_id:
        validation_data.user_id = user_id
    
    return await service.validate_promotion(validation_data)

@router.get("/gift-tiers/available", response_model=List[GiftTier], tags=["Promotions"])
async def get_available_gift_tiers(
    order_amount: float = Query(..., gt=0, description="Order total amount"),
    service: PromotionService = Depends(get_promotion_service)
):
    """Get available gift tiers for given order amount"""
    promotion_repo = PromotionRepository(get_database())
    return await promotion_repo.get_available_gift_tiers_for_amount(order_amount)

@router.get("/gift-tiers/nearby", tags=["Promotions"])
async def get_nearby_gift_tiers(
    order_amount: float = Query(..., gt=0, description="Current order total amount"),
    service: PromotionService = Depends(get_promotion_service)
):
    """Get nearby gift tiers for promotional messages"""
    promotion_repo = PromotionRepository(get_database())
    
    # Get all active gift tiers
    all_tiers = await promotion_repo.get_all_gift_tiers()
    active_tiers = [tier for tier in all_tiers if tier.is_active]
    
    # Find tiers that are close but not yet achieved
    nearby_tiers = []
    for tier in active_tiers:
        if tier.spending_threshold > order_amount:
            gap = tier.spending_threshold - order_amount
            # Only show tiers within $50 gap
            if gap <= 50.0:
                nearby_tiers.append({
                    "tier_name": tier.name,
                    "spending_threshold": tier.spending_threshold,
                    "amount_needed": gap,
                    "gift_count": len(tier.gift_items or [])
                })
    
    # Sort by smallest gap first
    nearby_tiers.sort(key=lambda x: x["amount_needed"])
    
    return {"nearby_tiers": nearby_tiers[:2]}  # Return top 2 closest tiers

# ==================== ADMIN STATISTICS ====================

@router.get("/admin/promotions/stats", tags=["Admin - Promotions"])
async def get_promotion_stats(
    user_id: str = Depends(get_current_user_id),
    service: PromotionService = Depends(get_promotion_service)
):
    """Get promotion usage statistics (Admin only)"""
    # TODO: Add admin role check
    return await service.get_promotion_stats()