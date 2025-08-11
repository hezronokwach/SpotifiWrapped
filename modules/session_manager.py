"""
Simplified session management for SpotifiWrapped application.
Database-only approach with individual user databases.
"""

from datetime import datetime
from modules.api import SpotifyAPI
from modules.database import SpotifyDatabase
from modules.data_collector import SpotifyDataCollector


def get_user_components(user_id):
    """Get user-specific components based on user_id."""
    if not user_id:
        return None, None, None
    
    # Get user's individual database
    user_db = SpotifyDatabase(db_path=f'data/user_{user_id}_spotify_data.db')
    
    # Try to get stored OAuth tokens
    tokens = user_db.get_oauth_tokens()
    if not tokens:
        return None, user_db, None
    
    # Create SpotifyAPI with stored tokens
    spotify_api = SpotifyAPI()
    spotify_api.set_token(tokens)
    
    # Create data collector
    data_collector = SpotifyDataCollector(spotify_api, user_db)
    
    return spotify_api, user_db, data_collector


def get_demo_components():
    """Get demo components for sample data users."""
    sample_db = SpotifyDatabase(db_path='data/sample_spotify_data.db')
    return None, sample_db, None


def store_user_tokens(user_id, tokens):
    """Store OAuth tokens in user's database."""
    user_db = SpotifyDatabase(db_path=f'data/user_{user_id}_spotify_data.db')
    user_db.store_oauth_tokens(tokens)


def get_authenticated_user_id():
    """Get current authenticated user ID from URL or state."""
    # This will be implemented based on how we track current user
    # For now, return None - will be updated when we implement URL-based tracking
    return None