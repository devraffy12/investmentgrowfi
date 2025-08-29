#!/usr/bin/env python3
"""
Simple test script to check Firebase app
"""
import sys
import os

def test_import():
    try:
        print("🔍 Testing import of firebase_only_app...")
        from firebase_only_app import app
        print("✅ Successfully imported app!")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_environment():
    print("🔍 Checking environment variables...")
    firebase_creds = os.environ.get('FIREBASE_CREDENTIALS_JSON')
    if firebase_creds:
        print("✅ FIREBASE_CREDENTIALS_JSON is set")
        try:
            import json
            json.loads(firebase_creds)
            print("✅ FIREBASE_CREDENTIALS_JSON is valid JSON")
        except:
            print("❌ FIREBASE_CREDENTIALS_JSON is not valid JSON")
    else:
        print("❌ FIREBASE_CREDENTIALS_JSON is not set")

def test_dependencies():
    print("🔍 Testing dependencies...")
    try:
        import fastapi
        print("✅ FastAPI available")
    except:
        print("❌ FastAPI not available")
    
    try:
        import uvicorn
        print("✅ Uvicorn available")
    except:
        print("❌ Uvicorn not available")
    
    try:
        import firebase_admin
        print("✅ Firebase Admin available")
    except:
        print("❌ Firebase Admin not available")

if __name__ == "__main__":
    print("🚀 Testing Firebase app for Render.com deployment...")
    test_dependencies()
    test_environment()
    if test_import():
        print("🎉 All tests passed! App should work.")
    else:
        print("💥 Tests failed! Fix errors before deployment.")
