#!/usr/bin/env python3
"""
Pure Firebase Referral System
Handles all referral operations using Firebase Realtime Database
"""

import os
import sys
import json
import random
import string
from datetime import datetime, timezone
from decimal import Decimal

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import firebase_admin
    from firebase_admin import credentials, db, auth
    from django.conf import settings
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
    django.setup()
except Exception as e:
    print(f"Error setting up environment: {e}")

class FirebaseReferralSystem:
    def __init__(self):
        self.db = None
        self.initialize_firebase()
        
    def initialize_firebase(self):
        """Initialize Firebase if not already done"""
        try:
            if not firebase_admin._apps:
                # Try to get credentials from environment or file
                cred_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
                if cred_path and os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                else:
                    # Fallback to service account key
                    service_account_info = {
                        "type": "service_account",
                        "project_id": os.environ.get('FIREBASE_PROJECT_ID', 'investmentgrowfi'),
                        "private_key_id": os.environ.get('FIREBASE_PRIVATE_KEY_ID'),
                        "private_key": os.environ.get('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                        "client_email": os.environ.get('FIREBASE_CLIENT_EMAIL'),
                        "client_id": os.environ.get('FIREBASE_CLIENT_ID'),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_x509_cert_url": f"https://www.googleapis.com/oauth2/v1/metadata/x509/{os.environ.get('FIREBASE_CLIENT_EMAIL', '').replace('@', '%40')}"
                    }
                    cred = credentials.Certificate(service_account_info)
                
                database_url = os.environ.get('FIREBASE_DATABASE_URL', 'https://investmentgrowfi-default-rtdb.firebaseio.com/')
                firebase_admin.initialize_app(cred, {'databaseURL': database_url})
            
            self.db = db
            print("✅ Firebase Referral System initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Firebase initialization failed: {e}")
            return False
    
    def generate_referral_code(self, length=8):
        """Generate a unique referral code"""
        characters = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choices(characters, k=length))
            # Check if code already exists
            if not self.get_user_by_referral_code(code):
                return code
    
    def create_user_referral_data(self, phone_number, referral_code=None, referred_by_code=None):
        """Create referral data for a new user in Firebase"""
        try:
            user_code = referral_code or self.generate_referral_code()
            
            user_data = {
                'phone_number': phone_number,
                'referral_code': user_code,
                'referred_by': referred_by_code or None,
                'referrals_count': 0,
                'active_referrals': 0,
                'total_earnings': 0,
                'team_volume': 0,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Store user referral data
            ref = self.db.reference(f'referrals/users/{phone_number}')
            ref.set(user_data)
            
            # Store referral code mapping
            code_ref = self.db.reference(f'referrals/codes/{user_code}')
            code_ref.set({'phone_number': phone_number})
            
            # If user was referred, update referrer's data
            if referred_by_code:
                self.process_new_referral(referred_by_code, phone_number)
            
            print(f"✅ Created referral data for {phone_number} with code {user_code}")
            return user_code
            
        except Exception as e:
            print(f"❌ Error creating user referral data: {e}")
            return None
    
    def get_user_by_referral_code(self, referral_code):
        """Get user by referral code"""
        try:
            ref = self.db.reference(f'referrals/codes/{referral_code}')
            data = ref.get()
            return data.get('phone_number') if data else None
        except Exception as e:
            print(f"❌ Error getting user by referral code: {e}")
            return None
    
    def get_user_referral_data(self, phone_number):
        """Get user's referral data"""
        try:
            ref = self.db.reference(f'referrals/users/{phone_number}')
            return ref.get()
        except Exception as e:
            print(f"❌ Error getting user referral data: {e}")
            return None
    
    def process_new_referral(self, referrer_code, new_user_phone):
        """Process a new referral registration"""
        try:
            referrer_phone = self.get_user_by_referral_code(referrer_code)
            if not referrer_phone:
                print(f"❌ Referrer code {referrer_code} not found")
                return False
            
            # Update referrer's counts
            ref = self.db.reference(f'referrals/users/{referrer_phone}')
            referrer_data = ref.get()
            if referrer_data:
                referrer_data['referrals_count'] = referrer_data.get('referrals_count', 0) + 1
                referrer_data['active_referrals'] = referrer_data.get('active_referrals', 0) + 1
                referrer_data['updated_at'] = datetime.now(timezone.utc).isoformat()
                ref.set(referrer_data)
            
            # Add to referrer's referrals list
            referrals_ref = self.db.reference(f'referrals/users/{referrer_phone}/referrals/{new_user_phone}')
            referrals_ref.set({
                'phone_number': new_user_phone,
                'joined_at': datetime.now(timezone.utc).isoformat(),
                'status': 'active'
            })
            
            # Give registration bonus
            self.add_referral_bonus(referrer_phone, 'registration', 100, f'Registration bonus for {new_user_phone}')
            
            print(f"✅ Processed new referral: {new_user_phone} referred by {referrer_phone}")
            return True
            
        except Exception as e:
            print(f"❌ Error processing new referral: {e}")
            return False
    
    def add_referral_bonus(self, phone_number, bonus_type, amount, description):
        """Add referral bonus to user"""
        try:
            # Add to user's earnings
            ref = self.db.reference(f'referrals/users/{phone_number}')
            user_data = ref.get()
            if user_data:
                user_data['total_earnings'] = user_data.get('total_earnings', 0) + amount
                user_data['updated_at'] = datetime.now(timezone.utc).isoformat()
                ref.set(user_data)
            
            # Record the transaction
            transaction_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(1000, 9999))
            transaction_ref = self.db.reference(f'referrals/transactions/{transaction_id}')
            transaction_ref.set({
                'user_phone': phone_number,
                'type': bonus_type,
                'amount': amount,
                'description': description,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'status': 'completed'
            })
            
            # Update user's balance in main system
            self.update_user_balance(phone_number, amount)
            
            print(f"✅ Added {bonus_type} bonus of ₱{amount} to {phone_number}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding referral bonus: {e}")
            return False
    
    def update_user_balance(self, phone_number, amount):
        """Update user's balance in Firebase"""
        try:
            balance_ref = self.db.reference(f'users/{phone_number}/balance')
            current_balance = balance_ref.get() or 0
            new_balance = current_balance + amount
            balance_ref.set(new_balance)
            
            # Log the balance update
            log_ref = self.db.reference(f'users/{phone_number}/balance_history').push()
            log_ref.set({
                'amount': amount,
                'new_balance': new_balance,
                'type': 'referral_bonus',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            return True
        except Exception as e:
            print(f"❌ Error updating user balance: {e}")
            return False
    
    def calculate_team_volume(self, phone_number):
        """Calculate team volume for a user"""
        try:
            # Get user's referrals
            referrals_ref = self.db.reference(f'referrals/users/{phone_number}/referrals')
            referrals = referrals_ref.get() or {}
            
            total_volume = 0
            for referral_phone in referrals.keys():
                # Get referral's investment amount
                investment_ref = self.db.reference(f'users/{referral_phone}/total_invested')
                invested = investment_ref.get() or 0
                total_volume += invested
                
                # Get referral's balance
                balance_ref = self.db.reference(f'users/{referral_phone}/balance')
                balance = balance_ref.get() or 0
                total_volume += balance
            
            # Update team volume
            volume_ref = self.db.reference(f'referrals/users/{phone_number}/team_volume')
            volume_ref.set(total_volume)
            
            return total_volume
        except Exception as e:
            print(f"❌ Error calculating team volume: {e}")
            return 0
    
    def get_referral_stats(self, phone_number):
        """Get comprehensive referral stats for a user"""
        try:
            user_data = self.get_user_referral_data(phone_number)
            if not user_data:
                return None
            
            # Calculate current team volume
            team_volume = self.calculate_team_volume(phone_number)
            
            return {
                'referral_code': user_data.get('referral_code'),
                'total_referrals': user_data.get('referrals_count', 0),
                'active_referrals': user_data.get('active_referrals', 0),
                'total_earnings': user_data.get('total_earnings', 0),
                'team_volume': team_volume,
                'referred_by': user_data.get('referred_by')
            }
        except Exception as e:
            print(f"❌ Error getting referral stats: {e}")
            return None
    
    def migrate_django_data_to_firebase(self):
        """Migrate existing Django referral data to Firebase"""
        try:
            from myproject.models import UserProfile, ReferralCommission
            
            print("🔄 Starting migration of Django data to Firebase...")
            
            # Migrate all users with referral codes
            users = UserProfile.objects.all()
            migrated_count = 0
            
            for user in users:
                try:
                    # Create Firebase referral data
                    referred_by_code = None
                    if user.referred_by:
                        referred_by_code = user.referred_by.referral_code
                    
                    self.create_user_referral_data(
                        phone_number=user.phone_number,
                        referral_code=user.referral_code,
                        referred_by_code=referred_by_code
                    )
                    
                    # Migrate commissions
                    commissions = ReferralCommission.objects.filter(referrer=user)
                    for commission in commissions:
                        self.add_referral_bonus(
                            phone_number=user.phone_number,
                            bonus_type=commission.commission_type,
                            amount=float(commission.amount),
                            description=f"Migrated: {commission.commission_type} bonus"
                        )
                    
                    migrated_count += 1
                    if migrated_count % 10 == 0:
                        print(f"✅ Migrated {migrated_count} users...")
                        
                except Exception as e:
                    print(f"❌ Error migrating user {user.phone_number}: {e}")
                    continue
            
            print(f"✅ Migration completed! Migrated {migrated_count} users to Firebase")
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False

def main():
    """Test the Firebase referral system"""
    print("🔥 Testing Firebase Referral System")
    print("=" * 50)
    
    referral_system = FirebaseReferralSystem()
    
    if not referral_system.db:
        print("❌ Firebase not initialized. Cannot proceed.")
        return
    
    # Test creating a user
    test_phone = "+639999999999"
    test_code = referral_system.create_user_referral_data(test_phone)
    
    if test_code:
        print(f"✅ Created test user {test_phone} with code {test_code}")
        
        # Test getting stats
        stats = referral_system.get_referral_stats(test_phone)
        print(f"📊 Stats: {stats}")
        
        # Test migration
        print("\n🔄 Testing migration...")
        referral_system.migrate_django_data_to_firebase()
    
    print("\n✅ Firebase Referral System test completed!")

if __name__ == "__main__":
    main()
