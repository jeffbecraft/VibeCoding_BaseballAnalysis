"""
Live AI Testing Script

Test the AI query handler with real queries and see the generated code.
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from data_fetcher import MLBDataFetcher
from data_processor import MLBDataProcessor
from ai_query_handler import AIQueryHandler


def test_query(ai_handler, question, season=2024):
    """Test a single query and show results."""
    print("\n" + "="*70)
    print(f"QUESTION: {question}")
    print("="*70)
    
    result = ai_handler.handle_query(question, season)
    
    print("\nSTATUS:", "[OK]" if result.get('success') else "[FAILED]")
    
    if result.get('generated_code'):
        print("\nGENERATED CODE:")
        print("-"*70)
        for i, line in enumerate(result['generated_code'].split('\n')[:20], 1):
            print(f"{i:3}: {line}")
        print("-"*70)
    
    if result.get('success'):
        if result.get('answer'):
            print(f"\nANSWER: {result['answer']}")
        if result.get('explanation'):
            print(f"EXPLANATION: {result['explanation']}")
        if result.get('data'):
            print(f"\nDATA: {type(result['data']).__name__} with {len(result['data'])} items")
    else:
        print(f"\nERROR: {result.get('error', 'Unknown error')}")
        if 'safety check' in str(result.get('error', '')):
            print("\n[!] The AI generated code that was blocked for security reasons.")
            print("    This shows the safety validation is working correctly.")


def main():
    """Run live AI tests."""
    print("="*70)
    print("  LIVE AI TESTING - Ollama Integration")
    print("="*70)
    
    # Initialize components
    print("\nInitializing...")
    fetcher = MLBDataFetcher(use_cache=True)
    processor = MLBDataProcessor()
    ai_handler = AIQueryHandler(fetcher, processor)
    
    if not ai_handler.is_available():
        print("\n[X] AI not available!")
        print("Make sure Ollama is running: ollama list")
        return
    
    provider_info = ai_handler.get_provider_info()
    print(f"\n[OK] AI Ready!")
    print(f"     Provider: {provider_info['provider']}")
    print(f"     Model: {provider_info['model']}")
    print(f"     Cost: {provider_info['cost']}")
    
    # Test queries
    test_queries = [
        "Who had the most home runs in 2024?",
        "What was Shohei Ohtani's batting average?",
        "Top 5 ERA leaders in 2024",
    ]
    
    print("\n" + "="*70)
    print("  TESTING QUERIES")
    print("="*70)
    
    for query in test_queries:
        test_query(ai_handler, query, 2024)
        input("\nPress Enter to continue...")
    
    # Interactive mode
    print("\n" + "="*70)
    print("  INTERACTIVE MODE")
    print("="*70)
    print("\nEnter your own questions (or 'quit' to exit):\n")
    
    while True:
        try:
            question = input("\nYour question: ").strip()
            
            if not question or question.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            test_query(ai_handler, question, 2024)
            
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n[X] Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
