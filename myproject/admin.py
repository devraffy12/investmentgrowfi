from django.contrib import admin
from .models import *

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'total_earnings', 'total_invested', 'is_verified', 'date_joined']
    list_filter = ['is_verified', 'registration_bonus_claimed', 'date_joined']
    search_fields = ['user__username', 'user__email', 'phone_number']
    readonly_fields = ['referral_code', 'date_joined']

@admin.register(InvestmentPlan)
class InvestmentPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'minimum_amount', 'maximum_amount', 'daily_return_rate', 'duration_days', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']

@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'amount', 'daily_return', 'status', 'start_date', 'end_date', 'days_completed']
    list_filter = ['status', 'start_date', 'plan']
    search_fields = ['user__username', 'plan__name']
    readonly_fields = ['start_date', 'end_date', 'daily_return']

@admin.register(DailyPayout)
class DailyPayoutAdmin(admin.ModelAdmin):
    list_display = ['investment', 'amount', 'day_number', 'payout_date']
    list_filter = ['payout_date']
    search_fields = ['investment__user__username']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_type', 'amount', 'status', 'reference_number', 'created_at']
    list_filter = ['transaction_type', 'status', 'created_at']
    search_fields = ['user__username', 'reference_number', 'gcash_number']
    readonly_fields = ['reference_number', 'created_at']
    
    actions = ['approve_transactions', 'reject_transactions']
    
    def approve_transactions(self, request, queryset):
        for transaction in queryset.filter(status='pending'):
            if transaction.transaction_type == 'deposit':
                profile = UserProfile.objects.get(user=transaction.user)
                profile.balance += transaction.amount
                profile.save()
                
                Notification.objects.create(
                    user=transaction.user,
                    title='Deposit Approved',
                    message=f'Your deposit of ₱{transaction.amount} has been approved.',
                    notification_type='deposit'
                )
            
            transaction.status = 'approved'
            transaction.save()
        
        self.message_user(request, f"{queryset.count()} transactions approved successfully.")
    
    def reject_transactions(self, request, queryset):
        for transaction in queryset.filter(status='pending'):
            if transaction.transaction_type == 'withdrawal':
                # Restore balance for rejected withdrawals
                profile = UserProfile.objects.get(user=transaction.user)
                fee = transaction.amount * 0.10
                profile.balance += (transaction.amount + fee)
                profile.save()
                
                Notification.objects.create(
                    user=transaction.user,
                    title='Withdrawal Rejected',
                    message=f'Your withdrawal of ₱{transaction.amount} has been rejected. Balance restored.',
                    notification_type='withdrawal'
                )
            
            transaction.status = 'rejected'
            transaction.save()
        
        self.message_user(request, f"{queryset.count()} transactions rejected.")

@admin.register(ReferralCommission)
class ReferralCommissionAdmin(admin.ModelAdmin):
    list_display = ['referrer', 'referred_user', 'commission_amount', 'level', 'date_earned']
    list_filter = ['level', 'date_earned']
    search_fields = ['referrer__username', 'referred_user__username']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title']

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'subject', 'status', 'priority', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['user__username', 'subject']

@admin.register(TicketReply)
class TicketReplyAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'user', 'is_staff_reply', 'created_at']
    list_filter = ['is_staff_reply', 'created_at']

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'is_important', 'created_by', 'created_at']
    list_filter = ['is_active', 'is_important', 'created_at']
    search_fields = ['title', 'content']

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'updated_at']
    search_fields = ['key', 'description']
