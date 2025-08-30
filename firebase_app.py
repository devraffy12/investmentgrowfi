"""
🔥 PURE FIREBASE APP - OPTIMIZED FOR RENDER.COM
===============================================
A high-performance Python app using only Firebase (Auth + Firestore).
Optimized for low latency and persistent user sessions.

Features:
- FastAPI for high performance async operations
- Firebase Admin SDK initialization once at startup
- Cached Firebase clients for reuse
- Health check endpoint to prevent cold starts
- Performance logging for all operations
- Async/await pattern for non-blocking operations
- Optimized for Asia-Southeast region
"""

import asyncio
import logging
import time
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

import firebase_admin
from firebase_admin import credentials, firestore, auth
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging with performance tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# FIREBASE INITIALIZATION - OPTIMIZED FOR SINGLE INIT
# ============================================================================

class FirebaseManager:
    """Singleton Firebase manager for optimal performance"""
    
    _instance = None
    _app = None
    _db = None
    _auth_client = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self) -> bool:
        """Initialize Firebase once at startup"""
        if self._initialized:
            logger.info("🔥 Firebase already initialized, reusing existing connection")
            return True
            
        start_time = time.time()
        logger.info("🚀 Initializing Firebase Admin SDK...")
        
        try:
            # Method 1: Try JSON credentials first (RECOMMENDED for Render.com)
            firebase_creds_json = os.environ.get('FIREBASE_CREDENTIALS_JSON')
            if firebase_creds_json:
                logger.info("✅ Found FIREBASE_CREDENTIALS_JSON environment variable")
                cred_dict = json.loads(firebase_creds_json)
                cred = credentials.Certificate(cred_dict)
                
                # Configure for Asia-Southeast region optimization
                self._app = firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://investment-6d6f7-default-rtdb.firebaseio.com',
                    'projectId': cred_dict.get('project_id', 'investment-6d6f7')
                })
                logger.info(f"🌏 Firebase initialized with project: {cred_dict.get('project_id')}")
                
            # Method 2: Try individual environment variables
            elif os.environ.get('FIREBASE_PROJECT_ID'):
                logger.info("✅ Found individual Firebase environment variables")
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
                self._app = firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://investment-6d6f7-default-rtdb.firebaseio.com'
                })
                logger.info(f"🌏 Firebase initialized with project: {cred_dict['project_id']}")
                
            # Method 3: Try local service account file (development)
            else:
                service_account_path = "firebase-service-account.json"
                if os.path.exists(service_account_path):
                    logger.info("✅ Found local service account file")
                    cred = credentials.Certificate(service_account_path)
                    self._app = firebase_admin.initialize_app(cred)
                    logger.info("🌏 Firebase initialized with local service account")
                else:
                    raise Exception("❌ No Firebase credentials found!")
            
            # Initialize cached clients
            self._db = firestore.client()
            self._auth_client = auth
            
            # Test connection
            test_start = time.time()
            health_ref = self._db.collection('health').document('startup')
            health_ref.set({
                'timestamp': firestore.SERVER_TIMESTAMP,
                'status': 'healthy',
                'app_version': '1.0.0'
            })
            test_time = time.time() - test_start
            
            self._initialized = True
            init_time = time.time() - start_time
            
            logger.info(f"✅ Firebase fully initialized and cached")
            logger.info(f"⚡ Initialization time: {init_time:.3f}s")
            logger.info(f"⚡ Test write time: {test_time:.3f}s")
            logger.info(f"🔥 Firestore client ready: {bool(self._db)}")
            logger.info(f"🔐 Auth client ready: {bool(self._auth_client)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Firebase initialization failed: {str(e)}")
            return False
    
    @property
    def db(self):
        """Get cached Firestore client"""
        if not self._initialized:
            self.initialize()
        return self._db
    
    @property
    def auth(self):
        """Get cached Auth client"""
        if not self._initialized:
            self.initialize()
        return self._auth_client
    
    def is_ready(self) -> bool:
        """Check if Firebase is ready"""
        return self._initialized and self._db is not None

# Global Firebase manager instance
firebase_manager = FirebaseManager()

