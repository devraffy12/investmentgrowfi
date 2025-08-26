# galaxy_api.py
import hashlib
import requests
import json
from decimal import Decimal
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class GalaxySystemAPI:
    def __init__(self, merchant_id: str = None, secret_key: str = None, base_url: str = None):
        # Use provided values or fallback to Django settings or defaults
        from django.conf import settings
        
        self.merchant_id = merchant_id or getattr(settings, 'GALAXY_MERCHANT_ID', 'RodolfHitler')
        self.secret_key = secret_key or getattr(settings, 'GALAXY_SECRET_KEY', '86cb40fe1666b41eb0ad21577d66baef')
        self.base_url = (base_url or getattr(settings, 'GALAXY_BASE_URL', 'https://cloud.la2568.site')).rstrip('/')
        
    def _generate_md5_signature(self, params: Dict[str, Any]) -> str:
        """
        Generate MD5 signature according to Galaxy API requirements
        """
        # Remove sign parameter if it exists and convert all to string
        filtered_params = {k: str(v) for k, v in params.items() if k != 'sign' and v is not None}
        
        # Sort parameters by key in ASCII ascending order
        sorted_params = sorted(filtered_params.items())
        
        # Create query string
        query_string = '&'.join([f'{k}={v}' for k, v in sorted_params])
        
        # Append secret key
        query_string += f'&key={self.secret_key}'
        
        # Generate MD5 hash (lowercase like in your code)
        md5_hash = hashlib.md5(query_string.encode('utf-8')).hexdigest().lower()
        
        logger.debug(f"Signature string: {query_string}")
        logger.debug(f"Generated signature: {md5_hash}")
        
        return md5_hash
    
    def create_deposit_order(self, 
                           amount: float, 
                           order_id: str, 
                           bank_code: str, 
                           callback_url: str, 
                           return_url: str, 
                           payment_type: str = "1",
                           customer_bank_card_account: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a deposit order
        
        Args:
            amount: Payment amount
            order_id: Your order ID
            bank_code: Bank code (gcash, PMP, GOT, mya)
            callback_url: Callback URL for notifications
            return_url: Return URL after payment
            payment_type: Payment type (1=Qrcode, 2=WEB_H5, 3=Fast Direct, 7=Original channel)
            customer_bank_card_account: Customer's GCash account (required for some payment types)
        """
        
        params = {
            'merchant': self.merchant_id,
            'payment_type': payment_type,
            'amount': f"{amount:.2f}",
            'order_id': order_id,
            'bank_code': bank_code,
            'callback_url': callback_url,
            'return_url': return_url
        }
        
        # Add customer account if provided
        if customer_bank_card_account:
            params['customer_bank_card_account'] = customer_bank_card_account
        
        # Generate signature
        params['sign'] = self._generate_md5_signature(params)
        
        try:
            response = requests.post(
                f'{self.base_url}/api/transfer',
                data=params,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'Django-Galaxy-Client/1.0'
                },
                timeout=30
            )
            
            logger.info(f"Deposit request params: {params}")
            logger.info(f"Deposit response status: {response.status_code}")
            logger.info(f"Deposit response content: {response.text}")
            
            response.raise_for_status()
            
            # Try to parse JSON response
            try:
                return response.json()
            except ValueError:
                logger.warning(f"Non-JSON response: {response.text}")
                return {
                    'status': '0', 
                    'message': 'Invalid response format',
                    'raw_response': response.text
                }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Deposit request failed: {e}")
            return {'status': '0', 'message': f'Request failed: {str(e)}'}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            return {'status': '0', 'message': 'Invalid response format'}
    
    def create_withdrawal_order(self,
                              total_amount: float,
                              order_id: str,
                              bank: str,
                              bank_card_name: str,
                              bank_card_account: str,
                              callback_url: str,
                              bank_card_remark: str = "no") -> Dict[str, Any]:
        """
        Create a withdrawal order
        
        Args:
            total_amount: Withdrawal amount
            order_id: Your order ID
            bank: Bank name
            bank_card_name: Account holder name or GCash number
            bank_card_account: Bank account or GCash number
            callback_url: Callback URL for notifications
            bank_card_remark: IFSC code or "no" for GCash
        """
        
        params = {
            'merchant': self.merchant_id,
            'total_amount': f"{total_amount:.2f}",
            'callback_url': callback_url,
            'order_id': order_id,
            'bank': bank,
            'bank_card_name': bank_card_name,
            'bank_card_account': str(bank_card_account),
            'bank_card_remark': bank_card_remark
        }
        
        # Generate signature
        params['sign'] = self._generate_md5_signature(params)
        
        try:
            response = requests.post(
                f'{self.base_url}/api/daifu',
                data=params,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            logger.info(f"Withdrawal request params: {params}")
            logger.info(f"Withdrawal response status: {response.status_code}")
            logger.info(f"Withdrawal response content: {response.text}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Withdrawal request failed: {e}")
            return {'status': '0', 'message': f'Request failed: {str(e)}'}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            return {'status': '0', 'message': 'Invalid response format'}
    
    def query_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Query order status
        
        Args:
            order_id: Your order ID
        """
        
        params = {
            'merchant': self.merchant_id,
            'order_id': order_id
        }
        
        # Generate signature
        params['sign'] = self._generate_md5_signature(params)
        
        try:
            response = requests.post(
                f'{self.base_url}/api/query',
                data=params,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            logger.info(f"Query request params: {params}")
            logger.info(f"Query response status: {response.status_code}")
            logger.info(f"Query response content: {response.text}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Query request failed: {e}")
            return {'status': '0', 'message': f'Request failed: {str(e)}'}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            return {'status': '0', 'message': 'Invalid response format'}
    
    def query_balance(self) -> Dict[str, Any]:
        """
        Query merchant balance
        """
        
        params = {
            'merchant': self.merchant_id
        }
        
        # Generate signature
        params['sign'] = self._generate_md5_signature(params)
        
        try:
            response = requests.post(
                f'{self.base_url}/api/me',
                data=params,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            logger.info(f"Balance query params: {params}")
            logger.info(f"Balance response status: {response.status_code}")
            logger.info(f"Balance response content: {response.text}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Balance query failed: {e}")
            return {'status': '0', 'message': f'Request failed: {str(e)}'}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            return {'status': '0', 'message': 'Invalid response format'}
    
    def query_receipt(self, order_id: str) -> Dict[str, Any]:
        """
        Query transaction receipt
        
        Args:
            order_id: Your order ID
        """
        
        params = {
            'merchant': self.merchant_id,
            'order_id': order_id
        }
        
        # Generate signature
        params['sign'] = self._generate_md5_signature(params)
        
        try:
            response = requests.post(
                f'{self.base_url}/api/receipt',
                data=params,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            logger.info(f"Receipt query params: {params}")
            logger.info(f"Receipt response status: {response.status_code}")
            logger.info(f"Receipt response content: {response.text}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Receipt query failed: {e}")
            return {'status': '0', 'message': f'Request failed: {str(e)}'}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            return {'status': '0', 'message': 'Invalid response format'}
    
    def verify_callback_signature(self, callback_data: Dict[str, Any]) -> bool:
        """
        Verify callback signature
        
        Args:
            callback_data: Data received from callback
        """
        
        received_sign = callback_data.get('sign', '')
        expected_sign = self._generate_md5_signature(callback_data)
        
        return received_sign.lower() == expected_sign.lower()
