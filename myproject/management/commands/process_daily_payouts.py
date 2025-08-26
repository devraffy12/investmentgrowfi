from django.core.management.base import BaseCommand
from django.utils import timezone
from myproject.models import Investment, DailyPayout, UserProfile, Notification, Transaction
from decimal import Decimal

class Command(BaseCommand):
    help = 'Process daily payouts for active investments'

    def handle(self, *args, **options):
        today = timezone.now().date()
        self.stdout.write(f'Processing daily payouts for {today}')
        
        # Get all active investments
        active_investments = Investment.objects.filter(
            status='active',
            start_date__date__lte=today,
            end_date__date__gte=today
        )
        
        payouts_processed = 0
        
        for investment in active_investments:
            # Check if payout already processed for today
            if DailyPayout.objects.filter(
                investment=investment,
                payout_date__date=today
            ).exists():
                continue
            
            # Calculate which day this is
            days_since_start = (today - investment.start_date.date()).days + 1
            
            if days_since_start <= investment.plan.duration_days:
                # Create daily payout
                payout = DailyPayout.objects.create(
                    investment=investment,
                    amount=investment.daily_return,
                    day_number=days_since_start
                )
                
                # Add to user balance
                profile = UserProfile.objects.get(user=investment.user)
                profile.balance += investment.daily_return
                profile.total_earnings += investment.daily_return
                profile.save()
                
                # Update investment
                investment.total_return += investment.daily_return
                investment.days_completed = days_since_start
                investment.last_payout_date = timezone.now()
                
                # Check if investment is completed
                if days_since_start >= investment.plan.duration_days:
                    investment.status = 'completed'
                    
                    # Create completion notification
                    Notification.objects.create(
                        user=investment.user,
                        title='Investment Completed!',
                        message=f'Your investment of ₱{investment.amount} has been completed. Total return: ₱{investment.total_return}',
                        notification_type='investment'
                    )
                
                investment.save()
                
                # Create transaction record
                Transaction.objects.create(
                    user=investment.user,
                    transaction_type='daily_payout',
                    amount=investment.daily_return,
                    status='completed'
                )
                
                # Create payout notification
                Notification.objects.create(
                    user=investment.user,
                    title='Daily Payout Received',
                    message=f'You received ₱{investment.daily_return} from your {investment.plan.name} investment (Day {days_since_start})',
                    notification_type='payout'
                )
                
                payouts_processed += 1
                self.stdout.write(f'Processed payout for {investment.user.username} - ₱{investment.daily_return}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully processed {payouts_processed} daily payouts')
        )
