"""
Debug script to check if Firebase is working in production after the private key fix
"""
import os
import json
import requests
from urllib.parse import urljoin

def check_production_firebase_status():
    """Check if Firebase warnings are gone from production logs"""
    print("🔍 Checking Firebase Status After Private Key Fix")
    print("=" * 50)
    
    # Test registration endpoint
    base_url = "https://investmentgrowfi.onrender.com"
    
    try:
        # 1. Check if site is responding
        print("1. 🌐 Testing site accessibility...")
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("   ✅ Site is accessible")
        else:
            print(f"   ❌ Site response: {response.status_code}")
            return
        
        # 2. Check registration page
        print("2. 📝 Testing registration page...")
        reg_response = requests.get(urljoin(base_url, "/register/"), timeout=10)
        if reg_response.status_code == 200:
            print("   ✅ Registration page loads")
        else:
            print(f"   ❌ Registration page error: {reg_response.status_code}")
            return
        
        # 3. Check login page
        print("3. 🔐 Testing login page...")
        login_response = requests.get(urljoin(base_url, "/login/"), timeout=10)
        if login_response.status_code == 200:
            print("   ✅ Login page loads")
        else:
            print(f"   ❌ Login page error: {login_response.status_code}")
        
        print("\n✅ Basic site functionality confirmed")
        
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        return
    
    print("\n📋 Next Steps to Verify Firebase:")
    print("-" * 30)
    print("1. Try registering a new user at:")
    print(f"   {base_url}/register/")
    print("2. Check your Firebase Console:")
    print("   https://console.firebase.google.com/project/investment-6d6f7")
    print("3. Look for new user data in:")
    print("   - Firestore Database > users collection")
    print("   - Realtime Database > users node")
    
    print("\n🔥 If Firebase is now working, you should see:")
    print("   ✅ No more PEM file warnings in logs")
    print("   ✅ User registration data in Firebase")
    print("   ✅ Both Firestore and Realtime Database populated")

def show_firebase_config_summary():
    """Show current Firebase configuration"""
    print("\n🔧 Current Firebase Configuration Summary:")
    print("=" * 50)
    print("📊 Project: investment-6d6f7")
    print("🔥 Private Key: Fixed formatting (removed double backslashes)")
    print("💾 Databases: Dual (Firestore + Realtime Database)")
    print("🌍 Environment: Production auto-detection")
    print("🔐 Credentials: Embedded in settings.py for production")

if __name__ == "__main__":
    check_production_firebase_status()
    show_firebase_config_summary()
