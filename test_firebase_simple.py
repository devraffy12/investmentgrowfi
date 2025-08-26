#!/usr/bin/env python3
"""
Simple Firebase Test for Production
Run this to test Firebase on Render.com: python test_firebase_simple.py
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from myproject.firebase_app import get_firebase_app
from firebase_admin import db as firebase_db, firestore
import json

def main():
    print("🔥 Firebase Production Test")
    print("=" * 40)
    
    # Check if we're on Render.com
    render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    print(f"Render.com detected: {'✓' if render_hostname else '✗'}")
    
    # Check Firebase credentials
    firebase_creds = os.environ.get('FIREBASE_CREDENTIALS_JSON')
    print(f"Firebase credentials: {'✓' if firebase_creds else '✗'}")
    
    if firebase_creds:
        try:
            creds_data = json.loads(firebase_creds)
            print(f"Project ID: {creds_data.get('project_id')}")
        except:
            print("❌ Invalid Firebase credentials JSON")
            return
    
    # Test Firebase initialization
    try:
        print("\n🔥 Initializing Firebase...")
        app = get_firebase_app()
        print(f"✅ Success! Project: {app.project_id}")
        
        # Test database write
        print("\n📊 Testing database...")
        ref = firebase_db.reference('test', app=app)
        ref.set({'status': 'working', 'timestamp': '2025-08-26'})
        print("✅ Database write successful!")
        
        # Test database read
        data = ref.get()
        if data and data.get('status') == 'working':
            print("✅ Database read successful!")
        
        # Clean up
        ref.delete()
        print("✅ Test cleanup complete!")
        
        print("\n🎉 ALL TESTS PASSED! Firebase is working!")
        
    except Exception as e:
        print(f"\n❌ Firebase test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
