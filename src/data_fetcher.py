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
            "gameType": "R",
            "hydrate": "currentTeam(league)"
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
    
    def get_team_player_stats(self, team_id: int, season: int, 
                              stat_group: str = "hitting") -> List[Dict]:
        """
        Get all player statistics for a specific team.
        
        Args:
            team_id: MLB team ID
            season: Season year
            stat_group: 'hitting' or 'pitching'
            
        Returns:
            List of player stat dictionaries
        """
        # Get team roster
        roster = self.get_team_roster(team_id, season)
        
        if not roster:
            return []
        
        # Get stats for each player
        all_stats = []
        for player_data in roster:
            person = player_data.get('person', {})
            player_id = person.get('id')
            
            if not player_id:
                continue
            
            # Get player stats
            stats = self.get_player_season_stats(player_id, season)
            
            if stats and 'stats' in stats:
                for stat_group_data in stats['stats']:
                    group = stat_group_data.get('group', {}).get('displayName', '')
                    
                    # Check if this is the stat group we want
                    if (stat_group == 'hitting' and group == 'hitting') or \
                       (stat_group == 'pitching' and group == 'pitching'):
                        
                        splits = stat_group_data.get('splits', [])
                        
                        # Find the split for this specific team
                        team_stat = None
                        for split in splits:
                            split_team = split.get('team', {})
                            if split_team.get('id') == team_id:
                                team_stat = split.get('stat', {})
                                break
                        
                        # If we found stats for this team, add them
                        if team_stat:
                            all_stats.append({
                                'person': person,
                                'team': {'id': team_id},
                                'stat': team_stat
                            })
                        break
        
        return all_stats
    
    def get_stats_leaders(self, stat_type: str, season: Optional[int] = None, 
                         limit: int = 50, stat_group: str = "hitting",
                         team_id: Optional[int] = None,
                         league_id: Optional[int] = None) -> List[Dict]:
        """
        Get top players by a specific statistic.
        
        Args:
            stat_type: Statistic to rank by (e.g., 'homeRuns', 'avg', 'era', 'strikeouts')
            season: Season year (defaults to current year)
            limit: Number of leaders to return (default 50)
            stat_group: 'hitting' or 'pitching'
            team_id: Filter by specific team ID (optional)
            league_id: Filter by league (103=AL, 104=NL) (optional)
            
        Returns:
            List of player dictionaries with stats
            
        Common hitting stats: homeRuns, rbi, avg, obp, slg, ops, stolenBases, hits, runs
        Common pitching stats: wins, era, strikeouts, saves, whip, inningsPitched
        """
        if season is None:
            season = datetime.now().year
        
        # For team-specific queries, use different endpoint
        if team_id is not None:
            team_stats = self.get_team_player_stats(team_id, season, stat_group)
            
            if not team_stats:
                return []
            
            # Convert to leaders format
            leaders = []
            for player_stat in team_stats:
                stat = player_stat.get('stat', {})
                value = stat.get(stat_type)
                
                # Skip players without this stat
                if value is None:
                    continue
                
                leaders.append({
                    'person': player_stat.get('person', {}),
                    'team': player_stat.get('team', {}),
                    'value': value
                })
            
            # Sort by value (descending for most stats, ascending for ERA/WHIP)
            reverse_sort = stat_type not in ['era', 'whip']
            leaders.sort(key=lambda x: float(x['value']), reverse=reverse_sort)
            
            # Assign ranks after sorting
            for idx, leader in enumerate(leaders):
                leader['rank'] = idx + 1
            
            return leaders
            
        endpoint = "stats/leaders"
        params = {
            "leaderCategories": stat_type,
            "season": season,
            "sportId": 1,
            "statGroup": stat_group,
            "limit": limit
        }
        
        # League ID is supported by the API
        if league_id is not None:
            params["leagueId"] = league_id
        
        data = self._make_request(endpoint, params)
        
        if data and "leagueLeaders" in data and len(data["leagueLeaders"]) > 0:
            leaders = data["leagueLeaders"][0]
            if "leaders" in leaders and len(leaders["leaders"]) > 0:
                return leaders["leaders"]
        return []
    
    def get_team_stats(self, season: Optional[int] = None, 
                       stat_group: str = "hitting") -> List[Dict]:
        """
        Get statistics for all MLB teams.
        
        Args:
            season: Season year (defaults to current year)
            stat_group: 'hitting' or 'pitching'
            
        Returns:
            List of team stat dictionaries
        """
        if season is None:
            season = datetime.now().year
        
        endpoint = "teams"
        params = {
            "sportId": 1,
            "season": season
        }
        
        response = self._make_request(endpoint, params)
        
        if not response or 'teams' not in response:
            return []
        
        teams = response['teams']
        team_stats = []
        
        # Get stats for each team
        for team in teams:
            team_id = team.get('id')
            team_name = team.get('name')
            
            # Get team season stats
            stats_endpoint = f"teams/{team_id}/stats"
            stats_params = {
                "stats": "season",
                "season": season,
                "group": stat_group
            }
            
            stats_response = self._make_request(stats_endpoint, stats_params)
            
            if stats_response and 'stats' in stats_response:
                for stat_data in stats_response['stats']:
                    splits = stat_data.get('splits', [])
                    if splits:
                        stat = splits[0].get('stat', {})
                        
                        team_stats.append({
                            'team_id': team_id,
                            'team_name': team_name,
                            'stat': stat
                        })
                        break
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
        
        return team_stats


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
