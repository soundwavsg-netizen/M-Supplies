#!/usr/bin/env python3
"""
Fix the actual Baby Blue product in the system
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

async def fix_actual_baby_blue():
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
        
        # Get the actual Baby Blue product ID from the system
        print("\n📋 Finding actual Baby Blue product...")
        async with session.get(f"{API_BASE}/products") as resp:
            if resp.status == 200:
                products = await resp.json()
                baby_blue_product = None
                for product in products:
                    if "baby blue" in product.get('name', '').lower():
                        baby_blue_product = product
                        break
                
                if not baby_blue_product:
                    print("❌ No Baby Blue product found in active products")
                    return
                
                actual_baby_blue_id = baby_blue_product['id']
                print(f"✅ Found Baby Blue product: {baby_blue_product.get('name')} (ID: {actual_baby_blue_id})")
            else:
                print(f"❌ Failed to get products: {resp.status}")
                return
        
        # Get full product details
        print(f"\n🔍 Getting full Baby Blue product details...")
        async with session.get(f"{API_BASE}/products/{actual_baby_blue_id}") as resp:
            if resp.status == 200:
                product = await resp.json()
                print(f"✅ Product details retrieved")
                print(f"   Name: {product.get('name')}")
                print(f"   Active: {product.get('is_active')}")
                
                variants = product.get('variants', [])
                print(f"   Variants: {len(variants)}")
                
                # Check for pricing issues
                problematic_variants = []
                for i, variant in enumerate(variants):
                    price_tiers = variant.get('price_tiers', [])
                    pack_size = variant.get('attributes', {}).get('pack_size', 'Unknown')
                    
                    print(f"     Variant {i+1}: Pack size {pack_size}")
                    print(f"       Price tiers: {price_tiers}")
                    
                    # Check for 0 values
                    has_zero_prices = any(tier.get('price', 0) == 0.0 for tier in price_tiers)
                    if has_zero_prices:
                        problematic_variants.append(variant)
                        print(f"       ❌ Has 0 pricing values!")
                    else:
                        print(f"       ✅ Pricing looks OK")
                
                if problematic_variants:
                    print(f"\n🔧 Fixing {len(problematic_variants)} variants with pricing issues...")
                    
                    # Create updated variants
                    updated_variants = []
                    for variant in variants:
                        updated_variant = variant.copy()
                        pack_size = variant.get('attributes', {}).get('pack_size', 50)
                        
                        # Fix pricing based on pack size
                        if pack_size == 50:
                            # 50-pack: $7.99
                            updated_variant['price_tiers'] = [
                                {"min_quantity": 1, "price": 7.99},
                                {"min_quantity": 25, "price": 7.99},
                                {"min_quantity": 50, "price": 7.99}
                            ]
                            print(f"       Fixed 50-pack pricing to $7.99")
                        elif pack_size == 100:
                            # 100-pack: $14.99 for 100+, $7.99 base
                            updated_variant['price_tiers'] = [
                                {"min_quantity": 1, "price": 7.99},
                                {"min_quantity": 25, "price": 7.99},
                                {"min_quantity": 50, "price": 7.99},
                                {"min_quantity": 100, "price": 14.99}
                            ]
                            print(f"       Fixed 100-pack pricing: $7.99 base, $14.99 for 100+")
                        else:
                            # Fix any 0 values with $7.99
                            price_tiers = variant.get('price_tiers', [])
                            fixed_tiers = []
                            for tier in price_tiers:
                                if tier.get('price', 0) == 0.0:
                                    fixed_tier = tier.copy()
                                    fixed_tier['price'] = 7.99
                                    fixed_tiers.append(fixed_tier)
                                else:
                                    fixed_tiers.append(tier)
                            
                            updated_variant['price_tiers'] = fixed_tiers if fixed_tiers else [{"min_quantity": 1, "price": 7.99}]
                            print(f"       Fixed other pack size ({pack_size}) pricing")
                        
                        updated_variants.append(updated_variant)
                    
                    # Send update
                    update_payload = {"variants": updated_variants}
                    
                    async with session.put(f"{API_BASE}/admin/products/{actual_baby_blue_id}", 
                                         json=update_payload, headers=headers) as resp:
                        if resp.status == 200:
                            print(f"✅ Baby Blue pricing updated successfully!")
                            
                            # Verify the fix
                            updated_product = await resp.json()
                            updated_variants_response = updated_product.get('variants', [])
                            
                            print(f"\n✅ Verification:")
                            for i, variant in enumerate(updated_variants_response):
                                price_tiers = variant.get('price_tiers', [])
                                pack_size = variant.get('attributes', {}).get('pack_size', 'Unknown')
                                has_zero_prices = any(tier.get('price', 0) == 0.0 for tier in price_tiers)
                                
                                if not has_zero_prices:
                                    print(f"   Variant {i+1} (Pack {pack_size}): ✅ No more 0 values")
                                else:
                                    print(f"   Variant {i+1} (Pack {pack_size}): ❌ Still has 0 values")
                        else:
                            error_text = await resp.text()
                            print(f"❌ Failed to update pricing: {resp.status}")
                            print(f"   Error: {error_text}")
                else:
                    print(f"✅ No pricing issues found - Baby Blue pricing is already correct")
                
            else:
                error_text = await resp.text()
                print(f"❌ Failed to get product details: {resp.status}")
                print(f"   Error: {error_text}")
        
        # Final verification - check price range in listing
        print(f"\n🎯 Final verification - checking price range in product listing...")
        async with session.get(f"{API_BASE}/products") as resp:
            if resp.status == 200:
                products = await resp.json()
                for product in products:
                    if product.get('id') == actual_baby_blue_id:
                        price_range = product.get('price_range', {})
                        min_price = price_range.get('min', 0)
                        max_price = price_range.get('max', 0)
                        
                        print(f"✅ Baby Blue in product listing:")
                        print(f"   Price range: ${min_price} - ${max_price}")
                        
                        if min_price > 0:
                            print(f"   ✅ No more $0 price range issue!")
                        else:
                            print(f"   ❌ Still showing $0 in price range")
                        break
                else:
                    print(f"❌ Baby Blue not found in product listing")
            else:
                print(f"❌ Failed to check final product listing: {resp.status}")

if __name__ == "__main__":
    asyncio.run(fix_actual_baby_blue())