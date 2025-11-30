"""
Test the defensive coding and auto-retry improvements.
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

def test_ai_improvements():
    """Test queries that previously failed."""
    print("\n" + "="*70)
    print("Testing AI Improvements: Defensive Coding + Auto-Retry")
    print("="*70)
    
    # Initialize components
    print("\n1. Initializing MLB Data Fetcher and AI Handler...")
    fetcher = MLBDataFetcher()
    processor = MLBDataProcessor()
    ai_handler = AIQueryHandler(fetcher, processor)
    
    if not ai_handler.is_available():
        print("❌ AI not available. Please start Ollama with llama3.2 model.")
        return False
    
    print(f"✓ AI Handler initialized ({ai_handler.provider}, {ai_handler.model})")
    
    # Test queries that previously failed in test_ai_live.py
    test_queries = [
        {
            'question': "Who had the most home runs in 2024?",
            'season': 2024,
            'expected': "Should find Aaron Judge with 58 HR",
            'previous_error': "Unauthorized import: MLB"
        },
        {
            'question': "What was Shohei Ohtani's batting average in 2024?",
            'season': 2024,
            'expected': "Should handle player search and stat extraction",
            'previous_error': "list index out of range"
        },
        {
            'question': "Who had the most stolen bases in 2023 on the Kansas City Royals?",
            'season': 2023,
            'expected': "Should handle team filtering",
            'previous_error': "name 'next' is not defined"
        },
        {
            'question': "Top 5 ERA leaders in 2024",
            'season': 2024,
            'expected': "Should get pitching leaders",
            'previous_error': "Unauthorized import: MLB"
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}: {test['question']}")
        print(f"Previous error: {test['previous_error']}")
        print(f"Expected: {test['expected']}")
        print("-"*70)
        
        def progress_callback(step, detail):
            print(f"  {step}: {detail}")
        
        result = ai_handler.handle_query_with_retry(
            test['question'],
            test['season'],
            report_progress=progress_callback
        )
        
        print()
        if result.get('success'):
            print(f"✓ SUCCESS!")
            print(f"  Answer: {result.get('answer', 'N/A')}")
            if result.get('retry_succeeded'):
                print(f"  ⚡ Succeeded on RETRY (auto-correction worked!)")
            elif result.get('cached'):
                print(f"  ⚡ Used cached code (instant!)")
            passed += 1
        else:
            print(f"❌ FAILED")
            print(f"  Error: {result.get('error', 'Unknown error')}")
            if result.get('retry_attempted'):
                print(f"  Retry attempted: {result.get('retry_failed', 'No details')}")
            failed += 1
        
        # Show steps
        if result.get('steps'):
            print(f"\n  Processing steps:")
            for step in result['steps']:
                print(f"    {step}")
    
    # Summary
    print("\n" + "="*70)
    print(f"Test Summary: {passed} passed, {failed} failed out of {len(test_queries)} tests")
    print("="*70)
    
    if passed > 0:
        improvement_rate = (passed / len(test_queries)) * 100
        print(f"\n✓ Improvement rate: {improvement_rate:.0f}% success")
        print(f"  (These queries all failed before the improvements)")
    
    # Check cache statistics
    print("\n" + "="*70)
    print("AI Code Cache Statistics")
    print("="*70)
    cache_stats = ai_handler.get_code_cache_stats()
    print(f"Total cached queries: {cache_stats.get('total_entries', 0)}")
    print(f"Total cache hits: {cache_stats.get('total_hits', 0)}")
    if cache_stats.get('top_queries'):
        print(f"\nMost popular queries:")
        for query_info in cache_stats['top_queries'][:5]:
            print(f"  • {query_info['question']} (hits: {query_info['hits']})")
    
    return passed > failed

if __name__ == "__main__":
    success = test_ai_improvements()
    sys.exit(0 if success else 1)
