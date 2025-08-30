#!/usr/bin/env python3
"""
Smart Django development server launcher with Firebase warmup
"""
import subprocess
import sys
import time
import threading
import os

def run_warmup():
    """Run Firebase warmup in background"""
    try:
        print("🔥 Starting Firebase warmup...")
        result = subprocess.run([
            sys.executable, 'manage.py', 'warmup_firebase'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Firebase warmup completed successfully")
            print(result.stdout)
        else:
            print("⚠️ Firebase warmup had issues:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⚠️ Firebase warmup timed out")
    except Exception as e:
        print(f"⚠️ Firebase warmup error: {e}")

def main():
    print("🚀 Starting Django development server with Firebase optimization...")
    
    # Start warmup in background
    warmup_thread = threading.Thread(target=run_warmup, daemon=True)
    warmup_thread.start()
    
    # Give warmup a moment to start
    time.sleep(1)
    
    # Start Django development server
    try:
        print("🌐 Starting Django development server...")
        subprocess.run([
            sys.executable, 'manage.py', 'runserver', '--noreload'
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()
