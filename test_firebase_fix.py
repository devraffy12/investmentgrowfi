#!/usr/bin/env python
"""
Test Firebase connection and user registration
"""
import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from myproject.models import UserProfile
from myproject.firebase_app import get_firebase_app
from firebase_admin import db as firebase_db, firestore
import json
from datetime import datetime
from django.utils import timezone

def test_firebase_connection():
    """Test Firebase initialization and connection"""
    print("🔥 Testing Firebase connection...")
    
    try:
        # Test Firebase app initialization
        app = get_firebase_app()
        print(f"✅ Firebase app initialized: {app.name}")
        
        # Test Realtime Database connection
        ref = firebase_db.reference('/', app=app)
        test_data = {
            'test_connection': {
                'timestamp': timezone.now().isoformat(),
                'message': 'Connection test successful'
            }
        }
        ref.child('connection_test').set(test_data)
        print("✅ Realtime Database connection successful")
        
        # Test Firestore connection
        db = firestore.client(app=app)
        doc_ref = db.collection('connection_test').document('test')
        doc_ref.set({
            'timestamp': firestore.SERVER_TIMESTAMP,
            'message': 'Firestore connection test successful'
        })
        print("✅ Firestore connection successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Firebase connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_registration():
    """Test user registration with Firebase"""
    print("\n🧪 Testing user registration with Firebase...")
    
    # Create test user
    test_phone = "+639999999999"
    test_username = f"testuser_{int(datetime.now().timestamp())}"
    
    try:
        # Check if user exists and delete if necessary
        try:
            existing_user = User.objects.get(username=test_username)
            existing_user.delete()
            print(f"🗑️ Deleted existing test user: {test_username}")
        except User.DoesNotExist:
            pass
        
        # Create new user
        user = User.objects.create_user(
            username=test_username,
            email=f"{test_username}@test.com",
            password="testpassword123",
            first_name="Test",
            last_name="User"
        )
        print(f"✅ Created Django user: {test_username}")
        
        # Create user profile
        profile = UserProfile.objects.create(
            user=user,
            phone_number=test_phone,
            balance=1000.00,
            referral_code=f"REF{user.id:06d}"
        )
        print(f"✅ Created user profile with referral code: {profile.referral_code}")
        
        # Test Firebase save
        from myproject.views import save_user_to_firebase_realtime_db
        result = save_user_to_firebase_realtime_db(user, test_phone)
        
        if result:
            print("✅ User successfully saved to Firebase!")
        else:
            print("❌ Failed to save user to Firebase")
            
        return result
        
    except Exception as e:
        print(f"❌ User registration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=== FIREBASE CONNECTION AND REGISTRATION TEST ===")
    
    # Test 1: Firebase connection
    connection_success = test_firebase_connection()
    
    if connection_success:
        # Test 2: User registration
        registration_success = test_user_registration()
        
        if registration_success:
            print("\n🎉 ALL TESTS PASSED! Firebase is working correctly.")
        else:
            print("\n❌ Registration test failed. Check Firebase credentials.")
    else:
        print("\n❌ Firebase connection failed. Check credentials and project settings.")
        print("\nPossible solutions:")
        print("1. Download new Firebase service account credentials")
        print("2. Verify Firebase project ID and database URL")
        print("3. Check if Firebase Realtime Database is enabled")

if __name__ == "__main__":
    main()
