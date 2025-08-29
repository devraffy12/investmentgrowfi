# Fixed Galaxy API Django implementation
import uuid
import requests
import logging
import hashlib
import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from myproject.views import firebase_login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.utils import timezone
from django.db.models import Sum, Q
from django.db import transaction as db_transaction
from .models import Transaction as PaymentTransaction, PaymentLog
from myproject.models import UserProfile, Transaction as InvestmentTransaction

logger = logging.getLogger(__name__)

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def generate_galaxy_signature(params, secret_key):
    """Generate Galaxy API MD5 signature using alphabetical order (working method)"""
    # Remove sign parameter and customer_bank_card_account (not included in signature)
    filtered_params = {k: v for k, v in params.items() if k not in ['sign', 'customer_bank_card_account'] and v is not None}
    
    # Use alphabetical order (known working method)
    ordered_keys = sorted(filtered_params.keys())
    
    # Create query string in alphabetical order
    query_parts = []
    for key in ordered_keys:
        query_parts.append(f"{key}={filtered_params[key]}")
    
    query_string = '&'.join(query_parts)
    
    # Add secret key at the end
    sign_string = f"{query_string}&key={secret_key}"
    
    logger.debug(f"Galaxy sign string (alphabetical, excluding customer_bank_card_account): {sign_string}")
    
    # Generate MD5 hash - lowercase
    signature = hashlib.md5(sign_string.encode("utf-8")).hexdigest().lower()
    logger.debug(f"Galaxy signature: {signature}")
    return signature

