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
- **AI-Powered Queries**: Use FREE local AI (Ollama) or OpenAI for complex questions
- **Smart Code Caching**: AI-generated code is cached for instant re-use (2-5s → 0.1s!)
- **Retry Feature**: Easily regenerate AI answers with one click
- **Web Application**: Browser-based interface for remote access and sharing
- **Stats Leaders**: Find top 50 players in any statistical category
- **Team & League Filtering**: Filter stats by specific teams or leagues (AL/NL)
- **Caching System**: Smart caching to reduce API calls and improve performance
- **Comprehensive Testing**: 54 automated tests including AI feature coverage
- **CI/CD Pipeline**: GitHub Actions with automated testing and security scanning

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

## Recent Enhancements (2025)

### Industry Best Practices (November 30, 2025) ✨
- **Structured Logging**: Professional logging with configurable levels (see `src/logger.py`)
- **Environment Configuration**: Centralized `.env` configuration management
- **Modern Packaging**: `pyproject.toml` (PEP 518) with optional dependencies
- **Dependency Pinning**: `requirements.lock` for reproducible builds
- **API Rate Limiting**: Automatic retry with exponential backoff (tenacity)
- **Pre-commit Hooks**: Automated code quality checks (black, flake8, bandit)
- **Health Monitoring**: System health status in Streamlit sidebar
- **Auto-Versioning**: Automatic version increment on successful test runs (see below)

See [Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md) | [Best Practices Guide](docs/BEST_PRACTICES.md)

### Automatic Version Management 🔄
The project now automatically increments its version number when:
1. Code is pushed to `master`/`main` branch
2. Full regression test suite executes successfully
3. Version format: `MAJOR.MINOR.PATCH` (e.g., `1.0.1` → `1.0.2`)

**Benefits:**
- Every commit has a unique version number
- Version only increments if all tests pass
- Git tags created automatically (e.g., `v1.0.2`)
- CHANGELOG updated automatically
- Version displayed in Streamlit UI sidebar

See [Version Management Guide](docs/VERSION_MANAGEMENT.md) for details.

### AI Query Improvements
- **Fixed Comparison Logic**: AI now correctly compares values and matches them to player names
  - Added Example 6 with critical comparison rules to AI prompt
  - Eliminates contradictory answers (e.g., stating "Henderson had 38 SB" when data showed 30)
- **Retry Feature**: One-click button to regenerate AI answers
  - Clears cache and forces fresh AI generation
  - Useful when answer seems incorrect or incomplete
  - See [docs/retry_feature.md](docs/retry_feature.md) for details

### User Experience
- **Fixed Spinner Animation**: Loading indicator now stops immediately after query execution
  - Previously continued during result display, preventing focus
  - Now only shows during actual data fetching

### Testing & Quality
- **Enhanced CI/CD**: Moved AI feature tests to automated test suite
  - 54 total tests (51 core + 3 AI features)
  - All tests run automatically on push via GitHub Actions
  - Pre-push hook prevents breaking changes

### Documentation
- **Architecture Guide**: Comprehensive beginner-friendly guide explaining how the system works
  - See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
  - Covers data flow, caching strategy, security model, and more
- **Verbose Code Comments**: All core modules now have detailed inline explanations
  - Adapter pattern explained in streamlit_app.py
  - Request flow documented in data_fetcher.py
  - Cache system thoroughly documented in utils/ai_code_cache.py

---

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

- **[Architecture Guide](docs/ARCHITECTURE.md)**: **NEW!** Beginner-friendly system architecture guide
- **[Retry Feature](docs/retry_feature.md)**: Guide to using the AI retry functionality
- **[GUI Guide](GUI_GUIDE.md)**: Complete guide to the desktop GUI
- **[Web App Summary](WEB_APP_SUMMARY.md)**: Overview of the web application
- **[Deploy Now](DEPLOY_NOW.md)**: Quick deployment to Streamlit Cloud
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)**: Detailed deployment instructions
- **[Testing Summary](TESTING_SUMMARY.md)**: Test suite documentation (54 tests)
- **[Team/League Filtering](TEAM_LEAGUE_FILTERING.md)**: Filtering documentation

## API Reference

This system uses the [MLB Stats API](https://statsapi.mlb.com/docs/) for retrieving official MLB statistics.

## License

MIT License
