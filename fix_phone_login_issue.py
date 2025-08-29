#!/usr/bin/env python3
"""
Phone Login Persistence Fix
Fix the phone number format mismatch between login form and authentication system
"""
import os
import sys
import django
from datetime import datetime

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from myproject.models import UserProfile

def test_phone_login_issue():
    """Test the exact phone login issue described by the user"""
    print('🔍 TESTING PHONE LOGIN ISSUE')
    print('=' * 50)
    
    # Find a recent user to test with
    recent_user = User.objects.filter(date_joined__gte=datetime.now().replace(day=26)).first()
    
    if not recent_user:
        print("❌ No recent users found for testing")
        return
    
    print(f"🎯 Testing with user: {recent_user.username}")
    print(f"📅 Registered: {recent_user.date_joined}")
    
    # Test different phone input formats that users might enter
    user_phone = recent_user.username  # This is typically +639xxxxxxxxx
    
    # Extract the digits after +63
    if user_phone.startswith('+63'):
        mobile_digits = user_phone[3:]  # Get 9xxxxxxxxx
        
        # Test scenarios:
        test_scenarios = [
            {
                'name': 'User enters "9xxxxxxxxx" (what login form sends)',
                'phone_input': mobile_digits,  # 9xxxxxxxxx
                'description': 'Raw digits without +63 prefix'
            },
            {
                'name': 'User enters "09xxxxxxxxx"',
                'phone_input': '0' + mobile_digits,  # 09xxxxxxxxx  
                'description': 'Philippine format with 0 prefix'
            },
            {
                'name': 'User enters full "+639xxxxxxxxx"',
                'phone_input': user_phone,  # +639xxxxxxxxx
                'description': 'Full international format'
            },
            {
                'name': 'User enters "639xxxxxxxxx"',
                'phone_input': user_phone[1:],  # 639xxxxxxxxx (without +)
                'description': 'International format without +'
            }
        ]
        
        print(f"\n📱 User's registered phone: {user_phone}")
        print(f"📱 Mobile digits: {mobile_digits}")
        
        # Test authentication with common password
        test_password = '123456'  # Most users in our system use this
        
        for scenario in test_scenarios:
            print(f"\n🧪 {scenario['name']}")
            print(f"   Input: '{scenario['phone_input']}'")
            print(f"   Description: {scenario['description']}")
            
            # Test direct authentication
            auth_user = authenticate(username=scenario['phone_input'], password=test_password)
            
            if auth_user:
                print(f"   ✅ Authentication: SUCCESS")
            else:
                print(f"   ❌ Authentication: FAILED")
                
                # Check if user exists with this format
                try:
                    found_user = User.objects.get(username=scenario['phone_input'])
                    print(f"      👤 User found in database")
                    if found_user.check_password(test_password):
                        print(f"      🔑 Password is correct")
                        print(f"      🚨 AUTHENTICATION SYSTEM ISSUE!")
                    else:
                        print(f"      ❌ Password is incorrect")
                except User.DoesNotExist:
                    print(f"      👤 User NOT found with this username format")
        
        # Now test the current login view logic
        print(f"\n🔧 TESTING CURRENT LOGIN VIEW LOGIC")
        print('-' * 40)
        
        # Simulate what happens when user enters just the digits
        form_input = mobile_digits  # This is what the login form sends
        
        print(f"📝 Form sends: '{form_input}'")
        
        # Test the normalization logic from views.py
        def normalize_phone_number(raw_phone):
            """Copy of the normalization logic from views.py"""
            if not raw_phone:
                return ''
                
            # Remove all non-digit characters except +
            clean_phone = raw_phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            
            # If already in +63 format, return as is
            if clean_phone.startswith('+63'):
                return clean_phone
                
            # Extract digits only
            digits_only = ''.join(filter(str.isdigit, clean_phone))
            
            # Handle different Philippine number formats
            if digits_only.startswith('63') and len(digits_only) >= 12:
                # 639xxxxxxxxx format
                return '+' + digits_only
            elif digits_only.startswith('09') and len(digits_only) == 11:
                # 09xxxxxxxxx format - convert to +639xxxxxxxxx
                return '+63' + digits_only[1:]
            elif digits_only.startswith('9') and len(digits_only) == 10:
                # 9xxxxxxxxx format - add +63
                return '+63' + digits_only
            elif len(digits_only) >= 10:
                # Handle edge cases by extracting last 10 digits
                last_10_digits = digits_only[-10:]
                if last_10_digits.startswith('9'):
                    return '+63' + last_10_digits
                else:
                    # Try with full digits
                    return '+63' + digits_only
            
            # Fallback: return original if can't normalize
            return clean_phone
        
        normalized = normalize_phone_number(form_input)
        print(f"🔄 Normalized to: '{normalized}'")
        
        # Test if normalized format works
        auth_user = authenticate(username=normalized, password=test_password)
        if auth_user:
            print(f"✅ Normalized format authentication: SUCCESS")
        else:
            print(f"❌ Normalized format authentication: FAILED")
            
        # The issue might be that the view expects +63 but form sends just digits
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        print(f"   User registered with: {user_phone}")
        print(f"   Login form sends: {form_input}")
        print(f"   View normalizes to: {normalized}")
        
        if normalized == user_phone:
            print(f"   ✅ Normalization is correct")
        else:
            print(f"   ❌ Normalization mismatch!")
            print(f"   Expected: {user_phone}")
            print(f"   Got: {normalized}")

