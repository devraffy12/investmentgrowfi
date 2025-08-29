#!/usr/bin/env python3
"""
COMPREHENSIVE USER AUTHENTICATION DIAGNOSTIC
Check exact issues with user login persistence
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
from django.db import connection

def check_1_database_direct():
    """1. DATABASE CHECK - Direct database verification"""
    print('🔍 1. DATABASE DIRECT CHECK')
    print('=' * 50)
    
    # Get recent users from database
    recent_users = User.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=7)
    ).order_by('-date_joined')[:10]
    
    print(f"📊 Found {recent_users.count()} users in last 7 days")
    
    for user in recent_users:
        print(f"\n👤 User: {user.username}")
        print(f"   📅 Date joined: {user.date_joined}")
        print(f"   ✅ Is active: {user.is_active}")
        print(f"   🔒 Has password: {bool(user.password)}")
        print(f"   📝 Password hash length: {len(user.password)}")
        print(f"   🔑 Last login: {user.last_login or 'Never'}")
        
        # Check exact username characters
        username_chars = [ord(c) for c in user.username]
        print(f"   📱 Username char codes: {username_chars}")
        print(f"   📱 Username repr: {repr(user.username)}")
        
        # Check if profile exists
        try:
            profile = UserProfile.objects.get(user=user)
            print(f"   👤 Profile exists: {profile.phone_number}")
        except UserProfile.DoesNotExist:
            print(f"   ❌ No profile found")

def check_2_authentication_backend():
    """2. AUTHENTICATION BACKEND CHECK"""
    print(f"\n🔐 2. AUTHENTICATION BACKEND CHECK")
    print('=' * 50)
    
    from django.conf import settings
    
    # Check authentication backends
    auth_backends = getattr(settings, 'AUTHENTICATION_BACKENDS', [])
    print(f"🔧 Authentication backends: {auth_backends}")
    
    # Check if custom auth is used
    for backend in auth_backends:
        print(f"   • {backend}")
        if 'django.contrib.auth.backends.ModelBackend' in backend:
            print(f"     ✅ Standard Django authentication")
        else:
            print(f"     ⚠️  Custom authentication backend")

def check_3_username_field_issue():
    """3. USERNAME FIELD ISSUE"""
    print(f"\n📝 3. USERNAME FIELD VERIFICATION")
    print('=' * 50)
    
    # Check recent user with raw SQL
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, username, is_active, date_joined, password
            FROM auth_user 
            WHERE date_joined >= datetime('now', '-7 days')
            ORDER BY date_joined DESC 
            LIMIT 5
        """)
        
        rows = cursor.fetchall()
        
        print(f"📊 Raw SQL results ({len(rows)} users):")
        for row in rows:
            user_id, username, is_active, date_joined, password = row
            print(f"   ID: {user_id}")
            print(f"   Username: '{username}' (length: {len(username)})")
            print(f"   Is Active: {is_active}")
            print(f"   Date Joined: {date_joined}")
            print(f"   Has Password: {bool(password)}")
            print(f"   Username bytes: {username.encode('utf-8')}")
            print()

def check_4_password_validation():
    """4. PASSWORD VALIDATION"""
    print(f"\n🔑 4. PASSWORD VALIDATION TEST")
    print('=' * 50)
    
    # Get a recent user for testing
    test_user = User.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=3)
    ).first()
    
    if not test_user:
        print("❌ No recent user found for testing")
        return
    
    print(f"🎯 Testing user: {test_user.username}")
    
    # Test common passwords
    test_passwords = ['123456', '12345', 'password', 'Password123', '123456789']
    
    for pwd in test_passwords:
        try:
            password_check = test_user.check_password(pwd)
            print(f"   Password '{pwd}': {'✅ CORRECT' if password_check else '❌ WRONG'}")
            
            if password_check:
                print(f"   🎯 WORKING PASSWORD FOUND: {pwd}")
                
                # Test authentication with this password
                auth_result = authenticate(username=test_user.username, password=pwd)
                print(f"   🔐 Authentication result: {'✅ SUCCESS' if auth_result else '❌ FAILED'}")
                
                if auth_result:
                    print(f"   ✅ USER CAN AUTHENTICATE SUCCESSFULLY")
                else:
                    print(f"   🚨 PASSWORD CORRECT BUT AUTHENTICATION FAILED!")
                break
        except Exception as e:
            print(f"   ⚠️  Error testing password '{pwd}': {e}")

def check_5_user_creation():
    """5. USER CREATION CHECK"""
    print(f"\n👤 5. USER CREATION METHOD CHECK")
    print('=' * 50)
    
    # Check recent users to see how they were created
    recent_users = User.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=3)
    ).order_by('-date_joined')[:3]
    
    for user in recent_users:
        print(f"\n👤 User: {user.username}")
        
        # Check password hash format
        if user.password:
            if user.password.startswith('pbkdf2_'):
                print(f"   ✅ Proper Django password hash (pbkdf2)")
            elif user.password.startswith('bcrypt'):
                print(f"   ✅ BCrypt password hash")
            elif user.password.startswith('argon2'):
                print(f"   ✅ Argon2 password hash")
            else:
                print(f"   ❌ INVALID PASSWORD HASH FORMAT: {user.password[:20]}...")
                print(f"   🚨 USER CREATED INCORRECTLY!")
        else:
            print(f"   ❌ NO PASSWORD SET!")
        
        # Check if user can be authenticated
        print(f"   🧪 Testing authentication with common passwords...")
        test_success = False
        for pwd in ['123456', '12345']:
            if user.check_password(pwd):
                auth_result = authenticate(username=user.username, password=pwd)
                print(f"      Password '{pwd}': check_password={'✅' if user.check_password(pwd) else '❌'}, authenticate={'✅' if auth_result else '❌'}")
                test_success = True
                break
        
        if not test_success:
            print(f"      ❌ No working password found")

