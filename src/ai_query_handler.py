"""
AI-Powered Query Handler for MLB Statistics

This module uses generative AI to interpret user questions and dynamically
generate Python code to answer queries that don't match predefined patterns.

When a query fails with the standard parser, this handler:
1. Sends the question to an AI model (OpenAI GPT-4 or Ollama)
2. AI generates Python code using the MLB API
3. Code is validated and executed in a sandboxed environment
4. Results are returned to the user

Supported AI Providers:
- OpenAI (GPT-4, GPT-3.5-Turbo) - Cloud, requires API key, costs money
- Ollama (llama3.2, mistral, etc.) - Local, FREE, no API key needed

This provides unlimited query flexibility without predefined patterns.
"""

import os
import sys
import json
import re
from typing import Dict, Any, Optional, Tuple
import traceback


class AIQueryHandler:
    """
    Handles queries using AI to generate and execute code dynamically.
    """
    
    def __init__(self, data_fetcher, data_processor, provider: str = "auto"):
        """
        Initialize the AI query handler.
        
        Args:
            data_fetcher: MLBDataFetcher instance for API access
            data_processor: MLBDataProcessor instance for data processing
            provider: "auto" (default), "ollama" (free), or "openai" (cloud)
        """
        self.data_fetcher = data_fetcher
        self.data_processor = data_processor
        self.provider = None
        self.openai = None
        self.ollama = None
        self.model = None
        self.ai_available = False
        
        # Auto-detect or use specified provider
        if provider == "auto":
            # Try Ollama first (free, local)
            if self._init_ollama():
                return
            # Fallback to OpenAI
            self._init_openai()
        elif provider == "ollama":
            self._init_ollama()
        elif provider == "openai":
            self._init_openai()
    
    def _init_ollama(self) -> bool:
        """Try to initialize Ollama (free, local AI)."""
        try:
            import ollama
            # Test if Ollama is running
            try:
                ollama.list()
                self.ollama = ollama
                self.model = os.environ.get('OLLAMA_MODEL', 'llama3.2')
                self.provider = "ollama"
                self.ai_available = True
                print(f"[OK] Using Ollama (FREE) with model: {self.model}")
                return True
            except Exception as e:
                print(f"Ollama not running: {e}")
                return False
        except ImportError:
            return False
    
    def _init_openai(self) -> bool:
        """Try to initialize OpenAI (cloud, paid)."""
        try:
            import openai
            api_key = self._get_api_key()
            if api_key:
                self.openai = openai
                self.openai.api_key = api_key
                self.model = "gpt-4"
                self.provider = "openai"
                self.ai_available = True
                print(f"[OK] Using OpenAI with model: {self.model}")
                return True
            else:
                print("No OPENAI_API_KEY found")
                return False
        except ImportError:
            print("OpenAI package not installed")
            return False
    
    def _get_api_key(self) -> Optional[str]:
        """Get OpenAI API key from environment variable."""
        return os.environ.get('OPENAI_API_KEY')
    
    def is_available(self) -> bool:
        """Check if AI query handling is available."""
        return self.ai_available
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the active AI provider."""
        if not self.ai_available:
            return {
                "provider": "none",
                "model": None,
                "cost": None,
                "location": None
            }
        
        if self.provider == "ollama":
            return {
                "provider": "ollama",
                "model": self.model,
                "cost": "free",
                "location": "local"
            }
        else:  # openai
            return {
                "provider": "openai",
                "model": self.model,
                "cost": "paid",
                "location": "cloud"
            }
    
    def handle_query(self, question: str, season: int = 2024, progress_callback=None) -> Dict[str, Any]:
        """
        Use AI to interpret the question and generate code to answer it.
        
        Args:
            question: User's natural language question
            season: Season year for the query
            progress_callback: Optional function to call with progress updates
            
        Returns:
            Dictionary with results or error information
        """
        def report_progress(step: str, detail: str = ""):
            """Report progress to callback if provided."""
            if progress_callback:
                progress_callback(step, detail)
        
        if not self.ai_available:
            return {
                'success': False,
                'error': 'AI not available. Install Ollama (free) or set OPENAI_API_KEY.',
                'suggestion': 'Try rephrasing your question or use standard query patterns.'
            }
        
        try:
            # Step 1: Send question to AI
            report_progress("Step 1", f"Sending your question to {self.provider.upper()} AI model ({self.model})...")
            code = self._generate_code(question, season)
            
            if not code:
                return {
                    'success': False,
                    'error': 'AI could not generate code for this question.',
                    'suggestion': 'Try rephrasing your question more clearly.'
                }
            
            # Step 2: Validate generated code
            report_progress("Step 2", "Analyzing AI-generated code for security and safety...")
            is_safe, safety_message = self._validate_code_safety(code)
            
            if not is_safe:
                return {
                    'success': False,
                    'error': f'Generated code failed safety check: {safety_message}',
                    'code': code,
                    'steps': [
                        "✓ AI understood your question",
                        "✓ Generated Python code",
                        "✗ Code blocked by security validation"
                    ]
                }
            
            report_progress("Step 3", "Code passed security checks. Executing query against MLB API...")
            
            # Step 3: Execute the code
            result = self._execute_code(code, question, season)
            
            # Add steps to result
            if result.get('success'):
                result['steps'] = [
                    f"✓ AI ({self.provider}) interpreted your question",
                    "✓ Generated Python code to query MLB API",
                    "✓ Code passed security validation",
                    "✓ Executed query and retrieved data",
                    "✓ Processed results successfully"
                ]
                report_progress("Complete", "Query completed successfully!")
            else:
                result['steps'] = [
                    f"✓ AI ({self.provider}) interpreted your question",
                    "✓ Generated Python code",
                    "✓ Code passed security checks",
                    "✗ Execution failed (see error details)"
                ]
                report_progress("Failed", f"Execution failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'AI query handling failed: {str(e)}',
                'traceback': traceback.format_exc(),
                'steps': [
                    "✗ AI query handler encountered an error"
                ]
            }
    
    def _generate_code(self, question: str, season: int) -> str:
        """
        Use AI to generate Python code that answers the question.
        
        Args:
            question: User's question
            season: Season year
            
        Returns:
            Generated Python code as string
        """
        system_prompt = """You are a Python code generator for MLB statistics queries.

