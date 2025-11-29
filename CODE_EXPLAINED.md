# Code Explanation for Beginners

This document explains all the code in this project in plain English, perfect for someone who has never coded before.

## Table of Contents
1. [What is This Project?](#what-is-this-project)
2. [Understanding Python Basics](#understanding-python-basics)
3. [How Each Module Works](#how-each-module-works)

---

## What is This Project?

This is a system that:
1. **Connects** to MLB's website to download baseball statistics
2. **Processes** that data (cleans it up and organizes it)
3. **Analyzes** the stats (calculates things like batting averages, ERAs, etc.)
4. **Visualizes** the results (creates charts and graphs)

Think of it like a research assistant that:
- Goes to the library (MLB API)
- Finds the books you need (player/team data)
- Takes notes and organizes them (data processing)
- Does the math for you (analytics)
- Creates visual presentations (charts and graphs)

---

## Understanding Python Basics

### What are imports?
At the top of each file, you'll see lines like:
```python
import pandas as pd
import requests
```

**What this means:** You're bringing in tools (libraries) that other people have built. It's like saying "I'm going to use a calculator" before doing math problems.

- `requests`: A tool for downloading data from websites
- `pandas`: A tool for working with tables of data (like Excel, but in code)
- `matplotlib`: A tool for creating charts and graphs
- `numpy`: A tool for doing math with numbers

### What is a class?
A class is like a blueprint or template. For example:
```python
class MLBDataFetcher:
```

Think of it like a car blueprint:
- The blueprint (class) describes what a car should have
- You can create many cars (objects) from that one blueprint
- Each car can drive (call methods) using the blueprint's design

### What is a function/method?
A function is a set of instructions that does a specific task. For example:
```python
def calculate_batting_average(hits, at_bats):
    return hits / at_bats
```

This is like a recipe:
- **Input (ingredients):** `hits` and `at_bats`
- **Process (steps):** Divide hits by at_bats
- **Output (result):** The batting average

### What is a variable?
A variable is a container that holds a value:
```python
player_name = "Aaron Judge"
home_runs = 62
```

Think of it like a labeled box:
- The box label is `player_name` or `home_runs`
- The contents are "Aaron Judge" or 62
- You can put new things in the box anytime

---

## How Each Module Works

### 1. data_fetcher.py - The Data Retriever

**Purpose:** This module connects to MLB's website and downloads statistics.

**Key Components:**

#### MLBDataFetcher Class
This is your data retrieval assistant.

**Main Methods:**

1. **`__init__()`** - The Setup
   ```python
   def __init__(self):
       self.session = requests.Session()
   ```
   - This runs when you create a new fetcher
   - It sets up a connection to the internet
   - `self` means "this specific fetcher object"

2. **`_make_request(endpoint, params)`** - The Worker
   ```python
   def _make_request(self, endpoint, params=None):
       url = f"{self.BASE_URL}/{endpoint}"
       response = self.session.get(url, params=params, timeout=10)
       return response.json()
   ```
   - Builds a complete web address (URL)
   - Goes to that address and asks for data
   - Converts the response into Python-friendly format
   - The `_` at the start means it's a "private" helper method

3. **`search_players(name)`** - Find a Player
   ```python
   def search_players(self, name):
       # Go to the players endpoint
       # Filter results by name
       # Return matching players
   ```
   - Input: Player's name (like "Aaron Judge")
   - Output: List of matching players with their IDs

4. **`get_player_stats(player_id, season)`** - Get Stats
   ```python
   def get_player_stats(self, player_id, season, stat_group="hitting"):
       endpoint = f"people/{player_id}"
       # Request stats from API
       return data
   ```
   - Input: Player's ID number and year
   - Output: All their statistics for that season

**How to Use It:**
```python
# Step 1: Create a fetcher
fetcher = MLBDataFetcher()

# Step 2: Search for a player
players = fetcher.search_players("Shohei Ohtani")

# Step 3: Get the first player's ID
player_id = players[0]['id']

# Step 4: Get their stats
stats = fetcher.get_player_stats(player_id, 2024)
```

---

### 2. data_processor.py - The Data Organizer

**Purpose:** This module takes messy API data and organizes it into clean, usable tables.

**Key Components:**

#### MLBDataProcessor Class
This is your data organization assistant.

**Main Methods:**

1. **`extract_batting_stats(player_data)`** - Extract Hitting Stats
   ```python
   def extract_batting_stats(self, player_data):
       stats_list = []
       for stat_group in player_data.get("stats", []):
           # Pull out hitting statistics
           # Organize them into a dictionary
           stats_list.append({...})
       return pd.DataFrame(stats_list)
   ```
   
   **What happens:**
   - Takes raw player data (messy JSON)
   - Loops through each season
   - Pulls out important numbers (hits, home runs, etc.)
   - Puts everything into a neat table (DataFrame)
   
   **Example:**
   ```
   Before: {stats: [{group: {displayName: "hitting"}, splits: [...]}]}
   After:  
   | season | hits | homeRuns | avg  |
   |--------|------|----------|------|
   | 2023   | 165  | 37       | .275 |
   | 2024   | 180  | 45       | .285 |
   ```

2. **`convert_numeric_columns(df)`** - Convert Text to Numbers
   ```python
   def convert_numeric_columns(self, df, exclude_cols=None):
       for col in df.columns:
           df[col] = pd.to_numeric(df[col], errors='ignore')
       return df
   ```
   
   **Why this matters:**
   - Sometimes numbers come as text: "180" instead of 180
   - Text numbers can't be used in math
   - This converts "180" → 180 so we can do calculations

3. **`filter_by_season(df, seasons)`** - Filter Data
   ```python
   def filter_by_season(self, df, seasons):
       return df[df["season"].isin(seasons)]
   ```
   
   **Example:**
   - You have data from 2020-2024
   - You only want 2024
   - This removes all rows except 2024

4. **`create_player_summary(batting_df)`** - Summarize Career
   ```python
   def create_player_summary(self, batting_df, pitching_df=None):
       summary = {
           "total_games": batting_df["gamesPlayed"].sum(),
           "total_hits": batting_df["hits"].sum(),
           # ... more totals
       }
       return summary
   ```
   
   **What it does:**
   - Adds up all seasons
   - Calculates career totals
   - Returns a summary dictionary

**How to Use It:**
```python
# Step 1: Create a processor
processor = MLBDataProcessor()

# Step 2: Extract batting stats from raw data
batting_df = processor.extract_batting_stats(player_data)

# Step 3: Convert text numbers to real numbers
batting_df = processor.convert_numeric_columns(batting_df)

# Step 4: Filter to only 2024 season
df_2024 = processor.filter_by_season(batting_df, 2024)

# Step 5: Create career summary
summary = processor.create_player_summary(batting_df)
```

---

### 3. analytics.py - The Mathematician

**Purpose:** This module calculates baseball statistics and advanced metrics.

**Key Components:**

#### BattingAnalytics Class
Calculates hitting statistics.

**Main Methods:**

1. **`calculate_batting_average(hits, at_bats)`** - AVG
   ```python
   def calculate_batting_average(self, hits, at_bats):
       if at_bats == 0:
           return 0.0
       return hits / at_bats
   ```
   
   **The Math:**
   - Batting Average = Hits ÷ At Bats
   - Example: 180 hits ÷ 600 at bats = .300
   - **Why check if at_bats == 0?** You can't divide by zero!

2. **`calculate_on_base_percentage(hits, walks, hbp, at_bats, sf)`** - OBP
   ```python
   def calculate_on_base_percentage(self, hits, walks, hbp, at_bats, sacrifice_flies=0):
       denominator = at_bats + walks + hbp + sacrifice_flies
       if denominator == 0:
           return 0.0
       return (hits + walks + hbp) / denominator
   ```
   
   **The Math:**
   - OBP = (Hits + Walks + Hit By Pitch) ÷ (At Bats + Walks + HBP + SF)
   - Measures how often a player gets on base
   - Higher is better (.400 is excellent)

3. **`calculate_slugging_percentage(singles, doubles, triples, home_runs, at_bats)`** - SLG
   ```python
   def calculate_slugging_percentage(self, singles, doubles, triples, home_runs, at_bats):
       if at_bats == 0:
           return 0.0
       total_bases = singles + (2 * doubles) + (3 * triples) + (4 * home_runs)
       return total_bases / at_bats
   ```
   
   **The Math:**
   - Total Bases = 1×Singles + 2×Doubles + 3×Triples + 4×Home Runs
   - SLG = Total Bases ÷ At Bats
   - Measures power (how far you hit)
   - Higher is better (.500 is excellent)

4. **`calculate_ops(obp, slg)`** - OPS
   ```python
   def calculate_ops(self, obp, slg):
       return obp + slg
   ```
   
   **The Math:**
   - OPS = On-Base Percentage + Slugging Percentage
   - Combines getting on base with power
   - An .800+ OPS is considered very good
   - .900+ is All-Star level
   - 1.000+ is MVP level

5. **`calculate_woba(...)`** - Weighted On-Base Average
   ```python
   def calculate_woba(self, walks, hbp, singles, doubles, triples, home_runs, at_bats, sacrifice_flies=0):
       # Different weights for different hit types
       wBB = 0.690    # Walk weight
       w1B = 0.880    # Single weight
       w2B = 1.247    # Double weight
       w3B = 1.578    # Triple weight
       wHR = 2.004    # Home run weight
       
       numerator = (wBB * walks + w1B * singles + w2B * doubles + w3B * triples + wHR * home_runs)
       denominator = at_bats + walks + sacrifice_flies + hbp
       return numerator / denominator
   ```
   
   **Why wOBA?**
   - Not all hits are equal in value
   - A home run is worth more than a single
   - wOBA assigns different weights to different events
   - Weights are calculated by statisticians based on run scoring
   - Scale is similar to OBP (.320 is average, .400 is excellent)

#### PitchingAnalytics Class
Calculates pitching statistics.

**Main Methods:**

1. **`calculate_era(earned_runs, innings_pitched)`** - ERA
   ```python
   def calculate_era(self, earned_runs, innings_pitched):
       if innings_pitched == 0:
           return 0.0
       return (earned_runs * 9) / innings_pitched
   ```
   
   **The Math:**
   - ERA = (Earned Runs × 9) ÷ Innings Pitched
   - Shows how many runs a pitcher gives up per 9 innings (a full game)
   - Lower is better (under 3.00 is excellent)
   - Example: 75 earned runs ÷ 200 innings × 9 = 3.38 ERA

2. **`calculate_whip(walks, hits, innings_pitched)`** - WHIP
   ```python
   def calculate_whip(self, walks, hits, innings_pitched):
       if innings_pitched == 0:
           return 0.0
       return (walks + hits) / innings_pitched
   ```
   
   **The Math:**
   - WHIP = (Walks + Hits) ÷ Innings Pitched
   - Shows how many runners a pitcher allows per inning
   - Lower is better (under 1.00 is elite)

3. **`calculate_fip(home_runs, walks, hbp, strikeouts, innings_pitched)`** - FIP
   ```python
   def calculate_fip(self, home_runs, walks, hbp, strikeouts, innings_pitched, fip_constant=3.10):
       if innings_pitched == 0:
           return 0.0
       numerator = (13 * home_runs) + (3 * (walks + hbp)) - (2 * strikeouts)
       return (numerator / innings_pitched) + fip_constant
   ```
   
   **What is FIP?**
   - Fielding Independent Pitching
   - Measures what a pitcher can control: strikeouts, walks, home runs
   - Ignores balls in play (where fielders matter)
   - Scale is like ERA (lower is better)
   - If FIP < ERA: pitcher might be unlucky
   - If FIP > ERA: pitcher might be lucky

---

### 4. visualizations.py - The Artist

**Purpose:** This module creates charts and graphs to visualize data.

**Key Components:**

#### StatsVisualizer Class
Creates various types of charts.

**Main Methods:**

1. **`plot_batting_comparison(players_data, metrics)`** - Bar Chart
   ```python
   def plot_batting_comparison(self, players_data, metrics, player_name_col="playerName", figsize=(12, 6)):
       # Create a figure with multiple subplots
       fig, axes = plt.subplots(1, len(metrics), figsize=figsize)
       
       # For each metric, create a bar chart
       for idx, metric in enumerate(metrics):
           axes[idx].bar(players_data[player_name_col], players_data[metric])
       
       return fig
   ```
   
   **What it creates:**
   ```
   Home Runs          RBIs
   ┌─────┐          ┌─────┐
   │ 45  │          │ 115 │  Judge
   └─────┘          └─────┘
   ┌─────┐          ┌─────┐
   │ 38  │          │ 95  │  Trout
   └─────┘          └─────┘
   ```

2. **`plot_career_trajectory(player_data, metric)`** - Line Graph
   ```python
   def plot_career_trajectory(self, player_data, metric, season_col="season", player_name="Player", figsize=(10, 6)):
       # Create line plot showing metric over time
       ax.plot(player_data[season_col], player_data[metric], marker='o')
       
       # Add a trend line
       z = np.polyfit(range(len(player_data)), player_data[metric], 1)
       p = np.poly1d(z)
       ax.plot(player_data[season_col], p(range(len(player_data))), "--", label='Trend')
       
       return fig
   ```
   
   **What it creates:**
   ```
   Home Runs
      50│        ●
        │      ●
      40│    ●
        │  ●
      30│●
        └─────────────
        2020  2021  2022  2023  2024
   ```

3. **`plot_scatter_comparison(data, x_metric, y_metric)`** - Scatter Plot
   ```python
   def plot_scatter_comparison(self, data, x_metric, y_metric, label_col=None, show_correlation=True):
       # Plot each player as a point
       ax.scatter(data[x_metric], data[y_metric])
       
       # Add trend line
       z = np.polyfit(data[x_metric], data[y_metric], 1)
       
       # Calculate correlation
       corr = data[[x_metric, y_metric]].corr().iloc[0, 1]
       
       return fig
   ```
   
   **What it shows:**
   - Relationship between two variables
   - Each dot is a player
   - Trend line shows overall pattern
   - Correlation number (0-1) shows how strong the relationship is
   
   **Example:**
   ```
   Home Runs
      50│              ●
        │          ●     ●
      40│      ●          ●
        │  ●         ●
      30│●    ●
        └─────────────────
         .250  .275  .300  .325
              Batting Average
   ```

4. **`plot_heatmap(data, metrics)`** - Correlation Matrix
   ```python
   def plot_heatmap(self, data, metrics, figsize=(10, 8), title="Correlation Heatmap"):
       # Calculate correlation matrix
       corr_matrix = data[metrics].corr()
       
       # Create heatmap
       sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm')
       
       return fig
   ```
   
   **What it shows:**
   - How different statistics relate to each other
   - Red = positive correlation (when one goes up, other goes up)
   - Blue = negative correlation (when one goes up, other goes down)
   - Numbers show strength (-1 to 1)

---

### 5. helpers.py - The Utility Belt

**Purpose:** This module provides helper functions used throughout the project.

**Key Functions:**

1. **`get_current_season()`** - Get Current Year
   ```python
   def get_current_season():
       now = datetime.now()
       # MLB season starts in April
       if now.month < 4:
           return now.year - 1
       return now.year
   ```
   
   **Why the if statement?**
   - If it's January-March, the MLB season hasn't started yet
   - So we return last year (the most recent completed season)

2. **`calculate_singles(hits, doubles, triples, home_runs)`** - Get Singles
   ```python
   def calculate_singles(hits, doubles, triples, home_runs):
       return hits - doubles - triples - home_runs
   ```
   
   **The Logic:**
   - Total hits includes all hit types
   - Singles = Total Hits - (Doubles + Triples + Home Runs)
   - Example: 180 hits - 40 doubles - 5 triples - 35 home runs = 100 singles

3. **`calculate_total_bases(singles, doubles, triples, home_runs)`** - Get Total Bases
   ```python
   def calculate_total_bases(singles, doubles, triples, home_runs):
       return singles + (2 * doubles) + (3 * triples) + (4 * home_runs)
   ```
   
   **Why multiply?**
   - Single = 1 base
   - Double = 2 bases
   - Triple = 3 bases
   - Home Run = 4 bases (touch all bases)

4. **TEAM_IDS Dictionary** - Team Reference
   ```python
   TEAM_IDS = {
       "Yankees": 147,
       "Red Sox": 111,
       "Dodgers": 119,
       # ... all 30 MLB teams
   }
   ```
   
   **How to use:**
   ```python
   yankees_id = TEAM_IDS["Yankees"]  # Returns 147
   stats = fetcher.get_team_stats(yankees_id, 2024)
   ```

---

## Putting It All Together

Here's how all the pieces work together:

```python
# STEP 1: Import the modules (bring in our tools)
from src.data_fetcher import MLBDataFetcher
from src.data_processor import MLBDataProcessor
from src.analytics import BattingAnalytics
from src.visualizations import StatsVisualizer

# STEP 2: Create instances of each class (like hiring assistants)
fetcher = MLBDataFetcher()      # Data retrieval assistant
processor = MLBDataProcessor()  # Data organization assistant
analytics = BattingAnalytics()  # Math assistant
viz = StatsVisualizer()         # Art assistant

# STEP 3: Find a player (like looking up someone in a directory)
players = fetcher.search_players("Aaron Judge")
player_id = players[0]['id']

# STEP 4: Get their stats (like downloading their resume)
raw_stats = fetcher.get_player_stats(player_id, 2024)

# STEP 5: Process the stats (like organizing the resume into a neat table)
batting_df = processor.extract_batting_stats(raw_stats)
batting_df = processor.convert_numeric_columns(batting_df)

# STEP 6: Calculate advanced metrics (like doing additional analysis)
hits = batting_df.loc[0, 'hits']
at_bats = batting_df.loc[0, 'atBats']
avg = analytics.calculate_batting_average(hits, at_bats)

# STEP 7: Create visualizations (like making a presentation)
fig = viz.plot_career_trajectory(batting_df, 'homeRuns', player_name="Aaron Judge")
plt.show()  # Display the chart
```

**What just happened?**
1. We searched for Aaron Judge
2. Downloaded his 2024 statistics
3. Organized the data into a neat table
4. Calculated his batting average
5. Created a chart showing his home run trend over his career

---

## Common Patterns You'll See

### 1. The "Check if empty" pattern
```python
if at_bats == 0:
    return 0.0
return hits / at_bats
```
**Why?** Prevents division by zero errors (computer crashes)

### 2. The "Loop through items" pattern
```python
for player in players:
    print(player['name'])
```
**What it does:** Repeats an action for each item in a list

### 3. The "Try/Except" pattern
```python
try:
    # Try to do something
    result = risky_operation()
except Exception as e:
    # If it fails, do this instead
    print(f"Error: {e}")
    result = None
```
**Why?** Prevents the program from crashing when something goes wrong

### 4. The "Dictionary lookup" pattern
```python
player_name = player_data.get("fullName", "Unknown")
```
**What it does:**
- Looks for "fullName" in the dictionary
- If found, returns the value
- If not found, returns "Unknown" (the default)

### 5. The "f-string" pattern
```python
message = f"Player {name} hit {home_runs} home runs"
```
**What it does:**
- Creates a string with variables inserted
- The `f` before the quote enables this
- Variables go inside {curly braces}
- Example result: "Player Aaron Judge hit 62 home runs"

---

## Tips for Understanding Code

1. **Read the docstrings** - The text in triple quotes `"""` explains what each function does

2. **Look at the examples** - At the bottom of each file, there's usually example code

3. **Follow the data flow**:
   - Where does the data come from? (API)
   - What happens to it? (Processing)
   - Where does it go? (Analysis, Visualization)

4. **Use print statements** - Add `print()` to see what's happening:
   ```python
   print(f"Player ID: {player_id}")
   print(f"Stats: {stats}")
   ```

5. **Start small** - Run one function at a time to understand what it does

6. **Check variable types** - Use `type()` to see what kind of data you have:
   ```python
   print(type(batting_df))  # Output: <class 'pandas.core.frame.DataFrame'>
   ```

---

## Glossary of Terms

- **API**: A way for programs to talk to each other
- **DataFrame**: A table of data (like Excel)
- **Dictionary**: A collection of key-value pairs `{"name": "Aaron Judge"}`
- **Function**: A reusable block of code that does a specific task
- **Class**: A blueprint for creating objects
- **Object**: An instance of a class
- **Method**: A function that belongs to a class
- **Variable**: A named container for storing data
- **Loop**: Repeating an action multiple times
- **Conditional**: An if/else decision in code
- **Parameter**: Input to a function
- **Return value**: Output from a function
- **Import**: Bringing in code from other files or libraries

---

## Next Steps

1. **Run the example notebook** - `notebooks/example_analysis.ipynb`
2. **Try modifying the examples** - Change player names, years, metrics
3. **Create your own analysis** - Combine the tools in new ways
4. **Ask questions** - Add comments or print statements to explore

Remember: Everyone starts as a beginner. The best way to learn is by doing!
