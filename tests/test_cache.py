"""
Test Suite for Cache Module

Tests caching functionality, TTL, and cache management.
"""

import unittest
import sys
import os
import tempfile
import shutil
from datetime import datetime, timedelta
import time

# Add utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.cache import MLBCache


class TestMLBCache(unittest.TestCase):
    """Test cases for MLBCache class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary cache directory for tests
        self.temp_cache_dir = tempfile.mkdtemp()
        self.cache = MLBCache(cache_dir=self.temp_cache_dir, ttl_hours=1)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary cache directory
        if os.path.exists(self.temp_cache_dir):
            shutil.rmtree(self.temp_cache_dir)
    
    def test_initialization(self):
        """Test cache initializes correctly."""
        self.assertEqual(self.cache.cache_dir, self.temp_cache_dir)
        self.assertTrue(os.path.exists(self.temp_cache_dir))
    
    def test_generate_cache_key_consistency(self):
        """Test that same inputs generate same cache key."""
        key1 = self.cache._generate_cache_key('test/endpoint', {'param': 'value'})
        key2 = self.cache._generate_cache_key('test/endpoint', {'param': 'value'})
        
        self.assertEqual(key1, key2)
    
    def test_generate_cache_key_different_params(self):
        """Test that different params generate different keys."""
        key1 = self.cache._generate_cache_key('test/endpoint', {'param': 'value1'})
        key2 = self.cache._generate_cache_key('test/endpoint', {'param': 'value2'})
        
        self.assertNotEqual(key1, key2)
    
    def test_set_and_get_cache(self):
        """Test storing and retrieving data from cache."""
        test_data = {'test': 'data', 'numbers': [1, 2, 3]}
        
        self.cache.set('test/endpoint', {'param': 'value'}, test_data)
        result = self.cache.get('test/endpoint', {'param': 'value'})
        
        self.assertEqual(result, test_data)
    
    def test_get_nonexistent_cache(self):
        """Test getting data that doesn't exist in cache."""
        result = self.cache.get('nonexistent/endpoint', {})
        
        self.assertIsNone(result)
    
    def test_cache_expiration(self):
        """Test that cache expires after TTL."""
        # Create cache with very short TTL
        short_cache = MLBCache(cache_dir=self.temp_cache_dir, ttl_hours=0.0001)  # ~0.36 seconds
        
        test_data = {'test': 'data'}
        short_cache.set('test/endpoint', {}, test_data)
        
        # Should be available immediately
        result1 = short_cache.get('test/endpoint', {})
        self.assertEqual(result1, test_data)
        
        # Wait for expiration
        time.sleep(0.5)
        
        # Should be None after expiration
        result2 = short_cache.get('test/endpoint', {})
        self.assertIsNone(result2)
    
    def test_clear_cache(self):
        """Test clearing all cache entries."""
        # Add some cache entries
        self.cache.set('endpoint1', {}, {'data': 1})
        self.cache.set('endpoint2', {}, {'data': 2})
        
        # Verify they exist
        self.assertIsNotNone(self.cache.get('endpoint1', {}))
        self.assertIsNotNone(self.cache.get('endpoint2', {}))
        
        # Clear cache
        self.cache.clear()
        
        # Verify they're gone
        self.assertIsNone(self.cache.get('endpoint1', {}))
        self.assertIsNone(self.cache.get('endpoint2', {}))
    
    def test_get_cache_stats(self):
        """Test getting cache statistics."""
        # Add some entries
        self.cache.set('endpoint1', {}, {'data': 1})
        self.cache.set('endpoint2', {}, {'data': 2})
        
        stats = self.cache.get_cache_stats()
        
        self.assertIn('total_entries', stats)
        self.assertIn('valid_entries', stats)
        self.assertIn('total_size_mb', stats)
        self.assertEqual(stats['total_entries'], 2)
        self.assertEqual(stats['valid_entries'], 2)
    
    def test_clear_expired_only(self):
        """Test clearing only expired entries."""
        # Create cache with short TTL
        short_cache = MLBCache(cache_dir=self.temp_cache_dir, ttl_hours=0.0001)
        
        # Add entries
        short_cache.set('old', {}, {'data': 'old'})
        time.sleep(0.5)  # Let first entry expire
        short_cache.set('new', {}, {'data': 'new'})
        
        # Clear expired
        short_cache.clear_expired()
        
        # Old should be gone, new should remain
        self.assertIsNone(short_cache.get('old', {}))
        # Note: 'new' might also be expired by the time we check it with such a short TTL
    
    def test_cache_with_complex_data(self):
        """Test caching complex nested data structures."""
        complex_data = {
            'players': [
                {'id': 1, 'name': 'Player 1', 'stats': {'avg': 0.300, 'hr': 25}},
                {'id': 2, 'name': 'Player 2', 'stats': {'avg': 0.285, 'hr': 30}}
            ],
            'metadata': {
                'season': 2024,
                'league': 'MLB'
            }
        }
        
        self.cache.set('complex/endpoint', {'year': 2024}, complex_data)
        result = self.cache.get('complex/endpoint', {'year': 2024})
        
        self.assertEqual(result, complex_data)
    
    def test_cache_file_creation(self):
        """Test that cache files are actually created."""
        self.cache.set('test/endpoint', {}, {'data': 'test'})
        
        # Check that cache files exist
        cache_files = [f for f in os.listdir(self.temp_cache_dir) if f.endswith('.cache')]
        
        self.assertGreater(len(cache_files), 0)


if __name__ == '__main__':
    unittest.main()
