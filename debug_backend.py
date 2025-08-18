#!/usr/bin/env python3
"""
Debug script to test backend functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment():
    """Test environment variables"""
    print("🔍 Testing Environment Variables:")
    print(f"  JWT_SECRET_KEY: {'✅ Set' if os.getenv('JWT_SECRET_KEY') else '❌ Missing'}")
    print(f"  SPOTIFY_REDIRECT_URI: {os.getenv('SPOTIFY_REDIRECT_URI', '❌ Missing')}")
    print(f"  ALLOWED_ORIGINS: {os.getenv('ALLOWED_ORIGINS', '❌ Missing')}")
    print(f"  FLASK_ENV: {os.getenv('FLASK_ENV', 'development')}")
    print()

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing Imports:")
    try:
        from modules.api import SpotifyAPI
        print("  ✅ SpotifyAPI imported successfully")
    except Exception as e:
        print(f"  ❌ SpotifyAPI import failed: {e}")
        return False
    
    try:
        from flask import Flask
        print("  ✅ Flask imported successfully")
    except Exception as e:
        print(f"  ❌ Flask import failed: {e}")
        return False
    
    try:
        from flask_jwt_extended import JWTManager
        print("  ✅ Flask-JWT-Extended imported successfully")
    except Exception as e:
        print(f"  ❌ Flask-JWT-Extended import failed: {e}")
        return False
    
    print()
    return True

def test_spotify_api():
    """Test SpotifyAPI initialization"""
    print("🔍 Testing SpotifyAPI:")
    try:
        from modules.api import SpotifyAPI
        
        # Test with sample credentials
        api = SpotifyAPI(
            client_id="test_client_id",
            client_secret="test_client_secret", 
            redirect_uri="http://localhost:3000/auth/callback"
        )
        print("  ✅ SpotifyAPI instance created successfully")
        
        # Test auth URL generation (should fail gracefully)
        try:
            auth_url = api.get_auth_url()
            if auth_url:
                print("  ✅ Auth URL generated successfully")
            else:
                print("  ⚠️  Auth URL is None (expected with test credentials)")
        except Exception as e:
            print(f"  ⚠️  Auth URL generation failed (expected): {e}")
        
    except Exception as e:
        print(f"  ❌ SpotifyAPI test failed: {e}")
        return False
    
    print()
    return True

def test_flask_app():
    """Test Flask app creation"""
    print("🔍 Testing Flask App:")
    try:
        from api_app import create_app
        app = create_app()
        print("  ✅ Flask app created successfully")
        
        # Test app configuration
        print(f"  JWT_SECRET_KEY configured: {'✅' if app.config.get('JWT_SECRET_KEY') else '❌'}")
        print(f"  JWT_ACCESS_TOKEN_EXPIRES: {app.config.get('JWT_ACCESS_TOKEN_EXPIRES')}")
        
    except Exception as e:
        print(f"  ❌ Flask app creation failed: {e}")
        return False
    
    print()
    return True

def main():
    print("🚀 Backend Debug Script")
    print("=" * 50)
    
    # Test environment
    test_environment()
    
    # Test imports
    if not test_imports():
        print("❌ Import tests failed. Please check your dependencies.")
        sys.exit(1)
    
    # Test SpotifyAPI
    if not test_spotify_api():
        print("❌ SpotifyAPI tests failed.")
        sys.exit(1)
    
    # Test Flask app
    if not test_flask_app():
        print("❌ Flask app tests failed.")
        sys.exit(1)
    
    print("🎉 All tests passed! Backend should be working.")
    print()
    print("Next steps:")
    print("1. Make sure your .env file has the correct values")
    print("2. Start the backend: python api_app.py")
    print("3. Test the health endpoint: curl http://localhost:5000/api/health")
    print("4. Test the debug endpoint: curl http://localhost:5000/api/debug")

if __name__ == "__main__":
    main()
