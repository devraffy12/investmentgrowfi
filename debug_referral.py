#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from myproject.models import UserProfile, User

def debug_referral_codes():
    print("=" * 60)
    print("🔍 DEBUGGING REFERRAL CODE VALIDATION")
    print("=" * 60)
    
    # Get all referral codes
    all_codes = UserProfile.objects.exclude(
        referral_code__isnull=True
    ).exclude(
        referral_code__exact=''
    ).values_list('referral_code', 'user__username')
    
    print(f"📊 Total users with referral codes: {len(all_codes)}")
    print("\n🔗 Available referral codes:")
    for code, username in all_codes[:10]:
        print(f"   Code: '{code}' -> User: {username}")
    
    # Test specific codes
    test_codes = ['A503D678', 'a503d678', '04F0F718', '822CDC49']
    
    print(f"\n🧪 Testing referral code validation:")
    for test_code in test_codes:
        print(f"\n   Testing: '{test_code}'")
        
        # Test exact match
        exact_match = UserProfile.objects.filter(referral_code=test_code).first()
        print(f"   Exact match: {exact_match}")
        
        # Test case insensitive
        iexact_match = UserProfile.objects.filter(referral_code__iexact=test_code).first()
        print(f"   Case-insensitive match: {iexact_match}")
        
        if iexact_match:
            print(f"   ✅ Found user: {iexact_match.user.username}")
        else:
            print(f"   ❌ No match found")
    
    # Test the validation logic from views.py
    print(f"\n🔧 Testing the exact logic from views.py:")
    test_input = "A503D678"  # Use one of the known codes
    
    # Clean the referral code input (same as in views.py)
    referral_code = test_input.strip().upper()
    print(f"   Input: '{test_input}' -> Cleaned: '{referral_code}'")
    
    # Simple lookup with case-insensitive match
    referrer_profile = UserProfile.objects.filter(
        referral_code__iexact=referral_code
    ).select_related('user').first()
    
    if referrer_profile:
        print(f"   ✅ SUCCESS: Found user {referrer_profile.user.username}")
        print(f"   User ID: {referrer_profile.user.id}")
        print(f"   User active: {referrer_profile.user.is_active}")
    else:
        print(f"   ❌ FAILED: No user found")
        
        # Debug: Show what we have in database
        print(f"   Available codes for comparison:")
        sample_codes = UserProfile.objects.exclude(
            referral_code__isnull=True
        ).exclude(
            referral_code__exact=''
        ).values_list('referral_code', flat=True)[:5]
        
        for code in sample_codes:
            print(f"      '{code}' (length: {len(code)})")

if __name__ == "__main__":
    debug_referral_codes()
