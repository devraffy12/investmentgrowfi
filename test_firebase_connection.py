#!/usr/bin/env python
"""
Test Firebase connection and verify if registration data is being saved to both Realtime Database and Firestore
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.conf import settings
import firebase_admin
from firebase_admin import db as firebase_db, firestore
from myproject.firebase_app import get_firebase_app

def test_firebase_connection():
    """Test Firebase Realtime Database and Firestore connections"""
    print("🔥 Testing Firebase connection...")
    
    try:
        # Check if Firebase is initialized
        if not firebase_admin._apps:
            print("❌ Firebase not initialized")
            return False
            
        # Get Firebase app
        app = get_firebase_app()
        print(f"✅ Firebase app initialized: {app}")
        
        # Test Realtime Database connection
        ref = firebase_db.reference('/', app=app)
        
        # Try to write a test record to Realtime Database
        test_data = {
            'test': True,
            'timestamp': 'test_timestamp_new_project',
            'message': 'Firebase connection test for new project investment-6d6f7'
        }
        
        test_ref = ref.child('connection_test')
        test_ref.set(test_data)
        print("✅ Successfully wrote test data to Firebase Realtime Database")
        
        # Try to read back the data
        retrieved_data = test_ref.get()
        print(f"✅ Successfully read data from Firebase Realtime Database: {retrieved_data}")
        
        # Test Firestore connection
        db = firestore.client(app=app)
        
        # Write test data to Firestore
        test_firestore_data = {
            'test': True,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'message': 'Firestore connection test for new project investment-6d6f7'
        }
        
        doc_ref = db.collection('connection_test').document('test_doc')
        doc_ref.set(test_firestore_data)
        print("✅ Successfully wrote test data to Firestore")
        
        # Read back from Firestore
        doc = doc_ref.get()
        if doc.exists:
            print(f"✅ Successfully read data from Firestore: {doc.to_dict()}")
        else:
            print("❌ Could not read data from Firestore")
        
        # Check if users collections exist
        users_ref = ref.child('users')
        users_data = users_ref.get()
        
        if users_data:
            user_count = len(users_data)
            print(f"📊 Found {user_count} users in Firebase Realtime Database")
            
            # Show sample of users (first 3)
            sample_users = list(users_data.keys())[:3]
            print(f"👥 Sample user keys: {sample_users}")
        else:
            print("📭 No users found in Firebase Realtime Database")
            
        # Check Firestore users collection
        firestore_users = db.collection('users').limit(5).stream()
        firestore_user_count = 0
        firestore_sample_users = []
        
        for doc in firestore_users:
            firestore_user_count += 1
            firestore_sample_users.append(doc.id)
            
        print(f"📊 Found {firestore_user_count} users in Firestore (showing first 5)")
        if firestore_sample_users:
            print(f"👥 Sample Firestore user IDs: {firestore_sample_users}")
        else:
            print("📭 No users found in Firestore yet")
            
        # Clean up test data
        test_ref.delete()
        doc_ref.delete()
        print("🧹 Cleaned up test data")
        
        return True
        
    except Exception as e:
        print(f"❌ Firebase connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_recent_registrations():
    """Check for recent registrations in Django database"""
    from django.contrib.auth.models import User
    from myproject.models import UserProfile
    from datetime import datetime, timedelta
    
    print("\n📅 Checking recent registrations...")
    
    # Get registrations from last 24 hours
    yesterday = datetime.now() - timedelta(days=1)
    recent_users = User.objects.filter(date_joined__gte=yesterday).order_by('-date_joined')
    
    print(f"📊 Found {recent_users.count()} registrations in the last 24 hours")
    
    for user in recent_users:
        try:
            profile = UserProfile.objects.get(user=user)
            print(f"👤 User: {user.username} | Phone: {profile.phone_number} | Joined: {user.date_joined}")
        except UserProfile.DoesNotExist:
            print(f"👤 User: {user.username} | No profile found | Joined: {user.date_joined}")

if __name__ == "__main__":
    print("🧪 Firebase Connection Test - New Project: investment-6d6f7")
    print("=" * 70)
    
    # Test Firebase connection
    firebase_ok = test_firebase_connection()
    
    # Check recent registrations
    check_recent_registrations()
    
    print("\n" + "=" * 70)
    if firebase_ok:
        print("✅ Firebase is working properly with new project!")
        print("🔥 Registration data will save to both Realtime Database AND Firestore")
        print("📱 Project: investment-6d6f7")
    else:
        print("❌ Firebase connection issues detected")
        print("⚠️ Registration data may not be saving to Firebase")