You have access to:
1. data_fetcher - An MLBDataFetcher instance with methods:
   - get_teams(season) -> list of teams for a season
   - search_players(name) -> list of players matching name (finds active and retired players)
   - get_player_season_stats(player_id, season) -> player stats for specific season
   - get_team_season_stats(team_id, season, stat_group='hitting') -> team stats for specific season
   - get_player_career_stats(player_id, stat_group) -> list of dicts with stats for each season
   - get_team_career_stats(team_id, stat_group, start_year, end_year) -> list of dicts with stats for each season
   - get_stats_leaders(stat_type, season, limit, stat_group, team_id=None, league_id=None, include_all=False) -> league leaders
   - get_team_stats(season, stat_group='hitting') -> stats for all MLB teams in a season

2. data_processor - An MLBDataProcessor instance with methods:
   - extract_stats_leaders(data) -> DataFrame with ranked leaders
   - extract_team_stats(teams_data, stat_name) -> DataFrame with team rankings
   - filter_by_season(data, season) -> filtered data
   - aggregate_career_stats(career_data, stat_group) -> dict with 'seasons', 'totals', 'career_rates'
   - create_career_dataframe(career_data) -> DataFrame with one row per season
   - compare_player_careers(player1_career, player2_career, stat_group) -> comparison DataFrame

3. pandas as pd, numpy as np - for data processing

IMPORTANT STAT FIELD NAMES (from get_player_season_stats after parsing):
Hitting stats: gamesPlayed, avg, homeRuns, rbi, runs, stolenBases, hits, doubles, triples, 
               atBats, obp, slg, ops, strikeOuts, baseOnBalls, hitByPitch
Pitching stats: wins, losses, era, whip, strikeOuts, inningsPitched, hits, earnedRuns, baseOnBalls

NOTE: Use 'runs' for runs scored (NOT 'r'), 'rbi' for RBI (NOT 'runsBattedIn')

Generate ONLY the Python code needed to answer the question. The code should:
- Use the provided data_fetcher and data_processor instances
- Return a result dictionary with 'data', 'explanation', and 'answer' keys
- Handle errors gracefully
- Be efficient and clean

IMPORTANT:
- Do NOT include import statements for data_fetcher, data_processor, pd, or np
- Do NOT include any explanatory text, just the code
- Use try/except to handle potential errors
- The code will be executed in a controlled environment

