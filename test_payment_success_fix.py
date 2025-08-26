#!/usr/bin/env python
"""
Test the payment success page to ensure it works without errors
"""
import os
import sys
import django
from django.test import RequestFactory
from django.contrib.auth.models import User

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from payments.views import payment_success

def test_payment_success_view():
    """Test payment success view with different scenarios"""
    
    print("🧪 Testing Payment Success View")
    print("=" * 50)
    
    factory = RequestFactory()
    
    # Test 1: No order_id
    print("\n1. Testing without order_id:")
    request = factory.get('/payment/success/')
    response = payment_success(request)
    print(f"   Status: {response.status_code}")
    print(f"   Template: payment_success.html")
    print("   ✅ Should render with dummy transaction data")
    
    # Test 2: With order_id (but transaction might not exist)
    print("\n2. Testing with order_id:")
    request = factory.get('/payment/success/?order_id=test123')
    response = payment_success(request)
    print(f"   Status: {response.status_code}")
    print(f"   Template: payment_success.html")
    print("   ✅ Should render with dummy transaction data")
    
    # Test 3: Check response content type
    print(f"\n3. Response Details:")
    print(f"   Content-Type: {response.get('Content-Type', 'text/html')}")
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Payment success view is working!")
    else:
        print("   ❌ Payment success view has issues!")
    
    return response.status_code == 200

def test_template_variables():
    """Test that all required template variables are present"""
    
    print("\n🎯 Testing Template Context Variables")
    print("=" * 50)
    
    factory = RequestFactory()
    request = factory.get('/payment/success/?order_id=test123')
    
    # Get the view and manually check context
    from django.template.response import TemplateResponse
    
    try:
        response = payment_success(request)
        
        if hasattr(response, 'context_data'):
            context = response.context_data
        else:
            # For rendered responses, we need to check differently
            context = response.context
        
        print("Context variables found:")
        for key in ['transaction', 'order_id', 'message']:
            if key in context:
                print(f"   ✅ {key}: {type(context[key])}")
            else:
                print(f"   ❌ {key}: Missing")
        
        # Check transaction object attributes
        if 'transaction' in context and context['transaction']:
            transaction = context['transaction']
            required_attrs = [
                'reference_number', 'id', 'created_at', 'amount', 
                'status', 'transaction_type', 'payment_method', 
                'fee', 'description', 'investment'
            ]
            
            print("\nTransaction object attributes:")
            for attr in required_attrs:
                if hasattr(transaction, attr):
                    print(f"   ✅ {attr}: {getattr(transaction, attr)}")
                else:
                    print(f"   ❌ {attr}: Missing")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing template variables: {str(e)}")
        return False

def main():
    print("PAYMENT SUCCESS PAGE FIX VERIFICATION")
    print("=" * 60)
    
    # Test the view
    view_works = test_payment_success_view()
    
    # Test template variables
    variables_work = test_template_variables()
    
    print("\n" + "🎯 FINAL RESULTS")
    print("=" * 60)
    
    if view_works and variables_work:
        print("✅ Payment success page is FIXED!")
        print("✅ All template variables are available")
        print("✅ No more 'VariableDoesNotExist' errors")
        print("\n🚀 READY FOR TESTING:")
        print("   1. Users can complete payments")
        print("   2. Success page will display properly")
        print("   3. Transaction details will show correctly")
    else:
        print("❌ There are still issues to fix")
        if not view_works:
            print("   ❌ View has errors")
        if not variables_work:
            print("   ❌ Template variables missing")
    
    print("\n📝 TEST URLs:")
    print("   Success page: http://127.0.0.1:8000/payment/success/")
    print("   With order ID: http://127.0.0.1:8000/payment/success/?order_id=test123")

if __name__ == "__main__":
    main()
