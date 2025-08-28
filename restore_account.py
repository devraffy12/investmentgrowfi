#!/usr/bin/env python3
"""
Account Recovery Script - Restore +639518383748
"""
import os
import sys
import django
from datetime import datetime

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from myproject.models import UserProfile
from django.contrib.auth import authenticate
from django.utils import timezone

def restore_account():
    print('🔧 ACCOUNT RECOVERY: +639518383748')
    print('=' * 50)
    
    target_phone = '+639518383748'
    new_password = 'recover123'  # Simple recovery password
    
    # First, check if user exists
    user = None
    found_format = None
    
    # Check different formats
    check_formats = [
        '+639518383748',
        '639518383748', 
        '09518383748',
        '9518383748'
    ]
    
    print('🔍 Searching for user in different formats...')
    for format_phone in check_formats:
        try:
            user = User.objects.get(username=format_phone)
            found_format = format_phone
            print(f'✅ User found with format: {format_phone}')
            break
        except User.DoesNotExist:
            print(f'   ❌ Not found: {format_phone}')
    
    if not user:
        # Create new user if not found
        print(f'\n🆕 Creating new user: {target_phone}')
        user = User.objects.create_user(
            username=target_phone,
            password=new_password
        )
        user.is_active = True
        user.save()
        print(f'✅ User created with ID: {user.id}')
        
        # Create profile
        profile = UserProfile.objects.create(
            user=user,
            phone_number=target_phone,
            balance=0,
            referral_code=f'REC{user.id:06d}'
        )
        print(f'✅ Profile created with referral code: {profile.referral_code}')
        
    else:
        # User exists, update password and reactivate
        print(f'\n🔧 Restoring existing user: {found_format} (ID: {user.id})')
        
        # Reset password
        user.set_password(new_password)
        user.is_active = True
        user.save()
        print(f'✅ Password reset to: {new_password}')
        
        # Check/create profile
        try:
            profile = UserProfile.objects.get(user=user)
            # Update phone to correct format if needed
            if profile.phone_number != target_phone:
                profile.phone_number = target_phone
                profile.save()
                print(f'✅ Profile phone updated to: {target_phone}')
            print(f'✅ Profile exists - Balance: ₱{profile.balance}')
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(
                user=user,
                phone_number=target_phone,
                balance=0,
                referral_code=f'REC{user.id:06d}'
            )
            print(f'✅ Profile created with referral code: {profile.referral_code}')
    
    # Test authentication
    print(f'\n🔐 Testing authentication...')
    auth_user = authenticate(username=target_phone, password=new_password)
    
    if auth_user:
        print(f'✅ Authentication test: SUCCESS')
        print(f'✅ User can login with: {target_phone}')
        print(f'✅ Password: {new_password}')
    else:
        print(f'❌ Authentication test: FAILED')
    
    # Update Firebase
    print(f'\n🔥 Updating Firebase...')
    try:
        from myproject.views import update_user_in_firebase_realtime_db
        firebase_data = {
            'phone_number': target_phone,
            'balance': float(profile.balance),
            'account_status': 'recovered',
            'last_recovery': timezone.now().isoformat(),
            'is_active': True,
            'recovery_password': new_password
        }
        
        update_user_in_firebase_realtime_db(user, target_phone, firebase_data)
        print(f'✅ Firebase updated successfully')
        
    except Exception as e:
        print(f'⚠️ Firebase update failed: {e}')
    
    # Final summary
    print(f'\n' + '=' * 50)
    print(f'🎉 ACCOUNT RECOVERY COMPLETE')
    print(f'=' * 50)
    print(f'📱 Phone: {target_phone}')
    print(f'🔐 Password: {new_password}')
    print(f'👤 User ID: {user.id}')
    print(f'💰 Balance: ₱{profile.balance}')
    print(f'🎯 Referral Code: {profile.referral_code}')
    print(f'✅ Status: ACTIVE - Ready to login!')
    
    return {
        'phone': target_phone,
        'password': new_password,
        'user_id': user.id,
        'balance': profile.balance,
        'referral_code': profile.referral_code
    }

if __name__ == '__main__':
    restore_account()
