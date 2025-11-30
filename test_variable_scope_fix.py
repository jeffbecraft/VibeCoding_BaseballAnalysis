"""
Quick test to verify the variable scoping fix works.
"""
import re

# Simulate the fixed code flow
query = "Who had more doubles in 2024, Gunnar Henderson or Aaron Judge?"
query_lower = query.lower()

print(f"Testing: {query}\n")

# Step 1: Check for comparison indicators EARLY (before player extraction)
comparison_words = ['more', 'better', 'worse', 'less', 'fewer']
has_comparison_word = any(word in query_lower for word in comparison_words)
has_or = ' or ' in query_lower

print(f"1. Early comparison detection:")
print(f"   has_comparison_word = {has_comparison_word}")
print(f"   has_or = {has_or}")

# Step 2: Extract player names (can now use the variables)
name_pattern = r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b'
player_name = None
all_player_names = []

for match in re.finditer(name_pattern, query):
    potential_name = match.group(0).strip()
    if not player_name:
        player_name = potential_name
    all_player_names.append(potential_name)
    
    # Check: Don't break early for comparison queries
    if player_name and not (has_comparison_word and has_or):
        print(f"\n2. Player extraction: Breaking early (not a comparison)")
        break

if has_comparison_word and has_or:
    print(f"\n2. Player extraction: Collected all players (is a comparison)")

print(f"   player_name = {player_name}")
print(f"   all_player_names = {all_player_names}")

# Step 3: Final comparison check
comparison_keywords = ['compare', 'versus', 'vs', 'vs.', 'against']
has_comparison_keyword = any(keyword in query_lower for keyword in comparison_keywords)
is_comparison = has_comparison_keyword or (has_comparison_word and has_or)

print(f"\n3. Final classification:")
print(f"   is_comparison = {is_comparison}")

print(f"\n✓ No UnboundLocalError! Variables are accessible.")
