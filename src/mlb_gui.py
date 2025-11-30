"""
MLB Statistics Natural Language Query GUI

This application provides a graphical interface for querying MLB statistics
using natural language questions.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import re
from typing import Optional, Dict, Tuple
from data_fetcher import MLBDataFetcher
from data_processor import MLBDataProcessor
from helpers import get_team_name, get_current_season


class MLBQueryGUI:
    """GUI application for natural language MLB statistics queries."""
    
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
    PITCHING_STATS = {'era', 'wins', 'saves', 'whip', 'inningsPitched'}
    
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
            "Find Shohei Ohtani's rank in home runs for 2024"
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
            if term in query_lower:
                stat_type = api_name
                if api_name in self.PITCHING_STATS:
                    stat_group = "pitching"
                break
        
        if not stat_type:
            return None
        
        # Extract player name (capitalized words, but not common query words)
        # Remove query words first
        query_words = {'where', 'did', 'rank', 'what', 'was', 'show', 'me', 'the', 'top',
                       'who', 'are', 'in', 'for', 'find', 'leaders', 'ranking', 'get'}
        
        # Look for patterns like "Player Name's" or just capitalized names
        name_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)(?:\'s)?\b',  # Multi-word capitalized names
            r'\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b'  # First Last name pattern
        ]
        
        player_name = None
        for pattern in name_patterns:
            name_match = re.search(pattern, query)
            if name_match:
                potential_name = name_match.group(0).replace("'s", "").strip()
                # Check if it's not a query word
                if potential_name.lower().split()[0] not in query_words:
                    player_name = potential_name
                    break
        
        # Determine if it's a leaders query or player rank query
        query_type = "rank" if player_name else "leaders"
        
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
            'limit': limit
        }
    
    def find_player_rank(self, player_name: str, stat_type: str, 
                        stat_group: str, year: int) -> Optional[Dict]:
        """
        Find a player's rank in a specific statistic.
        
        Args:
            player_name: Name of the player
            stat_type: Statistic type
            stat_group: 'hitting' or 'pitching'
            year: Season year
            
        Returns:
            Dictionary with rank information or None if not found
        """
        # Get top 100 to have better chance of finding the player
        leaders = self.fetcher.get_stats_leaders(
            stat_type=stat_type,
            season=year,
            limit=100,
            stat_group=stat_group
        )
        
        if not leaders:
            return None
        
        # Search for the player
        name_lower = player_name.lower()
        for leader in leaders:
            person = leader.get('person', {})
            full_name = person.get('fullName', '').lower()
            
            if name_lower in full_name or full_name in name_lower:
                team = leader.get('team', {})
                return {
                    'rank': leader.get('rank'),
                    'player_name': person.get('fullName'),
                    'team': team.get('name', get_team_name(team.get('id'))),
                    'value': leader.get('value'),
                    'stat_type': stat_type,
                    'year': year
                }
        
        return None
    
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
            self.results_text.insert(tk.END, "=" * 60 + "\n\n")
            
            # Process based on query type
            if params['query_type'] == 'rank' and params['player_name']:
                # Find player's rank
                rank_info = self.find_player_rank(
                    params['player_name'],
                    params['stat_type'],
                    params['stat_group'],
                    params['year']
                )
                
                if rank_info:
                    self.results_text.insert(tk.END, "🎯 Player Ranking:\n")
                    self.results_text.insert(tk.END, "=" * 60 + "\n")
                    self.results_text.insert(tk.END, f"Player: {rank_info['player_name']}\n")
                    self.results_text.insert(tk.END, f"Team: {rank_info['team']}\n")
                    self.results_text.insert(tk.END, f"Rank: #{rank_info['rank']}\n")
                    self.results_text.insert(tk.END, f"Value: {rank_info['value']}\n")
                    self.results_text.insert(tk.END, "=" * 60 + "\n")
                    self.status_var.set(f"Found {rank_info['player_name']} at rank #{rank_info['rank']}")
                else:
                    self.results_text.insert(tk.END, f"❌ Could not find {params['player_name']} ")
                    self.results_text.insert(tk.END, f"in the top 100 {self.get_stat_display_name(params['stat_type'])} ")
                    self.results_text.insert(tk.END, f"leaders for {params['year']}.\n")
                    self.status_var.set("Player not found in leaders")
            else:
                # Show leaders
                leaders = self.fetcher.get_stats_leaders(
                    stat_type=params['stat_type'],
                    season=params['year'],
                    limit=params['limit'],
                    stat_group=params['stat_group']
                )
                
                if leaders:
                    leaders_df = self.processor.extract_stats_leaders(leaders)
                    
                    self.results_text.insert(tk.END, f"🏆 Top {params['limit']} {self.get_stat_display_name(params['stat_type'])} Leaders ({params['year']}):\n")
                    self.results_text.insert(tk.END, "=" * 60 + "\n\n")
                    self.results_text.insert(tk.END, leaders_df.to_string(index=False))
                    self.results_text.insert(tk.END, "\n")
                    self.status_var.set(f"Showing top {params['limit']} leaders")
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


def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    app = MLBQueryGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
