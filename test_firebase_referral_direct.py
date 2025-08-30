"""
Quick Firebase referral system test - Pure Firebase approach
"""

def test_firebase_referral_locally():
    """Test Firebase referral system without Django"""
    
    print("🔥 TESTING PURE FIREBASE REFERRAL SYSTEM")
    print("=" * 50)
    
    try:
        # Import Firebase directly
        import firebase_admin
        from firebase_admin import credentials, db as firebase_db
        import json
        import os
        
        # Try to load Firebase credentials
        cred_file = "firebase-service-account.json"
        if not os.path.exists(cred_file):
            print("❌ Firebase credentials file not found")
            return
        
        # Initialize Firebase if not already done
        try:
            app = firebase_admin.get_app()
            print("✅ Using existing Firebase app")
        except ValueError:
            cred = credentials.Certificate(cred_file)
            app = firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://investment-6d6f7-default-rtdb.firebaseio.com/'
            })
            print("✅ Initialized new Firebase app")
        
        # Get database reference
        ref = firebase_db.reference('/')
        users_ref = ref.child('users')
        
        # Get all users
        all_users = users_ref.get() or {}
        print(f"📊 Total users in Firebase: {len(all_users)}")
        
        if len(all_users) == 0:
            print("❌ No users found in Firebase")
            return
        
        # Analyze referral system
        users_with_codes = 0
        referred_users = 0
        referral_relationships = []
        total_balances = 0
        
        print("\n🔍 Analyzing referral data...")
        
        for user_key, user_data in all_users.items():
            if not user_data:
                continue
            
            phone = user_data.get('phone_number', user_key)
            balance = float(user_data.get('balance', 0))
            total_balances += balance
            
            # Check if user has referral code
            if user_data.get('referral_code'):
                users_with_codes += 1
            
            # Check if user was referred
            referred_by_code = user_data.get('referred_by_code')
            if referred_by_code:
                referred_users += 1
                referral_relationships.append({
                    'phone': phone,
                    'referred_by': referred_by_code,
                    'balance': balance,
                    'user_key': user_key
                })
        
        print(f"✅ Users with referral codes: {users_with_codes}")
        print(f"✅ Users who were referred: {referred_users}")
        print(f"💰 Total user balances: ₱{total_balances:,.2f}")
        
        if referral_relationships:
            print(f"\n📋 Referral relationships found:")
            for rel in referral_relationships[:10]:  # Show first 10
                print(f"  📱 {rel['phone']} ← referred by {rel['referred_by']} (₱{rel['balance']})")
        
        # Test team calculation for a specific user
        if referral_relationships:
            print(f"\n🔍 Testing team calculation...")
            
            # Find a user who has referrals
            referrer_codes = {}
            for rel in referral_relationships:
                code = rel['referred_by']
                if code not in referrer_codes:
                    referrer_codes[code] = []
                referrer_codes[code].append(rel)
            
            # Show team stats for users with referrals
            for ref_code, referrals in referrer_codes.items():
                if len(referrals) > 0:
                    total_team_balance = sum(r['balance'] for r in referrals)
                    active_members = sum(1 for r in referrals if r['balance'] > 0)
                    
                    print(f"  🏆 Code {ref_code}:")
                    print(f"    Total Referrals: {len(referrals)}")
                    print(f"    Active Members: {active_members}")
                    print(f"    Team Volume: ₱{total_team_balance:,.2f}")
        
        print(f"\n✅ REFERRAL SYSTEM STATUS: {'WORKING' if referred_users > 0 else 'NO REFERRALS YET'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_firebase_referral_locally()
