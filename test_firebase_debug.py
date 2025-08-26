#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.conf import settings

def test_firebase_connection():
    print("🔍 Testing Firebase Connection...")
    print(f"IS_PRODUCTION: {getattr(settings, 'IS_PRODUCTION', 'Not set')}")
    print(f"FIREBASE_INITIALIZED: {getattr(settings, 'FIREBASE_INITIALIZED', 'Not set')}")
    
    # Test Firebase Admin import
    try:
        import firebase_admin
        print("✅ Firebase Admin imported successfully")
        
        # Check if app is initialized
        try:
            app = firebase_admin.get_app()
            print(f"✅ Firebase app found: {app.name}")
        except ValueError:
            print("❌ No Firebase app initialized")
            return
            
        # Test Realtime Database
        try:
            from firebase_admin import db as firebase_db
            ref = firebase_db.reference('/', app=app)
            print("✅ Realtime Database reference created")
            
            # Test write
            test_data = {'test': 'connection_test', 'timestamp': '2025-08-26'}
            ref.child('test_connection').set(test_data)
            print("✅ Successfully wrote to Realtime Database")
            
        except Exception as e:
            print(f"❌ Realtime Database error: {e}")
            
        # Test Firestore
        try:
            from firebase_admin import firestore
            db = firestore.client(app=app)
            print("✅ Firestore client created")
            
            # Test write
            doc_ref = db.collection('test').document('connection_test')
            doc_ref.set({'test': 'connection_test', 'timestamp': '2025-08-26'})
            print("✅ Successfully wrote to Firestore")
            
        except Exception as e:
            print(f"❌ Firestore error: {e}")
            
    except Exception as e:
        print(f"❌ Firebase import error: {e}")

if __name__ == "__main__":
    test_firebase_connection()
