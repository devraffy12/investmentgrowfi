#!/usr/bin/env python3
"""
Quick Security Test - Check if our API fixes work
"""

import os
import sys
import django

# Setup Django
sys.path.append('c:\\Users\\raffy\\OneDrive\\Desktop\\investment')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

# Now test the views directly
from myproject.views import recent_investments_api, recent_activities_api, deposits_withdrawals_api
from django.test import RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.http import Http404
import json

def test_api_security():
    """Test if APIs properly filter by user"""
    print("🔍 Testing API Security Fixes...")
    
    factory = RequestFactory()
    
    # Create or get test users
    try:
        user1 = User.objects.get(username='testuser1')
    except User.DoesNotExist:
        user1 = User.objects.create_user(username='testuser1', password='test123')
    
    try:
        user2 = User.objects.get(username='testuser2')
    except User.DoesNotExist:
        user2 = User.objects.create_user(username='testuser2', password='test123')
    
    # Test 1: recent_investments_api with user1
    print("\n1. Testing recent_investments_api...")
    request = factory.get('/api/recent-investments/')
    request.user = user1
    
    try:
        response = recent_investments_api(request)
        if response.status_code == 200:
            data = json.loads(response.content)
            investments = data.get('investments', [])
            print(f"   ✅ User1 gets {len(investments)} investments")
            
            # Check if any belong to user2
            user2_found = any(inv.get('user_name') == 'testuser2' for inv in investments)
            if user2_found:
                print("   ❌ SECURITY ISSUE: User1 can see User2's investments!")
            else:
                print("   ✅ User1 can only see their own investments")
        else:
            print(f"   ⚠️ API returned status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: recent_activities_api with user1
    print("\n2. Testing recent_activities_api...")
    request = factory.get('/api/recent-activities/')
    request.user = user1
    
    try:
        response = recent_activities_api(request)
        if response.status_code == 200:
            data = json.loads(response.content)
            activities = data.get('activities', [])
            print(f"   ✅ User1 gets {len(activities)} activities")
            
            # Check if any belong to user2
            user2_found = any(act.get('user') == 'testuser2' for act in activities)
            if user2_found:
                print("   ❌ SECURITY ISSUE: User1 can see User2's activities!")
            else:
                print("   ✅ User1 can only see their own activities")
        else:
            print(f"   ⚠️ API returned status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: deposits_withdrawals_api with user1
    print("\n3. Testing deposits_withdrawals_api...")
    request = factory.get('/api/deposits-withdrawals/')
    request.user = user1
    
    try:
        response = deposits_withdrawals_api(request)
        if response.status_code == 200:
            data = json.loads(response.content)
            results = data.get('results', [])
            print(f"   ✅ User1 gets {len(results)} deposit/withdrawal records")
            
            # Check if any belong to user2
            user2_found = any(tx.get('user') == 'testuser2' for tx in results)
            if user2_found:
                print("   ❌ SECURITY ISSUE: User1 can see User2's transactions!")
            else:
                print("   ✅ User1 can only see their own transactions")
        else:
            print(f"   ⚠️ API returned status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Test with anonymous user
    print("\n4. Testing with anonymous user...")
    request = factory.get('/api/recent-investments/')
    request.user = AnonymousUser()
    
    try:
        response = recent_investments_api(request)
        print(f"   Anonymous user gets status {response.status_code}")
        if response.status_code in [302, 401, 403]:
            print("   ✅ Anonymous users properly blocked")
        else:
            print("   ❌ SECURITY ISSUE: Anonymous users can access data!")
    except Exception as e:
        print(f"   ✅ Anonymous user blocked with exception: {type(e).__name__}")
    
    print("\n🔐 Security test completed!")

if __name__ == "__main__":
    test_api_security()
