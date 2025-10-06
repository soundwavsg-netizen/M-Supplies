from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Optional, List

from app.core.database import connect_to_mongo, close_mongo_connection, get_database
from app.core.config import settings
from app.core.security import get_current_user_id, get_current_user_optional

# Schemas
from app.schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse, UserUpdate
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListItem
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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=settings.cors_origins.split(',') if settings.cors_origins != '*' else ['*'],
    allow_methods=["*"],
    allow_headers=["*"],
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
    order_service = OrderService(order_repo, cart_repo, product_repo, coupon_repo)
    
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
    order_service = OrderService(order_repo, cart_repo, product_repo, coupon_repo)
    
    return await order_service.list_user_orders(user_id, skip, limit)


@api_router.get("/orders/{order_id}", response_model=OrderResponse, tags=["Orders"])
async def get_order(order_id: str, user_id: str = Depends(get_current_user_id)):
    """Get order by ID"""
    db = get_database()
    order_repo = OrderRepository(db)
    cart_repo = CartRepository(db)
    product_repo = ProductRepository(db)
    coupon_repo = CouponRepository(db)
    order_service = OrderService(order_repo, cart_repo, product_repo, coupon_repo)
    
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
    order_service = OrderService(order_repo, cart_repo, product_repo, coupon_repo)
    
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
    order_service = OrderService(order_repo, cart_repo, product_repo, coupon_repo)
    
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


# Include router
app.include_router(api_router)


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
