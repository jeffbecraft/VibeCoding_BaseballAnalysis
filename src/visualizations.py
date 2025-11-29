"""
Visualizations Module

This module provides visualization functions for MLB statistics analysis.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Tuple


class StatsVisualizer:
    """Create visualizations for baseball statistics."""
    
    def __init__(self, style: str = "darkgrid"):
        """
        Initialize the visualizer.
        
        Args:
            style: Seaborn style ('darkgrid', 'whitegrid', 'dark', 'white', 'ticks')
        """
        sns.set_style(style)
        self.colors = sns.color_palette("husl", 8)
    
    def plot_batting_comparison(self, players_data: pd.DataFrame,
                               metrics: List[str],
                               player_name_col: str = "playerName",
                               figsize: Tuple[int, int] = (12, 6)) -> plt.Figure:
        """
        Create a bar chart comparing batting metrics across players.
        
        Args:
            players_data: DataFrame with player statistics
            metrics: List of metric column names to compare
            player_name_col: Column name containing player names
            figsize: Figure size (width, height)
            
        Returns:
            Matplotlib figure
        """
        fig, axes = plt.subplots(1, len(metrics), figsize=figsize)
        
        if len(metrics) == 1:
            axes = [axes]
        
        for idx, metric in enumerate(metrics):
            if metric in players_data.columns:
                axes[idx].bar(players_data[player_name_col], 
                            players_data[metric],
                            color=self.colors[idx % len(self.colors)])
                axes[idx].set_title(f'{metric.upper()}')
                axes[idx].set_xlabel('Player')
                axes[idx].set_ylabel(metric)
                axes[idx].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return fig
    
    def plot_career_trajectory(self, player_data: pd.DataFrame,
                              metric: str,
                              season_col: str = "season",
                              player_name: str = "Player",
                              figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
        """
        Plot a player's performance over time.
        
        Args:
            player_data: DataFrame with player statistics by season
            metric: Metric to plot
            season_col: Column name for season
            player_name: Player name for title
            figsize: Figure size
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        if metric in player_data.columns and season_col in player_data.columns:
            ax.plot(player_data[season_col], player_data[metric], 
                   marker='o', linewidth=2, markersize=8, color=self.colors[0])
            ax.set_title(f"{player_name} - {metric.upper()} Over Time", fontsize=14)
            ax.set_xlabel('Season', fontsize=12)
            ax.set_ylabel(metric.upper(), fontsize=12)
            ax.grid(True, alpha=0.3)
            
            # Add trend line
            if len(player_data) > 1:
                z = np.polyfit(range(len(player_data)), player_data[metric], 1)
                p = np.poly1d(z)
                ax.plot(player_data[season_col], p(range(len(player_data))), 
                       "--", alpha=0.5, color='red', label='Trend')
                ax.legend()
        
        plt.tight_layout()
        return fig
    
    def plot_distribution(self, data: pd.DataFrame,
                         metric: str,
                         bins: int = 30,
                         figsize: Tuple[int, int] = (10, 6),
                         title: Optional[str] = None) -> plt.Figure:
        """
        Plot distribution of a metric (histogram with KDE).
        
        Args:
            data: DataFrame with statistics
            metric: Metric column to plot
            bins: Number of histogram bins
            figsize: Figure size
            title: Plot title
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        if metric in data.columns:
            ax.hist(data[metric], bins=bins, alpha=0.7, color=self.colors[0], 
                   edgecolor='black')
            
            # Add KDE
            data_clean = data[metric].dropna()
            if len(data_clean) > 1:
                ax2 = ax.twinx()
                data_clean.plot.kde(ax=ax2, color=self.colors[1], linewidth=2)
                ax2.set_ylabel('Density', fontsize=12)
            
            plot_title = title or f"Distribution of {metric.upper()}"
            ax.set_title(plot_title, fontsize=14)
            ax.set_xlabel(metric.upper(), fontsize=12)
            ax.set_ylabel('Frequency', fontsize=12)
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_scatter_comparison(self, data: pd.DataFrame,
                               x_metric: str,
                               y_metric: str,
                               label_col: Optional[str] = None,
                               figsize: Tuple[int, int] = (10, 8),
                               show_correlation: bool = True) -> plt.Figure:
        """
        Create scatter plot comparing two metrics.
        
        Args:
            data: DataFrame with statistics
            x_metric: Metric for x-axis
            y_metric: Metric for y-axis
            label_col: Column for point labels
            figsize: Figure size
            show_correlation: Whether to show correlation coefficient
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        if x_metric in data.columns and y_metric in data.columns:
            ax.scatter(data[x_metric], data[y_metric], 
                      alpha=0.6, s=100, color=self.colors[0])
            
            # Add labels if provided
            if label_col and label_col in data.columns:
                for idx, row in data.iterrows():
                    ax.annotate(row[label_col], 
                              (row[x_metric], row[y_metric]),
                              fontsize=8, alpha=0.7)
            
            # Add trend line
            if len(data) > 1:
                z = np.polyfit(data[x_metric].dropna(), 
                             data[y_metric].dropna(), 1)
                p = np.poly1d(z)
                x_line = np.linspace(data[x_metric].min(), 
                                    data[x_metric].max(), 100)
                ax.plot(x_line, p(x_line), "--", color='red', 
                       alpha=0.7, linewidth=2, label='Trend Line')
            
            # Show correlation
            if show_correlation:
                corr = data[[x_metric, y_metric]].corr().iloc[0, 1]
                ax.text(0.05, 0.95, f'Correlation: {corr:.3f}',
                       transform=ax.transAxes, fontsize=12,
                       verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            ax.set_title(f"{y_metric.upper()} vs {x_metric.upper()}", fontsize=14)
            ax.set_xlabel(x_metric.upper(), fontsize=12)
            ax.set_ylabel(y_metric.upper(), fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend()
        
        plt.tight_layout()
        return fig
    
    def plot_team_comparison(self, teams_data: pd.DataFrame,
                            metric: str,
                            team_name_col: str = "teamName",
                            figsize: Tuple[int, int] = (14, 6),
                            top_n: Optional[int] = None) -> plt.Figure:
        """
        Create horizontal bar chart for team comparison.
        
        Args:
            teams_data: DataFrame with team statistics
            metric: Metric to compare
            team_name_col: Column with team names
            figsize: Figure size
            top_n: Show only top N teams
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        if metric in teams_data.columns:
            # Sort and optionally limit
            sorted_data = teams_data.sort_values(metric, ascending=True)
            if top_n:
                sorted_data = sorted_data.tail(top_n)
            
            bars = ax.barh(sorted_data[team_name_col], sorted_data[metric],
                          color=self.colors[2])
            
            # Color top performers differently
            if len(bars) > 3:
                bars[-1].set_color(self.colors[3])
                bars[-2].set_color(self.colors[4])
                bars[-3].set_color(self.colors[5])
            
            ax.set_title(f"Team Comparison - {metric.upper()}", fontsize=14)
            ax.set_xlabel(metric.upper(), fontsize=12)
            ax.set_ylabel('Team', fontsize=12)
            ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        return fig
    
    def plot_heatmap(self, data: pd.DataFrame,
                    metrics: List[str],
                    figsize: Tuple[int, int] = (10, 8),
                    title: str = "Correlation Heatmap") -> plt.Figure:
        """
        Create correlation heatmap for multiple metrics.
        
        Args:
            data: DataFrame with statistics
            metrics: List of metrics to include
            figsize: Figure size
            title: Plot title
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Filter to available metrics
        available_metrics = [m for m in metrics if m in data.columns]
        
        if len(available_metrics) > 1:
            corr_matrix = data[available_metrics].corr()
            sns.heatmap(corr_matrix, annot=True, fmt='.2f', 
                       cmap='coolwarm', center=0, ax=ax,
                       square=True, linewidths=1, cbar_kws={"shrink": 0.8})
            ax.set_title(title, fontsize=14)
        
        plt.tight_layout()
        return fig
    
    def plot_radar_chart(self, player_data: Dict[str, float],
                        metrics: List[str],
                        player_name: str = "Player",
                        figsize: Tuple[int, int] = (8, 8)) -> plt.Figure:
        """
        Create radar chart for player metrics.
        
        Args:
            player_data: Dictionary of metric: value
            metrics: List of metrics to include
            player_name: Player name for title
            figsize: Figure size
            
        Returns:
            Matplotlib figure
        """
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='polar')
        
        # Filter available metrics
        available_metrics = [m for m in metrics if m in player_data]
        values = [player_data[m] for m in available_metrics]
        
        if len(available_metrics) > 2:
            # Number of variables
            num_vars = len(available_metrics)
            
            # Compute angle for each axis
            angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
            
            # Complete the loop
            values += values[:1]
            angles += angles[:1]
            
            # Plot
            ax.plot(angles, values, 'o-', linewidth=2, color=self.colors[0])
            ax.fill(angles, values, alpha=0.25, color=self.colors[0])
            
            # Fix axis to go in the right order
            ax.set_theta_offset(np.pi / 2)
            ax.set_theta_direction(-1)
            
            # Draw axis lines for each angle and label
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(available_metrics)
            
            ax.set_title(f"{player_name} - Performance Radar", 
                        fontsize=14, pad=20)
            ax.grid(True)
        
        plt.tight_layout()
        return fig
    
    def plot_box_plot(self, data: pd.DataFrame,
                     metric: str,
                     group_by: str,
                     figsize: Tuple[int, int] = (12, 6),
                     title: Optional[str] = None) -> plt.Figure:
        """
        Create box plot for metric grouped by category.
        
        Args:
            data: DataFrame with statistics
            metric: Metric to plot
            group_by: Column to group by
            figsize: Figure size
            title: Plot title
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        if metric in data.columns and group_by in data.columns:
            data.boxplot(column=metric, by=group_by, ax=ax, 
                        patch_artist=True, grid=False)
            
            plot_title = title or f"{metric.upper()} by {group_by}"
            ax.set_title(plot_title, fontsize=14)
            ax.set_xlabel(group_by, fontsize=12)
            ax.set_ylabel(metric.upper(), fontsize=12)
            plt.suptitle('')  # Remove default title
        
        plt.tight_layout()
        return fig
    
    def save_figure(self, fig: plt.Figure, filepath: str, dpi: int = 300) -> None:
        """
        Save figure to file.
        
        Args:
            fig: Matplotlib figure
            filepath: Output file path
            dpi: Resolution (dots per inch)
        """
        fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
        print(f"Figure saved to {filepath}")


if __name__ == "__main__":
    # Example usage
    viz = StatsVisualizer()
    
    # Create sample data
    sample_data = pd.DataFrame({
        'playerName': ['Player A', 'Player B', 'Player C', 'Player D'],
        'homeRuns': [35, 42, 28, 31],
        'rbi': [95, 110, 82, 88],
        'avg': [.285, .302, .268, .275],
        'ops': [.850, .920, .780, .810]
    })
    
    print("Creating sample visualization...")
    fig = viz.plot_batting_comparison(sample_data, ['homeRuns', 'rbi'])
    plt.show()
    print("Visualization complete!")
