import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from myproject.models import UserProfile
from django.contrib.auth import authenticate

print('🔧 RESTORING ACCOUNT: +639518383748')
print('=' * 40)

target_phone = '+639518383748'
new_password = 'recover123'

# Check if user exists in any format
user = None
formats = ['+639518383748', '639518383748', '09518383748', '9518383748']

for phone_format in formats:
    try:
        user = User.objects.get(username=phone_format)
        print(f'✅ Found user: {phone_format} (ID: {user.id})')
        break
    except User.DoesNotExist:
        continue

if not user:
    # Create new user
    print('🆕 Creating new user...')
    user = User.objects.create_user(
        username=target_phone,
        password=new_password
    )
    user.is_active = True
    user.save()
    print(f'✅ User created: ID {user.id}')
    
    # Create profile
    profile = UserProfile.objects.create(
        user=user,
        phone_number=target_phone,
        balance=0
    )
    print(f'✅ Profile created')
else:
    # Reset existing user
    print('🔧 Resetting existing user...')
    user.set_password(new_password)
    user.is_active = True
    user.save()
    print('✅ Password reset')
    
    # Get or create profile
    try:
        profile = UserProfile.objects.get(user=user)
        profile.phone_number = target_phone
        profile.save()
        print('✅ Profile updated')
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(
            user=user,
            phone_number=target_phone,
            balance=0
        )
        print('✅ Profile created')

# Test login
auth_user = authenticate(username=target_phone, password=new_password)
if auth_user:
    print('✅ Authentication test: SUCCESS')
else:
    print('❌ Authentication test: FAILED')

print(f'\n🎉 ACCOUNT RESTORED!')
print(f'📱 Phone: {target_phone}')
print(f'🔐 Password: {new_password}')
print(f'👤 User ID: {user.id}')
print(f'💰 Balance: ₱{profile.balance}')
print(f'✅ Status: ACTIVE - Ready to login!')
