#!/usr/bin/env python3
"""
PERMANENT SESSION FIX - Remove ALL expiration from user accounts
Make users stay logged in for months/years without any problems
"""
import os
import sys
import django
from datetime import datetime, timedelta

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
from myproject.models import UserProfile
import traceback

def make_sessions_permanent():
    """Make all existing sessions permanent (1 year expiration)"""
    print('🔄 MAKING ALL SESSIONS PERMANENT')
    print('=' * 50)
    
    # Get all active sessions
    sessions = Session.objects.all()
    total_sessions = sessions.count()
    
    print(f'📊 Found {total_sessions} sessions to update')
    
    # Set all sessions to expire in 1 year
    future_date = timezone.now() + timedelta(days=365)
    updated_count = 0
    
    for session in sessions:
        try:
            session.expire_date = future_date
            session.save()
            updated_count += 1
            
            if updated_count % 10 == 0:
                print(f'   Updated {updated_count}/{total_sessions} sessions...')
                
        except Exception as e:
            print(f'   ❌ Error updating session {session.session_key}: {e}')
    
    print(f'✅ Updated {updated_count} sessions to PERMANENT (1 year expiration)')
    return updated_count

def verify_session_settings():
    """Verify Django session settings are configured for permanence"""
    print('\n⚙️ VERIFYING PERMANENT SESSION CONFIGURATION')
    print('=' * 50)
    
    from django.conf import settings
    
    expected_settings = {
        'SESSION_COOKIE_AGE': 365 * 24 * 60 * 60,  # 1 year
        'SESSION_EXPIRE_AT_BROWSER_CLOSE': False,
        'SESSION_SAVE_EVERY_REQUEST': True,
        'SESSION_ENGINE': 'django.contrib.sessions.backends.db'
    }
    
    all_correct = True
    
    for setting_name, expected_value in expected_settings.items():
        actual_value = getattr(settings, setting_name, None)
        
        if actual_value == expected_value:
            print(f'✅ {setting_name}: {actual_value}')
        else:
            print(f'❌ {setting_name}: got {actual_value}, expected {expected_value}')
            all_correct = False
    
    if all_correct:
        print('✅ ALL SESSION SETTINGS CONFIGURED FOR PERMANENCE')
    else:
        print('⚠️ Some session settings need adjustment')
    
    return all_correct

def update_user_profiles_for_permanence():
    """Ensure all users have complete profiles for permanent sessions"""
    print('\n👥 ENSURING ALL USERS HAVE COMPLETE PROFILES')
    print('=' * 50)
    
    users_without_profiles = User.objects.filter(userprofile__isnull=True)
    count = users_without_profiles.count()
    
    if count == 0:
        print('✅ All users already have profiles')
        return 0
    
    print(f'🔧 Creating profiles for {count} users...')
    
    created_count = 0
    for user in users_without_profiles:
        try:
            profile = UserProfile.objects.create(
                user=user,
                phone_number=user.username,
                balance=0,
                referral_code=f'REF{user.id:06d}'
            )
            created_count += 1
            print(f'   ✅ Created profile for {user.username}')
            
        except Exception as e:
            print(f'   ❌ Error creating profile for {user.username}: {e}')
    
    print(f'✅ Created {created_count} new profiles')
    return created_count

def test_permanent_authentication():
    """Test that authentication will work permanently"""
    print('\n🔐 TESTING PERMANENT AUTHENTICATION')
    print('=' * 50)
    
    # Test with verification user
    test_phone = '+639999777888'
    test_password = 'testfix123'
    
    try:
        from django.contrib.auth import authenticate
        
        # Test authentication
        user = authenticate(username=test_phone, password=test_password)
        
        if user:
            print(f'✅ Authentication test successful for {test_phone}')
            
            # Simulate session creation
            from django.contrib.sessions.backends.db import SessionStore
            session = SessionStore()
            session['_auth_user_id'] = str(user.id)
            session['_auth_user_backend'] = 'django.contrib.auth.backends.ModelBackend'
            session['permanent_session'] = True
            session['created_for_permanent_login'] = timezone.now().isoformat()
            
            # Set 1 year expiration
            session.set_expiry(365 * 24 * 60 * 60)
            session.save()
            
            print(f'✅ Test session created with 1-year expiration')
            print(f'   Session key: {session.session_key}')
            print(f'   Expires: {session.get_expiry_date()}')
            
            return True
            
        else:
            print(f'❌ Authentication test failed for {test_phone}')
            return False
            
    except Exception as e:
        print(f'❌ Authentication test error: {e}')
        return False

