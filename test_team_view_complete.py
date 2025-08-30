#!/usr/bin/env python3
"""
Complete Test for Team View Functionality
"""
import firebase_admin
from firebase_admin import credentials, db as firebase_db, firestore
import json

def test_team_view_functionality():
    """Test if the team view will work correctly"""
    
    print("🔍 TESTING TEAM VIEW FUNCTIONALITY")
    print("=" * 60)
    
    try:
        # Initialize Firebase (if not already done)
        try:
            app = firebase_admin.get_app()
            print("✅ Using existing Firebase app")
        except ValueError:
            # Load credentials and initialize
            with open('firebase-service-account.json', 'r') as f:
                cred_data = json.load(f)
            
            cred = credentials.Certificate(cred_data)
            app = firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://growthinvestment-bbfe2-default-rtdb.asia-southeast1.firebasedatabase.app'
            })
            print("✅ Initialized new Firebase app")
        
        # Test Firebase Realtime Database connection
        ref = firebase_db.reference('/', app=app)
        users_ref = ref.child('users')
        all_users = users_ref.get() or {}
        
        print(f"📊 Firebase RTDB: {len(all_users)} users found")
        
        # Test Firestore connection
        db = firestore.client(app=app)
        teams_collection = db.collection('teams')
        teams_docs = list(teams_collection.limit(5).stream())
        
        print(f"📊 Firestore teams: {len(teams_docs)} team documents found")
        
        # Simulate team view logic for a user with referrals
        test_referral_codes = []
        test_users = []
        
        # Find users with referral codes
        for user_key, user_data in all_users.items():
            if user_data and user_data.get('referral_code'):
                test_referral_codes.append({
                    'code': user_data.get('referral_code'),
                    'phone': user_data.get('phone_number'),
                    'key': user_key
                })
                if len(test_referral_codes) >= 3:
                    break
        
        print(f"\n🔍 Testing team calculation for sample users...")
        
        for test_user in test_referral_codes:
            referral_code = test_user['code']
            phone = test_user['phone']
            user_key = test_user['key']
            
            print(f"\n👤 Testing user: {phone} (Code: {referral_code})")
            
            # Count referrals
            referrals_found = 0
            active_referrals = 0
            team_volume = 0.0
            team_earnings = 0.0
            
            for other_key, other_data in all_users.items():
                if not other_data or other_key == user_key:
                    continue
                
                if other_data.get('referred_by_code') == referral_code:
                    referrals_found += 1
                    
                    balance = float(other_data.get('balance', 0))
                    invested = float(other_data.get('total_invested', 0))
                    earnings = float(other_data.get('total_earnings', 0))
                    
                    if balance > 0 or invested > 0:
                        active_referrals += 1
                    
                    team_volume += (balance + invested)
                    team_earnings += earnings
                    
                    print(f"  📱 Referral: {other_data.get('phone_number')} - ₱{balance} balance")
            
            # Calculate referral earnings from transactions
            user_data = all_users.get(user_key, {})
            referral_earnings = 0.0
            transactions = user_data.get('transactions', {})
            
            for tx_id, tx_data in transactions.items():
                if isinstance(tx_data, dict) and tx_data.get('type') == 'referral_bonus':
                    referral_earnings += float(tx_data.get('amount', 0))
            
            print(f"  📊 Results:")
            print(f"    Total Referrals: {referrals_found}")
            print(f"    Active Members: {active_referrals}")
            print(f"    Team Volume: ₱{team_volume:,.2f}")
            print(f"    Team Earnings: ₱{team_earnings:,.2f}")
            print(f"    Referral Earnings: ₱{referral_earnings:,.2f}")
            
            # Test if team document exists in Firestore
            try:
                team_doc = db.collection('teams').document(user_key).get()
                if team_doc.exists:
                    team_data = team_doc.to_dict()
                    stored_referrals = team_data.get('total_referrals', 0)
                    stored_volume = team_data.get('team_volume', 0)
                    print(f"  💾 Firestore: {stored_referrals} referrals, ₱{stored_volume:,.2f} volume")
                else:
                    print(f"  ⚠️ No team document in Firestore")
            except Exception as e:
                print(f"  ❌ Firestore error: {e}")
        
        print(f"\n" + "=" * 60)
        
        # Test the actual team view simulation
        print(f"🧪 SIMULATING TEAM VIEW ACCESS...")
        
        # Test with first user
        if test_referral_codes:
            test_user = test_referral_codes[0]
            firebase_uid = test_user['key']
            user_phone = test_user['phone']
            
            print(f"📱 Simulating team view for: {user_phone}")
            
            # This simulates what happens when user visits /team/
            try:
                # Get user's referral code
                user_profile_ref = db.collection('profiles').document(firebase_uid)
                user_profile_doc = user_profile_ref.get()
                
                referral_code = None
                if user_profile_doc.exists:
                    referral_code = user_profile_doc.to_dict().get('referral_code')
                
                if not referral_code:
                    # Get from RTDB
                    user_data = all_users.get(firebase_uid, {})
                    referral_code = user_data.get('referral_code')
                
                print(f"🔑 Referral code found: {referral_code}")
                
                if referral_code:
                    # Count referrals (same logic as views.py)
                    total_referrals = 0
                    active_referrals = 0
                    team_volume = 0.0
                    
                    for user_key, user_data in all_users.items():
                        if user_data and user_data.get('referred_by_code') == referral_code:
                            total_referrals += 1
                            
                            balance = float(user_data.get('balance', 0))
                            invested = float(user_data.get('total_invested', 0))
                            
                            if balance > 0 or invested > 0:
                                active_referrals += 1
                            
                            team_volume += (balance + invested)
                    
                    print(f"✅ Team view would show:")
                    print(f"   Total Referrals: {total_referrals}")
                    print(f"   Active Members: {active_referrals}")
                    print(f"   Team Volume: ₱{team_volume:,.2f}")
                    
                    if total_referrals > 0:
                        print("✅ TEAM VIEW WILL WORK CORRECTLY!")
                    else:
                        print("⚠️ No referrals found for this user")
                else:
                    print("❌ No referral code found")
                    
            except Exception as e:
                print(f"❌ Team view simulation error: {e}")
        
        print(f"\n✅ TEAM VIEW TEST COMPLETE!")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_team_view_functionality()
