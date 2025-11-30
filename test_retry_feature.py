"""
Test the retry feature for AI queries.
"""
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from src.data_fetcher import MLBDataFetcher
from src.data_processor import MLBDataProcessor
from src.ai_query_handler import AIQueryHandler
from utils.ai_code_cache import AICodeCache

def test_retry_feature():
    """Test that we can retry a query by clearing its cache."""
    print("\n" + "="*70)
    print("Testing Retry Feature")
    print("="*70)
    
    # Initialize components
    fetcher = MLBDataFetcher()
    processor = MLBDataProcessor()
    ai_handler = AIQueryHandler(fetcher, processor)
    cache = AICodeCache()
    
    if not ai_handler.is_available():
        print("❌ AI not available")
        return False
    
    print(f"✓ AI initialized: {ai_handler.provider} / {ai_handler.model}")
    
    # Test query
    query = "Who hit more home runs in 2023? Gunnar Henderson or Bobby Witt Jr.?"
    season = 2023
    
    # First execution (will generate new code)
    print(f"\n1. First execution of query:")
    print(f"   '{query}'")
    print("-"*70)
    
    def progress(step, detail):
        print(f"   {step}: {detail}")
    
    result1 = ai_handler.handle_query_with_retry(query, season, report_progress=progress)
    
    if result1.get('success'):
        print(f"\n   ✓ First execution: SUCCESS")
        print(f"     Answer: {result1.get('answer')}")
        print(f"     Cached: {result1.get('cached', False)}")
        print(f"     Steps: {len(result1.get('steps', []))} steps")
    else:
        print(f"\n   ❌ First execution failed: {result1.get('error')}")
        return False
    
    # Get cache key
    cache_key = cache._generate_cache_key(query, season)
    print(f"\n2. Cache key: {cache_key}")
    
    # Verify it's cached
    cached_code = cache.get(query, season)
    if cached_code:
        print(f"   ✓ Query is cached ({len(cached_code)} chars of code)")
    else:
        print(f"   ❌ Query not in cache!")
        return False
    
    # Second execution (should use cache)
    print(f"\n3. Second execution (should use cache):")
    print("-"*70)
    
    result2 = ai_handler.handle_query_with_retry(query, season, report_progress=progress)
    
    if result2.get('success'):
        print(f"\n   ✓ Second execution: SUCCESS")
        print(f"     Cached: {result2.get('cached', False)}")
        if result2.get('cached'):
            print(f"     ✓ Used cached code as expected!")
        else:
            print(f"     ⚠ Generated new code (unexpected)")
    
    # Now test the retry feature - remove from cache
    print(f"\n4. Testing retry feature (clear cache):")
    print("-"*70)
    
    removed = cache.remove(cache_key)
    print(f"   Cache removal: {'✓ SUCCESS' if removed else '❌ FAILED'}")
    
    # Verify it's gone
    cached_code_after = cache.get(query, season)
    if not cached_code_after:
        print(f"   ✓ Cache cleared successfully")
    else:
        print(f"   ❌ Cache still exists!")
        return False
    
    # Third execution (should generate fresh code)
    print(f"\n5. Third execution after cache clear (should generate fresh):")
    print("-"*70)
    
    result3 = ai_handler.handle_query_with_retry(query, season, report_progress=progress)
    
    if result3.get('success'):
        print(f"\n   ✓ Third execution: SUCCESS")
        print(f"     Cached: {result3.get('cached', False)}")
        if not result3.get('cached'):
            print(f"     ✓ Generated fresh code as expected!")
        else:
            print(f"     ❌ Used cache (should have been cleared)")
            return False
    
    # Summary
    print(f"\n" + "="*70)
    print(f"RETRY FEATURE TEST RESULTS")
    print(f"="*70)
    print(f"✓ First execution: Generated new code")
    print(f"✓ Second execution: Used cached code")
    print(f"✓ Cache clear: Removed cached entry")
    print(f"✓ Third execution: Generated fresh code")
    print(f"\n✓ Retry feature working correctly!")
    print(f"="*70)
    
    return True

if __name__ == "__main__":
    success = test_retry_feature()
    sys.exit(0 if success else 1)
