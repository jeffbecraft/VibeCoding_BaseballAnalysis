"""
Demo: AI-Powered Query System

This script demonstrates how the AI query handler works.
Run this to test AI query generation without the full Streamlit app.
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from data_fetcher import MLBDataFetcher
from data_processor import MLBDataProcessor
from ai_query_handler import AIQueryHandler


def main():
    """Run AI query demo."""
    print("=" * 70)
    print("  MLB Statistics - AI Query Handler Demo")
    print("=" * 70)
    print()
    
    # Initialize components
    print("Initializing MLB data components...")
    fetcher = MLBDataFetcher(use_cache=True)
    processor = MLBDataProcessor()
    
    # Initialize AI handler
    print("Initializing AI query handler...")
    ai_handler = AIQueryHandler(fetcher, processor)
    
    # Check if AI is available
    if not ai_handler.is_available():
        print()
        print("❌ AI Query Handler NOT Available")
        print()
        print("To enable AI queries:")
        print("1. Install OpenAI: pip install openai")
        print("2. Set API key: export OPENAI_API_KEY='your-key'")
        print()
        return
    
    print("✅ AI Query Handler Ready!")
    print()
    
    # Test connection
    print("Testing AI connection...")
    test_result = ai_handler.test_connection()
    
    if test_result['success']:
        print(f"✅ {test_result['message']}")
        print(f"   Model: {test_result['model']}")
    else:
        print(f"❌ {test_result['message']}")
        return
    
    print()
    print("=" * 70)
    print("  Demo Queries")
    print("=" * 70)
    print()
    
    # Example queries
    demo_queries = [
        "Who had the most home runs in 2024?",
        "What was Shohei Ohtani's batting average in 2024?",
        "Which Yankees player had the best ERA in 2024?",
        "Compare Aaron Judge and Juan Soto home runs in 2024",
    ]
    
    for i, question in enumerate(demo_queries, 1):
        print(f"\n{i}. Question: {question}")
        print("-" * 70)
        
        # Execute query
        result = ai_handler.handle_query(question, 2024)
        
        if result.get('success'):
            print(f"✅ Success!")
            print(f"\nAnswer: {result.get('answer', 'No answer provided')}")
            
            if result.get('explanation'):
                print(f"Explanation: {result['explanation']}")
            
            # Show generated code
            if result.get('generated_code'):
                print(f"\nGenerated Code:")
                print("-" * 40)
                code_lines = result['generated_code'].split('\n')
                for line in code_lines[:10]:  # Show first 10 lines
                    print(f"  {line}")
                if len(code_lines) > 10:
                    print(f"  ... ({len(code_lines) - 10} more lines)")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        
        print()
    
    # Interactive mode
    print("=" * 70)
    print("  Interactive Mode")
    print("=" * 70)
    print()
    print("Enter your questions (or 'quit' to exit):")
    print()
    
    while True:
        try:
            question = input("\nYour question: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            print("\nProcessing...")
            result = ai_handler.handle_query(question, 2024)
            
            if result.get('success'):
                print(f"\n✅ {result.get('answer', 'Query successful')}")
                
                if result.get('explanation'):
                    print(f"\n💡 {result['explanation']}")
                
                # Show data if available
                if result.get('data'):
                    data = result['data']
                    if isinstance(data, list) and len(data) > 0:
                        print(f"\nTop Results:")
                        for item in data[:5]:
                            print(f"  - {item}")
            else:
                print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
        
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
