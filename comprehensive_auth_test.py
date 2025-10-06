#!/usr/bin/env python3
"""
Comprehensive JWT Authentication Testing
Testing various scenarios that might cause authentication issues
"""

import asyncio
import aiohttp
import json
import os
import time
from datetime import datetime, timezone

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://supply-manager-20.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "email": "admin@polymailer.com",
    "password": "admin123"
}

class ComprehensiveAuthTester:
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
        """Get admin token"""
        try:
            async with self.session.post(f"{API_BASE}/auth/login", json=ADMIN_CREDENTIALS) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.admin_token = data.get('access_token')
                    return True
        except Exception as e:
            print(f"Authentication failed: {str(e)}")
        return False
    
    async def test_concurrent_requests(self):
        """Test multiple concurrent requests with the same token"""
        print("\n🔄 Testing Concurrent Requests with Same Token...")
        
        if not self.admin_token:
            self.log_test("Concurrent Requests", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Create multiple concurrent requests
        tasks = []
        for i in range(5):
            task = self.session.get(f"{API_BASE}/admin/inventory", headers=headers)
            tasks.append(task)
        
        try:
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            success_count = 0
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    print(f"    Request {i+1}: Exception - {str(response)}")
                else:
                    async with response:
                        if response.status == 200:
                            success_count += 1
                            print(f"    Request {i+1}: Success (200)")
                        else:
                            error_text = await response.text()
                            print(f"    Request {i+1}: Failed ({response.status}) - {error_text}")
            
            if success_count == 5:
                self.log_test("Concurrent Requests", True, f"All {success_count} requests succeeded")
            else:
                self.log_test("Concurrent Requests", False, f"Only {success_count}/5 requests succeeded")
                
        except Exception as e:
            self.log_test("Concurrent Requests", False, f"Exception: {str(e)}")
    
    async def test_token_reuse_across_sessions(self):
        """Test using the same token across different sessions"""
        print("\n🔄 Testing Token Reuse Across Sessions...")
        
        if not self.admin_token:
            self.log_test("Token Reuse", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Create a new session and use the same token
        async with aiohttp.ClientSession() as new_session:
            try:
                async with new_session.get(f"{API_BASE}/admin/inventory", headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.log_test("Token Reuse Across Sessions", True, f"Token works in new session, found {len(data)} items")
                    else:
                        error_text = await resp.text()
                        self.log_test("Token Reuse Across Sessions", False, f"Status {resp.status}: {error_text}")
            except Exception as e:
                self.log_test("Token Reuse Across Sessions", False, f"Exception: {str(e)}")
    
    async def test_large_payload_with_auth(self):
        """Test authentication with large payloads"""
        print("\n📦 Testing Large Payload with Authentication...")
        
        if not self.admin_token:
            self.log_test("Large Payload Auth", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Create a large product payload
        large_payload = {
            "name": "Large Test Product",
            "description": "A" * 1000,  # Large description
            "category": "test",
            "specifications": {f"spec_{i}": f"value_{i}" for i in range(50)},  # Many specifications
            "variants": [{
                "sku": f"LARGE-{i:03d}",
                "attributes": {
                    "width_cm": 25,
                    "height_cm": 35,
                    "size_code": "25x35",
                    "type": "normal",
                    "color": "white"
                },
                "price_tiers": [{"min_quantity": 1, "price": 1.0}],
                "stock_qty": 100
            } for i in range(10)]  # Multiple variants
        }
        
        try:
            async with self.session.post(f"{API_BASE}/admin/products", 
                                       json=large_payload, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.log_test("Large Payload Auth", True, f"Large product created: {data.get('name')}")
                    
                    # Clean up - delete the created product
                    product_id = data.get('id')
                    if product_id:
                        await self.session.delete(f"{API_BASE}/admin/products/{product_id}", headers=headers)
                else:
                    error_text = await resp.text()
                    self.log_test("Large Payload Auth", False, f"Status {resp.status}: {error_text}")
        except Exception as e:
            self.log_test("Large Payload Auth", False, f"Exception: {str(e)}")
    
    async def test_special_characters_in_headers(self):
        """Test authentication with special characters in headers"""
        print("\n🔤 Testing Special Characters in Headers...")
        
        if not self.admin_token:
            self.log_test("Special Characters Auth", False, "No admin token available")
            return
        
        # Test with extra headers that might interfere
        headers = {
            "Authorization": f"Bearer {self.admin_token}",
            "X-Custom-Header": "test-value-with-special-chars-!@#$%^&*()",
            "User-Agent": "Test-Agent/1.0 (Special; Characters; Here)",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        try:
            async with self.session.get(f"{API_BASE}/admin/inventory", headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.log_test("Special Characters in Headers", True, f"Auth works with special headers, found {len(data)} items")
                else:
                    error_text = await resp.text()
                    self.log_test("Special Characters in Headers", False, f"Status {resp.status}: {error_text}")
        except Exception as e:
            self.log_test("Special Characters in Headers", False, f"Exception: {str(e)}")
    
    async def test_different_content_types(self):
        """Test authentication with different content types"""
        print("\n📄 Testing Different Content Types...")
        
        if not self.admin_token:
            self.log_test("Different Content Types", False, "No admin token available")
            return
        
        # Get a product ID first
        product_id = None
        try:
            async with self.session.post(f"{API_BASE}/products/filter", json={"page": 1, "limit": 1}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    products = data.get('products', [])
                    if products:
                        product_id = products[0]['id']
        except:
            pass
        
        if not product_id:
            self.log_test("Different Content Types", False, "No product ID available for testing")
            return
        
        # Test with different content types
        content_types = [
            "application/json",
            "application/json; charset=utf-8",
            "application/json; charset=UTF-8",
        ]
        
        update_data = {"name": "Content Type Test"}
        
        for content_type in content_types:
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": content_type
            }
            
            try:
                async with self.session.put(f"{API_BASE}/admin/products/{product_id}", 
                                          json=update_data, headers=headers) as resp:
                    if resp.status == 200:
                        self.log_test(f"Content-Type: {content_type}", True, "Auth successful")
                    else:
                        error_text = await resp.text()
                        self.log_test(f"Content-Type: {content_type}", False, f"Status {resp.status}: {error_text}")
            except Exception as e:
                self.log_test(f"Content-Type: {content_type}", False, f"Exception: {str(e)}")
    
    async def test_token_with_different_case(self):
        """Test authentication with different header case"""
        print("\n🔤 Testing Header Case Sensitivity...")
        
        if not self.admin_token:
            self.log_test("Header Case Test", False, "No admin token available")
            return
        
        # Test different cases for Authorization header
        header_variations = [
            {"Authorization": f"Bearer {self.admin_token}"},
            {"authorization": f"Bearer {self.admin_token}"},
            {"AUTHORIZATION": f"Bearer {self.admin_token}"},
            {"Authorization": f"bearer {self.admin_token}"},
            {"Authorization": f"BEARER {self.admin_token}"},
        ]
        
        for i, headers in enumerate(header_variations):
            try:
                async with self.session.get(f"{API_BASE}/admin/inventory", headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.log_test(f"Header Case Variation {i+1}", True, f"Auth successful with {list(headers.keys())[0]}")
                    else:
                        error_text = await resp.text()
                        self.log_test(f"Header Case Variation {i+1}", False, f"Status {resp.status}: {error_text}")
            except Exception as e:
                self.log_test(f"Header Case Variation {i+1}", False, f"Exception: {str(e)}")
    
    async def test_rapid_sequential_requests(self):
        """Test rapid sequential requests"""
        print("\n⚡ Testing Rapid Sequential Requests...")
        
        if not self.admin_token:
            self.log_test("Rapid Sequential", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        success_count = 0
        total_requests = 10
        
        for i in range(total_requests):
            try:
                async with self.session.get(f"{API_BASE}/admin/inventory", headers=headers) as resp:
                    if resp.status == 200:
                        success_count += 1
                    else:
                        error_text = await resp.text()
                        print(f"    Request {i+1}: Failed ({resp.status}) - {error_text}")
            except Exception as e:
                print(f"    Request {i+1}: Exception - {str(e)}")
        
        if success_count == total_requests:
            self.log_test("Rapid Sequential Requests", True, f"All {success_count} requests succeeded")
        else:
            self.log_test("Rapid Sequential Requests", False, f"Only {success_count}/{total_requests} requests succeeded")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("🧪 COMPREHENSIVE AUTHENTICATION TEST SUMMARY")
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
        
        return passed, failed

async def main():
    """Run comprehensive authentication tests"""
    print("🚀 Starting Comprehensive Authentication Tests")
    print(f"Testing against: {API_BASE}")
    
    async with ComprehensiveAuthTester() as tester:
        # Authenticate first
        if not await tester.authenticate():
            print("❌ Failed to authenticate - cannot run tests")
            return False
        
        # Run all tests
        await tester.test_concurrent_requests()
        await tester.test_token_reuse_across_sessions()
        await tester.test_large_payload_with_auth()
        await tester.test_special_characters_in_headers()
        await tester.test_different_content_types()
        await tester.test_token_with_different_case()
        await tester.test_rapid_sequential_requests()
        
        # Print summary
        passed, failed = tester.print_summary()
        
        return failed == 0

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)