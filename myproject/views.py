from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages 
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, Q, F, Count
from django.views.decorators.http import require_GET  # Added for deposits_withdrawals_api
from decimal import Decimal
from .models import *
import json
import uuid
import requests
import logging
import os  # Added missing import
from datetime import datetime, timedelta
import re  # for phone normalization
from django.views.decorators.csrf import csrf_exempt
from typing import Optional
import firebase_admin
from firebase_admin import credentials

# Set up logging    
logger = logging.getLogger(__name__)

# Safe Firebase imports
try:
    import firebase_admin
    from firebase_admin import credentials, auth as firebase_auth, db as firebase_db, firestore
    from .firebase_app import get_firebase_app  
    # Test if Firebase is actually working by trying to get the app
    try:
        test_app = get_firebase_app()
        # Check if we got a dummy app (indicates Firebase is unavailable)
        if hasattr(test_app, 'project_id') and test_app.project_id == "firebase-unavailable":
            FIREBASE_AVAILABLE = False
            print("❌ Firebase unavailable - dummy app detected")
        else:
            FIREBASE_AVAILABLE = True
            print("✅ Firebase connection test successful")
    except Exception as firebase_test_error:
        print(f"❌ Firebase connection test failed: {firebase_test_error}")
        print("⚠️ Firebase disabled - registration will continue without Firebase")
        FIREBASE_AVAILABLE = False
except ImportError as e:
    print(f"Firebase not available: {e}")
    FIREBASE_AVAILABLE = False

print(f"🔥 Firebase Status: {'✅ Available' if FIREBASE_AVAILABLE else '❌ Unavailable'}")

def _build_deposit_withdrawal_feed(limit: int, minutes: int, user=None):
    """Internal helper to build masked recent deposit/withdrawal list.
    
    WARNING: This function can expose ALL users' data if user parameter is not provided!
    Always pass a user parameter to filter data properly.
    """
    from django.utils import timezone as _tz
    since = _tz.now() - timedelta(minutes=minutes)
    
    if user and user.is_authenticated:
        # SECURITY: Only show current user's transactions
        qs = (Transaction.objects.select_related('user')
              .filter(user=user, transaction_type__in=['deposit', 'withdrawal'], created_at__gte=since)
              .order_by('-created_at')[:limit])
    else:
        # SECURITY: For public API, return empty list to prevent data exposure
        # Note: Previously this exposed ALL users' data - major security violation!
        qs = Transaction.objects.none()

    def _normalize_phone(raw: str) -> str:
        if not raw:
            return ''
        digits = re.sub(r'\D', '', raw)
        if digits.startswith('63') and len(digits) >= 12:
            digits = '0' + digits[2:]
        elif digits.startswith('9') and len(digits) == 10:
            digits = '0' + digits
        return digits

    def mask_phone(raw: str) -> str:
        p = _normalize_phone(raw)
        if len(p) < 5:
            return p
        return f"{p[:2]}{'*' * (len(p)-5)}{p[-3:]}"

    results = []
    for tx in qs:
        user = tx.user  
        phone_raw = ''
        if hasattr(user, 'userprofile'):
            phone_raw = getattr(user.userprofile, 'phone_number', '') or getattr(user.userprofile, 'phone', '')
        if not phone_raw:
            phone_raw = user.get_username()
        results.append({
            'id': tx.id,
            'type': tx.transaction_type,
            'amount': float(tx.amount),
            'created_at': tx.created_at.isoformat(),
            'user': user.get_username(),  # username (likely phone) but keep masked version below
            'phone': mask_phone(phone_raw)
        })
    return results

@require_GET
@login_required  # SECURITY FIX: Now requires authentication
def deposits_withdrawals_api(request):
    """(Private) User's own masked recent deposits & withdrawals - SECURITY FIXED"""
    try:
        limit = int(request.GET.get('limit', 50))
        minutes = int(request.GET.get('minutes', 1440))
    except ValueError:
        limit, minutes = 50, 1440
    
    # SECURITY: Only get current user's data
    data = _build_deposit_withdrawal_feed(limit, minutes, user=request.user)
    return JsonResponse({'results': data, 'count': len(data), 'public': False})

@require_GET
@login_required
def private_deposits_withdrawals_api(request):
    """(Authenticated) User's own deposit/withdrawal data - SECURITY FIXED"""
    try:
        limit = int(request.GET.get('limit', 50))
        minutes = int(request.GET.get('minutes', 1440))
    except ValueError:
        limit, minutes = 50, 1440
    
    # SECURITY: Only get current user's data
    data = _build_deposit_withdrawal_feed(limit, minutes, user=request.user)
    return JsonResponse({'results': data, 'count': len(data), 'public': False})

def is_ajax(request):
    """Helper function to check if request is AJAX (for Django 4.0+)"""
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def _ensure_firebase_user(phone_number: Optional[str] = None, email: Optional[str] = None, display_name: Optional[str] = None):
    """Ensure a corresponding Firebase Auth user exists for this account.

    Creates a user with phone_number or email if not found. Safe to call repeatedly.
    """
    try:
        get_firebase_app()
    except Exception:
        return  # If Firebase Admin is not configured, skip silently

def save_user_to_firebase_realtime_db(user, phone_number, additional_data=None):
    """Save user data to both Firebase Realtime Database and Firestore with enhanced error handling"""
    if not FIREBASE_AVAILABLE:
        print("⚠️ Firebase not available, skipping user save")
        return False
        
    print(f"🔥 Starting Firebase save for user: {phone_number}")
    
    try:
        # Get Firebase app
        app = get_firebase_app()
        print(f"✅ Firebase app obtained: {type(app)}")
        
        # Check if we got a dummy app (Firebase unavailable)
        if hasattr(app, 'project_id') and app.project_id == "firebase-unavailable":
            print("❌ Firebase is unavailable - dummy app detected")
            return False
            
        # Get user profile for referral code
        try:
            profile = UserProfile.objects.get(user=user)
            referral_code = profile.referral_code
            referred_by_username = profile.referred_by.username if profile.referred_by else None
            balance = float(profile.balance) if profile.balance else 0.0
            print(f"✅ User profile data loaded: balance={balance}, referral_code={referral_code}")
        except UserProfile.DoesNotExist:
            print("⚠️ UserProfile not found, using default values")
            referral_code = None
            referred_by_username = None
            balance = 0.0
        
        # Prepare user data
        user_data = {
            'user_id': user.id,
            'username': user.username,
            'phone_number': phone_number,
            'email': user.email if user.email else "",
            'first_name': user.first_name if user.first_name else "",
            'last_name': user.last_name if user.last_name else "",
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else "",
            'is_active': user.is_active,
            'created_at': timezone.now().isoformat(),
            'updated_at': timezone.now().isoformat(),
            'referral_code': referral_code,
            'referred_by': referred_by_username,
            'balance': balance,
            'account_status': 'active',
            'platform': 'django_app'
        }
        
        # Add additional data if provided
        if additional_data:
            user_data.update(additional_data)
            print(f"✅ Additional data added: {list(additional_data.keys())}")
        
        # Clean phone number for Firebase key (remove +, spaces, etc.)
        firebase_key = phone_number.replace('+', '').replace(' ', '').replace('-', '')
        print(f"✅ Firebase key generated: {firebase_key}")
        
        # 1. Save to Firebase Realtime Database under 'users' node
        try:
            ref = firebase_db.reference('/', app=app)
            users_ref = ref.child('users')
            users_ref.child(firebase_key).set(user_data)
            print(f"✅ User data saved to Firebase Realtime Database: {firebase_key}")
        except Exception as rtdb_error:
            print(f"❌ Failed to save to Realtime Database: {rtdb_error}")
            # Continue with Firestore even if RTDB fails
        
        # 2. Save to Firestore collection 'users'
        try:
            db = firestore.client(app=app)
            firestore_user_data = user_data.copy()
            firestore_user_data['firebase_key'] = firebase_key
            firestore_user_data['created_at'] = firestore.SERVER_TIMESTAMP
            firestore_user_data['updated_at'] = firestore.SERVER_TIMESTAMP
            
            doc_ref = db.collection('users').document(firebase_key)
            doc_ref.set(firestore_user_data)
            print(f"✅ User data saved to Firestore: {firebase_key}")
        except Exception as firestore_error:
            print(f"❌ Failed to save to Firestore: {firestore_error}")
        
        # 3. Also save under 'referral_codes' node for easy lookup (Realtime DB)
        if referral_code:
            try:
                referral_ref = ref.child('referral_codes')
                referral_ref.child(referral_code).set({
                    'user_id': user.id,
                    'username': user.username,
                    'phone_number': phone_number,
                    'firebase_key': firebase_key,
                    'created_at': timezone.now().isoformat()
                })
                print(f"✅ Referral code saved to Firebase: {referral_code}")
            except Exception as ref_error:
                print(f"❌ Failed to save referral code: {ref_error}")
        
        print(f"🎉 Firebase save completed for user: {phone_number}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving user to Firebase: {e}")
        import traceback
        print(f"❌ Full traceback:")
        traceback.print_exc()
        return False


