#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User

try:
    django_users = User.objects.count()
    print(f"📊 Django Users in database: {django_users}")
    
    if django_users > 0:
        recent_users = User.objects.all()[:5]
        print(f"📋 Recent Django users:")
        for user in recent_users:
            print(f"   - {user.username} (ID: {user.id})")
    else:
        print("✨ No Django users found - pure Firebase setup possible!")
        
except Exception as e:
    print(f"❌ Error checking Django users: {e}")
