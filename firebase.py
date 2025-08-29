"""
🔥 FIREBASE INITIALIZATION FOR PURE FIREBASE/FIRESTORE USAGE
===========================================================
Simple Firebase initialization for Firestore usage.
"""

import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from django.conf import settings

# Global Firebase app instance
_firebase_app = None
_firestore_client = None

def get_firebase_app():
    """Initialize and return Firebase app instance"""
    global _firebase_app
    
    if _firebase_app is not None:
        return _firebase_app
    
    try:
        # Check if running on Render.com (production)
        is_production = bool(os.environ.get('RENDER_EXTERNAL_HOSTNAME'))
        
        if is_production:
            # Production: Load from environment variables
            firebase_credentials = {
                "type": "service_account",
                "project_id": os.environ.get('FIREBASE_PROJECT_ID'),
                "private_key_id": os.environ.get('FIREBASE_PRIVATE_KEY_ID'),
                "private_key": os.environ.get('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                "client_email": os.environ.get('FIREBASE_CLIENT_EMAIL'),
                "client_id": os.environ.get('FIREBASE_CLIENT_ID'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.environ.get('FIREBASE_CLIENT_X509_CERT_URL')
            }
            
            cred = credentials.Certificate(firebase_credentials)
            print("🔥 Firebase initialized with production environment credentials")
            
        else:
            # Development: Load from JSON file
            service_account_path = os.path.join(settings.BASE_DIR, 'firebase-service-account.json')
            
            if os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                print("🔥 Firebase initialized with JSON file credentials")
            else:
                raise FileNotFoundError("Firebase service account JSON file not found")
        
        # Initialize Firebase app
        _firebase_app = firebase_admin.initialize_app(cred, {
            'databaseURL': os.environ.get('FIREBASE_DATABASE_URL', 'https://investment-6d6f7-default-rtdb.firebaseio.com')
        })
        
        print(f"✅ Firebase app initialized: {_firebase_app.project_id}")
        return _firebase_app
        
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        raise

def get_firestore_client():
    """Get Firestore client instance"""
    global _firestore_client
    
    if _firestore_client is not None:
        return _firestore_client
    
    try:
        # Ensure Firebase app is initialized
        get_firebase_app()
        
        # Initialize Firestore client
        _firestore_client = firestore.client()
        print("✅ Firestore client initialized")
        return _firestore_client
        
    except Exception as e:
        print(f"❌ Firestore initialization failed: {e}")
        raise

def create_user_document(uid, user_data):
    """Create a new user document in Firestore"""
    try:
        db = get_firestore_client()
        user_ref = db.collection('users').document(uid)
        
        # Default user data structure
        default_data = {
            'uid': uid,
            'email': '',
            'display_name': '',
            'phone_number': '',
            'balance': 0.0,
            'withdrawable_balance': 0.0,
            'non_withdrawable_bonus': 100.0,  # Registration bonus
            'total_invested': 0.0,
            'total_earnings': 0.0,
            'registration_bonus_claimed': False,
            'is_verified': False,
            'referral_code': '',
            'referred_by_uid': '',
            'created_at': firestore.SERVER_TIMESTAMP,
            'last_login': firestore.SERVER_TIMESTAMP,
        }
        
        # Merge with provided data
        default_data.update(user_data)
        
        # Generate unique referral code if not provided
        if not default_data.get('referral_code'):
            import random
            import string
            referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            default_data['referral_code'] = referral_code
        
        user_ref.set(default_data)
        print(f"✅ User document created in Firestore: {uid}")
        return default_data
        
    except Exception as e:
        print(f"❌ Error creating user document: {e}")
        raise

def get_user_document(uid):
    """Get user document from Firestore"""
    try:
        db = get_firestore_client()
        user_ref = db.collection('users').document(uid)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            return user_doc.to_dict()
        else:
            return None
            
    except Exception as e:
        print(f"❌ Error getting user document: {e}")
        raise

def update_user_document(uid, update_data):
    """Update user document in Firestore"""
    try:
        db = get_firestore_client()
        user_ref = db.collection('users').document(uid)
        
        # Add last updated timestamp
        update_data['last_updated'] = firestore.SERVER_TIMESTAMP
        
        user_ref.update(update_data)
        print(f"✅ User document updated: {uid}")
        
    except Exception as e:
        print(f"❌ Error updating user document: {e}")
        raise
