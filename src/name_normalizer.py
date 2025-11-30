"""
Name Normalization Module

Handles normalization of player names to improve search matching.
Removes accents, special characters, and handles common variations.
"""

import unicodedata
import re
from typing import Optional
import logging

# Initialize logger
logger = logging.getLogger(__name__)


def normalize_name(name: str) -> str:
    """
    Normalize a name for better matching by removing accents and special characters.
    
    This function:
    1. Converts to lowercase
    2. Removes accent marks (é → e, ñ → n, etc.)
    3. Removes apostrophes and hyphens
    4. Removes extra whitespace
    
    Args:
        name: Original name (e.g., "José Ramírez", "Ronald Acuña Jr.")
    
    Returns:
        Normalized name (e.g., "jose ramirez", "ronald acuna jr")
    
    Examples:
        >>> normalize_name("José Ramírez")
        'jose ramirez'
        
        >>> normalize_name("Vladimir Guerrero Jr.")
        'vladimir guerrero jr'
        
        >>> normalize_name("Shohei Ohtani")
        'shohei ohtani'
        
        >>> normalize_name("Hyun Jin Ryu")
        'hyun jin ryu'
    """
    if not name:
        return ""
    
    # Convert to lowercase
    normalized = name.lower()
    
    # Remove accents using Unicode normalization
    # NFD = Canonical Decomposition (separates base char from accent)
    # Example: "é" becomes "e" + "´" (combining accent)
    normalized = unicodedata.normalize('NFD', normalized)
    
    # Remove combining characters (accents)
    # Category 'Mn' = Nonspacing Mark (accents, diacritics)
    normalized = ''.join(
        char for char in normalized
        if unicodedata.category(char) != 'Mn'
    )
    
    # Remove apostrophes and periods (O'Brien → OBrien, Jr. → Jr)
    normalized = normalized.replace("'", "").replace(".", "")
    
    # Replace hyphens with spaces for better matching
    # (Jean-Pierre → Jean Pierre)
    normalized = normalized.replace("-", " ")
    
    # Remove extra whitespace
    normalized = ' '.join(normalized.split())
    
    return normalized


def fuzzy_name_match(search_name: str, player_name: str, threshold: float = 0.7) -> bool:
    """
    Perform fuzzy matching between search name and player name.
    
    Uses normalized name comparison with partial matching support.
    
    Args:
        search_name: Name being searched (user input)
        player_name: Player's actual name from database
        threshold: Minimum similarity score (0.0 to 1.0, default 0.7)
    
    Returns:
        True if names are considered a match
    
    Examples:
        >>> fuzzy_name_match("Jose Ramirez", "José Ramírez")
        True
        
        >>> fuzzy_name_match("Acuna", "Ronald Acuña Jr.")
        True
        
        >>> fuzzy_name_match("Ohtani", "Shohei Ohtani")
        True
    """
    # Normalize both names
    norm_search = normalize_name(search_name)
    norm_player = normalize_name(player_name)
    
    # Direct substring match (most common case)
    if norm_search in norm_player or norm_player in norm_search:
        return True
    
    # Check if all words in search appear in player name
    search_words = set(norm_search.split())
    player_words = set(norm_player.split())
    
    # If all search words appear in player name, it's a match
    if search_words.issubset(player_words):
        return True
    
    # Calculate simple similarity score
    # (number of matching words / total unique words)
    matching_words = search_words & player_words
    total_words = search_words | player_words
    
    if len(total_words) > 0:
        similarity = len(matching_words) / len(total_words)
        return similarity >= threshold
    
    return False


def get_name_variations(name: str) -> list:
    """
    Generate common variations of a name for better matching.
    
    Args:
        name: Player name
    
    Returns:
        List of name variations
    
    Examples:
        >>> get_name_variations("José Ramírez")
        ['josé ramírez', 'jose ramirez', 'ramirez jose', 'ramirez']
        
        >>> get_name_variations("Vladimir Guerrero Jr.")
        ['vladimir guerrero jr.', 'vladimir guerrero jr', 'guerrero vladimir', 'guerrero']
    """
    variations = []
    
    # Original name (lowercase)
    original_lower = name.lower()
    variations.append(original_lower)
    
    # Normalized version
    normalized = normalize_name(name)
    if normalized != original_lower:
        variations.append(normalized)
    
    # Split into parts
    parts = normalized.split()
    
    if len(parts) >= 2:
        # Last name first (for "Ramírez José" style searches)
        reversed_name = f"{parts[-1]} {' '.join(parts[:-1])}"
        variations.append(reversed_name)
        
        # Just last name
        variations.append(parts[-1])
        
        # First name + last name (skip middle names/suffixes)
        if len(parts) > 2:
            variations.append(f"{parts[0]} {parts[-1]}")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_variations = []
    for var in variations:
        if var not in seen:
            seen.add(var)
            unique_variations.append(var)
    
    return unique_variations


