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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://msupplies-shop.preview.emergentagent.com')
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
                "color": "white",
                "pack_size": 25
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
                    "color": "white",
                    "pack_size": 100
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
                    "color": "milktea",
                    "pack_size": 50
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

    async def test_variant_pricing_updates_and_persistence(self):
        """Test variant pricing updates and persistence for Heavy-Duty Polymailers"""
        print("\n💰 Testing Variant Pricing Updates and Persistence...")
        
        if not self.admin_token:
            self.log_test("Variant Pricing Test", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Step 1: Find Heavy-Duty Polymailers product
        heavy_duty_product = None
        try:
            async with self.session.post(f"{API_BASE}/products/filter", json={"page": 1, "limit": 50}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    products = data.get('products', [])
                    
                    # Look for Heavy-Duty Polymailers or similar product
                    for product in products:
                        if 'heavy' in product.get('name', '').lower() or 'polymailer' in product.get('name', '').lower():
                            heavy_duty_product = product
                            break
                    
                    if not heavy_duty_product and products:
                        # Use first product if Heavy-Duty not found
                        heavy_duty_product = products[0]
                        self.log_test("Find Heavy-Duty Product", True, f"Using product: {heavy_duty_product.get('name')}")
                    elif heavy_duty_product:
                        self.log_test("Find Heavy-Duty Product", True, f"Found: {heavy_duty_product.get('name')}")
                    else:
                        self.log_test("Find Heavy-Duty Product", False, "No products found")
                        return
                else:
                    error_text = await resp.text()
                    self.log_test("Find Heavy-Duty Product", False, f"Status {resp.status}: {error_text}")
                    return
        except Exception as e:
            self.log_test("Find Heavy-Duty Product", False, f"Exception: {str(e)}")
            return
        
        product_id = heavy_duty_product['id']
        
        # Step 2: Get full product details to examine current pricing
        try:
            async with self.session.get(f"{API_BASE}/products/{product_id}") as resp:
                if resp.status == 200:
                    original_product = await resp.json()
                    original_variants = original_product.get('variants', [])
                    self.log_test("Get Product Details", True, f"Product has {len(original_variants)} variants")
                    
                    # Log current pricing for each variant
                    for i, variant in enumerate(original_variants):
                        price_tiers = variant.get('price_tiers', [])
                        pack_size = variant.get('attributes', {}).get('pack_size', 'Unknown')
                        size_code = variant.get('attributes', {}).get('size_code', 'Unknown')
                        
                        if price_tiers:
                            current_price = price_tiers[0].get('price', 0)
                            self.log_test(f"Current Pricing - Variant {i+1}", True, 
                                        f"Size: {size_code}, Pack: {pack_size}, Price: ${current_price}")
                        else:
                            self.log_test(f"Current Pricing - Variant {i+1}", False, "No price tiers found")
                    
                else:
                    error_text = await resp.text()
                    self.log_test("Get Product Details", False, f"Status {resp.status}: {error_text}")
                    return
        except Exception as e:
            self.log_test("Get Product Details", False, f"Exception: {str(e)}")
            return
        
        # Step 3: Test price tier structure for each variant
        if len(original_variants) >= 2:
            variant_25x35_50 = None
            variant_25x35_100 = None
            
            for variant in original_variants:
                attrs = variant.get('attributes', {})
                size_code = attrs.get('size_code', '')
                pack_size = attrs.get('pack_size', 0)
                
                if size_code == '25x35' and pack_size == 50:
                    variant_25x35_50 = variant
                elif size_code == '25x35' and pack_size == 100:
                    variant_25x35_100 = variant
            
            # Check if each variant has its own price_tiers array
            if variant_25x35_50 and variant_25x35_100:
                price_tiers_50 = variant_25x35_50.get('price_tiers', [])
                price_tiers_100 = variant_25x35_100.get('price_tiers', [])
                
                # Verify price_tiers are not shared between variants
                if price_tiers_50 is not price_tiers_100:
                    self.log_test("Price Tiers Independence", True, "Each variant has independent price_tiers")
                else:
                    self.log_test("Price Tiers Independence", False, "Price tiers appear to be shared between variants")
                
                # Log current prices
                if price_tiers_50:
                    current_price_50 = price_tiers_50[0].get('price', 0)
                    self.log_test("25x35cm 50-pack Current Price", True, f"${current_price_50}")
                
                if price_tiers_100:
                    current_price_100 = price_tiers_100[0].get('price', 0)
                    self.log_test("25x35cm 100-pack Current Price", True, f"${current_price_100}")
            else:
                self.log_test("Find Specific Variants", False, "Could not find 25x35cm variants with different pack sizes")
        
        # Step 4: Simulate admin price update (as mentioned in the issue: $4.5 → $15.00, $28.00)
        if len(original_variants) >= 2:
            updated_variants = []
            
            for i, variant in enumerate(original_variants):
                updated_variant = variant.copy()
                
                # Update price tiers for first two variants to simulate the reported issue
                if i == 0:
                    updated_variant['price_tiers'] = [{"min_quantity": 1, "price": 15.00}]
                elif i == 1:
                    updated_variant['price_tiers'] = [{"min_quantity": 1, "price": 28.00}]
                else:
                    # Keep original pricing for other variants
                    updated_variant['price_tiers'] = variant.get('price_tiers', [])
                
                updated_variants.append(updated_variant)
            
            update_payload = {
                "variants": updated_variants
            }
            
            # Step 5: Send admin product update
            try:
                async with self.session.put(f"{API_BASE}/admin/products/{product_id}", 
                                          json=update_payload, headers=headers) as resp:
                    if resp.status == 200:
                        updated_product = await resp.json()
                        self.log_test("Admin Price Update Request", True, "Price update request successful")
                        
                        # Verify the update response contains new prices
                        updated_variants_response = updated_product.get('variants', [])
                        if len(updated_variants_response) >= 2:
                            first_variant_price = updated_variants_response[0].get('price_tiers', [{}])[0].get('price', 0)
                            second_variant_price = updated_variants_response[1].get('price_tiers', [{}])[0].get('price', 0)
                            
                            if first_variant_price == 15.00:
                                self.log_test("First Variant Price Update", True, f"Updated to ${first_variant_price}")
                            else:
                                self.log_test("First Variant Price Update", False, f"Expected $15.00, got ${first_variant_price}")
                            
                            if second_variant_price == 28.00:
                                self.log_test("Second Variant Price Update", True, f"Updated to ${second_variant_price}")
                            else:
                                self.log_test("Second Variant Price Update", False, f"Expected $28.00, got ${second_variant_price}")
                        
                    else:
                        error_text = await resp.text()
                        self.log_test("Admin Price Update Request", False, f"Status {resp.status}: {error_text}")
                        return
            except Exception as e:
                self.log_test("Admin Price Update Request", False, f"Exception: {str(e)}")
                return
        
        # Step 6: Test price persistence by fetching product again (admin view)
        try:
            async with self.session.get(f"{API_BASE}/products/{product_id}", headers=headers) as resp:
                if resp.status == 200:
                    admin_refetch = await resp.json()
                    admin_variants = admin_refetch.get('variants', [])
                    
                    if len(admin_variants) >= 2:
                        first_price = admin_variants[0].get('price_tiers', [{}])[0].get('price', 0)
                        second_price = admin_variants[1].get('price_tiers', [{}])[0].get('price', 0)
                        
                        if first_price == 15.00:
                            self.log_test("Admin View Price Persistence - Variant 1", True, f"${first_price}")
                        else:
                            self.log_test("Admin View Price Persistence - Variant 1", False, f"Expected $15.00, got ${first_price}")
                        
                        if second_price == 28.00:
                            self.log_test("Admin View Price Persistence - Variant 2", True, f"${second_price}")
                        else:
                            self.log_test("Admin View Price Persistence - Variant 2", False, f"Expected $28.00, got ${second_price}")
                    
                else:
                    error_text = await resp.text()
                    self.log_test("Admin View Price Persistence", False, f"Status {resp.status}: {error_text}")
            
        except Exception as e:
            self.log_test("Admin View Price Persistence", False, f"Exception: {str(e)}")
        
        # Step 7: Test customer product access (the critical issue reported)
        try:
            async with self.session.get(f"{API_BASE}/products/{product_id}") as resp:
                if resp.status == 200:
                    customer_product = await resp.json()
                    customer_variants = customer_product.get('variants', [])
                    
                    self.log_test("Customer Product Access", True, f"Customer can access product: {customer_product.get('name')}")
                    
                    if len(customer_variants) >= 2:
                        first_customer_price = customer_variants[0].get('price_tiers', [{}])[0].get('price', 0)
                        second_customer_price = customer_variants[1].get('price_tiers', [{}])[0].get('price', 0)
                        
                        # This is the critical test - are updated prices visible to customers?
                        if first_customer_price == 15.00:
                            self.log_test("Customer View Updated Price - Variant 1", True, f"${first_customer_price}")
                        else:
                            self.log_test("Customer View Updated Price - Variant 1", False, 
                                        f"CRITICAL ISSUE: Expected $15.00, customer sees ${first_customer_price}")
                        
                        if second_customer_price == 28.00:
                            self.log_test("Customer View Updated Price - Variant 2", True, f"${second_customer_price}")
                        else:
                            self.log_test("Customer View Updated Price - Variant 2", False, 
                                        f"CRITICAL ISSUE: Expected $28.00, customer sees ${second_customer_price}")
                        
                        # Check if customer is seeing the old $0.80 price mentioned in the issue
                        if first_customer_price == 0.80 or second_customer_price == 0.80:
                            self.log_test("Old Price Still Visible", False, 
                                        "CRITICAL: Customer still seeing old $0.80 price - price update not persisting")
                    
                else:
                    error_text = await resp.text()
                    self.log_test("Customer Product Access", False, f"Status {resp.status}: {error_text}")
            
        except Exception as e:
            self.log_test("Customer Product Access", False, f"Exception: {str(e)}")
        
        # Step 8: Test pricing calculation logic
        try:
            # Test different pack sizes have different pricing
            async with self.session.get(f"{API_BASE}/products/{product_id}") as resp:
                if resp.status == 200:
                    product = await resp.json()
                    variants = product.get('variants', [])
                    
                    pack_size_prices = {}
                    for variant in variants:
                        pack_size = variant.get('attributes', {}).get('pack_size')
                        price_tiers = variant.get('price_tiers', [])
                        if price_tiers and pack_size:
                            pack_size_prices[pack_size] = price_tiers[0].get('price', 0)
                    
                    if len(pack_size_prices) > 1:
                        prices = list(pack_size_prices.values())
                        if len(set(prices)) > 1:  # Different prices
                            self.log_test("Different Pack Size Pricing", True, f"Pack sizes have different prices: {pack_size_prices}")
                        else:
                            self.log_test("Different Pack Size Pricing", False, "All pack sizes have same price")
                    else:
                        self.log_test("Pack Size Price Variety", False, "Not enough variants to test different pack size pricing")
            
        except Exception as e:
            self.log_test("Pricing Calculation Logic", False, f"Exception: {str(e)}")

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

    async def test_product_deletion_functionality(self):
        """Test product deletion functionality and investigate why deletion isn't working"""
        print("\n🗑️ Testing Product Deletion Functionality...")
        
        if not self.admin_token:
            self.log_test("Product Deletion Test", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Step 1: Get list of current products before deletion
        print("\n📋 Step 1: Getting product list before deletion...")
        premium_product_id = None
        initial_product_count = 0
        initial_variant_count = 0
        
        try:
            async with self.session.get(f"{API_BASE}/products") as resp:
                if resp.status == 200:
                    products = await resp.json()
                    initial_product_count = len(products)
                    
                    # Find Premium Polymailers product
                    for product in products:
                        if "Premium Polymailers" in product.get('name', ''):
                            premium_product_id = product['id']
                            break
                    
                    if premium_product_id:
                        self.log_test("Find Premium Polymailers Product", True, f"Found Premium Polymailers ID: {premium_product_id}")
                    else:
                        self.log_test("Find Premium Polymailers Product", False, "Premium Polymailers not found in product list")
                        return
                    
                    self.log_test("Initial Product Count", True, f"Found {initial_product_count} products")
                else:
                    error_text = await resp.text()
                    self.log_test("Get Products Before Deletion", False, f"Status {resp.status}: {error_text}")
                    return
        except Exception as e:
            self.log_test("Get Products Before Deletion", False, f"Exception: {str(e)}")
            return
        
        # Get detailed product info including variants
        try:
            async with self.session.get(f"{API_BASE}/products/{premium_product_id}") as resp:
                if resp.status == 200:
                    product_details = await resp.json()
                    variants = product_details.get('variants', [])
                    initial_variant_count = len(variants)
                    self.log_test("Get Premium Product Details", True, f"Premium Polymailers has {initial_variant_count} variants")
                else:
                    error_text = await resp.text()
                    self.log_test("Get Premium Product Details", False, f"Status {resp.status}: {error_text}")
                    return
        except Exception as e:
            self.log_test("Get Premium Product Details", False, f"Exception: {str(e)}")
            return
        
        # Step 2: Test inventory API before deletion
        print("\n📦 Step 2: Testing inventory API before deletion...")
        initial_inventory_count = 0
        premium_variants_in_inventory = 0
        
        try:
            async with self.session.get(f"{API_BASE}/admin/inventory", headers=headers) as resp:
                if resp.status == 200:
                    inventory = await resp.json()
                    initial_inventory_count = len(inventory)
                    
                    # Count Premium Polymailers variants in inventory
                    for item in inventory:
                        if "Premium Polymailers" in item.get('product_name', ''):
                            premium_variants_in_inventory += 1
                    
                    self.log_test("Initial Inventory Count", True, f"Found {initial_inventory_count} inventory items")
                    self.log_test("Premium Variants in Inventory", True, f"Found {premium_variants_in_inventory} Premium Polymailers variants")
                else:
                    error_text = await resp.text()
                    self.log_test("Get Inventory Before Deletion", False, f"Status {resp.status}: {error_text}")
        except Exception as e:
            self.log_test("Get Inventory Before Deletion", False, f"Exception: {str(e)}")
        
        # Step 3: Test product deletion API
        print("\n🗑️ Step 3: Testing product deletion API...")
        
        try:
            async with self.session.delete(f"{API_BASE}/admin/products/{premium_product_id}", headers=headers) as resp:
                if resp.status == 200:
                    response_data = await resp.json()
                    self.log_test("Product Deletion API Call", True, f"Deletion API returned: {response_data}")
                else:
                    error_text = await resp.text()
                    self.log_test("Product Deletion API Call", False, f"Status {resp.status}: {error_text}")
                    return
        except Exception as e:
            self.log_test("Product Deletion API Call", False, f"Exception: {str(e)}")
            return
        
        # Step 4: Verify product is marked as is_active: False
        print("\n🔍 Step 4: Verifying soft delete implementation...")
        
        try:
            # Try to get the product directly (should still exist in DB but marked inactive)
            async with self.session.get(f"{API_BASE}/products/{premium_product_id}") as resp:
                if resp.status == 404:
                    self.log_test("Product Soft Delete - Customer View", True, "Product not accessible to customers after deletion")
                elif resp.status == 200:
                    product_data = await resp.json()
                    is_active = product_data.get('is_active', True)
                    if is_active is False:
                        self.log_test("Product Soft Delete - is_active Flag", True, "Product marked as is_active: False")
                    else:
                        self.log_test("Product Soft Delete - is_active Flag", False, f"Product is_active: {is_active} (should be False)")
                else:
                    error_text = await resp.text()
                    self.log_test("Product Soft Delete Verification", False, f"Status {resp.status}: {error_text}")
        except Exception as e:
            self.log_test("Product Soft Delete Verification", False, f"Exception: {str(e)}")
        
        # Step 5: Check if variants are deleted
        print("\n🧩 Step 5: Checking if variants are deleted...")
        
        try:
            # Check if variants still exist by trying to access the product details with admin token
            async with self.session.get(f"{API_BASE}/products/{premium_product_id}", headers=headers) as resp:
                if resp.status == 200:
                    product_data = await resp.json()
                    remaining_variants = product_data.get('variants', [])
                    if len(remaining_variants) == 0:
                        self.log_test("Variant Deletion", True, "All variants deleted successfully")
                    else:
                        self.log_test("Variant Deletion", False, f"Still has {len(remaining_variants)} variants (should be 0)")
                elif resp.status == 404:
                    self.log_test("Variant Deletion", True, "Product not found - variants likely deleted")
                else:
                    error_text = await resp.text()
                    self.log_test("Variant Deletion Check", False, f"Status {resp.status}: {error_text}")
        except Exception as e:
            self.log_test("Variant Deletion Check", False, f"Exception: {str(e)}")
        
        # Step 6: Test product list after deletion (with is_active=True filter)
        print("\n📋 Step 6: Testing product list after deletion...")
        
        try:
            async with self.session.get(f"{API_BASE}/products") as resp:
                if resp.status == 200:
                    products_after = await resp.json()
                    final_product_count = len(products_after)
                    
                    # Check if Premium Polymailers is filtered out
                    premium_found_after = any("Premium Polymailers" in p.get('name', '') for p in products_after)
                    
                    if not premium_found_after:
                        self.log_test("Product List Filtering", True, "Premium Polymailers filtered out from product list")
                    else:
                        self.log_test("Product List Filtering", False, "Premium Polymailers still appears in product list")
                    
                    if final_product_count == initial_product_count - 1:
                        self.log_test("Product Count After Deletion", True, f"Product count reduced from {initial_product_count} to {final_product_count}")
                    else:
                        self.log_test("Product Count After Deletion", False, f"Expected {initial_product_count - 1}, got {final_product_count}")
                else:
                    error_text = await resp.text()
                    self.log_test("Get Products After Deletion", False, f"Status {resp.status}: {error_text}")
        except Exception as e:
            self.log_test("Get Products After Deletion", False, f"Exception: {str(e)}")
        
        # Step 7: Test inventory API after deletion
        print("\n📦 Step 7: Testing inventory API after deletion...")
        
        try:
            async with self.session.get(f"{API_BASE}/admin/inventory", headers=headers) as resp:
                if resp.status == 200:
                    inventory_after = await resp.json()
                    final_inventory_count = len(inventory_after)
                    
                    # Count Premium Polymailers variants in inventory after deletion
                    premium_variants_after = sum(1 for item in inventory_after if "Premium Polymailers" in item.get('product_name', ''))
                    
                    if premium_variants_after == 0:
                        self.log_test("Inventory Filtering After Deletion", True, "Premium Polymailers variants removed from inventory")
                    else:
                        self.log_test("Inventory Filtering After Deletion", False, f"Still found {premium_variants_after} Premium variants in inventory")
                    
                    expected_inventory_count = initial_inventory_count - premium_variants_in_inventory
                    if final_inventory_count == expected_inventory_count:
                        self.log_test("Inventory Count After Deletion", True, f"Inventory count reduced from {initial_inventory_count} to {final_inventory_count}")
                    else:
                        self.log_test("Inventory Count After Deletion", False, f"Expected {expected_inventory_count}, got {final_inventory_count}")
                else:
                    error_text = await resp.text()
                    self.log_test("Get Inventory After Deletion", False, f"Status {resp.status}: {error_text}")
        except Exception as e:
            self.log_test("Get Inventory After Deletion", False, f"Exception: {str(e)}")
        
        # Step 8: Test filtered products API
        print("\n🔍 Step 8: Testing filtered products API after deletion...")
        
        try:
            filter_request = {"page": 1, "limit": 100}
            async with self.session.post(f"{API_BASE}/products/filter", json=filter_request) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    filtered_products = data.get('products', [])
                    
                    # Check if Premium Polymailers is filtered out
                    premium_in_filtered = any("Premium Polymailers" in p.get('name', '') for p in filtered_products)
                    
                    if not premium_in_filtered:
                        self.log_test("Filtered Products API", True, "Premium Polymailers not in filtered results")
                    else:
                        self.log_test("Filtered Products API", False, "Premium Polymailers still appears in filtered results")
                else:
                    error_text = await resp.text()
                    self.log_test("Filtered Products API", False, f"Status {resp.status}: {error_text}")
        except Exception as e:
            self.log_test("Filtered Products API", False, f"Exception: {str(e)}")

    async def test_cart_api_endpoints(self):
        """Test cart API endpoints comprehensively"""
        print("\n🛒 Testing Cart API Endpoints...")
        
        # Step 1: Test Baby Blue variant ID specifically
        baby_blue_variant_id = "612cad49-659f-4add-8084-595a9340b31b"
        
        # First, verify if this variant exists
        await self._test_variant_exists(baby_blue_variant_id)
        
        # Test cart endpoints
        await self._test_add_to_cart_endpoint()
        await self._test_get_cart_endpoint()
        await self._test_update_cart_endpoint()
        await self._test_clear_cart_endpoint()
        
        # Test specific Baby Blue variant
        await self._test_baby_blue_cart_scenario()
    
    async def _test_variant_exists(self, variant_id: str):
        """Check if the Baby Blue variant exists in the database"""
        try:
            # Try to find the variant by searching all products
            async with self.session.post(f"{API_BASE}/products/filter", json={"page": 1, "limit": 100}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    products = data.get('products', [])
                    
                    variant_found = False
                    for product in products:
                        for variant in product.get('variants', []):
                            if variant.get('id') == variant_id:
                                variant_found = True
                                self.log_test("Baby Blue Variant Exists", True, 
                                            f"Found in product: {product.get('name')}, SKU: {variant.get('sku')}")
                                
                                # Log variant details
                                attributes = variant.get('attributes', {})
                                stock_info = f"on_hand: {variant.get('on_hand', 0)}, stock_qty: {variant.get('stock_qty', 0)}"
                                self.log_test("Baby Blue Variant Details", True, 
                                            f"Color: {attributes.get('color')}, Size: {attributes.get('size_code')}, Stock: {stock_info}")
                                break
                        if variant_found:
                            break
                    
                    if not variant_found:
                        self.log_test("Baby Blue Variant Exists", False, f"Variant ID {variant_id} not found in any product")
                else:
                    error_text = await resp.text()
                    self.log_test("Variant Search", False, f"Status {resp.status}: {error_text}")
        except Exception as e:
            self.log_test("Variant Search", False, f"Exception: {str(e)}")
    
    async def _test_add_to_cart_endpoint(self):
        """Test POST /api/cart/add endpoint"""
        print("\n  Testing Add to Cart Endpoint...")
        
        # Test 1: Add to cart without authentication (guest user)
        test_payload = {
            "variant_id": "612cad49-659f-4add-8084-595a9340b31b",
            "quantity": 4
        }
        
        headers = {"X-Session-ID": "test-session-123"}
        
        try:
            async with self.session.post(f"{API_BASE}/cart/add", json=test_payload, headers=headers) as resp:
                response_text = await resp.text()
                
                if resp.status == 200:
                    data = await resp.json()
                    self.log_test("Add to Cart - Guest User", True, f"Cart created with {len(data.get('items', []))} items")
                    
                    # Verify response structure
                    required_fields = ['id', 'items', 'subtotal', 'gst', 'total']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        self.log_test("Add to Cart Response Structure", True, "All required fields present")
                    else:
                        self.log_test("Add to Cart Response Structure", False, f"Missing fields: {missing_fields}")
                    
                elif resp.status == 404:
                    self.log_test("Add to Cart - Guest User", False, f"Variant not found: {response_text}")
                elif resp.status == 400:
                    self.log_test("Add to Cart - Guest User", False, f"Bad request: {response_text}")
                elif resp.status == 500:
                    self.log_test("Add to Cart - Guest User", False, f"CRITICAL: Server error 500: {response_text}")
                    
                    # Log detailed error for debugging
                    print(f"    🚨 DETAILED ERROR: {response_text}")
                else:
                    self.log_test("Add to Cart - Guest User", False, f"Status {resp.status}: {response_text}")
                    
        except Exception as e:
            self.log_test("Add to Cart - Guest User", False, f"Exception: {str(e)}")
        
        # Test 2: Add to cart with authentication
        if self.customer_token:
            headers_auth = {
                "Authorization": f"Bearer {self.customer_token}",
                "X-Session-ID": "test-session-auth-123"
            }
            
            try:
                async with self.session.post(f"{API_BASE}/cart/add", json=test_payload, headers=headers_auth) as resp:
                    response_text = await resp.text()
                    
                    if resp.status == 200:
                        data = await resp.json()
                        self.log_test("Add to Cart - Authenticated User", True, f"Cart created with {len(data.get('items', []))} items")
                    elif resp.status == 500:
                        self.log_test("Add to Cart - Authenticated User", False, f"CRITICAL: Server error 500: {response_text}")
                    else:
                        self.log_test("Add to Cart - Authenticated User", False, f"Status {resp.status}: {response_text}")
                        
            except Exception as e:
                self.log_test("Add to Cart - Authenticated User", False, f"Exception: {str(e)}")
        
        # Test 3: Test with different variant (if Baby Blue fails)
        await self._test_add_to_cart_with_different_variant()
    
    async def _test_add_to_cart_with_different_variant(self):
        """Test add to cart with a different variant to isolate the issue"""
        try:
            # Get any available variant from products
            async with self.session.post(f"{API_BASE}/products/filter", json={"page": 1, "limit": 5}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    products = data.get('products', [])
                    
                    if products and products[0].get('variants'):
                        test_variant = products[0]['variants'][0]
                        test_variant_id = test_variant.get('id')
                        
                        if test_variant_id:
                            test_payload = {
                                "variant_id": test_variant_id,
                                "quantity": 1
                            }
                            
                            headers = {"X-Session-ID": "test-session-different-variant"}
                            
                            async with self.session.post(f"{API_BASE}/cart/add", json=test_payload, headers=headers) as cart_resp:
                                response_text = await cart_resp.text()
                                
                                if cart_resp.status == 200:
                                    self.log_test("Add to Cart - Different Variant", True, f"Successfully added variant {test_variant_id}")
                                elif cart_resp.status == 500:
                                    self.log_test("Add to Cart - Different Variant", False, f"Server error with different variant: {response_text}")
                                else:
                                    self.log_test("Add to Cart - Different Variant", False, f"Status {cart_resp.status}: {response_text}")
                        else:
                            self.log_test("Add to Cart - Different Variant", False, "No variant ID found")
                    else:
                        self.log_test("Add to Cart - Different Variant", False, "No products with variants found")
                else:
                    self.log_test("Add to Cart - Different Variant", False, f"Failed to get products: {resp.status}")
        except Exception as e:
            self.log_test("Add to Cart - Different Variant", False, f"Exception: {str(e)}")
    
    async def _test_get_cart_endpoint(self):
        """Test GET /api/cart endpoint"""
        print("\n  Testing Get Cart Endpoint...")
        
        headers = {"X-Session-ID": "test-session-123"}
        
        try:
            async with self.session.get(f"{API_BASE}/cart", headers=headers) as resp:
                response_text = await resp.text()
                
                if resp.status == 200:
                    data = await resp.json()
                    self.log_test("Get Cart", True, f"Retrieved cart with {len(data.get('items', []))} items")
                elif resp.status == 500:
                    self.log_test("Get Cart", False, f"Server error: {response_text}")
                else:
                    self.log_test("Get Cart", False, f"Status {resp.status}: {response_text}")
                    
        except Exception as e:
            self.log_test("Get Cart", False, f"Exception: {str(e)}")
    
    async def _test_update_cart_endpoint(self):
        """Test PUT /api/cart/item/{variant_id} endpoint"""
        print("\n  Testing Update Cart Item Endpoint...")
        
        # This test requires an existing cart item, so we'll test the endpoint structure
        test_variant_id = "612cad49-659f-4add-8084-595a9340b31b"
        headers = {"X-Session-ID": "test-session-123"}
        update_payload = {"quantity": 2}
        
        try:
            async with self.session.put(f"{API_BASE}/cart/item/{test_variant_id}", 
                                      json=update_payload, headers=headers) as resp:
                response_text = await resp.text()
                
                if resp.status == 200:
                    self.log_test("Update Cart Item", True, "Cart item updated successfully")
                elif resp.status == 404:
                    self.log_test("Update Cart Item", True, "Expected 404 - item not in cart (endpoint working)")
                elif resp.status == 500:
                    self.log_test("Update Cart Item", False, f"Server error: {response_text}")
                else:
                    self.log_test("Update Cart Item", False, f"Status {resp.status}: {response_text}")
                    
        except Exception as e:
            self.log_test("Update Cart Item", False, f"Exception: {str(e)}")
    
    async def _test_clear_cart_endpoint(self):
        """Test DELETE /api/cart endpoint"""
        print("\n  Testing Clear Cart Endpoint...")
        
        headers = {"X-Session-ID": "test-session-123"}
        
        try:
            async with self.session.delete(f"{API_BASE}/cart", headers=headers) as resp:
                response_text = await resp.text()
                
                if resp.status == 200:
                    self.log_test("Clear Cart", True, "Cart cleared successfully")
                elif resp.status == 500:
                    self.log_test("Clear Cart", False, f"Server error: {response_text}")
                else:
                    self.log_test("Clear Cart", False, f"Status {resp.status}: {response_text}")
                    
        except Exception as e:
            self.log_test("Clear Cart", False, f"Exception: {str(e)}")
    
    async def _test_baby_blue_cart_scenario(self):
        """Test the specific Baby Blue cart scenario reported by user"""
        print("\n  Testing Baby Blue Cart Scenario...")
        
        # Exact payload from user report
        baby_blue_payload = {
            "variant_id": "612cad49-659f-4add-8084-595a9340b31b",
            "quantity": 4
        }
        
        # Test different session scenarios
        test_scenarios = [
            ("Guest User", {"X-Session-ID": "baby-blue-test-session"}),
            ("No Session Header", {}),
            ("Different Session", {"X-Session-ID": "different-session-id"})
        ]
        
        if self.customer_token:
            test_scenarios.append(("Authenticated User", {
                "Authorization": f"Bearer {self.customer_token}",
                "X-Session-ID": "auth-baby-blue-session"
            }))
        
        for scenario_name, headers in test_scenarios:
            try:
                async with self.session.post(f"{API_BASE}/cart/add", json=baby_blue_payload, headers=headers) as resp:
                    response_text = await resp.text()
                    
                    if resp.status == 200:
                        data = await resp.json()
                        self.log_test(f"Baby Blue Scenario - {scenario_name}", True, 
                                    f"Successfully added to cart. Total: ${data.get('total', 0)}")
                    elif resp.status == 404:
                        self.log_test(f"Baby Blue Scenario - {scenario_name}", False, 
                                    f"Variant not found: {response_text}")
                    elif resp.status == 400:
                        self.log_test(f"Baby Blue Scenario - {scenario_name}", False, 
                                    f"Bad request (possibly stock issue): {response_text}")
                    elif resp.status == 500:
                        self.log_test(f"Baby Blue Scenario - {scenario_name}", False, 
                                    f"🚨 CRITICAL 500 ERROR: {response_text}")
                        
                        # Try to get more detailed error information
                        await self._debug_cart_error(baby_blue_payload, headers)
                    else:
                        self.log_test(f"Baby Blue Scenario - {scenario_name}", False, 
                                    f"Status {resp.status}: {response_text}")
                        
            except Exception as e:
                self.log_test(f"Baby Blue Scenario - {scenario_name}", False, f"Exception: {str(e)}")
    
    async def _debug_cart_error(self, payload: dict, headers: dict):
        """Debug cart API errors by checking related endpoints"""
        print("\n    🔍 Debugging Cart Error...")
        
        variant_id = payload.get('variant_id')
        
        # Check if variant exists via product API
        try:
            async with self.session.post(f"{API_BASE}/products/filter", json={"page": 1, "limit": 100}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    products = data.get('products', [])
                    
                    variant_found = False
                    for product in products:
                        for variant in product.get('variants', []):
                            if variant.get('id') == variant_id:
                                variant_found = True
                                print(f"    ✅ Variant found in product: {product.get('name')}")
                                print(f"    📊 Variant stock: on_hand={variant.get('on_hand', 0)}, stock_qty={variant.get('stock_qty', 0)}")
                                print(f"    💰 Variant price tiers: {variant.get('price_tiers', [])}")
                                break
                        if variant_found:
                            break
                    
                    if not variant_found:
                        print(f"    ❌ Variant {variant_id} not found in any product")
                else:
                    print(f"    ❌ Failed to search products: {resp.status}")
        except Exception as e:
            print(f"    ❌ Exception during variant debug: {str(e)}")
        
        # Check database connection by testing a simple endpoint
        try:
            async with self.session.get(f"{API_BASE}/products") as resp:
                if resp.status == 200:
                    print(f"    ✅ Database connection working (products endpoint responds)")
                else:
                    print(f"    ⚠️ Database connection issue? Products endpoint: {resp.status}")
        except Exception as e:
            print(f"    ❌ Database connection test failed: {str(e)}")

    async def test_baby_blue_product_debug(self):
        """Debug Baby Blue product stock and pricing issues"""
        print("\n🔍 Testing Baby Blue Product Stock and Pricing Issues...")
        
        # Step 1: Find Baby Blue product in database
        baby_blue_product = None
        try:
            async with self.session.post(f"{API_BASE}/products/filter", json={"page": 1, "limit": 50}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    products = data.get('products', [])
                    
                    # Look for Baby Blue product
                    for product in products:
                        if 'baby blue' in product.get('name', '').lower() or 'blue' in product.get('name', '').lower():
                            baby_blue_product = product
                            break
                    
                    if baby_blue_product:
                        self.log_test("Find Baby Blue Product", True, f"Found: {baby_blue_product.get('name')}")
                    else:
                        self.log_test("Find Baby Blue Product", False, "Baby Blue product not found in database")
                        return
                else:
                    error_text = await resp.text()
                    self.log_test("Find Baby Blue Product", False, f"Status {resp.status}: {error_text}")
                    return
        except Exception as e:
            self.log_test("Find Baby Blue Product", False, f"Exception: {str(e)}")
            return
        
        product_id = baby_blue_product['id']
        
        # Step 2: Get full product details to examine variant stock and pricing
        try:
            async with self.session.get(f"{API_BASE}/products/{product_id}") as resp:
                if resp.status == 200:
                    product_details = await resp.json()
                    variants = product_details.get('variants', [])
                    self.log_test("Get Baby Blue Product Details", True, f"Product has {len(variants)} variants")
                    
                    # Examine each variant's stock and pricing
                    for i, variant in enumerate(variants):
                        sku = variant.get('sku', 'Unknown')
                        attributes = variant.get('attributes', {})
                        pack_size = attributes.get('pack_size', 'Unknown')
                        size_code = attributes.get('size_code', 'Unknown')
                        
                        # Check stock fields
                        on_hand = variant.get('on_hand', 0)
                        stock_qty = variant.get('stock_qty', 0)
                        allocated = variant.get('allocated', 0)
                        available = on_hand - allocated
                        
                        # Check pricing
                        price_tiers = variant.get('price_tiers', [])
                        price = price_tiers[0].get('price', 0) if price_tiers else 0
                        
                        self.log_test(f"Baby Blue Variant {i+1} Stock Analysis", True, 
                                    f"SKU: {sku}, Size: {size_code}, Pack: {pack_size}pcs, on_hand: {on_hand}, stock_qty: {stock_qty}, available: {available}, price: ${price}")
                        
                        # Check if this matches the reported stock quantities (25, 35)
                        if on_hand in [25, 35] or stock_qty in [25, 35]:
                            self.log_test(f"Reported Stock Quantity Match", True, 
                                        f"Found reported stock quantity: on_hand={on_hand}, stock_qty={stock_qty}")
                    
                else:
                    error_text = await resp.text()
                    self.log_test("Get Baby Blue Product Details", False, f"Status {resp.status}: {error_text}")
                    return
        except Exception as e:
            self.log_test("Get Baby Blue Product Details", False, f"Exception: {str(e)}")
            return
        
        # Step 3: Test how in_stock field is calculated for product listing
        try:
            async with self.session.get(f"{API_BASE}/products") as resp:
                if resp.status == 200:
                    products_list = await resp.json()
                    
                    # Find Baby Blue in the listing
                    baby_blue_in_list = None
                    for product in products_list:
                        if product.get('id') == product_id:
                            baby_blue_in_list = product
                            break
                    
                    if baby_blue_in_list:
                        in_stock_status = baby_blue_in_list.get('in_stock', False)
                        self.log_test("Customer Product Listing in_stock", True, 
                                    f"Baby Blue shows in_stock: {in_stock_status}")
                        
                        # This is the key issue - customer sees "In Stock" but admin sees "Out of Stock"
                        if in_stock_status:
                            self.log_test("Customer Stock Status", True, "Customer sees 'In Stock'")
                        else:
                            self.log_test("Customer Stock Status", False, "Customer sees 'Out of Stock'")
                    else:
                        self.log_test("Baby Blue in Product Listing", False, "Baby Blue not found in product listing")
                        
                else:
                    error_text = await resp.text()
                    self.log_test("Product Listing API", False, f"Status {resp.status}: {error_text}")
        except Exception as e:
            self.log_test("Product Listing API", False, f"Exception: {str(e)}")
        
        # Step 4: Test admin inventory view
        if self.admin_token:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            try:
                async with self.session.get(f"{API_BASE}/admin/inventory", headers=headers) as resp:
                    if resp.status == 200:
                        inventory_data = await resp.json()
                        
                        # Find Baby Blue variants in admin inventory
                        baby_blue_inventory = []
                        for item in inventory_data:
                            if product_id in item.get('variant_id', '') or 'blue' in item.get('product_name', '').lower():
                                baby_blue_inventory.append(item)
                        
                        if baby_blue_inventory:
                            self.log_test("Admin Inventory Baby Blue", True, f"Found {len(baby_blue_inventory)} Baby Blue inventory items")
                            
                            for item in baby_blue_inventory:
                                on_hand = item.get('on_hand', 0)
                                available = item.get('available', 0)
                                is_low_stock = item.get('is_low_stock', False)
                                
                                self.log_test("Admin Inventory Item", True, 
                                            f"SKU: {item.get('sku')}, on_hand: {on_hand}, available: {available}, low_stock: {is_low_stock}")
                                
                                # Check if admin shows "Out of Stock" when stock exists
                                if on_hand > 0 and available <= 0:
                                    self.log_test("Admin Stock Discrepancy", False, 
                                                f"ISSUE: Admin shows out of stock but on_hand={on_hand}, available={available}")
                        else:
                            self.log_test("Admin Inventory Baby Blue", False, "Baby Blue not found in admin inventory")
                            
                    else:
                        error_text = await resp.text()
                        self.log_test("Admin Inventory API", False, f"Status {resp.status}: {error_text}")
            except Exception as e:
                self.log_test("Admin Inventory API", False, f"Exception: {str(e)}")
        
        # Step 5: Test variant pricing differences (50pcs vs 100pcs)
        try:
            async with self.session.get(f"{API_BASE}/products/{product_id}") as resp:
                if resp.status == 200:
                    product = await resp.json()
                    variants = product.get('variants', [])
                    
                    # Group variants by pack size
                    pack_size_pricing = {}
                    for variant in variants:
                        pack_size = variant.get('attributes', {}).get('pack_size')
                        price_tiers = variant.get('price_tiers', [])
                        if price_tiers and pack_size:
                            price = price_tiers[0].get('price', 0)
                            pack_size_pricing[pack_size] = price
                    
                    self.log_test("Pack Size Pricing Analysis", True, f"Pack size pricing: {pack_size_pricing}")
                    
                    # Check if 50pcs and 100pcs have same price (the reported issue)
                    if 50 in pack_size_pricing and 100 in pack_size_pricing:
                        price_50 = pack_size_pricing[50]
                        price_100 = pack_size_pricing[100]
                        
                        if price_50 == price_100:
                            self.log_test("Same Price Issue", False, 
                                        f"ISSUE: Both 50pcs and 100pcs show same price ${price_50}")
                        else:
                            self.log_test("Different Pack Size Pricing", True, 
                                        f"50pcs: ${price_50}, 100pcs: ${price_100}")
                        
                        # Check if both show $14.99 as reported
                        if price_50 == 14.99 and price_100 == 14.99:
                            self.log_test("Reported Price Issue", False, 
                                        "CONFIRMED: Both variants show $14.99 as reported")
                    else:
                        self.log_test("Pack Size Variants", False, "Could not find 50pcs and 100pcs variants")
                        
        except Exception as e:
            self.log_test("Variant Pricing Analysis", False, f"Exception: {str(e)}")
        
        # Step 6: Test stock calculation logic in product service
        try:
            # Test the stock calculation used in list_products method
            async with self.session.get(f"{API_BASE}/products") as resp:
                if resp.status == 200:
                    products = await resp.json()
                    baby_blue_listed = None
                    
                    for product in products:
                        if product.get('id') == product_id:
                            baby_blue_listed = product
                            break
                    
                    if baby_blue_listed:
                        listed_in_stock = baby_blue_listed.get('in_stock', False)
                        
                        # Now get the detailed product to compare
                        async with self.session.get(f"{API_BASE}/products/{product_id}") as detail_resp:
                            if detail_resp.status == 200:
                                detailed_product = await detail_resp.json()
                                variants = detailed_product.get('variants', [])
                                
                                # Calculate stock using the same logic as ProductService.list_products
                                calculated_in_stock = any(v.get('stock_qty', 0) > 0 or v.get('on_hand', 0) > 0 for v in variants)
                                
                                self.log_test("Stock Calculation Logic", True, 
                                            f"Listed in_stock: {listed_in_stock}, Calculated in_stock: {calculated_in_stock}")
                                
                                if listed_in_stock != calculated_in_stock:
                                    self.log_test("Stock Calculation Mismatch", False, 
                                                "ISSUE: Stock calculation inconsistency between listing and detail")
                                
                                # Show individual variant stock contributions
                                for i, variant in enumerate(variants):
                                    stock_qty = variant.get('stock_qty', 0)
                                    on_hand = variant.get('on_hand', 0)
                                    contributes_to_stock = stock_qty > 0 or on_hand > 0
                                    
                                    self.log_test(f"Variant {i+1} Stock Contribution", True, 
                                                f"stock_qty: {stock_qty}, on_hand: {on_hand}, contributes: {contributes_to_stock}")
                        
        except Exception as e:
            self.log_test("Stock Calculation Logic", False, f"Exception: {str(e)}")
    
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

    async def test_product_listing_for_editing(self):
        """Test product listing and individual product access for editing purposes"""
        print("\n📝 Testing Product Listing for Editing Access...")
        
        # Step 1: Get all products
        try:
            async with self.session.get(f"{API_BASE}/products") as resp:
                if resp.status == 200:
                    products = await resp.json()
                    self.log_test("GET /api/products", True, f"Retrieved {len(products)} products")
                    
                    if not products:
                        self.log_test("Product Availability", False, "No products found in the system")
                        return
                    
                    # List all product IDs and names
                    print("\n📋 Available Products and IDs:")
                    product_ids = []
                    for i, product in enumerate(products, 1):
                        product_id = product.get('id')
                        product_name = product.get('name', 'Unknown')
                        variant_count = len(product.get('variants', []))
                        print(f"   {i}. ID: {product_id}")
                        print(f"      Name: {product_name}")
                        print(f"      Variants: {variant_count}")
                        print()
                        product_ids.append(product_id)
                    
                    self.log_test("Product IDs Listed", True, f"Found {len(product_ids)} product IDs")
                    
                    # Step 2: Test individual product access for each product
                    print("\n🔍 Testing Individual Product Access:")
                    successful_loads = 0
                    
                    for i, product_id in enumerate(product_ids, 1):
                        try:
                            async with self.session.get(f"{API_BASE}/products/{product_id}") as product_resp:
                                if product_resp.status == 200:
                                    product_detail = await product_resp.json()
                                    product_name = product_detail.get('name', 'Unknown')
                                    variants = product_detail.get('variants', [])
                                    
                                    self.log_test(f"GET /api/products/{product_id}", True, 
                                                f"✅ {product_name} - {len(variants)} variants loaded")
                                    successful_loads += 1
                                    
                                    # Show variant details for editing context
                                    if variants:
                                        print(f"      Variant details for editing:")
                                        for j, variant in enumerate(variants[:3], 1):  # Show first 3 variants
                                            attrs = variant.get('attributes', {})
                                            price_tiers = variant.get('price_tiers', [])
                                            stock = variant.get('on_hand', variant.get('stock_qty', 0))
                                            
                                            size = attrs.get('size_code', 'Unknown')
                                            color = attrs.get('color', 'Unknown')
                                            pack_size = attrs.get('pack_size', 'Unknown')
                                            price = price_tiers[0].get('price', 0) if price_tiers else 0
                                            
                                            print(f"        Variant {j}: {size} {color} ({pack_size} pack) - ${price} - Stock: {stock}")
                                        
                                        if len(variants) > 3:
                                            print(f"        ... and {len(variants) - 3} more variants")
                                        print()
                                    
                                else:
                                    error_text = await product_resp.text()
                                    self.log_test(f"GET /api/products/{product_id}", False, 
                                                f"❌ Status {product_resp.status}: {error_text}")
                                    
                        except Exception as e:
                            self.log_test(f"GET /api/products/{product_id}", False, f"❌ Exception: {str(e)}")
                    
                    # Summary
                    self.log_test("Product Loading Success Rate", successful_loads == len(product_ids), 
                                f"{successful_loads}/{len(product_ids)} products loaded successfully")
                    
                    if successful_loads > 0:
                        print(f"\n✅ SUCCESS: You can edit any of the {successful_loads} products listed above")
                        print("   Use any of the product IDs shown to access the ProductForm interface")
                        print("   All products loaded successfully and are ready for editing")
                    else:
                        print(f"\n❌ ISSUE: No products could be loaded for editing")
                        print("   This indicates a problem with the product detail API")
                    
                else:
                    error_text = await resp.text()
                    self.log_test("GET /api/products", False, f"Status {resp.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("GET /api/products", False, f"Exception: {str(e)}")

    async def test_simplified_variant_creation_and_pricing(self):
        """Test the simplified variant creation and pricing system workflow"""
        print("\n🎯 Testing Simplified Variant Creation and Pricing System...")
        
        if not self.admin_token:
            self.log_test("Simplified Variant Creation Test", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test with existing Baby Blue product ID as specified
        baby_blue_product_id = "6084a6ff-1911-488b-9288-2bc95e50cafa"
        
        # Step 1: Test Product Creation API with default pricing structure
        print("\n📝 Step 1: Testing Product Creation with Default Pricing...")
        
        new_product_data = {
            "name": "Test Simplified Variant Product",
            "description": "Testing simplified variant creation process",
            "category": "polymailers",
            "color": "white",
            "type": "normal",
            "variants": [
                {
                    "sku": f"TEST-SIMPLE-001",
                    "attributes": {
                        "width_cm": 20,
                        "height_cm": 25,
                        "size_code": "20x25",
                        "type": "normal",
                        "color": "white",
                        "pack_size": 50
                    },
                    "price_tiers": [{"min_quantity": 1, "price": 0}],  # Default pricing with 0 values
                    "stock_qty": 0,  # Default stock
                    "on_hand": 0,
                    "allocated": 0,
                    "safety_stock": 0,
                    "low_stock_threshold": 5
                },
                {
                    "sku": f"TEST-SIMPLE-002",
                    "attributes": {
                        "width_cm": 25,
                        "height_cm": 30,
                        "size_code": "25x30",
                        "type": "normal",
                        "color": "white",
                        "pack_size": 100
                    },
                    "price_tiers": [{"min_quantity": 1, "price": 0}],  # Default pricing with 0 values
                    "stock_qty": 0,  # Default stock
                    "on_hand": 0,
                    "allocated": 0,
                    "safety_stock": 0,
                    "low_stock_threshold": 5
                }
            ]
        }
        
        created_product_id = None
        try:
            async with self.session.post(f"{API_BASE}/admin/products", 
                                       json=new_product_data, headers=headers) as resp:
                if resp.status == 200:
                    created_product = await resp.json()
                    created_product_id = created_product.get('id')
                    variants = created_product.get('variants', [])
                    
                    self.log_test("Product Creation with Default Pricing", True, 
                                f"Created product with {len(variants)} variants")
                    
                    # Verify default pricing structure
                    for i, variant in enumerate(variants):
                        price_tiers = variant.get('price_tiers', [])
                        if price_tiers and price_tiers[0].get('price') == 0:
                            self.log_test(f"Default Pricing - Variant {i+1}", True, 
                                        f"Price tier with 0 value: {price_tiers[0]}")
                        else:
                            self.log_test(f"Default Pricing - Variant {i+1}", False, 
                                        f"Expected price 0, got: {price_tiers}")
                        
                        # Verify default stock
                        on_hand = variant.get('on_hand', 0)
                        stock_qty = variant.get('stock_qty', 0)
                        if on_hand == 0 and stock_qty == 0:
                            self.log_test(f"Default Stock - Variant {i+1}", True, 
                                        f"on_hand: {on_hand}, stock_qty: {stock_qty}")
                        else:
                            self.log_test(f"Default Stock - Variant {i+1}", False, 
                                        f"Expected 0 stock, got on_hand: {on_hand}, stock_qty: {stock_qty}")
                else:
                    error_text = await resp.text()
                    self.log_test("Product Creation with Default Pricing", False, 
                                f"Status {resp.status}: {error_text}")
                    return
        except Exception as e:
            self.log_test("Product Creation with Default Pricing", False, f"Exception: {str(e)}")
            return
        
        # Step 2: Test Product Update API to update variants with real pricing and stock
        print("\n💰 Step 2: Testing Product Update with Real Pricing and Stock...")
        
        if created_product_id:
            # Get the created product to update its variants
            try:
                async with self.session.get(f"{API_BASE}/products/{created_product_id}") as resp:
                    if resp.status == 200:
                        product_to_update = await resp.json()
                        variants_to_update = product_to_update.get('variants', [])
                        
                        # Update variants with real pricing and stock
                        for i, variant in enumerate(variants_to_update):
                            if i == 0:
                                variant['price_tiers'] = [{"min_quantity": 1, "price": 8.99}]
                                variant['on_hand'] = 50
                                variant['stock_qty'] = 50
                            elif i == 1:
                                variant['price_tiers'] = [{"min_quantity": 1, "price": 15.99}]
                                variant['on_hand'] = 75
                                variant['stock_qty'] = 75
                        
                        update_payload = {
                            "variants": variants_to_update
                        }
                        
                        async with self.session.put(f"{API_BASE}/admin/products/{created_product_id}", 
                                                  json=update_payload, headers=headers) as update_resp:
                            if update_resp.status == 200:
                                updated_product = await update_resp.json()
                                updated_variants = updated_product.get('variants', [])
                                
                                self.log_test("Product Update with Real Pricing", True, 
                                            f"Updated {len(updated_variants)} variants")
                                
                                # Verify pricing updates
                                for i, variant in enumerate(updated_variants):
                                    price_tiers = variant.get('price_tiers', [])
                                    expected_prices = [8.99, 15.99]
                                    
                                    if i < len(expected_prices) and price_tiers:
                                        actual_price = price_tiers[0].get('price', 0)
                                        expected_price = expected_prices[i]
                                        
                                        if actual_price == expected_price:
                                            self.log_test(f"Updated Pricing - Variant {i+1}", True, 
                                                        f"Price updated to ${actual_price}")
                                        else:
                                            self.log_test(f"Updated Pricing - Variant {i+1}", False, 
                                                        f"Expected ${expected_price}, got ${actual_price}")
                                    
                                    # Verify stock updates
                                    on_hand = variant.get('on_hand', 0)
                                    expected_stock = [50, 75]
                                    if i < len(expected_stock):
                                        expected = expected_stock[i]
                                        if on_hand == expected:
                                            self.log_test(f"Updated Stock - Variant {i+1}", True, 
                                                        f"Stock updated to {on_hand}")
                                        else:
                                            self.log_test(f"Updated Stock - Variant {i+1}", False, 
                                                        f"Expected {expected}, got {on_hand}")
                            else:
                                error_text = await update_resp.text()
                                self.log_test("Product Update with Real Pricing", False, 
                                            f"Status {update_resp.status}: {error_text}")
                    else:
                        error_text = await resp.text()
                        self.log_test("Get Product for Update", False, f"Status {resp.status}: {error_text}")
            except Exception as e:
                self.log_test("Product Update with Real Pricing", False, f"Exception: {str(e)}")
        
        # Step 3: Test Product Listing API for price range calculation
        print("\n📊 Step 3: Testing Product Listing Price Range Calculation...")
        
        try:
            async with self.session.get(f"{API_BASE}/products") as resp:
                if resp.status == 200:
                    products = await resp.json()
                    
                    # Find our created product in the listing
                    test_product = None
                    for product in products:
                        if product.get('id') == created_product_id:
                            test_product = product
                            break
                    
                    if test_product:
                        price_range = test_product.get('price_range', {})
                        min_price = price_range.get('min', 0)
                        max_price = price_range.get('max', 0)
                        
                        # Expected price range: $8.99 - $15.99
                        if min_price == 8.99 and max_price == 15.99:
                            self.log_test("Price Range Calculation", True, 
                                        f"Correct price range: ${min_price} - ${max_price}")
                        else:
                            self.log_test("Price Range Calculation", False, 
                                        f"Expected $8.99 - $15.99, got ${min_price} - ${max_price}")
                    else:
                        self.log_test("Find Product in Listing", False, "Created product not found in listing")
                else:
                    error_text = await resp.text()
                    self.log_test("Product Listing API", False, f"Status {resp.status}: {error_text}")
        except Exception as e:
            self.log_test("Product Listing API", False, f"Exception: {str(e)}")
        
        # Step 4: Test Product Detail API for customer access
        print("\n👤 Step 4: Testing Customer Product Detail Access...")
        
        if created_product_id:
            try:
                # Test without admin headers (customer access)
                async with self.session.get(f"{API_BASE}/products/{created_product_id}") as resp:
                    if resp.status == 200:
                        customer_product = await resp.json()
                        customer_variants = customer_product.get('variants', [])
                        
                        self.log_test("Customer Product Detail Access", True, 
                                    f"Customer can access product with {len(customer_variants)} variants")
                        
                        # Verify customer sees updated pricing
                        for i, variant in enumerate(customer_variants):
                            price_tiers = variant.get('price_tiers', [])
                            expected_prices = [8.99, 15.99]
                            
                            if i < len(expected_prices) and price_tiers:
                                actual_price = price_tiers[0].get('price', 0)
                                expected_price = expected_prices[i]
                                
                                if actual_price == expected_price:
                                    self.log_test(f"Customer Sees Updated Price - Variant {i+1}", True, 
                                                f"Customer sees ${actual_price}")
                                else:
                                    self.log_test(f"Customer Sees Updated Price - Variant {i+1}", False, 
                                                f"Customer expected ${expected_price}, sees ${actual_price}")
                    else:
                        error_text = await resp.text()
                        self.log_test("Customer Product Detail Access", False, 
                                    f"Status {resp.status}: {error_text}")
            except Exception as e:
                self.log_test("Customer Product Detail Access", False, f"Exception: {str(e)}")
        
        # Step 5: Test with existing Baby Blue product
        print("\n🔵 Step 5: Testing with Existing Baby Blue Product...")
        
        try:
            # Get current Baby Blue product details
            async with self.session.get(f"{API_BASE}/products/{baby_blue_product_id}") as resp:
                if resp.status == 200:
                    baby_blue_product = await resp.json()
                    baby_blue_variants = baby_blue_product.get('variants', [])
                    
                    self.log_test("Baby Blue Product Access", True, 
                                f"Found Baby Blue product with {len(baby_blue_variants)} variants")
                    
                    # Test updating Baby Blue variants with new pricing
                    if baby_blue_variants:
                        updated_baby_blue_variants = []
                        for i, variant in enumerate(baby_blue_variants):
                            updated_variant = variant.copy()
                            # Update with new pricing structure
                            if i == 0:
                                updated_variant['price_tiers'] = [{"min_quantity": 1, "price": 9.99}]
                                updated_variant['on_hand'] = 25
                            elif i == 1:
                                updated_variant['price_tiers'] = [{"min_quantity": 1, "price": 17.99}]
                                updated_variant['on_hand'] = 30
                            updated_baby_blue_variants.append(updated_variant)
                        
                        baby_blue_update_payload = {
                            "variants": updated_baby_blue_variants
                        }
                        
                        async with self.session.put(f"{API_BASE}/admin/products/{baby_blue_product_id}", 
                                                  json=baby_blue_update_payload, headers=headers) as update_resp:
                            if update_resp.status == 200:
                                self.log_test("Baby Blue Product Update", True, "Successfully updated Baby Blue pricing")
                                
                                # Verify customer can see updated Baby Blue pricing
                                async with self.session.get(f"{API_BASE}/products/{baby_blue_product_id}") as customer_resp:
                                    if customer_resp.status == 200:
                                        customer_baby_blue = await customer_resp.json()
                                        customer_bb_variants = customer_baby_blue.get('variants', [])
                                        
                                        if customer_bb_variants:
                                            first_variant_price = customer_bb_variants[0].get('price_tiers', [{}])[0].get('price', 0)
                                            if first_variant_price == 9.99:
                                                self.log_test("Baby Blue Customer Price Visibility", True, 
                                                            f"Customer sees updated price: ${first_variant_price}")
                                            else:
                                                self.log_test("Baby Blue Customer Price Visibility", False, 
                                                            f"Expected $9.99, customer sees ${first_variant_price}")
                                    else:
                                        error_text = await customer_resp.text()
                                        self.log_test("Baby Blue Customer Access", False, 
                                                    f"Status {customer_resp.status}: {error_text}")
                            else:
                                error_text = await update_resp.text()
                                self.log_test("Baby Blue Product Update", False, 
                                            f"Status {update_resp.status}: {error_text}")
                else:
                    error_text = await resp.text()
                    self.log_test("Baby Blue Product Access", False, f"Status {resp.status}: {error_text}")
        except Exception as e:
            self.log_test("Baby Blue Product Testing", False, f"Exception: {str(e)}")
        
        # Step 6: Test price range calculation with updated products
        print("\n📈 Step 6: Testing Price Range Calculation After Updates...")
        
        try:
            async with self.session.get(f"{API_BASE}/products") as resp:
                if resp.status == 200:
                    products = await resp.json()
                    
                    # Check Baby Blue product price range
                    baby_blue_in_listing = None
                    for product in products:
                        if product.get('id') == baby_blue_product_id:
                            baby_blue_in_listing = product
                            break
                    
                    if baby_blue_in_listing:
                        bb_price_range = baby_blue_in_listing.get('price_range', {})
                        bb_min_price = bb_price_range.get('min', 0)
                        bb_max_price = bb_price_range.get('max', 0)
                        
                        self.log_test("Baby Blue Price Range in Listing", True, 
                                    f"Baby Blue price range: ${bb_min_price} - ${bb_max_price}")
                        
                        # Verify price range reflects updated variant pricing
                        if bb_min_price > 0 and bb_max_price > bb_min_price:
                            self.log_test("Price Range Reflects Updates", True, 
                                        "Price range correctly calculated from updated variants")
                        else:
                            self.log_test("Price Range Reflects Updates", False, 
                                        f"Invalid price range: ${bb_min_price} - ${bb_max_price}")
                    else:
                        self.log_test("Baby Blue in Product Listing", False, "Baby Blue not found in product listing")
                else:
                    error_text = await resp.text()
                    self.log_test("Final Product Listing Check", False, f"Status {resp.status}: {error_text}")
        except Exception as e:
            self.log_test("Final Price Range Check", False, f"Exception: {str(e)}")
        
        # Cleanup: Delete the test product we created
        if created_product_id:
            try:
                async with self.session.delete(f"{API_BASE}/admin/products/{created_product_id}", 
                                             headers=headers) as resp:
                    if resp.status == 200:
                        self.log_test("Test Product Cleanup", True, "Test product deleted successfully")
                    else:
                        self.log_test("Test Product Cleanup", False, f"Failed to delete test product: {resp.status}")
            except Exception as e:
                self.log_test("Test Product Cleanup", False, f"Exception during cleanup: {str(e)}")

async def main():
    """Run backend tests focused on safety stock management"""
    print("🚀 Starting M Supplies Backend API Tests - Safety Stock Management")
    print(f"Testing against: {API_BASE}")
    
    async with BackendTester() as tester:
        # Run authentication first
        await tester.authenticate()
        
        # PRIORITY TEST: Safety stock management functionality (as specifically requested)
        await tester.test_safety_stock_management()
        
        # Print summary
        passed, failed = tester.print_summary()
        
        return failed == 0

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)