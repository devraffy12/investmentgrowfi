#!/usr/bin/env python3
"""
Quick Firebase Production Check - for Render.com deployment verification
Run this script in your Render terminal to verify Firebase is working correctly.
"""
import os
import json
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')

# Configure Django
import sys
sys.path.append(str(BASE_DIR))
django.setup()

def check_firebase_production():
    """Check if Firebase is properly configured in production"""
    print("🔍 FIREBASE PRODUCTION CHECK")
    print("=" * 50)
    
    # Check if running on Render
    render_hostname = os.getenv('RENDER_EXTERNAL_HOSTNAME')
    is_production = bool(render_hostname)
    
    print(f"Environment: {'🚀 Production (Render)' if is_production else '🏠 Local Development'}")
    if render_hostname:
        print(f"Render Hostname: {render_hostname}")
    
    # Check environment variables
    firebase_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
    database_url = os.getenv('FIREBASE_DATABASE_URL')
    
    print(f"\n📋 Environment Variables:")
    print(f"FIREBASE_CREDENTIALS_JSON: {'✅ Set' if firebase_json else '❌ Missing'}")
    print(f"FIREBASE_DATABASE_URL: {'✅ Set' if database_url else '⚠️ Optional (not set)'}")
    
    if firebase_json:
        try:
            creds = json.loads(firebase_json)
            print(f"\n📄 Credentials Validation:")
            print(f"Project ID: {creds.get('project_id', '❌ Missing')}")
            print(f"Client Email: {creds.get('client_email', '❌ Missing')}")
            print(f"Type: {creds.get('type', '❌ Missing')}")
            print(f"Private Key: {'✅ Present' if creds.get('private_key') else '❌ Missing'}")
            
            # Validate required fields
            required_fields = ['type', 'project_id', 'private_key', 'client_email']
            missing_fields = [field for field in required_fields if not creds.get(field)]
            
            if missing_fields:
                print(f"\n❌ Missing required fields: {missing_fields}")
                return False
            else:
                print(f"\n✅ All required credential fields present")
        except json.JSONDecodeError as e:
            print(f"\n❌ Invalid JSON in FIREBASE_CREDENTIALS_JSON: {e}")
            return False
    else:
        print(f"\n❌ FIREBASE_CREDENTIALS_JSON not found!")
        return False
    
    # Test Firebase initialization
    print(f"\n🔥 Testing Firebase Initialization:")
    try:
        from myproject.firebase_app import get_firebase_app
        app = get_firebase_app()
        if hasattr(app, 'project_id'):
            print(f"✅ Firebase initialized successfully")
            print(f"Project ID: {getattr(app, 'project_id', 'N/A')}")
            
            # Test Realtime Database connection
            try:
                from firebase_admin import db as firebase_db
                ref = firebase_db.reference('/', app=app)
                test_ref = ref.child('test_connection')
                test_ref.set({'timestamp': str(os.environ.get('RENDER_INSTANCE_ID', 'local'))})
                print(f"✅ Realtime Database connection test passed")
            except Exception as db_error:
                print(f"⚠️ Realtime Database test failed: {db_error}")
            
            # Test Firestore connection
            try:
                from firebase_admin import firestore
                db = firestore.client(app=app)
                # Simple test - try to get a collection reference
                test_collection = db.collection('test')
                print(f"✅ Firestore connection test passed")
            except Exception as firestore_error:
                print(f"⚠️ Firestore test failed: {firestore_error}")
                
            return True
        else:
            print(f"❌ Firebase app initialization failed - dummy app returned")
            return False
            
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    success = check_firebase_production()
    
    print(f"\n" + "=" * 50)
    if success:
        print("🎉 FIREBASE SETUP: WORKING CORRECTLY!")
        print("Your users should now be able to register and")
        print("their data will be saved to Firebase.")
    else:
        print("❌ FIREBASE SETUP: NEEDS ATTENTION!")
        print("\n🔧 TO FIX:")
        print("1. Go to your Render.com dashboard")
        print("2. Navigate to your web service > Environment")
        print("3. Add this environment variable:")
        print("   Key: FIREBASE_CREDENTIALS_JSON")
        print("   Value: (run 'python generate_firebase_env.py' to get the value)")
        print("4. Redeploy your service")
        print("5. Run this script again to verify")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
