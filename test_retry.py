"""
Simple test of the auto-retry mechanism with a query that worked before.
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

def main():
    """Test auto-retry with Henderson vs Witt query that worked before."""
    print("\n" + "="*70)
    print("Testing Auto-Retry Mechanism")
    print("="*70)
    
    # Initialize
    fetcher = MLBDataFetcher()
    processor = MLBDataProcessor()
    ai_handler = AIQueryHandler(fetcher, processor)
    
    if not ai_handler.is_available():
        print("❌ AI not available")
        return False
    
    print(f"✓ AI initialized: {ai_handler.provider} / {ai_handler.model}")
    
    # Clear cache for this test
    print("  Clearing cache to force fresh generation...")
    cleared = ai_handler.clear_code_cache()
    print(f"  Cleared {cleared} cache entries\n")
    
    # Test query
    query = "Who hit more home runs in 2023? Gunnar Henderson or Bobby Witt Jr.?"
    season = 2023
    
    print("="*70)
    print(f"Query: {query}")
    print("="*70)
    
    def progress_callback(step, detail):
        print(f"{step}: {detail}")
    
    result = ai_handler.handle_query_with_retry(
        query,
        season,
        report_progress=progress_callback
    )
    
    print("\n" + "="*70)
    if result.get('success'):
        print("✓ SUCCESS!")
        print(f"Answer: {result.get('answer')}")
        if result.get('retry_succeeded'):
            print("\n⚡ Retry mechanism worked! Query succeeded on second attempt.")
        elif result.get('cached'):
            print("\n⚡ Used cached code (shouldn't happen, we cleared cache)")
        else:
            print("\n✓ Succeeded on first attempt")
    else:
        print("❌ FAILED")
        print(f"Error: {result.get('error')}")
        if result.get('retry_attempted'):
            print(f"\nRetry was attempted but failed:")
            print(f"  {result.get('retry_failed')}")
    
    # Show steps
    if result.get('steps'):
        print("\nProcessing steps:")
        for step in result['steps']:
            print(f"  {step}")
    
    print("="*70)
    
    return result.get('success', False)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
