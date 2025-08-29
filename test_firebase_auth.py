#!/usr/bin/env python3
"""
Test Firebase Authentication System
This script tests if a user can register and login successfully with Firebase
"""

import os
import sys
import django
import hashlib

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from firebase_auth import FirebaseAuth

def test_firebase_auth():
    """Test Firebase authentication flow"""
    
    print("🔥 Testing Firebase Authentication System")
    print("=" * 50)
    
    # Initialize Firebase Auth
    firebase_auth = FirebaseAuth()
    
    if not firebase_auth.db:
        print("❌ Firebase not available for testing")
        return False
    
    # Test data
    test_phone = "+639123456789"
    test_password = "testpassword123"
    test_hashed_password = hashlib.sha256(test_password.encode()).hexdigest()
    
    print(f"📱 Test phone: {test_phone}")
    print(f"🔑 Test password: {test_password}")
    print(f"🔐 Hashed password: {test_hashed_password[:20]}...")
    
    # Test 1: Create test user in Firebase
    print("\n1️⃣ Creating test user in Firebase...")
    try:
        firebase_key = firebase_auth.get_firebase_key(test_phone)
        user_data = {
            'phone_number': test_phone,
            'password': test_hashed_password,
            'balance': 100.0,
            'status': 'active',
            'created_at': '2025-08-29T12:00:00',
            'registration_bonus_claimed': True
        }
        
        firebase_auth.db.child('users').child(firebase_key).set(user_data)
        print(f"✅ Test user created with key: {firebase_key}")
        
    except Exception as e:
        print(f"❌ Failed to create test user: {e}")
        return False
    
    # Test 2: Find user by phone
    print("\n2️⃣ Testing find_user_by_phone...")
    found_user = firebase_auth.find_user_by_phone(test_phone)
    if found_user:
        print(f"✅ User found: {found_user.get('phone_number')}")
        print(f"   Balance: {found_user.get('balance')}")
        print(f"   Status: {found_user.get('status')}")
    else:
        print("❌ User not found")
        return False
    
    # Test 3: Test authentication with correct password
    print("\n3️⃣ Testing authentication with correct password...")
    auth_result = firebase_auth.authenticate_user(test_phone, test_password)
    if auth_result['success']:
        print("✅ Authentication successful!")
        print(f"   Firebase key: {auth_result['firebase_key']}")
        print(f"   User balance: {auth_result['user_data'].get('balance')}")
    else:
        print(f"❌ Authentication failed: {auth_result['error']}")
        return False
    
    # Test 4: Test authentication with wrong password
    print("\n4️⃣ Testing authentication with wrong password...")
    auth_result = firebase_auth.authenticate_user(test_phone, "wrongpassword")
    if not auth_result['success']:
        print(f"✅ Correctly rejected wrong password: {auth_result['error']}")
    else:
        print("❌ Should have rejected wrong password!")
        return False
    
    # Test 5: Test phone normalization
    print("\n5️⃣ Testing phone number normalization...")
    test_variations = [
        "09123456789",
        "639123456789", 
        "+639123456789",
        "9123456789",
        "063 9123456789"
    ]
    
    for variation in test_variations:
        normalized = firebase_auth.normalize_phone(variation)
        print(f"   {variation} → {normalized}")
        if normalized == test_phone:
            print(f"   ✅ Normalized correctly")
        else:
            print(f"   ❌ Normalization issue")
    
    # Cleanup: Remove test user
    print("\n🧹 Cleaning up test user...")
    try:
        firebase_auth.db.child('users').child(firebase_key).delete()
        print("✅ Test user removed")
    except Exception as e:
        print(f"⚠️ Could not remove test user: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Firebase Authentication Test Completed Successfully!")
    return True

if __name__ == "__main__":
    try:
        success = test_firebase_auth()
        if success:
            print("\n✅ All tests passed! Firebase authentication is working correctly.")
        else:
            print("\n❌ Tests failed! Check Firebase configuration.")
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()
