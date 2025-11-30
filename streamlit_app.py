"""
MLB Statistics Web Application
Streamlit-based web interface for querying MLB statistics using natural language.
"""

import streamlit as st
import sys
import os

# Add src and utils directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from data_fetcher import MLBDataFetcher
from data_processor import MLBDataProcessor
from helpers import get_team_name, get_current_season, TEAM_IDS, LEAGUE_IDS
from mlb_gui import MLBQueryGUI
import re
from typing import Optional, Dict

# Page configuration
st.set_page_config(
    page_title="MLB Statistics Query",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stTextInput > div > div > input {
        font-size: 16px;
    }
    .stats-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 10px 0;
    }
    .stat-value {
        font-size: 24px;
        font-weight: bold;
        color: #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'fetcher' not in st.session_state:
    st.session_state.fetcher = MLBDataFetcher(use_cache=True)
    st.session_state.processor = MLBDataProcessor()
    st.session_state.history = []

# Helper class to adapt GUI logic for Streamlit
class StreamlitMLBQuery:
    """Adapter class to use MLBQueryGUI parsing logic with Streamlit."""
    
    def __init__(self):
        # Create a dummy GUI instance just to access its parsing methods
        self.parser = self._create_parser()
        self.fetcher = st.session_state.fetcher
        self.processor = st.session_state.processor
    
    def _create_parser(self):
        """Create parser instance without initializing GUI."""
        class Parser:
            STAT_MAPPINGS = MLBQueryGUI.STAT_MAPPINGS
            PITCHING_STATS = MLBQueryGUI.PITCHING_STATS
            
            def parse_query(self, query: str) -> Optional[Dict]:
                """Parse natural language query - copied from MLBQueryGUI."""
                if not query or len(query.strip()) < 3:
                    return None
                
                query_lower = query.lower()
                
                # Extract year
                year_match = re.search(r'\b(20\d{2}|19\d{2})\b', query)
                year = int(year_match.group(1)) if year_match else get_current_season()
                
                # Extract statistic category
                stat_type = None
                stat_group = "hitting"
                
                for term, api_name in self.STAT_MAPPINGS.items():
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
                
                # Extract player name
                query_words = {'where', 'did', 'rank', 'what', 'was', 'show', 'me', 'the', 'top',
                               'who', 'are', 'in', 'for', 'find', 'leaders', 'ranking', 'get', 'era',
                               'rbi', 'mlb', 'season', 'year', 'player', 'players', 'stats', 'statistics',
                               'which', 'when', 'how', 'had', 'has', 'have'}
                
                exclude_words = query_words.copy()
                if team_name:
                    exclude_words.update(team_name.lower().split())
                if league_name:
                    exclude_words.update(league_name.lower().split())
                
                name_patterns = [
                    r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)(?:\'s)?\b',
                    r'\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b',
                    r'\b([A-Z][a-z]{2,})(?:\'s)?\b'
                ]
                
                player_name = None
                for pattern in name_patterns:
                    matches = re.finditer(pattern, query)
                    for name_match in matches:
                        potential_name = name_match.group(0).replace("'s", "").strip()
                        potential_name_lower = potential_name.lower()
                        
                        words_in_name = potential_name_lower.split()
                        if all(word not in exclude_words for word in words_in_name):
                            if (potential_name_lower != team_name.lower() if team_name else True and
                                potential_name_lower != league_name.lower() if league_name else True and
                                len(potential_name) > 2):
                                player_name = potential_name
                                break
                    if player_name:
                        break
                
                # Determine query type
                ranking_keywords = ['rank', 'leader', 'leaders', 'top', 'best', 'worst']
                wants_ranking = any(keyword in query_lower for keyword in ranking_keywords)
                
                query_type = "leaders"
                team_ranking_keywords = ['teams', 'team', 'which team', 'what team']
                is_team_query = any(keyword in query_lower for keyword in team_ranking_keywords)
                
                if is_team_query and not player_name:
                    query_type = "team_rank"
                elif player_name and wants_ranking:
                    query_type = "rank"
                elif player_name and not wants_ranking:
                    query_type = "player_stat"
                
                # Extract limit
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
            
            def get_stat_display_name(self, api_name: str) -> str:
                """Get human-readable stat name."""
                for term, api in self.STAT_MAPPINGS.items():
                    if api == api_name:
                        return term.title()
                return api_name
        
        return Parser()
    
    def execute_query(self, query_text: str):
        """Execute a natural language query and return results."""
        parsed = self.parser.parse_query(query_text)
        
        if not parsed:
            return None, "Could not understand the query. Please try rephrasing."
        
        query_type = parsed['query_type']
        
        try:
            if query_type == 'team_rank':
                return self._handle_team_ranking(parsed)
            elif query_type == 'rank':
                return self._handle_player_ranking(parsed)
            elif query_type == 'player_stat':
                return self._handle_player_stat(parsed)
            else:  # leaders
                return self._handle_leaders(parsed)
        except Exception as e:
            return None, f"Error executing query: {str(e)}"
    
    def _handle_leaders(self, parsed):
        """Handle stats leaders query."""
        stats_data = self.fetcher.get_stats_leaders(
            parsed['stat_type'],
            season=parsed['year'],
            limit=50,
            stat_group=parsed['stat_group']
        )
        
        if not stats_data:
            return None, "No data found for this query."
        
        leaders_df = self.processor.extract_stats_leaders(
            stats_data,
            parsed['stat_type'],
            parsed['stat_group']
        )
        
        if leaders_df.empty:
            return None, "No leaders found for this statistic."
        
        # Apply filters
        if parsed['team_id']:
            leaders_df = leaders_df[leaders_df['team_id'] == parsed['team_id']]
        if parsed['league_id']:
            leaders_df = leaders_df[leaders_df['league_id'] == parsed['league_id']]
        
        leaders_df = leaders_df.head(parsed['limit'])
        
        return leaders_df, None
    
    def _handle_player_stat(self, parsed):
        """Handle individual player stat query."""
        player_results = self.fetcher.search_players(parsed['player_name'])
        
        if not player_results:
            return None, f"Could not find player: {parsed['player_name']}"
        
        player = player_results[0]
        player_id = player.get('id')
        full_name = player.get('fullName', parsed['player_name'])
        
        stats_data = self.fetcher.get_player_season_stats(
            player_id,
            parsed['year'],
            stat_group=parsed['stat_group']
        )
        
        if not stats_data:
            return None, f"No {parsed['year']} stats found for {full_name}"
        
        # Extract the specific stat value
        stat_value = "N/A"
        for stat_group_data in stats_data.get('stats', []):
            group = stat_group_data.get('group', {}).get('displayName', '')
            if (parsed['stat_group'] == 'hitting' and group == 'hitting') or \
               (parsed['stat_group'] == 'pitching' and group == 'pitching'):
                splits = stat_group_data.get('splits', [])
                if splits and len(splits) > 0:
                    stat_value = splits[0].get('stat', {}).get(parsed['stat_type'], "N/A")
                    break
        
        result_dict = {
            'player': full_name,
            'stat': self.parser.get_stat_display_name(parsed['stat_type']),
            'value': stat_value,
            'year': parsed['year']
        }
        
        return result_dict, None
    
    def _handle_player_ranking(self, parsed):
        """Handle player ranking query."""
        player_results = self.fetcher.search_players(parsed['player_name'])
        
        if not player_results:
            return None, f"Could not find player: {parsed['player_name']}"
        
        player = player_results[0]
        full_name = player.get('fullName', parsed['player_name'])
        
        stats_data = self.fetcher.get_stats_leaders(
            parsed['stat_type'],
            season=parsed['year'],
            limit=500,
            stat_group=parsed['stat_group']
        )
        
        if not stats_data:
            return None, "No ranking data available."
        
        leaders_df = self.processor.extract_stats_leaders(
            stats_data,
            parsed['stat_type'],
            parsed['stat_group']
        )
        
        if leaders_df.empty:
            return None, "No ranking data available."
        
        # Apply filters
        if parsed['team_id']:
            leaders_df = leaders_df[leaders_df['team_id'] == parsed['team_id']]
        if parsed['league_id']:
            leaders_df = leaders_df[leaders_df['league_id'] == parsed['league_id']]
        
        # Find player rank
        player_row = leaders_df[leaders_df['name'].str.contains(parsed['player_name'], case=False, na=False)]
        
        if player_row.empty:
            return None, f"{full_name} not found in rankings for this statistic."
        
        rank = player_row.index[0] + 1
        stat_value = player_row.iloc[0][parsed['stat_type']]
        
        result_dict = {
            'player': full_name,
            'stat': self.parser.get_stat_display_name(parsed['stat_type']),
            'value': stat_value,
            'rank': rank,
            'year': parsed['year'],
            'total_players': len(leaders_df)
        }
        
        return result_dict, None
    
    def _handle_team_ranking(self, parsed):
        """Handle team ranking query."""
        teams_data = self.fetcher.get_team_stats(
            parsed['stat_type'],
            season=parsed['year'],
            stat_group=parsed['stat_group']
        )
        
        if not teams_data:
            return None, "No team data found."
        
        teams_df = self.processor.extract_team_stats(
            teams_data,
            parsed['stat_type'],
            parsed['stat_group']
        )
        
        if teams_df.empty:
            return None, "No team rankings available."
        
        # Apply league filter
        if parsed['league_id']:
            teams_df = teams_df[teams_df['league_id'] == parsed['league_id']]
        
        return teams_df, None

# Initialize query handler
if 'query_handler' not in st.session_state:
    st.session_state.query_handler = StreamlitMLBQuery()

# Header
st.title("⚾ MLB Statistics Query")
st.markdown("Ask questions about MLB statistics in natural language!")

# Sidebar
with st.sidebar:
    st.header("ℹ️ How to Use")
    st.markdown("""
    **Ask questions like:**
    - "Top 10 home runs in 2024"
    - "What was Shohei Ohtani's batting average in 2024?"
    - "Rank Aaron Judge's home runs"
    - "ERA leaders for the Yankees"
    - "Which team had the most wins in 2024?"
    - "Best strikeouts in the American League"
    
    **Supported statistics:**
    - Hitting: HR, RBI, AVG, Hits, Runs, SB, OBP, SLG, OPS
    - Pitching: ERA, Wins, Saves, Strikeouts, WHIP
    """)
    
    st.divider()
    
    # Cache management
    st.header("⚙️ Settings")
    
    if st.button("📊 Show Cache Stats"):
        cache_stats = st.session_state.fetcher.get_cache_stats()
        st.info(f"""
        **Cache Statistics:**
        - Total entries: {cache_stats['total_entries']}
        - Cache size: {cache_stats['total_size_mb']:.2f} MB
        - Oldest entry: {cache_stats['oldest_entry']}
        - Newest entry: {cache_stats['newest_entry']}
        """)
    
    if st.button("🗑️ Clear Cache"):
        st.session_state.fetcher.clear_cache()
        st.success("Cache cleared successfully!")
    
    st.divider()
    
    # Query history
    if st.session_state.history:
        st.header("📜 Recent Queries")
        for i, hist_query in enumerate(reversed(st.session_state.history[-5:])):
            if st.button(f"🔄 {hist_query}", key=f"hist_{i}"):
                st.session_state.current_query = hist_query

# Main query input
query = st.text_input(
    "Enter your question:",
    placeholder="e.g., Top 10 home runs in 2024",
    value=st.session_state.get('current_query', ''),
    key="query_input"
)

# Execute query
if query:
    with st.spinner("Analyzing query and fetching data..."):
        result, error = st.session_state.query_handler.execute_query(query)
        
        # Add to history
        if query not in st.session_state.history:
            st.session_state.history.append(query)
        
        if error:
            st.error(error)
        elif result is not None:
            st.success("✅ Query executed successfully!")
            
            # Display results based on type
            if isinstance(result, dict):
                # Single player stat or ranking
                st.markdown("### Results")
                
                cols = st.columns(len(result))
                for i, (key, value) in enumerate(result.items()):
                    with cols[i]:
                        st.metric(label=key.replace('_', ' ').title(), value=value)
            else:
                # DataFrame results (leaders or team rankings)
                st.markdown("### Results")
                st.dataframe(
                    result,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Download button
                csv = result.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"mlb_stats_{query[:30].replace(' ', '_')}.csv",
                    mime="text/csv"
                )
        else:
            st.warning("No results found.")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px;'>
    <p>Data provided by MLB Stats API | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
