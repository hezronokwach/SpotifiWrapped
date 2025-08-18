#!/bin/bash

# Simple development startup script
set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if setup has been run
if [ ! -d "venv" ] || [ ! -d "frontend/node_modules" ]; then
    log_error "Setup not completed. Please run: ./scripts/setup-dev.sh"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    log_warn "No .env file found. Creating from template..."
    cp .env.example .env
    log_warn "Please edit .env file with your configuration before continuing"
    exit 1
fi

log_info "🚀 Starting Spotify Analytics in development mode..."

# Function to start backend
start_backend() {
    log_info "Starting Flask backend..."
    source venv/bin/activate
    python api_app.py &
    BACKEND_PID=$!
    echo $BACKEND_PID > .backend.pid
}

# Function to start frontend
start_frontend() {
    log_info "Starting React frontend..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../.frontend.pid
    cd ..
}

# Function to cleanup on exit
cleanup() {
    log_info "Shutting down servers..."
    
    if [ -f ".backend.pid" ]; then
        kill $(cat .backend.pid) 2>/dev/null || true
        rm .backend.pid
    fi
    
    if [ -f ".frontend.pid" ]; then
        kill $(cat .frontend.pid) 2>/dev/null || true
        rm .frontend.pid
    fi
    
    log_info "Servers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start services
start_backend
sleep 3  # Give backend time to start
start_frontend

log_info "🎉 Development servers started!"
log_info "Backend: http://localhost:5000"
log_info "Frontend: http://localhost:3000"
log_info "Press Ctrl+C to stop both servers"

# Wait for user to stop
wait
