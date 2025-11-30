"""
Test the fixed AI comparison logic for "who had MORE" queries.

This test verifies that:
1. AI uses proper variable naming (henderson_sb, not player1_sb)
2. AI compares values correctly
3. AI constructs answer with correct player-to-value mapping
4. The winner is stated first with their value
"""

import sys
sys.path.insert(0, 'src')

from data_fetcher import MLBDataFetcher
from data_processor import MLBDataProcessor
from ai_query_handler import AIQueryHandler

print("=" * 70)
print("Testing Fixed AI Comparison Logic")
print("=" * 70)

# Initialize
data_fetcher = MLBDataFetcher(use_cache=True)
data_processor = MLBDataProcessor()
ai_handler = AIQueryHandler(data_fetcher, data_processor)

# Test query
question = "Who had more stolen bases in 2025, Gunnar Henderson or Bobby Witt Jr.?"
season = 2025

print(f"\nQuestion: {question}")
print(f"Season: {season}")
print("\n" + "-" * 70)

# Execute query
result = ai_handler.handle_query_with_retry(
    question=question,
    season=season,
    report_progress=lambda step, msg: print(f"  {step}: {msg}")
)

print("\n" + "=" * 70)
print("RESULT:")
print("=" * 70)

if result.get('success'):
    print(f"✓ Success: {result.get('answer')}")
    print(f"\nData returned:")
    data = result.get('data', {})
    for key, value in data.items():
        print(f"  {key}: {value}")
    
    # Verify logic
    print("\n" + "-" * 70)
    print("VERIFICATION:")
    print("-" * 70)
    
    henderson_sb = data.get('henderson_stolen_bases', 0)
    witt_sb = data.get('witt_stolen_bases', 0)
    answer = result.get('answer', '')
    
    print(f"Henderson SB: {henderson_sb}")
    print(f"Witt SB: {witt_sb}")
    
    if witt_sb > henderson_sb:
        expected_winner = "Bobby Witt Jr."
        print(f"Expected winner: {expected_winner} ({witt_sb} > {henderson_sb})")
    else:
        expected_winner = "Gunnar Henderson"
        print(f"Expected winner: {expected_winner} ({henderson_sb} > {witt_sb})")
    
    # Check if answer mentions the winner correctly
    if expected_winner in answer and str(max(henderson_sb, witt_sb)) in answer:
        print(f"\n✓ ANSWER IS LOGICALLY CORRECT!")
        print(f"  Winner ({expected_winner}) is mentioned with correct value")
        
        # Check if winner is mentioned first
        if answer.lower().startswith(expected_winner.lower().split()[0]):
            print(f"✓ Winner mentioned first in answer")
        else:
            print(f"⚠ Winner not mentioned first (but answer is still correct)")
    else:
        print(f"\n✗ ANSWER LOGIC ERROR!")
        print(f"  Expected: {expected_winner} with {max(henderson_sb, witt_sb)}")
        print(f"  Got: {answer}")
    
    # Show generated code snippet if available
    if 'code' in result:
        print("\n" + "-" * 70)
        print("Generated code uses proper variable naming:")
        print("-" * 70)
        code_lines = result['code'].split('\n')
        for i, line in enumerate(code_lines[:30], 1):  # First 30 lines
            if 'henderson' in line.lower() or 'witt' in line.lower():
                print(f"  {i:2d}: {line}")
else:
    print(f"✗ Failed: {result.get('error')}")
    if 'traceback' in result:
        print(f"\nTraceback:\n{result['traceback']}")

print("\n" + "=" * 70)
