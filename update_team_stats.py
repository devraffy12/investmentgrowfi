#!/usr/bin/env python3
"""
🔄 UPDATE TEAM STATS - Recalculate after removing demo plan
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
from django.db.models import Sum

def recalculate_team_stats():
    """Recalculate team stats after removing demo plan"""
    print("🔄 RECALCULATING TEAM STATS")
    print("=" * 60)
    
    user_phone = "+639919101001"
    user = User.objects.get(username=user_phone)
    
    # Get team members
    referred_users = User.objects.filter(userprofile__referred_by=user).select_related('userprofile')
    
    total_referrals = referred_users.count()
    active_referrals = referred_users.filter(is_active=True).count()
    
    # Calculate referral earnings
    referral_earnings = Transaction.objects.filter(
        user=user,
        transaction_type='referral_bonus',
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate team volume (investments of referred users)
    team_total_invested = 0
    for referred_user in referred_users:
        user_investments = Investment.objects.filter(user=referred_user, status='active')
        user_total_invested = user_investments.aggregate(total=Sum('amount'))['total'] or 0
        team_total_invested += user_total_invested
        
        if user_total_invested > 0:
            print(f"   {referred_user.username}: ₱{user_total_invested}")
    
    print(f"\n📊 UPDATED TEAM STATS:")
    print(f"   Total Referrals: {total_referrals}")
    print(f"   Active Members: {active_referrals}")
    print(f"   Total Earnings: ₱{referral_earnings}")
    print(f"   Team Volume: ₱{team_total_invested}")
    
    return {
        'total_referrals': total_referrals,
        'active_referrals': active_referrals,
        'referral_earnings': float(referral_earnings),
        'team_volume': float(team_total_invested)
    }

def main():
    print("🔄 TEAM STATS UPDATER")
    print("=" * 60)
    
    stats = recalculate_team_stats()
    
    print(f"\n🎯 FINAL TEAM STATS:")
    print("=" * 60)
    print(f"✅ Total Referrals: {stats['total_referrals']}")
    print(f"✅ Active Members: {stats['active_referrals']}")
    print(f"✅ Total Earnings: ₱{stats['referral_earnings']}")
    print(f"✅ Team Volume: ₱{stats['team_volume']}")
    
    if stats['team_volume'] == 0:
        print(f"\n💡 Team Volume is ₱0 because demo investment was removed")
        print(f"✅ This is correct - no real investments from team members yet")

if __name__ == "__main__":
    main()
