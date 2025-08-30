"""
🔥 FIREBASE CONFIGURATION MODULE
===============================
Centralized Firebase initialization and management for optimal performance.
"""

import os
import json
import logging
import time
from typing import Optional

import firebase_admin
from firebase_admin import credentials, firestore, auth

logger = logging.getLogger(__name__)

class FirebaseConfig:
    """Firebase configuration and initialization"""
    
    def __init__(self):
        self.app: Optional[firebase_admin.App] = None
        self.db: Optional[firestore.Client] = None
        self.auth_client: Optional[auth] = None
        self.initialized = False
    
    def initialize(self) -> bool:
        """Initialize Firebase with optimized settings"""
        if self.initialized:
            logger.info("🔥 Firebase already initialized")
            return True
        
        start_time = time.time()
        logger.info("🚀 Initializing Firebase Admin SDK...")
        
        try:
            # Method 1: JSON credentials (recommended for Render.com)
            firebase_creds_json = os.environ.get('FIREBASE_CREDENTIALS_JSON')
            if firebase_creds_json:
                logger.info("✅ Using FIREBASE_CREDENTIALS_JSON")
                cred_dict = json.loads(firebase_creds_json)
                cred = credentials.Certificate(cred_dict)
                
                # Initialize with Asia-Southeast optimization
                self.app = firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://investment-6d6f7-default-rtdb.firebaseio.com',
                    'projectId': cred_dict.get('project_id', 'investment-6d6f7')
                })
                
                logger.info(f"🌏 Firebase project: {cred_dict.get('project_id')}")
                
            # Method 2: Individual environment variables
            elif os.environ.get('FIREBASE_PROJECT_ID'):
                logger.info("✅ Using individual Firebase environment variables")
                cred_dict = {
                    "type": "service_account",
                    "project_id": os.environ.get('FIREBASE_PROJECT_ID'),
                    "private_key_id": os.environ.get('FIREBASE_PRIVATE_KEY_ID'),
                    "private_key": os.environ.get('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                    "client_email": os.environ.get('FIREBASE_CLIENT_EMAIL'),
                    "client_id": os.environ.get('FIREBASE_CLIENT_ID'),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
                }
                
                cred = credentials.Certificate(cred_dict)
                self.app = firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://investment-6d6f7-default-rtdb.firebaseio.com'
                })
                
            # Method 3: Local service account file
            else:
                service_account_path = "firebase-service-account.json"
                if os.path.exists(service_account_path):
                    logger.info("✅ Using local service account file")
                    cred = credentials.Certificate(service_account_path)
                    self.app = firebase_admin.initialize_app(cred)
                else:
                    raise Exception("❌ No Firebase credentials found!")
            
            # Initialize clients
            self.db = firestore.client()
            self.auth_client = auth
            
            # Test connection
            test_start = time.time()
            health_ref = self.db.collection('health').document('config_test')
            health_ref.set({
                'timestamp': firestore.SERVER_TIMESTAMP,
                'status': 'initialized',
                'module': 'firebase_config'
            })
            test_time = time.time() - test_start
            
            self.initialized = True
            init_time = time.time() - start_time
            
            logger.info(f"✅ Firebase initialized successfully")
            logger.info(f"⚡ Initialization time: {init_time:.3f}s")
            logger.info(f"⚡ Test connection time: {test_time:.3f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Firebase initialization failed: {str(e)}")
            return False
    
    def get_db(self):
        """Get Firestore client"""
        if not self.initialized:
            self.initialize()
        return self.db
    
    def get_auth(self):
        """Get Auth client"""
        if not self.initialized:
            self.initialize()
        return self.auth_client
    
    def is_ready(self) -> bool:
        """Check if Firebase is ready"""
        return self.initialized and self.db is not None

# Global Firebase configuration instance
firebase_config = FirebaseConfig()
