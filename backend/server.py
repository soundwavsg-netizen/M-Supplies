from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Header, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
from typing import Optional, List

from app.core.database import connect_to_mongo, close_mongo_connection, get_database
from app.core.config import settings
from app.core.security import get_current_user_id, get_current_user_optional

# Schemas
from app.schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse, UserUpdate
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListItem, ProductListRequest
from app.schemas.cart import AddToCartRequest, UpdateCartItemRequest, CartResponse
from app.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate
from app.schemas.coupon import CouponCreate, CouponUpdate, CouponResponse, CouponValidation
from app.schemas.inventory import (
    InventoryStatus, StockAdjustment, ExternalOrderImport, 
    ChannelMappingCreate, InventoryLedgerEntry, BusinessSettings
)

# Repositories
from app.repositories.user_repository import UserRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.coupon_repository import CouponRepository
from app.repositories.inventory_repository import (
    InventoryLedgerRepository, ChannelMappingRepository, SettingsRepository
)

# Services
from app.services.auth_service import AuthService
from app.services.product_service import ProductService
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.services.payment_service import PaymentService
from app.services.inventory_service import InventoryService
from app.services.upload_service import UploadService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    logger.info("Application started")
    yield
    # Shutdown
    await close_mongo_connection()
    logger.info("Application stopped")

# Create app
app = FastAPI(title="Polymailer E-commerce API", lifespan=lifespan)

# Create router with /api prefix
api_router = APIRouter(prefix="/api")

# CORS - Allow both shop.m-supplies.sg and www.m-supplies.sg
cors_origins = settings.cors_origins.split(',') if settings.cors_origins != '*' else ['*']
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


# ==================== AUTH ROUTES ====================

@api_router.post("/auth/register", response_model=TokenResponse, tags=["Auth"])
async def register(user_data: UserCreate):
    """Register a new user"""
    db = get_database()
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    
    result = await auth_service.register(user_data)
    
    return TokenResponse(
        access_token=result['access_token'],
        refresh_token=result['refresh_token'],
        user=UserResponse(**result['user'])
    )


@api_router.post("/auth/login", response_model=TokenResponse, tags=["Auth"])
async def login(credentials: UserLogin):
    """Login user"""
    db = get_database()
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    
    result = await auth_service.login(credentials)
    
    return TokenResponse(
        access_token=result['access_token'],
        refresh_token=result['refresh_token'],
        user=UserResponse(**result['user'])
    )


@api_router.get("/auth/me", response_model=UserResponse, tags=["Auth"])
async def get_current_user(user_id: str = Depends(get_current_user_id)):
    """Get current user info"""
    db = get_database()
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    
    user = await auth_service.get_user_by_id(user_id)
    return UserResponse(**user)


# ==================== PRODUCT ROUTES ====================

@api_router.get("/products", response_model=List[ProductListItem], tags=["Products"])
async def list_products(
    skip: int = 0,
    limit: int = 50,
    category: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = True
):
    """List products"""
    db = get_database()
    product_repo = ProductRepository(db)
    product_service = ProductService(product_repo)
    
    return await product_service.list_products(skip, limit, category, search, is_active)


@api_router.post("/products/filter", tags=["Products"])
async def filter_products(request: ProductListRequest):
    """Advanced product filtering with support for colors, sizes, types, price ranges, etc."""
    db = get_database()
    product_repo = ProductRepository(db)
    product_service = ProductService(product_repo)
    
    skip = (request.page - 1) * request.limit
    return await product_service.list_products_filtered(
        filters=request.filters,
        sort=request.sort,
        skip=skip,
        limit=request.limit
    )


@api_router.get("/products/filter-options", tags=["Products"])
async def get_filter_options():
    """Get available filter options (colors, sizes, types, categories, price range)"""
    db = get_database()
    product_repo = ProductRepository(db)
    product_service = ProductService(product_repo)
    
    return await product_service.get_filter_options()


