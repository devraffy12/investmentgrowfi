#!/usr/bin/env python3
"""
Phone Number Authentication & Firebase Persistence Debug Tool
Diagnose why users lose their accounts after registration
"""
import os
import sys
import django
from datetime import datetime, timedelta
import re

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from myproject.models import UserProfile

def normalize_phone_for_testing(raw_phone):
    """Test different phone number normalization strategies"""
    if not raw_phone:
        return []
    
    # Remove all non-digit characters except +
    clean_phone = raw_phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    variations = [raw_phone, clean_phone]  # Original and cleaned
    
    # If already in +63 format, add variations
    if clean_phone.startswith('+63'):
        variations.append(clean_phone)
        digits = clean_phone[3:]  # Remove +63
        if digits.startswith('9'):
            variations.extend([
                '09' + digits[1:],  # 09xxxxxxxxx
                '639' + digits[1:], # 639xxxxxxxxx
                digits,             # 9xxxxxxxxx
            ])
    else:
        # Extract digits only
        digits_only = ''.join(filter(str.isdigit, clean_phone))
        
        # Generate all possible valid Philippine formats
        if digits_only.startswith('63') and len(digits_only) >= 12:
            # 639xxxxxxxxx format
            variations.append('+' + digits_only)
            mobile_part = digits_only[2:]  # Remove 63
            if mobile_part.startswith('9'):
                variations.extend([
                    '+63' + mobile_part,
                    '09' + mobile_part[1:],
                    mobile_part
                ])
                
        elif digits_only.startswith('09') and len(digits_only) == 11:
            # 09xxxxxxxxx format
            variations.extend([
                '+63' + digits_only[1:],  # +639xxxxxxxxx
                '639' + digits_only[1:],  # 639xxxxxxxxx
                digits_only[1:],          # 9xxxxxxxxx
                digits_only               # 09xxxxxxxxx
            ])
            
        elif digits_only.startswith('9') and len(digits_only) == 10:
            # 9xxxxxxxxx format
            variations.extend([
                '+63' + digits_only,      # +639xxxxxxxxx
                '639' + digits_only,      # 639xxxxxxxxx
                '09' + digits_only[1:],   # 09xxxxxxxxx
                digits_only               # 9xxxxxxxxx
            ])
    
    # Remove duplicates while preserving order
    unique_variations = []
    for var in variations:
        if var and var not in unique_variations:
            unique_variations.append(var)
    
    return unique_variations

def test_user_authentication_variations(user, test_password='12345'):
    """Test authentication with different phone number variations"""
    print(f"\n🔍 Testing authentication for user: {user.username}")
    print(f"   📅 Date joined: {user.date_joined}")
    print(f"   🔒 Last login: {user.last_login or 'Never'}")
    print(f"   ✅ Is active: {user.is_active}")
    
    # Get all possible phone variations
    phone_variations = normalize_phone_for_testing(user.username)
    print(f"   📱 Phone variations ({len(phone_variations)}):")
    for i, variation in enumerate(phone_variations, 1):
        print(f"      {i}. '{variation}'")
    
    # Test password check first
    password_works = user.check_password(test_password)
    print(f"   🔑 Password check: {'✅ WORKS' if password_works else '❌ FAILED'}")
    
    if not password_works:
        # Try common passwords
        common_passwords = ['123456', 'password', '123456789', user.username[-6:]]
        for pwd in common_passwords:
            if user.check_password(pwd):
                print(f"   🎯 Found working password: {pwd}")
                test_password = pwd
                password_works = True
                break
    
    if not password_works:
        print(f"   ❌ No working password found - skipping authentication test")
        return False
    
    # Test authentication with each variation
    working_auths = []
    for i, variation in enumerate(phone_variations, 1):
        try:
            auth_user = authenticate(username=variation, password=test_password)
            if auth_user:
                working_auths.append(variation)
                print(f"   ✅ Auth variation {i}: '{variation}' WORKS")
            else:
                print(f"   ❌ Auth variation {i}: '{variation}' FAILED")
        except Exception as e:
            print(f"   ⚠️  Auth variation {i}: '{variation}' ERROR: {e}")
    
    print(f"   📊 Working authentications: {len(working_auths)}/{len(phone_variations)}")
    
    return len(working_auths) > 0

