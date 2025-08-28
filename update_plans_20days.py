#!/usr/bin/env python3
"""
Update Investment Plans to 20 Days Duration
Adjust daily profits and total returns accordingly
"""
import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from myproject.models import InvestmentPlan, Investment
from django.utils import timezone
from decimal import Decimal

def update_investment_plans():
    print('🔄 UPDATING INVESTMENT PLANS TO 20 DAYS')
    print('=' * 60)
    
    # Get all active plans
    plans = InvestmentPlan.objects.filter(is_active=True).order_by('name')
    
    print(f'Found {plans.count()} plans to update...\n')
    
    for plan in plans:
        old_duration = plan.duration_days
        old_daily = plan.daily_profit  # This will use the NEW mapping from models.py
        new_total = plan.total_revenue  # This will use the NEW mapping from models.py
        
        print(f'📋 Updating {plan.name}:')
        print(f'   Amount: ₱{plan.minimum_amount}')
        print(f'   Duration: {old_duration} days → 20 days')
        print(f'   Daily Profit: ₱{old_daily} (new)')
        print(f'   Total Return: ₱{new_total} (new)')
        
        # Update duration to 20 days
        plan.duration_days = 20
        plan.save()
        
        print(f'   ✅ Updated successfully\n')
    
    return plans.count()

def verify_updated_plans():
    print('✅ VERIFICATION OF UPDATED PLANS')
    print('=' * 60)
    
    plans = InvestmentPlan.objects.filter(is_active=True).order_by('name')
    
    for plan in plans:
        daily_profit = plan.daily_profit
        total_revenue = plan.total_revenue
        calculated_total = daily_profit * plan.duration_days
        
        print(f'Plan: {plan.name}')
        print(f'  Duration: {plan.duration_days} days')
        print(f'  Daily Profit: ₱{daily_profit}')
        print(f'  Total Revenue: ₱{total_revenue}')
        print(f'  Calculated (daily × days): ₱{calculated_total}')
        
        if total_revenue == calculated_total:
            print(f'  ✅ Math checks out!')
        else:
            print(f'  ⚠️ Math discrepancy detected')
        print()

def update_active_investments():
    print('🔄 UPDATING ACTIVE INVESTMENTS')
    print('=' * 60)
    
    # Get all active investments
    active_investments = Investment.objects.filter(status='active')
    updated_count = 0
    
    print(f'Found {active_investments.count()} active investments to update...\n')
    
    for investment in active_investments:
        old_daily = investment.daily_return
        new_daily = investment.plan.daily_profit  # Get updated daily profit from plan
        
        print(f'📈 Investment ID {investment.id} ({investment.plan.name}):')
        print(f'   User: {investment.user.username}')
        print(f'   Amount: ₱{investment.amount}')
        print(f'   Old Daily Return: ₱{old_daily}')
        print(f'   New Daily Return: ₱{new_daily}')
        
        # Update daily return and recalculate end date
        investment.daily_return = new_daily
        investment.end_date = investment.start_date + timezone.timedelta(days=20)
        investment.save()
        
        updated_count += 1
        print(f'   ✅ Updated successfully\n')
    
    return updated_count

def main():
    print('🚀 INVESTMENT PLANS UPDATE TO 20 DAYS')
    print('=' * 60)
    print('Updating all plans (GROWFI 1-8) to 20-day duration')
    print('Adjusting daily profits and total returns accordingly\n')
    
    try:
        # Update plans
        plans_updated = update_investment_plans()
        
        # Verify updates
        verify_updated_plans()
        
        # Update active investments
        investments_updated = update_active_investments()
        
        # Final summary
        print('🎉 UPDATE COMPLETE!')
        print('=' * 60)
        print(f'✅ Plans updated: {plans_updated}')
        print(f'✅ Active investments updated: {investments_updated}')
        print('\n📊 NEW PLAN STRUCTURE (20 DAYS):')
        print('-' * 40)
        
        plans = InvestmentPlan.objects.filter(is_active=True).order_by('name')
        for plan in plans:
            roi_percentage = ((plan.total_revenue - plan.minimum_amount) / plan.minimum_amount) * 100
            print(f'{plan.name}: ₱{plan.minimum_amount} → ₱{plan.total_revenue} (₱{plan.daily_profit}/day, {roi_percentage:.1f}% ROI)')
        
        print('\n🎯 ALL PLANS NOW HAVE 20-DAY DURATION!')
        print('📈 Daily profits adjusted to maintain same total returns')
        print('✅ Ready for production!')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
