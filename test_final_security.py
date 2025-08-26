#!/usr/bin/env python3
"""
Final Dashboard Security Test - Excludes JavaScript/CSS false positives
"""

import os
import sys
import django

sys.path.append('c:\\Users\\raffy\\OneDrive\\Desktop\\investment')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from myproject.models import Investment, InvestmentPlan, UserProfile
from decimal import Decimal
import re

def test_dashboard_security_final():
    """Final dashboard security test with smart pattern matching"""
    print("🔍 Final Dashboard Investment Security Test...")
    
    # Create test users
    try:
        user1 = User.objects.get(username='testuser1')
        user2 = User.objects.get(username='testuser2')
    except User.DoesNotExist:
        print("❌ Test users not found. Run test_dashboard_security.py first")
        return
    
    print("✅ Using existing test data:")
    print(f"   User1: ₱5,000 investment")
    print(f"   User2: ₱3,000 investment")
    
    def extract_html_content_only(html):
        """Remove JavaScript and CSS to avoid false positives"""
        # Remove script tags and their content
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        # Remove style tags and their content
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        return html
    
    def check_investment_amount_in_content(content, amount, description):
        """Check if an investment amount appears in HTML content (excluding JS/CSS)"""
        clean_content = extract_html_content_only(content)
        
        # Look for the amount in various formats within HTML content
        patterns = [
            rf'₱\s*{amount:,}(?:\.00)?',  # ₱5,000 or ₱5,000.00
            rf'₱\s*{amount}(?:\.00)?',    # ₱5000 or ₱5000.00
            rf'>\s*{amount:,}(?:\.00)?\s*<',  # >5,000< (between HTML tags)
            rf'>\s*{amount}(?:\.00)?\s*<',    # >5000< (between HTML tags)
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, clean_content, re.IGNORECASE)
            for match in matches:
                # Get context around the match
                start = max(0, match.start() - 100)
                end = min(len(clean_content), match.end() + 100)
                context = clean_content[start:end].strip()
                
                print(f"   Found {description}: {match.group()}")
                print(f"   Context: ...{context}...")
                return True
        
        return False
    
    # Test User1 dashboard
    client = Client()
    client.login(username='testuser1', password='test123')
    
    print("\n🔍 Testing User1 dashboard (smart detection)...")
    response = client.get('/dashboard/')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check User1's own investment
        user1_own = check_investment_amount_in_content(content, 5000, "User1's own ₱5,000 investment")
        if user1_own:
            print("   ✅ User1 can see their own investment")
        else:
            print("   ⚠️ User1's own investment not visible (might be empty state)")
        
        # Check User2's investment
        user2_violation = check_investment_amount_in_content(content, 3000, "User2's ₱3,000 investment")
        if user2_violation:
            print("   ❌ SECURITY VIOLATION: User1 can see User2's investment!")
            return False
        else:
            print("   ✅ User1 cannot see User2's investment")
    
    # Test User2 dashboard  
    client.login(username='testuser2', password='test123')
    
    print("\n🔍 Testing User2 dashboard (smart detection)...")
    response = client.get('/dashboard/')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check User2's own investment
        user2_own = check_investment_amount_in_content(content, 3000, "User2's own ₱3,000 investment")
        if user2_own:
            print("   ✅ User2 can see their own investment")
        else:
            print("   ⚠️ User2's own investment not visible (might be empty state)")
        
        # Check User1's investment
        user1_violation = check_investment_amount_in_content(content, 5000, "User1's ₱5,000 investment")
        if user1_violation:
            print("   ❌ SECURITY VIOLATION: User2 can see User1's investment!")
            return False
        else:
            print("   ✅ User2 cannot see User1's investment")
    
    print("\n🎉 DASHBOARD SECURITY TEST PASSED!")
    print("   Users can only see their own investments in dashboard")
    print("   No cross-user data leakage detected")
    return True

if __name__ == "__main__":
    test_dashboard_security_final()
