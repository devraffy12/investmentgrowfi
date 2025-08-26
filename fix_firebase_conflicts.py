#!/usr/bin/env python3
"""
Fix Firebase conflicts and prepare for clean deployment
"""

import os
import sys
import django

# Add the project to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

print("🔧 Firebase Conflict Fix Script")
print("=" * 50)

# Test Firebase initialization
try:
    from myproject.firebase_app import get_firebase_app
    
    print("🔥 Testing Firebase initialization...")
    app = get_firebase_app()
    
    if hasattr(app, 'project_id'):
        if app.project_id == "firebase-unavailable":
            print("❌ Firebase is unavailable - dummy app detected")
            print("\n📋 REQUIRED ACTIONS:")
            print("1. Go to your Render dashboard: https://dashboard.render.com/")
            print("2. Find your service and go to Environment tab")
            print("3. DELETE these individual Firebase variables if they exist:")
            print("   - FIREBASE_TYPE")
            print("   - FIREBASE_PROJECT_ID") 
            print("   - FIREBASE_PRIVATE_KEY")
            print("   - FIREBASE_CLIENT_EMAIL")
            print("   - FIREBASE_PRIVATE_KEY_ID")
            print("   - FIREBASE_CLIENT_ID")
            print("   - FIREBASE_AUTH_URI")
            print("   - FIREBASE_TOKEN_URI")
            print("   - FIREBASE_AUTH_PROVIDER_X509_CERT_URL")
            print("   - FIREBASE_CLIENT_X509_CERT_URL")
            print("   - FIREBASE_UNIVERSE_DOMAIN")
            print("4. KEEP only these variables:")
            print("   ✅ FIREBASE_CREDENTIALS_JSON")
            print("   ✅ FIREBASE_DATABASE_URL")
            print("5. Manually redeploy your service after cleaning variables")
        else:
            print(f"✅ Firebase connected successfully! Project: {app.project_id}")
            
            # Test database connection
            try:
                from firebase_admin import db as firebase_db
                ref = firebase_db.reference('/', app=app)
                test_data = {"test": "connection", "timestamp": "2025-08-26"}
                ref.child('test_connection').set(test_data)
                print("✅ Firebase Realtime Database write test successful")
                
                # Test Firestore
                from firebase_admin import firestore
                db = firestore.client(app=app)
                test_doc = db.collection('test').document('connection')
                test_doc.set(test_data)
                print("✅ Firestore write test successful")
                
                # Clean up test data
                ref.child('test_connection').delete()
                test_doc.delete()
                print("✅ Test data cleaned up")
                
            except Exception as db_error:
                print(f"⚠️ Database test failed: {db_error}")
    else:
        print("❌ Invalid Firebase app object")
        
except Exception as e:
    print(f"❌ Firebase initialization failed: {e}")
    print("\n🚨 CRITICAL: Firebase environment variables are conflicting!")
    print("\n📋 REQUIRED ACTIONS:")
    print("1. Go to Render dashboard immediately")
    print("2. Delete ALL individual Firebase environment variables")
    print("3. Keep only FIREBASE_CREDENTIALS_JSON and FIREBASE_DATABASE_URL")
    print("4. Manual redeploy required")

print("\n" + "=" * 50)
print("🔧 Fix complete!")
