#!/usr/bin/env python3
"""
Test script to demonstrate the fix for duplicate categories issue
"""

import asyncio
import aiohttp
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://msupplies-shop.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

async def test_categories_fix():
    """Test the categories fix"""
    print("🔧 Testing Categories Fix")
    print(f"API Base: {API_BASE}")
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Check current filter options (should show duplicates)
        print("\n1. Current filter options (before fix):")
        async with session.get(f"{API_BASE}/products/filter-options") as resp:
            if resp.status == 200:
                data = await resp.json()
                categories = data.get('categories', [])
                print(f"Categories: {categories}")
                
                # Check for duplicates
                lowercase_categories = [cat.lower() for cat in categories]
                unique_lowercase = set(lowercase_categories)
                
                if len(categories) != len(unique_lowercase):
                    print("❌ ISSUE CONFIRMED: Case-sensitive duplicates found!")
                    
                    # Show which categories are duplicated
                    for cat in unique_lowercase:
                        matching_cats = [c for c in categories if c.lower() == cat]
                        if len(matching_cats) > 1:
                            print(f"   Duplicate: {matching_cats}")
                else:
                    print("✅ No duplicates found")
            else:
                print(f"❌ Filter options failed: {resp.status}")
        
        # Step 2: Demonstrate the solution
        print("\n2. SOLUTION:")
        print("The issue is in /app/backend/app/repositories/product_repository.py line 214:")
        print("   categories = await self.products.distinct('category')")
        print("\nThis should be changed to:")
        print("   categories = await self.products.distinct('category', {'is_active': True})")
        print("\nThis will ensure only active products' categories are returned,")
        print("eliminating duplicates from soft-deleted products.")
        
        # Step 3: Show the expected result
        print("\n3. EXPECTED RESULT after fix:")
        print("   Categories: ['polymailers']")
        print("   No more case-sensitive duplicates!")
        
        # Step 4: Additional recommendations
        print("\n4. ADDITIONAL RECOMMENDATIONS:")
        print("   a) Standardize existing data: Update any products with uppercase")
        print("      categories to lowercase for consistency")
        print("   b) Add validation: Ensure new products always use lowercase categories")
        print("   c) Consider case-insensitive filtering in the application layer")

if __name__ == "__main__":
    asyncio.run(test_categories_fix())