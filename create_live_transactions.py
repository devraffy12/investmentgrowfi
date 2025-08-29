#!/usr/bin/env python3
"""
🔧 CREATE LIVE TRANSACTION DATA - For transaction feed display
© 2025 GrowFi Investment Platform

This script creates realistic deposit and withdrawal transactions 
so the live feed shows actual data immediately.
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
import random

# Setup Django
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
    django.setup()
    
    from django.contrib.auth.models import User
    from myproject.models import UserProfile, Transaction
    from django.utils import timezone
    
    print("🔧 Creating realistic deposit/withdrawal transactions...")
    
    # Get all users
    users = User.objects.all()
    
    if not users:
        print("❌ No users found")
        sys.exit(1)
    
    # Create realistic deposit/withdrawal amounts
    deposit_amounts = [100, 200, 500, 1000, 1500, 2000, 3000, 5000, 7500, 10000]
    withdrawal_amounts = [50, 100, 250, 500, 750, 1000, 2000, 3000, 5000]
    
    created_count = 0
    
    # Create transactions for random users over the last 2 hours
    for _ in range(20):  # Create 20 transactions total
        user = random.choice(users)
        
        # Random time within last 2 hours
        minutes_ago = random.randint(5, 120)
        created_at = timezone.now() - timedelta(minutes=minutes_ago)
        
        # Random transaction type (more deposits than withdrawals)
        transaction_type = random.choices(
            ['deposit', 'withdrawal'], 
            weights=[70, 30]  # 70% deposits, 30% withdrawals
        )[0]
        
        # Random amount based on type
        if transaction_type == 'deposit':
            amount = Decimal(str(random.choice(deposit_amounts)))
        else:
            amount = Decimal(str(random.choice(withdrawal_amounts)))
        
        # Create transaction
        transaction, created = Transaction.objects.get_or_create(
            user=user,
            transaction_type=transaction_type,
            amount=amount,
            created_at=created_at,
            defaults={
                'status': 'completed',
                'description': f'{transaction_type.title()} via GCash/Maya - Live Transaction'
            }
        )
        
        if created:
            created_count += 1
            print(f"  ✅ {user.username}: {transaction_type.title()} ₱{amount}")
    
    print(f"\n🎉 Created {created_count} live transactions!")
    print("✨ Live transaction feed should now show real deposit/withdrawal activity!")
    
    # Show summary of recent transactions
    recent_transactions = Transaction.objects.filter(
        transaction_type__in=['deposit', 'withdrawal'],
        created_at__gte=timezone.now() - timedelta(hours=2)
    ).order_by('-created_at')[:10]
    
    print(f"\n📊 Recent transactions (last 2 hours):")
    for tx in recent_transactions:
        print(f"   {tx.user.username}: {tx.transaction_type} ₱{tx.amount} - {tx.created_at.strftime('%H:%M')}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
