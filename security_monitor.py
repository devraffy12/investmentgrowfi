#!/usr/bin/env python
"""
Security Attack Detection System
Monitor for suspicious activities and potential attacks
"""

import os
import django
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
from myproject.models import UserProfile, Transaction

def detect_security_threats():
    """Comprehensive security threat detection"""
    print("🛡️ SECURITY ATTACK DETECTION SYSTEM")
    print("=" * 60)
    print(f"🕐 Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    threats_detected = []
    
    # 1. Brute Force Attack Detection
    print("1️⃣ BRUTE FORCE ATTACK DETECTION")
    print("-" * 40)
    
    # Check for multiple failed login attempts (simulate check)
    recent_time = timezone.now() - timedelta(hours=1)
    
    # Suspicious user creation patterns
    recent_users = User.objects.filter(date_joined__gte=recent_time)
    if recent_users.count() > 20:  # More than 20 users in 1 hour
        threat = f"⚠️ SUSPICIOUS: {recent_users.count()} users created in last hour"
        threats_detected.append(threat)
        print(threat)
    else:
        print(f"✅ Normal user registration rate: {recent_users.count()} users/hour")
    
    print()
    
    # 2. Suspicious Transaction Patterns
    print("2️⃣ SUSPICIOUS TRANSACTION DETECTION")
    print("-" * 40)
    
    recent_transactions = Transaction.objects.filter(created_at__gte=recent_time)
    
    # Check for unusual transaction volumes
    if recent_transactions.count() > 100:
        threat = f"⚠️ HIGH VOLUME: {recent_transactions.count()} transactions in last hour"
        threats_detected.append(threat)
        print(threat)
    else:
        print(f"✅ Normal transaction volume: {recent_transactions.count()} transactions/hour")
    
    # Check for large amount transactions
    large_transactions = recent_transactions.filter(amount__gte=10000)
    if large_transactions.exists():
        threat = f"⚠️ LARGE AMOUNTS: {large_transactions.count()} transactions ≥₱10,000"
        threats_detected.append(threat)
        print(threat)
        for tx in large_transactions[:5]:
            print(f"   - {tx.user.username}: ₱{tx.amount} ({tx.transaction_type})")
    else:
        print("✅ No unusually large transactions detected")
    
    print()
    
    # 3. Account Compromise Detection  
    print("3️⃣ ACCOUNT COMPROMISE DETECTION")
    print("-" * 40)
    
    # Check for users with suspicious balance changes
    suspicious_balances = UserProfile.objects.filter(balance__gte=50000)  # Very high balances
    if suspicious_balances.exists():
        threat = f"⚠️ SUSPICIOUS BALANCES: {suspicious_balances.count()} accounts with ≥₱50,000"
        threats_detected.append(threat)
        print(threat)
        for profile in suspicious_balances[:3]:
            print(f"   - {profile.user.username}: ₱{profile.balance}")
    else:
        print("✅ No suspicious account balances detected")
    
    print()
    
    # 4. Referral System Abuse
    print("4️⃣ REFERRAL SYSTEM ABUSE DETECTION")
    print("-" * 40)
    
    # Check for users with too many referrals
    heavy_referrers = User.objects.annotate(
        referral_count=Count('referrals')  # Fixed field name
    ).filter(referral_count__gte=20)
    
    if heavy_referrers.exists():
        threat = f"⚠️ REFERRAL ABUSE: {heavy_referrers.count()} users with ≥20 referrals"
        threats_detected.append(threat)
        print(threat)
        for user in heavy_referrers[:3]:
            count = user.referral_count
            print(f"   - {user.username}: {count} referrals")
    else:
        print("✅ No referral system abuse detected")
    
    print()
    
    # 5. Database Integrity Check
    print("5️⃣ DATABASE INTEGRITY CHECK")
    print("-" * 40)
    
    # Check for data inconsistencies
    total_users = User.objects.count()
    total_profiles = UserProfile.objects.count()
    orphaned_profiles = UserProfile.objects.filter(user__isnull=True).count()
    
    if total_users != total_profiles:
        threat = f"⚠️ DATA MISMATCH: {total_users} users vs {total_profiles} profiles"
        threats_detected.append(threat)
        print(threat)
    else:
        print(f"✅ Data consistency: {total_users} users = {total_profiles} profiles")
    
    if orphaned_profiles > 0:
        threat = f"⚠️ ORPHANED DATA: {orphaned_profiles} profiles without users"
        threats_detected.append(threat)
        print(threat)
    else:
        print("✅ No orphaned profile data detected")
    
    print()
    
    # 6. System Resource Monitoring
    print("6️⃣ SYSTEM RESOURCE MONITORING")
    print("-" * 40)
    
    # Check database size
    try:
        db_path = 'db.sqlite3'
        if os.path.exists(db_path):
            db_size_mb = os.path.getsize(db_path) / 1024 / 1024
            print(f"📊 Database size: {db_size_mb:.2f} MB")
            
            if db_size_mb > 100:  # Alert if DB > 100MB
                threat = f"⚠️ LARGE DATABASE: {db_size_mb:.2f} MB (may indicate attack)"
                threats_detected.append(threat)
                print(threat)
            else:
                print("✅ Database size within normal range")
        else:
            print("❌ Database file not found")
    except Exception as e:
        print(f"❌ Error checking database: {e}")
    
    print()
    
    # 7. Recent Activity Summary
    print("7️⃣ RECENT ACTIVITY SUMMARY")
    print("-" * 40)
    
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    today_users = User.objects.filter(date_joined__date=today).count()
    yesterday_users = User.objects.filter(date_joined__date=yesterday).count()
    
    today_transactions = Transaction.objects.filter(created_at__date=today).count()
    yesterday_transactions = Transaction.objects.filter(created_at__date=yesterday).count()
    
    print(f"📈 Today's Activity:")
    print(f"   New Users: {today_users} (yesterday: {yesterday_users})")
    print(f"   Transactions: {today_transactions} (yesterday: {yesterday_transactions})")
    
    # Check for unusual spikes
    if today_users > yesterday_users * 3:  # 3x increase
        threat = f"⚠️ USER SPIKE: {today_users} users today vs {yesterday_users} yesterday"
        threats_detected.append(threat)
        print(f"   {threat}")
    
    if today_transactions > yesterday_transactions * 3:  # 3x increase
        threat = f"⚠️ TRANSACTION SPIKE: {today_transactions} today vs {yesterday_transactions} yesterday"
        threats_detected.append(threat)
        print(f"   {threat}")
    
    print()
    
    # Final Security Report
    print("🎯 SECURITY ASSESSMENT REPORT")
    print("=" * 60)
    
    if threats_detected:
        print(f"🚨 THREATS DETECTED: {len(threats_detected)}")
        print("🔴 SECURITY ALERT LEVEL: HIGH")
        print()
        print("📋 DETECTED THREATS:")
        for i, threat in enumerate(threats_detected, 1):
            print(f"   {i}. {threat}")
        
        print()
        print("🛠️ RECOMMENDED ACTIONS:")
        print("   • Review user registration logs")
        print("   • Check server access logs")
        print("   • Monitor network traffic")
        print("   • Enable additional authentication")
        print("   • Backup database immediately")
        print("   • Consider temporary rate limiting")
        
    else:
        print("✅ NO THREATS DETECTED")
        print("🟢 SECURITY STATUS: NORMAL")
        print()
        print("📊 SYSTEM HEALTH:")
        print(f"   • Total Users: {total_users}")
        print(f"   • Total Transactions: {Transaction.objects.count()}")
        print(f"   • System Balance: ₱{sum(p.balance for p in UserProfile.objects.all())}")
        print("   • All security checks passed")
    
    return threats_detected

if __name__ == "__main__":
    threats = detect_security_threats()
    
    # Return exit code based on threat level
    if len(threats) >= 3:
        exit(2)  # Critical
    elif len(threats) >= 1:
        exit(1)  # Warning
    else:
        exit(0)  # Normal
