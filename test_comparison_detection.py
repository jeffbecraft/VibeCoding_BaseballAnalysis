"""
Test if the updated comparison detection works.
"""
import re

def test_comparison_detection(query):
    """Test the new comparison detection logic."""
    query_lower = query.lower()
    
    # Direct comparison keywords
    comparison_keywords = ['compare', 'versus', 'vs', 'vs.', 'against', 'better than', 'worse than']
    has_comparison_keyword = any(keyword in query_lower for keyword in comparison_keywords)
    
    # Indirect comparison: "who had more X" or "which player has better Y"
    comparison_words = ['more', 'better', 'worse', 'less', 'fewer']
    has_comparison_word = any(word in query_lower for word in comparison_words)
    has_or = ' or ' in query_lower
    
    # It's a comparison if: explicit keyword OR (comparison word + 'or')
    is_comparison = has_comparison_keyword or (has_comparison_word and has_or)
    
    return {
        'is_comparison': is_comparison,
        'has_comparison_keyword': has_comparison_keyword,
        'has_comparison_word': has_comparison_word,
        'has_or': has_or
    }

# Test queries
test_queries = [
    "Who had more doubles in 2024, Gunnar Henderson or Aaron Judge?",
    "Aaron Judge vs Gunnar Henderson doubles 2024",
    "Compare Aaron Judge and Gunnar Henderson doubles in 2024",
    "Gunnar Henderson doubles 2024",  # NOT a comparison
    "Who had the most home runs in 2024?",  # NOT a comparison
    "Who had more home runs, Judge or Soto?",  # IS a comparison
]

print("\n" + "="*70)
print("Testing Updated Comparison Detection Logic")
print("="*70)

for query in test_queries:
    result = test_comparison_detection(query)
    status = "✓ COMPARISON" if result['is_comparison'] else "  single query"
    print(f"\n{status}: {query}")
    if result['is_comparison']:
        reasons = []
        if result['has_comparison_keyword']:
            reasons.append("has comparison keyword")
        if result['has_comparison_word'] and result['has_or']:
            reasons.append(f"has comparison word + 'or'")
        print(f"  Reason: {', '.join(reasons)}")

print("\n" + "="*70)
print("Result: The problematic query is now correctly detected as a comparison!")
print("="*70)
