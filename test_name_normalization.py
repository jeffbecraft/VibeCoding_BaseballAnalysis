"""
Test name normalization with real MLB API
"""

from src.data_fetcher import MLBDataFetcher

fetcher = MLBDataFetcher()

print("=" * 70)
print("TESTING NAME NORMALIZATION")
print("=" * 70)

test_cases = [
    ("Jose Ramirez", "José Ramírez (without accent marks)"),
    ("Acuna", "Ronald Acuña Jr. (partial name, without accent)"),
    ("Ohtani", "Shohei Ohtani (last name only)"),
    ("Vlad Jr", "Vladimir Guerrero Jr. (nickname)"),
    ("Judge", "Aaron Judge (last name only)"),
]

for search_term, description in test_cases:
    print(f"\n{'-' * 70}")
    print(f"TEST: Searching for '{search_term}'")
    print(f"Expected: {description}")
    print(f"{'-' * 70}")
    
    results = fetcher.search_players(search_term)
    
    if results:
        player = results[0]
        print(f"✓ FOUND: {player.get('fullName')}")
        print(f"  ID: {player.get('id')}")
        if 'currentTeam' in player:
            print(f"  Team ID: {player['currentTeam'].get('id')}")
        if 'lastSeasonFound' in player:
            print(f"  Last Season: {player['lastSeasonFound']}")
    else:
        print("✗ NOT FOUND")

print(f"\n{'=' * 70}")
print("TESTS COMPLETE")
print("=" * 70)
