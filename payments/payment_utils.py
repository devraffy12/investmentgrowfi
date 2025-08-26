"""
Payment Utilities for Real GCash and Maya Integration
This module provides utilities for generating real payment URLs and QR codes
"""

import hashlib
import json
import logging
from decimal import Decimal
from typing import Dict, Any, Optional
from django.conf import settings
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


def generate_real_gcash_payment_url(amount: Decimal, reference_id: str, 
                                  merchant_name: str = None) -> Dict[str, Any]:
    """
    Generate real GCash payment URLs for actual payment processing
    
    Args:
        amount: Payment amount
        reference_id: Transaction reference ID
        merchant_name: Merchant name (optional)
        
    Returns:
        Dictionary containing payment URLs and metadata
    """
    try:
        config = getattr(settings, 'PAYMENT_API_CONFIG', {})
        merchant_name = merchant_name or config.get('GCASH_MERCHANT_NAME', 'GrowFi Investment')
        merchant_id = config.get('GCASH_MERCHANT_ID', 'GROWFI001')
        
        amount_str = f"{float(amount):.2f}"
        
        # Generate GCash app deep links (these work if GCash app is installed)
        app_deep_links = [
            f"gcash://pay?amount={amount_str}&reference={reference_id}&merchant={merchant_name}",
            f"gcash://send?amount={amount_str}&reference={reference_id}&recipient={merchant_name}",
            f"gcash://transfer?amount={amount_str}&note={reference_id}&to={merchant_id}",
            f"gcash://paybill?amount={amount_str}&biller={merchant_id}&account={reference_id}"
        ]
        
        # Generate GCash web URLs (for browsers/desktop)
        web_urls = [
            f"https://m.gcash.com/gcashapp/gcash-promopay-web/index.html#/pay?amount={amount_str}&reference={reference_id}",
            f"https://m.gcash.com/pay?amount={amount_str}&merchant={merchant_id}&ref={reference_id}",
            f"https://api.gcash.com/pay?amount={amount_str}&merchantId={merchant_id}&reference={reference_id}"
        ]
        
        # QR code data for GCash scanning
        qr_data = f"gcash://pay?amount={amount_str}&reference={reference_id}&merchant={merchant_name}"
        
        return {
            'primary_app_url': app_deep_links[0],
            'primary_web_url': web_urls[0],
            'app_urls': app_deep_links,
            'web_urls': web_urls,
            'qr_data': qr_data,
            'amount': amount,
            'reference_id': reference_id,
            'merchant_name': merchant_name,
            'payment_method': 'gcash'
        }
        
    except Exception as e:
        logger.error(f"Error generating GCash payment URL: {e}")
        raise


def generate_real_maya_payment_url(amount: Decimal, reference_id: str,
                                 merchant_name: str = None) -> Dict[str, Any]:
    """
    Generate real Maya payment URLs for actual payment processing
    
    Args:
        amount: Payment amount  
        reference_id: Transaction reference ID
        merchant_name: Merchant name (optional)
        
    Returns:
        Dictionary containing payment URLs and metadata
    """
    try:
        config = getattr(settings, 'PAYMENT_API_CONFIG', {})
        merchant_name = merchant_name or config.get('MAYA_MERCHANT_NAME', 'GrowFi Investment')
        merchant_id = config.get('MAYA_MERCHANT_ID', 'GROWFI001')
        
        amount_str = f"{float(amount):.2f}"
        
        # Generate Maya app deep links
        app_deep_links = [
            f"maya://pay?amount={amount_str}&reference={reference_id}&merchant={merchant_name}",
            f"maya://send?amount={amount_str}&reference={reference_id}&recipient={merchant_name}",
            f"maya://transfer?amount={amount_str}&note={reference_id}&to={merchant_id}",
            f"paymaya://pay?amount={amount_str}&reference={reference_id}&merchant={merchant_name}"
        ]
        
        # Generate Maya web URLs
        web_urls = [
            f"https://maya.ph/pay?amount={amount_str}&reference={reference_id}&merchant={merchant_id}",
            f"https://m.maya.ph/pay?amount={amount_str}&ref={reference_id}",
            f"https://api.maya.ph/pay?amount={amount_str}&merchantId={merchant_id}&reference={reference_id}"
        ]
        
        # QR code data for Maya scanning
        qr_data = f"maya://pay?amount={amount_str}&reference={reference_id}&merchant={merchant_name}"
        
        return {
            'primary_app_url': app_deep_links[0],
            'primary_web_url': web_urls[0], 
            'app_urls': app_deep_links,
            'web_urls': web_urls,
            'qr_data': qr_data,
            'amount': amount,
            'reference_id': reference_id,
            'merchant_name': merchant_name,
            'payment_method': 'maya'
        }
        
    except Exception as e:
        logger.error(f"Error generating Maya payment URL: {e}")
        raise


