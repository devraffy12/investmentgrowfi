#!/usr/bin/env python3
"""
🔧 TRANSACTION DISPLAY FIX - Create sample transactions for testing
© 2025 GrowFi Investment Platform

This script creates sample transactions so the live feed shows data immediately.
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta

# Setup Django
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
    django.setup()
    
    from django.contrib.auth.models import User
    from myproject.models import UserProfile, Transaction
    from django.utils import timezone
    import random
    
    print("🔧 Creating sample transactions for live feed...")
    
    # Get all users
    users = User.objects.all()[:10]  # Limit to first 10 users
    
    if not users:
        print("❌ No users found")
        sys.exit(1)
    
    # Sample transaction types and amounts
    transaction_types = ['deposit', 'withdrawal', 'daily_payout', 'referral_bonus']
    amounts = [100, 250, 500, 750, 1000, 1500, 2000, 3000, 5000]
    
    created_count = 0
    
    for user in users:
        # Create 2-3 random transactions per user
        num_transactions = random.randint(2, 3)
        
        for i in range(num_transactions):
            # Random transaction from last 24 hours
            hours_ago = random.randint(1, 24)
            created_at = timezone.now() - timedelta(hours=hours_ago)
            
            transaction_type = random.choice(transaction_types)
            amount = Decimal(str(random.choice(amounts)))
            
            # Create transaction
            Transaction.objects.get_or_create(
                user=user,
                transaction_type=transaction_type,
                amount=amount,
                created_at=created_at,
                defaults={
                    'status': 'completed',
                    'description': f'Sample {transaction_type} transaction'
                }
            )
            created_count += 1
    
    print(f"✅ Created {created_count} sample transactions")
    print("🎉 Live transaction feed should now display data!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
