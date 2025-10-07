#!/usr/bin/env python3
"""
Debug script to investigate the duplicate categories issue
"""

import asyncio
import aiohttp
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://msupplies-shop.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials
ADMIN_CREDENTIALS = {
    "email": "admin@polymailer.com",
    "password": "admin123"
}

async def debug_categories():
    """Debug the duplicate categories issue"""
    print("🔍 Debugging Duplicate Categories Issue")
    print(f"API Base: {API_BASE}")
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Authenticate as admin
        print("\n1. Authenticating as admin...")
        async with session.post(f"{API_BASE}/auth/login", json=ADMIN_CREDENTIALS) as resp:
            if resp.status == 200:
                data = await resp.json()
                admin_token = data.get('access_token')
                print(f"✅ Admin authenticated")
            else:
                print(f"❌ Admin authentication failed: {resp.status}")
                return
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Step 2: Check filter options API
        print("\n2. Checking filter options API...")
        async with session.get(f"{API_BASE}/products/filter-options") as resp:
            if resp.status == 200:
                data = await resp.json()
                categories = data.get('categories', [])
                print(f"Filter options categories: {categories}")
                
                # Check for duplicates
                if len(categories) != len(set(cat.lower() for cat in categories)):
                    print("❌ CONFIRMED: Case-sensitive duplicates found!")
                else:
                    print("✅ No duplicates found")
            else:
                print(f"❌ Filter options failed: {resp.status}")
        
        # Step 3: Check all products (including inactive)
        print("\n3. Checking all products (including inactive)...")
        async with session.get(f"{API_BASE}/products?limit=100") as resp:
            if resp.status == 200:
                active_products = await resp.json()
                print(f"Active products: {len(active_products)}")
                
                for product in active_products:
                    category = product.get('category', 'Unknown')
                    name = product.get('name', 'Unknown')
                    is_active = product.get('is_active', True)
                    print(f"  - {name}: category='{category}', is_active={is_active}")
            else:
                print(f"❌ Products API failed: {resp.status}")
        
        # Step 4: Try to access MongoDB directly through a custom endpoint or check variants
        print("\n4. Checking variants collection for category data...")
        async with session.get(f"{API_BASE}/admin/inventory", headers=headers) as resp:
            if resp.status == 200:
                inventory = await resp.json()
                print(f"Inventory items: {len(inventory)}")
                
                # Check if variants have category information
                product_names = set()
                for item in inventory:
                    product_name = item.get('product_name', 'Unknown')
                    product_names.add(product_name)
                
                print(f"Unique product names in inventory: {list(product_names)}")
            else:
                print(f"❌ Inventory API failed: {resp.status}")
        
        # Step 5: Test the specific distinct query behavior
        print("\n5. Testing product filtering to understand category behavior...")
        
        # Test filtering by 'Polymailers' (uppercase)
        filter_request = {
            "filters": {"categories": ["Polymailers"]},
            "page": 1,
            "limit": 20
        }
        
        async with session.post(f"{API_BASE}/products/filter", json=filter_request) as resp:
            if resp.status == 200:
                data = await resp.json()
                products = data.get('products', [])
                print(f"Products with 'Polymailers' category: {len(products)}")
                
                for product in products:
                    print(f"  - {product.get('name')}: category='{product.get('category')}'")
            else:
                print(f"❌ Filter by 'Polymailers' failed: {resp.status}")
        
        # Test filtering by 'polymailers' (lowercase)
        filter_request = {
            "filters": {"categories": ["polymailers"]},
            "page": 1,
            "limit": 20
        }
        
        async with session.post(f"{API_BASE}/products/filter", json=filter_request) as resp:
            if resp.status == 200:
                data = await resp.json()
                products = data.get('products', [])
                print(f"Products with 'polymailers' category: {len(products)}")
                
                for product in products:
                    print(f"  - {product.get('name')}: category='{product.get('category')}'")
            else:
                print(f"❌ Filter by 'polymailers' failed: {resp.status}")
        
        # Step 6: Check if there are any soft-deleted products that might have uppercase categories
        print("\n6. Investigating potential data sources for uppercase 'Polymailers'...")
        
        # The issue might be in the MongoDB distinct query itself
        # Let's see if we can understand what's happening
        print("\n🔍 ANALYSIS:")
        print("- Only 1 active product exists with category 'polymailers' (lowercase)")
        print("- Filter options API returns both 'Polymailers' and 'polymailers'")
        print("- Filtering by 'Polymailers' returns 0 products")
        print("- Filtering by 'polymailers' returns 1 product")
        print("\nThis suggests the MongoDB distinct('category') query is finding")
        print("a document with 'Polymailers' category that is not visible in the")
        print("regular product listing (possibly soft-deleted or in a different state)")

if __name__ == "__main__":
    asyncio.run(debug_categories())