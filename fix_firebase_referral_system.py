#!/usr/bin/env python3
"""
Fix Firebase Referral System
This script will fix the referral counting and ensure proper data sync
"""

import os
import sys
import django
from datetime import datetime, timezone

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

try:
    import firebase_admin
    from firebase_admin import credentials, db as firebase_db, firestore
    from myproject.firebase_app import get_firebase_app
    from django.conf import settings
    
    print("🔧 Starting Firebase Referral System Fix...")
    
    def fix_firebase_referral_system():
        """Fix and synchronize Firebase referral data"""
        try:
            # Get Firebase app
            app = get_firebase_app()
            if hasattr(app, 'project_id') and app.project_id == "firebase-unavailable":
                print("❌ Firebase unavailable")
                return False
            
            # Get Firebase references
            ref = firebase_db.reference('/', app=app)
            users_ref = ref.child('users')
            db_firestore = firestore.client()
            
            print("✅ Firebase connections established")
            
            # Get all users from Firebase
            all_users = users_ref.get() or {}
            print(f"📊 Found {len(all_users)} users in Firebase")
            
            # Process each user to fix referral data
            referral_stats = {}
            
            for user_key, user_data in all_users.items():
                if not user_data:
                    continue
                    
                phone_number = user_data.get('phone_number', '')
                referral_code = user_data.get('referral_code', '')
                referred_by_code = user_data.get('referred_by_code', '')
                
                if not referral_code:
                    # Generate missing referral code
                    import random
                    import string
                    while True:
                        new_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                        # Check if code exists
                        code_exists = any(
                            data and data.get('referral_code') == new_code
                            for data in all_users.values()
                            if data
                        )
                        if not code_exists:
                            referral_code = new_code
                            users_ref.child(user_key).update({'referral_code': referral_code})
                            print(f"✅ Generated referral code for {phone_number}: {referral_code}")
                            break
                
                # Initialize referral stats
                if referral_code not in referral_stats:
                    referral_stats[referral_code] = {
                        'phone_number': phone_number,
                        'user_key': user_key,
                        'total_referrals': 0,
                        'active_referrals': 0,
                        'team_volume': 0.0,
                        'referral_earnings': 0.0,
                        'referrals_list': []
                    }
            
            # Count referrals for each user
            for user_key, user_data in all_users.items():
                if not user_data:
                    continue
                    
                referred_by_code = user_data.get('referred_by_code', '')
                if referred_by_code and referred_by_code in referral_stats:
                    phone_number = user_data.get('phone_number', '')
                    balance = float(user_data.get('balance', 0.0))
                    total_invested = float(user_data.get('total_invested', 0.0))
                    total_earnings = float(user_data.get('total_earnings', 0.0))
                    
                    # Count this referral
                    referral_stats[referred_by_code]['total_referrals'] += 1
                    
                    # Check if active (has balance or investments)
                    is_active = balance > 0 or total_invested > 0
                    if is_active:
                        referral_stats[referred_by_code]['active_referrals'] += 1
                    
                    # Add to team volume
                    referral_stats[referred_by_code]['team_volume'] += total_invested + balance
                    
                    # Add to referrals list
                    referral_stats[referred_by_code]['referrals_list'].append({
                        'phone_number': phone_number,
                        'balance': balance,
                        'total_invested': total_invested,
                        'is_active': is_active,
                        'date_joined': user_data.get('date_joined', '')
                    })
                    
                    print(f"📈 {phone_number} referred by {referred_by_code}: Balance=₱{balance}, Invested=₱{total_invested}")
            
            # Calculate referral earnings from transactions
            for user_key, user_data in all_users.items():
                if not user_data:
                    continue
                    
                referral_code = user_data.get('referral_code', '')
                if referral_code in referral_stats:
                    transactions = user_data.get('transactions', {})
                    referral_earnings = 0.0
                    
                    for tx_id, tx_data in transactions.items():
                        if isinstance(tx_data, dict) and tx_data.get('type') == 'referral_bonus':
                            referral_earnings += float(tx_data.get('amount', 0.0))
                    
                    referral_stats[referral_code]['referral_earnings'] = referral_earnings
            
            # Update Firebase with corrected data
            print("🔄 Updating Firebase with corrected referral data...")
            
            for referral_code, stats in referral_stats.items():
                user_key = stats['user_key']
                
                # Update user's referral stats in Firebase
                updates = {
                    'total_referrals': stats['total_referrals'],
                    'active_referrals': stats['active_referrals'],
                    'team_volume': stats['team_volume'],
                    'referral_earnings': stats['referral_earnings'],
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }
                
                users_ref.child(user_key).update(updates)
                
                # Also update Firestore for consistency
                try:
                    doc_ref = db_firestore.collection('users').document(user_key)
                    doc_ref.set(updates, merge=True)
                    
                    # Update team collection
                    team_ref = db_firestore.collection('teams').document(user_key)
                    team_data = {
                        'uid': user_key,
                        'phone_number': stats['phone_number'],
                        'referral_code': referral_code,
                        'total_referrals': stats['total_referrals'],
                        'active_referrals': stats['active_referrals'],
                        'total_earnings': stats['referral_earnings'],
                        'team_volume': stats['team_volume'],
                        'referral_earnings': stats['referral_earnings'],
                        'referrals': stats['referrals_list'],
                        'updated_at': firestore.SERVER_TIMESTAMP
                    }
                    team_ref.set(team_data, merge=True)
                    
                except Exception as firestore_error:
                    print(f"⚠️ Firestore update error for {referral_code}: {firestore_error}")
                
                print(f"✅ Updated {referral_code}: {stats['total_referrals']} referrals, ₱{stats['team_volume']} volume, ₱{stats['referral_earnings']} earnings")
            
            print("🎉 Firebase referral system fix completed!")
            return True
            
        except Exception as e:
            print(f"❌ Error fixing Firebase referral system: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_referral_system():
        """Test the referral system after fix"""
        try:
            app = get_firebase_app()
            ref = firebase_db.reference('/', app=app)
            users_ref = ref.child('users')
            
            # Get some sample data
            all_users = users_ref.get() or {}
            
            print("📊 Referral System Test Results:")
            print("=" * 50)
            
            for user_key, user_data in list(all_users.items())[:5]:  # Test first 5 users
                if not user_data:
                    continue
                    
                phone = user_data.get('phone_number', '')
                referral_code = user_data.get('referral_code', '')
                total_referrals = user_data.get('total_referrals', 0)
                team_volume = user_data.get('team_volume', 0.0)
                referral_earnings = user_data.get('referral_earnings', 0.0)
                
                print(f"👤 {phone} ({referral_code})")
                print(f"   Total Referrals: {total_referrals}")
                print(f"   Team Volume: ₱{team_volume}")
                print(f"   Referral Earnings: ₱{referral_earnings}")
                print()
            
        except Exception as e:
            print(f"❌ Test error: {e}")
    
    # Run the fix
    if fix_firebase_referral_system():
        test_referral_system()
    
except Exception as e:
    print(f"❌ Setup error: {e}")
    import traceback
    traceback.print_exc()
