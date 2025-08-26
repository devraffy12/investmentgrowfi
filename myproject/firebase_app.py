import os
import json
from typing import Optional
from pathlib import Path

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from django.conf import settings


_firebase_app: Optional[firebase_admin.App] = None


def get_firebase_app() -> firebase_admin.App:
    """Initialize and return a singleton Firebase Admin app.

    Safe to call multiple times. If an app was already initialized elsewhere
    (e.g., in settings.py), this will reuse that instance.
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

    # Check if we're in production (Render.com)
    is_production = bool(os.environ.get('RENDER_EXTERNAL_HOSTNAME'))
    
    if is_production:
        print("🔥 Firebase App: Initializing for production using environment variables")
        
        # Debug: Check what environment variables are available
        firebase_credentials_json = os.environ.get('FIREBASE_CREDENTIALS_JSON')
        firebase_project_id = os.environ.get('FIREBASE_PROJECT_ID')
        firebase_private_key = os.environ.get('FIREBASE_PRIVATE_KEY')
        firebase_client_email = os.environ.get('FIREBASE_CLIENT_EMAIL')
        
        print(f"❓ Firebase credentials check - FIREBASE_CREDENTIALS_JSON: {'✅' if firebase_credentials_json else '❌'}")
        print(f"   Individual vars - PROJECT_ID: {'✅' if firebase_project_id else '❌'}, PRIVATE_KEY: {'✅' if firebase_private_key else '❌'}, CLIENT_EMAIL: {'✅' if firebase_client_email else '❌'}")
        
        # Try FIREBASE_CREDENTIALS_JSON first (our preferred method)
        if firebase_credentials_json:
            try:
                print("🔧 Attempting to parse FIREBASE_CREDENTIALS_JSON...")
                # Parse the JSON credentials
                firebase_creds = json.loads(firebase_credentials_json)
                print("✅ Successfully parsed FIREBASE_CREDENTIALS_JSON")
                
                # Fix escaped newlines in private key
                if 'private_key' in firebase_creds:
                    firebase_creds['private_key'] = firebase_creds['private_key'].replace('\\n', '\n')
                
                cred = credentials.Certificate(firebase_creds)
                _firebase_app = firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://investment-6d6f7-default-rtdb.firebaseio.com'
                })
                print("✅ Firebase App: Production initialization successful with FIREBASE_CREDENTIALS_JSON!")
                return _firebase_app
            except json.JSONDecodeError as e:
                print(f"❌ Firebase App: JSON parsing failed: {e}")
                print(f"   JSON starts with: {firebase_credentials_json[:100] if len(firebase_credentials_json) > 100 else firebase_credentials_json}...")
            except Exception as e:
                print(f"❌ Firebase App: Production initialization failed with FIREBASE_CREDENTIALS_JSON: {e}")
                # Fall back to individual environment variables
                
                # Fix escaped newlines in private key
                if 'private_key' in firebase_creds:
                    firebase_creds['private_key'] = firebase_creds['private_key'].replace('\\n', '\n')
                
                cred = credentials.Certificate(firebase_creds)
                _firebase_app = firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://investment-6d6f7-default-rtdb.firebaseio.com'
                })
                print("✅ Firebase App: Production initialization successful with FIREBASE_CREDENTIALS_JSON!")
                return _firebase_app
            except Exception as e:
                print(f"❌ Firebase App: Production initialization failed with FIREBASE_CREDENTIALS_JSON: {e}")
                # Fall back to individual environment variables
        
        # Fallback: Try individual environment variables
        firebase_project_id = os.environ.get('FIREBASE_PROJECT_ID')
        firebase_private_key = os.environ.get('FIREBASE_PRIVATE_KEY')
        firebase_client_email = os.environ.get('FIREBASE_CLIENT_EMAIL')
        
        if firebase_project_id and firebase_private_key and firebase_client_email:
            # Fix escaped newlines in private key
            firebase_private_key = firebase_private_key.replace('\\n', '\n')
            
            firebase_creds = {
                "type": "service_account",
                "project_id": firebase_project_id,
                "private_key": firebase_private_key,
                "client_email": firebase_client_email,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            }
            
            try:
                cred = credentials.Certificate(firebase_creds)
                _firebase_app = firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://investment-6d6f7-default-rtdb.firebaseio.com'
                })
                print("✅ Firebase App: Production initialization successful with individual env vars!")
                return _firebase_app
            except Exception as e:
                print(f"❌ Firebase App: Production initialization failed with individual env vars: {e}")
                raise RuntimeError(f'Firebase production initialization failed: {e}')
        else:
            print("❌ No Firebase credentials found in environment variables!")
            print("🔧 TO FIX ON RENDER.COM:")
            print("   1. Go to your Render.com dashboard")
            print("   2. Select your web service")
            print("   3. Go to Environment tab")
            print("   4. Add: FIREBASE_CREDENTIALS_JSON (get value from 'python generate_firebase_env.py')")
            print("   5. Save and redeploy")
            raise RuntimeError('Firebase production credentials not found in environment variables')
    else:
        print("🔥 Firebase App: Initializing for local development")
        # For local development, try to use the service account file
        firebase_service_account_path = Path(settings.BASE_DIR) / 'firebase-service-account.json'
        
        if firebase_service_account_path.exists():
            try:
                # Read and fix the JSON file
                with open(firebase_service_account_path, 'r') as f:
                    firebase_creds = json.load(f)
                
                # Fix escaped newlines in private key
                if 'private_key' in firebase_creds:
                    firebase_creds['private_key'] = firebase_creds['private_key'].replace('\\n', '\n')
                
                cred = credentials.Certificate(firebase_creds)
                _firebase_app = firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://investment-6d6f7-default-rtdb.firebaseio.com'
                })
                print("✅ Firebase App: Local development initialization successful!")
                return _firebase_app
            except Exception as e:
                print(f"❌ Firebase App: Local development initialization failed: {e}")
                # For now, let's just warn but not fail completely
                print("⚠️ Continuing without Firebase - registration will work but data won't be saved to Firebase")
                raise RuntimeError(f'Firebase local development initialization failed: {e}')
        else:
            print("⚠️ Firebase service account file not found - continuing without Firebase")
            raise RuntimeError('Firebase service account file not found for local development')

    raise RuntimeError('Firebase initialization failed - no valid configuration found')


def get_firestore_client() -> firestore.Client:
    """Return a Firestore client bound to the initialized Firebase app."""
    app = get_firebase_app()
    return firestore.client(app=app)






