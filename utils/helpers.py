"""
Utility Functions for MLB Statistics Analysis

Helper functions for common tasks.
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime


def ensure_directory_exists(directory: str) -> None:
    """
    Create directory if it doesn't exist.
    
    Args:
        directory: Directory path to create
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")


def save_json(data: Dict[str, Any], filepath: str) -> None:
    """
    Save data to JSON file.
    
    Args:
        data: Data to save
        filepath: Output file path
    """
    ensure_directory_exists(os.path.dirname(filepath))
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to {filepath}")


def load_json(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Load data from JSON file.
    
    Args:
        filepath: Input file path
        
    Returns:
        Loaded data or None if error
    """
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {filepath}")
        return None


def get_current_season() -> int:
    """
    Get the current MLB season year.
    
    Returns:
        Current season year
    """
    now = datetime.now()
    # MLB season typically starts in April
    if now.month < 4:
        return now.year - 1
    return now.year


def format_stat(value: float, decimal_places: int = 3) -> str:
    """
    Format a statistical value for display.
    
    Args:
        value: Statistical value
        decimal_places: Number of decimal places
        
    Returns:
        Formatted string
    """
    return f"{value:.{decimal_places}f}"


def parse_innings_pitched(ip_string: str) -> float:
    """
    Parse innings pitched string (e.g., "200.1" = 200 1/3 innings).
    
    Args:
        ip_string: Innings pitched as string
        
    Returns:
        Innings pitched as float
    """
    try:
        return float(ip_string)
    except (ValueError, TypeError):
        return 0.0


def calculate_singles(hits: int, doubles: int, triples: int, home_runs: int) -> int:
    """
    Calculate number of singles from hit totals.
    
    Args:
        hits: Total hits
        doubles: Number of doubles
        triples: Number of triples
        home_runs: Number of home runs
        
    Returns:
        Number of singles
    """
    return hits - doubles - triples - home_runs


def calculate_total_bases(singles: int, doubles: int, triples: int, home_runs: int) -> int:
    """
    Calculate total bases.
    
    Args:
        singles: Number of singles
        doubles: Number of doubles
        triples: Number of triples
        home_runs: Number of home runs
        
    Returns:
        Total bases
    """
    return singles + (2 * doubles) + (3 * triples) + (4 * home_runs)


# Common MLB team IDs for reference
TEAM_IDS = {
    "Yankees": 147,
    "Red Sox": 111,
    "Dodgers": 119,
    "Giants": 137,
    "Cubs": 112,
    "Cardinals": 138,
    "Astros": 117,
    "Braves": 144,
    "Phillies": 143,
    "Mets": 121,
    "Padres": 135,
    "Mariners": 136,
    "Angels": 108,
    "Blue Jays": 141,
    "Guardians": 114,
    "Twins": 142,
    "White Sox": 145,
    "Tigers": 116,
    "Royals": 118,
    "Orioles": 110,
    "Rays": 139,
    "Rangers": 140,
    "Athletics": 133,
    "Brewers": 158,
    "Pirates": 134,
    "Reds": 113,
    "Diamondbacks": 109,
    "Rockies": 115,
    "Marlins": 146,
    "Nationals": 120
}


# League IDs
LEAGUE_IDS = {
    "American League": 103,
    "National League": 104
}


if __name__ == "__main__":
    # Test utilities
    print(f"Current MLB season: {get_current_season()}")
    print(f"Yankees team ID: {TEAM_IDS['Yankees']}")
    
    # Test formatting
    avg = 0.285714
    print(f"Formatted average: {format_stat(avg, 3)}")
