"""
Django management command to test LA2568 API configuration
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from payments.la2568_service import la2568_service
from decimal import Decimal
import json


class Command(BaseCommand):
    help = 'Test LA2568 API configuration and connectivity'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--test-deposit',
            action='store_true',
            help='Test deposit API call (will not create real transaction)'
        )
        parser.add_argument(
            '--test-query',
            type=str,
            help='Test query API with specific order ID'
        )
        parser.add_argument(
            '--amount',
            type=float,
            default=100.0,
            help='Test amount for deposit (default: 100.0)'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Testing LA2568 API Configuration'))
        self.stdout.write('=' * 50)
        
        # Check configuration
        config_status = la2568_service.get_config_status()
        self.stdout.write(f"Configuration Status: {json.dumps(config_status, indent=2)}")
        
        if not la2568_service.is_configured():
            self.stdout.write(self.style.ERROR('❌ LA2568 service is not properly configured'))
            return
        
        self.stdout.write(self.style.SUCCESS('✅ LA2568 service is configured'))
        
        # Test payment methods
        self.stdout.write('\n📱 Available Payment Methods:')
        payment_methods = la2568_service.get_payment_methods()
        for code, config in payment_methods.items():
            self.stdout.write(f"  - {config['name']} ({code}): ₱{config['min_amount']} - ₱{config['max_amount']}")
        
        # Test deposit if requested
        if options['test_deposit']:
            self.stdout.write('\n💰 Testing Deposit API...')
            test_order_id = f"TEST_DEP_{int(timezone.now().timestamp())}"
            test_amount = Decimal(str(options['amount']))
            
            try:
                result = la2568_service.create_deposit(
                    amount=test_amount,
                    order_id=test_order_id,
                    payment_method='gcash',
                    user_id=1  # Test user ID
                )
                
                if result.get('success'):
                    self.stdout.write(self.style.SUCCESS('✅ Deposit API test successful'))
                    self.stdout.write(f"Order ID: {result.get('order_id')}")
                    self.stdout.write(f"Payment URL: {result.get('payment_url')}")
                    if result.get('qr_code_url'):
                        self.stdout.write(f"QR Code URL: {result.get('qr_code_url')}")
                else:
                    self.stdout.write(self.style.ERROR('❌ Deposit API test failed'))
                    self.stdout.write(f"Error: {result.get('message')}")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Deposit API test error: {str(e)}'))
        
        # Test query if order ID provided
        if options['test_query']:
            self.stdout.write(f'\n🔍 Testing Query API for order: {options["test_query"]}')
            
            try:
                result = la2568_service.query_transaction(options['test_query'])
                
                if result.get('status') != 'error':
                    self.stdout.write(self.style.SUCCESS('✅ Query API test successful'))
                    self.stdout.write(f"Result: {json.dumps(result, indent=2)}")
                else:
                    self.stdout.write(self.style.ERROR('❌ Query API test failed'))
                    self.stdout.write(f"Error: {result.get('message')}")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Query API test error: {str(e)}'))
        
        # Test signature generation
        self.stdout.write('\n🔐 Testing Signature Generation...')
        test_params = {
            'merchant': la2568_service.merchant_id,
            'amount': '100.00',
            'order_id': 'TEST_12345'
        }
        
        try:
            signature = la2568_service.generate_signature(test_params)
            self.stdout.write(self.style.SUCCESS(f'✅ Signature generated: {signature}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Signature generation failed: {str(e)}'))
        
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('🎉 LA2568 API test completed'))
        
        # Provide usage examples
        self.stdout.write('\n📚 Usage Examples:')
        self.stdout.write('  python manage.py test_la2568 --test-deposit --amount 500')
        self.stdout.write('  python manage.py test_la2568 --test-query DEP_1_1645123456')
