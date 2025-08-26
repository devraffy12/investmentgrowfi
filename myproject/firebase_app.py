import os
import json
from typing import Optional

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from django.conf import settings


_firebase_app: Optional[firebase_admin.App] = None


def get_firebase_app() -> firebase_admin.App:
    """Initialize and return a singleton Firebase Admin app.

    Safe to call multiple times. If an app was already initialized elsewhere
    (e.g., in settings.py), this will reuse that instance.
    
    Supports both file-based credentials and environment variable credentials.
    """
    global _firebase_app
    if _firebase_app is not None:
        return _firebase_app

    # If already initialized (e.g., in settings.py), just reuse it
    try:
        _firebase_app = firebase_admin.get_app()
        return _firebase_app
    except ValueError:
        # Not initialized yet, proceed to initialize
        pass

    cred = None
    
    # Method 1: Try environment variable JSON credentials (for production)
    json_creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    if json_creds:
        try:
            cred_dict = json.loads(json_creds)
            # Fix private key formatting
            if 'private_key' in cred_dict:
                cred_dict['private_key'] = cred_dict['private_key'].replace('\\n', '\n')
            cred = credentials.Certificate(cred_dict)
            print("🔥 Firebase initialized with JSON environment credentials")
        except Exception as e:
            print(f"❌ Error parsing JSON credentials: {e}")
    
    # Method 2: Try individual environment variables (for production)
    if not cred:
        firebase_type = os.getenv('FIREBASE_TYPE')
        firebase_project_id = os.getenv('FIREBASE_PROJECT_ID')
        firebase_private_key = os.getenv('FIREBASE_PRIVATE_KEY')
        firebase_client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
        
        if all([firebase_type, firebase_project_id, firebase_private_key, firebase_client_email]):
            try:
                # Fix private key formatting
                private_key = firebase_private_key.replace('\\n', '\n')
                
                cred_dict = {
                    "type": firebase_type,
                    "project_id": firebase_project_id,
                    "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                    "private_key": private_key,
                    "client_email": firebase_client_email,
                    "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                    "auth_uri": os.getenv('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
                    "token_uri": os.getenv('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
                    "auth_provider_x509_cert_url": os.getenv('FIREBASE_AUTH_PROVIDER_X509_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs'),
                    "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_X509_CERT_URL'),
                    "universe_domain": os.getenv('FIREBASE_UNIVERSE_DOMAIN', 'googleapis.com')
                }
                cred = credentials.Certificate(cred_dict)
                print("🔥 Firebase initialized with individual environment variables")
            except Exception as e:
                print(f"❌ Error creating credentials from environment variables: {e}")
    
    # Method 3: Try credentials file (for local development)
    if not cred:
        creds_path = getattr(settings, 'FIREBASE_CREDENTIALS_FILE', None) or os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if creds_path and os.path.exists(creds_path):
            try:
                cred = credentials.Certificate(creds_path)
                print(f"🔥 Firebase initialized with credentials file: {creds_path}")
            except Exception as e:
                print(f"❌ Error loading credentials file: {e}")
    
    # If no credentials found, raise error
    if not cred:
        error_msg = (
            'Firebase credentials not found. Please set one of:\n'
            '1. GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable\n'
            '2. Individual Firebase environment variables (FIREBASE_TYPE, FIREBASE_PROJECT_ID, etc.)\n'
            '3. settings.FIREBASE_CREDENTIALS_FILE or GOOGLE_APPLICATION_CREDENTIALS file path'
        )
        raise RuntimeError(error_msg)

    # Initialize Firebase app
    try:
        # Include database URL if available
        config = {}
        database_url = os.getenv('FIREBASE_DATABASE_URL')
        if database_url:
            config['databaseURL'] = database_url
            
        _firebase_app = firebase_admin.initialize_app(cred, config)
        print(f"✅ Firebase app initialized successfully with project: {cred.project_id}")
    except ValueError as e:
        if "already exists" in str(e).lower():
            # If default app already exists, reuse it
            _firebase_app = firebase_admin.get_app()
            print("✅ Firebase app already initialized, reusing existing instance")
        else:
            raise e
    except Exception as e:
        print(f"❌ Error initializing Firebase app: {e}")
        raise e
    
    return _firebase_app


def get_firestore_client() -> firestore.Client:
    """Return a Firestore client bound to the initialized Firebase app."""
    app = get_firebase_app()
    return firestore.client(app=app)
