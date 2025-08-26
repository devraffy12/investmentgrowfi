#!/usr/bin/env python
"""
Test different signature combinations for Galaxy API
"""
import sys
import os
import hashlib

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
import django
django.setup()

def test_signature_combinations():
    """Test different parameter combinations for signature"""
    
    # Test parameters
    base_params = {
        'merchant': 'RodolfHitler',
        'payment_type': '3',
        'amount': '300.00',
        'order_id': 'test_signature',
        'bank_code': 'PMP',
        'callback_url': 'https://investmentgrowfi.onrender.com/api/callback/',
        'return_url': 'https://investmentgrowfi.onrender.com/deposit/success/',
        'customer_bank_card_account': '09919067713'
    }
    
    secret_key = '86cb40fe1666b41eb0ad21577d66baef'
    
    print("🧪 Testing Galaxy API Signature Combinations")
    print("=" * 60)
    
    # Test 1: All parameters (what we're currently doing)
    params1 = base_params.copy()
    ordered_keys1 = sorted(params1.keys())
    query1 = '&'.join([f"{k}={params1[k]}" for k in ordered_keys1])
    sign1 = f"{query1}&key={secret_key}"
    signature1 = hashlib.md5(sign1.encode()).hexdigest().lower()
    
    print("Test 1: All parameters included")
    print(f"Query: {query1}")
    print(f"Signature: {signature1}")
    print()
    
    # Test 2: Without customer_bank_card_account
    params2 = {k: v for k, v in base_params.items() if k != 'customer_bank_card_account'}
    ordered_keys2 = sorted(params2.keys())
    query2 = '&'.join([f"{k}={params2[k]}" for k in ordered_keys2])
    sign2 = f"{query2}&key={secret_key}"
    signature2 = hashlib.md5(sign2.encode()).hexdigest().lower()
    
    print("Test 2: Without customer_bank_card_account")
    print(f"Query: {query2}")
    print(f"Signature: {signature2}")
    print()
    
    # Test 3: LA2568 order (from working implementation)
    la2568_order = ['merchant', 'payment_type', 'amount', 'order_id', 'bank_code', 'callback_url', 'return_url']
    params3 = {k: base_params[k] for k in la2568_order if k in base_params}
    query3 = '&'.join([f"{k}={params3[k]}" for k in la2568_order])
    sign3 = f"{query3}&key={secret_key}"
    signature3 = hashlib.md5(sign3.encode()).hexdigest().lower()
    
    print("Test 3: LA2568 parameter order (no customer_bank_card_account)")
    print(f"Query: {query3}")
    print(f"Signature: {signature3}")
    print()
    
    # Test 4: Try customer_bank_card_account in LA2568 order
    la2568_order_with_card = ['merchant', 'payment_type', 'amount', 'order_id', 'bank_code', 'customer_bank_card_account', 'callback_url', 'return_url']
    params4 = {k: base_params[k] for k in la2568_order_with_card if k in base_params}
    query4 = '&'.join([f"{k}={params4[k]}" for k in la2568_order_with_card])
    sign4 = f"{query4}&key={secret_key}"
    signature4 = hashlib.md5(sign4.encode()).hexdigest().lower()
    
    print("Test 4: LA2568 order WITH customer_bank_card_account")
    print(f"Query: {query4}")
    print(f"Signature: {signature4}")
    print()
    
    print("=" * 60)
    print("🎯 Try Test 3 first (known working), then Test 4 if needed")

if __name__ == "__main__":
    test_signature_combinations()
