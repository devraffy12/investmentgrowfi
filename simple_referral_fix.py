#!/usr/bin/env python3
"""
Simple Firebase Referral Fix
Run this from the project root
"""

import os
import sys
import django

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# Configure Django
import django
from django.conf import settings
django.setup()

print("🔧 Starting Firebase Referral Fix...")

try:
    # Now import Django and Firebase components
    from datetime import datetime, timezone
    import firebase_admin
    from firebase_admin import credentials, db as firebase_db, firestore
    
    # Try to get Firebase app
    try:
        from myproject.firebase_app import get_firebase_app
        app = get_firebase_app()
        
        if hasattr(app, 'project_id') and app.project_id == "firebase-unavailable":
            print("❌ Firebase not available")
            sys.exit(1)
            
        print("✅ Firebase connected successfully")
        
    except Exception as firebase_error:
        print(f"❌ Firebase connection error: {firebase_error}")
        sys.exit(1)
    
    # Get Firebase references
    ref = firebase_db.reference('/', app=app)
    users_ref = ref.child('users')
    
    # Get all users
    print("📊 Getting all users from Firebase...")
    all_users = users_ref.get() or {}
    print(f"Found {len(all_users)} users")
    
    # Process referral system
    print("🔄 Processing referral data...")
    
    referral_summary = {}
    
    # First pass: collect all referral codes and initialize counters
    for user_key, user_data in all_users.items():
        if not user_data:
            continue
            
        referral_code = user_data.get('referral_code')
        phone_number = user_data.get('phone_number', '')
        
        if referral_code:
            referral_summary[referral_code] = {
                'phone_number': phone_number,
                'user_key': user_key,
                'total_referrals': 0,
                'active_referrals': 0,
                'team_volume': 0.0,
                'referral_earnings': 0.0
            }
    
    # Second pass: count referrals for each user
    for user_key, user_data in all_users.items():
        if not user_data:
            continue
            
        referred_by_code = user_data.get('referred_by_code')
        
        if referred_by_code and referred_by_code in referral_summary:
            balance = float(user_data.get('balance', 0.0))
            total_invested = float(user_data.get('total_invested', 0.0))
            
            # Count referral
            referral_summary[referred_by_code]['total_referrals'] += 1
            
            # Count active referrals (users with balance > 0 or investments > 0)
            if balance > 0 or total_invested > 0:
                referral_summary[referred_by_code]['active_referrals'] += 1
            
            # Add to team volume (balance + invested amount)
            referral_summary[referred_by_code]['team_volume'] += (balance + total_invested)
    
    # Third pass: calculate referral earnings
    for user_key, user_data in all_users.items():
        if not user_data:
            continue
            
        referral_code = user_data.get('referral_code')
        
        if referral_code and referral_code in referral_summary:
            transactions = user_data.get('transactions', {})
            referral_earnings = 0.0
            
            for tx_id, tx_data in transactions.items():
                if isinstance(tx_data, dict) and tx_data.get('type') == 'referral_bonus':
                    referral_earnings += float(tx_data.get('amount', 0.0))
            
            referral_summary[referral_code]['referral_earnings'] = referral_earnings
    
    # Update Firebase with corrected data
    print("🔄 Updating Firebase with corrected referral data...")
    
    update_count = 0
    for referral_code, stats in referral_summary.items():
        user_key = stats['user_key']
        
        # Update user's referral stats
        update_data = {
            'total_referrals': stats['total_referrals'],
            'active_referrals': stats['active_referrals'],
            'team_volume': stats['team_volume'],
            'referral_earnings': stats['referral_earnings'],
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
        
        try:
            users_ref.child(user_key).update(update_data)
            update_count += 1
            
            if stats['total_referrals'] > 0:
                print(f"✅ {stats['phone_number']} ({referral_code}): {stats['total_referrals']} referrals, ₱{stats['team_volume']:.2f} volume, ₱{stats['referral_earnings']:.2f} earnings")
        
        except Exception as e:
            print(f"❌ Error updating {referral_code}: {e}")
    
    print(f"\n🎉 Firebase referral fix completed!")
    print(f"✅ Updated {update_count} users")
    
    # Show summary of users with referrals
    users_with_referrals = [stats for stats in referral_summary.values() if stats['total_referrals'] > 0]
    print(f"📊 {len(users_with_referrals)} users have referrals")
    
    total_referrals = sum(stats['total_referrals'] for stats in referral_summary.values())
    total_volume = sum(stats['team_volume'] for stats in referral_summary.values())
    total_earnings = sum(stats['referral_earnings'] for stats in referral_summary.values())
    
    print(f"📈 System totals:")
    print(f"   Total referrals: {total_referrals}")
    print(f"   Total team volume: ₱{total_volume:.2f}")
    print(f"   Total referral earnings: ₱{total_earnings:.2f}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
