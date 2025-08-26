#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

print("🔥 CHECKING FIREBASE FOR YOUR PHONE NUMBER")
print("=" * 50)

try:
    from myproject.firebase_app import get_firebase_app
    from firebase_admin import db as firebase_db
    
    app = get_firebase_app()
    ref = firebase_db.reference('/', app=app)
    users_ref = ref.child('users')
    
    # Search for your phone number in different formats
    search_keys = [
        '639919101001',     # Without +
        '+639919101001',    # With +
        '9919101001',       # Without 63
    ]
    
    print("Searching Firebase for your phone number...")
    
    found_user = None
    for key in search_keys:
        print(f"Looking for key: '{key}'")
        try:
            user_data = users_ref.child(key).get()
            if user_data:
                print(f"✅ FOUND YOU in Firebase with key: '{key}'")
                print(f"Data: {user_data}")
                found_user = (key, user_data)
                break
        except Exception as e:
            print(f"Error checking key '{key}': {e}")
    
    if not found_user:
        print("❌ Not found with direct key lookup. Checking all users...")
        
        # Get all users and search
        all_users = users_ref.get()
        if all_users:
            for firebase_key, user_data in all_users.items():
                if user_data and isinstance(user_data, dict):
                    phone = user_data.get('phone_number', '')
                    username = user_data.get('username', '')
                    
                    if '639919101001' in phone or '639919101001' in username:
                        print(f"✅ FOUND YOU! Firebase key: '{firebase_key}'")
                        print(f"Phone: {phone}")
                        print(f"Username: {username}")
                        print(f"Data: {user_data}")
                        found_user = (firebase_key, user_data)
                        break
        
        if not found_user:
            print("❌ Hindi ka nakita sa Firebase")
            print("\nMost recent Firebase users:")
            if all_users:
                recent_count = 0
                for key, data in all_users.items():
                    if data and recent_count < 5:
                        phone = data.get('phone_number', 'N/A')
                        print(f"  {phone}")
                        recent_count += 1
    
    if found_user:
        firebase_key, user_data = found_user
        print(f"\n🎯 SOLUTION:")
        print("=" * 50)
        stored_username = user_data.get('username', '')
        print(f"Your account exists in Firebase!")
        print(f"Firebase key: {firebase_key}")
        print(f"Stored username: {stored_username}")
        print(f"Try logging in with: {stored_username}")
        
        # Check if Django user exists
        from django.contrib.auth.models import User
        try:
            django_user = User.objects.get(username=stored_username)
            print(f"✅ Django user found: ID {django_user.id}")
            print(f"Account is active: {django_user.is_active}")
        except User.DoesNotExist:
            print(f"❌ Django user NOT found - account only exists in Firebase")
            print(f"Need to create Django account or sync from Firebase")

except Exception as e:
    print(f"❌ Error accessing Firebase: {e}")
    import traceback
    traceback.print_exc()

print(f"\n💡 RECOMMENDATIONS:")
print("=" * 50)
print("1. Try logging in with the exact format you used during registration")
print("2. Make sure your password is correct (case-sensitive)")
print("3. If the account only exists in Firebase, we may need to sync it")
print("4. Double-check na tama ang phone number: 639919101001")
