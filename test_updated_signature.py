#!/usr/bin/env python
"""
Test updated Galaxy API signature with correct parameter order and uppercase hash
"""
import hashlib

def test_updated_galaxy_signature():
    """Test updated Galaxy signature generation"""
    
    # Galaxy API credentials
    merchant_id = "RodolfHitler"
    secret_key = "86cb40fe1666b41eb0ad21577d66baef"
    
    # Sample parameters
    params = {
        'merchant': merchant_id,
        'payment_type': '3',  # PayMaya
        'amount': '300.00',
        'order_id': 'test_12345',
        'bank_code': 'PMP',
        'mobile': '09919067713',
        'callback_url': 'https://investmentgrowfi.onrender.com/api/callback/',
        'return_url': 'https://investmentgrowfi.onrender.com/deposit/success/'
    }
    
    print("🔐 Updated Galaxy API Signature Test")
    print("=" * 50)
    
    # Updated method with correct parameter order and uppercase hash
    def generate_signature_updated(params, secret_key):
        """Updated signature generation method"""
        filtered_params = {k: v for k, v in params.items() if k != 'sign' and v is not None}
        
        # Use specific order for deposit/transfer parameters
        ordered_keys = ['merchant', 'payment_type', 'amount', 'order_id', 'bank_code', 'mobile', 'callback_url', 'return_url']
        
        # Create query string in correct parameter order
        query_parts = []
        for key in ordered_keys:
            if key in filtered_params:
                query_parts.append(f"{key}={filtered_params[key]}")
        
        query_string = '&'.join(query_parts)
        sign_string = f"{query_string}&key={secret_key}"
        
        # Generate UPPERCASE MD5 hash
        signature = hashlib.md5(sign_string.encode("utf-8")).hexdigest().upper()
        return sign_string, signature
    
    sign_string, signature = generate_signature_updated(params, secret_key)
    
    print(f"📝 Updated Method (Correct Order + UPPERCASE):")
    print(f"Parameters in order:")
    ordered_keys = ['merchant', 'payment_type', 'amount', 'order_id', 'bank_code', 'mobile', 'callback_url', 'return_url']
    for key in ordered_keys:
        if key in params:
            print(f"  {key}: {params[key]}")
    
    print(f"\nSign String: {sign_string}")
    print(f"MD5 Hash (UPPERCASE): {signature}")
    
    print("\n" + "=" * 50)
    print("🎯 This should fix the signature error!")

if __name__ == "__main__":
    test_updated_galaxy_signature()
