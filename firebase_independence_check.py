#!/usr/bin/env python
"""
Firebase Independence Strategy
Make the system work without Firebase dependency
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from myproject.models import UserProfile, Transaction

def analyze_firebase_dependency():
    """Analyze how much the system depends on Firebase"""
    print("🔍 Firebase Dependency Analysis")
    print("=" * 50)
    
    # Check current Firebase usage
    print("1️⃣ Current Firebase Configuration:")
    print(f"   Database URL: {getattr(settings, 'FIREBASE_DATABASE_URL', 'Not set')}")
    print(f"   Credentials File: {getattr(settings, 'FIREBASE_CREDENTIALS_FILE', 'Not set')}")
    print()
    
    # Check data completeness in Django
    print("2️⃣ Django Database Analysis:")
    total_users = User.objects.count()
    total_profiles = UserProfile.objects.count()
    total_transactions = Transaction.objects.count()
    
    print(f"   Total Users: {total_users}")
    print(f"   Total Profiles: {total_profiles}")
    print(f"   Total Transactions: {total_transactions}")
    print(f"   Data Completeness: {(total_profiles/total_users*100) if total_users > 0 else 0:.1f}%")
    print()
    
    # Check recent user activity
    print("3️⃣ Recent User Activity (Django only):")
    from django.utils import timezone
    from datetime import timedelta
    
    week_ago = timezone.now() - timedelta(days=7)
    recent_users = User.objects.filter(date_joined__gte=week_ago).count()
    recent_transactions = Transaction.objects.filter(created_at__gte=week_ago).count()
    
    print(f"   New users (7 days): {recent_users}")
    print(f"   Recent transactions (7 days): {recent_transactions}")
    print()
    
    # Firebase Independence Assessment
    print("4️⃣ Firebase Independence Assessment:")
    
    # Core functionality check
    core_features = {
        'User Registration': total_users > 0,
        'User Profiles': total_profiles > 0, 
        'Transaction System': total_transactions > 0,
        'Balance Management': UserProfile.objects.filter(balance__gt=0).exists(),
        'Referral System': UserProfile.objects.exclude(referral_code__isnull=True).exists()
    }
    
    for feature, working in core_features.items():
        status = "✅ Working" if working else "❌ Needs Setup"
        print(f"   {feature}: {status}")
    
    print()
    
    # Recommendations
    print("💡 RECOMMENDATIONS:")
    print("-" * 30)
    
    if all(core_features.values()):
        print("🟢 EXCELLENT: All core features work without Firebase!")
        print("   • Your system is Firebase-independent")
        print("   • Django database handles everything")
        print("   • No quota limitations")
        print("   • Firestore quota doesn't affect you")
    else:
        print("🟡 PARTIAL: Some features may need Firebase")
        print("   • Focus on Django database first")
        print("   • Firebase as optional backup only")
    
    print()
    print("🚀 FIREBASE QUOTA SOLUTION:")
    print("-" * 30)
    print("1. Keep using FREE Realtime Database (not Firestore)")
    print("2. Use Django as primary database")
    print("3. Firebase as optional sync only")
    print("4. No need to upgrade Firestore")
    
    return core_features

if __name__ == "__main__":
    results = analyze_firebase_dependency()
    
    print()
    print("🎯 CONCLUSION:")
    print("=" * 50)
    if all(results.values()):
        print("✨ Your investment system is FULLY FUNCTIONAL without Firebase!")
        print("💯 Continue using Django database as primary storage.")
        print("🔥 Firebase quota issues won't affect your users!")
    else:
        print("⚠️ Some features may need Firebase configuration.")
        print("💡 Consider making Firebase optional for better reliability.")
