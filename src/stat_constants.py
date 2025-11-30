"""
Shared statistical constants for MLB Statistics application.

This module contains stat mappings and classifications used across
the application (web UI, desktop GUI, query parsing).
"""

# Mapping of common stat terms to API parameter names
STAT_MAPPINGS = {
    # Hitting stats
    'home runs': 'homeRuns',
    'home run': 'homeRuns',
    'hr': 'homeRuns',
    'homers': 'homeRuns',
    'stolen bases': 'stolenBases',
    'stolen base': 'stolenBases',
    'steals': 'stolenBases',
    'sb': 'stolenBases',
    'batting average': 'avg',
    'average': 'avg',
    'avg': 'avg',
    'rbi': 'rbi',
    'runs batted in': 'rbi',
    'hits': 'hits',
    'doubles': 'doubles',
    'triples': 'triples',
    'runs': 'runs',
    'walks': 'walks',
    'strikeouts': 'strikeouts',
    'on base percentage': 'obp',
    'obp': 'obp',
    'slugging percentage': 'slg',
    'slugging': 'slg',
    'slg': 'slg',
    'ops': 'ops',
    # Pitching stats
    'era': 'era',
    'earned run average': 'era',
    'wins': 'wins',
    'saves': 'saves',
    'strikeouts': 'strikeouts',
    'whip': 'whip',
    'innings pitched': 'inningsPitched',
    'innings': 'inningsPitched'
}

# Stats that are pitching-related
PITCHING_STATS = {'era', 'wins', 'saves', 'whip', 'inningsPitched', 'strikeouts'}