COMPARISON QUERY GUIDELINES:
- If comparing players/teams in a SINGLE SEASON with NO specific stat mentioned: Use get_player_season_stats or get_team_season_stats to get full stats
- If comparing a SPECIFIC STAT (like "home runs" or "batting average"): Use get_stats_leaders with include_all=True to show rankings
- If comparing CAREER stats: Use get_player_career_stats/get_team_career_stats and compare_player_careers
- Keywords that indicate full season comparison: "vs", "versus", "compare", "in [year]" without stat mention

Example 1 (Season Leaders):
Question: "Who hit the most home runs in 2024?"
Code:
```python
try:
    leaders = data_fetcher.get_stats_leaders('homeRuns', season, 1, 'hitting')
    processed = data_processor.extract_stats_leaders(leaders)
    if not processed.empty:
        player = processed.iloc[0]
        result = {
            'success': True,
            'data': processed.to_dict('records'),
            'answer': f"{player['playerName']} hit the most home runs with {player['value']} HR",
            'explanation': 'Retrieved hitting leaders for home runs from MLB API'
        }
    else:
        result = {'success': False, 'error': 'No data found'}
except Exception as e:
    result = {'success': False, 'error': str(e)}
```

Example 2 (Career Stats):
Question: "What are Aaron Judge's career home runs?"
Code:
```python
try:
    # Search for player
    players = data_fetcher.search_players('Aaron Judge')
    if not players:
        result = {'success': False, 'error': 'Player not found'}
    else:
        player_id = players[0]['id']
        player_name = players[0]['fullName']
        
        # Get career stats
        career_data = data_fetcher.get_player_career_stats(player_id, 'hitting')
        career_totals = data_processor.aggregate_career_stats(career_data, 'hitting')
        
        total_hrs = career_totals['totals'].get('homeRuns', 0)
        seasons = career_totals['seasons']
        
        result = {
            'success': True,
            'data': {'player': player_name, 'career_home_runs': total_hrs, 'seasons': seasons},
            'answer': f"{player_name} has {total_hrs} career home runs across {seasons} seasons",
            'explanation': 'Retrieved and aggregated career statistics for player'
        }
except Exception as e:
    result = {'success': False, 'error': str(e)}
```

Example 3 (Career Comparison):
Question: "Compare Aaron Judge and Juan Soto career stats"
Code:
```python
try:
    # Get both players
    judge_results = data_fetcher.search_players('Aaron Judge')
    soto_results = data_fetcher.search_players('Juan Soto')
    
    if not judge_results or not soto_results:
        result = {'success': False, 'error': 'One or both players not found'}
    else:
        # Get career data
        judge_career = data_fetcher.get_player_career_stats(judge_results[0]['id'], 'hitting')
        soto_career = data_fetcher.get_player_career_stats(soto_results[0]['id'], 'hitting')
        
        # Compare careers
        comparison_df = data_processor.compare_player_careers(judge_career, soto_career, 'hitting')
        
        result = {
            'success': True,
            'data': comparison_df.to_dict('records'),
            'answer': f"Career comparison between {judge_results[0]['fullName']} and {soto_results[0]['fullName']}",
            'explanation': 'Compared career statistics for both players'
        }
except Exception as e:
    result = {'success': False, 'error': str(e)}
```

