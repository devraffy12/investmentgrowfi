import requests
import hashlib
import time

def test_la2568_direct():
    """Test LA2568 API directly"""
    print("🧪 Testing LA2568 API directly...")
    
    # LA2568 API configuration
    merchant_id = "RodolfHitler"
    secret_key = "86cb40fe1666b41eb0ad21577d66baef"
    api_url = "https://cloud.la2568.site/api/transfer"
    
    # Test parameters
    params = {
        'merchant': merchant_id,
        'payment_type': '3',
        'amount': '100.00',
        'order_id': f'TEST_{int(time.time())}',
        'bank_code': 'gcash',
        'callback_url': 'https://investmentgrowfi.onrender.com/payment/callback/',
        'return_url': 'https://investmentgrowfi.onrender.com/payment/success/'
    }
    
    # Try different signature methods
    methods = [
        ("Method 1 - Standard", generate_signature_method1),
        ("Method 2 - No Sort", generate_signature_method2),
        ("Method 3 - Different Order", generate_signature_method3)
    ]
    
    for method_name, method_func in methods:
        print(f"\n🔧 {method_name}")
        signature = method_func(params, secret_key)
        test_params = params.copy()
        test_params['sign'] = signature
        
        print(f"🔐 Signature: {signature}")
        
        try:
            response = requests.post(
                api_url,
                data=test_params,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            print(f"📊 Status: {response.status_code}")
            result = response.json()
            print(f"📄 Response: {result}")
            
            if result.get('status') == '1':
                print(f"🎉 SUCCESS with {method_name}!")
                return True, signature
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    return False, None

def generate_signature_method1(params, secret_key):
    """Standard alphabetical sort"""
    sorted_params = sorted(params.items())
    query_string = '&'.join([f"{key}={value}" for key, value in sorted_params])
    sign_string = f"{query_string}&key={secret_key}"
    return hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()

def generate_signature_method2(params, secret_key):
    """No sorting - original order"""
    query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
    sign_string = f"{query_string}&key={secret_key}"
    return hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()

def generate_signature_method3(params, secret_key):
    """Specific order as in documentation"""
    ordered_keys = ['merchant', 'payment_type', 'amount', 'order_id', 'bank_code', 'callback_url', 'return_url']
    query_parts = []
    for key in ordered_keys:
        if key in params:
            query_parts.append(f"{key}={params[key]}")
    query_string = '&'.join(query_parts)
    sign_string = f"{query_string}&key={secret_key}"
    return hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()

if __name__ == "__main__":
    success, correct_signature = test_la2568_direct()
    if success:
        print(f"\n✅ LA2568 API is working!")
        print(f"🔧 Correct signature method found!")
        print(f"� Now updating the Django service...")
    else:
        print("\n❌ All signature methods failed.")
        print("🔧 Need to check LA2568 documentation or contact support.")
