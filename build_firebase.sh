#!/bin/bash
# Build script for Render.com deployment

echo "🚀 Starting Firebase-only app build for Render.com..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements_firebase.txt

echo "✅ Build completed successfully!"
echo "🔥 Firebase app ready for deployment!"
