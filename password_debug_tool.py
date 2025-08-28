#!/usr/bin/env python3
"""
Debugging the password issue - Find out what's really happening
"""
import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password, check_password

def debug_user_password(phone_number):
    """Debug a specific user's password issue"""
    try:
        user = User.objects.get(username=phone_number)
        print(f'🔍 Debugging user: {phone_number}')
        print('=' * 50)
        print(f'User ID: {user.id}')
        print(f'Username: {user.username}')
        print(f'Is Active: {user.is_active}')
        print(f'Password Hash: {user.password}')
        print(f'Password Algorithm: {user.password.split("$")[0] if "$" in user.password else "Unknown"}')
        print()
        
        # Test various password scenarios
        test_passwords = [
            '12345',
            '123456', 
            'password',
            phone_number,
            phone_number.replace('+63', ''),
            phone_number[-4:],  # Last 4 digits
            '1234',
            '000000'
        ]
        
        print('🧪 Testing common passwords:')
        for pwd in test_passwords:
            # Test direct password check
            direct_check = user.check_password(pwd)
            
            # Test authentication
            auth_user = authenticate(username=phone_number, password=pwd)
            
            status = "✅ WORKS" if direct_check else "❌ FAIL"
            auth_status = "✅ AUTH OK" if auth_user else "❌ AUTH FAIL"
            
            print(f'   {pwd:15} | Direct: {status} | Auth: {auth_status}')
            
            if direct_check:
                print(f'   🎯 FOUND WORKING PASSWORD: {pwd}')
                return pwd
                
        print('\n❌ No working password found among common ones')
        
        # Test if password was saved correctly during registration
        print('\n🔧 Password storage analysis:')
        if user.password.startswith('pbkdf2_'):
            print('✅ Password is properly hashed with PBKDF2')
        else:
            print('❌ Password is not properly hashed!')
            
        return None
        
    except User.DoesNotExist:
        print(f'❌ User {phone_number} not found')
        return None
    except Exception as e:
        print(f'❌ Error: {e}')
        return None

def test_registration_process():
    """Test the registration password process with a dummy user"""
    print('\n🧪 Testing Registration Process:')
    print('=' * 50)
    
    test_phone = '+639999999999'
    test_password = 'testpass123'
    
    # Delete test user if exists
    try:
        User.objects.filter(username=test_phone).delete()
    except:
        pass
    
    # Create user like in registration
    print(f'Creating test user: {test_phone} with password: {test_password}')
    
    try:
        user = User.objects.create_user(
            username=test_phone,
            password=test_password
        )
        
        print(f'✅ User created successfully')
        print(f'   User ID: {user.id}')
        print(f'   Password Hash: {user.password[:50]}...')
        
        # Test immediate authentication
        auth_user = authenticate(username=test_phone, password=test_password)
        if auth_user:
            print(f'✅ Immediate authentication successful')
        else:
            print(f'❌ Immediate authentication failed')
            
        # Test direct password check
        if user.check_password(test_password):
            print(f'✅ Direct password check successful')
        else:
            print(f'❌ Direct password check failed')
            
        # Clean up
        user.delete()
        
    except Exception as e:
        print(f'❌ Error creating test user: {e}')

if __name__ == '__main__':
    print('🔐 GrowFi Password Debug Tool')
    print('=' * 60)
    
    # Test recent users
    recent_users = ['+639214392306', '+639919101001']
    
    for phone in recent_users:
        password = debug_user_password(phone)
        if password:
            print(f'\n🎯 SOLUTION for {phone}: Use password "{password}"')
        print('\n' + '-'*60)
    
    # Test registration process
    test_registration_process()
    
    print('\n📋 SUMMARY:')
    print('='*60)
    print('If passwords are properly hashed but authentication fails,')
    print('the issue might be in the authentication backend or')
    print('in how the password was originally entered during registration.')