def update_user_in_firebase_realtime_db(user, phone_number, additional_data=None):
    """Update user data in both Firebase Realtime Database and Firestore"""
    if not FIREBASE_AVAILABLE:
        print("⚠️ Firebase not available, skipping user update")
        return False
        
    try:
        # Get Firebase app
        app = get_firebase_app()
        
        # Get Realtime Database reference
        ref = firebase_db.reference('/', app=app)
        
        # Get Firestore client
        db = firestore.client(app=app)
        
        # Prepare update data
        update_data = {
            'last_login': timezone.now().isoformat(),
            'updated_at': timezone.now().isoformat()
        }
        
        # Add additional data if provided
        if additional_data:
            update_data.update(additional_data)
        
        # Clean phone number for Firebase key
        firebase_key = phone_number.replace('+', '').replace(' ', '').replace('-', '')
        
        # 1. Update Firebase Realtime Database
        users_ref = ref.child('users')
        users_ref.child(firebase_key).update(update_data)
        print(f"✅ User data updated in Firebase Realtime Database: {firebase_key}")
        
        # 2. Update Firestore
        firestore_update_data = update_data.copy()
        firestore_update_data['updated_at'] = firestore.SERVER_TIMESTAMP
        
        doc_ref = db.collection('users').document(firebase_key)
        doc_ref.update(firestore_update_data)
        print(f"✅ User data updated in Firestore: {firebase_key}")
        
        # 3. Save login event to Firestore 'login_events' collection
        if 'last_login_time' in update_data:
            login_event = {
                'user_id': user.id,
                'phone_number': phone_number,
                'firebase_key': firebase_key,
                'login_time': firestore.SERVER_TIMESTAMP,
                'user_agent': additional_data.get('user_agent', '') if additional_data else '',
                'ip_address': additional_data.get('ip_address', '') if additional_data else ''
            }
            
            db.collection('login_events').add(login_event)
            print(f"✅ Login event saved to Firestore for user: {firebase_key}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating user in Firebase: {e}")
        import traceback
        traceback.print_exc()
        return False
        return True
        
    except Exception as e:
        print(f"❌ Error updating user in Firebase Realtime Database: {e}")
        return False

    try:
        if phone_number:
            try:
                firebase_auth.get_user_by_phone_number(phone_number)
                return
            except firebase_auth.UserNotFoundError:
                firebase_auth.create_user(phone_number=phone_number, display_name=display_name or '')
                return
        if email:
            try:
                firebase_auth.get_user_by_email(email)
                return
            except firebase_auth.UserNotFoundError:
                firebase_auth.create_user(email=email, display_name=display_name or '')
                return
    except Exception:
        # Do not break registration/login if Firebase call fails
        return


@csrf_exempt
def firebase_login(request):
    """Accept a Firebase ID token, verify it, and create/login a Django user.

    Request: POST JSON { idToken: string }
    Response: { success: bool, redirect: url } or { error }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        body = json.loads(request.body.decode('utf-8')) if request.body else {}
    except Exception:
        body = {}

    id_token = body.get('idToken') or request.POST.get('idToken')
    if not id_token:
        return JsonResponse({'error': 'Missing idToken'}, status=400)

    try:
        # Ensure app is initialized
        get_firebase_app()
        decoded = firebase_auth.verify_id_token(id_token)
        uid = decoded.get('uid')
        phone_number = decoded.get('phone_number')
        email = decoded.get('email')

        # Prefer phone as username if available, otherwise email, else uid
        username = None
        if phone_number:
            # Smart phone normalization for Philippine numbers
            clean_phone = phone_number.replace(' ', '').replace('-', '')
            if not clean_phone.startswith('+63'):
                # Remove all non-digits first
                digits_only = re.sub(r'\D', '', clean_phone)
                
                if digits_only.startswith('63') and len(digits_only) >= 12:
                    # 639xxxxxxxxx format
                    clean_phone = '+' + digits_only
                elif digits_only.startswith('09') and len(digits_only) == 11:
                    # 09xxxxxxxxx format - convert to +639xxxxxxxxx
                    clean_phone = '+63' + digits_only[1:]
                elif digits_only.startswith('099') and len(digits_only) == 12:
                    # 099xxxxxxxxx format - remove first two chars "09", keep "9xxxxxxxxx"
                    clean_phone = '+63' + digits_only[2:]  # Remove "09", keep rest
                elif digits_only.startswith('99') and len(digits_only) == 11:
                    # 99xxxxxxxxx format - remove first char "9", keep "9xxxxxxxxx"  
                    clean_phone = '+63' + digits_only[1:]  # Remove first "9", keep rest
                elif digits_only.startswith('9') and len(digits_only) == 10:
                    # 9xxxxxxxxx format - add +63
                    clean_phone = '+63' + digits_only
                elif len(digits_only) >= 10:
                    # Handle remaining edge cases by extracting the last 10 digits
                    last_10_digits = digits_only[-10:]
                    if last_10_digits.startswith('9'):
                        clean_phone = '+63' + last_10_digits
                    else:
                        # If doesn't start with 9, might be invalid, but try anyway
                        clean_phone = '+63' + digits_only
                else:
                    # Fallback: just add +63 to whatever digits we have
                    clean_phone = '+63' + digits_only if digits_only else clean_phone
            username = clean_phone
        elif email:
            username = email
        else:
            username = f"firebase:{uid}"

        # Get or create Django user
        user, created = User.objects.get_or_create(username=username, defaults={
            'email': email or '',
            'is_active': True,
        })

        # Ensure profile exists; give bonus on first creation only
        profile_created = False
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(
                user=user,
                phone_number=username if username.startswith('+') else ''
            )
            profile_created = True

        if created or profile_created:
            # Registration bonus
            from decimal import Decimal as _D
            profile.balance = (profile.balance or _D('0.00')) + _D('100.00')
            profile.registration_bonus_claimed = True
            profile.save()
            Transaction.objects.create(
                user=user,
                transaction_type='registration_bonus',
                amount=_D('100.00'),
                status='completed'
            )
            Notification.objects.create(
                user=user,
                title='Welcome to InvestPH!',
                message='You have received ₱100 registration bonus. Start investing now!',
                notification_type='system'
            )

        # Log the user into Django session
        login(request, user)
        return JsonResponse({'success': True, 'redirect': '/dashboard/'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def generate_gcash_payment_url(user, amount):
    """Generate GCash payment URL using real GCash number"""
    try:
        # Generate unique reference number
        reference_id = f"GROWFI_{user.id}_{int(datetime.now().timestamp())}"
        
        # GCash number removed for security
        gcash_number = "***HIDDEN***"  # Contact support for payment details
        recipient_name = "GrowFi Investment"
        
        # GCash deep link for mobile app (real payment)
        mobile_deep_link = f"gcash://pay?amount={amount}&mobile={gcash_number}&name={recipient_name}&message=GrowFi Deposit - {reference_id}"
        
        # Alternative deep link format
        alternative_link = f"gcash://send?amount={amount}&recipient={gcash_number}&recipient_name={recipient_name}&reference={reference_id}"
        
        # Web fallback URL (GCash web interface)
        # Example: call Galaxy API
        galaxy_response = call_galaxy_api(amount, reference_id)

        # Kunin ang redirect URL mula sa response
        redirect_url = galaxy_response.get("redirect_url")

        # Kung meron, gamitin yun; kung wala, fallback
        final_url = redirect_url if redirect_url else web_fallback        
                # Create our payment tracking page
        payment_page_url = f"/gcash/payment/?amount={amount}&reference={reference_id}&user={user.id}&gcash_number={gcash_number}"
        
        # Expiry time (15 minutes from now)
        expiry_time = (datetime.now() + timedelta(minutes=15)).isoformat()
        
        return {
            'checkout_url': payment_page_url,
            'deep_link': mobile_deep_link,
            'alternative_link': alternative_link,
            'web_fallback': web_fallback,
            'reference_id': reference_id,
            'expiry_time': expiry_time,
            'amount': float(amount),
            'gcash_number': gcash_number,
            'recipient_name': recipient_name
        }
        
    except Exception as e:
        raise Exception(f"Failed to generate GCash payment URL: {str(e)}")

def handle_gcash_webhook(request):
    """Handle GCash payment webhook notifications"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Verify webhook signature in production
            # signature = request.headers.get('X-GCash-Signature')
            # if not verify_webhook_signature(data, signature):
            #     return JsonResponse({'error': 'Invalid signature'}, status=400)
            
            reference_id = data.get('reference_id')
            status = data.get('status')  # 'success', 'failed', 'pending'
            amount = data.get('amount')
            gcash_reference = data.get('gcash_reference_number')
            
            if status == 'success':
                # Find the user and update their balance
                user_id = data.get('customer_info', {}).get('user_id')
                if user_id:
                    try:
                        user = User.objects.get(id=user_id)
                        profile = UserProfile.objects.get(user=user)
                        
                        # Create approved transaction
                        transaction = Transaction.objects.create(
                            user=user,
                            transaction_type='deposit',
                            amount=Decimal(str(amount)),
                            status='completed',
                            gcash_reference=gcash_reference,
                            reference_number=reference_id
                        )
                        
                        # Update user balance
                        profile.balance += Decimal(str(amount))
                        profile.save()
                        
                        # Create notification
                        Notification.objects.create(
                            user=user,
                            title='Deposit Successful',
                            message=f'Your GCash deposit of ₱{amount} has been successfully processed.',
                            notification_type='deposit'
                        )
                        
                        return JsonResponse({'status': 'success'})
                        
                    except User.DoesNotExist:
                        return JsonResponse({'error': 'User not found'}, status=404)
            
            return JsonResponse({'status': 'received'})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def index(request):
    """Homepage view"""
    try:
        investment_plans = InvestmentPlan.objects.filter(is_active=True)
        announcements = Announcement.objects.filter(is_active=True)[:5]
        context = {
            'investment_plans': investment_plans,
            'announcements': announcements,
        }
        return render(request, 'myproject/index.html', context)
    except Exception as e:
        print(f"Error in index view: {e}")
        # Return a simple context if there's an error
        context = {
            'investment_plans': [],
            'announcements': [],
        }
        return render(request, 'myproject/index.html', context)

