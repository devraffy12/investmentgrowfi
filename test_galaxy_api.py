#!/usr/bin/env python3
"""
Test Galaxy API Integration
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/Users/raffy/OneDrive/Desktop/investment')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from payments.galaxy_api_service import galaxy_service
from decimal import Decimal

def test_galaxy_api():
    print("🧪 Testing Galaxy API Integration...")
    print(f"📋 Merchant ID: {galaxy_service.merchant_id}")
    print(f"🔑 Secret Key: {galaxy_service.secret_key[:20]}...")
    print(f"🌐 Base URL: {galaxy_service.base_url}")
    print()
    
    # Test deposit creation
    test_order_id = f"TEST_{int(time.time())}"
    test_amount = Decimal('100.00')
    
    print(f"🚀 Creating test deposit:")
    print(f"   Order ID: {test_order_id}")
    print(f"   Amount: ₱{test_amount}")
    print(f"   Payment Method: gcash")
    print()
    
    result = galaxy_service.create_deposit(
        amount=test_amount,
        order_id=test_order_id,
        payment_method='gcash',
        user_id=1
    )
    
    print("📥 Galaxy API Response:")
    import json
    print(json.dumps(result, indent=2, default=str))
    
    # Check if we got a redirect_url
    if result.get('redirect_url'):
        print(f"✅ Got redirect_url: {result['redirect_url']}")
    else:
        print("❌ No redirect_url in response")
    
    return result

if __name__ == "__main__":
    import time
    test_galaxy_api()
