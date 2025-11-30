"""
MLB Statistics Web Application
Streamlit-based web interface for querying MLB statistics using natural language.
"""

import streamlit as st
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src and utils directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from data_fetcher import MLBDataFetcher
from data_processor import MLBDataProcessor
from helpers import get_team_name, get_current_season, TEAM_IDS, LEAGUE_IDS
from stat_constants import STAT_MAPPINGS, PITCHING_STATS
from ai_query_handler import AIQueryHandler
from github_issue_reporter import GitHubIssueReporter
from logger import get_logger
import re
from typing import Optional, Dict

# Import version info
try:
    from src import __version__
except ImportError:
    __version__ = "1.0.0"

# Initialize monitoring (optional - requires sentry-sdk)
try:
    from src.monitoring import init_monitoring, capture_exception, add_breadcrumb
    MONITORING_ENABLED = init_monitoring()
    if MONITORING_ENABLED:
        logger = get_logger(__name__)
        logger.info("Production monitoring enabled (Sentry)")
    else:
        logger = get_logger(__name__)
        logger.info("Monitoring not configured (optional)")
except ImportError:
    logger = get_logger(__name__)
    logger.info("Monitoring module not available (install: pip install sentry-sdk)")
    MONITORING_ENABLED = False
    # Define no-op functions if monitoring not available
    def capture_exception(e, context=None): pass
    def add_breadcrumb(message, category='default', level='info', data=None): pass

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
    # Initialize AI query handler
    st.session_state.ai_handler = AIQueryHandler(
        st.session_state.fetcher,
        st.session_state.processor
    )
    # Initialize GitHub issue reporter
    st.session_state.issue_reporter = GitHubIssueReporter()

def get_health_status() -> Dict:
    """
    Get system health status for monitoring.
    
    Returns health check information including:
    - Overall status (healthy, degraded, unhealthy)
    - Cache statistics
    - AI availability
    - Version information
    
    This is useful for:
    - Container orchestration (K8s, Docker)
    - Monitoring dashboards
    - Automated health checks
    """
    health = {
        'status': 'healthy',
        'cache': {
            'enabled': st.session_state.fetcher.use_cache,
            'stats': {}
        },
        'ai': {
            'available': st.session_state.ai_handler.is_available(),
            'provider': None
        },
        'version': '1.0.0',
        'environment': os.getenv('ENVIRONMENT', 'production')
    }
    
    # Get cache statistics
    if st.session_state.fetcher.use_cache:
        try:
            health['cache']['stats'] = st.session_state.fetcher.get_cache_stats()
        except Exception as e:
            logger.warning(f"Could not get cache stats: {e}")
            health['status'] = 'degraded'
    
    # Get AI provider info
    if health['ai']['available']:
        try:
            provider_info = st.session_state.ai_handler.get_provider_info()
            health['ai']['provider'] = provider_info.get('provider')
            health['ai']['model'] = provider_info.get('model')
        except Exception as e:
            logger.warning(f"Could not get AI provider info: {e}")
    else:
        health['status'] = 'degraded'  # AI not available
    
    return health

