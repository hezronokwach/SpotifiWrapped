#!/bin/bash

# Development environment setup script
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

log_info "🚀 Setting up Spotify Analytics development environment..."

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        log_error "npm is not installed"
        exit 1
    fi
    
    log_info "Prerequisites check passed ✓"
}

# Setup backend
setup_backend() {
    log_info "Setting up backend..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    log_info "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Create necessary directories
    mkdir -p data logs
    
    log_info "Backend setup completed ✓"
}

# Setup frontend
setup_frontend() {
    log_info "Setting up frontend..."
    
    cd frontend
    
    # Clear any existing node_modules and package-lock.json
    if [ -d "node_modules" ]; then
        log_info "Cleaning existing node_modules..."
        rm -rf node_modules package-lock.json
    fi

    # Install dependencies
    log_info "Installing Node.js dependencies..."
    npm install
    
    cd ..
    
    log_info "Frontend setup completed ✓"
}

# Setup environment
setup_environment() {
    log_info "Setting up environment..."
    
    if [ ! -f ".env" ]; then
        log_info "Creating .env file from template..."
        cp .env.example .env
        log_warn "Please edit .env file with your configuration"
    else
        log_info ".env file already exists"
    fi
    
    log_info "Environment setup completed ✓"
}

# Setup git hooks (optional)
setup_git_hooks() {
    if [ -d ".git" ]; then
        log_info "Setting up git hooks..."
        
        # Pre-commit hook for code quality
        cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Run frontend linting
cd frontend && npm run lint
if [ $? -ne 0 ]; then
    echo "Frontend linting failed. Please fix the issues before committing."
    exit 1
fi
cd ..

# Run backend tests (if available)
if [ -f "run_tests.py" ]; then
    python run_tests.py
    if [ $? -ne 0 ]; then
        echo "Backend tests failed. Please fix the issues before committing."
        exit 1
    fi
fi
EOF
        
        chmod +x .git/hooks/pre-commit
        log_info "Git hooks setup completed ✓"
    fi
}

# Main setup
main() {
    check_prerequisites
    setup_backend
    setup_frontend
    setup_environment
    setup_git_hooks
    
    log_info "🎉 Development environment setup completed!"
    echo ""
    log_info "Next steps:"
    echo "1. Edit .env file with your configuration"
    echo "2. Start backend: source venv/bin/activate && python api_app.py"
    echo "3. Start frontend: cd frontend && npm run dev"
    echo "4. Visit http://localhost:3000"
}

# Run main function
main "$@"
