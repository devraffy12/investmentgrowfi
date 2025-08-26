import requests
import json
import time

# Test Firebase functionality on production
PRODUCTION_URL = "https://investmentgrowfi.onrender.com"

def test_production_registration():
    """Test user registration on production to see if Firebase saves data"""
    print("🧪 Testing Firebase functionality on production...")
    
    # Test data
    test_user_data = {
        'phone_number': '+639999999999',
        'password': 'TestPassword123!',
        'confirm_password': 'TestPassword123!',
    }
    
    try:
        # First, get the page to get CSRF token
        print("📄 Getting registration page...")
        session = requests.Session()
        response = session.get(f"{PRODUCTION_URL}/register/")
        
        if response.status_code == 200:
            print("✅ Registration page loaded successfully")
            
            # Extract CSRF token
            csrf_token = None
            if 'csrfmiddlewaretoken' in response.text:
                # Simple extraction (in real scenario, you'd use BeautifulSoup)
                import re
                csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]*)"', response.text)
                if csrf_match:
                    csrf_token = csrf_match.group(1)
                    print(f"🔐 CSRF token extracted: {csrf_token[:20]}...")
            
            # Add CSRF token to data
            if csrf_token:
                test_user_data['csrfmiddlewaretoken'] = csrf_token
                
                # Attempt registration
                print("👤 Attempting test registration...")
                headers = {
                    'Referer': f"{PRODUCTION_URL}/register/",
                    'X-CSRFToken': csrf_token,
                }
                
                reg_response = session.post(
                    f"{PRODUCTION_URL}/register/",
                    data=test_user_data,
                    headers=headers
                )
                
                print(f"📊 Registration response status: {reg_response.status_code}")
                
                if reg_response.status_code == 302:
                    print("✅ Registration appears successful (redirect)")
                elif reg_response.status_code == 200:
                    if "error" in reg_response.text.lower() or "already exists" in reg_response.text.lower():
                        print("⚠️ User might already exist or validation error")
                    else:
                        print("✅ Registration form submitted successfully")
                else:
                    print(f"❌ Unexpected response: {reg_response.status_code}")
                    
            else:
                print("❌ Could not extract CSRF token")
        else:
            print(f"❌ Failed to load registration page: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing production registration: {e}")

def check_firebase_console():
    """Instructions for checking Firebase console"""
    print("\n🔥 Firebase Console Check Instructions:")
    print("=" * 50)
    print("1. Go to: https://console.firebase.google.com/project/investment-6d6f7")
    print("2. Check 'Realtime Database' section")
    print("3. Check 'Firestore Database' section")
    print("4. Look for 'users' collection in Firestore")
    print("5. Look for user data in Realtime Database")
    print("\n📱 Test by registering with a real phone number on:")
    print(f"   {PRODUCTION_URL}/register/")

if __name__ == "__main__":
    test_production_registration()
    time.sleep(2)
    check_firebase_console()
