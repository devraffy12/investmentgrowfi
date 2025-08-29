#!/usr/bin/env python3
"""
Simple Python build script for Render.com
Alternative to shell scripts for better compatibility
"""

import subprocess
import sys
import os

def run_command(command, description):
    print(f"🚀 {description}...")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        sys.exit(1)
    else:
        print(f"✅ {description} completed!")
    return result.stdout

def main():
    print("🔥 Starting Firebase-only app build for Render.com...")
    
    # Install requirements
    run_command("pip install -r requirements_firebase.txt", "Installing dependencies")
    
    print("🎉 Build completed successfully!")
    print("🚀 Ready for deployment!")

if __name__ == "__main__":
    main()
