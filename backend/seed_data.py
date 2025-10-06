"""
Seed script to populate database with initial data
Run with: python seed_data.py
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from app.core.security import hash_password
import uuid

# Database connection
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.getenv('DB_NAME', 'polymailer_db')

async def seed_database():
    print("🌱 Starting database seed...")
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Clear existing data
    print("Clearing existing data...")
    await db.users.delete_many({})
    await db.products.delete_many({})
    await db.variants.delete_many({})
    await db.coupons.delete_many({})
    
    # Create admin user
    print("Creating admin user...")
    admin_user = {
        'id': str(uuid.uuid4()),
        'email': 'admin@polymailer.com',
        'password': hash_password('admin123'),
        'first_name': 'Admin',
        'last_name': 'User',
        'phone': '+6591234567',
        'role': 'owner',
        'is_active': True,
        'created_at': datetime.now(timezone.utc)
    }
    await db.users.insert_one(admin_user)
    print(f"✅ Admin user created: {admin_user['email']} / admin123")
    
    # Create test customer
    customer_user = {
        'id': str(uuid.uuid4()),
        'email': 'customer@example.com',
        'password': hash_password('customer123'),
        'first_name': 'John',
        'last_name': 'Doe',
        'phone': '+6598765432',
        'role': 'customer',
        'is_active': True,
        'created_at': datetime.now(timezone.utc)
    }
    await db.users.insert_one(customer_user)
    print(f"✅ Customer user created: {customer_user['email']} / customer123")
    
    # Create polymailer products
    print("\nCreating polymailer products...")
    
    # Product 1: Standard Polymailers
    product1_id = str(uuid.uuid4())
    product1 = {
        'id': product1_id,
        'name': 'Premium Polymailers',
        'description': 'High-quality, lightweight polymailers perfect for e-commerce shipping. Made from durable LDPE material with strong self-sealing adhesive.',
        'category': 'Polymailers',
        'images': [
            'https://images.unsplash.com/photo-1586864387634-1e3c3e1a8c6b?w=800',
            'https://images.unsplash.com/photo-1611734449269-f90d7b3e0b1e?w=800'
        ],
        'specifications': {
            'material': 'LDPE (Low-Density Polyethylene)',
            'feature': 'Self-sealing adhesive strip',
            'waterproof': 'Yes',
            'tear_resistant': 'Yes'
        },
        'seo_title': 'Premium Polymailers | Durable Shipping Bags',
        'seo_description': 'Buy premium polymailers for your e-commerce business. Waterproof, tear-resistant, and available in multiple sizes.',
        'is_active': True,
        'featured': True,
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc)
    }
    await db.products.insert_one(product1)
    
    # Variants for Product 1
    colors = ['Pastel Pink', 'Champagne Pink', 'Blue', 'Milk Tea']
    sizes = [
        {'dimension': '17 x 30', 'cm': '17cm x 30cm'},
        {'dimension': '25 x 35', 'cm': '25cm x 35cm'},
        {'dimension': '32 x 43', 'cm': '32cm x 43cm'},
        {'dimension': '45 x 60', 'cm': '45cm x 60cm'}
    ]
    pack_sizes = [50, 100]
    
    variant_count = 0
    for size in sizes:
        for color in colors:
            for pack_size in pack_sizes:
                # Calculate price (larger sizes and packs = better unit price)
                base_price = 0.15 if size['dimension'] == '17 x 30' else \
                            0.20 if size['dimension'] == '25 x 35' else \
                            0.28 if size['dimension'] == '32 x 43' else 0.40
                
                pack_price = base_price * pack_size
                if pack_size == 100:
                    pack_price = pack_price * 0.9  # 10% discount for 100-pack
                
                variant = {
                    'id': str(uuid.uuid4()),
                    'product_id': product1_id,
                    'sku': f'PM-{size["dimension"].replace(" x ", "X")}-{color[:3].upper()}-{pack_size}',
                    'attributes': {
                        'size': size['cm'],
                        'thickness': '60 micron',
                        'color': color
                    },
                    'price_tiers': [
                        {'min_quantity': 1, 'price': round(pack_price, 2)},
                        {'min_quantity': 5, 'price': round(pack_price * 0.95, 2)},  # 5% off for 5+ packs
                        {'min_quantity': 10, 'price': round(pack_price * 0.90, 2)}  # 10% off for 10+ packs
                    ],
                    'stock_qty': 150,
                    'cost_price': round(pack_price * 0.6, 2),
                    'created_at': datetime.now(timezone.utc)
                }
                await db.variants.insert_one(variant)
                variant_count += 1
    
    print(f"✅ Created product: {product1['name']} with {variant_count} variants")
    
    # Product 2: Heavy-Duty Polymailers
    product2_id = str(uuid.uuid4())
    product2 = {
        'id': product2_id,
        'name': 'Heavy-Duty Polymailers',
        'description': 'Extra-strong polymailers for heavier items. 100 micron thickness provides maximum protection for fragile and heavy products.',
        'category': 'Polymailers',
        'images': [
            'https://images.unsplash.com/photo-1611734449268-e3c9c2c5b4d6?w=800'
        ],
        'specifications': {
            'material': 'LDPE (Low-Density Polyethylene)',
            'thickness': '100 micron',
            'feature': 'Double-sealed bottom, self-sealing top',
            'waterproof': 'Yes',
            'tear_resistant': 'Extra Strong'
        },
        'seo_title': 'Heavy-Duty Polymailers | Extra Strong Shipping Bags',
        'seo_description': '100 micron heavy-duty polymailers for maximum protection. Perfect for electronics and fragile items.',
        'is_active': True,
        'featured': True,
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc)
    }
    await db.products.insert_one(product2)
    
    # Variants for Product 2 (Heavy-duty in select sizes)
    variant_count2 = 0
    heavy_sizes = [
        {'dimension': '25 x 35', 'cm': '25cm x 35cm'},
        {'dimension': '32 x 43', 'cm': '32cm x 43cm'},
        {'dimension': '45 x 60', 'cm': '45cm x 60cm'}
    ]
    
    for size in heavy_sizes:
        for pack_size in [50, 100]:
            base_price = 0.30 if size['dimension'] == '25 x 35' else \
                        0.42 if size['dimension'] == '32 x 43' else 0.60
            
            pack_price = base_price * pack_size
            if pack_size == 100:
                pack_price = pack_price * 0.9
            
            variant = {
                'id': str(uuid.uuid4()),
                'product_id': product2_id,
                'sku': f'HD-{size["dimension"].replace(" x ", "X")}-WHT-{pack_size}',
                'attributes': {
                    'size': size['cm'],
                    'thickness': '100 micron',
                    'color': 'White'
                },
                'price_tiers': [
                    {'min_quantity': 1, 'price': round(pack_price, 2)},
                    {'min_quantity': 5, 'price': round(pack_price * 0.95, 2)},
                    {'min_quantity': 10, 'price': round(pack_price * 0.90, 2)}
                ],
                'stock_qty': 100,
                'cost_price': round(pack_price * 0.6, 2),
                'created_at': datetime.now(timezone.utc)
            }
            await db.variants.insert_one(variant)
            variant_count2 += 1
    
    print(f"✅ Created product: {product2['name']} with {variant_count2} variants")
    
    # Create sample coupons
    print("\nCreating sample coupons...")
    
    coupon1 = {
        'id': str(uuid.uuid4()),
        'code': 'WELCOME10',
        'type': 'percent',
        'value': 10.0,
        'min_order_amount': 50.0,
        'max_uses': None,
        'used_count': 0,
        'valid_from': datetime.now(timezone.utc),
        'valid_to': datetime.now(timezone.utc) + timedelta(days=90),
        'is_active': True,
        'created_at': datetime.now(timezone.utc)
    }
    await db.coupons.insert_one(coupon1)
    print(f"✅ Created coupon: {coupon1['code']} - 10% off orders above $50")
    
    coupon2 = {
        'id': str(uuid.uuid4()),
        'code': 'BULK20',
        'type': 'percent',
        'value': 20.0,
        'min_order_amount': 200.0,
        'max_uses': 100,
        'used_count': 0,
        'valid_from': datetime.now(timezone.utc),
        'valid_to': datetime.now(timezone.utc) + timedelta(days=60),
        'is_active': True,
        'created_at': datetime.now(timezone.utc)
    }
    await db.coupons.insert_one(coupon2)
    print(f"✅ Created coupon: {coupon2['code']} - 20% off orders above $200")
    
    print("\n✅ Database seeded successfully!")
    print("\n📝 Login credentials:")
    print("   Admin: admin@polymailer.com / admin123")
    print("   Customer: customer@example.com / customer123")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(seed_database())
