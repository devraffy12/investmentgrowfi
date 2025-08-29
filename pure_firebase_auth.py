#!/usr/bin/env python3
"""
Pure Firebase Authentication System
Complete rewrite to use only Firebase - no Django User model
"""
import os
import sys
import django
from datetime import datetime, timedelta

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json
import hashlib
import bcrypt
import re

# Firebase imports
try:
    from myproject.firebase_app import get_firebase_app
    from firebase_admin import db as firebase_db
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

class FirebaseAuthManager:
    """Pure Firebase Authentication Manager"""
    
    def __init__(self):
        self.app = None
        self.db_ref = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase connection"""
        try:
            self.app = get_firebase_app()
            if hasattr(self.app, 'project_id') and self.app.project_id != "firebase-unavailable":
                self.db_ref = firebase_db.reference('/', app=self.app)
                print("✅ Firebase Auth Manager initialized successfully")
                return True
            else:
                print("❌ Firebase unavailable - using dummy app")
                return False
        except Exception as e:
            print(f"❌ Firebase initialization error: {e}")
            return False
    
    def normalize_phone(self, raw_phone):
        """Normalize phone number to +63 format"""
        if not raw_phone:
            return None
            
        # Remove all non-digit characters except +
        clean_phone = raw_phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # If already in +63 format, return as is
        if clean_phone.startswith('+63'):
            return clean_phone
            
        # Extract digits only
        digits_only = ''.join(filter(str.isdigit, clean_phone))
        
        # Handle different Philippine number formats
        if digits_only.startswith('63') and len(digits_only) >= 12:
            return '+' + digits_only
        elif digits_only.startswith('09') and len(digits_only) == 11:
            return '+63' + digits_only[1:]
        elif digits_only.startswith('9') and len(digits_only) == 10:
            return '+63' + digits_only
        elif len(digits_only) >= 10:
            last_10_digits = digits_only[-10:]
            if last_10_digits.startswith('9'):
                return '+63' + last_10_digits
        
        return None
    
    def get_firebase_key(self, phone):
        """Convert phone to Firebase key format"""
        if not phone:
            return None
        return phone.replace('+', '').replace(' ', '').replace('-', '')
    
    def hash_password(self, password):
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password, hashed_password):
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except:
            # Fallback for plain text passwords (temporary)
            return password == hashed_password
    
    def find_user_by_phone(self, phone):
        """Find user in Firebase by phone number"""
        if not self.db_ref:
            return None
            
        normalized_phone = self.normalize_phone(phone)
        if not normalized_phone:
            return None
            
        firebase_key = self.get_firebase_key(normalized_phone)
        
        try:
            # Try direct lookup first
            users_ref = self.db_ref.child('users')
            user_data = users_ref.child(firebase_key).get()
            
            if user_data:
                print(f"✅ User found by direct lookup: {firebase_key}")
                user_data['firebase_key'] = firebase_key
                user_data['normalized_phone'] = normalized_phone
                return user_data
            
            # Try searching all users if direct lookup fails
            print(f"🔍 Direct lookup failed, searching all users...")
            all_users = users_ref.get()
            
            if all_users:
                for key, data in all_users.items():
                    if data and 'phone_number' in data:
                        if data['phone_number'] == normalized_phone:
                            print(f"✅ User found by search: {key}")
                            data['firebase_key'] = key
                            data['normalized_phone'] = normalized_phone
                            return data
            
            print(f"❌ User not found: {normalized_phone}")
            return None
            
        except Exception as e:
            print(f"❌ Error finding user: {e}")
            return None
    
    def authenticate_user(self, phone, password):
        """Authenticate user with Firebase data"""
        user_data = self.find_user_by_phone(phone)
        
        if not user_data:
            print(f"❌ Authentication failed - user not found")
            return None
        
        # Check if user has password field
        stored_password = user_data.get('password')
        if not stored_password:
            print(f"❌ Authentication failed - no password stored")
            return None
        
        # Verify password
        if self.verify_password(password, stored_password):
            print(f"✅ Authentication successful for {user_data.get('phone_number')}")
            
            # Update last login
            self.update_user_login(user_data['firebase_key'], {
                'last_login': timezone.now().isoformat(),
                'login_count': user_data.get('login_count', 0) + 1,
                'is_online': True
            })
            
            return user_data
        else:
            print(f"❌ Authentication failed - invalid password")
            return None
    
    def update_user_login(self, firebase_key, update_data):
        """Update user login information"""
        if not self.db_ref:
            return False
            
        try:
            users_ref = self.db_ref.child('users')
            users_ref.child(firebase_key).update(update_data)
            return True
        except Exception as e:
            print(f"❌ Error updating user login: {e}")
            return False
    
    def create_user(self, phone, password, additional_data=None):
        """Create new user in Firebase"""
        if not self.db_ref:
            return False
            
        normalized_phone = self.normalize_phone(phone)
        if not normalized_phone:
            return False
            
        firebase_key = self.get_firebase_key(normalized_phone)
        
        # Check if user already exists
        if self.find_user_by_phone(phone):
            print(f"❌ User already exists: {normalized_phone}")
            return False
        
        # Create user data
        user_data = {
            'phone_number': normalized_phone,
            'password': self.hash_password(password),
            'created_at': timezone.now().isoformat(),
            'updated_at': timezone.now().isoformat(),
            'is_active': True,
            'balance': 100.0,  # Registration bonus
            'registration_bonus_claimed': True,
            'platform': 'django_pure_firebase',
            'account_status': 'active'
        }
        
        if additional_data:
            user_data.update(additional_data)
        
        try:
            users_ref = self.db_ref.child('users')
            users_ref.child(firebase_key).set(user_data)
            print(f"✅ User created successfully: {normalized_phone}")
            return True
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            return False

# Global Firebase Auth Manager instance
firebase_auth = FirebaseAuthManager()

def firebase_login(request):
    """Pure Firebase Login View"""
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        
        print(f"🔐 Firebase login attempt - Phone: {phone}")
        
        if not phone or not password:
            messages.error(request, 'Pakilagay ang phone number at password.')
            return render(request, 'myproject/login.html')
        
        # Authenticate with Firebase
        user_data = firebase_auth.authenticate_user(phone, password)
        
        if user_data:
            # SUCCESS - Create manual session
            request.session['is_authenticated'] = True
            request.session['user_phone'] = user_data['normalized_phone']
            request.session['firebase_key'] = user_data['firebase_key']
            request.session['user_data'] = user_data
            request.session['login_time'] = timezone.now().isoformat()
            request.session['login_method'] = 'pure_firebase'
            
            # Force session save
            request.session.save()
            
            print(f"✅ Firebase login successful - session created")
            messages.success(request, 'Maligayang pagbabalik! Successfully na-login ka.')
            return redirect('firebase_dashboard')
        
        else:
            # FAILED - Check why
            normalized_phone = firebase_auth.normalize_phone(phone)
            user_exists = firebase_auth.find_user_by_phone(phone)
            
            if user_exists:
                messages.error(request, 'Mali ang password. Pakisuri ang inyong password at subukan ulit.')
            else:
                messages.error(request, 
                    'Hindi nahanap ang account. Pakisuri ang inyong phone number o mag-register muna.\\n\\n'
                    'Pakilagay ang inyong phone number sa format na nagsisimula sa +63 (halimbawa: +639123456789).')
    
    return render(request, 'myproject/login.html')

def firebase_register(request):
    """Pure Firebase Registration View"""
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        print(f"📝 Firebase registration attempt - Phone: {phone}")
        
        # Validate inputs
        if not phone or not password:
            messages.error(request, 'Pakilagay ang lahat ng required fields.')
            return render(request, 'myproject/register.html')
        
        if password != confirm_password:
            messages.error(request, 'Hindi magkatugma ang password. Subukan ulit.')
            return render(request, 'myproject/register.html')
        
        # Create user in Firebase
        if firebase_auth.create_user(phone, password):
            print(f"✅ Firebase registration successful")
            messages.success(request, 'Matagumpay na nag-register! Maaari na kayong mag-login.')
            return redirect('firebase_login')
        else:
            messages.error(request, 'Hindi successful ang registration. Maaring naka-register na ang phone number.')
            return render(request, 'myproject/register.html')
    
    return render(request, 'myproject/register.html')

def firebase_dashboard(request):
    """Pure Firebase Dashboard View"""
    # Check manual authentication
    if not request.session.get('is_authenticated'):
        messages.error(request, 'Kailangan mag-login muna.')
        return redirect('firebase_login')
    
    user_data = request.session.get('user_data', {})
    user_phone = request.session.get('user_phone', 'Unknown')
    
    # Get fresh user data from Firebase
    fresh_user_data = firebase_auth.find_user_by_phone(user_phone)
    if fresh_user_data:
        user_data = fresh_user_data
        # Update session with fresh data
        request.session['user_data'] = user_data
        request.session.save()
    
    context = {
        'user_data': user_data,
        'user_phone': user_phone,
        'balance': user_data.get('balance', 0),
        'is_authenticated': True,
    }
    
    return render(request, 'myproject/firebase_dashboard.html', context)

def firebase_logout(request):
    """Pure Firebase Logout View"""
    if request.session.get('firebase_key'):
        # Update Firebase user status
        firebase_auth.update_user_login(request.session['firebase_key'], {
            'is_online': False,
            'last_logout': timezone.now().isoformat()
        })
    
    # Clear session
    request.session.flush()
    messages.success(request, 'Matagumpay na nag-logout.')
    return redirect('firebase_login')

# Context processor for Firebase user
def firebase_user_context(request):
    """Context processor to add Firebase user data to templates"""
    return {
        'firebase_user': request.session.get('user_data', {}),
        'firebase_authenticated': request.session.get('is_authenticated', False),
        'firebase_phone': request.session.get('user_phone', ''),
    }

if __name__ == '__main__':
    print('🔥 PURE FIREBASE AUTHENTICATION SYSTEM')
    print('=' * 60)
    print('✅ Firebase Auth Manager created')
    print('✅ Pure Firebase login/register views ready')
    print('✅ Manual session management implemented')
    print('✅ No Django User model dependency')
    print('\\n💡 NEXT STEPS:')
    print('1. Add these views to urls.py')
    print('2. Create firebase_dashboard.html template')
    print('3. Add firebase_user_context to TEMPLATE_CONTEXT_PROCESSORS')
    print('4. Test login with existing Firebase users')
