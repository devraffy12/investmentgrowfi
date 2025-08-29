#!/usr/bin/env python3
"""
Simulate the exact user complaint: 
"User registers yesterday, tries to login today, gets 'Account not found'"
"""
import os
import sys
import django
from datetime import datetime, timedelta

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from myproject.models import UserProfile

def simulate_user_complaint():
    """Simulate the exact scenario described by the user"""
    print('🔍 SIMULATING USER COMPLAINT SCENARIO')
    print('=' * 60)
    print('Scenario: User registers yesterday, tries to login today, gets "Account not found"')
    
    # Find users who registered yesterday (in the last 24-48 hours)
    yesterday = timezone.now() - timedelta(hours=24)
    two_days_ago = timezone.now() - timedelta(hours=48)
    
    yesterday_users = User.objects.filter(
        date_joined__gte=two_days_ago,
        date_joined__lte=yesterday
    ).order_by('-date_joined')
    
    print(f"\n📊 Found {yesterday_users.count()} users who registered in the last 24-48 hours")
    
    if not yesterday_users.exists():
        print("❌ No users found from yesterday. Creating a test scenario...")
        
        # Create a test user as if they registered yesterday
        test_phone = '+639888777666'
        test_password = '123456'
        
        # Clean up any existing test user
        User.objects.filter(username=test_phone).delete()
        
        # Create user with yesterday's timestamp
        test_user = User.objects.create_user(
            username=test_phone,
            password=test_password
        )
        
        # Manually set the date_joined to yesterday
        test_user.date_joined = timezone.now() - timedelta(hours=24)
        test_user.save()
        
        # Create profile
        UserProfile.objects.create(
            user=test_user,
            phone_number=test_phone
        )
        
        print(f"✅ Created test user: {test_phone} (dated yesterday)")
        yesterday_users = [test_user]
    
    # Test each user from yesterday
    for user in yesterday_users[:3]:  # Test up to 3 users
        print(f"\n👤 Testing user: {user.username}")
        print(f"   📅 Registered: {user.date_joined}")
        print(f"   🔒 Last login: {user.last_login or 'Never'}")
        print(f"   ✅ Is active: {user.is_active}")
        
        # Check if user has a profile
        try:
            profile = UserProfile.objects.get(user=user)
            print(f"   📱 Profile phone: {profile.phone_number}")
            print(f"   💰 Profile balance: {profile.balance}")
        except UserProfile.DoesNotExist:
            print(f"   ❌ No UserProfile found!")
            
        # Simulate what happens when user tries to login "today"
        print(f"\n🧪 SIMULATING LOGIN ATTEMPT (24 hours later)")
        
        # Extract just the mobile digits (what the login form would send)
        if user.username.startswith('+63'):
            mobile_digits = user.username[3:]  # Remove +63 to get 9xxxxxxxxx
        else:
            mobile_digits = user.username
            
        print(f"   📝 User enters in login form: {mobile_digits}")
        
        # Test common passwords
        test_passwords = ['123456', '12345', 'password', user.username[-6:]]
        
        password_found = None
        for pwd in test_passwords:
            if user.check_password(pwd):
                password_found = pwd
                print(f"   🔑 Working password found: {pwd}")
                break
        
        if not password_found:
            print(f"   ❌ No working password found - user may have set a custom password")
            continue
            
        # Now test the authentication exactly as the login view would
        print(f"   🔐 Testing authentication with mobile digits...")
        
        # Test 1: Direct authentication with mobile digits
        auth_user = authenticate(username=mobile_digits, password=password_found)
        if auth_user:
            print(f"   ✅ Authentication with '{mobile_digits}': SUCCESS")
        else:
            print(f"   ❌ Authentication with '{mobile_digits}': FAILED")
            
            # Test 2: Try with full phone format
            full_phone = user.username
            auth_user = authenticate(username=full_phone, password=password_found)
            if auth_user:
                print(f"   ✅ Authentication with '{full_phone}': SUCCESS")
                print(f"   🚨 ISSUE FOUND: Mobile digits format fails but full format works!")
            else:
                print(f"   ❌ Authentication with '{full_phone}': FAILED")
                print(f"   🚨 CRITICAL: User cannot authenticate with any format!")
                
        # Test 3: Check if user exists in database with different formats
        print(f"   🔍 Checking user existence in database...")
        
        formats_to_check = [
            mobile_digits,           # 9xxxxxxxxx
            '0' + mobile_digits,     # 09xxxxxxxxx  
            '+63' + mobile_digits,   # +639xxxxxxxxx
            '63' + mobile_digits,    # 639xxxxxxxxx
        ]
        
        for fmt in formats_to_check:
            try:
                found_user = User.objects.get(username=fmt)
                print(f"      ✅ Found user with format: '{fmt}'")
                if found_user.id == user.id:
                    print(f"         👤 This is the same user (ID: {user.id})")
                else:
                    print(f"         👤 This is a different user (ID: {found_user.id})")
            except User.DoesNotExist:
                print(f"      ❌ No user found with format: '{fmt}'")
                
        # Test 4: Check Firebase data
        print(f"   🔥 Checking Firebase data...")
        try:
            from myproject.firebase_app import get_firebase_app
            from firebase_admin import db as firebase_db
            
            app = get_firebase_app()
            if hasattr(app, 'project_id') and app.project_id != "firebase-unavailable":
                ref = firebase_db.reference('/', app=app)
                users_ref = ref.child('users')
                
                # Check Firebase with cleaned phone number
                firebase_key = user.username.replace('+', '').replace(' ', '').replace('-', '')
                firebase_data = users_ref.child(firebase_key).get()
                
                if firebase_data:
                    print(f"      ✅ User found in Firebase under key: {firebase_key}")
                    print(f"         📅 Firebase created: {firebase_data.get('created_at', 'Unknown')}")
                    print(f"         💰 Firebase balance: {firebase_data.get('balance', 'Unknown')}")
                else:
                    print(f"      ❌ User NOT found in Firebase under key: {firebase_key}")
            else:
                print(f"      ⚠️  Firebase not available")
                
        except Exception as e:
            print(f"      ❌ Firebase check error: {e}")

