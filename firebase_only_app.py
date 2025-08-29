#!/usr/bin/env python3
"""
🚀 FIREBASE-ONLY PYTHON APP FOR RENDER.COM
© 2025 GrowFi Investment Platform

Complete Firebase app with:
- Global Firebase initialization (once only)
- Auth + Firestore integration
- Health check endpoint
- User registration system
- Cold start optimization
- Ready for Render.com deployment
"""

import os
import json
import logging
import uvicorn
from datetime import datetime
from typing import Optional, Dict, Any
from functools import lru_cache

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global Firebase instances (initialized once)
_firebase_app = None
_auth_client = None
_firestore_client = None
_firebase_ready = False

# Pydantic models
class UserRegistration(BaseModel):
    phone_number: str
    email: Optional[str] = None
    display_name: Optional[str] = None

class UserLogin(BaseModel):
    phone_number: str

class HealthResponse(BaseModel):
    status: str
    firebase: str
    timestamp: str
    environment: str

@lru_cache(maxsize=1)
def get_firebase_credentials() -> Optional[Dict]:
    """Get Firebase credentials from environment or file"""
    try:
        # Priority 1: Environment JSON (Render.com)
        creds_json = os.environ.get('FIREBASE_CREDENTIALS_JSON')
        if creds_json:
            logger.info("🔑 Using Firebase credentials from environment")
            return json.loads(creds_json)
        
        # Priority 2: Individual environment variables
        firebase_vars = {
            'type': os.environ.get('FIREBASE_TYPE'),
            'project_id': os.environ.get('FIREBASE_PROJECT_ID'),
            'private_key_id': os.environ.get('FIREBASE_PRIVATE_KEY_ID'),
            'private_key': os.environ.get('FIREBASE_PRIVATE_KEY'),
            'client_email': os.environ.get('FIREBASE_CLIENT_EMAIL'),
            'client_id': os.environ.get('FIREBASE_CLIENT_ID'),
            'auth_uri': os.environ.get('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
            'token_uri': os.environ.get('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
        }
        
        if all(firebase_vars[key] for key in ['type', 'project_id', 'private_key', 'client_email']):
            # Fix private key formatting
            firebase_vars['private_key'] = firebase_vars['private_key'].replace('\\n', '\n')
            logger.info("🔑 Using Firebase credentials from individual env vars")
            return firebase_vars
        
        # Priority 3: Service account file (local development)
        creds_file = 'firebase-service-account.json'
        if os.path.exists(creds_file):
            logger.info("🔑 Using Firebase credentials from local file")
            with open(creds_file, 'r') as f:
                return json.load(f)
        
        logger.warning("⚠️ No Firebase credentials found")
        return None
        
    except Exception as e:
        logger.error(f"❌ Firebase credentials error: {e}")
        return None

def initialize_firebase() -> bool:
    """Initialize Firebase Admin SDK once and cache globally"""
    global _firebase_app, _auth_client, _firestore_client, _firebase_ready
    
    if _firebase_ready:
        logger.info("🔥 Firebase already initialized")
        return True
    
    try:
        import firebase_admin
        from firebase_admin import credentials, auth, firestore
        
        # Get credentials
        creds_data = get_firebase_credentials()
        if not creds_data:
            logger.error("❌ No Firebase credentials available")
            return False
        
        # Initialize Firebase Admin SDK
        try:
            # Check if already initialized
            _firebase_app = firebase_admin.get_app()
            logger.info("🔄 Using existing Firebase app")
        except ValueError:
            # Not initialized yet, create new
            cred = credentials.Certificate(creds_data)
            _firebase_app = firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://investment-6d6f7-default-rtdb.firebaseio.com'
            })
            logger.info("🚀 Firebase Admin SDK initialized successfully")
        
        # Initialize global clients
        _auth_client = auth
        _firestore_client = firestore.client()
        _firebase_ready = True
        
        logger.info("✅ Firebase fully initialized and cached")
        logger.info(f"📱 Project: {creds_data.get('project_id', 'unknown')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Firebase initialization failed: {e}")
        _firebase_ready = False
        return False

def get_auth_client():
    """Get global Auth client"""
    if not _firebase_ready:
        initialize_firebase()
    return _auth_client

def get_firestore_client():
    """Get global Firestore client"""
    if not _firebase_ready:
        initialize_firebase()
    return _firestore_client

