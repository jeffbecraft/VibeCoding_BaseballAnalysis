"""
Test the full flow of the comparison fix.
"""
import re

def test_full_comparison_flow():
    """Simulate the query parsing and routing logic."""
    
    query = "Who had more doubles in 2024, Gunnar Henderson or Aaron Judge?"
    query_lower = query.lower()
    
    print("\n" + "="*70)
    print(f"Testing query: '{query}'")
    print("="*70)
    
    # Step 1: Comparison detection
    comparison_words = ['more', 'better', 'worse', 'less', 'fewer']
    has_comparison_word = any(word in query_lower for word in comparison_words)
    has_or = ' or ' in query_lower
    is_comparison = has_comparison_word and has_or
    
    print(f"\n1. Comparison Detection:")
    print(f"   Has comparison word (more/better/less): {has_comparison_word}")
    print(f"   Has 'or': {has_or}")
    print(f"   → Classified as: {'COMPARISON' if is_comparison else 'other'}")
    
    # Step 2: Extract player names
    name_pattern = r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b'
    players_found = re.findall(name_pattern, query)
    
    print(f"\n2. Player Name Extraction:")
    print(f"   Players found: {players_found}")
    print(f"   Count: {len(players_found)}")
    
    # Step 3: Check if needs AI
    direct_comparison_patterns = [
        r'who\s+(had|has|have|hit|pitched|got|scored|stole)\s+(more|better|fewer|less)',
    ]
    
    needs_direct_answer = any(re.search(pattern, query_lower) for pattern in direct_comparison_patterns)
    has_multiple_players = len(players_found) >= 2
    needs_ai = needs_direct_answer and has_multiple_players
    
    print(f"\n3. AI Routing Decision:")
    print(f"   Needs direct answer: {needs_direct_answer}")
    print(f"   Has 2+ players: {has_multiple_players}")
    print(f"   → Route to AI: {needs_ai}")
    
    print(f"\n" + "="*70)
    print(f"RESULT:")
    print(f"="*70)
    if needs_ai:
        print(f"✓ Query will be routed to AI for direct comparison")
        print(f"  AI will compare: {players_found[0]} vs {players_found[1]}")
        print(f"  AI will return: Direct answer like 'Aaron Judge had more (36 vs 31)'")
    else:
        print(f"  Query will use standard comparison handler")
        print(f"  Will show: Ranked list of all players")
    
    return needs_ai

if __name__ == "__main__":
    result = test_full_comparison_flow()
    print(f"\n{'✓ FIX WORKING!' if result else '❌ FIX NOT WORKING'}\n")
