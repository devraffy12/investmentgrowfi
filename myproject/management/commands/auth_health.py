"""
Django management command to monitor and maintain authentication health
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import timedelta
import json


class Command(BaseCommand):
    help = 'Monitor authentication health and clean up old sessions'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up expired sessions',
        )
        parser.add_argument(
            '--report',
            action='store_true',
            help='Generate authentication health report',
        )
    
    def handle(self, *args, **options):
        if options['cleanup']:
            self.cleanup_sessions()
        
        if options['report']:
            self.generate_report()
        
        if not options['cleanup'] and not options['report']:
            # Default: run both
            self.generate_report()
            self.cleanup_sessions()
    
    def cleanup_sessions(self):
        """Clean up expired sessions"""
        self.stdout.write('🧹 Cleaning up expired sessions...')
        
        # Delete expired sessions
        expired_count = Session.objects.filter(expire_date__lt=timezone.now()).count()
        Session.objects.filter(expire_date__lt=timezone.now()).delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Deleted {expired_count} expired sessions')
        )
    
    def generate_report(self):
        """Generate authentication health report"""
        self.stdout.write('📊 Authentication Health Report')
        self.stdout.write('=' * 50)
        
        # User statistics
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        recent_logins = User.objects.filter(
            last_login__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        self.stdout.write(f'👥 Total Users: {total_users}')
        self.stdout.write(f'✅ Active Users: {active_users}')
        self.stdout.write(f'🔐 Recent Logins (7 days): {recent_logins}')
        
        # Session statistics
        active_sessions = Session.objects.filter(expire_date__gt=timezone.now()).count()
        expired_sessions = Session.objects.filter(expire_date__lte=timezone.now()).count()
        
        self.stdout.write(f'📱 Active Sessions: {active_sessions}')
        self.stdout.write(f'💀 Expired Sessions: {expired_sessions}')
        
        # Recent registrations
        recent_users = User.objects.filter(
            date_joined__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        self.stdout.write(f'🆕 New Users (7 days): {recent_users}')
        
        # Authentication issues (users with no recent login)
        old_users = User.objects.filter(
            is_active=True,
            last_login__lt=timezone.now() - timedelta(days=30)
        ).count() if User.objects.filter(last_login__isnull=False).exists() else 0
        
        never_logged_in = User.objects.filter(
            is_active=True,
            last_login__isnull=True
        ).count()
        
        self.stdout.write(f'⚠️ Users not logged in 30+ days: {old_users}')
        self.stdout.write(f'❓ Users never logged in: {never_logged_in}')
        
        # Recommendations
        self.stdout.write('\n💡 Recommendations:')
        if expired_sessions > 100:
            self.stdout.write('• Run session cleanup more frequently')
        if never_logged_in > recent_users * 0.5:
            self.stdout.write('• Check registration process - many users not logging in')
        if active_sessions < recent_logins * 0.3:
            self.stdout.write('• Session persistence issues detected')
            
        self.stdout.write('\n✅ Report complete')
