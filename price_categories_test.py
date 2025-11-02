#!/usr/bin/env python3
"""
Price Range and Duplicate Categories Investigation
Specific testing for the reported issues:
1. Price Range $0 Issue
2. Duplicate Categories Issue
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

class PriceCategoriesInvestigator:
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
                    self.log_test("Admin Authentication", True, f"Token received: {self.admin_token[:20]}...")
                else:
                    error_text = await resp.text()
                    self.log_test("Admin Authentication", False, f"Status {resp.status}: {error_text}")
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")

    async def investigate_price_range_issue(self):
        """Investigate Price Range $0 Issue"""
        print("\n💰 INVESTIGATING PRICE RANGE $0 ISSUE...")
        
        # Issue 1: Check GET /api/products for $0 price ranges
        print("\n📊 Checking Customer Products API for Price Range Issues...")
        try:
            async with self.session.get(f"{API_BASE}/products") as resp:
                if resp.status == 200:
                    products = await resp.json()
                    self.log_test("GET /api/products", True, f"Retrieved {len(products)} products")
                    
                    # Check each product's price range
                    zero_price_products = []
                    print(f"\n📋 Product Price Range Analysis:")
                    for product in products:
                        price_range = product.get('price_range', {})
                        min_price = price_range.get('min', 0)
                        max_price = price_range.get('max', 0)
                        product_name = product.get('name', 'Unknown')
                        
                        print(f"  Product: {product_name}")
                        print(f"    Price Range: ${min_price} - ${max_price}")
                        
                        if min_price == 0 or max_price == 0:
                            zero_price_products.append({
                                'name': product_name,
                                'id': product.get('id'),
                                'price_range': price_range
                            })
                            print(f"    ❌ ISSUE: Contains $0 in price range")
                        else:
                            print(f"    ✅ OK: Valid price range")
                        print()
                    
                    if zero_price_products:
                        self.log_test("Price Range $0 Issue Found", False, 
                                    f"Found {len(zero_price_products)} products with $0 in price range")
                        
                        print(f"\n❌ PRODUCTS WITH $0 PRICE RANGES:")
                        for product in zero_price_products:
                            print(f"  - {product['name']}: {product['price_range']}")
                    else:
                        self.log_test("Price Range $0 Issue", True, "No products showing $0 in price ranges")
                        
                else:
                    error_text = await resp.text()
                    self.log_test("GET /api/products", False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("GET /api/products", False, f"Exception: {str(e)}")

    async def investigate_baby_blue_variants(self):
        """Investigate Baby Blue Product Variants Price Tiers"""
        print("\n🔍 INVESTIGATING BABY BLUE PRODUCT VARIANTS PRICE TIERS...")
        
        try:
            # Find Baby Blue product
            baby_blue_product = None
            async with self.session.get(f"{API_BASE}/products") as resp:
                if resp.status == 200:
                    products = await resp.json()
                    for product in products:
                        if "Baby Blue" in product.get('name', ''):
                            baby_blue_product = product
                            break
                    
                    if baby_blue_product:
                        product_id = baby_blue_product['id']
                        self.log_test("Find Baby Blue Product", True, f"Found Baby Blue: {baby_blue_product.get('name')}")
                        
                        # Get full product details to examine price_tiers
                        async with self.session.get(f"{API_BASE}/products/{product_id}") as detail_resp:
                            if detail_resp.status == 200:
                                product_details = await detail_resp.json()
                                variants = product_details.get('variants', [])
                                
                                print(f"\n📊 BABY BLUE PRODUCT VARIANTS ANALYSIS:")
                                print(f"Product Name: {product_details.get('name')}")
                                print(f"Product ID: {product_id}")
                                print(f"Number of Variants: {len(variants)}")
                                print("="*60)
                                
                                zero_price_variants = []
                                for i, variant in enumerate(variants):
                                    variant_id = variant.get('id')
                                    sku = variant.get('sku')
                                    price_tiers = variant.get('price_tiers', [])
                                    attributes = variant.get('attributes', {})
                                    pack_size = attributes.get('pack_size', 'Unknown')
                                    size_code = attributes.get('size_code', 'Unknown')
                                    
                                    print(f"\nVariant {i+1}:")
                                    print(f"  ID: {variant_id}")
                                    print(f"  SKU: {sku}")
                                    print(f"  Size: {size_code}")
                                    print(f"  Pack Size: {pack_size}")
                                    print(f"  Price Tiers: {json.dumps(price_tiers, indent=4)}")
                                    
                                    # Check for 0 values in price_tiers
                                    has_zero_price = False
                                    for tier in price_tiers:
                                        if tier.get('price', 0) == 0:
                                            has_zero_price = True
                                            zero_price_variants.append({
                                                'variant_id': variant_id,
                                                'sku': sku,
                                                'size_code': size_code,
                                                'pack_size': pack_size,
                                                'zero_tier': tier,
                                                'all_tiers': price_tiers
                                            })
                                    
                                    if has_zero_price:
                                        print(f"  ❌ CONTAINS ZERO PRICING")
                                    else:
                                        print(f"  ✅ NO ZERO PRICING")
                                
                                if zero_price_variants:
                                    self.log_test("Baby Blue Zero Price Tiers Found", False, 
                                                f"Found {len(zero_price_variants)} variants with 0 pricing")
                                    
                                    print(f"\n❌ ZERO PRICE VARIANTS DETAILS:")
                                    for variant in zero_price_variants:
                                        print(f"  Variant: {variant['sku']}")
                                        print(f"  Size: {variant['size_code']} ({variant['pack_size']} pack)")
                                        print(f"  Zero Price Tier: {variant['zero_tier']}")
                                        print(f"  All Price Tiers: {variant['all_tiers']}")
                                        print(f"  ---")
                                else:
                                    self.log_test("Baby Blue Zero Price Tiers", True, "No variants with 0 pricing found")
                                
                                self.log_test("Baby Blue Variants Analysis", True, f"Analyzed {len(variants)} variants")
                                
                            else:
                                error_text = await detail_resp.text()
                                self.log_test("Baby Blue Product Details", False, f"Status {detail_resp.status}: {error_text}")
                    else:
                        self.log_test("Find Baby Blue Product", False, "Baby Blue product not found")
                        
        except Exception as e:
            self.log_test("Baby Blue Investigation", False, f"Exception: {str(e)}")

    async def investigate_duplicate_categories_issue(self):
        """Investigate Duplicate Categories Issue"""
        print("\n📂 INVESTIGATING DUPLICATE CATEGORIES ISSUE...")
        
        # Check GET /api/products/filter-options for duplicate categories
        print("\n🔍 Checking Filter Options API for Duplicate Categories...")
        try:
            async with self.session.get(f"{API_BASE}/products/filter-options") as resp:
                if resp.status == 200:
                    filter_options = await resp.json()
                    self.log_test("GET /api/products/filter-options", True, "Filter options retrieved successfully")
                    
                    categories = filter_options.get('categories', [])
                    print(f"\n📋 FILTER OPTIONS CATEGORIES ANALYSIS:")
                    print(f"Categories: {categories}")
                    print(f"Category Count: {len(categories)}")
                    
                    # Check for duplicates
                    unique_categories = list(set(categories))
                    if len(categories) != len(unique_categories):
                        duplicates = [cat for cat in categories if categories.count(cat) > 1]
                        unique_duplicates = list(set(duplicates))
                        self.log_test("Duplicate Categories in Filter Options", False, 
                                    f"Found duplicate categories: {unique_duplicates}")
                        
                        print(f"\n❌ DUPLICATE CATEGORIES FOUND:")
                        for duplicate in unique_duplicates:
                            count = categories.count(duplicate)
                            print(f"  - '{duplicate}' appears {count} times")
                    else:
                        self.log_test("Duplicate Categories in Filter Options", True, "No duplicate categories found")
                    
                    # Log all filter options for reference
                    print(f"\n📊 COMPLETE FILTER OPTIONS:")
                    for key, value in filter_options.items():
                        print(f"  {key}: {value}")
                        
                else:
                    error_text = await resp.text()
                    self.log_test("GET /api/products/filter-options", False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("GET /api/products/filter-options", False, f"Exception: {str(e)}")

    async def investigate_business_settings_categories(self):
        """Check BusinessSettings for duplicate categories"""
        print("\n⚙️ INVESTIGATING BUSINESS SETTINGS CATEGORIES...")
        
        if not self.admin_token:
            self.log_test("BusinessSettings Investigation", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        try:
            async with self.session.get(f"{API_BASE}/admin/settings", headers=headers) as resp:
                if resp.status == 200:
                    business_settings = await resp.json()
                    self.log_test("GET /api/admin/settings", True, "Business settings retrieved successfully")
                    
                    available_categories = business_settings.get('available_categories', [])
                    print(f"\n⚙️ BUSINESS SETTINGS AVAILABLE CATEGORIES:")
                    print(f"Available Categories: {available_categories}")
                    print(f"Category Count: {len(available_categories)}")
                    
                    # Check for duplicates in business settings
                    unique_business_categories = list(set(available_categories))
                    if len(available_categories) != len(unique_business_categories):
                        business_duplicates = [cat for cat in available_categories if available_categories.count(cat) > 1]
                        unique_business_duplicates = list(set(business_duplicates))
                        self.log_test("Duplicate Categories in BusinessSettings", False, 
                                    f"Found duplicate categories in BusinessSettings: {unique_business_duplicates}")
                        
                        print(f"\n❌ DUPLICATE CATEGORIES IN BUSINESS SETTINGS:")
                        for duplicate in unique_business_duplicates:
                            count = available_categories.count(duplicate)
                            print(f"  - '{duplicate}' appears {count} times")
                    else:
                        self.log_test("Duplicate Categories in BusinessSettings", True, "No duplicate categories in BusinessSettings")
                    
                    # Log complete business settings for reference
                    print(f"\n📊 COMPLETE BUSINESS SETTINGS:")
                    for key, value in business_settings.items():
                        if isinstance(value, list) and len(value) > 10:
                            print(f"  {key}: [{len(value)} items] {value[:5]}...")
                        else:
                            print(f"  {key}: {value}")
                        
                else:
                    error_text = await resp.text()
                    self.log_test("GET /api/admin/settings", False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("GET /api/admin/settings", False, f"Exception: {str(e)}")

    async def scan_all_variants_for_zero_pricing(self):
        """Find any variants with price_tiers containing 0 values across all products"""
        print("\n🔍 SCANNING ALL PRODUCTS FOR VARIANTS WITH 0 PRICE TIERS...")
        
        try:
            async with self.session.get(f"{API_BASE}/products") as resp:
                if resp.status == 200:
                    products = await resp.json()
                    
                    all_zero_price_variants = []
                    
                    for product in products:
                        product_id = product.get('id')
                        product_name = product.get('name')
                        
                        # Get full product details
                        async with self.session.get(f"{API_BASE}/products/{product_id}") as detail_resp:
                            if detail_resp.status == 200:
                                product_details = await detail_resp.json()
                                variants = product_details.get('variants', [])
                                
                                for variant in variants:
                                    price_tiers = variant.get('price_tiers', [])
                                    for tier in price_tiers:
                                        if tier.get('price', 0) == 0:
                                            all_zero_price_variants.append({
                                                'product_name': product_name,
                                                'product_id': product_id,
                                                'variant_id': variant.get('id'),
                                                'sku': variant.get('sku'),
                                                'zero_tier': tier,
                                                'all_tiers': price_tiers,
                                                'attributes': variant.get('attributes', {})
                                            })
                    
                    if all_zero_price_variants:
                        self.log_test("System-wide Zero Price Variants", False, 
                                    f"Found {len(all_zero_price_variants)} variants with 0 pricing across all products")
                        
                        print(f"\n❌ ALL VARIANTS WITH ZERO PRICING:")
                        print("="*80)
                        for variant in all_zero_price_variants:
                            print(f"Product: {variant['product_name']}")
                            print(f"Variant SKU: {variant['sku']}")
                            print(f"Variant ID: {variant['variant_id']}")
                            print(f"Attributes: {variant['attributes']}")
                            print(f"Zero Price Tier: {variant['zero_tier']}")
                            print(f"All Price Tiers: {variant['all_tiers']}")
                            print("-" * 40)
                    else:
                        self.log_test("System-wide Zero Price Variants", True, "No variants with 0 pricing found across all products")
                        
        except Exception as e:
            self.log_test("System-wide Zero Price Scan", False, f"Exception: {str(e)}")

    async def run_investigation(self):
        """Run the complete investigation"""
        print("🔍 STARTING PRICE RANGE AND DUPLICATE CATEGORIES INVESTIGATION")
        print(f"🌐 Backend URL: {API_BASE}")
        print("="*80)
        
        await self.authenticate()
        
        if not self.admin_token:
            print("❌ Cannot proceed without admin authentication")
            return
        
        # Run all investigations
        await self.investigate_price_range_issue()
        await self.investigate_baby_blue_variants()
        await self.investigate_duplicate_categories_issue()
        await self.investigate_business_settings_categories()
        await self.scan_all_variants_for_zero_pricing()
        
        # Print summary
        print("\n" + "="*80)
        print("📊 INVESTIGATION SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        
        if failed_tests > 0:
            print(f"\n❌ ISSUES FOUND:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['details']}")
        
        print(f"\n🎯 Investigation completed!")
        return failed_tests == 0

async def main():
    """Run the investigation"""
    async with PriceCategoriesInvestigator() as investigator:
        success = await investigator.run_investigation()
        return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)