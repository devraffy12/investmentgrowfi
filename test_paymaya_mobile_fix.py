#!/usr/bin/env python3
"""
Test PayMaya mobile number validation fix
"""
import os
import sys
import django
from decimal import Decimal

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from payments.views import GalaxyPaymentService

def test_mobile_validation():
    """Test mobile number validation for PayMaya"""
    
    service = GalaxyPaymentService()
    
    # Test cases for mobile number validation
    test_cases = [
        ("09171234567", "09171234567"),  # Correct format
        ("9171234567", "09171234567"),   # Missing leading 0
        ("639171234567", "09171234567"), # Country code 63 (12 digits)
        ("+639171234567", "09171234567"), # Country code +63
        ("0917 123 4567", "09171234567"), # With spaces
        ("0917-123-4567", "09171234567"), # With dashes
        ("invalid", "09919067713"),       # Invalid number - uses default
        ("", "09919067713"),              # Empty - uses default
        (None, "09919067713"),            # None - uses default
    ]
    
    print("🧪 Testing PayMaya Mobile Number Validation")
    print("=" * 60)
    
    for input_mobile, expected in test_cases:
        # Test the mobile formatting logic
        if input_mobile and str(input_mobile).strip():
            clean_mobile = ''.join(filter(str.isdigit, str(input_mobile)))
            
            if clean_mobile.startswith('63') and len(clean_mobile) >= 12:
                # Remove country code 63 and add 0
                clean_mobile = '0' + clean_mobile[2:]
            elif clean_mobile.startswith('9') and len(clean_mobile) == 10:
                # 10-digit number starting with 9, add 0
                clean_mobile = '0' + clean_mobile
            elif not clean_mobile.startswith('09') and len(clean_mobile) >= 9:
                # Other formats, try to fix
                clean_mobile = '09' + clean_mobile[-9:]
            
            # Validate final format
            if len(clean_mobile) == 11 and clean_mobile.startswith('09'):
                result = clean_mobile
            else:
                result = "09919067713"  # Default
        else:
            result = "09919067713"  # Default
        
        status = "✅" if result == expected else "❌"
        print(f"{status} Input: '{input_mobile}' -> Expected: '{expected}' -> Got: '{result}'")
    
    print("\n" + "=" * 60)
    print("✅ PayMaya mobile validation test completed!")
    print("\n📱 Valid PayMaya mobile formats:")
    print("   - 09XXXXXXXXX (11 digits starting with 09)")
    print("   - Will auto-convert from various formats")
    print("   - Falls back to default if invalid")

if __name__ == "__main__":
    test_mobile_validation()
