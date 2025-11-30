"""
Data Processor Module

This module provides functionality to clean, transform, and process MLB statistics data.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
import json


class MLBDataProcessor:
    """Processes and cleans MLB statistics data."""
    
    def __init__(self):
        """Initialize the data processor."""
        pass
    
    def extract_batting_stats(self, player_data: Dict) -> pd.DataFrame:
        """
        Extract batting statistics from player data.
        
        Args:
            player_data: Player data dictionary from API
            
        Returns:
            DataFrame with batting statistics
        """
        if not player_data or "stats" not in player_data:
            return pd.DataFrame()
        
        stats_list = []
        for stat_group in player_data.get("stats", []):
            if stat_group.get("group", {}).get("displayName") == "hitting":
                for split in stat_group.get("splits", []):
                    stat = split.get("stat", {})
                    season = split.get("season", "Unknown")
                    
                    stats_list.append({
                        "season": season,
                        "gamesPlayed": stat.get("gamesPlayed", 0),
                        "atBats": stat.get("atBats", 0),
                        "runs": stat.get("runs", 0),
                        "hits": stat.get("hits", 0),
                        "doubles": stat.get("doubles", 0),
                        "triples": stat.get("triples", 0),
                        "homeRuns": stat.get("homeRuns", 0),
                        "rbi": stat.get("rbi", 0),
                        "stolenBases": stat.get("stolenBases", 0),
                        "caughtStealing": stat.get("caughtStealing", 0),
                        "walks": stat.get("baseOnBalls", 0),
                        "strikeouts": stat.get("strikeOuts", 0),
                        "avg": stat.get("avg", ".000"),
                        "obp": stat.get("obp", ".000"),
                        "slg": stat.get("slg", ".000"),
                        "ops": stat.get("ops", ".000")
                    })
        
        return pd.DataFrame(stats_list)
    
    def extract_pitching_stats(self, player_data: Dict) -> pd.DataFrame:
        """
        Extract pitching statistics from player data.
        
        Args:
            player_data: Player data dictionary from API
            
        Returns:
            DataFrame with pitching statistics
        """
        if not player_data or "stats" not in player_data:
            return pd.DataFrame()
        
        stats_list = []
        for stat_group in player_data.get("stats", []):
            if stat_group.get("group", {}).get("displayName") == "pitching":
                for split in stat_group.get("splits", []):
                    stat = split.get("stat", {})
                    season = split.get("season", "Unknown")
                    
                    stats_list.append({
                        "season": season,
                        "gamesPlayed": stat.get("gamesPlayed", 0),
                        "gamesStarted": stat.get("gamesStarted", 0),
                        "wins": stat.get("wins", 0),
                        "losses": stat.get("losses", 0),
                        "saves": stat.get("saves", 0),
                        "inningsPitched": stat.get("inningsPitched", "0.0"),
                        "hits": stat.get("hits", 0),
                        "runs": stat.get("runs", 0),
                        "earnedRuns": stat.get("earnedRuns", 0),
                        "homeRuns": stat.get("homeRuns", 0),
                        "walks": stat.get("baseOnBalls", 0),
                        "strikeouts": stat.get("strikeOuts", 0),
                        "era": stat.get("era", "0.00"),
                        "whip": stat.get("whip", "0.00")
                    })
        
        return pd.DataFrame(stats_list)
    
    def convert_numeric_columns(self, df: pd.DataFrame, 
                               exclude_cols: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Convert string columns to numeric where appropriate.
        
        Args:
            df: Input DataFrame
            exclude_cols: Columns to exclude from conversion
            
        Returns:
            DataFrame with converted columns
        """
        if df.empty:
            return df
        
        exclude = exclude_cols or []
        df_copy = df.copy()
        
        for col in df_copy.columns:
            if col not in exclude:
                # Try to convert to numeric, keeping non-numeric values as-is
                try:
                    df_copy[col] = pd.to_numeric(df_copy[col])
                except (ValueError, TypeError):
                    # If conversion fails, keep the column as-is
                    pass
        
        return df_copy
    
    def aggregate_team_stats(self, roster_stats: List[pd.DataFrame]) -> pd.DataFrame:
        """
        Aggregate individual player statistics to team level.
        
        Args:
            roster_stats: List of DataFrames with player statistics
            
        Returns:
            DataFrame with aggregated team statistics
        """
        if not roster_stats:
            return pd.DataFrame()
        
        combined = pd.concat(roster_stats, ignore_index=True)
        
        # Sum numeric columns
        numeric_cols = combined.select_dtypes(include=[np.number]).columns
        team_totals = combined[numeric_cols].sum()
        
        return pd.DataFrame([team_totals])
    
    def calculate_rate_stats(self, df: pd.DataFrame, stat_type: str = "batting") -> pd.DataFrame:
        """
        Calculate rate statistics from counting stats.
        
        Args:
            df: DataFrame with counting statistics
            stat_type: Type of stats ('batting' or 'pitching')
            
        Returns:
            DataFrame with added rate statistics
        """
        df_copy = df.copy()
        
        if stat_type == "batting":
            # Batting average
            if "hits" in df_copy.columns and "atBats" in df_copy.columns:
                df_copy["calculated_avg"] = df_copy.apply(
                    lambda row: row["hits"] / row["atBats"] if row["atBats"] > 0 else 0,
                    axis=1
                )
            
            # On-base percentage
            if all(col in df_copy.columns for col in ["hits", "walks", "atBats"]):
                df_copy["calculated_obp"] = df_copy.apply(
                    lambda row: (row["hits"] + row["walks"]) / (row["atBats"] + row["walks"]) 
                    if (row["atBats"] + row["walks"]) > 0 else 0,
                    axis=1
                )
        
        elif stat_type == "pitching":
            # ERA (Earned Run Average)
            if "earnedRuns" in df_copy.columns and "inningsPitched" in df_copy.columns:
                df_copy["calculated_era"] = df_copy.apply(
                    lambda row: (row["earnedRuns"] * 9) / float(row["inningsPitched"]) 
                    if float(row["inningsPitched"]) > 0 else 0,
                    axis=1
                )
        
        return df_copy
    
    def clean_missing_values(self, df: pd.DataFrame, 
                            strategy: str = "zero") -> pd.DataFrame:
        """
        Handle missing values in the dataset.
        
        Args:
            df: Input DataFrame
            strategy: Strategy for handling missing values ('zero', 'mean', 'drop')
            
        Returns:
            DataFrame with handled missing values
        """
        df_copy = df.copy()
        
        if strategy == "zero":
            df_copy = df_copy.fillna(0)
        elif strategy == "mean":
            numeric_cols = df_copy.select_dtypes(include=[np.number]).columns
            df_copy[numeric_cols] = df_copy[numeric_cols].fillna(
                df_copy[numeric_cols].mean()
            )
        elif strategy == "drop":
            df_copy = df_copy.dropna()
        
        return df_copy
    
    def filter_by_season(self, df: pd.DataFrame, 
                        seasons: Union[int, List[int]]) -> pd.DataFrame:
        """
        Filter DataFrame by season(s).
        
        Args:
            df: Input DataFrame with 'season' column
            seasons: Single season or list of seasons
            
        Returns:
            Filtered DataFrame
        """
        if "season" not in df.columns:
            return df
        
        if isinstance(seasons, int):
            seasons = [seasons]
        
        return df[df["season"].isin(seasons)]
    
    def filter_by_minimum_threshold(self, df: pd.DataFrame, 
                                    column: str, 
                                    threshold: float) -> pd.DataFrame:
        """
        Filter DataFrame by minimum threshold for a column.
        
        Args:
            df: Input DataFrame
            column: Column name to filter
            threshold: Minimum threshold value
            
        Returns:
            Filtered DataFrame
        """
        if column not in df.columns:
            return df
        
        return df[df[column] >= threshold]
    
    def create_player_summary(self, batting_df: pd.DataFrame, 
                             pitching_df: Optional[pd.DataFrame] = None) -> Dict:
        """
        Create a summary dictionary for a player.
        
        Args:
            batting_df: Batting statistics DataFrame
            pitching_df: Pitching statistics DataFrame (optional)
            
        Returns:
            Dictionary with player summary statistics
        """
        summary = {}
        
        if not batting_df.empty:
            summary["batting"] = {
                "total_games": batting_df["gamesPlayed"].sum(),
                "total_hits": batting_df["hits"].sum(),
                "total_home_runs": batting_df["homeRuns"].sum(),
                "total_rbi": batting_df["rbi"].sum(),
                "career_avg": batting_df["hits"].sum() / batting_df["atBats"].sum() 
                              if batting_df["atBats"].sum() > 0 else 0
            }
        
        if pitching_df is not None and not pitching_df.empty:
            total_ip = sum(float(ip) for ip in pitching_df["inningsPitched"])
            summary["pitching"] = {
                "total_games": pitching_df["gamesPlayed"].sum(),
                "total_wins": pitching_df["wins"].sum(),
                "total_strikeouts": pitching_df["strikeouts"].sum(),
                "total_innings": total_ip,
                "career_era": (pitching_df["earnedRuns"].sum() * 9) / total_ip 
                             if total_ip > 0 else 0
            }
        
        return summary
    
    def export_to_csv(self, df: pd.DataFrame, filepath: str) -> None:
        """
        Export DataFrame to CSV file.
        
        Args:
            df: DataFrame to export
            filepath: Output file path
        """
        df.to_csv(filepath, index=False)
        print(f"Data exported to {filepath}")
    
    def export_to_json(self, data: Union[Dict, pd.DataFrame], filepath: str) -> None:
        """
        Export data to JSON file.
        
        Args:
            data: Data to export (Dict or DataFrame)
            filepath: Output file path
        """
        if isinstance(data, pd.DataFrame):
            data.to_json(filepath, orient="records", indent=2)
        else:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        print(f"Data exported to {filepath}")
    
    def extract_stats_leaders(self, leaders_data: List[Dict]) -> pd.DataFrame:
        """
        Extract and format stats leaders data into a DataFrame.
        
        Args:
            leaders_data: List of leader dictionaries from API
            
        Returns:
            DataFrame with player rankings and stats
        """
        if not leaders_data:
            return pd.DataFrame()
        
        rows = []
        for leader in leaders_data:
            person = leader.get("person", {})
            team = leader.get("team", {})
            
            row = {
                "rank": leader.get("rank"),
                "playerName": person.get("fullName"),
                "playerId": person.get("id"),
                "team": team.get("name", "N/A"),
                "teamId": team.get("id"),
                "value": leader.get("value")
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        return df
    
    def extract_team_stats(self, team_stats_data: List[Dict], 
                          stat_type: str) -> pd.DataFrame:
        """
        Extract and rank team statistics.
        
        Args:
            team_stats_data: List of team stat dictionaries
            stat_type: Specific stat to rank by (e.g., 'era', 'homeRuns', 'stolenBases')
            
        Returns:
            DataFrame with ranked team statistics
        """
        if not team_stats_data:
            return pd.DataFrame()
        
        rows = []
        for team_data in team_stats_data:
            stat = team_data.get('stat', {})
            value = stat.get(stat_type)
            
            # Skip teams without this stat
            if value is None:
                continue
            
            row = {
                'team_name': team_data.get('team_name'),
                'team_id': team_data.get('team_id'),
                'value': value
            }
            rows.append(row)
        
        if not rows:
            return pd.DataFrame()
        
        df = pd.DataFrame(rows)
        
        # Sort by value (ascending for ERA/WHIP, descending for most others)
        ascending = stat_type in ['era', 'whip']
        df = df.sort_values('value', ascending=ascending).reset_index(drop=True)
        
        # Add rank column
        df.insert(0, 'rank', range(1, len(df) + 1))
        
        return df
    
    def aggregate_career_stats(self, career_data: List[Dict], stat_group: str = "hitting") -> Dict:
        """
        Aggregate career statistics across all seasons.
        
        Args:
            career_data: List of season stat dictionaries from get_player_career_stats
            stat_group: 'hitting' or 'pitching'
            
        Returns:
            Dictionary with aggregated career totals and averages
        """
        if not career_data:
            return {}
        
        # Initialize totals
        totals = {}
        rate_stats = []
        season_count = len(career_data)
        
        # Define which stats to sum vs average
        if stat_group == "hitting":
            sum_stats = ['gamesPlayed', 'atBats', 'runs', 'hits', 'doubles', 'triples', 
                        'homeRuns', 'rbi', 'stolenBases', 'caughtStealing', 
                        'baseOnBalls', 'strikeOuts', 'sacFlies', 'sacBunts']
            rate_stat_names = ['avg', 'obp', 'slg', 'ops']
        else:  # pitching
            sum_stats = ['gamesPlayed', 'gamesStarted', 'wins', 'losses', 'saves',
                        'hits', 'runs', 'earnedRuns', 'homeRuns', 'baseOnBalls', 
                        'strikeOuts', 'completeGames', 'shutouts']
            rate_stat_names = ['era', 'whip']
        
        # Sum counting stats
        for stat_name in sum_stats:
            totals[stat_name] = 0
            for season in career_data:
                stat_value = season.get('stat', {}).get(stat_name, 0)
                if stat_value and stat_value != '':
                    try:
                        totals[stat_name] += float(stat_value)
                    except (ValueError, TypeError):
                        totals[stat_name] += 0
        
        # Handle innings pitched specially (it's a string like "123.1")
        if stat_group == "pitching":
            total_ip = 0.0
            for season in career_data:
                ip_str = season.get('stat', {}).get('inningsPitched', '0.0')
                if ip_str:
                    try:
                        total_ip += float(ip_str)
                    except (ValueError, TypeError):
                        pass
            totals['inningsPitched'] = f"{total_ip:.1f}"
        
        # Calculate career rate stats
        career_rates = {}
        
        if stat_group == "hitting":
            # Career batting average
            if totals.get('atBats', 0) > 0:
                career_rates['avg'] = f"{totals['hits'] / totals['atBats']:.3f}"
            else:
                career_rates['avg'] = ".000"
            
            # Career OBP
            pa = totals.get('atBats', 0) + totals.get('baseOnBalls', 0) + \
                 totals.get('sacFlies', 0)
            if pa > 0:
                obp_num = totals.get('hits', 0) + totals.get('baseOnBalls', 0)
                career_rates['obp'] = f"{obp_num / pa:.3f}"
            else:
                career_rates['obp'] = ".000"
            
            # Career SLG
            if totals.get('atBats', 0) > 0:
                singles = totals.get('hits', 0) - totals.get('doubles', 0) - \
                         totals.get('triples', 0) - totals.get('homeRuns', 0)
                total_bases = singles + (2 * totals.get('doubles', 0)) + \
                             (3 * totals.get('triples', 0)) + (4 * totals.get('homeRuns', 0))
                career_rates['slg'] = f"{total_bases / totals['atBats']:.3f}"
            else:
                career_rates['slg'] = ".000"
            
            # Career OPS
            try:
                career_rates['ops'] = f"{float(career_rates['obp']) + float(career_rates['slg']):.3f}"
            except:
                career_rates['ops'] = ".000"
        
        elif stat_group == "pitching":
            # Career ERA
            try:
                ip = float(totals.get('inningsPitched', '0.0'))
                if ip > 0:
                    career_rates['era'] = f"{(totals.get('earnedRuns', 0) * 9) / ip:.2f}"
                else:
                    career_rates['era'] = "0.00"
            except:
                career_rates['era'] = "0.00"
            
            # Career WHIP
            try:
                ip = float(totals.get('inningsPitched', '0.0'))
                if ip > 0:
                    whip = (totals.get('baseOnBalls', 0) + totals.get('hits', 0)) / ip
                    career_rates['whip'] = f"{whip:.2f}"
                else:
                    career_rates['whip'] = "0.00"
            except:
                career_rates['whip'] = "0.00"
        
        # Combine totals and rates
        result = {
            'seasons': season_count,
            'totals': totals,
            'career_rates': career_rates
        }
        
        return result
    
    def create_career_dataframe(self, career_data: List[Dict]) -> pd.DataFrame:
        """
        Convert career data from multiple seasons into a DataFrame.
        
        Args:
            career_data: List of season dictionaries from get_player_career_stats
            
        Returns:
            DataFrame with one row per season
        """
        if not career_data:
            return pd.DataFrame()
        
        rows = []
        for season_data in career_data:
            season = season_data.get('season')
            team = season_data.get('team', 'Unknown')
            stat = season_data.get('stat', {})
            
            row = {'season': season, 'team': team}
            row.update(stat)
            rows.append(row)
        
        df = pd.DataFrame(rows)
        return self.convert_numeric_columns(df, exclude_cols=['season', 'team'])
    
    def compare_player_careers(self, player1_career: List[Dict], 
                              player2_career: List[Dict],
                              stat_group: str = "hitting") -> pd.DataFrame:
        """
        Compare career statistics for two players side by side.
        
        Args:
            player1_career: Career data for first player
            player2_career: Career data for second player
            stat_group: 'hitting' or 'pitching'
            
        Returns:
            DataFrame comparing career totals
        """
        player1_totals = self.aggregate_career_stats(player1_career, stat_group)
        player2_totals = self.aggregate_career_stats(player2_career, stat_group)
        
        if not player1_totals or not player2_totals:
            return pd.DataFrame()
        
        # Create comparison DataFrame
        comparison = {
            'Statistic': [],
            'Player 1': [],
            'Player 2': []
        }
        
        # Add season count
        comparison['Statistic'].append('Seasons')
        comparison['Player 1'].append(player1_totals['seasons'])
        comparison['Player 2'].append(player2_totals['seasons'])
        
        # Add all counting stats
        for stat_name, value in player1_totals['totals'].items():
            comparison['Statistic'].append(stat_name)
            comparison['Player 1'].append(value)
            comparison['Player 2'].append(player2_totals['totals'].get(stat_name, 0))
        
        # Add rate stats
        for stat_name, value in player1_totals['career_rates'].items():
            comparison['Statistic'].append(f"Career {stat_name.upper()}")
            comparison['Player 1'].append(value)
            comparison['Player 2'].append(player2_totals['career_rates'].get(stat_name, 'N/A'))
        
        return pd.DataFrame(comparison)


if __name__ == "__main__":
    # Example usage
    processor = MLBDataProcessor()
    
    # Create sample data
    sample_data = {
        "season": [2023, 2024],
        "gamesPlayed": [150, 145],
        "atBats": [550, 530],
        "hits": [165, 158],
        "homeRuns": [35, 40]
    }
    
    df = pd.DataFrame(sample_data)
    print("Sample DataFrame:")
    print(df)
    
    # Filter by season
    filtered = processor.filter_by_season(df, 2024)
    print("\nFiltered by 2024:")
    print(filtered)
