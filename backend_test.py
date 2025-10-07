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

    async def test_product_update_with_variants(self):
        """Test product update functionality with variant changes"""
        print("\n🔄 Testing Product Update with Variant Changes...")
        
        if not self.admin_token:
            self.log_test("Product Update Test", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Step 1: Get a product with variants
        try:
            async with self.session.post(f"{API_BASE}/products/filter", json={"page": 1, "limit": 1}) as resp:
                if resp.status != 200:
                    self.log_test("Get Product for Update", False, f"Failed to get products: {resp.status}")
                    return
                
                data = await resp.json()
                products = data.get('products', [])
                if not products:
                    self.log_test("Get Product for Update", False, "No products found")
                    return
                
                product_id = products[0]['id']
                self.log_test("Get Product for Update", True, f"Found product ID: {product_id}")
                
        except Exception as e:
            self.log_test("Get Product for Update", False, f"Exception: {str(e)}")
            return
        
        # Step 2: Get full product details
        try:
            async with self.session.get(f"{API_BASE}/products/{product_id}") as resp:
                if resp.status != 200:
                    self.log_test("Get Product Details", False, f"Failed to get product details: {resp.status}")
                    return
                
                original_product = await resp.json()
                original_variants = original_product.get('variants', [])
                self.log_test("Get Product Details", True, f"Product has {len(original_variants)} variants")
                
        except Exception as e:
            self.log_test("Get Product Details", False, f"Exception: {str(e)}")
            return
        
        # Step 3: Create update payload with variant changes
        if len(original_variants) < 2:
            self.log_test("Variant Update Test", False, "Need at least 2 variants for testing")
            return
        
        # Remove one existing variant and add a new one
        updated_variants = original_variants[1:]  # Remove first variant
        
        # Add a new variant
        new_variant = {
            "sku": f"TEST-{product_id}-NEW",
            "attributes": {
                "width_cm": 30,
                "height_cm": 40,
                "size_code": "30x40",
                "type": "normal",
                "color": "white"
            },
            "price_tiers": [{"min_quantity": 1, "price": 1.50}],
            "stock_qty": 100,
            "on_hand": 100,
            "allocated": 0,
            "safety_stock": 10,
            "low_stock_threshold": 5
        }
        updated_variants.append(new_variant)
        
        update_payload = {
            "color": "pastel pink",  # Update product-level color
            "type": "bubble wrap",   # Update product-level type
            "variants": updated_variants
        }
        
        # Step 4: Send update request
        try:
            async with self.session.put(f"{API_BASE}/admin/products/{product_id}", 
                                      json=update_payload, headers=headers) as resp:
                if resp.status == 200:
                    updated_product = await resp.json()
                    self.log_test("Product Update Request", True, "Update request successful")
                    
                    # Verify changes
                    new_variants = updated_product.get('variants', [])
                    
                    # Check variant count changed
                    if len(new_variants) == len(original_variants):
                        self.log_test("Variant Count Change", True, f"Variant count: {len(new_variants)}")
                    else:
                        self.log_test("Variant Count Change", False, 
                                    f"Expected {len(original_variants)}, got {len(new_variants)}")
                    
                    # Check product-level fields updated
                    if updated_product.get('color') == 'pastel pink':
                        self.log_test("Product Color Update", True, "Color updated to pastel pink")
                    else:
                        self.log_test("Product Color Update", False, 
                                    f"Expected 'pastel pink', got '{updated_product.get('color')}'")
                    
                    if updated_product.get('type') == 'bubble wrap':
                        self.log_test("Product Type Update", True, "Type updated to bubble wrap")
                    else:
                        self.log_test("Product Type Update", False, 
                                    f"Expected 'bubble wrap', got '{updated_product.get('type')}'")
                    
                    # Check new variant exists
                    new_variant_found = any(v['sku'] == f"TEST-{product_id}-NEW" for v in new_variants)
                    self.log_test("New Variant Added", new_variant_found, 
                                f"New variant {'found' if new_variant_found else 'not found'}")
                    
                else:
                    error_text = await resp.text()
                    self.log_test("Product Update Request", False, f"Status {resp.status}: {error_text}")
                    return
                    
        except Exception as e:
            self.log_test("Product Update Request", False, f"Exception: {str(e)}")
            return
        
        # Step 5: Verify persistence by fetching the product again
        try:
            async with self.session.get(f"{API_BASE}/products/{product_id}") as resp:
                if resp.status == 200:
                    refetched_product = await resp.json()
                    
                    # Check if changes persisted
                    if refetched_product.get('color') == 'pastel pink':
                        self.log_test("Color Persistence", True, "Color change persisted")
                    else:
                        self.log_test("Color Persistence", False, 
                                    f"Color not persisted: {refetched_product.get('color')}")
                    
                    if refetched_product.get('type') == 'bubble wrap':
                        self.log_test("Type Persistence", True, "Type change persisted")
                    else:
                        self.log_test("Type Persistence", False, 
                                    f"Type not persisted: {refetched_product.get('type')}")
                    
                    refetched_variants = refetched_product.get('variants', [])
                    new_variant_persisted = any(v['sku'] == f"TEST-{product_id}-NEW" for v in refetched_variants)
                    self.log_test("Variant Persistence", new_variant_persisted, 
                                f"New variant {'persisted' if new_variant_persisted else 'not persisted'}")
                    
                    # Check if old variant was removed
                    if original_variants:
                        old_variant_sku = original_variants[0]['sku']
                        old_variant_removed = not any(v['sku'] == old_variant_sku for v in refetched_variants)
                        self.log_test("Variant Removal", old_variant_removed, 
                                    f"Old variant {'removed' if old_variant_removed else 'still exists'}")
                    
                else:
                    error_text = await resp.text()
                    self.log_test("Persistence Verification", False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Persistence Verification", False, f"Exception: {str(e)}")

    async def test_complete_variant_replacement(self):
        """Test replacing all variants with a completely new set"""
        print("\n🔄 Testing Complete Variant Replacement...")
        
        if not self.admin_token:
            self.log_test("Complete Variant Replacement", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get a product with multiple variants
        try:
            async with self.session.post(f"{API_BASE}/products/filter", json={"page": 1, "limit": 10}) as resp:
                if resp.status != 200:
                    self.log_test("Get Product for Replacement", False, f"Failed to get products: {resp.status}")
                    return
                
                data = await resp.json()
                products = data.get('products', [])
                
                # Find a product with multiple variants
                target_product = None
                for product in products:
                    if len(product.get('variants', [])) >= 2:
                        target_product = product
                        break
                
                if not target_product:
                    self.log_test("Get Product for Replacement", False, "No product with multiple variants found")
                    return
                
                product_id = target_product['id']
                original_variant_count = len(target_product.get('variants', []))
                self.log_test("Get Product for Replacement", True, 
                            f"Found product with {original_variant_count} variants")
                
        except Exception as e:
            self.log_test("Get Product for Replacement", False, f"Exception: {str(e)}")
            return
        
        # Create completely new set of variants
        new_variants = [
            {
                "sku": f"REPLACE-{product_id}-001",
                "attributes": {
                    "width_cm": 20,
                    "height_cm": 25,
                    "size_code": "20x25",
                    "type": "normal",
                    "color": "white"
                },
                "price_tiers": [{"min_quantity": 1, "price": 0.80}],
                "stock_qty": 50,
                "on_hand": 50,
                "allocated": 0,
                "safety_stock": 5,
                "low_stock_threshold": 10
            },
            {
                "sku": f"REPLACE-{product_id}-002",
                "attributes": {
                    "width_cm": 25,
                    "height_cm": 30,
                    "size_code": "25x30",
                    "type": "normal",
                    "color": "milktea"
                },
                "price_tiers": [{"min_quantity": 1, "price": 0.90}],
                "stock_qty": 75,
                "on_hand": 75,
                "allocated": 0,
                "safety_stock": 10,
                "low_stock_threshold": 15
            }
        ]
        
        update_payload = {
            "variants": new_variants
        }
        
        # Send replacement request
        try:
            async with self.session.put(f"{API_BASE}/admin/products/{product_id}", 
                                      json=update_payload, headers=headers) as resp:
                if resp.status == 200:
                    updated_product = await resp.json()
                    new_variant_count = len(updated_product.get('variants', []))
                    
                    if new_variant_count == 2:
                        self.log_test("Variant Replacement Count", True, f"Now has {new_variant_count} variants")
                    else:
                        self.log_test("Variant Replacement Count", False, 
                                    f"Expected 2 variants, got {new_variant_count}")
                    
                    # Check if new variants exist
                    variant_skus = [v['sku'] for v in updated_product.get('variants', [])]
                    expected_skus = [f"REPLACE-{product_id}-001", f"REPLACE-{product_id}-002"]
                    
                    all_new_variants_found = all(sku in variant_skus for sku in expected_skus)
                    self.log_test("New Variants Created", all_new_variants_found, 
                                f"New variants {'all found' if all_new_variants_found else 'missing'}")
                    
                else:
                    error_text = await resp.text()
                    self.log_test("Variant Replacement Request", False, f"Status {resp.status}: {error_text}")
                    return
                    
        except Exception as e:
            self.log_test("Variant Replacement Request", False, f"Exception: {str(e)}")
            return
        
        # Verify persistence
        try:
            async with self.session.get(f"{API_BASE}/products/{product_id}") as resp:
                if resp.status == 200:
                    refetched_product = await resp.json()
                    refetched_variants = refetched_product.get('variants', [])
                    
                    if len(refetched_variants) == 2:
                        self.log_test("Replacement Persistence", True, "Variant replacement persisted")
                    else:
                        self.log_test("Replacement Persistence", False, 
                                    f"Expected 2 variants, found {len(refetched_variants)}")
                    
                else:
                    error_text = await resp.text()
                    self.log_test("Replacement Persistence Check", False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Replacement Persistence Check", False, f"Exception: {str(e)}")

    async def test_dynamic_field_updates(self):
        """Test updating product-level dynamic color and type fields"""
        print("\n🎨 Testing Dynamic Color/Type Field Updates...")
        
        if not self.admin_token:
            self.log_test("Dynamic Field Updates", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get a product to test with
        try:
            async with self.session.post(f"{API_BASE}/products/filter", json={"page": 1, "limit": 1}) as resp:
                if resp.status != 200:
                    self.log_test("Get Product for Dynamic Fields", False, f"Failed to get products: {resp.status}")
                    return
                
                data = await resp.json()
                products = data.get('products', [])
                if not products:
                    self.log_test("Get Product for Dynamic Fields", False, "No products found")
                    return
                
                product_id = products[0]['id']
                
        except Exception as e:
            self.log_test("Get Product for Dynamic Fields", False, f"Exception: {str(e)}")
            return
        
        # Test color field update
        color_update = {"color": "champagne pink"}
        try:
            async with self.session.put(f"{API_BASE}/admin/products/{product_id}", 
                                      json=color_update, headers=headers) as resp:
                if resp.status == 200:
                    updated_product = await resp.json()
                    if updated_product.get('color') == 'champagne pink':
                        self.log_test("Dynamic Color Field Update", True, "Color updated successfully")
                    else:
                        self.log_test("Dynamic Color Field Update", False, 
                                    f"Color not updated: {updated_product.get('color')}")
                else:
                    error_text = await resp.text()
                    self.log_test("Dynamic Color Field Update", False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Dynamic Color Field Update", False, f"Exception: {str(e)}")
        
        # Test type field update
        type_update = {"type": "bubble wrap"}
        try:
            async with self.session.put(f"{API_BASE}/admin/products/{product_id}", 
                                      json=type_update, headers=headers) as resp:
                if resp.status == 200:
                    updated_product = await resp.json()
                    if updated_product.get('type') == 'bubble wrap':
                        self.log_test("Dynamic Type Field Update", True, "Type updated successfully")
                    else:
                        self.log_test("Dynamic Type Field Update", False, 
                                    f"Type not updated: {updated_product.get('type')}")
                else:
                    error_text = await resp.text()
                    self.log_test("Dynamic Type Field Update", False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Dynamic Type Field Update", False, f"Exception: {str(e)}")
        
        # Verify both changes persisted
        try:
            async with self.session.get(f"{API_BASE}/products/{product_id}") as resp:
                if resp.status == 200:
                    final_product = await resp.json()
                    
                    color_persisted = final_product.get('color') == 'champagne pink'
                    type_persisted = final_product.get('type') == 'bubble wrap'
                    
                    self.log_test("Dynamic Fields Persistence", color_persisted and type_persisted, 
                                f"Color: {final_product.get('color')}, Type: {final_product.get('type')}")
                    
                else:
                    error_text = await resp.text()
                    self.log_test("Dynamic Fields Persistence Check", False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Dynamic Fields Persistence Check", False, f"Exception: {str(e)}")

    async def test_pack_size_schema_structure(self):
        """Test product API and variant structure after pack_size schema changes"""
        print("\n📦 Testing Pack Size Schema Structure...")
        
        # Test 1: Product Listing API
        try:
            async with self.session.get(f"{API_BASE}/products") as resp:
                if resp.status == 200:
                    products = await resp.json()
                    self.log_test("Product Listing API", True, f"Retrieved {len(products)} products")
                    
                    # Check if products have variants with new structure
                    if products:
                        first_product = products[0]
                        product_id = first_product.get('id')
                        self.log_test("Product ID Structure", bool(product_id), f"Product ID: {product_id}")
                    else:
                        self.log_test("Product Listing Content", False, "No products returned")
                        return
                else:
                    error_text = await resp.text()
                    self.log_test("Product Listing API", False, f"Status {resp.status}: {error_text}")
                    return
        except Exception as e:
            self.log_test("Product Listing API", False, f"Exception: {str(e)}")
            return
        
        # Test 2: Individual Product API with variant structure
        try:
            async with self.session.get(f"{API_BASE}/products/{product_id}") as resp:
                if resp.status == 200:
                    product = await resp.json()
                    self.log_test("Individual Product API", True, f"Retrieved product: {product.get('name', 'Unknown')}")
                    
                    # Check variant structure
                    variants = product.get('variants', [])
                    if variants:
                        first_variant = variants[0]
                        attributes = first_variant.get('attributes', {})
                        
                        # Check for pack_size in attributes
                        pack_size = attributes.get('pack_size')
                        if pack_size is not None:
                            self.log_test("Pack Size in Attributes", True, f"Pack size: {pack_size}")
                        else:
                            self.log_test("Pack Size in Attributes", False, "pack_size not found in variant attributes")
                        
                        # Check other required attributes
                        required_attrs = ['width_cm', 'height_cm', 'size_code', 'type', 'color']
                        missing_attrs = [attr for attr in required_attrs if attr not in attributes]
                        
                        if not missing_attrs:
                            self.log_test("Variant Attributes Structure", True, "All required attributes present")
                        else:
                            self.log_test("Variant Attributes Structure", False, f"Missing attributes: {missing_attrs}")
                        
                        # Check price_tiers structure
                        price_tiers = first_variant.get('price_tiers', [])
                        if price_tiers and isinstance(price_tiers, list):
                            first_tier = price_tiers[0]
                            if 'min_quantity' in first_tier and 'price' in first_tier:
                                self.log_test("Price Tiers Structure", True, f"Price tier: {first_tier}")
                            else:
                                self.log_test("Price Tiers Structure", False, "Invalid price tier structure")
                        else:
                            self.log_test("Price Tiers Structure", False, "No price tiers found")
                        
                        # Check stock quantities (on_hand vs stock_qty)
                        on_hand = first_variant.get('on_hand')
                        stock_qty = first_variant.get('stock_qty')
                        
                        if on_hand is not None:
                            self.log_test("On Hand Stock Field", True, f"on_hand: {on_hand}")
                        else:
                            self.log_test("On Hand Stock Field", False, "on_hand field missing")
                        
                        if stock_qty is not None:
                            self.log_test("Legacy Stock Field", True, f"stock_qty: {stock_qty}")
                        else:
                            self.log_test("Legacy Stock Field", False, "stock_qty field missing")
                        
                    else:
                        self.log_test("Product Variants", False, "No variants found in product")
                        
                else:
                    error_text = await resp.text()
                    if resp.status == 404:
                        self.log_test("Individual Product API", False, f"Product not found - this matches the reported issue")
                    else:
                        self.log_test("Individual Product API", False, f"Status {resp.status}: {error_text}")
                    return
                    
        except Exception as e:
            self.log_test("Individual Product API", False, f"Exception: {str(e)}")
            return
        
        # Test 3: Customer Product Page Data (simulate frontend access)
        try:
            # Test without authentication (customer access)
            async with self.session.get(f"{API_BASE}/products/{product_id}") as resp:
                if resp.status == 200:
                    customer_product = await resp.json()
                    self.log_test("Customer Product Access", True, "Customer can access product details")
                    
                    # Verify variant structure matches frontend expectations
                    variants = customer_product.get('variants', [])
                    if variants:
                        variant = variants[0]
                        attributes = variant.get('attributes', {})
                        
                        # Check if pack_size is accessible for frontend
                        pack_size = attributes.get('pack_size')
                        if pack_size:
                            self.log_test("Frontend Pack Size Access", True, f"Pack size accessible: {pack_size}")
                        else:
                            self.log_test("Frontend Pack Size Access", False, "Pack size not accessible to frontend")
                        
                        # Check if all necessary data is present for product display
                        essential_fields = ['price_tiers', 'attributes']
                        missing_fields = [field for field in essential_fields if field not in variant]
                        
                        if not missing_fields:
                            self.log_test("Frontend Data Completeness", True, "All essential variant data present")
                        else:
                            self.log_test("Frontend Data Completeness", False, f"Missing fields: {missing_fields}")
                    
                else:
                    error_text = await resp.text()
                    self.log_test("Customer Product Access", False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Customer Product Access", False, f"Exception: {str(e)}")
        
        # Test 4: Verify pack_size in filtered products
        try:
            filter_request = {"page": 1, "limit": 5}
            async with self.session.post(f"{API_BASE}/products/filter", json=filter_request) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    products = data.get('products', [])
                    
                    if products:
                        # Check first product's variants for pack_size
                        first_product = products[0]
                        variants = first_product.get('variants', [])
                        
                        if variants:
                            attributes = variants[0].get('attributes', {})
                            pack_size = attributes.get('pack_size')
                            
                            if pack_size is not None:
                                self.log_test("Filtered Products Pack Size", True, f"Pack size in filtered results: {pack_size}")
                            else:
                                self.log_test("Filtered Products Pack Size", False, "Pack size missing in filtered results")
                        else:
                            self.log_test("Filtered Products Variants", False, "No variants in filtered products")
                    else:
                        self.log_test("Filtered Products Content", False, "No products in filter results")
                        
                else:
                    error_text = await resp.text()
                    self.log_test("Filtered Products API", False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Filtered Products API", False, f"Exception: {str(e)}")
    
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
        
        # Run new product update tests
        await tester.test_product_update_with_variants()
        await tester.test_complete_variant_replacement()
        await tester.test_dynamic_field_updates()
        
        # Print summary
        passed, failed = tester.print_summary()
        
        return failed == 0

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)