#!/usr/bin/env python
"""
Daily Investment Processor
This script should be run daily to:
1. Process daily payouts for all active investments
2. Update investment progress
3. Complete investments that have reached their duration
4. Send notifications

Add this to your cron job:
0 0 * * * cd /path/to/your/project && python daily_processor.py

Or on Windows Task Scheduler:
Daily at 12:00 AM
"""

import os
import django
import logging
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.core.management import call_command
from django.utils import timezone
from myproject.models import Investment, UserProfile
from decimal import Decimal

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_payouts.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_daily_processing():
    """Run daily investment processing"""
    logger.info("=" * 60)
    logger.info("🚀 Starting Daily Investment Processing")
    logger.info(f"⏰ Processing date: {timezone.now().date()}")
    
    try:
        # 1. Process daily payouts using Django management command
        logger.info("📊 Processing daily payouts...")
        call_command('process_daily_payouts', verbosity=1)
        
        # 2. Update investment progress for all active investments
        logger.info("🔄 Updating investment progress...")
        update_investment_progress()
        
        # 3. Update user profile totals
        logger.info("💰 Updating user profile totals...")
        update_user_totals()
        
        logger.info("✅ Daily processing completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error during daily processing: {e}")
        import traceback
        logger.error(traceback.format_exc())

def update_investment_progress():
    """Update progress for all active investments"""
    active_investments = Investment.objects.filter(status='active')
    logger.info(f"   Found {active_investments.count()} active investments")
    
    for investment in active_investments:
        # Calculate days since start
        now = timezone.now()
        days_since_start = (now.date() - investment.start_date.date()).days + 1
        days_completed = min(days_since_start, investment.plan.duration_days)
        
        # Update investment record
        old_days = investment.days_completed
        investment.days_completed = days_completed
        investment.total_return = investment.daily_return * Decimal(str(days_completed))
        
        # Check if investment should be completed
        if days_completed >= investment.plan.duration_days and investment.status == 'active':
            investment.status = 'completed'
            logger.info(f"   ✅ Investment #{investment.id} completed for {investment.user.username}")
        
        investment.save()
        
        if old_days != days_completed:
            logger.info(f"   📈 Investment #{investment.id}: {old_days} → {days_completed} days")

def update_user_totals():
    """Update user profile totals based on transactions"""
    from django.db.models import Sum
    from myproject.models import Transaction
    
    profiles = UserProfile.objects.all()
    logger.info(f"   Updating {profiles.count()} user profiles")
    
    for profile in profiles:
        # Calculate total earnings from completed transactions
        earnings = Transaction.objects.filter(
            user=profile.user,
            transaction_type__in=['daily_payout', 'referral_bonus'],
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Calculate total invested
        invested = Transaction.objects.filter(
            user=profile.user,
            transaction_type='investment',
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Update profile
        old_earnings = profile.total_earnings
        old_invested = profile.total_invested
        
        profile.total_earnings = earnings
        profile.total_invested = invested
        profile.save()
        
        if old_earnings != earnings or old_invested != invested:
            logger.info(f"   💰 {profile.user.username}: Earnings ₱{old_earnings}→₱{earnings}, Invested ₱{old_invested}→₱{invested}")

def show_daily_summary():
    """Show summary of today's activity"""
    from myproject.models import DailyPayout, Transaction
    from django.db.models import Sum, Count
    
    today = timezone.now().date()
    
    # Today's payouts
    today_payouts = DailyPayout.objects.filter(payout_date__date=today)
    total_paid = today_payouts.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Today's transactions
    today_transactions = Transaction.objects.filter(
        created_at__date=today,
        transaction_type='daily_payout',
        status='completed'
    )
    
    logger.info("📊 Daily Summary:")
    logger.info(f"   💸 Payouts processed: {today_payouts.count()}")
    logger.info(f"   💰 Total amount paid: ₱{total_paid}")
    logger.info(f"   📝 Transactions created: {today_transactions.count()}")
    
    # Active investments
    active_investments = Investment.objects.filter(status='active')
    completed_today = Investment.objects.filter(
        status='completed',
        end_date__date=today
    )
    
    logger.info(f"   📈 Active investments: {active_investments.count()}")
    logger.info(f"   🏁 Completed today: {completed_today.count()}")

if __name__ == "__main__":
    run_daily_processing()
    show_daily_summary()
    logger.info("🎯 Daily processing finished")
