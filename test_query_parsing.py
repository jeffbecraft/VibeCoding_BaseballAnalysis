"""
Test what the query parser extracts from the doubles comparison query.
"""
import sys
import os
import re

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Import the Streamlit app module to get the parser
from streamlit_app import MLBQueryHandler

def main():
    """Test query parsing for the doubles comparison."""
    print("\n" + "="*70)
    print("Testing Query Parser")
    print("="*70)
    
    # Create a mock handler to access the parser
    handler = MLBQueryHandler()
    parser = handler.parser
    
    test_queries = [
        "Who had more doubles in 2024, Gunnar Henderson or Aaron Judge?",
        "Aaron Judge vs Gunnar Henderson doubles 2024",
        "Compare Aaron Judge and Gunnar Henderson doubles in 2024",
        "Gunnar Henderson doubles 2024",
        "Aaron Judge doubles ranking 2024",
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 70)
        
        parsed = parser.parse_query(query)
        
        if parsed:
            print(f"Query Type: {parsed.get('query_type')}")
            print(f"Stat Type: {parsed.get('stat_type')}")
            print(f"Stat Group: {parsed.get('stat_group')}")
            print(f"Year: {parsed.get('year')}")
            print(f"Player Name: {parsed.get('player_name')}")
            print(f"Is Comparison: {parsed.get('query_type') == 'comparison'}")
            
            # Check for comparison keywords
            query_lower = query.lower()
            has_vs = 'vs' in query_lower or 'versus' in query_lower
            has_compare = 'compare' in query_lower
            has_or = ' or ' in query_lower
            has_more = 'more' in query_lower or 'better' in query_lower
            
            print(f"\nComparison indicators:")
            print(f"  Has 'vs/versus': {has_vs}")
            print(f"  Has 'compare': {has_compare}")
            print(f"  Has 'or': {has_or}")
            print(f"  Has 'more/better': {has_more}")
        else:
            print("❌ Parser returned None")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
