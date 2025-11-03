#!/usr/bin/env python3
"""
Debug Baby Blue Product Issue
"""

import asyncio
import aiohttp
import json
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://msupplies-store.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "email": "admin@polymailer.com",
    "password": "admin123"
}

# Baby Blue product ID
BABY_BLUE_PRODUCT_ID = "6084a6ff-1911-488b-9288-2bc95e50cafa"

async def debug_baby_blue():
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
        
        # Check all products in system
        print("\n📋 Checking all products in system...")
        async with session.get(f"{API_BASE}/products") as resp:
            if resp.status == 200:
                products = await resp.json()
                print(f"✅ Found {len(products)} products in system")
                for i, product in enumerate(products):
                    print(f"  {i+1}. {product.get('name')} (ID: {product.get('id')})")
                    if product.get('id') == BABY_BLUE_PRODUCT_ID:
                        print(f"      ⭐ This is the Baby Blue product!")
            else:
                print(f"❌ Failed to get products: {resp.status}")
        
        # Try to get Baby Blue product directly
        print(f"\n🔍 Checking Baby Blue product directly (ID: {BABY_BLUE_PRODUCT_ID})...")
        async with session.get(f"{API_BASE}/products/{BABY_BLUE_PRODUCT_ID}") as resp:
            if resp.status == 200:
                product = await resp.json()
                print(f"✅ Baby Blue product found: {product.get('name')}")
                print(f"   Active: {product.get('is_active', 'Unknown')}")
                print(f"   Category: {product.get('category', 'Unknown')}")
                print(f"   Type: {product.get('type', 'Unknown')}")
                print(f"   Color: {product.get('color', 'Unknown')}")
                
                variants = product.get('variants', [])
                print(f"   Variants: {len(variants)}")
                
                for i, variant in enumerate(variants):
                    print(f"     Variant {i+1}:")
                    print(f"       ID: {variant.get('id')}")
                    print(f"       SKU: {variant.get('sku')}")
                    print(f"       Price tiers: {variant.get('price_tiers', [])}")
                    print(f"       Stock: on_hand={variant.get('on_hand', 0)}, stock_qty={variant.get('stock_qty', 0)}")
                    print(f"       Attributes: {variant.get('attributes', {})}")
                
            else:
                error_text = await resp.text()
                print(f"❌ Failed to get Baby Blue product: {resp.status}")
                print(f"   Error: {error_text}")
        
        # Check admin products endpoint
        print(f"\n🔧 Checking admin products endpoint...")
        async with session.get(f"{API_BASE}/admin/products", headers=headers) as resp:
            print(f"Admin products endpoint status: {resp.status}")
            if resp.status == 404:
                print("Admin products endpoint not found - this is expected")
        
        # Check filter options to see available data
        print(f"\n🎯 Checking filter options...")
        async with session.get(f"{API_BASE}/products/filter-options") as resp:
            if resp.status == 200:
                options = await resp.json()
                print(f"✅ Filter options:")
                print(f"   Categories: {options.get('categories', [])}")
                print(f"   Colors: {options.get('colors', [])}")
                print(f"   Types: {options.get('types', [])}")
                print(f"   Price range: {options.get('price_range', {})}")
            else:
                print(f"❌ Failed to get filter options: {resp.status}")
        
        # Try filtered products
        print(f"\n🔍 Trying filtered products...")
        filter_request = {"page": 1, "limit": 50}
        async with session.post(f"{API_BASE}/products/filter", json=filter_request) as resp:
            if resp.status == 200:
                data = await resp.json()
                products = data.get('products', [])
                print(f"✅ Filtered products found: {len(products)}")
                
                for product in products:
                    if product.get('id') == BABY_BLUE_PRODUCT_ID:
                        print(f"⭐ Baby Blue found in filtered results!")
                        print(f"   Price range: {product.get('price_range', {})}")
                        break
                else:
                    print(f"❌ Baby Blue not found in filtered results")
            else:
                print(f"❌ Failed to get filtered products: {resp.status}")

if __name__ == "__main__":
    asyncio.run(debug_baby_blue())