@api_router.get("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
async def get_product(product_id: str):
    """Get product by ID"""
    db = get_database()
    product_repo = ProductRepository(db)
    product_service = ProductService(product_repo)
    
    return await product_service.get_product(product_id)


@api_router.get("/categories", response_model=List[str], tags=["Products"])
async def get_categories():
    """Get all product categories"""
    db = get_database()
    product_repo = ProductRepository(db)
    product_service = ProductService(product_repo)
    
    return await product_service.get_categories()


# ==================== CART ROUTES ====================

@api_router.post("/cart/add", response_model=CartResponse, tags=["Cart"])
async def add_to_cart(
    request: AddToCartRequest,
    user_id: Optional[str] = Depends(get_current_user_optional),
    x_session_id: Optional[str] = Header(None)
):
    """Add item to cart"""
    db = get_database()
    cart_repo = CartRepository(db)
    product_repo = ProductRepository(db)
    cart_service = CartService(cart_repo, product_repo)
    
    return await cart_service.add_to_cart(
        request.variant_id,
        request.quantity,
        user_id,
        x_session_id
    )


@api_router.get("/cart", response_model=CartResponse, tags=["Cart"])
async def get_cart(
    user_id: Optional[str] = Depends(get_current_user_optional),
    x_session_id: Optional[str] = Header(None)
):
    """Get cart"""
    db = get_database()
    cart_repo = CartRepository(db)
    product_repo = ProductRepository(db)
    cart_service = CartService(cart_repo, product_repo)
    
    cart = await cart_service.get_or_create_cart(user_id, x_session_id)
    return await cart_service.get_cart_with_details(cart['id'], user_id, x_session_id)


@api_router.put("/cart/item/{variant_id}", response_model=CartResponse, tags=["Cart"])
async def update_cart_item(
    variant_id: str,
    request: UpdateCartItemRequest,
    user_id: Optional[str] = Depends(get_current_user_optional),
    x_session_id: Optional[str] = Header(None)
):
    """Update cart item quantity"""
    db = get_database()
    cart_repo = CartRepository(db)
    product_repo = ProductRepository(db)
    cart_service = CartService(cart_repo, product_repo)
    
    return await cart_service.update_cart_item(
        variant_id,
        request.quantity,
        user_id,
        x_session_id
    )


@api_router.delete("/cart", tags=["Cart"])
async def clear_cart(
    user_id: Optional[str] = Depends(get_current_user_optional),
    x_session_id: Optional[str] = Header(None)
):
    """Clear cart"""
    db = get_database()
    cart_repo = CartRepository(db)
    product_repo = ProductRepository(db)
    cart_service = CartService(cart_repo, product_repo)
    
    await cart_service.clear_cart(user_id, x_session_id)
    return {"message": "Cart cleared"}


# ==================== ORDER ROUTES ====================

@api_router.post("/orders", response_model=OrderResponse, tags=["Orders"])
async def create_order(
    order_data: OrderCreate,
    user_id: Optional[str] = Depends(get_current_user_optional),
    x_session_id: Optional[str] = Header(None)
):
    """Create order"""
    db = get_database()
    order_repo = OrderRepository(db)
    cart_repo = CartRepository(db)
    product_repo = ProductRepository(db)
    coupon_repo = CouponRepository(db)
    ledger_repo = InventoryLedgerRepository(db)
    order_service = OrderService(order_repo, cart_repo, product_repo, coupon_repo, ledger_repo)
    
    return await order_service.create_order(order_data, user_id, x_session_id)


@api_router.get("/orders", response_model=List[OrderResponse], tags=["Orders"])
async def list_my_orders(
    skip: int = 0,
    limit: int = 50,
    user_id: str = Depends(get_current_user_id)
):
    """List current user's orders"""
    db = get_database()
    order_repo = OrderRepository(db)
    cart_repo = CartRepository(db)
    product_repo = ProductRepository(db)
    coupon_repo = CouponRepository(db)
    ledger_repo = InventoryLedgerRepository(db)
    order_service = OrderService(order_repo, cart_repo, product_repo, coupon_repo, ledger_repo)
    
    return await order_service.list_user_orders(user_id, skip, limit)


@api_router.get("/orders/{order_id}", response_model=OrderResponse, tags=["Orders"])
async def get_order(order_id: str, user_id: str = Depends(get_current_user_id)):
    """Get order by ID"""
    db = get_database()
    order_repo = OrderRepository(db)
    cart_repo = CartRepository(db)
    product_repo = ProductRepository(db)
    coupon_repo = CouponRepository(db)
    ledger_repo = InventoryLedgerRepository(db)
    order_service = OrderService(order_repo, cart_repo, product_repo, coupon_repo, ledger_repo)
    
    order = await order_service.get_order(order_id)
    
    # Check if user owns this order
    if order.get('user_id') != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order"
        )
    
    return order


