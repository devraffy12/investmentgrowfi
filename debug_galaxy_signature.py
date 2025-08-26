#!/usr/bin/env python
"""
Debug Galaxy API signature generation
"""
import hashlib

def test_galaxy_signature():
    """Test Galaxy signature generation with sample data"""
    
    # Galaxy API credentials
    merchant_id = "RodolfHitler"
    secret_key = "86cb40fe1666b41eb0ad21577d66baef"
    
    # Sample parameters na dapat ma-send sa Galaxy API
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
    
    print("🔐 Galaxy API Signature Debug")
    print("=" * 50)
    print(f"Merchant ID: {merchant_id}")
    print(f"Secret Key: {secret_key}")
    print("\n📋 Parameters:")
    for key, value in params.items():
        print(f"  {key}: {value}")
    
    # Method 1: Current implementation
    def generate_signature_method1(params, secret_key):
        """Current signature generation method"""
        filtered_params = {k: v for k, v in params.items() if k != 'sign' and v is not None}
        sorted_params = sorted(filtered_params.items())
        query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        sign_string = f"{query_string}&key={secret_key}"
        signature = hashlib.md5(sign_string.encode("utf-8")).hexdigest()
        return sign_string, signature
    
    # Method 2: Alternative method (no key parameter)
    def generate_signature_method2(params, secret_key):
        """Alternative signature method"""
        filtered_params = {k: v for k, v in params.items() if k != 'sign' and v is not None}
        sorted_params = sorted(filtered_params.items())
        query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        sign_string = f"{query_string}{secret_key}"  # Direct concatenation
        signature = hashlib.md5(sign_string.encode("utf-8")).hexdigest()
        return sign_string, signature
    
    # Method 3: Another common method
    def generate_signature_method3(params, secret_key):
        """Another signature method"""
        filtered_params = {k: v for k, v in params.items() if k != 'sign' and v is not None}
        # Add secret key as parameter
        filtered_params['key'] = secret_key
        sorted_params = sorted(filtered_params.items())
        query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        signature = hashlib.md5(query_string.encode("utf-8")).hexdigest()
        return query_string, signature
    
    print("\n🔍 Testing Different Signature Methods:")
    print("-" * 50)
    
    # Test Method 1
    sign_string1, signature1 = generate_signature_method1(params, secret_key)
    print(f"\n📝 Method 1 (Current):")
    print(f"Sign String: {sign_string1}")
    print(f"MD5 Hash: {signature1}")
    
    # Test Method 2
    sign_string2, signature2 = generate_signature_method2(params, secret_key)
    print(f"\n📝 Method 2 (Direct):")
    print(f"Sign String: {sign_string2}")
    print(f"MD5 Hash: {signature2}")
    
    # Test Method 3
    sign_string3, signature3 = generate_signature_method3(params, secret_key)
    print(f"\n📝 Method 3 (Key as param):")
    print(f"Sign String: {sign_string3}")
    print(f"MD5 Hash: {signature3}")
    
    print("\n" + "=" * 50)
    print("🎯 Try these signatures with Galaxy API to see which works!")

if __name__ == "__main__":
    test_galaxy_signature()
