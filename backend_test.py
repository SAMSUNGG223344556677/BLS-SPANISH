#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for BLS-SPANISH System
Tests all 21 endpoints across 3 main modules:
- Applicant Management APIs (6 endpoints)
- Login Credentials Management APIs (8 endpoints) 
- BLS Automation Core System APIs (7 endpoints)
"""

import asyncio
import aiohttp
import json
import websockets
from datetime import datetime
import sys
import os

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except:
        pass
    return "https://44c25e8e-2b3e-4316-b962-665a2581e188.preview.emergentagent.com"

BASE_URL = get_backend_url()
API_URL = f"{BASE_URL}/api"

class BLSBackendTester:
    def __init__(self):
        self.session = None
        self.test_results = {
            "applicant_management": {},
            "credentials_management": {},
            "bls_automation": {},
            "websocket": {},
            "summary": {"passed": 0, "failed": 0, "total": 0}
        }
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
            
    def log_result(self, category, test_name, success, message="", data=None):
        """Log test result"""
        self.test_results[category][test_name] = {
            "success": success,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results["summary"]["total"] += 1
        if success:
            self.test_results["summary"]["passed"] += 1
            print(f"✅ {category}.{test_name}: {message}")
        else:
            self.test_results["summary"]["failed"] += 1
            print(f"❌ {category}.{test_name}: {message}")
            
    async def test_api_endpoint(self, method, endpoint, data=None, expected_status=200):
        """Generic API endpoint tester"""
        try:
            url = f"{API_URL}{endpoint}"
            
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    response_data = await response.json()
                    return response.status, response_data
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    response_data = await response.json()
                    return response.status, response_data
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data) as response:
                    response_data = await response.json()
                    return response.status, response_data
            elif method.upper() == "DELETE":
                async with self.session.delete(url) as response:
                    response_data = await response.json()
                    return response.status, response_data
                    
        except Exception as e:
            return 500, {"error": str(e)}

    # ==================== APPLICANT MANAGEMENT TESTS ====================
    
    async def test_applicant_management(self):
        """Test all 6 Applicant Management APIs"""
        print("\n🧪 Testing Applicant Management APIs...")
        
        # Test data
        applicant_data = {
            "first_name": "Maria",
            "last_name": "Garcia",
            "email": "maria.garcia@email.com",
            "phone": "+34612345678",
            "passport_number": "ESP123456789",
            "nationality": "Spanish",
            "date_of_birth": "1990-05-15",
            "is_primary": True
        }
        
        applicant_data_2 = {
            "first_name": "Carlos",
            "last_name": "Rodriguez",
            "email": "carlos.rodriguez@email.com", 
            "phone": "+34687654321",
            "passport_number": "ESP987654321",
            "nationality": "Spanish",
            "date_of_birth": "1985-08-22",
            "is_primary": False
        }
        
        created_applicant_id = None
        created_applicant_id_2 = None
        
        # 1. POST /api/applicants - Create new applicant
        try:
            status, response = await self.test_api_endpoint("POST", "/applicants", applicant_data)
            if status == 200 and "id" in response:
                created_applicant_id = response["id"]
                self.log_result("applicant_management", "create_applicant", True, 
                              f"Created applicant with ID: {created_applicant_id}")
            else:
                self.log_result("applicant_management", "create_applicant", False, 
                              f"Failed to create applicant. Status: {status}, Response: {response}")
        except Exception as e:
            self.log_result("applicant_management", "create_applicant", False, f"Exception: {str(e)}")
            
        # 2. Create second applicant to test primary designation logic
        try:
            status, response = await self.test_api_endpoint("POST", "/applicants", applicant_data_2)
            if status == 200 and "id" in response:
                created_applicant_id_2 = response["id"]
                self.log_result("applicant_management", "create_second_applicant", True, 
                              f"Created second applicant with ID: {created_applicant_id_2}")
            else:
                self.log_result("applicant_management", "create_second_applicant", False, 
                              f"Failed to create second applicant. Status: {status}")
        except Exception as e:
            self.log_result("applicant_management", "create_second_applicant", False, f"Exception: {str(e)}")
            
        # 3. GET /api/applicants - List all applicants
        try:
            status, response = await self.test_api_endpoint("GET", "/applicants")
            if status == 200 and isinstance(response, list):
                self.log_result("applicant_management", "list_applicants", True, 
                              f"Retrieved {len(response)} applicants")
            else:
                self.log_result("applicant_management", "list_applicants", False, 
                              f"Failed to list applicants. Status: {status}")
        except Exception as e:
            self.log_result("applicant_management", "list_applicants", False, f"Exception: {str(e)}")
            
        # 4. GET /api/applicants/{id} - Get specific applicant
        if created_applicant_id:
            try:
                status, response = await self.test_api_endpoint("GET", f"/applicants/{created_applicant_id}")
                if status == 200 and response.get("id") == created_applicant_id:
                    self.log_result("applicant_management", "get_applicant_by_id", True, 
                                  f"Retrieved applicant: {response.get('first_name')} {response.get('last_name')}")
                else:
                    self.log_result("applicant_management", "get_applicant_by_id", False, 
                                  f"Failed to get applicant by ID. Status: {status}")
            except Exception as e:
                self.log_result("applicant_management", "get_applicant_by_id", False, f"Exception: {str(e)}")
                
        # 5. GET /api/applicants/primary/info - Get primary applicant
        try:
            status, response = await self.test_api_endpoint("GET", "/applicants/primary/info")
            if status == 200 and response.get("is_primary") == True:
                self.log_result("applicant_management", "get_primary_applicant", True, 
                              f"Retrieved primary applicant: {response.get('first_name')} {response.get('last_name')}")
            else:
                self.log_result("applicant_management", "get_primary_applicant", False, 
                              f"Failed to get primary applicant. Status: {status}")
        except Exception as e:
            self.log_result("applicant_management", "get_primary_applicant", False, f"Exception: {str(e)}")
            
        # 6. PUT /api/applicants/{id} - Update applicant
        if created_applicant_id:
            try:
                update_data = applicant_data.copy()
                update_data["phone"] = "+34600000000"  # Update phone number
                status, response = await self.test_api_endpoint("PUT", f"/applicants/{created_applicant_id}", update_data)
                if status == 200 and response.get("phone") == "+34600000000":
                    self.log_result("applicant_management", "update_applicant", True, 
                                  f"Updated applicant phone to: {response.get('phone')}")
                else:
                    self.log_result("applicant_management", "update_applicant", False, 
                                  f"Failed to update applicant. Status: {status}")
            except Exception as e:
                self.log_result("applicant_management", "update_applicant", False, f"Exception: {str(e)}")
                
        # 7. DELETE /api/applicants/{id} - Delete applicant
        if created_applicant_id_2:  # Delete the second applicant
            try:
                status, response = await self.test_api_endpoint("DELETE", f"/applicants/{created_applicant_id_2}")
                if status == 200:
                    self.log_result("applicant_management", "delete_applicant", True, 
                                  "Successfully deleted applicant")
                else:
                    self.log_result("applicant_management", "delete_applicant", False, 
                                  f"Failed to delete applicant. Status: {status}")
            except Exception as e:
                self.log_result("applicant_management", "delete_applicant", False, f"Exception: {str(e)}")

    # ==================== CREDENTIALS MANAGEMENT TESTS ====================
    
    async def test_credentials_management(self):
        """Test all 8 Login Credentials Management APIs"""
        print("\n🔐 Testing Login Credentials Management APIs...")
        
        # Test data
        credential_data = {
            "email": "maria.garcia@blsspain.com",
            "password": "SecurePass123!",
            "name": "Maria Garcia BLS Account",
            "is_primary": True,
            "is_active": True
        }
        
        credential_data_2 = {
            "email": "carlos.rodriguez@blsspain.com",
            "password": "AnotherPass456!",
            "name": "Carlos Rodriguez BLS Account", 
            "is_primary": False,
            "is_active": True
        }
        
        created_credential_id = None
        created_credential_id_2 = None
        
        # 1. POST /api/credentials - Create new credentials
        try:
            status, response = await self.test_api_endpoint("POST", "/credentials", credential_data)
            if status == 200 and "id" in response:
                created_credential_id = response["id"]
                self.log_result("credentials_management", "create_credential", True, 
                              f"Created credential with ID: {created_credential_id}")
            else:
                self.log_result("credentials_management", "create_credential", False, 
                              f"Failed to create credential. Status: {status}")
        except Exception as e:
            self.log_result("credentials_management", "create_credential", False, f"Exception: {str(e)}")
            
        # 2. Create second credential to test primary designation logic
        try:
            status, response = await self.test_api_endpoint("POST", "/credentials", credential_data_2)
            if status == 200 and "id" in response:
                created_credential_id_2 = response["id"]
                self.log_result("credentials_management", "create_second_credential", True, 
                              f"Created second credential with ID: {created_credential_id_2}")
            else:
                self.log_result("credentials_management", "create_second_credential", False, 
                              f"Failed to create second credential. Status: {status}")
        except Exception as e:
            self.log_result("credentials_management", "create_second_credential", False, f"Exception: {str(e)}")
            
        # 3. GET /api/credentials - List all credentials
        try:
            status, response = await self.test_api_endpoint("GET", "/credentials")
            if status == 200 and isinstance(response, list):
                self.log_result("credentials_management", "list_credentials", True, 
                              f"Retrieved {len(response)} credentials")
            else:
                self.log_result("credentials_management", "list_credentials", False, 
                              f"Failed to list credentials. Status: {status}")
        except Exception as e:
            self.log_result("credentials_management", "list_credentials", False, f"Exception: {str(e)}")
            
        # 4. GET /api/credentials with filtering (active_only=true)
        try:
            status, response = await self.test_api_endpoint("GET", "/credentials?active_only=true")
            if status == 200 and isinstance(response, list):
                self.log_result("credentials_management", "list_active_credentials", True, 
                              f"Retrieved {len(response)} active credentials")
            else:
                self.log_result("credentials_management", "list_active_credentials", False, 
                              f"Failed to list active credentials. Status: {status}")
        except Exception as e:
            self.log_result("credentials_management", "list_active_credentials", False, f"Exception: {str(e)}")
            
        # 5. GET /api/credentials/{id} - Get specific credential
        if created_credential_id:
            try:
                status, response = await self.test_api_endpoint("GET", f"/credentials/{created_credential_id}")
                if status == 200 and response.get("id") == created_credential_id:
                    self.log_result("credentials_management", "get_credential_by_id", True, 
                                  f"Retrieved credential: {response.get('name')}")
                else:
                    self.log_result("credentials_management", "get_credential_by_id", False, 
                                  f"Failed to get credential by ID. Status: {status}")
            except Exception as e:
                self.log_result("credentials_management", "get_credential_by_id", False, f"Exception: {str(e)}")
                
        # 6. GET /api/credentials/primary/info - Get primary credential
        try:
            status, response = await self.test_api_endpoint("GET", "/credentials/primary/info")
            if status == 200 and response.get("is_primary") == True:
                self.log_result("credentials_management", "get_primary_credential", True, 
                              f"Retrieved primary credential: {response.get('name')}")
            else:
                self.log_result("credentials_management", "get_primary_credential", False, 
                              f"Failed to get primary credential. Status: {status}")
        except Exception as e:
            self.log_result("credentials_management", "get_primary_credential", False, f"Exception: {str(e)}")
            
        # 7. POST /api/credentials/{id}/set-primary - Set credential as primary
        if created_credential_id_2:
            try:
                status, response = await self.test_api_endpoint("POST", f"/credentials/{created_credential_id_2}/set-primary")
                if status == 200:
                    self.log_result("credentials_management", "set_primary_credential", True, 
                                  "Successfully set credential as primary")
                else:
                    self.log_result("credentials_management", "set_primary_credential", False, 
                                  f"Failed to set primary credential. Status: {status}")
            except Exception as e:
                self.log_result("credentials_management", "set_primary_credential", False, f"Exception: {str(e)}")
                
        # 8. POST /api/credentials/{id}/test - Test credential functionality
        if created_credential_id:
            try:
                status, response = await self.test_api_endpoint("POST", f"/credentials/{created_credential_id}/test")
                if status == 200 and response.get("status") == "success":
                    self.log_result("credentials_management", "test_credential", True, 
                                  f"Credential test completed: {response.get('message')}")
                else:
                    self.log_result("credentials_management", "test_credential", False, 
                                  f"Failed to test credential. Status: {status}")
            except Exception as e:
                self.log_result("credentials_management", "test_credential", False, f"Exception: {str(e)}")
                
        # 9. PUT /api/credentials/{id} - Update credential
        if created_credential_id:
            try:
                update_data = credential_data.copy()
                update_data["name"] = "Updated Maria Garcia BLS Account"
                status, response = await self.test_api_endpoint("PUT", f"/credentials/{created_credential_id}", update_data)
                if status == 200 and "Updated" in response.get("name", ""):
                    self.log_result("credentials_management", "update_credential", True, 
                                  f"Updated credential name to: {response.get('name')}")
                else:
                    self.log_result("credentials_management", "update_credential", False, 
                                  f"Failed to update credential. Status: {status}")
            except Exception as e:
                self.log_result("credentials_management", "update_credential", False, f"Exception: {str(e)}")
                
        # 10. DELETE /api/credentials/{id} - Delete credential
        if created_credential_id_2:  # Delete the second credential
            try:
                status, response = await self.test_api_endpoint("DELETE", f"/credentials/{created_credential_id_2}")
                if status == 200:
                    self.log_result("credentials_management", "delete_credential", True, 
                                  "Successfully deleted credential")
                else:
                    self.log_result("credentials_management", "delete_credential", False, 
                                  f"Failed to delete credential. Status: {status}")
            except Exception as e:
                self.log_result("credentials_management", "delete_credential", False, f"Exception: {str(e)}")

    # ==================== BLS AUTOMATION TESTS ====================
    
    async def test_bls_automation(self):
        """Test all 7 BLS Automation Core System APIs"""
        print("\n🤖 Testing BLS Automation Core System APIs...")
        
        # 1. GET /api/bls/status - Get system status
        try:
            status, response = await self.test_api_endpoint("GET", "/bls/status")
            if status == 200 and "is_running" in response:
                self.log_result("bls_automation", "get_system_status", True, 
                              f"System status: {'Running' if response.get('is_running') else 'Stopped'}")
            else:
                self.log_result("bls_automation", "get_system_status", False, 
                              f"Failed to get system status. Status: {status}")
        except Exception as e:
            self.log_result("bls_automation", "get_system_status", False, f"Exception: {str(e)}")
            
        # 2. POST /api/bls/start - Start system
        try:
            status, response = await self.test_api_endpoint("POST", "/bls/start")
            if status == 200 and "started" in response.get("message", "").lower():
                self.log_result("bls_automation", "start_system", True, 
                              "BLS automation system started successfully")
            else:
                self.log_result("bls_automation", "start_system", False, 
                              f"Failed to start system. Status: {status}")
        except Exception as e:
            self.log_result("bls_automation", "start_system", False, f"Exception: {str(e)}")
            
        # 3. POST /api/bls/solve-captcha - Solve captcha
        try:
            captcha_data = {
                "target_number": "7",
                "captcha_images": ["base64image1", "base64image2", "base64image3"]  # Mock base64 images
            }
            status, response = await self.test_api_endpoint("POST", "/bls/solve-captcha", captcha_data)
            if status == 200 and "selected_indices" in response:
                self.log_result("bls_automation", "solve_captcha", True, 
                              f"Captcha solved with confidence: {response.get('confidence', 'N/A')}")
            else:
                self.log_result("bls_automation", "solve_captcha", False, 
                              f"Failed to solve captcha. Status: {status}")
        except Exception as e:
            self.log_result("bls_automation", "solve_captcha", False, f"Exception: {str(e)}")
            
        # 4. POST /api/bls/book-appointment - Book appointment (requires primary applicant and credential)
        try:
            booking_data = {
                "location": "Madrid",
                "visa_type": "Tourist",
                "visa_sub_type": "Short Stay",
                "category": "Normal",
                "appointment_for": "Individual",
                "number_of_members": 1
            }
            status, response = await self.test_api_endpoint("POST", "/bls/book-appointment", booking_data)
            if status == 200 and response.get("status") == "success":
                self.log_result("bls_automation", "book_appointment", True, 
                              f"Appointment booked successfully: {response.get('booking_id')}")
            else:
                self.log_result("bls_automation", "book_appointment", False, 
                              f"Failed to book appointment. Status: {status}, Response: {response}")
        except Exception as e:
            self.log_result("bls_automation", "book_appointment", False, f"Exception: {str(e)}")
            
        # 5. GET /api/bls/bookings - Get booking history
        try:
            status, response = await self.test_api_endpoint("GET", "/bls/bookings")
            if status == 200 and isinstance(response, list):
                self.log_result("bls_automation", "get_bookings", True, 
                              f"Retrieved {len(response)} booking records")
            else:
                self.log_result("bls_automation", "get_bookings", False, 
                              f"Failed to get bookings. Status: {status}")
        except Exception as e:
            self.log_result("bls_automation", "get_bookings", False, f"Exception: {str(e)}")
            
        # 6. POST /api/bls/stop - Stop system
        try:
            status, response = await self.test_api_endpoint("POST", "/bls/stop")
            if status == 200 and "stopped" in response.get("message", "").lower():
                self.log_result("bls_automation", "stop_system", True, 
                              "BLS automation system stopped successfully")
            else:
                self.log_result("bls_automation", "stop_system", False, 
                              f"Failed to stop system. Status: {status}")
        except Exception as e:
            self.log_result("bls_automation", "stop_system", False, f"Exception: {str(e)}")
            
        # 7. Verify system status after stop
        try:
            status, response = await self.test_api_endpoint("GET", "/bls/status")
            if status == 200 and response.get("is_running") == False:
                self.log_result("bls_automation", "verify_system_stopped", True, 
                              "System status correctly shows stopped")
            else:
                self.log_result("bls_automation", "verify_system_stopped", False, 
                              f"System status incorrect after stop. Status: {status}")
        except Exception as e:
            self.log_result("bls_automation", "verify_system_stopped", False, f"Exception: {str(e)}")

    # ==================== WEBSOCKET TESTS ====================
    
    async def test_websocket(self):
        """Test WebSocket connectivity"""
        print("\n🔌 Testing WebSocket connectivity...")
        
        try:
            ws_url = f"{BASE_URL.replace('https://', 'wss://').replace('http://', 'ws://')}/ws"
            
            async with websockets.connect(ws_url) as websocket:
                # Send test message
                test_message = "Hello BLS WebSocket"
                await websocket.send(test_message)
                
                # Wait for response
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                
                if "Echo:" in response and test_message in response:
                    self.log_result("websocket", "connection_test", True, 
                                  f"WebSocket echo successful: {response}")
                else:
                    self.log_result("websocket", "connection_test", False, 
                                  f"Unexpected WebSocket response: {response}")
                    
        except asyncio.TimeoutError:
            self.log_result("websocket", "connection_test", False, "WebSocket connection timeout")
        except Exception as e:
            self.log_result("websocket", "connection_test", False, f"WebSocket error: {str(e)}")

    # ==================== MAIN TEST RUNNER ====================
    
    async def run_all_tests(self):
        """Run all backend tests"""
        print(f"🚀 Starting BLS-SPANISH Backend API Tests")
        print(f"📡 Backend URL: {BASE_URL}")
        print(f"🔗 API Base URL: {API_URL}")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Run all test suites
            await self.test_applicant_management()
            await self.test_credentials_management() 
            await self.test_bls_automation()
            await self.test_websocket()
            
        finally:
            await self.cleanup()
            
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 80)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 80)
        
        summary = self.test_results["summary"]
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"📈 Total: {summary['total']}")
        print(f"📊 Success Rate: {(summary['passed']/summary['total']*100):.1f}%" if summary['total'] > 0 else "0%")
        
        print("\n📋 DETAILED RESULTS BY CATEGORY:")
        
        for category, tests in self.test_results.items():
            if category == "summary":
                continue
                
            print(f"\n🔸 {category.upper().replace('_', ' ')}:")
            passed = sum(1 for test in tests.values() if test["success"])
            total = len(tests)
            
            for test_name, result in tests.items():
                status = "✅" if result["success"] else "❌"
                print(f"  {status} {test_name}: {result['message']}")
                
            print(f"  📊 Category Score: {passed}/{total} ({(passed/total*100):.1f}%)" if total > 0 else "  📊 Category Score: 0/0 (0%)")

if __name__ == "__main__":
    tester = BLSBackendTester()
    asyncio.run(tester.run_all_tests())