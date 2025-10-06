"""
Seed data for Phase 2 - Advanced Product Filtering System
Creates products with the specific variants and attributes required for filtering
"""

import asyncio
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import os

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'polymailer_db')
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

async def clear_existing_data():
    """Clear existing product data"""
    await db.products.delete_many({})
    await db.variants.delete_many({})
    print("Cleared existing product data...")

async def create_polymailer_products():
    """Create polymailer products with exact specifications from Sean's requirements"""
    
    # Product 1: Normal Polymailers
    product1_id = str(uuid.uuid4())
    product1 = {
        'id': product1_id,
        'name': 'Premium Polymailers',
        'description': 'Durable, waterproof polymailers in vibrant colors. Bulk discounts available. Fast Singapore delivery.',
        'category': 'polymailers',
        'images': [
            'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800',
            'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=800'
        ],
        'specifications': {
            'material': 'LDPE (Low-Density Polyethylene)',
            'thickness': '60 micron',
            'feature': 'Self-sealing top',
            'waterproof': 'Yes',
            'tear_resistant': 'Standard'
        },
        'seo_title': 'Premium Polymailers | Colorful Shipping Bags Singapore',
        'seo_description': 'Buy premium polymailers in white, pastel pink, champagne pink, and milktea colors. Multiple sizes available.',
        'seo_keywords': ['polymailers', 'shipping bags', 'singapore', 'colorful', 'waterproof'],
        'is_active': True,
        'featured': True,
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc)
    }
    await db.products.insert_one(product1)
    
    # Normal polymailer variants
    colors = ['white', 'pastel pink', 'champagne pink', 'milktea']
    sizes = [
        {'width': 25, 'height': 35, 'code': '25x35'},
        {'width': 17, 'height': 30, 'code': '17x30'},
        {'width': 32, 'height': 43, 'code': '32x43'},
        {'width': 45, 'height': 60, 'code': '45x60'},
        {'width': 20, 'height': 28, 'code': '20x28'},
        {'width': 35, 'height': 45, 'code': '35x45'}
    ]
    
    variant_count = 0
    for size in sizes:
        for color in colors:
            # Calculate price based on size (area-based pricing)
            area = size['width'] * size['height']
            base_price = max(0.12, area * 0.0002)  # Minimum $0.12, area-based pricing
            
            # Color premium (milktea is premium color)
            if color == 'milktea':
                base_price *= 1.15
            elif color in ['pastel pink', 'champagne pink']:
                base_price *= 1.10
                
            variant = {
                'id': str(uuid.uuid4()),
                'product_id': product1_id,
                'sku': f'POLYMAILERS_NORMAL_{color.upper().replace(" ", "_")}_{size["code"]}',
                'attributes': {
                    'width_cm': size['width'],
                    'height_cm': size['height'],
                    'size_code': size['code'],
                    'type': 'normal',
                    'color': color,
                    'thickness': '60 micron'
                },
                'price_tiers': [
                    {'min_quantity': 1, 'price': round(base_price, 2)},
                    {'min_quantity': 50, 'price': round(base_price * 0.95, 2)},
                    {'min_quantity': 100, 'price': round(base_price * 0.90, 2)}
                ],
                'stock_qty': 200,  # Legacy field
                'on_hand': 200,
                'allocated': 0,
                'safety_stock': 10,
                'low_stock_threshold': 20,
                'channel_buffers': {'website': 0, 'shopee': 5},
                'cost_price': round(base_price * 0.55, 2),
                'created_at': datetime.now(timezone.utc)
            }
            await db.variants.insert_one(variant)
            variant_count += 1
    
    print(f"✅ Created product: {product1['name']} with {variant_count} variants")
    
    # Product 2: Bubble Wrap Polymailers (WHITE ONLY per business rule)
    product2_id = str(uuid.uuid4())
    product2 = {
        'id': product2_id,
        'name': 'Bubble Wrap Polymailers',
        'description': 'Extra protection with built-in bubble wrap lining. Perfect for fragile items and electronics. Available in white only.',
        'category': 'polymailers',
        'images': [
            'https://images.unsplash.com/photo-1586854982617-828a89d1e605?w=800',
            'https://images.unsplash.com/photo-1611734449268-e3c9c2c5b4d6?w=800'
        ],
        'specifications': {
            'material': 'LDPE with Bubble Wrap Lining',
            'thickness': '80 micron + bubble wrap',
            'feature': 'Built-in bubble wrap protection',
            'waterproof': 'Yes',
            'tear_resistant': 'Extra Strong'
        },
        'seo_title': 'Bubble Wrap Polymailers | Protected Shipping Bags Singapore',
        'seo_description': 'Premium bubble wrap polymailers for fragile items. Built-in protection, waterproof design.',
        'seo_keywords': ['bubble wrap', 'polymailers', 'fragile', 'protection', 'singapore'],
        'is_active': True,
        'featured': True,
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc)
    }
    await db.products.insert_one(product2)
    
    # Bubble wrap variants (WHITE ONLY - important business rule)
    bubble_sizes = [
        {'width': 25, 'height': 35, 'code': '25x35'},
        {'width': 32, 'height': 43, 'code': '32x43'},
        {'width': 45, 'height': 60, 'code': '45x60'}
    ]
    
    variant_count2 = 0
    for size in bubble_sizes:
        # Bubble wrap is premium - higher pricing
        area = size['width'] * size['height']
        base_price = max(0.25, area * 0.0003)  # Premium pricing
        
        variant = {
            'id': str(uuid.uuid4()),
            'product_id': product2_id,
            'sku': f'POLYMAILERS_BUBBLE WRAP_WHITE_{size["code"]}',
            'attributes': {
                'width_cm': size['width'],
                'height_cm': size['height'],
                'size_code': size['code'],
                'type': 'bubble wrap',
                'color': 'white',  # Only white available for bubble wrap
                'thickness': '80 micron + bubble wrap'
            },
            'price_tiers': [
                {'min_quantity': 1, 'price': round(base_price, 2)},
                {'min_quantity': 25, 'price': round(base_price * 0.95, 2)},
                {'min_quantity': 50, 'price': round(base_price * 0.90, 2)}
            ],
            'stock_qty': 100,  # Legacy field
            'on_hand': 100,
            'allocated': 0,
            'safety_stock': 8,
            'low_stock_threshold': 15,
            'channel_buffers': {'website': 0, 'shopee': 3},
            'cost_price': round(base_price * 0.6, 2),
            'created_at': datetime.now(timezone.utc)
        }
        await db.variants.insert_one(variant)
        variant_count2 += 1
    
    print(f"✅ Created product: {product2['name']} with {variant_count2} variants")