class GalaxyPaymentService:
    def __init__(self):
        # Use Galaxy API configuration with LA2568 API details
        self.api_domain = getattr(settings, 'GALAXY_BASE_URL', 'https://cloud.la2568.site')
        self.merchant_id = getattr(settings, 'GALAXY_MERCHANT_ID', 'RodolfHitler')
        self.secret_key = getattr(settings, 'GALAXY_SECRET_KEY', '86cb40fe1666b41eb0ad21577d66baef')
        
    def create_payment(self, amount, order_id, bank_code='gcash', payment_type='2', callback_url=None, return_url=None, mobile_number=None):
        """Create Galaxy payment request"""
        try:
            # Prepare Galaxy API parameters according to docs
            params = {
                'merchant': self.merchant_id,
                'payment_type': payment_type,  # 2=WEB_H5 for redirect
                'amount': f"{float(amount):.2f}",
                'order_id': order_id,
                'bank_code': bank_code,  # gcash, PMP, mya, GOT
                'callback_url': callback_url,
                'return_url': return_url,
            }
            
            # Add customer_bank_card_account (required for Galaxy API)
            # PayMaya Direct (PMP) doesn't need customer_bank_card_account parameter
            if bank_code != 'PMP':  # Skip customer_bank_card_account for PayMaya
                if mobile_number and mobile_number.strip():
                    # Clean mobile number - remove spaces and special characters
                    clean_mobile = ''.join(filter(str.isdigit, mobile_number))
                    
                    # Ensure proper Philippine mobile format (09xxxxxxxxx)
                    if clean_mobile.startswith('63') and len(clean_mobile) >= 12:
                        # Remove country code 63 and add 0
                        clean_mobile = '0' + clean_mobile[2:]
                    elif clean_mobile.startswith('9') and len(clean_mobile) == 10:
                        # 10-digit number starting with 9, add 0
                        clean_mobile = '0' + clean_mobile
                    elif not clean_mobile.startswith('09') and len(clean_mobile) >= 9:
                        # Other formats, try to fix
                        clean_mobile = '09' + clean_mobile[-9:]
                    
                    # Validate final format - must be 11 digits starting with 09
                    if len(clean_mobile) == 11 and clean_mobile.startswith('09'):
                        params['customer_bank_card_account'] = clean_mobile
                        logger.info(f"Adding customer_bank_card_account to Galaxy API: {clean_mobile}")
                    else:
                        # Use default mobile number format as required by CloudPay
                        params['customer_bank_card_account'] = "09171234567"
                        logger.warning(f"Invalid mobile format '{mobile_number}' -> '{clean_mobile}', using default: 09171234567")
                else:
                    # Use default mobile number format as required by CloudPay
                    params['customer_bank_card_account'] = "09171234567"
                    logger.info("No mobile number provided, using default customer_bank_card_account: 09171234567")
            else:
                # PayMaya Direct - no customer_bank_card_account parameter needed
                logger.info("PayMaya Direct (PMP) - skipping customer_bank_card_account parameter")
            
            # Generate signature using Galaxy method
            params['sign'] = generate_galaxy_signature(params, self.secret_key)
            
            logger.info(f"Galaxy API request: {params}")
            
            # Make request to Galaxy API
            response = requests.post(
                f"{self.api_domain}/api/transfer",
                data=params,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            logger.info(f"Galaxy API response status: {response.status_code}")
            logger.info(f"Galaxy API response text: {response.text}")
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Galaxy API request failed: {str(e)}")
            return {'status': '0', 'message': f'Request failed: {str(e)}'}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Galaxy API: {response.text}")
            return {'status': '0', 'message': 'Invalid API response format'}
    
    def query_transaction(self, order_id):
        """Query Galaxy transaction status"""
        try:
            params = {
                'merchant': self.merchant_id,
                'order_id': order_id,
            }
            
            params['sign'] = generate_galaxy_signature(params, self.secret_key)
            
            response = requests.post(
                f"{self.api_domain}/api/query",
                data=params,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Galaxy query failed: {str(e)}")
            return {'status': '0', 'message': f'Query failed: {str(e)}'}
    
    def verify_callback_signature(self, params):
        """Verify Galaxy callback signature"""
        received_sign = params.get('sign', '')
        calculated_sign = generate_galaxy_signature(params, self.secret_key)
        return received_sign.lower() == calculated_sign.lower()

# Initialize Galaxy service
galaxy_service = GalaxyPaymentService()

@firebase_login_required
def deposit_view(request):
    """Fixed deposit view with proper Galaxy API integration"""
    try:
        # Try to get Django user first, fallback to Firebase user logic
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Django user exists
            user_for_profile = request.user
            user_phone = request.user.username
        elif hasattr(request, 'firebase_user') and request.firebase_user:
            # Pure Firebase user - find or create Django user
            from django.contrib.auth.models import User
            user_phone = request.firebase_user.phone_number
            
            try:
                # Try to find existing Django user
                user_for_profile = User.objects.get(username=user_phone)
            except User.DoesNotExist:
                # Create Django user for compatibility
                user_for_profile = User.objects.create_user(
                    username=user_phone,
                    email=request.firebase_user.email or '',
                    first_name=request.firebase_user.display_name or ''
                )
                print(f"✅ Created Django user for Firebase user: {user_phone}")
        else:
            messages.error(request, 'Authentication error. Please log in again.')
            return redirect('login')
        
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(
            user=user_for_profile,
            defaults={
                'phone_number': user_phone,
                'balance': Decimal('100.00')  # Give ₱100 registration bonus
            }
        )
        
        if created:
            # Add registration bonus transaction for new Firebase users
            from myproject.models import Transaction
            Transaction.objects.create(
                user=user_for_profile,
                transaction_type='registration_bonus',
                status='completed',
                amount=Decimal('100.00'),
                description='Welcome bonus for new registration'
            )
            profile.registration_bonus_claimed = True
            profile.save()
            print(f"✅ Created UserProfile with ₱100 bonus for: {user_phone}")
        else:
            # Check if existing user needs registration bonus
            if not getattr(profile, 'registration_bonus_claimed', False) and profile.balance == Decimal('0.00'):
                # Give existing user the registration bonus
                profile.balance = Decimal('100.00')
                profile.registration_bonus_claimed = True
                profile.save()
                
                # Add registration bonus transaction
                from myproject.models import Transaction
                Transaction.objects.create(
                    user=user_for_profile,
                    transaction_type='registration_bonus',
                    status='completed',
                    amount=Decimal('100.00'),
                    description='Welcome bonus for new registration'
                )
                print(f"✅ Added ₱100 bonus to existing user: {user_phone}")
        
        print(f"💰 Current user balance: ₱{profile.balance}")

    except Exception as profile_error:
        print(f"❌ Error getting user profile: {profile_error}")
        messages.error(request, 'Unable to access your profile. Please try again.')
        return redirect('dashboard')

    try:
        recent_deposits = InvestmentTransaction.objects.filter(
            user=user_for_profile,
            transaction_type='deposit'
        ).order_by('-created_at')[:5]
    except Exception as e:
        print(f"⚠️ Error getting recent deposits: {e}")
        recent_deposits = []

    payment_methods = {
        'gcash_qr': {
            'name': 'GCash QR',
            'code': 'gcash',  # bank_code for GCash QR
            'payment_type': '1',  # payment_type for GCash QR
            'min_amount': Decimal('100.00'),
            'max_amount': Decimal('50000.00'),
            'enabled': True
        },
        'gcash_h5': {
            'name': 'GCash Mobile',
            'code': 'mya',  # bank_code for GCash H5
            'payment_type': '7',  # payment_type for GCash H5
            'min_amount': Decimal('100.00'),
            'max_amount': Decimal('50000.00'),
            'enabled': True
        },
        'paymaya': {
            'name': 'PayMaya Direct',
            'code': 'PMP',  # FIXED: bank_code for PayMaya Direct
            'payment_type': '3',  # FIXED: payment_type for PayMaya Direct
            'min_amount': Decimal('100.00'),
            'max_amount': Decimal('50000.00'),
            'enabled': True
        },
        # Backward compatibility mappings
        'gcash': {
            'name': 'GCash',
            'code': 'gcash',  # bank_code for GCash QR (default)
            'payment_type': '1',  # payment_type for GCash QR (default)
            'min_amount': Decimal('100.00'),
            'max_amount': Decimal('50000.00'),
            'enabled': True
        }
    }

    if request.method == "POST":
        amount = request.POST.get("amount")
        payment_method = request.POST.get("payment_method", "gcash")

        # Validate amount
        try:
            amount_decimal = Decimal(str(amount))
            if amount_decimal <= 0:
                raise ValueError("Invalid amount")
                
            if payment_method in payment_methods:
                method_config = payment_methods[payment_method]
                if amount_decimal < method_config['min_amount']:
                    raise ValueError(f"Minimum deposit for {method_config['name']} is ₱{method_config['min_amount']}")
                if amount_decimal > method_config['max_amount']:
                    raise ValueError(f"Maximum deposit for {method_config['name']} is ₱{method_config['max_amount']}")
        except (ValueError, TypeError) as e:
            messages.error(request, str(e))
            return render(request, "myproject/deposit.html", {
                'profile': profile,
                'recent_deposits': recent_deposits,
                'payment_methods': payment_methods
            })

        reference_id = f"DEP_{user_for_profile.id}_{int(timezone.now().timestamp())}"
        client_ip = get_client_ip(request)
        
        # Prepare URLs
        site_url = request.build_absolute_uri('/').rstrip('/')
        callback_url = f"{site_url}/api/galaxy/callback/"
        return_url = f"{site_url}/payment/processing/?order_id={reference_id}&amount={amount_decimal}&payment_method={payment_method}"

        try:
            with db_transaction.atomic():
                # Create investment transaction
                investment_transaction = InvestmentTransaction.objects.create(
                    user=user_for_profile,
                    transaction_type='deposit',
                    amount=amount_decimal,
                    status='pending',
                    reference_number=reference_id,
                    payment_method=payment_method.upper()
                )

                # Create payment transaction
                payment_transaction = PaymentTransaction.objects.create(
                    user=user_for_profile,
                    transaction_type='deposit',
                    amount=amount_decimal,
                    reference_id=reference_id,
                    status='pending',
                    payment_method=payment_method,
                    client_ip=client_ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
                )

                logger.info(f"Processing Galaxy payment for user {user_for_profile.id}, amount: {amount_decimal}")
                
                # Get bank code and payment type for Galaxy API
                bank_code = payment_methods[payment_method]['code']
                payment_type = payment_methods[payment_method]['payment_type']
                
                logger.info(f"Payment method selected: {payment_method}")
                logger.info(f"Payment method config: {payment_methods[payment_method]}")
                logger.info(f"Galaxy API parameters: bank_code={bank_code}, payment_type={payment_type}")
                
                # Call Galaxy API (no mobile number needed - will use default)
                api_result = galaxy_service.create_payment(
                    amount=amount_decimal,
                    order_id=reference_id,
                    bank_code=bank_code,
                    payment_type=payment_type,
                    callback_url=callback_url,  
                    return_url=return_url
                )
                
                logger.info(f"Galaxy API response: {json.dumps(api_result, indent=2, default=str)}")
                
                # Process Galaxy API response
                if api_result.get("status") == "1":  # Success
                    # Get redirect URL from Galaxy response
                    redirect_url = (api_result.get("redirect_url") or 
                                  api_result.get("qrcode_url") or 
                                  api_result.get("gcash_qr_url"))
                    
                    if redirect_url and redirect_url.strip():
                        # Update payment transaction with API response
                        payment_transaction.payment_url = redirect_url
                        payment_transaction.api_response_data = api_result
                        payment_transaction.save()

                        investment_transaction.external_reference = api_result.get("order_id", reference_id)
                        investment_transaction.save()

                        # Log success
                        create_payment_log(
                            payment_transaction,
                            'api_success',
                            f'Galaxy API SUCCESS: {payment_method.upper()} payment created for ₱{amount_decimal}',
                            api_result
                        )

                        messages.success(request, f'{payment_method.upper()} payment ready! Redirecting to payment gateway...')
                        logger.info(f"Redirecting user to Galaxy payment gateway: {redirect_url}")
                        return redirect(redirect_url)
                    else:
                        error_msg = "Galaxy API returned success but no payment URL provided"
                        logger.error(f"Galaxy API success but no redirect URL: {api_result}")
                else:
                    # API Error
                    error_msg = api_result.get('message', f'Galaxy API error - Status: {api_result.get("status")}')
                    logger.error(f"Galaxy API Error: {error_msg}")

                # Handle API errors
                create_payment_log(
                    payment_transaction,
                    'api_error',
                    f'Galaxy API failed: {error_msg}',
                    {'error': error_msg, 'response': api_result}
                )
                
                payment_transaction.status = 'failed'
                payment_transaction.notes = f"API Error: {error_msg}"
                payment_transaction.save()
                
                investment_transaction.status = 'failed'
                investment_transaction.save()
                
                messages.error(request, f"Payment gateway error: {error_msg}")
                
                return render(request, "myproject/deposit.html", {
                    'profile': profile,
                    'recent_deposits': recent_deposits,
                    'payment_methods': payment_methods,
                    'error': error_msg
                })

        except Exception as e:
            logger.error(f"Deposit process failed for user {user_for_profile.id}: {str(e)}")
            messages.error(request, f"An error occurred while processing your deposit: {str(e)}")
            
            return render(request, "myproject/deposit.html", {
                'profile': profile,
                'recent_deposits': recent_deposits,
                'payment_methods': payment_methods
            })

    return render(request, 'myproject/deposit.html', {
        'profile': profile,
        'recent_deposits': recent_deposits,
        'payment_methods': payment_methods
    })

def create_payment_log(transaction, log_type, message, data=None, user=None):
    """Create payment log entry"""
    try:
        PaymentLog.objects.create(
            transaction=transaction,
            log_type=log_type,
            message=message,
            data=data or {},
            created_by=user
        )
    except Exception as e:
        logger.error(f"Failed to create payment log: {str(e)}")

@csrf_exempt
def galaxy_callback_view(request):
    """Handle Galaxy API callback notifications - FIXED VERSION TO RETURN PROPER SUCCESS"""
    
    if request.method != 'POST':
        logger.warning("Galaxy callback received non-POST request")
        return HttpResponse("SUCCESS", content_type="text/plain", status=200)
    
    try:
        # Parse callback data
        if request.content_type == 'application/json':
            callback_data = json.loads(request.body)
        else:
            callback_data = dict(request.POST.items())
        
        logger.info(f"=== GALAXY CALLBACK RECEIVED ===")
        logger.info(f"Callback URL: {request.build_absolute_uri()}")
        logger.info(f"Callback Time: {timezone.now()}")
        logger.info(f"Callback Data: {callback_data}")
        logger.info(f"Request Headers: {dict(request.headers)}")
        logger.info(f"Request Body: {request.body}")
        
        # Extract Galaxy callback parameters according to docs
        merchant = callback_data.get('merchant')
        order_id = callback_data.get('order_id')
        amount = callback_data.get('amount')
        status = callback_data.get('status')
        message = callback_data.get('message', '')
        received_sign = callback_data.get('sign')
        
        if not all([merchant, order_id, amount, status, received_sign]):
            logger.error(f"Missing required Galaxy callback parameters: {callback_data}")
            # Galaxy API documentation suggests returning "SUCCESS" for any callback
            return HttpResponse("SUCCESS", content_type="text/plain", status=200)
        
        # Verify merchant
        if merchant != galaxy_service.merchant_id:
            logger.error(f"Invalid merchant in callback: {merchant}, expected: {galaxy_service.merchant_id}")
            # Return SUCCESS to avoid retries from wrong merchant
            return HttpResponse("SUCCESS", content_type="text/plain", status=200)
        
        # Verify signature
        signature_valid = galaxy_service.verify_callback_signature(callback_data)
        logger.info(f"Signature verification: {signature_valid}")
        
        if not signature_valid:
            logger.error(f"Invalid Galaxy callback signature. Received: {received_sign}")
            logger.error(f"Callback data for signature verification: {callback_data}")
            # Still return SUCCESS to avoid infinite retries
            return HttpResponse("SUCCESS", content_type="text/plain", status=200)
        
        try:
            with db_transaction.atomic():
                # Find payment transaction
                try:
                    payment_transaction = PaymentTransaction.objects.select_for_update().get(
                        reference_id=order_id
                    )
                    investment_transaction = InvestmentTransaction.objects.select_for_update().get(
                        reference_number=order_id
                    )
                    logger.info(f"Found transactions for order {order_id}")
                except (PaymentTransaction.DoesNotExist, InvestmentTransaction.DoesNotExist):
                    logger.error(f"Transaction not found for order_id: {order_id}")
                    # Return SUCCESS to avoid retries for non-existent orders
                    return HttpResponse("SUCCESS", content_type="text/plain", status=200)
                
                old_status = payment_transaction.status
                
                # Map Galaxy status to internal status according to docs
                # Galaxy docs: 5=success, 3=failure, 1=waiting, 2,6,10=in progress
                status_mapping = {
                    '5': 'completed',    # Success
                    5: 'completed',
                    '3': 'failed',       # Failed
                    3: 'failed',
                    '1': 'pending',      # Waiting
                    1: 'pending',
                    '2': 'processing',   # In progress
                    2: 'processing',
                    '6': 'processing',
                    6: 'processing',
                    '10': 'processing',
                    10: 'processing',
                    '0': 'failed'        # Error
                }
                
                new_status = status_mapping.get(status, 'pending')
                
                logger.info(f"Processing callback for order {order_id}: Galaxy status {status} -> Internal status {new_status}")
                logger.info(f"Galaxy message: {message}")
                
                # Update payment transaction
                payment_transaction.status = new_status
                payment_transaction.callback_data = callback_data
                
                if new_status == 'completed' and not payment_transaction.completed_at:
                    payment_transaction.completed_at = timezone.now()
                
                payment_transaction.save()
                
                # Update investment transaction
                investment_transaction.status = new_status
                investment_transaction.save()
                
                # Log callback
                create_payment_log(
                    payment_transaction,
                    'callback',
                    f'Galaxy callback - status changed from {old_status} to {new_status} (Galaxy status: {status}, message: {message})',
                    callback_data
                )
                
                logger.info(f"Transaction {order_id} updated: {old_status} -> {new_status}")
                
                # Handle balance updates
                if new_status == "completed" and old_status != "completed":
                    if payment_transaction.transaction_type == "deposit":
                        # Add to user balance
                        try:
                            profile = UserProfile.objects.select_for_update().get(user=payment_transaction.user)
                            old_balance = profile.balance
                            profile.balance += payment_transaction.amount
                            profile.save()
                            
                            logger.info(f"Updated user {payment_transaction.user.id} balance: ₱{old_balance} -> ₱{profile.balance} (+₱{payment_transaction.amount})")
                            
                            # Create notification
                            try:
                                from myproject.models import Notification
                                Notification.objects.create(
                                    user=payment_transaction.user,
                                    title='Deposit Completed',
                                    message=f'Your {payment_transaction.payment_method} deposit of ₱{payment_transaction.amount} has been completed successfully.',
                                    notification_type='deposit'
                                )
                                logger.info(f"Created notification for user {payment_transaction.user.id}")
                            except Exception as e:
                                logger.error(f"Failed to create notification: {str(e)}")
                        except UserProfile.DoesNotExist:
                            logger.error(f"UserProfile not found for user {payment_transaction.user.id}")
                            
                elif new_status == "failed" and old_status in ["pending", "processing"]:
                    # Handle failed transactions
                    logger.info(f"Payment failed for order {order_id}")
                    try:
                        from myproject.models import Notification
                        Notification.objects.create(
                            user=payment_transaction.user,
                            title='Payment Failed',
                            message=f'Your {payment_transaction.payment_method} payment of ₱{payment_transaction.amount} failed. Please try again or contact support.',
                            notification_type='deposit'
                        )
                    except Exception as e:
                        logger.error(f"Failed to create notification: {str(e)}")
                
                # CRITICAL: Return exactly "SUCCESS" as plain text (Galaxy API requirement)
                logger.info(f"=== CALLBACK PROCESSED SUCCESSFULLY ===")
                logger.info(f"Order: {order_id}")
                logger.info(f"Status: {old_status} -> {new_status}")
                logger.info(f"Returning: SUCCESS")
                logger.info(f"=== END CALLBACK PROCESSING ===")
                
                return HttpResponse("SUCCESS", content_type="text/plain", status=200)
                
        except Exception as e:
            logger.error(f"Database error in Galaxy callback for order {order_id}: {str(e)}")
            logger.exception("Full error details:")
            # Still return SUCCESS to avoid infinite retries
            return HttpResponse("SUCCESS", content_type="text/plain", status=200)
            
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in Galaxy callback: {str(e)}")
        return HttpResponse("SUCCESS", content_type="text/plain", status=200)
    except Exception as e:
        logger.error(f"Unexpected error in Galaxy callback: {str(e)}")
        logger.exception("Full error details:")
        return HttpResponse("SUCCESS", content_type="text/plain", status=200)

# Alias for callback - with enhanced debugging
@csrf_exempt
def payment_callback(request):
    """Alias for galaxy_callback_view with enhanced debugging"""
    logger.info("=== PAYMENT CALLBACK DEBUG START ===")
    logger.info(f"Method: {request.method}")
    logger.info(f"Content-Type: {request.content_type}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"URL: {request.build_absolute_uri()}")
    logger.info(f"Remote IP: {get_client_ip(request)}")
    
    if request.method == 'POST':
        logger.info(f"POST data: {request.POST}")
        logger.info(f"Body: {request.body}")
    elif request.method == 'GET':
        logger.info(f"GET data: {request.GET}")
    
    result = galaxy_callback_view(request)
    logger.info(f"Response content: {result.content}")
    logger.info(f"Response status: {result.status_code}")
    logger.info("=== PAYMENT CALLBACK DEBUG END ===")
    
    return result

@firebase_login_required
def payment_success(request):
    """Handle successful payment redirect from Galaxy"""
    order_id = request.GET.get('order_id')
    
    context = {
        'order_id': order_id,
        'message': 'Payment processed successfully! Please wait for confirmation.',
        'transaction': None  # Default value for template
    }
    
    if order_id:
        try:
            payment_transaction = PaymentTransaction.objects.get(reference_id=order_id)
            investment_transaction = InvestmentTransaction.objects.get(reference_number=order_id)
            
            # Use investment_transaction as the main 'transaction' object for the template
            context.update({
                'transaction': investment_transaction,  # This is what the template expects
                'payment_transaction': payment_transaction,
                'investment_transaction': investment_transaction,
                'amount': payment_transaction.amount,
                'payment_method': payment_transaction.payment_method
            })
        except (PaymentTransaction.DoesNotExist, InvestmentTransaction.DoesNotExist):
            logger.warning(f"Transaction not found for order_id: {order_id}")
            # Create a dummy transaction object for template compatibility
            from types import SimpleNamespace
            dummy_transaction = SimpleNamespace()
            dummy_transaction.reference_number = order_id or 'N/A'
            dummy_transaction.id = order_id or 'N/A'
            dummy_transaction.created_at = timezone.now()
            dummy_transaction.amount = Decimal('0.00')
            dummy_transaction.status = 'processing'
            dummy_transaction.transaction_type = 'deposit'
            dummy_transaction.payment_method = 'paymaya'
            dummy_transaction.fee = Decimal('0.00')
            dummy_transaction.description = 'Payment processed - awaiting confirmation'
            dummy_transaction.investment = None
            context['transaction'] = dummy_transaction
    else:
        # No order_id provided, create minimal dummy transaction
        from types import SimpleNamespace
        dummy_transaction = SimpleNamespace()
        dummy_transaction.reference_number = 'N/A'
        dummy_transaction.id = 'N/A'
        dummy_transaction.created_at = timezone.now()
        dummy_transaction.amount = Decimal('0.00')
        dummy_transaction.status = 'processing'
        dummy_transaction.transaction_type = 'deposit'
        dummy_transaction.payment_method = 'paymaya'
        dummy_transaction.fee = Decimal('0.00')
        dummy_transaction.description = 'Payment processed - awaiting confirmation'
        dummy_transaction.investment = None
        context['transaction'] = dummy_transaction
    
    return render(request, 'myproject/payment_success.html', context)

def payment_processing(request):
    """Show payment processing page with real-time verification"""
    order_id = request.GET.get('order_id')
    amount = request.GET.get('amount')
    payment_method = request.GET.get('payment_method', 'paymaya')
    
    context = {
        'order_id': order_id,
        'amount': amount,
        'payment_method': payment_method,
    }
    
    return render(request, 'myproject/payment_processing.html', context)

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

@firebase_login_required
def withdraw_view(request):
    """Withdraw view for users to request withdrawals"""
    try:
        # Try to get Django user first, fallback to Firebase user logic
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Django user exists
            user_for_profile = request.user
            user_phone = request.user.username
        elif hasattr(request, 'firebase_user') and request.firebase_user:
            # Pure Firebase user - find or create Django user
            from django.contrib.auth.models import User
            user_phone = request.firebase_user.phone_number
            
            try:
                # Try to find existing Django user
                user_for_profile = User.objects.get(username=user_phone)
            except User.DoesNotExist:
                # Create Django user for compatibility
                user_for_profile = User.objects.create_user(
                    username=user_phone,
                    email=request.firebase_user.email or '',
                    first_name=request.firebase_user.display_name or ''
                )
                print(f"✅ Created Django user for Firebase user: {user_phone}")
        else:
            messages.error(request, 'Authentication error. Please log in again.')
            return redirect('login')
        
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(
            user=user_for_profile,
            defaults={
                'phone_number': user_phone,
                'balance': Decimal('100.00')  # Give ₱100 registration bonus
            }
        )
        
        if created:
            # Add registration bonus transaction for new Firebase users
            from myproject.models import Transaction
            Transaction.objects.create(
                user=user_for_profile,
                transaction_type='registration_bonus',
                status='completed',
                amount=Decimal('100.00'),
                description='Welcome bonus for new registration'
            )
            profile.registration_bonus_claimed = True
            profile.save()
            print(f"✅ Created UserProfile with ₱100 bonus for: {user_phone}")
        else:
            # Check if existing user needs registration bonus
            if not getattr(profile, 'registration_bonus_claimed', False) and profile.balance == Decimal('0.00'):
                # Give existing user the registration bonus
                profile.balance = Decimal('100.00')
                profile.registration_bonus_claimed = True
                profile.save()
                
                # Add registration bonus transaction
                from myproject.models import Transaction
                Transaction.objects.create(
                    user=user_for_profile,
                    transaction_type='registration_bonus',
                    status='completed',
                    amount=Decimal('100.00'),
                    description='Welcome bonus for new registration'
                )
                print(f"✅ Added ₱100 bonus to existing user: {user_phone}")
        
        print(f"💰 Current user balance: ₱{profile.balance}")

    except Exception as profile_error:
        print(f"❌ Error getting user profile: {profile_error}")
        messages.error(request, 'Unable to access your profile. Please try again.')
        return redirect('dashboard')

    try:
        recent_withdrawals = InvestmentTransaction.objects.filter(
            user=user_for_profile,
            transaction_type='withdrawal'
        ).order_by('-created_at')[:5]
    except Exception as e:
        print(f"⚠️ Error getting recent withdrawals: {e}")
        recent_withdrawals = []

    if request.method == "POST":
        amount = request.POST.get("amount")
        withdrawal_method = request.POST.get("withdrawal_method", "bank_transfer")

        # Validate amount
        try:
            amount_decimal = Decimal(str(amount))
            if amount_decimal <= 0:
                raise ValueError("Invalid amount")
                
            # Check if user has sufficient balance
            if amount_decimal > profile.balance:
                raise ValueError("Insufficient balance")
                
            # Check minimum withdrawal amount
            if amount_decimal < Decimal('100.00'):
                raise ValueError("Minimum withdrawal amount is ₱100.00")
                
        except (ValueError, TypeError) as e:
            messages.error(request, str(e))
            return render(request, "myproject/withdraw.html", {
                'profile': profile,
                'recent_withdrawals': recent_withdrawals
            })

        reference_id = f"WIT_{user_for_profile.id}_{int(timezone.now().timestamp())}"

        try:
            with db_transaction.atomic():
                # Create investment transaction
                investment_transaction = InvestmentTransaction.objects.create(
                    user=user_for_profile,
                    transaction_type='withdrawal',
                    amount=amount_decimal,
                    status='pending',
                    reference_number=reference_id,
                    payment_method=withdrawal_method.upper()
                )

                # Create payment transaction
                payment_transaction = PaymentTransaction.objects.create(
                    user=user_for_profile,
                    transaction_type='withdrawal',
                    amount=amount_decimal,
                    reference_id=reference_id,
                    status='pending',
                    payment_method=withdrawal_method,
                    client_ip=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
                )

                # Temporarily deduct from user balance (will be reverted if withdrawal fails)
                profile.balance -= amount_decimal
                profile.save()

                logger.info(f"Withdrawal request created for user {user_for_profile.id}, amount: {amount_decimal}")

                # Log withdrawal request
                create_payment_log(
                    payment_transaction,
                    'withdrawal_request',
                    f'Withdrawal request created for ₱{amount_decimal}',
                    {'amount': str(amount_decimal), 'method': withdrawal_method}
                )

                messages.success(request, f'Withdrawal request for ₱{amount_decimal} has been submitted successfully. It will be processed within 24 hours.')
                
                return redirect('withdraw')

        except Exception as e:
            logger.error(f"Withdrawal request failed for user {user_for_profile.id}: {str(e)}")
            messages.error(request, f"An error occurred while processing your withdrawal: {str(e)}")
            
            return render(request, "myproject/withdraw.html", {
                'profile': profile,
                'recent_withdrawals': recent_withdrawals
            })

    return render(request, 'myproject/withdraw.html', {
        'profile': profile,
        'recent_withdrawals': recent_withdrawals
    })

@login_required
def check_payment_status(request):
    """AJAX endpoint to check payment status"""
    order_id = request.GET.get('order_id')
    
    if not order_id:
        return JsonResponse({'error': 'Missing order_id'}, status=400)
    
    try:
        payment_transaction = PaymentTransaction.objects.get(reference_id=order_id, user=request.user)
        
        # Optionally query Galaxy API for real-time status
        if request.GET.get('refresh') == '1':
            api_result = galaxy_service.query_transaction(order_id)
            if api_result.get('status') in ['1', '5', '3']:  # Valid Galaxy statuses
                # Update local status based on API response
                status_mapping = {'5': 'completed', '3': 'failed', '1': 'pending'}
                new_status = status_mapping.get(api_result.get('status'), 'pending')
                if payment_transaction.status != new_status:
                    payment_transaction.status = new_status
                    payment_transaction.save()
        
        return JsonResponse({
            'success': True,
            'status': payment_transaction.status,
            'amount': str(payment_transaction.amount),
            'payment_method': payment_transaction.payment_method,
            'created_at': payment_transaction.created_at.isoformat(),
            'completed_at': payment_transaction.completed_at.isoformat() if payment_transaction.completed_at else None
        })
        
    except PaymentTransaction.DoesNotExist:
        return JsonResponse({'error': 'Transaction not found'}, status=404)
    except Exception as e:
        logger.error(f"Error checking payment status: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@login_required
def transaction_history(request):
    """View for displaying transaction history"""
    transactions = PaymentTransaction.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'myproject/transaction_history.html', {
        'transactions': transactions
    })

@login_required
def payment_cancel(request):
    """Handle cancelled payment redirect from Galaxy"""
    order_id = request.GET.get('order_id')
    
    context = {
        'order_id': order_id,
        'message': 'Payment was cancelled.'
    }
    
    if order_id:
        try:
            payment_transaction = PaymentTransaction.objects.get(reference_id=order_id)
            payment_transaction.status = 'cancelled'
            payment_transaction.save()
            
            investment_transaction = InvestmentTransaction.objects.get(reference_number=order_id)
            investment_transaction.status = 'cancelled'
            investment_transaction.save()
            
            context.update({
                'payment_transaction': payment_transaction,
                'amount': payment_transaction.amount,
                'payment_method': payment_transaction.payment_method
            })
        except (PaymentTransaction.DoesNotExist, InvestmentTransaction.DoesNotExist):
            logger.warning(f"Transaction not found for order_id: {order_id}")
    
    return render(request, 'myproject/payment_cancel.html', context)

def payment_status_api(request, reference_id):
    """API endpoint to check payment status by reference ID"""
    try:
        payment_transaction = PaymentTransaction.objects.get(reference_id=reference_id)
        
        return JsonResponse({
            'success': True,
            'status': payment_transaction.status,
            'amount': str(payment_transaction.amount),
            'payment_method': payment_transaction.payment_method,
            'created_at': payment_transaction.created_at.isoformat(),
            'completed_at': payment_transaction.completed_at.isoformat() if payment_transaction.completed_at else None
        })
        
    except PaymentTransaction.DoesNotExist:
        return JsonResponse({'error': 'Transaction not found'}, status=404)
    except Exception as e:
        logger.error(f"Error checking payment status: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

def query_transaction(request, order_id):
    """Query transaction using Galaxy API"""
    try:
        api_result = galaxy_service.query_transaction(order_id)
        return JsonResponse(api_result)
    except Exception as e:
        logger.error(f"Error querying transaction: {str(e)}")
        return JsonResponse({'error': 'Query failed'}, status=500)

@csrf_exempt
def test_callback(request):
    """Test endpoint to verify callback URL is working and returns proper Galaxy response"""
    logger.info("=== TEST CALLBACK ENDPOINT ===")
    logger.info(f"Method: {request.method}")
    logger.info(f"URL: {request.build_absolute_uri()}")
    
    if request.method == 'POST':
        logger.info(f"POST data: {request.POST}")
        logger.info(f"Body: {request.body}")
        
        # Test with sample Galaxy callback data
        test_data = {
            'merchant': 'RodolfHitler',
            'order_id': 'TEST_123456',
            'amount': '300.0000',
            'status': '5',
            'message': '成功',
            'sign': 'test_signature'
        }
        
        # Return the same response as Galaxy callback
        logger.info("Returning SUCCESS response (same as Galaxy callback)")
        return HttpResponse("SUCCESS", content_type="text/plain", status=200)
    
    return JsonResponse({
        'status': 'success',
        'message': 'Callback URL is accessible',
        'method': request.method,
        'timestamp': timezone.now().isoformat(),
        'expected_response': 'SUCCESS (as plain text)',
        'galaxy_callback_url': request.build_absolute_uri().replace('/test/', '/galaxy/'),
        'data': dict(request.POST) if request.method == 'POST' else dict(request.GET)
    })

def merchant_balance(request):
    """Get merchant balance from Galaxy API"""
    try:
        # This would need to be implemented based on Galaxy API docs
        # For now, return a placeholder
        return JsonResponse({'balance': '0.00', 'currency': 'PHP'})
    except Exception as e:
        logger.error(f"Error getting merchant balance: {str(e)}")
        return JsonResponse({'error': 'Balance query failed'}, status=500)

@login_required
def manual_payment_verify(request):
    """Manual payment verification endpoint for admin use"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    order_id = request.POST.get('order_id')
    if not order_id:
        return JsonResponse({'error': 'Missing order_id'}, status=400)
    
    try:
        payment_transaction = PaymentTransaction.objects.get(reference_id=order_id)
        
        # Query Galaxy API for current status
        api_result = galaxy_service.query_transaction(order_id)
        
        return JsonResponse({
            'success': True,
            'local_status': payment_transaction.status,
            'api_result': api_result
        })
        
    except PaymentTransaction.DoesNotExist:
        return JsonResponse({'error': 'Transaction not found'}, status=404)
    except Exception as e:
        logger.error(f"Error in manual verification: {str(e)}")
        return JsonResponse({'error': 'Verification failed'}, status=500)