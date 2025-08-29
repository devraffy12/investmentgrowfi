"""
Test Firebase Authentication Login
This will test if users who registered in Firebase can now login
"""
import os
import sys
import django

# Add the project root to the Python path
sys.path.insert(0, r'C:\Users\raffy\OneDrive\Desktop\investment')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from firebase_auth import FirebaseAuth

def test_firebase_login():
    """Test Firebase authentication"""
    print("🔥 Testing Firebase Authentication")
    print("=" * 50)
    
    firebase_auth = FirebaseAuth()
    
    # Test phone normalization
    test_phones = [
        '09123456789',
        '+639123456789',
        '639123456789',
        '9123456789'
    ]
    
    print("📱 Testing phone normalization:")
    for phone in test_phones:
        normalized = firebase_auth.normalize_phone(phone)
        firebase_key = firebase_auth.get_firebase_key(normalized)
        print(f"   {phone} -> {normalized} (key: {firebase_key})")
    
    print("\n🔍 Testing user lookup in Firebase:")
    
    # Try to find existing users
    sample_phone = '+639123456789'
    user_data = firebase_auth.find_user_by_phone(sample_phone)
    
    if user_data:
        print(f"✅ Found user: {sample_phone}")
        print(f"   Balance: ₱{user_data.get('balance', 0)}")
        print(f"   Status: {user_data.get('status', 'unknown')}")
        print(f"   Created: {user_data.get('created_at', 'unknown')}")
        print(f"   Referral Code: {user_data.get('referral_code', 'none')}")
    else:
        print(f"❌ No user found for: {sample_phone}")
    
    print("\n🔐 Testing authentication:")
    
    # Test login (you can change this to a real phone/password)
    test_phone = input("Enter phone number to test (or press Enter to skip): ").strip()
    if test_phone:
        test_password = input("Enter password: ").strip()
        
        if test_password:
            auth_result = firebase_auth.authenticate_user(test_phone, test_password)
            
            if auth_result['success']:
                print("✅ Authentication successful!")
                user_data = auth_result['user_data']
                print(f"   Phone: {user_data.get('phone_number')}")
                print(f"   Balance: ₱{user_data.get('balance', 0)}")
                print(f"   Login Count: {user_data.get('login_count', 0)}")
            else:
                print(f"❌ Authentication failed: {auth_result['error']}")
    
    print("\n📊 Checking Firebase connection:")
    if firebase_auth.db:
        try:
            # Try to read from Firebase
            users_ref = firebase_auth.db.child('users')
            users_snapshot = users_ref.limit_to_first(1).get()
            
            if users_snapshot:
                print("✅ Firebase database connection working")
                print(f"   Sample user keys: {list(users_snapshot.keys()) if users_snapshot else 'None'}")
            else:
                print("⚠️ Firebase connected but no users found")
                
        except Exception as e:
            print(f"❌ Firebase connection error: {e}")
    else:
        print("❌ Firebase database not initialized")

if __name__ == '__main__':
    test_firebase_login()