def register(request):
    """User registration view"""
    if request.method == 'POST':
        phone = request.POST.get('phone', '')
        password = request.POST['password']
        confirm_password = request.POST.get('confirm_password', '')
        referral_code = request.POST.get('referral_code', '').strip()
        
        # Clean phone number - remove spaces and ensure +63 format
        clean_phone = phone.replace(' ', '').replace('-', '')
        
        # Smart phone normalization for Philippine numbers
        if not clean_phone.startswith('+63'):
            # Remove all non-digits first
            digits_only = ''.join(filter(str.isdigit, clean_phone))
            
            if digits_only.startswith('63') and len(digits_only) >= 12:
                # 639xxxxxxxxx format
                clean_phone = '+' + digits_only
            elif digits_only.startswith('09') and len(digits_only) == 11:
                # 09xxxxxxxxx format - convert to +639xxxxxxxxx
                clean_phone = '+63' + digits_only[1:]
            elif len(digits_only) >= 10:
                # Handle various formats by extracting the last 10 digits
                # This covers cases like 099xxxxxxxx, 99xxxxxxxx, etc.
                last_10_digits = digits_only[-10:]
                if last_10_digits.startswith('9'):
                    clean_phone = '+63' + last_10_digits
                else:
                    # If doesn't start with 9, might be invalid, but try anyway
                    clean_phone = '+63' + digits_only
            else:
                # Fallback: just add +63 to whatever digits we have
                clean_phone = '+63' + digits_only if digits_only else clean_phone
        
        # Validate password confirmation
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'myproject/register.html')
        
        # Check if phone number already exists
        if UserProfile.objects.filter(phone_number=clean_phone).exists():
            messages.error(request, 'Phone number already registered')
            return render(request, 'myproject/register.html')
        
        # Validate referral code if provided
        referrer = None
        if referral_code:
            try:
                # Clean the referral code input
                referral_code_original = referral_code
                referral_code = referral_code.strip().upper()
                
                # Enhanced Debug: Print everything about the referral code
                print(f"🔍 REFERRAL CODE DEBUG:")
                print(f"   Original input: '{referral_code_original}' (type: {type(referral_code_original)})")
                print(f"   After cleaning: '{referral_code}' (length: {len(referral_code)})")
                print(f"   Character codes: {[ord(c) for c in referral_code]}")
                
                # Check if the code has any non-printable characters
                printable_chars = ''.join(c for c in referral_code if c.isprintable())
                if printable_chars != referral_code:
                    print(f"   ⚠️ Found non-printable characters!")
                    referral_code = printable_chars
                    print(f"   After removing non-printable: '{referral_code}'")
                
                # Simple and efficient lookup with case-insensitive match
                referrer_profile = UserProfile.objects.filter(
                    referral_code__iexact=referral_code
                ).select_related('user').first()
                
                if referrer_profile:
                    referrer = referrer_profile.user
                    print(f"✅ Valid referral code found: {referral_code} from user {referrer.username}")
                else:
                    # Debug: Show available codes for troubleshooting
                    all_profiles = UserProfile.objects.exclude(
                        referral_code__isnull=True
                    ).exclude(
                        referral_code__exact=''
                    ).values_list('referral_code', flat=True)[:10]
                    
                    print(f"❌ No matching referral code found for: '{referral_code}'")
                    print(f"� Sample available referral codes: {list(all_profiles)}")
                    
                    messages.error(request, f'Invalid referral code "{referral_code}". Please check and try again.')
                    return render(request, 'myproject/register.html', {'referral_code': referral_code})
                            
            except Exception as e:
                print(f"❌ Error during referral code validation: {e}")
                import traceback
                traceback.print_exc()
                messages.error(request, 'Error validating referral code. Please try again.')
                return render(request, 'myproject/register.html', {'referral_code': referral_code})
        
        # Create user with phone as username
        try:
            user = User.objects.create_user(
                username=clean_phone,  # Use full phone as username
                password=password
            )
            
            # Create user profile with referral
            profile = UserProfile.objects.create(
                user=user,
                phone_number=clean_phone,
                referred_by=referrer  # Set the referrer
            )
            
            # Give registration bonus (100 pesos, non-withdrawable)
            profile.balance = Decimal('100.00')
            profile.registration_bonus_claimed = True
            profile.save()
            
            # Create registration bonus transaction
            Transaction.objects.create(
                user=user,
                transaction_type='registration_bonus',
                amount=Decimal('100.00'),
                status='completed'
            )
            
            # Handle referral bonus for referrer
            if referrer:
                try:
                    referral_bonus = Decimal('15.00')  # ₱15 referral bonus
                    referrer_profile = UserProfile.objects.get(user=referrer)
                    referrer_profile.balance += referral_bonus
                    referrer_profile.save()
                    
                    # Create referral commission record with enhanced error handling
                    commission = ReferralCommission.objects.create(
                        referrer=referrer,
                        referred_user=user,
                        investment=None,  # No investment for registration bonus
                        commission_rate=Decimal('5.00'),  # 5% commission rate for display
                        commission_amount=referral_bonus,
                        level=1,
                        commission_type='registration'  # Specify this is a registration bonus
                    )
                    print(f"✅ Referral commission created: ID={commission.id}")
                    
                    # Create referral bonus transaction
                    Transaction.objects.create(
                        user=referrer,
                        transaction_type='referral_bonus',
                        amount=referral_bonus,
                        status='completed'
                    )
                    
                    # Create notification for referrer
                    Notification.objects.create(
                        user=referrer,
                        title='Referral Bonus!',
                        message=f'You earned ₱{referral_bonus} for referring {clean_phone}',
                        notification_type='referral'
                    )
                    
                    print(f"💰 Referral bonus of ₱{referral_bonus} awarded to {referrer.username}")
                    
                except Exception as referral_error:
                    print(f"❌ Error creating referral commission: {referral_error}")
                    import traceback
                    traceback.print_exc()
                    # Don't fail the registration, just log the error
                    print("⚠️ Registration will continue without referral commission")
            
            # Create notification
            Notification.objects.create(
                user=user,
                title='Welcome to InvestPH!',
                message='You have received ₱100 registration bonus. Start investing now!',
                notification_type='system'
            )

            # 🔥 Save user data to Firebase Realtime Database
            firebase_data = {
                'balance': float(profile.balance),
                'registration_bonus_claimed': True,
                'registration_bonus_amount': 100.00,
                'account_type': 'standard',
                'status': 'active',
                'referred_by': referrer.username if referrer else None,
                'referrer_id': referrer.id if referrer else None,
                'referral_code': profile.referral_code,
                'total_referrals': 0,
                'referral_earnings': 0.0,
                'date_joined': user.date_joined.isoformat(),
                'user_id': user.id
            }
            save_user_to_firebase_realtime_db(user, clean_phone, firebase_data)
            
            # If there's a referrer, also update their Firebase data
            if referrer:
                try:
                    referrer_profile = UserProfile.objects.get(user=referrer)
                    # Update referrer's Firebase data with new referral count
                    referrer_referrals = User.objects.filter(userprofile__referred_by=referrer).count()
                    referrer_earnings = Transaction.objects.filter(
                        user=referrer,
                        transaction_type='referral_bonus',
                        status='completed'
                    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                    
                    referrer_firebase_data = {
                        'total_referrals': referrer_referrals,
                        'referral_earnings': float(referrer_earnings),
                        'balance': float(referrer_profile.balance),
                        'last_referral_date': timezone.now().isoformat(),
                        'new_referral': {
                            'phone': clean_phone,
                            'date': timezone.now().isoformat(),
                            'bonus_earned': float(referral_bonus)
                        }
                    }
                    update_user_in_firebase_realtime_db(referrer, referrer_profile.phone_number or referrer.username, referrer_firebase_data)
                    
                except UserProfile.DoesNotExist:
                    print(f"⚠️ Referrer profile not found for {referrer.username}")
                except Exception as e:
                    print(f"❌ Error updating referrer Firebase data: {e}")
            
            # Auto-login the user after registration
            print(f"🔐 Attempting to auto-login user: {clean_phone}")
            user = authenticate(request, username=clean_phone, password=password)
            print(f"🔐 Auto-login authentication result: {user}")
            
            if user is not None:
                login(request, user)
                print(f"✅ User auto-logged in successfully: {user.username}")
                
                # Update login time in Firebase
                update_user_in_firebase_realtime_db(user, clean_phone, {'login_count': 1})
                
                success_msg = 'Registration successful! You received ₱100 bonus.'
                if referrer:
                    success_msg += f' Your referrer ({referrer.username}) earned a bonus too!'
                messages.success(request, success_msg + ' Welcome to GrowFi!')
                return redirect('dashboard')
            else:
                print("❌ Auto-login failed")
                messages.success(request, 'Registration successful! You received ₱100 bonus.')
                return redirect('login')
            
        except Exception as e:
            print(f"❌ Registration error: {e}")
            import traceback
            traceback.print_exc()
            
            # Provide more specific error messages
            if "UNIQUE constraint failed" in str(e):
                messages.error(request, 'Phone number already registered. Please use a different number.')
            elif "referral" in str(e).lower():
                messages.error(request, 'Invalid referral code. Please check and try again.')
            else:
                messages.error(request, f'Registration failed: {str(e)}')
            
            return render(request, 'myproject/register.html', {'referral_code': referral_code})
    
    # Handle GET request with referral code from URL
    referral_code = request.GET.get('ref', '')
    context = {'referral_code': referral_code}
    return render(request, 'myproject/register.html', context)

def user_login(request):
    """Pure Firebase login - SOLVES 'Account not found' issue"""
    if request.method == 'POST':
        phone = request.POST.get('phone', '')
        password = request.POST.get('password', '')
        
        print(f"🔐 Firebase login attempt - Phone: {phone}")
        
        if not phone or not password:
            messages.error(request, 'Please enter both phone number and password.')
            return render(request, 'myproject/login.html')
        
        # Import Firebase auth here to avoid circular imports
        try:
            from firebase_auth import FirebaseAuth
            firebase_auth = FirebaseAuth()
            
            # Authenticate user with Firebase
            auth_result = firebase_auth.authenticate_user(phone, password)
            
            if auth_result['success']:
                # Create session for Firebase user
                user_data = auth_result['user_data']
                firebase_key = auth_result['firebase_key']
                
                # Set session data
                request.session['firebase_key'] = firebase_key
                request.session['user_phone'] = user_data.get('phone_number')
                request.session['login_time'] = timezone.now().isoformat()
                request.session['login_method'] = 'firebase_auth'
                request.session['user_balance'] = user_data.get('balance', 0)
                request.session['user_name'] = user_data.get('name', '')
                request.session['is_authenticated'] = True
                
                # Force session save
                request.session.save()
                
                print(f"✅ Firebase login successful: {phone}")
                messages.success(request, 'Welcome back! Logged in successfully.')
                return redirect('dashboard')
            else:
                print(f"❌ Firebase login failed: {auth_result['error']}")
                messages.error(request, auth_result['error'])
                
        except ImportError:
            print("❌ Firebase auth module not found")
            messages.error(request, 'Login system temporarily unavailable. Please try again.')
        except Exception as e:
            print(f"❌ Login error: {e}")
            messages.error(request, 'Login failed. Please try again.')
    
    return render(request, 'myproject/login.html')

@login_required
def dashboard(request):
    """Enhanced user dashboard view with improved session tracking and persistence"""  
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(
            user=request.user,
            phone_number=request.user.username
        )
    
    # 🔍 Enhanced session health check and automatic renewal
    session_info = {
        'session_key': request.session.session_key,
        'user_phone': request.session.get('user_phone', 'Unknown'),
        'login_time': request.session.get('login_time', 'Unknown'),
        'session_age': request.session.get_expiry_age(),
        'session_expires': request.session.get_expiry_date(),
        'user_id': request.session.get('user_id', 'Unknown'),
        'login_method': request.session.get('login_method', 'Unknown')
    }
    
    # Log session info for debugging
    print(f"📊 Dashboard access by {request.user.username}:")
    print(f"   Session Key: {session_info['session_key']}")
    print(f"   Session Age: {session_info['session_age']} seconds")
    print(f"   Expires: {session_info['session_expires']}")
    
    # Automatic session renewal if near expiry (less than 1 day left)
    if session_info['session_age'] and session_info['session_age'] < 86400:  # Less than 24 hours
        request.session.set_expiry(7 * 24 * 60 * 60)  # Extend for 7 more days
        print(f"🔄 Session automatically renewed for user: {request.user.username}")
    
    # Update session tracking data
    request.session['last_dashboard_access'] = timezone.now().isoformat()
    request.session['dashboard_access_count'] = request.session.get('dashboard_access_count', 0) + 1
    
    # Enhanced Firebase tracking with error handling
    try:
        firebase_data = {
            'last_dashboard_access': timezone.now().isoformat(),
            'is_online': True,
            'session_key_hash': hash(session_info['session_key']) if session_info['session_key'] else None,
            'session_age_seconds': session_info['session_age'],
            'dashboard_visits': request.session.get('dashboard_access_count', 1),
            'last_activity': timezone.now().isoformat(),
            'platform': 'web_django_dashboard',
            'user_agent_hash': hash(request.META.get('HTTP_USER_AGENT', ''))[:10] if request.META.get('HTTP_USER_AGENT') else None
        }
        
        # Non-blocking Firebase update
        update_user_in_firebase_realtime_db(request.user, request.user.username, firebase_data)
        print(f"🔥 Firebase dashboard tracking updated")
        
    except Exception as firebase_error:
        print(f"⚠️ Firebase dashboard update error (non-critical): {firebase_error}")
    
    # Get dashboard data with enhanced error handling
    try:
        active_investments = Investment.objects.filter(user=request.user, status='active')
        recent_transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')[:5]
        notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
        
        # Calculate total active investment
        total_active_investment = active_investments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        # Calculate total invested (all time)
        total_invested = Transaction.objects.filter(
            user=request.user,
            transaction_type='investment',
            status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        # Calculate total earnings (all time) - daily payouts + referral bonuses (WITHDRAWABLE)
        total_earnings = Transaction.objects.filter(
            user=request.user,
            transaction_type__in=['daily_payout', 'referral_bonus'],
            status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        # Calculate today's earnings
        today = timezone.now().date()
        today_earnings = Transaction.objects.filter(
            user=request.user,
            transaction_type__in=['daily_payout', 'referral_bonus'],
            status='completed',
            created_at__date=today
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        # Calculate withdrawable balance (earnings minus withdrawals)
        total_withdrawn = Transaction.objects.filter(
            user=request.user,
            transaction_type='withdrawal',
            status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        withdrawable_balance = total_earnings - total_withdrawn
        
        # Registration bonus (non-withdrawable)
        registration_bonus = Transaction.objects.filter(
            user=request.user,
            transaction_type='registration_bonus',
            status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        # Total balance = withdrawable + non-withdrawable bonus + deposits
        total_deposits = Transaction.objects.filter(
            user=request.user,
            transaction_type='deposit',
            status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        # Available balance = withdrawable + deposits + bonus - investments
        available_balance = withdrawable_balance + registration_bonus + total_deposits - total_invested
        
        # Update profile balance
        profile.balance = available_balance
        profile.total_invested = total_invested
        profile.total_earnings = total_earnings 
        profile.save()
        
        # Calculate performance analytics only if user has investments
        performance_analytics = None
        if active_investments.exists():
            # Calculate ROI (Return on Investment)
            if total_invested > 0:
                roi_percentage = ((total_earnings / total_invested) * 100)
            else:
                roi_percentage = 0
                
            # Calculate risk score based on diversification and investment amounts
            unique_plans = active_investments.values('plan').distinct().count()
            total_investments = active_investments.count()
            
            if total_investments >= 3 and unique_plans >= 2:
                risk_score = "Low"
                risk_percentage = 25
            elif total_investments >= 2:
                risk_score = "Medium"
                risk_percentage = 60
            else:
                risk_score = "High"
                risk_percentage = 85
                
            # Calculate diversification score
            if unique_plans >= 3:
                diversification = "Excellent"
            elif unique_plans >= 2:
                diversification = "Good"
            else:
                diversification = "Poor"
                
            # Calculate average daily earnings
            total_days = sum([inv.days_completed for inv in active_investments])
            if total_days > 0:
                avg_daily_earnings = total_earnings / total_days
            else:
                avg_daily_earnings = 0
                
            performance_analytics = {
                'roi_percentage': round(roi_percentage, 1),
                'risk_score': risk_score,
                'risk_percentage': risk_percentage,
                'diversification': diversification,
                'total_investments': total_investments,
                'unique_plans': unique_plans,
                'avg_daily_earnings': avg_daily_earnings,
                'days_invested': total_days,
            }
        
        # Add referral statistics to dashboard
        referred_users = User.objects.filter(userprofile__referred_by=request.user).select_related('userprofile')
        
        # Calculate team stats
        total_referrals = referred_users.count()
        active_referrals = referred_users.filter(is_active=True).count()
        
        # Calculate referral earnings
        referral_earnings = Transaction.objects.filter(
            user=request.user,
            transaction_type='referral_bonus',
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate team investment volume
        team_total_invested = 0
        for referred_user in referred_users:
            user_investments = Investment.objects.filter(user=referred_user, status='active')
            user_total_invested = user_investments.aggregate(total=Sum('amount'))['total'] or 0
            team_total_invested += user_total_invested
        
        # Enhanced context with session info for debugging
        context = {
            'profile': profile,
            'active_investments': active_investments,
            'recent_transactions': recent_transactions,
            'notifications': notifications,
            'total_active_investment': total_active_investment,
            'total_invested': total_invested,
            'total_earnings': total_earnings,
            'today_earnings': today_earnings,
            'withdrawable_balance': withdrawable_balance,
            'registration_bonus': registration_bonus,
            'available_balance': available_balance,
            'performance_analytics': performance_analytics,
            # Add referral statistics
            'total_referrals': total_referrals,
            'active_referrals': active_referrals,
            'referral_earnings': referral_earnings,
            'team_total_invested': team_total_invested,
            # Session info for debugging (in development only)
            'session_info': session_info if request.user.is_staff else None,
        }
        
        return render(request, 'myproject/dashboard.html', context)
        
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback context in case of errors
        context = {
            'profile': profile,
            'active_investments': [],
            'recent_transactions': [],
            'notifications': [],
            'total_active_investment': Decimal('0.00'),
            'total_invested': Decimal('0.00'),
            'total_earnings': Decimal('0.00'),
            'today_earnings': Decimal('0.00'),
            'withdrawable_balance': Decimal('0.00'),
            'registration_bonus': Decimal('0.00'),
            'available_balance': profile.balance,
            'performance_analytics': None,
            'total_referrals': 0,
            'active_referrals': 0,
            'referral_earnings': 0,
            'team_total_invested': 0,
            'error_message': 'Dashboard temporarily unavailable. Please refresh the page.',
        }
        
        return render(request, 'myproject/dashboard.html', context)

@login_required
def investment_plans(request):
    """Investment plans view"""
    plans = InvestmentPlan.objects.filter(is_active=True)
    if not plans.exists():
        # Auto-seed default plans if database just migrated and empty
        default_plans = [
            ('GROWFI 1', Decimal('1000.00'), Decimal('1000.00'), Decimal('0.00')),
            ('GROWFI 2', Decimal('2000.00'), Decimal('2000.00'), Decimal('0.00')),
            ('GROWFI 3', Decimal('6000.00'), Decimal('6000.00'), Decimal('0.00')),
            ('GROWFI 4', Decimal('10000.00'), Decimal('10000.00'), Decimal('0.00')),
            ('GROWFI 5', Decimal('20000.00'), Decimal('20000.00'), Decimal('0.00')),
            ('GROWFI 6', Decimal('30000.00'), Decimal('30000.00'), Decimal('0.00')),
        ]
        for name, min_amt, max_amt, rate in default_plans:
            InvestmentPlan.objects.create(
                name=name,
                minimum_amount=min_amt,
                maximum_amount=max_amt,
                daily_return_rate=Decimal('0.00'),  # Kept for consistency; display uses hardcoded values
                duration_days=30,
                is_active=True
            )
        plans = InvestmentPlan.objects.filter(is_active=True)
    return render(request, 'myproject/investment_plans.html', {'plans': plans})

@login_required
def make_investment(request, plan_id):
    """Make investment view"""
    plan = get_object_or_404(InvestmentPlan, id=plan_id, is_active=True)
    profile = UserProfile.objects.get(user=request.user)
    
    if request.method == 'POST':
        amount = Decimal(request.POST['amount'])
        
        # Validate amount
        if amount < plan.minimum_amount or amount > plan.maximum_amount:
            messages.error(request, f'Amount must be between ₱{plan.minimum_amount} and ₱{plan.maximum_amount}')
            return render(request, 'myproject/make_investment.html', {'plan': plan, 'profile': profile})
        
        # Check if user has enough balance
        if profile.balance < amount:
            messages.error(request, 'Insufficient balance')
            return render(request, 'myproject/make_investment.html', {'plan': plan, 'profile': profile})
        
        # Create investment
        investment = Investment.objects.create(
            user=request.user,
            plan=plan,
            amount=amount,
            end_date=timezone.now() + timezone.timedelta(days=plan.duration_days)
        )
        
        # Deduct balance
        profile.balance -= amount
        profile.total_invested += amount
        profile.save()
        
        # Create transaction record
        Transaction.objects.create(
            user=request.user,
            transaction_type='investment',
            amount=amount,
            status='completed'
        )
        
        # Create notification
        Notification.objects.create(
            user=request.user,
            title='Investment Created',
            message=f'Your investment of ₱{amount} has been created successfully.',
            notification_type='investment'
        )
        
        # Handle referral commission
        if profile.referred_by:
            commission_rate = Decimal('5.00')  # 5% commission
            commission_amount = (amount * commission_rate) / 100
            
            referrer_profile = UserProfile.objects.get(user=profile.referred_by)
            referrer_profile.balance += commission_amount
            referrer_profile.save()
            
            ReferralCommission.objects.create(
                referrer=profile.referred_by,
                referred_user=request.user,
                investment=investment,
                commission_rate=commission_rate,
                commission_amount=commission_amount,
                level=1,
                commission_type='investment'  # Specify this is an investment commission
            )
            
            Transaction.objects.create(
                user=profile.referred_by,
                transaction_type='referral_bonus',
                amount=commission_amount,
                status='completed'
            )
        
        messages.success(request, 'Investment created successfully!')
        return redirect('my_investments')
    
    return render(request, 'myproject/make_investment.html', {'plan': plan, 'profile': profile})

@login_required
def my_investments(request):
    """User investments view with enhanced calculations - SECURITY ENHANCED: Only shows current user's investments"""
    from django.db.models import Sum
    from django.utils import timezone
    from datetime import timedelta
    import logging
    
    # CRITICAL SECURITY: Double-check user authentication
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to view your investments.')
        return redirect('login')
    
    # SECURITY: Only get investments for the current authenticated user
    investments = Investment.objects.filter(user=request.user).order_by('-start_date')
    
    # Calculate enhanced investment data for each investment
    enhanced_investments = []
    for investment in investments:
        # Calculate days completed since investment started
        now = timezone.now()
        start_date = investment.start_date
        
        # Calculate actual days completed
        if investment.status == 'active':
            days_passed = (now - start_date).days
            days_completed = min(days_passed, investment.plan.duration_days)
        else:
            days_completed = investment.days_completed or 0
        
        # Update the investment object's days_completed
        if investment.days_completed != days_completed:
            investment.days_completed = days_completed
            investment.save()
        
        # Calculate total earned based on days completed
        daily_return = investment.daily_return or investment.plan.daily_profit
        total_earned = daily_return * Decimal(str(days_completed))
        
        # Update the investment's total_return if needed
        if investment.total_return != total_earned:
            investment.total_return = total_earned
            investment.save()
        
        # Calculate progress percentage
        if investment.plan.duration_days > 0:
            progress_percentage = min((days_completed / investment.plan.duration_days) * 100, 100)
        else:
            progress_percentage = 0
        
        # Calculate remaining days
        remaining_days = max(investment.plan.duration_days - days_completed, 0)
        
        # Check if investment should be completed
        if days_completed >= investment.plan.duration_days and investment.status == 'active':
            investment.status = 'completed'
            investment.save()
        
        # Add calculated properties to investment object
        investment.calculated_total_earned = total_earned
        investment.calculated_days_completed = days_completed
        investment.progress_percentage = progress_percentage
        investment.remaining_days = remaining_days
        investment.is_completed = investment.status == 'completed'
        
        enhanced_investments.append(investment)
    
    # SECURITY: Only calculate total for current user's investments
    total_invested = investments.aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate portfolio statistics
    total_earned = sum(inv.calculated_total_earned for inv in enhanced_investments)
    total_daily_return = sum(inv.daily_return or 0 for inv in enhanced_investments)
    active_investments_count = len([inv for inv in enhanced_investments if inv.status == 'active'])
    
    # Calculate average return rate
    if total_invested > 0:
        avg_return_rate = (total_daily_return / total_invested) * 100
    else:
        avg_return_rate = 0
    
    # SECURITY: Log access for audit trail
    logger = logging.getLogger(__name__)
    logger.info(f"User {request.user.id} ({request.user.username}) accessed their investments page. Found {investments.count()} investments, {active_investments_count} active.")
    
    context = {
        'investments': enhanced_investments,
        'total_invested': total_invested,
        'total_earned': total_earned,
        'total_daily_return': total_daily_return,
        'active_investments_count': active_investments_count,
        'avg_return_rate': round(avg_return_rate, 1),
    }
    
    return render(request, 'myproject/my_investments.html', context)
@login_required
@login_required
def transaction_history(request):
    """Transaction history view with filtering and pagination"""
    from django.core.paginator import Paginator
    
    # Base queryset
    transactions = Transaction.objects.filter(user=request.user)
    
    # Apply filters
    transaction_type = request.GET.get('type')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    if status:
        transactions = transactions.filter(status=status)
    
    if date_from:
        transactions = transactions.filter(created_at__date__gte=date_from)
    
    if date_to:
        transactions = transactions.filter(created_at__date__lte=date_to)
    
    # Order by most recent
    transactions = transactions.order_by('-created_at')
    
    # Calculate summary statistics (include all statuses, not just completed)
    all_user_transactions = Transaction.objects.filter(user=request.user)
    completed_transactions = all_user_transactions.filter(status='completed')
    
    # Calculate totals and counts
    deposits = completed_transactions.filter(transaction_type='deposit')
    withdrawals = completed_transactions.filter(transaction_type='withdrawal')
    investments = completed_transactions.filter(transaction_type='investment')
    earnings = completed_transactions.filter(transaction_type__in=['daily_payout', 'referral_bonus', 'registration_bonus'])
    
    summary = {
        'total_deposits': deposits.aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_withdrawals': withdrawals.aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_investments': investments.aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_earnings': earnings.aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_transactions': all_user_transactions.count(),
        'deposit_count': deposits.count(),
        'withdrawal_count': withdrawals.count(),
        'investment_count': investments.count(),
        'earning_count': earnings.count(),
    }
    
    # Pagination
    paginator = Paginator(transactions, 20)  # Show 20 transactions per page
    page_number = request.GET.get('page')
    transactions = paginator.get_page(page_number)
    
    context = {
        'transactions': transactions,
        'summary': summary,
    }
    
    return render(request, 'myproject/transaction_history.html', context)

@login_required
def notifications(request):
    """Notifications view"""
    try:
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        # Mark all as read
        notifications.update(is_read=True)
        return render(request, 'myproject/notifications.html', {'notifications': notifications})
    except Exception as e:
        print(f"Error in notifications view: {e}")
        import traceback
        traceback.print_exc()
        messages.error(request, 'Unable to load notifications at this time.')
        return redirect('dashboard')

@login_required
def notification_detail(request, notification_id):
    """Notification detail view"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return render(request, 'myproject/notification_detail.html', {'notification': notification})

@login_required
def profile(request):
    """User profile view"""
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(
            user=request.user,
            phone_number=request.user.username
        )
    
    # Get team statistics
    from django.db.models import Sum
    referred_users = User.objects.filter(userprofile__referred_by=request.user)
    total_referrals = referred_users.count()
    active_referrals = referred_users.filter(is_active=True).count()
    
    # Calculate referral earnings
    referral_earnings = Transaction.objects.filter(
        user=request.user,
        transaction_type='referral_bonus',
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    if request.method == 'POST':
        # Update profile information
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        profile.phone_number = request.POST.get('phone_number', '')
        profile.address = request.POST.get('address', '')
        
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        if 'valid_id' in request.FILES:
            profile.valid_id = request.FILES['valid_id']
        
        if 'proof_of_address' in request.FILES:
            profile.proof_of_address = request.FILES['proof_of_address']
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
    
    context = {
        'profile': profile,
        'total_referrals': total_referrals,
        'active_referrals': active_referrals,
        'referral_earnings': referral_earnings,
    }
    return render(request, 'myproject/profile.html', context)

@login_required
def referrals(request):
    """Referrals view"""
    profile = UserProfile.objects.get(user=request.user)
    referred_users = User.objects.filter(userprofile__referred_by=request.user)
    commissions = ReferralCommission.objects.filter(referrer=request.user)
    total_commission = commissions.aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0
    
    context = {
        'profile': profile,
        'referred_users': referred_users,
        'commissions': commissions,
        'total_commission': total_commission,
    }
    return render(request, 'myproject/referrals.html', context)

@login_required
def support(request):
    """Support ticket view"""
    tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        subject = request.POST['subject']
        description = request.POST['description']
        priority = request.POST.get('priority', 'medium')
        
        SupportTicket.objects.create(
            user=request.user,
            subject=subject,
            description=description,
            priority=priority
        )
        
        messages.success(request, 'Support ticket created successfully!')
        return redirect('support')
    
    return render(request, 'myproject/support.html', {'tickets': tickets})

@login_required
def ticket_detail(request, ticket_id):
    """Support ticket detail view"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
    
    if request.method == 'POST':
        message = request.POST['message']
        TicketReply.objects.create(
            ticket=ticket,
            user=request.user,
            message=message,
            is_staff_reply=False
        )
        messages.success(request, 'Reply added successfully!')
        return redirect('ticket_detail', ticket_id=ticket_id)
    
    return render(request, 'myproject/ticket_detail.html', {'ticket': ticket})

@login_required
def calculator(request):
    """Investment calculator view"""
    plans = InvestmentPlan.objects.filter(is_active=True)
    return render(request, 'myproject/calculator.html', {'plans': plans})

@login_required
def calculate_investment(request):
    """AJAX endpoint for investment calculation"""
    if request.method == 'POST':
        data = json.loads(request.body)
        amount = Decimal(str(data['amount']))
        plan_id = data['plan_id']
        
        try:
            plan = InvestmentPlan.objects.get(id=plan_id)
            daily_return = plan.daily_profit  # Use the plan's daily profit property
            total_return = plan.total_revenue  # Use the plan's total revenue property
            total_profit = plan.net_profit     # Use the plan's net profit property
            
            return JsonResponse({
                'daily_return': str(daily_return),
                'total_return': str(total_return),
                'total_profit': str(total_profit),
                'duration': plan.duration_days
            })
        except InvestmentPlan.DoesNotExist:
            return JsonResponse({'error': 'Plan not found'}, status=404)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def user_logout(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('login')

def about(request):
    """About page view"""
    return render(request, 'myproject/about.html')

def terms(request):
    """Terms and conditions view"""
    return render(request, 'myproject/terms.html')

def privacy(request):
    """Privacy policy view"""
    return render(request, 'myproject/privacy.html')

def contact(request):
    """Contact page view"""
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']
        
        # Create a support ticket for contact form
        if request.user.is_authenticated:
            SupportTicket.objects.create(
                user=request.user,
                subject=f"Contact Form: {subject}",
                description=f"From: {name} ({email})\n\n{message}",
                priority='medium'
            )
        
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact')
    
    return render(request, 'myproject/contact.html')

@login_required
def api_notification_count(request):
    """API endpoint to get notification count for current user"""
    try:
        profile = request.user.userprofile
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        return JsonResponse({
            'count': unread_count,
            'status': 'success'
        })
    except Exception as e:
        return JsonResponse({
            'count': 0,
            'status': 'error',
            'message': str(e)
        })

def gcash_webhook(request):
    """Handle GCash payment webhook notifications"""
    return handle_gcash_webhook(request)

@login_required
def deposit_success(request):
    """GCash deposit success page"""
    return render(request, 'myproject/deposit_success.html')

def gcash_payment_page(request):
    """GCash payment interface page"""
    amount = request.GET.get('amount', 0)
    reference_id = request.GET.get('reference', '')
    user_id = request.GET.get('user', '')
    
    try:
        amount = Decimal(amount)
        user = User.objects.get(id=user_id) if user_id else request.user
    except (ValueError, User.DoesNotExist):
        return redirect('deposit')
    
    # Generate deep link for mobile
    mobile_deep_link = f"gcash://send?amount={amount}&recipient_name=GrowFi&reference={reference_id}"
    
    # Calculate expiry time (15 minutes from now)
    expiry_time = (datetime.now() + timedelta(minutes=15)).isoformat()
    
    context = {
        'amount': amount,
        'reference_id': reference_id,
        'deep_link': mobile_deep_link,
        'expiry_time': expiry_time,
        'user': user,
    }
    
    return render(request, 'myproject/gcash_payment.html', context)

def payment_status_api(request, reference_id):
    """API endpoint to check payment status"""
    try:
        # Check Transaction model first
        transaction = Transaction.objects.filter(
            reference_number=reference_id,
            status='completed'
        ).first()
        
        if transaction:
            return JsonResponse({
                'success': True,
                'status': 'completed',
                'amount': str(transaction.amount),
                'timestamp': transaction.created_at.isoformat(),
                'reference_id': reference_id
            })
        
        # Check pending transactions
        pending_transaction = Transaction.objects.filter(
            reference_number=reference_id,
            status='pending'
        ).first()
        
        if pending_transaction:
            return JsonResponse({
                'success': True,
                'status': 'pending',
                'amount': str(pending_transaction.amount),
                'reference_id': reference_id
            })
            
        # Check PaymentTransaction model for LA2568 orders
        from payments.models import PaymentTransaction
        
        try:
            payment = PaymentTransaction.objects.get(reference_id=reference_id)
            
            # Map payment status to standard statuses
            status_mapping = {
                'pending': 'pending',
                'processing': 'pending', 
                'completed': 'completed',
                'success': 'completed',
                'failed': 'failed',
                'cancelled': 'failed',
                'expired': 'failed'
            }
            
            mapped_status = status_mapping.get(payment.status.lower(), 'pending')
            
            return JsonResponse({
                'success': True,
                'status': mapped_status,
                'reference_id': reference_id,
                'amount': str(payment.amount),
                'transaction_type': 'deposit',
                'timestamp': payment.created_at.isoformat() if hasattr(payment, 'created_at') else None
            })
            
        except PaymentTransaction.DoesNotExist:
            pass
        
        # No transaction found
        return JsonResponse({
            'success': True,
            'status': 'not_found',
            'reference_id': reference_id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'status': 'error',
            'error': str(e)
        }, status=500)

@csrf_exempt
def la2568_callback(request):
    """Handle LA2568 payment callbacks"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # Get callback data
        data = json.loads(request.body)
        logger.info(f"LA2568 callback received: {data}")
        
        # Required fields from LA2568
        order_id = data.get('order_id')
        status = data.get('status')
        amount = data.get('amount')
        signature = data.get('signature')
        
        if not all([order_id, status, amount, signature]):
            logger.error("Missing required fields in LA2568 callback")
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Verify signature
        from .la2568_api import LA2568API
        api = LA2568API()
        
        if not api.verify_callback_signature(data, signature):
            logger.error("Invalid signature in LA2568 callback")
            return JsonResponse({'error': 'Invalid signature'}, status=400)
        
        # Update payment status
        from payments.models import PaymentTransaction
        
        try:
            payment = PaymentTransaction.objects.get(reference_id=order_id)
            
            # Map LA2568 status to our status
            status_mapping = {
                'success': 'completed',
                'completed': 'completed', 
                'failed': 'failed',
                'pending': 'pending',
                'cancelled': 'failed'
            }
            
            new_status = status_mapping.get(status.lower(), 'pending')
            payment.status = new_status
            payment.save()
            
            # If completed, create transaction record
            if new_status == 'completed':
                user = payment.user if hasattr(payment, 'user') else None
                
                if user:
                    # Create transaction record
                    transaction = Transaction.objects.create(
                        user=user,
                        transaction_type='deposit',
                        amount=Decimal(str(amount)),
                        status='completed',
                        reference_number=order_id,
                        description=f'Deposit via LA2568 - Order {order_id}'
                    )
                    
                    # Update user balance
                    user.balance = F('balance') + Decimal(str(amount))
                    user.save()
                    
                    logger.info(f"Payment completed for order {order_id}, amount: {amount}")
            
            return JsonResponse({'success': True, 'status': new_status})
            
        except PaymentTransaction.DoesNotExist:
            logger.error(f"Payment transaction not found for order {order_id}")
            return JsonResponse({'error': 'Payment not found'}, status=404)
    
    except json.JSONDecodeError:
        logger.error("Invalid JSON in LA2568 callback")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
    except Exception as e:
        logger.error(f"Error processing LA2568 callback: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def detect_mobile_device(request):
    """Detect if user is on mobile device"""
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    mobile_agents = ['iphone', 'android', 'mobile', 'phone', 'tablet', 'ipad']
    return any(agent in user_agent for agent in mobile_agents)

@login_required
def deposit_success(request):
    """Success page after deposit completion"""
    order_id = request.GET.get('order_id')
    amount = request.GET.get('amount')
    
    if not order_id:
        messages.error(request, 'Invalid success page access.')
        return redirect('dashboard')
    
    context = {
        'order_id': order_id,
        'amount': Decimal(amount) if amount else None,
        'new_balance': request.user.balance
    }
    
    return render(request, 'myproject/deposit_success.html', context)

@login_required
def deposit_success(request):
    """Deposit success page"""
    order_id = request.GET.get('order_id')
    amount = request.GET.get('amount', '0')
    
    # Get the latest transaction for this user if order_id not provided
    if not order_id:
        latest_transaction = Transaction.objects.filter(
            user=request.user,
            transaction_type='deposit',
            status='completed'
        ).order_by('-created_at').first()
        
        if latest_transaction:
            order_id = latest_transaction.reference_number
            amount = latest_transaction.amount
    
    try:
        amount = Decimal(str(amount))
    except:
        amount = Decimal('0')
    
    context = {
        'order_id': order_id,
        'amount': amount,
        'new_balance': request.user.balance,
        'user': request.user
    }
    
    return render(request, 'myproject/deposit_success.html', context)
@login_required
def about(request):
    """About page"""
    return render(request, 'myproject/about.html')

@login_required  
def terms(request):
    """Terms page"""
    return render(request, 'myproject/terms.html')

@login_required
def privacy(request):
    """Privacy page"""
    return render(request, 'myproject/privacy.html')

@login_required
def contact(request):
    """Contact page"""
    return render(request, 'myproject/contact.html')

@login_required
def deposit_success(request):
    """Deposit success page"""
    return render(request, 'myproject/deposit_success.html')

@login_required
def gcash_payment_page(request):
    """GCash payment page"""
    reference_id = request.GET.get('reference_id', '')
    amount = request.GET.get('amount', '0')
    
    context = {
        'reference_id': reference_id,
        'amount': amount,
    }
    return render(request, 'myproject/gcash_payment.html', context)

@login_required
def bank_accounts(request):
    """Bank accounts management"""
    from .models import BankAccount
    
    accounts = BankAccount.objects.filter(user=request.user, is_active=True).order_by('-is_primary', 'account_name')
    
    context = {
        'accounts': accounts,
    }
    
    return render(request, 'myproject/bank_accounts.html', context)

@login_required
def add_bank_account(request):
    """Add new bank account"""
    from .models import BankAccount
    
    if request.method == 'POST':
        try:
            account_type = request.POST.get('payment_type')
            account_name = request.POST.get('account_name')
            account_number = request.POST.get('account_number')
            is_primary = request.POST.get('is_primary') == 'on'
            
            # Validate required fields
            if not account_type:
                raise ValueError('Payment type is required')
            if not account_name:
                raise ValueError('Account name is required')
            if not account_number:
                raise ValueError('Account number is required')
            
            # Check for duplicate account
            existing_account = BankAccount.objects.filter(
                user=request.user,
                account_type=account_type,
                account_number=account_number
            ).first()
            
            if existing_account:
                raise ValueError('This account already exists')
            
            # If this is set as primary, remove primary from other accounts
            if is_primary:
                BankAccount.objects.filter(user=request.user).update(is_primary=False)
            
            # Create new account
            account = BankAccount.objects.create(
                user=request.user,
                account_type=account_type,
                account_name=account_name,
                account_number=account_number,
                is_primary=is_primary,
                is_active=True
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Bank account added successfully!',
                    'account_id': account.id
                })
            else:
                messages.success(request, 'Bank account added successfully!')
                return redirect('bank_accounts')
                
        except Exception as e:
            error_message = str(e) if str(e) else 'Failed to add account'
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': error_message
                })
            else:
                messages.error(request, f'Error adding bank account: {error_message}')
                return redirect('bank_accounts')
    
    # Handle non-POST requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': False,
            'error': 'Invalid request method'
        })
    else:
        return redirect('bank_accounts')

@login_required
def delete_bank_account(request, account_id):
    """Delete bank account"""
    from .models import BankAccount
    
    if request.method == 'POST':
        try:
            account = BankAccount.objects.get(id=account_id, user=request.user)
            account.is_active = False
            account.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Bank account deleted successfully!'
            })
            
        except BankAccount.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Bank account not found.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method.'
    })

@login_required
def set_primary_account(request, account_id):
    """Set account as primary"""
    from .models import BankAccount
    
    if request.method == 'POST':
        try:
            # Remove primary from all accounts
            BankAccount.objects.filter(user=request.user).update(is_primary=False)
            
            # Set new primary
            account = BankAccount.objects.get(id=account_id, user=request.user, is_active=True)
            account.is_primary = True
            account.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Primary account updated successfully!'
            })
            
        except BankAccount.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Bank account not found.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method.'
    })

@login_required
def api_notification_count(request):
    """API endpoint for notification count"""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})

@login_required  
def gcash_webhook(request):
    """GCash webhook handler"""
    if request.method == 'POST':
        try:
            # Handle GCash webhook data
            data = json.loads(request.body)
            reference_id = data.get('reference_id')
            status = data.get('status')
            
            # Update transaction status
            if reference_id and status:
                Transaction.objects.filter(
                    reference_number=reference_id
                ).update(status=status)
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})

@login_required
def team(request):
    """Team/Referral System view"""
    from django.db.models import Sum, Count
    
    profile = UserProfile.objects.get(user=request.user)
    
    # Get referral statistics
    referred_users = User.objects.filter(userprofile__referred_by=request.user).select_related('userprofile')
    
    # Calculate team stats
    total_referrals = referred_users.count()
    # Count users who are still active (Django's built-in is_active field)
    active_referrals = referred_users.filter(is_active=True).count()
    
    # Calculate referral earnings
    referral_earnings = Transaction.objects.filter(
        user=request.user,
        transaction_type='referral_bonus',
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Get recent referral activities
    recent_referrals = referred_users.order_by('-date_joined')[:10]
    
    # Calculate team investment stats
    team_total_invested = 0
    team_total_earnings = 0
    
    for referred_user in referred_users:
        user_investments = Investment.objects.filter(user=referred_user, status='active')
        user_total_invested = user_investments.aggregate(total=Sum('amount'))['total'] or 0
        team_total_invested += user_total_invested
        
        user_earnings = Transaction.objects.filter(
            user=referred_user,
            transaction_type='daily_payout',
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        team_total_earnings += user_earnings
    
    context = {
        'profile': profile,
        'referral_code': profile.referral_code,
        'total_referrals': total_referrals,
        'active_referrals': active_referrals,
        'referral_earnings': referral_earnings,
        'recent_referrals': recent_referrals,
        'team_total_invested': team_total_invested,
        'team_total_earnings': team_total_earnings,
        'referral_link': f"{request.scheme}://{request.get_host()}/register/?ref={profile.referral_code}",
    }
    
    return render(request, 'myproject/team.html', context)

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Transaction
from django.utils import timezone
from datetime import timedelta
import random

@require_http_methods(["GET"])
@login_required
def recent_activities_api(request):
    """API endpoint to get current user's recent activities for notifications"""
    
    # SECURITY FIX: Get only current user's recent transactions from last 24 hours
    yesterday = timezone.now() - timedelta(days=1)
    recent_transactions = Transaction.objects.filter(
        user=request.user,  # Only current user's transactions
        created_at__gte=yesterday,
        status='completed'
    ).order_by('-created_at')[:20]
    
    activities = []
    
    def _normalize_phone(raw: str) -> str:
        if not raw:
            return ''
        digits = re.sub(r'\D', '', raw)
        if digits.startswith('63') and len(digits) >= 12:
            digits = '0' + digits[2:]
        elif digits.startswith('9') and len(digits) == 10:
            digits = '0' + digits
        return digits

    def mask_phone(raw: str) -> str:
        p = _normalize_phone(raw)
        if len(p) < 5:
            return p
        middle_len = len(p) - 5
        return f"{p[:2]}{'*' * middle_len}{p[-3:]}"

    for transaction in recent_transactions:
        user_phone = None
        if hasattr(transaction.user, 'userprofile'):
            user_phone = getattr(transaction.user.userprofile, 'phone_number', None) or getattr(transaction.user.userprofile, 'phone', None)
        if not user_phone:
            user_phone = transaction.user.username
        activities.append({
            'type': transaction.transaction_type,
            'amount': float(transaction.amount),
            'phone': mask_phone(user_phone),
            'time': transaction.created_at.strftime('%H:%M')
        })
    
    # If no real transactions, add some sample ones
    if not activities:
        sample_phones = ["09123456789", "09234567890", "09345678901", "09456789012", "09567890123", "09678901234"]
        for _type in ['deposit', 'withdrawal', 'investment', 'earning']:
            raw_phone = random.choice(sample_phones)
            activities.append({
                'type': _type,
                'amount': float(random.randint(1000, 5000)),
                'phone': mask_phone(raw_phone),
                'time': timezone.now().strftime('%H:%M')
            })
    
    return JsonResponse({
        'activities': activities,
        'count': len(activities)
    })

@require_http_methods(["GET"])
@login_required  # Add login required decorator
def recent_investments_api(request):
    """API endpoint to get user's own recent investments for dashboard"""
    try:
        # SECURITY FIX: Only get current user's investments
        recent_investments = Investment.objects.filter(
            user=request.user
        ).select_related('plan').order_by('-start_date')[:5]
        
        investments_data = []
        for investment in recent_investments:
            investments_data.append({
                'id': investment.id,
                'user_name': investment.user.username,  # This will always be current user now
                'plan_name': investment.plan.name,
                'amount': float(investment.amount),
                'status': investment.status,
                'created_at': investment.start_date.strftime('%Y-%m-%d %H:%M'),
                'expected_return': float(investment.total_return) if investment.total_return else 0,
            })
        
        return JsonResponse({
            'success': True,
            'investments': investments_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
