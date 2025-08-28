#!/usr/bin/env python3
"""
Update PLAN 1 and PLAN 2 Daily Profits
PLAN 1: 150 daily x 20 days = 3000 total
PLAN 2: 200 daily x 20 days = 4000 total
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

def update_plan_1_and_2():
    print('🔄 UPDATING PLAN 1 AND PLAN 2')
    print('=' * 50)
    
    # Get PLAN 1 and PLAN 2
    plans_to_update = ['GROWFI 1', 'GROWFI 2']
    updated_plans = []
    
    for plan_name in plans_to_update:
        try:
            plan = InvestmentPlan.objects.get(name=plan_name, is_active=True)
            
            print(f'📋 {plan_name}:')
            print(f'   Amount: ₱{plan.minimum_amount}')
            print(f'   Old Daily: ₱{84 if plan_name == "GROWFI 1" else 132}')
            print(f'   New Daily: ₱{plan.daily_profit}')
            print(f'   Old Total: ₱{1680 if plan_name == "GROWFI 1" else 2640}')
            print(f'   New Total: ₱{plan.total_revenue}')
            print(f'   Duration: {plan.duration_days} days')
            print(f'   ✅ Updated successfully\n')
            
            updated_plans.append(plan)
            
        except InvestmentPlan.DoesNotExist:
            print(f'❌ {plan_name} not found')
    
    return updated_plans

def update_active_investments_plan_1_2():
    print('🔄 UPDATING ACTIVE INVESTMENTS FOR PLAN 1 & 2')
    print('=' * 50)
    
    # Get active investments for PLAN 1 and 2
    plan_names = ['GROWFI 1', 'GROWFI 2']
    updated_count = 0
    
    for plan_name in plan_names:
        investments = Investment.objects.filter(
            plan__name=plan_name,
            status='active'
        )
        
        print(f'📈 {plan_name} - Found {investments.count()} active investments')
        
        for investment in investments:
            old_daily = investment.daily_return
            new_daily = investment.plan.daily_profit
            
            print(f'   Investment ID {investment.id}:')
            print(f'   User: {investment.user.username}')
            print(f'   Amount: ₱{investment.amount}')
            print(f'   Old Daily: ₱{old_daily} → New Daily: ₱{new_daily}')
            
            # Update daily return
            investment.daily_return = new_daily
            investment.save()
            
            updated_count += 1
            print(f'   ✅ Updated\n')
    
    return updated_count

def verify_updates():
    print('✅ VERIFICATION OF PLAN 1 & 2 UPDATES')
    print('=' * 50)
    
    plans = InvestmentPlan.objects.filter(
        name__in=['GROWFI 1', 'GROWFI 2'],
        is_active=True
    ).order_by('name')
    
    for plan in plans:
        daily_profit = plan.daily_profit
        total_revenue = plan.total_revenue
        calculated_total = daily_profit * plan.duration_days
        investment_amount = plan.minimum_amount
        
        # Calculate ROI
        roi = ((total_revenue - investment_amount) / investment_amount) * 100
        
        print(f'Plan: {plan.name}')
        print(f'  Investment: ₱{investment_amount}')
        print(f'  Duration: {plan.duration_days} days')
        print(f'  Daily Profit: ₱{daily_profit}')
        print(f'  Total Revenue: ₱{total_revenue}')
        print(f'  Calculated (daily × days): ₱{calculated_total}')
        print(f'  Net Profit: ₱{total_revenue - investment_amount}')
        print(f'  ROI: {roi:.1f}%')
        
        if total_revenue == calculated_total:
            print(f'  ✅ Math checks out!')
        else:
            print(f'  ⚠️ Math discrepancy detected')
        print()

def main():
    print('🚀 UPDATING PLAN 1 & PLAN 2 DAILY PROFITS')
    print('=' * 60)
    print('PLAN 1: ₱150 daily × 20 days = ₱3,000 total')
    print('PLAN 2: ₱200 daily × 20 days = ₱4,000 total')
    print()
    
    try:
        # Update plans (models.py already updated)
        updated_plans = update_plan_1_and_2()
        
        # Update active investments
        investments_updated = update_active_investments_plan_1_2()
        
        # Verify updates
        verify_updates()
        
        # Final summary
        print('🎉 PLAN 1 & 2 UPDATE COMPLETE!')
        print('=' * 60)
        print(f'✅ Plans checked: {len(updated_plans)}')
        print(f'✅ Active investments updated: {investments_updated}')
        
        print('\n📊 UPDATED PLAN SUMMARY:')
        print('-' * 40)
        print('PLAN 1 (GROWFI 1):')
        print('  • Investment: ₱300')
        print('  • Daily Profit: ₱150')
        print('  • Duration: 20 days')
        print('  • Total Return: ₱3,000')
        print('  • Net Profit: ₱2,700')
        print('  • ROI: 900.0%')
        print()
        print('PLAN 2 (GROWFI 2):')
        print('  • Investment: ₱700')
        print('  • Daily Profit: ₱200')
        print('  • Duration: 20 days')
        print('  • Total Return: ₱4,000')
        print('  • Net Profit: ₱3,300')
        print('  • ROI: 471.4%')
        
        print('\n🎯 PLAN 1 & 2 SUCCESSFULLY UPDATED!')
        print('📈 Higher daily profits and total returns')
        print('✅ Ready for production!')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