# Helper class to adapt GUI logic for Streamlit
class StreamlitMLBQuery:
    """
    Adapter class to bridge Desktop GUI parsing logic with Streamlit Web App.
    
    WHY THIS EXISTS (Beginner Explanation):
    -------------------------------------------
    We have two interfaces:
    1. Desktop app (mlb_gui.py) - has excellent query parsing
    2. Web app (this file) - needs the same parsing
    
    Instead of copying all the parsing code, we "adapt" the Desktop GUI's
    parser to work in the web environment. This is called the "Adapter Pattern"
    and it helps us avoid duplicating 500+ lines of code!
    
    WHAT IT DOES:
    - Creates a lightweight "parser" that has all the query parsing logic
    - Shares the same stat mappings (home runs → homeRuns API name)
    - Reuses the same validation and extraction methods
    
    BENEFITS:
    - Only maintain query parsing logic in ONE place
    - Bug fixes automatically work in both interfaces
    - Consistent behavior between desktop and web apps
    """
    
    def __init__(self):
        """
        Initialize the Streamlit query adapter.
        
        PROCESS:
        1. Create a parser object (has query parsing methods)
        2. Link to the MLB data fetcher (gets data from API)
        3. Link to the processor (formats the data nicely)
        """
        # Create a dummy GUI instance just to access its parsing methods
        # (We don't actually show a GUI, we just borrow its brain!)
        self.parser = self._create_parser()
        
        # Use the same fetcher and processor from session state
        # (This ensures caching works across queries)
        self.fetcher = st.session_state.fetcher
        self.processor = st.session_state.processor
    
    def _create_parser(self):
        """
        Create parser instance without initializing full GUI.
        
        WHAT THIS DOES (Beginner Explanation):
        ---------------------------------------
        Imagine you have a Swiss Army knife (MLBQueryGUI) with 20 tools,
        but you only need the scissors. Instead of carrying the whole knife,
        we extract just the scissors (parsing methods) into a smaller tool.
        
        HOW IT WORKS:
        1. Create a lightweight "Parser" class
        2. Copy over the stat mappings dictionary
           (e.g., {"home runs": "homeRuns", "hr": "homeRuns"})
        3. Copy over the pitching stats list
           (so we know when to fetch pitching vs batting data)
        4. Include the main parsing method (parse_query)
        
        RETURNS:
        A Parser object with just the query parsing capabilities,
        no GUI components like buttons or text boxes.
        
        EXAMPLE:
        parser.parse_query("Aaron Judge home runs 2024")
        → Returns: {type: "player_stat", player: "Aaron Judge", 
                    stat: "homeRuns", year: 2024}
        """
        class Parser:
            # Use shared stat mappings from stat_constants module
            # This dictionary translates common terms to API field names
            # Example: "home runs" → "homeRuns" (what the MLB API expects)
            STAT_MAPPINGS = STAT_MAPPINGS
            
            # Use shared pitching stats list so we know when to request pitching data
            # Example: "era" is in PITCHING_STATS, so use stat_group="pitching"
            PITCHING_STATS = PITCHING_STATS
            
            def parse_query(self, query: str) -> Optional[Dict]:
                """Parse natural language query using shared constants."""
                if not query or len(query.strip()) < 3:
                    return None
                
                query_lower = query.lower()
                
                # Check for career queries
                is_career_query = 'career' in query_lower
                
                # Extract year (not used for career queries)
                year_match = re.search(r'\b(20\d{2}|19\d{2})\b', query)
                year = int(year_match.group(1)) if year_match and not is_career_query else get_current_season()
                
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
                
                if not stat_type and not is_career_query:
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
                
                # Check for comparison indicators early (needed for player name extraction)
                comparison_words = ['more', 'better', 'worse', 'less', 'fewer']
                has_comparison_word = any(word in query_lower for word in comparison_words)
                has_or = ' or ' in query_lower
                
                # Extract player name
                query_words = {'where', 'did', 'rank', 'what', 'was', 'show', 'me', 'the', 'top',
                               'who', 'are', 'in', 'for', 'find', 'leaders', 'ranking', 'get', 'era',
                               'rbi', 'mlb', 'season', 'year', 'player', 'players', 'stats', 'statistics',
                               'which', 'when', 'how', 'had', 'has', 'have', 'runs', 'hits', 'wins',
                               'saves', 'walks', 'doubles', 'triples', 'strikeouts', 'innings', 'games',
                               'average', 'errors', 'stolen', 'bases', 'percentage', 'batted', 'whip',
                               'career', 'total', 'totals', 'all', 'time'}
                
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
                all_player_names = []  # Collect all potential player names for comparisons
                
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
                                # For comparisons, collect all names; for others, take the first
                                if not player_name:
                                    player_name = potential_name
                                all_player_names.append(potential_name)
                    if player_name and not (has_comparison_word and has_or):  # Don't break early for comparison queries
                        break
                
                # Determine query type
                ranking_keywords = ['rank', 'leader', 'leaders', 'top', 'best', 'worst']
                wants_ranking = any(keyword in query_lower for keyword in ranking_keywords)
                
                # Check for comparison queries
                # Direct comparison keywords
                comparison_keywords = ['compare', 'versus', 'vs', 'vs.', 'against', 'better than', 'worse than']
                has_comparison_keyword = any(keyword in query_lower for keyword in comparison_keywords)
                
                # Indirect comparison already detected earlier (has_comparison_word and has_or)
                # It's a comparison if: explicit keyword OR (comparison word + 'or')
                is_comparison = has_comparison_keyword or (has_comparison_word and has_or)
                
                # Career-specific query types
                if is_career_query:
                    if player_name:
                        query_type = "player_career"
                    elif team_name:
                        query_type = "team_career"
                    else:
                        # Generic career query - might need AI
                        return None
                else:
                    # Check if this is asking about team-level stats (e.g., "which team had the most wins")
                    # vs team-filtered player stats (e.g., "rank the Orioles by home runs")
                    team_level_keywords = ['which team', 'what team', 'team with', 'team had']
                    is_team_level_query = any(keyword in query_lower for keyword in team_level_keywords)
                    
                    if is_team_level_query and not player_name:
                        query_type = "team_rank"
                    elif is_comparison and stat_type:
                        query_type = "comparison"
                    elif player_name and wants_ranking:
                        query_type = "rank"
                    elif player_name and not wants_ranking:
                        query_type = "player_stat"
                    # If team_name is present but no player_name, it's a team-filtered leaders query
                    # This stays as "leaders" query type
                    else:
                        query_type = "leaders"
                
                # Extract limit
                limit = 10
                limit_match = re.search(r'\btop\s+(\d+)\b', query_lower)
                if limit_match:
                    limit = int(limit_match.group(1))
                
                return {
                    'player_name': player_name,
                    'all_player_names': all_player_names,  # For comparison queries
                    'stat_type': stat_type,
                    'stat_group': stat_group,
                    'year': year,
                    'query_type': query_type,
                    'limit': limit,
                    'team_id': team_id,
                    'team_name': team_name,
                    'league_id': league_id,
                    'league_name': league_name,
                    'is_career': is_career_query
                }
            
            def needs_ai_for_comparison(self, query: str, parsed: Dict) -> bool:
                """Check if this comparison query needs AI for a direct answer."""
                if parsed.get('query_type') != 'comparison':
                    return False
                
                query_lower = query.lower()
                
                # Questions asking "who had more/better/less" need direct answers
                direct_comparison_patterns = [
                    r'who\s+(had|has|have|hit|pitched|got|scored|stole)\s+(more|better|fewer|less)',
                    r'which\s+(player|person|team)\s+(had|has|have|hit|pitched)\s+(more|better|fewer|less)',
                    r'(more|better|fewer|less)\s+\w+\s*[,]?\s+\w+\s+or\s+\w+'
                ]
                
                needs_direct_answer = any(re.search(pattern, query_lower) for pattern in direct_comparison_patterns)
                
                # Also check if there are 2+ player names (indicating a multi-player comparison)
                # that would benefit from AI's ability to extract and compare multiple entities
                has_multiple_players = len(parsed.get('all_player_names', [])) >= 2
                
                return needs_direct_answer and has_multiple_players
            
            def get_stat_display_name(self, api_name: str) -> str:
                """Get human-readable stat name."""
                for term, api in self.STAT_MAPPINGS.items():
                    if api == api_name:
                        return term.title()
                return api_name
        
        return Parser()
    
    def execute_query(self, query_text: str):
        """Execute a natural language query and return results."""
        # Add breadcrumb for monitoring
        add_breadcrumb(
            message=f"Executing query: {query_text[:100]}",
            category='query',
            level='info',
            data={'query_length': len(query_text)}
        )
        
        parsed = self.parser.parse_query(query_text)
        
        if not parsed:
            # Try AI-powered query handling as fallback
            if st.session_state.ai_handler and st.session_state.ai_handler.is_available():
                st.info("🤖 Standard query pattern not recognized. Using AI to interpret your question...")
                
                # Create progress placeholder
                progress_container = st.empty()
                steps_container = st.empty()
                
                # Extract year from query if present
                year_match = re.search(r'\b(20\d{2}|19\d{2})\b', query_text)
                season = int(year_match.group(1)) if year_match else get_current_season()
                
                # Progress callback
                def update_progress(step: str, detail: str):
                    progress_container.info(f"**{step}:** {detail}")
                
                ai_result = st.session_state.ai_handler.handle_query_with_retry(query_text, season, report_progress=update_progress)
                
                # Clear progress, show steps
                progress_container.empty()
                
                # Display processing steps
                if ai_result.get('steps'):
                    with st.expander("🔍 How AI Processed Your Question", expanded=True):
                        for step in ai_result['steps']:
                            st.write(step)
                
                if ai_result.get('success'):
                    return ai_result, None
                else:
                    return None, f"AI Query Failed: {ai_result.get('error', 'Unknown error')}"
            else:
                return None, "Could not understand the query. Please try rephrasing."
        
        query_type = parsed['query_type']
        
        # Check if this comparison needs AI for a direct answer
        if query_type == 'comparison' and self.parser.needs_ai_for_comparison(query_text, parsed):
            if st.session_state.ai_handler and st.session_state.ai_handler.is_available():
                st.info("🤖 This comparison question needs a direct answer. Using AI...")
                
                # Create progress placeholder
                progress_container = st.empty()
                
                # Extract year
                year_match = re.search(r'\b(20\d{2}|19\d{2})\b', query_text)
                season = int(year_match.group(1)) if year_match else get_current_season()
                
                # Progress callback
                def update_progress(step: str, detail: str):
                    progress_container.info(f"**{step}:** {detail}")
                
                ai_result = st.session_state.ai_handler.handle_query_with_retry(query_text, season, report_progress=update_progress)
                
                # Clear progress, show steps
                progress_container.empty()
                
                # Display processing steps
                if ai_result.get('steps'):
                    with st.expander("🔍 How AI Processed Your Question", expanded=False):
                        for step in ai_result['steps']:
                            st.write(step)
                
                if ai_result.get('success'):
                    return ai_result, None
                else:
                    # If AI fails, fall through to standard comparison handler
                    st.warning(f"AI comparison failed: {ai_result.get('error')}. Showing ranked list instead...")
        
        try:
            if query_type == 'team_rank':
                return self._handle_team_ranking(parsed)
            elif query_type == 'comparison':
                return self._handle_comparison(parsed)
            elif query_type == 'rank':
                return self._handle_player_ranking(parsed)
            elif query_type == 'player_stat':
                return self._handle_player_stat(parsed, show_context=True)
            elif query_type == 'player_career':
                return self._handle_player_career(parsed)
            elif query_type == 'team_career':
                return self._handle_team_career(parsed)
            else:  # leaders
                return self._handle_leaders(parsed)
        except Exception as e:
            # Capture exception for monitoring
            capture_exception(e, context={
                'query_text': query_text,
                'query_type': query_type if 'query_type' in locals() else 'unknown',
                'parsed': parsed if 'parsed' in locals() else None
            })
            
            # If standard query fails, try AI fallback
            if st.session_state.ai_handler and st.session_state.ai_handler.is_available():
                st.warning(f"⚠️ Standard query failed: {str(e)}")
                st.info("🤖 Trying AI-powered query interpretation...")
                
                # Create progress placeholder
                progress_container = st.empty()
                
                year_match = re.search(r'\b(20\d{2}|19\d{2})\b', query_text)
                season = int(year_match.group(1)) if year_match else get_current_season()
                
                # Progress callback
                def update_progress(step: str, detail: str):
                    progress_container.info(f"**{step}:** {detail}")
                
                ai_result = st.session_state.ai_handler.handle_query_with_retry(query_text, season, report_progress=update_progress)
                
                # Clear progress, show steps
                progress_container.empty()
                
                # Display processing steps
                if ai_result.get('steps'):
                    with st.expander("🔍 How AI Processed Your Question", expanded=True):
                        for step in ai_result['steps']:
                            st.write(step)
                
                if ai_result.get('success'):
                    return ai_result, None
                else:
                    return None, f"Both standard and AI queries failed. Error: {str(e)}"
            else:
                return None, f"Error executing query: {str(e)}"
    
    def _handle_leaders(self, parsed):
        """Handle stats leaders query."""
        # When filtering by team, we need all players from that team
        # When not filtering, limit to top 50 for performance
        limit = None if parsed['team_id'] else 50
        include_all = True if parsed['team_id'] or parsed['league_id'] else False
        
        stats_data = self.fetcher.get_stats_leaders(
            parsed['stat_type'],
            season=parsed['year'],
            limit=limit if not include_all else 500,
            stat_group=parsed['stat_group'],
            team_id=parsed['team_id'],
            league_id=parsed['league_id'],
            include_all=include_all
        )
        
        if not stats_data:
            return None, "No data found for this query."
        
        leaders_df = self.processor.extract_stats_leaders(stats_data)
        
        if leaders_df.empty:
            return None, "No leaders found for this statistic."
        
        # Team and league filtering is already done by get_stats_leaders when include_all=True
        # Only apply limit if no team/league filter
        if not parsed['team_id'] and not parsed['league_id']:
            leaders_df = leaders_df.head(parsed['limit'])
        
        return leaders_df, None
    
    def _handle_player_stat(self, parsed, show_context=False):
        """Handle individual player stat query."""
        player_results = self.fetcher.search_players(parsed['player_name'])
        
        if not player_results:
            return None, f"Could not find player: {parsed['player_name']}"
        
        player = player_results[0]
        player_id = player.get('id')
        full_name = player.get('fullName', parsed['player_name'])
        
        stats_data = self.fetcher.get_player_season_stats(
            player_id,
            parsed['year']
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
        
        # If show_context is True, also get league leaders to show ranking
        if show_context:
            leaders_data = self.fetcher.get_stats_leaders(
                parsed['stat_type'],
                season=parsed['year'],
                limit=50,
                stat_group=parsed['stat_group'],
                team_id=parsed.get('team_id'),
                league_id=parsed.get('league_id')
            )
            
            if leaders_data:
                leaders_df = self.processor.extract_stats_leaders(leaders_data)
                if not leaders_df.empty:
                    # Find player's rank
                    player_rank_row = leaders_df[leaders_df['playerName'].str.contains(parsed['player_name'], case=False, na=False)]
                    if not player_rank_row.empty:
                        result_dict['rank'] = player_rank_row.iloc[0]['rank']
                        result_dict['leaders_context'] = leaders_df.head(20)  # Show top 20 for context
        
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
        
        leaders_df = self.processor.extract_stats_leaders(stats_data)
        
        if leaders_df.empty:
            return None, "No ranking data available."
        
        # Apply filters
        if parsed['team_id']:
            leaders_df = leaders_df[leaders_df['teamId'] == parsed['team_id']]
        if parsed['league_id']:
            # League filtering was already done in get_stats_leaders
            pass
        
        # Find player rank
        player_row = leaders_df[leaders_df['playerName'].str.contains(parsed['player_name'], case=False, na=False)]
        
        if player_row.empty:
            return None, f"{full_name} not found in rankings for this statistic."
        
        rank = player_row.iloc[0]['rank']
        stat_value = player_row.iloc[0]['value']
        
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
            season=parsed['year'],
            stat_group=parsed['stat_group']
        )
        
        if not teams_data:
            return None, "No team data found."
        
        teams_df = self.processor.extract_team_stats(
            teams_data,
            parsed['stat_type']
        )
        
        if teams_df.empty:
            return None, "No team rankings available."
        
        return teams_df, None
    
    def _handle_comparison(self, parsed):
        """Handle comparison queries - show rankings with both entities highlighted."""
        import pandas as pd
        
        # Get all leaders for the stat
        stats_data = self.fetcher.get_stats_leaders(
            parsed['stat_type'],
            season=parsed['year'],
            limit=100,
            stat_group=parsed['stat_group'],
            team_id=parsed.get('team_id'),
            league_id=parsed.get('league_id'),
            include_all=True
        )
        
        if not stats_data:
            return None, "No data found for comparison."
        
        leaders_df = self.processor.extract_stats_leaders(stats_data)
        
        if leaders_df.empty:
            return None, "No leaders found for this statistic."
        
        # Return ranked list with comparison flag
        return {
            'type': 'comparison_ranking',
            'data': leaders_df,
            'stat': self.parser.get_stat_display_name(parsed['stat_type']),
            'year': parsed['year'],
            'search_term': parsed.get('player_name', '')
        }, None
    
    def _handle_player_career(self, parsed):
        """Handle player career statistics query."""
        import pandas as pd
        
        player_results = self.fetcher.search_players(parsed['player_name'])
        
        if not player_results:
            return None, f"Could not find player: {parsed['player_name']}"
        
        player = player_results[0]
        player_id = player.get('id')
        full_name = player.get('fullName', parsed['player_name'])
        
        # Get career stats
        career_data = self.fetcher.get_player_career_stats(
            player_id,
            parsed['stat_group']
        )
        
        if not career_data:
            return None, f"No career stats found for {full_name}"
        
        # If a specific stat was requested, show career total for that stat
        if parsed['stat_type']:
            career_totals = self.processor.aggregate_career_stats(career_data, parsed['stat_group'])
            
            if not career_totals:
                return None, f"Could not calculate career stats for {full_name}"
            
            # Get the specific stat value
            stat_value = "N/A"
            if parsed['stat_type'] in ['avg', 'obp', 'slg', 'ops', 'era', 'whip']:
                # Rate stat
                stat_value = career_totals['career_rates'].get(parsed['stat_type'], 'N/A')
            else:
                # Counting stat
                stat_value = career_totals['totals'].get(parsed['stat_type'], 'N/A')
            
            result_dict = {
                'player': full_name,
                'stat': self.parser.get_stat_display_name(parsed['stat_type']),
                'career_value': stat_value,
                'seasons': career_totals['seasons']
            }
            
            return result_dict, None
        else:
            # Show full career breakdown by season
            career_df = self.processor.create_career_dataframe(career_data)
            
            if career_df.empty:
                return None, f"No career data available for {full_name}"
            
            # Add career totals row
            career_totals = self.processor.aggregate_career_stats(career_data, parsed['stat_group'])
            
            return {
                'type': 'career_breakdown',
                'player': full_name,
                'by_season': career_df,
                'totals': career_totals
            }, None
    
    def _handle_team_career(self, parsed):
        """Handle team career statistics query."""
        import pandas as pd
        
        # Get team career stats (default to last 20 years if not specified)
        current_year = get_current_season()
        start_year = parsed.get('start_year', current_year - 19)
        end_year = parsed.get('end_year', current_year)
        
        career_data = self.fetcher.get_team_career_stats(
            parsed['team_id'],
            parsed['stat_group'],
            start_year,
            end_year
        )
        
        if not career_data:
            return None, f"No career stats found for {parsed['team_name']}"
        
        # Create DataFrame
        rows = []
        for season_data in career_data:
            season = season_data.get('season')
            stat = season_data.get('stat', {})
            
            row = {'season': season}
            row.update(stat)
            rows.append(row)
        
        career_df = pd.DataFrame(rows)
        
        if career_df.empty:
            return None, f"No career data available for {parsed['team_name']}"
        
        career_df = self.processor.convert_numeric_columns(career_df, exclude_cols=['season'])
        
        return {
            'type': 'team_career',
            'team': parsed['team_name'],
            'data': career_df
        }, None

