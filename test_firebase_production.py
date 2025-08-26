#!/usr/bin/env python3
"""
Firebase Production Test Script for Render.com
This script helps verify Firebase configuration in production
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/opt/render/project/src')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

import json
from myproject.firebase_app import get_firebase_app
from firebase_admin import db as firebase_db, firestore

def test_firebase_connection():
    """Test Firebase connection and basic operations"""
    print("🔥 Testing Firebase Connection on Render.com")
    print("=" * 50)
    
    # Check environment variables
    print("📋 Environment Variables Check:")
    firebase_creds_json = os.environ.get('FIREBASE_CREDENTIALS_JSON')
    render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    
    print(f"   RENDER_EXTERNAL_HOSTNAME: {'✓' if render_hostname else '✗'}")
    print(f"   FIREBASE_CREDENTIALS_JSON: {'✓' if firebase_creds_json else '✗'}")
    
    if firebase_creds_json:
        try:
            creds_data = json.loads(firebase_creds_json)
            print(f"   - Project ID: {creds_data.get('project_id', 'N/A')}")
            print(f"   - Client Email: {creds_data.get('client_email', 'N/A')}")
            print(f"   - Private Key: {'✓' if creds_data.get('private_key') else '✗'}")
        except Exception as e:
            print(f"   ❌ Error parsing Firebase credentials: {e}")
    
    print("\n🔥 Firebase App Initialization:")
    try:
        app = get_firebase_app()
        print("   ✅ Firebase app initialized successfully!")
        print(f"   App name: {app.name}")
        print(f"   Project ID: {app.project_id}")
    except Exception as e:
        print(f"   ❌ Firebase app initialization failed: {e}")
        return False
    
    print("\n📊 Testing Firebase Realtime Database:")
    try:
        ref = firebase_db.reference('/', app=app)
        test_ref = ref.child('test')
        
        # Write test data
        test_data = {
            'message': 'Hello from Render.com!',
            'timestamp': '2025-08-26T15:00:00Z',
            'source': 'production_test'
        }
        test_ref.set(test_data)
        print("   ✅ Successfully wrote to Realtime Database!")
        
        # Read test data
        data = test_ref.get()
        if data and data.get('message') == 'Hello from Render.com!':
            print("   ✅ Successfully read from Realtime Database!")
        else:
            print("   ⚠️ Data read doesn't match what was written")
            
        # Clean up test data
        test_ref.delete()
        print("   ✅ Test data cleaned up")
        
    except Exception as e:
        print(f"   ❌ Realtime Database test failed: {e}")
        return False
    
    print("\n🗃️ Testing Firestore:")
    try:
        db = firestore.client(app=app)
        
        # Write test document
        test_doc = {
            'message': 'Hello from Render.com Firestore!',
            'timestamp': firestore.SERVER_TIMESTAMP,
            'source': 'production_test'
        }
        doc_ref = db.collection('test').document('render_test')
        doc_ref.set(test_doc)
        print("   ✅ Successfully wrote to Firestore!")
        
        # Read test document
        doc = doc_ref.get()
        if doc.exists and doc.to_dict().get('message') == 'Hello from Render.com Firestore!':
            print("   ✅ Successfully read from Firestore!")
        else:
            print("   ⚠️ Document read doesn't match what was written")
            
        # Clean up test document
        doc_ref.delete()
        print("   ✅ Test document cleaned up")
        
    except Exception as e:
        print(f"   ❌ Firestore test failed: {e}")
        return False
    
    print("\n🎉 All Firebase tests passed!")
    print("Firebase is properly configured and working on Render.com")
    return True

if __name__ == "__main__":
    try:
        success = test_firebase_connection()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test script failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
