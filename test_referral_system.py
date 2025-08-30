#!/usr/bin/env python3
"""
Test script to analyze and fix the referral system
"""
import sys
import os

# Add the project directory to Python path
project_dir = os.path.join(os.path.dirname(__file__), 'myproject')
sys.path.insert(0, project_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

import django
django.setup()

from myproject.firebase_config import get_firebase_app, FIREBASE_AVAILABLE
from django.contrib.auth.models import User
from myproject.models import UserProfile, ReferralCommission
from decimal import Decimal
import json

def test_referral_system():
    print("🔍 REFERRAL SYSTEM ANALYSIS")
    print("=" * 50)
    
    # 1. Check Django users and referrals
    print("\n📊 DJANGO DATA:")
    total_users = User.objects.count()
    total_profiles = UserProfile.objects.count()
    total_commissions = ReferralCommission.objects.count()
    
    print(f"   Total Django users: {total_users}")
    print(f"   Total user profiles: {total_profiles}")
    print(f"   Total referral commissions: {total_commissions}")
    
    # Show some referral codes
    profiles_with_codes = UserProfile.objects.exclude(referral_code__isnull=True).exclude(referral_code__exact='')
    print(f"   Profiles with referral codes: {profiles_with_codes.count()}")
    for profile in profiles_with_codes[:5]:
        print(f"     - {profile.phone_number}: {profile.referral_code}")
    
    # 2. Check Firebase data if available
    if FIREBASE_AVAILABLE:
        try:
            print("\n🔥 FIREBASE DATA:")
            app = get_firebase_app()
            
            # Try Firebase Realtime Database
            try:
                from firebase_admin import db as firebase_db
                ref = firebase_db.reference('/', app)
                users_ref = ref.child('users')
                firebase_users = users_ref.get() or {}
                
                print(f"   Total Firebase RTDB users: {len(firebase_users)}")
                
                # Count users with referral codes and referred users
                users_with_codes = 0
                referred_users = 0
                total_balance = 0
                
                for user_key, user_data in firebase_users.items():
                    if not user_data:
                        continue
                    
                    if user_data.get('referral_code'):
                        users_with_codes += 1
                    
                    if user_data.get('referred_by_code'):
                        referred_users += 1
                        
                    balance = float(user_data.get('balance', 0))
                    total_balance += balance
                
                print(f"   Users with referral codes: {users_with_codes}")
                print(f"   Users who were referred: {referred_users}")
                print(f"   Total user balances: ₱{total_balance:,.2f}")
                
                # Show some example referral relationships
                print("\n   Sample referral relationships:")
                for user_key, user_data in list(firebase_users.items())[:10]:
                    if user_data and user_data.get('referred_by_code'):
                        phone = user_data.get('phone_number', user_key)
                        ref_code = user_data.get('referred_by_code')
                        balance = user_data.get('balance', 0)
                        print(f"     - {phone} referred by {ref_code}, balance: ₱{balance}")
                
            except Exception as rtdb_error:
                print(f"   ❌ RTDB Error: {rtdb_error}")
            
            # Try Firestore
            try:
                from firebase_admin import firestore
                db = firestore.client()
                
                # Check users collection
                users_docs = db.collection('users').limit(10).get()
                print(f"   Firestore users sample: {len(users_docs)} docs")
                
                # Check profiles collection
                profiles_docs = db.collection('profiles').limit(10).get()
                print(f"   Firestore profiles sample: {len(profiles_docs)} docs")
                
                # Check teams collection
                teams_docs = db.collection('teams').limit(10).get()
                print(f"   Firestore teams sample: {len(teams_docs)} docs")
                
            except Exception as firestore_error:
                print(f"   ❌ Firestore Error: {firestore_error}")
                
        except Exception as firebase_error:
            print(f"   ❌ Firebase Error: {firebase_error}")
    else:
        print("\n❌ Firebase not available")
    
    print("\n" + "=" * 50)
    print("✅ Analysis complete!")

def fix_referral_counting():
    """Fix referral counting issues"""
    print("\n🔧 FIXING REFERRAL COUNTING...")
    
    if not FIREBASE_AVAILABLE:
        print("❌ Firebase not available for fixing")
        return
    
    try:
        app = get_firebase_app()
        from firebase_admin import db as firebase_db, firestore
        
        # Get Firebase refs
        ref = firebase_db.reference('/', app)
        users_ref = ref.child('users')
        db = firestore.client()
        
        # Get all Firebase users
        firebase_users = users_ref.get() or {}
        print(f"Processing {len(firebase_users)} Firebase users...")
        
        # Process each user to fix their referral data
        for user_key, user_data in firebase_users.items():
            if not user_data:
                continue
                
            phone_number = user_data.get('phone_number', '')
            referral_code = user_data.get('referral_code', '')
            
            if not referral_code:
                continue
            
            print(f"\n🔍 Processing user {phone_number} with code {referral_code}")
            
            # Count actual referrals for this user
            actual_referrals = []
            total_team_volume = 0
            total_team_earnings = 0
            
            for other_key, other_data in firebase_users.items():
                if not other_data or other_key == user_key:
                    continue
                
                # Check if this user was referred by current user
                if other_data.get('referred_by_code') == referral_code:
                    other_phone = other_data.get('phone_number', '')
                    other_balance = float(other_data.get('balance', 0))
                    other_invested = float(other_data.get('total_invested', 0))
                    other_earnings = float(other_data.get('total_earnings', 0))
                    
                    actual_referrals.append({
                        'phone': other_phone,
                        'balance': other_balance,
                        'invested': other_invested,
                        'earnings': other_earnings
                    })
                    
                    total_team_volume += (other_balance + other_invested)
                    total_team_earnings += other_earnings
            
            # Update user's referral counts
            actual_count = len(actual_referrals)
            active_count = sum(1 for r in actual_referrals if r['balance'] > 0 or r['invested'] > 0)
            
            # Calculate referral earnings from transactions
            referral_earnings = 0
            transactions = user_data.get('transactions', {})
            for tx_id, tx_data in transactions.items():
                if isinstance(tx_data, dict) and tx_data.get('type') == 'referral_bonus':
                    referral_earnings += float(tx_data.get('amount', 0))
            
            # Update Firebase user data
            updates = {
                'total_referrals': actual_count,
                'active_referrals': active_count,
                'team_volume': total_team_volume,
                'team_earnings': total_team_earnings,
                'referral_earnings': referral_earnings,
                'last_referral_update': firebase_db.ServerValue.TIMESTAMP
            }
            
            users_ref.child(user_key).update(updates)
            
            # Also update Firestore team document
            team_data = {
                'uid': user_key,
                'phone_number': phone_number,
                'referral_code': referral_code,
                'total_referrals': actual_count,
                'active_referrals': active_count,
                'total_earnings': total_team_earnings,
                'team_volume': total_team_volume,
                'referral_earnings': referral_earnings,
                'referrals': actual_referrals,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            db.collection('teams').document(user_key).set(team_data, merge=True)
            
            print(f"✅ Updated {phone_number}: {actual_count} referrals, ₱{total_team_volume:,.2f} volume")
        
        print("\n✅ Referral counting fix complete!")
        
    except Exception as e:
        print(f"❌ Error fixing referral counting: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_referral_system()
    fix_referral_counting()
    
    # Run analysis again to see the results
    print("\n" + "="*50)
    print("🔍 POST-FIX ANALYSIS")
    test_referral_system()
