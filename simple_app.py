#!/usr/bin/env python3
"""
Minimal Firebase app for Render.com
"""
import os
from fastapi import FastAPI

app = FastAPI(title="GrowFi", version="1.0.0")

@app.get("/")
def home():
    return {"message": "🚀 GrowFi Firebase App is Running!", "status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy", "app": "firebase_growfi"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
