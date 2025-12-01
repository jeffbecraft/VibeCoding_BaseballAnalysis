"""Test the comparison fix with real API calls."""
from src.data_fetcher import MLBDataFetcher

def test_stat_extraction():
    """Test extracting stats from the nested response."""
    fetcher = MLBDataFetcher(use_cache=False)
    
    print("Testing stat extraction for Gunnar Henderson...")
    player_results = fetcher.search_players("Gunnar Henderson")
    
    if player_results:
        player_id = player_results[0]['id']
        print(f"Found player ID: {player_id}")
        
        stats_response = fetcher.get_player_season_stats(player_id, 2024)
        
        if stats_response and 'stats' in stats_response:
            print(f"\nStats groups found: {len(stats_response['stats'])}")
            
            for i, stat_group in enumerate(stats_response['stats']):
                group_name = stat_group.get('group', {}).get('displayName', 'Unknown')
                splits = stat_group.get('splits', [])
                print(f"\nGroup {i}: {group_name}")
                print(f"  Splits: {len(splits)}")
                
                if splits:
                    stat_dict = splits[0].get('stat', {})
                    print(f"  Available stats: {list(stat_dict.keys())[:10]}...")
                    
                    # Try to get home runs
                    hr = stat_dict.get('homeRuns')
                    if hr is not None:
                        print(f"  ✓ Home Runs: {hr}")

if __name__ == '__main__':
    test_stat_extraction()