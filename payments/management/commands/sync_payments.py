"""
Django management command to check pending payments and sync with LA2568
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction as db_transaction
from payments.models import Transaction as PaymentTransaction
from payments.la2568_service import la2568_service
from myproject.models import Transaction as InvestmentTransaction, UserProfile
import time


class Command(BaseCommand):
    help = 'Check and sync pending payments with LA2568 API'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--max-age-hours',
            type=int,
            default=24,
            help='Maximum age of transactions to check (in hours, default: 24)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Maximum number of transactions to process (default: 50)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes'
        )
    
    def handle(self, *args, **options):
        max_age_hours = options['max_age_hours']
        limit = options['limit']
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS('🔄 Syncing pending payments with LA2568'))
        self.stdout.write('=' * 60)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️  DRY RUN MODE - No changes will be made'))
        
        # Calculate cutoff time
        cutoff_time = timezone.now() - timezone.timedelta(hours=max_age_hours)
        
        # Get pending transactions
        pending_transactions = PaymentTransaction.objects.filter(
            status__in=['pending', 'processing'],
            created_at__gte=cutoff_time
        ).order_by('-created_at')[:limit]
        
        self.stdout.write(f"📊 Found {pending_transactions.count()} pending transactions to check")
        
        if not pending_transactions.exists():
            self.stdout.write(self.style.SUCCESS('✅ No pending transactions found'))
            return
        
        updated_count = 0
        error_count = 0
        
        for payment_transaction in pending_transactions:
            self.stdout.write(f"\n🔍 Checking transaction: {payment_transaction.reference_id}")
            
            try:
                # Query LA2568 API
                result = la2568_service.query_transaction(payment_transaction.reference_id)
                
                if result.get('status') == 'error':
                    self.stdout.write(f"❌ API Error: {result.get('message')}")
                    error_count += 1
                    continue
                
                # Get current and new status
                current_status = payment_transaction.status
                api_status = result.get('status', '')
                new_status = la2568_service.map_status_to_internal(api_status)
                
                self.stdout.write(f"  Current: {current_status}")
                self.stdout.write(f"  API Status: {api_status}")
                self.stdout.write(f"  New Status: {new_status}")
                
                # Check if status changed
                if new_status != current_status:
                    self.stdout.write(f"  ⚡ Status change detected: {current_status} → {new_status}")
                    
                    if not dry_run:
                        try:
                            with db_transaction.atomic():
                                # Update payment transaction
                                payment_transaction.status = new_status
                                payment_transaction.api_response_data = result
                                
                                if new_status == 'completed' and not payment_transaction.completed_at:
                                    payment_transaction.completed_at = timezone.now()
                                
                                payment_transaction.save()
                                
                                # Update investment transaction
                                try:
                                    investment_transaction = InvestmentTransaction.objects.select_for_update().get(
                                        reference_number=payment_transaction.reference_id
                                    )
                                    investment_transaction.status = new_status
                                    investment_transaction.save()
                                except InvestmentTransaction.DoesNotExist:
                                    self.stdout.write(f"  ⚠️  Investment transaction not found")
                                
                                # Handle balance updates
                                if new_status == 'completed' and current_status != 'completed':
                                    if payment_transaction.transaction_type == 'deposit':
                                        try:
                                            profile = UserProfile.objects.select_for_update().get(
                                                user=payment_transaction.user
                                            )
                                            profile.balance += payment_transaction.amount
                                            profile.save()
                                            self.stdout.write(f"  💰 Added ₱{payment_transaction.amount} to user balance")
                                        except UserProfile.DoesNotExist:
                                            self.stdout.write(f"  ❌ User profile not found")
                                
                                elif new_status == 'failed' and payment_transaction.transaction_type == 'withdraw':
                                    if current_status in ['pending', 'processing']:
                                        try:
                                            profile = UserProfile.objects.select_for_update().get(
                                                user=payment_transaction.user
                                            )
                                            profile.balance += payment_transaction.amount
                                            profile.save()
                                            self.stdout.write(f"  🔄 Refunded ₱{payment_transaction.amount} for failed withdrawal")
                                        except UserProfile.DoesNotExist:
                                            self.stdout.write(f"  ❌ User profile not found")
                                
                                updated_count += 1
                                self.stdout.write(f"  ✅ Transaction updated successfully")
                                
                        except Exception as e:
                            self.stdout.write(f"  ❌ Database update failed: {str(e)}")
                            error_count += 1
                    else:
                        self.stdout.write(f"  🔄 Would update transaction (dry run)")
                        updated_count += 1
                else:
                    self.stdout.write(f"  ✓ No status change")
                
                # Add small delay to avoid hitting API rate limits
                time.sleep(0.5)
                
            except Exception as e:
                self.stdout.write(f"❌ Error processing transaction: {str(e)}")
                error_count += 1
        
        # Summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS(f'📈 Sync Summary:'))
        self.stdout.write(f"  Transactions checked: {pending_transactions.count()}")
        self.stdout.write(f"  Transactions updated: {updated_count}")
        self.stdout.write(f"  Errors encountered: {error_count}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING('  (This was a dry run - no actual changes made)'))
        
        self.stdout.write('\n💡 Usage Examples:')
        self.stdout.write('  python manage.py sync_payments --max-age-hours 6 --limit 20')
        self.stdout.write('  python manage.py sync_payments --dry-run')
