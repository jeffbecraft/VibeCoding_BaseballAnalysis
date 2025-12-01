"""
Test suite for comparison query scenarios.

This test suite validates that comparison queries work efficiently for:
1. Active players vs active players
2. Active players vs retired players  
3. Retired players vs retired players

Each scenario tests performance with the search_players API to ensure
the fast-path optimization works correctly.
"""

import unittest
import time
import sys
import os

# Add src and utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))

from data_fetcher import MLBDataFetcher


class TestComparisonScenarios(unittest.TestCase):
    """Test comparison queries for different player combinations."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Disable cache for accurate performance testing
        self.fetcher = MLBDataFetcher(use_cache=False)
    
    def test_active_vs_active_players(self):
        """
        Test comparison of two active players performs efficiently.
        
        Example: "Compare Aaron Judge vs Shohei Ohtani home runs"
        
        This should:
        1. Find both active players
        2. Complete quickly (< 5 seconds)
        """
        start_time = time.time()
        
        # Simulate the fast-path by searching for both active players
        judge_results = self.fetcher.search_players('Aaron Judge')
        ohtani_results = self.fetcher.search_players('Shohei Ohtani')
        
        elapsed_time = time.time() - start_time
        
        # Both players should be found
        self.assertGreater(len(judge_results), 0,
                         "Should find Aaron Judge")
        self.assertGreater(len(ohtani_results), 0,
                         "Should find Shohei Ohtani")
        
        # Should complete quickly
        self.assertLess(elapsed_time, 5.0,
                       f"Active vs active search took {elapsed_time:.2f}s, should be < 5s")
        
        print(f"\nPASS: Active vs Active - 2 player searches in {elapsed_time:.2f}s")
    
    def test_active_vs_retired_players(self):
        """
        Test comparison of active and retired players performs efficiently.
        
        Example: "Compare Aaron Judge vs Ken Griffey Jr home runs"
        
        This should:
        1. Find both players (one active, one retired)
        2. Complete quickly (< 5 seconds)
        """
        start_time = time.time()
        
        # Simulate the fast-path by searching for both players
        judge_results = self.fetcher.search_players('Aaron Judge')
        griffey_results = self.fetcher.search_players('Ken Griffey Jr')
        
        elapsed_time = time.time() - start_time
        
        # Both players should be found
        self.assertGreater(len(judge_results), 0,
                         "Should find Aaron Judge")
        self.assertGreater(len(griffey_results), 0,
                         "Should find Ken Griffey Jr")
        
        # Should complete quickly (even though one is retired)
        self.assertLess(elapsed_time, 5.0,
                       f"Active vs retired search took {elapsed_time:.2f}s, should be < 5s")
        
        print(f"\nPASS: Active vs Retired - 2 player searches in {elapsed_time:.2f}s")
    
    def test_retired_vs_retired_players(self):
        """
        Test comparison of two retired players performs efficiently.
        
        Example: "Compare Babe Ruth vs Hank Aaron home runs"
        
        This should:
        1. Find both retired players
        2. Complete quickly (< 5 seconds)
        """
        start_time = time.time()
        
        # Simulate the fast-path by searching for both players
        ruth_results = self.fetcher.search_players('Babe Ruth')
        aaron_results = self.fetcher.search_players('Hank Aaron')
        
        elapsed_time = time.time() - start_time
        
        # Both players should be found
        self.assertGreater(len(ruth_results), 0,
                         "Should find Babe Ruth")
        self.assertGreater(len(aaron_results), 0,
                         "Should find Hank Aaron")
        
        # Should complete quickly (this was the original performance issue)
        self.assertLess(elapsed_time, 5.0,
                       f"Retired vs retired search took {elapsed_time:.2f}s, should be < 5s")
        
        print(f"\nPASS: Retired vs Retired - 2 player searches in {elapsed_time:.2f}s")
    
    def test_multiple_active_players(self):
        """
        Test comparison of 3+ active players performs efficiently.
        
        Example: "Compare Aaron Judge vs Shohei Ohtani vs Mookie Betts home runs"
        
        This should find all players and complete quickly.
        """
        start_time = time.time()
        
        judge_results = self.fetcher.search_players('Aaron Judge')
        ohtani_results = self.fetcher.search_players('Shohei Ohtani')
        betts_results = self.fetcher.search_players('Mookie Betts')
        
        elapsed_time = time.time() - start_time
        
        # All should be found
        self.assertGreater(len(judge_results), 0)
        self.assertGreater(len(ohtani_results), 0)
        self.assertGreater(len(betts_results), 0)
        
        # Should still be reasonably fast
        self.assertLess(elapsed_time, 10.0,
                       f"3 active player searches took {elapsed_time:.2f}s, should be < 10s")
        
        print(f"\nPASS: Multiple Active Players - 3 player searches in {elapsed_time:.2f}s")
    
    def test_multiple_retired_players(self):
        """
        Test comparison of 3+ retired players performs efficiently.
        
        Example: "Compare Babe Ruth vs Hank Aaron vs Willie Mays home runs"
        
        This should work efficiently for multiple retired players.
        """
        start_time = time.time()
        
        ruth_results = self.fetcher.search_players('Babe Ruth')
        aaron_results = self.fetcher.search_players('Hank Aaron')
        mays_results = self.fetcher.search_players('Willie Mays')
        
        elapsed_time = time.time() - start_time
        
        # All should be found
        self.assertGreater(len(ruth_results), 0)
        self.assertGreater(len(aaron_results), 0)
        self.assertGreater(len(mays_results), 0)
        
        # Should still be reasonably fast
        self.assertLess(elapsed_time, 10.0,
                       f"3 retired player searches took {elapsed_time:.2f}s, should be < 10s")
        
        print(f"\nPASS: Multiple Retired Players - 3 player searches in {elapsed_time:.2f}s")
    
    def test_mixed_active_and_retired(self):
        """
        Test comparison with mix of active and retired players performs efficiently.
        
        Example: "Compare Aaron Judge vs Babe Ruth vs Shohei Ohtani home runs"
        """
        start_time = time.time()
        
        judge_results = self.fetcher.search_players('Aaron Judge')
        ruth_results = self.fetcher.search_players('Babe Ruth')
        ohtani_results = self.fetcher.search_players('Shohei Ohtani')
        
        elapsed_time = time.time() - start_time
        
        # All should be found
        self.assertGreater(len(judge_results), 0)
        self.assertGreater(len(ruth_results), 0)
        self.assertGreater(len(ohtani_results), 0)
        
        # Should still be reasonably fast
        self.assertLess(elapsed_time, 10.0,
                       f"3 mixed player searches took {elapsed_time:.2f}s, should be < 10s")
        
        print(f"\nPASS: Mixed Active/Retired - 3 player searches in {elapsed_time:.2f}s")


if __name__ == '__main__':
    unittest.main(verbosity=2)
