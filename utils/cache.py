"""
Cache Module

This module provides functionality to cache API responses to avoid redundant API calls.
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import pickle


class MLBCache:
    """Manages caching of MLB API responses."""
    
    def __init__(self, cache_dir: str = None, ttl_hours: int = 24):
        """
        Initialize the cache.
        
        Args:
            cache_dir: Directory to store cache files (defaults to data/cache)
            ttl_hours: Time-to-live in hours for cached data (default 24)
        """
        if cache_dir is None:
            # Default to data/cache directory
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cache_dir = os.path.join(base_dir, 'data', 'cache')
        
        self.cache_dir = cache_dir
        self.ttl = timedelta(hours=ttl_hours)
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _generate_cache_key(self, endpoint: str, params: Dict) -> str:
        """
        Generate a unique cache key based on endpoint and parameters.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            Hash string to use as cache key
        """
        # Create a stable string representation of the request
        param_str = json.dumps(params, sort_keys=True) if params else ""
        cache_string = f"{endpoint}:{param_str}"
        
        # Generate hash
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get the file path for a cache key."""
        return os.path.join(self.cache_dir, f"{cache_key}.cache")
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Any]:
        """
        Retrieve data from cache if available and not expired.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            Cached data or None if not found/expired
        """
        cache_key = self._generate_cache_key(endpoint, params)
        cache_path = self._get_cache_path(cache_key)
        
        # Check if cache file exists
        if not os.path.exists(cache_path):
            return None
        
        try:
            # Load cache file
            with open(cache_path, 'rb') as f:
                cache_data = pickle.load(f)
            
            # Check if expired
            cached_time = cache_data.get('timestamp')
            if cached_time and datetime.now() - cached_time < self.ttl:
                return cache_data.get('data')
            else:
                # Expired - remove cache file
                os.remove(cache_path)
                return None
                
        except Exception as e:
            # If there's any error reading cache, just return None
            print(f"Cache read error: {e}")
            return None
    
    def set(self, endpoint: str, params: Optional[Dict], data: Any):
        """
        Store data in cache.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            data: Data to cache
        """
        cache_key = self._generate_cache_key(endpoint, params)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            cache_data = {
                'timestamp': datetime.now(),
                'endpoint': endpoint,
                'params': params,
                'data': data
            }
            
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
                
        except Exception as e:
            print(f"Cache write error: {e}")
    
    def clear(self):
        """Clear all cached data."""
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    os.remove(os.path.join(self.cache_dir, filename))
            print("Cache cleared successfully")
        except Exception as e:
            print(f"Error clearing cache: {e}")
    
    def clear_expired(self):
        """Remove expired cache entries."""
        try:
            count = 0
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    cache_path = os.path.join(self.cache_dir, filename)
                    try:
                        with open(cache_path, 'rb') as f:
                            cache_data = pickle.load(f)
                        
                        cached_time = cache_data.get('timestamp')
                        if cached_time and datetime.now() - cached_time >= self.ttl:
                            os.remove(cache_path)
                            count += 1
                    except:
                        # If there's an error, remove the corrupted cache file
                        os.remove(cache_path)
                        count += 1
            
            print(f"Removed {count} expired cache entries")
        except Exception as e:
            print(f"Error clearing expired cache: {e}")
    
    def get_cache_stats(self) -> Dict:
        """
        Get statistics about the cache.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            total_files = 0
            expired_files = 0
            total_size = 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    total_files += 1
                    cache_path = os.path.join(self.cache_dir, filename)
                    total_size += os.path.getsize(cache_path)
                    
                    try:
                        with open(cache_path, 'rb') as f:
                            cache_data = pickle.load(f)
                        
                        cached_time = cache_data.get('timestamp')
                        if cached_time and datetime.now() - cached_time >= self.ttl:
                            expired_files += 1
                    except:
                        expired_files += 1
            
            return {
                'total_entries': total_files,
                'expired_entries': expired_files,
                'valid_entries': total_files - expired_files,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'cache_dir': self.cache_dir
            }
        except Exception as e:
            return {'error': str(e)}


if __name__ == "__main__":
    # Example usage
    cache = MLBCache()
    
    # Show cache stats
    stats = cache.get_cache_stats()
    print("Cache Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
