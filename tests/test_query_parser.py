"""
Test Suite for GUI Query Parser

Tests natural language query parsing and parameter extraction.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# Add src and utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))

from mlb_gui import MLBQueryGUI


class TestQueryParser(unittest.TestCase):
    """Test cases for query parsing logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock root window
        self.mock_root = Mock()
        self.mock_root.title = Mock()
        self.mock_root.geometry = Mock()
        
        # Patch tkinter components to avoid GUI initialization
        with patch('mlb_gui.tk.Label'), \
             patch('mlb_gui.tk.Entry'), \
             patch('mlb_gui.tk.Button'), \
             patch('mlb_gui.tk.Frame'), \
             patch('mlb_gui.tk.LabelFrame'), \
             patch('mlb_gui.tk.StringVar') as mock_stringvar, \
             patch('mlb_gui.scrolledtext.ScrolledText'):
            
            # Mock StringVar to return a mock with set/get methods
            mock_var = Mock()
            mock_stringvar.return_value = mock_var
            
            self.gui = MLBQueryGUI(self.mock_root)
    
    def test_parse_simple_stat_query(self):
        """Test parsing a simple statistic query."""
        result = self.gui.parse_query("Top 10 home runs 2024")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['stat_type'], 'homeRuns')
        self.assertEqual(result['year'], 2024)
        self.assertEqual(result['limit'], 10)
        self.assertEqual(result['query_type'], 'leaders')
    
    def test_parse_player_stat_query(self):
        """Test parsing a player-specific stat query."""
        result = self.gui.parse_query("What was Ohtani's batting average in 2024?")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['stat_type'], 'avg')
        self.assertEqual(result['player_name'], 'Ohtani')
        self.assertEqual(result['year'], 2024)
        self.assertEqual(result['query_type'], 'player_stat')
    
    def test_parse_player_rank_query(self):
        """Test parsing a player ranking query."""
        result = self.gui.parse_query("Rank Yamamoto's ERA in 2025")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['stat_type'], 'era')
        self.assertEqual(result['player_name'], 'Yamamoto')
        self.assertEqual(result['year'], 2025)
        self.assertEqual(result['query_type'], 'rank')
    
    def test_parse_team_filter_query(self):
        """Test parsing a query with team filter."""
        result = self.gui.parse_query("Orioles home run leaders 2024")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['stat_type'], 'homeRuns')
        self.assertEqual(result['team_name'], 'Orioles')
        self.assertEqual(result['team_id'], 110)
    
    def test_parse_league_filter_query(self):
        """Test parsing a query with league filter."""
        result = self.gui.parse_query("American League ERA leaders 2024")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['stat_type'], 'era')
        self.assertEqual(result['league_name'], 'American League')
        self.assertEqual(result['league_id'], 103)
    
    def test_parse_team_ranking_query(self):
        """Test parsing a team ranking query."""
        result = self.gui.parse_query("Which team had the lowest ERA in 2024?")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['stat_type'], 'era')
        self.assertEqual(result['query_type'], 'team_rank')
    
    def test_parse_year_extraction(self):
        """Test year extraction from queries."""
        result1 = self.gui.parse_query("Home runs in 2023")
        self.assertEqual(result1['year'], 2023)
        
        result2 = self.gui.parse_query("Strikeouts 2022")
        self.assertEqual(result2['year'], 2022)
    
    def test_parse_default_year(self):
        """Test default year when not specified."""
        result = self.gui.parse_query("Top home runs")
        
        # Should use current season
        self.assertIsNotNone(result['year'])
        self.assertGreaterEqual(result['year'], 2024)
    
    def test_parse_pitching_stats(self):
        """Test parsing pitching statistics."""
        pitching_queries = [
            ("ERA leaders", 'era'),
            ("Best strikeouts", 'strikeouts'),
            ("Top wins", 'wins'),
            ("WHIP leaders", 'whip')
        ]
        
        for query, expected_stat in pitching_queries:
            result = self.gui.parse_query(query)
            self.assertEqual(result['stat_type'], expected_stat)
            self.assertEqual(result['stat_group'], 'pitching')
    
    def test_parse_hitting_stats(self):
        """Test parsing hitting statistics."""
        hitting_queries = [
            ("Home runs leaders", 'homeRuns'),
            ("RBI leaders", 'rbi'),
            ("Batting average", 'avg'),
            ("Stolen bases", 'stolenBases')
        ]
        
        for query, expected_stat in hitting_queries:
            result = self.gui.parse_query(query)
            self.assertEqual(result['stat_type'], expected_stat)
            self.assertEqual(result['stat_group'], 'hitting')
    
    def test_parse_invalid_query(self):
        """Test parsing invalid query with no recognizable stat."""
        result = self.gui.parse_query("Tell me about baseball")
        
        # Should return None for invalid query
        self.assertIsNone(result)
    
    def test_parse_full_player_name(self):
        """Test parsing full player names."""
        result = self.gui.parse_query("Aaron Judge home runs")
        
        self.assertEqual(result['player_name'], 'Aaron Judge')
    
    def test_parse_player_possessive(self):
        """Test parsing player names with possessive."""
        result = self.gui.parse_query("Ohtani's ERA in 2024")
        
        self.assertEqual(result['player_name'], 'Ohtani')
    
    def test_parse_excludes_common_words(self):
        """Test that common words aren't parsed as player names."""
        result = self.gui.parse_query("What was the top ERA?")
        
        # "What" should not be detected as player name
        self.assertIsNone(result['player_name'])
    
    def test_get_stat_display_name(self):
        """Test getting human-readable stat names."""
        self.assertEqual(self.gui.get_stat_display_name('homeRuns'), 'Home Runs')
        self.assertEqual(self.gui.get_stat_display_name('era'), 'Era')
        self.assertEqual(self.gui.get_stat_display_name('avg'), 'Batting Average')


