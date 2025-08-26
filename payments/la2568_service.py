"""
LA2568 Payment API Service
Complete integration for LA2568 payment gateway
"""

import hashlib
import requests
import logging
import time
import json
from decimal import Decimal
from typing import Dict, Optional, Any, Tuple
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class LA2568PaymentService:
    """
    Comprehensive LA2568 Payment Gateway Service
    Handles deposits, withdrawals, and webhook verification
    """
    
    def __init__(self):
        self.config = getattr(settings, 'PAYMENT_API_CONFIG', {})
        self.merchant_key = '86cb40fe1666b41eb0ad21577d66baef'  # From API documentation
        self.merchant_id = 'RodolfHitler'  # From API documentation  
        self.secret_key = self.merchant_key
        self.base_url = 'https://cloud.la2568.site'  # From API documentation
        self.callback_ip = '52.77.112.163'  # From API documentation
        self.timeout = self.config.get('TIMEOUT', 30)
        self.max_retries = self.config.get('MAX_RETRIES', 3)
        
        logger.info(f"LA2568 Service initialized with merchant: {self.merchant_id} (length: {len(self.merchant_id)})")
        logger.info(f"LA2568 Secret key: {self.secret_key[:20]}...")
        logger.info(f"LA2568 Base URL: {self.base_url}")
    
    def generate_signature(self, params: Dict[str, Any]) -> str:
        """
        Generate MD5 signature for LA2568 API using specification order
        
        Args:
            params: Dictionary of parameters
            
        Returns:
            MD5 signature string
        """
        try:
            # Use specification order (not alphabetical) for LA2568
            if 'payment_type' in params:
                # Deposit/transfer order
                ordered_keys = ['merchant', 'payment_type', 'amount', 'order_id', 'bank_code', 'callback_url', 'return_url']
            else:
                # Other operations - use alphabetical sort as fallback
                ordered_keys = sorted(params.keys())
            
            # Create query string in correct order
            query_parts = []
            for key in ordered_keys:
                if key in params:
                    query_parts.append(f"{key}={params[key]}")
            
            query_string = '&'.join(query_parts)
            
            # Append secret key (LA2568 format)
            sign_string = f"{query_string}&key={self.secret_key}"
            
            # Generate MD5 hash and return uppercase
            signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
            
            logger.debug(f"Generated signature for: {query_string}")
            logger.debug(f"Sign string: {sign_string}")
            logger.debug(f"Signature: {signature}")
            return signature
            
        except Exception as e:
            logger.error(f"Error generating signature: {str(e)}")
            raise
    
    def make_api_request(self, endpoint: str, params: Dict[str, Any], method: str = 'POST') -> Dict[str, Any]:
        """
        Make API request to LA2568 with proper error handling and retries
        
        Args:
            endpoint: API endpoint (e.g., '/api/transfer')
            params: Request parameters
            method: HTTP method (default: POST)
            
        Returns:
            API response dictionary
        """
        for attempt in range(self.max_retries + 1):
            try:
                url = f"{self.base_url}{endpoint}"
                
                # Generate signature
                signature = self.generate_signature(params)
                params['sign'] = signature
                
                logger.info(f"LA2568 API Request (attempt {attempt + 1}): {url}")
                logger.debug(f"Request params: {json.dumps(params, indent=2)}")
                
                # Make request with form data (LA2568 expects application/x-www-form-urlencoded)
                response = requests.post(
                    url,
                    data=params,  # Send as form data, not JSON
                    headers={
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'User-Agent': 'Django-LA2568-Client/1.0'
                    },
                    timeout=self.timeout
                )
                
                response.raise_for_status()
                
                # Parse response
                try:
                    result = response.json()
                except ValueError:
                    # Handle non-JSON responses
                    logger.warning(f"Non-JSON response from LA2568: {response.text}")
                    result = {
                        'status': 'error',
                        'message': 'Invalid response format',
                        'raw_response': response.text
                    }
                
                logger.info(f"LA2568 API Response: {json.dumps(result, indent=2)}")
                return result
                
            except requests.exceptions.Timeout:
                logger.warning(f"LA2568 API timeout (attempt {attempt + 1})")
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                return {'status': 'error', 'message': 'API request timeout'}
                
            except requests.exceptions.ConnectionError:
                logger.warning(f"LA2568 API connection error (attempt {attempt + 1})")
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                    continue
                return {'status': 'error', 'message': 'API connection failed'}
                
            except requests.exceptions.RequestException as e:
                logger.error(f"LA2568 API request failed: {str(e)}")
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                    continue
                return {'status': 'error', 'message': f'API request failed: {str(e)}'}
                
            except Exception as e:
                logger.error(f"Unexpected error in LA2568 API request: {str(e)}")
                return {'status': 'error', 'message': f'Unexpected error: {str(e)}'}
        
        return {'status': 'error', 'message': 'Max retries exceeded'}
    
    def create_deposit(self, 
                      amount: Decimal, 
                      order_id: str, 
                      payment_method: str = 'gcash',
                      user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Create deposit transaction via LA2568
        
        Args:
            amount: Deposit amount
            order_id: Unique order ID
            payment_method: Payment method (gcash, maya, paymaya)
            user_id: User ID for tracking
            
        Returns:
            API response with payment URL and QR code
        """
        try:
            # Validate inputs
            if amount <= 0:
                return {'status': 'error', 'message': 'Invalid amount'}
            
            if not order_id:
                return {'status': 'error', 'message': 'Order ID required'}
            
            # Map payment methods to LA2568 bank codes
            bank_code_mapping = {
                'gcash': 'gcash',
                'maya': 'paymaya',
                'paymaya': 'paymaya'
            }
            
            bank_code = bank_code_mapping.get(payment_method.lower(), 'gcash')
            
            # Prepare callback URLs (per LA2568 specification)
            site_url = 'https://investmentgrowfi.onrender.com'
            callback_url = f"{site_url}/payment/callback/"  # Match your existing callback endpoint
            return_url = f"{site_url}/payment/success/"  # Where users return AFTER payment completion
            
            # Prepare LA2568 deposit parameters (exact per specification)
            params = {
                'merchant': self.merchant_id,  # RodolfHitler
                'payment_type': '2',  # Required: 2 for deposit payments (not 3)
                'amount': f"{float(amount):.2f}",
                'order_id': order_id,
                'bank_code': bank_code,
                'callback_url': callback_url,
                'return_url': return_url
            }
            
            logger.info(f"🔥 LA2568 API Call: /api/deposit")
            logger.info(f"   merchant: {params['merchant']}")
            logger.info(f"   payment_type: {params['payment_type']}")
            logger.info(f"   amount: {params['amount']}")
            logger.info(f"   order_id: {params['order_id']}")
            logger.info(f"   bank_code: {params['bank_code']}")
            
            # Make API request
            result = self.make_api_request('/api/deposit', params)
            
            # Process response
            if result.get('status') == '1' or result.get('status') == 1 or result.get('status') == 'success':
                logger.info(f"✅ LA2568 deposit created successfully: {order_id}")
                response_data = {
                    'success': True,
                    'status': 'success',
                    'order_id': result.get('order_id', order_id),
                    'redirect_url': result.get('redirect_url'),
                    'qrcode_url': result.get('qrcode_url'), 
                    'gcashqr': result.get('gcashqr'),  # Base64 QR image
                    'amount': amount,
                    'payment_method': payment_method,
                    'raw_response': result
                }
                
                # Log the redirect URL for debugging
                if response_data['redirect_url']:
                    logger.info(f"🔗 LA2568 redirect URL: {response_data['redirect_url']}")
                else:
                    logger.warning("⚠️ No redirect_url in LA2568 response")
                    
                return response_data
            else:
                # Enhanced error detection for primary channel availability
                error_msg = result.get('message', 'Unknown error')
                status_code = result.get('status', 'unknown')
                
                # Log detailed error information for debugging
                logger.error(f"❌ LA2568 deposit failed - Status: {status_code}, Message: {error_msg}")
                logger.error(f"Full response: {json.dumps(result, indent=2)}")
                
                # Detect specific conditions that indicate primary channel unavailability
                primary_channel_unavailable_indicators = [
                    'channel not available',
                    'service temporarily unavailable', 
                    'maintenance mode',
                    'channel offline',
                    'service down',
                    'system busy',
                    'try again later',
                    'temporarily out of service'
                ]
                
                is_channel_unavailable = any(
                    indicator in error_msg.lower() 
                    for indicator in primary_channel_unavailable_indicators
                ) or status_code in ['503', '502', '500', 503, 502, 500]
                
                return {
                    'success': False,
                    'status': 'error',
                    'message': error_msg,
                    'channel_unavailable': is_channel_unavailable,
                    'raw_response': result
                }
                
        except Exception as e:
            logger.error(f"Exception in create_deposit: {str(e)}")
            return {
                'success': False,
                'status': 'error',
                'message': f'Deposit creation failed: {str(e)}'
            }
    
    def create_withdrawal(self, 
                         amount: Decimal, 
                         order_id: str, 
                         payment_method: str = 'gcash',
                         account_number: Optional[str] = None,
                         account_name: Optional[str] = None,
                         user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Create withdrawal transaction via LA2568
        
        Args:
            amount: Withdrawal amount
            order_id: Unique order ID
            payment_method: Payment method (gcash, maya)
            account_number: Recipient account number
            account_name: Recipient account name
            user_id: User ID for tracking
            
        Returns:
            API response with withdrawal status
        """
        try:
            # Validate inputs
            if amount <= 0:
                return {'status': 'error', 'message': 'Invalid amount'}
            
            if not order_id:
                return {'status': 'error', 'message': 'Order ID required'}
            
            # Map payment methods
            bank_code_mapping = {
                'gcash': 'gcash',
                'maya': 'paymaya',
                'paymaya': 'paymaya'
            }
            
            bank_code = bank_code_mapping.get(payment_method.lower(), 'gcash')
            
            # Prepare callback URL
            site_url = getattr(settings, 'SITE_URL', 'https://investmentgrowfi.onrender.com/')
            notify_url = f"{site_url}/payments/notify/"
            
            # Prepare LA2568 withdrawal parameters
            params = {
                'merchant': self.merchant_id,
                'amount': f"{float(amount):.2f}",
                'order_id': order_id,
                'bank_code': bank_code,
                'notify_url': notify_url
            }
            
            # Add recipient details
            if account_number:
                params['account_number'] = account_number
            if account_name:
                params['account_name'] = account_name
            if user_id:
                params['user_id'] = str(user_id)
            
            # Make API request
            result = self.make_api_request('/api/daifu', params)
            
            # Process response
            if result.get('status') == '1' or result.get('status') == 1:
                logger.info(f"✅ LA2568 withdrawal created successfully: {order_id}")
                return {
                    'success': True,
                    'status': 'success',
                    'order_id': result.get('order_id', order_id),
                    'transaction_id': result.get('transaction_id'),
                    'amount': amount,
                    'payment_method': payment_method,
                    'raw_response': result
                }
            else:
                error_msg = result.get('message', 'Unknown error')
                logger.error(f"❌ LA2568 withdrawal failed: {error_msg}")
                return {
                    'success': False,
                    'status': 'error',
                    'message': error_msg,
                    'raw_response': result
                }
                
        except Exception as e:
            logger.error(f"Exception in create_withdrawal: {str(e)}")
            return {
                'success': False,
                'status': 'error',
                'message': f'Withdrawal creation failed: {str(e)}'
            }
    
    def query_transaction(self, order_id: str) -> Dict[str, Any]:
        """
        Query transaction status from LA2568
        
        Args:
            order_id: Order ID to query
            
        Returns:
            Transaction status information
        """
        try:
            if not order_id:
                return {'status': 'error', 'message': 'Order ID required'}
            
            # Prepare query parameters
            params = {
                'merchant': self.merchant_id,
                'order_id': order_id
            }
            
            # Make API request
            result = self.make_api_request('/api/query', params)
            
            logger.info(f"Transaction query for {order_id}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Exception in query_transaction: {str(e)}")
            return {
                'status': 'error',
                'message': f'Query failed: {str(e)}'
            }
    
    def verify_callback(self, callback_data: Dict[str, Any], client_ip: str = None) -> Tuple[bool, str]:
        """
        Verify LA2568 callback authenticity
        
        Args:
            callback_data: Callback data from LA2568
            client_ip: Client IP address
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Verify IP address if configured
            if self.callback_ip and client_ip:
                if client_ip != self.callback_ip:
                    logger.warning(f"Callback from unauthorized IP: {client_ip}, expected: {self.callback_ip}")
                    return False, f"Unauthorized IP: {client_ip}"
            
            # Verify signature
            received_signature = callback_data.get('sign', '')
            if not received_signature:
                logger.warning("No signature in callback data")
                return False, "Missing signature"
            
            # Prepare parameters for signature verification (exclude 'sign')
            params_to_verify = {k: v for k, v in callback_data.items() if k != 'sign'}
            
            # Generate expected signature
            expected_signature = self.generate_signature(params_to_verify)
            
            # Compare signatures (case-insensitive)
            if received_signature.upper() != expected_signature.upper():
                logger.error(f"Invalid callback signature. Expected: {expected_signature}, Received: {received_signature}")
                return False, f"Invalid signature"
            
            logger.info(f"✅ Callback verification successful for order: {callback_data.get('order_id')}")
            return True, "Valid"
            
        except Exception as e:
            logger.error(f"Exception in verify_callback: {str(e)}")
            return False, f"Verification error: {str(e)}"
    
    def map_status_to_internal(self, api_status: str) -> str:
        """
        Map LA2568 status codes to internal status
        
        Args:
            api_status: Status from LA2568 API
            
        Returns:
            Internal status string
        """
        status_mapping = {
            '1': 'pending',      # Pending
            '2': 'processing',   # Processing  
            '3': 'failed',       # Failed
            '5': 'completed',    # Success
            'success': 'completed',
            'failed': 'failed',
            'pending': 'pending',
            'processing': 'processing'
        }
        
        return status_mapping.get(str(api_status), 'pending')
    
    def get_payment_methods(self) -> Dict[str, Dict[str, Any]]:
        """Get available payment methods configuration"""
        return {
            'gcash': {
                'name': 'GCash',
                'code': 'gcash',
                'min_amount': Decimal('1.00'),
                'max_amount': Decimal('50000.00'),
                'enabled': True
            },
            'maya': {
                'name': 'Maya (PayMaya)',
                'code': 'paymaya',
                'min_amount': Decimal('1.00'),
                'max_amount': Decimal('50000.00'),
                'enabled': True
            }
        }
    
    def is_configured(self) -> bool:
        """Check if LA2568 service is properly configured"""
        return bool(
            self.merchant_key and 
            self.merchant_id and 
            self.base_url
        )
    
    def get_config_status(self) -> Dict[str, Any]:
        """Get configuration status for debugging"""
        return {
            'configured': self.is_configured(),
            'merchant_id': self.merchant_id,
            'merchant_key_set': bool(self.merchant_key),
            'base_url': self.base_url,
            'callback_ip': self.callback_ip,
            'timeout': self.timeout,
            'max_retries': self.max_retries
        }
    
    def create_payment(self, order_id: str, amount: float, payment_method: str = 'gcash', 
                      callback_url: str = '', success_url: str = '', cancel_url: str = '') -> Dict[str, Any]:
        """
        Create payment (alias for create_deposit for compatibility)
        
        Args:
            order_id: Unique order ID
            amount: Payment amount
            payment_method: Payment method (gcash, maya, paymaya)
            callback_url: Callback URL for notifications
            success_url: Success redirect URL
            cancel_url: Cancel redirect URL
            
        Returns:
            Payment response with URLs and QR codes
        """
        try:
            amount_decimal = Decimal(str(amount))
            result = self.create_deposit(
                amount=amount_decimal,
                order_id=order_id,
                payment_method=payment_method
            )
            
            if result.get('status') == 'success':
                return {
                    'success': True,
                    'order_id': result.get('order_id', order_id),
                    'payment_url': result.get('payment_url'),
                    'qr_code_url': result.get('qr_code_url'),
                    'qr_code_base64': result.get('qr_code_base64'),
                    'data': result.get('data', {})
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'Payment creation failed'),
                    'data': result.get('data', {})
                }
                
        except Exception as e:
            logger.error(f"Error in create_payment: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': {}
            }
    
    def verify_signature(self, params: Dict[str, Any], signature: str) -> bool:
        """
        Verify LA2568 signature
        
        Args:
            params: Parameters to verify
            signature: Signature to check
            
        Returns:
            True if signature is valid
        """
        try:
            expected_signature = self.generate_signature(params)
            return expected_signature.upper() == signature.upper()
        except Exception as e:
            logger.error(f"Error verifying signature: {e}")
            return False
    
    @property
    def deposit_url(self) -> str:
        """Get deposit API URL"""
        return self.config.get('DEPOSIT_URL', f'{self.base_url}/api/deposit')
    
    @property
    def withdraw_url(self) -> str:
        """Get withdrawal API URL"""
        return self.config.get('WITHDRAW_URL', f'{self.base_url}/api/daifu')


# Create singleton instance
la2568_service = LA2568PaymentService()
import logging

logger = logging.getLogger(__name__)

class LA2568Service:
    """Placeholder LA2568 service for backward compatibility"""
    
    def query_transaction(self, order_id: str):
        """Placeholder query method"""
        return {
            'status': 'error',
            'message': 'LA2568 service not implemented',
            'order_id': order_id
        }
    
    def map_status_to_internal(self, status):
        """Map status to internal format"""
        return 'pending'

# Global instance for backward compatibility
la2568_service = LA2568Service()
