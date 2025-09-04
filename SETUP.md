# 🚀 SpotifiWrapped Setup Guide

## Prerequisites Installation

### 1. Install Python
**Windows:**
- Download from https://python.org/downloads/
- ✅ Check "Add Python to PATH" during installation
- Verify: Open Command Prompt and run `python --version`

**macOS:**
```bash
# Using Homebrew (recommended)
brew install python3

# Or download from python.org
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### 2. Install Node.js
**All Platforms:**
- Download from https://nodejs.org/ (LTS version)
- Verify: `node --version` and `npm --version`

## Quick Setup

### Option 1: Automated Script
```bash
./start-dev.sh
```

### Option 2: Manual Setup

#### Backend (Flask API)
```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Edit .env with your Spotify credentials

# 5. Start Flask API
python api_app.py
```

#### Frontend (React)
```bash
# In a new terminal
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Access the Application
- 🌐 Frontend: http://localhost:3000
- 🔌 API: http://localhost:5000

## Spotify API Setup
1. Go to https://developer.spotify.com/dashboard
2. Create a new app
3. Set redirect URI to: `http://localhost:3000/auth/callback`
4. Copy Client ID and Client Secret to `.env` file

## Troubleshooting

### Python Issues
- **"python not found"**: Install Python and add to PATH
- **"venv not found"**: Install python3-venv package
- **Permission errors**: Use `python -m pip install --user`

### Node.js Issues
- **"npm not found"**: Install Node.js from nodejs.org
- **Permission errors**: Use `npm config set prefix ~/.npm-global`

### Port Issues
- **Port 5000 busy**: Kill process with `lsof -ti:5000 | xargs kill -9`
- **Port 3000 busy**: Kill process with `lsof -ti:3000 | xargs kill -9`