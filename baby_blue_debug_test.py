#!/usr/bin/env python3
"""
Baby Blue Product Variant Pricing Debug Test
Specifically tests the reported issue where both variants show $14.99 in customer view
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, Any, List

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://msupplies-shop.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "email": "admin@polymailer.com",
    "password": "admin123"
}

class BabyBlueDebugTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
    
    async def authenticate(self):
        """Authenticate admin user"""
        print("\n🔐 Authenticating Admin...")
        
        try:
            async with self.session.post(f"{API_BASE}/auth/login", json=ADMIN_CREDENTIALS) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.admin_token = data.get('access_token')
                    self.log_test("Admin Authentication", True, f"Token received")
                else:
                    error_text = await resp.text()
                    self.log_test("Admin Authentication", False, f"Status {resp.status}: {error_text}")
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
    
    async def find_baby_blue_product(self):
        """Find Baby Blue product in database by name"""
        print("\n🔍 Step 1: Finding Baby Blue Product in Database...")
        
        try:
            async with self.session.post(f"{API_BASE}/products/filter", json={"page": 1, "limit": 100}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    products = data.get('products', [])
                    
                    # Look for Baby Blue product
                    baby_blue_product = None
                    for product in products:
                        product_name = product.get('name', '').lower()
                        if 'baby blue' in product_name or ('baby' in product_name and 'blue' in product_name):
                            baby_blue_product = product
                            break
                    
                    if baby_blue_product:
                        self.log_test("Find Baby Blue Product", True, f"Found: {baby_blue_product.get('name')}")
                        return baby_blue_product
                    else:
                        # List all products to see what's available
                        product_names = [p.get('name', 'Unknown') for p in products]
                        self.log_test("Find Baby Blue Product", False, f"Not found. Available products: {product_names}")
                        return None
                else:
                    error_text = await resp.text()
                    self.log_test("Find Baby Blue Product", False, f"Status {resp.status}: {error_text}")
                    return None
        except Exception as e:
            self.log_test("Find Baby Blue Product", False, f"Exception: {str(e)}")
            return None
    
    async def extract_variant_data(self, product_id: str):
        """Extract both variants (25x35 - 50 pcs/pack and 25x35 - 100 pcs/pack) and show actual price_tiers"""
        print("\n📊 Step 2: Extracting Raw Variant Data...")
        
        try:
            async with self.session.get(f"{API_BASE}/products/{product_id}") as resp:
                if resp.status == 200:
                    product = await resp.json()
                    variants = product.get('variants', [])
                    
                    self.log_test("Get Product Details", True, f"Product has {len(variants)} variants")
                    
                    # Find the specific variants mentioned in the issue
                    variant_50_pack = None
                    variant_100_pack = None
                    
                    for variant in variants:
                        attrs = variant.get('attributes', {})
                        size_code = attrs.get('size_code', '')
                        pack_size = attrs.get('pack_size', 0)
                        
                        if size_code == '25x35':
                            if pack_size == 50:
                                variant_50_pack = variant
                            elif pack_size == 100:
                                variant_100_pack = variant
                    
                    # Log raw variant data
                    if variant_50_pack:
                        print("\n🔍 RAW DATA - 25x35 - 50 pcs/pack variant:")
                        print(f"    Variant ID: {variant_50_pack.get('id')}")
                        print(f"    SKU: {variant_50_pack.get('sku')}")
                        print(f"    Price Tiers: {json.dumps(variant_50_pack.get('price_tiers', []), indent=6)}")
                        print(f"    Stock (on_hand): {variant_50_pack.get('on_hand', 0)}")
                        print(f"    Stock (stock_qty): {variant_50_pack.get('stock_qty', 0)}")
                        self.log_test("Extract 50-pack Variant", True, f"Price tiers: {variant_50_pack.get('price_tiers', [])}")
                    else:
                        self.log_test("Extract 50-pack Variant", False, "25x35 - 50 pcs/pack variant not found")
                    
                    if variant_100_pack:
                        print("\n🔍 RAW DATA - 25x35 - 100 pcs/pack variant:")
                        print(f"    Variant ID: {variant_100_pack.get('id')}")
                        print(f"    SKU: {variant_100_pack.get('sku')}")
                        print(f"    Price Tiers: {json.dumps(variant_100_pack.get('price_tiers', []), indent=6)}")
                        print(f"    Stock (on_hand): {variant_100_pack.get('on_hand', 0)}")
                        print(f"    Stock (stock_qty): {variant_100_pack.get('stock_qty', 0)}")
                        self.log_test("Extract 100-pack Variant", True, f"Price tiers: {variant_100_pack.get('price_tiers', [])}")
                    else:
                        self.log_test("Extract 100-pack Variant", False, "25x35 - 100 pcs/pack variant not found")
                    
                    return variant_50_pack, variant_100_pack, variants
                    
                else:
                    error_text = await resp.text()
                    self.log_test("Get Product Details", False, f"Status {resp.status}: {error_text}")
                    return None, None, []
                    
        except Exception as e:
            self.log_test("Get Product Details", False, f"Exception: {str(e)}")
            return None, None, []
    
    async def compare_price_tiers(self, variant_50, variant_100):
        """Compare the price_tiers arrays between variants"""
        print("\n⚖️ Step 3: Comparing Price Tier Structures...")
        
        if not variant_50 or not variant_100:
            self.log_test("Price Tier Comparison", False, "Missing variant data for comparison")
            return
        
        price_tiers_50 = variant_50.get('price_tiers', [])
        price_tiers_100 = variant_100.get('price_tiers', [])
        
        # Check if both variants have identical price_tiers arrays
        if price_tiers_50 == price_tiers_100:
            self.log_test("Price Tiers Identical", False, "CRITICAL: Both variants have identical price_tiers arrays")
            print(f"    Both variants share: {json.dumps(price_tiers_50, indent=6)}")
        else:
            self.log_test("Price Tiers Identical", True, "Variants have different price_tiers arrays")
        
        # Extract actual prices
        price_50 = None
        price_100 = None
        
        if price_tiers_50 and len(price_tiers_50) > 0:
            price_50 = price_tiers_50[0].get('price', 0)
        
        if price_tiers_100 and len(price_tiers_100) > 0:
            price_100 = price_tiers_100[0].get('price', 0)
        
        print(f"\n💰 PRICE COMPARISON:")
        print(f"    50-pack variant price: ${price_50}")
        print(f"    100-pack variant price: ${price_100}")
        
        # Check if prices match expected values ($7.99 vs $14.99)
        if price_50 == 7.99:
            self.log_test("50-pack Price Correct", True, f"${price_50} matches expected $7.99")
        else:
            self.log_test("50-pack Price Correct", False, f"Expected $7.99, found ${price_50}")
        
        if price_100 == 14.99:
            self.log_test("100-pack Price Correct", True, f"${price_100} matches expected $14.99")
        else:
            self.log_test("100-pack Price Correct", False, f"Expected $14.99, found ${price_100}")
        
        # Check if both show $14.99 (the reported issue)
        if price_50 == 14.99 and price_100 == 14.99:
            self.log_test("Both Show $14.99", False, "CONFIRMED ISSUE: Both variants show $14.99")
        else:
            self.log_test("Both Show $14.99", True, "Variants show different prices")
        
        return price_50, price_100
    
    async def test_customer_api_response(self, product_id: str):
        """Test GET /api/products/{baby_blue_id} response for customer"""
        print("\n🛒 Step 4: Testing Customer API Response...")
        
        try:
            # Test without authentication (customer access)
            async with self.session.get(f"{API_BASE}/products/{product_id}") as resp:
                if resp.status == 200:
                    customer_product = await resp.json()
                    self.log_test("Customer API Access", True, f"Customer can access product")
                    
                    variants = customer_product.get('variants', [])
                    
                    # Find the specific variants and check what prices are served to customer
                    customer_prices = {}
                    for variant in variants:
                        attrs = variant.get('attributes', {})
                        size_code = attrs.get('size_code', '')
                        pack_size = attrs.get('pack_size', 0)
                        
                        if size_code == '25x35':
                            price_tiers = variant.get('price_tiers', [])
                            if price_tiers:
                                price = price_tiers[0].get('price', 0)
                                customer_prices[f"{pack_size}-pack"] = price
                    
                    print(f"\n🛒 CUSTOMER VIEW PRICES:")
                    for pack_type, price in customer_prices.items():
                        print(f"    {pack_type}: ${price}")
                    
                    # Check if customer sees both variants as $14.99
                    if len(customer_prices) >= 2:
                        prices = list(customer_prices.values())
                        if all(price == 14.99 for price in prices):
                            self.log_test("Customer Sees Both $14.99", False, "CONFIRMED: Customer sees both variants as $14.99")
                        else:
                            self.log_test("Customer Sees Both $14.99", True, f"Customer sees different prices: {customer_prices}")
                    
                    return customer_prices
                    
                else:
                    error_text = await resp.text()
                    self.log_test("Customer API Access", False, f"Status {resp.status}: {error_text}")
                    return {}
                    
        except Exception as e:
            self.log_test("Customer API Access", False, f"Exception: {str(e)}")
            return {}
    
    async def check_admin_update_impact(self, product_id: str):
        """Check if recent admin price updates affected both variants"""
        print("\n🔧 Step 5: Checking Admin Update Impact...")
        
        if not self.admin_token:
            self.log_test("Admin Update Check", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Get product with admin access to see if there are differences
            async with self.session.get(f"{API_BASE}/products/{product_id}", headers=headers) as resp:
                if resp.status == 200:
                    admin_product = await resp.json()
                    variants = admin_product.get('variants', [])
                    
                    self.log_test("Admin Product Access", True, "Admin can access product")
                    
                    # Check if admin sees different data than customer
                    admin_prices = {}
                    for variant in variants:
                        attrs = variant.get('attributes', {})
                        size_code = attrs.get('size_code', '')
                        pack_size = attrs.get('pack_size', 0)
                        
                        if size_code == '25x35':
                            price_tiers = variant.get('price_tiers', [])
                            if price_tiers:
                                price = price_tiers[0].get('price', 0)
                                admin_prices[f"{pack_size}-pack"] = price
                    
                    print(f"\n🔧 ADMIN VIEW PRICES:")
                    for pack_type, price in admin_prices.items():
                        print(f"    {pack_type}: ${price}")
                    
                    return admin_prices
                    
                else:
                    error_text = await resp.text()
                    self.log_test("Admin Product Access", False, f"Status {resp.status}: {error_text}")
                    return {}
                    
        except Exception as e:
            self.log_test("Admin Product Access", False, f"Exception: {str(e)}")
            return {}
    
    async def test_price_update_logic(self, product_id: str, variant_50, variant_100):
        """Test if price update logic is working correctly per variant"""
        print("\n🧪 Step 6: Testing Price Update Logic...")
        
        if not self.admin_token or not variant_50 or not variant_100:
            self.log_test("Price Update Logic Test", False, "Missing admin token or variant data")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Create a test update that changes only one variant's price
        test_variants = []
        
        # Get all current variants
        try:
            async with self.session.get(f"{API_BASE}/products/{product_id}") as resp:
                if resp.status == 200:
                    product = await resp.json()
                    current_variants = product.get('variants', [])
                    
                    # Modify only the 50-pack variant price to test if update affects both
                    for variant in current_variants:
                        updated_variant = variant.copy()
                        attrs = variant.get('attributes', {})
                        
                        if attrs.get('size_code') == '25x35' and attrs.get('pack_size') == 50:
                            # Change 50-pack price to $9.99 to test selective update
                            updated_variant['price_tiers'] = [{"min_quantity": 1, "price": 9.99}]
                            print(f"    Testing: Updating 50-pack price to $9.99")
                        
                        test_variants.append(updated_variant)
                    
                    # Send update
                    update_payload = {"variants": test_variants}
                    
                    async with self.session.put(f"{API_BASE}/admin/products/{product_id}", 
                                              json=update_payload, headers=headers) as update_resp:
                        if update_resp.status == 200:
                            self.log_test("Test Price Update Request", True, "Update request successful")
                            
                            # Check if only the intended variant was updated
                            updated_product = await update_resp.json()
                            updated_variants = updated_product.get('variants', [])
                            
                            prices_after_update = {}
                            for variant in updated_variants:
                                attrs = variant.get('attributes', {})
                                size_code = attrs.get('size_code', '')
                                pack_size = attrs.get('pack_size', 0)
                                
                                if size_code == '25x35':
                                    price_tiers = variant.get('price_tiers', [])
                                    if price_tiers:
                                        price = price_tiers[0].get('price', 0)
                                        prices_after_update[f"{pack_size}-pack"] = price
                            
                            print(f"\n🧪 PRICES AFTER TEST UPDATE:")
                            for pack_type, price in prices_after_update.items():
                                print(f"    {pack_type}: ${price}")
                            
                            # Check if update was selective
                            if prices_after_update.get("50-pack") == 9.99:
                                self.log_test("Selective Price Update - 50-pack", True, "50-pack price updated correctly")
                            else:
                                self.log_test("Selective Price Update - 50-pack", False, f"50-pack price not updated: ${prices_after_update.get('50-pack')}")
                            
                            # Check if 100-pack price remained unchanged
                            original_100_price = variant_100.get('price_tiers', [{}])[0].get('price', 0)
                            if prices_after_update.get("100-pack") == original_100_price:
                                self.log_test("Selective Price Update - 100-pack Unchanged", True, "100-pack price remained unchanged")
                            else:
                                self.log_test("Selective Price Update - 100-pack Unchanged", False, 
                                            f"100-pack price changed unexpectedly: ${prices_after_update.get('100-pack')}")
                            
                        else:
                            error_text = await update_resp.text()
                            self.log_test("Test Price Update Request", False, f"Status {update_resp.status}: {error_text}")
                            
                else:
                    error_text = await resp.text()
                    self.log_test("Get Current Variants", False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Price Update Logic Test", False, f"Exception: {str(e)}")
    
    async def run_debug_test(self):
        """Run the complete Baby Blue product debug test"""
        print("🔍 BABY BLUE PRODUCT VARIANT PRICING DEBUG TEST")
        print("=" * 60)
        
        # Authenticate
        await self.authenticate()
        
        # Step 1: Find Baby Blue product
        baby_blue_product = await self.find_baby_blue_product()
        if not baby_blue_product:
            print("\n❌ Cannot continue without Baby Blue product")
            return
        
        product_id = baby_blue_product['id']
        
        # Step 2: Extract variant data
        variant_50, variant_100, all_variants = await self.extract_variant_data(product_id)
        
        # Step 3: Compare price tiers
        if variant_50 and variant_100:
            price_50, price_100 = await self.compare_price_tiers(variant_50, variant_100)
        
        # Step 4: Test customer API response
        customer_prices = await self.test_customer_api_response(product_id)
        
        # Step 5: Check admin update impact
        admin_prices = await self.check_admin_update_impact(product_id)
        
        # Step 6: Test price update logic
        if variant_50 and variant_100:
            await self.test_price_update_logic(product_id, variant_50, variant_100)
        
        # Summary
        print("\n" + "=" * 60)
        print("🔍 DEBUG SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        
        print(f"Tests passed: {passed_tests}/{total_tests}")
        
        # Key findings
        print("\n🔍 KEY FINDINGS:")
        
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            for test in failed_tests:
                print(f"❌ {test['test']}: {test['details']}")
        else:
            print("✅ All tests passed - no issues found")

async def main():
    async with BabyBlueDebugTester() as tester:
        await tester.run_debug_test()

if __name__ == "__main__":
    asyncio.run(main())