def get_payment_gateway_config(payment_method: str) -> Dict[str, Any]:
    """
    Get payment gateway configuration for specified method
    
    Args:
        payment_method: Payment method ('gcash' or 'maya')
        
    Returns:
        Configuration dictionary
    """
    config = getattr(settings, 'PAYMENT_API_CONFIG', {})
    
    if payment_method.lower() == 'gcash':
        return {
            'enabled': config.get('GCASH_ENABLED', True),
            'merchant_name': config.get('GCASH_MERCHANT_NAME', 'GrowFi Investment'),
            'merchant_id': config.get('GCASH_MERCHANT_ID', 'GROWFI001'),
            'api_base': config.get('GCASH_API_BASE', 'https://api.gcash.com'),
            'min_amount': Decimal('1.00'),
            'max_amount': Decimal('50000.00')
        }
    elif payment_method.lower() in ['maya', 'paymaya']:
        return {
            'enabled': config.get('MAYA_ENABLED', True),
            'merchant_name': config.get('MAYA_MERCHANT_NAME', 'GrowFi Investment'),
            'merchant_id': config.get('MAYA_MERCHANT_ID', 'GROWFI001'),
            'api_base': config.get('MAYA_API_BASE', 'https://api.maya.ph'),
            'min_amount': Decimal('1.00'),
            'max_amount': Decimal('50000.00')
        }
    else:
        raise ValueError(f"Unsupported payment method: {payment_method}")


def generate_payment_signature(params: Dict[str, Any], secret_key: str) -> str:
    """
    Generate payment signature for security
    
    Args:
        params: Payment parameters
        secret_key: Secret key for signing
        
    Returns:
        Generated signature
    """
    try:
        # Sort parameters
        sorted_params = sorted(params.items())
        
        # Create query string
        query_string = '&'.join([f"{key}={value}" for key, value in sorted_params])
        
        # Add secret key
        sign_string = f"{query_string}&key={secret_key}"
        
        # Generate hash
        signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
        
        return signature
        
    except Exception as e:
        logger.error(f"Error generating payment signature: {e}")
        raise


def create_real_payment_request(amount: Decimal, reference_id: str, 
                              payment_method: str, user_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Create a real payment request with proper URLs
    
    Args:
        amount: Payment amount
        reference_id: Transaction reference
        payment_method: Payment method ('gcash' or 'maya')
        user_id: Optional user ID
        
    Returns:
        Payment request data with real URLs
    """
    try:
        if payment_method.lower() == 'gcash':
            payment_data = generate_real_gcash_payment_url(amount, reference_id)
        elif payment_method.lower() in ['maya', 'paymaya']:
            payment_data = generate_real_maya_payment_url(amount, reference_id)
        else:
            raise ValueError(f"Unsupported payment method: {payment_method}")
        
        # Add additional metadata
        payment_data.update({
            'user_id': user_id,
            'created_at': None,  # Will be set by calling code
            'expires_at': None,  # Will be set by calling code
            'status': 'pending'
        })
        
        logger.info(f"Created real payment request for {payment_method}: {reference_id}")
        return payment_data
        
    except Exception as e:
        logger.error(f"Error creating payment request: {e}")
        raise


def validate_payment_amount(amount: Decimal, payment_method: str) -> bool:
    """
    Validate payment amount for specified method
    
    Args:
        amount: Amount to validate
        payment_method: Payment method
        
    Returns:
        True if amount is valid
    """
    try:
        config = get_payment_gateway_config(payment_method)
        min_amount = config['min_amount']
        max_amount = config['max_amount']
        
        return min_amount <= amount <= max_amount
        
    except Exception as e:
        logger.error(f"Error validating payment amount: {e}")
        return False


def is_mobile_device(user_agent: str) -> bool:
    """
    Check if request is from mobile device
    
    Args:
        user_agent: User agent string
        
    Returns:
        True if mobile device
    """
    mobile_indicators = [
        'Mobile', 'Android', 'iPhone', 'iPad', 'iPod', 
        'BlackBerry', 'IEMobile', 'Opera Mini', 'webOS'
    ]
    
    return any(indicator in user_agent for indicator in mobile_indicators)


def get_optimal_payment_url(payment_data: Dict[str, Any], is_mobile: bool) -> str:
    """
    Get optimal payment URL based on device type
    
    Args:
        payment_data: Payment data with URLs
        is_mobile: True if mobile device
        
    Returns:
        Optimal payment URL
    """
    if is_mobile:
        return payment_data.get('primary_app_url', payment_data.get('primary_web_url'))
    else:
        return payment_data.get('primary_web_url', payment_data.get('primary_app_url'))
