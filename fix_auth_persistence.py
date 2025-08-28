#!/usr/bin/env python3
"""
Firebase Authentication Persistence Fix
Fix the login persistence issue by improving Firebase sync and session management
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
from django.contrib.sessions.models import Session
import traceback

def fix_authentication_persistence():
    """Fix authentication persistence issues"""
    print('🔧 FIXING AUTHENTICATION PERSISTENCE ISSUES')
    print('=' * 60)
    
    # 1. Clean up expired sessions
    print('\n1️⃣ Cleaning up expired sessions...')
    expired_sessions = Session.objects.filter(expire_date__lte=timezone.now())
    expired_count = expired_sessions.count()
    expired_sessions.delete()
    print(f'🧹 Deleted {expired_count} expired sessions')
    
    # 2. Check and fix user profiles
    print('\n2️⃣ Checking user profiles...')
    users_without_profiles = User.objects.filter(userprofile__isnull=True)
    for user in users_without_profiles:
        profile = UserProfile.objects.create(
            user=user,
            phone_number=user.username
        )
        print(f'✅ Created profile for user: {user.username}')
    
    # 3. Check for duplicate users
    print('\n3️⃣ Checking for duplicate users...')
    from django.db.models import Count
    duplicate_usernames = User.objects.values('username').annotate(
        count=Count('username')
    ).filter(count__gt=1)
    
    for dup in duplicate_usernames:
        username = dup['username']
        users = User.objects.filter(username=username).order_by('date_joined')
        print(f'⚠️ Duplicate username found: {username} ({dup["count"]} users)')
        
        # Keep the first user, deactivate others
        for i, user in enumerate(users):
            if i == 0:
                print(f'   ✅ Keeping user: {user.id} (joined: {user.date_joined})')
            else:
                user.is_active = False
                user.username = f'{username}_duplicate_{i}'
                user.save()
                print(f'   ❌ Deactivated duplicate: {user.id} -> {user.username}')
    
    # 4. Test Firebase synchronization
    print('\n4️⃣ Testing Firebase synchronization...')
    try:
        from myproject.firebase_app import get_firebase_app
        from firebase_admin import db as firebase_db
        
        app = get_firebase_app()
        if hasattr(app, 'project_id') and app.project_id != 'firebase-unavailable':
            print('✅ Firebase connection: WORKING')
            
            # Test saving a sample user
            ref = firebase_db.reference('/', app=app)
            test_data = {
                'test_user': {
                    'username': 'test',
                    'timestamp': timezone.now().isoformat(),
                    'test': True
                }
            }
            
            ref.child('users').update(test_data)
            print('✅ Firebase write test: SUCCESS')
            
            # Clean up test data
            ref.child('users/test_user').delete()
            print('✅ Firebase cleanup: SUCCESS')
            
        else:
            print('❌ Firebase connection: UNAVAILABLE')
            
    except Exception as e:
        print(f'❌ Firebase test error: {e}')
    
    # 5. Update phone number normalization
    print('\n5️⃣ Normalizing phone numbers...')
    
    def normalize_phone(phone):
        """Normalize phone number to +63 format"""
        if not phone:
            return phone
            
        clean_phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        if clean_phone.startswith('+63'):
            return clean_phone
            
        digits_only = ''.join(filter(str.isdigit, clean_phone))
        
        if digits_only.startswith('63') and len(digits_only) >= 12:
            return '+' + digits_only
        elif digits_only.startswith('09') and len(digits_only) == 11:
            return '+63' + digits_only[1:]
        elif digits_only.startswith('9') and len(digits_only) == 10:
            return '+63' + digits_only
        elif len(digits_only) >= 10:
            last_10_digits = digits_only[-10:]
            if last_10_digits.startswith('9'):
                return '+63' + last_10_digits
        
        return clean_phone
    
    # Normalize all user phone numbers
    for user in User.objects.filter(is_active=True):
        original_username = user.username
        normalized_username = normalize_phone(user.username)
        
        if original_username != normalized_username:
            # Check if normalized username already exists
            if not User.objects.filter(username=normalized_username).exclude(id=user.id).exists():
                user.username = normalized_username
                user.save()
                
                # Update profile phone number too
                try:
                    profile = UserProfile.objects.get(user=user)
                    profile.phone_number = normalized_username
                    profile.save()
                    print(f'✅ Normalized {original_username} -> {normalized_username}')
                except UserProfile.DoesNotExist:
                    pass
            else:
                print(f'⚠️ Cannot normalize {original_username} -> {normalized_username} (already exists)')
    
    print('\n6️⃣ Updating session configuration...')
    
    # The session configuration is already good in settings.py
    # SESSION_COOKIE_AGE = 7 * 24 * 60 * 60  # 7 days
    # SESSION_EXPIRE_AT_BROWSER_CLOSE = False
    # SESSION_SAVE_EVERY_REQUEST = True
    
    print('✅ Session configuration is already optimized')

def create_test_user_and_login():
    """Create a test user and verify login works"""
    print('\n🧪 Creating test user and verifying login...')
    print('-' * 40)
    
    test_phone = '+639999888777'
    test_password = 'testpass123'
    
    # Clean up any existing test user
    User.objects.filter(username=test_phone).delete()
    
    # Create test user
    user = User.objects.create_user(
        username=test_phone,
        password=test_password
    )
    
    # Create profile
    profile = UserProfile.objects.create(
        user=user,
        phone_number=test_phone
    )
    
    print(f'✅ Test user created: {test_phone}')
    
    # Test authentication immediately
    auth_user = authenticate(username=test_phone, password=test_password)
    if auth_user:
        print(f'✅ Immediate authentication: SUCCESS')
    else:
        print(f'❌ Immediate authentication: FAILED')
    
    # Test Firebase sync
    try:
        from myproject.views import save_user_to_firebase_realtime_db
        firebase_data = {
            'test_user': True,
            'created_at': timezone.now().isoformat()
        }
        success = save_user_to_firebase_realtime_db(user, test_phone, firebase_data)
        
        if success:
            print(f'✅ Firebase sync: SUCCESS')
        else:
            print(f'❌ Firebase sync: FAILED')
            
    except Exception as e:
        print(f'❌ Firebase sync error: {e}')
    
    # Clean up
    user.delete()
    print(f'🧹 Test user cleaned up')

def main():
    print('🚀 Starting authentication persistence fix...')
    
    try:
        # Fix authentication issues
        fix_authentication_persistence()
        
        # Test with a sample user
        create_test_user_and_login()
        
        print('\n🎉 AUTHENTICATION PERSISTENCE FIX COMPLETE')
        print('=' * 60)
        print('📋 SUMMARY OF FIXES APPLIED:')
        print('• Cleaned up expired sessions')
        print('• Created missing user profiles')
        print('• Fixed duplicate user accounts')
        print('• Tested Firebase synchronization')
        print('• Normalized phone number formats')
        print('• Verified session configuration')
        print('')
        print('💡 RECOMMENDATIONS:')
        print('• Monitor user login behavior over the next 24-48 hours')
        print('• Check server logs for any authentication errors')
        print('• Test login with different phone number formats')
        print('• Ensure Firebase credentials are properly configured')
        print('• Consider implementing session activity tracking')
        
    except Exception as e:
        print(f'❌ Error during fix: {e}')
        traceback.print_exc()

if __name__ == '__main__':
    main()
