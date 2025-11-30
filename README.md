# MLB Statistics Analysis System

A comprehensive Python-based system for fetching, processing, and analyzing Major League Baseball statistics.

## Features

- **Data Fetching**: Retrieve player and team statistics from the MLB Stats API
- **Data Processing**: Clean, transform, and aggregate baseball data
- **Statistical Analysis**: Calculate advanced metrics (OPS, wOBA, ERA+, FIP, etc.)
- **Visualization**: Create insightful charts and graphs for statistical analysis
- **Player Comparison**: Compare multiple players across various metrics
- **Team Analysis**: Analyze team performance and trends
- **Natural Language GUI**: Query MLB statistics using natural language questions
- **Stats Leaders**: Find top 50 players in any statistical category
- **Team & League Filtering**: Filter stats by specific teams or leagues (AL/NL)

## Project Structure

```
VibeCoding_BaseballAnalysis/
├── data/               # Raw and processed data storage
│   ├── raw/           # Raw data from APIs
│   └── processed/     # Cleaned and processed data
├── src/               # Source code
│   ├── data_fetcher.py      # MLB API data fetching
│   ├── data_processor.py    # Data cleaning and transformation
│   ├── analytics.py         # Statistical analysis functions
│   └── visualizations.py    # Plotting and visualization
├── notebooks/         # Jupyter notebooks for analysis
├── utils/            # Utility functions
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

## Installation

1. Clone or navigate to this directory
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Natural Language Query GUI

Launch the graphical interface to ask questions in plain English:

```bash
python run_gui.py
```

Example questions:
- "Where did Gunnar Henderson rank in stolen bases in 2025?"
- "Show me the top 10 ERA leaders in 2024"
- "What was Aaron Judge's home run ranking in 2024?"
- "Top home run leaders for the Yankees in 2025"
- "American League ERA leaders"

See [GUI_GUIDE.md](GUI_GUIDE.md) for complete documentation.

### Team & League Filtering

Filter statistics by team or league:

```python
from helpers import TEAM_IDS, LEAGUE_IDS

# Get Yankees home run leaders
yankees_hr = fetcher.get_stats_leaders(
    stat_type="homeRuns",
    season=2025,
    limit=10,
    team_id=TEAM_IDS["Yankees"]
)

# Get American League ERA leaders
al_era = fetcher.get_stats_leaders(
    stat_type="era",
    season=2025,
    limit=10,
    stat_group="pitching",
    league_id=LEAGUE_IDS["American League"]
)
```

See [TEAM_LEAGUE_FILTERING.md](TEAM_LEAGUE_FILTERING.md) for detailed examples.

### Fetching Data

```python
from src.data_fetcher import MLBDataFetcher

fetcher = MLBDataFetcher()
player_stats = fetcher.get_player_stats(player_id=660271, season=2024)
team_stats = fetcher.get_team_stats(team_id=147, season=2024)
```

### Analyzing Statistics

```python
from src.analytics import BattingAnalytics, PitchingAnalytics

batting = BattingAnalytics()
ops = batting.calculate_ops(hits=150, doubles=30, triples=5, home_runs=25, 
                             walks=60, at_bats=500)
```

### Creating Visualizations

```python
from src.visualizations import StatsVisualizer

viz = StatsVisualizer()
viz.plot_batting_comparison(player_data_list)
```

## Example Analysis

Check out the `notebooks/example_analysis.ipynb` for a complete walkthrough of the system's capabilities.

## Dependencies

- pandas: Data manipulation and analysis
- numpy: Numerical computing
- requests: HTTP requests for API calls
- matplotlib: Basic plotting
- seaborn: Statistical visualizations
- jupyter: Interactive notebooks

## API Reference

This system uses the [MLB Stats API](https://statsapi.mlb.com/docs/) for retrieving official MLB statistics.

## License

MIT License
