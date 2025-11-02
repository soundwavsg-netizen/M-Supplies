#!/usr/bin/env python3
"""
Specific 422 Image Upload Error Debug Script
Reproduces the exact error reported by user: "422 Unprocessable Content" when uploading "m-supplies-logo-white.png"
"""

import asyncio
import aiohttp
import json
import os
import io
from PIL import Image

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://smart-retail-ai-6.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials
ADMIN_CREDENTIALS = {
    "email": "admin@polymailer.com",
    "password": "admin123"
}

async def debug_422_error():
    """Debug the specific 422 error reported by user"""
    print("🚨 DEBUGGING SPECIFIC 422 IMAGE UPLOAD ERROR")
    print("User reported: '422 Unprocessable Content' when uploading 'm-supplies-logo-white.png image/png 28007' (28KB PNG)")
    print("Error response: {detail: Array(1)}")
    print("Frontend FormData field name: 'files' for multiple files")
    print()
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Authenticate
        print("🔐 Step 1: Authenticating...")
        async with session.post(f"{API_BASE}/auth/login", json=ADMIN_CREDENTIALS) as resp:
            if resp.status == 200:
                data = await resp.json()
                admin_token = data.get('access_token')
                print(f"✅ Admin authenticated: {admin_token[:20]}...")
            else:
                print(f"❌ Authentication failed: {resp.status}")
                return
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Step 2: Create a 28KB PNG file similar to user's file
        print("\n📁 Step 2: Creating test file similar to user's...")
        
        # Create a larger image to get closer to 28KB
        test_image = Image.new('RGB', (400, 400), color='white')
        # Add some pattern to increase file size
        for x in range(0, 400, 20):
            for y in range(0, 400, 20):
                test_image.putpixel((x, y), (0, 0, 0))  # Black pixels
        
        image_buffer = io.BytesIO()
        test_image.save(image_buffer, format='PNG', optimize=False)
        file_size = len(image_buffer.getvalue())
        image_buffer.seek(0)
        
        print(f"✅ Created PNG file: {file_size} bytes (target: ~28KB)")
        
        # Step 3: Test exact scenarios that might cause 422
        print("\n🔍 Step 3: Testing scenarios that might cause 422...")
        
        # Scenario 1: Empty files array (common frontend issue)
        print("\n--- Scenario 1: Empty files array ---")
        try:
            form_data = aiohttp.FormData()
            # Add empty files field
            form_data.add_field('files', b'', filename='', content_type='')
            
            async with session.post(f"{API_BASE}/admin/upload/images", 
                                  data=form_data, headers=headers) as resp:
                response_text = await resp.text()
                print(f"Status: {resp.status}")
                
                if resp.status == 422:
                    try:
                        error_data = json.loads(response_text)
                        detail = error_data.get('detail', [])
                        print(f"✅ 422 Error reproduced!")
                        print(f"Detail: {detail}")
                        if detail and isinstance(detail, list):
                            for i, error in enumerate(detail):
                                print(f"  Error {i+1}: {error}")
                    except json.JSONDecodeError:
                        print(f"Response: {response_text}")
                else:
                    print(f"Response: {response_text}")
        except Exception as e:
            print(f"Exception: {e}")
        
        # Scenario 2: Wrong content type
        print("\n--- Scenario 2: Wrong content type ---")
        image_buffer.seek(0)
        try:
            form_data = aiohttp.FormData()
            form_data.add_field('files', image_buffer, filename='m-supplies-logo-white.png', content_type='application/octet-stream')
            
            async with session.post(f"{API_BASE}/admin/upload/images", 
                                  data=form_data, headers=headers) as resp:
                response_text = await resp.text()
                print(f"Status: {resp.status}")
                
                if resp.status == 422:
                    try:
                        error_data = json.loads(response_text)
                        detail = error_data.get('detail', [])
                        print(f"✅ 422 Error reproduced!")
                        print(f"Detail: {detail}")
                    except json.JSONDecodeError:
                        print(f"Response: {response_text}")
                else:
                    print(f"Response: {response_text}")
        except Exception as e:
            print(f"Exception: {e}")
        
        # Scenario 3: Missing filename
        print("\n--- Scenario 3: Missing filename ---")
        image_buffer.seek(0)
        try:
            form_data = aiohttp.FormData()
            form_data.add_field('files', image_buffer, filename='', content_type='image/png')
            
            async with session.post(f"{API_BASE}/admin/upload/images", 
                                  data=form_data, headers=headers) as resp:
                response_text = await resp.text()
                print(f"Status: {resp.status}")
                
                if resp.status == 422:
                    try:
                        error_data = json.loads(response_text)
                        detail = error_data.get('detail', [])
                        print(f"✅ 422 Error reproduced!")
                        print(f"Detail: {detail}")
                    except json.JSONDecodeError:
                        print(f"Response: {response_text}")
                else:
                    print(f"Response: {response_text}")
        except Exception as e:
            print(f"Exception: {e}")
        
        # Scenario 4: Invalid file extension in filename
        print("\n--- Scenario 4: Invalid file extension ---")
        image_buffer.seek(0)
        try:
            form_data = aiohttp.FormData()
            form_data.add_field('files', image_buffer, filename='m-supplies-logo-white.txt', content_type='image/png')
            
            async with session.post(f"{API_BASE}/admin/upload/images", 
                                  data=form_data, headers=headers) as resp:
                response_text = await resp.text()
                print(f"Status: {resp.status}")
                
                if resp.status == 422:
                    try:
                        error_data = json.loads(response_text)
                        detail = error_data.get('detail', [])
                        print(f"✅ 422 Error reproduced!")
                        print(f"Detail: {detail}")
                    except json.JSONDecodeError:
                        print(f"Response: {response_text}")
                elif resp.status == 400:
                    print(f"Got 400 instead of 422: {response_text}")
                else:
                    print(f"Response: {response_text}")
        except Exception as e:
            print(f"Exception: {e}")
        
        # Scenario 5: Corrupted file data
        print("\n--- Scenario 5: Corrupted file data ---")
        try:
            corrupted_data = b'corrupted image data that is not a valid PNG'
            form_data = aiohttp.FormData()
            form_data.add_field('files', corrupted_data, filename='m-supplies-logo-white.png', content_type='image/png')
            
            async with session.post(f"{API_BASE}/admin/upload/images", 
                                  data=form_data, headers=headers) as resp:
                response_text = await resp.text()
                print(f"Status: {resp.status}")
                
                if resp.status == 422:
                    try:
                        error_data = json.loads(response_text)
                        detail = error_data.get('detail', [])
                        print(f"✅ 422 Error reproduced!")
                        print(f"Detail: {detail}")
                    except json.JSONDecodeError:
                        print(f"Response: {response_text}")
                else:
                    print(f"Response: {response_text}")
        except Exception as e:
            print(f"Exception: {e}")
        
        # Scenario 6: Multiple files with one invalid
        print("\n--- Scenario 6: Multiple files with one invalid ---")
        image_buffer.seek(0)
        try:
            form_data = aiohttp.FormData()
            # Add valid file
            form_data.add_field('files', image_buffer, filename='valid.png', content_type='image/png')
            # Add invalid file
            form_data.add_field('files', b'invalid', filename='invalid.txt', content_type='text/plain')
            
            async with session.post(f"{API_BASE}/admin/upload/images", 
                                  data=form_data, headers=headers) as resp:
                response_text = await resp.text()
                print(f"Status: {resp.status}")
                
                if resp.status == 422:
                    try:
                        error_data = json.loads(response_text)
                        detail = error_data.get('detail', [])
                        print(f"✅ 422 Error reproduced!")
                        print(f"Detail: {detail}")
                    except json.JSONDecodeError:
                        print(f"Response: {response_text}")
                elif resp.status == 400:
                    print(f"Got 400 instead of 422: {response_text}")
                else:
                    print(f"Response: {response_text}")
        except Exception as e:
            print(f"Exception: {e}")
        
        # Scenario 7: Exact working case for comparison
        print("\n--- Scenario 7: Working case for comparison ---")
        image_buffer.seek(0)
        try:
            form_data = aiohttp.FormData()
            form_data.add_field('files', image_buffer, filename='m-supplies-logo-white.png', content_type='image/png')
            
            async with session.post(f"{API_BASE}/admin/upload/images", 
                                  data=form_data, headers=headers) as resp:
                response_text = await resp.text()
                print(f"Status: {resp.status}")
                
                if resp.status == 200:
                    try:
                        data = json.loads(response_text)
                        print(f"✅ Success: {data}")
                    except json.JSONDecodeError:
                        print(f"Response: {response_text}")
                else:
                    print(f"❌ Failed: {response_text}")
        except Exception as e:
            print(f"Exception: {e}")
        
        print("\n🔍 CONCLUSION:")
        print("Based on the tests above, the 422 error is likely caused by:")
        print("1. Empty or missing file data")
        print("2. Invalid file extension in filename")
        print("3. Missing filename")
        print("4. Wrong field name (should be 'files' for multiple upload)")
        print("5. Pydantic validation errors in FastAPI")

if __name__ == "__main__":
    asyncio.run(debug_422_error())