"""Quick test to verify Gemini AI is working."""
from src.data_fetcher import MLBDataFetcher
from src.data_processor import MLBDataProcessor
from src.ai_query_handler import AIQueryHandler

# Initialize components
fetcher = MLBDataFetcher(use_cache=True)
processor = MLBDataProcessor()
ai_handler = AIQueryHandler(fetcher, processor, provider="gemini")

# Check what AI provider is being used
print(f"AI Available: {ai_handler.ai_available}")
print(f"Provider: {ai_handler.provider}")
print(f"Model: {ai_handler.model}")

if ai_handler.ai_available:
    provider_info = ai_handler.get_provider_info()
    print(f"\nProvider Info:")
    for key, value in provider_info.items():
        print(f"  {key}: {value}")
    
    # Test a simple query
    print("\nTesting AI query...")
    try:
        query = "Who had more home runs in 2024, Aaron Judge or Juan Soto?"
        result = ai_handler.handle_query(query)
        if result['success']:
            print(f"✓ AI query successful!")
            print(f"Answer: {result['answer'][:100]}...")
        else:
            print(f"✗ AI query failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"✗ Error during test: {e}")
else:
    print("\n✗ No AI provider available!")
