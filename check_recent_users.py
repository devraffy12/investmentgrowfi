#!/usr/bin/env python3
import os
import sys
import django
import json
from datetime import datetime, timedelta
import pytz

sys.path.append('.')
sys.path.append('./myproject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from myproject.firebase_app import initialize_firebase_app

print('🔥 Checking all recent Firebase users...')
print('=' * 50)

try:
    db = initialize_firebase_app()
    users_ref = db.reference('users')
    all_users = users_ref.get()
    
    if all_users:
        print(f'📊 Total users in Firebase: {len(all_users)}')
        print()
        
        # Get users from yesterday (August 27)
        yesterday = datetime.now(pytz.UTC) - timedelta(days=1)
        recent_users = []
        
        for phone, user_data in all_users.items():
            if isinstance(user_data, dict) and 'created_at' in user_data:
                try:
                    created_at = datetime.fromisoformat(user_data['created_at'].replace('Z', '+00:00'))
                    if created_at >= yesterday:
                        recent_users.append({
                            'phone': phone,
                            'created_at': created_at,
                            'user_data': user_data
                        })
                except:
                    pass
        
        if recent_users:
            print(f'🆕 Recent users (last 24 hours): {len(recent_users)}')
            print()
            for user in sorted(recent_users, key=lambda x: x['created_at'], reverse=True):
                data = user['user_data']
                print(f'📱 Phone: {user["phone"]}')
                print(f'⏰ Created: {user["created_at"].strftime("%Y-%m-%d %H:%M:%S")}')
                print(f'👤 Name: {data.get("first_name", "")} {data.get("last_name", "")}')
                print(f'📧 Email: {data.get("email", "Not provided")}')
                print(f'🔑 Referral Code: {data.get("referral_code", "Not set")}')
                print(f'✅ Active: {data.get("is_active", False)}')
                print('-' * 40)
        else:
            print('❌ No recent users found in the last 24 hours')
            
        # Show all users for debugging
        print('\n📋 All Firebase users:')
        print('=' * 30)
        for phone, user_data in all_users.items():
            if isinstance(user_data, dict):
                created = user_data.get('created_at', 'Unknown')
                if created != 'Unknown':
                    try:
                        created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                        created = created_dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        pass
                print(f'📱 {phone} - Created: {created} - Active: {data.get("is_active", False)}')
    else:
        print('❌ No users found in Firebase!')
        
except Exception as e:
    print(f'❌ Error checking Firebase: {e}')
    import traceback
    traceback.print_exc()
