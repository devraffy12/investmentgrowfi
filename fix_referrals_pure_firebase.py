#!/usr/bin/env python3
"""
Pure Firebase Referral Fix Script
"""
import sys
import os
import django

# Setup Django
project_dir = os.path.join(os.path.dirname(__file__), 'myproject')
sys.path.insert(0, project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject.firebase_config import get_firebase_app, FIREBASE_AVAILABLE

def fix_all_referral_data():
    """Fix all users' referral data in Firebase"""
    if not FIREBASE_AVAILABLE:
        print("❌ Firebase not available")
        return
    
    print("🔧 FIXING ALL REFERRAL DATA IN FIREBASE...")
    
    try:
        from firebase_admin import db as firebase_db, firestore
        
        app = get_firebase_app()
        ref = firebase_db.reference('/', app)
        users_ref = ref.child('users')
        db = firestore.client()
        
        # Get all Firebase users
        all_users = users_ref.get() or {}
        print(f"Processing {len(all_users)} Firebase users...")
        
        # Process each user
        for user_key, user_data in all_users.items():
            if not user_data:
                continue
                
            phone_number = user_data.get('phone_number', '')
            referral_code = user_data.get('referral_code', '')
            
            if not referral_code:
                # Generate referral code if missing
                import random
                import string
                while True:
                    new_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                    # Check uniqueness
                    code_exists = any(
                        other_data and other_data.get('referral_code') == new_code
                        for other_key, other_data in all_users.items()
                        if other_data and other_key != user_key
                    )
                    if not code_exists:
                        referral_code = new_code
                        break
                
                # Update user with new referral code
                users_ref.child(user_key).update({'referral_code': referral_code})
                print(f"🔑 Generated referral code {referral_code} for {phone_number}")
            
            # Count actual referrals
            actual_referrals = []
            total_team_volume = 0
            total_team_earnings = 0
            active_count = 0
            
            for other_key, other_data in all_users.items():
                if not other_data or other_key == user_key:
                    continue
                
                # Check if referred by this user
                if other_data.get('referred_by_code') == referral_code:
                    other_phone = other_data.get('phone_number', '')
                    other_balance = float(other_data.get('balance', 0))
                    other_invested = float(other_data.get('total_invested', 0))
                    other_earnings = float(other_data.get('total_earnings', 0))
                    
                    # Calculate from transactions if main fields are zero
                    transactions = other_data.get('transactions', {})
                    if other_invested == 0 or other_earnings == 0:
                        tx_invested = 0
                        tx_earnings = 0
                        
                        for tx_id, tx_data in transactions.items():
                            if isinstance(tx_data, dict) and tx_data.get('status') == 'completed':
                                tx_type = tx_data.get('type', '')
                                tx_amount = float(tx_data.get('amount', 0))
                                
                                if tx_type in ['investment', 'deposit', 'add_funds']:
                                    tx_invested += tx_amount
                                elif tx_type in ['daily_earning', 'profit', 'earning']:
                                    tx_earnings += tx_amount
                        
                        other_invested = max(other_invested, tx_invested)
                        other_earnings = max(other_earnings, tx_earnings)
                    
                    # Check if active
                    is_active = other_balance > 0 or other_invested > 0 or len(transactions) > 1
                    if is_active:
                        active_count += 1
                    
                    actual_referrals.append({
                        'phone': other_phone,
                        'balance': other_balance,
                        'invested': other_invested,
                        'earnings': other_earnings,
                        'active': is_active
                    })
                    
                    total_team_volume += (other_balance + other_invested)
                    total_team_earnings += other_earnings
            
            # Calculate referral earnings
            referral_earnings = 0
            transactions = user_data.get('transactions', {})
            for tx_id, tx_data in transactions.items():
                if isinstance(tx_data, dict) and tx_data.get('type') == 'referral_bonus':
                    referral_earnings += float(tx_data.get('amount', 0))
            
            # Update Firebase RTDB
            rtdb_updates = {
                'referral_code': referral_code,
                'total_referrals': len(actual_referrals),
                'active_referrals': active_count,
                'team_volume': total_team_volume,
                'team_earnings': total_team_earnings,
                'referral_earnings': referral_earnings,
                'last_referral_fix': firebase_db.ServerValue.TIMESTAMP
            }
            
            users_ref.child(user_key).update(rtdb_updates)
            
            # Update Firestore team document
            team_data = {
                'uid': user_key,
                'phone_number': phone_number,
                'referral_code': referral_code,
                'total_referrals': len(actual_referrals),
                'active_referrals': active_count,
                'total_earnings': total_team_earnings,
                'team_volume': total_team_volume,
                'referral_earnings': referral_earnings,
                'referrals': actual_referrals,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            db.collection('teams').document(user_key).set(team_data, merge=True)
            
            if len(actual_referrals) > 0:
                print(f"✅ {phone_number}: {len(actual_referrals)} referrals, {active_count} active, ₱{total_team_volume:,.2f} volume")
        
        print("✅ All referral data fixed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_all_referral_data()
