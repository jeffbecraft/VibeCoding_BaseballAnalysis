# MLB Statistics Natural Language Query GUI

A graphical user interface that allows you to query MLB statistics using natural language questions.

## Features

- **Natural Language Processing**: Ask questions in plain English
- **Player Rankings**: Find where specific players rank in various statistics
- **Stats Leaders**: View top performers in any statistical category
- **Flexible Queries**: Specify player names, statistics, and years naturally

## How to Run

### Option 1: Using the Launcher Script
```powershell
python run_gui.py
```

### Option 2: Direct Execution
```powershell
cd src
python mlb_gui.py
```

## Example Questions

The GUI understands natural language questions like:

### Player Ranking Queries
- "Where did Gunnar Henderson rank in stolen bases in 2025?"
- "What was Aaron Judge's home run ranking in 2024?"
- "Find Shohei Ohtani's rank in home runs for 2024"
- "Where did Max Fried rank in ERA for 2025?"

### Leaders Queries
- "Show me the top 10 ERA leaders in 2025"
- "Who are the stolen base leaders for 2025?"
- "Top 20 home run leaders in 2024"
- "Show the top 5 batting average leaders"

### Team-Specific Queries
- "Top 10 home run leaders for the Yankees in 2025"
- "Show me the Orioles batting average leaders"
- "Who are the top 5 RBI leaders for the Dodgers?"
- "Top ERA leaders for the Red Sox in 2024"

### League-Specific Queries
- "Top ERA leaders in the American League for 2025"
- "National League stolen base leaders in 2024"
- "Show me the top 15 batting average leaders in the AL"
- "Who are the NL home run leaders?"

## Supported Statistics

### Hitting Statistics
- Home Runs (home runs, HR, homers)
- Stolen Bases (stolen bases, steals, SB)
- Batting Average (batting average, average, AVG)
- RBI (runs batted in, RBI)
- Hits
- Doubles
- Triples
- Runs
- Walks
- On-Base Percentage (OBP)
- Slugging Percentage (SLG, slugging)
- OPS

### Pitching Statistics
- ERA (earned run average)
- Wins
- Saves
- Strikeouts
- WHIP
- Innings Pitched (innings)

## How It Works

1. **Type your question** in the input field using natural language
2. **Press Enter or click "Ask Question"** to submit
3. **View results** in the results area below

The system will:
- Parse your question to extract the player name, statistic, and year
- Show you what it understood
- Fetch data from the MLB Stats API
- Display the ranking or leaders list

## Query Format Tips

For best results:
- **Include the statistic name** (e.g., "home runs", "ERA", "stolen bases")
- **Capitalize player names** (e.g., "Aaron Judge", "Shohei Ohtani")
- **Include the year** as a 4-digit number (e.g., "2024", "2025")
- **Specify team names** to filter by team (e.g., "Yankees", "Dodgers", "Orioles")
- **Mention league** to filter by league (e.g., "American League", "National League", "AL", "NL")
- If no year is specified, the current season is used
- **Note**: When filtering by team or league, ALL players from that team/league are shown (limit is ignored)

## Technical Details

- Built with Python's tkinter for the GUI
- Uses the MLB Stats API for data
- Supports querying top 100 leaders for player rankings
- Default shows top 10 leaders (can be customized with "top X" in your query)
- Filters by team: Recognizes all 30 MLB team names
- Filters by league: American League (AL) and National League (NL)

## Requirements

- Python 3.8+
- Required packages: pandas, requests, tkinter (usually included with Python)
- Active internet connection (to access MLB Stats API)

## Troubleshooting

**"Could not understand the question"**
- Make sure to include a recognized statistic name
- Check that player names are capitalized

**"Player not found in leaders"**
- Player may not be in the top 100 for that statistic
- Verify the player name spelling
- Check if the statistic type matches (hitting vs pitching)

**"No data found"**
- The API may not have data for that specific year/stat combination
- Try a different year or statistic
