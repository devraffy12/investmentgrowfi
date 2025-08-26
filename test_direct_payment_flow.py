#!/usr/bin/env python3
"""
Test Direct Payment Flow Implementation
Tests the complete direct GCash/Maya payment flow without LA2568 API
"""

import os
import sys
import django
from decimal import Decimal

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from payments.models import Transaction, PaymentMethod, PaymentLog
from payments.views import generate_direct_payment_urls
import json

def test_direct_payment_flow():
    """Test the complete direct payment flow"""
    print("🧪 Testing Direct Payment Flow...")
    
    # Create test user if doesn't exist
    try:
        user = User.objects.get(username='testuser')
        print(f"✅ Using existing test user: {user.username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        print(f"✅ Created test user: {user.username}")
    
    # Test direct payment URL generation
    print("\n📱 Testing Direct Payment URL Generation...")
    
    test_cases = [
        {
            'amount': Decimal('100.00'),
            'method': 'gcash',
            'reference': 'TEST-GCASH-001'
        },
        {
            'amount': Decimal('250.50'),
            'method': 'maya',
            'reference': 'TEST-MAYA-001'
        }
    ]
    
    for case in test_cases:
        try:
            urls = generate_direct_payment_urls(
                amount=case['amount'],
                reference_id=case['reference'],
                payment_method=case['method']
            )
            
            print(f"✅ {case['method'].upper()} URLs generated:")
            print(f"   📱 App URL: {urls['redirect_url'][:50]}...")
            print(f"   🔗 Web URL: {urls['qrcode_url'][:50]}...")
            
            # Verify URL format
            if case['method'] == 'gcash':
                assert 'gcash://' in urls['redirect_url'] or 'https://m.gcash.com' in urls['redirect_url']
            elif case['method'] == 'maya':
                assert 'maya://' in urls['redirect_url'] or 'https://maya.ph' in urls['redirect_url']
            
            print(f"   ✅ URL format validation passed")
            
        except Exception as e:
            print(f"   ❌ Error generating {case['method']} URLs: {e}")
    
    # Test transaction creation
    print("\n💳 Testing Transaction Creation...")
    
    try:
        # Create test transaction
        transaction = Transaction.objects.create(
            user=user,
            transaction_type='deposit',
            amount=Decimal('100.00'),
            payment_method='gcash',
            status='pending',
            reference_id='TEST-DIRECT-001',
            la2568_order_id='DIRECT-001',
            notes='Test direct payment'
        )
        
        print(f"✅ Transaction created: {transaction.reference_id}")
        print(f"   Amount: ₱{transaction.amount}")
        print(f"   Status: {transaction.status}")
        print(f"   Method: {transaction.payment_method}")
        
        # Test transaction update
        transaction.status = 'completed'
        transaction.save()
        
        print(f"✅ Transaction status updated to: {transaction.status}")
        
    except Exception as e:
        print(f"❌ Error creating transaction: {e}")
    
    # Test payment logging
    print("\n📝 Testing Payment Logging...")
    
    try:
        log_entry = PaymentLog.objects.create(
            transaction=transaction,
            action='payment_initiated',
            status='success',
            request_data={'method': 'direct', 'amount': '100.00'},
            response_data={'status': 'success', 'urls_generated': True},
            notes='Direct payment URLs generated successfully'
        )
        
        print(f"✅ Payment log created: {log_entry.action}")
        print(f"   Status: {log_entry.status}")
        print(f"   Notes: {log_entry.notes}")
        
    except Exception as e:
        print(f"❌ Error creating payment log: {e}")
    
    # Test client simulation
    print("\n🌐 Testing Client Simulation...")
    
    try:
        client = Client()
        
        # Login test user
        login_success = client.login(username='testuser', password='testpass123')
        if login_success:
            print("✅ Test user logged in successfully")
        else:
            print("❌ Failed to login test user")
            return
        
        # Test deposit page (GET)
        response = client.get(reverse('deposit'))
        print(f"✅ Deposit page GET: {response.status_code}")
        
        # Test deposit submission (POST)
        post_data = {
            'amount': '150.00',
            'payment_method': 'gcash'
        }
        
        response = client.post(reverse('deposit'), post_data, follow=True)
        print(f"✅ Deposit POST: {response.status_code}")
        
        if response.status_code == 200:
            # Check if we got redirected to payment page
            if 'galaxy_payment.html' in str(response.content) or 'reference_id' in response.context:
                print("✅ Successfully redirected to payment page")
            else:
                print("⚠️  Response received but not payment page")
        
    except Exception as e:
        print(f"❌ Error in client simulation: {e}")
    
    # Summary
    print("\n📊 Test Summary:")
    total_transactions = Transaction.objects.filter(user=user).count()
    total_logs = PaymentLog.objects.filter(transaction__user=user).count()
    
    print(f"✅ Total transactions created: {total_transactions}")
    print(f"✅ Total payment logs created: {total_logs}")
    
    # Available payment methods
    gcash_methods = PaymentMethod.objects.filter(code='gcash', is_active=True).count()
    maya_methods = PaymentMethod.objects.filter(code='maya', is_active=True).count()
    
    print(f"✅ Active GCash methods: {gcash_methods}")
    print(f"✅ Active Maya methods: {maya_methods}")
    
    print("\n🎉 Direct Payment Flow Test Completed!")
    print("\n💡 Next Steps:")
    print("   1. Test with real mobile device for app redirects")
    print("   2. Verify QR code generation works")
    print("   3. Test payment status checking")
    print("   4. Configure webhook endpoints for payment confirmation")

if __name__ == '__main__':
    test_direct_payment_flow()
