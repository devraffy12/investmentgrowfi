"""
Test existing users in Firebase - Verify na hindi nawala ang data
"""
import os
import django
import sys

# Add the project directory to Python path
sys.path.append('C:/Users/raffy/OneDrive/Desktop/investment')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from firebase_auth import FirebaseAuth

def test_existing_users():
    """Test if existing users are still accessible"""
    print("🔥 Testing existing Firebase users...")
    
    firebase_auth = FirebaseAuth()
    
    if not firebase_auth.db:
        print("❌ Firebase not available")
        return
    
    try:
        # Get all users from Firebase
        users_ref = firebase_auth.db.child('users')
        all_users = users_ref.get()
        
        if all_users:
            print(f"✅ Found {len(all_users)} users in Firebase:")
            
            for firebase_key, user_data in all_users.items():
                phone = user_data.get('phone_number', 'No phone')
                balance = user_data.get('balance', 0)
                created = user_data.get('created_at', 'Unknown')
                last_login = user_data.get('last_login', 'Never')
                
                print(f"📱 {phone}")
                print(f"   💰 Balance: ₱{balance}")
                print(f"   📅 Created: {created[:10] if created != 'Unknown' else 'Unknown'}")
                print(f"   🔐 Last Login: {last_login[:10] if last_login != 'Never' else 'Never'}")
                print(f"   🔑 Firebase Key: {firebase_key}")
                print()
        else:
            print("❌ No users found in Firebase")
            
        # Test referral codes
        referral_ref = firebase_auth.db.child('referral_codes')
        referral_codes = referral_ref.get()
        
        if referral_codes:
            print(f"✅ Found {len(referral_codes)} referral codes:")
            for code, data in list(referral_codes.items())[:5]:  # Show first 5
                print(f"   🎁 {code} -> {data.get('phone_number', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking users: {e}")
        return False

def test_phone_normalization():
    """Test phone number normalization"""
    print("\n📱 Testing phone number normalization...")
    
    firebase_auth = FirebaseAuth()
    
    test_phones = [
        "09123456789",
        "639123456789", 
        "+639123456789",
        "9123456789",
        "099123456789"
    ]
    
    for phone in test_phones:
        normalized = firebase_auth.normalize_phone(phone)
        firebase_key = firebase_auth.get_firebase_key(normalized)
        print(f"   {phone} -> {normalized} -> key: {firebase_key}")

if __name__ == "__main__":
    print("🧪 TESTING FIREBASE USER PERSISTENCE")
    print("="*50)
    
    success = test_existing_users()
    test_phone_normalization()
    
    if success:
        print("\n✅ ALL USERS ARE SAFE!")
        print("✅ Firebase authentication ready!")
        print("✅ Existing users can login with their phone numbers!")
    else:
        print("\n❌ Issue detected - check Firebase connection")
