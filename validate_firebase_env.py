#!/usr/bin/env python
"""
Validate Firebase Environment Setup for Render.com Production
This script helps verify that your Firebase environment variables are properly configured.
"""
import os
import sys
import json


def validate_firebase_env():
    """Validate Firebase environment variables"""
    print("🔍 Validating Firebase Environment Configuration...")
    print("=" * 60)
    
    issues = []
    warnings = []
    
    # Check Method 1: JSON Credentials
    json_creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    if json_creds:
        print("✅ Found GOOGLE_APPLICATION_CREDENTIALS_JSON")
        try:
            cred_dict = json.loads(json_creds)
            required_fields = [
                'type', 'project_id', 'private_key', 'client_email'
            ]
            missing_fields = [field for field in required_fields if field not in cred_dict]
            if missing_fields:
                issues.append(f"Missing required fields in JSON credentials: {missing_fields}")
            else:
                print("✅ JSON credentials contain all required fields")
                
            # Check private key format
            private_key = cred_dict.get('private_key', '')
            if '\\n' in private_key and '\n' not in private_key:
                print("⚠️ Private key needs newline conversion (this is handled automatically)")
            elif '-----BEGIN PRIVATE KEY-----' not in private_key:
                issues.append("Private key format appears invalid")
            else:
                print("✅ Private key format looks correct")
                
        except json.JSONDecodeError as e:
            issues.append(f"Invalid JSON in GOOGLE_APPLICATION_CREDENTIALS_JSON: {e}")
    else:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS_JSON not found")
        
        # Check Method 2: Individual Environment Variables
        print("\n🔍 Checking individual Firebase environment variables...")
        
        required_env_vars = {
            'FIREBASE_TYPE': 'service_account',
            'FIREBASE_PROJECT_ID': 'investment-6d6f7', 
            'FIREBASE_PRIVATE_KEY': '-----BEGIN PRIVATE KEY-----',
            'FIREBASE_CLIENT_EMAIL': 'firebase-adminsdk-fbsvc@investment-6d6f7.iam.gserviceaccount.com'
        }
        
        optional_env_vars = {
            'FIREBASE_PRIVATE_KEY_ID': 'Private key ID',
            'FIREBASE_CLIENT_ID': 'Client ID',
            'FIREBASE_DATABASE_URL': 'https://investment-6d6f7-default-rtdb.firebaseio.com'
        }
        
        all_vars_present = True
        for var, expected in required_env_vars.items():
            value = os.getenv(var)
            if value:
                if expected in value:
                    print(f"✅ {var}: Present and valid")
                else:
                    issues.append(f"{var}: Present but may be incorrect (expected to contain '{expected}')")
            else:
                print(f"❌ {var}: Missing")
                all_vars_present = False
                
        for var, description in optional_env_vars.items():
            value = os.getenv(var)
            if value:
                print(f"✅ {var}: Present")
            else:
                warnings.append(f"{var}: Missing ({description})")
                
        if not all_vars_present and not json_creds:
            issues.append("Neither JSON credentials nor individual environment variables are complete")
    
    # Check other important environment variables
    print("\n🔍 Checking other environment variables...")
    
    other_vars = {
        'ENVIRONMENT': 'production',
        'DEBUG': 'False',
        'SECRET_KEY': 'Should be set',
        'RENDER_EXTERNAL_HOSTNAME': 'investmentgrowfi.onrender.com'
    }
    
    for var, description in other_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            warnings.append(f"{var}: Not set ({description})")
    
    # Final assessment
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    if not issues:
        print("🎉 All critical Firebase configurations look good!")
        if warnings:
            print(f"⚠️ {len(warnings)} warnings (non-critical):")
            for warning in warnings:
                print(f"   • {warning}")
    else:
        print(f"❌ {len(issues)} critical issues found:")
        for issue in issues:
            print(f"   • {issue}")
        
        if warnings:
            print(f"\n⚠️ {len(warnings)} additional warnings:")
            for warning in warnings:
                print(f"   • {warning}")
    
    print("\n📝 NEXT STEPS:")
    if issues:
        print("1. Fix the critical issues listed above")
        print("2. Add missing environment variables to Render.com")
        print("3. Redeploy your service")
        print("4. Test user registration")
    else:
        print("1. Your Firebase configuration looks good!")
        print("2. If registration still doesn't work, check:")
        print("   - Firebase Console Database Rules")
        print("   - Render.com deployment logs")
        print("   - Network connectivity to Firebase")
        
    return len(issues) == 0


def generate_env_vars():
    """Generate properly formatted environment variables for copy-paste"""
    print("\n" + "=" * 60)
    print("📋 COPY-PASTE ENVIRONMENT VARIABLES FOR RENDER.COM")
    print("=" * 60)
    
    print("\n# Add these to your Render.com Environment settings:")
    print("# (Go to your service → Environment tab → Add each variable)")
    print()
    
    env_vars = {
        'FIREBASE_TYPE': 'service_account',
        'FIREBASE_PROJECT_ID': 'investment-6d6f7',
        'FIREBASE_PRIVATE_KEY_ID': 'ecd0afac04d2aedc359bbffe13e9f8a0585fe74b',
        'FIREBASE_CLIENT_EMAIL': 'firebase-adminsdk-fbsvc@investment-6d6f7.iam.gserviceaccount.com',
        'FIREBASE_CLIENT_ID': '113203784259300491698',
        'FIREBASE_AUTH_URI': 'https://accounts.google.com/o/oauth2/auth',
        'FIREBASE_TOKEN_URI': 'https://oauth2.googleapis.com/token',
        'FIREBASE_AUTH_PROVIDER_X509_CERT_URL': 'https://www.googleapis.com/oauth2/v1/certs',
        'FIREBASE_CLIENT_X509_CERT_URL': 'https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40investment-6d6f7.iam.gserviceaccount.com',
        'FIREBASE_UNIVERSE_DOMAIN': 'googleapis.com',
        'FIREBASE_DATABASE_URL': 'https://investment-6d6f7-default-rtdb.firebaseio.com',
        'ENVIRONMENT': 'production',
        'DEBUG': 'False'
    }
    
    for var, value in env_vars.items():
        print(f"{var}={value}")
    
    # Private key needs special handling
    print("\n# IMPORTANT: Add this private key (get from your local firebase-service-account.json file):")
    print('FIREBASE_PRIVATE_KEY=[COPY THE PRIVATE KEY FROM YOUR LOCAL firebase-service-account.json FILE]')
    print('# Make sure to include \\n for line breaks, like:')
    print('# FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\\nYOUR_ACTUAL_KEY_CONTENT\\n-----END PRIVATE KEY-----')
    
    print("\n⚠️ IMPORTANT NOTES:")
    print("• Make sure to copy the FIREBASE_PRIVATE_KEY exactly as shown above")
    print("• The \\n characters represent line breaks and must be included")
    print("• Don't add extra spaces or line breaks")
    print("• After adding all variables, click 'Save Changes' in Render.com")
    print("• Wait for automatic redeploy to complete")


if __name__ == "__main__":
    print("🔥 Firebase Environment Validator for Render.com")
    print("=" * 60)
    
    # First validate current environment
    is_valid = validate_firebase_env()
    
    # Always show the environment variables for easy copy-paste
    generate_env_vars()
    
    print("\n" + "=" * 60)
    if is_valid:
        print("✅ Validation completed - Configuration looks good!")
    else:
        print("❌ Validation failed - Please fix the issues above")
    print("=" * 60)
