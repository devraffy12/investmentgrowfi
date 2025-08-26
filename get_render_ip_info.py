#!/usr/bin/env python
"""
Script to determine the IP addresses used by Render.com
"""
import requests
import socket
import sys

def get_render_ip_info():
    """
    Get IP information about Render.com deployment
    """
    print("🔍 Checking Render.com IP Information")
    print("=" * 50)
    
    # Your Render.com domain
    render_domain = "investmentgrowfi.onrender.com"
    
    # 1. Get DNS information
    try:
        print(f"Looking up DNS for: {render_domain}")
        ip_addresses = socket.gethostbyname_ex(render_domain)[2]
        print(f"DNS resolved to: {ip_addresses}")
    except Exception as e:
        print(f"DNS lookup failed: {e}")
        ip_addresses = []
    
    # 2. Get current outgoing IP
    try:
        print("\nChecking your current outgoing IP:")
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        current_ip = response.json()["ip"]
        print(f"Current IP: {current_ip}")
    except Exception as e:
        print(f"IP check failed: {e}")
        current_ip = "Unknown"
    
    # 3. Build the IP whitelist request
    print("\n" + "=" * 50)
    print("📝 LA2568 WHITELIST REQUEST INFORMATION")
    print("=" * 50)
    print("Please send the following to LA2568 support:")
    print("\nDear LA2568 Support,")
    print("\nI continue to receive the whitelist error:")
    print('"Not added to the api whitelist:QXBpQ29udHJvbGxlci5waHA=:682"')
    print("\nPlease whitelist the following for my merchant account:")
    print(f"1. Merchant ID: RodolfHitler")
    print(f"2. Production Domain: https://investmentgrowfi.onrender.com")
    print(f"3. Render.com IP Addresses: {', '.join(ip_addresses)}")
    print(f"4. My Development IP Address: {current_ip}")
    print(f"5. Callback URL: https://investmentgrowfi.onrender.com/payment/callback/")
    print(f"6. Return URL: https://investmentgrowfi.onrender.com/payment/success/")
    
    print("\nI've updated my code with the correct payment channel configurations you provided:")
    print("- GCash QR: payment_type=1, bank_code=gcash")
    print("- GCash H5: payment_type=7, bank_code=mya")
    print("- PayMaya: payment_type=3, bank_code=PMP")
    
    print("\nThank you for your assistance.")
    
if __name__ == "__main__":
    get_render_ip_info()
