from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q
from myproject.models import Investment, Transaction, UserProfile, DailyPayout
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import os
import json

# Firebase imports
try:
    import firebase_admin
    from firebase_admin import credentials, firestore, db
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check against hardcoded credentials
        if username == 'RodolfHitler' and password == 'cloudpay':
            # Set session to mark user as logged in
            request.session['admin_logged_in'] = True
            request.session['admin_username'] = username
            return redirect('admindashboard:dashboard')
        else:
            context = {'error': 'Invalid username or password'}
            return render(request, 'admindashboard/admindlogin.html', context)
    
    # If already logged in, redirect to dashboard
    if request.session.get('admin_logged_in'):
        return redirect('admindashboard:dashboard')
    
    return render(request, 'admindashboard/admindlogin.html')

def admin_logout(request):
    request.session.flush()
    return redirect('admindashboard:admindlogin')

def check_admin_login(request):
    """Helper function to check if admin is logged in"""
    return request.session.get('admin_logged_in', False)

def get_firebase_users():
    """Fetch users from Firebase Firestore and Realtime Database"""
    firebase_users = []
    
    if not FIREBASE_AVAILABLE:
        return []
    
    try:
        # Check if Firebase is initialized
        if not firebase_admin._apps:
            return []
        
        # Get users from Firestore
        firestore_db = firestore.client()
        users_ref = firestore_db.collection('users')
        docs = users_ref.stream()
        
        for doc in docs:
            user_data = doc.to_dict()
            user_data['id'] = doc.id
            user_data['source'] = 'firestore'
            firebase_users.append(user_data)
        
        # Also try to get from Realtime Database
        try:
            realtime_db = db.reference('users')
            realtime_users = realtime_db.get()
            
            if realtime_users:
                for user_id, user_data in realtime_users.items():
                    # Check if user already exists from Firestore
                    existing_user = next((u for u in firebase_users if u.get('phone_number') == user_data.get('phone_number')), None)
                    if not existing_user:
                        user_data['id'] = user_id
                        user_data['source'] = 'realtime'
                        firebase_users.append(user_data)
        except Exception as e:
            print(f"Could not fetch from Realtime Database: {e}")
        
    except Exception as e:
        print(f"Error fetching Firebase users: {e}")
    
    return firebase_users

# Add login requirement
def admin_dashboard(request):
    # Check if admin is logged in
    if not check_admin_login(request):
        return redirect('admindashboard:admindlogin')
        
    # Get real data from your database
    
    # Total deposits (completed)
    total_deposits = Transaction.objects.filter(
        transaction_type='deposit', 
        status__in=['completed', 'approved']
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Total withdrawals (completed)
    total_withdrawals = Transaction.objects.filter(
        transaction_type='withdrawal', 
        status__in=['completed', 'approved']
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # All transactions count    
    total_transactions = Transaction.objects.count()
    
    # Total users (local + Firebase)
    local_users = User.objects.count()
    firebase_users = get_firebase_users()
    total_users = local_users + len(firebase_users)
    
    # Recent transactions (last 10)
    recent_transactions = Transaction.objects.select_related('user').order_by('-created_at')[:10]
    
    # Monthly data for charts
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    
    # Recent deposits (last 30 days)
    recent_deposits = Transaction.objects.filter(
        transaction_type='deposit',
        status__in=['completed', 'approved'],
        created_at__gte=thirty_days_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Recent withdrawals (last 30 days)
    recent_withdrawals = Transaction.objects.filter(
        transaction_type='withdrawal',
        status__in=['completed', 'approved'],
        created_at__gte=thirty_days_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # New users this month
    new_users_this_month = User.objects.filter(date_joined__gte=thirty_days_ago).count()
    
    # Investment stats
    total_investments = Investment.objects.count()  
    active_investments = Investment.objects.filter(status='active').count()
    
    # Total amount invested
    total_invested = Investment.objects.aggregate(total=Sum('amount'))['total'] or 0
    
    # Daily payouts total
    total_payouts = DailyPayout.objects.aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'total_transactions': total_transactions,
        'total_users': total_users,
        'local_users': local_users,
        'firebase_users_count': len(firebase_users),
        'recent_transactions': recent_transactions,
        'recent_deposits': recent_deposits,
        'recent_withdrawals': recent_withdrawals,
        'new_users_this_month': new_users_this_month,
        'total_investments': total_investments,
        'active_investments': active_investments,
        'total_invested': total_invested,
        'total_payouts': total_payouts,
    }
    
    return render(request, 'admindashboard/admindashboard.html', context)

def admin_users(request):
    # Check if admin is logged in
    if not check_admin_login(request):
        return redirect('admindashboard:admindlogin')
    
    # Get local users
    local_users = User.objects.all().order_by('-date_joined')
    
    # Get Firebase users
    firebase_users = get_firebase_users()
    
    # Sort Firebase users by registration date if available
    firebase_users.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    context = {
        'local_users': local_users,
        'firebase_users': firebase_users,
        'total_local': local_users.count(),
        'total_firebase': len(firebase_users),
    }
    return render(request, 'admindashboard/users.html', context)

def admin_deposits(request):
    # Check if admin is logged in
    if not check_admin_login(request):
        return redirect('admindashboard:admindlogin')
        
    deposits = Transaction.objects.filter(
        transaction_type='deposit'
    ).select_related('user').order_by('-created_at')
    context = {
        'deposits': deposits,
    }
    return render(request, 'admindashboard/deposits.html', context)

def admin_withdrawals(request):
    # Check if admin is logged in
    if not check_admin_login(request):
        return redirect('admindashboard:admindlogin')
        
    withdrawals = Transaction.objects.filter(
        transaction_type='withdrawal'
    ).select_related('user').order_by('-created_at')
    context = {
        'withdrawals': withdrawals,
    }
    return render(request, 'admindashboard/withdrawals.html', context)

def admin_transactions(request):
    # Check if admin is logged in
    if not check_admin_login(request):
        return redirect('admindashboard:admindlogin')
        
    transactions = Transaction.objects.select_related('user').order_by('-created_at')
    context = {
        'transactions': transactions,
    }
    return render(request, 'admindashboard/transactions.html', context)
