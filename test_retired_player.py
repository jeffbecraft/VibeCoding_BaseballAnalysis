"""
Quick test to verify we can find retired players
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_fetcher import MLBDataFetcher
from data_processor import MLBDataProcessor

fetcher = MLBDataFetcher(use_cache=True)
processor = MLBDataProcessor()

print("Searching for Derek Jeter...")
players = fetcher.search_players("Derek Jeter")

if players:
    player = players[0]
    print(f"✓ Found: {player.get('fullName')} (ID: {player.get('id')})")
    if 'lastSeasonFound' in player:
        print(f"  Last season found: {player['lastSeasonFound']}")
    
    # Get career stats
    print("\nFetching career stats...")
    career_data = fetcher.get_player_career_stats(player['id'], 'hitting')
    
    if career_data:
        print(f"✓ Retrieved {len(career_data)} seasons of data")
        
        # Aggregate
        career_totals = processor.aggregate_career_stats(career_data, 'hitting')
        print(f"\nCareer Summary:")
        print(f"  Seasons: {career_totals['seasons']}")
        print(f"  Hits: {career_totals['totals'].get('hits', 0)}")
        print(f"  Home Runs: {career_totals['totals'].get('homeRuns', 0)}")
        print(f"  AVG: {career_totals['career_rates'].get('avg', '.000')}")
    else:
        print("✗ No career data found")
else:
    print("✗ Player not found!")
