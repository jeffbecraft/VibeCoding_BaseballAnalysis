"""
Test that defensive coding improvements work in AI-generated code.
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data_fetcher import MLBDataFetcher
from src.data_processor import MLBDataProcessor
from src.ai_query_handler import AIQueryHandler


class TestAIDefensiveCoding(unittest.TestCase):
    """Test that AI generates code with defensive patterns."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.fetcher = MLBDataFetcher()
        cls.processor = MLBDataProcessor()
        cls.ai_handler = AIQueryHandler(cls.fetcher, cls.processor)
    
    def test_defensive_coding_patterns(self):
        """Test that defensive coding patterns are used in AI-generated code."""
        # Skip if AI not available
        if not self.ai_handler.is_available():
            self.skipTest("AI not available")
        
        # Test a comparison query
        result = self.ai_handler.handle_query_with_retry(
            "Who hit more home runs in 2024? Aaron Judge or Juan Soto?",
            2024
        )
        
        # Verify success
        self.assertTrue(result.get('success'), "Query should succeed with defensive coding")
        
        # Verify answer exists
        self.assertIsNotNone(result.get('answer'), "Should return an answer")
        
        # Check if code was generated (not just cached)
        generated_code = result.get('generated_code', '')
        if generated_code:
            # Verify defensive patterns are present (at least some of them)
            has_defensive_patterns = (
                'get(' in generated_code or
                'len(' in generated_code or
                'if not' in generated_code or
                '.empty' in generated_code
            )
            self.assertTrue(has_defensive_patterns, 
                          "Generated code should use defensive patterns like .get(), len(), or .empty checks")


if __name__ == "__main__":
    unittest.main()
