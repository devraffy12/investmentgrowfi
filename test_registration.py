#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from myproject.models import UserProfile, User
from django.contrib.auth import authenticate

def test_registration_flow():
    print("=" * 60)
    print("🧪 TESTING REGISTRATION FLOW WITH REFERRAL CODE")
    print("=" * 60)
    
    # Get a valid referral code
    referrer_profile = UserProfile.objects.exclude(
        referral_code__isnull=True
    ).exclude(
        referral_code__exact=''
    ).first()
    
    if not referrer_profile:
        print("❌ No referrer profiles found")
        return
    
    test_referral_code = referrer_profile.referral_code
    print(f"🎯 Using referral code: '{test_referral_code}' from user: {referrer_profile.user.username}")
    
    # Simulate the form input
    form_data = {
        'phone': '09123456789',  # This will be cleaned to +639123456789
        'password': 'testpass123',
        'confirm_password': 'testpass123',
        'referral_code': test_referral_code,  # Use the actual code
    }
    
    print(f"\n📝 Form data:")
    for key, value in form_data.items():
        if key == 'password' or key == 'confirm_password':
            print(f"   {key}: {'*' * len(value)}")
        else:
            print(f"   {key}: '{value}'")
    
    # Clean phone number (same logic as in views.py)
    phone = form_data['phone']
    clean_phone = phone.replace(' ', '').replace('-', '')
    if not clean_phone.startswith('+63'):
        if clean_phone.startswith('63'):
            clean_phone = '+' + clean_phone
        elif clean_phone.startswith('09'):
            clean_phone = '+63' + clean_phone[1:]
        elif clean_phone.startswith('9'):
            clean_phone = '+63' + clean_phone
    
    print(f"\n📱 Phone processing:")
    print(f"   Original: '{phone}'")
    print(f"   Cleaned: '{clean_phone}'")
    
    # Test if phone already exists
    existing_profile = UserProfile.objects.filter(phone_number=clean_phone).first()
    if existing_profile:
        print(f"⚠️  Phone number already exists: {existing_profile.user.username}")
        return
    
    # Validate referral code (exact logic from views.py)
    referral_code = form_data['referral_code'].strip().upper()
    print(f"\n🔍 Referral code validation:")
    print(f"   Input: '{form_data['referral_code']}'")
    print(f"   Cleaned: '{referral_code}'")
    
    # Simple and efficient lookup with case-insensitive match
    referrer_profile_found = UserProfile.objects.filter(
        referral_code__iexact=referral_code
    ).select_related('user').first()
    
    if referrer_profile_found:
        referrer = referrer_profile_found.user
        print(f"   ✅ Valid referral code found: {referral_code} from user {referrer.username}")
        print(f"   Referrer ID: {referrer.id}")
        print(f"   Referrer active: {referrer.is_active}")
    else:
        print(f"   ❌ No matching referral code found")
        # Show available codes for debugging
        all_profiles = UserProfile.objects.exclude(
            referral_code__isnull=True
        ).exclude(
            referral_code__exact=''
        ).values_list('referral_code', flat=True)[:5]
        
        print(f"   Available codes in DB: {list(all_profiles)}")
        return
    
    print(f"\n✅ All validations passed! Registration would succeed.")
    print(f"   New user phone: {clean_phone}")
    print(f"   Referrer: {referrer.username} (Code: {referral_code})")

if __name__ == "__main__":
    test_registration_flow()
