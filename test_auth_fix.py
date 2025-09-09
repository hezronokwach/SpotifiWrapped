#!/usr/bin/env python3
"""
Test script to verify the authentication fix is working
"""

import requests
import json
import time

BASE_URL = 'http://localhost:5000'

def test_health_check():
    """Test that health check works without authentication"""
    print("🔍 Testing health check...")
    response = requests.get(f'{BASE_URL}/api/health')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Health check passed")
        return True
    else:
        print("❌ Health check failed")
        return False

def test_protected_endpoint_without_token():
    """Test that protected endpoints return 401 without token"""
    print("\n🔍 Testing protected endpoint without token...")
    response = requests.get(f'{BASE_URL}/api/user/profile')
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print("✅ Protected endpoint correctly returns 401")
        return True
    else:
        print("❌ Protected endpoint should return 401")
        return False

def test_protected_endpoint_with_invalid_token():
    """Test that protected endpoints return 401 with invalid token"""
    print("\n🔍 Testing protected endpoint with invalid token...")
    headers = {'Authorization': 'Bearer invalid_token_here'}
    response = requests.get(f'{BASE_URL}/api/user/profile', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print("✅ Protected endpoint correctly rejects invalid token")
        return True
    else:
        print("❌ Protected endpoint should reject invalid token")
        return False

def test_auth_endpoints():
    """Test that auth endpoints work without token"""
    print("\n🔍 Testing auth endpoints...")
    
    # Test validate credentials endpoint
    response = requests.post(f'{BASE_URL}/api/auth/validate-credentials', 
                           json={'clientId': 'test', 'clientSecret': 'test'})
    print(f"Validate credentials status: {response.status_code}")
    
    if response.status_code in [200, 400]:  # 400 is expected for invalid credentials
        print("✅ Auth endpoints accessible without token")
        return True
    else:
        print("❌ Auth endpoints should be accessible without token")
        return False

def main():
    """Run all authentication tests"""
    print("🚀 Starting authentication fix tests...\n")
    
    tests = [
        test_health_check,
        test_protected_endpoint_without_token,
        test_protected_endpoint_with_invalid_token,
        test_auth_endpoints
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All authentication tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Check the Flask app configuration.")
        return False

if __name__ == '__main__':
    main()