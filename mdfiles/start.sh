#!/bin/bash

# Solar Sharing - Complete Startup Script
# This script properly starts both backend and frontend

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         SOLAR SHARING - COMPLETE STARTUP                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Must run from /home/akash/Desktop/SOlar_Sharing"
    exit 1
fi

# Step 1: Kill any existing processes
echo "📋 Step 1: Cleaning up existing processes..."
pkill -f "npm start" 2>/dev/null || true
pkill -f "expo start" 2>/dev/null || true
pkill -f "node" 2>/dev/null || true
sleep 2
echo "✓ Processes cleaned up"
echo ""

# Step 2: Start Backend
echo "📋 Step 2: Starting Backend Server..."
cd backend
npm start &
BACKEND_PID=$!
echo "✓ Backend starting (PID: $BACKEND_PID)"
sleep 3
echo ""

# Step 3: Clear Frontend Cache
echo "📋 Step 3: Clearing Frontend Cache..."
cd ../frontend
rm -rf .expo node_modules/.cache metro.config.js.cache
echo "✓ Cache cleared"
echo ""

# Step 4: Start Frontend
echo "📋 Step 4: Starting Frontend (Expo)..."
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  EXPO DEV SERVER STARTING                                      ║"
echo "║  • Scan QR code with Expo Go (Android)                         ║"
echo "║  • Or press 'a' for Android emulator                           ║"
echo "║  • Press 'w' for web browser                                   ║"
echo "║  • Press 'r' to reload                                         ║"
echo "║  • Press 'q' to quit                                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

npx expo start --clear

# Cleanup on exit
trap "kill $BACKEND_PID 2>/dev/null" EXIT
