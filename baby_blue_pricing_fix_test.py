#!/usr/bin/env python3
"""
Baby Blue Product Pricing Fix Test
Fixes the Baby Blue product price_tiers issue with 0 values and verifies the fix
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, Any

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://msupplies-store.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "email": "admin@polymailer.com",
    "password": "admin123"
}

# Baby Blue product ID from the review request
BABY_BLUE_PRODUCT_ID = "6084a6ff-1911-488b-9288-2bc95e50cafa"

class BabyBluePricingFixer:
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
                    return False
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
        
        return True
    
    async def investigate_baby_blue_pricing_issue(self):
        """Investigate the current Baby Blue product pricing structure"""
        print("\n🔍 Investigating Baby Blue Product Pricing Issue...")
        
        try:
            async with self.session.get(f"{API_BASE}/products/{BABY_BLUE_PRODUCT_ID}") as resp:
                if resp.status == 200:
                    product = await resp.json()
                    self.log_test("Baby Blue Product Access", True, f"Product: {product.get('name')}")
                    
                    variants = product.get('variants', [])
                    self.log_test("Baby Blue Variants Found", len(variants) > 0, f"Found {len(variants)} variants")
                    
                    # Analyze each variant's pricing structure
                    problematic_variants = []
                    for i, variant in enumerate(variants):
                        variant_id = variant.get('id')
                        sku = variant.get('sku', 'Unknown')
                        price_tiers = variant.get('price_tiers', [])
                        pack_size = variant.get('attributes', {}).get('pack_size', 'Unknown')
                        
                        print(f"\n  Variant {i+1}: {sku} (Pack size: {pack_size})")
                        print(f"  Price tiers: {price_tiers}")
                        
                        # Check for 0 values in price_tiers
                        has_zero_prices = any(tier.get('price', 0) == 0.0 for tier in price_tiers)
                        if has_zero_prices:
                            problematic_variants.append({
                                'variant_id': variant_id,
                                'sku': sku,
                                'pack_size': pack_size,
                                'price_tiers': price_tiers,
                                'variant_index': i
                            })
                            self.log_test(f"Variant {i+1} Pricing Issue", False, f"Found 0 values in price_tiers: {price_tiers}")
                        else:
                            self.log_test(f"Variant {i+1} Pricing OK", True, f"No 0 values found")
                    
                    if problematic_variants:
                        self.log_test("Pricing Issue Confirmed", False, f"Found {len(problematic_variants)} variants with 0 pricing")
                        return product, problematic_variants
                    else:
                        self.log_test("Pricing Issue Status", True, "No pricing issues found")
                        return product, []
                    
                else:
                    error_text = await resp.text()
                    self.log_test("Baby Blue Product Access", False, f"Status {resp.status}: {error_text}")
                    return None, []
                    
        except Exception as e:
            self.log_test("Baby Blue Investigation", False, f"Exception: {str(e)}")
            return None, []
    
    async def check_price_range_in_listing(self):
        """Check the current price range display in product listing"""
        print("\n💰 Checking Price Range in Product Listing...")
        
        try:
            async with self.session.get(f"{API_BASE}/products") as resp:
                if resp.status == 200:
                    products = await resp.json()
                    
                    # Find Baby Blue product in listing
                    baby_blue_listing = None
                    for product in products:
                        if product.get('id') == BABY_BLUE_PRODUCT_ID:
                            baby_blue_listing = product
                            break
                    
                    if baby_blue_listing:
                        price_range = baby_blue_listing.get('price_range', {})
                        min_price = price_range.get('min', 0)
                        max_price = price_range.get('max', 0)
                        
                        self.log_test("Baby Blue in Product Listing", True, f"Found in listing")
                        self.log_test("Current Price Range", min_price > 0, f"Price range: ${min_price} - ${max_price}")
                        
                        if min_price == 0:
                            self.log_test("Price Range $0 Issue Confirmed", False, "Price range shows $0 minimum")
                            return True  # Issue confirmed
                        else:
                            self.log_test("Price Range Status", True, "No $0 price range issue")
                            return False  # No issue
                    else:
                        self.log_test("Baby Blue in Product Listing", False, "Baby Blue not found in product listing")
                        return False
                        
                else:
                    error_text = await resp.text()
                    self.log_test("Product Listing Check", False, f"Status {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Price Range Check", False, f"Exception: {str(e)}")
            return False
    
    async def fix_baby_blue_pricing(self, product, problematic_variants):
        """Fix the Baby Blue product pricing by updating price_tiers"""
        print("\n🔧 Fixing Baby Blue Product Pricing...")
        
        if not self.admin_token:
            self.log_test("Fix Baby Blue Pricing", False, "No admin token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Create updated variants with fixed pricing
        updated_variants = []
        for variant in product.get('variants', []):
            updated_variant = variant.copy()
            pack_size = variant.get('attributes', {}).get('pack_size', 50)
            
            # Fix pricing based on pack size as specified in the review request
            if pack_size == 50:
                # 50-pack: $7.99 (base price)
                updated_variant['price_tiers'] = [
                    {"min_quantity": 1, "price": 7.99},
                    {"min_quantity": 25, "price": 7.99},
                    {"min_quantity": 50, "price": 7.99}
                ]
                self.log_test(f"50-pack Pricing Fix", True, "Set to $7.99 for all quantities")
            elif pack_size == 100:
                # 100-pack: $14.99 (standard 100-pack pricing)
                updated_variant['price_tiers'] = [
                    {"min_quantity": 1, "price": 7.99},    # Base price for small quantities
                    {"min_quantity": 25, "price": 7.99},   # Same base price
                    {"min_quantity": 50, "price": 7.99},   # Same base price
                    {"min_quantity": 100, "price": 14.99}  # 100-pack pricing
                ]
                self.log_test(f"100-pack Pricing Fix", True, "Set to $7.99 base, $14.99 for 100+")
            else:
                # Keep existing pricing for other pack sizes, but ensure no 0 values
                price_tiers = variant.get('price_tiers', [])
                fixed_price_tiers = []
                for tier in price_tiers:
                    if tier.get('price', 0) == 0.0:
                        # Replace 0 values with base price of $7.99
                        fixed_tier = tier.copy()
                        fixed_tier['price'] = 7.99
                        fixed_price_tiers.append(fixed_tier)
                    else:
                        fixed_price_tiers.append(tier)
                
                updated_variant['price_tiers'] = fixed_price_tiers if fixed_price_tiers else [{"min_quantity": 1, "price": 7.99}]
                self.log_test(f"Other Pack Size Fix", True, f"Fixed pricing for pack size {pack_size}")
            
            updated_variants.append(updated_variant)
        
        # Prepare update payload
        update_payload = {
            "variants": updated_variants
        }
        
        # Send update request
        try:
            async with self.session.put(f"{API_BASE}/admin/products/{BABY_BLUE_PRODUCT_ID}", 
                                      json=update_payload, headers=headers) as resp:
                if resp.status == 200:
                    updated_product = await resp.json()
                    self.log_test("Baby Blue Pricing Update", True, "Pricing update successful")
                    
                    # Verify the update response
                    updated_variants_response = updated_product.get('variants', [])
                    for i, variant in enumerate(updated_variants_response):
                        price_tiers = variant.get('price_tiers', [])
                        has_zero_prices = any(tier.get('price', 0) == 0.0 for tier in price_tiers)
                        
                        if not has_zero_prices:
                            self.log_test(f"Variant {i+1} Fix Verification", True, "No more 0 values in pricing")
                        else:
                            self.log_test(f"Variant {i+1} Fix Verification", False, "Still has 0 values in pricing")
                    
                    return True
                    
                else:
                    error_text = await resp.text()
                    self.log_test("Baby Blue Pricing Update", False, f"Status {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Baby Blue Pricing Update", False, f"Exception: {str(e)}")
            return False
    
    async def verify_fix_in_product_listing(self):
        """Verify that the fix is reflected in the product listing"""
        print("\n✅ Verifying Fix in Product Listing...")
        
        try:
            async with self.session.get(f"{API_BASE}/products") as resp:
                if resp.status == 200:
                    products = await resp.json()
                    
                    # Find Baby Blue product in listing
                    baby_blue_listing = None
                    for product in products:
                        if product.get('id') == BABY_BLUE_PRODUCT_ID:
                            baby_blue_listing = product
                            break
                    
                    if baby_blue_listing:
                        price_range = baby_blue_listing.get('price_range', {})
                        min_price = price_range.get('min', 0)
                        max_price = price_range.get('max', 0)
                        
                        self.log_test("Baby Blue Post-Fix Listing", True, f"Found in listing")
                        
                        if min_price > 0:
                            self.log_test("Price Range Fix Verification", True, f"Price range now: ${min_price} - ${max_price}")
                            
                            # Check if price range is reasonable (should be $7.99 - $14.99)
                            if min_price >= 7.99 and max_price >= 14.99:
                                self.log_test("Price Range Values", True, "Price range values are correct")
                            else:
                                self.log_test("Price Range Values", False, f"Unexpected price range: ${min_price} - ${max_price}")
                        else:
                            self.log_test("Price Range Fix Verification", False, "Price range still shows $0 minimum")
                            return False
                        
                        return True
                    else:
                        self.log_test("Baby Blue Post-Fix Listing", False, "Baby Blue not found in product listing")
                        return False
                        
                else:
                    error_text = await resp.text()
                    self.log_test("Post-Fix Listing Check", False, f"Status {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Fix Verification", False, f"Exception: {str(e)}")
            return False
    
    async def verify_customer_product_access(self):
        """Verify that customers can access the product with correct pricing"""
        print("\n👥 Verifying Customer Product Access...")
        
        try:
            # Access product without authentication (customer view)
            async with self.session.get(f"{API_BASE}/products/{BABY_BLUE_PRODUCT_ID}") as resp:
                if resp.status == 200:
                    product = await resp.json()
                    self.log_test("Customer Product Access", True, f"Customer can access: {product.get('name')}")
                    
                    variants = product.get('variants', [])
                    for i, variant in enumerate(variants):
                        price_tiers = variant.get('price_tiers', [])
                        pack_size = variant.get('attributes', {}).get('pack_size', 'Unknown')
                        
                        if price_tiers:
                            base_price = price_tiers[0].get('price', 0)
                            has_zero_prices = any(tier.get('price', 0) == 0.0 for tier in price_tiers)
                            
                            if not has_zero_prices and base_price > 0:
                                self.log_test(f"Customer Variant {i+1} Pricing", True, 
                                            f"Pack size {pack_size}: Base price ${base_price}")
                            else:
                                self.log_test(f"Customer Variant {i+1} Pricing", False, 
                                            f"Pack size {pack_size}: Still has pricing issues")
                        else:
                            self.log_test(f"Customer Variant {i+1} Pricing", False, "No price tiers found")
                    
                    return True
                    
                else:
                    error_text = await resp.text()
                    self.log_test("Customer Product Access", False, f"Status {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Customer Access Verification", False, f"Exception: {str(e)}")
            return False
    
    async def run_complete_fix_and_verification(self):
        """Run the complete Baby Blue pricing fix and verification process"""
        print("🎯 Baby Blue Product Pricing Fix and Verification")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not await self.authenticate():
            return
        
        # Step 2: Investigate current issue
        product, problematic_variants = await self.investigate_baby_blue_pricing_issue()
        if not product:
            return
        
        # Step 3: Check price range in listing
        has_price_range_issue = await self.check_price_range_in_listing()
        
        # Step 4: Fix pricing if issues found
        if problematic_variants or has_price_range_issue:
            print(f"\n🚨 Issues found - proceeding with fix...")
            fix_success = await self.fix_baby_blue_pricing(product, problematic_variants)
            
            if fix_success:
                # Step 5: Verify fix in product listing
                await self.verify_fix_in_product_listing()
                
                # Step 6: Verify customer access
                await self.verify_customer_product_access()
            else:
                self.log_test("Fix Process", False, "Failed to apply pricing fix")
        else:
            print(f"\n✅ No pricing issues found - Baby Blue product pricing is already correct")
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 BABY BLUE PRICING FIX SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for result in failed_tests:
                print(f"  • {result['test']}: {result['details']}")
        else:
            print(f"\n✅ All tests passed! Baby Blue pricing issue has been resolved.")

async def main():
    async with BabyBluePricingFixer() as fixer:
        await fixer.run_complete_fix_and_verification()

if __name__ == "__main__":
    asyncio.run(main())