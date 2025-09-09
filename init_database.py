#!/usr/bin/env python3
"""Initialize user database with proper schema"""

import sys
import os
sys.path.append('.')

from modules.database import SpotifyDatabase

def init_user_database(user_id):
    """Initialize database for a specific user"""
    db_path = f'data/user_{user_id}_spotify_data.db'
    
    print(f"Initializing database: {db_path}")
    
    # Create database with proper schema
    db = SpotifyDatabase(db_path)
    
    print("Database initialized successfully!")
    print(f"Tables created in: {db_path}")
    
    return db

if __name__ == "__main__":
    user_id = sys.argv[1] if len(sys.argv) > 1 else "hezronokwach"
    init_user_database(user_id)