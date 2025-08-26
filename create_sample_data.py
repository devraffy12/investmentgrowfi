#!/usr/bin/env python
"""
Script to add sample data for admin dashboard testing
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from myproject.models import Transaction, Investment, InvestmentPlan, UserProfile
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import random

def create_sample_data():
    print("Creating sample data for admin dashboard...")
    
    # Create sample users if they don't exist
    users_data = [
        {'username': 'john_doe', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe'},
        {'username': 'maria_santos', 'email': 'maria@example.com', 'first_name': 'Maria', 'last_name': 'Santos'},
        {'username': 'pedro_cruz', 'email': 'pedro@example.com', 'first_name': 'Pedro', 'last_name': 'Cruz'},
        {'username': 'ana_reyes', 'email': 'ana@example.com', 'first_name': 'Ana', 'last_name': 'Reyes'},
    ]
    
    created_users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults=user_data
        )
        created_users.append(user)
        
        # Create user profile
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={'phone_number': f'+6391234567{random.randint(10, 99)}'}
        )
        
        if created:
            print(f"Created user: {user.username}")
    
    # Create sample transactions
    transaction_types = ['deposit', 'withdrawal', 'investment', 'daily_payout']
    statuses = ['completed', 'pending', 'approved']
    payment_methods = ['gcash', 'paymaya', 'manual']
    
    for i in range(20):  # Create 20 sample transactions
        user = random.choice(created_users)
        transaction_type = random.choice(transaction_types)
        amount = Decimal(str(random.randint(100, 50000)))
        status = random.choice(statuses)
        payment_method = random.choice(payment_methods) if transaction_type in ['deposit', 'withdrawal'] else ''
        
        # Create transaction
        transaction = Transaction.objects.create(
            user=user,
            transaction_type=transaction_type,
            amount=amount,
            status=status,
            payment_method=payment_method,
            description=f"Sample {transaction_type} transaction",
            created_at=timezone.now() - timedelta(days=random.randint(0, 30))
        )
        print(f"Created transaction: {transaction.reference_number} - {transaction_type} ₱{amount}")
    
    # Create sample investment plans if they don't exist
    plans_data = [
        {'name': 'GROWFI 1', 'minimum_amount': 300, 'maximum_amount': 300, 'duration_days': 30},
        {'name': 'GROWFI 2', 'minimum_amount': 700, 'maximum_amount': 700, 'duration_days': 30},
        {'name': 'GROWFI 3', 'minimum_amount': 2200, 'maximum_amount': 2200, 'duration_days': 60},
    ]
    
    for plan_data in plans_data:
        plan, created = InvestmentPlan.objects.get_or_create(
            name=plan_data['name'],
            defaults={
                **plan_data,
                'daily_return_rate': Decimal('0.05'),  # 5% daily return
                'is_active': True
            }
        )
        if created:
            print(f"Created investment plan: {plan.name}")
    
    # Create sample investments
    plans = InvestmentPlan.objects.all()
    for user in created_users[:3]:  # Only for first 3 users
        plan = random.choice(plans)
        investment = Investment.objects.create(
            user=user,
            plan=plan,
            amount=plan.minimum_amount,
            daily_return=plan.daily_profit,
            status='active',
            start_date=timezone.now() - timedelta(days=random.randint(1, 15)),
            days_completed=random.randint(1, 10)
        )
        print(f"Created investment: {user.username} - {plan.name} ₱{plan.minimum_amount}")
    
    print("\nSample data creation completed!")
    print(f"Total users: {User.objects.count()}")
    print(f"Total transactions: {Transaction.objects.count()}")
    print(f"Total investments: {Investment.objects.count()}")

if __name__ == "__main__":
    create_sample_data()
