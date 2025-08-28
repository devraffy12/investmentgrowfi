#!/usr/bin/env python3
"""
Authentication Issue Test
Check why users are getting "Account not found" error after some time
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
from myproject.models import UserProfile
from django.utils import timezone
import traceback

def test_user_authentication():
    """Test recent users for authentication issues"""
    print('🔍 Testing Firebase user authentication and persistence...')
    print('=' * 60)

    # Check recent users who might be experiencing issues
    recent_users = User.objects.filter(is_active=True).order_by('-date_joined')[:10]

    print(f"Found {len(recent_users)} recent active users")

    for user in recent_users:
        print(f'\n👤 User: {user.username}')
        print(f'   📅 Joined: {user.date_joined}')
        print(f'   🔐 Last login: {user.last_login or "Never"}')
        print(f'   ✅ Active: {user.is_active}')
        
        # Check profile
        try:
            profile = UserProfile.objects.get(user=user)
            print(f'   📱 Phone: {profile.phone_number}')
            print(f'   💰 Balance: {profile.balance}')
        except UserProfile.DoesNotExist:
            print(f'   ❌ No profile found')
        
        # Test authentication with common passwords
        test_passwords = ['12345', '123456', 'password', 'admin', '1234']
        auth_success = False
        
        for pwd in test_passwords:
            try:
                if user.check_password(pwd):
                    print(f'   🔑 Password found: {pwd}')
                    
                    # Test Django authentication
                    auth_user = authenticate(username=user.username, password=pwd)
                    if auth_user:
                        print(f'   ✅ Django Auth: SUCCESS')
                        auth_success = True
                    else:
                        print(f'   ❌ Django Auth: FAILED')
                    break
            except Exception as e:
                print(f'   ❌ Password test error: {e}')
        
        if not auth_success:
            print(f'   ❓ Password: Unknown (not common passwords)')

def test_firebase_sync():
    """Test Firebase synchronization"""
    print('\n🔥 Testing Firebase sync status...')
    print('-' * 40)
    
    try:
        from myproject.firebase_app import get_firebase_app
        app = get_firebase_app()
        
        if hasattr(app, 'project_id') and app.project_id != 'firebase-unavailable':
            print('✅ Firebase connection: WORKING')
            
            # Test Firebase database access
            from firebase_admin import db as firebase_db
            ref = firebase_db.reference('/', app=app)
            users_ref = ref.child('users')
            
            # Check if users exist in Firebase
            firebase_users = users_ref.get()
            if firebase_users:
                print(f'✅ Firebase users found: {len(firebase_users)}')
                
                # Sample a few users
                sample_keys = list(firebase_users.keys())[:5]
                for key in sample_keys:
                    user_data = firebase_users[key]
                    username = user_data.get('username', 'Unknown')
                    last_login = user_data.get('last_login_time', 'Never')
                    print(f'   📱 Firebase user: {key} -> {username} (last login: {last_login})')
            else:
                print('❌ No users found in Firebase database')
                
        else:
            print('❌ Firebase connection: UNAVAILABLE')
            
    except Exception as e:
        print(f'❌ Firebase test error: {e}')
        traceback.print_exc()

def test_specific_user_login(phone_number):
    """Test login for a specific user"""
    print(f'\n🧪 Testing specific user login: {phone_number}')
    print('-' * 40)
    
    try:
        # Try to find user
        user = User.objects.get(username=phone_number)
        print(f'✅ User found: {user.username}')
        print(f'   📅 Joined: {user.date_joined}')
        print(f'   🔐 Last login: {user.last_login or "Never"}')
        print(f'   ✅ Active: {user.is_active}')
        
        # Test with common passwords
        test_passwords = ['12345', '123456', 'password']
        for pwd in test_passwords:
            if user.check_password(pwd):
                print(f'   🔑 Password: {pwd}')
                
                # Test authentication
                auth_user = authenticate(username=phone_number, password=pwd)
                if auth_user:
                    print(f'   ✅ Authentication: SUCCESS')
                    
                    # Check profile
                    try:
                        profile = UserProfile.objects.get(user=user)
                        print(f'   📱 Profile phone: {profile.phone_number}')
                        print(f'   💰 Balance: {profile.balance}')
                    except UserProfile.DoesNotExist:
                        print(f'   ❌ No profile found')
                        
                else:
                    print(f'   ❌ Authentication: FAILED')
                break
        
    except User.DoesNotExist:
        print(f'❌ User not found: {phone_number}')
        
        # Try to find similar users
        similar_users = User.objects.filter(username__contains=phone_number[-8:])
        if similar_users:
            print(f'   💡 Found similar users:')
            for u in similar_users[:3]:
                print(f'      - {u.username}')

def check_session_persistence():
    """Check session configuration for persistence issues"""
    print('\n🔧 Checking session persistence configuration...')
    print('-' * 40)
    
    from django.conf import settings
    
    session_age = getattr(settings, 'SESSION_COOKIE_AGE', None)
    session_expire_browser = getattr(settings, 'SESSION_EXPIRE_AT_BROWSER_CLOSE', None)
    session_engine = getattr(settings, 'SESSION_ENGINE', None)
    session_save_every_request = getattr(settings, 'SESSION_SAVE_EVERY_REQUEST', None)
    
    print(f'⏰ Session cookie age: {session_age} seconds ({session_age//3600} hours)')
    print(f'🔒 Expire at browser close: {session_expire_browser}')
    print(f'💾 Session engine: {session_engine}')
    print(f'💾 Save every request: {session_save_every_request}')
    
    # Check if settings are optimal for persistence
    issues = []
    if session_age < 86400:  # Less than 24 hours
        issues.append("❌ Session expires too quickly (< 24 hours)")
    
    if session_expire_browser:
        issues.append("❌ Sessions expire when browser closes")
    
    if not session_save_every_request:
        issues.append("⚠️ Sessions not saved on every request")
    
    if issues:
        print('\n🚨 Potential issues found:')
        for issue in issues:
            print(f'   {issue}')
    else:
        print('\n✅ Session configuration looks good')

def main():
    print('🚀 Starting authentication issue analysis...')
    
    # Run all tests
    test_user_authentication()
    test_firebase_sync()
    check_session_persistence()
    
    # Test specific users if needed
    print('\n🧪 Testing specific problematic users...')
    test_phones = ['+639214392306', '+639333333333', '+639222222222']
    
    for phone in test_phones:
        test_specific_user_login(phone)
    
    print('\n🏁 ANALYSIS COMPLETE')
    print('=' * 60)

if __name__ == '__main__':
    main()