def check_firebase_user_data():
    """Check if users exist in Firebase Realtime Database"""
    print(f"\n🔥 FIREBASE REALTIME DATABASE CHECK")
    print('-' * 50)
    
    try:
        from myproject.firebase_app import get_firebase_app
        from firebase_admin import db as firebase_db
        
        app = get_firebase_app()
        
        # Check if we got a dummy app
        if hasattr(app, 'project_id') and app.project_id == "firebase-unavailable":
            print("❌ Firebase is unavailable - dummy app detected")
            return False
        
        print("✅ Firebase app initialized successfully")
        
        # Get reference to users node
        ref = firebase_db.reference('/', app=app)
        users_ref = ref.child('users')
        
        # Get all users from Firebase
        firebase_users = users_ref.get()
        
        if firebase_users:
            print(f"📊 Found {len(firebase_users)} users in Firebase")
            
            # Show sample users
            sample_count = min(5, len(firebase_users))
            print(f"📋 Sample Firebase users ({sample_count}):")
            
            for i, (firebase_key, user_data) in enumerate(firebase_users.items()):
                if i >= sample_count:
                    break
                    
                phone = user_data.get('phone_number', 'Unknown')
                username = user_data.get('username', 'Unknown')
                created = user_data.get('created_at', 'Unknown')
                platform = user_data.get('platform', 'Unknown')
                
                print(f"   {i+1}. Key: {firebase_key}")
                print(f"      Phone: {phone}")
                print(f"      Username: {username}")
                print(f"      Created: {created}")
                print(f"      Platform: {platform}")
                print()
                
        else:
            print("❌ No users found in Firebase Realtime Database")
            
        return True
        
    except Exception as e:
        print(f"❌ Firebase check error: {e}")
        import traceback
        traceback.print_exc()
        return False

def compare_django_vs_firebase_users():
    """Compare Django users with Firebase users"""
    print(f"\n🔄 DJANGO vs FIREBASE USER COMPARISON")
    print('-' * 50)
    
    # Get recent Django users
    recent_users = User.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=7)
    ).order_by('-date_joined')[:10]
    
    print(f"📊 Found {recent_users.count()} recent Django users (last 7 days)")
    
    try:
        from myproject.firebase_app import get_firebase_app
        from firebase_admin import db as firebase_db
        
        app = get_firebase_app()
        if hasattr(app, 'project_id') and app.project_id == "firebase-unavailable":
            print("❌ Firebase unavailable - skipping comparison")
            return
        
        ref = firebase_db.reference('/', app=app)
        users_ref = ref.child('users')
        firebase_users = users_ref.get() or {}
        
        print(f"📊 Found {len(firebase_users)} users in Firebase")
        
        # Compare each Django user
        for django_user in recent_users:
            print(f"\n👤 Django User: {django_user.username}")
            print(f"   📅 Joined: {django_user.date_joined}")
            
            # Generate possible Firebase keys
            phone_variations = normalize_phone_for_testing(django_user.username)
            firebase_keys = []
            
            for variation in phone_variations:
                # Clean for Firebase key (remove +, spaces, etc.)
                firebase_key = variation.replace('+', '').replace(' ', '').replace('-', '')
                if firebase_key not in firebase_keys:
                    firebase_keys.append(firebase_key)
            
            print(f"   🔑 Possible Firebase keys: {firebase_keys}")
            
            # Check if user exists in Firebase
            found_in_firebase = False
            for key in firebase_keys:
                if key in firebase_users:
                    found_in_firebase = True
                    firebase_data = firebase_users[key]
                    print(f"   ✅ Found in Firebase under key: {key}")
                    print(f"      📱 Firebase phone: {firebase_data.get('phone_number', 'Unknown')}")
                    print(f"      📅 Firebase created: {firebase_data.get('created_at', 'Unknown')}")
                    print(f"      💰 Firebase balance: {firebase_data.get('balance', 'Unknown')}")
                    break
            
            if not found_in_firebase:
                print(f"   ❌ NOT found in Firebase")
                
                # Try to find by partial match
                matching_keys = []
                for firebase_key in firebase_users.keys():
                    # Check if any part of the phone matches
                    for variation in phone_variations:
                        clean_variation = variation.replace('+', '').replace(' ', '').replace('-', '')
                        if clean_variation in firebase_key or firebase_key in clean_variation:
                            matching_keys.append(firebase_key)
                            break
                
                if matching_keys:
                    print(f"   💡 Possible partial matches: {matching_keys}")
                    
    except Exception as e:
        print(f"❌ Comparison error: {e}")

