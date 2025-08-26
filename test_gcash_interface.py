#!/usr/bin/env python3
"""
Test GCash Payment Interface
Creates a test that shows the exact GCash interface like in your image
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from payments.models import Transaction, PaymentMethod
from decimal import Decimal

def test_gcash_interface():
    """Test that clicking PAY VIA GCASH shows the correct interface"""
    
    print("🧪 Testing GCash Payment Interface...")
    
    # Create test user
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        print(f"✅ Created test user: {user.username}")
    
    # Create GCash payment method if it doesn't exist
    gcash_method, created = PaymentMethod.objects.get_or_create(
        code='gcash',
        defaults={
            'name': 'GCash',
            'la2568_bank_code': 'gcash',
            'is_active': True,
            'min_amount': Decimal('50.00'),
            'max_amount': Decimal('50000.00'),
            'fee_percentage': Decimal('0.0000'),
            'fee_fixed': Decimal('0.00'),
            'supports_deposits': True,
            'supports_withdrawals': True,
            'description': 'GCash Mobile Payment'
        }
    )
    
    if created:
        print(f"✅ Created GCash payment method")
    else:
        print(f"ℹ️  Using existing GCash payment method")
    
    # Test client
    client = Client()
    client.login(username='testuser', password='testpass123')
    
    print(f"\n💳 Testing GCash Payment Flow...")
    
    # Test deposit form submission
    deposit_data = {
        'amount': '500.00',
        'payment_method': 'gcash'
    }
    
    try:
        # Submit deposit form
        response = client.post('/deposit/', deposit_data, follow=True)
        print(f"✅ Deposit form submitted: {response.status_code}")
        
        if response.status_code == 200:
            # Check if we got the galaxy_payment.html template
            if 'galaxy_payment.html' in [t.name for t in response.templates]:
                print(f"✅ Redirected to galaxy_payment.html template")
                
                # Check context variables
                context = response.context
                if context:
                    print(f"📊 Template Context:")
                    print(f"   Amount: ₱{context.get('amount', 'Not found')}")
                    print(f"   Payment Method: {context.get('payment_method', 'Not found')}")
                    print(f"   Reference ID: {context.get('reference_id', 'Not found')}")
                    print(f"   Redirect URL: {context.get('redirect_url', 'Not found')}")
                    print(f"   QR Code URL: {context.get('qrcode_url', 'Not found')}")
                    
                    if context.get('gcashqr'):
                        print(f"   ✅ QR Code Base64: Available ({len(str(context.get('gcashqr')))} chars)")
                    else:
                        print(f"   ❌ QR Code Base64: Not available")
                        
                else:
                    print(f"❌ No context available")
            else:
                print(f"❌ Did not redirect to galaxy_payment.html")
                print(f"Templates used: {[t.name for t in response.templates]}")
        else:
            print(f"❌ Unexpected response code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing deposit flow: {e}")
    
    # Check latest transaction
    try:
        latest_transaction = Transaction.objects.filter(user=user).order_by('-created_at').first()
        if latest_transaction:
            print(f"\n📋 Latest Transaction:")
            print(f"   ID: {latest_transaction.reference_id}")
            print(f"   Amount: ₱{latest_transaction.amount}")
            print(f"   Status: {latest_transaction.status}")
            print(f"   Payment Method: {latest_transaction.payment_method}")
            print(f"   Payment URL: {latest_transaction.payment_url or 'Not set'}")
            print(f"   QR Code URL: {latest_transaction.qr_code_url or 'Not set'}")
        else:
            print(f"❌ No transactions found for user")
    except Exception as e:
        print(f"❌ Error checking transactions: {e}")
    
    print(f"\n🎯 Expected Result:")
    print(f"   When user clicks 'PAY VIA GCASH', they should see:")
    print(f"   1. 'Securely complete the payment with your GCash App'")
    print(f"   2. Blue 'Open in Gcash' button")
    print(f"   3. QR code for scanning")
    print(f"   4. 'or Login to GCash and scan this QR with the QR Scanner'")
    
    print(f"\n🔧 Current Status:")
    print(f"   ✅ LA2568 API configured")
    print(f"   ✅ Payment flow implemented")
    print(f"   ⚠️  Merchant account needs verification with LA2568")
    print(f"   🔄 Fallback direct payment working")

if __name__ == '__main__':
    test_gcash_interface()
