#!/usr/bin/env python
"""
Test GCash H5 QRPH channel that's now working
"""
import requests
import json
import hashlib

def test_gcash_h5_qrph():
    """Test GCash H5 QRPH channel specifically"""
    
    print("🧪 TESTING GCASH H5 QRPH CHANNEL")
    print("=" * 50)
    print("📢 CloudPay Status: GCash H5 QRPH channel - Payin & Payout NORMAL✅")
    print()
    
    # GCash H5 QRPH parameters
    params = {
        'merchant': 'RodolfHitler',
        'payment_type': '7',  # GCash H5 QRPH
        'amount': '300.00',
        'order_id': 'gcash_h5_test_001',
        'bank_code': 'mya',  # GCash H5 QRPH bank code
        'customer_bank_card_account': '09919067713',
        'callback_url': 'https://investmentgrowfi.onrender.com/api/callback/',
        'return_url': 'https://investmentgrowfi.onrender.com/deposit/success/'
    }
    
    # Generate signature (exclude customer_bank_card_account)
    signature_params = {k: v for k, v in params.items() if k != 'customer_bank_card_account'}
    ordered_keys = sorted(signature_params.keys())
    query_string = '&'.join([f"{k}={signature_params[k]}" for k in ordered_keys])
    secret_key = '86cb40fe1666b41eb0ad21577d66baef'
    sign_string = f"{query_string}&key={secret_key}"
    signature = hashlib.md5(sign_string.encode()).hexdigest().lower()
    
    params['sign'] = signature
    
    print("📤 GCash H5 QRPH Request:")
    for key, value in params.items():
        if key != 'sign':
            print(f"   {key}: {value}")
    print(f"   sign: {signature}")
    print()
    
    try:
        response = requests.post(
            'https://cloud.la2568.site/api/transfer',
            data=params,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        result = response.json()
        print(f"📤 API Response:")
        print(json.dumps(result, indent=2))
        
        if result.get('status') == '1':
            print("\n✅ GCASH H5 QRPH SUCCESS!")
            print("🎉 Channel is working as confirmed by CloudPay")
            redirect_url = result.get('redirect_url')
            qr_url = result.get('qrcode_url')
            gcash_qr_url = result.get('gcash_qr_url')
            
            if redirect_url:
                print(f"🔗 Redirect URL: {redirect_url}")
            if qr_url:
                print(f"📱 QR Code URL: {qr_url}")
            if gcash_qr_url:
                print(f"💚 GCash QR URL: {gcash_qr_url}")
                
        elif result.get('status') == '0':
            message = result.get('message', '')
            if 'maintenance' in message.lower():
                print("\n⚠️  GCASH H5 QRPH MAINTENANCE")
                print("🔧 Channel temporarily unavailable")
            else:
                print(f"\n❌ GCASH H5 QRPH ERROR: {message}")
        
    except Exception as e:
        print(f"💥 Exception: {e}")
        
    print("\n" + "=" * 50)
    print("🎯 NEXT STEPS:")
    print("• Enable GCash H5 QRPH in deposit form")
    print("• Test with real users")
    print("• Both PayMaya and GCash H5 should work now")

if __name__ == "__main__":
    test_gcash_h5_qrph()
