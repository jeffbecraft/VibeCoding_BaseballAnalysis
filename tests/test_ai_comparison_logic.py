"""
Test the fixed AI comparison logic for "who had MORE" queries.
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data_fetcher import MLBDataFetcher
from src.data_processor import MLBDataProcessor
from src.ai_query_handler import AIQueryHandler


class TestAIComparisonLogic(unittest.TestCase):
    """Test AI comparison logic for 'who had more' queries."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.fetcher = MLBDataFetcher(use_cache=True)
        cls.processor = MLBDataProcessor()
        cls.ai_handler = AIQueryHandler(cls.fetcher, cls.processor)
    
    def test_comparison_logic(self):
        """Test that AI generates logically correct comparison answers."""
        # Skip if AI not available
        if not self.ai_handler.is_available():
            self.skipTest("AI not available")
        
        question = "Who had more stolen bases in 2025, Gunnar Henderson or Bobby Witt Jr.?"
        season = 2025
        
        # Execute query
        result = self.ai_handler.handle_query_with_retry(question=question, season=season)
        
        # Verify success
        self.assertTrue(result.get('success'), "Query should succeed")
        
        # Get data
        data = result.get('data', {})
        self.assertIn('henderson_stolen_bases', data, "Should have Henderson's stolen bases")
        self.assertIn('witt_stolen_bases', data, "Should have Witt's stolen bases")
        
        henderson_sb = data.get('henderson_stolen_bases', 0)
        witt_sb = data.get('witt_stolen_bases', 0)
        answer = result.get('answer', '')
        
        # Determine expected winner
        if witt_sb > henderson_sb:
            expected_winner = "Bobby Witt Jr."
            max_sb = witt_sb
        else:
            expected_winner = "Gunnar Henderson"
            max_sb = henderson_sb
        
        # Verify answer mentions winner with correct value
        self.assertIn(expected_winner, answer, f"Answer should mention winner: {expected_winner}")
        self.assertIn(str(max_sb), answer, f"Answer should mention winner's value: {max_sb}")


if __name__ == "__main__":
    unittest.main()

