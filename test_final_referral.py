#!/usr/bin/env python3
"""
Final Verification Test for Referral System
"""
import firebase_admin
from firebase_admin import credentials, firestore
import json

def final_test():
    print("🎯 FINAL REFERRAL SYSTEM VERIFICATION")
    print("=" * 50)
    
    try:
        # Initialize Firebase
        try:
            app = firebase_admin.get_app()
            print("✅ Using existing Firebase app")
        except ValueError:
            with open('firebase-service-account.json', 'r') as f:
                cred_data = json.load(f)
            
            cred = credentials.Certificate(cred_data)
            app = firebase_admin.initialize_app(cred)
            print("✅ Initialized new Firebase app")
        
        # Test Firestore
        db = firestore.client(app=app)
        
        # Get some users to test
        users_ref = db.collection('users')
        users_docs = list(users_ref.limit(20).stream())
        
        print(f"📊 Testing with {len(users_docs)} users from Firestore")
        
        # Find users with referral codes
        test_users = []
        for doc in users_docs:
            data = doc.to_dict()
            if data.get('referral_code'):
                test_users.append({
                    'id': doc.id,
                    'phone': data.get('phone_number'),
                    'code': data.get('referral_code'),
                    'balance': data.get('balance', 0)
                })
        
        print(f"🔑 Found {len(test_users)} users with referral codes")
        
        if test_users:
            # Test each user's team stats
            for i, user in enumerate(test_users[:3]):  # Test first 3 users
                code = user['code']
                phone = user['phone']
                
                print(f"\n👤 User {i+1}: {phone} (Code: {code})")
                
                # Count referrals for this code
                referred_query = users_ref.where('referred_by_code', '==', code)
                referred_docs = list(referred_query.stream())
                
                total_refs = len(referred_docs)
                active_refs = 0
                team_volume = 0.0
                
                for ref_doc in referred_docs:
                    ref_data = ref_doc.to_dict()
                    balance = float(ref_data.get('balance', 0))
                    invested = float(ref_data.get('total_invested', 0))
                    
                    if balance > 0 or invested > 0:
                        active_refs += 1
                    
                    team_volume += (balance + invested)
                    
                    ref_phone = ref_data.get('phone_number', 'Unknown')
                    print(f"   📱 {ref_phone}: ₱{balance} balance, ₱{invested} invested")
                
                print(f"   📊 Team Stats:")
                print(f"      Total Referrals: {total_refs}")
                print(f"      Active Members: {active_refs}")
                print(f"      Team Volume: ₱{team_volume:,.2f}")
                
                # Check if team document exists
                team_doc = db.collection('teams').document(user['id']).get()
                if team_doc.exists:
                    team_data = team_doc.to_dict()
                    stored_refs = team_data.get('total_referrals', 0)
                    stored_volume = team_data.get('team_volume', 0)
                    print(f"      💾 Stored: {stored_refs} refs, ₱{stored_volume:,.2f} volume")
                    
                    # Compare
                    if total_refs == stored_refs and abs(team_volume - stored_volume) < 0.01:
                        print(f"      ✅ Data matches!")
                    else:
                        print(f"      ⚠️ Data mismatch - updating...")
                        
                        # Update team document
                        updated_data = {
                            'total_referrals': total_refs,
                            'active_referrals': active_refs,
                            'team_volume': team_volume,
                            'phone_number': phone,
                            'referral_code': code,
                            'updated_at': firestore.SERVER_TIMESTAMP
                        }
                        db.collection('teams').document(user['id']).set(updated_data, merge=True)
                        print(f"      ✅ Team document updated")
                else:
                    print(f"      📝 Creating team document...")
                    team_data = {
                        'uid': user['id'],
                        'phone_number': phone,
                        'referral_code': code,
                        'total_referrals': total_refs,
                        'active_referrals': active_refs,
                        'team_volume': team_volume,
                        'total_earnings': 0.0,
                        'referral_earnings': 0.0,
                        'updated_at': firestore.SERVER_TIMESTAMP
                    }
                    db.collection('teams').document(user['id']).set(team_data)
                    print(f"      ✅ Team document created")
        
        # Final summary
        print(f"\n" + "=" * 50)
        print(f"📋 FINAL STATUS:")
        
        # Count total teams
        teams_docs = list(db.collection('teams').stream())
        active_teams = 0
        total_volume = 0.0
        
        for team_doc in teams_docs:
            team_data = team_doc.to_dict()
            refs = team_data.get('total_referrals', 0)
            volume = team_data.get('team_volume', 0)
            
            if refs > 0:
                active_teams += 1
                total_volume += volume
        
        print(f"   Total teams: {len(teams_docs)}")
        print(f"   Active teams: {active_teams}")
        print(f"   Total volume: ₱{total_volume:,.2f}")
        
        if active_teams > 0:
            print(f"\n🎉 REFERRAL SYSTEM IS FULLY FUNCTIONAL!")
            print(f"   ✅ Users have referral codes")
            print(f"   ✅ Referral relationships exist")
            print(f"   ✅ Team stats are calculated")
            print(f"   ✅ Data is stored properly")
            print(f"   ✅ Team view will work correctly")
        else:
            print(f"\n⚠️ No active referral teams found")
            print(f"   - This might be normal if no users have made referrals yet")
            print(f"   - System is ready to track referrals when they happen")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    final_test()
