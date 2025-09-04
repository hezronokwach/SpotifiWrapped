#!/bin/bash

# SpotifiWrapped Development Startup Script
# Starts both Flask API and React frontend in development mode

echo "🎵 Starting SpotifiWrapped Development Environment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python is not installed or not in PATH"
    echo ""
    echo "Please install Python first:"
    echo "📥 Windows: Download from https://python.org/downloads/"
    echo "📥 macOS: brew install python3"
    echo "📥 Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "📥 CentOS/RHEL: sudo yum install python3 python3-pip"
    echo ""
    echo "Make sure to add Python to your PATH during installation"
    exit 1
fi

# Determine Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
fi

echo "🐍 Using Python: $PYTHON_CMD"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo "❌ Could not find virtual environment activation script"
    exit 1
fi

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your Spotify API credentials!"
    echo "   SPOTIFY_CLIENT_ID=your_client_id"
    echo "   SPOTIFY_CLIENT_SECRET=your_client_secret"
    echo "   SPOTIFY_REDIRECT_URI=http://localhost:3000/auth/callback"
    read -p "Press Enter after updating .env file..."
fi

# Start Flask API in background
echo "🚀 Starting Flask API server on port 5000..."
$PYTHON_CMD api_app.py &
FLASK_PID=$!

# Wait for Flask to start
sleep 3

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ and try again."
    kill $FLASK_PID
    exit 1
fi

# Install frontend dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install

# Start React development server
echo "🎨 Starting React development server on port 3000..."
npm run dev &
REACT_PID=$!

# Wait for React to start
sleep 5

echo ""
echo "✅ SpotifiWrapped is now running!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 API: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop all servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $FLASK_PID 2>/dev/null
    kill $REACT_PID 2>/dev/null
    echo "✅ All servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Keep script running
wait