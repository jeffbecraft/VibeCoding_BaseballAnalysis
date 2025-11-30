"""
Simple test of query parsing logic without Streamlit.
"""
import sys
import re

query = "Who had more doubles in 2024, Gunnar Henderson or Aaron Judge?"

print(f"\nAnalyzing query: '{query}'")
print("="*70)

query_lower = query.lower()

# Check for comparison keywords
comparison_keywords = ['compare', 'versus', 'vs', 'vs.', 'against', 'better than', 'worse than']
is_comparison = any(keyword in query_lower for keyword in comparison_keywords)

print(f"\nComparison keywords found: {is_comparison}")
print(f"Keywords checked: {comparison_keywords}")

# The word "or" is often used in comparisons
has_or = ' or ' in query_lower
has_more = 'more' in query_lower or 'better' in query_lower or 'less' in query_lower or 'worse' in query_lower

print(f"\nHas ' or ': {has_or}")
print(f"Has comparison word (more/better/less/worse): {has_more}")

# Extract player names
name_patterns = [
    r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)(?:\'s)?\b',
    r'\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b',
]

players_found = []
for pattern in name_patterns:
    matches = re.finditer(pattern, query)
    for match in matches:
        name = match.group(0).strip()
        if name not in players_found:
            players_found.append(name)

print(f"\nPlayers found: {players_found}")
print(f"Number of players: {len(players_found)}")

# The issue: current parser only extracts ONE player name
# For "Who had more doubles in 2024, Gunnar Henderson or Aaron Judge?"
# It will extract ONLY "Gunnar Henderson" (the first one found)

print(f"\n{'='*70}")
print("DIAGNOSIS:")
print("="*70)
print("The query parser can only extract ONE player name.")
print("For comparison queries with 'or', it needs to extract BOTH names.")
print(f"\nThis query should be recognized as a COMPARISON with:")
print(f"  Player 1: {players_found[0] if players_found else 'N/A'}")
print(f"  Player 2: {players_found[1] if len(players_found) > 1 else 'N/A'}")
print(f"\nBut the current parser probably extracted only: {players_found[0] if players_found else 'N/A'}")
print("And classified it as: 'rank' (player ranking query)")
print("\nThis caused the app to show only Henderson's ranking (Rank #33, 31 doubles)")
print("instead of comparing both players.")