async def create_accessories():
    """Create accessory products"""
    
    # Scissors
    product3_id = str(uuid.uuid4())
    product3 = {
        'id': product3_id,
        'name': 'Heavy-Duty Packaging Scissors',
        'description': 'Professional grade scissors for cutting packaging materials, tapes, and polymailers. Ergonomic design for comfort.',
        'category': 'accessories',
        'images': [
            'https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=800'
        ],
        'specifications': {
            'material': 'Stainless Steel Blades',
            'handle': 'Ergonomic Plastic',
            'length': '8 inches',
            'feature': 'Non-slip grip'
        },
        'seo_title': 'Heavy-Duty Packaging Scissors | Professional Cutting Tools',
        'seo_description': 'Professional packaging scissors for e-commerce and shipping needs. Durable and comfortable.',
        'seo_keywords': ['scissors', 'packaging', 'cutting', 'tools', 'shipping'],
        'is_active': True,
        'featured': False,
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc)
    }
    await db.products.insert_one(product3)
    
    # Single variant for scissors
    variant = {
        'id': str(uuid.uuid4()),
        'product_id': product3_id,
        'sku': 'ACCESSORIES_SCISSORS_BLACK_8INCH',
        'attributes': {
            'width_cm': 8,  # Length converted to width for consistency
            'height_cm': 3,
            'size_code': '8inch',
            'type': 'tool',
            'color': 'black'
        },
        'price_tiers': [
            {'min_quantity': 1, 'price': 12.90},
            {'min_quantity': 5, 'price': 11.90},
            {'min_quantity': 10, 'price': 10.90}
        ],
        'stock_qty': 50,
        'on_hand': 50,
        'allocated': 0,
        'safety_stock': 5,
        'low_stock_threshold': 10,
        'channel_buffers': {'website': 0},
        'cost_price': 6.50,
        'created_at': datetime.now(timezone.utc)
    }
    await db.variants.insert_one(variant)
    
    # Packaging Tape
    product4_id = str(uuid.uuid4())
    product4 = {
        'id': product4_id,
        'name': 'Clear Packaging Tape',
        'description': 'Premium clear packaging tape for sealing boxes and packages. Strong adhesive, crystal clear visibility.',
        'category': 'accessories',
        'images': [
            'https://images.unsplash.com/photo-1611532736671-d725d4e80c23?w=800'
        ],
        'specifications': {
            'material': 'Acrylic Adhesive',
            'width': '2 inches (48mm)',
            'length': '100 meters',
            'feature': 'Crystal clear, strong adhesive'
        },
        'seo_title': 'Clear Packaging Tape | Strong Adhesive Shipping Tape',
        'seo_description': 'Premium clear packaging tape for professional shipping and packaging needs.',
        'seo_keywords': ['tape', 'packaging', 'clear', 'adhesive', 'shipping'],
        'is_active': True,
        'featured': False,
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc)
    }
    await db.products.insert_one(product4)
    
    # Tape variants
    tape_variants = [
        {'width': 2, 'length': 50, 'price': 3.50},
        {'width': 2, 'length': 100, 'price': 6.90},
        {'width': 3, 'length': 100, 'price': 8.90}
    ]
    
    for tv in tape_variants:
        variant = {
            'id': str(uuid.uuid4()),
            'product_id': product4_id,
            'sku': f'ACCESSORIES_TAPE_CLEAR_{tv["width"]}INX{tv["length"]}M',
            'attributes': {
                'width_cm': tv['width'],
                'height_cm': 1,  # Roll height
                'size_code': f'{tv["width"]}inx{tv["length"]}m',
                'type': 'consumable',
                'color': 'clear'
            },
            'price_tiers': [
                {'min_quantity': 1, 'price': tv['price']},
                {'min_quantity': 6, 'price': round(tv['price'] * 0.95, 2)},
                {'min_quantity': 12, 'price': round(tv['price'] * 0.90, 2)}
            ],
            'stock_qty': 100,
            'on_hand': 100,
            'allocated': 0,
            'safety_stock': 10,
            'low_stock_threshold': 20,
            'channel_buffers': {'website': 0},
            'cost_price': round(tv['price'] * 0.5, 2),
            'created_at': datetime.now(timezone.utc)
        }
        await db.variants.insert_one(variant)
    
    print("✅ Created accessories: Scissors and Packaging Tape")

async def update_business_settings():
    """Ensure M Supplies branding is set"""
    await db.settings.delete_many({'type': 'business'})
    settings = {
        'id': str(uuid.uuid4()),
        'type': 'business',
        'business_name': 'M Supplies',
        'currency': 'SGD',
        'gst_percent': 9.0,
        'default_safety_stock': 10,
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc)
    }
    await db.settings.insert_one(settings)
    print("✅ Business settings updated: M Supplies")

async def main():
    print("🌱 Starting Phase 2 product seeding...")
    await clear_existing_data()
    await create_polymailer_products()
    await create_accessories()
    await update_business_settings()
    print("\n✅ Phase 2 seed data created successfully!")
    
    print("\n📝 Product Summary:")
    print("   • Normal Polymailers: 4 colors × 6 sizes = 24 variants")
    print("   • Bubble Wrap Polymailers: WHITE ONLY × 3 sizes = 3 variants")
    print("   • Scissors: 1 variant")
    print("   • Tape: 3 variants")
    print("   • Total: 31 variants across 4 products")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())