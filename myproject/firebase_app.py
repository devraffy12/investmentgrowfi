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

    # If already initialized (e.g., in settings.py), just reuse it
    try:
        _firebase_app = firebase_admin.get_app()
        return _firebase_app
    except ValueError:
        # Not initialized yet, proceed to initialize
        pass

    # Determine credentials file path
    creds_path = getattr(settings, 'FIREBASE_CREDENTIALS_FILE', None) or os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not creds_path or not os.path.exists(creds_path):
        # If there is an already initialized app at the firebase_admin level, reuse it
        try:
            _firebase_app = firebase_admin.get_app()
            return _firebase_app
        except ValueError:
            raise RuntimeError(
                'Firebase credentials file not found. Set settings.FIREBASE_CREDENTIALS_FILE or GOOGLE_APPLICATION_CREDENTIALS.'
            )

    cred = credentials.Certificate(creds_path)
    try:
        _firebase_app = firebase_admin.initialize_app(cred)
    except ValueError:
        # If default app already exists, reuse it
        _firebase_app = firebase_admin.get_app()
    return _firebase_app


def get_firestore_client() -> firestore.Client:
    """Return a Firestore client bound to the initialized Firebase app."""
    app = get_firebase_app()
    return firestore.client(app=app)
