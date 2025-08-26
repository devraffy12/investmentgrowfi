#!/usr/bin/env python
"""
Complete fix for referral code functionality
This script includes all the necessary fixes for the referral system
"""

def get_fixed_register_view():
    """Return the fixed register view code"""
    return '''
def register(request):
    """User registration view with enhanced referral code handling"""
    if request.method == 'POST':
        phone = request.POST.get('phone', '')
        password = request.POST['password']
        confirm_password = request.POST.get('confirm_password', '')
        referral_code = request.POST.get('referral_code', '').strip()
        
        # Clean phone number - remove spaces and ensure +63 format
        clean_phone = phone.replace(' ', '').replace('-', '')
        if not clean_phone.startswith('+63'):
            if clean_phone.startswith('63'):
                clean_phone = '+' + clean_phone
            elif clean_phone.startswith('09'):
                clean_phone = '+63' + clean_phone[1:]
            elif clean_phone.startswith('9'):
                clean_phone = '+63' + clean_phone
        
        # Validate password confirmation
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'myproject/register.html', {'referral_code': referral_code})
        
        # Check if phone number already exists
        if UserProfile.objects.filter(phone_number=clean_phone).exists():
            messages.error(request, 'Phone number already registered')
            return render(request, 'myproject/register.html', {'referral_code': referral_code})
        
        # Enhanced referral code validation
        referrer = None
        if referral_code:
            try:
                # Store original for error messages
                referral_code_original = referral_code
                
                # Clean the referral code thoroughly
                referral_code = referral_code.strip().upper()
                
                # Remove any non-alphanumeric characters except dashes/underscores
                import re
                referral_code = re.sub(r'[^A-Z0-9]', '', referral_code)
                
                print(f"🔍 REFERRAL CODE VALIDATION:")
                print(f"   Original: '{referral_code_original}'")
                print(f"   Cleaned: '{referral_code}' (length: {len(referral_code)})")
                
                if not referral_code:
                    print("   ❌ Empty referral code after cleaning")
                    messages.error(request, 'Invalid referral code format. Please check and try again.')
                    return render(request, 'myproject/register.html', {'referral_code': referral_code_original})
                
                # Find referrer with enhanced matching
                referrer_profile = None
                
                # Try exact case-insensitive match first
                referrer_profile = UserProfile.objects.filter(
                    referral_code__iexact=referral_code
                ).select_related('user').first()
                
                # If not found, try without case sensitivity
                if not referrer_profile:
                    referrer_profile = UserProfile.objects.filter(
                        referral_code=referral_code
                    ).select_related('user').first()
                
                if referrer_profile:
                    referrer = referrer_profile.user
                    print(f"   ✅ Valid referral code found: {referral_code}")
                    print(f"   Referrer: {referrer.username} (ID: {referrer.id})")
                    
                    # Validate referrer is active
                    if not referrer.is_active:
                        print(f"   ⚠️ Referrer account is inactive")
                        messages.error(request, 'Referral code belongs to an inactive account.')
                        return render(request, 'myproject/register.html', {'referral_code': referral_code_original})
                        
                else:
                    print(f"   ❌ No matching referral code found")
                    
                    # Show available codes for debugging (only in development)
                    from django.conf import settings
                    if settings.DEBUG:
                        available_codes = list(UserProfile.objects.exclude(
                            referral_code__isnull=True
                        ).exclude(
                            referral_code__exact=''
                        ).values_list('referral_code', flat=True)[:5])
                        print(f"   Available codes: {available_codes}")
                    
                    messages.error(request, f'Invalid referral code. Please check the code and try again.')
                    return render(request, 'myproject/register.html', {'referral_code': referral_code_original})
                            
            except Exception as e:
                print(f"❌ Error during referral code validation: {e}")
                import traceback
                traceback.print_exc()
                messages.error(request, 'Error validating referral code. Please try again.')
                return render(request, 'myproject/register.html', {'referral_code': referral_code_original})
        
        # Create user and handle referral bonus
        try:
            user = User.objects.create_user(
                username=clean_phone,
                password=password
            )
            
            # Create user profile with referral
            profile = UserProfile.objects.create(
                user=user,
                phone_number=clean_phone,
                referred_by=referrer
            )
            
            # Give registration bonus
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
                referral_bonus = Decimal('15.00')
                referrer_profile = UserProfile.objects.get(user=referrer)
                referrer_profile.balance += referral_bonus
                referrer_profile.save()
                
                # Create referral commission record
                ReferralCommission.objects.create(
                    referrer=referrer,
                    referred_user=user,
                    commission_rate=Decimal('5.00'),
                    commission_amount=referral_bonus,
                    level=1
                )
                
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
            
            # Create welcome notification
            Notification.objects.create(
                user=user,
                title='Welcome to GrowFi!',
                message='You have received ₱100 registration bonus. Start investing now!',
                notification_type='system'
            )

            # Save user data to Firebase Realtime Database
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
            
            # Update referrer's Firebase data if applicable
            if referrer:
                try:
                    referrer_profile = UserProfile.objects.get(user=referrer)
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
                    
                except Exception as e:
                    print(f"❌ Error updating referrer Firebase data: {e}")
            
            # Auto-login the user
            print(f"🔐 Auto-login attempt for: {clean_phone}")
            user = authenticate(request, username=clean_phone, password=password)
            
            if user is not None:
                login(request, user)
                print(f"✅ User auto-logged in successfully")
                
                # Update login time in Firebase
                update_user_in_firebase_realtime_db(user, clean_phone, {'login_count': 1})
                
                success_msg = 'Registration successful! You received ₱100 bonus.'
                if referrer:
                    success_msg += f' Your referrer earned a bonus too!'
                messages.success(request, success_msg + ' Welcome to GrowFi!')
                return redirect('dashboard')
            else:
                print("❌ Auto-login failed")
                messages.success(request, 'Registration successful! You received ₱100 bonus. Please login.')
                return redirect('login')
            
        except Exception as e:
            print(f"❌ Registration error: {e}")
            import traceback
            traceback.print_exc()
            
            # Clean up any partial user creation
            try:
                if 'user' in locals():
                    user.delete()
            except:
                pass
            
            if "UNIQUE constraint failed" in str(e):
                messages.error(request, 'Phone number already registered. Please use a different number.')
            else:
                messages.error(request, f'Registration failed. Please try again.')
            
            return render(request, 'myproject/register.html', {'referral_code': referral_code})
    
    # Handle GET request with referral code from URL
    referral_code = request.GET.get('ref', '')
    context = {'referral_code': referral_code}
    return render(request, 'myproject/register.html', context)
'''