# ==================== PAYMENT ROUTES ====================

@api_router.post("/payment/create-intent", tags=["Payment"])
async def create_payment_intent(order_id: str):
    """Create Stripe payment intent for an order"""
    db = get_database()
    order_repo = OrderRepository(db)
    
    order = await order_repo.get_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    payment_service = PaymentService()
    result = await payment_service.create_payment_intent(
        amount=order['total'],
        currency=settings.default_currency,
        metadata={
            'order_id': order_id,
            'order_number': order['order_number']
        }
    )
    
    # Update order with payment intent ID
    await order_repo.update(order_id, {'payment_intent_id': result['payment_intent_id']})
    
    return result


@api_router.get("/payment/config", tags=["Payment"])
async def get_payment_config():
    """Get Stripe public key"""
    return {
        "public_key": settings.stripe_public_key,
        "currency": settings.default_currency
    }


# ==================== ADMIN ROUTES ====================

# Products Admin
@api_router.post("/admin/products", response_model=ProductResponse, tags=["Admin - Products"])
async def admin_create_product(
    product_data: ProductCreate,
    user_id: str = Depends(get_current_user_id)
):
    """Create product (Admin only)"""
    # TODO: Add role check
    db = get_database()
    product_repo = ProductRepository(db)
    product_service = ProductService(product_repo)
    
    return await product_service.create_product(product_data)


