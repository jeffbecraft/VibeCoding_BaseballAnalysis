"""
Basic functionality tests for MLB Statistics App
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from data_fetcher import MLBDataFetcher
from data_processor import MLBDataProcessor
from ai_query_handler import AIQueryHandler

def test_data_fetcher():
    """Test basic data fetching."""
    print("\n" + "="*70)
    print("TEST 1: Data Fetcher")
    print("="*70)
    
    fetcher = MLBDataFetcher(use_cache=True)
    
    # Test 1: Get teams
    print("\n1. Testing get_teams()...")
    teams = fetcher.get_teams()
    print(f"✅ Found {len(teams)} teams")
    if teams:
        print(f"   Example: {teams[0]['name']}")
    
    # Test 2: Get stats leaders
    print("\n2. Testing get_stats_leaders('homeRuns', 2024)...")
    leaders = fetcher.get_stats_leaders('homeRuns', 2024, 5, 'hitting')
    print(f"✅ Found {len(leaders)} home run leaders")
    if leaders:
        for i, player in enumerate(leaders[:3], 1):
            print(f"   {i}. {player.get('name', 'Unknown')} - {player.get('value', 0)} HR")
    
    # Test 3: Search players
    print("\n3. Testing search_players('Shohei Ohtani')...")
    players = fetcher.search_players('Shohei Ohtani')
    print(f"✅ Found {len(players)} matching players")
    if players:
        print(f"   Example: {players[0].get('name', 'Unknown')}")
    
    return True

def test_data_processor():
    """Test data processing."""
    print("\n" + "="*70)
    print("TEST 2: Data Processor")
    print("="*70)
    
    processor = MLBDataProcessor()
    fetcher = MLBDataFetcher(use_cache=True)
    
    # Test processing stats leaders
    print("\n1. Testing extract_stats_leaders()...")
    raw_data = fetcher.get_stats_leaders('homeRuns', 2024, 10, 'hitting')
    processed = processor.extract_stats_leaders(raw_data)
    print(f"✅ Processed {len(processed)} leaders")
    if len(processed) > 0:
        first = processed.iloc[0] if hasattr(processed, 'iloc') else processed[0]
        if hasattr(first, 'get'):
            print(f"   Top player: {first.get('name', 'Unknown')} - {first.get('value', 0)} HR")
        else:
            print(f"   Data type: {type(processed)}")
    
    return True

def test_ai_handler():
    """Test AI handler initialization."""
    print("\n" + "="*70)
    print("TEST 3: AI Query Handler")
    print("="*70)
    
    fetcher = MLBDataFetcher(use_cache=True)
    processor = MLBDataProcessor()
    
    print("\n1. Initializing AI handler...")
    ai_handler = AIQueryHandler(fetcher, processor)
    
    print(f"   Available: {ai_handler.is_available()}")
    
    if ai_handler.is_available():
        provider_info = ai_handler.get_provider_info()
        print(f"   Provider: {provider_info['provider']}")
        print(f"   Model: {provider_info['model']}")
        print(f"   Cost: {provider_info['cost']}")
        print(f"   Location: {provider_info['location']}")
        
        # Test connection
        print("\n2. Testing AI connection...")
        test_result = ai_handler.test_connection()
        if test_result['success']:
            print(f"   ✅ {test_result['message']}")
            if test_result.get('provider'):
                print(f"   Provider: {test_result['provider']}")
        else:
            print(f"   ⚠️  {test_result['message']}")
            print(f"   Note: This is expected if Ollama isn't installed or no model downloaded")
    else:
        print("   ⚠️  No AI provider available")
        print("   This is OK - standard queries will still work")
    
    return True

def test_cache():
    """Test caching functionality."""
    print("\n" + "="*70)
    print("TEST 4: Cache System")
    print("="*70)
    
    fetcher = MLBDataFetcher(use_cache=True)
    
    print("\n1. Getting cache stats...")
    stats = fetcher.get_cache_stats()
    print(f"   Total entries: {stats['total_entries']}")
    print(f"   Cache size: {stats['total_size_mb']:.2f} MB")
    if stats.get('oldest_entry'):
        print(f"   Oldest: {stats['oldest_entry']}")
    if stats.get('newest_entry'):
        print(f"   Newest: {stats['newest_entry']}")
    
    return True

def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("  MLB Statistics Application - Test Suite")
    print("="*70)
    
    tests = [
        ("Data Fetcher", test_data_fetcher),
        ("Data Processor", test_data_processor),
        ("AI Handler", test_ai_handler),
        ("Cache System", test_cache),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success, None))
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"\n❌ ERROR in {name}: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for name, success, error in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")
        if error:
            print(f"        Error: {error}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

if __name__ == "__main__":
    main()