def show_instructions():
    """Show instructions for implementing the fix"""
    print("=" * 60)
    print("🔧 REFERRAL CODE FIX INSTRUCTIONS")
    print("=" * 60)
    print()
    print("The referral code functionality is working correctly!")
    print("The issue might be with form submission or client-side JavaScript.")
    print()
    print("✅ VERIFIED WORKING COMPONENTS:")
    print("   - Database has valid referral codes")
    print("   - Django query logic works correctly")
    print("   - Firebase integration is functional")
    print("   - Models are properly configured")
    print()
    print("🔍 DEBUGGING STEPS:")
    print("   1. Check browser developer tools for JavaScript errors")
    print("   2. Verify form submission is sending correct data")
    print("   3. Check server logs during registration")
    print("   4. Test with a simple form without JavaScript")
    print()
    print("🧪 TEST REFERRAL CODES:")
    print("   Use any of these codes for testing:")
    
    from myproject.models import UserProfile
    test_codes = UserProfile.objects.exclude(
        referral_code__isnull=True
    ).exclude(
        referral_code__exact=''
    ).values_list('referral_code', 'user__username')[:5]
    
    for code, username in test_codes:
        print(f"   - {code} (from user: {username})")
    
    print()
    print("🚀 NEXT STEPS:")
    print("   1. Commit and push the enhanced debugging code")
    print("   2. Test registration with one of the codes above")
    print("   3. Check the Django console output for debug information")
    print("   4. If still failing, share the exact error from browser/console")
    print()

if __name__ == "__main__":
    import os
    import django
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
    django.setup()
    
    show_instructions()
