#!/usr/bin/env python3
"""
Generate Firebase credentials for Render.com - FIXED VERSION
This version ensures proper JSON formatting and escaping
"""
import json

# Read the Firebase service account file
with open('firebase-service-account.json', 'r') as f:
    firebase_creds = json.load(f)

# Ensure private key has proper newline formatting
if 'private_key' in firebase_creds:
    # Replace actual newlines with \\n for environment variable storage
    firebase_creds['private_key'] = firebase_creds['private_key'].replace('\n', '\\n')

# Convert to compact JSON string (no whitespace)
firebase_env_value = json.dumps(firebase_creds, separators=(',', ':'))

print("=" * 80)
print("FIREBASE CREDENTIALS FOR RENDER.COM - FIXED VERSION")
print("=" * 80)
print("\n🔧 IMPORTANT: Remove the OLD environment variable first!")
print("1. Go to Render.com dashboard")
print("2. Your service → Environment Variables")
print("3. DELETE the existing FIREBASE_CREDENTIALS_JSON variable")
print("4. Add NEW environment variable:")
print("   - Key: FIREBASE_CREDENTIALS_JSON")
print("   - Value: (copy the text below)")

print("\n" + "=" * 80)
print("COPY THIS ENTIRE VALUE (including quotes):")
print("=" * 80)
print(firebase_env_value)
print("=" * 80)

print("\n🔍 VERIFICATION:")
print(f"✅ Length: {len(firebase_env_value)} characters")
print(f"✅ Starts with: {firebase_env_value[:50]}...")
print(f"✅ Ends with: ...{firebase_env_value[-50:]}")

print("\n📋 ENVIRONMENT VARIABLE SUMMARY:")
print("Key: FIREBASE_CREDENTIALS_JSON")
print("Value starts with: {\"type\":\"service_account\"...")
print("Value ends with: ...\"googleapis.com\"}")

print("\n⚠️ CRITICAL STEPS:")
print("1. DELETE old FIREBASE_CREDENTIALS_JSON from Render")
print("2. ADD new FIREBASE_CREDENTIALS_JSON with value above")
print("3. REDEPLOY your service manually")
print("4. Check logs for: '🔥 Firebase initialized with JSON environment credentials'")
print("=" * 80)
