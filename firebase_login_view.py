"""
Pure Firebase Login View
This will replace the Django authentication login
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from firebase_auth import FirebaseAuth
import json

def firebase_user_login(request):
    """Pure Firebase login - no Django User dependency"""
    if request.method == 'POST':
        phone = request.POST.get('phone', '')
        password = request.POST.get('password', '')
        
        print(f"🔐 Firebase login attempt - Phone: {phone}")
        
        if not phone or not password:
            messages.error(request, 'Please enter both phone number and password.')
            return render(request, 'myproject/login.html')
        
        # Initialize Firebase auth
        firebase_auth = FirebaseAuth()
        
        # Authenticate user
        auth_result = firebase_auth.authenticate_user(phone, password)
        
        if auth_result['success']:
            # Create session
            user_data = auth_result['user_data']
            firebase_key = auth_result['firebase_key']
            
            if firebase_auth.create_session(request, user_data, firebase_key):
                messages.success(request, f'Welcome back! Logged in successfully.')
                return redirect('dashboard')
            else:
                messages.error(request, 'Login failed. Please try again.')
        else:
            # Show the specific error from Firebase auth
            messages.error(request, auth_result['error'])
    
    return render(request, 'myproject/login.html')

@csrf_exempt
def firebase_login_api(request):
    """API endpoint for Firebase login"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone = data.get('phone', '')
            password = data.get('password', '')
            
            firebase_auth = FirebaseAuth()
            auth_result = firebase_auth.authenticate_user(phone, password)
            
            if auth_result['success']:
                user_data = auth_result['user_data']
                firebase_key = auth_result['firebase_key']
                
                if firebase_auth.create_session(request, user_data, firebase_key):
                    return JsonResponse({
                        'success': True,
                        'message': 'Login successful',
                        'redirect': '/dashboard/'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Session creation failed'
                    })
            else:
                return JsonResponse({
                    'success': False,
                    'error': auth_result['error']
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Login failed: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
