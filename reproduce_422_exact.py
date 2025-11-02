#!/usr/bin/env python3
"""
Reproduce the EXACT 422 error by testing Pydantic validation scenarios
"""

import asyncio
import aiohttp
import json
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://smart-retail-ai-6.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials
ADMIN_CREDENTIALS = {
    "email": "admin@polymailer.com",
    "password": "admin123"
}

async def reproduce_exact_422():
    """Reproduce the exact 422 error by testing Pydantic validation"""
    print("🎯 REPRODUCING EXACT 422 PYDANTIC VALIDATION ERROR")
    print("FastAPI route expects: files: List[UploadFile] = File(...)")
    print("422 occurs when Pydantic can't validate the request body")
    print()
    
    async with aiohttp.ClientSession() as session:
        # Authenticate
        async with session.post(f"{API_BASE}/auth/login", json=ADMIN_CREDENTIALS) as resp:
            if resp.status == 200:
                data = await resp.json()
                admin_token = data.get('access_token')
                print(f"✅ Authenticated: {admin_token[:20]}...")
            else:
                print(f"❌ Auth failed: {resp.status}")
                return
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Test 1: No 'files' field at all (should cause 422)
        print("\n🔍 Test 1: Missing 'files' field entirely")
        try:
            form_data = aiohttp.FormData()
            form_data.add_field('wrong_field', b'test', filename='test.png', content_type='image/png')
            
            async with session.post(f"{API_BASE}/admin/upload/images", 
                                  data=form_data, headers=headers) as resp:
                response_text = await resp.text()
                print(f"Status: {resp.status}")
                
                if resp.status == 422:
                    try:
                        error_data = json.loads(response_text)
                        detail = error_data.get('detail', [])
                        print(f"✅ 422 REPRODUCED!")
                        print(f"Detail array: {detail}")
                        if detail and isinstance(detail, list):
                            for i, error in enumerate(detail):
                                print(f"  Error {i+1}: {error}")
                                if isinstance(error, dict):
                                    print(f"    Type: {error.get('type')}")
                                    print(f"    Location: {error.get('loc')}")
                                    print(f"    Message: {error.get('msg')}")
                    except json.JSONDecodeError:
                        print(f"Raw response: {response_text}")
                else:
                    print(f"Got {resp.status} instead of 422: {response_text}")
        except Exception as e:
            print(f"Exception: {e}")
        
        # Test 2: Empty form data (should cause 422)
        print("\n🔍 Test 2: Completely empty form data")
        try:
            form_data = aiohttp.FormData()
            # Don't add any fields
            
            async with session.post(f"{API_BASE}/admin/upload/images", 
                                  data=form_data, headers=headers) as resp:
                response_text = await resp.text()
                print(f"Status: {resp.status}")
                
                if resp.status == 422:
                    try:
                        error_data = json.loads(response_text)
                        detail = error_data.get('detail', [])
                        print(f"✅ 422 REPRODUCED!")
                        print(f"Detail array: {detail}")
                        if detail and isinstance(detail, list):
                            for i, error in enumerate(detail):
                                print(f"  Error {i+1}: {error}")
                    except json.JSONDecodeError:
                        print(f"Raw response: {response_text}")
                else:
                    print(f"Got {resp.status} instead of 422: {response_text}")
        except Exception as e:
            print(f"Exception: {e}")
        
        # Test 3: Send JSON instead of form data (should cause 422)
        print("\n🔍 Test 3: Send JSON instead of multipart form data")
        try:
            json_data = {"files": ["test.png"]}
            
            async with session.post(f"{API_BASE}/admin/upload/images", 
                                  json=json_data, headers=headers) as resp:
                response_text = await resp.text()
                print(f"Status: {resp.status}")
                
                if resp.status == 422:
                    try:
                        error_data = json.loads(response_text)
                        detail = error_data.get('detail', [])
                        print(f"✅ 422 REPRODUCED!")
                        print(f"Detail array: {detail}")
                        if detail and isinstance(detail, list):
                            for i, error in enumerate(detail):
                                print(f"  Error {i+1}: {error}")
                    except json.JSONDecodeError:
                        print(f"Raw response: {response_text}")
                else:
                    print(f"Got {resp.status} instead of 422: {response_text}")
        except Exception as e:
            print(f"Exception: {e}")
        
        # Test 4: Send wrong content-type header
        print("\n🔍 Test 4: Wrong Content-Type header")
        try:
            headers_with_wrong_content_type = headers.copy()
            headers_with_wrong_content_type['Content-Type'] = 'application/json'
            
            form_data = aiohttp.FormData()
            form_data.add_field('files', b'test', filename='test.png', content_type='image/png')
            
            async with session.post(f"{API_BASE}/admin/upload/images", 
                                  data=form_data, headers=headers_with_wrong_content_type) as resp:
                response_text = await resp.text()
                print(f"Status: {resp.status}")
                
                if resp.status == 422:
                    try:
                        error_data = json.loads(response_text)
                        detail = error_data.get('detail', [])
                        print(f"✅ 422 REPRODUCED!")
                        print(f"Detail array: {detail}")
                    except json.JSONDecodeError:
                        print(f"Raw response: {response_text}")
                else:
                    print(f"Got {resp.status} instead of 422: {response_text}")
        except Exception as e:
            print(f"Exception: {e}")
        
        # Test 5: Send raw data without proper multipart encoding
        print("\n🔍 Test 5: Raw data without multipart encoding")
        try:
            raw_data = b'raw file data'
            headers_raw = headers.copy()
            headers_raw['Content-Type'] = 'application/octet-stream'
            
            async with session.post(f"{API_BASE}/admin/upload/images", 
                                  data=raw_data, headers=headers_raw) as resp:
                response_text = await resp.text()
                print(f"Status: {resp.status}")
                
                if resp.status == 422:
                    try:
                        error_data = json.loads(response_text)
                        detail = error_data.get('detail', [])
                        print(f"✅ 422 REPRODUCED!")
                        print(f"Detail array: {detail}")
                    except json.JSONDecodeError:
                        print(f"Raw response: {response_text}")
                else:
                    print(f"Got {resp.status} instead of 422: {response_text}")
        except Exception as e:
            print(f"Exception: {e}")
        
        # Test 6: Malformed multipart data
        print("\n🔍 Test 6: Malformed multipart boundary")
        try:
            malformed_data = b'--boundary\r\nContent-Disposition: form-data; name="files"\r\n\r\ntest\r\n--boundary--'
            headers_malformed = headers.copy()
            headers_malformed['Content-Type'] = 'multipart/form-data; boundary=boundary'
            
            async with session.post(f"{API_BASE}/admin/upload/images", 
                                  data=malformed_data, headers=headers_malformed) as resp:
                response_text = await resp.text()
                print(f"Status: {resp.status}")
                
                if resp.status == 422:
                    try:
                        error_data = json.loads(response_text)
                        detail = error_data.get('detail', [])
                        print(f"✅ 422 REPRODUCED!")
                        print(f"Detail array: {detail}")
                    except json.JSONDecodeError:
                        print(f"Raw response: {response_text}")
                else:
                    print(f"Got {resp.status} instead of 422: {response_text}")
        except Exception as e:
            print(f"Exception: {e}")
        
        print("\n🎯 SUMMARY:")
        print("The 422 'Unprocessable Content' error occurs when:")
        print("1. The 'files' field is missing from the form data")
        print("2. The request body cannot be parsed as multipart/form-data")
        print("3. Pydantic cannot validate the request against List[UploadFile]")
        print("4. The Content-Type header is incorrect for file uploads")
        print()
        print("This suggests the frontend issue is likely:")
        print("- Not including the 'files' field in FormData")
        print("- Sending empty FormData")
        print("- Incorrect Content-Type header")
        print("- Malformed multipart request")

if __name__ == "__main__":
    asyncio.run(reproduce_exact_422())