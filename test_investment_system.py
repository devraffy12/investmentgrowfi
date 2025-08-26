#!/usr/bin/env python
"""
Test script to verify and fix investment system
Run this to:
1. Process any missing daily payouts
2. Update investment progress 
3. Fix days_completed calculations
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth.models import User
from myproject.models import Investment, DailyPayout, UserProfile, Notification, Transaction
from decimal import Decimal
from datetime import timedelta

def test_and_fix_investments():
    """Test and fix investment calculations"""
    print("🔍 Testing and fixing investment system...")
    
    # Get all active investments
    active_investments = Investment.objects.filter(status='active')
    print(f"📊 Found {active_investments.count()} active investments")
    
    for investment in active_investments:
        print(f"\n🔄 Processing investment #{investment.id} for {investment.user.username}")
        print(f"   Plan: {investment.plan.name}")
        print(f"   Amount: ₱{investment.amount}")
        print(f"   Start Date: {investment.start_date}")
        print(f"   Daily Return: ₱{investment.daily_return}")
        
        # Calculate actual days since start
        now = timezone.now()
        days_since_start = (now.date() - investment.start_date.date()).days + 1
        days_completed = min(days_since_start, investment.plan.duration_days)
        
        print(f"   Days since start: {days_since_start}")
        print(f"   Days completed: {days_completed}")
        print(f"   Plan duration: {investment.plan.duration_days}")
        
        # Update investment record
        old_days = investment.days_completed
        old_total = investment.total_return
        
        investment.days_completed = days_completed
        investment.total_return = investment.daily_return * Decimal(str(days_completed))
        
        if days_completed >= investment.plan.duration_days:
            investment.status = 'completed'
            print(f"   ✅ Investment completed!")
        
        investment.save()
        
        print(f"   Updated days: {old_days} → {days_completed}")
        print(f"   Updated total return: ₱{old_total} → ₱{investment.total_return}")
        
        # Process missing daily payouts
        process_missing_payouts(investment, days_completed)

def process_missing_payouts(investment, days_completed):
    """Process any missing daily payouts for an investment"""
    print(f"   🔍 Checking for missing payouts...")
    
    # Get existing payouts
    existing_payouts = DailyPayout.objects.filter(investment=investment).count()
    print(f"   Existing payouts: {existing_payouts}")
    print(f"   Should have payouts: {days_completed}")
    
    if existing_payouts < days_completed:
        missing_days = days_completed - existing_payouts
        print(f"   ⚠️ Missing {missing_days} payouts - creating them...")
        
        for day in range(existing_payouts + 1, days_completed + 1):
            # Create missing payout
            payout = DailyPayout.objects.create(
                investment=investment,
                amount=investment.daily_return,
                day_number=day
            )
            
            # Create transaction record
            Transaction.objects.create(
                user=investment.user,
                transaction_type='daily_payout',
                amount=investment.daily_return,
                status='completed'
            )
            
            print(f"     ✅ Created payout for day {day}: ₱{investment.daily_return}")
        
        # Update user profile balance
        try:
            profile = UserProfile.objects.get(user=investment.user)
            missing_earnings = investment.daily_return * Decimal(str(missing_days))
            
            old_balance = profile.balance
            old_earnings = profile.total_earnings
            
            profile.balance += missing_earnings
            profile.total_earnings += missing_earnings
            profile.save()
            
            print(f"   💰 Updated user balance: ₱{old_balance} → ₱{profile.balance}")
            print(f"   💰 Updated total earnings: ₱{old_earnings} → ₱{profile.total_earnings}")
            
        except UserProfile.DoesNotExist:
            print(f"   ❌ UserProfile not found for {investment.user.username}")
    else:
        print(f"   ✅ All payouts up to date")

def create_test_investment():
    """Create a test investment for demonstration"""
    print("\n🧪 Creating test investment...")
    
    # Get first user
    user = User.objects.first()
    if not user:
        print("❌ No users found")
        return
    
    # Get first investment plan
    from myproject.models import InvestmentPlan
    plan = InvestmentPlan.objects.first()
    if not plan:
        print("❌ No investment plans found")
        return
    
    # Create test investment (backdated by 5 days to show progress)
    test_amount = Decimal('1000.00')
    start_date = timezone.now() - timedelta(days=5)
    
    investment = Investment.objects.create(
        user=user,
        plan=plan,
        amount=test_amount,
        daily_return=plan.daily_profit,
        start_date=start_date,
        end_date=start_date + timedelta(days=plan.duration_days)
    )
    
    print(f"✅ Created test investment #{investment.id}")
    print(f"   User: {user.username}")
    print(f"   Plan: {plan.name}")
    print(f"   Amount: ₱{test_amount}")
    print(f"   Start Date: {start_date}")
    print(f"   Daily Return: ₱{plan.daily_profit}")
    
    # Process payouts for this investment
    days_completed = min(5, plan.duration_days)
    process_missing_payouts(investment, days_completed)
    
    return investment

def show_user_stats():
    """Show current user statistics"""
    print("\n📊 Current User Statistics:")
    print("-" * 50)
    
    for user in User.objects.all()[:3]:  # Show first 3 users
        try:
            profile = UserProfile.objects.get(user=user)
            investments = Investment.objects.filter(user=user)
            
            print(f"\n👤 User: {user.username}")
            print(f"   Balance: ₱{profile.balance}")
            print(f"   Total Earnings: ₱{profile.total_earnings}")
            print(f"   Total Invested: ₱{profile.total_invested}")
            print(f"   Active Investments: {investments.filter(status='active').count()}")
            print(f"   Completed Investments: {investments.filter(status='completed').count()}")
            
        except UserProfile.DoesNotExist:
            print(f"   ❌ No profile found for {user.username}")

if __name__ == "__main__":
    print("🚀 Starting Investment System Test & Fix")
    print("=" * 60)
    
    # Show current stats
    show_user_stats()
    
    # Test and fix existing investments
    test_and_fix_investments()
    
    # Show updated stats
    print("\n" + "=" * 60)
    print("📈 AFTER PROCESSING:")
    show_user_stats()
    
    print("\n✅ Investment system test completed!")
    print("\n💡 To run daily payouts regularly, set up a cron job:")
    print("   python manage.py process_daily_payouts")
