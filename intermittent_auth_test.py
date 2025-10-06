#!/usr/bin/env python3
"""
Intermittent Authentication Issue Testing
Testing to reproduce the intermittent 401 errors seen in logs
"""

import asyncio
import aiohttp
import json
import os
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://supply-manager-20.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "email": "admin@polymailer.com",
    "password": "admin123"
}

class IntermittentAuthTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.test_results = []
        self.product_id = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': timestamp
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
            print(f"Error getting test product ID: {str(e)}")
        return False
    
    async def test_repeated_put_requests(self, iterations=20):
        """Test repeated PUT requests to see if we can reproduce the intermittent issue"""
        print(f"\n🔄 Testing {iterations} Repeated PUT Requests...")
        
        if not self.admin_token:
            self.log_result("Repeated PUT Test", False, "No admin token available")
            return
        
        if not await self.get_test_product_id():
            self.log_result("Repeated PUT Test", False, "No product ID available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        success_count = 0
        failure_count = 0
        
        for i in range(iterations):
            update_data = {
                "name": f"Test Product Update {i+1}",
                "description": f"Updated description for iteration {i+1}"
            }
            
            try:
                async with self.session.put(f"{API_BASE}/admin/products/{self.product_id}", 
                                          json=update_data, headers=headers) as resp:
                    if resp.status == 200:
                        success_count += 1
                        self.log_result(f"PUT Request {i+1}", True, f"Success (200)")
                    else:
                        failure_count += 1
                        error_text = await resp.text()
                        self.log_result(f"PUT Request {i+1}", False, f"Status {resp.status}: {error_text}")
                        
                        # If it's a 401, let's get more details
                        if resp.status == 401:
                            print(f"    🔍 401 Error Details:")
                            print(f"    Response headers: {dict(resp.headers)}")
                            print(f"    Token used: {self.admin_token[:50]}...")
            except Exception as e:
                failure_count += 1
                self.log_result(f"PUT Request {i+1}", False, f"Exception: {str(e)}")
            
            # Small delay between requests
            await asyncio.sleep(0.1)
        
        print(f"\n📊 Results: {success_count} successes, {failure_count} failures out of {iterations} requests")
        
        if failure_count > 0:
            failure_rate = (failure_count / iterations) * 100
            print(f"❌ Failure rate: {failure_rate:.1f}%")
            return False
        else:
            print("✅ All requests succeeded")
            return True
    
    async def test_concurrent_put_requests(self, concurrent_count=10):
        """Test concurrent PUT requests"""
        print(f"\n🚀 Testing {concurrent_count} Concurrent PUT Requests...")
        
        if not self.admin_token:
            self.log_result("Concurrent PUT Test", False, "No admin token available")
            return
        
        if not self.product_id:
            self.log_result("Concurrent PUT Test", False, "No product ID available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Create concurrent PUT requests
        async def make_put_request(request_id):
            update_data = {
                "name": f"Concurrent Test {request_id}",
                "description": f"Concurrent update {request_id}"
            }
            
            try:
                async with self.session.put(f"{API_BASE}/admin/products/{self.product_id}", 
                                          json=update_data, headers=headers) as resp:
                    if resp.status == 200:
                        return (request_id, True, f"Success (200)")
                    else:
                        error_text = await resp.text()
                        return (request_id, False, f"Status {resp.status}: {error_text}")
            except Exception as e:
                return (request_id, False, f"Exception: {str(e)}")
        
        # Execute concurrent requests
        tasks = [make_put_request(i+1) for i in range(concurrent_count)]
        results = await asyncio.gather(*tasks)
        
        success_count = 0
        failure_count = 0
        
        for request_id, success, details in results:
            if success:
                success_count += 1
                self.log_result(f"Concurrent PUT {request_id}", True, details)
            else:
                failure_count += 1
                self.log_result(f"Concurrent PUT {request_id}", False, details)
        
        print(f"\n📊 Concurrent Results: {success_count} successes, {failure_count} failures out of {concurrent_count} requests")
        
        if failure_count > 0:
            failure_rate = (failure_count / concurrent_count) * 100
            print(f"❌ Failure rate: {failure_rate:.1f}%")
            return False
        else:
            print("✅ All concurrent requests succeeded")
            return True
    
    async def test_mixed_request_types(self, iterations=15):
        """Test mixing GET and PUT requests to see if there's a pattern"""
        print(f"\n🔀 Testing Mixed GET/PUT Requests ({iterations} iterations)...")
        
        if not self.admin_token:
            self.log_result("Mixed Request Test", False, "No admin token available")
            return
        
        if not self.product_id:
            self.log_result("Mixed Request Test", False, "No product ID available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        success_count = 0
        failure_count = 0
        
        for i in range(iterations):
            # Alternate between GET and PUT requests
            if i % 2 == 0:
                # GET request
                try:
                    async with self.session.get(f"{API_BASE}/admin/inventory", headers=headers) as resp:
                        if resp.status == 200:
                            success_count += 1
                            self.log_result(f"GET Request {i+1}", True, "Success (200)")
                        else:
                            failure_count += 1
                            error_text = await resp.text()
                            self.log_result(f"GET Request {i+1}", False, f"Status {resp.status}: {error_text}")
                except Exception as e:
                    failure_count += 1
                    self.log_result(f"GET Request {i+1}", False, f"Exception: {str(e)}")
            else:
                # PUT request
                update_data = {
                    "name": f"Mixed Test Update {i+1}",
                    "description": f"Mixed test iteration {i+1}"
                }
                
                try:
                    async with self.session.put(f"{API_BASE}/admin/products/{self.product_id}", 
                                              json=update_data, headers=headers) as resp:
                        if resp.status == 200:
                            success_count += 1
                            self.log_result(f"PUT Request {i+1}", True, "Success (200)")
                        else:
                            failure_count += 1
                            error_text = await resp.text()
                            self.log_result(f"PUT Request {i+1}", False, f"Status {resp.status}: {error_text}")
                except Exception as e:
                    failure_count += 1
                    self.log_result(f"PUT Request {i+1}", False, f"Exception: {str(e)}")
            
            # Small delay between requests
            await asyncio.sleep(0.05)
        
        print(f"\n📊 Mixed Results: {success_count} successes, {failure_count} failures out of {iterations} requests")
        
        if failure_count > 0:
            failure_rate = (failure_count / iterations) * 100
            print(f"❌ Failure rate: {failure_rate:.1f}%")
            return False
        else:
            print("✅ All mixed requests succeeded")
            return True
    
    async def test_token_refresh_scenario(self):
        """Test authentication after getting a fresh token"""
        print("\n🔄 Testing Fresh Token Scenario...")
        
        # Get a fresh token
        if not await self.authenticate():
            self.log_result("Fresh Token Test", False, "Failed to get fresh token")
            return
        
        if not self.product_id:
            self.log_result("Fresh Token Test", False, "No product ID available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        update_data = {
            "name": "Fresh Token Test",
            "description": "Testing with freshly obtained token"
        }
        
        try:
            async with self.session.put(f"{API_BASE}/admin/products/{self.product_id}", 
                                      json=update_data, headers=headers) as resp:
                if resp.status == 200:
                    self.log_result("Fresh Token PUT", True, "Success with fresh token")
                    return True
                else:
                    error_text = await resp.text()
                    self.log_result("Fresh Token PUT", False, f"Status {resp.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_result("Fresh Token PUT", False, f"Exception: {str(e)}")
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("🧪 INTERMITTENT AUTHENTICATION TEST SUMMARY")
        print("="*70)
        
        passed = sum(1 for result in self.test_results if result['success'])
        failed = len(self.test_results) - passed
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/len(self.test_results)*100):.1f}%")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            failure_patterns = {}
            for result in self.test_results:
                if not result['success']:
                    print(f"  • [{result['timestamp']}] {result['test']}: {result['details']}")
                    
                    # Analyze failure patterns
                    if 'PUT' in result['test']:
                        failure_patterns['PUT'] = failure_patterns.get('PUT', 0) + 1
                    if 'GET' in result['test']:
                        failure_patterns['GET'] = failure_patterns.get('GET', 0) + 1
                    if '401' in result['details']:
                        failure_patterns['401_errors'] = failure_patterns.get('401_errors', 0) + 1
            
            if failure_patterns:
                print("\n📊 FAILURE PATTERNS:")
                for pattern, count in failure_patterns.items():
                    print(f"  • {pattern}: {count} failures")
        
        return passed, failed

async def main():
    """Run intermittent authentication tests"""
    print("🚀 Starting Intermittent Authentication Issue Tests")
    print(f"Testing against: {API_BASE}")
    
    async with IntermittentAuthTester() as tester:
        # Authenticate first
        if not await tester.authenticate():
            print("❌ Failed to authenticate - cannot run tests")
            return False
        
        # Run tests to try to reproduce the intermittent issue
        await tester.test_repeated_put_requests(20)
        await tester.test_concurrent_put_requests(10)
        await tester.test_mixed_request_types(15)
        await tester.test_token_refresh_scenario()
        
        # Print summary
        passed, failed = tester.print_summary()
        
        return failed == 0

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)