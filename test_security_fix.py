#!/usr/bin/env python3
"""
Security Test Script for Investment Platform
Tests if user data isolation is working properly
"""

import os
import sys
import django
import requests
from django.test import Client
from django.contrib.auth.models import User

# Add the project path
sys.path.append('c:\\Users\\raffy\\OneDrive\\Desktop\\investment')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from myproject.models import Investment, Transaction, UserProfile, InvestmentPlan

def test_user_data_isolation():
    """Test that users can only see their own data"""
    print("🔒 Testing User Data Isolation...")
    
    # Create test users
    try:
        user1 = User.objects.get(username='testuser1')
    except User.DoesNotExist:
        user1 = User.objects.create_user(username='testuser1', password='testpass123')
        UserProfile.objects.get_or_create(user=user1, defaults={'phone_number': '09123456781'})
    
    try:
        user2 = User.objects.get(username='testuser2') 
    except User.DoesNotExist:
        user2 = User.objects.create_user(username='testuser2', password='testpass123')
        UserProfile.objects.get_or_create(user=user2, defaults={'phone_number': '09123456782'})
    
    # Create test plan if needed
    plan, created = InvestmentPlan.objects.get_or_create(
        name='Test Plan',
        defaults={
            'minimum_amount': 1000,
            'maximum_amount': 10000,
            'daily_return_rate': 5.0,
            'duration_days': 30,
            'is_active': True
        }
    )
    
    # Create test investments for each user
    investment1 = Investment.objects.get_or_create(
        user=user1, 
        plan=plan, 
        amount=5000,
        defaults={'status': 'active'}
    )[0]
    
    investment2 = Investment.objects.get_or_create(
        user=user2, 
        plan=plan, 
        amount=3000,
        defaults={'status': 'active'}
    )[0]
    
    print(f"✅ Created test data:")
    print(f"   User1 investment: {investment1.amount}")
    print(f"   User2 investment: {investment2.amount}")
    
    # Test Django Client (simulates logged-in requests)
    client = Client()
    
    # Test User 1 access
    client.login(username='testuser1', password='testpass123')
    
    print("\n🔍 Testing User1 API access...")
    
    # Test recent_investments_api
    response = client.get('/api/recent-investments/')
    if response.status_code == 200:
        data = response.json()
        investments = data.get('investments', [])
        print(f"   recent_investments_api: {len(investments)} items returned")
        
        # Check if any investment belongs to user2
        user2_data_found = any(inv.get('user_name') == 'testuser2' for inv in investments)
        if user2_data_found:
            print("   ❌ SECURITY VIOLATION: User1 can see User2's investments!")
            return False
        else:
            print("   ✅ User1 can only see their own investments")
    else:
        print(f"   ❌ API returned status {response.status_code}")
        return False
    
    # Test recent_activities_api
    response = client.get('/api/recent-activities/')
    if response.status_code == 200:
        data = response.json()
        activities = data.get('activities', [])
        print(f"   recent_activities_api: {len(activities)} items returned")
        
        # Check if any activity belongs to user2
        user2_activity_found = any(act.get('user') == 'testuser2' for act in activities)
        if user2_activity_found:
            print("   ❌ SECURITY VIOLATION: User1 can see User2's activities!")
            return False
        else:
            print("   ✅ User1 can only see their own activities")
    else:
        print(f"   ❌ API returned status {response.status_code}")
    
    # Test deposits_withdrawals_api  
    response = client.get('/api/deposits-withdrawals/')
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        print(f"   deposits_withdrawals_api: {len(results)} items returned")
        
        # Check if any transaction belongs to user2
        user2_transaction_found = any(tx.get('user') == 'testuser2' for tx in results)
        if user2_transaction_found:
            print("   ❌ SECURITY VIOLATION: User1 can see User2's transactions!")
            return False
        else:
            print("   ✅ User1 can only see their own transactions")
    else:
        print(f"   ❌ API returned status {response.status_code}")
    
    print("\n🔍 Testing User2 API access...")
    
    # Test User 2 access
    client.login(username='testuser2', password='testpass123')
    
    response = client.get('/api/recent-investments/')
    if response.status_code == 200:
        data = response.json()
        investments = data.get('investments', [])
        print(f"   recent_investments_api: {len(investments)} items returned")
        
        # Check if any investment belongs to user1
        user1_data_found = any(inv.get('user_name') == 'testuser1' for inv in investments)
        if user1_data_found:
            print("   ❌ SECURITY VIOLATION: User2 can see User1's investments!")
            return False
        else:
            print("   ✅ User2 can only see their own investments")
    
    print("\n✅ ALL SECURITY TESTS PASSED!")
    print("   Users can only access their own data")
    return True

def test_unauthenticated_access():
    """Test that unauthenticated users cannot access APIs"""
    print("\n🚫 Testing Unauthenticated Access...")
    
    client = Client()
    
    # Test without login
    apis_to_test = [
        '/api/recent-investments/',
        '/api/recent-activities/', 
        '/api/deposits-withdrawals/',
        '/api/private/deposits-withdrawals/',
    ]
    
    for api in apis_to_test:
        response = client.get(api)
        if response.status_code == 302:  # Redirect to login
            print(f"   ✅ {api}: Properly redirects to login")
        elif response.status_code == 401:  # Unauthorized
            print(f"   ✅ {api}: Returns 401 Unauthorized")
        elif response.status_code == 403:  # Forbidden
            print(f"   ✅ {api}: Returns 403 Forbidden")
        else:
            print(f"   ❌ {api}: Allows access without authentication! Status: {response.status_code}")
            return False
    
    print("   ✅ All APIs properly require authentication")
    return True

if __name__ == "__main__":
    print("🔐 Starting Security Tests for Investment Platform\n")
    
    try:
        test1_passed = test_user_data_isolation()
        test2_passed = test_unauthenticated_access()
        
        if test1_passed and test2_passed:
            print("\n🎉 ALL SECURITY TESTS PASSED!")
            print("   The platform is secure - users can only see their own data")
        else:
            print("\n💥 SECURITY TESTS FAILED!")
            print("   There are still security vulnerabilities!")
            
    except Exception as e:
        print(f"\n💥 Error running tests: {e}")
        import traceback
        traceback.print_exc()
