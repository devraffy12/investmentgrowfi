#!/usr/bin/env python3
"""
Firebase Production Debug Script
This script will test Firebase connectivity and save operations in production
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from myproject.models import UserProfile
from myproject.views import save_user_to_firebase_realtime_db
from django.utils import timezone
import json

def test_firebase_production():
    """Test Firebase functionality in production"""
    print("🔥 FIREBASE PRODUCTION DEBUG TEST")
    print("=" * 60)
    
    # Check environment
    render_hostname = os.getenv('RENDER_EXTERNAL_HOSTNAME')
    print(f"Environment: {'🚀 Production (Render)' if render_hostname else '🏠 Local'}")
    if render_hostname:
        print(f"Render Hostname: {render_hostname}")
    
    # Check environment variables
    firebase_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
    database_url = os.getenv('FIREBASE_DATABASE_URL')
    
    print(f"\n📋 Environment Variables:")
    print(f"FIREBASE_CREDENTIALS_JSON: {'✅ Set (' + str(len(firebase_json)) + ' chars)' if firebase_json else '❌ Missing'}")
    print(f"FIREBASE_DATABASE_URL: {database_url or '❌ Missing'}")
    
    if firebase_json:
        try:
            creds = json.loads(firebase_json)
            print(f"\n📄 Credentials Validation:")
            print(f"Project ID: {creds.get('project_id', '❌ Missing')}")
            print(f"Client Email: {creds.get('client_email', '❌ Missing')}")
            print(f"Type: {creds.get('type', '❌ Missing')}")
            print(f"Private Key: {'✅ Present' if creds.get('private_key') else '❌ Missing'}")
        except Exception as e:
            print(f"\n❌ JSON Parse Error: {e}")
            return False
    
    # Test Firebase app initialization
    print(f"\n🔥 Testing Firebase App Initialization:")
    try:
        from myproject.firebase_app import get_firebase_app
        app = get_firebase_app()
        
        if hasattr(app, 'project_id') and app.project_id != "firebase-unavailable":
            print(f"✅ Firebase app initialized successfully")
            print(f"Project ID: {getattr(app, 'project_id', 'N/A')}")
        else:
            print(f"❌ Firebase unavailable or dummy app returned")
            return False
            
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test Realtime Database connection
    print(f"\n🗄️ Testing Realtime Database:")
    try:
        from firebase_admin import db as firebase_db
        ref = firebase_db.reference('/', app=app)
        test_ref = ref.child('production_test')
        
        test_data = {
            'test_timestamp': timezone.now().isoformat(),
            'test_environment': 'production' if render_hostname else 'local',
            'render_instance': os.getenv('RENDER_INSTANCE_ID', 'local')
        }
        
        test_ref.set(test_data)
        print(f"✅ Realtime Database write test successful")
        
        # Try to read it back
        read_data = test_ref.get()
        if read_data and read_data.get('test_timestamp') == test_data['test_timestamp']:
            print(f"✅ Realtime Database read test successful")
        else:
            print(f"⚠️ Realtime Database read test failed")
            
    except Exception as db_error:
        print(f"❌ Realtime Database test failed: {db_error}")
        import traceback
        traceback.print_exc()
    
    # Test Firestore connection
    print(f"\n🔥 Testing Firestore:")
    try:
        from firebase_admin import firestore
        db = firestore.client(app=app)
        
        test_collection = db.collection('production_test')
        test_doc = test_collection.document('test_document')
        
        test_data = {
            'test_timestamp': firestore.SERVER_TIMESTAMP,
            'test_environment': 'production' if render_hostname else 'local',
            'render_instance': os.getenv('RENDER_INSTANCE_ID', 'local')
        }
        
        test_doc.set(test_data)
        print(f"✅ Firestore write test successful")
        
        # Try to read it back
        doc_snapshot = test_doc.get()
        if doc_snapshot.exists:
            print(f"✅ Firestore read test successful")
        else:
            print(f"⚠️ Firestore read test failed")
            
    except Exception as firestore_error:
        print(f"❌ Firestore test failed: {firestore_error}")
        import traceback
        traceback.print_exc()
    
    # Test user save function
    print(f"\n👤 Testing User Save Function:")
    try:
        # Create a test user (if it doesn't exist)
        test_phone = "+639876543210"
        test_username = test_phone
        
        # Check if test user exists
        test_user = None
        try:
            test_user = User.objects.get(username=test_username)
            print(f"✅ Found existing test user: {test_username}")
        except User.DoesNotExist:
            print(f"⚠️ Test user not found, you can manually test with a real registration")
            return True
        
        if test_user:
            # Test the save function
            test_additional_data = {
                'test_save': True,
                'test_timestamp': timezone.now().isoformat(),
                'test_from': 'production_debug_script'
            }
            
            result = save_user_to_firebase_realtime_db(test_user, test_phone, test_additional_data)
            if result:
                print(f"✅ User save function test successful")
            else:
                print(f"❌ User save function test failed")
                
    except Exception as save_error:
        print(f"❌ User save test failed: {save_error}")
        import traceback
        traceback.print_exc()
    
    print(f"\n" + "=" * 60)
    print(f"🎯 TEST COMPLETE")
    print(f"If all tests passed, Firebase should be working for user registration!")
    print(f"=" * 60)
    
    return True

if __name__ == "__main__":
    test_firebase_production()
