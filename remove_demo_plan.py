#!/usr/bin/env python3
"""
🗑️ REMOVE DEMO PLAN - Clean up unnecessary demo data
"""

import os
import sys
import django

# Add project to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from myproject.models import InvestmentPlan, Investment

def check_current_plans():
    """Check all existing investment plans"""
    print("📋 CHECKING CURRENT INVESTMENT PLANS")
    print("=" * 60)
    
    plans = InvestmentPlan.objects.all().order_by('id')
    
    for plan in plans:
        print(f"ID {plan.id}: {plan.name}")
        print(f"   Amount: ₱{plan.minimum_amount} - ₱{plan.maximum_amount}")
        print(f"   Duration: {plan.duration_days} days")
        print(f"   Return Rate: {plan.daily_return_rate}%")
        print(f"   Active: {plan.is_active}")
        
        # Check if plan has investments
        investments = Investment.objects.filter(plan=plan)
        print(f"   Investments: {investments.count()}")
        
        if investments.count() > 0:
            total_invested = sum(inv.amount for inv in investments)
            print(f"   Total Invested: ₱{total_invested}")
        
        print()

def remove_demo_plan():
    """Remove the Demo Plan and related investments"""
    print("🗑️ REMOVING DEMO PLAN")
    print("=" * 60)
    
    try:
        # Find Demo Plan
        demo_plan = InvestmentPlan.objects.get(name="Demo Plan")
        print(f"Found Demo Plan: ID {demo_plan.id}")
        
        # Check investments using this plan
        demo_investments = Investment.objects.filter(plan=demo_plan)
        investment_count = demo_investments.count()
        
        print(f"Demo investments to remove: {investment_count}")
        
        if investment_count > 0:
            for inv in demo_investments:
                print(f"   Removing investment: {inv.user.username} - ₱{inv.amount}")
                inv.delete()
        
        # Remove the plan
        demo_plan.delete()
        print(f"✅ Demo Plan removed successfully!")
        
    except InvestmentPlan.DoesNotExist:
        print(f"❌ Demo Plan not found")

def clean_demo_users():
    """Optionally clean demo users that were created for testing"""
    print("\n🧹 CHECKING DEMO USERS")
    print("=" * 60)
    
    from django.contrib.auth.models import User
    from myproject.models import UserProfile
    
    demo_phones = [
        "+639111111111",
        "+639222222222", 
        "+639333333333",
        "+639999999999"
    ]
    
    for phone in demo_phones:
        try:
            user = User.objects.get(username=phone)
            profile = UserProfile.objects.get(user=user)
            
            print(f"Demo user found: {phone}")
            print(f"   Referred by: {profile.referred_by.username if profile.referred_by else 'None'}")
            
            # Check if user has investments
            investments = Investment.objects.filter(user=user)
            print(f"   Investments: {investments.count()}")
            
            if investments.count() > 0:
                print(f"   ⚠️  User has investments - keeping for now")
            else:
                print(f"   No investments - can be removed if needed")
            
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            print(f"Demo user not found: {phone}")
    
    print(f"\n💡 Demo users are kept for testing referral system")

def verify_growfi_plans():
    """Verify that original GrowFi plans 1-8 are intact"""
    print(f"\n✅ VERIFYING ORIGINAL GROWFI PLANS")
    print("=" * 60)
    
    growfi_plans = [
        "GROWFI 1", "GROWFI 2", "GROWFI 3", "GROWFI 4",
        "GROWFI 5", "GROWFI 6", "GROWFI 7", "GROWFI 8"
    ]
    
    for plan_name in growfi_plans:
        try:
            plan = InvestmentPlan.objects.get(name=plan_name)
            print(f"✅ {plan_name}: ₱{plan.minimum_amount} - {plan.duration_days} days")
        except InvestmentPlan.DoesNotExist:
            print(f"❌ {plan_name}: NOT FOUND")

def main():
    print("🗑️ DEMO PLAN REMOVER")
    print("=" * 60)
    
    # Check current plans
    check_current_plans()
    
    # Remove demo plan
    remove_demo_plan()
    
    # Clean demo users (optional)
    clean_demo_users()
    
    # Verify original plans are intact
    verify_growfi_plans()
    
    print(f"\n🎯 SUMMARY:")
    print("=" * 60)
    print(f"✅ Demo Plan removed")
    print(f"✅ Original GrowFi plans 1-8 preserved")
    print(f"✅ Demo users kept for referral testing")
    print(f"✅ System cleaned up")

if __name__ == "__main__":
    main()
