#!/usr/bin/env python3
"""
Simple start script for Render.com deployment
Uses uvicorn directly for better compatibility
"""
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting Firebase GrowFi app on port {port}...")
    
    uvicorn.run(
        "firebase_only_app:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )
