def register(request):
    """Pure Firebase registration - NO Django User creation"""
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
                last_10_digits = digits_only[-10:]
                if last_10_digits.startswith('9'):
                    clean_phone = '+63' + last_10_digits
                else:
                    clean_phone = '+63' + digits_only
            else:
                # Fallback: just add +63 to whatever digits we have
                clean_phone = '+63' + digits_only if digits_only else clean_phone
        
        print(f"🔥 Pure Firebase Registration - Phone: {clean_phone}")
        
        # Validate password confirmation
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'myproject/register.html')
        
        # Check Firebase availability
        try:
            if not FIREBASE_AVAILABLE:
                messages.error(request, 'Registration system unavailable. Please try again later.')
                return render(request, 'myproject/register.html')
            
            # Get Firebase app and database reference
            app = get_firebase_app()
            if hasattr(app, 'project_id') and app.project_id == "firebase-unavailable":
                messages.error(request, 'Registration system unavailable. Please try again later.')
                return render(request, 'myproject/register.html')
            
            # Create Firebase key
            firebase_key = clean_phone.replace('+', '').replace(' ', '').replace('-', '')
            
            # Get Firebase database reference
            ref = firebase_db.reference('/', app=app)
            users_ref = ref.child('users')
            
            # Check if phone number already exists in Firebase
            existing_user = users_ref.child(firebase_key).get()
            if existing_user:
                messages.error(request, 'Phone number already registered')
                return render(request, 'myproject/register.html')
            
            # Validate referral code if provided
            referrer_data = None
            if referral_code:
                referral_code = referral_code.strip().upper()
                print(f"🔍 Checking referral code: {referral_code}")
                
                # Search all Firebase users for matching referral code
                all_users = users_ref.get() or {}
                referrer_key = None
                
                for user_key, user_data in all_users.items():
                    if user_data and user_data.get('referral_code', '').upper() == referral_code:
                        referrer_key = user_key
                        referrer_data = user_data
                        break
                
                if not referrer_data:
                    print(f"❌ Invalid referral code: {referral_code}")
                    messages.error(request, f'Invalid referral code "{referral_code}". Please check and try again.')
                    return render(request, 'myproject/register.html', {'referral_code': referral_code})
                
                print(f"✅ Valid referral code found: {referral_code}")
            
            # Generate unique referral code for new user
            import random
            import string
            new_referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            # Ensure referral code is unique
            while True:
                all_users = users_ref.get() or {}
                code_exists = any(
                    user_data and user_data.get('referral_code') == new_referral_code
                    for user_data in all_users.values()
                    if user_data
                )
                if not code_exists:
                    break
                new_referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            # Hash password
            import hashlib
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Create new user data for Firebase
            user_data = {
                'phone_number': clean_phone,
                'password': hashed_password,
                'balance': 100.00,  # Registration bonus
                'registration_bonus_claimed': True,
                'registration_bonus_amount': 100.00,
                'account_type': 'standard',
                'status': 'active',
                'account_status': 'active',
                'referral_code': new_referral_code,
                'referred_by': referrer_data.get('phone_number') if referrer_data else None,
                'referred_by_code': referral_code if referral_code else None,
                'total_referrals': 0,
                'referral_earnings': 0.0,
                'date_joined': timezone.now().isoformat(),
                'created_at': timezone.now().isoformat(),
                'last_login': None,
                'login_count': 0,
                'is_online': False,
                'transactions': {
                    'registration_bonus': {
                        'amount': 100.00,
                        'type': 'registration_bonus',
                        'status': 'completed',
                        'date': timezone.now().isoformat()
                    }
                }
            }
            
            # Save user to Firebase
            users_ref.child(firebase_key).set(user_data)
            print(f"✅ User saved to Firebase: {clean_phone}")
            
            # Handle referral bonus for referrer
            if referrer_data and referrer_key:
                try:
                    referral_bonus = 15.00  # ₱15 referral bonus
                    
                    # Update referrer's data
                    referrer_new_balance = float(referrer_data.get('balance', 0)) + referral_bonus
                    referrer_total_referrals = int(referrer_data.get('total_referrals', 0)) + 1
                    referrer_earnings = float(referrer_data.get('referral_earnings', 0)) + referral_bonus
                    
                    users_ref.child(referrer_key).update({
                        'balance': referrer_new_balance,
                        'total_referrals': referrer_total_referrals,
                        'referral_earnings': referrer_earnings,
                        'last_referral_date': timezone.now().isoformat()
                    })
                    
                    # Add referral bonus transaction to referrer
                    referral_transaction_key = f"referral_bonus_{firebase_key}_{int(timezone.now().timestamp())}"
                    users_ref.child(referrer_key).child('transactions').child(referral_transaction_key).set({
                        'amount': referral_bonus,
                        'type': 'referral_bonus',
                        'status': 'completed',
                        'date': timezone.now().isoformat(),
                        'from_user': clean_phone,
                        'description': f'Referral bonus from {clean_phone}'
                    })
                    
                    print(f"💰 Referral bonus of ₱{referral_bonus} awarded to referrer")
                    
                except Exception as referral_error:
                    print(f"❌ Error processing referral bonus: {referral_error}")
                    # Don't fail registration, just log the error
            
            # Create pure Firebase session for auto-login
            request.session['firebase_authenticated'] = True
            request.session['firebase_key'] = firebase_key
            request.session['user_phone'] = clean_phone
            request.session['is_authenticated'] = True
            request.session['firebase_user_data'] = user_data
            request.session['login_time'] = timezone.now().isoformat()
            request.session['login_method'] = 'firebase_registration'
            
            # Force session save
            request.session.save()
            
            print(f"🎉 Pure Firebase registration successful: {clean_phone}")
            success_msg = 'Registration successful! You received ₱100 bonus.'
            if referrer_data:
                success_msg += f' Your referrer earned a bonus too!'
            messages.success(request, success_msg + ' Welcome to GrowFi!')
            return redirect('dashboard')
            
        except Exception as e:
            print(f"❌ Pure Firebase registration error: {e}")
            import traceback
            traceback.print_exc()
            
            # Provide specific error messages
            if "already exists" in str(e).lower():
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
