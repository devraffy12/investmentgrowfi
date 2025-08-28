from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import uuid

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    withdrawable_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  # Only earnings
    non_withdrawable_bonus = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  # Registration bonus
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_invested = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    registration_bonus_claimed = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    valid_id = models.ImageField(upload_to='documents/', blank=True, null=True)
    proof_of_address = models.ImageField(upload_to='documents/', blank=True, null=True)
    referral_code = models.CharField(max_length=20, unique=True, blank=True)
    referred_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    date_joined = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - Profile"
    
    def save(self, *args, **kwargs):
        if not self.referral_code:
            # Generate a unique referral code
            import random
            import string
            while True:
                # Create an 8-character code with letters and numbers
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                # Ensure it's unique
                if not UserProfile.objects.filter(referral_code=code).exists():
                    self.referral_code = code
                    break
        super().save(*args, **kwargs)

class InvestmentPlan(models.Model):
    name = models.CharField(max_length=100)
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2)
    maximum_amount = models.DecimalField(max_digits=10, decimal_places=2)
    daily_return_rate = models.DecimalField(max_digits=15, decimal_places=10)  # Percentage
    duration_days = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - ₱{self.minimum_amount} to ₱{self.maximum_amount}"

    @property
    def daily_profit(self):
        """Return fixed daily profit mapping for GrowFi plans (1-8) - 20 DAYS DURATION."""
        mapping = {
            'GROWFI 1': Decimal('150'),  # ₱300 price, 20 days => 3000 total
            'GROWFI 2': Decimal('200'),  # ₱700 price, 20 days => 4000 total
            'GROWFI 3': Decimal('225'),  # ₱2200 price, 20 days => 4500 total
            'GROWFI 4': Decimal('570'),  # ₱3500 price, 20 days => 11400 total
            'GROWFI 5': Decimal('1125'), # ₱5000 price, 20 days => 22500 total
            'GROWFI 6': Decimal('2100'), # ₱7000 price, 20 days => 42000 total
            'GROWFI 7': Decimal('3150'), # ₱9000 price, 20 days => 63000 total
            'GROWFI 8': Decimal('3850'), # ₱11000 price, 20 days => 77000 total
        }
        if self.name in mapping:
            return mapping[self.name]
        # fallback to percentage if custom
        return (self.minimum_amount * (self.daily_return_rate or Decimal('0'))) / 100

    @property
    def total_revenue(self):
        """Return fixed total revenue for 20-day duration plans."""
        mapping = {
            'GROWFI 1': Decimal('3000'),  # ₱150 daily × 20 days
            'GROWFI 2': Decimal('4000'),  # ₱200 daily × 20 days
            'GROWFI 3': Decimal('4500'),  # ₱225 daily × 20 days
            'GROWFI 4': Decimal('11400'), # ₱570 daily × 20 days
            'GROWFI 5': Decimal('22500'), # ₱1125 daily × 20 days
            'GROWFI 6': Decimal('42000'), # ₱2100 daily × 20 days
            'GROWFI 7': Decimal('63000'), # ₱3150 daily × 20 days
            'GROWFI 8': Decimal('77000'), # ₱3850 daily × 20 days
        }
        if self.name in mapping:
            return mapping[self.name]
        return self.daily_profit * self.duration_days

    @property
    def net_profit(self):
        """Net profit equals stated total revenue for GrowFi spec."""
        return self.total_revenue

    @property
    def return_rate(self):
        """Alias used by some templates (percentage)."""
        return self.daily_return_rate

