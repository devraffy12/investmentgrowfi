#!/usr/bin/env python3
import os
import sys
import django
from datetime import datetime, timedelta

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from myproject.models import UserProfile

print('🔍 Checking Django users in local database...')
print('=' * 50)

# Check Django users
users = User.objects.all().order_by('-date_joined')
print(f'📊 Total Django users: {users.count()}')
print()

if users.exists():
    print('👥 Recent Django users:')
    for user in users[:10]:  # Show last 10 users
        try:
            profile = getattr(user, 'userprofile', None)
            phone = profile.phone_number if profile else 'No phone'
            name = user.get_full_name() or user.username
            joined = user.date_joined.strftime('%Y-%m-%d %H:%M')
            print(f'🆔 ID: {user.id} | 📱 Phone: {phone} | 👤 {name} | ⏰ {joined}')
        except Exception as e:
            print(f'❌ Error displaying user {user.id}: {e}')
else:
    print('❌ No Django users found!')

print()
print('🔄 Checking user status...')
print('=' * 30)

# Check active users
active_users = User.objects.filter(is_active=True)
print(f'✅ Active users: {active_users.count()}')

# Check users with profiles
profiles = UserProfile.objects.all()
print(f'📋 Users with profiles: {profiles.count()}')

# Check yesterday's registrations
yesterday = datetime.now() - timedelta(days=1)
recent_users = User.objects.filter(date_joined__gte=yesterday)
print(f'🆕 Users registered in last 24 hours: {recent_users.count()}')

if recent_users.exists():
    print('\nRecent registrations:')
    for user in recent_users:
        try:
            profile = getattr(user, 'userprofile', None)
            phone = profile.phone_number if profile else 'No phone'
            print(f'  - {user.username} ({phone}) at {user.date_joined}')
        except:
            print(f'  - {user.username} (error getting details)')
