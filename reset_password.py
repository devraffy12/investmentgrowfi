#!/usr/bin/env python3
"""
Quick Password Reset Tool for Firebase Users
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from migrate_firebase_passwords import reset_user_password_in_firebase

def main():
    print("🔧 Firebase Password Reset Tool")
    print("=" * 40)
    
    # Common users from the migration that might need password reset
    print("Recent users who may need password reset:")
    print("1. +639519092103 (temp_1_2103)")
    print("2. +639590192301 (temp_2_2301)")
    print("3. +639919101001 (temp_80_1001)")
    print("4. +639191191919 (temp_82_1919)")
    print("5. Custom phone number")
    
    choice = input("\nChoose option (1-5): ").strip()
    
    phone_map = {
        '1': '+639519092103',
        '2': '+639590192301', 
        '3': '+639919101001',
        '4': '+639191191919'
    }
    
    if choice in phone_map:
        phone = phone_map[choice]
        print(f"Selected: {phone}")
    elif choice == '5':
        phone = input("Enter phone number (+639xxxxxxxxx): ").strip()
    else:
        print("❌ Invalid choice")
        return
    
    if not phone:
        print("❌ Phone number required")
        return
    
    # Suggest a simple password
    suggested_password = "123456"
    
    password = input(f"Enter new password (default: {suggested_password}): ").strip()
    if not password:
        password = suggested_password
    
    print(f"\n🔄 Resetting password for {phone}...")
    print(f"New password: {password}")
    
    confirm = input("Confirm reset? (y/n): ").strip().lower()
    
    if confirm == 'y':
        success = reset_user_password_in_firebase(phone, password)
        if success:
            print(f"\n✅ Password reset successful!")
            print(f"📱 Phone: {phone}")
            print(f"🔑 New Password: {password}")
            print("\n📝 User can now login with these credentials.")
        else:
            print("❌ Password reset failed")
    else:
        print("❌ Reset cancelled")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Reset cancelled by user")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()
