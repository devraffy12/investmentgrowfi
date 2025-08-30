#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from myproject.models import UserProfile, User, ReferralCommission, Transaction
from django.db.models import Sum, Count

def debug_referral_system():
    print("=" * 80)
    print("🔍 COMPREHENSIVE REFERRAL SYSTEM DEBUG")
    print("=" * 80)
    
    # 1. Check total users and profiles
    total_users = User.objects.count()
    total_profiles = UserProfile.objects.count()
    users_with_referrals = UserProfile.objects.filter(referred_by__isnull=False).count()
    
    print(f"📊 DATABASE OVERVIEW:")
    print(f"   Total Users: {total_users}")
    print(f"   Total UserProfiles: {total_profiles}")
    print(f"   Users with referrals: {users_with_referrals}")
    
    # 2. Check referral codes
    users_with_codes = UserProfile.objects.exclude(referral_code__isnull=True).exclude(referral_code__exact='').count()
    print(f"   Users with referral codes: {users_with_codes}")
    
    # 3. Check referral commissions
    total_commissions = ReferralCommission.objects.count()
    registration_commissions = ReferralCommission.objects.filter(commission_type='registration').count()
    investment_commissions = ReferralCommission.objects.filter(commission_type='investment').count()
    
    print(f"\n💰 REFERRAL COMMISSIONS:")
    print(f"   Total commissions: {total_commissions}")
    print(f"   Registration bonuses: {registration_commissions}")
    print(f"   Investment commissions: {investment_commissions}")
    
    # 4. Check referral bonus transactions
    referral_transactions = Transaction.objects.filter(transaction_type='referral_bonus').count()
    referral_amount = Transaction.objects.filter(transaction_type='referral_bonus', status='completed').aggregate(total=Sum('amount'))['total'] or 0
    
    print(f"\n📝 REFERRAL TRANSACTIONS:")
    print(f"   Referral bonus transactions: {referral_transactions}")
    print(f"   Total referral bonus amount: ₱{referral_amount}")
    
    # 5. Detailed referral chain analysis
    print(f"\n🔗 DETAILED REFERRAL ANALYSIS:")
    
    # Get users who have referred others
    referrers = UserProfile.objects.filter(
        user__in=User.objects.filter(referrals__isnull=False)
    ).distinct()
    
    print(f"   Users who are referrers: {referrers.count()}")
    
    for referrer_profile in referrers[:5]:  # Show top 5 referrers
        referrer = referrer_profile.user
        referred_users = User.objects.filter(userprofile__referred_by=referrer)
        
        # Count different metrics for this referrer
        total_referred = referred_users.count()
        active_referred = referred_users.filter(is_active=True).count()
        
        # Calculate team investment volume
        team_investments = 0
        for referred_user in referred_users:
            user_investments = Transaction.objects.filter(
                user=referred_user,
                transaction_type='investment',
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0
            team_investments += user_investments
        
        # Calculate referral earnings
        referral_earnings = Transaction.objects.filter(
            user=referrer,
            transaction_type='referral_bonus',
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        print(f"\n   👤 {referrer.username} (Code: {referrer_profile.referral_code}):")
        print(f"      Total referrals: {total_referred}")
        print(f"      Active referrals: {active_referred}")
        print(f"      Team volume: ₱{team_investments}")
        print(f"      Referral earnings: ₱{referral_earnings}")
        
        # Show individual referrals
        for referred_user in referred_users[:3]:  # Show first 3 referrals
            referred_profile = UserProfile.objects.get(user=referred_user)
            user_balance = referred_profile.balance
            user_invested = Transaction.objects.filter(
                user=referred_user,
                transaction_type='investment',
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            print(f"         -> {referred_user.username}: Balance=₱{user_balance}, Invested=₱{user_invested}")
    
    # 6. Check for potential issues
    print(f"\n⚠️  POTENTIAL ISSUES:")
    
    # Users without referral codes
    users_without_codes = UserProfile.objects.filter(
        referral_code__isnull=True
    ) | UserProfile.objects.filter(referral_code__exact='')
    print(f"   Users without referral codes: {users_without_codes.count()}")
    
    # Users with referrals but no commissions
    referred_users_all = User.objects.filter(userprofile__referred_by__isnull=False)
    users_with_commissions = ReferralCommission.objects.values_list('referred_user', flat=True).distinct()
    
    missing_commissions = referred_users_all.exclude(id__in=users_with_commissions).count()
    print(f"   Referred users missing commissions: {missing_commissions}")
    
    # Referral bonus transactions without commissions
    referral_txns = Transaction.objects.filter(transaction_type='referral_bonus')
    commission_user_ids = ReferralCommission.objects.values_list('referrer', flat=True)
    
    txns_without_commissions = referral_txns.exclude(user__in=commission_user_ids).count()
    print(f"   Referral transactions without commission records: {txns_without_commissions}")
    
    # 7. Sample registration flow test
    print(f"\n🧪 TESTING REGISTRATION FLOW:")
    
    # Find a user with a referral code to test
    test_referrer = UserProfile.objects.exclude(referral_code__isnull=True).exclude(referral_code__exact='').first()
    
    if test_referrer:
        test_code = test_referrer.referral_code
        print(f"   Test referral code: {test_code}")
        print(f"   Test referrer: {test_referrer.user.username}")
        
        # Simulate the lookup that happens during registration
        referrer_profile = UserProfile.objects.filter(
            referral_code__iexact=test_code
        ).select_related('user').first()
        
        if referrer_profile:
            print(f"   ✅ Referral code lookup works!")
            print(f"   Found referrer: {referrer_profile.user.username}")
            
            # Check if this referrer has received any bonuses
            referrer_bonuses = Transaction.objects.filter(
                user=referrer_profile.user,
                transaction_type='referral_bonus',
                status='completed'
            ).count()
            
            print(f"   Referrer's bonus count: {referrer_bonuses}")
            
        else:
            print(f"   ❌ Referral code lookup failed!")
    
    print(f"\n" + "=" * 80)
    print("🎯 RECOMMENDATIONS:")
    print("=" * 80)
    
    if missing_commissions > 0:
        print("1. 🔧 Need to fix missing referral commissions")
    
    if users_without_codes.count() > 0:
        print("2. 🔧 Need to generate referral codes for users without them")
    
    if txns_without_commissions > 0:
        print("3. 🔧 Need to create commission records for existing transactions")
    
    print("4. 🔧 Need to ensure proper tracking in Firebase for pure Firebase users")
    print("5. 🔧 Need to sync data between Django and Firebase systems")

if __name__ == "__main__":
    debug_referral_system()
