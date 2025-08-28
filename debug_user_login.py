#!/usr/bin/env python
"""
Debug user login issue for phone number: 9214392306
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from myproject.models import UserProfile

def debug_user_login():
    """Debug login issue for specific user"""
    phone_number = "9214392306"
    
    print("🔍 Debugging User Login Issue")
    print("=" * 50)
    print(f"📱 Phone Number: {phone_number}")
    print()
    
    # Check if user exists in Django database
    print("1️⃣ Checking Django Database...")
    try:
        # Try to find user by username (phone number)
        user = User.objects.get(username=phone_number)
        print(f"✅ User found in Django database")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   First Name: {user.first_name}")
        print(f"   Last Name: {user.last_name}")
        print(f"   Is Active: {user.is_active}")
        print(f"   Date Joined: {user.date_joined}")
        print(f"   Last Login: {user.last_login}")
        print(f"   Has Usable Password: {user.has_usable_password()}")
        
        # Check UserProfile
        try:
            profile = UserProfile.objects.get(user=user)
            print(f"✅ UserProfile found")
            print(f"   Phone: {profile.phone_number}")
            print(f"   Referral Code: {profile.referral_code}")
            print(f"   Balance: ₱{profile.balance}")
            print(f"   Referred By: {profile.referred_by}")
        except UserProfile.DoesNotExist:
            print("❌ UserProfile not found")
            
    except User.DoesNotExist:
        print("❌ User not found in Django database")
        
        # Check if there are similar usernames
        similar_users = User.objects.filter(username__icontains=phone_number[-4:])
        if similar_users.exists():
            print(f"🔍 Found {similar_users.count()} users with similar numbers:")
            for u in similar_users[:5]:
                print(f"   - {u.username} (joined: {u.date_joined})")
    
    print()
    
    # Check all users that start with 921
    print("2️⃣ Checking Similar Phone Numbers...")
    similar_users = User.objects.filter(username__startswith="921")
    print(f"Found {similar_users.count()} users starting with '921':")
    for user in similar_users[:10]:
        print(f"   - {user.username} (active: {user.is_active}, joined: {user.date_joined})")
    
    print()
    
    # Test authentication with different password combinations
    print("3️⃣ Testing Common Password Patterns...")
    if User.objects.filter(username=phone_number).exists():
        user = User.objects.get(username=phone_number)
        
        # Common password patterns to test
        test_passwords = [
            phone_number,  # Same as phone number
            phone_number[-4:],  # Last 4 digits
            phone_number[-6:],  # Last 6 digits
            "123456",
            "password", 
            "12345678",
            f"{phone_number}123",
            "admin",
            "user123"
        ]
        
        print("Testing password combinations:")
        for password in test_passwords:
            test_user = authenticate(username=phone_number, password=password)
            if test_user:
                print(f"✅ SUCCESS: Password is '{password}'")
                break
            else:
                print(f"❌ Failed: '{password}'")
        else:
            print("🚨 None of the common passwords worked")
            print("💡 Password might be custom or account might have authentication issues")
    
    print()
    
    # Check Django login view for any errors
    print("4️⃣ Checking Login Configuration...")
    from django.conf import settings
    print(f"AUTH_USER_MODEL: {getattr(settings, 'AUTH_USER_MODEL', 'Default')}")
    print(f"LOGIN_URL: {getattr(settings, 'LOGIN_URL', '/login/')}")
    print(f"LOGIN_REDIRECT_URL: {getattr(settings, 'LOGIN_REDIRECT_URL', '/')}")
    
    print()
    
    # Recommendations
    print("💡 RECOMMENDATIONS:")
    print("-" * 30)
    
    if User.objects.filter(username=phone_number).exists():
        user = User.objects.get(username=phone_number)
        if not user.is_active:
            print("• User account is inactive - activate the account")
        elif not user.has_usable_password():
            print("• User has no usable password - reset password required")
        else:
            print("• Try password reset functionality")
            print("• Check if user is entering correct password")
            print("• Verify login form is working correctly")
    else:
        print("• User not found in Django database")
        print("• Check if registration completed properly")
        print("• Verify Firebase to Django sync is working")

if __name__ == "__main__":
    debug_user_login()
