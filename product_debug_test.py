#!/usr/bin/env python3
"""
Product Loading Debug Test for M Supplies E-commerce Platform
Specifically designed to debug the "Failed to load product" issue
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

class ProductDebugTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.test_results = []
        self.product_ids = []
        
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
    
    async def authenticate_admin(self):
        """Authenticate admin user"""
        print("\n🔐 Testing Admin Authentication...")
        
        try:
            async with self.session.post(f"{API_BASE}/auth/login", json=ADMIN_CREDENTIALS) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.admin_token = data.get('access_token')
                    self.log_test("Admin Authentication", True, f"Token received: {self.admin_token[:20]}...")
                    return True
                else:
                    error_text = await resp.text()
                    self.log_test("Admin Authentication", False, f"Status {resp.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    async def test_product_list_endpoint(self):
        """Test GET /api/products endpoint"""
        print("\n📋 Testing Product List Endpoint...")
        
        try:
            async with self.session.get(f"{API_BASE}/products") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if isinstance(data, list):
                        self.product_ids = [product.get('id') for product in data if product.get('id')]
                        self.log_test("Product List Endpoint", True, f"Found {len(data)} products")
                        
                        # Check product structure
                        if data:
                            first_product = data[0]
                            required_fields = ['id', 'name', 'category']
                            missing_fields = [field for field in required_fields if field not in first_product]
                            
                            if missing_fields:
                                self.log_test("Product Structure Check", False, f"Missing fields: {missing_fields}")
                            else:
                                self.log_test("Product Structure Check", True, "All required fields present")
                        
                        return True
                    else:
                        self.log_test("Product List Endpoint", False, f"Expected list, got {type(data)}")
                        return False
                else:
                    error_text = await resp.text()
                    self.log_test("Product List Endpoint", False, f"Status {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Product List Endpoint", False, f"Exception: {str(e)}")
            return False
    
    async def test_individual_product_loading(self):
        """Test loading each product individually to identify problematic ones"""
        print("\n🔍 Testing Individual Product Loading...")
        
        if not self.product_ids:
            self.log_test("Individual Product Loading", False, "No product IDs available")
            return
        
        failed_products = []
        successful_products = []
        
        for i, product_id in enumerate(self.product_ids):
            try:
                async with self.session.get(f"{API_BASE}/products/{product_id}") as resp:
                    if resp.status == 200:
                        product_data = await resp.json()
                        
                        # Validate product data structure
                        required_fields = ['id', 'name', 'category', 'variants']
                        missing_fields = [field for field in required_fields if field not in product_data]
                        
                        if missing_fields:
                            failed_products.append({
                                'id': product_id,
                                'reason': f"Missing fields: {missing_fields}"
                            })
                            self.log_test(f"Product {i+1} Structure", False, f"ID: {product_id}, Missing: {missing_fields}")
                        else:
                            # Check variants structure
                            variants = product_data.get('variants', [])
                            if not variants:
                                failed_products.append({
                                    'id': product_id,
                                    'reason': "No variants found"
                                })
                                self.log_test(f"Product {i+1} Variants", False, f"ID: {product_id}, No variants")
                            else:
                                # Check variant structure
                                variant_issues = []
                                for j, variant in enumerate(variants):
                                    variant_required = ['id', 'sku', 'attributes', 'price_tiers']
                                    variant_missing = [field for field in variant_required if field not in variant]
                                    if variant_missing:
                                        variant_issues.append(f"Variant {j}: missing {variant_missing}")
                                
                                if variant_issues:
                                    failed_products.append({
                                        'id': product_id,
                                        'reason': f"Variant issues: {'; '.join(variant_issues)}"
                                    })
                                    self.log_test(f"Product {i+1} Variant Structure", False, f"ID: {product_id}, Issues: {variant_issues}")
                                else:
                                    successful_products.append(product_id)
                                    self.log_test(f"Product {i+1} Load", True, f"ID: {product_id}, {len(variants)} variants")
                    else:
                        error_text = await resp.text()
                        failed_products.append({
                            'id': product_id,
                            'reason': f"HTTP {resp.status}: {error_text}"
                        })
                        self.log_test(f"Product {i+1} Load", False, f"ID: {product_id}, Status: {resp.status}")
                        
            except Exception as e:
                failed_products.append({
                    'id': product_id,
                    'reason': f"Exception: {str(e)}"
                })
                self.log_test(f"Product {i+1} Load", False, f"ID: {product_id}, Exception: {str(e)}")
        
        # Summary
        total_products = len(self.product_ids)
        successful_count = len(successful_products)
        failed_count = len(failed_products)
        
        self.log_test("Product Loading Summary", failed_count == 0, 
                     f"Success: {successful_count}/{total_products}, Failed: {failed_count}")
        
        if failed_products:
            print("\n❌ FAILED PRODUCTS DETAILS:")
            for product in failed_products:
                print(f"  • ID: {product['id']} - {product['reason']}")
        
        return failed_products
    
    async def test_admin_product_access(self):
        """Test admin access to products for editing"""
        print("\n🔧 Testing Admin Product Access...")
        
        if not self.admin_token:
            self.log_test("Admin Product Access", False, "No admin token available")
            return
        
        if not self.product_ids:
            self.log_test("Admin Product Access", False, "No product IDs available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test accessing first few products as admin
        test_products = self.product_ids[:3]  # Test first 3 products
        
        for i, product_id in enumerate(test_products):
            try:
                async with self.session.get(f"{API_BASE}/products/{product_id}", headers=headers) as resp:
                    if resp.status == 200:
                        product_data = await resp.json()
                        self.log_test(f"Admin Access Product {i+1}", True, f"ID: {product_id}")
                        
                        # Test if this product can be updated (simulate edit form access)
                        # Check if all required fields for editing are present
                        edit_required = ['id', 'name', 'description', 'category', 'variants', 'color', 'type']
                        missing_edit_fields = [field for field in edit_required if field not in product_data]
                        
                        if missing_edit_fields:
                            self.log_test(f"Edit Form Data Product {i+1}", False, 
                                        f"ID: {product_id}, Missing for edit: {missing_edit_fields}")
                        else:
                            self.log_test(f"Edit Form Data Product {i+1}", True, 
                                        f"ID: {product_id}, All edit fields present")
                    else:
                        error_text = await resp.text()
                        self.log_test(f"Admin Access Product {i+1}", False, 
                                    f"ID: {product_id}, Status: {resp.status}, Error: {error_text}")
                        
            except Exception as e:
                self.log_test(f"Admin Access Product {i+1}", False, 
                            f"ID: {product_id}, Exception: {str(e)}")
    
    async def test_product_schema_validation(self):
        """Test if products match expected schema after recent changes"""
        print("\n📋 Testing Product Schema Validation...")
        
        if not self.product_ids:
            self.log_test("Product Schema Validation", False, "No product IDs available")
            return
        
        # Test first product for detailed schema validation
        product_id = self.product_ids[0]
        
        try:
            async with self.session.get(f"{API_BASE}/products/{product_id}") as resp:
                if resp.status == 200:
                    product_data = await resp.json()
                    
                    # Expected schema based on recent changes
                    expected_schema = {
                        'id': str,
                        'name': str,
                        'description': str,
                        'category': str,
                        'color': str,  # Product-level color field
                        'type': str,   # Product-level type field
                        'variants': list,
                        'is_active': bool,
                        'created_at': str,
                        'updated_at': str
                    }
                    
                    schema_issues = []
                    
                    for field, expected_type in expected_schema.items():
                        if field not in product_data:
                            schema_issues.append(f"Missing field: {field}")
                        elif not isinstance(product_data[field], expected_type):
                            actual_type = type(product_data[field]).__name__
                            schema_issues.append(f"Field {field}: expected {expected_type.__name__}, got {actual_type}")
                    
                    # Validate variant schema
                    variants = product_data.get('variants', [])
                    if variants:
                        variant_schema = {
                            'id': str,
                            'sku': str,
                            'attributes': dict,
                            'price_tiers': list,
                            'stock_qty': int,
                            'on_hand': int,
                            'allocated': int
                        }
                        
                        for i, variant in enumerate(variants[:2]):  # Check first 2 variants
                            for field, expected_type in variant_schema.items():
                                if field not in variant:
                                    schema_issues.append(f"Variant {i}: Missing field {field}")
                                elif not isinstance(variant[field], expected_type):
                                    actual_type = type(variant[field]).__name__
                                    schema_issues.append(f"Variant {i} field {field}: expected {expected_type.__name__}, got {actual_type}")
                            
                            # Check attributes structure
                            attributes = variant.get('attributes', {})
                            required_attributes = ['color', 'type', 'size_code']
                            for attr in required_attributes:
                                if attr not in attributes:
                                    schema_issues.append(f"Variant {i}: Missing attribute {attr}")
                    
                    if schema_issues:
                        self.log_test("Product Schema Validation", False, f"Schema issues: {'; '.join(schema_issues)}")
                    else:
                        self.log_test("Product Schema Validation", True, "Product schema matches expected structure")
                        
                else:
                    error_text = await resp.text()
                    self.log_test("Product Schema Validation", False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Product Schema Validation", False, f"Exception: {str(e)}")
    
    async def test_database_seed_data_integrity(self):
        """Test if seed data exists and has correct structure"""
        print("\n🌱 Testing Database Seed Data Integrity...")
        
        # Use filter endpoint to get all products with full details
        try:
            filter_request = {
                "page": 1,
                "limit": 100,
                "filters": {}
            }
            
            async with self.session.post(f"{API_BASE}/products/filter", json=filter_request) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    products = data.get('products', [])
                    
                    if not products:
                        self.log_test("Seed Data Existence", False, "No products found in database")
                        return
                    
                    self.log_test("Seed Data Existence", True, f"Found {len(products)} products")
                    
                    # Check for expected products
                    expected_products = [
                        "Premium Polymailers",
                        "Bubble Wrap Polymailers",
                        "Heavy-Duty Packaging Scissors",
                        "Clear Packaging Tape"
                    ]
                    
                    found_products = [p['name'] for p in products]
                    missing_products = [name for name in expected_products if name not in found_products]
                    
                    if missing_products:
                        self.log_test("Expected Products Check", False, f"Missing products: {missing_products}")
                    else:
                        self.log_test("Expected Products Check", True, "All expected products found")
                    
                    # Check variant counts
                    total_variants = 0
                    product_variant_counts = {}
                    
                    for product in products:
                        variants = product.get('variants', [])
                        variant_count = len(variants)
                        total_variants += variant_count
                        product_variant_counts[product['name']] = variant_count
                    
                    # Expected variant counts based on seed data
                    expected_variant_counts = {
                        "Premium Polymailers": 24,  # 6 sizes × 4 colors
                        "Bubble Wrap Polymailers": 3,  # 3 sizes × 1 color (white only)
                        "Heavy-Duty Packaging Scissors": 1,
                        "Clear Packaging Tape": 3
                    }
                    
                    variant_count_issues = []
                    for product_name, expected_count in expected_variant_counts.items():
                        actual_count = product_variant_counts.get(product_name, 0)
                        if actual_count != expected_count:
                            variant_count_issues.append(f"{product_name}: expected {expected_count}, got {actual_count}")
                    
                    if variant_count_issues:
                        self.log_test("Variant Count Validation", False, f"Issues: {'; '.join(variant_count_issues)}")
                    else:
                        self.log_test("Variant Count Validation", True, f"All variant counts correct. Total: {total_variants}")
                    
                else:
                    error_text = await resp.text()
                    self.log_test("Seed Data Integrity", False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Seed Data Integrity", False, f"Exception: {str(e)}")
    
    async def test_specific_product_edit_simulation(self):
        """Simulate the exact scenario where product edit fails"""
        print("\n🎯 Testing Specific Product Edit Simulation...")
        
        if not self.admin_token or not self.product_ids:
            self.log_test("Product Edit Simulation", False, "Missing admin token or product IDs")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Try to simulate the exact edit flow
        for i, product_id in enumerate(self.product_ids[:3]):  # Test first 3 products
            print(f"\n  Testing edit flow for product {i+1} (ID: {product_id})...")
            
            # Step 1: Fetch product for editing (this is where the error occurs)
            try:
                async with self.session.get(f"{API_BASE}/products/{product_id}", headers=headers) as resp:
                    if resp.status == 200:
                        product_data = await resp.json()
                        
                        # Step 2: Validate all data needed for edit form
                        edit_form_fields = [
                            'id', 'name', 'description', 'category', 'color', 'type', 
                            'variants', 'is_active', 'images'
                        ]
                        
                        missing_fields = []
                        for field in edit_form_fields:
                            if field not in product_data:
                                missing_fields.append(field)
                            elif product_data[field] is None:
                                missing_fields.append(f"{field} (null)")
                        
                        if missing_fields:
                            self.log_test(f"Edit Form Data Product {i+1}", False, 
                                        f"Missing/null fields: {missing_fields}")
                        else:
                            # Step 3: Validate variant data for edit form
                            variants = product_data.get('variants', [])
                            variant_issues = []
                            
                            for j, variant in enumerate(variants):
                                required_variant_fields = ['id', 'sku', 'attributes', 'price_tiers', 'stock_qty']
                                for field in required_variant_fields:
                                    if field not in variant or variant[field] is None:
                                        variant_issues.append(f"Variant {j}: {field} missing/null")
                                
                                # Check attributes
                                attributes = variant.get('attributes', {})
                                if not isinstance(attributes, dict):
                                    variant_issues.append(f"Variant {j}: attributes not a dict")
                                else:
                                    required_attrs = ['color', 'type', 'size_code']
                                    for attr in required_attrs:
                                        if attr not in attributes or attributes[attr] is None:
                                            variant_issues.append(f"Variant {j}: attribute {attr} missing/null")
                            
                            if variant_issues:
                                self.log_test(f"Edit Variant Data Product {i+1}", False, 
                                            f"Issues: {'; '.join(variant_issues[:5])}")  # Show first 5 issues
                            else:
                                self.log_test(f"Edit Form Complete Product {i+1}", True, 
                                            f"All edit form data valid, {len(variants)} variants")
                    
                    elif resp.status == 401:
                        self.log_test(f"Edit Auth Product {i+1}", False, "Authentication failed - this could be the issue!")
                    elif resp.status == 404:
                        self.log_test(f"Edit Access Product {i+1}", False, "Product not found - this could be the issue!")
                    else:
                        error_text = await resp.text()
                        self.log_test(f"Edit Access Product {i+1}", False, 
                                    f"HTTP {resp.status}: {error_text} - this could be the issue!")
                        
            except Exception as e:
                self.log_test(f"Edit Access Product {i+1}", False, 
                            f"Exception: {str(e)} - this could be the issue!")
    
    def print_summary(self):
        """Print test summary with focus on debugging results"""
        print("\n" + "="*70)
        print("🔍 PRODUCT LOADING DEBUG TEST SUMMARY")
        print("="*70)
        
        passed = sum(1 for result in self.test_results if result['success'])
        failed = len(self.test_results) - passed
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        if failed > 0:
            print("\n🚨 CRITICAL ISSUES FOUND:")
            print("The following issues could be causing 'Failed to load product' errors:")
            print("-" * 70)
            
            for result in self.test_results:
                if not result['success']:
                    print(f"❌ {result['test']}")
                    print(f"   Details: {result['details']}")
                    print()
        else:
            print("\n✅ NO CRITICAL ISSUES FOUND")
            print("All product loading tests passed. The issue might be frontend-related.")
        
        return passed, failed

async def main():
    """Run product loading debug tests"""
    print("🔍 Starting Product Loading Debug Tests")
    print(f"Testing against: {API_BASE}")
    print("Focus: Debugging 'Failed to load product' issue")
    
    async with ProductDebugTester() as tester:
        # Authentication is critical for admin product access
        auth_success = await tester.authenticate_admin()
        
        # Test basic product listing
        await tester.test_product_list_endpoint()
        
        # Test individual product loading - this is key to finding the issue
        await tester.test_individual_product_loading()
        
        # Test admin access to products
        if auth_success:
            await tester.test_admin_product_access()
        
        # Test product schema validation
        await tester.test_product_schema_validation()
        
        # Test database integrity
        await tester.test_database_seed_data_integrity()
        
        # Simulate the exact edit scenario
        if auth_success:
            await tester.test_specific_product_edit_simulation()
        
        # Print detailed summary
        passed, failed = tester.print_summary()
        
        return failed == 0

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)