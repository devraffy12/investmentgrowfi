#!/bin/bash
# Start script for Render.com deployment

echo "🚀 Starting Firebase-only GrowFi app on Render.com..."

# Set default port if not provided
PORT=${PORT:-8000}

echo "🌐 Starting app on port $PORT..."

# Start the FastAPI app with Gunicorn (production)
exec gunicorn firebase_only_app:app \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --log-level info
