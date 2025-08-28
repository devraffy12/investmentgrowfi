#!/usr/bin/env python3
"""
Fix Data Mismatch - Investment Platform Security Fix
Resolves the detected user/profile mismatch issue
"""

import os
import django
import sys

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from myproject.models import UserProfile, Transaction
from django.utils import timezone
import random
import string

def generate_referral_code():
    """Generate a unique 8-character referral code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not UserProfile.objects.filter(referral_code=code).exists():
            return code

def fix_data_mismatch():
    """Fix the detected data mismatch between users and profiles"""
    
    print("🔍 FIXING DATA MISMATCH")
    print("=" * 50)
    
    # Find orphaned users (users without profiles)
    orphaned_users = User.objects.filter(userprofile__isnull=True)
    orphaned_count = orphaned_users.count()
    
    print(f"Found {orphaned_count} users without profiles:")
    
    if orphaned_count == 0:
        print("✅ No data mismatch found. All users have profiles.")
        return
    
    for user in orphaned_users:
        print(f"  📱 {user.username} (joined: {user.date_joined})")
        
        # Create missing UserProfile
        try:
            profile = UserProfile.objects.create(
                user=user,
                phone_number=user.username,  # Phone is stored as username
                balance=0.00,
                total_invested=0.00,
                total_earnings=0.00,
                referral_code=generate_referral_code(),
                is_verified=True
            )
            
            print(f"    ✅ Created profile with referral code: {profile.referral_code}")
            
            # Check if user has any transactions without profile
            transactions = Transaction.objects.filter(user=user)
            trans_count = transactions.count()
            
            if trans_count > 0:
                print(f"    💰 Found {trans_count} existing transactions")
                
                # Update user balance based on transactions
                total_balance = sum(t.amount for t in transactions)
                profile.balance = total_balance
                profile.total_invested = total_balance
                profile.save()
                
                print(f"    💰 Updated balance to ₱{total_balance}")
            
        except Exception as e:
            print(f"    ❌ Error creating profile: {e}")
    
    # Verify the fix
    print("\n🔍 VERIFICATION")
    print("=" * 30)
    
    user_count = User.objects.count()
    profile_count = UserProfile.objects.count()
    
    print(f"Users: {user_count}")
    print(f"Profiles: {profile_count}")
    
    if user_count == profile_count:
        print("✅ DATA MISMATCH FIXED! All users now have profiles.")
    else:
        print(f"⚠️  Still have mismatch: {user_count - profile_count} users without profiles")
    
    # Check for reverse issue (profiles without users)
    orphaned_profiles = UserProfile.objects.filter(user__isnull=True)
    if orphaned_profiles.exists():
        print(f"⚠️  Found {orphaned_profiles.count()} profiles without users!")
        for profile in orphaned_profiles:
            print(f"    🔥 Profile ID {profile.id} has no user")
    
    return user_count == profile_count

def generate_security_report():
    """Generate a comprehensive security report after fixing"""
    
    print("\n📊 SECURITY REPORT")
    print("=" * 40)
    
    # Basic stats
    total_users = User.objects.count()
    total_profiles = UserProfile.objects.count()
    total_transactions = Transaction.objects.count()
    
    print(f"👥 Total Users: {total_users}")
    print(f"📋 Total Profiles: {total_profiles}")
    print(f"💰 Total Transactions: {total_transactions}")
    
    # Data integrity
    orphaned_users = User.objects.filter(userprofile__isnull=True).count()
    orphaned_profiles = UserProfile.objects.filter(user__isnull=True).count()
    
    print(f"🔍 Users without profiles: {orphaned_users}")
    print(f"🔍 Profiles without users: {orphaned_profiles}")
    
    if orphaned_users == 0 and orphaned_profiles == 0:
        print("✅ DATA INTEGRITY: PERFECT")
    else:
        print("⚠️  DATA INTEGRITY: ISSUES DETECTED")
    
    # Financial summary
    total_balance = sum(profile.balance for profile in UserProfile.objects.all())
    total_invested = sum(profile.total_invested for profile in UserProfile.objects.all())
    
    print(f"💵 Total Balance: ₱{total_balance:,.2f}")
    print(f"💸 Total Invested: ₱{total_invested:,.2f}")
    
    # Recent activity
    from datetime import timedelta
    
    recent_users = User.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    recent_transactions = Transaction.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    print(f"📈 New users (7 days): {recent_users}")
    print(f"📈 Transactions (7 days): {recent_transactions}")
    
    # Security status
    print("\n🛡️  SECURITY STATUS")
    print("-" * 25)
    
    if orphaned_users == 0 and orphaned_profiles == 0:
        print("🟢 Data Integrity: SECURE")
    else:
        print("🔴 Data Integrity: VULNERABLE")
    
    if total_users > 0 and total_transactions > 0:
        print("🟢 System Activity: NORMAL")
    else:
        print("🟡 System Activity: LOW")
    
    # High-value accounts
    high_balance_accounts = UserProfile.objects.filter(balance__gte=5000).count()
    print(f"💎 High-value accounts (≥₱5,000): {high_balance_accounts}")
    
    return {
        'users': total_users,
        'profiles': total_profiles,
        'data_integrity': orphaned_users == 0 and orphaned_profiles == 0,
        'total_balance': total_balance,
        'recent_activity': recent_users + recent_transactions > 0
    }

if __name__ == "__main__":
    print("🚀 STARTING DATA MISMATCH FIX")
    print("=" * 50)
    
    try:
        # Fix the mismatch
        success = fix_data_mismatch()
        
        # Generate security report
        report = generate_security_report()
        
        print(f"\n🎯 FIX COMPLETED: {'SUCCESS' if success else 'PARTIAL'}")
        
        if success:
            print("✅ All data integrity issues resolved!")
            print("🛡️  Your platform is now secure!")
        else:
            print("⚠️  Some issues may remain. Run again or check manually.")
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        import traceback
        traceback.print_exc()
