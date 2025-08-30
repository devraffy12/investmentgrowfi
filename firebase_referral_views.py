#!/usr/bin/env python3
"""
Firebase Referral Views
Pure Firebase implementation for referral system in views.py
"""

import json
import logging
from datetime import datetime, timezone
from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from firebase_referral_system import FirebaseReferralSystem

logger = logging.getLogger(__name__)

def get_firebase_referral_system():
    """Get Firebase referral system instance"""
    return FirebaseReferralSystem()

@csrf_exempt
def firebase_register_with_referral(request):
    """Handle user registration with referral code using Firebase"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone_number = data.get('phone_number')
            referral_code = data.get('referral_code')
            
            if not phone_number:
                return JsonResponse({'success': False, 'error': 'Phone number required'})
            
            referral_system = get_firebase_referral_system()
            
            # Check if referral code is valid
            if referral_code:
                referrer_phone = referral_system.get_user_by_referral_code(referral_code)
                if not referrer_phone:
                    return JsonResponse({'success': False, 'error': 'Invalid referral code'})
            
            # Create user referral data
            user_code = referral_system.create_user_referral_data(
                phone_number=phone_number,
                referred_by_code=referral_code
            )
            
            if user_code:
                return JsonResponse({
                    'success': True,
                    'referral_code': user_code,
                    'message': 'User registered successfully'
                })
            else:
                return JsonResponse({'success': False, 'error': 'Failed to create referral data'})
                
        except Exception as e:
            logger.error(f"Firebase registration error: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def firebase_get_referral_stats(request):
    """Get referral statistics using Firebase"""
    if request.method == 'GET':
        try:
            phone_number = request.GET.get('phone_number')
            if not phone_number:
                return JsonResponse({'success': False, 'error': 'Phone number required'})
            
            referral_system = get_firebase_referral_system()
            stats = referral_system.get_referral_stats(phone_number)
            
            if stats:
                return JsonResponse({'success': True, 'data': stats})
            else:
                return JsonResponse({'success': False, 'error': 'User not found'})
                
        except Exception as e:
            logger.error(f"Firebase stats error: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def firebase_team_view(request):
    """Team view using Firebase referral system"""
    if request.method == 'GET':
        try:
            # Get user from session or Firebase auth
            phone_number = request.session.get('phone_number')
            if not phone_number:
                # Try to get from Firebase auth
                authorization_header = request.headers.get('Authorization')
                if authorization_header:
                    # Extract phone from Firebase token (implement token verification)
                    phone_number = verify_firebase_token_and_get_phone(authorization_header)
            
            if not phone_number:
                return redirect('login')
            
            referral_system = get_firebase_referral_system()
            stats = referral_system.get_referral_stats(phone_number)
            
            context = {
                'referral_code': stats.get('referral_code', 'N/A') if stats else 'N/A',
                'total_referrals': stats.get('total_referrals', 0) if stats else 0,
                'active_referrals': stats.get('active_referrals', 0) if stats else 0,
                'total_earnings': stats.get('total_earnings', 0) if stats else 0,
                'team_volume': stats.get('team_volume', 0) if stats else 0,
                'referred_by': stats.get('referred_by', 'None') if stats else 'None',
                'phone_number': phone_number
            }
            
            return render(request, 'team.html', context)
            
        except Exception as e:
            logger.error(f"Firebase team view error: {e}")
            messages.error(request, f'Error loading team data: {e}')
            return redirect('dashboard')

def verify_firebase_token_and_get_phone(authorization_header):
    """Verify Firebase token and extract phone number"""
    try:
        # This would implement Firebase token verification
        # For now, return None - implement based on your Firebase auth setup
        return None
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return None

@csrf_exempt
def firebase_process_investment_bonus(request):
    """Process investment bonus using Firebase"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone_number = data.get('phone_number')
            investment_amount = data.get('amount', 0)
            
            if not phone_number or investment_amount <= 0:
                return JsonResponse({'success': False, 'error': 'Invalid parameters'})
            
            referral_system = get_firebase_referral_system()
            user_data = referral_system.get_user_referral_data(phone_number)
            
            if user_data and user_data.get('referred_by'):
                # Find referrer
                referrer_phone = referral_system.get_user_by_referral_code(user_data['referred_by'])
                if referrer_phone:
                    # Calculate 10% commission
                    commission = investment_amount * 0.10
                    
                    # Add investment bonus
                    success = referral_system.add_referral_bonus(
                        phone_number=referrer_phone,
                        bonus_type='investment',
                        amount=commission,
                        description=f'10% investment bonus from {phone_number} (₱{investment_amount})'
                    )
                    
                    if success:
                        # Update team volume
                        referral_system.calculate_team_volume(referrer_phone)
                        
                        return JsonResponse({
                            'success': True,
                            'commission': commission,
                            'message': f'Investment bonus of ₱{commission} added to {referrer_phone}'
                        })
            
            return JsonResponse({'success': True, 'commission': 0, 'message': 'No referrer found'})
            
        except Exception as e:
            logger.error(f"Firebase investment bonus error: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def firebase_migrate_referral_data(request):
    """Migrate existing Django data to Firebase"""
    if request.method == 'POST':
        try:
            referral_system = get_firebase_referral_system()
            success = referral_system.migrate_django_data_to_firebase()
            
            if success:
                return JsonResponse({'success': True, 'message': 'Migration completed successfully'})
            else:
                return JsonResponse({'success': False, 'error': 'Migration failed'})
                
        except Exception as e:
            logger.error(f"Migration error: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# Additional helper functions for Firebase integration

def get_user_referral_link(phone_number):
    """Get user's referral link"""
    try:
        referral_system = get_firebase_referral_system()
        user_data = referral_system.get_user_referral_data(phone_number)
        
        if user_data and user_data.get('referral_code'):
            base_url = "https://investmentgrowfi.onrender.com"  # Your site URL
            return f"{base_url}/register?ref={user_data['referral_code']}"
        
        return None
    except Exception as e:
        logger.error(f"Error getting referral link: {e}")
        return None

def update_team_volumes():
    """Background task to update all team volumes"""
    try:
        referral_system = get_firebase_referral_system()
        
        # Get all users from Firebase
        users_ref = referral_system.db.reference('referrals/users')
        users = users_ref.get() or {}
        
        for phone_number in users.keys():
            referral_system.calculate_team_volume(phone_number)
        
        return True
    except Exception as e:
        logger.error(f"Error updating team volumes: {e}")
        return False