Example 4 (Single Season Full Stats Comparison):
Question: "Aaron Judge vs Cal Raleigh in 2024"
Code:
```python
try:
    # Search for both players
    judge_results = data_fetcher.search_players('Aaron Judge')
    raleigh_results = data_fetcher.search_players('Cal Raleigh')
    
    if not judge_results or not raleigh_results:
        result = {'success': False, 'error': 'One or both players not found'}
    else:
        # Get season stats for both players (returns nested structure)
        judge_stats_raw = data_fetcher.get_player_season_stats(judge_results[0]['id'], season)
        raleigh_stats_raw = data_fetcher.get_player_season_stats(raleigh_results[0]['id'], season)
        
        # Parse the nested stats structure: stats[0]['splits'][0]['stat']
        judge_stats = {}
        if judge_stats_raw and 'stats' in judge_stats_raw:
            for stat_group in judge_stats_raw['stats']:
                if stat_group.get('group', {}).get('displayName') == 'hitting' and stat_group.get('splits'):
                    judge_stats = stat_group['splits'][0]['stat']
                    break
        
        raleigh_stats = {}
        if raleigh_stats_raw and 'stats' in raleigh_stats_raw:
            for stat_group in raleigh_stats_raw['stats']:
                if stat_group.get('group', {}).get('displayName') == 'hitting' and stat_group.get('splits'):
                    raleigh_stats = stat_group['splits'][0]['stat']
                    break
        
        # Check if we have data for both players
        if not judge_stats or not raleigh_stats:
            result = {'success': False, 'error': f'No {season} season data available yet for one or both players'}
        else:
            # Extract key hitting stats for comparison
            judge_data = {
                'player': judge_results[0]['fullName'],
                'games': judge_stats.get('gamesPlayed', 0),
                'avg': judge_stats.get('avg', '.000'),
                'hr': judge_stats.get('homeRuns', 0),
                'rbi': judge_stats.get('rbi', 0),
                'runs': judge_stats.get('runs', 0),
                'sb': judge_stats.get('stolenBases', 0),
                'ops': judge_stats.get('ops', '.000')
            }
            
            raleigh_data = {
                'player': raleigh_results[0]['fullName'],
                'games': raleigh_stats.get('gamesPlayed', 0),
                'avg': raleigh_stats.get('avg', '.000'),
                'hr': raleigh_stats.get('homeRuns', 0),
                'rbi': raleigh_stats.get('rbi', 0),
                'runs': raleigh_stats.get('runs', 0),
                'sb': raleigh_stats.get('stolenBases', 0),
                'ops': raleigh_stats.get('ops', '.000')
            }
            
            comparison_df = pd.DataFrame([judge_data, raleigh_data])
            
            result = {
                'success': True,
                'data': comparison_df.to_dict('records'),
                'answer': f"{season} season comparison: {judge_results[0]['fullName']} vs {raleigh_results[0]['fullName']}",
                'explanation': f'Retrieved and compared {season} season statistics for both players'
            }
except Exception as e:
    result = {'success': False, 'error': str(e)}
```

Example 5 (Single Stat Comparison with Ranking):
Question: "Aaron Judge vs Juan Soto home runs in 2024"
Code:
```python
try:
    # Get leaders to show both in context
    leaders = data_fetcher.get_stats_leaders('homeRuns', season, 100, 'hitting', include_all=True)
    leaders_df = data_processor.extract_stats_leaders(leaders)
    
    if leaders_df.empty:
        result = {'success': False, 'error': 'No leaders data found'}
    else:
        # Find both players
        judge_row = leaders_df[leaders_df['playerName'].str.contains('Judge', case=False, na=False)]
        soto_row = leaders_df[leaders_df['playerName'].str.contains('Soto', case=False, na=False)]
        
        comparison_text = ""
        if not judge_row.empty and not soto_row.empty:
            judge_rank = judge_row.iloc[0]['rank']
            judge_hrs = judge_row.iloc[0]['value']
            soto_rank = soto_row.iloc[0]['rank']
            soto_hrs = soto_row.iloc[0]['value']
            
            comparison_text = f"Aaron Judge: #{judge_rank} with {judge_hrs} HR, Juan Soto: #{soto_rank} with {soto_hrs} HR"
        
        result = {
            'success': True,
            'data': leaders_df.head(50).to_dict('records'),
            'answer': comparison_text if comparison_text else "Home run leaders comparison",
            'explanation': f'Retrieved {season} home run leaders showing both players in ranked context'
        }
except Exception as e:
    result = {'success': False, 'error': str(e)}
```

