#!/usr/bin/env python
"""
Enhanced test script for LA2568 API integration
Supports testing all available payment channels
"""
import requests
import hashlib
import json
import sys
from datetime import datetime

# Your LA2568 credentials
MERCHANT_ID = 'RodolfHitler'
SECRET_KEY = '86cb40fe1666b41eb0ad21577d66baef'
API_URL = 'https://cloud.la2568.site/api/transfer'

# Payment channel configurations from LA2568 support
PAYMENT_CHANNELS = {
    "gcash_qr": {
        'payment_type': '1',
        'bank_code': 'gcash',
        'name': 'GCash QR'
    },
    "gcash_h5": {
        'payment_type': '7',
        'bank_code': 'mya',
        'name': 'GCash H5 QRPH'
    },
    "paymaya": {
        'payment_type': '3',
        'bank_code': 'PMP',
        'name': 'PayMaya Direct'
    }
}

def test_la2568_api(channel="gcash_qr"):
    """Test LA2568 API with the specified channel"""
    if channel not in PAYMENT_CHANNELS:
        print(f"❌ Unknown payment channel: {channel}")
        print(f"Available channels: {', '.join(PAYMENT_CHANNELS.keys())}")
        return
    
    channel_config = PAYMENT_CHANNELS[channel]
    print(f"🚀 Testing LA2568 API Integration - {channel_config['name']}")
    print("=" * 50)
    
    # Generate a unique order ID for testing
    order_id = f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Prepare order data with the selected channel configuration
    order_data = {
        'merchant': MERCHANT_ID,
        'payment_type': channel_config['payment_type'],
        'amount': '100.00',  # Test amount
        'order_id': order_id,
        'bank_code': channel_config['bank_code'],
        'callback_url': 'http://localhost:8000/payment/callback/',
        'return_url': 'http://localhost:8000/payment/success/'
    }
    
    print(f"📝 Order Data: {order_data}")
    
    # Generate signature
    sorted_params = sorted(order_data.items())
    sign_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
    sign_string += f"&key={SECRET_KEY}"
    signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
    
    order_data['sign'] = signature
    
    print(f"🔐 Sign String: {sign_string}")
    print(f"🔐 Signature: {signature}")
    print(f"📤 Final Data: {order_data}")
    
    # Make API request
    try:
        print(f"\n📡 Sending request to: {API_URL}")
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.post(
            API_URL,
            data=order_data,
            headers=headers,
            timeout=30
        )
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        print(f"📥 Response Body: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ JSON Response: {json.dumps(result, indent=2)}")
                
                if result.get('status') == 1 or result.get('status') == '1':
                    print(f"✅ API call successful for {channel_config['name']}!")
                    payment_url = result.get('payment_url') or result.get('payurl')
                    if payment_url:
                        print(f"🔗 Payment URL: {payment_url}")
                    else:
                        print("❌ No payment URL in response")
                else:
                    error_msg = result.get('msg', result.get('message', 'Unknown error'))
                    print(f"❌ API Error: {error_msg}")
                    
                    # Check for whitelist error
                    if 'whitelist' in str(error_msg).lower():
                        print("\n🔒 WHITELIST ERROR DETECTED 🔒")
                        print("You need to contact LA2568 support to whitelist your IP/domain:")
                        print("1. Your current domain/IP is not in their whitelist")
                        print("2. Provide them with your production URL: https://investmentgrowfi.onrender.com")
                        print("3. Ask them to whitelist Render.com's IP addresses")
            except json.JSONDecodeError:
                print(f"❌ Non-JSON response: {response.text}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    # Get payment channel from command line args or use default
    channel = "gcash_qr"  # Default channel
    
    if len(sys.argv) > 1:
        channel = sys.argv[1]
    
    # Print available channels
    print("Available payment channels:")
    for key, config in PAYMENT_CHANNELS.items():
        print(f"  - {key}: {config['name']} (payment_type={config['payment_type']}, bank_code={config['bank_code']})")
    print()
    
    # Run test with specified channel
    test_la2568_api(channel)
