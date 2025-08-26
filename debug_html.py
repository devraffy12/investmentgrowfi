#!/usr/bin/env python3
"""
Debug HTML Content - Check exactly what's in the dashboard HTML
"""

import os
import sys
import django

sys.path.append('c:\\Users\\raffy\\OneDrive\\Desktop\\investment')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def debug_html_content():
    """Debug what's actually in the dashboard HTML"""
    print("🔍 Debugging Dashboard HTML Content...")
    
    # Get test users
    try:
        user1 = User.objects.get(username='testuser1')
        user2 = User.objects.get(username='testuser2')
    except User.DoesNotExist:
        print("❌ Test users not found")
        return
    
    # Test User1 dashboard
    client = Client()
    client.login(username='testuser1', password='test123')
    
    print(f"\n🔍 Testing User1 dashboard...")
    response = client.get('/dashboard/')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Search for numbers around investment amounts
        print("🔍 Searching for investment amounts in HTML...")
        
        # Look for 3000 or 3,000 (User2's investment)
        if '3000' in content:
            print("   ❌ Found '3000' in User1's dashboard!")
            # Find context around 3000
            import re
            matches = re.finditer(r'.{50}3000.{50}', content, re.IGNORECASE)
            for i, match in enumerate(matches):
                print(f"   Context {i+1}: ...{match.group()}...")
        elif '3,000' in content:
            print("   ❌ Found '3,000' in User1's dashboard!")
            import re
            matches = re.finditer(r'.{50}3,000.{50}', content, re.IGNORECASE)
            for i, match in enumerate(matches):
                print(f"   Context {i+1}: ...{match.group()}...")
        else:
            print("   ✅ No '3000' found in User1's dashboard")
        
        # Look for 5000 or 5,000 (User1's investment)
        if '5000' in content or '5,000' in content:
            print("   ✅ Found User1's '5000' investment in dashboard")
        else:
            print("   ⚠️ User1's investment not found in dashboard")
        
        # Look for testuser2 username
        if 'testuser2' in content:
            print("   ❌ Found 'testuser2' username in User1's dashboard!")
            import re
            matches = re.finditer(r'.{30}testuser2.{30}', content, re.IGNORECASE)
            for i, match in enumerate(matches):
                print(f"   Context {i+1}: ...{match.group()}...")
        else:
            print("   ✅ No 'testuser2' username found in User1's dashboard")
            
        # Save the HTML for manual inspection
        with open('user1_dashboard.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("   💾 Saved User1's dashboard HTML to 'user1_dashboard.html'")
        
    else:
        print(f"   ❌ Dashboard returned status {response.status_code}")

if __name__ == "__main__":
    debug_html_content()
