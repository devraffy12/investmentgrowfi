#!/usr/bin/env python3
"""
Debug Firebase environment variables on Render.com
Run this to check if FIREBASE_CREDENTIALS_JSON is properly set
"""
import os
import json

def check_firebase_env():
    print("🔍 FIREBASE ENVIRONMENT CHECK")
    print("=" * 50)
    
    firebase_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
    print(f"FIREBASE_CREDENTIALS_JSON: {'✅ Found' if firebase_json else '❌ Missing'}")
    
    if firebase_json:
        print(f"Length: {len(firebase_json)} characters")
        try:
            parsed = json.loads(firebase_json)
            print(f"Valid JSON: ✅")
            print(f"Project ID: {parsed.get('project_id', 'Missing')}")
            print(f"Client Email: {parsed.get('client_email', 'Missing')}")
        except json.JSONDecodeError as e:
            print(f"JSON Error: ❌ {e}")
    
    # Check if production
    is_prod = bool(os.getenv('RENDER_EXTERNAL_HOSTNAME'))
    print(f"Production Environment: {'✅' if is_prod else '❌'}")
    
    if not firebase_json and is_prod:
        print("\n🚨 MISSING FIREBASE CREDENTIALS!")
        print("Run: python generate_firebase_env.py")
        print("Then add FIREBASE_CREDENTIALS_JSON to Render.com environment")

if __name__ == "__main__":
    check_firebase_env()
