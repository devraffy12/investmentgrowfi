#!/usr/bin/env python
"""
Test script to verify Django app works without Firebase delays
"""
import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_pages():
    """Test different pages for response time"""
    
    pages = [
        ('/', 'Home Page'),
        ('/login/', 'Login Page'),
        ('/register/', 'Register Page'),
        ('/plans/', 'Investment Plans'),
    ]
    
    print("🧪 Testing page response times...")
    print("=" * 50)
    
    session = requests.Session()
    
    for path, name in pages:
        try:
            start_time = time.time()
            response = session.get(f"{BASE_URL}{path}", timeout=10)
            end_time = time.time()
            
            duration = (end_time - start_time) * 1000  # Convert to milliseconds
            status = "✅" if response.status_code == 200 else "❌"
            
            print(f"{status} {name:20} | {response.status_code} | {duration:6.1f}ms")
            
            if duration > 5000:  # More than 5 seconds
                print(f"   ⚠️  SLOW RESPONSE: {duration:.1f}ms")
                
        except requests.exceptions.Timeout:
            print(f"❌ {name:20} | TIMEOUT | >10000ms")
        except Exception as e:
            print(f"❌ {name:20} | ERROR | {str(e)}")
    
    print("=" * 50)
    print("✅ Test completed!")

if __name__ == "__main__":
    print("🚀 Starting Django response time test...")
    print("Make sure the server is running: python manage.py runserver")
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    test_pages()
