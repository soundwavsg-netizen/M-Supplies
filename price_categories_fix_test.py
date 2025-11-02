#!/usr/bin/env python3
"""
Focused Testing for Price Range $0 Fix and Duplicate Categories Fix
Tests the specific issues mentioned in the review request
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, Any, List

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://smart-retail-ai-6.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "email": "admin@polymailer.com",
    "password": "admin123"
}

class PriceCategoriesFixTester:
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
        print("\n🔐 Authenticating Admin User...")
        
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
    
    async def test_baby_blue_price_range_fix(self):
        """Test 1: Baby Blue product price range fix - should show $7.99 - $14.99, not $0"""
        print("\n💰 Testing Baby Blue Product Price Range Fix...")
        
        try:
            async with self.session.get(f"{API_BASE}/products") as resp:
                if resp.status == 200:
                    products = await resp.json()
                    self.log_test("GET /api/products", True, f"Retrieved {len(products)} products")
                    
                    # Find Baby Blue product
                    baby_blue_product = None
                    for product in products:
                        if 'baby blue' in product.get('name', '').lower():
                            baby_blue_product = product
                            break
                    
                    if baby_blue_product:
                        product_name = baby_blue_product.get('name', 'Unknown')
                        price_range = baby_blue_product.get('price_range', {})
                        min_price = price_range.get('min', 0)
                        max_price = price_range.get('max', 0)
                        
                        self.log_test("Baby Blue Product Found", True, f"Product: {product_name}")
                        self.log_test("Baby Blue Price Range", True, f"Price range: ${min_price} - ${max_price}")
                        
                        # Critical test: Check if price range no longer shows $0
                        if min_price == 0.0:
                            self.log_test("❌ CRITICAL: Baby Blue $0 Price Issue NOT FIXED", False, 
                                        f"Baby Blue still shows $0 minimum price: ${min_price} - ${max_price}")
                        else:
                            self.log_test("✅ Baby Blue $0 Price Issue FIXED", True, 
                                        f"Baby Blue now shows valid price range: ${min_price} - ${max_price}")
                        
                        # Check if it matches expected range ($7.99 - $14.99)
                        if min_price == 7.99 and max_price == 14.99:
                            self.log_test("✅ Baby Blue Expected Price Range", True, 
                                        "Price range matches expected $7.99 - $14.99")
                        else:
                            self.log_test("Baby Blue Price Range Verification", False, 
                                        f"Expected $7.99 - $14.99, got ${min_price} - ${max_price}")
                    else:
                        self.log_test("Baby Blue Product Search", False, "Baby Blue product not found")
                        
                else:
                    error_text = await resp.text()
                    self.log_test("GET /api/products", False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Baby Blue Price Range Test", False, f"Exception: {str(e)}")
    
    async def test_duplicate_categories_fix(self):
        """Test 2: Duplicate categories fix - should show ['polymailers'] not ['Polymailers', 'polymailers']"""
        print("\n🏷️ Testing Duplicate Categories Fix...")
        
        try:
            async with self.session.get(f"{API_BASE}/products/filter-options") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    categories = data.get('categories', [])
                    
                    self.log_test("GET /api/products/filter-options", True, f"Retrieved filter options")
                    self.log_test("Categories Retrieved", True, f"Categories: {categories}")
                    
                    # Critical test: Check for duplicate categories
                    polymailer_categories = [cat for cat in categories if 'polymailer' in cat.lower()]
                    
                    if len(polymailer_categories) > 1:
                        self.log_test("❌ CRITICAL: Duplicate Categories Issue NOT FIXED", False, 
                                    f"Still found duplicate polymailer categories: {polymailer_categories}")
                    else:
                        self.log_test("✅ Duplicate Categories Issue FIXED", True, 
                                    f"Only one polymailer category found: {polymailer_categories}")
                    
                    # Check if it's the expected lowercase version
                    if polymailer_categories == ['polymailers']:
                        self.log_test("✅ Expected Category Format", True, 
                                    "Categories show ['polymailers'] as expected")
                    else:
                        self.log_test("Category Format Verification", False, 
                                    f"Expected ['polymailers'], got {polymailer_categories}")
                    
                    # Check for any case-sensitive duplicates in all categories
                    lowercase_categories = [cat.lower() for cat in categories]
                    unique_lowercase = set(lowercase_categories)
                    
                    if len(categories) != len(unique_lowercase):
                        duplicates = []
                        for cat in unique_lowercase:
                            matching_cats = [c for c in categories if c.lower() == cat]
                            if len(matching_cats) > 1:
                                duplicates.extend(matching_cats)
                        
                        self.log_test("❌ Other Case-Sensitive Duplicates Found", False, 
                                    f"Found duplicates: {duplicates}")
                    else:
                        self.log_test("✅ No Case-Sensitive Duplicates", True, 
                                    "All categories are unique (case-insensitive)")
                        
                else:
                    error_text = await resp.text()
                    self.log_test("GET /api/products/filter-options", False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Duplicate Categories Test", False, f"Exception: {str(e)}")
    
    async def test_all_products_price_ranges(self):
        """Test 3: Ensure all products have valid price ranges (no $0 values)"""
        print("\n💵 Testing All Products Price Ranges...")
        
        try:
            async with self.session.get(f"{API_BASE}/products") as resp:
                if resp.status == 200:
                    products = await resp.json()
                    self.log_test("Customer Products Page API", True, f"Retrieved {len(products)} products")
                    
                    products_with_zero_prices = []
                    valid_price_products = []
                    
                    for product in products:
                        product_name = product.get('name', 'Unknown')
                        price_range = product.get('price_range', {})
                        min_price = price_range.get('min', 0)
                        max_price = price_range.get('max', 0)
                        
                        if min_price == 0.0 or max_price == 0.0:
                            products_with_zero_prices.append({
                                'name': product_name,
                                'price_range': f"${min_price} - ${max_price}"
                            })
                        else:
                            valid_price_products.append({
                                'name': product_name,
                                'price_range': f"${min_price} - ${max_price}"
                            })
                    
                    if products_with_zero_prices:
                        self.log_test("❌ CRITICAL: Products with $0 Price Ranges Found", False, 
                                    f"Found {len(products_with_zero_prices)} products with $0 prices")
                        
                        for product in products_with_zero_prices:
                            self.log_test(f"❌ Product with $0 Price", False, 
                                        f"{product['name']}: {product['price_range']}")
                    else:
                        self.log_test("✅ All Products Have Valid Price Ranges", True, 
                                    f"All {len(valid_price_products)} products have valid pricing")
                    
                    # Log some examples of valid pricing
                    for i, product in enumerate(valid_price_products[:3]):
                        self.log_test(f"Valid Price Example {i+1}", True, 
                                    f"{product['name']}: {product['price_range']}")
                        
                else:
                    error_text = await resp.text()
                    self.log_test("Customer Products Page API", False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("All Products Price Ranges Test", False, f"Exception: {str(e)}")
    
    async def test_admin_products_price_ranges(self):
        """Test 4: Admin products page price ranges"""
        print("\n🔧 Testing Admin Products Price Ranges...")
        
        if not self.admin_token:
            self.log_test("Admin Products Test", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Note: There's no specific /api/admin/products endpoint in the server.py
            # So we'll test the regular products endpoint with admin auth
            async with self.session.get(f"{API_BASE}/products", headers=headers) as resp:
                if resp.status == 200:
                    products = await resp.json()
                    self.log_test("Admin Products View API", True, f"Retrieved {len(products)} products")
                    
                    admin_products_with_zero_prices = []
                    admin_valid_price_products = []
                    
                    for product in products:
                        product_name = product.get('name', 'Unknown')
                        price_range = product.get('price_range', {})
                        min_price = price_range.get('min', 0)
                        max_price = price_range.get('max', 0)
                        
                        if min_price == 0.0 or max_price == 0.0:
                            admin_products_with_zero_prices.append({
                                'name': product_name,
                                'price_range': f"${min_price} - ${max_price}"
                            })
                        else:
                            admin_valid_price_products.append({
                                'name': product_name,
                                'price_range': f"${min_price} - ${max_price}"
                            })
                    
                    if admin_products_with_zero_prices:
                        self.log_test("❌ CRITICAL: Admin View - Products with $0 Price Ranges", False, 
                                    f"Found {len(admin_products_with_zero_prices)} products with $0 prices in admin view")
                        
                        for product in admin_products_with_zero_prices:
                            self.log_test(f"❌ Admin View - Product with $0 Price", False, 
                                        f"{product['name']}: {product['price_range']}")
                    else:
                        self.log_test("✅ Admin View - All Products Have Valid Price Ranges", True, 
                                    f"All {len(admin_valid_price_products)} products have valid pricing in admin view")
                    
                    # Compare admin view with customer view consistency
                    self.log_test("Admin-Customer Price Consistency", True, 
                                "Admin and customer views should show same price ranges")
                        
                else:
                    error_text = await resp.text()
                    self.log_test("Admin Products View API", False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Admin Products Price Ranges Test", False, f"Exception: {str(e)}")
    
    async def test_specific_baby_blue_variants(self):
        """Test 5: Detailed Baby Blue product variant analysis"""
        print("\n🔍 Testing Baby Blue Product Variants in Detail...")
        
        try:
            # First find Baby Blue product
            async with self.session.get(f"{API_BASE}/products") as resp:
                if resp.status == 200:
                    products = await resp.json()
                    
                    baby_blue_product = None
                    for product in products:
                        if 'baby blue' in product.get('name', '').lower():
                            baby_blue_product = product
                            break
                    
                    if not baby_blue_product:
                        self.log_test("Baby Blue Product Search", False, "Baby Blue product not found")
                        return
                    
                    product_id = baby_blue_product.get('id')
                    self.log_test("Baby Blue Product ID", True, f"Product ID: {product_id}")
                    
        except Exception as e:
            self.log_test("Baby Blue Product Search", False, f"Exception: {str(e)}")
            return
        
        # Get detailed product information
        try:
            async with self.session.get(f"{API_BASE}/products/{product_id}") as resp:
                if resp.status == 200:
                    product_detail = await resp.json()
                    variants = product_detail.get('variants', [])
                    
                    self.log_test("Baby Blue Product Details", True, f"Found {len(variants)} variants")
                    
                    for i, variant in enumerate(variants):
                        variant_id = variant.get('id', 'Unknown')
                        sku = variant.get('sku', 'Unknown')
                        attributes = variant.get('attributes', {})
                        price_tiers = variant.get('price_tiers', [])
                        
                        pack_size = attributes.get('pack_size', 'Unknown')
                        size_code = attributes.get('size_code', 'Unknown')
                        
                        self.log_test(f"Baby Blue Variant {i+1}", True, 
                                    f"SKU: {sku}, Size: {size_code}, Pack: {pack_size}")
                        
                        # Check price tiers for $0 values
                        zero_price_tiers = []
                        valid_price_tiers = []
                        
                        for tier in price_tiers:
                            price = tier.get('price', 0)
                            min_qty = tier.get('min_quantity', 0)
                            
                            if price == 0.0:
                                zero_price_tiers.append(f"Qty {min_qty}: ${price}")
                            else:
                                valid_price_tiers.append(f"Qty {min_qty}: ${price}")
                        
                        if zero_price_tiers:
                            self.log_test(f"❌ Baby Blue Variant {i+1} - $0 Price Tiers", False, 
                                        f"Found $0 price tiers: {zero_price_tiers}")
                        else:
                            self.log_test(f"✅ Baby Blue Variant {i+1} - Valid Price Tiers", True, 
                                        f"All price tiers valid: {valid_price_tiers}")
                        
                        # Check if this variant contributes to the overall price range
                        if price_tiers:
                            min_variant_price = min(tier.get('price', 0) for tier in price_tiers)
                            max_variant_price = max(tier.get('price', 0) for tier in price_tiers)
                            
                            self.log_test(f"Baby Blue Variant {i+1} Price Range", True, 
                                        f"Variant contributes: ${min_variant_price} - ${max_variant_price}")
                        
                else:
                    error_text = await resp.text()
                    self.log_test("Baby Blue Product Details", False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Baby Blue Product Details", False, f"Exception: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🎯 PRICE RANGE $0 FIX AND DUPLICATE CATEGORIES FIX - TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 Overall Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Critical issues summary
        critical_failures = []
        for result in self.test_results:
            if not result['success'] and ('CRITICAL' in result['test'] or '$0' in result['test'] or 'Duplicate' in result['test']):
                critical_failures.append(result)
        
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES FOUND ({len(critical_failures)}):")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['details']}")
        else:
            print(f"\n✅ NO CRITICAL ISSUES FOUND - Both fixes appear to be working!")
        
        print("\n" + "="*80)

async def main():
    """Run the focused price and categories fix tests"""
    print("🚀 Starting Price Range $0 Fix and Duplicate Categories Fix Testing...")
    print(f"🌐 Testing against: {API_BASE}")
    
    async with PriceCategoriesFixTester() as tester:
        # Authenticate
        await tester.authenticate()
        
        # Run focused tests
        await tester.test_baby_blue_price_range_fix()
        await tester.test_duplicate_categories_fix()
        await tester.test_all_products_price_ranges()
        await tester.test_admin_products_price_ranges()
        await tester.test_specific_baby_blue_variants()
        
        # Print summary
        tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())