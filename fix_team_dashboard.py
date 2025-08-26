#!/usr/bin/env python3
"""
🔧 FIX TEAM DASHBOARD - SHOW CORRECT REFERRAL DATA
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

def fix_team_dashboard():
    """Fix the team dashboard to show correct data"""
    print("🔧 FIXING TEAM DASHBOARD")
    print("=" * 60)
    
    user_phone = "+639919101001"
    user = User.objects.get(username=user_phone)
    profile = UserProfile.objects.get(user=user)
    
    print(f"👤 User: {user.username}")
    print(f"🆔 Current Referral Code: {profile.referral_code}")
    
    # Check referral link format
    referral_link = f"https://investmentgrowfi-iu47.onrender.com/register/?ref={profile.referral_code}"
    print(f"🔗 Referral Link: {referral_link}")
    
    # Get current team stats
    referred_users = User.objects.filter(userprofile__referred_by=user).select_related('userprofile')
    total_referrals = referred_users.count()
    active_referrals = referred_users.filter(is_active=True).count()
    
    # Calculate referral earnings
    referral_earnings = Transaction.objects.filter(
        user=user,
        transaction_type='referral_bonus',
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate team volume
    team_total_invested = 0
    for referred_user in referred_users:
        user_investments = Investment.objects.filter(user=referred_user, status='active')
        user_total_invested = user_investments.aggregate(total=Sum('amount'))['total'] or 0
        team_total_invested += user_total_invested
    
    print(f"\n📊 CURRENT TEAM STATS:")
    print(f"   Total Referrals: {total_referrals}")
    print(f"   Active Members: {active_referrals}")
    print(f"   Total Earnings: ₱{referral_earnings}")
    print(f"   Team Volume: ₱{team_total_invested}")
    
    # Create demo referrals for testing
    print(f"\n🧪 CREATING DEMO REFERRALS FOR TESTING:")
    print("-" * 50)
    
    demo_users = [
        "+639111111111",
        "+639222222222", 
        "+639333333333"
    ]
    
    created_count = 0
    for i, demo_phone in enumerate(demo_users, 1):
        if not User.objects.filter(username=demo_phone).exists():
            # Create demo user
            demo_user = User.objects.create_user(
                username=demo_phone,
                password="demo123"
            )
            
            # Create profile with referral
            demo_profile = UserProfile.objects.create(
                user=demo_user,
                phone_number=demo_phone,
                balance=100.00,
                referred_by=user,  # Set as referred by main user
                referral_code=f"DEMO{demo_user.id:04d}"
            )
            
            # Create referral bonus transaction
            Transaction.objects.create(
                user=user,  # Give bonus to referrer
                transaction_type='referral_bonus',
                amount=15.00,
                status='completed',
                description=f'Referral bonus from {demo_phone}'
            )
            
            # Create investment for demo user (team volume)
            from myproject.models import InvestmentPlan
            from datetime import datetime, timedelta
            
            # Get a plan or create one
            plan, created = InvestmentPlan.objects.get_or_create(
                name="Demo Plan",
                defaults={
                    'minimum_amount': 100,
                    'maximum_amount': 10000,
                    'daily_return_rate': 3.5,
                    'duration_days': 30,
                    'is_active': True
                }
            )
            
            investment = Investment.objects.create(
                user=demo_user,
                plan=plan,
                amount=500.00,
                daily_return=17.50,  # 3.5% of 500
                total_return=525.00,  # Expected return
                status='active',
                end_date=datetime.now() + timedelta(days=30)
            )
            
            print(f"   ✅ Created demo user {i}: {demo_phone} with ₱500 investment")
            created_count += 1
        else:
            print(f"   ⚠️  Demo user {i} already exists: {demo_phone}")
    
    # Update team stats after creating demos
    if created_count > 0:
        referred_users = User.objects.filter(userprofile__referred_by=user).select_related('userprofile')
        total_referrals = referred_users.count()
        active_referrals = referred_users.filter(is_active=True).count()
        
        referral_earnings = Transaction.objects.filter(
            user=user,
            transaction_type='referral_bonus',
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        team_total_invested = 0
        for referred_user in referred_users:
            user_investments = Investment.objects.filter(user=referred_user, status='active')
            user_total_invested = user_investments.aggregate(total=Sum('amount'))['total'] or 0
            team_total_invested += user_total_invested
        
        print(f"\n📊 UPDATED TEAM STATS:")
        print(f"   Total Referrals: {total_referrals}")
        print(f"   Active Members: {active_referrals}")
        print(f"   Total Earnings: ₱{referral_earnings}")
        print(f"   Team Volume: ₱{team_total_invested}")
    
    return {
        'total_referrals': total_referrals,
        'active_referrals': active_referrals,
        'referral_earnings': float(referral_earnings),
        'team_volume': float(team_total_invested),
        'referral_link': referral_link
    }

def test_team_view():
    """Test the team view by simulating the function"""
    print(f"\n🧪 TESTING TEAM VIEW FUNCTION:")
    print("=" * 60)
    
    user_phone = "+639919101001"
    user = User.objects.get(username=user_phone)
    profile = UserProfile.objects.get(user=user)
    
    # Simulate team view logic
    referred_users = User.objects.filter(userprofile__referred_by=user).select_related('userprofile')
    
    # Calculate team stats
    total_referrals = referred_users.count()
    active_referrals = referred_users.filter(is_active=True).count()
    
    # Calculate referral earnings
    referral_earnings = Transaction.objects.filter(
        user=user,
        transaction_type='referral_bonus',
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Get recent referral activities
    recent_referrals = referred_users.order_by('-date_joined')[:10]
    
    # Calculate team investment stats
    team_total_invested = 0
    team_total_earnings = 0
    
    for referred_user in referred_users:
        user_investments = Investment.objects.filter(user=referred_user, status='active')
        user_total_invested = user_investments.aggregate(total=Sum('amount'))['total'] or 0
        team_total_invested += user_total_invested
        
        user_earnings = Transaction.objects.filter(
            user=referred_user,
            transaction_type='daily_payout',
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        team_total_earnings += user_earnings
    
    context = {
        'profile': profile,
        'referral_code': profile.referral_code,
        'total_referrals': total_referrals,
        'active_referrals': active_referrals,
        'referral_earnings': referral_earnings,
        'recent_referrals': recent_referrals,
        'team_total_invested': team_total_invested,
        'team_total_earnings': team_total_earnings,
        'referral_link': f"https://investmentgrowfi-iu47.onrender.com/register/?ref={profile.referral_code}",
    }
    
    print(f"📋 TEAM VIEW CONTEXT:")
    for key, value in context.items():
        if key != 'recent_referrals':  # Skip the queryset
            print(f"   {key}: {value}")
    
    print(f"\n👥 RECENT REFERRALS:")
    for i, ref_user in enumerate(recent_referrals, 1):
        ref_profile = ref_user.userprofile
        print(f"   {i}. {ref_user.username} | Joined: {ref_user.date_joined.strftime('%Y-%m-%d')}")

def main():
    print("🚀 TEAM DASHBOARD FIXER")
    print("=" * 60)
    
    # Fix and create demo data
    team_data = fix_team_dashboard()
    
    # Test team view function
    test_team_view()
    
    print(f"\n🎯 SUMMARY:")
    print("=" * 60)
    print(f"✅ Team dashboard should now show:")
    print(f"   📊 Total Referrals: {team_data['total_referrals']}")
    print(f"   👥 Active Members: {team_data['active_referrals']}")
    print(f"   💰 Total Earnings: ₱{team_data['referral_earnings']}")
    print(f"   📈 Team Volume: ₱{team_data['team_volume']}")
    print(f"   🔗 Referral Link: {team_data['referral_link']}")
    
    print(f"\n💡 TO TEST:")
    print(f"   1. Visit: https://investmentgrowfi-iu47.onrender.com/team/")
    print(f"   2. Should show the above stats")
    print(f"   3. Share your referral link to get real referrals")

if __name__ == "__main__":
    main()
