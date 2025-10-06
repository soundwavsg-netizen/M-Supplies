#!/usr/bin/env python3
"""
Backend API Testing for M Supplies E-commerce Platform
Tests the advanced product filtering system and business rules
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, Any, List

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://supply-manager-20.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "email": "admin@polymailer.com",
    "password": "admin123"
}

CUSTOMER_CREDENTIALS = {
    "email": "customer@example.com", 
    "password": "customer123"
}

class BackendTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.customer_token = None
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
        """Authenticate admin and customer users"""
        print("\n🔐 Testing Authentication...")
        
        # Test admin login
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
        
        # Test customer login
        try:
            async with self.session.post(f"{API_BASE}/auth/login", json=CUSTOMER_CREDENTIALS) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.customer_token = data.get('access_token')
                    self.log_test("Customer Authentication", True, f"Token received: {self.customer_token[:20]}...")
                else:
                    error_text = await resp.text()
                    self.log_test("Customer Authentication", False, f"Status {resp.status}: {error_text}")
        except Exception as e:
            self.log_test("Customer Authentication", False, f"Exception: {str(e)}")
    
    async def test_filter_options_endpoint(self):
        """Test GET /api/products/filter-options"""
        print("\n🔍 Testing Filter Options Endpoint...")
        
        try:
            async with self.session.get(f"{API_BASE}/products/filter-options") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    # Check required fields
                    required_fields = ['colors', 'sizes', 'types', 'categories', 'price_range']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test("Filter Options Structure", False, f"Missing fields: {missing_fields}")
                    else:
                        self.log_test("Filter Options Structure", True, "All required fields present")
                    
                    # Validate expected data
                    expected_colors = ['white', 'pastel pink', 'champagne pink', 'milktea']
                    actual_colors = data.get('colors', [])
                    colors_match = all(color in actual_colors for color in expected_colors)
                    self.log_test("Filter Options - Colors", colors_match, 
                                f"Expected: {expected_colors}, Got: {actual_colors}")
                    
                    expected_types = ['normal', 'bubble wrap']
                    actual_types = data.get('types', [])
                    types_match = all(t in actual_types for t in expected_types)
                    self.log_test("Filter Options - Types", types_match,
                                f"Expected: {expected_types}, Got: {actual_types}")
                    
                    expected_categories = ['polymailers', 'accessories']
                    actual_categories = data.get('categories', [])
                    categories_match = all(cat in actual_categories for cat in expected_categories)
                    self.log_test("Filter Options - Categories", categories_match,
                                f"Expected: {expected_categories}, Got: {actual_categories}")
                    
                else:
                    error_text = await resp.text()
                    self.log_test("Filter Options Endpoint", False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Filter Options Endpoint", False, f"Exception: {str(e)}")
    
    async def test_product_filtering(self):
        """Test POST /api/products/filter with various filter combinations"""
        print("\n🎯 Testing Product Filtering...")
        
        # Test 1: Filter by color
        await self._test_filter({
            "filters": {"colors": ["white"]},
            "page": 1,
            "limit": 20
        }, "Filter by White Color")
        
        # Test 2: Filter by type (normal polymailers)
        await self._test_filter({
            "filters": {"type": "normal"},
            "page": 1,
            "limit": 20
        }, "Filter by Normal Type")
        
        # Test 3: Filter by type (bubble wrap) - should only return white
        await self._test_filter({
            "filters": {"type": "bubble wrap"},
            "page": 1,
            "limit": 20
        }, "Filter by Bubble Wrap Type")
        
        # Test 4: Filter by category
        await self._test_filter({
            "filters": {"categories": ["polymailers"]},
            "page": 1,
            "limit": 20
        }, "Filter by Polymailers Category")
        
        # Test 5: Filter by size
        await self._test_filter({
            "filters": {"sizes": ["25x35"]},
            "page": 1,
            "limit": 20
        }, "Filter by Size 25x35")
        
        # Test 6: Filter by price range
        await self._test_filter({
            "filters": {"price_min": 0.10, "price_max": 1.00},
            "page": 1,
            "limit": 20
        }, "Filter by Price Range")
        
        # Test 7: Filter by in_stock_only
        await self._test_filter({
            "filters": {"in_stock_only": True},
            "page": 1,
            "limit": 20
        }, "Filter by In Stock Only")
        
        # Test 8: Combined filters
        await self._test_filter({
            "filters": {
                "type": "normal",
                "colors": ["white", "pastel pink"],
                "sizes": ["25x35", "32x43"]
            },
            "page": 1,
            "limit": 20
        }, "Combined Filters Test")
    
    async def _test_filter(self, filter_request: Dict[str, Any], test_name: str):
        """Helper method to test a specific filter"""
        try:
            async with self.session.post(f"{API_BASE}/products/filter", json=filter_request) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    # Check response structure
                    required_fields = ['products', 'total', 'page', 'pages']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test(test_name, False, f"Missing response fields: {missing_fields}")
                        return
                    
                    products = data.get('products', [])
                    self.log_test(test_name, True, f"Found {len(products)} products, Total: {data.get('total', 0)}")
                    
                    # Validate filter results if specific filters applied
                    if 'filters' in filter_request:
                        await self._validate_filter_results(products, filter_request['filters'], test_name)
                    
                else:
                    error_text = await resp.text()
                    self.log_test(test_name, False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test(test_name, False, f"Exception: {str(e)}")
    
    async def _validate_filter_results(self, products: List[Dict], filters: Dict, test_name: str):
        """Validate that filter results match the applied filters"""
        for product in products:
            variants = product.get('variants', [])
            
            # Check color filter
            if 'colors' in filters and filters['colors']:
                for variant in variants:
                    variant_color = variant.get('attributes', {}).get('color')
                    if variant_color not in filters['colors']:
                        self.log_test(f"{test_name} - Color Validation", False, 
                                    f"Found variant with color '{variant_color}' not in filter {filters['colors']}")
                        return
            
            # Check type filter
            if 'type' in filters and filters['type']:
                for variant in variants:
                    variant_type = variant.get('attributes', {}).get('type')
                    if variant_type != filters['type']:
                        self.log_test(f"{test_name} - Type Validation", False,
                                    f"Found variant with type '{variant_type}' != '{filters['type']}'")
                        return
            
            # Check size filter
            if 'sizes' in filters and filters['sizes']:
                for variant in variants:
                    variant_size = variant.get('attributes', {}).get('size_code')
                    if variant_size not in filters['sizes']:
                        self.log_test(f"{test_name} - Size Validation", False,
                                    f"Found variant with size '{variant_size}' not in filter {filters['sizes']}")
                        return
    
    async def test_business_rules(self):
        """Test critical business rule: Bubble wrap polymailers only in white"""
        print("\n⚖️ Testing Business Rules...")
        
        # Get all bubble wrap products
        filter_request = {
            "filters": {"type": "bubble wrap"},
            "page": 1,
            "limit": 50
        }
        
        try:
            async with self.session.post(f"{API_BASE}/products/filter", json=filter_request) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    products = data.get('products', [])
                    
                    bubble_wrap_colors = set()
                    for product in products:
                        for variant in product.get('variants', []):
                            if variant.get('attributes', {}).get('type') == 'bubble wrap':
                                color = variant.get('attributes', {}).get('color')
                                bubble_wrap_colors.add(color)
                    
                    # Should only have white
                    if bubble_wrap_colors == {'white'}:
                        self.log_test("Business Rule - Bubble Wrap Colors", True, 
                                    "Bubble wrap only available in white")
                    else:
                        self.log_test("Business Rule - Bubble Wrap Colors", False,
                                    f"Found bubble wrap in colors: {bubble_wrap_colors}")
                else:
                    error_text = await resp.text()
                    self.log_test("Business Rule Test", False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Business Rule Test", False, f"Exception: {str(e)}")
    
    async def test_seed_data_verification(self):
        """Verify the expected seed data is present"""
        print("\n📊 Testing Seed Data Verification...")
        
        # Get all products
        try:
            async with self.session.post(f"{API_BASE}/products/filter", json={"page": 1, "limit": 100}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    products = data.get('products', [])
                    
                    # Expected products
                    expected_products = [
                        "Premium Polymailers",
                        "Bubble Wrap Polymailers", 
                        "Heavy-Duty Packaging Scissors",
                        "Clear Packaging Tape"
                    ]
                    
                    found_products = [p['name'] for p in products]
                    
                    for expected in expected_products:
                        if expected in found_products:
                            self.log_test(f"Seed Data - {expected}", True, "Product found")
                        else:
                            self.log_test(f"Seed Data - {expected}", False, "Product missing")
                    
                    # Count variants
                    total_variants = sum(len(p.get('variants', [])) for p in products)
                    
                    # Expected: 24 (normal) + 3 (bubble) + 1 (scissors) + 3 (tape) = 31
                    expected_variants = 31
                    if total_variants == expected_variants:
                        self.log_test("Seed Data - Variant Count", True, f"Found {total_variants} variants")
                    else:
                        self.log_test("Seed Data - Variant Count", False, 
                                    f"Expected {expected_variants}, found {total_variants}")
                    
                else:
                    error_text = await resp.text()
                    self.log_test("Seed Data Verification", False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Seed Data Verification", False, f"Exception: {str(e)}")
    
    async def test_sorting_options(self):
        """Test different sorting options"""
        print("\n📈 Testing Sorting Options...")
        
        sort_options = [
            ("best_sellers", "Best Sellers Sort"),
            ("price_low_high", "Price Low to High Sort"),
            ("price_high_low", "Price High to Low Sort"),
            ("newest", "Newest Sort")
        ]
        
        for sort_by, test_name in sort_options:
            filter_request = {
                "sort": {"sort_by": sort_by},
                "page": 1,
                "limit": 10
            }
            
            try:
                async with self.session.post(f"{API_BASE}/products/filter", json=filter_request) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        products = data.get('products', [])
                        self.log_test(test_name, True, f"Returned {len(products)} products")
                    else:
                        error_text = await resp.text()
                        self.log_test(test_name, False, f"Status {resp.status}: {error_text}")
            except Exception as e:
                self.log_test(test_name, False, f"Exception: {str(e)}")
    
    async def test_admin_inventory_management(self):
        """Test admin inventory management endpoints"""
        print("\n🔧 Testing Admin Inventory Management...")
        
        if not self.admin_token:
            self.log_test("Admin Inventory Test", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test inventory listing
        try:
            async with self.session.get(f"{API_BASE}/admin/inventory", headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.log_test("Admin Inventory Listing", True, f"Found {len(data)} inventory items")
                    
                    # Test stock adjustment if we have inventory items
                    if data:
                        variant_id = data[0]['variant_id']
                        adjustment_data = {
                            "variant_id": variant_id,
                            "adjustment_type": "change",
                            "on_hand_change": 5,
                            "reason": "manual_adjustment",
                            "notes": "Backend testing"
                        }
                        
                        async with self.session.post(f"{API_BASE}/admin/inventory/adjust", 
                                                   json=adjustment_data, headers=headers) as adj_resp:
                            if adj_resp.status == 200:
                                self.log_test("Admin Stock Adjustment", True, "Stock adjusted successfully")
                            else:
                                error_text = await adj_resp.text()
                                self.log_test("Admin Stock Adjustment", False, 
                                            f"Status {adj_resp.status}: {error_text}")
                else:
                    error_text = await resp.text()
                    self.log_test("Admin Inventory Listing", False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Admin Inventory Management", False, f"Exception: {str(e)}")
    
    async def test_deep_link_support(self):
        """Test URL query parameter handling (simulated)"""
        print("\n🔗 Testing Deep Link Support...")
        
        # Test various filter combinations that would come from URL params
        deep_link_tests = [
            ({"colors": ["white"], "type": "normal"}, "Deep Link - Color + Type"),
            ({"categories": ["polymailers"], "sizes": ["25x35"]}, "Deep Link - Category + Size"),
            ({"price_min": 0.5, "price_max": 2.0, "in_stock_only": True}, "Deep Link - Price + Stock")
        ]
        
        for filters, test_name in deep_link_tests:
            filter_request = {
                "filters": filters,
                "page": 1,
                "limit": 20
            }
            
            try:
                async with self.session.post(f"{API_BASE}/products/filter", json=filter_request) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.log_test(test_name, True, f"Processed deep link filters successfully")
                    else:
                        error_text = await resp.text()
                        self.log_test(test_name, False, f"Status {resp.status}: {error_text}")
            except Exception as e:
                self.log_test(test_name, False, f"Exception: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("🧪 BACKEND TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        failed = len(self.test_results) - passed
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/len(self.test_results)*100):.1f}%")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['details']}")
        
        return passed, failed

async def main():
    """Run all backend tests"""
    print("🚀 Starting M Supplies Backend API Tests")
    print(f"Testing against: {API_BASE}")
    
    async with BackendTester() as tester:
        # Run all tests
        await tester.authenticate()
        await tester.test_filter_options_endpoint()
        await tester.test_product_filtering()
        await tester.test_business_rules()
        await tester.test_seed_data_verification()
        await tester.test_sorting_options()
        await tester.test_admin_inventory_management()
        await tester.test_deep_link_support()
        
        # Print summary
        passed, failed = tester.print_summary()
        
        return failed == 0

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)