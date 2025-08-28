#!/usr/bin/env python3
"""
Password Recovery Tool - Recover original user passwords
"""
import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

def find_working_password(phone_number):
    """Brute force find the working password for a user"""
    try:
        user = User.objects.get(username=phone_number)
        
        # Extended list of possible passwords
        possible_passwords = [
            # Common passwords
            '12345', '123456', '1234', '123', 
            'password', 'admin', '000000', '111111',
            
            # Phone-based passwords
            phone_number,  # Full phone
            phone_number.replace('+63', ''),  # Without country code
            phone_number.replace('+63', '').replace('9', '', 1),  # Without +63 and first 9
            phone_number[-4:],  # Last 4 digits
            phone_number[-6:],  # Last 6 digits
            phone_number[-8:],  # Last 8 digits
            
            # Date-based (common registration dates)
            '2025', '08', '27', '26', '28',
            '082725', '082625', '082825',
            '270825', '260825', '280825',
            
            # Common number patterns
            '1111', '2222', '3333', '4444', '5555', 
            '6666', '7777', '8888', '9999', '0000',
            '1122', '1234', '4321', '1111',
            
            # Birth years (common ages 18-60)
            '1990', '1991', '1992', '1993', '1994', '1995', '1996', '1997', '1998', '1999',
            '2000', '2001', '2002', '2003', '2004', '2005',
            
            # Common Filipino passwords
            'pinoy', 'pinas', 'pilipinas', 'manila',
            
            # Names (common Filipino names)
            'maria', 'jose', 'juan', 'ana', 'pedro', 'rosa'
        ]
        
        print(f'🔍 Testing {len(possible_passwords)} possible passwords for {phone_number}...')
        
        for i, pwd in enumerate(possible_passwords):
            if user.check_password(pwd):
                print(f'🎯 FOUND PASSWORD: "{pwd}"')
                
                # Verify with authentication
                auth_user = authenticate(username=phone_number, password=pwd)
                if auth_user:
                    print(f'✅ Authentication confirmed!')
                    return pwd
                else:
                    print(f'❌ Authentication failed, but password check passed (weird!)')
                    return pwd
                    
            # Progress indicator
            if (i + 1) % 20 == 0:
                print(f'   Tested {i + 1}/{len(possible_passwords)} passwords...')
                
        print(f'❌ No password found after testing {len(possible_passwords)} possibilities')
        return None
        
    except User.DoesNotExist:
        print(f'❌ User {phone_number} not found')
        return None
    except Exception as e:
        print(f'❌ Error: {e}')
        return None

def create_password_reset_for_user(phone_number, new_password="user123"):
    """Create a new password for a user and test it"""
    try:
        user = User.objects.get(username=phone_number)
        
        print(f'🔧 Resetting password for {phone_number} to "{new_password}"')
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        # Test the new password
        auth_user = authenticate(username=phone_number, password=new_password)
        if auth_user:
            print(f'✅ Password reset successful! New password: "{new_password}"')
            return new_password
        else:
            print(f'❌ Password reset failed!')
            return None
            
    except User.DoesNotExist:
        print(f'❌ User {phone_number} not found')
        return None
    except Exception as e:
        print(f'❌ Error: {e}')
        return None

if __name__ == '__main__':
    print('🔐 GrowFi Password Recovery Tool')
    print('=' * 60)
    
    # Test users that need password recovery
    problem_users = ['+639919101001']  # Your account
    
    for phone in problem_users:
        print(f'\\n🔍 Processing {phone}...')
        print('='*50)
        
        # First try to find the existing password
        password = find_working_password(phone)
        
        if password:
            print(f'✅ Existing password found: "{password}"')
        else:
            print(f'❌ Could not find existing password')
            
            # Ask if we should reset
            print(f'\\n🤔 Should we reset the password for {phone}?')
            choice = input('Enter new password (or press Enter to skip): ').strip()
            
            if choice:
                new_password = create_password_reset_for_user(phone, choice)
                if new_password:
                    print(f'🎯 SOLUTION: User {phone} can now login with password "{new_password}"')
            else:
                print(f'⏭️ Skipping password reset for {phone}')
                
        print('\\n' + '-'*60)
    
    print(f'\\n✅ Password recovery process completed!')
    print(f'💡 Tip: Ask users what password they remember using during registration')
