#!/usr/bin/env python
"""
Complete Maya Payment Flow Debug - Check exact error happening
"""
import sys
import os
import json
import requests
from decimal import Decimal

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
import django
django.setup()

from payments.views import GalaxyPaymentService

def debug_complete_maya_flow():
    """Debug complete Maya payment flow to identify exact issue"""
    
    print("🔍 COMPLETE MAYA PAYMENT FLOW DEBUG")
    print("=" * 60)
    
    galaxy = GalaxyPaymentService()
    
    # Test PayMaya Direct payment with exact current configuration
    print("1️⃣ Testing Galaxy API Call")
    print("-" * 30)
    
    try:
        result = galaxy.create_payment(
            amount=Decimal('300.00'),
            order_id="debug_maya_flow_001",
            bank_code='PMP',  # PayMaya Direct
            payment_type='3',
            callback_url="https://investmentgrowfi.onrender.com/api/callback/",
            return_url="https://investmentgrowfi.onrender.com/deposit/success/",
            mobile_number="09919067713"  # CloudPay test number
        )
        
        print(f"✅ Galaxy API Response:")
        print(json.dumps(result, indent=2))
        print()
        
        if result.get('status') == '1':
            redirect_url = result.get('redirect_url')
            print(f"2️⃣ Testing Maya Redirect URL")
            print("-" * 30)
            print(f"🔗 Redirect URL: {redirect_url}")
            
            if redirect_url:
                try:
                    # Test accessing the Maya payment page
                    print("📡 Making request to Maya payment page...")
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    
                    response = requests.get(redirect_url, headers=headers, timeout=15, allow_redirects=True)
                    
                    print(f"📊 HTTP Status Code: {response.status_code}")
                    print(f"📍 Final URL: {response.url}")
                    print(f"📋 Response Headers: {dict(list(response.headers.items())[:5])}")  # First 5 headers
                    print()
                    
                    # Check response content for errors
                    content = response.text.lower()
                    
                    # Common error patterns
                    error_patterns = [
                        'wrong mobile',
                        'wrong username', 
                        'wrong account',
                        'incorrect',
                        'invalid',
                        'error',
                        'failed',
                        'cashier'
                    ]
                    
                    found_errors = []
                    for pattern in error_patterns:
                        if pattern in content:
                            found_errors.append(pattern)
                    
                    if found_errors:
                        print(f"❌ ERROR PATTERNS FOUND: {found_errors}")
                        print()
                        print("📄 Response Content (first 1000 chars):")
                        print("-" * 40)
                        print(response.text[:1000])
                        print()
                        print("🎯 CONCLUSION: Error is on Maya payment page side")
                        print("💡 SOLUTION: User needs to enter correct Maya mobile number on payment page")
                    else:
                        print("✅ No obvious errors found in Maya payment page")
                        print("📄 Response looks normal - payment page loaded successfully")
                        
                except requests.RequestException as e:
                    print(f"❌ Error accessing Maya payment page: {e}")
                    
        else:
            print(f"❌ Galaxy API Error: {result.get('message', 'Unknown error')}")
            print("🔧 This is a Galaxy API configuration issue")
            
    except Exception as e:
        print(f"💥 Exception in Galaxy API call: {e}")
        
    print("\n" + "=" * 60)
    print("🎯 DIAGNOSTIC SUMMARY:")
    print("• If Galaxy API returns status=1: API integration is working")
    print("• If Maya redirect loads: Galaxy→Maya handoff is working")  
    print("• If error appears on Maya page: User input validation issue")
    print("• If Galaxy API fails: Our code/signature issue")

if __name__ == "__main__":
    debug_complete_maya_flow()
