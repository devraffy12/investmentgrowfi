#!/usr/bin/env python
"""
Monitor Render.com IP address changes for LA2568 whitelist management
"""
import requests
import socket
import json
import os
from datetime import datetime

def get_current_ips():
    """Get current IP addresses for the domain"""
    domain = "investmentgrowfi.onrender.com"
    
    try:
        # Get DNS resolved IPs (inbound traffic)
        ip_info = socket.gethostbyname_ex(domain)
        dns_ips = ip_info[2]
        
        # Static outbound IPs from Render dashboard (for API calls)
        render_outbound_ips = [
            "44.229.227.142",
            "54.188.71.94", 
            "52.13.128.108"
        ]
        
        # Get current outgoing IP (development)
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        current_ip = response.json()["ip"]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "domain": domain,
            "dns_ips": dns_ips,  # For inbound traffic to your site
            "render_outbound_ips": render_outbound_ips,  # For API calls from your site
            "dev_ip": current_ip,
            "status": "success"
        }
    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "status": "error"
        }

def load_previous_ips():
    """Load previously recorded IP addresses"""
    ip_file = "ip_history.json"
    if os.path.exists(ip_file):
        try:
            with open(ip_file, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_ip_history(current_data, history):
    """Save IP history to file"""
    history.append(current_data)
    
    # Keep only last 50 records
    if len(history) > 50:
        history = history[-50:]
    
    with open("ip_history.json", 'w') as f:
        json.dump(history, f, indent=2)
    
    return history

def compare_ips(current, previous):
    """Compare current IPs with previous ones"""
    if not previous:
        return {"status": "first_run", "message": "First IP check - no previous data"}
    
    last_record = previous[-1]
    if last_record.get("status") != "success":
        return {"status": "no_comparison", "message": "Previous check failed"}
    
    # Compare DNS IPs (inbound)
    current_dns = set(current.get("dns_ips", []))
    previous_dns = set(last_record.get("dns_ips", []))
    
    # Compare Render outbound IPs  
    current_outbound = set(current.get("render_outbound_ips", []))
    previous_outbound = set(last_record.get("render_outbound_ips", []))
    
    current_dev = current.get("dev_ip")
    previous_dev = last_record.get("dev_ip")
    
    changes = {}
    
    # Check DNS IP changes (inbound traffic)
    if current_dns != previous_dns:
        changes["dns_ips"] = {
            "changed": True,
            "added": list(current_dns - previous_dns),
            "removed": list(previous_dns - current_dns),
            "current": list(current_dns),
            "previous": list(previous_dns)
        }
    else:
        changes["dns_ips"] = {"changed": False, "ips": list(current_dns)}
    
    # Check Render outbound IP changes (API calls)
    if current_outbound != previous_outbound:
        changes["render_outbound_ips"] = {
            "changed": True,
            "added": list(current_outbound - previous_outbound),
            "removed": list(previous_outbound - current_outbound),
            "current": list(current_outbound),
            "previous": list(previous_outbound)
        }
    else:
        changes["render_outbound_ips"] = {"changed": False, "ips": list(current_outbound)}
    
    # Check development IP changes
    if current_dev != previous_dev:
        changes["dev_ip"] = {
            "changed": True,
            "current": current_dev,
            "previous": previous_dev
        }
    else:
        changes["dev_ip"] = {"changed": False, "ip": current_dev}
    
    return {"status": "compared", "changes": changes}

def print_whitelist_info(current_data, comparison):
    """Print current whitelist information"""
    print("🔍 RENDER.COM IP MONITORING")
    print("=" * 60)
    print(f"Timestamp: {current_data['timestamp']}")
    print(f"Domain: {current_data.get('domain', 'N/A')}")
    print()
    
    if current_data.get("status") == "success":
        # Current IPs
        print("📍 CURRENT IP ADDRESSES:")
        print(f"DNS IPs (inbound to your site): {', '.join(current_data['dns_ips'])}")
        print(f"Render Outbound IPs (API calls): {', '.join(current_data['render_outbound_ips'])}")
        print(f"Your Dev IP: {current_data['dev_ip']}")
        print()
        
        # Changes detection
        if comparison["status"] == "compared":
            changes = comparison["changes"]
            
            print("🔄 IP CHANGE DETECTION:")
            
            # DNS IP changes
            if changes["dns_ips"]["changed"]:
                print("⚠️  DNS IPs CHANGED!")
                if changes["dns_ips"]["added"]:
                    print(f"   ➕ Added: {', '.join(changes['dns_ips']['added'])}")
                if changes["dns_ips"]["removed"]:
                    print(f"   ➖ Removed: {', '.join(changes['dns_ips']['removed'])}")
            else:
                print("✅ DNS IPs unchanged")
            
            # Render outbound IP changes
            if changes["render_outbound_ips"]["changed"]:
                print("⚠️  RENDER OUTBOUND IPs CHANGED!")
                if changes["render_outbound_ips"]["added"]:
                    print(f"   ➕ Added: {', '.join(changes['render_outbound_ips']['added'])}")
                if changes["render_outbound_ips"]["removed"]:
                    print(f"   ➖ Removed: {', '.join(changes['render_outbound_ips']['removed'])}")
                print("   🚨 UPDATE LA2568 WHITELIST!")
            else:
                print("✅ Render outbound IPs unchanged")
            
            # Dev IP changes  
            if changes["dev_ip"]["changed"]:
                print(f"⚠️  YOUR DEV IP CHANGED!")
                print(f"   Old: {changes['dev_ip']['previous']}")
                print(f"   New: {changes['dev_ip']['current']}")
                print("   🚨 UPDATE LA2568 WHITELIST!")
            else:
                print("✅ Your dev IP unchanged")
        else:
            print(f"ℹ️  {comparison['message']}")
        
        print()
        print("📝 WHITELIST REQUEST FOR LA2568:")
        print("-" * 40)
        print("Merchant ID: RodolfHitler")
        print("Domain: https://investmentgrowfi.onrender.com")
        print()
        print("🌐 OUTBOUND IPs TO WHITELIST (for API calls):")
        for ip in current_data['render_outbound_ips']:
            print(f"   • {ip}")
        print()
        print(f"🔧 DEV IP TO WHITELIST: {current_data['dev_ip']}")
        print("📞 Callback URL: https://investmentgrowfi.onrender.com/payment/callback/")
        print("✅ Return URL: https://investmentgrowfi.onrender.com/payment/success/")
        print()
        
        # Important note
        print("⚠️  IMPORTANT:")
        print("   LA2568 needs to whitelist the OUTBOUND IPs (API calls)")
        print("   These are different from DNS IPs (inbound traffic)")
        print()
        
        # Check if we need to notify LA2568
        if (comparison["status"] == "compared" and 
            (comparison["changes"]["render_outbound_ips"]["changed"] or 
             comparison["changes"]["dev_ip"]["changed"])):
            
            print("🚨 ACTION REQUIRED:")
            print("   Contact LA2568 support to update whitelist!")
            print("   Send them the updated OUTBOUND IP addresses above.")
            
    else:
        print(f"❌ Error getting IP information: {current_data.get('error')}")

def main():
    print("Starting IP monitoring for LA2568 whitelist management...\n")
    
    # Get current IP information
    current_data = get_current_ips()
    
    # Load previous history
    history = load_previous_ips()
    
    # Compare with previous
    comparison = compare_ips(current_data, history)
    
    # Save to history
    history = save_ip_history(current_data, history)
    
    # Print results
    print_whitelist_info(current_data, comparison)
    
    # Summary
    print("=" * 60)
    print(f"💾 History saved ({len(history)} records total)")
    print("🔄 Run this script regularly to monitor IP changes")
    print("📋 Always keep LA2568 updated with current IPs")

if __name__ == "__main__":
    main()
