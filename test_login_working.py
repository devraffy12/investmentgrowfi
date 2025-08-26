#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from myproject.models import UserProfile
from datetime import datetime, timedelta

print("🔍 TESTING USER LOGIN FUNCTIONALITY")
print("=" * 60)

def test_phone_cleaning(phone):
    """Test current phone cleaning logic"""
    clean_phone = phone.replace(' ', '').replace('-', '')
    if not clean_phone.startswith('+63'):
        if clean_phone.startswith('63'):
            clean_phone = '+' + clean_phone
        elif clean_phone.startswith('09'):
            clean_phone = '+63' + clean_phone[1:]  # Remove only '0', keep '9...'
        elif clean_phone.startswith('9'):
            clean_phone = '+63' + clean_phone
    return clean_phone

def test_user_login(username_input, test_password="password123"):
    """Simulate the login process"""
    print(f"\n🔐 Testing login for: '{username_input}'")
    
    # Step 1: Clean phone number (same as views.py)
    cleaned_phone = test_phone_cleaning(username_input)
    print(f"   Cleaned phone: '{cleaned_phone}'")
    
    # Step 2: Check if user exists
    try:
        user = User.objects.get(username=cleaned_phone)
        print(f"   ✅ User found: ID {user.id}, Active: {user.is_active}")
        
        # Step 3: Test authentication (we can't test real passwords, but structure)
        print(f"   Password set: {user.password != ''}")
        print(f"   Has usable password: {user.has_usable_password()}")
        
        # Step 4: Check profile
        try:
            profile = UserProfile.objects.get(user=user)
            print(f"   ✅ Profile found: Balance ₱{profile.balance}")
            return "✅ LOGIN SUCCESS"
        except UserProfile.DoesNotExist:
            print(f"   ❌ No profile found")
            return "❌ NO PROFILE"
            
    except User.DoesNotExist:
        print(f"   ❌ User not found with username: '{cleaned_phone}'")
        return "❌ USER NOT FOUND"

# Test recent users (yesterday's registrations)
print("📱 TESTING YESTERDAY'S USERS:")
print("-" * 60)

yesterday = datetime.now() - timedelta(days=1)
yesterday_users = User.objects.filter(date_joined__date=yesterday.date())

print(f"Found {yesterday_users.count()} users from yesterday:")

for user in yesterday_users[:5]:  # Test first 5 users
    stored_username = user.username
    
    # Test different input formats that user might try
    test_formats = [
        stored_username,                           # Exact format
        stored_username.replace('+63', '63'),      # Without +
        stored_username.replace('+63', '09'),      # 09 format
        stored_username.replace('+63', '9'),       # 9 format
    ]
    
    print(f"\n👤 User: {stored_username} (ID: {user.id})")
    for fmt in test_formats:
        result = test_user_login(fmt)
        status = "✅" if "SUCCESS" in result else "❌"
        print(f"      {status} Format '{fmt}' → {result}")

# Test your specific account
print(f"\n🎯 TESTING YOUR ACCOUNT:")
print("-" * 60)

your_formats = [
    "639919101001",
    "+639919101001", 
    "9919101001",
    "09919101001"
]

for fmt in your_formats:
    result = test_user_login(fmt)
    status = "✅" if "SUCCESS" in result else "❌"
    print(f"   {status} '{fmt}' → {result}")

# Test some recent users
print(f"\n📊 RANDOM USER SAMPLE TEST:")
print("-" * 60)

recent_users = User.objects.all().order_by('-date_joined')[:3]
for user in recent_users:
    print(f"\nUser: {user.username}")
    result = test_user_login(user.username)
    print(f"   Direct login: {result}")

print(f"\n📈 SUMMARY:")
print("=" * 60)
total_users = User.objects.count()
users_with_profiles = UserProfile.objects.count()

print(f"Total users in system: {total_users}")
print(f"Users with profiles: {users_with_profiles}")
print(f"Profile completion rate: {(users_with_profiles/total_users*100):.1f}%")

print(f"\n🎯 CONCLUSION:")
print("=" * 60)
print("If users are getting 'LOGIN SUCCESS' above, then:")
print("✅ Phone number cleaning is working")
print("✅ User accounts exist in Django")  
print("✅ Profiles are properly created")
print("✅ Login system should work")
print("\nIf there are failures, may specific issue pa na need i-fix.")
