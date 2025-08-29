"""
Pure Firebase Authentication System
Solves the "Account not found" issue for users who registered in Firebase
"""

import hashlib
import re
from django.utils import timezone
from django.conf import settings
import firebase_admin
from firebase_admin import credentials, db as firebase_db
import os

class FirebaseAuth:
    """Pure Firebase Authentication - no Django User dependency"""
    
    def __init__(self):
        self.app = self.get_firebase_app()
        self.db = None
        if hasattr(self.app, 'project_id') and self.app.project_id != "firebase-unavailable":
            self.db = firebase_db.reference('/', app=self.app)
    
    def get_firebase_app(self):
        """Get or initialize Firebase app"""
        try:
            return firebase_admin.get_app()
        except ValueError:
            try:
                # Try to load from service account file
                cred_path = os.path.join(settings.BASE_DIR, 'firebase-service-account.json')
                if os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                else:
                    # Use environment variables
                    firebase_credentials = {
                        "type": "service_account",
                        "project_id": "investment-6d6f7",
                        "private_key_id": os.environ.get('FIREBASE_PRIVATE_KEY_ID'),
                        "private_key": os.environ.get('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                        "client_email": os.environ.get('FIREBASE_CLIENT_EMAIL'),
                        "client_id": os.environ.get('FIREBASE_CLIENT_ID'),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_x509_cert_url": os.environ.get('FIREBASE_CLIENT_CERT_URL')
                    }
                    cred = credentials.Certificate(firebase_credentials)
                
                app = firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://investment-6d6f7-default-rtdb.firebaseio.com'
                })
                print("✅ Firebase initialized successfully")
                return app
            except Exception as e:
                print(f"❌ Firebase initialization failed: {e}")
                class DummyApp:
                    project_id = "firebase-unavailable"
                return DummyApp()
    
    def normalize_phone(self, phone):
        """Normalize Philippine phone number to +63 format"""
        if not phone:
            return ''
        
        # Remove spaces, dashes, parentheses
        clean_phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
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
            else:
                return '+63' + digits_only
        
        return clean_phone
    
    def get_firebase_key(self, phone):
        """Convert phone number to Firebase key"""
        return phone.replace('+', '').replace(' ', '').replace('-', '')
    
    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password, hashed_password):
        """Verify password against hash"""
        return self.hash_password(password) == hashed_password
    
    def find_user_by_phone(self, phone):
        """Find user by phone number in Firebase"""
        if not self.db:
            print("❌ Firebase not available")
            return None
        
        try:
            normalized_phone = self.normalize_phone(phone)
            firebase_key = self.get_firebase_key(normalized_phone)
            
            print(f"🔍 Looking for user: {normalized_phone} (key: {firebase_key})")
            
            users_ref = self.db.child('users')
            user_data = users_ref.child(firebase_key).get()
            
            if user_data:
                user_data['firebase_key'] = firebase_key
                user_data['phone_number'] = normalized_phone
                print(f"✅ User found in Firebase: {normalized_phone}")
                return user_data
            else:
                print(f"❌ User not found in Firebase: {normalized_phone}")
                return None
                
        except Exception as e:
            print(f"❌ Error finding user: {e}")
            return None
    
    def authenticate_user(self, phone, password):
        """Authenticate user with Firebase data"""
        print(f"🔐 Authenticating user: {phone}")
        
        user_data = self.find_user_by_phone(phone)
        if not user_data:
            return {'success': False, 'error': 'Account not found. Please check your phone number or register first.'}
        
        # Check if account is active
        if user_data.get('status') != 'active':
            return {'success': False, 'error': 'Account is inactive. Please contact support.'}
        
        # Verify password
        stored_password = user_data.get('password', '')
        if not self.verify_password(password, stored_password):
            return {'success': False, 'error': 'Invalid password. Please check your password and try again.'}
        
        # Update login information
        try:
            firebase_key = user_data.get('firebase_key')
            users_ref = self.db.child('users').child(firebase_key)
            login_count = int(user_data.get('login_count', 0)) + 1
            
            users_ref.update({
                'last_login': timezone.now().isoformat(),
                'login_count': login_count,
                'is_online': True,
                'last_login_ip': '',  # Add IP if needed
                'platform': 'web'
            })
            
            print(f"✅ User authenticated successfully: {phone}")
            return {
                'success': True,
                'user_data': user_data,
                'firebase_key': firebase_key
            }
            
        except Exception as e:
            print(f"❌ Error updating login info: {e}")
            return {'success': False, 'error': 'Login failed. Please try again.'}
    
    def create_session(self, request, user_data, firebase_key):
        """Create session for authenticated user"""
        try:
            # Set session data
            request.session['firebase_key'] = firebase_key
            request.session['user_phone'] = user_data.get('phone_number')
            request.session['login_time'] = timezone.now().isoformat()
            request.session['login_method'] = 'firebase_auth'
            request.session['user_balance'] = user_data.get('balance', 0)
            
            # Force session save
            request.session.save()
            
            print(f"✅ Session created for user: {user_data.get('phone_number')}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating session: {e}")
            return False

def firebase_login_required(view_func):
    """Decorator to require Firebase authentication instead of Django login"""
    from functools import wraps
    from django.shortcuts import redirect
    from django.contrib import messages
    
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        firebase_key = request.session.get('firebase_key')
        is_authenticated = request.session.get('is_authenticated', False)
        
        if not firebase_key or not is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')
        
        # Optionally verify user still exists in Firebase
        try:
            firebase_auth = FirebaseAuth()
            user_data = firebase_auth.db.child('users').child(firebase_key).get() if firebase_auth.db else None
            
            if not user_data or user_data.get('status') != 'active':
                # Clear invalid session
                request.session.flush()
                messages.error(request, 'Your session has expired. Please log in again.')
                return redirect('login')
            
            # Add user data to request for use in views
            request.firebase_user = user_data
            request.firebase_key = firebase_key
            
        except Exception as e:
            print(f"⚠️ Firebase verification error: {e}")
            # Don't fail the request, just log the error
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view
