#!/usr/bin/env python3
"""
User Login Fix Tool - Para sa mga nawwalang users
"""
import os
import sys
import django
import getpass

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

def reset_user_password(phone_number, new_password="12345"):
    """Reset a user's password to a known value"""
    try:
        # Remove country code variations
        clean_phone = phone_number.replace('+63', '').replace('63', '')
        if not clean_phone.startswith('9'):
            clean_phone = '9' + clean_phone
        full_phone = '+63' + clean_phone
        
        user = User.objects.get(username=full_phone)
        user.set_password(new_password)
        user.save()
        
        print(f'✅ Password reset successful for {full_phone}')
        print(f'   New password: {new_password}')
        
        # Test the new password
        test_user = authenticate(username=full_phone, password=new_password)
        if test_user:
            print(f'✅ Login test successful!')
        else:
            print(f'❌ Login test failed')
            
        return True
        
    except User.DoesNotExist:
        print(f'❌ User {phone_number} not found')
        return False
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

def list_recent_users():
    """List recent users who might need password reset"""
    users = User.objects.all().order_by('-date_joined')[:10]
    
    print('📋 Recent Users (candidates for password reset):')
    print('=' * 60)
    
    for i, user in enumerate(users, 1):
        profile = getattr(user, 'userprofile', None)
        referral_code = profile.referral_code if profile else 'No code'
        
        print(f'{i:2d}. 📱 {user.username}')
        print(f'    🆔 ID: {user.id} | 🔑 Code: {referral_code}')
        print(f'    ⏰ Joined: {user.date_joined.strftime("%Y-%m-%d %H:%M")}')
        print()

if __name__ == '__main__':
    print('🔧 GrowFi User Login Fix Tool')
    print('=' * 50)
    
    # List recent users
    list_recent_users()
    
    print('🔑 Password Reset Options:')
    print('1. Reset specific user password')
    print('2. Reset ALL recent users to default password (12345)')
    print('3. Exit')
    
    choice = input('\\nEnter choice (1-3): ').strip()
    
    if choice == '1':
        phone = input('Enter phone number (e.g., 9214392306 or +639214392306): ').strip()
        new_password = input('Enter new password (default: 12345): ').strip() or '12345'
        reset_user_password(phone, new_password)
        
    elif choice == '2':
        confirm = input('Reset ALL recent users to password "12345"? (yes/no): ').strip().lower()
        if confirm == 'yes':
            users = User.objects.all().order_by('-date_joined')[:5]
            for user in users:
                reset_user_password(user.username, '12345')
                
    print('\\n✅ Password reset tool completed!')
    print('💡 Users can now login with their phone number and the new password.')
