#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from myproject.models import UserProfile, User, ReferralCommission
from decimal import Decimal

def test_referral_system():
    print("=" * 60)
    print("TESTING REFERRAL SYSTEM AFTER FIXES")
    print("=" * 60)
    
    # Test with existing referral codes
    test_codes = ['QI4TUJX9', 'A503D678', '04F0F718']
    
    for test_code in test_codes:
        print(f"\n🔍 Testing referral code: '{test_code}'")
        
        try:
            # Clean the referral code input (same as in views.py)
            cleaned_code = test_code.strip().upper()
            
            # Simple and efficient lookup with case-insensitive match
            referrer_profile = UserProfile.objects.filter(
                referral_code__iexact=cleaned_code
            ).select_related('user').first()
            
            if referrer_profile:
                referrer = referrer_profile.user
                print(f"   ✅ VALID - Found user: {referrer.username}")
                print(f"   📱 Phone: {referrer_profile.phone_number}")
                print(f"   💰 Balance: ₱{referrer_profile.balance}")
                
                # Check referral commissions
                commissions = ReferralCommission.objects.filter(referrer=referrer)
                print(f"   👥 Total referral commissions: {commissions.count()}")
                
                if commissions.exists():
                    for comm in commissions[:3]:  # Show first 3
                        print(f"      - Type: {comm.commission_type}, Amount: ₱{comm.commission_amount}, User: {comm.referred_user.username}")
                
            else:
                print(f"   ❌ INVALID - No user found")
                
        except Exception as e:
            print(f"   🔥 ERROR: {e}")
    
    print(f"\n" + "=" * 60)
    print("TESTING REFERRAL COMMISSION CREATION")
    print("=" * 60)
    
    # Test creating a referral commission without investment (registration type)
    try:
        first_user = User.objects.first()
        second_user = User.objects.all()[1] if User.objects.count() > 1 else None
        
        if first_user and second_user:
            print(f"Testing commission creation:")
            print(f"  Referrer: {first_user.username}")
            print(f"  Referred: {second_user.username}")
            
            # Try to create a registration commission
            test_commission = ReferralCommission(
                referrer=first_user,
                referred_user=second_user,
                investment=None,  # No investment for registration bonus
                commission_rate=Decimal('5.00'),
                commission_amount=Decimal('15.00'),
                level=1,
                commission_type='registration'
            )
            
            # Test validation without saving
            test_commission.full_clean()
            print("   ✅ Commission validation passed!")
            
            # Don't actually save to avoid duplicates
            # test_commission.save()
            # print("   ✅ Commission created successfully!")
            
        else:
            print("   ⚠️  Not enough users to test commission creation")
            
    except Exception as e:
        print(f"   ❌ Commission creation error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_referral_system()
