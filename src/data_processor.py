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
                # Try to convert to numeric
                df_copy[col] = pd.to_numeric(df_copy[col], errors='ignore')
        
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
