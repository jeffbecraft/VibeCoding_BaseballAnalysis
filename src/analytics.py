"""
Analytics Module

This module provides advanced baseball statistics and analytics calculations.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple


class BattingAnalytics:
    """Calculate batting statistics and advanced metrics."""
    
    def __init__(self):
        """Initialize batting analytics."""
        pass
    
    def calculate_batting_average(self, hits: int, at_bats: int) -> float:
        """
        Calculate batting average (AVG).
        
        Args:
            hits: Number of hits
            at_bats: Number of at bats
            
        Returns:
            Batting average
        """
        if at_bats == 0:
            return 0.0
        return hits / at_bats
    
    def calculate_on_base_percentage(self, hits: int, walks: int, hbp: int,
                                     at_bats: int, sacrifice_flies: int = 0) -> float:
        """
        Calculate on-base percentage (OBP).
        
        Args:
            hits: Number of hits
            walks: Number of walks (BB)
            hbp: Hit by pitch
            at_bats: Number of at bats
            sacrifice_flies: Number of sacrifice flies
            
        Returns:
            On-base percentage
        """
        denominator = at_bats + walks + hbp + sacrifice_flies
        if denominator == 0:
            return 0.0
        return (hits + walks + hbp) / denominator
    
    def calculate_slugging_percentage(self, singles: int, doubles: int, 
                                      triples: int, home_runs: int, 
                                      at_bats: int) -> float:
        """
        Calculate slugging percentage (SLG).
        
        Args:
            singles: Number of singles
            doubles: Number of doubles
            triples: Number of triples
            home_runs: Number of home runs
            at_bats: Number of at bats
            
        Returns:
            Slugging percentage
        """
        if at_bats == 0:
            return 0.0
        total_bases = singles + (2 * doubles) + (3 * triples) + (4 * home_runs)
        return total_bases / at_bats
    
    def calculate_ops(self, obp: float, slg: float) -> float:
        """
        Calculate OPS (On-base Plus Slugging).
        
        Args:
            obp: On-base percentage
            slg: Slugging percentage
            
        Returns:
            OPS value
        """
        return obp + slg
    
    def calculate_ops_from_stats(self, hits: int, doubles: int, triples: int,
                                 home_runs: int, walks: int, at_bats: int,
                                 hbp: int = 0, sacrifice_flies: int = 0) -> float:
        """
        Calculate OPS directly from counting stats.
        
        Args:
            hits: Total hits
            doubles: Number of doubles
            triples: Number of triples
            home_runs: Number of home runs
            walks: Number of walks
            at_bats: Number of at bats
            hbp: Hit by pitch
            sacrifice_flies: Sacrifice flies
            
        Returns:
            OPS value
        """
        singles = hits - doubles - triples - home_runs
        obp = self.calculate_on_base_percentage(hits, walks, hbp, at_bats, sacrifice_flies)
        slg = self.calculate_slugging_percentage(singles, doubles, triples, home_runs, at_bats)
        return self.calculate_ops(obp, slg)
    
    def calculate_iso(self, slugging: float, batting_avg: float) -> float:
        """
        Calculate Isolated Power (ISO).
        
        Args:
            slugging: Slugging percentage
            batting_avg: Batting average
            
        Returns:
            ISO value
        """
        return slugging - batting_avg
    
    def calculate_babip(self, hits: int, home_runs: int, at_bats: int,
                       strikeouts: int, sacrifice_flies: int = 0) -> float:
        """
        Calculate BABIP (Batting Average on Balls In Play).
        
        Args:
            hits: Number of hits
            home_runs: Number of home runs
            at_bats: Number of at bats
            strikeouts: Number of strikeouts
            sacrifice_flies: Sacrifice flies
            
        Returns:
            BABIP value
        """
        numerator = hits - home_runs
        denominator = at_bats - strikeouts - home_runs + sacrifice_flies
        if denominator == 0:
            return 0.0
        return numerator / denominator
    
    def calculate_woba(self, walks: int, hbp: int, singles: int, doubles: int,
                      triples: int, home_runs: int, at_bats: int,
                      sacrifice_flies: int = 0) -> float:
        """
        Calculate wOBA (Weighted On-Base Average).
        Using 2023 FanGraphs weights as default.
        
        Args:
            walks: Walks (BB)
            hbp: Hit by pitch
            singles: Singles
            doubles: Doubles
            triples: Triples
            home_runs: Home runs
            at_bats: At bats
            sacrifice_flies: Sacrifice flies
            
        Returns:
            wOBA value
        """
        # 2023 weights
        wBB = 0.690
        wHBP = 0.720
        w1B = 0.880
        w2B = 1.247
        w3B = 1.578
        wHR = 2.004
        
        numerator = (wBB * walks + wHBP * hbp + w1B * singles + 
                    w2B * doubles + w3B * triples + wHR * home_runs)
        denominator = at_bats + walks + sacrifice_flies + hbp
        
        if denominator == 0:
            return 0.0
        return numerator / denominator
    
    def calculate_rc(self, hits: int, walks: int, total_bases: int,
                    at_bats: int) -> float:
        """
        Calculate Runs Created (RC) - Basic version.
        
        Args:
            hits: Number of hits
            walks: Number of walks
            total_bases: Total bases
            at_bats: At bats
            
        Returns:
            Runs Created
        """
        if (at_bats + walks) == 0:
            return 0.0
        return ((hits + walks) * total_bases) / (at_bats + walks)


class PitchingAnalytics:
    """Calculate pitching statistics and advanced metrics."""
    
    def __init__(self):
        """Initialize pitching analytics."""
        pass
    
    def calculate_era(self, earned_runs: int, innings_pitched: float) -> float:
        """
        Calculate ERA (Earned Run Average).
        
        Args:
            earned_runs: Number of earned runs
            innings_pitched: Innings pitched
            
        Returns:
            ERA value
        """
        if innings_pitched == 0:
            return 0.0
        return (earned_runs * 9) / innings_pitched
    
    def calculate_whip(self, walks: int, hits: int, innings_pitched: float) -> float:
        """
        Calculate WHIP (Walks + Hits per Inning Pitched).
        
        Args:
            walks: Number of walks
            hits: Hits allowed
            innings_pitched: Innings pitched
            
        Returns:
            WHIP value
        """
        if innings_pitched == 0:
            return 0.0
        return (walks + hits) / innings_pitched
    
    def calculate_k_per_9(self, strikeouts: int, innings_pitched: float) -> float:
        """
        Calculate K/9 (Strikeouts per 9 innings).
        
        Args:
            strikeouts: Number of strikeouts
            innings_pitched: Innings pitched
            
        Returns:
            K/9 value
        """
        if innings_pitched == 0:
            return 0.0
        return (strikeouts * 9) / innings_pitched
    
    def calculate_bb_per_9(self, walks: int, innings_pitched: float) -> float:
        """
        Calculate BB/9 (Walks per 9 innings).
        
        Args:
            walks: Number of walks
            innings_pitched: Innings pitched
            
        Returns:
            BB/9 value
        """
        if innings_pitched == 0:
            return 0.0
        return (walks * 9) / innings_pitched
    
    def calculate_k_bb_ratio(self, strikeouts: int, walks: int) -> float:
        """
        Calculate K/BB ratio.
        
        Args:
            strikeouts: Number of strikeouts
            walks: Number of walks
            
        Returns:
            K/BB ratio
        """
        if walks == 0:
            return float('inf') if strikeouts > 0 else 0.0
        return strikeouts / walks
    
    def calculate_fip(self, home_runs: int, walks: int, hbp: int,
                     strikeouts: int, innings_pitched: float,
                     fip_constant: float = 3.10) -> float:
        """
        Calculate FIP (Fielding Independent Pitching).
        
        Args:
            home_runs: Home runs allowed
            walks: Walks (BB)
            hbp: Hit by pitch
            strikeouts: Strikeouts
            innings_pitched: Innings pitched
            fip_constant: League FIP constant (default 3.10)
            
        Returns:
            FIP value
        """
        if innings_pitched == 0:
            return 0.0
        
        numerator = (13 * home_runs) + (3 * (walks + hbp)) - (2 * strikeouts)
        return (numerator / innings_pitched) + fip_constant
    
    def calculate_babip_against(self, hits: int, home_runs: int, at_bats: int,
                               strikeouts: int, sacrifice_flies: int = 0) -> float:
        """
        Calculate BABIP against (for pitchers).
        
        Args:
            hits: Hits allowed
            home_runs: Home runs allowed
            at_bats: At bats against
            strikeouts: Strikeouts
            sacrifice_flies: Sacrifice flies
            
        Returns:
            BABIP against value
        """
        numerator = hits - home_runs
        denominator = at_bats - strikeouts - home_runs + sacrifice_flies
        if denominator == 0:
            return 0.0
        return numerator / denominator
    
    def calculate_win_percentage(self, wins: int, losses: int) -> float:
        """
        Calculate win percentage.
        
        Args:
            wins: Number of wins
            losses: Number of losses
            
        Returns:
            Win percentage
        """
        total_decisions = wins + losses
        if total_decisions == 0:
            return 0.0
        return wins / total_decisions


class TeamAnalytics:
    """Calculate team-level statistics and metrics."""
    
    def __init__(self):
        """Initialize team analytics."""
        pass
    
    def calculate_pythagorean_expectation(self, runs_scored: int,
                                         runs_allowed: int,
                                         exponent: float = 1.83) -> float:
        """
        Calculate Pythagorean expected win percentage.
        
        Args:
            runs_scored: Total runs scored
            runs_allowed: Total runs allowed
            exponent: Pythagorean exponent (default 1.83 for baseball)
            
        Returns:
            Expected win percentage
        """
        if runs_scored + runs_allowed == 0:
            return 0.0
        
        numerator = runs_scored ** exponent
        denominator = (runs_scored ** exponent) + (runs_allowed ** exponent)
        return numerator / denominator
    
    def calculate_run_differential(self, runs_scored: int, runs_allowed: int) -> int:
        """
        Calculate run differential.
        
        Args:
            runs_scored: Total runs scored
            runs_allowed: Total runs allowed
            
        Returns:
            Run differential
        """
        return runs_scored - runs_allowed
    
    def calculate_team_ops(self, team_obp: float, team_slg: float) -> float:
        """
        Calculate team OPS.
        
        Args:
            team_obp: Team on-base percentage
            team_slg: Team slugging percentage
            
        Returns:
            Team OPS
        """
        return team_obp + team_slg


class ComparativeAnalytics:
    """Compare players and calculate relative metrics."""
    
    def __init__(self):
        """Initialize comparative analytics."""
        pass
    
    def calculate_ops_plus(self, player_ops: float, league_avg_ops: float,
                          park_factor: float = 1.0) -> float:
        """
        Calculate OPS+ (normalized to league average).
        
        Args:
            player_ops: Player's OPS
            league_avg_ops: League average OPS
            park_factor: Park factor adjustment
            
        Returns:
            OPS+ value (100 = league average)
        """
        if league_avg_ops == 0:
            return 0.0
        return 100 * (player_ops / league_avg_ops) / park_factor
    
    def calculate_era_plus(self, player_era: float, league_avg_era: float,
                          park_factor: float = 1.0) -> float:
        """
        Calculate ERA+ (normalized to league average).
        
        Args:
            player_era: Player's ERA
            league_avg_era: League average ERA
            park_factor: Park factor adjustment
            
        Returns:
            ERA+ value (100 = league average)
        """
        if player_era == 0:
            return 0.0
        return 100 * (league_avg_era / player_era) * park_factor
    
    def rank_players(self, player_stats: pd.DataFrame, 
                    metric: str, ascending: bool = False) -> pd.DataFrame:
        """
        Rank players by a specific metric.
        
        Args:
            player_stats: DataFrame with player statistics
            metric: Column name to rank by
            ascending: Whether to rank in ascending order
            
        Returns:
            DataFrame with rankings
        """
        if metric not in player_stats.columns:
            return player_stats
        
        ranked = player_stats.copy()
        ranked['rank'] = ranked[metric].rank(ascending=ascending, method='min')
        return ranked.sort_values('rank')


if __name__ == "__main__":
    # Example usage
    batting = BattingAnalytics()
    pitching = PitchingAnalytics()
    
    # Calculate batting stats
    print("Batting Analytics Example:")
    ops = batting.calculate_ops_from_stats(
        hits=180, doubles=40, triples=5, home_runs=35,
        walks=70, at_bats=550
    )
    print(f"OPS: {ops:.3f}")
    
    # Calculate pitching stats
    print("\nPitching Analytics Example:")
    era = pitching.calculate_era(earned_runs=75, innings_pitched=200.0)
    print(f"ERA: {era:.2f}")
    
    fip = pitching.calculate_fip(
        home_runs=25, walks=50, hbp=10,
        strikeouts=220, innings_pitched=200.0
    )
    print(f"FIP: {fip:.2f}")
