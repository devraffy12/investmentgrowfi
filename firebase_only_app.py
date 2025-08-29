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
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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

# Create templates directory if it doesn't exist
import pathlib
templates_dir = pathlib.Path("templates")
if not templates_dir.exists():
    templates_dir.mkdir()

# Set up templates and static files
templates = Jinja2Templates(directory="templates")

# Create simple HTML templates inline since we might not have template files
HOMEPAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GrowFi - Investment Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .container { background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); text-align: center; max-width: 400px; width: 90%; }
        h1 { color: #333; margin-bottom: 1rem; font-size: 2rem; }
        .subtitle { color: #666; margin-bottom: 2rem; }
        .btn-group { display: flex; flex-direction: column; gap: 1rem; }
        .btn { padding: 12px 24px; border: none; border-radius: 10px; font-size: 16px; font-weight: 600; cursor: pointer; text-decoration: none; display: inline-block; transition: all 0.3s ease; }
        .btn-primary { background: #667eea; color: white; }
        .btn-secondary { background: #f8f9fa; color: #333; border: 2px solid #dee2e6; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .features { margin-top: 2rem; text-align: left; }
        .feature { padding: 0.5rem 0; color: #666; }
        .feature::before { content: "✓"; color: #28a745; font-weight: bold; margin-right: 0.5rem; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 GrowFi</h1>
        <p class="subtitle">Your Investment Growth Platform</p>
        
        <div class="btn-group">
            <a href="/register" class="btn btn-primary">Create Account</a>
            <a href="/login" class="btn btn-secondary">Login</a>
            <a href="/dashboard" class="btn btn-secondary">Dashboard</a>
        </div>
        
        <div class="features">
            <div class="feature">Secure Firebase Authentication</div>
            <div class="feature">Real-time Investment Tracking</div>
            <div class="feature">Daily Earnings & Rewards</div>
            <div class="feature">Mobile-Responsive Design</div>
        </div>
    </div>
</body>
</html>
"""

REGISTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register - GrowFi</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .container { background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); max-width: 400px; width: 90%; }
        h1 { color: #333; margin-bottom: 1rem; text-align: center; }
        .form-group { margin-bottom: 1rem; }
        label { display: block; margin-bottom: 0.5rem; color: #555; font-weight: 500; }
        input { width: 100%; padding: 12px; border: 2px solid #e1e5e9; border-radius: 8px; font-size: 16px; }
        input:focus { outline: none; border-color: #667eea; }
        .btn { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; margin-top: 1rem; }
        .btn:hover { background: #5a6fd8; }
        .back-link { text-align: center; margin-top: 1rem; }
        .back-link a { color: #667eea; text-decoration: none; }
        .message { margin-top: 1rem; padding: 10px; border-radius: 5px; text-align: center; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Create Account</h1>
        <form id="registerForm">
            <div class="form-group">
                <label for="phone">Phone Number *</label>
                <input type="tel" id="phone" name="phone_number" required placeholder="+639123456789">
            </div>
            <div class="form-group">
                <label for="email">Email (Optional)</label>
                <input type="email" id="email" name="email" placeholder="your@email.com">
            </div>
            <div class="form-group">
                <label for="name">Display Name (Optional)</label>
                <input type="text" id="name" name="display_name" placeholder="Your Name">
            </div>
            <button type="submit" class="btn">Create Account</button>
        </form>
        <div id="message"></div>
        <div class="back-link">
            <a href="/">← Back to Home</a>
        </div>
    </div>
    
    <script>
        document.getElementById('registerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                const messageDiv = document.getElementById('message');
                
                if (response.ok) {
                    messageDiv.innerHTML = '<div class="success">Registration successful! You can now login.</div>';
                    e.target.reset();
                } else {
                    messageDiv.innerHTML = `<div class="error">${result.detail || 'Registration failed'}</div>`;
                }
            } catch (error) {
                document.getElementById('message').innerHTML = '<div class="error">Network error. Please try again.</div>';
            }
        });
    </script>
</body>
</html>
"""

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - GrowFi</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .container { background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); max-width: 400px; width: 90%; }
        h1 { color: #333; margin-bottom: 1rem; text-align: center; }
        .form-group { margin-bottom: 1rem; }
        label { display: block; margin-bottom: 0.5rem; color: #555; font-weight: 500; }
        input { width: 100%; padding: 12px; border: 2px solid #e1e5e9; border-radius: 8px; font-size: 16px; }
        input:focus { outline: none; border-color: #667eea; }
        .btn { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; margin-top: 1rem; }
        .btn:hover { background: #5a6fd8; }
        .back-link { text-align: center; margin-top: 1rem; }
        .back-link a { color: #667eea; text-decoration: none; }
        .message { margin-top: 1rem; padding: 10px; border-radius: 5px; text-align: center; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Login</h1>
        <form id="loginForm">
            <div class="form-group">
                <label for="phone">Phone Number</label>
                <input type="tel" id="phone" name="phone_number" required placeholder="+639123456789">
            </div>
            <button type="submit" class="btn">Login</button>
        </form>
        <div id="message"></div>
        <div class="back-link">
            <a href="/">← Back to Home</a> | <a href="/register">Create Account</a>
        </div>
    </div>
    
    <script>
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                const messageDiv = document.getElementById('message');
                
                if (response.ok) {
                    messageDiv.innerHTML = '<div class="success">Login successful! Redirecting to dashboard...</div>';
                    setTimeout(() => window.location.href = '/dashboard', 1500);
                } else {
                    messageDiv.innerHTML = `<div class="error">${result.detail || 'Login failed'}</div>`;
                }
            } catch (error) {
                document.getElementById('message').innerHTML = '<div class="error">Network error. Please try again.</div>';
            }
        });
    </script>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - GrowFi</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #f8f9fa; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem; text-align: center; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .stat-card { background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
        .stat-value { font-size: 2rem; font-weight: bold; color: #667eea; margin-bottom: 0.5rem; }
        .stat-label { color: #666; font-size: 0.9rem; }
        .actions { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .btn { padding: 12px 24px; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; text-decoration: none; display: inline-block; text-align: center; transition: all 0.3s ease; }
        .btn-primary { background: #667eea; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .transactions { background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 1.5rem; }
        .transaction-item { padding: 1rem; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
        .transaction-item:last-child { border-bottom: none; }
        .transaction-amount { font-weight: bold; color: #28a745; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 GrowFi Dashboard</h1>
        <p>Welcome to your investment platform</p>
    </div>
    
    <div class="container">
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="totalBalance">₱0.00</div>
                <div class="stat-label">Total Balance</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="totalEarnings">₱0.00</div>
                <div class="stat-label">Total Earnings</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="activeInvestments">0</div>
                <div class="stat-label">Active Investments</div>
            </div>
        </div>
        
        <div class="actions">
            <button class="btn btn-primary" onclick="investNow()">Invest Now</button>
            <button class="btn btn-success" onclick="loadTransactions()">View Records</button>
            <a href="/" class="btn btn-secondary">Home</a>
        </div>
        
        <div class="transactions">
            <h3>Recent Transactions</h3>
            <div id="transactionsList">
                <p style="text-align: center; color: #666; padding: 2rem;">Loading transactions...</p>
            </div>
        </div>
    </div>
    
    <script>
        async function loadTransactions() {
            try {
                const response = await fetch('/api/transactions');
                const result = await response.json();
                
                const transactionsList = document.getElementById('transactionsList');
                
                if (result.success && result.transactions.length > 0) {
                    transactionsList.innerHTML = result.transactions.map(tx => `
                        <div class="transaction-item">
                            <div>
                                <strong>${tx.type || 'Investment'}</strong><br>
                                <small>${new Date(tx.timestamp).toLocaleString()}</small>
                            </div>
                            <div class="transaction-amount">₱${tx.amount || '0.00'}</div>
                        </div>
                    `).join('');
                } else {
                    transactionsList.innerHTML = '<p style="text-align: center; color: #666; padding: 2rem;">No transactions found. Start investing to see your records here!</p>';
                }
            } catch (error) {
                document.getElementById('transactionsList').innerHTML = '<p style="text-align: center; color: #dc3545; padding: 2rem;">Error loading transactions. Please try again.</p>';
            }
        }
        
        async function investNow() {
            const amount = prompt('Enter investment amount (₱):');
            if (!amount || isNaN(amount) || amount <= 0) return;
            
            try {
                const response = await fetch('/api/invest', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ amount: parseFloat(amount) })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    alert('Investment successful!');
                    loadTransactions();
                } else {
                    alert(result.detail || 'Investment failed');
                }
            } catch (error) {
                alert('Network error. Please try again.');
            }
        }
        
        // Load transactions on page load
        loadTransactions();
    </script>
</body>
</html>
"""

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

@app.get("/", response_class=HTMLResponse)
async def root():
    """Home page"""
    return HOMEPAGE_HTML

@app.get("/register", response_class=HTMLResponse)
async def register_page():
    """Registration page"""
    return REGISTER_HTML

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """Login page"""
    return LOGIN_HTML

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    """Dashboard page"""
    return DASHBOARD_HTML

@app.get("/api", response_model=Dict[str, Any])
async def api_info():
    """API information endpoint"""
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

@app.post("/api/register")
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

@app.post("/api/login")
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

@app.get("/api/users/{phone_number}")
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

@app.get("/api/transactions")
async def get_transactions(user_uid: Optional[str] = None, limit: int = 10):
    """Get transactions from Firestore"""
    try:
        if not _firebase_ready:
            raise HTTPException(status_code=503, detail="Firebase not available")
        
        db = get_firestore_client()
        
        # Get transactions (filtered by user if provided)
        transactions_ref = db.collection('transactions')
        if user_uid:
            query = transactions_ref.where('user_uid', '==', user_uid).limit(limit)
        else:
            query = transactions_ref.limit(limit)
        
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

class InvestmentRequest(BaseModel):
    amount: float
    user_uid: Optional[str] = None

@app.post("/api/invest")
async def create_investment(investment: InvestmentRequest):
    """Create a new investment"""
    try:
        if not _firebase_ready:
            raise HTTPException(status_code=503, detail="Firebase not available")
        
        if investment.amount <= 0:
            raise HTTPException(status_code=400, detail="Investment amount must be positive")
        
        db = get_firestore_client()
        
        # Create transaction record
        transaction_data = {
            'user_uid': investment.user_uid or 'demo_user',
            'type': 'investment',
            'amount': investment.amount,
            'status': 'completed',
            'timestamp': datetime.now().isoformat(),
            'description': f'Investment of ₱{investment.amount}'
        }
        
        # Add to Firestore
        db.collection('transactions').add(transaction_data)
        
        logger.info(f"✅ Investment created: ₱{investment.amount}")
        
        return {
            "success": True,
            "message": "Investment successful",
            "transaction": transaction_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Investment failed: {e}")
        raise HTTPException(status_code=500, detail=f"Investment failed: {str(e)}")

@app.get("/api/transactions/{user_uid}")
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
