# Getting Started with MLB Statistics Analysis

This guide will help you get started with the MLB Statistics Analysis system.

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Fetch Player Statistics

```python
from src.data_fetcher import MLBDataFetcher

fetcher = MLBDataFetcher()

# Search for a player
players = fetcher.search_players("Shohei Ohtani")
player_id = players[0]['id']

# Get player stats
stats = fetcher.get_player_stats(player_id, season=2024, stat_group="hitting")
```

### 2. Process the Data

```python
from src.data_processor import MLBDataProcessor

processor = MLBDataProcessor()
batting_df = processor.extract_batting_stats(stats)
batting_df = processor.convert_numeric_columns(batting_df)
```

### 3. Calculate Advanced Metrics

```python
from src.analytics import BattingAnalytics

analytics = BattingAnalytics()
ops = analytics.calculate_ops_from_stats(
    hits=180, doubles=40, triples=5, home_runs=35,
    walks=70, at_bats=550
)
print(f"OPS: {ops:.3f}")
```

### 4. Create Visualizations

```python
from src.visualizations import StatsVisualizer
import pandas as pd

viz = StatsVisualizer()

# Compare players
data = pd.DataFrame({
    'playerName': ['Player A', 'Player B'],
    'homeRuns': [35, 42],
    'ops': [.850, .920]
})

fig = viz.plot_batting_comparison(data, ['homeRuns', 'ops'])
```

## Using the Example Notebook

The easiest way to learn the system is through the example Jupyter notebook:

```bash
jupyter notebook notebooks/example_analysis.ipynb
```

## Common Use Cases

### Analyze a Specific Player

```python
from src.data_fetcher import MLBDataFetcher
from src.data_processor import MLBDataProcessor

fetcher = MLBDataFetcher()
processor = MLBDataProcessor()

# Get player data
players = fetcher.search_players("Aaron Judge")
player_id = players[0]['id']
stats = fetcher.get_player_stats(player_id, 2024)

# Process and analyze
batting_df = processor.extract_batting_stats(stats)
summary = processor.create_player_summary(batting_df)
print(summary)
```

### Compare Multiple Players

```python
from src.visualizations import StatsVisualizer
import pandas as pd

# Create comparison dataset
players_data = pd.DataFrame({
    'playerName': ['Judge', 'Trout', 'Ohtani'],
    'homeRuns': [45, 38, 44],
    'rbi': [115, 95, 105],
    'avg': [.285, .295, .275]
})

viz = StatsVisualizer()
fig = viz.plot_batting_comparison(players_data, ['homeRuns', 'rbi'])
```

### Analyze Team Statistics

```python
from utils.helpers import TEAM_IDS

# Get Yankees stats
team_id = TEAM_IDS['Yankees']
team_stats = fetcher.get_team_stats(team_id, 2024)
roster = fetcher.get_team_roster(team_id, 2024)

print(f"Yankees roster size: {len(roster)}")
```

## Advanced Features

### Calculate Sabermetrics

The system supports advanced metrics including:
- **Batting**: OPS, wOBA, ISO, BABIP, RC (Runs Created)
- **Pitching**: ERA, FIP, WHIP, K/9, BB/9, K/BB ratio
- **Team**: Pythagorean expectation, run differential

### Export Data

```python
# Export to CSV
processor.export_to_csv(batting_df, 'data/processed/player_stats.csv')

# Export to JSON
processor.export_to_json(summary, 'data/processed/player_summary.json')
```

## API Reference

### Data Fetcher Methods
- `get_player_stats(player_id, season, stat_group)` - Get player statistics
- `get_team_stats(team_id, season)` - Get team statistics
- `search_players(name)` - Search for players by name
- `get_teams(season)` - Get all MLB teams
- `get_schedule(team_id, start_date, end_date)` - Get team schedule

### Analytics Methods
- `calculate_ops()` - On-base plus slugging
- `calculate_woba()` - Weighted on-base average
- `calculate_fip()` - Fielding independent pitching
- `calculate_pythagorean_expectation()` - Expected win percentage

### Visualization Methods
- `plot_batting_comparison()` - Compare batting metrics
- `plot_career_trajectory()` - Show player performance over time
- `plot_scatter_comparison()` - Scatter plot of two metrics
- `plot_heatmap()` - Correlation heatmap
- `plot_radar_chart()` - Multi-dimensional player profile

## Need Help?

Check out:
- `notebooks/example_analysis.ipynb` - Complete walkthrough
- Source code documentation in each module
- MLB Stats API docs: https://statsapi.mlb.com/docs/

## Tips

1. The MLB Stats API is free and doesn't require authentication
2. Player IDs can be found using `search_players()`
3. Team IDs are available in `utils/helpers.py`
4. Season data is typically available from April onward
5. Use `get_current_season()` to get the active season year
