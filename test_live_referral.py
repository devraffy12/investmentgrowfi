"""
Simple test to check if referral system is working
"""
import requests
import json

def test_team_page():
    """Test the team page to see if referral data shows up"""
    
    # Test with your deployed site
    base_url = "https://investmentgrowfi.onrender.com"
    
    print("🔍 Testing referral system on live site...")
    
    try:
        # Try to access the team page (this should show referral data)
        response = requests.get(f"{base_url}/team/", timeout=10)
        
        print(f"Team page status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Check if referral elements are present
            checks = {
                "Referral Code": "referral_code" in content or "Referral Code" in content,
                "Total Referrals": "total_referrals" in content or "Total Referrals" in content,
                "Active Members": "active_referrals" in content or "Active Members" in content,
                "Team Volume": "team_volume" in content or "Team Volume" in content,
                "Total Earnings": "total_earnings" in content or "Total Earnings" in content,
            }
            
            print("\n📊 Team page elements check:")
            for check_name, found in checks.items():
                status = "✅" if found else "❌"
                print(f"  {status} {check_name}: {'Found' if found else 'Missing'}")
            
            # Check if there are any referral numbers displayed
            import re
            numbers = re.findall(r'₱[\d,]+\.?\d*', content)
            if numbers:
                print(f"\n💰 Found monetary values: {numbers[:5]}...")
            
            referral_patterns = re.findall(r'[A-Z0-9]{6,10}', content)
            if referral_patterns:
                print(f"🔑 Found potential referral codes: {referral_patterns[:3]}...")
            
        else:
            print(f"❌ Team page returned status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing team page: {e}")

def test_registration_with_referral():
    """Test if registration with referral code works"""
    
    base_url = "https://investmentgrowfi.onrender.com"
    
    print("\n🔍 Testing registration page for referral functionality...")
    
    try:
        # Get registration page
        response = requests.get(f"{base_url}/register/", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # Check if referral code input exists
            has_referral_input = "referral_code" in content or "ref=" in content
            print(f"🔑 Referral code input: {'✅ Found' if has_referral_input else '❌ Missing'}")
            
            # Check if there are example referral codes in the page
            import re
            potential_codes = re.findall(r'ref=([A-Z0-9]+)', content)
            if potential_codes:
                print(f"📝 Found referral examples: {potential_codes[:3]}")
        
    except Exception as e:
        print(f"❌ Error testing registration: {e}")

if __name__ == "__main__":
    test_team_page()
    test_registration_with_referral()
    
    print("\n" + "="*50)
    print("📋 SUMMARY:")
    print("1. Check if your team page shows referral data")
    print("2. Try registering a new user with a referral code")
    print("3. Check if the referrer gets bonus and count updates")
    print("="*50)