def extract_last_name(full_name: str) -> Optional[str]:
    """
    Extract the last name from a full name.
    
    Handles suffixes like Jr., Sr., III, etc.
    
    Args:
        full_name: Complete player name
    
    Returns:
        Last name (without suffix) or None
    
    Examples:
        >>> extract_last_name("Vladimir Guerrero Jr.")
        'guerrero'
        
        >>> extract_last_name("Fernando Tatis Jr.")
        'tatis'
        
        >>> extract_last_name("Cal Ripken Jr.")
        'ripken'
    """
    if not full_name:
        return None
    
    # Normalize the name
    normalized = normalize_name(full_name)
    parts = normalized.split()
    
    if not parts:
        return None
    
    # Common suffixes to ignore
    suffixes = {'jr', 'sr', 'ii', 'iii', 'iv', 'v'}
    
    # Get last name (skip suffixes)
    last_name = parts[-1]
    if last_name in suffixes and len(parts) > 1:
        last_name = parts[-2]
    
    return last_name


# Common name mappings for known variations
# This can be expanded with more known aliases
KNOWN_ALIASES = {
    'mike': 'michael',
    'mike trout': 'michael trout',
    'a-rod': 'alex rodriguez',
    'arod': 'alex rodriguez',
    'big papi': 'david ortiz',
    'king felix': 'felix hernandez',
    'vladdy': 'vladimir guerrero',
    'vlad jr': 'vladimir guerrero jr',
    'tatis': 'fernando tatis',
    'acuna': 'ronald acuna',
    'ohtani': 'shohei ohtani',
    'judge': 'aaron judge',
}


def apply_known_aliases(name: str) -> str:
    """
    Apply known nickname/alias mappings.
    
    Args:
        name: Search name (potentially a nickname)
    
    Returns:
        Full name if alias recognized, otherwise original name
    
    Examples:
        >>> apply_known_aliases("Big Papi")
        'david ortiz'
        
        >>> apply_known_aliases("A-Rod")
        'alex rodriguez'
        
        >>> apply_known_aliases("Vlad Jr")
        'vladimir guerrero jr'
    """
    normalized = normalize_name(name)
    
    # Check if the normalized name matches any known alias
    if normalized in KNOWN_ALIASES:
        return KNOWN_ALIASES[normalized]
    
    return name


if __name__ == "__main__":
    # Test the normalization functions
    import logging
    logging.basicConfig(level=logging.INFO)
    
    test_names = [
        "José Ramírez",
        "Ronald Acuña Jr.",
        "Shohei Ohtani",
        "Vladimir Guerrero Jr.",
        "Hyun Jin Ryu",
        "Édgar Martínez",
        "Iván Rodríguez",
        "Víctor Robles",
        "O'Brien",
        "Jean-Pierre"
    ]
    
    print("Name Normalization Tests:")
    print("=" * 60)
    
    for name in test_names:
        normalized = normalize_name(name)
        variations = get_name_variations(name)
        last_name = extract_last_name(name)
        
        print(f"\nOriginal:     {name}")
        print(f"Normalized:   {normalized}")
        print(f"Last Name:    {last_name}")
        print(f"Variations:   {', '.join(variations)}")
    
    print("\n" + "=" * 60)
    print("\nFuzzy Matching Tests:")
    print("=" * 60)
    
    test_pairs = [
        ("Jose Ramirez", "José Ramírez"),
        ("Acuna", "Ronald Acuña Jr."),
        ("Ohtani", "Shohei Ohtani"),
        ("Vlad Jr", "Vladimir Guerrero Jr."),
        ("Hyun Jin", "Hyun Jin Ryu"),
    ]
    
    for search, player in test_pairs:
        match = fuzzy_name_match(search, player)
        print(f"'{search}' vs '{player}': {'✓ MATCH' if match else '✗ NO MATCH'}")
    
    print("\n" + "=" * 60)
    print("\nAlias Tests:")
    print("=" * 60)
    
    aliases = ["Big Papi", "A-Rod", "Vlad Jr", "Judge"]
    for alias in aliases:
        result = apply_known_aliases(alias)
        print(f"'{alias}' → '{result}'")
