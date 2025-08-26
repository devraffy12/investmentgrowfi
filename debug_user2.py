#!/usr/bin/env python3
"""
Debug User2 Dashboard HTML
"""

import os
import sys
import django

sys.path.append('c:\\Users\\raffy\\OneDrive\\Desktop\\investment')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def debug_user2_html():
    """Debug User2's dashboard HTML"""
    print("🔍 Debugging User2 Dashboard HTML...")
    
    # Test User2 dashboard
    client = Client()
    client.login(username='testuser2', password='test123')
    
    response = client.get('/dashboard/')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Save User2's HTML
        with open('user2_dashboard.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("   💾 Saved User2's dashboard HTML to 'user2_dashboard.html'")
        
        # Search for 5000 patterns
        import re
        pattern = r'\b5,?000(?:\.\d{2})?\b'
        matches = re.finditer(pattern, content)
        
        print("🔍 Found 5000 patterns in User2's dashboard:")
        for i, match in enumerate(matches):
            start = max(0, match.start() - 50)
            end = min(len(content), match.end() + 50)
            context = content[start:end]
            print(f"   Match {i+1}: ...{context}...")
            print(f"   Position: {match.start()}-{match.end()}")
            print()

if __name__ == "__main__":
    debug_user2_html()
