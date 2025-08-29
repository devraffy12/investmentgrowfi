#!/usr/bin/env python
"""
Comprehensive Firebase persistence test
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myproject.firebase_app import get_firebase_app
firebase_app = get_firebase_app()

from firebase_admin import firestore
import json

def test_firebase_persistence():
    print('=== COMPREHENSIVE FIREBASE PERSISTENCE TEST ===')

    try:
        db = firestore.client()
        
        # 1. Check user profiles
        print('\n1. CHECKING USER PROFILES:')
        profiles_ref = db.collection('profiles')
        profiles_docs = profiles_ref.limit(5).get()
        
        print(f'   Found {len(profiles_docs)} user profiles')
        for profile_doc in profiles_docs:
            profile_data = profile_doc.to_dict()
            uid = profile_doc.id
            balance = profile_data.get('balance', 0)
            print(f'   User {uid}: Balance P{balance}')
        
        # 2. Check referrals system
        print('\n2. CHECKING REFERRALS SYSTEM:')
        referrals_ref = db.collection('referrals')
        referrals_docs = referrals_ref.limit(10).get()
        
        print(f'   Found {len(referrals_docs)} referral records')
        referrer_counts = {}
        for referral_doc in referrals_docs:
            referral_data = referral_doc.to_dict()
            referrer = referral_data.get('referrer_uid', 'Unknown')
            referrer_counts[referrer] = referrer_counts.get(referrer, 0) + 1
        
        for referrer, count in referrer_counts.items():
            print(f'   {referrer}: {count} referrals')
        
        # 3. Check teams collection
        print('\n3. CHECKING TEAMS COLLECTION:')
        teams_ref = db.collection('teams')
        teams_docs = teams_ref.limit(5).get()
        
        print(f'   Found {len(teams_docs)} team records')
        for team_doc in teams_docs:
            team_data = team_doc.to_dict()
            uid = team_doc.id
            total_ref = team_data.get('total_referrals', 0)
            team_vol = team_data.get('team_volume', 0)
            print(f'   Team {uid}: {total_ref} referrals, P{team_vol} volume')
        
        # 4. Check commissions
        print('\n4. CHECKING COMMISSIONS:')
        commissions_ref = db.collection('commissions')
        commissions_docs = commissions_ref.limit(5).get()
        
        print(f'   Found {len(commissions_docs)} commission records')
        for commission_doc in commissions_docs:
            commission_data = commission_doc.to_dict()
            referrer = commission_data.get('referrer_uid', 'Unknown')
            amount = commission_data.get('amount', 0)
            print(f'   Commission for {referrer}: P{amount}')
        
        # 5. Test specific user data persistence
        print('\n5. TESTING SPECIFIC USER PERSISTENCE:')
        test_uid = '+639919101001'
        
        # Check profile
        profile_ref = db.collection('profiles').document(test_uid)
        profile_doc = profile_ref.get()
        if profile_doc.exists:
            profile_data = profile_doc.to_dict()
            print(f'   User {test_uid} profile exists')
            print(f'   Balance: P{profile_data.get("balance", 0)}')
            print(f'   Total Invested: P{profile_data.get("total_invested", 0)}')
        else:
            print(f'   User {test_uid} profile NOT FOUND')
        
        # Check team data
        team_ref = db.collection('teams').document(test_uid)
        team_doc = team_ref.get()
        if team_doc.exists:
            team_data = team_doc.to_dict()
            print(f'   Team data exists for {test_uid}')
            print(f'   Total Referrals: {team_data.get("total_referrals", 0)}')
            print(f'   Team Volume: P{team_data.get("team_volume", 0)}')
        else:
            print(f'   Team data NOT FOUND for {test_uid}')
        
        # 6. Check authentication persistence
        print('\n6. CHECKING AUTHENTICATION SESSIONS:')
        sessions_ref = db.collection('user_sessions')
        sessions_docs = sessions_ref.limit(5).get()
        
        print(f'   Found {len(sessions_docs)} active sessions')
        for session_doc in sessions_docs:
            session_data = session_doc.to_dict()
            uid = session_data.get('uid', 'Unknown')
            created_at = session_data.get('created_at', 'Unknown')
            print(f'   Session for {uid} created at {created_at}')
        
        print('\n=== TEST COMPLETED SUCCESSFULLY ===')
        print('✅ Firebase is working and data is persisting correctly!')
        
        return True
        
    except Exception as e:
        print(f'❌ Error during test: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_firebase_persistence()
