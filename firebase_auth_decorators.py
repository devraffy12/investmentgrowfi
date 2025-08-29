from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def firebase_login_required(view_func):
    """Pure Firebase authentication decorator - replaces Django's login_required"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if user has Firebase authentication session
        firebase_authenticated = request.session.get('firebase_authenticated', False)
        firebase_key = request.session.get('firebase_key')
        user_phone = request.session.get('user_phone')
        
        if not (firebase_authenticated and firebase_key and user_phone):
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')
        
        # Optional: Verify with Firebase that the session is still valid
        try:
            if FIREBASE_AVAILABLE:
                from .firebase_app import get_firebase_app
                from firebase_admin import db as firebase_db
                
                app = get_firebase_app()
                ref = firebase_db.reference('/', app=app)
                users_ref = ref.child('users')
                user_data = users_ref.child(firebase_key).get()
                
                if not user_data or user_data.get('status') != 'active':
                    # User no longer exists or is inactive
                    request.session.flush()
                    messages.error(request, 'Your session has expired. Please log in again.')
                    return redirect('login')
                
                # Update session with fresh user data
                request.session['firebase_user_data'] = user_data
                
        except Exception as e:
            print(f"⚠️ Firebase session validation failed: {e}")
            # Continue anyway - don't break the app if Firebase is temporarily unavailable
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

def get_firebase_user_data(request):
    """Helper function to get current Firebase user data from session"""
    return request.session.get('firebase_user_data', {})

def get_firebase_user_balance(request):
    """Helper function to get current user's balance from Firebase"""
    user_data = get_firebase_user_data(request)
    return float(user_data.get('balance', 0.0))

def get_firebase_user_phone(request):
    """Helper function to get current user's phone from session"""
    return request.session.get('user_phone', '')

def update_firebase_user_balance(request, new_balance):
    """Helper function to update user's balance in Firebase and session"""
    try:
        if FIREBASE_AVAILABLE:
            from .firebase_app import get_firebase_app
            from firebase_admin import db as firebase_db
            
            firebase_key = request.session.get('firebase_key')
            if firebase_key:
                app = get_firebase_app()
                ref = firebase_db.reference('/', app=app)
                users_ref = ref.child('users')
                
                # Update in Firebase
                users_ref.child(firebase_key).update({'balance': float(new_balance)})
                
                # Update in session
                user_data = request.session.get('firebase_user_data', {})
                user_data['balance'] = float(new_balance)
                request.session['firebase_user_data'] = user_data
                request.session.save()
                
                return True
    except Exception as e:
        print(f"❌ Error updating Firebase balance: {e}")
        return False
    
    return False
