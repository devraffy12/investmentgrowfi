#!/usr/bin/env python3
"""
Generate Firebase credentials environment variable for Render.com deployment
"""
import json

# Read the Firebase service account file
with open('firebase-service-account.json', 'r') as f:
    firebase_creds = json.load(f)

# Convert to compact JSON string (no whitespace)
firebase_env_value = json.dumps(firebase_creds, separators=(',', ':'))

print("=" * 80)
print("FIREBASE CREDENTIALS FOR RENDER.COM DEPLOYMENT")
print("=" * 80)
print("\n1. Go to your Render.com dashboard")
print("2. Navigate to your web service settings")
print("3. Go to Environment Variables section")
print("4. Add a new environment variable:")
print("   - Key: FIREBASE_CREDENTIALS_JSON")
print("   - Value: (copy the text below)")
print("\n" + "=" * 80)
print("COPY THIS VALUE:")
print("=" * 80)
print(firebase_env_value)
print("=" * 80)
print("\nIMPORTANT NOTES:")
print("- Make sure to copy the ENTIRE string including all brackets and quotes")
print("- Do NOT add extra quotes around this value in Render.com")
print("- The value should start with { and end with }")
print("- After adding this environment variable, redeploy your service")
print("=" * 80)
