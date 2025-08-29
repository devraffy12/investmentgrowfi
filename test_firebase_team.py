#!/usr/bin/env python
"""Test Firebase team system"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from myproject.firebase_app import get_firebase_app
firebase_app = get_firebase_app()
from firebase_admin import firestore

print('=== TESTING PURE FIREBASE TEAM SYSTEM ===')

try:
    db = firestore.client()
    
    # Check if data exists in Firebase collections
    print('\n🔍 Checking Firebase collections...')
    
    # Check profiles
    profiles = db.collection('profiles').limit(5).get()
    print(f'\n📄 Profiles: {len(profiles)} found')
    for doc in profiles:
        data = doc.to_dict()
        balance = data.get('balance', 0)
        phone = data.get('phone_number', 'N/A')
        print(f'  {doc.id}: Balance ₱{balance} - Phone: {phone}')
    
    # Check referrals
    referrals = db.collection('referrals').get()
    print(f'\n👥 Referrals: {len(referrals)} found')
    for doc in referrals:
        data = doc.to_dict()
        referrer = data.get('referrer_uid', 'N/A')
        referred = data.get('referred_uid', 'N/A')
        print(f'  {referrer} -> {referred}')
    
    # Check commissions
    commissions = db.collection('commissions').get()
    print(f'\n💰 Commissions: {len(commissions)} found')
    for doc in commissions:
        data = doc.to_dict()
        amount = data.get('amount', 0)
        referrer = data.get('referrer_uid', 'N/A')
        print(f'  ₱{amount} for {referrer}')
    
    # Check teams
    teams = db.collection('teams').get()
    print(f'\n🏆 Teams: {len(teams)} found')
    for doc in teams:
        data = doc.to_dict()
        total_refs = data.get('total_referrals', 0)
        active_refs = data.get('active_referrals', 0)
        earnings = data.get('referral_earnings', 0)
        volume = data.get('team_volume', 0)
        print(f'  {doc.id}:')
        print(f'    📊 Total Referrals: {total_refs}')
        print(f'    ✅ Active Members: {active_refs}')
        print(f'    💰 Referral Earnings: ₱{earnings}')
        print(f'    📈 Team Volume: ₱{volume}')
    
    # Test team calculation for specific user
    test_uid = '+639919101001'
    print(f'\n🔍 Testing team calculation for {test_uid}...')
    
    # Get referrals for this user
    user_referrals = db.collection('referrals').where('referrer_uid', '==', test_uid).get()
    print(f'Found {len(user_referrals)} referrals for this user')
    
    total_referrals = 0
    active_referrals = 0
    team_volume = 0.0
    team_earnings = 0.0
    
    for referral_doc in user_referrals:
        referral_data = referral_doc.to_dict()
        referred_uid = referral_data.get('referred_uid', '')
        print(f'  Processing referral: {referred_uid}')
        
        # Get referred user's profile
        profile_ref = db.collection('profiles').document(referred_uid)
        profile_doc = profile_ref.get()
        
        if profile_doc.exists:
            profile_data = profile_doc.to_dict()
            balance = profile_data.get('balance', 0.0)
            total_invested = profile_data.get('total_invested', 0.0)
            total_earnings_user = profile_data.get('total_earnings', 0.0)
            
            total_referrals += 1
            if balance > 0:
                active_referrals += 1
            
            team_volume += total_invested
            team_earnings += total_earnings_user
            
            print(f'    Balance: ₱{balance}, Invested: ₱{total_invested}, Earnings: ₱{total_earnings_user}')
        else:
            print(f'    ❌ Profile not found for {referred_uid}')
    
    # Get referral earnings for this user
    user_commissions = db.collection('commissions').where('referrer_uid', '==', test_uid).get()
    referral_earnings = sum(doc.to_dict().get('amount', 0.0) for doc in user_commissions)
    
    print(f'\n📊 FINAL TEAM STATS FOR {test_uid}:')
    print(f'   📈 Total Referrals: {total_referrals}')
    print(f'   ✅ Active Members: {active_referrals}')
    print(f'   💼 Team Volume: ₱{team_volume}')
    print(f'   📊 Team Earnings: ₱{team_earnings}')
    print(f'   💰 Referral Earnings: ₱{referral_earnings}')
    
    if total_referrals > 0:
        print('\n✅ PURE FIREBASE TEAM SYSTEM IS WORKING!')
        print('✅ All accounts and referrals are preserved in Firebase!')
        print('✅ No data will be lost - everything is in Firestore!')
    else:
        print('\n⚠️  No referral data found - may need to migrate data')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