def fix_login_view():
    """Create the fix for the login view"""
    print(f"\n🔧 GENERATING LOGIN VIEW FIX")
    print('=' * 50)
    
    fix_code = '''
def user_login(request):
    """Fixed user login view with enhanced phone number handling"""
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        
        print(f"🔐 Login attempt - Phone: {phone}")
        
        # Enhanced phone number normalization and strategy generation
        def generate_phone_strategies(raw_phone):
            """Generate all possible phone number formats for authentication"""
            if not raw_phone:
                return []
                
            strategies = []
            
            # Add original input
            strategies.append(raw_phone)
            
            # Clean the input
            clean_phone = raw_phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            if clean_phone != raw_phone:
                strategies.append(clean_phone)
            
            # If it starts with +63, we have the full format
            if clean_phone.startswith('+63'):
                base_digits = clean_phone[3:]  # Remove +63
                strategies.extend([
                    clean_phone,                    # +639xxxxxxxxx
                    clean_phone[1:],               # 639xxxxxxxxx  
                    '0' + base_digits if base_digits.startswith('9') else '09' + base_digits,  # 09xxxxxxxxx
                    base_digits                     # 9xxxxxxxxx
                ])
            else:
                # Extract only digits
                digits_only = ''.join(filter(str.isdigit, clean_phone))
                
                if digits_only.startswith('63') and len(digits_only) >= 12:
                    # Format: 639xxxxxxxxx
                    mobile_part = digits_only[2:]  # Remove 63
                    strategies.extend([
                        '+' + digits_only,                    # +639xxxxxxxxx
                        digits_only,                          # 639xxxxxxxxx
                        '0' + mobile_part if mobile_part.startswith('9') else '09' + mobile_part,  # 09xxxxxxxxx
                        mobile_part                           # 9xxxxxxxxx
                    ])
                elif digits_only.startswith('09') and len(digits_only) == 11:
                    # Format: 09xxxxxxxxx
                    mobile_part = digits_only[1:]  # Remove 0
                    strategies.extend([
                        '+63' + mobile_part,                  # +639xxxxxxxxx
                        '63' + mobile_part,                   # 639xxxxxxxxx
                        digits_only,                          # 09xxxxxxxxx
                        mobile_part                           # 9xxxxxxxxx
                    ])
                elif digits_only.startswith('9') and len(digits_only) == 10:
                    # Format: 9xxxxxxxxx (most common from login form)
                    strategies.extend([
                        '+63' + digits_only,                  # +639xxxxxxxxx
                        '63' + digits_only,                   # 639xxxxxxxxx
                        '0' + digits_only,                    # 09xxxxxxxxx
                        digits_only                           # 9xxxxxxxxx
                    ])
                elif len(digits_only) >= 10:
                    # Handle other formats by extracting last 10 digits
                    last_10 = digits_only[-10:]
                    if last_10.startswith('9'):
                        strategies.extend([
                            '+63' + last_10,                  # +639xxxxxxxxx
                            '63' + last_10,                   # 639xxxxxxxxx
                            '0' + last_10,                    # 09xxxxxxxxx
                            last_10                           # 9xxxxxxxxx
                        ])
            
            # Remove duplicates while preserving order
            unique_strategies = []
            for strategy in strategies:
                if strategy and strategy not in unique_strategies:
                    unique_strategies.append(strategy)
            
            return unique_strategies
        
        # Generate all possible authentication strategies
        auth_strategies = generate_phone_strategies(phone)
        print(f"📱 Generated {len(auth_strategies)} phone format strategies")
        
        # Try authentication with each strategy
        authenticated_user = None
        successful_format = None
        
        for strategy in auth_strategies:
            print(f"🔍 Trying: {strategy}")
            user = authenticate(request, username=strategy, password=password)
            if user is not None:
                authenticated_user = user
                successful_format = strategy
                print(f"✅ Authentication successful with: {strategy}")
                break
        
        if authenticated_user is not None:
            # LOGIN SUCCESS
            login(request, authenticated_user)
            authenticated_user.last_login = timezone.now()
            authenticated_user.save()
            
            print(f"✅ User logged in: {authenticated_user.username}")
            
            # Ensure UserProfile exists and update
            try:
                profile = UserProfile.objects.get(user=authenticated_user)
                # Update phone to normalized format for consistency
                normalized_phone = auth_strategies[0] if auth_strategies[0].startswith('+63') else '+63' + phone if phone.startswith('9') else authenticated_user.username
                if profile.phone_number != normalized_phone:
                    profile.phone_number = normalized_phone
                    profile.save()
            except UserProfile.DoesNotExist:
                # Create profile with normalized phone
                normalized_phone = auth_strategies[0] if auth_strategies[0].startswith('+63') else '+63' + phone if phone.startswith('9') else authenticated_user.username
                profile = UserProfile.objects.create(
                    user=authenticated_user,
                    phone_number=normalized_phone
                )
            
            # Enhanced session management
            request.session['user_phone'] = profile.phone_number
            request.session['login_time'] = timezone.now().isoformat()
            request.session['user_id'] = authenticated_user.id
            request.session['login_method'] = 'django_auth_fixed'
            request.session['successful_format'] = successful_format
            request.session.save()
            
            # Update Firebase
            try:
                firebase_data = {
                    'last_login_time': timezone.now().isoformat(),
                    'balance': float(profile.balance),
                    'is_online': True,
                    'login_success': True,
                    'successful_phone_format': successful_format,
                    'login_method': 'django_auth_fixed'
                }
                update_user_in_firebase_realtime_db(authenticated_user, profile.phone_number, firebase_data)
            except Exception as e:
                print(f"⚠️ Firebase update failed: {e}")
            
            messages.success(request, 'Welcome back!')
            return redirect('dashboard')
        
        else:
            # LOGIN FAILED - Enhanced error handling
            print("❌ Authentication failed for all strategies")
            
            # Check if user exists with any of the formats
            user_found = None
            for strategy in auth_strategies:
                try:
                    user_found = User.objects.get(username=strategy)
                    print(f"👤 User found with format: {strategy}")
                    break
                except User.DoesNotExist:
                    continue
            
            if user_found:
                if not user_found.is_active:
                    messages.error(request, 'Account is deactivated. Please contact support.')
                else:
                    messages.error(request, 'Invalid password. Please check your password.')
            else:
                # User not found - check for similar numbers
                if len(phone) >= 8:
                    # Look for users with similar phone endings
                    search_digits = phone[-8:] if len(phone) >= 8 else phone
                    similar_users = User.objects.filter(username__contains=search_digits)[:3]
                    
                    if similar_users.exists():
                        messages.error(request, 'Account not found. Please check your phone number or register first.\\n\\nPakilagay ang iyong phone number sa format na nagsisimula sa +63 (halimbawa: +639123456789). Huwag gumamit ng 0 sa unahan')
                    else:
                        messages.error(request, 'Account not found. Please register first.\\n\\nPakilagay ang iyong phone number sa format na nagsisimula sa +63 (halimbawa: +639123456789). Huwag gumamit ng 0 sa unahan')
                else:
                    messages.error(request, 'Please enter a valid phone number.')
    
    return render(request, 'myproject/login.html')
    '''
    
    print("✅ Fix code generated. Key improvements:")
    print("   • Generates multiple phone format strategies")
    print("   • Tests all possible formats automatically")
    print("   • Handles +63, 63, 09, and 9 prefixes")
    print("   • Provides specific Filipino error messages")
    print("   • Enhanced debugging and logging")
    
    return fix_code

if __name__ == '__main__':
    print('🚀 Phone Login Persistence Diagnostic and Fix')
    print('=' * 60)
    
    # Test the current issue
    test_phone_login_issue()
    
    # Generate the fix
    fix_login_view()
    
    print(f"\n💡 SOLUTION SUMMARY:")
    print('• The issue is phone format mismatch between registration and login')
    print('• Users register with +639xxxxxxxxx but login form sends 9xxxxxxxxx')
    print('• The fix generates all possible phone formats and tests each one')
    print('• This ensures users can login regardless of the format they enter')
    print('• Enhanced error messages help users understand the correct format')
