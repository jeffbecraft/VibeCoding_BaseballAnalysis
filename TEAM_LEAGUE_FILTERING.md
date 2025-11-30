# Team and League Filtering Guide

## Overview

The MLB Statistics system now supports filtering stats leaders by **team** and **league**, allowing you to analyze players within specific contexts.

## Features

### 🏟️ Team Filtering
Filter statistics to show only players from a specific MLB team.

### ⚾ League Filtering
Filter statistics to show only players from the American League (AL) or National League (NL).

## Usage

### In the GUI Application

Simply mention the team name or league in your natural language query:

#### Team Examples:
```
"Top 10 home run leaders for the Yankees in 2025"
"Show me the Orioles batting average leaders"
"Who are the top 5 RBI leaders for the Dodgers?"
"Top ERA leaders for the Red Sox in 2024"
```

#### League Examples:
```
"Top ERA leaders in the American League for 2025"
"National League stolen base leaders in 2024"
"Show me the top 15 batting average leaders in the AL"
"Who are the NL home run leaders?"
```

### In Python Code / Jupyter Notebooks

Use the `get_stats_leaders()` method with optional `team_id` or `league_id` parameters:

#### Team Filtering Example:
```python
from data_fetcher import MLBDataFetcher
from data_processor import MLBDataProcessor
from helpers import TEAM_IDS

fetcher = MLBDataFetcher()
processor = MLBDataProcessor()

# Get Yankees home run leaders
yankees_hr = fetcher.get_stats_leaders(
    stat_type="homeRuns",
    season=2025,
    limit=10,
    stat_group="hitting",
    team_id=TEAM_IDS["Yankees"]  # Filter by Yankees
)

# Process and display
yankees_df = processor.extract_stats_leaders(yankees_hr)
print(yankees_df)
```

#### League Filtering Example:
```python
from helpers import LEAGUE_IDS

# Get American League ERA leaders
al_era = fetcher.get_stats_leaders(
    stat_type="era",
    season=2025,
    limit=10,
    stat_group="pitching",
    league_id=LEAGUE_IDS["American League"]  # Filter by AL
)

# Process and display
al_df = processor.extract_stats_leaders(al_era)
print(al_df)
```

## Available Teams

All 30 MLB teams are supported:

**American League:**
- Yankees, Red Sox, Orioles, Rays, Blue Jays
- Guardians, Twins, White Sox, Tigers, Royals
- Astros, Rangers, Mariners, Angels, Athletics

**National League:**
- Dodgers, Giants, Padres, Diamondbacks, Rockies
- Braves, Phillies, Mets, Marlins, Nationals
- Cubs, Cardinals, Brewers, Pirates, Reds

## Available Leagues

- **American League** (ID: 103) - Can also use "AL" in queries
- **National League** (ID: 104) - Can also use "NL" in queries

## Combining Filters

You can combine filtering with other query parameters:

```python
# Top 20 Yankees home run leaders from 2024
yankees_2024_hr = fetcher.get_stats_leaders(
    stat_type="homeRuns",
    season=2024,
    limit=20,
    stat_group="hitting",
    team_id=TEAM_IDS["Yankees"]
)
```

## Use Cases

### Team Analysis
- Compare players within a single team
- Identify team leaders in various categories
- Track team performance across seasons
- Analyze roster strength in specific areas

### League Analysis
- Compare league-wide performance
- Identify league leaders
- Analyze differences between AL and NL
- Track league trends over time

### Competitive Analysis
- Compare player performance within division
- Identify standout performers in specific contexts
- Analyze positional competition within teams

## API Parameters

The `get_stats_leaders()` method now accepts:

```python
def get_stats_leaders(
    stat_type: str,           # Required: e.g., 'homeRuns', 'era'
    season: Optional[int],    # Optional: defaults to current year
    limit: int = 50,          # Optional: number of leaders
    stat_group: str = "hitting",  # 'hitting' or 'pitching'
    team_id: Optional[int] = None,    # NEW: Filter by team
    league_id: Optional[int] = None   # NEW: Filter by league
)
```

## Examples in Action

### Example 1: Find Your Team's Best Players
```python
# Who are the top 5 home run hitters on the Dodgers?
dodgers_power = fetcher.get_stats_leaders(
    stat_type="homeRuns",
    season=2025,
    limit=5,
    stat_group="hitting",
    team_id=TEAM_IDS["Dodgers"]
)
```

### Example 2: League Comparison
```python
# Compare ERA leaders between leagues
al_era = fetcher.get_stats_leaders(
    stat_type="era",
    season=2025,
    limit=10,
    stat_group="pitching",
    league_id=LEAGUE_IDS["American League"]
)

nl_era = fetcher.get_stats_leaders(
    stat_type="era",
    season=2025,
    limit=10,
    stat_group="pitching",
    league_id=LEAGUE_IDS["National League"]
)
```

### Example 3: Historical Team Analysis
```python
# Who led the Yankees in stolen bases in 2023?
yankees_2023_sb = fetcher.get_stats_leaders(
    stat_type="stolenBases",
    season=2023,
    limit=10,
    stat_group="hitting",
    team_id=TEAM_IDS["Yankees"]
)
```

## Tips

- Team and league filters work with **all statistics** (hitting and pitching)
- You can use filters for **any season** with available data
- The **limit parameter** still applies when using filters
- Filters are **optional** - omit them to see MLB-wide leaders
- **Cannot combine** team and league filters (team filter takes precedence)

## Support

For questions or issues with filtering:
1. Check that team names are spelled correctly (case-insensitive)
2. Verify the season has data available
3. Ensure you're using a valid statistic type
4. See the main documentation for available teams and leagues