# Initialize query handler
if 'query_handler' not in st.session_state:
    st.session_state.query_handler = StreamlitMLBQuery()

# Header
st.title("⚾ MLB Statistics Query")
st.markdown("Ask questions about MLB statistics in natural language!")

# Sidebar
with st.sidebar:
    st.header("ℹ️ How to Use")
    
    # Version information
    st.caption(f"⚾ MLB Stats Analysis v{__version__}")
    environment = os.getenv('ENVIRONMENT', 'production')
    if environment != 'production':
        st.caption(f"Environment: {environment}")
    
    st.markdown("""
    **Ask questions like:**
    - "Top 10 home runs in 2025"
    - "What was Gunnar Henderson's batting average in 2025?"
    - "Rank Anthony Santander's home runs"
    - "ERA leaders for the Orioles"
    - "Which team had the most wins in 2025?"
    - "Best strikeouts in the American League"
    - **"What are Adley Rutschman's career home runs?"**
    - **"Show me Ryan Mountcastle's career stats"**
    - **"Orioles career wins"**
    - **"Compare Gunnar Henderson vs Anthony Santander home runs"**
    - **"Corbin Burnes versus Kyle Bradish ERA"**
    
    **Supported statistics:**
    - Hitting: HR, RBI, AVG, Hits, Runs, SB, OBP, SLG, OPS
    - Pitching: ERA, Wins, Saves, Strikeouts, WHIP
    
    **New: Career Stats!**
    - Use "career" in your query to get all-time totals
    - Works for both players and teams
    
    **New: Comparisons!**
    - Use "compare", "vs", or "versus" to see ranked results
    - Both players/teams shown in context of league leaders
    """)
    
    st.divider()
    
    # System Health Check
    st.header("🏥 System Health")
    
    health_status = get_health_status()
    
    # Overall status
    if health_status['status'] == 'healthy':
        st.success("✅ All systems operational")
    elif health_status['status'] == 'degraded':
        st.warning("⚠️ Some features unavailable")
    else:
        st.error("❌ System issues detected")
    
    # Cache stats
    if health_status['cache']['enabled']:
        cache_stats = health_status['cache']['stats']
        valid_entries = cache_stats.get('valid_entries', 0)
        total_entries = cache_stats.get('total_entries', 0)
        st.metric("Cached Entries", f"{valid_entries}")
        st.caption(f"Total: {total_entries} | Size: {cache_stats.get('total_size_mb', 0)} MB")
    
    # AI status
    if health_status['ai']['available']:
        st.caption(f"✓ AI: {health_status['ai']['provider']}")
    else:
        st.caption("✗ AI: Not available")
    
    st.divider()
    
    # AI Query Status
    st.header("🤖 AI-Powered Queries")
    
    if st.session_state.ai_handler.is_available():
        provider_info = st.session_state.ai_handler.get_provider_info()
        
        if provider_info['provider'] == 'ollama':
            st.success("✅ AI Assistant Enabled (FREE)")
            st.caption(f"""
            Using **Ollama** ({provider_info['model']}) - completely free!
            AI can answer questions that don't match standard patterns.
            """)
        elif provider_info['provider'] == 'openai':
            st.success("✅ AI Assistant Enabled")
            st.caption(f"""
            Using **OpenAI** ({provider_info['model']})
            AI can answer questions that don't match standard patterns.
            """)
        
        # Test AI connection
        if st.button("Test AI Connection"):
            test_result = st.session_state.ai_handler.test_connection()
            if test_result['success']:
                st.success(f"✅ {test_result['message']}")
                if test_result.get('provider'):
                    st.caption(f"Provider: {test_result['provider']}")
            else:
                st.error(f"❌ {test_result['message']}")
    else:
        st.warning("⚠️ AI Assistant Not Available")
        st.caption("""
        To enable AI-powered queries, choose one option:
        """)
        
        with st.expander("🆓 Option 1: Ollama (FREE - Recommended)"):
            st.markdown("""
            **Run AI models locally - completely free!**
            
            1. Download Ollama from [ollama.com](https://ollama.com)
            2. Install and run it
            3. Download a model:
               ```bash
               ollama pull llama3.2
               ```
            4. Restart this app
            
            **Benefits:**
            - ✅ Completely free
            - ✅ Runs on your computer
            - ✅ Private (no data sent to cloud)
            - ✅ No API keys needed
            """)
        
        with st.expander("💳 Option 2: OpenAI (Paid)"):
            st.markdown("""
            **Use OpenAI's cloud models**
            
            1. Get API key from [platform.openai.com](https://platform.openai.com)
            2. Set environment variable:
               ```bash
               export OPENAI_API_KEY='your-key-here'
               ```
            3. Restart this app
            
            **Note:** Costs $0.01-$0.05 per AI query
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
    
    # Feedback / Issue Reporting
    st.header("💬 Report an Issue")
    
    if st.session_state.issue_reporter.is_available():
        st.caption("Issues are automatically logged to GitHub")
        
        with st.expander("📝 Submit Feedback"):
            feedback_type = st.selectbox(
                "Type",
                ["Bug Report", "Feature Request", "General Feedback"],
                key="feedback_type"
            )
            
            if feedback_type == "Bug Report":
                st.text_area(
                    "What went wrong?",
                    placeholder="Describe the bug...",
                    key="bug_description",
                    height=100
                )
                st.text_input(
                    "Query (if applicable)",
                    placeholder="The question you asked...",
                    key="bug_query"
                )
                st.text_input(
                    "Your email (optional, for follow-up)",
                    placeholder="your.email@example.com",
                    key="bug_email"
                )
                
                if st.button("Submit Bug Report", key="submit_bug"):
                    description = st.session_state.get('bug_description', '').strip()
                    if description:
                        result = st.session_state.issue_reporter.create_bug_report(
                            description=description,
                            query=st.session_state.get('bug_query'),
                            user_email=st.session_state.get('bug_email')
                        )
                        if result['success']:
                            st.success(f"✅ {result['message']}")
                            st.info(f"[View issue]({result['url']})")
                        else:
                            st.error(f"❌ {result['message']}")
                    else:
                        st.warning("Please describe the bug")
            
            elif feedback_type == "Feature Request":
                st.text_input(
                    "Feature title",
                    placeholder="Brief feature name...",
                    key="feature_title"
                )
                st.text_area(
                    "Description",
                    placeholder="Describe the feature you'd like...",
                    key="feature_description",
                    height=100
                )
                st.text_input(
                    "Your email (optional)",
                    placeholder="your.email@example.com",
                    key="feature_email"
                )
                
                if st.button("Submit Feature Request", key="submit_feature"):
                    title = st.session_state.get('feature_title', '').strip()
                    description = st.session_state.get('feature_description', '').strip()
                    if title and description:
                        result = st.session_state.issue_reporter.create_feature_request(
                            title=title,
                            description=description,
                            user_email=st.session_state.get('feature_email')
                        )
                        if result['success']:
                            st.success(f"✅ {result['message']}")
                            st.info(f"[View issue]({result['url']})")
                        else:
                            st.error(f"❌ {result['message']}")
                    else:
                        st.warning("Please provide title and description")
            
            else:  # General Feedback
                st.text_area(
                    "Your feedback",
                    placeholder="Tell us what you think...",
                    key="general_feedback",
                    height=100
                )
                st.text_input(
                    "Your email (optional)",
                    placeholder="your.email@example.com",
                    key="general_email"
                )
                
                if st.button("Submit Feedback", key="submit_general"):
                    feedback = st.session_state.get('general_feedback', '').strip()
                    if feedback:
                        result = st.session_state.issue_reporter.create_general_feedback(
                            feedback=feedback,
                            user_email=st.session_state.get('general_email')
                        )
                        if result['success']:
                            st.success(f"✅ {result['message']}")
                            st.info(f"[View issue]({result['url']})")
                        else:
                            st.error(f"❌ {result['message']}")
                    else:
                        st.warning("Please provide your feedback")
    else:
        st.info("""
        📧 To report issues, please:
        - Email: jeffbecraft@gmail.com
        - GitHub: [Create an issue](https://github.com/jeffbecraft/VibeCoding_BaseballAnalysis/issues)
        """)
    
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
    # Execute query with spinner (only during execution, not display)
    with st.spinner("Analyzing query and fetching data..."):
        result, error = st.session_state.query_handler.execute_query(query)
    
    # Add to history
    if query not in st.session_state.history:
        st.session_state.history.append(query)
    
    # Display results (outside spinner context)
    if error:
        st.error(error)
        
        # Retry button for errors
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("🔄 Retry Question", key="retry_error", help="Clear cache and try again with fresh AI generation"):
                # Clear cache for this specific query if it was an AI query
                if st.session_state.ai_handler:
                    from utils.ai_code_cache import AICodeCache
                    import re
                    year_match = re.search(r'\b(20\d{2}|19\d{2})\b', query)
                    season = int(year_match.group(1)) if year_match else get_current_season()
                    
                    cache = AICodeCache()
                    cache_key = cache._generate_cache_key(query, season)
                    removed = cache.remove(cache_key)
                    
                    if removed:
                        st.success("✓ Cache cleared! Re-running query...")
                    else:
                        st.info("No cached result found. Re-running query...")
                    
                    # Rerun to execute the query again
                    st.rerun()
        with col2:
            if st.button("📝 Edit Query", key="edit_error", help="Modify your question"):
                st.info("💡 Edit your question above and submit again")
    elif result is not None:
        st.success("✅ Query executed successfully!")
        
        # Check if this is an AI-generated result
        if isinstance(result, dict) and result.get('ai_generated'):
            st.info("🤖 This answer was generated using AI")
            
            # Display the answer
            if result.get('answer'):
                st.markdown(f"### {result['answer']}")
            
            # Display explanation
            if result.get('explanation'):
                st.caption(result['explanation'])
            
            # Show the data if available
            if result.get('data'):
                data = result['data']
                if isinstance(data, list) and len(data) > 0:
                    import pandas as pd
                    st.dataframe(pd.DataFrame(data), width='stretch', hide_index=True)
                elif hasattr(data, 'to_dict'):  # DataFrame
                    st.dataframe(data, width='stretch', hide_index=True)
                else:
                    st.json(data)
            
            # Option to see generated code
            with st.expander("🔍 View Generated Code"):
                st.code(result.get('generated_code', 'No code available'), language='python')
                st.caption("This code was automatically generated by AI to answer your question")
            
            # Retry button for AI-generated results
            st.markdown("---")
            st.markdown("**Not satisfied with this answer?**")
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("🔄 Retry with Fresh AI", key="retry_ai", help="Clear cached code and generate a new answer"):
                    # Clear the cache for this specific query
                    from utils.ai_code_cache import AICodeCache
                    import re
                    year_match = re.search(r'\b(20\d{2}|19\d{2})\b', query)
                    season = int(year_match.group(1)) if year_match else get_current_season()
                    
                    cache = AICodeCache()
                    cache_key = cache._generate_cache_key(query, season)
                    removed = cache.remove(cache_key)
                    
                    if removed:
                        st.success("✓ Cached answer cleared! Generating fresh response...")
                    else:
                        st.info("Generating new response...")
                    
                    # Rerun to execute the query again with fresh AI generation
                    st.rerun()
            with col2:
                if st.button("📝 Rephrase Question", key="rephrase_ai", help="Try asking in a different way"):
                    st.info("💡 Try rephrasing your question above for a different approach")
        
        # Display results based on type
        elif isinstance(result, dict):
            # Check for comparison ranking view
            if result.get('type') == 'comparison_ranking':
                st.markdown(f"### {result['stat']} Leaders - {result['year']}")
                st.caption("Showing ranked results for comparison")
                
                # Highlight search term if provided
                df = result['data']
                if result.get('search_term'):
                    st.info(f"Looking for players matching: **{result['search_term']}**")
                
                # Display with highlighting
                st.dataframe(
                    df.head(50),  # Show top 50
                    width='stretch',
                    hide_index=True
                )
                
                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Rankings as CSV",
                    data=csv,
                    file_name=f"{result['stat']}_rankings_{result['year']}.csv",
                    mime="text/csv"
                )
            
            # Check if it's a career breakdown
            elif result.get('type') == 'career_breakdown':
                st.markdown(f"### Career Statistics for {result['player']}")
                
                # Show season-by-season breakdown
                st.markdown("#### Season by Season")
                st.dataframe(
                    result['by_season'],
                    width='stretch',
                    hide_index=True
                )
                
                # Show career totals
                st.markdown("#### Career Totals")
                totals = result['totals']
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Seasons Played", totals['seasons'])
                
                # Display counting stats
                st.markdown("**Counting Stats:**")
                totals_cols = st.columns(4)
                stats_to_show = list(totals['totals'].items())[:8]  # Show first 8 stats
                for i, (stat_name, value) in enumerate(stats_to_show):
                    with totals_cols[i % 4]:
                        st.metric(stat_name, value)
                
                # Display rate stats
                st.markdown("**Career Rate Stats:**")
                rate_cols = st.columns(len(totals['career_rates']))
                for i, (stat_name, value) in enumerate(totals['career_rates'].items()):
                    with rate_cols[i]:
                        st.metric(stat_name.upper(), value)
                
                # Download button
                csv = result['by_season'].to_csv(index=False)
                st.download_button(
                    label="📥 Download Career Stats as CSV",
                    data=csv,
                    file_name=f"{result['player']}_career_stats.csv",
                    mime="text/csv"
                )
            
            elif result.get('type') == 'team_career':
                st.markdown(f"### Career Statistics for {result['team']}")
                
                st.dataframe(
                    result['data'],
                    width='stretch',
                    hide_index=True
                )
                
                # Download button
                csv = result['data'].to_csv(index=False)
                st.download_button(
                    label="📥 Download Team Career Stats as CSV",
                    data=csv,
                    file_name=f"{result['team']}_career_stats.csv",
                    mime="text/csv"
                )
            
            else:
                # Single player stat or ranking
                st.markdown("### Results")
                
                # Check if there's leaders context to show
                if 'leaders_context' in result:
                    # Show player's stat prominently
                    metrics_to_show = {k: v for k, v in result.items() if k not in ['leaders_context']}
                    cols = st.columns(len(metrics_to_show))
                    for i, (key, value) in enumerate(metrics_to_show.items()):
                        with cols[i]:
                            st.metric(label=key.replace('_', ' ').title(), value=value)
                    
                    # Show ranking context
                    st.markdown("#### League Context")
                    st.caption(f"Top players in {result.get('stat', 'this statistic')} - {result.get('year', '')}")
                    st.dataframe(
                        result['leaders_context'],
                        width='stretch',
                        hide_index=True
                    )
                else:
                    # Just show metrics
                    cols = st.columns(len(result))
                    for i, (key, value) in enumerate(result.items()):
                        with cols[i]:
                            st.metric(label=key.replace('_', ' ').title(), value=value)
        else:
            # DataFrame results (leaders or team rankings)
            st.markdown("### Results")
            st.dataframe(
                result,
                width='stretch',
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
