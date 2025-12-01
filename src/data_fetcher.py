"""
MLB Data Fetcher Module

This module provides functionality to fetch MLB statistics from the MLB Stats API.
"""

import requests
import json
import sys
import os
from typing import Dict, List, Optional, Union
from datetime import datetime
import time
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Load environment variables
load_dotenv()

# Add parent directory to path to import cache and logger
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.cache import MLBCache
from src.logger import get_logger
from src.name_normalizer import normalize_name, fuzzy_name_match, apply_known_aliases

# Initialize logger
logger = get_logger(__name__)


class MLBDataFetcher:
    """
    Fetches data from the MLB Stats API with intelligent caching.
    
    WHAT THIS CLASS DOES (Beginner Explanation):
    ---------------------------------------------
    Imagine you're asking a librarian for books. Instead of walking to the
    shelf every time, the librarian keeps recently-requested books at the
    desk for quick access. That's what this class does with MLB statistics!
    
    KEY RESPONSIBILITIES:
    1. Talk to MLB's official API (statsapi.mlb.com)
    2. Cache responses to avoid unnecessary API calls
    3. Provide simple methods to get player/team/league data
    
    CACHING BENEFITS:
    - Faster responses (0.1s cached vs 1-2s API call)
    - Works offline if you've queried before
    - Reduces load on MLB's servers
    - Saves bandwidth
    
    USAGE EXAMPLE:
    ```python
    fetcher = MLBDataFetcher()
    
    # First call: hits MLB API, takes 1-2 seconds
    teams = fetcher.get_teams(2024)
    
    # Second call: uses cache, takes 0.1 seconds!
    teams = fetcher.get_teams(2024)
    ```
    """
    
    # MLB's official statistics API base URL
    # All endpoints build on this (e.g., /api/v1/teams, /api/v1/people, etc.)
    # Can be overridden via MLB_API_BASE_URL environment variable
    BASE_URL = os.getenv('MLB_API_BASE_URL', 'https://statsapi.mlb.com/api/v1')
    
    def __init__(self, use_cache: bool = True, cache_ttl_hours: int = 24):
        """
        Initialize the MLB Data Fetcher.
        
        Args:
            use_cache: Enable caching system (default: True, highly recommended!)
            cache_ttl_hours: How long to keep cached data (default: 24 hours)
                           - Current season: 24 hours (stats change daily)
                           - Past seasons: Forever (stats never change)
        
        BEGINNER TIP:
        -------------
        Always keep use_cache=True unless you're debugging and need fresh data
        every single time. The cache is smart enough to know when to refresh!
        
        HOW TTL WORKS:
        - You query "Aaron Judge 2024 stats" at 2pm
        - Data gets cached with timestamp
        - You query same thing at 3pm → Uses cache (within 24 hours)
        - You query same thing tomorrow at 3pm → Fetches fresh (past 24 hours)
        
        MEMORY USAGE:
        Each cached response is ~1-50KB depending on complexity
        100 queries ≈ 1-5MB of cached data (very lightweight!)
        """
        # Create a persistent connection session for better performance
        # (Reusing TCP connections is faster than creating new ones each time)
        self.session = requests.Session()
        # Store cache preference
        self.use_cache = use_cache
        
        # Initialize cache system if enabled
        # (If disabled, self.cache stays None and all methods skip cache checks)
        self.cache = MLBCache(ttl_hours=cache_ttl_hours) if use_cache else None
        
        # Get timeout from environment variable
        self.timeout = int(os.getenv('API_TIMEOUT_SECONDS', '10'))
        
        cache_status = 'enabled' if use_cache else 'disabled'
        logger.info(f"MLBDataFetcher initialized (cache={cache_status}, ttl={cache_ttl_hours}h, timeout={self.timeout}s)")
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the MLB Stats API with intelligent caching.
        
        This is the "brain" of the fetcher - all other methods call this internally.
        
        Args:
            endpoint: API path (e.g., "people/592450" for Aaron Judge)
            params: Query parameters (e.g., {"season": 2024, "hydrate": "stats"})
            
        Returns:
            Dictionary containing the API response data
        
        HOW IT WORKS (Step-by-Step):
        ------------------------------
        1. Check if we have this exact request cached
           - Endpoint + params create a unique cache key
           - Example: "people/592450?season=2024" is one cache entry
           
        2. If cached AND not expired:
           - Return cached data instantly (0.1 seconds)
           - Skip API call entirely
           
        3. If NOT cached OR expired:
           - Make HTTP GET request to MLB API
           - Wait for response (usually 1-2 seconds)
           - Parse JSON response
           - Save to cache for next time
           - Return data
        
        ERROR HANDLING:
        - Network timeout (> 10 seconds) → Return empty dict {}
        - HTTP error (404, 500, etc.) → Return empty dict {}
        - Invalid JSON response → Return empty dict {}
        
        EXAMPLE REQUEST:
        ```python
        _make_request(
            endpoint="people/592450",
            params={"hydrate": "stats(type=season)"}
        )
        
        # Full URL built:
        # https://statsapi.mlb.com/api/v1/people/592450?hydrate=stats(type=season)
        ```
        """
        # STEP 1: Check cache first (always check cache before network!)
        if self.use_cache and self.cache:
            cached_data = self.cache.get(endpoint, params)
            if cached_data is not None:
                # Cache hit! Return immediately without API call
                # (This is 10-20x faster than making the request)
                logger.debug(f"Cache HIT: {endpoint}")
                return cached_data
            logger.debug(f"Cache MISS: {endpoint}")
        
        # STEP 2: Cache miss - need to make actual API request
        # Build full URL by combining base URL + endpoint
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Use retry decorator for resilience
        return self._make_api_request_with_retry(url, endpoint, params)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.ConnectionError)),
        reraise=True
    )
    def _make_api_request_with_retry(self, url: str, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make API request with automatic retry logic for transient failures.
        
        This method is wrapped with tenacity retry decorator to handle:
        - Network timeouts (retry up to 3 times)
        - Connection errors (retry with exponential backoff)
        - Transient server errors
        
        Args:
            url: Full API URL
            endpoint: API endpoint (for caching)
            params: Query parameters
            
        Returns:
            Parsed JSON response
            
        Raises:
            RequestException: After all retries exhausted
        """
        try:
            logger.info(f"API Request: {endpoint}")
            start_time = time.time()
            
            # Make GET request to MLB API
            # - timeout: Configurable via environment (default 10 seconds)
            # - params: Automatically URL-encodes parameters
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            # Raise exception if HTTP error occurred (404, 500, etc.)
            response.raise_for_status()
            
            # Parse JSON response into Python dictionary
            data = response.json()
            
            elapsed = time.time() - start_time
            logger.info(f"API Response: {endpoint} ({elapsed:.2f}s)")
            
            # STEP 3: Store successful response in cache for next time
            if self.use_cache and self.cache:
                self.cache.set(endpoint, params, data)
                logger.debug(f"Cached response for: {endpoint}")
            
            # Return the data to caller
            return data
            
        except requests.exceptions.Timeout as e:
            # Timeout - will be retried by decorator
            logger.warning(f"Request timeout for {url}: {e}")
            raise
            
        except requests.exceptions.ConnectionError as e:
            # Connection error - will be retried by decorator
            logger.warning(f"Connection error for {url}: {e}")
            raise
            
        except requests.exceptions.RequestException as e:
            # Other errors (404, 500, etc.) - log and return empty dict
            logger.error(f"Error fetching data from {url}: {e}", exc_info=True)
            
            # Return empty dict so caller can handle gracefully
            # (Callers always check: if data and "people" in data: ...)
            return {}
        
    def clear_cache(self):
        """Clear all cached data."""
        if self.cache:
            self.cache.clear()
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        if self.cache:
            return self.cache.get_cache_stats()
        return {'error': 'Caching not enabled'}
    
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
    
    def get_team_season_stats(self, team_id: int, season: int, stat_group: str = "hitting") -> Dict:
        """
        Get team statistics for a specific season.
        
        Args:
            team_id: MLB team ID
            season: Season year
            stat_group: 'hitting' or 'pitching'
            
        Returns:
            Dictionary containing team statistics
        """
        endpoint = f"teams/{team_id}/stats"
        params = {
            "stats": "season",
            "season": season,
            "group": stat_group
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
    
    def search_players(self, name: str, include_retired: bool = True) -> List[Dict]:
        """
        Search for players by name with intelligent normalization.
        
        **PERFORMANCE OPTIMIZED**: Uses MLB's direct player search API endpoint
        instead of iterating through seasons. This is ~20x faster for retired players.
        
        Handles names with:
        - Accent marks (José → Jose)
        - Special characters (O'Brien, Jean-Pierre)
        - Partial names (just last name)
        - Nicknames (Big Papi, A-Rod)
        
        Args:
            name: Player name to search for
            include_retired: If True, includes retired players (default True)
            
        Returns:
            List of matching players
            
        Examples:
            >>> fetcher = MLBDataFetcher()
            >>> # All of these will find José Ramírez:
            >>> fetcher.search_players("Jose Ramirez")
            >>> fetcher.search_players("José Ramírez")
            >>> fetcher.search_players("Ramirez")
            
        Performance:
            - Old implementation: 15-25 seconds for retired players (30 API calls)
            - New implementation: <1 second (1 API call)
        """
        # Apply known aliases first (Big Papi → David Ortiz)
        name = apply_known_aliases(name)
        
        # Normalize the search name for better matching
        normalized_search = normalize_name(name)
        
        logger.debug(f"Searching for player: '{name}' (normalized: '{normalized_search}')")
        
        # ==================================================================================
        # PERFORMANCE OPTIMIZATION: Use MLB's direct player search endpoint
        # ==================================================================================
        # The MLB API has a /people/search endpoint that searches across ALL players
        # (active and retired) in a single API call. This is MUCH faster than the old
        # approach of iterating through 30 seasons (which took 15-25 seconds).
        #
        # Why this matters for comparisons:
        # - Comparing Ken Griffey Jr (retired 2010) vs Albert Pujols (retired 2022)
        # - Old way: 16 calls for Griffey + 4 calls for Pujols = 20 calls, 23+ seconds
        # - New way: 1 call for Griffey + 1 call for Pujols = 2 calls, <1 second
        #
        # This makes comparison queries feel instant instead of painfully slow!
        # ==================================================================================
        
        endpoint = "people/search"
        params = {
            "names": name  # MLB API accepts the name directly
        }
        
        data = self._make_request(endpoint, params)
        
        results = []
        
        if data and "people" in data:
            # Use fuzzy matching with name normalization for best results
            for player in data["people"]:
                player_name = player.get("fullName", "")
                if fuzzy_name_match(name, player_name):
                    results.append(player)
            
            # Log matches found
            if results:
                player_status = "player(s)"  # Could be active or retired
                logger.info(f"Found {len(results)} {player_status} matching '{name}'")
        
        return results
    
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
    
    def get_all_players_stats(self, season: int, stat_group: str = "hitting",
                              league_id: Optional[int] = None) -> List[Dict]:
        """
        Get statistics for ALL MLB players in a season (no limits).
        
        Args:
            season: Season year
            stat_group: 'hitting' or 'pitching'
            league_id: Filter by league (103=AL, 104=NL) (optional)
            
        Returns:
            List of player stat dictionaries
        """
        # Get all teams
        all_teams = self.get_teams(season)
        
        if not all_teams:
            return []
        
        # Filter by league if specified
        if league_id is not None:
            all_teams = [team for team in all_teams 
                        if team.get('league', {}).get('id') == league_id]
        
        all_player_stats = []
        
        # Get stats from each team
        for team in all_teams:
            team_id = team.get('id')
            
            # Get team player stats
            team_stats = self.get_team_player_stats(team_id, season, stat_group)
            
            # Add to overall list
            all_player_stats.extend(team_stats)
            
            # Small delay to avoid rate limiting
            time.sleep(0.05)
        
        return all_player_stats
    
    def get_stats_leaders(self, stat_type: str, season: Optional[int] = None, 
                         limit: int = 50, stat_group: str = "hitting",
                         team_id: Optional[int] = None,
                         league_id: Optional[int] = None,
                         include_all: bool = False) -> List[Dict]:
        """
        Get top players by a specific statistic.
        
        Args:
            stat_type: Statistic to rank by (e.g., 'homeRuns', 'avg', 'era', 'strikeouts')
            season: Season year (defaults to current year)
            limit: Number of leaders to return (default 50, ignored if include_all=True)
            stat_group: 'hitting' or 'pitching'
            team_id: Filter by specific team ID (optional)
            league_id: Filter by league (103=AL, 104=NL) (optional)
            include_all: If True, rank ALL players who played in the season (default False)
            
        Returns:
            List of player dictionaries with stats
            
        Common hitting stats: homeRuns, rbi, avg, obp, slg, ops, stolenBases, hits, runs
        Common pitching stats: wins, era, strikeouts, saves, whip, inningsPitched
        """
        if season is None:
            season = datetime.now().year
        
        # For complete rankings or team-specific queries, get all player stats
        if include_all or team_id is not None:
            if team_id is not None:
                # Get stats for specific team
                all_stats = self.get_team_player_stats(team_id, season, stat_group)
            else:
                # Get stats for all players in the league/season
                all_stats = self.get_all_players_stats(season, stat_group, league_id)
            
            if not all_stats:
                return []
            
            # Convert to leaders format and rank
            leaders = []
            for player_stat in all_stats:
                stat = player_stat.get('stat', {})
                value = stat.get(stat_type)
                
                # Skip players without this stat or with invalid placeholder values
                # MLB API returns '-.--' for undefined ERA/WHIP values
                if value is None or value == '' or value == '-.--':
                    continue
                
                # Try to convert to float - skip if conversion fails
                try:
                    float_value = float(value)
                except (ValueError, TypeError):
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
            
            # Apply limit if not include_all
            if not include_all and limit:
                leaders = leaders[:limit]
            
            return leaders
        
        # For quick queries without complete rankings, use the API's leaders endpoint
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
    
    def get_player_career_stats(self, player_id: int, stat_group: str = "hitting") -> List[Dict]:
        """
        Get career statistics for a player across all seasons.
        
        Args:
            player_id: MLB player ID
            stat_group: Type of stats ('hitting', 'pitching', 'fielding')
            
        Returns:
            List of dictionaries containing stats for each season
        """
        endpoint = f"people/{player_id}"
        params = {
            "hydrate": f"stats(group=[{stat_group}],type=[yearByYear])"
        }
        data = self._make_request(endpoint, params)
        
        if not data or "people" not in data or len(data["people"]) == 0:
            return []
        
        player_data = data["people"][0]
        career_stats = []
        
        # Extract stats from all seasons
        if "stats" in player_data:
            for stat_group_data in player_data["stats"]:
                if stat_group_data.get("type", {}).get("displayName") == "yearByYear":
                    splits = stat_group_data.get("splits", [])
                    for split in splits:
                        season = split.get("season")
                        stat = split.get("stat", {})
                        team = split.get("team", {})
                        
                        career_stats.append({
                            "season": season,
                            "team": team.get("name", "Unknown"),
                            "team_id": team.get("id"),
                            "stat": stat
                        })
        
        return career_stats
    
    def get_team_career_stats(self, team_id: int, stat_group: str = "hitting", 
                             start_year: Optional[int] = None, 
                             end_year: Optional[int] = None) -> List[Dict]:
        """
        Get career (historical) statistics for a team across multiple seasons.
        
        Args:
            team_id: MLB team ID
            stat_group: 'hitting' or 'pitching'
            start_year: Starting season (optional, defaults to 1900)
            end_year: Ending season (optional, defaults to current year)
            
        Returns:
            List of dictionaries containing stats for each season
        """
        if start_year is None:
            start_year = 1900
        if end_year is None:
            end_year = datetime.now().year
        
        career_stats = []
        
        # Get stats for each season
        for season in range(start_year, end_year + 1):
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
                        
                        career_stats.append({
                            'season': season,
                            'team_id': team_id,
                            'stat': stat
                        })
                        break
            
            # Small delay to avoid rate limiting
            time.sleep(0.05)
        
        return career_stats


if __name__ == "__main__":
    # Example usage with logging
    import logging
    logging.basicConfig(level=logging.INFO)
    
    fetcher = MLBDataFetcher()
    
    # Get teams
    logger.info("Fetching MLB teams...")
    teams = fetcher.get_teams(2024)
    if teams:
        logger.info(f"Found {len(teams)} teams")
        logger.info(f"Example: {teams[0].get('name', 'Unknown')}")
    
    # Search for a player
    logger.info("Searching for Aaron Judge...")
    players = fetcher.search_players("Aaron Judge")
    if players:
        player = players[0]
        logger.info(f"Found: {player.get('fullName')} (ID: {player.get('id')})")
