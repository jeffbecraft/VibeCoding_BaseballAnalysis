"""Test performance of comparing two active players."""
import time
from src.data_fetcher import MLBDataFetcher

def test_active_comparison():
    """Test comparing Gunnar Henderson vs Anthony Santander."""
    df = MLBDataFetcher(use_cache=False)
    
    total_start = time.time()
    
    # Search for first player
    s1 = time.time()
    r1 = df.search_players('Gunnar Henderson')
    search1_time = time.time() - s1
    print(f'Search Gunnar Henderson: {search1_time:.2f}s, found {len(r1)} player(s)')
    
    # Search for second player
    s2 = time.time()
    r2 = df.search_players('Anthony Santander')
    search2_time = time.time() - s2
    print(f'Search Anthony Santander: {search2_time:.2f}s, found {len(r2)} player(s)')
    
    # Get stats for first player
    if r1:
        s3 = time.time()
        st1 = df.get_player_season_stats(r1[0]['id'], 2024)
        stats1_time = time.time() - s3
        print(f'Stats for Henderson: {stats1_time:.2f}s')
        
    # Get stats for second player
    if r2:
        s4 = time.time()
        st2 = df.get_player_season_stats(r2[0]['id'], 2024)
        stats2_time = time.time() - s4
        print(f'Stats for Santander: {stats2_time:.2f}s')
    
    total_time = time.time() - total_start
    print(f'\n🎯 TOTAL TIME: {total_time:.2f}s')
    print(f'   Search time: {search1_time + search2_time:.2f}s')
    if r1 and r2:
        print(f'   Stats time: {stats1_time + stats2_time:.2f}s')

if __name__ == '__main__':
    test_active_comparison()
