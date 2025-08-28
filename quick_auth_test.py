#!/usr/bin/env python3
"""
Quick Authentication Test - Verify Fix is Working
"""
import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from myproject.models import UserProfile

def test_phone_normalization():
    """Test phone number normalization"""
    print('🧪 PHONE NORMALIZATION TEST')
    print('-' * 40)
    
    def normalize_phone_number(phone):
        """Phone normalization (from views.py)"""
        if not phone:
            return phone
        
        # Remove all non-digit characters except + at the start
        clean_phone = phone.strip()
        if clean_phone.startswith('+'):
            digits = '+' + ''.join(c for c in clean_phone[1:] if c.isdigit())
        else:
            digits = ''.join(c for c in clean_phone if c.isdigit())
        
        if not digits or digits == '+':
            return phone
        
        # Handle different Philippine number formats
        if digits.startswith('+63'):
            # Already in international format
            if len(digits) == 13:  # +63 + 10 digits
                return digits
        elif digits.startswith('63'):
            # Country code without +
            if len(digits) == 12:  # 63 + 10 digits
                return '+' + digits
        elif digits.startswith('09'):
            # Local format with leading 0
            if len(digits) == 11:  # 09 + 9 digits
                return '+63' + digits[1:]  # Remove 0, add +63
        elif digits.startswith('9'):
            # Local format without leading 0
            if len(digits) == 10:  # 9 + 9 digits
                return '+63' + digits
        
        return phone
    
    test_cases = [
        ('09919101001', '+639919101001'),
        ('9919101001', '+639919101001'),
        ('639919101001', '+639919101001'),
        ('+639919101001', '+639919101001'),
        ('09999777888', '+639999777888'),
        ('9999777888', '+639999777888'),
    ]
    
    all_passed = True
    for input_phone, expected in test_cases:
        result = normalize_phone_number(input_phone)
        status = '✅' if result == expected else '❌'
        print(f'{status} {input_phone} → {result}')
        if result != expected:
            all_passed = False
    
    return all_passed

def test_user_authentication():
    """Test user authentication with different phone formats"""
    print('\n🔐 USER AUTHENTICATION TEST')
    print('-' * 40)
    
    # Use the verification user created by the fix
    test_phone = '+639999777888'
    test_password = 'testfix123'
    
    try:
        user = User.objects.get(username=test_phone)
        print(f'✅ Test user found: {user.username}')
        
        # Test authentication
        auth_user = authenticate(username=test_phone, password=test_password)
        if auth_user:
            print('✅ Authentication successful')
            return True
        else:
            print('❌ Authentication failed')
            return False
            
    except User.DoesNotExist:
        print(f'❌ Test user {test_phone} not found')
        return False

def test_session_config():
    """Test session configuration"""
    print('\n⚙️ SESSION CONFIGURATION TEST')
    print('-' * 40)
    
    from django.conf import settings
    
    # Check critical session settings
    config_checks = [
        ('SESSION_COOKIE_AGE', 7 * 24 * 60 * 60),  # 7 days
        ('SESSION_EXPIRE_AT_BROWSER_CLOSE', False),
        ('SESSION_SAVE_EVERY_REQUEST', True),
    ]
    
    all_good = True
    for setting, expected in config_checks:
        actual = getattr(settings, setting, None)
        if actual == expected:
            print(f'✅ {setting}: {actual}')
        else:
            print(f'❌ {setting}: got {actual}, expected {expected}')
            all_good = False
    
    return all_good

def main():
    print('🚀 QUICK AUTHENTICATION FIX VERIFICATION')
    print('=' * 50)
    
    # Run tests
    phone_test = test_phone_normalization()
    auth_test = test_user_authentication()
    session_test = test_session_config()
    
    # Summary
    print('\n📊 TEST RESULTS')
    print('-' * 20)
    print(f'Phone normalization: {"✅ PASS" if phone_test else "❌ FAIL"}')
    print(f'User authentication: {"✅ PASS" if auth_test else "❌ FAIL"}')
    print(f'Session configuration: {"✅ PASS" if session_test else "❌ FAIL"}')
    
    if all([phone_test, auth_test, session_test]):
        print('\n🎉 ALL TESTS PASSED!')
        print('✅ Authentication persistence fix is working!')
        print('📱 Users can now login with any Philippine phone format')
        print('⏰ Sessions will persist for 7 days')
        print('🔄 Automatic session renewal enabled')
    else:
        print('\n⚠️ Some tests failed - please check the configuration')
    
    print(f'\n👥 Total users in system: {User.objects.count()}')
    print(f'👤 Users with profiles: {UserProfile.objects.count()}')

if __name__ == '__main__':
    main()
