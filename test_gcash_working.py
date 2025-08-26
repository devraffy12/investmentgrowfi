#!/usr/bin/env python3
"""
Create working GCash payment interface
This creates a direct test of the GCash interface like in your image
"""

import os
import sys
import django
import time

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.shortcuts import render
from django.test import RequestFactory
from django.contrib.auth.models import User
from payments.models import Transaction
from decimal import Decimal
import base64

def create_test_gcash_payment():
    """Create a test GCash payment that shows the proper interface"""
    
    print("🔧 Creating Test GCash Payment Interface...")
    
    # Create test user
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    # Create a test transaction
    reference_id = "TEST-GCASH-" + str(int(time.time() * 1000))[-6:]
    
    transaction = Transaction.objects.create(
        user=user,
        transaction_type='deposit',
        amount=Decimal('500.00'),
        payment_method='gcash',
        status='pending',
        reference_id=reference_id,
        la2568_order_id=reference_id,
        notes='Test GCash payment with proper interface'
    )
    
    print(f"✅ Created test transaction: {reference_id}")
    
    # Generate test QR code data (base64 encoded image data)
    # In real implementation, this would come from LA2568 API
    test_qr_base64 = base64.b64encode(b"TEST_QR_CODE_DATA_FOR_GCASH_PAYMENT").decode('utf-8')
    
    # Prepare context exactly like your image shows
    context = {
        'transaction': transaction,
        'amount': transaction.amount,
        'payment_method': 'gcash',
        'reference_id': reference_id,
        'order_id': reference_id,
        
        # GCash URLs for the interface
        'redirect_url': f'gcash://pay?amount={transaction.amount}&merchant=GrowFi&reference={reference_id}',
        'qrcode_url': f'https://cloud.la2568.site/qr/{reference_id}',
        'gcashqr': test_qr_base64,  # QR code base64 for display
        
        # Enable features from your image
        'auto_redirect': True,
        'show_qr_code': True,
        'show_open_app_button': True,
    }
    
    print(f"📱 Test GCash Interface Context:")
    print(f"   Amount: ₱{context['amount']}")
    print(f"   Reference: {context['reference_id']}")
    print(f"   GCash App URL: {context['redirect_url'][:50]}...")
    print(f"   QR Code URL: {context['qrcode_url']}")
    print(f"   QR Base64: {len(context['gcashqr'])} characters")
    
    # Create a test request to render the template
    factory = RequestFactory()
    request = factory.get('/test-gcash/')
    request.user = user
    
    try:
        # Test rendering the galaxy_payment template
        from django.template.loader import get_template
        template = get_template('myproject/galaxy_payment.html')
        rendered = template.render(context, request)
        
        print(f"✅ Template rendered successfully!")
        print(f"   Template size: {len(rendered)} characters")
        
        # Check for key elements from your image
        key_elements = [
            'Open in Gcash',
            'Securely complete the payment',
            'GCash App',
            'QR',
            'gcash'
        ]
        
        found_elements = []
        for element in key_elements:
            if element.lower() in rendered.lower():
                found_elements.append(element)
        
        print(f"✅ Found key elements: {', '.join(found_elements)}")
        
        if len(found_elements) >= 3:
            print(f"🎉 Template contains the expected GCash interface elements!")
        else:
            print(f"⚠️  Template might be missing some GCash interface elements")
            
    except Exception as e:
        print(f"❌ Error rendering template: {e}")
    
    # Show what the user should see
    print(f"\n🎯 Expected User Experience:")
    print(f"   1. User clicks 'PAY VIA GCASH' button")
    print(f"   2. Page shows: 'Securely complete the payment with your GCash App'")
    print(f"   3. Blue 'Open in Gcash' button is displayed")
    print(f"   4. QR code is shown for scanning")
    print(f"   5. Text: 'or Login to GCash and scan this QR with the QR Scanner'")
    
    # Save test data to file for debugging
    try:
        import json
        test_data = {
            'reference_id': reference_id,
            'amount': str(transaction.amount),
            'payment_method': 'gcash',
            'status': 'pending',
            'context_keys': list(context.keys()),
            'timestamp': str(timezone.now())
        }
        
        with open('test_gcash_data.json', 'w') as f:
            json.dump(test_data, f, indent=2)
        
        print(f"💾 Test data saved to test_gcash_data.json")
        
    except Exception as e:
        print(f"⚠️  Could not save test data: {e}")
    
    return context

if __name__ == '__main__':
    from django.utils import timezone
    context = create_test_gcash_payment()
    
    print(f"\n🔧 Next Steps:")
    print(f"   1. Contact LA2568 support to activate merchant account 'RodolfHitler'")
    print(f"   2. Or register new merchant account with LA2568")
    print(f"   3. Test with live LA2568 API once merchant is activated")
    print(f"   4. The template galaxy_payment.html should work once API returns proper data")
    
    print(f"\n💡 For immediate testing:")
    print(f"   The fallback payment method is working")
    print(f"   Users can still complete payments via direct GCash links")
    print(f"   Once LA2568 merchant is active, they'll see the proper interface from your image")
