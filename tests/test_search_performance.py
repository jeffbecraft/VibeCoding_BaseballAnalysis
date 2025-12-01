"""
Test suite for player search performance optimization.

This test verifies that the search_players method uses the efficient
MLB API /people/search endpoint instead of iterating through seasons.

Background:
-----------
The original implementation searched for retired players by iterating
through up to 30 historical seasons, making 1 API call per season until
it found the player. For comparison queries with retired players:

Before optimization:
- Ken Griffey Jr. (retired 2010): 16 API calls
- Albert Pujols (retired 2022): 4 API calls
- Total: 20 API calls, 23+ seconds

After optimization:
- Ken Griffey Jr.: 1 API call
- Albert Pujols: 1 API call
- Total: 2 API calls, <3 seconds

The optimization uses MLB's /people/search endpoint which searches
across ALL players (active and retired) in a single call.
"""

import unittest
import time
from unittest.mock import patch, Mock
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_fetcher import MLBDataFetcher


class TestSearchPerformance(unittest.TestCase):
    """Test that player search uses efficient API endpoints."""
    
    def test_search_uses_direct_endpoint(self):
        """
        Test that search_players uses /people/search endpoint.
        
        This is the key performance optimization. The method should use
        the direct search endpoint, not iterate through seasons.
        """
        fetcher = MLBDataFetcher(use_cache=False)  # Disable cache for accurate testing
        
        # Mock the _make_request method to track which endpoints are called
        original_make_request = fetcher._make_request
        endpoints_called = []
        
        def mock_make_request(endpoint, params=None):
            """Track which endpoints are called."""
            endpoints_called.append(endpoint)
            return original_make_request(endpoint, params)
        
        with patch.object(fetcher, '_make_request', side_effect=mock_make_request):
            # Search for a retired player
            results = fetcher.search_players('Ken Griffey Jr')
            
            # Should have called people/search endpoint
            self.assertIn('people/search', endpoints_called,
                         "Should use efficient /people/search endpoint")
            
            # Should NOT have called sports/1/players multiple times
            sports_player_calls = [e for e in endpoints_called if e == 'sports/1/players']
            self.assertEqual(len(sports_player_calls), 0,
                           "Should not iterate through seasons (old slow method)")
            
            # Should have found the player
            self.assertGreater(len(results), 0,
                             "Should find retired player Ken Griffey Jr")
    
    def test_comparison_query_performance(self):
        """
        Test that comparing two retired players is fast.
        
        This simulates a real-world comparison query like:
        "Who hit more home runs? Ken Griffey Jr or Albert Pujols?"
        
        The search should take < 5 seconds for two retired players.
        """
        fetcher = MLBDataFetcher(use_cache=False)  # Disable cache for accurate testing
        
        start_time = time.time()
        
        # Search for two retired players (typical comparison query)
        griffey_results = fetcher.search_players('Ken Griffey Jr')
        pujols_results = fetcher.search_players('Albert Pujols')
        
        elapsed_time = time.time() - start_time
        
        # Both players should be found
        self.assertGreater(len(griffey_results), 0,
                         "Should find Ken Griffey Jr")
        self.assertGreater(len(pujols_results), 0,
                         "Should find Albert Pujols")
        
        # Should be fast (< 5 seconds for 2 searches)
        # This is a generous limit; actual performance is usually < 3 seconds
        self.assertLess(elapsed_time, 5.0,
                       f"Searching 2 retired players took {elapsed_time:.2f}s, should be < 5s")
        
        print(f"\n✓ Performance test passed: 2 player searches in {elapsed_time:.2f}s")
    
    def test_search_finds_active_players(self):
        """
        Test that the optimized search still finds active players.
        
        The new /people/search endpoint should work for both active
        and retired players.
        """
        fetcher = MLBDataFetcher()
        
        # Search for an active player (as of 2024 season)
        results = fetcher.search_players('Aaron Judge')
        
        # Should find the player
        self.assertGreater(len(results), 0,
                         "Should find active player Aaron Judge")
        
        # Verify it's the right player
        player = results[0]
        self.assertIn('Judge', player.get('fullName', ''),
                     "Found player should be Aaron Judge")
    
    def test_search_finds_retired_players(self):
        """
        Test that the optimized search finds retired players.
        
        The /people/search endpoint should find players who are no
        longer active.
        """
        fetcher = MLBDataFetcher()
        
        # Search for a retired player
        results = fetcher.search_players('Babe Ruth')
        
        # Should find the player
        self.assertGreater(len(results), 0,
                         "Should find retired player Babe Ruth")
        
        # Verify it's the right player
        player = results[0]
        self.assertIn('Ruth', player.get('fullName', ''),
                     "Found player should be Babe Ruth")


def run_tests():
    """Run all search performance tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSearchPerformance)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    """
    Run tests when this file is executed directly.
    
    Usage:
        python -m tests.test_search_performance
    """
    success = run_tests()
    sys.exit(0 if success else 1)
