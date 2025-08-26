# payments/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import uuid

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
    ]
    
    PAYMENT_METHODS = [
        ('gcash', 'GCash'),
        ('maya', 'Maya'),
        ('paymaya', 'PayMaya'),
        ('manual', 'Manual'),
    ]
    
    # Basic transaction info
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='payment_transactions'
    )
    transaction_type = models.CharField(
        max_length=10, 
        choices=TRANSACTION_TYPES
    )
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text="Transaction amount"
    )
    
    # LA2568 specific fields
    reference_id = models.CharField(
        max_length=100, 
        unique=True,
        help_text="Unique reference ID (order_id for LA2568)"
    )
    la2568_order_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="LA2568 returned order ID"
    )
    la2568_transaction_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="LA2568 transaction ID"
    )
    
    # Status and payment details
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default='gcash'
    )
    
    # API response data
    api_request_data = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Data sent to LA2568 API"
    )
    api_response_data = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Response from LA2568 API"
    )
    callback_data = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Callback data from LA2568"
    )
    
    # Payment URLs and QR codes
    payment_url = models.URLField(
        blank=True,
        null=True,
        help_text="Direct payment URL from LA2568"
    )
    qr_code_url = models.URLField(
        blank=True,
        null=True,
        help_text="QR code image URL"
    )
    qr_code_base64 = models.TextField(
        blank=True,
        null=True,
        help_text="Base64 encoded QR code image"
    )
    
    # Financial details
    fee_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Transaction fee charged"
    )
    net_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Net amount after fees"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When transaction was processed by LA2568"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When transaction was completed"
    )
    
    # Tracking and audit
    client_ip = models.GenericIPAddressField(
        null=True, 
        blank=True,
        help_text="Client IP when transaction was created"
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        help_text="User agent string"
    )
    notes = models.TextField(
        blank=True, 
        null=True,
        help_text="Internal notes about transaction"
    )
    admin_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Admin notes and actions"
    )
    
    # Retry and error handling
    retry_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of API retry attempts"
    )
    last_error = models.TextField(
        blank=True,
        null=True,
        help_text="Last error message"
    )
    
    class Meta:
        db_table = 'payment_transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['reference_id']),
            models.Index(fields=['la2568_order_id']),
            models.Index(fields=['transaction_type', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['payment_method']),
        ]
        
    def __str__(self):
        return f"{self.get_transaction_type_display()} - ₱{self.amount} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        # Generate reference ID if not provided
        if not self.reference_id:
            timestamp = int(timezone.now().timestamp())
            self.reference_id = f"{self.transaction_type.upper()}_{self.user.id}_{timestamp}"
        
        # Calculate net amount
        if self.net_amount is None:
            self.net_amount = self.amount - self.fee_amount
            
        # Set completion timestamp
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
            
        super().save(*args, **kwargs)
    
    @property
    def is_completed(self):
        """Check if transaction is in a final state"""
        return self.status in ['completed', 'failed', 'cancelled', 'refunded']
    
    @property
    def is_successful(self):
        """Check if transaction was successful"""
        return self.status == 'completed'
    
    @property
    def can_be_cancelled(self):
        """Check if transaction can be cancelled"""
        return self.status in ['pending', 'processing']
    
    @property
    def can_be_retried(self):
        """Check if failed transaction can be retried"""
        return self.status == 'failed' and self.retry_count < 3
    
    def get_display_status(self):
        """Get user-friendly status display"""
        status_display = {
            'pending': 'Waiting for Payment',
            'processing': 'Processing Payment',
            'completed': 'Payment Successful',
            'failed': 'Payment Failed',
            'cancelled': 'Payment Cancelled',
            'refunded': 'Payment Refunded'
        }
        return status_display.get(self.status, self.status.title())
    
    def get_status_color(self):
        """Get Bootstrap color class for status"""
        color_map = {
            'pending': 'warning',
            'processing': 'info',
            'completed': 'success',
            'failed': 'danger',
            'cancelled': 'secondary',
            'refunded': 'primary'
        }
        return color_map.get(self.status, 'secondary')


class PaymentLog(models.Model):
    """Log all payment-related activities"""
    
    LOG_TYPES = [
        ('api_request', 'API Request'),
        ('api_response', 'API Response'),
        ('callback', 'Callback Received'),
        ('status_change', 'Status Change'),
        ('error', 'Error'),
        ('manual_action', 'Manual Action'),
    ]
    
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    log_type = models.CharField(
        max_length=20,
        choices=LOG_TYPES
    )
    message = models.TextField()
    data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional log data"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who triggered this log (for manual actions)"
    )
    
    class Meta:
        db_table = 'payment_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction', 'log_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.transaction.reference_id} - {self.get_log_type_display()}"


class PaymentMethod(models.Model):
    """Payment method configuration"""
    
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Payment method code (gcash, maya, etc.)"
    )
    name = models.CharField(
        max_length=100,
        help_text="Display name"
    )
    la2568_bank_code = models.CharField(
        max_length=20,
        help_text="Bank code for LA2568 API"
    )
    min_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('1.00')
    )
    max_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('50000.00')
    )
    fee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=Decimal('0.0000'),
        help_text="Fee percentage (0.02 = 2%)"
    )
    fee_fixed = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Fixed fee amount"
    )
    is_active = models.BooleanField(default=True)
    supports_deposits = models.BooleanField(default=True)
    supports_withdrawals = models.BooleanField(default=True)
    icon_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_methods'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def calculate_fee(self, amount):
        """Calculate fee for given amount"""
        percentage_fee = amount * self.fee_percentage
        total_fee = percentage_fee + self.fee_fixed
        return total_fee.quantize(Decimal('0.01'))
    
    def get_net_amount(self, amount):
        """Get net amount after fees"""
        fee = self.calculate_fee(amount)
        return amount - fee