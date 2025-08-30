#!/usr/bin/env python3
"""
Test script to verify withdrawal balance calculation with referral earnings
"""
import os
import sys
import django
from decimal import Decimal

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

# Now import Django modules
from django.contrib.auth.models import User
from myproject.models import UserProfile

def test_withdrawal_balance():
    print("=" * 80)
    print("🧪 WITHDRAWAL BALANCE TEST")
    print("=" * 80)
    
    try:
        # Test user with referrals
        user = User.objects.get(username='+639919101001')
        profile = user.profile
        
        print(f"📱 Testing User: {user.username}")
        print(f"💰 Main Balance: ₱{profile.balance}")
        
        # Simulate referral earnings calculation (as done in withdraw_view)
        referral_earnings = Decimal('205.00')  # From debug output: ₱205
        withdrawable_amount = profile.balance + referral_earnings
        
        print(f"🎁 Referral Earnings: ₱{referral_earnings}")
        print(f"💸 Total Withdrawable: ₱{withdrawable_amount}")
        print()
        print("✅ WITHDRAWAL PAGE DISPLAY:")
        print("   " + "─" * 50)
        print(f"   │ Main Balance:     ₱{profile.balance:>8.2f} │")
        print(f"   │ Referral Earnings: ₱{referral_earnings:>8.2f} │")
        print(f"   │ Total Available:   ₱{withdrawable_amount:>8.2f} │")
        print("   " + "─" * 50)
        print()
        
        # Test various withdrawal amounts
        print("🧮 WITHDRAWAL CALCULATIONS:")
        test_amounts = [100, 500, 1000, float(withdrawable_amount)]
        
        for amount in test_amounts:
            amount_decimal = Decimal(str(amount))
            fee = amount_decimal * Decimal('0.10')  # 10% fee
            net_amount = amount_decimal - fee
            
            print(f"   Withdraw ₱{amount_decimal:,.2f}")
            print(f"   - Fee (10%): ₱{fee:,.2f}")
            print(f"   = You receive: ₱{net_amount:,.2f}")
            print()
        
        return True
        
    except User.DoesNotExist:
        print("❌ Test user +639919101001 not found")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_withdrawal_balance()
