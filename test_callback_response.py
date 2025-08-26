#!/usr/bin/env python
"""Test script to verify Galaxy API callback response format"""

import os
import django
from django.test import RequestFactory
from django.conf import settings

# Setup Django
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from payments.views import galaxy_callback_view

def test_callback_response():
    """Test that callback returns 'success' with 200 status"""
    factory = RequestFactory()
    
    # Test with POST data (typical Galaxy callback)
    post_data = {
        'status': 'success',
        'amount': '100.00',
        'txnid': 'test123',
        'signature': 'test_signature'
    }
    
    request = factory.post('/api/galaxy/callback/', post_data)
    response = galaxy_callback_view(request)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: '{response.content.decode()}'")
    print(f"Content Type: {response.get('Content-Type', 'Not set')}")
    
    # Check if it matches what Galaxy expects
    if response.status_code == 200 and response.content.decode() == 'success':
        print("✅ Callback response is correct!")
        return True
    else:
        print("❌ Callback response is incorrect!")
        return False

if __name__ == '__main__':
    test_callback_response()