class TestQueryTypeDetection(unittest.TestCase):
    """Test cases for query type detection."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_root = Mock()
        self.mock_root.title = Mock()
        self.mock_root.geometry = Mock()
        
        with patch('mlb_gui.tk.Label'), \
             patch('mlb_gui.tk.Entry'), \
             patch('mlb_gui.tk.Button'), \
             patch('mlb_gui.tk.Frame'), \
             patch('mlb_gui.tk.LabelFrame'), \
             patch('mlb_gui.tk.StringVar') as mock_stringvar, \
             patch('mlb_gui.scrolledtext.ScrolledText'):
            
            # Mock StringVar to return a mock with set/get methods
            mock_var = Mock()
            mock_stringvar.return_value = mock_var
            
            self.gui = MLBQueryGUI(self.mock_root)
    
    def test_detect_ranking_keywords(self):
        """Test detection of ranking keywords."""
        ranking_queries = [
            "Rank Ohtani's ERA",
            "Top 10 home runs",
            "Best strikeouts",
            "ERA leaders",
            "Worst batting average"
        ]
        
        for query in ranking_queries:
            result = self.gui.parse_query(query)
            if result['player_name']:
                self.assertEqual(result['query_type'], 'rank')
    
    def test_detect_simple_stat_query(self):
        """Test detection of simple stat queries without ranking."""
        result = self.gui.parse_query("What was Ohtani's ERA in 2024?")
        
        self.assertEqual(result['query_type'], 'player_stat')
    
    def test_detect_team_ranking(self):
        """Test detection of team ranking queries."""
        team_queries = [
            "Which team had the most home runs?",
            "Rank teams by ERA",
            "What team had the best strikeouts?"
        ]
        
        for query in team_queries:
            result = self.gui.parse_query(query)
            self.assertEqual(result['query_type'], 'team_rank')


if __name__ == '__main__':
    unittest.main()
