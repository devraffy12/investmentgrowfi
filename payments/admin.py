# Enhanced LA2568 Payment Admin
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from .models import Transaction, PaymentLog, PaymentMethod
import json


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'reference_id',
        'user_link',
        'transaction_type',
        'amount',
        'payment_method',
        'status_badge',
        'la2568_order_id',
        'created_at',
        'completed_at'
    ]
    
    list_filter = [
        'status',
        'transaction_type',
        'payment_method',
        'created_at',
        'completed_at'
    ]
    
    search_fields = [
        'reference_id',
        'la2568_order_id',
        'la2568_transaction_id',
        'user__username',
        'user__email'
    ]
    
    readonly_fields = [
        'reference_id',
        'created_at',
        'updated_at',
        'api_response_display',
        'callback_data_display',
        'payment_links'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'user',
                'transaction_type',
                'amount',
                'payment_method',
                'status'
            )
        }),
        ('LA2568 Details', {
            'fields': (
                'reference_id',
                'la2568_order_id',
                'la2568_transaction_id',
                'payment_links'
            )
        }),
        ('Financial Details', {
            'fields': (
                'fee_amount',
                'net_amount'
            ),
            'classes': ('collapse',)
        }),
        ('API Data', {
            'fields': (
                'api_response_display',
                'callback_data_display'
            ),
            'classes': ('collapse',)
        }),
        ('Tracking & Audit', {
            'fields': (
                'client_ip',
                'user_agent',
                'notes',
                'admin_notes',
                'retry_count',
                'last_error'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'processed_at',
                'completed_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    actions = [
        'verify_with_la2568',
        'mark_as_completed',
        'mark_as_failed',
        'export_transactions'
    ]
    
    def user_link(self, obj):
        """Create link to user admin page"""
        url = reverse('admin:auth_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    
    def status_badge(self, obj):
        """Display status with color coding"""
        colors = {
            'pending': '#ffc107',
            'processing': '#17a2b8',
            'completed': '#28a745',
            'failed': '#dc3545',
            'cancelled': '#6c757d',
            'refunded': '#007bff'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_display_status()
        )
    status_badge.short_description = 'Status'
    
    def payment_links(self, obj):
        """Display payment URLs"""
        links = []
        if obj.payment_url:
            links.append(f'<a href="{obj.payment_url}" target="_blank">Payment URL</a>')
        if obj.qr_code_url:
            links.append(f'<a href="{obj.qr_code_url}" target="_blank">QR Code</a>')
        if obj.qr_code_base64:
            links.append('<span title="Base64 QR available">📱 QR Data</span>')
        
        return format_html('<br>'.join(links)) if links else '-'
    payment_links.short_description = 'Payment Links'
    
    def api_response_display(self, obj):
        """Display formatted API response"""
        if obj.api_response_data:
            formatted = json.dumps(obj.api_response_data, indent=2)
            return format_html('<pre style="background: #f8f9fa; padding: 10px; border-radius: 4px; font-size: 12px;">{}</pre>', formatted)
        return '-'
    api_response_display.short_description = 'API Response Data'
    
    def callback_data_display(self, obj):
        """Display formatted callback data"""
        if obj.callback_data:
            formatted = json.dumps(obj.callback_data, indent=2)
            return format_html('<pre style="background: #f8f9fa; padding: 10px; border-radius: 4px; font-size: 12px;">{}</pre>', formatted)
        return '-'
    callback_data_display.short_description = 'Callback Data'
    
    def verify_with_la2568(self, request, queryset):
        """Verify selected transactions with LA2568 API"""
        from .la2568_service import la2568_service
        from django.db import transaction as db_transaction
        
        updated = 0
        errors = 0
        
        for transaction in queryset:
            try:
                result = la2568_service.query_transaction(transaction.reference_id)
                
                if result.get('status') != 'error':
                    new_status = la2568_service.map_status_to_internal(result.get('status'))
                    
                    if new_status != transaction.status:
                        with db_transaction.atomic():
                            transaction.status = new_status
                            transaction.api_response_data = result
                            transaction.admin_notes = f"Manual verification by {request.user.username} at {timezone.now()}"
                            transaction.save()
                            updated += 1
                else:
                    errors += 1
            except Exception:
                errors += 1
        
        if updated:
            self.message_user(request, f"Successfully updated {updated} transactions.")
        if errors:
            self.message_user(request, f"Failed to verify {errors} transactions.", level='ERROR')
    
    verify_with_la2568.short_description = "Verify with LA2568 API"
    
    def mark_as_completed(self, request, queryset):
        """Mark selected transactions as completed"""
        updated = queryset.filter(
            status__in=['pending', 'processing']
        ).update(
            status='completed',
            completed_at=timezone.now(),
            admin_notes=f"Manually marked as completed by {request.user.username} at {timezone.now()}"
        )
        self.message_user(request, f"Marked {updated} transactions as completed.")
    
    mark_as_completed.short_description = "Mark as completed"
    
    def mark_as_failed(self, request, queryset):
        """Mark selected transactions as failed"""
        updated = queryset.filter(
            status__in=['pending', 'processing']
        ).update(
            status='failed',
            admin_notes=f"Manually marked as failed by {request.user.username} at {timezone.now()}"
        )
        self.message_user(request, f"Marked {updated} transactions as failed.")
    
    mark_as_failed.short_description = "Mark as failed"


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_link',
        'log_type',
        'message_preview',
        'created_by',
        'created_at'
    ]
    
    list_filter = [
        'log_type',
        'created_at',
        'created_by'
    ]
    
    search_fields = [
        'transaction__reference_id',
        'message',
        'transaction__user__username'
    ]
    
    readonly_fields = [
        'transaction',
        'log_type',
        'message',
        'data_display',
        'created_at',
        'created_by'
    ]
    
    def transaction_link(self, obj):
        """Create link to transaction admin page"""
        url = reverse('admin:payments_transaction_change', args=[obj.transaction.pk])
        return format_html('<a href="{}">{}</a>', url, obj.transaction.reference_id)
    transaction_link.short_description = 'Transaction'
    
    def message_preview(self, obj):
        """Show truncated message"""
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_preview.short_description = 'Message'
    
    def data_display(self, obj):
        """Display formatted log data"""
        if obj.data:
            formatted = json.dumps(obj.data, indent=2)
            return format_html('<pre style="background: #f8f9fa; padding: 10px; border-radius: 4px; font-size: 12px;">{}</pre>', formatted)
        return '-'
    data_display.short_description = 'Log Data'


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'code',
        'la2568_bank_code',
        'min_amount',
        'max_amount',
        'fee_display',
        'is_active',
        'supports_deposits',
        'supports_withdrawals'
    ]
    
    list_filter = [
        'is_active',
        'supports_deposits',
        'supports_withdrawals'
    ]
    
    search_fields = [
        'name',
        'code',
        'la2568_bank_code'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name',
                'code',
                'la2568_bank_code',
                'description'
            )
        }),
        ('Limits & Fees', {
            'fields': (
                'min_amount',
                'max_amount',
                'fee_percentage',
                'fee_fixed'
            )
        }),
        ('Capabilities', {
            'fields': (
                'is_active',
                'supports_deposits',
                'supports_withdrawals'
            )
        }),
        ('Display', {
            'fields': (
                'icon_url',
            )
        })
    )
    
    def fee_display(self, obj):
        """Display fee information"""
        fees = []
        if obj.fee_percentage > 0:
            fees.append(f"{obj.fee_percentage * 100}%")
        if obj.fee_fixed > 0:
            fees.append(f"₱{obj.fee_fixed}")
        
        return " + ".join(fees) if fees else "Free"
    fee_display.short_description = 'Fees'


# Custom admin site configuration
admin.site.site_header = "LA2568 Payment Administration"
admin.site.site_title = "LA2568 Payments"
admin.site.index_title = "Payment Management Dashboard"