@api_router.put("/admin/products/{product_id}", response_model=ProductResponse, tags=["Admin - Products"])
async def admin_update_product(
    product_id: str,
    update_data: ProductUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """Update product (Admin only)"""
    # TODO: Add role check
    db = get_database()
    product_repo = ProductRepository(db)
    product_service = ProductService(product_repo)
    
    return await product_service.update_product(product_id, update_data)


@api_router.delete("/admin/products/{product_id}", tags=["Admin - Products"])
async def admin_delete_product(
    product_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete product (Admin only)"""
    # TODO: Add role check
    db = get_database()
    product_repo = ProductRepository(db)
    product_service = ProductService(product_repo)
    
    await product_service.delete_product(product_id)
    return {"message": "Product deleted"}


# Orders Admin
@api_router.get("/admin/orders", response_model=List[OrderResponse], tags=["Admin - Orders"])
async def admin_list_orders(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    search: Optional[str] = None,
    user_id: str = Depends(get_current_user_id)
):
    """List all orders (Admin only)"""
    # TODO: Add role check
    db = get_database()
    order_repo = OrderRepository(db)
    cart_repo = CartRepository(db)
    product_repo = ProductRepository(db)
    coupon_repo = CouponRepository(db)
    ledger_repo = InventoryLedgerRepository(db)
    order_service = OrderService(order_repo, cart_repo, product_repo, coupon_repo, ledger_repo)
    
    return await order_service.list_orders(skip, limit, status, search)


@api_router.put("/admin/orders/{order_id}/status", response_model=OrderResponse, tags=["Admin - Orders"])
async def admin_update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """Update order status (Admin only)"""
    # TODO: Add role check
    db = get_database()
    order_repo = OrderRepository(db)
    cart_repo = CartRepository(db)
    product_repo = ProductRepository(db)
    coupon_repo = CouponRepository(db)
    ledger_repo = InventoryLedgerRepository(db)
    order_service = OrderService(order_repo, cart_repo, product_repo, coupon_repo, ledger_repo)
    
    return await order_service.update_order_status(order_id, status_update)


# Coupons Admin
@api_router.post("/admin/coupons", response_model=CouponResponse, tags=["Admin - Coupons"])
async def admin_create_coupon(
    coupon_data: CouponCreate,
    user_id: str = Depends(get_current_user_id)
):
    """Create coupon (Admin only)"""
    # TODO: Add role check
    db = get_database()
    coupon_repo = CouponRepository(db)
    
    coupon_dict = coupon_data.model_dump()
    coupon_dict['code'] = coupon_dict['code'].upper()
    coupon = await coupon_repo.create(coupon_dict)
    
    return CouponResponse(**coupon)


@api_router.get("/admin/coupons", response_model=List[CouponResponse], tags=["Admin - Coupons"])
async def admin_list_coupons(
    skip: int = 0,
    limit: int = 50,
    is_active: Optional[bool] = None,
    user_id: str = Depends(get_current_user_id)
):
    """List coupons (Admin only)"""
    # TODO: Add role check
    db = get_database()
    coupon_repo = CouponRepository(db)
    
    coupons = await coupon_repo.list_coupons(skip, limit, is_active)
    return [CouponResponse(**c) for c in coupons]


@api_router.put("/admin/coupons/{coupon_id}", response_model=CouponResponse, tags=["Admin - Coupons"])
async def admin_update_coupon(
    coupon_id: str,
    update_data: CouponUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """Update coupon (Admin only)"""
    # TODO: Add role check
    db = get_database()
    coupon_repo = CouponRepository(db)
    
    coupon = await coupon_repo.get_by_id(coupon_id)
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    update_dict = update_data.model_dump(exclude_unset=True)
    if 'code' in update_dict:
        update_dict['code'] = update_dict['code'].upper()
    
    await coupon_repo.update(coupon_id, update_dict)
    
    updated_coupon = await coupon_repo.get_by_id(coupon_id)
    return CouponResponse(**updated_coupon)


# Users Admin
@api_router.get("/admin/users", response_model=List[UserResponse], tags=["Admin - Users"])
async def admin_list_users(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    user_id: str = Depends(get_current_user_id)
):
    """List users (Admin only)"""
    # TODO: Add role check
    db = get_database()
    user_repo = UserRepository(db)
    
    users = await user_repo.list_users(skip, limit, search)
    return [UserResponse(**{**u, 'password': None}) for u in users]


@api_router.put("/admin/users/{target_user_id}", response_model=UserResponse, tags=["Admin - Users"])
async def admin_update_user(
    target_user_id: str,
    update_data: UserUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """Update user (Admin only)"""
    # TODO: Add role check
    db = get_database()
    user_repo = UserRepository(db)
    
    user = await user_repo.get_by_id(target_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    update_dict = update_data.model_dump(exclude_unset=True)
    await user_repo.update(target_user_id, update_dict)
    
    updated_user = await user_repo.get_by_id(target_user_id)
    updated_user.pop('password', None)
    return UserResponse(**updated_user)



# ==================== INVENTORY ADMIN ROUTES ====================

@api_router.get("/admin/inventory", response_model=List[InventoryStatus], tags=["Admin - Inventory"])
async def admin_list_inventory(
    user_id: str = Depends(get_current_user_id)
):
    """List all inventory (Admin only)"""
    # TODO: Add role check
    db = get_database()
    product_repo = ProductRepository(db)
    ledger_repo = InventoryLedgerRepository(db)
    mapping_repo = ChannelMappingRepository(db)
    inventory_service = InventoryService(ledger_repo, product_repo, mapping_repo)
    
    # Get only active products (exclude deleted products)
    products = await product_repo.list_products(skip=0, limit=1000, is_active=True)
    inventory_list = []
    
    for product in products:
        variants = await product_repo.get_variants_by_product(product['id'])
        for variant in variants:
            on_hand = variant.get('on_hand', variant.get('stock_qty', 0))
            allocated = variant.get('allocated', 0)
            safety_stock = variant.get('safety_stock', 0)
            available = max(0, on_hand - allocated - safety_stock)
            low_stock_threshold = variant.get('low_stock_threshold', 10)
            
            inventory_list.append(InventoryStatus(
                variant_id=variant['id'],
                sku=variant['sku'],
                product_name=product['name'],
                on_hand=on_hand,
                allocated=allocated,
                available=available,
                safety_stock=safety_stock,
                low_stock_threshold=low_stock_threshold,
                is_low_stock=available < low_stock_threshold,
                channel_buffers=variant.get('channel_buffers', {})
            ))
    
    return inventory_list


@api_router.get("/admin/inventory/{variant_id}", response_model=InventoryStatus, tags=["Admin - Inventory"])
async def admin_get_variant_inventory(
    variant_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get inventory status for a specific variant (Admin only)"""
    # TODO: Add role check
    db = get_database()
    product_repo = ProductRepository(db)
    ledger_repo = InventoryLedgerRepository(db)
    mapping_repo = ChannelMappingRepository(db)
    inventory_service = InventoryService(ledger_repo, product_repo, mapping_repo)
    
    return await inventory_service.get_variant_inventory(variant_id)


@api_router.get("/admin/inventory/{variant_id}/ledger", response_model=List[InventoryLedgerEntry], tags=["Admin - Inventory"])
async def admin_get_inventory_ledger(
    variant_id: str,
    skip: int = 0,
    limit: int = 100,
    user_id: str = Depends(get_current_user_id)
):
    """Get inventory ledger history for a variant (Admin only)"""
    # TODO: Add role check
    db = get_database()
    product_repo = ProductRepository(db)
    ledger_repo = InventoryLedgerRepository(db)
    mapping_repo = ChannelMappingRepository(db)
    inventory_service = InventoryService(ledger_repo, product_repo, mapping_repo)
    
    history = await inventory_service.get_ledger_history(variant_id, skip, limit)
    return [InventoryLedgerEntry(**entry) for entry in history]


@api_router.post("/admin/inventory/adjust", response_model=InventoryStatus, tags=["Admin - Inventory"])
async def admin_adjust_stock(
    adjustment: StockAdjustment,
    user_id: str = Depends(get_current_user_id)
):
    """Manually adjust stock levels (Admin only)"""
    # TODO: Add role check
    db = get_database()
    product_repo = ProductRepository(db)
    ledger_repo = InventoryLedgerRepository(db)
    mapping_repo = ChannelMappingRepository(db)
    inventory_service = InventoryService(ledger_repo, product_repo, mapping_repo)
    
    return await inventory_service.adjust_stock(adjustment, user_id)


@api_router.post("/admin/external-orders/import", tags=["Admin - Inventory"])
async def admin_import_external_order(
    external_order: ExternalOrderImport,
    user_id: str = Depends(get_current_user_id)
):
    """Import external order from another channel (Admin only)"""
    # TODO: Add role check
    db = get_database()
    product_repo = ProductRepository(db)
    ledger_repo = InventoryLedgerRepository(db)
    mapping_repo = ChannelMappingRepository(db)
    inventory_service = InventoryService(ledger_repo, product_repo, mapping_repo)
    
    return await inventory_service.import_external_order(external_order, user_id)


@api_router.post("/admin/channel-mappings", tags=["Admin - Inventory"])
async def admin_create_channel_mapping(
    mapping: ChannelMappingCreate,
    user_id: str = Depends(get_current_user_id)
):
    """Create a new channel mapping (Admin only)"""
    # TODO: Add role check
    db = get_database()
    product_repo = ProductRepository(db)
    ledger_repo = InventoryLedgerRepository(db)
    mapping_repo = ChannelMappingRepository(db)
    inventory_service = InventoryService(ledger_repo, product_repo, mapping_repo)
    
    return await inventory_service.create_channel_mapping(mapping)


@api_router.get("/admin/channel-mappings/{channel}", tags=["Admin - Inventory"])
async def admin_list_channel_mappings(
    channel: str,
    user_id: str = Depends(get_current_user_id)
):
    """List all channel mappings for a specific channel (Admin only)"""
    # TODO: Add role check
    db = get_database()
    mapping_repo = ChannelMappingRepository(db)
    
    return await mapping_repo.list_by_channel(channel)


@api_router.get("/admin/settings", response_model=BusinessSettings, tags=["Admin - Settings"])
async def admin_get_settings(
    user_id: str = Depends(get_current_user_id)
):
    """Get business settings (Admin only)"""
    # TODO: Add role check
    db = get_database()
    settings_repo = SettingsRepository(db)
    
    settings_data = await settings_repo.get_settings()
    return BusinessSettings(**settings_data)


@api_router.put("/admin/settings", response_model=BusinessSettings, tags=["Admin - Settings"])
async def admin_update_settings(
    settings_update: BusinessSettings,
    user_id: str = Depends(get_current_user_id)
):
    """Update business settings (Admin only)"""
    # TODO: Add role check
    db = get_database()
    settings_repo = SettingsRepository(db)
    
    update_data = settings_update.model_dump()
    await settings_repo.update_settings(update_data)
    
    updated_settings = await settings_repo.get_settings()
    return BusinessSettings(**updated_settings)


# ==================== SHOPEE WEBHOOK (STUB) ====================

@api_router.post("/webhooks/shopee/orders", tags=["Webhooks"])
async def shopee_order_webhook(request: dict):
    """Shopee order webhook (Stub - disabled until keys provided)"""
    logger.info(f"Shopee webhook received: {request}")
    return {
        "status": "received",
        "message": "Webhook endpoint ready. Integration pending Shopee API keys."
    }



# ==================== FILE UPLOAD ROUTES ====================

@api_router.post("/admin/upload/image", tags=["Admin - Upload"])
async def upload_image(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id)
):
    """Upload a product image (Admin only)"""
    # TODO: Add role check
    image_url = await UploadService.upload_product_image(file)
    return {"url": image_url}


@api_router.post("/admin/upload/images", tags=["Admin - Upload"])
async def upload_images(
    files: List[UploadFile] = File(...),
    user_id: str = Depends(get_current_user_id)
):
    """Upload multiple product images (Admin only)"""
    # TODO: Add role check
    image_urls = await UploadService.upload_multiple_images(files)
    return {"urls": image_urls}


@api_router.get("/images/{filename}", tags=["Images"])
async def serve_image(filename: str):
    """Serve images with proper MIME types (bypasses ingress issues)"""
    from fastapi.responses import FileResponse
    import mimetypes
    from pathlib import Path
    
    # Security: only allow safe filenames
    if '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    upload_dir = Path(os.getenv('UPLOAD_DIR', '/app/backend/uploads'))
    file_path = upload_dir / "products" / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Determine MIME type
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if not mime_type or not mime_type.startswith('image/'):
        mime_type = 'image/jpeg'  # Default fallback
    
    return FileResponse(
        path=str(file_path),
        media_type=mime_type,
        headers={
            "Cache-Control": "public, max-age=3600",
            "Access-Control-Allow-Origin": "*"
        }
    )


# Include router
app.include_router(api_router)

# Serve uploaded files
import os
upload_dir = os.getenv('UPLOAD_DIR', '/app/backend/uploads')
if os.path.exists(upload_dir):
    app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
