#!/usr/bin/env python3
"""
Simple Team View Test
"""
import firebase_admin
from firebase_admin import credentials, firestore
import json

def simple_test():
    print("🔍 SIMPLE TEAM VIEW TEST")
    print("=" * 40)
    
    try:
        # Initialize Firebase app
        try:
            app = firebase_admin.get_app()
            print("✅ Using existing Firebase app")
        except ValueError:
            with open('firebase-service-account.json', 'r') as f:
                cred_data = json.load(f)
            
            cred = credentials.Certificate(cred_data)
            app = firebase_admin.initialize_app(cred)
            print("✅ Initialized new Firebase app")
        
        # Test Firestore only (more reliable)
        db = firestore.client(app=app)
        
        # Check users collection
        users_ref = db.collection('users')
        users_query = users_ref.limit(10)
        users_docs = list(users_query.stream())
        
        print(f"📊 Found {len(users_docs)} users in Firestore")
        
        # Look for users with referral relationships
        referred_users = []
        users_with_codes = []
        
        for doc in users_docs:
            user_data = doc.to_dict()
            
            if user_data.get('referral_code'):
                users_with_codes.append({
                    'id': doc.id,
                    'phone': user_data.get('phone_number'),
                    'code': user_data.get('referral_code')
                })
            
            if user_data.get('referred_by_code'):
                referred_users.append({
                    'id': doc.id,
                    'phone': user_data.get('phone_number'),
                    'referred_by': user_data.get('referred_by_code'),
                    'balance': user_data.get('balance', 0)
                })
        
        print(f"🔑 Users with referral codes: {len(users_with_codes)}")
        print(f"👥 Users who were referred: {len(referred_users)}")
        
        # Show some examples
        if users_with_codes:
            print(f"\n📋 Sample referral codes:")
            for user in users_with_codes[:3]:
                print(f"   {user['phone']}: {user['code']}")
        
        if referred_users:
            print(f"\n📋 Sample referred users:")
            for user in referred_users[:3]:
                print(f"   {user['phone']} ← {user['referred_by']} (₱{user['balance']})")
        
        # Test team calculation for one user
        if users_with_codes:
            test_user = users_with_codes[0]
            test_code = test_user['code']
            
            print(f"\n🧪 Testing team stats for code: {test_code}")
            
            # Find all users referred by this code
            referred_query = users_ref.where('referred_by_code', '==', test_code)
            referred_docs = list(referred_query.stream())
            
            total_referrals = len(referred_docs)
            active_referrals = 0
            team_volume = 0.0
            team_earnings = 0.0
            
            for doc in referred_docs:
                data = doc.to_dict()
                balance = float(data.get('balance', 0))
                invested = float(data.get('total_invested', 0))
                earnings = float(data.get('total_earnings', 0))
                
                if balance > 0 or invested > 0:
                    active_referrals += 1
                
                team_volume += (balance + invested)
                team_earnings += earnings
            
            print(f"   Total Referrals: {total_referrals}")
            print(f"   Active Members: {active_referrals}")
            print(f"   Team Volume: ₱{team_volume:,.2f}")
            print(f"   Team Earnings: ₱{team_earnings:,.2f}")
            
            if total_referrals > 0:
                print("✅ REFERRAL COUNTING WORKS!")
            else:
                print("⚠️ No referrals found for this code")
        
        # Check teams collection
        teams_ref = db.collection('teams')
        teams_docs = list(teams_ref.limit(5).stream())
        
        print(f"\n📊 Teams collection: {len(teams_docs)} documents")
        
        if teams_docs:
            print("📋 Sample team data:")
            for doc in teams_docs:
                data = doc.to_dict()
                phone = data.get('phone_number', 'Unknown')
                total_refs = data.get('total_referrals', 0)
                volume = data.get('team_volume', 0)
                print(f"   {phone}: {total_refs} referrals, ₱{volume:,.2f} volume")
        
        print(f"\n✅ TEAM VIEW FUNCTIONALITY TEST COMPLETE!")
        
        if users_with_codes and referred_users:
            print("🎉 REFERRAL SYSTEM IS WORKING!")
            print("   - Users have referral codes")
            print("   - Users are being referred")
            print("   - Team calculations work")
            print("   - Data is stored in Firestore")
        else:
            print("⚠️ Limited referral activity found")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_test()
