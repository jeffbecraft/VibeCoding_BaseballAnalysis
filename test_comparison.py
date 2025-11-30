"""
Test comparison query functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_fetcher import MLBDataFetcher
from data_processor import MLBDataProcessor

def test_comparison_query():
    """Test that comparison queries return ranked results."""
    print("\n" + "="*60)
    print("Testing Comparison Queries")
    print("="*60)
    
    fetcher = MLBDataFetcher(use_cache=True)
    processor = MLBDataProcessor()
    
    # Get home run leaders for 2024
    print("\n1. Fetching 2024 home run leaders...")
    leaders_data = fetcher.get_stats_leaders(
        'homeRuns',
        season=2024,
        limit=100,
        stat_group='hitting',
        include_all=True
    )
    
    if not leaders_data:
        print("   ✗ No leaders data found")
        return False
    
    print(f"   ✓ Retrieved {len(leaders_data)} players")
    
    # Process into DataFrame
    leaders_df = processor.extract_stats_leaders(leaders_data)
    
    if leaders_df.empty:
        print("   ✗ Could not create DataFrame")
        return False
    
    print(f"   ✓ Created DataFrame with {len(leaders_df)} rows")
    
    # Find specific players
    print("\n2. Finding Aaron Judge and Juan Soto in rankings...")
    
    judge_row = leaders_df[leaders_df['playerName'].str.contains('Judge', case=False, na=False)]
    soto_row = leaders_df[leaders_df['playerName'].str.contains('Soto', case=False, na=False)]
    
    if not judge_row.empty:
        judge_rank = judge_row.iloc[0]['rank']
        judge_hrs = judge_row.iloc[0]['value']
        print(f"   ✓ Aaron Judge: Rank #{judge_rank} with {judge_hrs} HR")
    else:
        print("   ⚠ Aaron Judge not found in rankings")
    
    if not soto_row.empty:
        soto_rank = soto_row.iloc[0]['rank']
        soto_hrs = soto_row.iloc[0]['value']
        print(f"   ✓ Juan Soto: Rank #{soto_rank} with {soto_hrs} HR")
    else:
        print("   ⚠ Juan Soto not found in rankings")
    
    # Show top 10 for context
    print("\n3. Top 10 Home Run Leaders (2024):")
    print(leaders_df[['rank', 'playerName', 'team', 'value']].head(10).to_string(index=False))
    
    print("\n✓ Comparison query test PASSED!")
    return True


if __name__ == "__main__":
    try:
        success = test_comparison_query()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
