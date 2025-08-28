#!/usr/bin/env python3
"""
📱 Phone Number Format Policy Implementation
Enforces +63XXXXXXXXXX format for all phone numbers in the system
"""

import re

class PhoneNumberFormatter:
    """
    Handles phone number formatting and normalization for the investment system
    """
    
    @staticmethod
    def normalize_phone_number(phone_input):
        """
        Converts any Philippine phone number format to +63XXXXXXXXXX
        
        Supported input formats:
        - 09012903192 (local format)
        - 639012903192 (international without +)
        - +639012903192 (full international)
        - 9012903192 (minimal format)
        
        Returns: +63XXXXXXXXXX format or None if invalid
        """
        if not phone_input:
            return None
            
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', str(phone_input).strip())
        
        # Handle different formats
        if cleaned.startswith('+63') and len(cleaned) == 13:
            # Already in correct format: +639012903192
            return cleaned
            
        elif cleaned.startswith('63') and len(cleaned) == 12:
            # International without +: 639012903192
            return '+' + cleaned
            
        elif cleaned.startswith('09') and len(cleaned) == 11:
            # Local format: 09012903192
            return '+63' + cleaned[1:]  # Remove 0, add +63
            
        elif cleaned.startswith('9') and len(cleaned) == 10:
            # Minimal format: 9012903192
            return '+63' + cleaned
            
        else:
            # Invalid format
            return None
    
    @staticmethod
    def is_valid_philippine_number(phone_number):
        """
        Validates if the phone number is a valid Philippine number
        """
        if not phone_number:
            return False
            
        # Must be in +63XXXXXXXXXX format
        pattern = r'^\+63[0-9]{10}$'
        return bool(re.match(pattern, phone_number))
    
    @staticmethod
    def format_for_display(phone_number):
        """
        Formats phone number for user display
        +639012903192 -> +63 901 290 3192
        """
        if not phone_number or len(phone_number) != 13:
            return phone_number
            
        return f"{phone_number[:3]} {phone_number[3:6]} {phone_number[6:9]} {phone_number[9:]}"


def test_phone_formatter():
    """Test the phone number formatter with various inputs"""
    
    print('📱 PHONE NUMBER FORMAT POLICY TESTING')
    print('=' * 60)
    
    test_cases = [
        '09012903192',      # Local format
        '639012903192',     # International without +
        '+639012903192',    # Full international (correct)
        '9012903192',       # Minimal format
        '09999999999',      # Another local
        '639123456789',     # Another international
        '+639876543210',    # Another full international
        '9876543210',       # Another minimal
        'invalid',          # Invalid input
        '123',              # Too short
        '091234567890',     # Too long
    ]
    
    formatter = PhoneNumberFormatter()
    
    print('🔄 NORMALIZATION TESTING:')
    print('-' * 60)
    print(f'{"Input":<20} {"Normalized":<20} {"Valid":<10} {"Display"}')
    print('-' * 60)
    
    for test_input in test_cases:
        normalized = formatter.normalize_phone_number(test_input)
        is_valid = formatter.is_valid_philippine_number(normalized)
        display = formatter.format_for_display(normalized) if normalized else 'N/A'
        
        print(f'{test_input:<20} {normalized or "INVALID":<20} {"✅" if is_valid else "❌":<10} {display}')
    
    print()
    print('📋 POLICY SUMMARY:')
    print('=' * 60)
    print('✅ Storage Format: +63XXXXXXXXXX only')
    print('✅ Input Support: 09XX, 63XX, +63XX, 9XX formats')
    print('✅ Validation: Philippine numbers only')
    print('✅ Display: Formatted for readability')

if __name__ == '__main__':
    test_phone_formatter()
