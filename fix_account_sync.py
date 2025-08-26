#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from myproject.models import UserProfile
from decimal import Decimal
import pytz
from datetime import datetime

print("🔧 CREATING DJANGO ACCOUNT FROM FIREBASE DATA")
print("=" * 50)

# Your Firebase data
firebase_data = {
    'username': '+639919101001',
    'phone_number': '+639919101001', 
    'balance': 115.0,
    'user_id': 81,
    'referral_code': 'ME93OPRF',
    'date_joined': '2025-08-26T13:14:23.476619+00:00',
    'is_active': True,
    'first_name': '',
    'last_name': '',
    'email': ''
}

try:
    # Check if user already exists
    try:
        existing_user = User.objects.get(username=firebase_data['username'])
        print(f"✅ User already exists: {existing_user.username}")
        print(f"Account active: {existing_user.is_active}")
        
        # Check profile
        try:
            profile = UserProfile.objects.get(user=existing_user)
            print(f"✅ Profile exists: Balance ₱{profile.balance}")
        except UserProfile.DoesNotExist:
            print("❌ Profile missing - creating profile...")
            profile = UserProfile.objects.create(
                user=existing_user,
                phone_number=firebase_data['phone_number'],
                balance=Decimal(str(firebase_data['balance'])),
                referral_code=firebase_data['referral_code']
            )
            print(f"✅ Profile created with balance ₱{profile.balance}")
            
    except User.DoesNotExist:
        print("❌ User not found in Django - creating user...")
        
        # Create Django user
        user = User.objects.create_user(
            username=firebase_data['username'],
            password='temp123',  # Temporary password - you'll need to reset this
            email=firebase_data['email'],
            first_name=firebase_data['first_name'],
            last_name=firebase_data['last_name'],
            is_active=firebase_data['is_active']
        )
        
        # Set the date_joined from Firebase
        user.date_joined = datetime.fromisoformat(firebase_data['date_joined'].replace('Z', '+00:00'))
        user.save()
        
        print(f"✅ User created: {user.username} (ID: {user.id})")
        
        # Create UserProfile
        profile = UserProfile.objects.create(
            user=user,
            phone_number=firebase_data['phone_number'],
            balance=Decimal(str(firebase_data['balance'])),
            referral_code=firebase_data['referral_code']
        )
        
        print(f"✅ Profile created with balance ₱{profile.balance}")
        print(f"✅ Referral code: {profile.referral_code}")
        
        print(f"\n🔑 TEMPORARY PASSWORD SET:")
        print(f"Username: {firebase_data['username']}")
        print(f"Password: temp123")
        print(f"⚠️ IMPORTANT: Change your password after logging in!")
        
    print(f"\n✅ ACCOUNT SYNC COMPLETE!")
    print("=" * 50)
    print(f"You can now log in with:")
    print(f"Phone: {firebase_data['username']}")
    print(f"Or try these formats:")
    print(f"  - +639919101001")
    print(f"  - 639919101001")
    print(f"  - 9919101001")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
