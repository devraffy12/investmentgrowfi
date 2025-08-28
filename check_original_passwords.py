#!/usr/bin/env python3
"""
Check original passwords for all recent users
"""
import os
import sys
import django

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

print('🔍 Checking original passwords for all recent users...')
print('=' * 60)

# Get recent users from last 7 days
recent_users = User.objects.filter(
    date_joined__gte=timezone.now() - timedelta(days=7)
).order_by('-date_joined')

print(f'Found {recent_users.count()} recent users to check:')
print()

for user in recent_users:
    print(f'📱 {user.username} (ID: {user.id})')
    print(f'   Joined: {user.date_joined}')
    print(f'   Last Login: {user.last_login or "Never"}')
    
    # Test a broader range of possible passwords
    possible_passwords = [
        # Common registration passwords
        '123456', '12345', '1234', '123', 
        'password', 'admin', '000000', '111111',
        
        # Phone-based patterns
        user.username,  # Full phone
        user.username.replace('+63', ''),  # Without +63
        user.username[-4:],  # Last 4 digits
        user.username[-6:],  # Last 6 digits
        
        # Common Filipino passwords
        'pinoy', 'pinas', 'manila', 'pasig',
        
        # Date-based (registration dates)
        '2025', '08', '27', '26', '082725', '260825', '270825',
        
        # Number patterns
        '1111', '2222', '3333', '4444', '5555',
        '1122', '4321', '1212', '2121',
        
        # Birth years (common ages)
        '1990', '1995', '2000', '2005', '1985', '1980',
        
        # Simple passwords
        'simple', 'user', 'test', 'demo'
    ]
    
    # Remove +63 variations
    if user.username.startswith('+63'):
        without_country = user.username.replace('+63', '')
        possible_passwords.extend([
            without_country,  # Full without +63
            without_country[1:] if without_country.startswith('9') else without_country,  # Without leading 9
        ])
    
    password_found = False
    for pwd in possible_passwords:
        if user.check_password(pwd):
            print(f'   🎯 ORIGINAL PASSWORD: "{pwd}"')
            password_found = True
            break
            
    if not password_found:
        print(f'   ❓ Password: NOT FOUND in common patterns')
        print(f'   🔐 Hash: {user.password[:30]}...')
        
    print()

print()
print("🔧 Next step: Once we identify original passwords,")
print("   we'll restore them and ensure accounts persist!")
