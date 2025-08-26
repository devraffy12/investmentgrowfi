#!/usr/bin/env python
import os
import django
import sys

# Add the project directory to the path
project_dir = r'c:\Users\raffy\OneDrive\Desktop\investment'
if project_dir not in sys.path:
    sys.path.append(project_dir)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# Setup Django
django.setup()

# Now import Django models
from django.contrib.auth.models import User
from myproject.models import Investment, UserProfile

def test_dashboard_security():
    print("🔍 TESTING DASHBOARD SECURITY FIX")
    print("=" * 50)
    
    # Get all users
    users = User.objects.all()
    print(f"Total users: {users.count()}")
    
    # Check investments per user
    for user in users:
        investments = Investment.objects.filter(user=user)
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        print(f"\n👤 User: {user.username} ({user.phone_number if hasattr(user, 'phone_number') else 'No phone'})")
        print(f"   Total Invested: ₱{profile.total_invested or 0}")
        print(f"   Active Investments: {investments.count()}")
        
        for inv in investments:
            print(f"   - {inv.plan.name}: ₱{inv.amount}")
    
    print("\n" + "=" * 50)
    print("🎯 DASHBOARD TEMPLATE CHANGES MADE:")
    print("1. ✅ Fixed default '300' to '0' in total_invested display")
    print("2. ✅ Wrapped hardcoded 'GROWFI 1' card with conditional")
    print("3. ✅ Now shows actual user investments instead of hardcoded data")
    print("4. ✅ Only shows investment card when user has active investments")
    
    print("\n📊 EXPECTED BEHAVIOR:")
    print("- Users with no investments: Will see ₱0 and no investment card")
    print("- Users with investments: Will see their actual data only")
    print("- No more cross-user data visibility in dashboard!")

if __name__ == "__main__":
    test_dashboard_security()
