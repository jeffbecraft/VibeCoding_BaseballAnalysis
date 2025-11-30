"""
Test Suite for MLBDataFetcher

Tests API calls, caching, error handling, and data retrieval.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_fetcher import MLBDataFetcher


class TestMLBDataFetcher(unittest.TestCase):
    """Test cases for MLBDataFetcher class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary cache directory for tests
        self.temp_cache_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary cache directory
        if os.path.exists(self.temp_cache_dir):
            shutil.rmtree(self.temp_cache_dir)
    
    def test_initialization_with_cache(self):
        """Test that fetcher initializes properly with caching enabled."""
        fetcher = MLBDataFetcher(use_cache=True)
        self.assertTrue(fetcher.use_cache)
        self.assertIsNotNone(fetcher.cache)
    
    def test_initialization_without_cache(self):
        """Test that fetcher initializes properly with caching disabled."""
        fetcher = MLBDataFetcher(use_cache=False)
        self.assertFalse(fetcher.use_cache)
        self.assertIsNone(fetcher.cache)
    
    @patch('data_fetcher.requests.Session.get')
    def test_make_request_success(self, mock_get):
        """Test successful API request."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {'test': 'data'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        fetcher = MLBDataFetcher(use_cache=False)
        result = fetcher._make_request('test/endpoint', {'param': 'value'})
        
        self.assertEqual(result, {'test': 'data'})
        mock_get.assert_called_once()
    
    @patch('data_fetcher.requests.Session.get')
    def test_make_request_error_handling(self, mock_get):
        """Test API request error handling."""
        # Mock failed API response
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        fetcher = MLBDataFetcher(use_cache=False)
        result = fetcher._make_request('test/endpoint')
        
        # Should return empty dict on error
        self.assertEqual(result, {})
    
    @patch('data_fetcher.requests.Session.get')
    def test_caching_stores_data(self, mock_get):
        """Test that successful requests are cached."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {'cached': 'data'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        fetcher = MLBDataFetcher(use_cache=True)
        
        # First call should hit the API
        result1 = fetcher._make_request('test/endpoint', {'param': 'value'})
        self.assertEqual(result1, {'cached': 'data'})
        self.assertEqual(mock_get.call_count, 1)
        
        # Second call should use cache (no additional API call)
        result2 = fetcher._make_request('test/endpoint', {'param': 'value'})
        self.assertEqual(result2, {'cached': 'data'})
        self.assertEqual(mock_get.call_count, 1)  # Still only 1 call
    
    @patch('data_fetcher.requests.Session.get')
    def test_search_players_returns_list(self, mock_get):
        """Test player search returns a list."""
        # Mock player search response
        mock_response = Mock()
        mock_response.json.return_value = {
            'people': [
                {'id': 1, 'fullName': 'Test Player'}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        fetcher = MLBDataFetcher(use_cache=False)
        result = fetcher.search_players('Test')
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['fullName'], 'Test Player')
    
    @patch('data_fetcher.requests.Session.get')
    def test_search_players_empty_result(self, mock_get):
        """Test player search with no results."""
        # Mock empty search response
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        fetcher = MLBDataFetcher(use_cache=False)
        result = fetcher.search_players('NonexistentPlayer')
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)
    
    @patch('data_fetcher.requests.Session.get')
    def test_get_teams_returns_list(self, mock_get):
        """Test getting teams returns a list."""
        # Mock teams response
        mock_response = Mock()
        mock_response.json.return_value = {
            'teams': [
                {'id': 110, 'name': 'Baltimore Orioles'},
                {'id': 147, 'name': 'New York Yankees'}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        fetcher = MLBDataFetcher(use_cache=False)
        result = fetcher.get_teams(2024)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
    
    def test_get_cache_stats_with_cache_disabled(self):
        """Test cache stats when caching is disabled."""
        fetcher = MLBDataFetcher(use_cache=False)
        stats = fetcher.get_cache_stats()
        
        self.assertIn('error', stats)
    
    def test_clear_cache_with_cache_enabled(self):
        """Test clearing cache."""
        fetcher = MLBDataFetcher(use_cache=True)
        
        # Should not raise an error
        try:
            fetcher.clear_cache()
        except Exception as e:
            self.fail(f"clear_cache raised an exception: {e}")


class TestMLBDataFetcherIntegration(unittest.TestCase):
    """Integration tests that make real API calls (marked as slow)."""
    
    @unittest.skip("Integration test - uncomment to run with real API")
    def test_real_api_search_players(self):
        """Test real API call for player search."""
        fetcher = MLBDataFetcher(use_cache=False)
        result = fetcher.search_players("Aaron Judge")
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn('fullName', result[0])
    
    @unittest.skip("Integration test - uncomment to run with real API")
    def test_real_api_get_teams(self):
        """Test real API call for getting teams."""
        fetcher = MLBDataFetcher(use_cache=False)
        result = fetcher.get_teams(2024)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 30)  # 30 MLB teams


if __name__ == '__main__':
    unittest.main()
