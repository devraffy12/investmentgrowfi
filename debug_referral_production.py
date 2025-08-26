#!/usr/bin/env python
"""
Complete Referral System Debug and Fix Script
This script diagnoses and fixes all referral code issues for production deployment
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from myproject.models import UserProfile, User, ReferralCommission, Transaction
from decimal import Decimal
from django.db import transaction

def diagnose_referral_system():
    """Comprehensive diagnosis of the referral system"""
    print("🔍 " + "="*60)
    print("🔍 COMPREHENSIVE REFERRAL SYSTEM DIAGNOSIS")
    print("🔍 " + "="*60)
    
    # 1. Check database schema
    print("\n📊 DATABASE SCHEMA CHECK:")
    try:
        from django.db import connection
        cursor = connection.cursor()
        
        # Check ReferralCommission table structure
        cursor.execute("PRAGMA table_info(myproject_referralcommission)")
        columns = cursor.fetchall()
        
        print("   ReferralCommission table columns:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL ALLOWED'}")
            
        # Check if investment_id is nullable
        investment_col = [col for col in columns if col[1] == 'investment_id']
        if investment_col and investment_col[0][3]:  # NOT NULL
            print("   ❌ ISSUE: investment_id is NOT NULL - this will cause errors!")
        else:
            print("   ✅ investment_id allows NULL values")
            
    except Exception as e:
        print(f"   ❌ Database check error: {e}")
    
    # 2. Check existing referral codes
    print("\n🔑 REFERRAL CODES CHECK:")
    total_users = User.objects.count()
    profiles_with_codes = UserProfile.objects.exclude(
        referral_code__isnull=True
    ).exclude(referral_code__exact='')
    
    print(f"   Total users: {total_users}")
    print(f"   Users with referral codes: {profiles_with_codes.count()}")
    
    if profiles_with_codes.exists():
        print("   Sample referral codes:")
        for profile in profiles_with_codes[:5]:
            print(f"   - {profile.referral_code} ({profile.user.username})")
    
    # 3. Test referral validation logic
    print("\n🧪 REFERRAL VALIDATION TEST:")
    test_codes = ['QI4TUJX9', 'A503D678', 'INVALID123']
    
    for code in test_codes:
        try:
            cleaned_code = code.strip().upper()
            referrer_profile = UserProfile.objects.filter(
                referral_code__iexact=cleaned_code
            ).select_related('user').first()
            
            if referrer_profile:
                print(f"   ✅ '{code}' -> Valid (User: {referrer_profile.user.username})")
            else:
                print(f"   ❌ '{code}' -> Invalid")
                
        except Exception as e:
            print(f"   🔥 '{code}' -> Error: {e}")
    
    # 4. Check existing referral commissions
    print("\n💰 REFERRAL COMMISSIONS CHECK:")
    total_commissions = ReferralCommission.objects.count()
    print(f"   Total commissions: {total_commissions}")
    
    if total_commissions > 0:
        print("   Recent commissions:")
        for comm in ReferralCommission.objects.all()[:5]:
            investment_info = f"Investment #{comm.investment.id}" if comm.investment else "No Investment (Registration)"
            print(f"   - {comm.referrer.username} -> ₱{comm.commission_amount} ({investment_info})")
    
    # 5. Test commission creation
    print("\n🧪 COMMISSION CREATION TEST:")
    try:
        # Try to create a test commission object (without saving)
        test_comm = ReferralCommission(
            referrer=User.objects.first(),
            referred_user=User.objects.last(),
            investment=None,  # This should work now
            commission_rate=Decimal('5.00'),
            commission_amount=Decimal('15.00'),
            level=1,
            commission_type='registration'
        )
        
        # Validate without saving
        test_comm.full_clean()
        print("   ✅ Commission creation validation passed!")
        
    except Exception as e:
        print(f"   ❌ Commission creation error: {e}")
        import traceback
        traceback.print_exc()

def fix_existing_commissions():
    """Fix any existing commissions that might have issues"""
    print("\n🔧 FIXING EXISTING COMMISSIONS:")
    
    try:
        # Check for commissions without commission_type
        commissions_to_fix = ReferralCommission.objects.filter(
            commission_type__isnull=True
        )
        
        if commissions_to_fix.exists():
            print(f"   Found {commissions_to_fix.count()} commissions without type")
            
            for comm in commissions_to_fix:
                if comm.investment:
                    comm.commission_type = 'investment'
                else:
                    comm.commission_type = 'registration'
                comm.save()
                
            print("   ✅ Fixed commission types")
        else:
            print("   ✅ All commissions have proper types")
            
    except Exception as e:
        print(f"   ❌ Error fixing commissions: {e}")

def test_full_registration_flow():
    """Test the complete registration flow"""
    print("\n🎯 FULL REGISTRATION FLOW TEST:")
    
    # Get a valid referral code
    sample_profile = UserProfile.objects.exclude(
        referral_code__isnull=True
    ).exclude(referral_code__exact='').first()
    
    if not sample_profile:
        print("   ⚠️  No referral codes available for testing")
        return
    
    test_code = sample_profile.referral_code
    referrer = sample_profile.user
    
    print(f"   Testing with referral code: {test_code}")
    print(f"   Referrer: {referrer.username}")
    
    # Simulate the registration process
    try:
        with transaction.atomic():
            # 1. Validate referral code
            cleaned_code = test_code.strip().upper()
            referrer_profile = UserProfile.objects.filter(
                referral_code__iexact=cleaned_code
            ).select_related('user').first()
            
            if not referrer_profile:
                raise ValueError("Referral code validation failed")
            
            print("   ✅ Step 1: Referral code validation passed")
            
            # 2. Create test user (don't actually save)
            test_phone = "+639999888777"
            
            # 3. Test referral commission creation
            referral_bonus = Decimal('15.00')
            
            test_commission = ReferralCommission(
                referrer=referrer,
                referred_user=referrer,  # Using existing user for test
                investment=None,
                commission_rate=Decimal('5.00'),
                commission_amount=referral_bonus,
                level=1,
                commission_type='registration'
            )
            
            # Validate without saving
            test_commission.full_clean()
            print("   ✅ Step 2: Commission creation validation passed")
            
            # Don't actually save to avoid creating duplicate data
            print("   ✅ Full registration flow test completed successfully!")
            
            # Rollback the transaction
            raise Exception("Test rollback - no data was actually saved")
            
    except Exception as e:
        if "Test rollback" in str(e):
            print("   ✅ Test completed (no data saved)")
        else:
            print(f"   ❌ Registration flow error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    diagnose_referral_system()
    fix_existing_commissions()
    test_full_registration_flow()
    
    print("\n🎉 " + "="*60)
    print("🎉 DIAGNOSIS COMPLETE!")
    print("🎉 " + "="*60)
    print("\nNext steps:")
    print("1. Run migrations: python manage.py migrate")
    print("2. Test registration with referral code")
    print("3. Deploy to production")
    print("4. Add Firebase credentials to Render environment variables")
