#!/usr/bin/env python3
"""
Daily Security Check - Investment Platform
Quick daily security health check script
"""

import os
import django
import sys
from datetime import datetime, timedelta

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from myproject.models import UserProfile, Transaction
from django.utils import timezone

def daily_security_check():
    """Quick daily security health check"""
    
    print("🛡️  DAILY SECURITY CHECK")
    print("=" * 40)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()
    
    # Data integrity check
    user_count = User.objects.count()
    profile_count = UserProfile.objects.count()
    
    print("🔍 DATA INTEGRITY:")
    if user_count == profile_count:
        print(f"✅ Users & Profiles: {user_count} = {profile_count}")
    else:
        print(f"⚠️  MISMATCH: {user_count} users vs {profile_count} profiles")
    
    # Recent activity (last 24 hours)
    yesterday = timezone.now() - timedelta(days=1)
    new_users = User.objects.filter(date_joined__gte=yesterday).count()
    new_transactions = Transaction.objects.filter(created_at__gte=yesterday).count()
    
    print("📈 RECENT ACTIVITY (24h):")
    print(f"   New Users: {new_users}")
    print(f"   Transactions: {new_transactions}")
    
    # High-value account monitoring
    high_balance = UserProfile.objects.filter(balance__gte=5000).count()
    print(f"💎 High-value accounts (≥₱5,000): {high_balance}")
    
    # System totals
    total_balance = sum(p.balance for p in UserProfile.objects.all())
    total_transactions = Transaction.objects.count()
    
    print("\n💰 SYSTEM TOTALS:")
    print(f"   Total Balance: ₱{total_balance:,.2f}")
    print(f"   Total Transactions: {total_transactions}")
    
    # Security status
    print("\n🛡️  SECURITY STATUS:")
    
    security_issues = []
    
    # Check for data integrity issues
    if user_count != profile_count:
        security_issues.append("Data integrity mismatch")
    
    # Check for unusual activity
    if new_users > 50:  # More than 50 new users in 24h
        security_issues.append("High registration rate")
    
    if new_transactions > 100:  # More than 100 transactions in 24h
        security_issues.append("High transaction volume")
    
    if not security_issues:
        print("✅ ALL SYSTEMS SECURE")
        print("🟢 No security threats detected")
    else:
        print("⚠️  ISSUES DETECTED:")
        for issue in security_issues:
            print(f"   • {issue}")
    
    print("\n" + "=" * 40)
    print("Security check completed! 🎯")
    
    return len(security_issues) == 0

if __name__ == "__main__":
    try:
        is_secure = daily_security_check()
        exit_code = 0 if is_secure else 1
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ Error during security check: {e}")
        sys.exit(1)
