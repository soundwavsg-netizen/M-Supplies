#!/usr/bin/env python3
"""
JWT Authentication Testing for M Supplies E-commerce Platform
Focused testing of JWT authentication flow, especially for admin product update functionality
"""

import asyncio
import aiohttp
import json
import os
import jwt as pyjwt
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://chatbot-store-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "email": "admin@polymailer.com",
    "password": "admin123"
}

class JWTAuthTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.test_results = []
        self.product_id = None  # Will store a product ID for testing
        
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
    
    async def test_admin_login_and_token_extraction(self):
        """Test admin login and extract JWT token"""
        print("\n🔐 Testing Admin Login and JWT Token Extraction...")
        
        try:
            async with self.session.post(f"{API_BASE}/auth/login", json=ADMIN_CREDENTIALS) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.admin_token = data.get('access_token')
                    refresh_token = data.get('refresh_token')
                    user_data = data.get('user', {})
                    
                    if self.admin_token:
                        self.log_test("Admin Login Success", True, f"Token received: {self.admin_token[:20]}...")
                        self.log_test("Token Structure Check", True, f"Access token length: {len(self.admin_token)}")
                        
                        if refresh_token:
                            self.log_test("Refresh Token Present", True, f"Refresh token: {refresh_token[:20]}...")
                        else:
                            self.log_test("Refresh Token Present", False, "No refresh token received")
                        
                        # Check user data
                        if user_data.get('email') == ADMIN_CREDENTIALS['email']:
                            self.log_test("User Data Validation", True, f"User email: {user_data.get('email')}")
                        else:
                            self.log_test("User Data Validation", False, f"Expected {ADMIN_CREDENTIALS['email']}, got {user_data.get('email')}")
                    else:
                        self.log_test("Admin Login Success", False, "No access token in response")
                else:
                    error_text = await resp.text()
                    self.log_test("Admin Login Success", False, f"Status {resp.status}: {error_text}")
        except Exception as e:
            self.log_test("Admin Login Success", False, f"Exception: {str(e)}")
    
    async def test_token_structure_and_expiration(self):
        """Test JWT token structure and expiration time"""
        print("\n🔍 Testing JWT Token Structure and Expiration...")
        
        if not self.admin_token:
            self.log_test("Token Structure Test", False, "No admin token available")
            return
        
        try:
            # Decode token without verification to inspect structure
            decoded = pyjwt.decode(self.admin_token, options={"verify_signature": False})
            
            # Check required fields
            required_fields = ['sub', 'exp', 'type']
            missing_fields = [field for field in required_fields if field not in decoded]
            
            if missing_fields:
                self.log_test("Token Required Fields", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("Token Required Fields", True, "All required fields present")
            
            # Check token type
            if decoded.get('type') == 'access':
                self.log_test("Token Type Validation", True, "Token type is 'access'")
            else:
                self.log_test("Token Type Validation", False, f"Expected 'access', got '{decoded.get('type')}'")
            
            # Check expiration
            exp_timestamp = decoded.get('exp')
            if exp_timestamp:
                exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
                now = datetime.now(timezone.utc)
                time_until_exp = exp_datetime - now
                
                if time_until_exp.total_seconds() > 0:
                    self.log_test("Token Expiration Check", True, f"Token expires in {time_until_exp}")
                else:
                    self.log_test("Token Expiration Check", False, "Token is already expired")
            else:
                self.log_test("Token Expiration Check", False, "No expiration field in token")
            
            # Print full token payload for debugging
            print(f"    Token payload: {json.dumps(decoded, indent=2, default=str)}")
            
        except Exception as e:
            self.log_test("Token Structure Test", False, f"Exception decoding token: {str(e)}")
    
    async def get_test_product_id(self):
        """Get a product ID for testing"""
        try:
            async with self.session.post(f"{API_BASE}/products/filter", json={"page": 1, "limit": 1}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    products = data.get('products', [])
                    if products:
                        self.product_id = products[0]['id']
                        return True
        except Exception as e:
            print(f"    Error getting test product ID: {str(e)}")
        return False
    
    async def test_get_requests_with_jwt(self):
        """Test GET requests with JWT token (should work)"""
        print("\n📥 Testing GET Requests with JWT Token...")
        
        if not self.admin_token:
            self.log_test("GET Request Test", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test 1: GET /api/auth/me (requires authentication)
        try:
            async with self.session.get(f"{API_BASE}/auth/me", headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.log_test("GET /auth/me with JWT", True, f"User: {data.get('email')}")
                else:
                    error_text = await resp.text()
                    self.log_test("GET /auth/me with JWT", False, f"Status {resp.status}: {error_text}")
        except Exception as e:
            self.log_test("GET /auth/me with JWT", False, f"Exception: {str(e)}")
        
        # Test 2: GET /api/admin/inventory (admin endpoint)
        try:
            async with self.session.get(f"{API_BASE}/admin/inventory", headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.log_test("GET /admin/inventory with JWT", True, f"Found {len(data)} inventory items")
                else:
                    error_text = await resp.text()
                    self.log_test("GET /admin/inventory with JWT", False, f"Status {resp.status}: {error_text}")
        except Exception as e:
            self.log_test("GET /admin/inventory with JWT", False, f"Exception: {str(e)}")
        
        # Test 3: GET product by ID (if we have one)
        if await self.get_test_product_id():
            try:
                async with self.session.get(f"{API_BASE}/products/{self.product_id}") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.log_test("GET /products/{id} (no auth required)", True, f"Product: {data.get('name')}")
                    else:
                        error_text = await resp.text()
                        self.log_test("GET /products/{id} (no auth required)", False, f"Status {resp.status}: {error_text}")
            except Exception as e:
                self.log_test("GET /products/{id} (no auth required)", False, f"Exception: {str(e)}")
    
    async def test_put_requests_with_jwt(self):
        """Test PUT requests with JWT token (the failing case)"""
        print("\n📤 Testing PUT Requests with JWT Token...")
        
        if not self.admin_token:
            self.log_test("PUT Request Test", False, "No admin token available")
            return
        
        if not self.product_id:
            if not await self.get_test_product_id():
                self.log_test("PUT Request Test", False, "No product ID available for testing")
                return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test PUT /api/admin/products/{product_id}
        update_data = {
            "name": "Test Product Update",
            "description": "Updated description for testing JWT authentication"
        }
        
        try:
            async with self.session.put(f"{API_BASE}/admin/products/{self.product_id}", 
                                      json=update_data, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.log_test("PUT /admin/products/{id} with JWT", True, f"Product updated: {data.get('name')}")
                else:
                    error_text = await resp.text()
                    self.log_test("PUT /admin/products/{id} with JWT", False, f"Status {resp.status}: {error_text}")
                    
                    # If this is the 401 error, let's debug further
                    if resp.status == 401:
                        print(f"    🔍 DEBUG: 401 Unauthorized error details:")
                        print(f"    Response headers: {dict(resp.headers)}")
                        print(f"    Request headers sent: {headers}")
                        print(f"    Token being used: {self.admin_token[:50]}...")
        except Exception as e:
            self.log_test("PUT /admin/products/{id} with JWT", False, f"Exception: {str(e)}")
    
    async def test_token_edge_cases(self):
        """Test token edge cases"""
        print("\n🧪 Testing Token Edge Cases...")
        
        if not self.product_id:
            if not await self.get_test_product_id():
                print("    Skipping edge case tests - no product ID available")
                return
        
        update_data = {"name": "Edge Case Test"}
        
        # Test 1: Missing Authorization header
        try:
            async with self.session.put(f"{API_BASE}/admin/products/{self.product_id}", json=update_data) as resp:
                if resp.status == 401:
                    self.log_test("Missing Authorization Header", True, "Correctly returned 401")
                else:
                    self.log_test("Missing Authorization Header", False, f"Expected 401, got {resp.status}")
        except Exception as e:
            self.log_test("Missing Authorization Header", False, f"Exception: {str(e)}")
        
        # Test 2: Malformed token
        malformed_headers = {"Authorization": "Bearer invalid.token.here"}
        try:
            async with self.session.put(f"{API_BASE}/admin/products/{self.product_id}", 
                                      json=update_data, headers=malformed_headers) as resp:
                if resp.status == 401:
                    self.log_test("Malformed Token", True, "Correctly returned 401")
                else:
                    self.log_test("Malformed Token", False, f"Expected 401, got {resp.status}")
        except Exception as e:
            self.log_test("Malformed Token", False, f"Exception: {str(e)}")
        
        # Test 3: Wrong Bearer format
        wrong_format_headers = {"Authorization": f"Token {self.admin_token}"}
        try:
            async with self.session.put(f"{API_BASE}/admin/products/{self.product_id}", 
                                      json=update_data, headers=wrong_format_headers) as resp:
                if resp.status == 401:
                    self.log_test("Wrong Bearer Format", True, "Correctly returned 401")
                else:
                    self.log_test("Wrong Bearer Format", False, f"Expected 401, got {resp.status}")
        except Exception as e:
            self.log_test("Wrong Bearer Format", False, f"Exception: {str(e)}")
        
        # Test 4: Empty Bearer token
        empty_headers = {"Authorization": "Bearer "}
        try:
            async with self.session.put(f"{API_BASE}/admin/products/{self.product_id}", 
                                      json=update_data, headers=empty_headers) as resp:
                if resp.status == 401:
                    self.log_test("Empty Bearer Token", True, "Correctly returned 401")
                else:
                    self.log_test("Empty Bearer Token", False, f"Expected 401, got {resp.status}")
        except Exception as e:
            self.log_test("Empty Bearer Token", False, f"Exception: {str(e)}")
    
    async def test_authentication_middleware_debugging(self):
        """Debug authentication middleware behavior"""
        print("\n🔧 Debugging Authentication Middleware...")
        
        if not self.admin_token:
            self.log_test("Middleware Debug", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test different HTTP methods with the same token
        methods_to_test = [
            ("GET", f"{API_BASE}/auth/me", None),
            ("POST", f"{API_BASE}/admin/products", {
                "name": "Test Product",
                "description": "Test description",
                "category": "test",
                "variants": [{
                    "sku": "TEST-001",
                    "attributes": {
                        "width_cm": 25,
                        "height_cm": 35,
                        "size_code": "25x35",
                        "type": "normal",
                        "color": "white"
                    },
                    "price_tiers": [{"min_quantity": 1, "price": 1.0}],
                    "stock_qty": 100
                }]
            }),
        ]
        
        if self.product_id:
            methods_to_test.append(("PUT", f"{API_BASE}/admin/products/{self.product_id}", {"name": "Updated Test Product"}))
            methods_to_test.append(("DELETE", f"{API_BASE}/admin/products/{self.product_id}", None))
        
        for method, url, data in methods_to_test:
            try:
                async with self.session.request(method, url, json=data, headers=headers) as resp:
                    status_text = "SUCCESS" if resp.status < 400 else "FAILED"
                    self.log_test(f"{method} Request Authentication", resp.status < 400, 
                                f"{method} {url} -> {resp.status} ({status_text})")
                    
                    if resp.status >= 400:
                        error_text = await resp.text()
                        print(f"    Error details: {error_text}")
            except Exception as e:
                self.log_test(f"{method} Request Authentication", False, f"Exception: {str(e)}")
    
    async def test_token_validation_consistency(self):
        """Test if token validation is consistent across different endpoints"""
        print("\n🔄 Testing Token Validation Consistency...")
        
        if not self.admin_token:
            self.log_test("Token Validation Consistency", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test multiple admin endpoints to see if they all handle JWT the same way
        admin_endpoints = [
            ("GET", f"{API_BASE}/admin/inventory"),
            ("GET", f"{API_BASE}/admin/users"),
            ("GET", f"{API_BASE}/admin/orders"),
            ("GET", f"{API_BASE}/admin/coupons"),
        ]
        
        consistent_behavior = True
        results = []
        
        for method, url in admin_endpoints:
            try:
                async with self.session.request(method, url, headers=headers) as resp:
                    results.append((url, resp.status))
                    if resp.status == 401:
                        consistent_behavior = False
                        error_text = await resp.text()
                        print(f"    ❌ {method} {url} -> 401: {error_text}")
                    else:
                        print(f"    ✅ {method} {url} -> {resp.status}")
            except Exception as e:
                results.append((url, f"Exception: {str(e)}"))
                consistent_behavior = False
        
        self.log_test("Token Validation Consistency", consistent_behavior, 
                     f"All admin endpoints should accept the same valid JWT token")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("🧪 JWT AUTHENTICATION TEST SUMMARY")
        print("="*70)
        
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
        
        # Specific analysis for the reported issue
        put_test_failed = any(
            not result['success'] and 'PUT' in result['test'] 
            for result in self.test_results
        )
        
        get_test_passed = any(
            result['success'] and 'GET' in result['test'] and 'JWT' in result['test']
            for result in self.test_results
        )
        
        if put_test_failed and get_test_passed:
            print("\n🔍 ISSUE ANALYSIS:")
            print("  • GET requests with JWT token work correctly")
            print("  • PUT requests with JWT token fail with 401")
            print("  • This suggests an inconsistency in authentication middleware")
            print("  • Recommendation: Check if PUT request handling differs from GET")
        
        return passed, failed

async def main():
    """Run JWT authentication tests"""
    print("🚀 Starting JWT Authentication Tests for M Supplies")
    print(f"Testing against: {API_BASE}")
    
    async with JWTAuthTester() as tester:
        # Run all tests in sequence
        await tester.test_admin_login_and_token_extraction()
        await tester.test_token_structure_and_expiration()
        await tester.test_get_requests_with_jwt()
        await tester.test_put_requests_with_jwt()
        await tester.test_token_edge_cases()
        await tester.test_authentication_middleware_debugging()
        await tester.test_token_validation_consistency()
        
        # Print summary
        passed, failed = tester.print_summary()
        
        return failed == 0

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)