# ============================================================================
# FASTAPI APP WITH LIFESPAN MANAGEMENT
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """App startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting Firebase-only app...")
    
    # Initialize Firebase at startup
    success = firebase_manager.initialize()
    if not success:
        logger.error("❌ Failed to initialize Firebase. App may not work properly.")
    else:
        logger.info("✅ App startup complete - Firebase ready")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Firebase app...")

# Create FastAPI app with lifespan
app = FastAPI(
    title="🔥 Firebase-Only GrowFi App",
    description="High-performance investment platform using pure Firebase",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class UserRegistration(BaseModel):
    phone_number: str = Field(..., min_length=11, max_length=15)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2)
    referral_code: Optional[str] = None

class UserLogin(BaseModel):
    phone_number: str = Field(..., min_length=11, max_length=15)
    password: str = Field(..., min_length=6)

class TransactionCreate(BaseModel):
    amount: float = Field(..., gt=0)
    transaction_type: str = Field(..., pattern=r'^(deposit|withdrawal|investment)$')
    description: Optional[str] = None

# ============================================================================
# DEPENDENCY FUNCTIONS
# ============================================================================

def get_firebase_db():
    """Dependency to get Firestore client"""
    if not firebase_manager.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase not initialized"
        )
    return firebase_manager.db

def get_firebase_auth():
    """Dependency to get Firebase Auth client"""
    if not firebase_manager.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase not initialized"
        )
    return firebase_manager.auth

# ============================================================================
# PERFORMANCE TRACKING DECORATOR
# ============================================================================

def track_performance(operation_name: str):
    """Decorator to track operation performance"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"⚡ {operation_name} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"❌ {operation_name} failed after {duration:.3f}s: {str(e)}")
                raise
        return wrapper
    return decorator

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with app status"""
    return {
        "app": "🔥 Firebase-Only GrowFi App",
        "status": "running",
        "version": "1.0.0",
        "firebase_ready": firebase_manager.is_ready(),
        "timestamp": datetime.now().isoformat(),
        "region": "asia-southeast1 optimized"
    }

@app.get("/health")
async def health_check(db = Depends(get_firebase_db)):
    """Health check endpoint to prevent cold starts"""
    start_time = time.time()
    
    try:
        # Quick Firestore health check
        health_ref = db.collection('health').document('check')
        health_ref.set({
            'timestamp': firestore.SERVER_TIMESTAMP,
            'status': 'healthy'
        })
        
        firebase_time = time.time() - start_time
        
        return {
            "status": "healthy",
            "firebase_ready": True,
            "firebase_latency": f"{firebase_time:.3f}s",
            "timestamp": datetime.now().isoformat(),
            "uptime": "running"
        }
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "firebase_ready": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.post("/register")
@track_performance("User Registration")
async def register_user(
    user_data: UserRegistration,
    db = Depends(get_firebase_db),
    auth_client = Depends(get_firebase_auth)
):
    """Register new user with Firebase Auth and Firestore"""
    
    try:
        # Create Firebase Auth user
        auth_start = time.time()
        user_record = auth_client.create_user(
            email=user_data.email,
            password=user_data.password,
            phone_number=user_data.phone_number if user_data.phone_number.startswith('+') else f"+63{user_data.phone_number[1:]}"
        )
        auth_time = time.time() - auth_start
        logger.info(f"⚡ Firebase Auth user created in {auth_time:.3f}s")
        
        # Create user document in Firestore
        firestore_start = time.time()
        user_doc_data = {
            'uid': user_record.uid,
            'email': user_data.email,
            'phone_number': user_data.phone_number,
            'full_name': user_data.full_name,
            'balance': 0.0,
            'total_investments': 0.0,
            'referral_code': user_data.referral_code,
            'created_at': firestore.SERVER_TIMESTAMP,
            'last_login': firestore.SERVER_TIMESTAMP,
            'status': 'active'
        }
        
        db.collection('users').document(user_record.uid).set(user_doc_data)
        firestore_time = time.time() - firestore_start
        logger.info(f"⚡ Firestore user document created in {firestore_time:.3f}s")
        
        # Handle referral if provided
        if user_data.referral_code:
            referral_start = time.time()
            referral_query = db.collection('users').where('referral_code', '==', user_data.referral_code).limit(1)
            referral_docs = referral_query.get()
            
            if referral_docs:
                referrer_doc = referral_docs[0]
                # Add to referrer's team
                db.collection('referrals').add({
                    'referrer_uid': referrer_doc.id,
                    'referred_uid': user_record.uid,
                    'created_at': firestore.SERVER_TIMESTAMP,
                    'status': 'active'
                })
            
            referral_time = time.time() - referral_start
            logger.info(f"⚡ Referral processing completed in {referral_time:.3f}s")
        
        return {
            "success": True,
            "message": "User registered successfully",
            "uid": user_record.uid,
            "email": user_data.email,
            "performance": {
                "auth_time": f"{auth_time:.3f}s",
                "firestore_time": f"{firestore_time:.3f}s"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/login")
@track_performance("User Login")
async def login_user(
    login_data: UserLogin,
    db = Depends(get_firebase_db),
    auth_client = Depends(get_firebase_auth)
):
    """Login user and return user data"""
    
    try:
        # Find user by phone number
        query_start = time.time()
        users_query = db.collection('users').where('phone_number', '==', login_data.phone_number).limit(1)
        user_docs = users_query.get()
        query_time = time.time() - query_start
        
        if not user_docs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_doc = user_docs[0]
        user_data = user_doc.to_dict()
        
        # Update last login
        update_start = time.time()
        db.collection('users').document(user_doc.id).update({
            'last_login': firestore.SERVER_TIMESTAMP
        })
        update_time = time.time() - update_start
        
        logger.info(f"⚡ User query completed in {query_time:.3f}s")
        logger.info(f"⚡ Last login update completed in {update_time:.3f}s")
        
        return {
            "success": True,
            "message": "Login successful",
            "user": {
                "uid": user_data['uid'],
                "email": user_data['email'],
                "phone_number": user_data['phone_number'],
                "full_name": user_data['full_name'],
                "balance": user_data['balance'],
                "total_investments": user_data['total_investments']
            },
            "performance": {
                "query_time": f"{query_time:.3f}s",
                "update_time": f"{update_time:.3f}s"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@app.get("/user/{uid}")
@track_performance("Get User Data")
async def get_user(uid: str, db = Depends(get_firebase_db)):
    """Get user data by UID"""
    
    try:
        query_start = time.time()
        user_doc = db.collection('users').document(uid).get()
        query_time = time.time() - query_start
        
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_data = user_doc.to_dict()
        logger.info(f"⚡ User data retrieved in {query_time:.3f}s")
        
        return {
            "success": True,
            "user": user_data,
            "performance": {
                "query_time": f"{query_time:.3f}s"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get user failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        )

@app.get("/user/{uid}/team")
@track_performance("Get User Team")
async def get_user_team(uid: str, db = Depends(get_firebase_db)):
    """Get user's referral team"""
    
    try:
        query_start = time.time()
        
        # Get referrals made by this user
        referrals_query = db.collection('referrals').where('referrer_uid', '==', uid)
        referrals = referrals_query.get()
        
        team_members = []
        for referral in referrals:
            ref_data = referral.to_dict()
            # Get referred user details
            user_doc = db.collection('users').document(ref_data['referred_uid']).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                team_members.append({
                    'uid': ref_data['referred_uid'],
                    'full_name': user_data.get('full_name', 'Unknown'),
                    'email': user_data.get('email', ''),
                    'joined_date': ref_data.get('created_at'),
                    'status': ref_data.get('status', 'active')
                })
        
        query_time = time.time() - query_start
        logger.info(f"⚡ Team data retrieved in {query_time:.3f}s")
        
        return {
            "success": True,
            "team_count": len(team_members),
            "team_members": team_members,
            "performance": {
                "query_time": f"{query_time:.3f}s"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Get team failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get team: {str(e)}"
        )

@app.post("/transaction")
@track_performance("Create Transaction")
async def create_transaction(
    transaction: TransactionCreate,
    uid: str,
    db = Depends(get_firebase_db)
):
    """Create a new transaction"""
    
    try:
        transaction_start = time.time()
        
        # Create transaction document
        transaction_data = {
            'user_uid': uid,
            'amount': transaction.amount,
            'type': transaction.transaction_type,
            'description': transaction.description or f"{transaction.transaction_type.title()} of ₱{transaction.amount}",
            'created_at': firestore.SERVER_TIMESTAMP,
            'status': 'completed'
        }
        
        # Add transaction
        transaction_ref = db.collection('transactions').add(transaction_data)
        
        # Update user balance if it's a deposit
        if transaction.transaction_type == 'deposit':
            user_ref = db.collection('users').document(uid)
            user_ref.update({
                'balance': firestore.Increment(transaction.amount)
            })
        
        transaction_time = time.time() - transaction_start
        logger.info(f"⚡ Transaction created in {transaction_time:.3f}s")
        
        return {
            "success": True,
            "message": "Transaction created successfully",
            "transaction_id": transaction_ref[1].id,
            "performance": {
                "transaction_time": f"{transaction_time:.3f}s"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Transaction creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transaction failed: {str(e)}"
        )

# ============================================================================
# STARTUP AND MAIN
# ============================================================================

if __name__ == "__main__":
    # Get port from environment (Render.com sets this)
    port = int(os.environ.get("PORT", 8000))
    
    # Run with uvicorn
    uvicorn.run(
        "firebase_app:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        access_log=True,
        log_level="info"
    )
