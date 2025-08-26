"""
LA2568 Deposit API View
Simple, focused view for handling deposits with proper redirect_url handling
"""

import json
import logging
import time
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from .la2568_service import la2568_service

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_deposit_api(request):
    """
    Create deposit using LA2568 API and return redirect_url
    
    Request JSON:
    {
        "amount": 100.00,
        "payment_method": "gcash"
    }
    
    Response JSON:
    {
        "success": true,
        "redirect_url": "https://cloud.la2568.site/api/payment_direct/redirect/XXXXXXXX",
        "order_id": "ORDER123456",
        "amount": "100.00"
    }
    """
    try:
        # Parse request data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.dict()
        
        amount = data.get('amount')
        payment_method = data.get('payment_method', 'gcash')
        
        # Validate inputs
        if not amount:
            return JsonResponse({
                'success': False,
                'error': 'Amount is required'
            }, status=400)
        
        try:
            amount_decimal = Decimal(str(amount))
            if amount_decimal <= 0:
                raise ValueError("Amount must be positive")
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'Invalid amount format'
            }, status=400)
        
        # Generate unique order ID
        order_id = f"DEP_{request.user.id}_{int(time.time())}"
        
        logger.info(f"🚀 Creating LA2568 deposit for user {request.user.id}: ₱{amount_decimal} via {payment_method}")
        
        # Call LA2568 API directly
        result = la2568_service.create_deposit(
            amount=amount_decimal,
            order_id=order_id,
            payment_method=payment_method,
            user_id=request.user.id
        )
        
        logger.info(f"📡 LA2568 API Result: {json.dumps(result, default=str, indent=2)}")
        
        if result.get('success'):
            # Success response with redirect_url from LA2568
            redirect_url = result.get('redirect_url')
            if not redirect_url:
                logger.error("❌ LA2568 API did not return redirect_url")
                return JsonResponse({
                    'success': False,
                    'error': 'Payment gateway did not return redirect URL'
                }, status=400)
            
            # Save deposit record to database
            try:
                from myproject.models import Transaction
                transaction = Transaction.objects.create(
                    user=request.user,
                    transaction_type='deposit',
                    amount=amount_decimal,
                    payment_method=payment_method,
                    reference_number=order_id,
                    status='pending',
                    api_transaction_id=result.get('order_id', order_id)
                )
                logger.info(f"💾 Created transaction record: {transaction.id}")
            except Exception as e:
                logger.error(f"❌ Failed to save transaction: {str(e)}")
                # Continue anyway, don't fail the payment
            
            response_data = {
                'success': True,
                'order_id': result.get('order_id', order_id),
                'amount': str(amount_decimal),
                'payment_method': payment_method,
                'redirect_url': redirect_url,
                'qrcode_url': result.get('qrcode_url'),
                'message': 'Deposit created successfully - redirecting to GCash'
            }
            
            logger.info(f"✅ Deposit created successfully. Redirect URL: {redirect_url}")
            return JsonResponse(response_data)
        else:
            # Error response from LA2568
            error_message = result.get('message', 'Deposit creation failed')
            logger.error(f"❌ LA2568 deposit creation failed: {error_message}")
            
            return JsonResponse({
                'success': False,
                'error': f'Payment gateway error: {error_message}',
                'details': result.get('raw_response', {})
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format'
        }, status=400)
        
    except Exception as e:
        logger.error(f"💥 Unexpected error in create_deposit_api: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class DepositAPIView(View):
    """
    Class-based view for deposit API (alternative to function-based view)
    """
    
    def post(self, request):
        """Handle POST request for deposit creation"""
        return create_deposit_api(request)
    
    def get(self, request):
        """Handle GET request - return available payment methods"""
        try:
            payment_methods = la2568_service.get_payment_methods()
            config_status = la2568_service.get_config_status()
            
            return JsonResponse({
                'success': True,
                'payment_methods': payment_methods,
                'service_configured': config_status['configured'],
                'config': config_status
            })
            
        except Exception as e:
            logger.error(f"Error getting payment methods: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to get payment methods'
            }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def check_deposit_status(request, order_id):
    """
    Check deposit status using LA2568 API
    
    URL: /api/deposit/status/<order_id>/
    
    Response:
    {
        "success": true,
        "order_id": "ORDER123456",
        "status": "completed",
        "amount": "100.00"
    }
    """
    try:
        if not order_id:
            return JsonResponse({
                'success': False,
                'error': 'Order ID is required'
            }, status=400)
        
        logger.info(f"🔍 Checking deposit status for order: {order_id}")
        
        # Query LA2568 API
        result = la2568_service.query_transaction(order_id)
        
        if result.get('status') != 'error':
            # Map LA2568 status to internal status
            internal_status = la2568_service.map_status_to_internal(result.get('status', 'pending'))
            
            return JsonResponse({
                'success': True,
                'order_id': order_id,
                'status': internal_status,
                'amount': result.get('amount'),
                'transaction_id': result.get('transaction_id'),
                'raw_response': result
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('message', 'Status check failed'),
                'order_id': order_id
            }, status=400)
            
    except Exception as e:
        logger.error(f"Error checking deposit status: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Status check failed'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def test_la2568_connection(request):
    """
    Test LA2568 API connection and configuration
    
    Response:
    {
        "success": true,
        "config_status": {...},
        "test_result": "API connection successful"
    }
    """
    try:
        config_status = la2568_service.get_config_status()
        
        # Test with a small amount
        test_order_id = f"TEST_{int(time.time())}"
        test_result = la2568_service.create_deposit(
            amount=Decimal('1.00'),
            order_id=test_order_id,
            payment_method='gcash'
        )
        
        return JsonResponse({
            'success': True,
            'config_status': config_status,
            'test_order_id': test_order_id,
            'test_result': test_result,
            'message': 'LA2568 connection test completed'
        })
        
    except Exception as e:
        logger.error(f"LA2568 connection test failed: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'config_status': la2568_service.get_config_status()
        }, status=500)
