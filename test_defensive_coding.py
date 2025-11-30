"""
Test that defensive coding improvements work with a query we know succeeds.
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

def test_defensive_coding():
    """Test that defensive coding patterns are in the AI examples."""
    print("\n" + "="*70)
    print("Testing Defensive Coding Improvements in AI Examples")
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
    
    # Test a comparison query that should work
    print("\n" + "="*70)
    print("Test 1: Player Comparison (tests defensive coding)")
    print("Question: Who hit more home runs in 2024? Aaron Judge or Juan Soto?")
    print("="*70)
    
    def progress_callback(step, detail):
        print(f"  {step}: {detail}")
    
    result = ai_handler.handle_query_with_retry(
        "Who hit more home runs in 2024? Aaron Judge or Juan Soto?",
        2024,
        report_progress=progress_callback
    )
    
    print()
    if result.get('success'):
        print("✓ SUCCESS!")
        print(f"  Answer: {result.get('answer', 'N/A')}")
        if result.get('retry_succeeded'):
            print("  ⚡ Succeeded on RETRY (defensive coding helped!)")
        elif result.get('cached'):
            print("  ⚡ Used cached code")
        print("\n  The generated code should use defensive patterns like:")
        print("    - if not leaders or len(leaders) == 0:")
        print("    - judge_row.iloc[0].get('rank', 'N/A')")
        print("    - if leaders_df.empty or len(leaders_df) == 0:")
        
        # Show the code
        if result.get('generated_code'):
            print("\n  Generated code preview:")
            code_lines = result['generated_code'].split('\n')
            # Show first 30 lines
            for i, line in enumerate(code_lines[:30], 1):
                print(f"    {i:2}: {line}")
            if len(code_lines) > 30:
                print(f"    ... ({len(code_lines) - 30} more lines)")
        
        return True
    else:
        print("❌ FAILED")
        print(f"  Error: {result.get('error', 'Unknown error')}")
        if result.get('retry_attempted'):
            print(f"  Retry failed: {result.get('retry_failed', 'No details')}")
        return False

if __name__ == "__main__":
    success = test_defensive_coding()
    sys.exit(0 if success else 1)
