#!/usr/bin/env python3
"""
Emergency Firebase Fix - Check all environment variables
This will help us see exactly what's set in Render
"""
import os
import json

def emergency_firebase_check():
    print("🚨 EMERGENCY FIREBASE DEBUG")
    print("=" * 70)
    
    # Check EVERYTHING
    print("🔍 ALL Firebase Environment Variables:")
    
    firebase_vars = [
        'FIREBASE_CREDENTIALS_JSON',
        'GOOGLE_APPLICATION_CREDENTIALS_JSON', 
        'FIREBASE_TYPE',
        'FIREBASE_PROJECT_ID',
        'FIREBASE_PRIVATE_KEY',
        'FIREBASE_CLIENT_EMAIL',
        'FIREBASE_PRIVATE_KEY_ID',
        'FIREBASE_CLIENT_ID',
        'FIREBASE_AUTH_URI',
        'FIREBASE_TOKEN_URI',
        'FIREBASE_AUTH_PROVIDER_X509_CERT_URL',
        'FIREBASE_CLIENT_X509_CERT_URL',
        'FIREBASE_UNIVERSE_DOMAIN',
        'FIREBASE_DATABASE_URL',
        'GOOGLE_APPLICATION_CREDENTIALS'
    ]
    
    for var in firebase_vars:
        value = os.getenv(var)
        if value:
            if var in ['FIREBASE_CREDENTIALS_JSON', 'GOOGLE_APPLICATION_CREDENTIALS_JSON']:
                print(f"✅ {var}: SET ({len(value)} chars)")
                print(f"   Preview: {value[:100]}...")
                # Try to parse JSON
                try:
                    parsed = json.loads(value)
                    print(f"   ✅ Valid JSON with {len(parsed)} fields")
                    print(f"   Type: {parsed.get('type', 'MISSING')}")
                    print(f"   Project: {parsed.get('project_id', 'MISSING')}")
                except:
                    print(f"   ❌ Invalid JSON")
            elif var == 'FIREBASE_PRIVATE_KEY':
                print(f"✅ {var}: SET ({len(value)} chars)")
                if '\\n' in value:
                    print(f"   Format: Contains \\n (good for individual vars)")
                elif '\n' in value:
                    print(f"   Format: Contains real newlines")
                else:
                    print(f"   Format: No newlines detected")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET")
    
    print("\n" + "=" * 70)
    print("🎯 DIAGNOSIS:")
    
    # Check what method should work
    json_creds = os.getenv('FIREBASE_CREDENTIALS_JSON') or os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    individual_vars = all([
        os.getenv('FIREBASE_TYPE'),
        os.getenv('FIREBASE_PROJECT_ID'), 
        os.getenv('FIREBASE_PRIVATE_KEY'),
        os.getenv('FIREBASE_CLIENT_EMAIL')
    ])
    
    if json_creds and individual_vars:
        print("⚠️ CONFLICT: Both JSON and individual variables are set!")
        print("   This might cause conflicts. Remove individual variables.")
    elif json_creds:
        print("✅ JSON method should work")
    elif individual_vars:
        print("✅ Individual variables method should work")
    else:
        print("❌ No valid credentials found")
    
    print("=" * 70)

if __name__ == "__main__":
    emergency_firebase_check()
