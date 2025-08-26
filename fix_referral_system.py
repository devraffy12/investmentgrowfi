#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from myproject.models import UserProfile, User

def check_firebase_data():
    """Check if Firebase saving is working"""
    print("=" * 60)
    print("🔥 CHECKING FIREBASE INTEGRATION")
    print("=" * 60)
    
    try:
        # Test Firebase imports
        from firebase_admin import auth as firebase_auth, db as firebase_db
        from myproject.firebase_app import get_firebase_app
        
        print("✅ Firebase imports successful")
        
        # Test Firebase app
        app = get_firebase_app()
        print("✅ Firebase app initialized")
        
        # Test database reference
        ref = firebase_db.reference('/', app=app)
        print("✅ Firebase database reference created")
        
        # Test writing data
        test_ref = ref.child('test')
        test_ref.set({'message': 'Hello from Python', 'timestamp': '2025-08-13'})
        print("✅ Firebase write test successful")
        
        # Test reading data
        test_data = test_ref.get()
        print(f"✅ Firebase read test successful: {test_data}")
        
        # Clean up test data
        test_ref.delete()
        print("✅ Firebase cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Firebase error: {e}")
        import traceback
        traceback.print_exc()
        return False

def fix_referral_codes():
    """Fix any referral codes that might have issues"""
    print("\n" + "=" * 60)
    print("🔧 FIXING REFERRAL CODES")
    print("=" * 60)
    
    # Find profiles without referral codes
    profiles_without_codes = UserProfile.objects.filter(
        referral_code__isnull=True
    ) | UserProfile.objects.filter(
        referral_code__exact=''
    )
    
    if profiles_without_codes.exists():
        print(f"Found {profiles_without_codes.count()} profiles without referral codes")
        
        for profile in profiles_without_codes:
            # Generate a new referral code
            import random
            import string
            while True:
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                if not UserProfile.objects.filter(referral_code=code).exists():
                    profile.referral_code = code
                    profile.save()
                    print(f"   Generated code {code} for user {profile.user.username}")
                    break
    else:
        print("✅ All profiles have referral codes")
    
    # Check for duplicates
    from django.db.models import Count
    duplicates = UserProfile.objects.values('referral_code').annotate(
        count=Count('referral_code')
    ).filter(count__gt=1).exclude(referral_code__exact='')
    
    if duplicates.exists():
        print(f"⚠️ Found {duplicates.count()} duplicate referral codes")
        for dup in duplicates:
            print(f"   Duplicate code: {dup['referral_code']} ({dup['count']} times)")
    else:
        print("✅ No duplicate referral codes found")

if __name__ == "__main__":
    firebase_ok = check_firebase_data()
    
    if firebase_ok:
        print("\n🎉 Firebase is working correctly!")
    else:
        print("\n⚠️ Firebase has issues, but referral codes should still work")
    
    fix_referral_codes()
    
    print("\n" + "=" * 60)
    print("🚀 READY TO TEST REFERRAL REGISTRATION!")
    print("=" * 60)
    print("Available test referral codes:")
    
    test_codes = UserProfile.objects.exclude(
        referral_code__isnull=True
    ).exclude(
        referral_code__exact=''
    ).values_list('referral_code', 'user__username')[:5]
    
    for code, username in test_codes:
        print(f"   Code: {code} -> User: {username}")
    
    print("\nNow try registering with one of these codes!")
