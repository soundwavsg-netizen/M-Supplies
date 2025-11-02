#!/usr/bin/env python3
"""
Test the complete promotion workflow: Create coupon → Load all promotion data
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

async def test_complete_workflow():
    """Test the complete workflow that was failing"""
    print("🎯 Testing Complete Promotion Workflow")
    print("Simulating: Create coupon → fetchAllData() → Load promotion data")
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Authenticate
        print("\n1️⃣ Authenticating...")
        async with session.post(f"{API_BASE}/auth/login", json=ADMIN_CREDENTIALS) as resp:
            if resp.status == 200:
                data = await resp.json()
                admin_token = data.get('access_token')
                print(f"✅ Authenticated successfully")
            else:
                print(f"❌ Authentication failed: {resp.status}")
                return False
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Step 2: Create a coupon (this was working)
        print("\n2️⃣ Creating a coupon...")
        coupon_payload = {
            "code": "WORKFLOW10",
            "type": "percent",
            "value": 10,
            "valid_from": "2025-01-07T12:00:00.000Z",
            "valid_to": "2025-12-31T23:59:59.000Z",
            "is_active": True
        }
        
        async with session.post(f"{API_BASE}/admin/coupons", json=coupon_payload, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"✅ Coupon created: {data.get('code')}")
            else:
                error_text = await resp.text()
                print(f"❌ Coupon creation failed: {resp.status} - {error_text}")
                return False
        
        # Step 3: Simulate fetchAllData() - Load all promotion data
        print("\n3️⃣ Loading all promotion data (fetchAllData simulation)...")
        
        # Test each API endpoint that fetchAllData() calls
        endpoints_to_test = [
            ("/admin/coupons", "Coupons"),
            ("/admin/gift-items", "Gift Items"),
            ("/admin/gift-tiers", "Gift Tiers"),
            ("/admin/promotions/stats", "Promotion Stats")
        ]
        
        all_success = True
        for endpoint, name in endpoints_to_test:
            try:
                async with session.get(f"{API_BASE}{endpoint}", headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if endpoint == "/admin/coupons":
                            # Verify our newly created coupon is in the list
                            coupon_found = any(c.get('code') == 'WORKFLOW10' for c in data)
                            if coupon_found:
                                print(f"✅ {name}: Loaded successfully, newly created coupon found")
                            else:
                                print(f"⚠️ {name}: Loaded but newly created coupon not found")
                        elif endpoint == "/admin/promotions/stats":
                            print(f"✅ {name}: Loaded successfully (this was the failing endpoint)")
                        else:
                            print(f"✅ {name}: Loaded successfully ({len(data)} items)")
                    else:
                        error_text = await resp.text()
                        print(f"❌ {name}: Failed with {resp.status} - {error_text}")
                        all_success = False
            except Exception as e:
                print(f"❌ {name}: Exception - {str(e)}")
                all_success = False
        
        if all_success:
            print("\n🎉 SUCCESS: Complete workflow working!")
            print("✅ Coupon creation works")
            print("✅ All fetchAllData() endpoints work")
            print("✅ No more 'failed to load promotions data' error")
            return True
        else:
            print("\n❌ FAILURE: Some endpoints still failing")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_complete_workflow())
    print(f"\n{'🎉 WORKFLOW TEST PASSED' if success else '❌ WORKFLOW TEST FAILED'}")
    exit(0 if success else 1)