# FastAPI app
app = FastAPI(
    title="GrowFi Investment Platform",
    description="Firebase-only Python app for Render.com",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize Firebase on app startup"""
    logger.info("🚀 Starting Firebase-only app...")
    
    # Initialize Firebase immediately
    success = initialize_firebase()
    if success:
        logger.info("✅ App startup complete - Firebase ready")
    else:
        logger.warning("⚠️ App started but Firebase unavailable")

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint"""
    return {
        "app": "GrowFi Investment Platform",
        "version": "1.0.0",
        "firebase": "ready" if _firebase_ready else "unavailable",
        "timestamp": datetime.now().isoformat(),
        "environment": "render" if os.environ.get('RENDER_EXTERNAL_HOSTNAME') else "local"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Render.com"""
    try:
        firebase_status = "ready" if _firebase_ready else "unavailable"
        
        # Quick Firestore test if available
        if _firebase_ready:
            try:
                db = get_firestore_client()
                # Test with a simple read operation
                test_ref = db.collection('health').document('test')
                test_ref.set({'last_check': datetime.now().isoformat()}, merge=True)
                firebase_status = "connected"
            except Exception as e:
                logger.warning(f"Firestore test failed: {e}")
                firebase_status = "degraded"
        
        return HealthResponse(
            status="healthy" if firebase_status == "connected" else "degraded",
            firebase=firebase_status,
            timestamp=datetime.now().isoformat(),
            environment="render" if os.environ.get('RENDER_EXTERNAL_HOSTNAME') else "local"
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="error",
            firebase="error",
            timestamp=datetime.now().isoformat(),
            environment="render" if os.environ.get('RENDER_EXTERNAL_HOSTNAME') else "local"
        )

@app.post("/register")
async def register_user(user_data: UserRegistration):
    """Register new user with Firebase Auth and Firestore"""
    try:
        if not _firebase_ready:
            raise HTTPException(status_code=503, detail="Firebase not available")
        
        auth_client = get_auth_client()
        db = get_firestore_client()
        
        # Create unique UID
        import random
        import string
        uid = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        
        # Create user data for Firestore
        firestore_user_data = {
            'uid': uid,
            'phone_number': user_data.phone_number,
            'email': user_data.email or '',
            'display_name': user_data.display_name or user_data.phone_number,
            'balance': 0.0,
            'withdrawable_balance': 0.0,
            'non_withdrawable_bonus': 100.0,  # Registration bonus
            'total_invested': 0.0,
            'total_earnings': 0.0,
            'is_verified': True,
            'created_at': datetime.now().isoformat(),
            'last_login': datetime.now().isoformat(),
            'referral_code': ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        }
        
        # Save to Firestore
        user_ref = db.collection('users').document(uid)
        user_ref.set(firestore_user_data)
        
        # Create registration bonus transaction
        transaction_data = {
            'id': ''.join(random.choices(string.ascii_letters + string.digits, k=16)),
            'user_uid': uid,
            'type': 'registration_bonus',
            'amount': 100.0,
            'status': 'completed',
            'description': 'Welcome bonus - Thank you for joining GrowFi!',
            'created_at': datetime.now().isoformat()
        }
        
        # Save transaction to Firestore
        tx_ref = db.collection('transactions').document(transaction_data['id'])
        tx_ref.set(transaction_data)
        
        logger.info(f"✅ User registered: {user_data.phone_number}")
        
        return {
            "success": True,
            "message": "User registered successfully",
            "user": {
                "uid": uid,
                "phone_number": user_data.phone_number,
                "email": user_data.email,
                "display_name": firestore_user_data['display_name'],
                "balance": firestore_user_data['balance'],
                "registration_bonus": firestore_user_data['non_withdrawable_bonus'],
                "referral_code": firestore_user_data['referral_code']
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Registration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/login")
async def login_user(login_data: UserLogin):
    """Login user and return profile data"""
    try:
        if not _firebase_ready:
            raise HTTPException(status_code=503, detail="Firebase not available")
        
        db = get_firestore_client()
        
        # Find user by phone number
        users_ref = db.collection('users')
        query = users_ref.where('phone_number', '==', login_data.phone_number).limit(1)
        docs = list(query.stream())
        
        if not docs:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_doc = docs[0]
        user_data = user_doc.to_dict()
        
        # Update last login
        user_ref = db.collection('users').document(user_doc.id)
        user_ref.update({'last_login': datetime.now().isoformat()})
        
        logger.info(f"✅ User logged in: {login_data.phone_number}")
        
        return {
            "success": True,
            "message": "Login successful",
            "user": {
                "uid": user_data['uid'],
                "phone_number": user_data['phone_number'],
                "email": user_data.get('email', ''),
                "display_name": user_data.get('display_name', ''),
                "balance": user_data.get('balance', 0.0),
                "withdrawable_balance": user_data.get('withdrawable_balance', 0.0),
                "non_withdrawable_bonus": user_data.get('non_withdrawable_bonus', 0.0),
                "total_invested": user_data.get('total_invested', 0.0),
                "total_earnings": user_data.get('total_earnings', 0.0),
                "referral_code": user_data.get('referral_code', ''),
                "last_login": user_data.get('last_login', '')
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login failed: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.get("/users/{phone_number}")
async def get_user_profile(phone_number: str):
    """Get user profile by phone number"""
    try:
        if not _firebase_ready:
            raise HTTPException(status_code=503, detail="Firebase not available")
        
        db = get_firestore_client()
        
        # Find user by phone number
        users_ref = db.collection('users')
        query = users_ref.where('phone_number', '==', phone_number).limit(1)
        docs = list(query.stream())
        
        if not docs:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_doc = docs[0]
        user_data = user_doc.to_dict()
        
        return {
            "success": True,
            "user": user_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get user failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")

@app.get("/transactions/{user_uid}")
async def get_user_transactions(user_uid: str, limit: int = 10):
    """Get user transactions from Firestore"""
    try:
        if not _firebase_ready:
            raise HTTPException(status_code=503, detail="Firebase not available")
        
        db = get_firestore_client()
        
        # Get user transactions
        transactions_ref = db.collection('transactions')
        query = transactions_ref.where('user_uid', '==', user_uid).limit(limit)
        docs = list(query.stream())
        
        transactions = []
        for doc in docs:
            tx_data = doc.to_dict()
            transactions.append(tx_data)
        
        return {
            "success": True,
            "transactions": transactions,
            "count": len(transactions)
        }
        
    except Exception as e:
        logger.error(f"❌ Get transactions failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get transactions: {str(e)}")

# Initialize Firebase on module import for production
if os.environ.get('RENDER_EXTERNAL_HOSTNAME'):
    logger.info("🚀 Render.com detected - pre-initializing Firebase")
    initialize_firebase()

if __name__ == "__main__":
    # For local development
    uvicorn.run(
        "firebase_only_app:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=True
    )
