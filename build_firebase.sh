#!/bin/bash
# Build script for Render.com deployment

echo "🚀 Starting Firebase-only app build for Render.com..."

# Upgrade pip first
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Build completed successfully!"
echo "🔥 Firebase app ready for deployment!"
