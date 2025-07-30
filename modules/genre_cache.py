"""Simple in-memory cache for genre data to improve performance."""
import time
from typing import Dict, List, Optional

class GenreCache:
    """Simple in-memory cache for artist genres."""
    
    def __init__(self, ttl_seconds: int = 3600):  # 1 hour TTL
        """
        Initialize the cache.
        
        Args:
            ttl_seconds: Time to live for cached entries in seconds
        """
        self.cache: Dict[str, Dict] = {}
        self.ttl_seconds = ttl_seconds
    
    def get(self, artist_name: str) -> Optional[List[str]]:
        """
        Get genres for an artist from cache.
        
        Args:
            artist_name: Name of the artist
            
        Returns:
            List of genres or None if not cached or expired
        """
        if artist_name not in self.cache:
            return None
            
        entry = self.cache[artist_name]
        
        # Check if entry has expired
        if time.time() - entry['timestamp'] > self.ttl_seconds:
            del self.cache[artist_name]
            return None
            
        return entry['genres']
    
    def set(self, artist_name: str, genres: List[str]) -> None:
        """
        Cache genres for an artist.
        
        Args:
            artist_name: Name of the artist
            genres: List of genres for the artist
        """
        self.cache[artist_name] = {
            'genres': genres,
            'timestamp': time.time()
        }
    
    def clear(self) -> None:
        """Clear all cached entries."""
        self.cache.clear()
    
    def size(self) -> int:
        """Get the number of cached entries."""
        return len(self.cache)
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache.
        
        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = []
        
        for artist_name, entry in self.cache.items():
            if current_time - entry['timestamp'] > self.ttl_seconds:
                expired_keys.append(artist_name)
        
        for key in expired_keys:
            del self.cache[key]
            
        return len(expired_keys)

# Global cache instance
_genre_cache = GenreCache()

def get_genre_cache() -> GenreCache:
    """Get the global genre cache instance."""
    return _genre_cache