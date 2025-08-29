#!/usr/bin/env python3
"""
🧪 Test Firebase-only app locally
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_app():
    print("🧪 Testing Firebase-only app...")
    
    # Test 1: Root endpoint
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Root endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
    
    # Test 2: Health check
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 3: User registration
    try:
        user_data = {
            "phone_number": "09123456789",
            "email": "test@example.com", 
            "display_name": "Test User"
        }
        response = requests.post(
            f"{BASE_URL}/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ User registration: {response.status_code}")
        result = response.json()
        print(f"   User UID: {result.get('user', {}).get('uid', 'N/A')}")
        
        # Store for login test
        phone_number = user_data["phone_number"]
        
    except Exception as e:
        print(f"❌ User registration failed: {e}")
        phone_number = "09123456789"  # Fallback
    
    # Test 4: User login
    try:
        login_data = {"phone_number": phone_number}
        response = requests.post(
            f"{BASE_URL}/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ User login: {response.status_code}")
        result = response.json()
        print(f"   Balance: ₱{result.get('user', {}).get('balance', 0)}")
        print(f"   Bonus: ₱{result.get('user', {}).get('non_withdrawable_bonus', 0)}")
        
    except Exception as e:
        print(f"❌ User login failed: {e}")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    print("🚀 Starting app test...")
    print("📝 Make sure the app is running: python firebase_only_app.py")
    print()
    time.sleep(1)
    test_app()
