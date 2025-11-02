#!/usr/bin/env python3
"""
Add 100-pack variant to Baby Blue product as specified in the review request
"""

import asyncio
import aiohttp
import json
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://smart-retail-ai-6.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "email": "admin@polymailer.com",
    "password": "admin123"
}

async def add_100_pack_variant():
    async with aiohttp.ClientSession() as session:
        # Authenticate
        print("🔐 Authenticating...")
        async with session.post(f"{API_BASE}/auth/login", json=ADMIN_CREDENTIALS) as resp:
            if resp.status == 200:
                data = await resp.json()
                admin_token = data.get('access_token')
                print(f"✅ Admin authenticated")
            else:
                print(f"❌ Auth failed: {resp.status}")
                return
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get the Baby Blue product
        print("\n📋 Finding Baby Blue product...")
        async with session.get(f"{API_BASE}/products") as resp:
            if resp.status == 200:
                products = await resp.json()
                baby_blue_product = None
                for product in products:
                    if "baby blue" in product.get('name', '').lower():
                        baby_blue_product = product
                        break
                
                if not baby_blue_product:
                    print("❌ No Baby Blue product found")
                    return
                
                actual_baby_blue_id = baby_blue_product['id']
                print(f"✅ Found Baby Blue product: {baby_blue_product.get('name')} (ID: {actual_baby_blue_id})")
            else:
                print(f"❌ Failed to get products: {resp.status}")
                return
        
        # Get full product details
        print(f"\n🔍 Getting current Baby Blue variants...")
        async with session.get(f"{API_BASE}/products/{actual_baby_blue_id}") as resp:
            if resp.status == 200:
                product = await resp.json()
                variants = product.get('variants', [])
                print(f"✅ Current variants: {len(variants)}")
                
                # Check if 100-pack variant already exists
                has_100_pack = False
                for variant in variants:
                    pack_size = variant.get('attributes', {}).get('pack_size', 0)
                    if pack_size == 100:
                        has_100_pack = True
                        print(f"   ✅ 100-pack variant already exists")
                        break
                
                if not has_100_pack:
                    print(f"   📦 Adding 100-pack variant as specified in review request...")
                    
                    # Create new 100-pack variant
                    new_100_pack_variant = {
                        "sku": "POLYMAILERS_PREMIUM_BABY_BLUE_25x35_100",
                        "attributes": {
                            "width_cm": 25,
                            "height_cm": 35,
                            "size_code": "25x35",
                            "type": "normal",
                            "color": "baby blue",
                            "pack_size": 100
                        },
                        "price_tiers": [
                            {"min_quantity": 1, "price": 7.99},    # Base price
                            {"min_quantity": 25, "price": 7.99},   # Same base price
                            {"min_quantity": 50, "price": 7.99},   # Same base price  
                            {"min_quantity": 100, "price": 14.99}  # 100-pack pricing as specified
                        ],
                        "stock_qty": 25,
                        "on_hand": 25,
                        "allocated": 0,
                        "safety_stock": 0,
                        "low_stock_threshold": 10
                    }
                    
                    # Add new variant to existing variants
                    updated_variants = variants + [new_100_pack_variant]
                    
                    # Send update
                    update_payload = {"variants": updated_variants}
                    
                    async with session.put(f"{API_BASE}/admin/products/{actual_baby_blue_id}", 
                                         json=update_payload, headers=headers) as resp:
                        if resp.status == 200:
                            print(f"✅ 100-pack variant added successfully!")
                            
                            # Verify the addition
                            updated_product = await resp.json()
                            updated_variants_response = updated_product.get('variants', [])
                            
                            print(f"\n✅ Verification - now has {len(updated_variants_response)} variants:")
                            for i, variant in enumerate(updated_variants_response):
                                pack_size = variant.get('attributes', {}).get('pack_size', 'Unknown')
                                price_tiers = variant.get('price_tiers', [])
                                base_price = price_tiers[0].get('price', 0) if price_tiers else 0
                                max_price = max(tier.get('price', 0) for tier in price_tiers) if price_tiers else 0
                                
                                print(f"   Variant {i+1}: {pack_size}-pack, Price: ${base_price} - ${max_price}")
                        else:
                            error_text = await resp.text()
                            print(f"❌ Failed to add 100-pack variant: {resp.status}")
                            print(f"   Error: {error_text}")
                else:
                    print(f"   ✅ 100-pack variant already exists, no need to add")
                
            else:
                error_text = await resp.text()
                print(f"❌ Failed to get product details: {resp.status}")
                print(f"   Error: {error_text}")
        
        # Final verification - check updated price range
        print(f"\n🎯 Final verification - checking updated price range...")
        async with session.get(f"{API_BASE}/products") as resp:
            if resp.status == 200:
                products = await resp.json()
                for product in products:
                    if product.get('id') == actual_baby_blue_id:
                        price_range = product.get('price_range', {})
                        min_price = price_range.get('min', 0)
                        max_price = price_range.get('max', 0)
                        
                        print(f"✅ Updated Baby Blue price range: ${min_price} - ${max_price}")
                        
                        # Should now show $7.99 - $14.99 as specified in review request
                        if min_price == 7.99 and max_price == 14.99:
                            print(f"   ✅ Perfect! Price range matches review request specification")
                        else:
                            print(f"   ⚠️  Price range differs from expected $7.99 - $14.99")
                        break
                else:
                    print(f"❌ Baby Blue not found in product listing")
            else:
                print(f"❌ Failed to check final product listing: {resp.status}")

if __name__ == "__main__":
    asyncio.run(add_100_pack_variant())