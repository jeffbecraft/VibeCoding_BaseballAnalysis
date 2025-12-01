"""Test AI query performance for active player comparison."""
import time
from src.ai_query_handler import AIQueryHandler
from src.data_fetcher import MLBDataFetcher
from src.data_processor import MLBDataProcessor

def test_ai_comparison():
    """Test the full AI query flow for comparing two active players."""
    df = MLBDataFetcher(use_cache=False)
    dp = MLBDataProcessor()
    ai = AIQueryHandler(df, dp, provider='ollama')
    
    print('Starting AI query for: Compare Gunnar Henderson vs Anthony Santander home runs')
    start = time.time()
    
    result = ai.handle_query('Compare Gunnar Henderson vs Anthony Santander home runs', season=2024)
    
    elapsed = time.time() - start
    print(f'\n🎯 AI query completed in {elapsed:.2f}s')
    print(f'Success: {result.get("success")}')
    
    if 'steps' in result:
        print(f'\nSteps taken:')
        for step in result['steps']:
            print(f'  - {step}')

if __name__ == '__main__':
    test_ai_comparison()
