#!/usr/bin/env python3
"""
Check Firebase users and test login
"""
import os
import sys
import django
import hashlib

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from myproject.firebase_app import get_firebase_app
from firebase_admin import db as firebase_db

def check_firebase_users():
    print("🔍 Checking Firebase Users")
    print("=" * 40)
    
    try:
        app = get_firebase_app()
        if hasattr(app, 'project_id') and app.project_id != 'firebase-unavailable':
            ref = firebase_db.reference('/', app=app)
            users_ref = ref.child('users')
            
            # Get all users
            all_users = users_ref.get()
            
            if all_users:
                print(f"✅ Found {len(all_users)} users in Firebase:")
                
                # Show first 3 users
                count = 0
                for key, data in all_users.items():
                    if count >= 3:
                        break
                    if data:
                        phone = data.get('phone_number', 'Unknown')
                        password_hash = data.get('password', 'No password')
                        status = data.get('status', data.get('account_status', 'Unknown'))
                        
                        print(f"\n📱 User {count + 1}:")
                        print(f"   Phone: {phone}")
                        print(f"   Firebase Key: {key}")
                        print(f"   Password hash: {password_hash[:20]}..." if len(password_hash) > 20 else f"   Password: {password_hash}")
                        print(f"   Status: {status}")
                        
                        # Check password format
                        if len(password_hash) == 64 and all(c in '0123456789abcdef' for c in password_hash):
                            print(f"   ✅ Password looks like SHA256 hash")
                        else:
                            print(f"   ❌ Password format unknown")
                        
                        count += 1
                
                return all_users
            else:
                print("❌ No users found in Firebase")
                return None
        else:
            print("❌ Firebase not available")
            return None
            
    except Exception as e:
        print(f"❌ Error checking Firebase: {e}")
        return None

def test_password_verification(phone, test_password):
    """Test if a password would work for a user"""
    print(f"\n🔐 Testing password verification for {phone}")
    print("=" * 50)
    
    try:
        app = get_firebase_app()
        ref = firebase_db.reference('/', app=app)
        
        # Normalize phone to Firebase key
        firebase_key = phone.replace('+', '').replace(' ', '').replace('-', '')
        
        # Get user data
        users_ref = ref.child('users')
        user_data = users_ref.child(firebase_key).get()
        
        if not user_data:
            print(f"❌ User not found: {phone}")
            return False
        
        stored_password = user_data.get('password', '')
        if not stored_password:
            print(f"❌ No password stored for user")
            return False
        
        # Test password verification
        test_hash = hashlib.sha256(test_password.encode()).hexdigest()
        
        print(f"📱 Phone: {phone}")
        print(f"🔑 Test password: {test_password}")
        print(f"🔐 Test hash: {test_hash[:20]}...")
        print(f"🔐 Stored hash: {stored_password[:20]}...")
        print(f"✅ Match: {test_hash == stored_password}")
        
        return test_hash == stored_password
        
    except Exception as e:
        print(f"❌ Error testing password: {e}")
        return False

if __name__ == '__main__':
    users = check_firebase_users()
    
    if users:
        print(f"\n🧪 MANUAL PASSWORD TEST")
        print("=" * 30)
        
        # Get user input for testing
        phone = input("Enter phone number to test (with +63): ").strip()
        if phone:
            password = input("Enter password to test: ").strip()
            if password:
                result = test_password_verification(phone, password)
                if result:
                    print(f"\n🎉 SUCCESS: Password verification would work!")
                else:
                    print(f"\n❌ FAILED: Password verification would fail!")
            else:
                print("No password entered.")
        else:
            print("No phone number entered.")
