#!/usr/bin/env python3
"""
Debug Firebase Environment Variables - Render Production
This script helps debug Firebase environment variable issues in production
"""
import os
import json

def debug_firebase_env():
    """Debug Firebase environment variables"""
    print("🔍 FIREBASE ENVIRONMENT DEBUG")
    print("=" * 60)
    
    # Check if running on Render
    render_hostname = os.getenv('RENDER_EXTERNAL_HOSTNAME')
    print(f"Environment: {'🚀 Production (Render)' if render_hostname else '🏠 Local'}")
    if render_hostname:
        print(f"Render Hostname: {render_hostname}")
    
    print(f"\n📋 Checking Environment Variables:")
    
    # Check for FIREBASE_CREDENTIALS_JSON
    firebase_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
    if firebase_json:
        print(f"✅ FIREBASE_CREDENTIALS_JSON: Found ({len(firebase_json)} chars)")
        print(f"   Preview: {firebase_json[:100]}...")
        
        # Try to parse it
        try:
            creds = json.loads(firebase_json)
            print(f"✅ JSON parsing: Success")
            print(f"   Type: {creds.get('type', 'MISSING')}")
            print(f"   Project ID: {creds.get('project_id', 'MISSING')}")
            print(f"   Client Email: {creds.get('client_email', 'MISSING')}")
            print(f"   Private Key: {'Present' if creds.get('private_key') else 'MISSING'}")
            
            # Check private key format
            private_key = creds.get('private_key', '')
            if private_key:
                if '\\n' in private_key:
                    print(f"   Private Key Format: Contains \\n (needs replacement)")
                    # Test the replacement
                    fixed_key = private_key.replace('\\n', '\n')
                    if fixed_key.startswith('-----BEGIN PRIVATE KEY-----'):
                        print(f"   Private Key After Fix: ✅ Valid format")
                    else:
                        print(f"   Private Key After Fix: ❌ Invalid format")
                elif '\n' in private_key:
                    print(f"   Private Key Format: Contains actual newlines")
                else:
                    print(f"   Private Key Format: ❌ No newlines detected")
                    
            # Validate required fields
            required_fields = ['type', 'project_id', 'private_key', 'client_email']
            missing_fields = [field for field in required_fields if not creds.get(field)]
            if missing_fields:
                print(f"❌ Missing fields: {missing_fields}")
            else:
                print(f"✅ All required fields present")
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"   This means the environment variable has invalid JSON")
            
    else:
        print(f"❌ FIREBASE_CREDENTIALS_JSON: Not found")
    
    # Check for old variable name
    old_firebase_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    if old_firebase_json:
        print(f"⚠️ GOOGLE_APPLICATION_CREDENTIALS_JSON: Found (old name)")
        print(f"   Length: {len(old_firebase_json)} chars")
    else:
        print(f"✅ GOOGLE_APPLICATION_CREDENTIALS_JSON: Not found (good)")
    
    # Check database URL
    database_url = os.getenv('FIREBASE_DATABASE_URL')
    if database_url:
        print(f"✅ FIREBASE_DATABASE_URL: {database_url}")
    else:
        print(f"⚠️ FIREBASE_DATABASE_URL: Not set")
    
    # Check individual variables (fallback method)
    print(f"\n📋 Individual Environment Variables (fallback):")
    individual_vars = [
        'FIREBASE_TYPE', 'FIREBASE_PROJECT_ID', 'FIREBASE_PRIVATE_KEY', 
        'FIREBASE_CLIENT_EMAIL', 'FIREBASE_PRIVATE_KEY_ID'
    ]
    
    for var in individual_vars:
        value = os.getenv(var)
        if value:
            if var == 'FIREBASE_PRIVATE_KEY':
                print(f"✅ {var}: Present ({len(value)} chars)")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
    
    print(f"\n" + "=" * 60)
    
    # Provide recommendations
    if firebase_json:
        print("🎯 RECOMMENDATION: JSON credentials found, should work")
        print("   If still failing, check the JSON format in Render dashboard")
    elif any(os.getenv(var) for var in individual_vars):
        print("🎯 RECOMMENDATION: Individual variables found, should work as fallback")
    else:
        print("🎯 RECOMMENDATION: No Firebase credentials found!")
        print("   Add FIREBASE_CREDENTIALS_JSON to Render environment variables")
    
    print("=" * 60)

if __name__ == "__main__":
    debug_firebase_env()
