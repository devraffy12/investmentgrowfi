import hashlib
import requests
import logging
import json
from decimal import Decimal
from django.conf import settings
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class GalaxyPaymentService: 
    """Galaxy Payment API service for handling deposits and withdrawals"""
    
    def __init__(self):
        self.merchant = "RodolfHitler"
        self.secret_key = "86cb40fe1666b41eb0ad21577d66baef"
        self.deposit_url = "https://cloud.la2568.site/api/transfer"
        self.withdraw_url = "https://cloud.la2568.site/api/daifu"
        self.callback_url = "https://investmentgrowfi.onrender.com/api/callback/"
        self.return_url = "https://investmentgrowfi.onrender.com/deposit/success/"
        
    def generate_md5_signature(self, params: Dict[str, Any]) -> str:
        """
        Generate MD5 signature for Galaxy API
        
        Args:
            params: Dictionary of parameters
            
        Returns:
            MD5 signature string (lowercase hex)
        """
        try:
            # Sort parameters alphabetically by key
            sorted_params = sorted(params.items())
            
            # Create query string
            query_string = '&'.join([f"{key}={value}" for key, value in sorted_params])
            
            # Append secret key
            sign_string = f"{query_string}&key={self.secret_key}"
            
            # Generate MD5 hash (lowercase hex)
            signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest()
            
            logger.info(f"Sign string: {sign_string}")
            logger.info(f"Generated signature: {signature}")
            
            return signature
            
        except Exception as e:
            logger.error(f"Error generating MD5 signature: {e}")
            raise
    
    def verify_callback_signature(self, params: Dict[str, Any]) -> bool:
        """
        Verify callback signature from Galaxy
        
        Args:
            params: Callback parameters including 'sign'
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            received_sign = params.pop('sign', '')
            expected_sign = self.generate_md5_signature(params)
            
            is_valid = received_sign.lower() == expected_sign.lower()
            
            if not is_valid:
                logger.warning(f"Signature mismatch - Received: {received_sign}, Expected: {expected_sign}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error verifying callback signature: {e}")
            return False
    
    def create_deposit_request(self, amount: Decimal, order_id: str, bank_code: str = "gcash", mobile_number: str = None) -> Dict[str, Any]:
        """
        Create deposit request to Galaxy API
        
        Args:
            amount: Deposit amount
            order_id: Unique transaction ID
            bank_code: Payment method (gcash, paymaya)
            mobile_number: User's mobile number (required by Galaxy API)
            
        Returns:
            API response with redirect_url
        """
        try:
            # Use default mobile number if not provided (as per CloudPay requirement)
            if not mobile_number:
                mobile_number = "09919067713"  # Default mobile number format
            
            # Prepare parameters
            params = {
                "merchant": self.merchant,
                "payment_type": "2",  # redirect mode
                "amount": f"{float(amount):.2f}",
                "order_id": order_id,
                "bank_code": bank_code,
                "mobile": mobile_number,  # Add mobile number field
                "callback_url": self.callback_url,
                "return_url": self.return_url
            }
            
            # Generate signature
            signature = self.generate_md5_signature(params.copy())
            params["sign"] = signature
            
            logger.info(f"🚀 Galaxy API deposit request: {json.dumps(params, indent=2)}")
            
            # Make API request
            response = requests.post(
                self.deposit_url,
                data=params,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"✅ Galaxy API deposit response: {json.dumps(result, indent=2)}")
            
            return {
                'success': True,
                'status': result.get('status'),
                'redirect_url': result.get('redirect_url'),
                'order_id': result.get('order_id', order_id),
                'message': result.get('message', 'Success'),
                'raw_response': result
            }
            
        except requests.RequestException as e:
            logger.error(f"❌ Galaxy API request failed: {e}")
            return {
                'success': False,
                'error': f'API request failed: {str(e)}',
                'redirect_url': None
            }
        except Exception as e:
            logger.error(f"❌ Galaxy API error: {e}")
            return {
                'success': False,
                'error': str(e),
                'redirect_url': None
            }
    
    def create_withdraw_request(self, amount: Decimal, order_id: str, bank_account: str, bank_code: str = "gcash") -> Dict[str, Any]:
        """
        Create withdraw request to Galaxy API
        
        Args:
            amount: Withdrawal amount
            order_id: Unique transaction ID
            bank_account: User's GCash/Maya number
            bank_code: Withdrawal method (gcash, paymaya)
            
        Returns:
            API response
        """
        try:
            # Prepare parameters
            params = {
                "merchant": self.merchant,
                "total_amount": f"{float(amount):.2f}",
                "order_id": order_id,
                "bank": bank_code,
                "bank_card_account": bank_account,
                "callback_url": self.callback_url
            }
            
            # Generate signature
            signature = self.generate_md5_signature(params.copy())
            params["sign"] = signature
            
            logger.info(f"🚀 Galaxy API withdraw request: {json.dumps(params, indent=2)}")
            
            # Make API request
            response = requests.post(
                self.withdraw_url,
                data=params,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"✅ Galaxy API withdraw response: {json.dumps(result, indent=2)}")
            
            return {
                'success': True,
                'status': result.get('status'),
                'order_id': result.get('order_id', order_id),
                'message': result.get('message', 'Success'),
                'raw_response': result
            }
            
        except requests.RequestException as e:
            logger.error(f"❌ Galaxy withdraw API request failed: {e}")
            return {
                'success': False,
                'error': f'API request failed: {str(e)}'
            }
        except Exception as e:
            logger.error(f"❌ Galaxy withdraw API error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def map_status_to_internal(self, galaxy_status: Any) -> str:
        """
        Map Galaxy API status to internal status
        
        Args:
            galaxy_status: Status from Galaxy API
            
        Returns:
            Internal status string
        """
        status_map = {
            5: 'completed',      # Success
            '5': 'completed',
            1: 'pending',        # Pending
            '1': 'pending',
            2: 'processing',     # Processing
            '2': 'processing',
            3: 'failed',         # Failed
            '3': 'failed',
            4: 'cancelled',      # Cancelled
            '4': 'cancelled'
        }
        
        return status_map.get(galaxy_status, 'pending')

    def query_transaction(self, order_id: str) -> Dict[str, Any]:
        """
        Query transaction status (placeholder for future implementation)
        
        Args:
            order_id: Transaction order ID
            
        Returns:
            Transaction status response
        """
        # Placeholder implementation
        return {
            'status': 'error',
            'message': 'Query transaction not yet implemented',
            'order_id': order_id
        }
    
    def get_merchant_balance(self) -> Dict[str, Any]:
        """
        Get merchant balance (placeholder for future implementation)
        
        Returns:
            Merchant balance information
        """
        # Placeholder implementation
        return {
            'status': 'success',
            'balance': '0.00',
            'currency': 'PHP',
            'message': 'Balance query not yet implemented for Galaxy API'
        }

# Global instance
galaxy_service = GalaxyPaymentService()