Now generate code for the user's question."""

        user_prompt = f"""Question: {question}
Season: {season}

Generate Python code to answer this question using the MLB API."""

        try:
            if self.provider == "ollama":
                # Use Ollama (free, local)
                response = self.ollama.chat(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                generated_code = response['message']['content'].strip()
            else:
                # Use OpenAI (cloud, paid)
                response = self.openai.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,
                    max_tokens=1000
                )
                generated_code = response.choices[0].message.content.strip()
            
            # Extract code from markdown code blocks if present
            code_match = re.search(r'```python\n(.*?)\n```', generated_code, re.DOTALL)
            if code_match:
                generated_code = code_match.group(1)
            
            return generated_code
            
        except Exception as e:
            print(f"Error generating code with AI: {e}")
            return ""
    
    def _validate_code_safety(self, code: str) -> Tuple[bool, str]:
        """
        Validate that generated code is safe to execute.
        
        Args:
            code: Generated Python code
            
        Returns:
            Tuple of (is_safe: bool, message: str)
        """
        # List of dangerous patterns that should not appear in generated code
        dangerous_patterns = [
            r'\beval\s*\(',
            r'\bexec\s*\(',
            r'\b__import__\s*\(',
            r'\bcompile\s*\(',
            r'\bopen\s*\(',
            r'\bfile\s*\(',
            r'\binput\s*\(',
            r'\bos\.system',
            r'\bos\.popen',
            r'\bsubprocess',
            r'\bshutil',
            r'\brmdir',
            r'\bunlink',
            r'\bremove',
            r'import\s+os',
            r'import\s+sys',
            r'import\s+subprocess',
            r'import\s+shutil',
            r'from\s+os',
            r'from\s+sys',
            r'__',  # Dunder methods (except in strings)
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code):
                return False, f"Dangerous pattern detected: {pattern}"
        
        # Check for allowed imports only
        allowed_imports = ['pandas', 'numpy', 'json', 'datetime', 're']
        import_pattern = r'import\s+(\w+)|from\s+(\w+)'
        imports = re.findall(import_pattern, code)
        
        for imp in imports:
            module = imp[0] or imp[1]
            if module and module not in allowed_imports:
                return False, f"Unauthorized import: {module}"
        
        # Basic syntax check
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
        
        return True, "Code passed safety checks"
    
    def _execute_code(self, code: str, question: str, season: int) -> Dict[str, Any]:
        """
        Execute the generated code in a controlled environment.
        
        Args:
            code: Python code to execute
            question: Original question
            season: Season year
            
        Returns:
            Results dictionary
        """
        # Create a restricted execution environment
        restricted_globals = {
            'data_fetcher': self.data_fetcher,
            'data_processor': self.data_processor,
            'season': season,
            'question': question,
            '__builtins__': {
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'map': map,
                'filter': filter,
                'sum': sum,
                'min': min,
                'max': max,
                'abs': abs,
                'round': round,
                'sorted': sorted,
                'any': any,
                'all': all,
                'print': print,  # Allow print for debugging
                'Exception': Exception,
                'ValueError': ValueError,
                'KeyError': KeyError,
                'TypeError': TypeError,
            }
        }
        
        # Import commonly needed modules in the execution environment
        try:
            import pandas as pd
            import numpy as np
            restricted_globals['pd'] = pd
            restricted_globals['np'] = np
        except ImportError:
            pass
        
        restricted_locals = {}
        
        try:
            # Execute the generated code
            exec(code, restricted_globals, restricted_locals)
            
            # Get the result
            result = restricted_locals.get('result', {})
            
            if not isinstance(result, dict):
                result = {
                    'success': False,
                    'error': 'Generated code did not produce a result dictionary'
                }
            
            # Add metadata
            result['ai_generated'] = True
            result['generated_code'] = code
            result['original_question'] = question
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Code execution failed: {str(e)}',
                'traceback': traceback.format_exc(),
                'generated_code': code,
                'ai_generated': True
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test if AI connection is working.
        
        Returns:
            Status dictionary
        """
        if not self.ai_available:
            return {
                'success': False,
                'message': 'No AI provider available. Install Ollama or set OPENAI_API_KEY.'
            }
        
        try:
            if self.provider == "ollama":
                # Test Ollama
                response = self.ollama.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": "Say 'OK'"}]
                )
                return {
                    'success': True,
                    'message': 'Connection successful!',
                    'model': self.model,
                    'provider': 'Ollama (FREE, local)'
                }
            else:
                # Test OpenAI
                response = self.openai.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": "Say 'OK'"}],
                    max_tokens=10
                )
                return {
                    'success': True,
                    'message': 'Connection successful!',
                    'model': self.model,
                    'provider': 'OpenAI (cloud, paid)'
                }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Connection failed: {str(e)}'
            }


def get_ai_handler(data_fetcher, data_processor) -> Optional[AIQueryHandler]:
    """
    Factory function to create an AI query handler.
    
    Args:
        data_fetcher: MLBDataFetcher instance
        data_processor: MLBDataProcessor instance
        
    Returns:
        AIQueryHandler instance or None if not available
    """
    handler = AIQueryHandler(data_fetcher, data_processor)
    
    if handler.is_available():
        return handler
    else:
        return None
