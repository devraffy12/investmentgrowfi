#!/usr/bin/env python3
"""
Debug Dashboard Query - Check what data is being passed to template
"""

import os
import sys
import django

sys.path.append('c:\\Users\\raffy\\OneDrive\\Desktop\\investment')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from myproject.models import Investment, InvestmentPlan, UserProfile

def debug_dashboard_query():
    """Debug what data users see"""
    print("🔍 Debugging Dashboard Query...")
    
    # Get test users
    try:
        user1 = User.objects.get(username='testuser1')
        user2 = User.objects.get(username='testuser2')
    except User.DoesNotExist:
        print("❌ Test users not found. Run test_dashboard_security.py first")
        return
    
    print(f"\n👤 User1 ({user1.username}) investments:")
    user1_investments = Investment.objects.filter(user=user1, status='active')
    for inv in user1_investments:
        print(f"   ₱{inv.amount} - {inv.plan.name} - User: {inv.user.username}")
    
    print(f"\n👤 User2 ({user2.username}) investments:")
    user2_investments = Investment.objects.filter(user=user2, status='active')
    for inv in user2_investments:
        print(f"   ₱{inv.amount} - {inv.plan.name} - User: {inv.user.username}")
    
    print(f"\n🔍 ALL investments in database:")
    all_investments = Investment.objects.filter(status='active')
    for inv in all_investments:
        print(f"   ₱{inv.amount} - {inv.plan.name} - User: {inv.user.username}")
    
    print(f"\n🔍 Check if dashboard view is properly filtering...")
    
    # Simulate dashboard view query for user1
    from django.test import RequestFactory
    from myproject.views import dashboard
    
    factory = RequestFactory()
    request = factory.get('/dashboard/')
    request.user = user1
    
    # Get the active_investments queryset like dashboard view does
    active_investments = Investment.objects.filter(user=request.user, status='active')
    
    print(f"\n✅ Dashboard query for User1:")
    print(f"   Query: Investment.objects.filter(user={request.user.username}, status='active')")
    print(f"   Results: {active_investments.count()} investments")
    for inv in active_investments:
        print(f"     ₱{inv.amount} - {inv.plan.name} - User: {inv.user.username}")
    
    # Check for user2
    request.user = user2
    active_investments = Investment.objects.filter(user=request.user, status='active')
    
    print(f"\n✅ Dashboard query for User2:")
    print(f"   Query: Investment.objects.filter(user={request.user.username}, status='active')")
    print(f"   Results: {active_investments.count()} investments")
    for inv in active_investments:
        print(f"     ₱{inv.amount} - {inv.plan.name} - User: {inv.user.username}")

if __name__ == "__main__":
    debug_dashboard_query()
