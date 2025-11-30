# MLB Statistics System Architecture

**A Beginner-Friendly Guide to Understanding the Application**

## Table of Contents
1. [System Overview](#system-overview)
2. [How Data Flows](#how-data-flows)
3. [Core Components](#core-components)
4. [AI Query System](#ai-query-system)
5. [Caching Strategy](#caching-strategy)
6. [Security Model](#security-model)

---

## System Overview

This application helps you ask questions about baseball statistics in plain English and get answers quickly. Think of it as having a baseball statistics expert who can answer any question you have.

### The Big Picture

```
You ask a question (in plain English)
        ↓
App understands your question (parses it OR uses AI)
        ↓
App fetches data from MLB's official API
        ↓
App processes and formats the data
        ↓
You get a beautiful answer with charts/tables
```

### Two Ways to Access

1. **Web App** (streamlit_app.py)
   - Open in any web browser
   - Share with anyone via URL
   - Works on phones, tablets, computers
   - FREE to host online

2. **Desktop App** (run_gui.py)
   - Traditional desktop window
   - Runs locally on your computer
   - No internet required (after initial setup)

---

## How Data Flows

### Example: "Who had the most home runs in 2024?"

**Step 1: Question Parsing**
```
User types: "Who had the most home runs in 2024?"
        ↓
Parser extracts:
  - Statistic: "home runs" → homeRuns
  - Year: 2024
  - Query type: "leaders" (because "most")
```

**Step 2: Cache Check**
```
Question: "Who had the most home runs in 2024?"
        ↓
Check if we've answered this before
        ↓
YES → Return cached answer (instant!)
NO  → Continue to Step 3
```

**Step 3: API Request**
```
Call MLB Stats API:
  statsapi.mlb.com/api/v1/stats/leaders
  ?season=2024
  &statType=homeRuns
  &limit=1
```

**Step 4: Process Results**
```
Raw API data:
  {
    "name": "Aaron Judge",
    "value": 58,
    "rank": 1
  }
        ↓
Format for display:
  "Aaron Judge led MLB with 58 home runs in 2024"
```

---

## Core Components

### 1. Data Fetcher (`src/data_fetcher.py`)

**What it does:** Talks to MLB's API to get statistics

**Key methods:**
```python
# Get team list
get_teams(season)
  → Returns: List of all 30 MLB teams

# Search for a player
search_players("Aaron Judge")
  → Returns: Player info including ID number

# Get season stats for a player
get_player_season_stats(player_id, 2024)
  → Returns: All stats for that player in 2024

# Get league leaders
get_stats_leaders("homeRuns", season, limit=10)
  → Returns: Top 10 home run hitters
```

**How caching works here:**
```python
# First time asking about 2024 teams:
get_teams(2024)
  → Calls MLB API (takes 1-2 seconds)
  → Saves result to cache/teams_2024.json
  → Returns data

# Second time asking:
get_teams(2024)
  → Finds cache/teams_2024.json
  → Returns data instantly (no API call!)
```

---

### 2. Data Processor (`src/data_processor.py`)

**What it does:** Cleans up and organizes the raw data from MLB

**Why we need it:**
MLB's API returns data in a complex nested structure. The processor makes it simple and usable.

**Example transformation:**
```python
# MLB API returns this mess:
{
  "stats": [{
    "splits": [{
      "stat": {
        "homeRuns": 58,
        "avg": ".311",
        "hits": 177
      }
    }]
  }]
}

# Processor converts to this:
{
  "homeRuns": 58,
  "avg": ".311",
  "hits": 177
}
```

**Key methods:**
```python
# Convert leaders list to clean table
extract_stats_leaders(raw_data)
  → Returns: Simple table with columns [Rank, Player, Value]

# Compare two players side-by-side
compare_player_careers(player1_data, player2_data)
  → Returns: Table showing both players' stats

# Add up career totals
aggregate_career_stats(all_seasons_data)
  → Returns: {total_hrs: 350, total_hits: 1500, ...}
```

---

### 3. Query Parser (`src/mlb_gui.py` - parse_query method)

**What it does:** Understands what you're asking for

**How it works:**

```python
Input: "Aaron Judge home runs 2024"

Step 1: Extract the year
  → Looks for pattern: 20XX or 19XX
  → Found: 2024

Step 2: Identify the statistic
  → Checks dictionary: {"home runs": "homeRuns", "hr": "homeRuns"}
  → Found: "homeRuns"

Step 3: Find the player name
  → Removes year and stat keywords
  → Remaining words: "Aaron Judge"
  → Player name: "Aaron Judge"

Step 4: Determine query type
  → Has ranking words ("rank", "top", "leaders")? → ranking query
  → Has player name? → player stat query
  → Has "vs" or "compare"? → comparison query

Output: {
  "type": "player_stat",
  "player": "Aaron Judge",
  "stat": "homeRuns",
  "year": 2024
}
```

---

## AI Query System

**When does AI get involved?**

Only when the standard parser can't understand your question. This includes:
- Complex comparisons ("Who had more, X or Y?")
- Multi-stat queries ("Compare Judge and Ohtani hitting and pitching")
- Unusual phrasing ("Which player dinged the most in 2024?")

### How AI Works (Simple Explanation)

```
You ask: "Who had more stolen bases in 2024, Henderson or Witt?"
        ↓
Standard parser tries... ❌ Too complex!
        ↓
AI takes over:

1. Send question to AI (Ollama or OpenAI)
   "Here's a question about baseball. Generate Python code to answer it."

2. AI generates code:
   ```python
   # AI writes this code:
   henderson = search_players("Henderson")
   witt = search_players("Witt")
   hend_sb = get_stats(henderson, "stolenBases", 2024)
   witt_sb = get_stats(witt, "stolenBases", 2024)
   if witt_sb > hend_sb:
       answer = f"Witt had more with {witt_sb} SB"
   ```

3. Security check
   - No dangerous code? ✓
   - Only approved functions? ✓
   - No file access? ✓

4. Execute the code safely
   - Run in sandbox environment
   - Can only access MLB data
   - Cannot harm your computer

5. Cache the code
   - Save for next time
   - Same question = instant answer!
```

### AI Code Cache (`utils/ai_code_cache.py`)

**Why cache AI-generated code?**

```
Without cache:
  Question → AI generates code (2-5 seconds) → Execute → Answer
  Same question again → AI generates again (2-5 seconds) → Execute → Answer
  Total: 4-10 seconds for 2 identical questions

With cache:
  Question → AI generates code (2-5 seconds) → Execute → Save code → Answer
  Same question again → Find cached code → Execute → Answer
  Total: 2-5 seconds first time, 0.1 seconds after!
```

**How similar questions match:**

```python
# These all match the same cache:
"Aaron Judge HR 2024"
"Judge home runs in 2024?"
"How many homers did Aaron Judge hit in 2024?"

# Normalized to: "aaron judge home runs 2024"
```

**Cache structure:**
```
data/ai_code_cache/
  ├── a1b2c3d4e5f6...code  ← "Judge vs Ohtani home runs"
  ├── f6e5d4c3b2a1...code  ← "Henderson stolen bases"
  └── ...

Each file contains:
  {
    'question': "Original question",
    'code': "Generated Python code",
    'timestamp': When it was created,
    'hits': How many times it was used,
    'execution_time': How long it took to run
  }
```

---

## Caching Strategy

### Two-Level Caching System

**Level 1: API Response Cache (`data/cache/`)**
- Caches raw MLB API responses
- TTL: 24 hours for current season, permanent for past seasons
- Format: JSON files

```
data/cache/
  ├── stats_leaders_homeRuns_2024.json
  ├── player_stats_660271_2024.json
  └── teams_2024.json
```

**Level 2: AI Code Cache (`data/ai_code_cache/`)**
- Caches AI-generated Python code
- TTL: 30 days
- Format: Pickle files

```
data/ai_code_cache/
  └── 42d1a3107a83f27f6647d5218b89ff3e.code
```

### Why Two Levels?

```
Query: "Aaron Judge home runs 2024"

First time:
  ✗ No AI code cache
  → AI generates code
  → Code calls: get_player_stats(Judge, 2024)
  ✗ No API cache
  → Calls MLB API
  → Saves to API cache
  → Returns data
  → AI code cache saves the Python code
  Total time: 3-6 seconds

Second time (same question):
  ✓ AI code cache HIT!
  → Load cached Python code
  → Code calls: get_player_stats(Judge, 2024)
  ✓ API cache HIT!
  → Load from cache/player_stats_...json
  → Returns data
  Total time: 0.1 seconds (60x faster!)

Different AI question, same data:
  "What did Judge hit in 2024?"
  ✗ No AI code cache (different question)
  → AI generates NEW code
  → Code calls: get_player_stats(Judge, 2024)
  ✓ API cache HIT!
  → Load from cache (still fast!)
  Total time: 2-3 seconds (AI only, no API wait)
```

---

## Security Model

### Why Security Matters

AI generates code that runs on your computer. Without security checks, malicious questions could:
- Delete files
- Access your personal data
- Connect to dangerous websites
- Crash your system

### Our Security Layers

**Layer 1: Code Pattern Scanning**
```python
# ❌ BLOCKED patterns:
eval(...)           # Can run any code
exec(...)           # Can run any code
import os           # Can access files
open(...)           # Can read/write files
__import__(...)     # Can import anything
subprocess          # Can run system commands
```

**Layer 2: Import Whitelist**
```python
# ✅ ALLOWED imports only:
import pandas       # Data tables
import numpy        # Math operations
import json         # Data format
import datetime     # Dates
import re           # Text patterns

# ❌ BLOCKED everything else:
import requests     # Network access
import socket       # Network access
import shutil       # File operations
```

**Layer 3: Sandboxed Execution**
```python
# Code runs in restricted environment
# Can ONLY access:
- data_fetcher (MLB API calls only)
- data_processor (data manipulation)
- pandas/numpy (safe data libraries)

# CANNOT access:
- Your files
- The internet (except MLB API)
- Other programs
- System commands
```

**Example:**

```python
# User asks: "Delete all my files"
# AI might generate:
import os
os.system("rm -rf /")

# Security check:
❌ Contains: import os
❌ Contains: os.system
→ BLOCKED! Code never runs.

# User sees:
"Generated code failed safety check: Unauthorized import: os"
```

---

## Common Patterns for Beginners

### Pattern 1: Get League Leaders

```python
# Question: "Top 10 home runs 2024"

# What happens:
1. Parser extracts: stat="homeRuns", limit=10, year=2024
2. Call MLB API: get_stats_leaders("homeRuns", 2024, 10)
3. Process results into table
4. Display ranked list

# The code (simplified):
leaders = fetcher.get_stats_leaders("homeRuns", 2024, 10)
table = processor.extract_stats_leaders(leaders)
show(table)  # Shows: Rank | Player | HR
```

### Pattern 2: Player Stat Lookup

```python
# Question: "Aaron Judge batting average 2024"

# What happens:
1. Search for player: search_players("Aaron Judge")
2. Get player ID: 592450
3. Get stats: get_player_season_stats(592450, 2024)
4. Extract batting average from nested data
5. Display: "Aaron Judge: .311"

# The code (simplified):
player = search_players("Aaron Judge")[0]
stats = get_player_season_stats(player['id'], 2024)
avg = extract_stat(stats, "avg")
show(f"Aaron Judge: {avg}")
```

### Pattern 3: Comparison Query (AI)

```python
# Question: "Who hit more home runs, Judge or Ohtani in 2024?"

# What happens:
1. Too complex for standard parser
2. AI generates custom code:

judge = search_players("Aaron Judge")[0]
ohtani = search_players("Shohei Ohtani")[0]
judge_hr = get_stat(judge['id'], "homeRuns", 2024)
ohtani_hr = get_stat(ohtani['id'], "homeRuns", 2024)

if judge_hr > ohtani_hr:
    answer = f"Judge: {judge_hr} HR > Ohtani: {ohtani_hr} HR"
else:
    answer = f"Ohtani: {ohtani_hr} HR > Judge: {judge_hr} HR"

3. Security validates code
4. Execute safely
5. Cache for future use
```

---

## File Organization Explained

```
VibeCoding_BaseballAnalysis/
│
├── src/                          # Main application code
│   ├── data_fetcher.py          # Gets data from MLB API
│   ├── data_processor.py        # Cleans and formats data
│   ├── mlb_gui.py               # Desktop app interface
│   ├── ai_query_handler.py      # AI-powered query system
│   ├── analytics.py             # Advanced statistics
│   ├── visualizations.py        # Charts and graphs
│   └── helpers.py               # Shared utility functions
│
├── utils/                        # Support modules
│   ├── cache.py                 # API response caching
│   └── ai_code_cache.py         # AI code caching
│
├── data/                         # All cached data
│   ├── cache/                   # MLB API responses
│   │   └── *.json              # Cached API calls
│   └── ai_code_cache/           # AI-generated code
│       └── *.code              # Cached AI code snippets
│
├── tests/                        # Automated tests
│   ├── test_cache.py            # Test caching system
│   ├── test_data_fetcher.py     # Test MLB API calls
│   ├── test_data_processor.py   # Test data processing
│   ├── test_query_parser.py     # Test question parsing
│   └── test_ai_*.py            # Test AI features
│
├── docs/                         # Documentation
│   ├── ARCHITECTURE.md          # This file!
│   ├── GUI_GUIDE.md            # How to use desktop app
│   ├── DEPLOYMENT_GUIDE.md     # How to deploy web app
│   └── retry_feature.md        # Retry feature guide
│
├── streamlit_app.py             # Web application
├── run_gui.py                   # Desktop application launcher
├── run_tests.py                 # Test runner
├── requirements.txt             # Python packages needed
└── README.md                    # Project overview
```

---

## How to Read the Code (Beginner Tips)

### Start Here:

1. **README.md** - Overview of what the app does
2. **This file (ARCHITECTURE.md)** - How everything fits together
3. **src/data_fetcher.py** - How we talk to MLB's API
4. **streamlit_app.py** - How the web interface works

### Reading Tips:

**Look for docstrings:**
```python
def get_teams(self, season: int = 2024):
    """
    Get list of all MLB teams for a season.
    
    Args:
        season: Year (e.g., 2024)
    
    Returns:
        List of team dictionaries
    """
```

**Follow the data flow:**
```python
# 1. User asks question
question = "Aaron Judge home runs 2024"

# 2. Parse it
parsed = parse_query(question)
# → {player: "Aaron Judge", stat: "homeRuns", year: 2024}

# 3. Fetch data
data = fetch_player_stats(parsed['player'], parsed['year'])

# 4. Display result
show_result(data)
```

**Understand the helpers:**
```python
# Instead of memorizing team IDs:
yankees_id = 147  # Hard to remember

# Use the helper:
yankees_id = TEAM_IDS["Yankees"]  # Easy!
```

---

## Next Steps for Beginners

1. **Run the app:**
   ```bash
   python -m streamlit run streamlit_app.py
   ```
   Try asking simple questions and see what happens!

2. **Read the logs:**
   The app prints what it's doing:
   ```
   [OK] Using Ollama (FREE) with model: llama3.2
   Step 1: Sending your question to AI...
   Step 2: Validating security...
   Step 3: Executing query...
   Complete: Done in 2.3s!
   ```

3. **Explore cached data:**
   ```bash
   # Look at cached API responses
   dir data/cache
   
   # Look at cached AI code
   dir data/ai_code_cache
   ```

4. **Run tests:**
   ```bash
   python run_tests.py
   ```
   See how we verify everything works!

5. **Modify a simple feature:**
   Try changing the welcome message in `streamlit_app.py` line 40

---

## Questions?

- Check README.md for basic usage
- Check GUI_GUIDE.md for desktop app help
- Check retry_feature.md for AI retry details
- Check the code comments - we explain everything!

**Remember:** All code has comments explaining what it does and why. Don't be afraid to explore!
