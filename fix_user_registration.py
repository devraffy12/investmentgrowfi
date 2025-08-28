#!/usr/bin/env python
"""
Fix user registration issue - Add user to Django database
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from myproject.models import UserProfile, Transaction
from decimal import Decimal
import random
import string

def generate_referral_code():
    """Generate a unique referral code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not UserProfile.objects.filter(referral_code=code).exists():
            return code

def fix_user_registration():
    """Fix registration for phone number 9214392306"""
    phone_input = "9214392306"
    
    print("🔧 Fixing User Registration Issue")
    print("=" * 50)
    print(f"📱 Original Phone: {phone_input}")
    
    # Apply same normalization as registration
    clean_phone = phone_input.replace(' ', '').replace('-', '')
    
    # Smart phone normalization for Philippine numbers
    if not clean_phone.startswith('+63'):
        # Remove all non-digits first
        digits_only = ''.join(filter(str.isdigit, clean_phone))
        
        if digits_only.startswith('63') and len(digits_only) >= 12:
            # 639xxxxxxxxx format
            clean_phone = '+' + digits_only
        elif digits_only.startswith('09') and len(digits_only) == 11:
            # 09xxxxxxxxx format - convert to +639xxxxxxxxx
            clean_phone = '+63' + digits_only[1:]
        elif len(digits_only) >= 10:
            # Handle various formats by extracting the last 10 digits
            # This covers cases like 099xxxxxxxx, 99xxxxxxxx, etc.
            last_10_digits = digits_only[-10:]
            if last_10_digits.startswith('9'):
                clean_phone = '+63' + last_10_digits
            else:
                # If doesn't start with 9, might be invalid, but try anyway
                clean_phone = '+63' + digits_only
        else:
            # Fallback: just add +63 to whatever digits we have
            clean_phone = '+63' + digits_only if digits_only else clean_phone
    
    print(f"📱 Normalized Phone: {clean_phone}")
    
    # Check if user already exists
    if User.objects.filter(username=clean_phone).exists():
        print("❌ User already exists in Django database!")
        user = User.objects.get(username=clean_phone)
        print(f"   Username: {user.username}")
        print(f"   Active: {user.is_active}")
        print(f"   Has Password: {user.has_usable_password()}")
        return
    
    # Create the user manually
    try:
        print("🚀 Creating user in Django database...")
        
        # Create User account
        user = User.objects.create_user(
            username=clean_phone,
            password=phone_input  # Use original phone as default password
        )
        print(f"✅ User created: {user.username}")
        
        # Create UserProfile
        profile = UserProfile.objects.create(
            user=user,
            phone_number=clean_phone,
            referral_code=generate_referral_code(),
            balance=Decimal('100.00'),  # Registration bonus
            registration_bonus_claimed=True
        )
        print(f"✅ UserProfile created with referral code: {profile.referral_code}")
        
        # Create registration bonus transaction
        transaction = Transaction.objects.create(
            user=user,
            transaction_type='registration_bonus',
            amount=Decimal('100.00'),
            status='completed'
        )
        print(f"✅ Registration bonus transaction created: ₱{transaction.amount}")
        
        print()
        print("🎉 SUCCESS! User registration fixed!")
        print("-" * 40)
        print(f"Username: {user.username}")
        print(f"Password: {phone_input} (original phone number)")
        print(f"Balance: ₱{profile.balance}")
        print(f"Referral Code: {profile.referral_code}")
        print()
        print("💡 User can now login with:")
        print(f"   Phone: {phone_input} (original) or {clean_phone} (normalized)")
        print(f"   Password: {phone_input}")
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_user_registration()