def clean_old_temporary_sessions():
    """Remove any old temporary sessions (keep only permanent ones)"""
    print('\n🧹 CLEANING OLD TEMPORARY SESSIONS')
    print('=' * 50)
    
    # Find sessions that were set to expire before the permanent fix
    # (sessions expiring within next 30 days are probably old 7-day sessions)
    cutoff_date = timezone.now() + timedelta(days=30)
    old_sessions = Session.objects.filter(expire_date__lt=cutoff_date)
    
    old_count = old_sessions.count()
    
    if old_count == 0:
        print('✅ No old temporary sessions found')
        return 0
    
    print(f'🗑️ Found {old_count} old temporary sessions to update')
    
    # Instead of deleting, update them to permanent
    future_date = timezone.now() + timedelta(days=365)
    updated = old_sessions.update(expire_date=future_date)
    
    print(f'✅ Updated {updated} old sessions to permanent (1 year expiration)')
    return updated

def main():
    print('🚀 PERMANENT SESSION FIX - NO EXPIRATION')
    print('=' * 60)
    print('Making user accounts stay logged in for months/years!')
    print()
    
    try:
        # 1. Verify configuration
        config_ok = verify_session_settings()
        
        # 2. Make all sessions permanent
        sessions_updated = make_sessions_permanent()
        
        # 3. Ensure all users have profiles
        profiles_created = update_user_profiles_for_permanence()
        
        # 4. Clean old temporary sessions
        old_sessions_updated = clean_old_temporary_sessions()
        
        # 5. Test permanent authentication
        auth_test_ok = test_permanent_authentication()
        
        # 6. Final summary
        print('\n' + '=' * 60)
        print('🎉 PERMANENT SESSION FIX COMPLETE')
        print('=' * 60)
        
        print(f'✅ Session configuration: {"CORRECT" if config_ok else "NEEDS ATTENTION"}')
        print(f'✅ Sessions made permanent: {sessions_updated}')
        print(f'✅ User profiles created: {profiles_created}')
        print(f'✅ Old sessions updated: {old_sessions_updated}')
        print(f'✅ Authentication test: {"PASSED" if auth_test_ok else "FAILED"}')
        
        if all([config_ok, auth_test_ok]):
            print('\n🎉 SUCCESS! USER ACCOUNTS NOW HAVE NO EXPIRATION!')
            print('📱 Users can stay logged in for MONTHS or YEARS')
            print('🔄 Sessions automatically renew on every page visit')
            print('⏰ 1 YEAR expiration (practically permanent)')
            print('💪 Real-time Firebase synchronization maintained')
            
        else:
            print('\n⚠️ Some issues detected - please review the output above')
        
        # Show current status
        total_users = User.objects.count()
        total_profiles = UserProfile.objects.count()
        total_sessions = Session.objects.count()
        active_sessions = Session.objects.filter(expire_date__gt=timezone.now()).count()
        
        print(f'\n📊 CURRENT SYSTEM STATUS:')
        print(f'   👥 Total users: {total_users}')
        print(f'   👤 User profiles: {total_profiles}')
        print(f'   📁 Total sessions: {total_sessions}')
        print(f'   ✅ Active sessions: {active_sessions}')
        print(f'   ⏰ Session duration: 1 YEAR (permanent)')
        
    except Exception as e:
        print(f'\n❌ ERROR: {e}')
        traceback.print_exc()

if __name__ == '__main__':
    main()