def test_authentication_flow():
    """Test the full authentication flow"""
    print(f"\n🧪 FULL AUTHENTICATION FLOW TEST")
    print('-' * 50)
    
    # Test with a known recent user
    recent_user = User.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=3)
    ).first()
    
    if not recent_user:
        print("❌ No recent users found for testing")
        return
    
    print(f"🎯 Testing with user: {recent_user.username}")
    
    # Test authentication variations
    success = test_user_authentication_variations(recent_user)
    
    if success:
        print("✅ Authentication test: PASSED")
    else:
        print("❌ Authentication test: FAILED")
        
        # Try to diagnose the issue
        print("\n🔍 DIAGNOSING AUTHENTICATION FAILURE:")
        
        # Check if user profile exists
        try:
            profile = UserProfile.objects.get(user=recent_user)
            print(f"✅ UserProfile exists: {profile.phone_number}")
        except UserProfile.DoesNotExist:
            print(f"❌ UserProfile missing - this could be the issue!")
            
        # Check user status
        if not recent_user.is_active:
            print(f"❌ User is inactive")
        else:
            print(f"✅ User is active")
            
        # Check if password is set
        if recent_user.password:
            print(f"✅ Password is set (length: {len(recent_user.password)})")
        else:
            print(f"❌ No password set")

def main():
    """Run comprehensive phone authentication diagnostic"""
    print('🔍 PHONE AUTHENTICATION & FIREBASE PERSISTENCE DIAGNOSTIC')
    print('=' * 70)
    print(f"🕒 Started at: {datetime.now()}")
    
    # 1. Basic statistics
    print(f"\n📊 USER STATISTICS")
    print('-' * 30)
    
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    recent_users = User.objects.filter(date_joined__gte=timezone.now() - timedelta(days=7)).count()
    yesterday_users = User.objects.filter(date_joined__gte=timezone.now() - timedelta(days=1)).count()
    
    print(f"👥 Total users: {total_users}")
    print(f"✅ Active users: {active_users}")
    print(f"📅 Last 7 days: {recent_users}")
    print(f"📅 Last 24 hours: {yesterday_users}")
    
    # 2. Test recent users
    print(f"\n👥 TESTING RECENT USERS")
    print('-' * 30)
    
    recent_test_users = User.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=2)
    ).order_by('-date_joined')[:3]
    
    authentication_successes = 0
    for user in recent_test_users:
        if test_user_authentication_variations(user):
            authentication_successes += 1
    
    print(f"\n📊 Authentication Success Rate: {authentication_successes}/{len(recent_test_users)}")
    
    # 3. Check Firebase
    firebase_available = check_firebase_user_data()
    
    # 4. Compare Django vs Firebase
    if firebase_available:
        compare_django_vs_firebase_users()
    
    # 5. Test full flow
    test_authentication_flow()
    
    # 6. Summary and recommendations
    print(f"\n📋 DIAGNOSTIC SUMMARY")
    print('=' * 50)
    
    if authentication_successes == len(recent_test_users) and len(recent_test_users) > 0:
        print("✅ All tested users can authenticate - authentication system is working")
    elif authentication_successes > 0:
        print("⚠️  Some users can authenticate, some cannot - partial issue")
    else:
        print("❌ No users can authenticate - critical authentication issue")
    
    if firebase_available:
        print("✅ Firebase is available and accessible")
    else:
        print("❌ Firebase is not available - this could cause persistence issues")
    
    print(f"\n💡 RECOMMENDATIONS:")
    
    if authentication_successes < len(recent_test_users):
        print("• Check phone number normalization consistency")
        print("• Verify user passwords are set correctly")
        print("• Ensure UserProfile objects exist for all users")
    
    if not firebase_available:
        print("• Fix Firebase connectivity issues")
        print("• Check Firebase credentials and configuration")
    
    print("• Test login immediately after registration")
    print("• Monitor user sessions for persistence")
    print("• Check browser cookies and session storage")
    
    print(f"\n🏁 Diagnostic completed at: {datetime.now()}")

if __name__ == '__main__':
    main()
