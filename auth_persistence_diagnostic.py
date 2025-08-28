#!/usr/bin/env python3
"""
Firebase Authentication Persistence Diagnostic Tool
Diagnose and fix user login persistence issues
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
from django.contrib.sessions.models import Session
from django.utils import timezone

def diagnose_authentication_issue():
    """Comprehensive authentication diagnosis"""
    print('🔍 FIREBASE AUTHENTICATION PERSISTENCE DIAGNOSIS')
    print('=' * 60)
    
    # 1. Check Django user database integrity
    print('\n1️⃣ DJANGO USER DATABASE CHECK')
    print('-' * 40)
    
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    recent_users = User.objects.filter(date_joined__gte=timezone.now() - timedelta(days=7)).count()
    
    print(f'📊 Total users: {total_users}')
    print(f'✅ Active users: {active_users}')
    print(f'🆕 Users registered in last 7 days: {recent_users}')
    
    # 2. Check session configuration
    print('\n2️⃣ SESSION CONFIGURATION CHECK')
    print('-' * 40)
    
    from django.conf import settings
    
    session_age = getattr(settings, 'SESSION_COOKIE_AGE', None)
    session_expire_browser = getattr(settings, 'SESSION_EXPIRE_AT_BROWSER_CLOSE', None)
    session_engine = getattr(settings, 'SESSION_ENGINE', None)
    
    print(f'⏰ Session cookie age: {session_age} seconds ({session_age//3600} hours)')
    print(f'🔒 Expire at browser close: {session_expire_browser}')
    print(f'💾 Session engine: {session_engine}')
    
    # 3. Check active sessions
    print('\n3️⃣ ACTIVE SESSIONS CHECK')
    print('-' * 40)
    
    try:
        active_sessions = Session.objects.filter(expire_date__gt=timezone.now()).count()
        expired_sessions = Session.objects.filter(expire_date__lte=timezone.now()).count()
        
        print(f'✅ Active sessions: {active_sessions}')
        print(f'❌ Expired sessions: {expired_sessions}')
        
        # Show recent sessions
        recent_sessions = Session.objects.filter(expire_date__gt=timezone.now()).order_by('-expire_date')[:5]
        for session in recent_sessions:
            print(f'   📅 Session expires: {session.expire_date}')
            
    except Exception as e:
        print(f'❌ Session check error: {e}')
    
    # 4. Test authentication for recent users
    print('\n4️⃣ AUTHENTICATION TEST FOR RECENT USERS')
    print('-' * 40)
    
    recent_users = User.objects.filter(date_joined__gte=timezone.now() - timedelta(days=3)).order_by('-date_joined')[:3]
    
    for user in recent_users:
        print(f'\\n🧪 Testing user: {user.username}')
        print(f'   📅 Joined: {user.date_joined}')
        print(f'   🔒 Last login: {user.last_login or "Never"}')
        print(f'   ✅ Is active: {user.is_active}')
        
        # Test common passwords
        test_passwords = ['12345', '123456', 'password']
        password_found = False
        
        for pwd in test_passwords:
            if user.check_password(pwd):
                print(f'   🎯 Working password: {pwd}')
                
                # Test authentication
                auth_user = authenticate(username=user.username, password=pwd)
                if auth_user:
                    print(f'   ✅ Authentication: WORKS')
                else:
                    print(f'   ❌ Authentication: FAILED (but password check passed)')
                    
                password_found = True
                break
                
        if not password_found:
            print(f'   ❓ Password: Unknown (not common passwords)')
    
    # 5. Check Firebase connectivity
    print('\n5️⃣ FIREBASE CONNECTIVITY CHECK')
    print('-' * 40)
    
    try:
        # Check if Firebase is configured
        firebase_configured = hasattr(settings, 'FIREBASE_CREDENTIALS_JSON') or os.getenv('FIREBASE_CREDENTIALS_JSON')
        print(f'🔥 Firebase configured: {firebase_configured}')
        
        if firebase_configured:
            # Try to initialize Firebase (basic check)
            try:
                from myproject.firebase_app import get_firebase_app
                app = get_firebase_app()
                print(f'✅ Firebase app initialized successfully')
                
                # Basic project info
                if hasattr(app, 'project_id'):
                    print(f'📋 Project ID: {app.project_id}')
                    
            except Exception as firebase_error:
                print(f'❌ Firebase initialization error: {firebase_error}')
        else:
            print(f'❌ Firebase not configured')
            
    except Exception as e:
        print(f'❌ Firebase check error: {e}')
    
    return True

def identify_persistence_issues():
    """Identify specific persistence issues"""
    print('\n🔧 PERSISTENCE ISSUE ANALYSIS')
    print('=' * 60)
    
    issues = []
    solutions = []
    
    from django.conf import settings
    
    # Check session configuration issues
    session_age = getattr(settings, 'SESSION_COOKIE_AGE', 1209600)  # Default 2 weeks
    
    if session_age < 86400:  # Less than 24 hours
        issues.append("❌ Session expires too quickly (< 24 hours)")
        solutions.append("✅ Increase SESSION_COOKIE_AGE to at least 86400 (24 hours)")
    
    session_expire_browser = getattr(settings, 'SESSION_EXPIRE_AT_BROWSER_CLOSE', False)
    if session_expire_browser:
        issues.append("❌ Sessions expire when browser closes")
        solutions.append("✅ Set SESSION_EXPIRE_AT_BROWSER_CLOSE = False")
    
    # Check production vs development settings
    is_production = getattr(settings, 'IS_PRODUCTION', False)
    session_secure = getattr(settings, 'SESSION_COOKIE_SECURE', False)
    
    if is_production and not session_secure:
        issues.append("❌ SESSION_COOKIE_SECURE should be True in production")
        solutions.append("✅ Ensure SESSION_COOKIE_SECURE = IS_PRODUCTION")
    
    # Check database sessions
    session_engine = getattr(settings, 'SESSION_ENGINE', '')
    if 'cached_db' in session_engine:
        issues.append("⚠️ Using cached_db sessions - may lose data if cache clears")
        solutions.append("💡 Consider using 'django.contrib.sessions.backends.db' for better persistence")
    
    print('🚨 IDENTIFIED ISSUES:')
    for issue in issues:
        print(f'   {issue}')
    
    print('\n💡 RECOMMENDED SOLUTIONS:')
    for solution in solutions:
        print(f'   {solution}')
    
    return issues, solutions

def create_authentication_test():
    """Create a test to verify authentication works"""
    print('\n🧪 AUTHENTICATION TEST SUITE')
    print('=' * 60)
    
    # Test basic Django authentication
    print('1. Testing Django authentication system...')
    
    try:
        # Create a temporary test user
        test_phone = '+639999999999'
        test_password = 'testpass123'
        
        # Clean up any existing test user
        User.objects.filter(username=test_phone).delete()
        
        # Create test user
        test_user = User.objects.create_user(
            username=test_phone,
            password=test_password
        )
        
        print(f'✅ Test user created: {test_phone}')
        
        # Test authentication immediately
        auth_user = authenticate(username=test_phone, password=test_password)
        if auth_user:
            print(f'✅ Immediate authentication: WORKS')
        else:
            print(f'❌ Immediate authentication: FAILED')
            
        # Test password check
        if test_user.check_password(test_password):
            print(f'✅ Password check: WORKS')
        else:
            print(f'❌ Password check: FAILED')
            
        # Clean up
        test_user.delete()
        print(f'🧹 Test user cleaned up')
        
    except Exception as e:
        print(f'❌ Authentication test error: {e}')

if __name__ == '__main__':
    print('🚀 Starting comprehensive authentication diagnosis...')
    
    # Run all diagnostic checks
    diagnose_authentication_issue()
    identify_persistence_issues()
    create_authentication_test()
    
    print('\n🏁 DIAGNOSIS COMPLETE')
    print('=' * 60)
    print('📋 SUMMARY OF FINDINGS:')
    print('• Check the session configuration issues above')
    print('• Verify Firebase connectivity is working')
    print('• Test authentication with known working passwords')
    print('• Consider session persistence improvements')
    print('\\n💡 NEXT STEPS:')
    print('• Apply the recommended configuration changes')
    print('• Test with a known user account')
    print('• Monitor session behavior over 24+ hours')
    print('• Check browser developer tools for session cookies')
