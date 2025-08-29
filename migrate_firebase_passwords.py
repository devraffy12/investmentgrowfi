#!/usr/bin/env python3
"""
Firebase Password Migration Script
Adds hashed passwords to existing Firebase users based on Django User passwords
"""

import os
import sys
import django
import hashlib

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from myproject.models import UserProfile
from firebase_auth import FirebaseAuth

def migrate_passwords_to_firebase():
    """Migrate Django user passwords to Firebase"""
    
    print("🔄 Starting Firebase Password Migration")
    print("=" * 50)
    
    # Initialize Firebase Auth
    firebase_auth = FirebaseAuth()
    
    if not firebase_auth.db:
        print("❌ Firebase not available for migration")
        return False
    
    # Get all users with profiles
    users_with_profiles = User.objects.filter(userprofile__isnull=False).select_related('userprofile')
    
    print(f"👥 Found {users_with_profiles.count()} users to migrate")
    
    migrated_count = 0
    error_count = 0
    
    for user in users_with_profiles:
        try:
            profile = user.userprofile
            phone_number = profile.phone_number
            
            if not phone_number:
                print(f"⚠️ User {user.username} has no phone number, skipping")
                continue
            
            # Generate Firebase key
            firebase_key = firebase_auth.get_firebase_key(phone_number)
            
            print(f"\n🔄 Processing user: {phone_number} (Django ID: {user.id})")
            
            # Check if user exists in Firebase
            existing_user = firebase_auth.db.child('users').child(firebase_key).get()
            
            if existing_user:
                # Check if password already exists
                if existing_user.get('password'):
                    print(f"   ✅ Password already exists, skipping")
                    continue
                
                # Get Django password hash - we'll use it directly since it's already hashed
                django_password_hash = user.password
                
                # For Firebase compatibility, we'll create a new hash from the username as password
                # This is a workaround since we can't reverse Django's password hash
                temp_password = f"temp_{user.id}_{phone_number[-4:]}"  # Temporary password
                firebase_password_hash = hashlib.sha256(temp_password.encode()).hexdigest()
                
                # Update Firebase user with password
                update_data = {
                    'password': firebase_password_hash,
                    'temp_password': temp_password,  # Store temp password for user reference
                    'password_migrated': True,
                    'django_user_id': user.id,
                    'migration_date': '2025-08-29T12:00:00'
                }
                
                firebase_auth.db.child('users').child(firebase_key).update(update_data)
                
                print(f"   ✅ Password migrated successfully")
                print(f"   📝 Temporary password: {temp_password}")
                print(f"   🔑 Firebase key: {firebase_key}")
                
                migrated_count += 1
                
            else:
                print(f"   ❌ User not found in Firebase, skipping")
                
        except Exception as e:
            print(f"   ❌ Error migrating user {user.username}: {e}")
            error_count += 1
            continue
    
    print("\n" + "=" * 50)
    print(f"🎉 Migration completed!")
    print(f"   ✅ Migrated: {migrated_count} users")
    print(f"   ❌ Errors: {error_count} users")
    
    if migrated_count > 0:
        print("\n📋 Important Notes:")
        print("1. Users with migrated passwords need to use their temporary passwords")
        print("2. Temporary passwords are in format: temp_{user_id}_{last_4_phone_digits}")
        print("3. Users should change their passwords after first login")
        print("4. You can provide users their temporary passwords or reset them")
    
    return migrated_count > 0

def reset_user_password_in_firebase(phone_number, new_password):
    """Reset a specific user's password in Firebase"""
    
    firebase_auth = FirebaseAuth()
    
    if not firebase_auth.db:
        print("❌ Firebase not available")
        return False
    
    try:
        firebase_key = firebase_auth.get_firebase_key(phone_number)
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
        
        # Update password in Firebase
        firebase_auth.db.child('users').child(firebase_key).update({
            'password': hashed_password,
            'password_reset': True,
            'password_reset_date': '2025-08-29T12:00:00'
        })
        
        print(f"✅ Password reset for {phone_number}")
        return True
        
    except Exception as e:
        print(f"❌ Error resetting password: {e}")
        return False

if __name__ == "__main__":
    try:
        print("🔥 Firebase Password Migration Tool")
        print("Choose an option:")
        print("1. Migrate all passwords from Django to Firebase")
        print("2. Reset specific user password")
        
        choice = input("\nEnter choice (1 or 2): ").strip()
        
        if choice == "1":
            migrate_passwords_to_firebase()
        elif choice == "2":
            phone = input("Enter phone number (+639xxxxxxxxx): ").strip()
            password = input("Enter new password: ").strip()
            
            if phone and password:
                reset_user_password_in_firebase(phone, password)
            else:
                print("❌ Phone number and password are required")
        else:
            print("❌ Invalid choice")
            
    except Exception as e:
        print(f"\n💥 Migration error: {e}")
        import traceback
        traceback.print_exc()
