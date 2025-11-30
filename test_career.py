"""
Test script for career statistics functionality
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_fetcher import MLBDataFetcher
from data_processor import MLBDataProcessor

def test_player_career_stats():
    """Test fetching and processing player career stats."""
    print("\n" + "="*60)
    print("Testing Player Career Stats")
    print("="*60)
    
    fetcher = MLBDataFetcher(use_cache=True)
    processor = MLBDataProcessor()
    
    # Search for Aaron Judge
    print("\n1. Searching for Aaron Judge...")
    players = fetcher.search_players("Aaron Judge")
    if not players:
        print("   ERROR: Player not found!")
        return False
    
    player = players[0]
    player_id = player.get('id')
    player_name = player.get('fullName')
    print(f"   Found: {player_name} (ID: {player_id})")
    
    # Get career stats
    print("\n2. Fetching career hitting stats...")
    career_data = fetcher.get_player_career_stats(player_id, 'hitting')
    if not career_data:
        print("   ERROR: No career data found!")
        return False
    
    print(f"   Retrieved {len(career_data)} seasons of data")
    
    # Show first few seasons
    print("\n   Sample seasons:")
    for season_data in career_data[:3]:
        season = season_data.get('season')
        team = season_data.get('team')
        hr = season_data.get('stat', {}).get('homeRuns', 0)
        print(f"     {season} ({team}): {hr} HR")
    
    # Aggregate career stats
    print("\n3. Aggregating career statistics...")
    career_totals = processor.aggregate_career_stats(career_data, 'hitting')
    
    if not career_totals:
        print("   ERROR: Could not aggregate career stats!")
        return False
    
    print(f"   Seasons: {career_totals['seasons']}")
    print(f"   Career Home Runs: {career_totals['totals'].get('homeRuns', 0)}")
    print(f"   Career Hits: {career_totals['totals'].get('hits', 0)}")
    print(f"   Career AVG: {career_totals['career_rates'].get('avg', '.000')}")
    print(f"   Career OPS: {career_totals['career_rates'].get('ops', '.000')}")
    
    # Create career DataFrame
    print("\n4. Creating career DataFrame...")
    career_df = processor.create_career_dataframe(career_data)
    
    if career_df.empty:
        print("   ERROR: Could not create DataFrame!")
        return False
    
    print(f"   DataFrame created with {len(career_df)} rows")
    print("\n   First few rows:")
    print(career_df[['season', 'team', 'gamesPlayed', 'homeRuns', 'hits']].head(3))
    
    print("\n✓ Player career stats test PASSED!")
    return True


def test_team_career_stats():
    """Test fetching team career stats."""
    print("\n" + "="*60)
    print("Testing Team Career Stats")
    print("="*60)
    
    fetcher = MLBDataFetcher(use_cache=True)
    
    # Get Yankees team ID (147)
    team_id = 147
    team_name = "New York Yankees"
    
    print(f"\n1. Fetching {team_name} career stats (last 5 years)...")
    
    from datetime import datetime
    current_year = datetime.now().year
    start_year = current_year - 4
    
    career_data = fetcher.get_team_career_stats(
        team_id,
        'hitting',
        start_year,
        current_year
    )
    
    if not career_data:
        print("   ERROR: No team career data found!")
        return False
    
    print(f"   Retrieved {len(career_data)} seasons of data")
    
    # Show sample data
    print("\n   Sample seasons:")
    for season_data in career_data[:3]:
        season = season_data.get('season')
        hr = season_data.get('stat', {}).get('homeRuns', 0)
        avg = season_data.get('stat', {}).get('avg', '.000')
        print(f"     {season}: {hr} HR, {avg} AVG")
    
    print("\n✓ Team career stats test PASSED!")
    return True


def test_career_comparison():
    """Test comparing two players' careers."""
    print("\n" + "="*60)
    print("Testing Career Comparison")
    print("="*60)
    
    fetcher = MLBDataFetcher(use_cache=True)
    processor = MLBDataProcessor()
    
    # Get two players
    print("\n1. Searching for players...")
    judge_results = fetcher.search_players("Aaron Judge")
    soto_results = fetcher.search_players("Juan Soto")
    
    if not judge_results or not soto_results:
        print("   ERROR: Could not find one or both players!")
        return False
    
    judge_name = judge_results[0].get('fullName')
    soto_name = soto_results[0].get('fullName')
    print(f"   Found: {judge_name} and {soto_name}")
    
    # Get career data
    print("\n2. Fetching career data...")
    judge_career = fetcher.get_player_career_stats(judge_results[0]['id'], 'hitting')
    soto_career = fetcher.get_player_career_stats(soto_results[0]['id'], 'hitting')
    
    if not judge_career or not soto_career:
        print("   ERROR: Could not retrieve career data!")
        return False
    
    print(f"   {judge_name}: {len(judge_career)} seasons")
    print(f"   {soto_name}: {len(soto_career)} seasons")
    
    # Compare careers
    print("\n3. Comparing careers...")
    comparison_df = processor.compare_player_careers(judge_career, soto_career, 'hitting')
    
    if comparison_df.empty:
        print("   ERROR: Could not create comparison!")
        return False
    
    print(f"   Comparison created with {len(comparison_df)} statistics")
    print("\n   Sample comparison:")
    print(comparison_df.head(10))
    
    print("\n✓ Career comparison test PASSED!")
    return True


def main():
    """Run all career tests."""
    print("\n" + "="*60)
    print("CAREER STATISTICS FUNCTIONALITY TEST SUITE")
    print("="*60)
    
    tests = [
        test_player_career_stats,
        test_team_career_stats,
        test_career_comparison
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests PASSED!")
        return 0
    else:
        print("\n✗ Some tests FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
