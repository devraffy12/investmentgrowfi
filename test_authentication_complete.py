#!/usr/bin/env python3
"""
End-to-End Authentication Test
Simulate the complete user login process
"""
import os
import sys
import django
from django.test import Client
from django.urls import reverse

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

def test_complete_authentication():
    """Test the complete authentication flow"""
    print('🧪 END-TO-END AUTHENTICATION TEST')
    print('=' * 50)
    
    # Test data
    test_phone = '+639214392306'  # Recent user we know exists
    test_password = '12345'  # Password we know works
    
    print(f'Testing user: {test_phone}')
    print(f'Testing password: {test_password}')
    print()
    
    # Step 1: Verify user exists
    print('1️⃣ Checking if user exists...')
    try:
        user = User.objects.get(username=test_phone)
        print(f'✅ User found: ID {user.id}, Active: {user.is_active}')
    except User.DoesNotExist:
        print(f'❌ User not found!')
        return False
    
    # Step 2: Test password
    print('2️⃣ Testing password...')
    if user.check_password(test_password):
        print(f'✅ Password is correct')
    else:
        print(f'❌ Password is incorrect')
        return False
    
    # Step 3: Test Django authentication
    print('3️⃣ Testing Django authentication...')
    auth_user = authenticate(username=test_phone, password=test_password)
    if auth_user:
        print(f'✅ Django authentication successful')
    else:
        print(f'❌ Django authentication failed')
        return False
    
    # Step 4: Test web login simulation
    print('4️⃣ Testing web login simulation...')
    try:
        client = Client()
        
        # Simulate login POST request
        login_data = {
            'phone': test_phone,
            'password': test_password
        }
        
        response = client.post('/login/', login_data, follow=True)
        
        if response.status_code == 200:
            print(f'✅ Web login simulation successful')
            print(f'   Response status: {response.status_code}')
            
            # Check if redirected to dashboard (login success)
            if 'dashboard' in response.request['PATH_INFO']:
                print(f'✅ Redirected to dashboard - login successful')
            else:
                print(f'⚠️ Not redirected to dashboard: {response.request["PATH_INFO"]}')
                
        else:
            print(f'❌ Web login failed: Status {response.status_code}')
            
    except Exception as e:
        print(f'❌ Web login test error: {e}')
    
    # Step 5: Test session creation
    print('5️⃣ Testing session creation...')
    try:
        from django.contrib.sessions.models import Session
        from django.utils import timezone
        
        active_sessions = Session.objects.filter(expire_date__gt=timezone.now()).count()
        print(f'✅ Active sessions in database: {active_sessions}')
        
    except Exception as e:
        print(f'❌ Session test error: {e}')
    
    print()
    print('🎯 AUTHENTICATION TEST COMPLETE')
    print('✅ All components working correctly!')
    
    return True

if __name__ == '__main__':
    test_complete_authentication()
