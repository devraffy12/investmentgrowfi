#!/usr/bin/env python3
"""
🔧 DEBUG TEAM/REFERRAL SYSTEM
============================

Test yung team view at referral system
"""

import os
import sys
import django

# Add project to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from myproject.models import UserProfile, Transaction, Investment
from django.db.models import Sum, Count

def debug_team_data():
    """Debug yung team data ng user 9919101001"""
    print("🔍 DEBUGGING TEAM/REFERRAL DATA")
    print("=" * 60)
    
    # Get your user
    user_phone = "+639919101001"
    try:
        user = User.objects.get(username=user_phone)
        profile = UserProfile.objects.get(user=user)
        
        print(f"👤 User: {user.username}")
        print(f"📞 Phone: {profile.phone_number}")
        print(f"🆔 Referral Code: {profile.referral_code}")
        print()
        
        # Check referred users
        print("👥 CHECKING REFERRED USERS:")
        print("-" * 40)
        
        referred_users = User.objects.filter(userprofile__referred_by=user).select_related('userprofile')
        total_referrals = referred_users.count()
        
        print(f"Total Referrals: {total_referrals}")
        
        if total_referrals > 0:
            print("List of referred users:")
            for i, ref_user in enumerate(referred_users, 1):
                ref_profile = ref_user.userprofile
                print(f"  {i}. {ref_user.username} | Phone: {ref_profile.phone_number} | Active: {ref_user.is_active}")
        else:
            print("❌ No referred users found")
        
        # Check if user was referred by someone
        print(f"\n🔗 WHO REFERRED THIS USER:")
        print("-" * 40)
        
        if profile.referred_by:
            print(f"Referred by: {profile.referred_by.username}")
        else:
            print("❌ Not referred by anyone")
        
        # Check referral earnings
        print(f"\n💰 REFERRAL EARNINGS:")
        print("-" * 40)
        
        referral_transactions = Transaction.objects.filter(
            user=user,
            transaction_type='referral_bonus',
            status='completed'
        )
        
        total_referral_earnings = referral_transactions.aggregate(total=Sum('amount'))['total'] or 0
        print(f"Total Referral Earnings: ₱{total_referral_earnings}")
        print(f"Number of referral transactions: {referral_transactions.count()}")
        
        if referral_transactions.count() > 0:
            print("Recent referral transactions:")
            for trans in referral_transactions.order_by('-created_at')[:5]:
                print(f"  ₱{trans.amount} - {trans.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        # Check team volume (investments of referred users)
        print(f"\n📊 TEAM VOLUME:")
        print("-" * 40)
        
        team_total_invested = 0
        team_active_investments = 0
        
        for ref_user in referred_users:
            investments = Investment.objects.filter(user=ref_user, status='active')
            user_invested = investments.aggregate(total=Sum('amount'))['total'] or 0
            team_total_invested += user_invested
            team_active_investments += investments.count()
            
            if user_invested > 0:
                print(f"  {ref_user.username}: ₱{user_invested} ({investments.count()} investments)")
        
        print(f"Team Total Invested: ₱{team_total_invested}")
        print(f"Team Active Investments: {team_active_investments}")
        
        return {
            'total_referrals': total_referrals,
            'active_referrals': referred_users.filter(is_active=True).count(),
            'referral_earnings': float(total_referral_earnings),
            'team_volume': float(team_total_invested)
        }
        
    except User.DoesNotExist:
        print(f"❌ User {user_phone} not found")
        return None
    except UserProfile.DoesNotExist:
        print(f"❌ Profile for {user_phone} not found")
        return None

def check_all_referral_relationships():
    """Check all referral relationships in the system"""
    print(f"\n🌐 SYSTEM-WIDE REFERRAL ANALYSIS:")
    print("=" * 60)
    
    # Count total referral relationships
    profiles_with_referrer = UserProfile.objects.filter(referred_by__isnull=False).count()
    profiles_without_referrer = UserProfile.objects.filter(referred_by__isnull=True).count()
    
    print(f"👥 Users with referrer: {profiles_with_referrer}")
    print(f"🚫 Users without referrer: {profiles_without_referrer}")
    
    # Top referrers
    top_referrers = User.objects.annotate(
        referral_count=Count('referrals')
    ).filter(referral_count__gt=0).order_by('-referral_count')[:10]
    
    print(f"\n🏆 TOP 10 REFERRERS:")
    print("-" * 40)
    
    if top_referrers.exists():
        for i, referrer in enumerate(top_referrers, 1):
            print(f"  {i}. {referrer.username}: {referrer.referral_count} referrals")
    else:
        print("❌ No referrers found")
    
    # Check for broken referral links
    print(f"\n🔍 CHECKING FOR ISSUES:")
    print("-" * 40)
    
    # Check for users with referral_code but no referrals
    users_no_referrals = UserProfile.objects.filter(
        referral_code__isnull=False
    ).annotate(
        referral_count=Count('user__referrals')
    ).filter(referral_count=0)
    
    print(f"Users with referral codes but 0 referrals: {users_no_referrals.count()}")

def create_test_referral():
    """Create a test referral for debugging"""
    print(f"\n🧪 CREATING TEST REFERRAL:")
    print("=" * 60)
    
    # Get your user
    user_phone = "+639919101001"
    
    try:
        referrer = User.objects.get(username=user_phone)
        referrer_profile = UserProfile.objects.get(user=referrer)
        
        # Create a test user as referral
        test_phone = "+639999999999"
        
        # Check if test user already exists
        if User.objects.filter(username=test_phone).exists():
            print(f"Test user {test_phone} already exists")
            test_user = User.objects.get(username=test_phone)
        else:
            test_user = User.objects.create_user(
                username=test_phone,
                password="testpass123"
            )
            print(f"✅ Created test user: {test_phone}")
        
        # Create/update profile with referral
        test_profile, created = UserProfile.objects.get_or_create(
            user=test_user,
            defaults={
                'phone_number': test_phone,
                'balance': 50.00,
                'referred_by': referrer,
                'referral_code': f"GROW{test_user.id:04d}"
            }
        )
        
        if not created and not test_profile.referred_by:
            test_profile.referred_by = referrer
            test_profile.save()
            print(f"✅ Updated test user referral link")
        elif created:
            print(f"✅ Created test profile with referral")
        else:
            print(f"✅ Test user already has referral link")
        
        # Create a test referral bonus transaction
        referral_bonus, created = Transaction.objects.get_or_create(
            user=referrer,
            transaction_type='referral_bonus',
            amount=10.00,
            defaults={
                'status': 'completed',
                'description': f'Referral bonus from {test_phone}'
            }
        )
        
        if created:
            print(f"✅ Created test referral bonus: ₱10.00")
        else:
            print(f"✅ Test referral bonus already exists")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test referral: {e}")
        return False

def main():
    print("🔧 TEAM/REFERRAL SYSTEM DEBUGGER")
    print("=" * 60)
    
    # Debug user's team data
    team_data = debug_team_data()
    
    # Check system-wide referrals
    check_all_referral_relationships()
    
    # Create test referral if needed
    if team_data and team_data['total_referrals'] == 0:
        print(f"\n⚠️  User has 0 referrals. Creating test referral...")
        create_test_referral()
        
        # Re-check after creating test
        print(f"\n🔄 RE-CHECKING AFTER TEST CREATION:")
        debug_team_data()
    
    print(f"\n🎯 SUMMARY:")
    print("=" * 60)
    if team_data:
        print(f"✅ Total Referrals: {team_data['total_referrals']}")
        print(f"✅ Active Members: {team_data['active_referrals']}")
        print(f"✅ Total Earnings: ₱{team_data['referral_earnings']}")
        print(f"✅ Team Volume: ₱{team_data['team_volume']}")
        
        if team_data['total_referrals'] == 0:
            print(f"\n💡 SOLUTION: User needs to share referral link to get referrals")
            print(f"Referral Link: https://investmentgrowfi-iu47.onrender.com/register/?ref=GROW0080")
    else:
        print(f"❌ Could not get team data")

if __name__ == "__main__":
    main()
