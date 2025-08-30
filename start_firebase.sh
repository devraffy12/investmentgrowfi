#!/bin/bash
# Start script for Render.com deployment

echo "🚀 Starting Firebase-only GrowFi app on Render.com..."

# Set default port if not provided
PORT=${PORT:-8000}

echo "🌐 Starting app on port $PORT..."

# Start the FastAPI app with optimized settings
exec python firebase_app.py