def check_6_console_output_simulation():
    """6. CONSOLE OUTPUT SIMULATION"""
    print(f"\n🖥️  6. LOGIN SIMULATION WITH CONSOLE OUTPUT")
    print('=' * 50)
    
    # Get a test user
    test_user = User.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=3)
    ).first()
    
    if not test_user:
        print("❌ No test user found")
        return
    
    print(f"🎯 Simulating login for: {test_user.username}")
    
    # Extract mobile digits (what login form would send)
    if test_user.username.startswith('+63'):
        mobile_digits = test_user.username[3:]  # Remove +63
    else:
        mobile_digits = test_user.username
    
    print(f"📱 Login form would send: '{mobile_digits}'")
    
    # Simulate the phone strategy generation
    def generate_all_phone_strategies(raw_phone):
        strategies = []
        strategies.append(raw_phone)
        
        clean_phone = raw_phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if clean_phone != raw_phone:
            strategies.append(clean_phone)
        
        if clean_phone.startswith('+63'):
            base_digits = clean_phone[3:]
            strategies.extend([
                clean_phone,
                clean_phone[1:],
                '0' + base_digits if base_digits.startswith('9') else '09' + base_digits,
                base_digits
            ])
        else:
            digits_only = ''.join(filter(str.isdigit, clean_phone))
            
            if digits_only.startswith('9') and len(digits_only) == 10:
                strategies.extend([
                    '+63' + digits_only,
                    '63' + digits_only,
                    '0' + digits_only,
                    digits_only
                ])
        
        # Remove duplicates
        unique_strategies = []
        for strategy in strategies:
            if strategy and strategy not in unique_strategies:
                unique_strategies.append(strategy)
        
        return unique_strategies
    
    strategies = generate_all_phone_strategies(mobile_digits)
    print(f"📱 Generated {len(strategies)} strategies: {strategies}")
    
    # Test each strategy
    working_password = None
    for pwd in ['123456', '12345']:
        if test_user.check_password(pwd):
            working_password = pwd
            break
    
    if working_password:
        print(f"🔑 Using password: {working_password}")
        
        for i, strategy in enumerate(strategies, 1):
            print(f"\n🔍 Strategy {i}: Trying '{strategy}'")
            
            # Check if user exists with this username
            try:
                found_user = User.objects.get(username=strategy)
                print(f"   👤 User found: ID={found_user.id}, same user={'✅' if found_user.id == test_user.id else '❌'}")
                
                # Test authentication
                auth_result = authenticate(username=strategy, password=working_password)
                if auth_result:
                    print(f"   ✅ Authentication successful")
                    print(f"   🎉 LOGIN WOULD SUCCEED WITH THIS STRATEGY")
                    break
                else:
                    print(f"   ❌ Authentication failed")
                    
            except User.DoesNotExist:
                print(f"   ❌ No user found with username '{strategy}'")
    else:
        print(f"❌ No working password found for user")

def check_7_specific_tests():
    """7. SPECIFIC ADMIN AND SHELL TESTS"""
    print(f"\n🧪 7. SPECIFIC TEST INSTRUCTIONS")
    print('=' * 50)
    
    recent_user = User.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=3)
    ).first()
    
    if recent_user:
        print(f"📋 MANUAL TESTS TO PERFORM:")
        print(f"")
        print(f"1. Django Admin Test:")
        print(f"   - Go to /admin/")
        print(f"   - Try login with: {recent_user.username}")
        print(f"   - Try passwords: 123456, 12345")
        print(f"")
        print(f"2. Django Shell Test:")
        print(f"   python manage.py shell")
        print(f"   >>> from django.contrib.auth.models import User")
        print(f"   >>> user = User.objects.get(username='{recent_user.username}')")
        print(f"   >>> user.check_password('123456')  # Should return True/False")
        print(f"   >>> from django.contrib.auth import authenticate")
        print(f"   >>> authenticate(username='{recent_user.username}', password='123456')")
        print(f"")
        print(f"3. Database Direct Query:")
        print(f"   SELECT * FROM auth_user WHERE username = '{recent_user.username}';")
        print(f"")
        print(f"4. Check User Active Status:")
        print(f"   >>> user.is_active  # Should be True")

if __name__ == '__main__':
    print('🚀 COMPREHENSIVE AUTHENTICATION DIAGNOSTIC')
    print('=' * 70)
    print('Checking EXACT issues with user authentication and persistence')
    print()
    
    try:
        check_1_database_direct()
        check_2_authentication_backend()
        check_3_username_field_issue()
        check_4_password_validation()
        check_5_user_creation()
        check_6_console_output_simulation()
        check_7_specific_tests()
        
        print(f"\n📋 DIAGNOSTIC COMPLETE")
        print('=' * 50)
        print('🔍 NEXT STEPS:')
        print('1. Run the manual tests provided in section 7')
        print('2. Check the exact error messages from the console simulation')
        print('3. Verify the password hashing format from section 5')
        print('4. Test authentication in Django admin')
        
    except Exception as e:
        print(f"❌ Diagnostic error: {e}")
        import traceback
        traceback.print_exc()
