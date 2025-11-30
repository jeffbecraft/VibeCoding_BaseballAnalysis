"""
Test Suite for MLBDataProcessor

Tests data processing, transformation, and extraction functions.
"""

import unittest
import sys
import os
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_processor import MLBDataProcessor


class TestMLBDataProcessor(unittest.TestCase):
    """Test cases for MLBDataProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = MLBDataProcessor()
    
    def test_initialization(self):
        """Test processor initializes correctly."""
        self.assertIsInstance(self.processor, MLBDataProcessor)
    
    def test_extract_stats_leaders_empty_data(self):
        """Test extracting stats leaders with empty data."""
        result = self.processor.extract_stats_leaders([])
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)
    
    def test_extract_stats_leaders_valid_data(self):
        """Test extracting stats leaders with valid data."""
        test_data = [
            {
                'rank': 1,
                'person': {'id': 123, 'fullName': 'Player One'},
                'team': {'id': 110, 'name': 'Orioles'},
                'value': 50
            },
            {
                'rank': 2,
                'person': {'id': 456, 'fullName': 'Player Two'},
                'team': {'id': 147, 'name': 'Yankees'},
                'value': 48
            }
        ]
        
        result = self.processor.extract_stats_leaders(test_data)
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn('rank', result.columns)
        self.assertIn('playerName', result.columns)
        self.assertIn('value', result.columns)
        self.assertEqual(result.iloc[0]['playerName'], 'Player One')
        self.assertEqual(result.iloc[0]['value'], 50)
    
    def test_extract_stats_leaders_missing_fields(self):
        """Test extracting stats leaders with missing fields."""
        test_data = [
            {
                'rank': 1,
                'person': {'id': 123},  # Missing fullName
                'team': {},  # Missing name and id
                'value': 50
            }
        ]
        
        result = self.processor.extract_stats_leaders(test_data)
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['team'], 'N/A')
    
    def test_extract_team_stats_empty_data(self):
        """Test extracting team stats with empty data."""
        result = self.processor.extract_team_stats([], 'homeRuns')
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)
    
    def test_extract_team_stats_valid_data(self):
        """Test extracting team stats with valid data."""
        test_data = [
            {
                'team_id': 110,
                'team_name': 'Orioles',
                'stat': {'homeRuns': 240, 'runs': 800}
            },
            {
                'team_id': 147,
                'team_name': 'Yankees',
                'stat': {'homeRuns': 250, 'runs': 850}
            }
        ]
        
        result = self.processor.extract_team_stats(test_data, 'homeRuns')
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn('rank', result.columns)
        self.assertIn('team_name', result.columns)
        self.assertIn('value', result.columns)
        
        # Should be sorted by value descending (higher home runs first)
        self.assertEqual(result.iloc[0]['team_name'], 'Yankees')
        self.assertEqual(result.iloc[0]['rank'], 1)
    
    def test_extract_team_stats_era_sorting(self):
        """Test team stats sorting for ERA (ascending)."""
        test_data = [
            {
                'team_id': 110,
                'team_name': 'Team A',
                'stat': {'era': 4.50}
            },
            {
                'team_id': 147,
                'team_name': 'Team B',
                'stat': {'era': 3.25}
            }
        ]
        
        result = self.processor.extract_team_stats(test_data, 'era')
        
        # Lower ERA should rank first
        self.assertEqual(result.iloc[0]['team_name'], 'Team B')
        self.assertEqual(result.iloc[0]['rank'], 1)
    
    def test_extract_team_stats_missing_stat(self):
        """Test team stats when some teams don't have the stat."""
        test_data = [
            {
                'team_id': 110,
                'team_name': 'Team A',
                'stat': {'homeRuns': 240}
            },
            {
                'team_id': 147,
                'team_name': 'Team B',
                'stat': {}  # Missing homeRuns
            }
        ]
        
        result = self.processor.extract_team_stats(test_data, 'homeRuns')
        
        # Should only include Team A
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['team_name'], 'Team A')
    
    def test_filter_by_season_with_valid_data(self):
        """Test filtering data by season."""
        test_df = pd.DataFrame({
            'season': [2023, 2024, 2023, 2024],
            'value': [10, 20, 30, 40]
        })
        
        result = self.processor.filter_by_season(test_df, 2024)
        
        self.assertEqual(len(result), 2)
        self.assertTrue(all(result['season'] == 2024))
    
    def test_filter_by_season_empty_result(self):
        """Test filtering by season with no matches."""
        test_df = pd.DataFrame({
            'season': [2023, 2023],
            'value': [10, 20]
        })
        
        result = self.processor.filter_by_season(test_df, 2025)
        
        self.assertEqual(len(result), 0)


if __name__ == '__main__':
    unittest.main()
