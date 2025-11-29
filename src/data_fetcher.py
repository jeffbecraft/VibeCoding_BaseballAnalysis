"""
MLB Data Fetcher Module

This module provides functionality to fetch MLB statistics from the MLB Stats API.
"""

import requests
import json
from typing import Dict, List, Optional, Union
from datetime import datetime
import time


class MLBDataFetcher:
    """Fetches data from the MLB Stats API."""
    
    BASE_URL = "https://statsapi.mlb.com/api/v1"
    
    def __init__(self):
        """Initialize the MLB Data Fetcher."""
        self.session = requests.Session()
        
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the MLB Stats API.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response as dictionary
        """
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            return {}
    
    def get_player_stats(self, player_id: int, season: int, 
                        stat_group: str = "hitting") -> Dict:
        """
        Get player statistics for a specific season.
        
        Args:
            player_id: MLB player ID
            season: Season year
            stat_group: Type of stats ('hitting', 'pitching', 'fielding')
            
        Returns:
            Dictionary containing player statistics
        """
        endpoint = f"people/{player_id}"
        params = {
            "hydrate": f"stats(group=[{stat_group}],type=[yearByYear])"
        }
        data = self._make_request(endpoint, params)
        
        if data and "people" in data and len(data["people"]) > 0:
            return data["people"][0]
        return {}
    
    def get_player_season_stats(self, player_id: int, season: int) -> Dict:
        """
        Get comprehensive player statistics for a season.
        
        Args:
            player_id: MLB player ID
            season: Season year
            
        Returns:
            Dictionary with both hitting and pitching stats if available
        """
        endpoint = f"people/{player_id}/stats"
        params = {
            "stats": "season",
            "season": season,
            "group": "hitting,pitching"
        }
        return self._make_request(endpoint, params)
    
    def get_team_stats(self, team_id: int, season: int) -> Dict:
        """
        Get team statistics for a specific season.
        
        Args:
            team_id: MLB team ID
            season: Season year
            
        Returns:
            Dictionary containing team statistics
        """
        endpoint = f"teams/{team_id}/stats"
        params = {
            "stats": "season",
            "season": season
        }
        return self._make_request(endpoint, params)
    
    def get_team_roster(self, team_id: int, season: int) -> List[Dict]:
        """
        Get team roster for a specific season.
        
        Args:
            team_id: MLB team ID
            season: Season year
            
        Returns:
            List of player dictionaries
        """
        endpoint = f"teams/{team_id}/roster"
        params = {
            "rosterType": "active",
            "season": season
        }
        data = self._make_request(endpoint, params)
        
        if data and "roster" in data:
            return data["roster"]
        return []
    
    def search_players(self, name: str) -> List[Dict]:
        """
        Search for players by name.
        
        Args:
            name: Player name to search for
            
        Returns:
            List of matching players
        """
        endpoint = "sports/1/players"
        params = {
            "season": datetime.now().year,
            "gameType": "R"
        }
        data = self._make_request(endpoint, params)
        
        if not data or "people" not in data:
            return []
        
        # Filter by name
        name_lower = name.lower()
        return [
            player for player in data["people"]
            if name_lower in player.get("fullName", "").lower()
        ]
    
    def get_teams(self, season: Optional[int] = None) -> List[Dict]:
        """
        Get all MLB teams.
        
        Args:
            season: Specific season year (optional)
            
        Returns:
            List of team dictionaries
        """
        endpoint = "teams"
        params = {"sportId": 1}
        if season:
            params["season"] = season
            
        data = self._make_request(endpoint, params)
        
        if data and "teams" in data:
            return data["teams"]
        return []
    
    def get_game_stats(self, game_id: int) -> Dict:
        """
        Get statistics for a specific game.
        
        Args:
            game_id: MLB game ID
            
        Returns:
            Dictionary containing game statistics
        """
        endpoint = f"game/{game_id}/boxscore"
        return self._make_request(endpoint)
    
    def get_schedule(self, team_id: int, start_date: str, end_date: str) -> List[Dict]:
        """
        Get team schedule between dates.
        
        Args:
            team_id: MLB team ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of scheduled games
        """
        endpoint = "schedule"
        params = {
            "teamId": team_id,
            "startDate": start_date,
            "endDate": end_date,
            "sportId": 1
        }
        data = self._make_request(endpoint, params)
        
        if data and "dates" in data:
            games = []
            for date_entry in data["dates"]:
                games.extend(date_entry.get("games", []))
            return games
        return []
    
    def get_standings(self, league_id: int, season: int) -> Dict:
        """
        Get league standings for a season.
        
        Args:
            league_id: League ID (103=AL, 104=NL)
            season: Season year
            
        Returns:
            Dictionary containing standings data
        """
        endpoint = f"standings"
        params = {
            "leagueId": league_id,
            "season": season,
            "standingsTypes": "regularSeason"
        }
        return self._make_request(endpoint, params)


if __name__ == "__main__":
    # Example usage
    fetcher = MLBDataFetcher()
    
    # Get teams
    print("Fetching MLB teams...")
    teams = fetcher.get_teams(2024)
    if teams:
        print(f"Found {len(teams)} teams")
        print(f"Example: {teams[0].get('name', 'Unknown')}")
    
    # Search for a player
    print("\nSearching for Aaron Judge...")
    players = fetcher.search_players("Aaron Judge")
    if players:
        player = players[0]
        print(f"Found: {player.get('fullName')} (ID: {player.get('id')})")
