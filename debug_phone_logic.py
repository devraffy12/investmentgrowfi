#!/usr/bin/env python3

def clean_phone_number(phone):
    """Test the exact logic issue"""
    if not phone:
        return phone
    
    # Remove all non-digit characters
    digits = ''.join(c for c in str(phone) if c.isdigit())
    print(f"Input: '{phone}' -> Digits: '{digits}' -> Length: {len(digits)}")
    
    if not digits:
        return phone
    
    # Handle different formats
    if digits.startswith('09') and len(digits) == 11:
        # 09xxxxxxxxx -> +639xxxxxxxxx
        result = f'+63{digits[1:]}'
        print(f"  Matched: 09 format -> {result}")
        return result
    elif digits.startswith('099') and len(digits) == 12:
        # 099xxxxxxxxx -> +639xxxxxxxxx (remove first 0, keep 9xxxxxxxxx)
        result = f'+63{digits[2:]}'  # Skip first two chars "09", keep rest
        print(f"  Matched: 099 format -> {result}")
        return result
    elif digits.startswith('99') and len(digits) == 11:
        # 99xxxxxxxxx -> +639xxxxxxxxx (remove first 9, keep 9xxxxxxxxx) 
        result = f'+63{digits[1:]}'  # Skip first char "9", keep rest "9xxxxxxxxx"
        print(f"  Matched: 99 format -> {result}")
        return result
    elif digits.startswith('9') and len(digits) == 10:
        # 9xxxxxxxxx -> +639xxxxxxxxx  
        result = f'+63{digits}'
        print(f"  Matched: 9 format -> {result}")
        return result
    elif digits.startswith('63') and len(digits) == 12:
        # 639xxxxxxxxx -> +639xxxxxxxxx
        result = f'+{digits}'
        print(f"  Matched: 63 format -> {result}")
        return result
    elif len(digits) >= 10:
        # For edge cases, take last 10 digits and add +639
        last_10 = digits[-10:]
        result = f'+639{last_10}'
        print(f"  Matched: fallback format -> {result}")
        return result
    
    print(f"  No match, returning original: {phone}")
    return phone

# Test the problematic cases
test_cases = [
    "099012903192",
    "99012903192",
    "09012903192",
    "9012903192"
]

print("🔍 DEBUGGING PHONE NORMALIZATION")
print("=" * 50)

for test in test_cases:
    result = clean_phone_number(test)
    print(f"Final result: '{test}' -> '{result}'")
    print()