class Investment(models.Model):
    INVESTMENT_STATUS = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(InvestmentPlan, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    daily_return = models.DecimalField(max_digits=10, decimal_places=2)
    total_return = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=INVESTMENT_STATUS, default='active')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    last_payout_date = models.DateTimeField(null=True, blank=True)
    days_completed = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - ₱{self.amount} Investment"
    
    def save(self, *args, **kwargs):
        if not self.daily_return:
            self.daily_return = self.plan.daily_profit  # Use the plan's daily profit property
        if not self.end_date:
            self.end_date = self.start_date + timezone.timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.status == 'active'

    @property
    def total_earned(self):
        """Amount earned so far; fall back to computed estimation if total_return not updated."""
        if self.total_return and self.total_return > 0:
            return self.total_return
        # Estimate based on daily_return * days_completed
        try:
            return (self.daily_return or Decimal('0')) * Decimal(str(self.days_completed))
        except Exception:
            return Decimal('0')

class DailyPayout(models.Model):
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payout_date = models.DateTimeField(auto_now_add=True)
    day_number = models.IntegerField()
    
    def __str__(self):
        return f"Day {self.day_number} - ₱{self.amount} for {self.investment.user.username}"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('investment', 'Investment'),
        ('daily_payout', 'Daily Payout'),
        ('referral_bonus', 'Referral Bonus'),
        ('registration_bonus', 'Registration Bonus'),
    )
    
    TRANSACTION_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='pending')
    reference_number = models.CharField(max_length=100, unique=True, blank=True)
    api_transaction_id = models.CharField(max_length=200, blank=True, null=True)  # API transaction ID
    payment_method = models.CharField(max_length=20, blank=True)  # GCASH, PAYMAYA, etc.
    payment_url = models.URLField(blank=True, null=True)  # Payment gateway URL
    external_reference = models.CharField(max_length=200, blank=True, null=True)  # For PayMongo session ID
    gcash_number = models.CharField(max_length=15, blank=True)
    gcash_reference = models.CharField(max_length=100, blank=True)
    proof_of_payment = models.ImageField(upload_to='payments/', blank=True, null=True)
    admin_notes = models.TextField(blank=True)
    description = models.TextField(blank=True)  # Transaction description
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - ₱{self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            import uuid
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S%f')
            unique_suffix = str(uuid.uuid4()).replace('-', '')[:8]
            self.reference_number = f"TXN{timestamp}{self.user.id}{unique_suffix}"
        super().save(*args, **kwargs)

class ReferralCommission(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_earnings')
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_source')
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, null=True, blank=True)  # Made optional for registration bonuses
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    level = models.IntegerField()  # 1st level, 2nd level, etc.
    commission_type = models.CharField(max_length=20, default='registration', choices=[
        ('registration', 'Registration Bonus'),
        ('investment', 'Investment Commission'),
    ])  # Track type of commission
    date_earned = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.commission_type == 'registration':
            return f"{self.referrer.username} earned ₱{self.commission_amount} registration bonus from {self.referred_user.username}"
        else:
            return f"{self.referrer.username} earned ₱{self.commission_amount} from {self.referred_user.username}'s investment"

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('investment', 'Investment'),
        ('payout', 'Daily Payout'),
        ('withdrawal', 'Withdrawal'),
        ('deposit', 'Deposit'),
        ('referral', 'Referral'),
        ('system', 'System'),
        ('promotion', 'Promotion'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

class SupportTicket(models.Model):
    TICKET_STATUS = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    
    PRIORITY_LEVELS = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=TICKET_STATUS, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='medium')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Ticket #{self.id} - {self.subject}"

class TicketReply(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_staff_reply = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Reply to Ticket #{self.ticket.id}"

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    is_important = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class SystemSettings(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.key}: {self.value}"

class BankAccount(models.Model):
    ACCOUNT_TYPES = (
        ('gcash', 'GCash'),
        ('paymaya', 'PayMaya'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_accounts')
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    account_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=100, blank=True)  # For traditional banks
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'account_number', 'account_type']
    
    def __str__(self):
        return f"{self.get_account_type_display()} - {self.account_number} ({self.user.username})"
    
    def save(self, *args, **kwargs):
        # Ensure only one primary account per user
        if self.is_primary:
            BankAccount.objects.filter(user=self.user, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)
