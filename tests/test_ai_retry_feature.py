"""
Test the retry feature for AI queries.
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data_fetcher import MLBDataFetcher
from src.data_processor import MLBDataProcessor
from src.ai_query_handler import AIQueryHandler
from utils.ai_code_cache import AICodeCache


class TestAIRetryFeature(unittest.TestCase):
    """Test AI query retry functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.fetcher = MLBDataFetcher()
        cls.processor = MLBDataProcessor()
        cls.ai_handler = AIQueryHandler(cls.fetcher, cls.processor)
        cls.cache = AICodeCache()
    
    def test_retry_feature(self):
        """Test that we can retry a query by clearing its cache."""
        # Skip if AI not available
        if not self.ai_handler.is_available():
            self.skipTest("AI not available")
        
        query = "Who hit more home runs in 2023? Gunnar Henderson or Bobby Witt Jr.?"
        season = 2023
        
        # First execution (should generate or use existing cache)
        result1 = self.ai_handler.handle_query_with_retry(query, season)
        self.assertTrue(result1.get('success'), "First execution should succeed")
        
        # Get cache key
        cache_key = self.cache._generate_cache_key(query, season)
        
        # Verify it's cached
        cached_code = self.cache.get(query, season)
        self.assertIsNotNone(cached_code, "Query should be cached after execution")
        
        # Second execution (should use cache)
        result2 = self.ai_handler.handle_query_with_retry(query, season)
        self.assertTrue(result2.get('success'), "Second execution should succeed")
        
        # Test retry feature - remove from cache
        removed = self.cache.remove(cache_key)
        self.assertTrue(removed, "Cache removal should succeed")
        
        # Verify cache is cleared
        cached_code_after = self.cache.get(query, season)
        self.assertIsNone(cached_code_after, "Cache should be cleared after removal")
        
        # Third execution (should generate fresh code)
        result3 = self.ai_handler.handle_query_with_retry(query, season)
        self.assertTrue(result3.get('success'), "Third execution should succeed")
        self.assertFalse(result3.get('cached', False), "Should generate fresh code after cache clear")


if __name__ == "__main__":
    unittest.main()

