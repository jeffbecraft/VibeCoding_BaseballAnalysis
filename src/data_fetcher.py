"""
MLB Data Fetcher Module

This module provides functionality to fetch MLB statistics from the MLB Stats API.
It handles all the communication with the official MLB API to get player and team data.
"""

# Import statements - these bring in code libraries we need to use
import requests  # This library helps us make requests to websites/APIs on the internet
import json  # This library helps us work with JSON data (a common data format)
from typing import Dict, List, Optional, Union  # These help us specify what type of data to expect
from datetime import datetime  # This helps us work with dates and times
import time  # This helps us work with time-related functions


class MLBDataFetcher:
    """
    This class is responsible for fetching (getting) data from the MLB Stats API.
    
    Think of this class as a messenger that goes to MLB's website and brings back
    information about players, teams, and games.
    """
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the MLB Stats API.
        
        This is a helper function (the underscore _ prefix means it's for internal use).
        It handles the actual communication with the MLB API.
        
        Args:
            endpoint: The specific part of the API we want to access (like "teams" or "players")
            params: Optional additional parameters to customize our request
            
        Returns:
            A dictionary containing the data we requested from the API
        """
        # Build the complete URL by combining the base URL with the specific endpoint
        # For example: "https://statsapi.mlb.com/api/v1/teams"
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            # Try to get data from the URL
            # timeout=10 means we'll wait up to 10 seconds for a response
            response = self.session.get(url, params=params, timeout=10)
            
            # Check if the request was successful (no errors from the server)
            response.raise_for_status()
            
            # Convert the response from JSON format into a Python dictionary
            # and return it so other functions can use the data
            return response.json()
            
        except requests.exceptions.RequestException as e:
            # If something went wrong (like no internet connection or bad URL),
            # print an error message and return an empty dictionary
            print(f"Error fetching data from {url}: {e}")
            return {}t to the MLB Stats API.
        
    def get_player_stats(self, player_id: int, season: int, 
                        stat_group: str = "hitting") -> Dict:
        """
        Get player statistics for a specific season.
        
        This function retrieves all the statistics for a particular player
        (like batting average, home runs, etc.) for a given year.
        
        Args:
            player_id: The unique ID number that MLB assigns to each player
            season: The year you want stats for (like 2024)
            stat_group: What type of stats you want: 'hitting', 'pitching', or 'fielding'
            
        Returns:
            A dictionary containing all the player's statistics
        """
        # Create the endpoint (URL path) to get this specific player's data
        # For example: "people/660271" for Aaron Judge
        endpoint = f"people/{player_id}"
        
        # Set up the parameters to specify what data we want
        # "hydrate" tells the API to include detailed stats
        # We're asking for year-by-year stats for the specified stat group
        params = {
            "hydrate": f"stats(group=[{stat_group}],type=[yearByYear])"
        }
        
        # Make the actual request to the API
        data = self._make_request(endpoint, params)
        
        # Check if we got valid data back
        # We check: 1) Did we get any data? 2) Does it have a "people" key? 3) Is there at least one person?
        if data and "people" in data and len(data["people"]) > 0:
            # Return the first (and only) player's data
            return data["people"][0]
        
        # If we didn't get valid data, return an empty dictionary
        return {}
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
