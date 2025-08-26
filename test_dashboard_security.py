#!/usr/bin/env python3
"""
Dashboard Security Test - Check if users can see each other's investments in dashboard
"""

import os
import sys
import django

# Setup Django
sys.path.append('c:\\Users\\raffy\\OneDrive\\Desktop\\investment')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from myproject.models import Investment, InvestmentPlan, UserProfile
from decimal import Decimal

def test_dashboard_security():
    """Test dashboard shows only user's own investments"""
    print("🔍 Testing Dashboard Investment Security...")
    
    # Create test users
    try:
        user1 = User.objects.get(username='testuser1')
    except User.DoesNotExist:
        user1 = User.objects.create_user(username='testuser1', password='test123')
        UserProfile.objects.get_or_create(user=user1, defaults={'phone_number': '09123456781'})
    
    try:
        user2 = User.objects.get(username='testuser2')
    except User.DoesNotExist:
        user2 = User.objects.create_user(username='testuser2', password='test123')
        UserProfile.objects.get_or_create(user=user2, defaults={'phone_number': '09123456782'})
    
    # Create test plan
    plan, created = InvestmentPlan.objects.get_or_create(
        name='Test Plan',
        defaults={
            'minimum_amount': Decimal('1000'),
            'maximum_amount': Decimal('10000'),
            'daily_return_rate': Decimal('5.0'),
            'duration_days': 30,
            'is_active': True
        }
    )
    
    # Create test investments with proper fields
    from django.utils import timezone
    
    investment1, created = Investment.objects.get_or_create(
        user=user1,
        plan=plan,
        amount=Decimal('5000'),
        defaults={
            'status': 'active',
            'daily_return': Decimal('250'),
            'total_return': Decimal('0'),
            'start_date': timezone.now(),
        }
    )
    
    investment2, created = Investment.objects.get_or_create(
        user=user2,
        plan=plan,
        amount=Decimal('3000'),
        defaults={
            'status': 'active',
            'daily_return': Decimal('150'),
            'total_return': Decimal('0'),
            'start_date': timezone.now(),
        }
    )
    
    print("✅ Created test investments:")
    print(f"   User1: ₱5,000 investment")
    print(f"   User2: ₱3,000 investment")
    
    # Test User1 dashboard access
    client = Client()
    client.login(username='testuser1', password='test123')
    
    print("\n🔍 Testing User1 dashboard access...")
    response = client.get('/dashboard/')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check if User1's investment appears (be more specific)
        import re
        user1_amount_pattern = r'\b5,?000(?:\.\d{2})?\b'
        user1_found = re.search(user1_amount_pattern, content)
        
        if user1_found:
            print(f"   ✅ User1 can see their own ₱5,000 investment")
        else:
            print("   ⚠️ User1 cannot see their own investment (might be empty)")
        
        # Check if User2's investment appears (be more specific)
        import re
        # Look for 3000 as a standalone number, not part of larger numbers
        user2_amount_pattern = r'\b3,?000(?:\.\d{2})?\b'
        user2_found = re.search(user2_amount_pattern, content)
        
        if user2_found:
            print(f"   ❌ SECURITY VIOLATION: User1 can see User2's ₱3,000 investment! Found: {user2_found.group()}")
            return False
        else:
            print("   ✅ User1 cannot see User2's investment")
            
        # Check for user2's username in content
        if 'testuser2' in content:
            print("   ❌ SECURITY VIOLATION: User1 can see User2's username!")
            return False
        else:
            print("   ✅ User1 cannot see User2's username")
    else:
        print(f"   ❌ Dashboard returned status {response.status_code}")
        return False
    
    # Test User2 dashboard access
    client.login(username='testuser2', password='test123')
    
    print("\n🔍 Testing User2 dashboard access...")
    response = client.get('/dashboard/')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check if User2's investment appears (be more specific)
        user2_amount_pattern = r'\b3,?000(?:\.\d{2})?\b'
        user2_found = re.search(user2_amount_pattern, content)
        
        if user2_found:
            print(f"   ✅ User2 can see their own ₱3,000 investment")
        else:
            print("   ⚠️ User2 cannot see their own investment (might be empty)")
        
        # Check if User1's investment appears (be more specific)
        user1_amount_pattern = r'\b5,?000(?:\.\d{2})?\b'
        user1_violation = re.search(user1_amount_pattern, content)
        
        if user1_violation:
            print(f"   ❌ SECURITY VIOLATION: User2 can see User1's ₱5,000 investment! Found: {user1_violation.group()}")
            return False
        else:
            print("   ✅ User2 cannot see User1's investment")
            
        # Check for user1's username in content
        if 'testuser1' in content:
            print("   ❌ SECURITY VIOLATION: User2 can see User1's username!")
            return False
        else:
            print("   ✅ User2 cannot see User1's username")
    else:
        print(f"   ❌ Dashboard returned status {response.status_code}")
        return False
    
    print("\n🎉 DASHBOARD SECURITY TEST PASSED!")
    print("   Users can only see their own investments in dashboard")
    return True

if __name__ == "__main__":
    test_dashboard_security()
