from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from app.schemas.promotion import (
    Coupon, CouponCreate, CouponUpdate, CouponUsage, CouponUsageCreate,
    GiftItem, GiftItemCreate, GiftItemUpdate,
    GiftTier, GiftTierCreate, GiftTierUpdate
)
import uuid
from fastapi import HTTPException, status

class PromotionRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.coupons = database.coupons
        self.gift_items = database.gift_items
        self.gift_tiers = database.gift_tiers
        self.coupon_usage = database.coupon_usage

    # ==================== COUPON MANAGEMENT ====================

    async def create_coupon(self, coupon_data: CouponCreate) -> Coupon:
        """Create a new coupon"""
        # Check if coupon code already exists
        existing = await self.coupons.find_one({"code": coupon_data.code.upper()})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Coupon code '{coupon_data.code}' already exists"
            )

        coupon_dict = coupon_data.dict()
        coupon_dict.update({
            "id": str(uuid.uuid4()),
            "code": coupon_data.code.upper(),  # Store codes in uppercase
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "usage_count": 0,
            "status": "active"
        })

        await self.coupons.insert_one(coupon_dict)
        return Coupon(**coupon_dict)

    async def get_coupon_by_code(self, code: str) -> Optional[Coupon]:
        """Get coupon by code"""
        coupon_doc = await self.coupons.find_one({"code": code.upper()})
        return Coupon(**coupon_doc) if coupon_doc else None

    async def get_coupon_by_id(self, coupon_id: str) -> Optional[Coupon]:
        """Get coupon by ID"""
        coupon_doc = await self.coupons.find_one({"id": coupon_id})
        return Coupon(**coupon_doc) if coupon_doc else None

    async def list_coupons(self, skip: int = 0, limit: int = 100) -> List[Coupon]:
        """List all coupons"""
        cursor = self.coupons.find().skip(skip).limit(limit).sort("created_at", -1)
        coupons = await cursor.to_list(length=limit)
        return [Coupon(**coupon) for coupon in coupons]

    async def update_coupon(self, coupon_id: str, update_data: CouponUpdate) -> Optional[Coupon]:
        """Update coupon"""
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        update_dict["updated_at"] = datetime.now(timezone.utc)

        result = await self.coupons.update_one(
            {"id": coupon_id},
            {"$set": update_dict}
        )

        if result.matched_count == 0:
            return None

        return await self.get_coupon_by_id(coupon_id)

    async def delete_coupon(self, coupon_id: str) -> bool:
        """Delete coupon"""
        result = await self.coupons.delete_one({"id": coupon_id})
        return result.deleted_count > 0

    async def increment_coupon_usage(self, coupon_id: str) -> bool:
        """Increment coupon usage count"""
        result = await self.coupons.update_one(
            {"id": coupon_id},
            {"$inc": {"usage_count": 1}}
        )
        return result.modified_count > 0

    # ==================== GIFT ITEM MANAGEMENT ====================

    async def create_gift_item(self, gift_data: GiftItemCreate) -> GiftItem:
        """Create a new gift item"""
        gift_dict = gift_data.dict()
        gift_dict.update({
            "id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        })

        await self.gift_items.insert_one(gift_dict)
        return GiftItem(**gift_dict)

    async def get_gift_item_by_id(self, gift_id: str) -> Optional[GiftItem]:
        """Get gift item by ID"""
        gift_doc = await self.gift_items.find_one({"id": gift_id})
        return GiftItem(**gift_doc) if gift_doc else None

    async def list_gift_items(self, active_only: bool = False) -> List[GiftItem]:
        """List gift items"""
        filter_query = {"is_active": True} if active_only else {}
        cursor = self.gift_items.find(filter_query).sort("name", 1)
        gifts = await cursor.to_list(length=None)
        return [GiftItem(**gift) for gift in gifts]

    async def update_gift_item(self, gift_id: str, update_data: GiftItemUpdate) -> Optional[GiftItem]:
        """Update gift item"""
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        update_dict["updated_at"] = datetime.now(timezone.utc)

        result = await self.gift_items.update_one(
            {"id": gift_id},
            {"$set": update_dict}
        )

        if result.matched_count == 0:
            return None

        return await self.get_gift_item_by_id(gift_id)

    async def delete_gift_item(self, gift_id: str) -> bool:
        """Delete gift item"""
        result = await self.gift_items.delete_one({"id": gift_id})
        return result.deleted_count > 0

    # ==================== GIFT TIER MANAGEMENT ====================

    async def create_gift_tier(self, tier_data: GiftTierCreate) -> GiftTier:
        """Create a new gift tier"""
        tier_dict = tier_data.dict()
        tier_dict.update({
            "id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        })

        await self.gift_tiers.insert_one(tier_dict)
        return await self.get_gift_tier_by_id_with_items(tier_dict["id"])

    async def get_gift_tier_by_id(self, tier_id: str) -> Optional[GiftTier]:
        """Get gift tier by ID (without items)"""
        tier_doc = await self.gift_tiers.find_one({"id": tier_id})
        if not tier_doc:
            return None

        tier_doc["gift_items"] = []  # Empty list for basic fetch
        return GiftTier(**tier_doc)

    async def get_gift_tier_by_id_with_items(self, tier_id: str) -> Optional[GiftTier]:
        """Get gift tier by ID with populated gift items"""
        tier_doc = await self.gift_tiers.find_one({"id": tier_id})
        if not tier_doc:
            return None

        # Populate gift items
        gift_items = []
        for gift_id in tier_doc.get("gift_item_ids", []):
            gift_item = await self.get_gift_item_by_id(gift_id)
            if gift_item and gift_item.is_active:
                gift_items.append(gift_item)

        tier_doc["gift_items"] = [gift.dict() for gift in gift_items]
        return GiftTier(**tier_doc)

    async def list_gift_tiers(self, active_only: bool = False) -> List[GiftTier]:
        """List gift tiers with populated items"""
        filter_query = {"is_active": True} if active_only else {}
        cursor = self.gift_tiers.find(filter_query).sort("spending_threshold", 1)
        tiers = await cursor.to_list(length=None)

        result = []
        for tier in tiers:
            tier_with_items = await self.get_gift_tier_by_id_with_items(tier["id"])
            if tier_with_items:
                result.append(tier_with_items)

        return result

    async def update_gift_tier(self, tier_id: str, update_data: GiftTierUpdate) -> Optional[GiftTier]:
        """Update gift tier"""
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        update_dict["updated_at"] = datetime.now(timezone.utc)

        result = await self.gift_tiers.update_one(
            {"id": tier_id},
            {"$set": update_dict}
        )

        if result.matched_count == 0:
            return None

        return await self.get_gift_tier_by_id_with_items(tier_id)

    async def delete_gift_tier(self, tier_id: str) -> bool:
        """Delete gift tier"""
        result = await self.gift_tiers.delete_one({"id": tier_id})
        return result.deleted_count > 0

    async def get_available_gift_tiers_for_amount(self, amount: float) -> List[GiftTier]:
        """Get gift tiers available for given amount"""
        cursor = self.gift_tiers.find({
            "spending_threshold": {"$lte": amount},
            "is_active": True
        }).sort("spending_threshold", -1)  # Highest threshold first
        
        tiers = await cursor.to_list(length=None)
        
        result = []
        for tier in tiers:
            tier_with_items = await self.get_gift_tier_by_id_with_items(tier["id"])
            if tier_with_items and tier_with_items.gift_items:
                result.append(tier_with_items)
        
        return result

    # ==================== COUPON USAGE TRACKING ====================

    async def record_coupon_usage(self, usage_data: CouponUsageCreate) -> CouponUsage:
        """Record coupon usage"""
        usage_dict = usage_data.dict()
        usage_dict.update({
            "id": str(uuid.uuid4()),
            "used_at": datetime.now(timezone.utc)
        })

        await self.coupon_usage.insert_one(usage_dict)
        return CouponUsage(**usage_dict)

    async def get_coupon_usage_count(self, coupon_id: str) -> int:
        """Get total usage count for a coupon"""
        count = await self.coupon_usage.count_documents({"coupon_id": coupon_id})
        return count

    async def get_user_coupon_usage(self, user_id: str, coupon_id: str) -> int:
        """Get usage count for specific user and coupon"""
        count = await self.coupon_usage.count_documents({
            "user_id": user_id,
            "coupon_id": coupon_id
        })
        return count