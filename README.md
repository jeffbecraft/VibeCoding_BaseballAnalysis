# MLB Statistics Analysis System

A comprehensive Python-based system for fetching, processing, and analyzing Major League Baseball statistics. Available as both a **desktop application** and a **web application** for easy sharing!

## 🌟 New: Web Application!

**Share MLB stats with anyone via a simple URL!** The web version is now available and can be deployed for free to Streamlit Cloud.

👉 **[Quick Deployment Guide](DEPLOY_NOW.md)** | **[Full Deployment Guide](DEPLOYMENT_GUIDE.md)** | **[Web App Summary](WEB_APP_SUMMARY.md)**

### Web App Features
- ⚾ No installation required - just open a URL
- 📱 Works on any device (desktop, tablet, mobile)
- 🔗 Share with family and friends
- 🆓 FREE hosting on Streamlit Cloud
- ⚡ Same natural language queries as desktop version
- 📊 Download results as CSV

**Launch Web Version Locally:**
```bash
python -m streamlit run streamlit_app.py
```

## Features

- **Data Fetching**: Retrieve player and team statistics from the MLB Stats API
- **Data Processing**: Clean, transform, and aggregate baseball data
- **Statistical Analysis**: Calculate advanced metrics (OPS, wOBA, ERA+, FIP, etc.)
- **Visualization**: Create insightful charts and graphs for statistical analysis
- **Player Comparison**: Compare multiple players across various metrics
- **Team Analysis**: Analyze team performance and trends
- **Natural Language GUI**: Query MLB statistics using natural language questions
- **Web Application**: Browser-based interface for remote access and sharing
- **Stats Leaders**: Find top 50 players in any statistical category
- **Team & League Filtering**: Filter stats by specific teams or leagues (AL/NL)
- **Caching System**: Smart caching to reduce API calls and improve performance
- **Regression Testing**: Comprehensive test suite to ensure reliability

## Project Structure

```
VibeCoding_BaseballAnalysis/
├── data/               # Raw and processed data storage
│   ├── raw/           # Raw data from APIs
│   ├── processed/     # Cleaned and processed data
│   └── cache/         # Cache directory for API responses
├── src/               # Source code
│   ├── data_fetcher.py      # MLB API data fetching
│   ├── data_processor.py    # Data cleaning and transformation
│   ├── analytics.py         # Statistical analysis functions
│   ├── visualizations.py    # Plotting and visualization
│   ├── mlb_gui.py          # Desktop GUI application
│   └── helpers.py          # Utility functions
├── utils/            # Utility modules
│   └── cache.py      # Caching system
├── tests/            # Test suite
├── notebooks/        # Jupyter notebooks for analysis
├── streamlit_app.py  # Web application
├── requirements.txt  # Python dependencies
├── requirements_web.txt  # Web app dependencies
└── README.md        # This file
```

## Installation

### Desktop Version

1. Clone or navigate to this directory
2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Web Version

1. Install web dependencies:
```bash
pip install -r requirements_web.txt
```

2. Run locally:
```bash
python -m streamlit run streamlit_app.py
```

3. Deploy to cloud (FREE):
   - See [DEPLOY_NOW.md](DEPLOY_NOW.md) for quick start
   - See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions

## Usage

### Web Application (Recommended for Sharing)

**Local Testing:**
```bash
python -m streamlit run streamlit_app.py
```
Then open http://localhost:8501 in your browser.

**Cloud Deployment:**
Follow the guide in [DEPLOY_NOW.md](DEPLOY_NOW.md) to deploy to Streamlit Cloud in 5 minutes.

Example questions in the web app:
- "Top 10 home runs in 2024"
- "What was Aaron Judge's batting average in 2024?"
- "Rank Shohei Ohtani's ERA"
- "Yankees home run leaders"
- "Which team had the best ERA in 2024?"

### Natural Language Query GUI (Desktop)

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

### Core Dependencies
- pandas: Data manipulation and analysis
- numpy: Numerical computing
- requests: HTTP requests for API calls

### Desktop Application
- matplotlib: Basic plotting
- seaborn: Statistical visualizations
- jupyter: Interactive notebooks
- tkinter: Desktop GUI (included with Python)

### Web Application
- streamlit: Web application framework

## Testing

Run the comprehensive regression test suite:

```bash
python run_tests.py
```

See [TESTING_SUMMARY.md](TESTING_SUMMARY.md) for details on the test suite.

## Documentation

- **[GUI Guide](GUI_GUIDE.md)**: Complete guide to the desktop GUI
- **[Web App Summary](WEB_APP_SUMMARY.md)**: Overview of the web application
- **[Deploy Now](DEPLOY_NOW.md)**: Quick deployment to Streamlit Cloud
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)**: Detailed deployment instructions
- **[Testing Summary](TESTING_SUMMARY.md)**: Test suite documentation
- **[Team/League Filtering](TEAM_LEAGUE_FILTERING.md)**: Filtering documentation

## API Reference

This system uses the [MLB Stats API](https://statsapi.mlb.com/docs/) for retrieving official MLB statistics.

## License

MIT License
