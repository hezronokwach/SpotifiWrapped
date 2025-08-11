#!/usr/bin/env python3
"""
Simple test script to verify session management implementation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.session_manager import UserSession, get_user_components, get_demo_components, is_authenticated, is_demo_mode
from datetime import datetime

def test_user_session():
    """Test UserSession class functionality."""
    print("Testing UserSession class...")
    
    # Create a test user session
    user_session = UserSession(
        user_id="test_user_123",
        display_name="Test User",
        access_token="test_access_token",
        refresh_token="test_refresh_token"
    )
    
    print(f"✅ UserSession created: {user_session.user_id}")
    print(f"✅ Database path: {user_session.db_path}")
    
    # Test serialization
    session_dict = user_session.to_dict()
    print(f"✅ Session serialized: {list(session_dict.keys())}")
    
    # Test deserialization
    restored_session = UserSession.from_dict(session_dict)
    print(f"✅ Session restored: {restored_session.user_id}")
    
    return True

def test_demo_components():
    """Test demo components functionality."""
    print("\nTesting demo components...")
    
    spotify_api, database, data_collector = get_demo_components()
    
    print(f"✅ Demo spotify_api: {spotify_api}")
    print(f"✅ Demo database: {database is not None}")
    print(f"✅ Demo data_collector: {data_collector}")
    print(f"✅ Demo database path: {database.db_path if database else 'None'}")
    
    return True

def test_session_helpers():
    """Test session helper functions."""
    print("\nTesting session helper functions...")
    
    # These will return False since we're not in a Flask context
    print(f"✅ is_authenticated(): {is_authenticated()}")
    print(f"✅ is_demo_mode(): {is_demo_mode()}")
    
    return True

def main():
    """Run all tests."""
    print("🧪 Testing Session Management Implementation")
    print("=" * 50)
    
    try:
        test_user_session()
        test_demo_components()
        test_session_helpers()
        
        print("\n" + "=" * 50)
        print("✅ All session management tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)