def test_phone_normalization_edge_cases():
    """Test edge cases in phone normalization that might cause issues"""
    print(f"\n🔧 TESTING PHONE NORMALIZATION EDGE CASES")
    print('=' * 50)
    
    # Test cases that might cause issues
    test_cases = [
        {
            'input': '9123456789',
            'expected': '+639123456789',
            'description': 'Mobile digits only (login form input)'
        },
        {
            'input': '09123456789', 
            'expected': '+639123456789',
            'description': 'Philippine format with 0'
        },
        {
            'input': '+639123456789',
            'expected': '+639123456789', 
            'description': 'Full international format'
        },
        {
            'input': '639123456789',
            'expected': '+639123456789',
            'description': 'International without +'
        },
        {
            'input': '912 345 6789',
            'expected': '+639123456789',
            'description': 'With spaces'
        },
        {
            'input': '912-345-6789',
            'expected': '+639123456789',
            'description': 'With dashes'
        }
    ]
    
    # Import the normalization function from views.py
    def normalize_phone_number(raw_phone):
        """Copy of normalization logic from views.py"""
        if not raw_phone:
            return ''
            
        # Remove all non-digit characters except +
        clean_phone = raw_phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # If already in +63 format, return as is
        if clean_phone.startswith('+63'):
            return clean_phone
            
        # Extract digits only
        digits_only = ''.join(filter(str.isdigit, clean_phone))
        
        # Handle different Philippine number formats
        if digits_only.startswith('63') and len(digits_only) >= 12:
            # 639xxxxxxxxx format
            return '+' + digits_only
        elif digits_only.startswith('09') and len(digits_only) == 11:
            # 09xxxxxxxxx format - convert to +639xxxxxxxxx
            return '+63' + digits_only[1:]
        elif digits_only.startswith('9') and len(digits_only) == 10:
            # 9xxxxxxxxx format - add +63
            return '+63' + digits_only
        elif len(digits_only) >= 10:
            # Handle edge cases by extracting last 10 digits
            last_10_digits = digits_only[-10:]
            if last_10_digits.startswith('9'):
                return '+63' + last_10_digits
            else:
                # Try with full digits
                return '+63' + digits_only
        
        # Fallback: return original if can't normalize
        return clean_phone
    
    print("📱 Testing normalization function:")
    for case in test_cases:
        result = normalize_phone_number(case['input'])
        status = "✅" if result == case['expected'] else "❌"
        print(f"   {status} Input: '{case['input']}' → Output: '{result}' (Expected: '{case['expected']}')")
        print(f"      Description: {case['description']}")
        
        if result != case['expected']:
            print(f"      🚨 MISMATCH DETECTED!")

if __name__ == '__main__':
    print('🚀 USER COMPLAINT SIMULATION')
    print('=' * 60)
    print('Investigating: "User registers yesterday, tries to login today, gets Account not found"')
    
    # Run the simulation
    simulate_user_complaint()
    
    # Test normalization edge cases
    test_phone_normalization_edge_cases()
    
    print(f"\n📋 ANALYSIS SUMMARY:")
    print('• If authentication works but user gets "Account not found"')
    print('• The issue might be in the login view error handling logic')
    print('• Or session/cookie persistence after successful authentication')
    print('• Check browser developer tools for session cookies')
    print('• Test with incognito/private browsing mode')
