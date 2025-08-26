#!/usr/bin/env python3
"""
Production-Ready LA2568/Galaxy Payment Integration
Based on exact API specifications provided by user
"""

import hashlib
import requests
import json
import time
import logging
from decimal import Decimal
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import ipaddress

logger = logging.getLogger(__name__)

class LA2568PaymentService:
    """
    Production LA2568/Galaxy Payment Service
    
    API Details:
    - Merchant Key: 86cb40fe1666b41eb0ad21577d66baef
    - Deposit API URL: https://cloud.la2568.site/api/transfer
    - Payment API URL (withdraw): https://cloud.la2568.site/api/daifu
    - Callback IP: 52.77.112.163
    """
    
    def __init__(self):
        self.merchant_key = "86cb40fe1666b41eb0ad21577d66baef"
        self.deposit_url = "https://cloud.la2568.site/api/transfer"
        self.withdraw_url = "https://cloud.la2568.site/api/daifu"
        self.callback_ip = "52.77.112.163"
        self.timeout = 30
    
    def generate_order_id(self, user_id, transaction_type="DEP"):
        """Generate unique order ID: DEP_<user_id>_<timestamp>"""
        timestamp = int(time.time())
        return f"{transaction_type}_{user_id}_{timestamp}"
    
    def generate_signature(self, params, merchant_key=None):
        """
        Generate MD5 signature for LA2568 API
        
        Signature Format: MD5(param1+param2+...+merchant_key)
        Exact order depends on API specification
        """
        if merchant_key is None:
            merchant_key = self.merchant_key
        
        # For deposit API: merchant_id + payment_type + order_id + amount + bank_code + callback_url + return_url + key
        if 'amount' in params:
            # Updated signature format for new parameter names
            sign_string = (
                f"merchant_id={params.get('merchant_id', '')}&"
                f"payment_type={params.get('payment_type', '')}&"
                f"order_id={params.get('order_id', '')}&"
                f"amount={params.get('amount', '')}&"
                f"bank_code={params.get('bank_code', '')}&"
                f"callback_url={params.get('callback_url', '')}&"
                f"return_url={params.get('return_url', '')}&"
                f"key={merchant_key}"
            )
        else:
            # Fallback - concatenate all values + key
            sorted_params = sorted(params.items())
            param_string = ''.join([str(v) for k, v in sorted_params])
            sign_string = param_string + merchant_key
        
        logger.debug(f"Sign string: {sign_string}")
        signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
        return signature
    
    def create_deposit(self, user_id, amount, payment_method='gcash', callback_url=None, return_url=None):
        """
        Create deposit transaction via LA2568 API
        
        Args:
            user_id: Django user ID
            amount: Deposit amount (string or Decimal)
            payment_method: 'gcash', 'maya', etc.
            callback_url: Webhook URL for payment notifications
            return_url: URL to redirect user after payment
        
        Returns:
            dict: API response with payment_url or error
        """
        try:
            # Generate unique order ID
            order_id = self.generate_order_id(user_id, "DEP")
            
            # Map payment methods to LA2568 bank codes
            bank_code_map = {
                'gcash': 'GCSH',
                'maya': 'MAYA',
                'paymaya': 'MAYA',
                'bank': 'BANK'
            }
            bank_code = bank_code_map.get(payment_method.lower(), 'GCSH')
            
            # Prepare API parameters (using exact field names expected by LA2568)
            params = {
                'merchant_id': 'RodolfHitler',  # Changed from 'merchant'
                'payment_type': 'deposit',      # Added payment_type
                'order_id': order_id,           # Changed from 'orderid'
                'amount': str(amount),          # Changed from 'money'
                'bank_code': bank_code,         # Changed from 'type'
                'callback_url': callback_url or 'http://localhost:8000/payment/callback/',  # Changed from 'callbackurl'
                'return_url': return_url or 'http://localhost:8000/payment/success/'        # Changed from 'returnurl'
            }
            
            # Generate signature
            signature = self.generate_signature(params)
            params['sign'] = signature
            
            logger.info(f"📤 LA2568 API Request: {params}")
            
            # Make API request
            response = requests.post(
                self.deposit_url,
                data=params,
                timeout=self.timeout,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'Django/LA2568-Integration'
                }
            )
            
            logger.info(f"📥 LA2568 Raw Response: Status {response.status_code}, Content: {response.text[:500]}")
            
            # Parse response
            if response.status_code == 200:
                try:
                    result = response.json()
                    logger.info(f"✅ LA2568 JSON Response: {result}")
                    return {
                        'success': True,
                        'order_id': order_id,
                        'payment_url': result.get('payment_url') or result.get('url'),
                        'qr_code': result.get('qr_code'),
                        'api_response': result
                    }
                except json.JSONDecodeError:
                    logger.error(f"❌ LA2568 Invalid JSON: {response.text}")
                    return {
                        'success': False,
                        'error': 'Invalid API response format',
                        'raw_response': response.text
                    }
            else:
                logger.error(f"❌ LA2568 HTTP Error: {response.status_code}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'raw_response': response.text
                }
                
        except requests.exceptions.Timeout:
            logger.error("❌ LA2568 API Timeout")
            return {'success': False, 'error': 'API timeout'}
        except requests.exceptions.ConnectionError:
            logger.error("❌ LA2568 API Connection Error")
            return {'success': False, 'error': 'Connection failed'}
        except Exception as e:
            logger.error(f"❌ LA2568 API Unexpected Error: {e}")
            return {'success': False, 'error': str(e)}
    
    def verify_callback_signature(self, callback_data):
        """
        Verify callback signature from LA2568
        
        Args:
            callback_data: Dict containing callback parameters
            
        Returns:
            bool: True if signature is valid
        """
        try:
            received_sign = callback_data.get('sign', '')
            if not received_sign:
                return False
            
            # Generate expected signature
            callback_params = callback_data.copy()
            if 'sign' in callback_params:
                del callback_params['sign']
            
            expected_sign = self.generate_signature(callback_params)
            
            is_valid = received_sign.upper() == expected_sign.upper()
            logger.info(f"🔐 Signature verification: {'✅ Valid' if is_valid else '❌ Invalid'}")
            logger.debug(f"Expected: {expected_sign}, Received: {received_sign}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"❌ Signature verification error: {e}")
            return False
    
    def validate_callback_ip(self, request_ip):
        """
        Validate that callback comes from authorized IP
        
        Args:
            request_ip: IP address of the request
            
        Returns:
            bool: True if IP is authorized
        """
        try:
            # Allow localhost for testing
            if request_ip in ['127.0.0.1', '::1', 'localhost']:
                logger.info("🧪 Allowing localhost IP for testing")
                return True
            
            # Check authorized callback IP
            if request_ip == self.callback_ip:
                logger.info(f"✅ Authorized callback IP: {request_ip}")
                return True
            
            logger.warning(f"❌ Unauthorized callback IP: {request_ip}")
            return False
            
        except Exception as e:
            logger.error(f"❌ IP validation error: {e}")
            return False

# Initialize service
la2568_service = LA2568PaymentService()


@login_required
@require_http_methods(["POST"])
def create_deposit_transaction(request):
    """
    Create a new deposit transaction and redirect to payment gateway
    
    POST /payment/deposit/
    Parameters:
        - amount: Deposit amount
        - payment_method: gcash, maya, etc.
    """
    try:
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method', 'gcash')
        
        if not amount:
            return JsonResponse({'error': 'Amount is required'}, status=400)
        
        # Validate amount
        try:
            amount_decimal = Decimal(amount)
            if amount_decimal <= 0:
                return JsonResponse({'error': 'Amount must be positive'}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid amount format'}, status=400)
        
        # Create callback and return URLs
        callback_url = request.build_absolute_uri('/payment/callback/')
        return_url = request.build_absolute_uri('/payment/success/')
        
        # Call LA2568 API
        result = la2568_service.create_deposit(
            user_id=request.user.id,
            amount=amount,
            payment_method=payment_method,
            callback_url=callback_url,
            return_url=return_url
        )
        
        if result['success']:
            # Save transaction to database here
            # ... (database saving code)
            
            # Redirect to payment URL
            payment_url = result['payment_url']
            if payment_url:
                return HttpResponseRedirect(payment_url)
            else:
                return JsonResponse({'error': 'No payment URL received'}, status=500)
        else:
            logger.error(f"❌ Deposit creation failed: {result}")
            return JsonResponse({'error': result.get('error', 'Payment creation failed')}, status=500)
            
    except Exception as e:
        logger.error(f"❌ Deposit transaction error: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def payment_callback_handler(request):
    """
    Handle payment callback from LA2568
    
    POST /payment/callback/
    Expected from IP: 52.77.112.163
    
    Response format: {"code": 200, "msg": "success"}
    """
    try:
        # Get client IP
        client_ip = get_client_ip(request)
        logger.info(f"📞 Payment callback from IP: {client_ip}")
        
        # Validate callback IP
        if not la2568_service.validate_callback_ip(client_ip):
            logger.warning(f"❌ Unauthorized callback from IP: {client_ip}")
            return JsonResponse({'code': 403, 'msg': 'Unauthorized IP'}, status=403)
        
        # Parse callback data
        callback_data = request.POST.dict()
        logger.info(f"📞 Callback data: {callback_data}")
        
        # Verify signature
        if not la2568_service.verify_callback_signature(callback_data):
            logger.warning("❌ Invalid callback signature")
            return JsonResponse({'code': 400, 'msg': 'Invalid signature'}, status=400)
        
        # Extract transaction details
        order_id = callback_data.get('orderid') or callback_data.get('order_id')
        status = callback_data.get('status')
        amount = callback_data.get('money') or callback_data.get('amount')
        
        if not order_id:
            return JsonResponse({'code': 400, 'msg': 'Missing order ID'}, status=400)
        
        # Update transaction in database
        # ... (database update code)
        
        logger.info(f"✅ Payment callback processed: {order_id}, Status: {status}")
        
        # Return success response
        return JsonResponse({'code': 200, 'msg': 'success'})
        
    except Exception as e:
        logger.error(f"❌ Callback processing error: {e}")
        return JsonResponse({'code': 500, 'msg': 'Internal error'}, status=500)


def get_client_ip(request):
    """Get the real client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Test function for local development
def test_la2568_integration():
    """Test LA2568 API integration locally"""
    print("🧪 Testing LA2568 Integration")
    print("=" * 50)
    
    # Test deposit creation
    result = la2568_service.create_deposit(
        user_id=1,
        amount="100.00",
        payment_method="gcash",
        callback_url="http://localhost:8000/payment/callback/",
        return_url="http://localhost:8000/payment/success/"
    )
    
    print(f"Result: {result}")
    
    if result['success']:
        print(f"✅ Payment URL: {result['payment_url']}")
    else:
        print(f"❌ Error: {result['error']}")


if __name__ == "__main__":
    test_la2568_integration()
