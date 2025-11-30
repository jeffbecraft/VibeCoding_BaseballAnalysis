"""
MLB Statistics Natural Language Query GUI

This application provides a graphical interface for querying MLB statistics
using natural language questions.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import re
from typing import Optional, Dict, Tuple, List
from data_fetcher import MLBDataFetcher
from data_processor import MLBDataProcessor
from helpers import get_team_name, get_current_season, TEAM_IDS, LEAGUE_IDS
from stat_constants import STAT_MAPPINGS, PITCHING_STATS


class MLBQueryGUI:
    """GUI application for natural language MLB statistics queries."""
    
    # Use shared stat mappings from stat_constants module
    STAT_MAPPINGS = STAT_MAPPINGS
    
    # Use shared pitching stats list
    PITCHING_STATS = PITCHING_STATS
    
    def __init__(self, root):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("MLB Statistics Natural Language Query")
        self.root.geometry("900x700")
        
        # Initialize API clients
        self.fetcher = MLBDataFetcher()
        self.processor = MLBDataProcessor()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface components."""
        # Title
        title_label = tk.Label(
            self.root,
            text="MLB Statistics Query System",
            font=("Arial", 18, "bold"),
            pady=10
        )
        title_label.pack()
        
        # Instructions
        instructions = tk.Label(
            self.root,
            text="Ask questions in natural language about MLB statistics",
            font=("Arial", 10),
            pady=5
        )
        instructions.pack()
        
        # Examples frame
        examples_frame = tk.LabelFrame(
            self.root,
            text="Example Questions",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        examples_frame.pack(fill="x", padx=20, pady=10)
        
        examples = [
            "Where did Gunnar Henderson rank in stolen bases in 2025?",
            "What was Aaron Judge's home run ranking in 2024?",
            "Show me the top 10 ERA leaders in 2025",
            "Who are the stolen base leaders for 2025?",
            "Find Shohei Ohtani's rank in home runs for 2024",
            "Top 10 home run leaders for the Yankees in 2025",
            "Show me the Orioles batting average leaders",
            "Top ERA leaders in the American League for 2025",
            "National League stolen base leaders in 2024"
        ]
        
        for example in examples:
            tk.Label(
                examples_frame,
                text=f"• {example}",
                font=("Arial", 9),
                anchor="w"
            ).pack(fill="x")
        
        # Query input frame
        input_frame = tk.Frame(self.root, padx=20, pady=10)
        input_frame.pack(fill="x")
        
        tk.Label(
            input_frame,
            text="Your Question:",
            font=("Arial", 11, "bold")
        ).pack(anchor="w")
        
        self.query_entry = tk.Entry(
            input_frame,
            font=("Arial", 11),
            width=70
        )
        self.query_entry.pack(fill="x", pady=5)
        self.query_entry.bind("<Return>", lambda e: self.process_query())
        
        # Buttons
        button_frame = tk.Frame(self.root, padx=20)
        button_frame.pack(fill="x")
        
        tk.Button(
            button_frame,
            text="Ask Question",
            command=self.process_query,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=5
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame,
            text="Clear",
            command=self.clear_results,
            bg="#f44336",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=5
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame,
            text="Cache Stats",
            command=self.show_cache_stats,
            bg="#2196F3",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=5
        ).pack(side="left", padx=5)
        
        tk.Button(
            button_frame,
            text="Clear Cache",
            command=self.clear_cache,
            bg="#FF9800",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=5
        ).pack(side="left", padx=5)
        
        # Results area
        results_frame = tk.LabelFrame(
            self.root,
            text="Results",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10
        )
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            font=("Courier", 10),
            wrap=tk.WORD,
            height=20
        )
        self.results_text.pack(fill="both", expand=True)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Arial", 9)
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def parse_query(self, query: str) -> Optional[Dict]:
        """
        Parse natural language query to extract parameters.
        
        Args:
            query: Natural language question
            
        Returns:
            Dictionary with parsed parameters or None if parsing fails
        """
        query_lower = query.lower()
        
        # Extract year (4-digit number)
        year_match = re.search(r'\b(20\d{2})\b', query)
        year = int(year_match.group(1)) if year_match else get_current_season()
        
        # Extract statistic category
        stat_type = None
        stat_group = "hitting"
        
        for term, api_name in self.STAT_MAPPINGS.items():
            # Use word boundaries to match complete words only
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, query_lower):
                stat_type = api_name
                if api_name in self.PITCHING_STATS:
                    stat_group = "pitching"
                break
        
        if not stat_type:
            return None
        
        # Extract team name
        team_id = None
        team_name = None
        for name, tid in TEAM_IDS.items():
            if name.lower() in query_lower:
                team_id = tid
                team_name = name
                break
        
        # Extract league
        league_id = None
        league_name = None
        if 'american league' in query_lower or ' al ' in query_lower:
            league_id = LEAGUE_IDS["American League"]
            league_name = "American League"
        elif 'national league' in query_lower or ' nl ' in query_lower:
            league_id = LEAGUE_IDS["National League"]
            league_name = "National League"
        
        # Extract player name (capitalized words, but not common query words, teams, or leagues)
        # Remove query words first
        query_words = {'where', 'did', 'rank', 'what', 'was', 'show', 'me', 'the', 'top',
                       'who', 'are', 'in', 'for', 'find', 'leaders', 'ranking', 'get', 'era',
                       'rbi', 'mlb', 'season', 'year', 'player', 'players', 'stats', 'statistics',
                       'which', 'when', 'how', 'had', 'has', 'have'}
        
        # Words to exclude from player name matching
        exclude_words = query_words.copy()
        if team_name:
            exclude_words.update(team_name.lower().split())
        if league_name:
            exclude_words.update(league_name.lower().split())
        
        # Look for patterns like "Player Name's", "First Last", or single last names
        # Try multi-word patterns first, then single words
        name_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)(?:\'s)?\b',  # Multi-word capitalized names
            r'\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b',  # First Last name pattern
            r'\b([A-Z][a-z]{2,})(?:\'s)?\b'  # Single capitalized word (at least 3 letters, potential last name)
        ]
        
        player_name = None
        for pattern in name_patterns:
            matches = re.finditer(pattern, query)
            for name_match in matches:
                potential_name = name_match.group(0).replace("'s", "").strip()
                potential_name_lower = potential_name.lower()
                
                # Check if it's not a query word, team name, or league name
                # For single words, be extra careful to exclude common words
                words_in_name = potential_name_lower.split()
                if all(word not in exclude_words for word in words_in_name):
                    if (potential_name_lower != team_name.lower() if team_name else True and
                        potential_name_lower != league_name.lower() if league_name else True and
                        'league' not in potential_name_lower):
                        player_name = potential_name
                        break
            
            if player_name:
                break
        
        # Check if ranking is requested (look for ranking keywords)
        ranking_keywords = ['rank', 'leader', 'leaders', 'top', 'best', 'worst', 'leading']
        wants_ranking = any(keyword in query_lower for keyword in ranking_keywords)
        
        # Determine query type
        query_type = "leaders"  # default
        
        # Check if this is a team ranking query
        team_ranking_keywords = ['teams', 'team', 'which team', 'what team']
        is_team_query = any(keyword in query_lower for keyword in team_ranking_keywords)
        if is_team_query and not player_name:
            query_type = "team_rank"
        elif player_name and wants_ranking:
            query_type = "rank"  # Player ranking query
        elif player_name and not wants_ranking:
            query_type = "player_stat"  # Just get the stat, no ranking
        
        # Extract limit for leaders queries
        limit = 10
        limit_match = re.search(r'\btop\s+(\d+)\b', query_lower)
        if limit_match:
            limit = int(limit_match.group(1))
        
        return {
            'player_name': player_name,
            'stat_type': stat_type,
            'stat_group': stat_group,
            'year': year,
            'query_type': query_type,
            'limit': limit,
            'team_id': team_id,
            'team_name': team_name,
            'league_id': league_id,
            'league_name': league_name
        }
    
    def find_player_rank(self, player_name: str, stat_type: str, 
                        stat_group: str, year: int,
                        team_id: Optional[int] = None,
                        league_id: Optional[int] = None) -> List[Dict]:
        """
        Find a player's rank in a specific statistic.
        
        Args:
            player_name: Name of the player (can be full name or last name only)
            stat_type: Statistic type
            stat_group: 'hitting' or 'pitching'
            year: Season year
            team_id: Filter by team ID (optional)
            league_id: Filter by league ID (optional)
            
        Returns:
            List of matching player dictionaries with rank information (empty if not found)
        """
        # Get complete rankings for all players
        leaders = self.fetcher.get_stats_leaders(
            stat_type=stat_type,
            season=year,
            limit=None,
            stat_group=stat_group,
            team_id=team_id,
            league_id=league_id,
            include_all=True  # Get ALL players for accurate ranking
        )
        
        matches = []
        
        if leaders:
            # Search for the player in leaders
            name_lower = player_name.lower().strip()
            
            for leader in leaders:
                person = leader.get('person', {})
                full_name = person.get('fullName', '')
                full_name_lower = full_name.lower()
                last_name = person.get('lastName', '').lower()
                
                # Match if:
                # 1. Search term matches full name (substring)
                # 2. Search term matches last name exactly (for last-name-only searches)
                # 3. Full name contains search term as a word
                if (name_lower in full_name_lower or 
                    name_lower == last_name or
                    full_name_lower in name_lower):
                    
                    team = leader.get('team', {})
                    matches.append({
                        'rank': leader.get('rank'),
                        'player_name': full_name,
                        'team': team.get('name', get_team_name(team.get('id'))),
                        'value': leader.get('value'),
                        'stat_type': stat_type,
                        'year': year
                    })
        
        # If no matches in leaders, try to find them directly via API search
        if not matches:
            players = self.fetcher.search_players(player_name)
            
            for player in players:
                player_id = player.get('id')
                full_name = player.get('fullName', '')
                
                # Get player's season stats
                stats = self.fetcher.get_player_season_stats(player_id, year)
                
                if stats and 'stats' in stats:
                    for stat_group_data in stats['stats']:
                        group = stat_group_data.get('group', {}).get('displayName', '')
                        
                        if (stat_group == 'hitting' and group == 'hitting') or \
                           (stat_group == 'pitching' and group == 'pitching'):
                            
                            splits = stat_group_data.get('splits', [])
                            if splits:
                                stat = splits[0].get('stat', {})
                                value = stat.get(stat_type)
                                
                                if value is not None:
                                    # Get player's team
                                    team_info = splits[0].get('team', {})
                                    
                                    matches.append({
                                        'rank': 'N/A',  # Not in top leaders
                                        'player_name': full_name,
                                        'team': team_info.get('name', 'N/A'),
                                        'value': value,
                                        'stat_type': stat_type,
                                        'year': year,
                                        'not_in_leaders': True
                                    })
                                    break
        
        return matches
    
    def get_player_stat_simple(self, player_name: str, stat_type: str,
                               stat_group: str, year: int) -> List[Dict]:
        """
        Get a player's stat value without ranking (faster).
        
        Args:
            player_name: Name of the player
            stat_type: Statistic type
            stat_group: 'hitting' or 'pitching'
            year: Season year
            
        Returns:
            List of matching player dictionaries with stat values (no ranking)
        """
        # Search for the player
        players = self.fetcher.search_players(player_name)
        
        if not players:
            return []
        
        matches = []
        
        for player in players:
            player_id = player.get('id')
            full_name = player.get('fullName', '')
            last_name = player.get('lastName', '').lower()
            player_name_lower = player_name.lower()
            
            # Check if this player matches the search
            if not (player_name_lower in full_name.lower() or 
                   player_name_lower == last_name):
                continue
            
            # Get player's season stats
            stats = self.fetcher.get_player_season_stats(player_id, year)
            
            if stats and 'stats' in stats:
                for stat_group_data in stats['stats']:
                    group = stat_group_data.get('group', {}).get('displayName', '')
                    
                    if (stat_group == 'hitting' and group == 'hitting') or \
                       (stat_group == 'pitching' and group == 'pitching'):
                        
                        splits = stat_group_data.get('splits', [])
                        if splits:
                            stat = splits[0].get('stat', {})
                            value = stat.get(stat_type)
                            
                            if value is not None:
                                # Get player's team
                                team_info = splits[0].get('team', {})
                                
                                matches.append({
                                    'player_name': full_name,
                                    'team': team_info.get('name', 'N/A'),
                                    'value': value,
                                    'stat_type': stat_type,
                                    'year': year
                                })
                                break
        
        return matches
    
    def get_stat_display_name(self, stat_type: str) -> str:
        """Get human-readable name for a stat type."""
        reverse_mapping = {v: k for k, v in self.STAT_MAPPINGS.items()}
        # Get first matching key, capitalize it
        for key, value in self.STAT_MAPPINGS.items():
            if value == stat_type:
                return key.title()
        return stat_type
    
    def process_query(self):
        """Process the natural language query."""
        query = self.query_entry.get().strip()
        
        if not query:
            messagebox.showwarning("Empty Query", "Please enter a question.")
            return
        
        self.status_var.set("Processing query...")
        self.results_text.delete(1.0, tk.END)
        
        try:
            # Parse the query
            params = self.parse_query(query)
            
            if not params:
                self.results_text.insert(tk.END, "❌ Could not understand the question.\n\n")
                self.results_text.insert(tk.END, "Please make sure to include:\n")
                self.results_text.insert(tk.END, "- A statistic (e.g., home runs, stolen bases, ERA)\n")
                self.results_text.insert(tk.END, "- Optionally: a player name and/or year\n")
                self.status_var.set("Query not understood")
                return
            
            # Display what was understood
            self.results_text.insert(tk.END, "📊 Query Understanding:\n")
            self.results_text.insert(tk.END, "=" * 60 + "\n")
            self.results_text.insert(tk.END, f"Statistic: {self.get_stat_display_name(params['stat_type'])}\n")
            self.results_text.insert(tk.END, f"Category: {params['stat_group'].title()}\n")
            self.results_text.insert(tk.END, f"Season: {params['year']}\n")
            if params['player_name']:
                self.results_text.insert(tk.END, f"Player: {params['player_name']}\n")
            if params['team_name']:
                self.results_text.insert(tk.END, f"Team Filter: {params['team_name']}\n")
            if params['league_name']:
                self.results_text.insert(tk.END, f"League Filter: {params['league_name']}\n")
            self.results_text.insert(tk.END, "=" * 60 + "\n\n")
            
            # Process based on query type
            if params['query_type'] == 'team_rank':
                # Rank teams by statistic
                self.status_var.set("Fetching team statistics...")
                
                team_stats = self.fetcher.get_team_stats(
                    season=params['year'],
                    stat_group=params['stat_group']
                )
                
                if team_stats:
                    teams_df = self.processor.extract_team_stats(
                        team_stats,
                        params['stat_type']
                    )
                    
                    if not teams_df.empty:
                        self.results_text.insert(tk.END, f"🏆 Team Rankings by {self.get_stat_display_name(params['stat_type'])} ({params['year']}):\n")
                        self.results_text.insert(tk.END, "=" * 60 + "\n\n")
                        self.results_text.insert(tk.END, teams_df.to_string(index=False))
                        self.results_text.insert(tk.END, "\n")
                        self.status_var.set(f"Showing {len(teams_df)} teams")
                    else:
                        self.results_text.insert(tk.END, f"❌ No team data found for {self.get_stat_display_name(params['stat_type'])}.\n")
                        self.status_var.set("No team data found")
                else:
                    self.results_text.insert(tk.END, "❌ Could not fetch team statistics.\n")
                    self.status_var.set("Error fetching team stats")
            
            elif params['query_type'] == 'player_stat' and params['player_name']:
                # Get player's stat without ranking (faster)
                matches = self.get_player_stat_simple(
                    params['player_name'],
                    params['stat_type'],
                    params['stat_group'],
                    params['year']
                )
                
                if matches:
                    # Show results for all matching players
                    if len(matches) == 1:
                        self.results_text.insert(tk.END, "📊 Player Statistics:\n")
                    else:
                        self.results_text.insert(tk.END, f"📊 Found {len(matches)} Players Matching '{params['player_name']}':\n")
                    
                    self.results_text.insert(tk.END, "=" * 60 + "\n")
                    
                    for idx, stat_info in enumerate(matches):
                        if idx > 0:
                            self.results_text.insert(tk.END, "-" * 60 + "\n")
                        
                        self.results_text.insert(tk.END, f"Player: {stat_info['player_name']}\n")
                        self.results_text.insert(tk.END, f"Team: {stat_info['team']}\n")
                        self.results_text.insert(tk.END, f"{self.get_stat_display_name(params['stat_type'])}: {stat_info['value']}\n")
                    
                    self.results_text.insert(tk.END, "=" * 60 + "\n")
                    
                    if len(matches) == 1:
                        status_msg = f"Found {matches[0]['player_name']}'s stats"
                    else:
                        status_msg = f"Found {len(matches)} players matching '{params['player_name']}'"
                    self.status_var.set(status_msg)
                else:
                    self.results_text.insert(tk.END, f"❌ Could not find {params['player_name']} ")
                    self.results_text.insert(tk.END, f"for {params['year']}.\n")
                    self.status_var.set("Player not found")
                    
            elif params['query_type'] == 'rank' and params['player_name']:
                # Find player's rank (returns list of matches)
                matches = self.find_player_rank(
                    params['player_name'],
                    params['stat_type'],
                    params['stat_group'],
                    params['year'],
                    team_id=params['team_id'],
                    league_id=params['league_id']
                )
                
                if matches:
                    # Show results for all matching players
                    if len(matches) == 1:
                        self.results_text.insert(tk.END, "🎯 Player Ranking:\n")
                    else:
                        self.results_text.insert(tk.END, f"🎯 Found {len(matches)} Players Matching '{params['player_name']}':\n")
                    
                    self.results_text.insert(tk.END, "=" * 60 + "\n")
                    
                    for idx, rank_info in enumerate(matches):
                        if idx > 0:
                            self.results_text.insert(tk.END, "-" * 60 + "\n")
                        
                        self.results_text.insert(tk.END, f"Player: {rank_info['player_name']}\n")
                        self.results_text.insert(tk.END, f"Team: {rank_info['team']}\n")
                        
                        if rank_info.get('not_in_leaders'):
                            self.results_text.insert(tk.END, f"Rank: Not in top leaders\n")
                        else:
                            self.results_text.insert(tk.END, f"Rank: #{rank_info['rank']}\n")
                        
                        self.results_text.insert(tk.END, f"{self.get_stat_display_name(params['stat_type'])}: {rank_info['value']}\n")
                    
                    self.results_text.insert(tk.END, "=" * 60 + "\n")
                    
                    if len(matches) == 1:
                        status_msg = f"Found {matches[0]['player_name']}"
                        if not matches[0].get('not_in_leaders'):
                            status_msg += f" at rank #{matches[0]['rank']}"
                    else:
                        status_msg = f"Found {len(matches)} players matching '{params['player_name']}'"
                    self.status_var.set(status_msg)
                else:
                    filter_context = ""
                    if params['team_name']:
                        filter_context = f" on the {params['team_name']}"
                    elif params['league_name']:
                        filter_context = f" in the {params['league_name']}"
                    
                    self.results_text.insert(tk.END, f"❌ Could not find {params['player_name']} ")
                    self.results_text.insert(tk.END, f"in {self.get_stat_display_name(params['stat_type'])} ")
                    self.results_text.insert(tk.END, f"leaders{filter_context} for {params['year']}.\n")
                    self.status_var.set("Player not found in leaders")
            else:
                # Show leaders
                # When filtering by team/league, get all players for accurate ranking
                include_all = bool(params['team_id'] or params['league_id'])
                
                leaders = self.fetcher.get_stats_leaders(
                    stat_type=params['stat_type'],
                    season=params['year'],
                    limit=params['limit'],
                    stat_group=params['stat_group'],
                    team_id=params['team_id'],
                    league_id=params['league_id'],
                    include_all=include_all
                )
                
                if leaders:
                    leaders_df = self.processor.extract_stats_leaders(leaders)
                    
                    # If filtered by team/league, show actual count instead of requested limit
                    if params['team_id'] or params['league_id']:
                        display_count = len(leaders_df)
                    else:
                        display_count = params['limit']
                    
                    # Build title with filters
                    title_parts = [f"Top {display_count}"]
                    if params['team_name']:
                        title_parts.append(params['team_name'])
                    if params['league_name']:
                        title_parts.append(params['league_name'])
                    title_parts.append(f"{self.get_stat_display_name(params['stat_type'])} Leaders")
                    title_parts.append(f"({params['year']})")
                    
                    self.results_text.insert(tk.END, f"🏆 {' '.join(title_parts)}:\n")
                    self.results_text.insert(tk.END, "=" * 60 + "\n\n")
                    self.results_text.insert(tk.END, leaders_df.to_string(index=False))
                    self.results_text.insert(tk.END, "\n")
                    self.status_var.set(f"Showing {display_count} leaders")
                else:
                    self.results_text.insert(tk.END, "❌ No data found for this query.\n")
                    self.status_var.set("No data found")
                    
        except Exception as e:
            self.results_text.insert(tk.END, f"❌ Error processing query: {str(e)}\n")
            self.status_var.set(f"Error: {str(e)}")
    
    def clear_results(self):
        """Clear the results and query input."""
        self.query_entry.delete(0, tk.END)
        self.results_text.delete(1.0, tk.END)
        self.status_var.set("Ready")
    
    def show_cache_stats(self):
        """Display cache statistics."""
        stats = self.fetcher.get_cache_stats()
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "📦 Cache Statistics:\n")
        self.results_text.insert(tk.END, "=" * 60 + "\n\n")
        
        if 'error' in stats:
            self.results_text.insert(tk.END, f"❌ {stats['error']}\n")
        else:
            self.results_text.insert(tk.END, f"Cache Directory: {stats.get('cache_dir', 'N/A')}\n")
            self.results_text.insert(tk.END, f"Total Entries: {stats.get('total_entries', 0)}\n")
            self.results_text.insert(tk.END, f"Valid Entries: {stats.get('valid_entries', 0)}\n")
            self.results_text.insert(tk.END, f"Expired Entries: {stats.get('expired_entries', 0)}\n")
            self.results_text.insert(tk.END, f"Total Size: {stats.get('total_size_mb', 0)} MB\n")
            self.results_text.insert(tk.END, "\n💡 Cached data speeds up queries by avoiding API calls.\n")
            self.results_text.insert(tk.END, "Cache entries expire after 24 hours by default.\n")
        
        self.status_var.set("Cache stats displayed")
    
    def clear_cache(self):
        """Clear the cache after confirmation."""
        result = messagebox.askyesno(
            "Clear Cache",
            "Are you sure you want to clear all cached data?\n\nThis will remove all stored API responses."
        )
        
        if result:
            self.fetcher.clear_cache()
            messagebox.showinfo("Cache Cleared", "All cached data has been removed.")
            self.status_var.set("Cache cleared")


def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    app = MLBQueryGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
