import os
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
    """
    global _firebase_app
    if _firebase_app is not None:
        return _firebase_app

    # Try to get existing app first (from settings.py)
    try:
        _firebase_app = firebase_admin.get_app()
        print("🔥 Using existing Firebase app from settings.py")
        return _firebase_app
    except ValueError:
        # No app exists, need to initialize
        print("🔥 No existing Firebase app found, initializing new one")
        pass

    # Check if Firebase is already initialized in settings
    if hasattr(settings, 'FIREBASE_INITIALIZED') and settings.FIREBASE_INITIALIZED:
        try:
            _firebase_app = firebase_admin.get_app()
            print("✅ Firebase app retrieved successfully")
            return _firebase_app
        except ValueError:
            print("⚠️ Settings says Firebase is initialized but no app found")

    # Fallback: try to initialize with credentials file
    creds_path = getattr(settings, 'FIREBASE_CREDENTIALS_FILE', None) or os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if creds_path and os.path.exists(creds_path):
        print(f"🔥 Trying to initialize Firebase with credentials file: {creds_path}")
        cred = credentials.Certificate(creds_path)
        try:
            _firebase_app = firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized with credentials file")
            return _firebase_app
        except ValueError as e:
            print(f"⚠️ Could not initialize Firebase: {e}")
            # Try to get existing app
            try:
                _firebase_app = firebase_admin.get_app()
                return _firebase_app
            except ValueError:
                pass

    # Last resort - raise error
    raise RuntimeError(
        '❌ Firebase not available. Check if Firebase is properly configured in settings.py'
    )


def get_firestore_client() -> firestore.Client:
    """Return a Firestore client bound to the initialized Firebase app."""
    app = get_firebase_app()
    return firestore.client(app=app)





