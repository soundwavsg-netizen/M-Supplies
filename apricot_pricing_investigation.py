#!/usr/bin/env python3
"""
Apricot Product Pricing Investigation
Investigates the apricot color product showing "$0 to $17" price range instead of "$8.99 to $17"
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, Any, List

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://msupplies-store.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "email": "admin@polymailer.com",
    "password": "admin123"
}

class ApricotPricingInvestigator:
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
                    self.log_test("Admin Authentication", True, f"Token received: {self.admin_token[:20]}...")
                else:
                    error_text = await resp.text()
                    self.log_test("Admin Authentication", False, f"Status {resp.status}: {error_text}")
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
    
    async def find_apricot_product(self):
        """Find the apricot product by searching GET /api/products"""
        print("\n🔍 Step 1: Finding Apricot Product...")
        
        apricot_product = None
        
        try:
            # Search all products for apricot
            async with self.session.get(f"{API_BASE}/products?limit=100") as resp:
                if resp.status == 200:
                    products = await resp.json()
                    self.log_test("Get All Products", True, f"Retrieved {len(products)} products")
                    
                    # Search for apricot in product name or color
                    for product in products:
                        product_name = product.get('name', '').lower()
                        product_color = product.get('color', '').lower()
                        
                        # Check if apricot is in name or color
                        if 'apricot' in product_name or 'apricot' in product_color:
                            apricot_product = product
                            self.log_test("Found Apricot Product", True, 
                                        f"Product: {product.get('name')}, Color: {product.get('color')}")
                            break
                        
                        # Also check variants for apricot color
                        variants = product.get('variants', [])
                        for variant in variants:
                            variant_color = variant.get('attributes', {}).get('color', '').lower()
                            if 'apricot' in variant_color:
                                apricot_product = product
                                self.log_test("Found Apricot Product (in variants)", True, 
                                            f"Product: {product.get('name')}, Variant Color: {variant_color}")
                                break
                        
                        if apricot_product:
                            break
                    
                    if not apricot_product:
                        self.log_test("Find Apricot Product", False, "No product with 'apricot' found in name or color")
                        
                        # List all available colors for debugging
                        all_colors = set()
                        for product in products:
                            if product.get('color'):
                                all_colors.add(product.get('color'))
                            for variant in product.get('variants', []):
                                variant_color = variant.get('attributes', {}).get('color')
                                if variant_color:
                                    all_colors.add(variant_color)
                        
                        self.log_test("Available Colors", True, f"Found colors: {sorted(list(all_colors))}")
                        return None
                    
                else:
                    error_text = await resp.text()
                    self.log_test("Get All Products", False, f"Status {resp.status}: {error_text}")
                    return None
                    
        except Exception as e:
            self.log_test("Find Apricot Product", False, f"Exception: {str(e)}")
            return None
        
        return apricot_product
    
    async def examine_price_tiers_structure(self, product_id: str):
        """Get full product details and examine price_tiers structure"""
        print("\n🔍 Step 2: Examining Price Tiers Structure...")
        
        try:
            async with self.session.get(f"{API_BASE}/products/{product_id}") as resp:
                if resp.status == 200:
                    product = await resp.json()
                    self.log_test("Get Product Details", True, f"Retrieved product: {product.get('name')}")
                    
                    variants = product.get('variants', [])
                    self.log_test("Product Variants", True, f"Product has {len(variants)} variants")
                    
                    # Examine each variant's price_tiers
                    zero_value_found = False
                    all_prices = []
                    
                    for i, variant in enumerate(variants):
                        variant_id = variant.get('id')
                        sku = variant.get('sku', 'Unknown')
                        attributes = variant.get('attributes', {})
                        pack_size = attributes.get('pack_size', 'Unknown')
                        size_code = attributes.get('size_code', 'Unknown')
                        color = attributes.get('color', 'Unknown')
                        
                        self.log_test(f"Variant {i+1} Info", True, 
                                    f"SKU: {sku}, Size: {size_code}, Pack: {pack_size}, Color: {color}")
                        
                        price_tiers = variant.get('price_tiers', [])
                        if price_tiers:
                            self.log_test(f"Variant {i+1} Price Tiers", True, f"Has {len(price_tiers)} price tiers")
                            
                            for j, tier in enumerate(price_tiers):
                                min_qty = tier.get('min_quantity', 0)
                                price = tier.get('price', 0)
                                
                                self.log_test(f"Variant {i+1} Tier {j+1}", True, 
                                            f"Min Qty: {min_qty}, Price: ${price}")
                                
                                # Check for zero values
                                if price == 0 or price == 0.0:
                                    zero_value_found = True
                                    self.log_test(f"❌ ZERO PRICE FOUND", False, 
                                                f"Variant {i+1} Tier {j+1}: Min Qty {min_qty}, Price ${price}")
                                
                                all_prices.append(price)
                        else:
                            self.log_test(f"Variant {i+1} Price Tiers", False, "No price tiers found")
                    
                    # Analyze price range calculation
                    if all_prices:
                        min_price = min(all_prices)
                        max_price = max(all_prices)
                        non_zero_prices = [p for p in all_prices if p > 0]
                        
                        if non_zero_prices:
                            min_non_zero = min(non_zero_prices)
                            max_non_zero = max(non_zero_prices)
                            
                            self.log_test("Price Range Analysis", True, 
                                        f"All prices: ${min_price} - ${max_price}")
                            self.log_test("Non-Zero Price Range", True, 
                                        f"Non-zero prices: ${min_non_zero} - ${max_non_zero}")
                            
                            if min_price == 0 and min_non_zero > 0:
                                self.log_test("❌ PRICE RANGE ISSUE CONFIRMED", False, 
                                            f"Price range shows ${min_price} - ${max_price} instead of ${min_non_zero} - ${max_non_zero}")
                        else:
                            self.log_test("Price Analysis", False, "All prices are zero")
                    
                    if zero_value_found:
                        self.log_test("❌ ZERO VALUES IDENTIFIED", False, 
                                    "Found price tiers with 0 values causing $0 to appear in price range")
                    else:
                        self.log_test("Zero Values Check", True, "No zero values found in price tiers")
                    
                    return product
                    
                else:
                    error_text = await resp.text()
                    self.log_test("Get Product Details", False, f"Status {resp.status}: {error_text}")
                    return None
                    
        except Exception as e:
            self.log_test("Examine Price Tiers", False, f"Exception: {str(e)}")
            return None
    
    async def check_price_range_calculation(self):
        """Check how the backend calculates min/max prices from price_tiers"""
        print("\n🔍 Step 3: Checking Price Range Calculation Logic...")
        
        try:
            # Get filter options to see system-wide price range
            async with self.session.get(f"{API_BASE}/products/filter-options") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    price_range = data.get('price_range', {})
                    
                    min_price = price_range.get('min', 0)
                    max_price = price_range.get('max', 0)
                    
                    self.log_test("System Price Range", True, f"System shows: ${min_price} - ${max_price}")
                    
                    if min_price == 0:
                        self.log_test("❌ SYSTEM PRICE RANGE ISSUE", False, 
                                    "System-wide price range starts at $0, indicating zero values in price_tiers")
                    else:
                        self.log_test("System Price Range Check", True, "System price range does not start at $0")
                    
                else:
                    error_text = await resp.text()
                    self.log_test("Get Filter Options", False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Check Price Range Calculation", False, f"Exception: {str(e)}")
        
        # Also check product listing to see how individual products show price ranges
        try:
            async with self.session.get(f"{API_BASE}/products") as resp:
                if resp.status == 200:
                    products = await resp.json()
                    
                    for product in products:
                        product_name = product.get('name', 'Unknown')
                        price_range = product.get('price_range', {})
                        
                        if price_range:
                            min_price = price_range.get('min', 0)
                            max_price = price_range.get('max', 0)
                            
                            if min_price == 0:
                                self.log_test(f"❌ PRODUCT PRICE RANGE ISSUE", False, 
                                            f"{product_name}: Shows ${min_price} - ${max_price}")
                            else:
                                self.log_test(f"Product Price Range OK", True, 
                                            f"{product_name}: ${min_price} - ${max_price}")
                    
                else:
                    error_text = await resp.text()
                    self.log_test("Check Product Listing Prices", False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Check Product Listing Prices", False, f"Exception: {str(e)}")
    
    async def investigate_50pcs_pricing(self, product):
        """Specifically investigate the 50pcs pricing that should be $8.99"""
        print("\n🔍 Step 4: Investigating 50pcs Pricing...")
        
        if not product:
            self.log_test("50pcs Investigation", False, "No product provided")
            return
        
        variants = product.get('variants', [])
        found_50pcs = False
        
        for variant in variants:
            attributes = variant.get('attributes', {})
            pack_size = attributes.get('pack_size')
            
            if pack_size == 50:
                found_50pcs = True
                sku = variant.get('sku', 'Unknown')
                price_tiers = variant.get('price_tiers', [])
                
                self.log_test("Found 50pcs Variant", True, f"SKU: {sku}")
                
                if price_tiers:
                    # Look for the price that should be $8.99
                    for tier in price_tiers:
                        min_qty = tier.get('min_quantity', 0)
                        price = tier.get('price', 0)
                        
                        if min_qty == 50 or (min_qty <= 50 and price > 0):
                            if price == 8.99:
                                self.log_test("50pcs Price Correct", True, f"Found $8.99 for 50pcs (Min Qty: {min_qty})")
                            elif price == 0:
                                self.log_test("❌ 50pcs Price Issue", False, 
                                            f"50pcs price is $0 instead of $8.99 (Min Qty: {min_qty})")
                            else:
                                self.log_test("50pcs Price Different", True, 
                                            f"50pcs price is ${price} (Min Qty: {min_qty})")
                else:
                    self.log_test("50pcs Price Tiers", False, "No price tiers found for 50pcs variant")
        
        if not found_50pcs:
            self.log_test("50pcs Variant Search", False, "No 50pcs variant found")
            
            # List all pack sizes for debugging
            pack_sizes = []
            for variant in variants:
                pack_size = variant.get('attributes', {}).get('pack_size')
                if pack_size:
                    pack_sizes.append(pack_size)
            
            self.log_test("Available Pack Sizes", True, f"Found pack sizes: {pack_sizes}")
    
    async def run_investigation(self):
        """Run the complete apricot pricing investigation"""
        print("🚀 Starting Apricot Product Pricing Investigation...")
        print("=" * 60)
        
        # Step 1: Authenticate
        await self.authenticate()
        
        if not self.admin_token:
            print("❌ Cannot proceed without admin authentication")
            return
        
        # Step 2: Find apricot product
        apricot_product = await self.find_apricot_product()
        
        if not apricot_product:
            print("❌ Cannot proceed without finding apricot product")
            return
        
        product_id = apricot_product.get('id')
        
        # Step 3: Examine price tiers structure
        detailed_product = await self.examine_price_tiers_structure(product_id)
        
        # Step 4: Check price range calculation logic
        await self.check_price_range_calculation()
        
        # Step 5: Investigate 50pcs pricing specifically
        await self.investigate_50pcs_pricing(detailed_product)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 INVESTIGATION SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        
        if failed_tests > 0:
            print("\n🚨 CRITICAL ISSUES FOUND:")
            for result in self.test_results:
                if not result['success'] and result['test'].startswith('❌'):
                    print(f"  • {result['test']}: {result['details']}")
        
        print("\n🔧 RECOMMENDED ACTIONS:")
        print("1. Remove all 0 values from price_tiers arrays")
        print("2. Ensure 50pcs variant has correct $8.99 pricing")
        print("3. Update price range calculation to exclude 0 values")
        print("4. Verify price_tiers structure for all variants")

async def main():
    async with ApricotPricingInvestigator() as investigator:
        await investigator.run_investigation()

if __name__ == "__main__":
    asyncio.run(main())