#!/usr/bin/env python
"""
Enhanced payment verification system for Maya/Galaxy API
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json
import logging
from decimal import Decimal
import requests
import time

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def verify_payment_api(request):
    """
    Real-time payment verification API
    Called from frontend before showing success page
    """
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        payment_method = data.get('payment_method')
        amount = data.get('amount')
        
        logger.info(f"Payment verification request: order_id={order_id}, method={payment_method}, amount={amount}")
        
        if not order_id:
            return JsonResponse({
                'success': False,
                'message': 'Order ID is required',
                'status': 'error'
            })
        
        # Check if transaction exists in our database
        try:
            payment_transaction = PaymentTransaction.objects.get(reference_id=order_id)
            investment_transaction = InvestmentTransaction.objects.get(reference_number=order_id)
        except (PaymentTransaction.DoesNotExist, InvestmentTransaction.DoesNotExist):
            return JsonResponse({
                'success': False,
                'message': 'Transaction not found',
                'status': 'error'
            })
        
        # Verify with Galaxy API
        verification_result = verify_with_galaxy_api(order_id, payment_method, amount)
        
        if verification_result['success']:
            # Update transaction status to completed
            with db_transaction.atomic():
                payment_transaction.status = 'completed'
                payment_transaction.completed_at = timezone.now()
                payment_transaction.save()
                
                investment_transaction.status = 'completed'
                investment_transaction.save()
                
                # Update user balance
                user_profile = payment_transaction.user.userprofile
                user_profile.balance += Decimal(str(amount))
                user_profile.save()
                
                create_payment_log(
                    payment_transaction,
                    'verification_success',
                    f'Payment verified and completed: {verification_result["message"]}',
                    verification_result,
                    request.user
                )
            
            return JsonResponse({
                'success': True,
                'message': 'Payment verified successfully!',
                'status': 'completed',
                'transaction_id': order_id,
                'amount': str(amount),
                'new_balance': str(user_profile.balance)
            })
        else:
            # Update transaction status to failed
            payment_transaction.status = 'failed'
            payment_transaction.save()
            
            investment_transaction.status = 'failed'
            investment_transaction.save()
            
            create_payment_log(
                payment_transaction,
                'verification_failed',
                f'Payment verification failed: {verification_result["message"]}',
                verification_result,
                request.user
            )
            
            return JsonResponse({
                'success': False,
                'message': verification_result.get('message', 'Payment verification failed'),
                'status': 'failed',
                'error_code': verification_result.get('error_code', 'VERIFICATION_FAILED')
            })
            
    except Exception as e:
        logger.error(f"Payment verification error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Payment verification system error',
            'status': 'error'
        })

def verify_with_galaxy_api(order_id, payment_method, amount):
    """
    Verify payment status with Galaxy/LA2568 API
    """
    try:
        # Query payment status from Galaxy API
        query_params = {
            'merchant': galaxy_service.merchant_id,
            'order_id': order_id,
            'amount': str(amount)
        }
        
        # Generate signature for query
        query_params['sign'] = generate_galaxy_signature(query_params, galaxy_service.secret_key)
        
        # Call Galaxy query API
        query_url = f"{galaxy_service.api_domain}/api/query"
        
        logger.info(f"Querying Galaxy API: {query_url} with params: {query_params}")
        
        response = requests.post(
            query_url,
            data=query_params,
            timeout=30,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        logger.info(f"Galaxy query response: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                
                # Check Galaxy API response format
                status = result.get('status')
                message = result.get('message', '')
                payment_status = result.get('payment_status')
                
                if status == '1' and payment_status == '5':  # Success
                    return {
                        'success': True,
                        'message': 'Payment verified successfully',
                        'galaxy_response': result,
                        'payment_status': 'completed'
                    }
                elif payment_status in ['3', '0']:  # Failed
                    return {
                        'success': False,
                        'message': f'Payment failed: {message}',
                        'error_code': 'PAYMENT_FAILED',
                        'galaxy_response': result
                    }
                else:  # Pending or processing
                    return {
                        'success': False,
                        'message': f'Payment still processing: {message}',
                        'error_code': 'PAYMENT_PENDING',
                        'galaxy_response': result
                    }
                    
            except json.JSONDecodeError:
                return {
                    'success': False,
                    'message': 'Invalid response from payment gateway',
                    'error_code': 'INVALID_RESPONSE'
                }
        else:
            return {
                'success': False,
                'message': f'Payment gateway error: {response.status_code}',
                'error_code': 'GATEWAY_ERROR'
            }
            
    except requests.RequestException as e:
        logger.error(f"Galaxy API query failed: {str(e)}")
        return {
            'success': False,
            'message': 'Unable to verify payment with gateway',
            'error_code': 'NETWORK_ERROR'
        }

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def check_payment_status(request):
    """
    Check payment status without updating database
    For polling/checking status
    """
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        
        if not order_id:
            return JsonResponse({
                'success': False,
                'message': 'Order ID is required'
            })
        
        # Check database status first
        try:
            payment_transaction = PaymentTransaction.objects.get(reference_id=order_id)
            
            if payment_transaction.status == 'completed':
                return JsonResponse({
                    'success': True,
                    'status': 'completed',
                    'message': 'Payment completed'
                })
            elif payment_transaction.status == 'failed':
                return JsonResponse({
                    'success': False,
                    'status': 'failed',
                    'message': 'Payment failed'
                })
            else:
                # Still processing - check with Galaxy API
                verification_result = verify_with_galaxy_api(
                    order_id, 
                    payment_transaction.payment_method, 
                    payment_transaction.amount
                )
                
                return JsonResponse({
                    'success': verification_result['success'],
                    'status': verification_result.get('payment_status', 'processing'),
                    'message': verification_result['message']
                })
                
        except PaymentTransaction.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Transaction not found',
                'status': 'error'
            })
            
    except Exception as e:
        logger.error(f"Payment status check error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Status check failed',
            'status': 'error'
        })
